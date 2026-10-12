"""Calibrated trial contract and strict support boundaries."""

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path

import numpy as np

CHANNELS = ("time_s", "normal_force_n", "tangential_force_n", "velocity_m_s", "tactile_m_s2")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class Trial:
    trial_id: str
    group_id: str
    specimen_id: str
    repetition: int
    speed_m_s: float
    load_n: float
    valid_start_s: float
    native_rate_hz: float
    time: np.ndarray
    normal: np.ndarray
    tangential: np.ndarray
    velocity: np.ndarray
    tactile: np.ndarray

    @property
    def condition(self):
        return self.speed_m_s, self.load_n

    def window(self, seconds):
        if not np.isfinite(seconds) or seconds <= 0:
            raise ValueError("Support duration must be finite and positive")
        end = self.valid_start_s + seconds
        if self.time[0] > self.valid_start_s or self.time[-1] + 1 / self.native_rate_hz < end - 1e-9:
            raise ValueError(f"Incomplete support window: {self.trial_id}")
        mask = (self.time >= self.valid_start_s - 1e-12) & (self.time < end - 1e-12)
        arrays = [a[mask].copy() for a in [self.time, self.normal, self.tangential, self.velocity, self.tactile]]
        if len(arrays[0]) < 8:
            raise ValueError("Too few samples in support window")
        if np.max(np.diff(arrays[0])) > 1.5 / self.native_rate_hz:
            raise ValueError("Missing samples in support window")
        for a in arrays:
            a.setflags(write=False)
        return replace(self, time=arrays[0], normal=arrays[1], tangential=arrays[2],
                       velocity=arrays[3], tactile=arrays[4])


def load_dataset(manifest_path):
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Expected trial manifest schema_version=1")
    if manifest.get("source_kind") not in ("synthetic", "real"):
        raise ValueError("source_kind must be synthetic or real")
    if manifest.get("cohort") != "pilot":
        raise ValueError("This runner only opens pilot data; confirmation requires a frozen protocol")
    if manifest.get("units") != dict(zip(CHANNELS, ("s", "N", "N", "m/s", "m/s^2"))):
        raise ValueError("Channels must use declared SI units")
    if manifest.get("force_frame") != "force_on_moving_body":
        raise ValueError("Transform fixture reaction into force_on_moving_body first")
    hashes = {str(path): digest(path)}
    if manifest["source_kind"] == "real":
        evidence = manifest.get("measurement_evidence", {})
        for key in ("force_calibration", "timing_alignment", "sliding_verification", "contact_geometry"):
            entry = evidence.get(key, {})
            file = path.parent / entry.get("path", "")
            if entry.get("status") != "verified" or not file.is_file():
                raise ValueError(f"Measurement gate not passed: {key}")
            if entry.get("sha256") != digest(file):
                raise ValueError(f"Evidence digest mismatch: {key}")
            hashes[str(file)] = digest(file)
    trials, seen = [], set()
    for row in manifest["trials"]:
        if row["trial_id"] in seen:
            raise ValueError("Duplicate trial identity")
        seen.add(row["trial_id"])
        file = (path.parent / row["path"]).resolve()
        hashes[str(file)] = digest(file)
        if row.get("sha256") != hashes[str(file)]:
            raise ValueError(f"Raw digest mismatch: {file}")
        if row.get("sliding_verified") is not True:
            raise ValueError("Each trial requires independently verified sliding")
        if not row.get("calibration_id") or not row.get("pad_id") or not row.get("session_id"):
            raise ValueError("Trial requires calibration, pad and session IDs")
        with np.load(file, allow_pickle=False) as archive:
            arrays = [np.asarray(archive[k], dtype=float).copy() for k in CHANNELS]
        n = len(arrays[0])
        if n < 8 or any(a.shape != (n,) or not np.isfinite(a).all() for a in arrays):
            raise ValueError("Nonfinite, missing, or incompatible channel samples")
        rate = float(row["native_rate_hz"])
        if not np.isfinite(rate) or rate <= 0 or np.any(np.diff(arrays[0]) <= 0):
            raise ValueError("Invalid sampling rate or nonmonotonic timestamps")
        if not np.allclose(np.diff(arrays[0]), 1 / rate, rtol=0.01, atol=1e-9):
            raise ValueError("Irregular/native-rate-inconsistent signals; verify before conversion")
        for a in arrays:
            a.setflags(write=False)
        trial = Trial(row["trial_id"], row["group_id"], row["specimen_id"], int(row["repetition"]),
                      float(row["speed_m_s"]), float(row["load_n"]), float(row["valid_start_s"]),
                      rate, *arrays)
        if not all(np.isfinite(x) for x in (trial.speed_m_s, trial.load_n, trial.valid_start_s)):
            raise ValueError("Invalid condition/window metadata")
        trials.append(trial)
    # A single pad is the initial experiment's contact domain.
    if len({r["pad_id"] for r in manifest["trials"]}) != 1:
        raise ValueError("Mixed contact pads require a separately declared transfer protocol")
    specimen_groups = {}
    for t in trials:
        if t.specimen_id in specimen_groups and specimen_groups[t.specimen_id] != t.group_id:
            raise ValueError("A specimen cannot occur in multiple holdout groups")
        specimen_groups[t.specimen_id] = t.group_id
    return trials, manifest, hashes


def verify_unchanged(hashes):
    for path, expected in hashes.items():
        if digest(path) != expected:
            raise ValueError(f"Input changed during evaluation: {path}")
