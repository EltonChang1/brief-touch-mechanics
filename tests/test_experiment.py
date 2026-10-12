import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from brief_touch.cli import collection_schedule
from brief_touch.data import Trial, digest, load_dataset
from brief_touch.dynamics import coast, release_speed, stop_error
from brief_touch.evaluation import allocate, evaluate_pilot
from brief_touch.ingestion import import_csv
from brief_touch.models import features, fit_coulomb, fit_global
from brief_touch.synthetic import generate


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())


def trial(mu=0.4, velocity=0.15, load=2.0):
    time = np.arange(1000) / 1000
    return Trial("t", "g", "s", 0, velocity, load, 0.1, 1000, time,
                 np.full(1000, load), np.full(1000, -mu * load * np.sign(velocity)),
                 np.full(1000, velocity), np.sin(2 * np.pi * 100 * time))


class BoundaryTests(unittest.TestCase):
    def test_half_open_support_and_future_invariance(self):
        first, changed = trial(), trial()
        changed.normal[600:] = 100
        changed.tangential[600:] = -1000
        changed.tactile[600:] = 1000
        a, b = first.window(0.5), changed.window(0.5)
        self.assertEqual(len(a.time), 500)
        self.assertLess(a.time[-1], 0.6)
        self.assertEqual(fit_coulomb([a]), fit_coulomb([b]))
        np.testing.assert_array_equal(features(a, "force_tactile", CONFIG), features(b, "force_tactile", CONFIG))

    def test_tactile_interface_hides_support_force(self):
        a, b = trial(), trial(mu=8)
        b.normal[:] = 100
        np.testing.assert_array_equal(features(a.window(0.5), "tactile", CONFIG),
                                      features(b.window(0.5), "tactile", CONFIG))

    def test_negative_velocity_force_sign(self):
        self.assertAlmostEqual(fit_coulomb([trial(velocity=-0.15).window(0.5)]), 0.4)

    def test_bad_force_sign_is_rejected(self):
        t = trial()
        t.tangential[:] *= -1
        with self.assertRaisesRegex(ValueError, "assisting"):
            fit_coulomb([t.window(0.5)])

    def test_incomplete_window_and_static_contact(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            trial().window(1)
        with self.assertRaisesRegex(ValueError, "low-speed"):
            fit_coulomb([trial(velocity=0).window(0.5)])

    def test_global_groups_are_equally_weighted(self):
        a, b = trial(mu=0.2).window(0.5), trial(mu=0.8).window(0.5)
        self.assertAlmostEqual(fit_global([[a]*10, [b]], 0.2, 0.01), 0.5)

    def test_feature_bandwidth_is_checked(self):
        c = copy.deepcopy(CONFIG)
        c["spectral_bands_hz"] = [[0, 1000]]
        with self.assertRaisesRegex(ValueError, "Nyquist"):
            features(trial().window(0.5), "tactile", c)


class DynamicsTests(unittest.TestCase):
    def test_analytic_stop_without_reversal(self):
        r = coast(0.4, 0.2, 1.962, 0.2, np.linspace(0, 1, 1001))
        self.assertAlmostEqual(r.stop_distance_m, 0.2**2 / (2 * 0.4 * 9.81))
        self.assertTrue(np.all(r.velocity >= 0))
        self.assertAlmostEqual(r.position[-1], r.stop_distance_m)
        self.assertTrue(np.all(np.diff(r.position) >= -1e-12))

    def test_negative_velocity_and_zero_friction(self):
        r = coast(0.5, 1, 9.81, -0.2, [0, 1])
        self.assertLess(r.position[-1], 0)
        self.assertEqual(r.velocity[-1], 0)
        no_stop = coast(0, 1, 9.81, 0.2, [0, 1])
        self.assertTrue(np.isinf(no_stop.stop_time_s))
        self.assertAlmostEqual(no_stop.position[-1], 0.2)
        self.assertEqual(stop_error(np.inf, 0.01, np.inf, 0.1, 1, 0.2), 0.2)

    def test_zero_velocity_and_failures_retained(self):
        stationary = coast(0, 1, 0, 0, [0, 1])
        self.assertEqual(stationary.stop_distance_m, 0)
        self.assertEqual(stop_error(0.01, 0.02, 0.1, 0.2, 1, 0.2), 0.01)
        self.assertEqual(stop_error(0.3, 0.02, 0.1, 0.2, 1, 0.2), 0.2)

    def test_launch_saturation_and_units(self):
        command = release_speed(0.5, 0.02, 0.2, 1.962, 0.1)
        self.assertTrue(command["saturated"])
        self.assertEqual(command["commanded_m_s"], 0.1)
        self.assertAlmostEqual(command["requested_m_s"], np.sqrt(2*0.5*9.81*0.02))
        with self.assertRaises(ValueError):
            coast(-1, 1, 9.81, 0.2, [0, 1])


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_collection_counts_roles_and_reproducible_order(self):
        p, q = self.root / "p.csv", self.root / "q.csv"
        self.assertEqual(collection_schedule(p, CONFIG, 10), 450)
        collection_schedule(q, CONFIG, 10)
        self.assertEqual(p.read_bytes(), q.read_bytes())
        with p.open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(sum(r["role"] == "query" for r in rows), 160)
        self.assertEqual(sum(r["role"] == "brief_and_extended_support" for r in rows), 10)

    def test_real_gate_and_confirmation_boundary(self):
        manifest = generate(self.root / "d", CONFIG, 4)
        body = json.loads(manifest.read_text())
        body["source_kind"] = "real"
        manifest.write_text(json.dumps(body))
        with self.assertRaisesRegex(ValueError, "Measurement gate"):
            load_dataset(manifest)
        body["cohort"] = "confirmation"
        manifest.write_text(json.dumps(body))
        with self.assertRaisesRegex(ValueError, "only opens pilot"):
            load_dataset(manifest)

    def test_input_integrity_and_missing_trial(self):
        manifest = generate(self.root / "d", CONFIG, 4)
        trials, _, _ = load_dataset(manifest)
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            allocate(trials[1:], CONFIG)
        file = manifest.parent / json.loads(manifest.read_text())["trials"][0]["path"]
        with file.open("ab") as f:
            f.write(b"tamper")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            load_dataset(manifest)

    def test_csv_calibration_and_provenance(self):
        source = self.root / "raw.csv"
        source.write_text("time_s,normal_raw,tangential_raw,velocity_mm_s,acceleration_m_s2\n0,2,1,150,3\n0.001,2,1,150,4\n")
        cal = ROOT / "templates/calibration.json"
        output = self.root / "calibrated.npz"
        provenance = import_csv(source, cal, output)
        with np.load(output) as data:
            np.testing.assert_allclose(data["velocity_m_s"], 0.15)
            np.testing.assert_allclose(data["tangential_force_n"], -1)
        self.assertEqual(provenance["source_sha256"], digest(source))
        with self.assertRaises(FileExistsError):
            import_csv(source, cal, output)

    def test_end_to_end_pilot_and_held_query_invariance(self):
        manifest = generate(self.root / "d", CONFIG, 4)
        config_path = ROOT / "configs/pilot.json"
        first = evaluate_pilot(manifest, config_path, self.root / "r1")
        self.assertFalse(first["physical_claims_allowed"])
        self.assertLess(first["means_n"]["B1"], first["means_n"]["B0"])
        episodes = json.loads((self.root / "r1/episodes.json").read_text())
        for episode in episodes:
            self.assertNotIn(episode["held_out_group"], episode["training_groups"])
            self.assertEqual(len(episode["query_trials"]), 16)
            self.assertFalse(set(episode["query_trials"]) & set(episode["extended_trials"]))
        body = json.loads(manifest.read_text())
        held = body["trials"][0]["group_id"]
        # Change only the held group's query labels. Its fitted parameters must not change.
        for row in body["trials"]:
            if row["group_id"] == held and row["repetition"] >= 3:
                file = manifest.parent / row["path"]
                with np.load(file) as data:
                    arrays = {k: data[k].copy() for k in data.files}
                arrays["tangential_force_n"] -= 2
                np.savez_compressed(file, **arrays)
                row["sha256"] = digest(file)
        manifest.write_text(json.dumps(body))
        evaluate_pilot(manifest, config_path, self.root / "r2")
        def fitted(folder):
            with (self.root / folder / "predictions.csv").open(newline="") as f:
                return [(r["trial_id"], r["method"], r["estimated_mu"]) for r in csv.DictReader(f)
                        if r["group_id"] == held]
        self.assertEqual(fitted("r1"), fitted("r2"))


if __name__ == "__main__":
    unittest.main()
