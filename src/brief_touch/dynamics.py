"""Exact unforced 1-D Coulomb motion, including a non-reversing stop event."""

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class Rollout:
    time: np.ndarray
    position: np.ndarray
    velocity: np.ndarray
    stop_time_s: float
    stop_distance_m: float


def coast(mu, mass_kg, normal_load_n, initial_velocity_m_s, times_s, initial_position_m=0.0):
    parameters = (mu, mass_kg, normal_load_n, initial_velocity_m_s, initial_position_m)
    if not all(math.isfinite(v) for v in parameters) or mu < 0 or mass_kg <= 0 or normal_load_n < 0:
        raise ValueError("Invalid coasting parameters")
    t = np.asarray(times_s, dtype=float)
    if t.ndim != 1 or not len(t) or not np.isfinite(t).all() or np.any(t < 0) or np.any(np.diff(t) <= 0):
        raise ValueError("Times must be finite, nonnegative and strictly increasing")
    speed = abs(initial_velocity_m_s)
    direction = np.sign(initial_velocity_m_s)
    a = mu * normal_load_n / mass_kg
    stop = 0.0 if speed == 0 else speed / a if a > 0 else math.inf
    active_t = np.minimum(t, stop)
    velocity = direction * np.maximum(0, speed - a * active_t)
    position = initial_position_m + direction * (speed * active_t - 0.5 * a * active_t**2)
    distance = 0.0 if speed == 0 else speed**2 / (2 * a) if a > 0 else math.inf
    return Rollout(t, position, velocity, stop, distance)


def stop_error(predicted_distance_m, observed_distance_m, predicted_time_s, observed_time_s,
               max_time_s, travel_limit_m):
    if max_time_s <= 0 or travel_limit_m <= 0 or not math.isfinite(max_time_s + travel_limit_m):
        raise ValueError("Invalid tracking limits")
    values = (predicted_distance_m, observed_distance_m, predicted_time_s, observed_time_s)
    valid = all(math.isfinite(v) and v >= 0 for v in values)
    valid &= max(predicted_time_s, observed_time_s) <= max_time_s
    valid &= max(predicted_distance_m, observed_distance_m) <= travel_limit_m
    return abs(predicted_distance_m - observed_distance_m) if valid else travel_limit_m


def release_speed(mu, target_distance_m, mass_kg, normal_load_n, max_speed_m_s):
    if not all(math.isfinite(v) for v in (mu, target_distance_m, mass_kg, normal_load_n, max_speed_m_s)):
        raise ValueError("Nonfinite launch parameters")
    if min(mu, target_distance_m, normal_load_n) < 0 or mass_kg <= 0 or max_speed_m_s <= 0:
        raise ValueError("Invalid launch parameters")
    requested = math.sqrt(2 * mu * normal_load_n * target_distance_m / mass_kg)
    return {"requested_m_s": requested, "commanded_m_s": min(requested, max_speed_m_s),
            "saturated": requested > max_speed_m_s}
