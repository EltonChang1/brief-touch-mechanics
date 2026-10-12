"""Convert explicit CSV channels through a versioned calibration to the SI contract."""

import csv
import json
from pathlib import Path

import numpy as np

from .data import digest


def import_csv(source, calibration, output):
    source, calibration, output = map(Path, (source, calibration, output))
    if output.exists() or output.with_suffix(".provenance.json").exists():
        raise FileExistsError("Refusing to overwrite a calibrated trial")
    if output.suffix != ".npz":
        raise ValueError("Output must be an .npz file")
    settings = json.loads(calibration.read_text(encoding="utf-8"))
    if settings.get("force_output_frame") != "force_on_moving_body":
        raise ValueError("Calibration must explicitly produce the moving-body force convention")
    with source.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    columns = settings["columns"]
    arrays = {key: np.asarray([float(row[column]) for row in rows]) for key, column in columns.items()}
    if not rows or any(not np.isfinite(v).all() for v in arrays.values()):
        raise ValueError("CSV contains no samples or nonfinite values")
    raw_force = np.column_stack([arrays["normal"], arrays["tangential"]])
    matrix, bias = np.asarray(settings["force_matrix_n_per_raw"]), np.asarray(settings["force_bias_n"])
    if matrix.shape != (2, 2) or bias.shape != (2,) or not np.isfinite(matrix).all() or not np.isfinite(bias).all():
        raise ValueError("Invalid force calibration matrix/bias")
    force = raw_force @ matrix.T + bias
    scales = settings["scales_to_si"]
    if any(not np.isfinite(scales[k]) or scales[k] <= 0 for k in ("time", "velocity", "tactile")):
        raise ValueError("Unit conversion scales must be finite and positive")
    time = arrays["time"] * scales["time"]
    if np.any(np.diff(time) <= 0):
        raise ValueError("CSV timestamps must be strictly increasing")
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, time_s=time, normal_force_n=force[:, 0], tangential_force_n=force[:, 1],
                        velocity_m_s=arrays["velocity"] * scales["velocity"],
                        tactile_m_s2=arrays["tactile"] * scales["tactile"])
    provenance = {"source_path": str(source.resolve()), "source_sha256": digest(source),
                  "calibration_path": str(calibration.resolve()), "calibration_sha256": digest(calibration),
                  "output_sha256": digest(output), "calibration_id": settings["calibration_id"],
                  "measurement_gate": "requires independent calibration/timing/sliding evidence"}
    output.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance
