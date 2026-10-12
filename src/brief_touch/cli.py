"""Command-line entry points for audit, collection preparation and software checks."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .data import load_dataset
from .evaluation import allocate, evaluate_pilot
from .ingestion import import_csv
from .synthetic import generate


def collection_schedule(path, config, group_count):
    if group_count < 1:
        raise ValueError("At least one planned surface group required")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ref = config["reference_speed_m_s"], config["reference_load_n"]
    rows = []
    for group in range(group_count):
        for speed in config["speeds_m_s"]:
            for load in config["loads_n"]:
                for rep in range(config["repetitions"]):
                    role = "extended_support" if rep < 3 else "query" if (speed, load) != ref else "repeatability"
                    if rep == 0 and (speed, load) == ref:
                        role = "brief_and_extended_support"
                    rows.append({"group_id": f"planned-{group+1:02d}", "speed_m_s": speed,
                                 "load_n": load, "repetition": rep, "role": role,
                                 "trial_id": f"G{group+1:02d}-v{speed:g}-n{load:g}-r{rep}",
                                 "status": "planned", "session_id": "", "pad_id": "",
                                 "calibration_id": "", "contact_location": "", "raw_path": ""})
    # Block by group/speed/load; randomize role order inside each workable condition.
    rng = np.random.default_rng(config["seed"])
    ordered = []
    for start in range(0, len(rows), config["repetitions"]):
        block = rows[start:start+config["repetitions"]]
        rng.shuffle(block)
        ordered.extend(block)
    for i, row in enumerate(ordered):
        row["acquisition_order"] = i + 1
    with path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ordered[0]))
        writer.writeheader()
        writer.writerows(ordered)
    return len(ordered)


def main():
    parser = argparse.ArgumentParser(prog="brief-touch")
    parser.add_argument("--config", type=Path, default=Path("configs/pilot.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Generate synthetic contacts and exercise all force methods")
    demo.add_argument("--out", type=Path, required=True)
    demo.add_argument("--groups", type=int, default=10)
    collect = sub.add_parser("prepare-collection", help="Write a planned, uncollected trial schedule")
    collect.add_argument("--out", type=Path, required=True)
    collect.add_argument("--groups", type=int, default=10)
    audit = sub.add_parser("audit", help="Validate local pilot measurement contract and trial allocation")
    audit.add_argument("manifest", type=Path)
    evaluate = sub.add_parser("evaluate-pilot", help="Run whole-group exploratory force evaluation")
    evaluate.add_argument("manifest", type=Path)
    evaluate.add_argument("--out", type=Path, required=True)
    ingest = sub.add_parser("import-csv", help="Convert a CSV using explicit calibrated scales/signs")
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--calibration", type=Path, required=True)
    ingest.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.command == "prepare-collection":
        print(f"Prepared {collection_schedule(args.out, config, args.groups)} planned trials")
    elif args.command == "import-csv":
        print(json.dumps(import_csv(args.source, args.calibration, args.out), indent=2))
    elif args.command == "audit":
        trials, manifest, hashes = load_dataset(args.manifest)
        groups = allocate(trials, config)
        print(json.dumps({"trials": len(trials), "groups": len(groups), "source_kind": manifest["source_kind"],
                          "inputs_hashed": len(hashes), "status": "software contract validated"}, indent=2))
    else:
        if args.command == "demo":
            manifest = generate(args.out / "data", config, args.groups)
            report = evaluate_pilot(manifest, args.config, args.out / "evaluation")
        else:
            report = evaluate_pilot(args.manifest, args.config, args.out)
        print(report["interpretation"])
        print(json.dumps(report["means_n"], indent=2))


if __name__ == "__main__":
    main()
