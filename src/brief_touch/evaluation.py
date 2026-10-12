"""Whole-group pilot evaluation with common queries and training-only estimators."""

import csv
import json
from pathlib import Path
import platform

import numpy as np

from .data import digest, load_dataset, verify_unchanged
from . import __version__
from .models import Ridge, features, fit_coulomb, fit_global, predict_force


def allocate(trials, config):
    groups = {}
    expected = {(s, n, r) for s in config["speeds_m_s"] for n in config["loads_n"]
                for r in range(config["repetitions"])}
    ref = config["reference_speed_m_s"], config["reference_load_n"]
    for trial in trials:
        groups.setdefault(trial.group_id, []).append(trial)
    if len(groups) < 4:
        raise ValueError("Grouped learned pilot requires at least four independent groups")
    allocation = {}
    for group, items in sorted(groups.items()):
        # One planned specimen per group in v0.1; duplicate coupons need explicit episode allocation.
        actual = [(t.speed_m_s, t.load_n, t.repetition) for t in items]
        if len(actual) != len(expected) or set(actual) != expected:
            raise ValueError(f"Incomplete or duplicated controlled trial grid for {group}")
        if len({t.specimen_id for t in items}) != 1:
            raise ValueError("v0.1 allocation expects one specimen per independent group")
        windows = [t.window(config["support_seconds"]) for t in items]
        support = next(t for t in windows if t.condition == ref and t.repetition == 0)
        extended = [t for t in windows if t.repetition < 3]
        query = [t for t in windows if t.condition != ref and t.repetition >= 3]
        allocation[group] = {"support": support, "extended": extended, "query": query,
                             "training": windows}
    return allocation


def paired_summary(group_scores, config):
    groups = sorted(group_scores)
    methods = list(group_scores[groups[0]])
    summary = {"means_n": {m: float(np.mean([group_scores[g][m] for g in groups])) for m in methods},
               "independent_groups": len(groups), "comparisons": {}}
    rng = np.random.default_rng(config["seed"])
    indices = rng.integers(0, len(groups), (config["bootstrap_repetitions"], len(groups)))
    for method, baseline in [("B1", "B0"), ("T1", "B2"), ("T2", "B3"), ("T2", "B1")]:
        difference = np.asarray([group_scores[g][baseline] - group_scores[g][method] for g in groups])
        low, high = np.quantile(difference[indices].mean(axis=1), [0.025, 0.975])
        base = summary["means_n"][baseline]
        summary["comparisons"][f"{method}_vs_{baseline}"] = {
            "improvement_n": float(difference.mean()),
            "relative_improvement": float(difference.mean() / base) if base > 0 else None,
            "paired_group_bootstrap_95_ci_n": [float(low), float(high)]}
    primary = summary["comparisons"]["B1_vs_B0"]
    relative = primary["relative_improvement"]
    summary["provisional_primary_targets_met"] = bool(
        relative is not None and relative >= config["force_relative_improvement_target"]
        and primary["improvement_n"] >= config["force_absolute_improvement_n"]
        and summary["means_n"]["B1"] <= config["force_mae_target_n"]
        and primary["paired_group_bootstrap_95_ci_n"][0] > 0)
    return summary


def evaluate_pilot(manifest_path, config_path, output):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if config["phase"] != "pilot" or config["repetitions"] != 5:
        raise ValueError("This runner supports the declared five-repeat pilot, not confirmation")
    trials, manifest, hashes = load_dataset(manifest_path)
    hashes[str(config_path)] = digest(config_path)
    allocation = allocate(trials, config)
    groups = list(allocation)
    tracks = {"B2": "conditions", "T1": "tactile", "B3": "force", "T2": "force_tactile"}
    predictions, scores, episodes = [], {}, []
    for held in groups:
        training = [g for g in groups if g != held]
        episode = allocation[held]
        kwargs = {"min_load": config["min_load_n"], "min_speed": config["min_sliding_speed_m_s"]}
        mus = {"B0": fit_global([allocation[g]["training"] for g in training], **kwargs),
               "B1": fit_coulomb([episode["support"]], **kwargs),
               "R": fit_coulomb(episode["extended"], **kwargs)}
        target = [fit_coulomb(allocation[g]["extended"], **kwargs) for g in training]
        models = {}
        for name, track in tracks.items():
            x = [features(allocation[g]["support"], track, config) for g in training]
            model = Ridge(config["ridge_alpha"]).fit(x, target)
            mus[name] = model.predict(features(episode["support"], track, config))
            models[name] = model
        wrong_group = groups[(groups.index(held) + 1) % len(groups)]
        mus["T1_wrong_surface"] = models["T1"].predict(features(allocation[wrong_group]["support"], "tactile", config))
        condition_errors = {name: {} for name in mus}
        # Query force labels are first consumed here, after support estimators are fitted.
        for query in episode["query"]:
            for name, mu in mus.items():
                force = predict_force(mu, query.speed_m_s, query.load_n)
                error = float(np.mean(np.abs(query.tangential - force)))
                condition_errors[name].setdefault(query.condition, []).append(error)
                predictions.append({"group_id": held, "trial_id": query.trial_id,
                                    "speed_m_s": query.speed_m_s, "load_n": query.load_n,
                                    "method": name, "estimated_mu": mu,
                                    "predicted_tangential_force_n": float(force), "mae_n": error})
        scores[held] = {name: float(np.mean([np.mean(v) for v in conditions.values()]))
                        for name, conditions in condition_errors.items()}
        episodes.append({"held_out_group": held, "training_groups": training,
                         "support_trial": episode["support"].trial_id,
                         "support_start_s": episode["support"].valid_start_s,
                         "support_seconds": config["support_seconds"],
                         "extended_trials": [t.trial_id for t in episode["extended"]],
                         "query_trials": [t.trial_id for t in episode["query"]]})
    verify_unchanged(hashes)
    report = paired_summary(scores, config)
    report.update({"source_kind": manifest["source_kind"], "phase": "pilot", "config": config,
                   "force_interface": "nominal commanded query conditions; no future measured load/speed",
                   "physical_claims_allowed": False,
                   "interpretation": "Synthetic software check only" if manifest["source_kind"] == "synthetic"
                   else "Exploratory force pilot; held-out confirmation and motion validation remain required",
                   "input_sha256": hashes, "per_group_mae_n": scores,
                   "software": {"brief_touch_version": __version__, "python": platform.python_version(),
                                "numpy": np.__version__,
                                "source_sha256": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))}},
                   "uncertainty_scope": "Exploratory group bootstrap of saved pilot scores; training-set variability is not refitted"})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    (output / "episodes.json").write_text(json.dumps(episodes, indent=2), encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    return report
