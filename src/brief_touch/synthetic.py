"""Deliberately identifiable toy contacts for software checks, not research results."""

import json
from pathlib import Path

import numpy as np

from .data import CHANNELS, digest


def generate(output, config, groups=10):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(config["seed"])
    manifest = {"schema_version": 1, "cohort": "pilot", "source_kind": "synthetic",
                "force_frame": "force_on_moving_body",
                "units": dict(zip(CHANNELS, ("s", "N", "N", "m/s", "m/s^2"))),
                "warning": "Generated Coulomb toy data; no real experimental conclusions", "trials": []}
    time = np.arange(700) / 1000
    for group in range(groups):
        mu = 0.15 + 0.7 * group / max(1, groups - 1)
        for speed in config["speeds_m_s"]:
            for load in config["loads_n"]:
                for repeat in range(config["repetitions"]):
                    identity = f"S{group:02d}_v{speed:g}_n{load:g}_r{repeat}"
                    force_n = np.full(len(time), load) + rng.normal(0, 0.003, len(time))
                    force_t = -mu * force_n + rng.normal(0, 0.008, len(time))
                    acceleration = (1 + 5 * mu) * np.sin(2 * np.pi * 100 * time)
                    acceleration += rng.normal(0, 0.08, len(time))
                    path = output / f"{identity}.npz"
                    np.savez_compressed(path, time_s=time, normal_force_n=force_n,
                                        tangential_force_n=force_t, velocity_m_s=np.full(len(time), speed),
                                        tactile_m_s2=acceleration)
                    manifest["trials"].append({"trial_id": identity, "group_id": f"synthetic-{group:02d}",
                                               "specimen_id": f"synthetic-{group:02d}", "repetition": repeat,
                                               "speed_m_s": speed, "load_n": load, "valid_start_s": 0.1,
                                               "native_rate_hz": 1000, "sliding_verified": True,
                                               "pad_id": "synthetic-pad", "session_id": "synthetic-session",
                                               "calibration_id": "synthetic-identity", "path": path.name,
                                               "sha256": digest(path)})
    path = output / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
