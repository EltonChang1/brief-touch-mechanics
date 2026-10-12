"""Simple contact estimators; features only consume cropped support."""

import numpy as np


def sufficient_statistics(window, min_load, min_speed):
    if np.any(window.normal < min_load) or np.any(np.abs(window.velocity) < min_speed):
        raise ValueError("Support includes low load or unverified low-speed sliding")
    resisting = -window.tangential * np.sign(window.velocity)
    # Diagnose convention errors instead of hiding systematic negative estimates.
    if float(np.mean(resisting)) < -0.01:
        raise ValueError("Tangential force convention gives an assisting sliding force")
    return float(np.mean(window.normal * resisting)), float(np.mean(window.normal**2))


def fit_coulomb(windows, min_load=0.2, min_speed=0.01):
    pairs = np.asarray([sufficient_statistics(w, min_load, min_speed) for w in windows])
    return max(0.0, float(pairs[:, 0].mean() / pairs[:, 1].mean()))


def fit_global(group_windows, min_load, min_speed):
    # Each group contributes one mean objective, independent of sample/trial count.
    means = [np.mean([sufficient_statistics(w, min_load, min_speed) for w in windows], axis=0)
             for windows in group_windows]
    stats = np.asarray(means)
    return max(0.0, float(stats[:, 0].sum() / stats[:, 1].sum()))


def features(window, track, config):
    values = [window.speed_m_s, window.load_n]
    if track in ("force", "force_tactile"):
        mu = fit_coulomb([window], config["min_load_n"], config["min_sliding_speed_m_s"])
        values.extend([mu, float(window.normal.mean()), float(window.normal.std()),
                       float(window.tangential.std())])
    if track in ("tactile", "force_tactile"):
        signal = window.tactile - window.tactile.mean()
        freq = np.fft.rfftfreq(len(signal), 1 / window.native_rate_hz)
        if max(b[1] for b in config["spectral_bands_hz"]) > window.native_rate_hz / 2:
            raise ValueError("Feature bands exceed native Nyquist bandwidth")
        power = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))**2 / len(signal)**2
        values.append(float(np.sqrt(np.mean(signal**2))))
        for lo, hi in config["spectral_bands_hz"]:
            values.append(float(np.log1p(power[(freq >= lo) & (freq < hi)].sum())))
    return np.asarray(values)


class Ridge:
    def __init__(self, alpha=1):
        if alpha <= 0:
            raise ValueError("Regularization must be positive")
        self.alpha = alpha

    def fit(self, x, y):
        x, y = np.asarray(x), np.asarray(y)
        self.mean = x.mean(axis=0)
        self.scale = x.std(axis=0)
        self.scale[self.scale < 1e-12] = 1
        self.y_mean = float(y.mean())
        z = (x - self.mean) / self.scale
        self.weights = np.linalg.solve(z.T @ z + self.alpha * np.eye(z.shape[1]), z.T @ (y - self.y_mean))
        return self

    def predict(self, x):
        return max(0.0, float((np.asarray(x) - self.mean) / self.scale @ self.weights + self.y_mean))


def predict_force(mu, speed, nominal_load):
    if not np.isfinite(mu) or mu < 0 or nominal_load <= 0:
        raise ValueError("Invalid physical parameters")
    return -mu * nominal_load * np.sign(speed)
