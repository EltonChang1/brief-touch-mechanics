# Can a Short Touch Predict a Slide?



## Goal

Use **0.5 seconds of sliding observation on an unseen surface** to estimate friction and predict forces during later, independent slides. Compare this adaptation with one global friction setting, and test whether tactile vibrations add useful information beyond forces or known conditions. If force prediction succeeds, validate stopping distance and a robot slide-to-target task.

The proposed primary target is at least **25% lower force error**. This remains a draft target to finalize before physical confirmation.

## What we have done

- Built calibrated CSV ingestion with explicit units, force signs and provenance; implemented eight force methods and controls with whole-surface holdouts and paired uncertainty estimates.
- Prepared a **450-trial collection schedule** for 10 planned groups, three speeds, three loads and five repetitions. Physical collection has not started.
- Ran the full pipeline on synthetic contacts and implemented analytical coasting, stopping and bounded release-speed calculations.
- Audited a bounded official Penn Haptic Texture Toolkit (HaTT) subset and verified **16 automated tests** covering data integrity, inference boundaries, calibration conversion and dynamics.

## Results

### Synthetic force prediction

The software exercise used **450 generated trials, 10 held-out groups and 160 query trials**. Each method scored the same queries; lower mean absolute error (MAE) is better.

| Method | Force MAE (N) |
| --- | ---: |
| B0: one global friction coefficient | 0.51308 |
| B1: direct 0.5-second force estimate | **0.00658** |
| B2: conditions-only regression | 0.51308 |
| T1: tactile + conditions regression | 0.04403 |
| B3: force + conditions regression | 0.11361 |
| T2: force + tactile + conditions regression | 0.05594 |
| R: extended force calibration | 0.00655 |
| T1 with wrong-surface support | 0.32441 |

B1 reduced error by **98.7%** against B0 and nearly matched extended calibration. Tactile inputs improved their matched regressions: **91.4%** for T1 versus B2 and **50.8%** for T2 versus B3. The simple B1 estimate still outperformed both tactile methods.

**These are software-check results.** The generator deliberately encodes friction in vibration amplitude. The scores establish pipeline operation on that toy problem; real force accuracy, tactile benefit, motion prediction and robot-task utility remain untested. Full scores, intervals, predictions and provenance are in the [execution report](docs/execution-report.md) and [saved synthetic results](docs/results/synthetic-pilot-v1/summary.json).

### Real-data access audit

The HaTT archive index contains **100 surface folders**. We inspected **nine files from ABS Plastic, Aluminum and Book**: force, acceleration and motion channels, each with 100,000 finite samples and a declared stored rate of 10 kHz. Access and schema checks passed. Native timing, calibration, force conventions, independent trials and verified sliding remain unresolved, so **no HaTT force benchmark has been scored**. The [saved audit](docs/results/hatt-audit/audit.json) contains metadata and hashes; restricted raw recordings remain outside Git.

## Next step

Pass the physical measurement gate using calibrated, synchronized force/tactile/motion recordings and verified sliding. Then run the real force pilot, freeze confirmation rules, and progress to independent free-motion and task validation.

See the [run guide](docs/running-experiment.md), [experiment plan](docs/experiment-plan.md), [methods and research review](docs/methods.md), and [origin note](docs/origin.md).
