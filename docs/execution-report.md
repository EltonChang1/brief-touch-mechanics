# Execution report

**Updated: 12 October 2026.** This report covers every completed result in this repository: the synthetic force pilot, analytical/software checks, and the bounded HaTT access/schema audit.

**Status: implementation and source audit executed; physical measurement gate remains open. No real force-prediction, movement or robot-task result is claimed.**

## What was completed

| Plan item | Executed work | Status |
| --- | --- | --- |
| Source/rig access audit | Inspected this repository and neighboring project documentation; located and fetched a bounded official HaTT subset | Source access established; rig capability unconfirmed |
| Channel audit | Parsed nine real XML files from three development surfaces; checked counts, units, finite values, ZIP CRCs and SHA-256 hashes | File/schema checks complete |
| Collection preparation | Generated 450 planned force trials with explicit support/query roles and randomized repetition order | Ready to assign actual groups and sessions |
| Ingestion | Implemented explicit calibration/sign/unit conversion with raw/calibration provenance hashes | Software implemented; bench coefficients unavailable |
| Baselines and tactile comparisons | Implemented B0/B1, matched B2/T1 and B3/T2 regressions, R and wrong-surface control | Ran on synthetic contacts |
| Grouped pilot evaluation | Whole-group holdouts, fixed support crops, common queries, paired bootstrap intervals and input-integrity checks | Ran on synthetic contacts |
| Motion primitives | Exact coasting, non-reversing stop, no-stop penalty and bounded release-speed planner | Analytical checks pass |
| Confirmation, engine and robot task | Requires measured pilot variability, frozen protocol and real free-motion capability | Not started; prerequisites not met |

## Actual HaTT findings

The [official UPenn record](https://repository.upenn.edu/items/c1b8168b-b8a7-4f22-9e38-6430c233a600) exposes the recorded-model archive through its public REST API. Direct fetches succeeded even though the web reading tool returned an error for the manual. No mirror or third-party rendering code was used.

The archive index contains **300 entries: three modality XML files for each of 100 surface folders**. Only **ABS Plastic, Aluminum and Book** source signals were opened in this pass. These are development exposures; no confirmation cohort was opened.

The downloaded nine files total **120,219,419 uncompressed bytes**. Each inspected numeric channel has **100,000 finite values**. Their metadata declares a common stored sample rate of **10,000 Hz**. This describes the stored files; it does not establish acquisition bandwidth or synchronization.

| Modality | Verified file fields | Declared units |
| --- | --- | --- |
| Acceleration | Combined signal and x/y/z axes | m/s² |
| Force | Normal, tangential and x/y/z forces | N |
| Motion | Speed and x/y/z position | mm/s and mm |

Normal force minima reach below the proposed 0.2 N support threshold for Aluminum and Book, and the tangential fields contain both signs. These facts require explicit validity/sign analysis; the importer must not silently take absolute values or declare the entire trace steady sliding.

The model archive supplies one aligned-length modality set per inspected surface folder, rather than the controlled 45-trial grid. The separate friction archive's measurement/trial relationships were not audited. A shared sample count is not evidence of independent trials or common native timing.

Unresolved requirements are **native channel rates, timing offset/drift/filter delays, force calibration and uncertainty, force-frame conventions, independent trial relationships and actual sliding verification**. This subset therefore does not pass the physical measurement gate or the controlled-pilot allocation. An offline protocol would need to be revised and frozen before any force benchmark is scored.

The metadata-only [audit](results/hatt-audit/audit.json), [archive index](results/hatt-audit/archive-index.json), and [provenance](results/hatt-audit/provenance.json) are saved in Git. Raw source files and the original license and manual remain under ignored `data/hatt-audit/`. The source license restricts use to nonprofit research and limits redistribution; raw source bytes have not been added to Git. Source attribution and any required research-use feedback remain responsibilities of the experiment owner under the [original notice](https://repository.upenn.edu/bitstreams/c3c70778-1c6e-412b-8e99-8c5e57aa7a33/download).

Source attribution: Heather Culbertson, Juan Jose Lopez Delgado, and Katherine J. Kuchenbecker, *One Hundred Data-Driven Haptic Texture Models and Open-Source Methods for Rendering on 3D Objects*, IEEE Haptics Symposium, 2014.

The neighboring vibration study uses Cluster recordings without per-scan tangential-force targets for this protocol. Its reserved signals were not opened. The neighboring data toolkit and collection standard provide tooling/proposals, not verified measurements for this experiment.

## Synthetic force-pilot results

The full synthetic exercise ran **450 trials across 10 groups**, with **16 common query trials per held-out group**: 160 unique query trials and 1,280 prediction rows across eight methods. Each fold trained on the other nine groups. The grid used speeds of 0.05, 0.15 and 0.30 m/s, loads of 1, 2 and 4 N, and five repetitions. Brief support was 0.5 seconds at 0.15 m/s and 2 N; the extended reference used 27 support trials, totaling 13.5 seconds of scored support windows. Those budgets exclude approach, settling and total collection travel.

Force MAE is averaged equally over query conditions and held-out groups. Query predictions use nominal commanded conditions, without future measured load or speed.

| Method | New-group inference inputs | Mean force MAE (N) |
| --- | --- | ---: |
| B0: global friction | No new-group support | 0.513079 |
| B1: direct brief force fit | Brief force and motion readings | **0.006578** |
| B2: conditions-only regression | Brief declared conditions | 0.513080 |
| T1: tactile regression | Brief tactile readings + conditions; support forces hidden | 0.044030 |
| B3: force regression | Brief force features + conditions | 0.113606 |
| T2: force/tactile regression | Brief force + tactile features + conditions | 0.055940 |
| R: extended force calibration | 27 support trials over nine conditions | 0.006548 |
| T1 wrong-surface control | Another group's brief tactile support at matched conditions | 0.324409 |

Positive improvement below means lower MAE than the comparison baseline. Intervals use 2,000 paired bootstrap resamples of the ten saved group scores, with seed 20261010. They are exploratory software diagnostics and do not refit training models or capture training-set variability.

| Comparison | MAE improvement (N) | Relative error reduction | Paired group-bootstrap 95% interval (N) |
| --- | ---: | ---: | --- |
| B1 versus B0 | 0.506501 | 98.7% | [0.321751, 0.691158] |
| T1 versus B2 | 0.469050 | 91.4% | [0.298288, 0.632908] |
| T2 versus B3 | 0.057666 | 50.8% | [0.006969, 0.109438] |
| T2 versus B1 | -0.049362 | Higher error | [-0.075292, -0.029174] |

The direct brief force estimate nearly matched extended calibration and outperformed both tactile regressions. Tactile inputs helped their matched regression comparisons, while swapping to wrong-surface support increased T1 error. **The generator deliberately encodes friction into vibration amplitude**, so these findings demonstrate operation on a designed toy problem. They do not establish real material behavior, tactile benefit or robotics usefulness.

The saved `provisional_primary_targets_met: true` flag applies only to this synthetic check: B1 cleared the draft 25% relative improvement, 0.02 N absolute improvement, 0.10 N MAE and positive-interval checks. Physical success targets remain provisional and unmet by real measurements.

## Software verification and saved evidence

**16 automated tests pass**, covering support boundaries and future-signal invariance, hidden-force tactile inputs, force sign and low-speed rejection, native feature bandwidth, equal group weighting, independent holdouts, query-label perturbation, missing trials, raw integrity, real-data evidence gates, confirmation exclusion, unit conversion, provenance, analytical stops, zero friction, failure penalties and launch limits.

On 12 October 2026, all **452 recorded input hashes** and **eight source-code hashes** matched the verified run. A fresh evaluation reproduced its means, comparisons and group scores exactly, and reproduced predictions and episode assignments byte for byte. The initial and verified runs have the same scores; the verified run adds provenance and is the published snapshot.

Machine-readable results are saved in Git:

- [Synthetic summary](results/synthetic-pilot-v1/summary.json): all method and group scores, paired intervals, configuration, runtime versions, input/source-code hashes, `source_kind: synthetic` and `physical_claims_allowed: false`.
- [Query predictions](results/synthetic-pilot-v1/predictions.csv) and [episode assignments](results/synthetic-pilot-v1/episodes.json): every scored query, method estimate and whole-group split.
- [Snapshot provenance](results/synthetic-pilot-v1/provenance.json): original/output digests, reproduction checks and initial-run equivalence. Summary input paths were made repository-relative; values and hashes are unchanged.
- [HaTT audit](results/hatt-audit/audit.json), [archive index](results/hatt-audit/archive-index.json), and [audit provenance](results/hatt-audit/provenance.json): access/schema findings and source integrity metadata. All nine cached XML files matched their recorded hashes, sizes and CRCs.

Reproduction commands and the real-data contract are in [running the experiment](running-experiment.md). Original synthetic runs remain under ignored `runs/synthetic-pilot-v1/`; restricted HaTT recordings remain under ignored `data/`. The tracked [results index](results/README.md) explains the snapshot layout. There are no completed real-force, engine, free-motion or robot-task benchmark outputs.

## Next dependency

Provide either an accessible calibrated slide/robot rig and its channel details, or recorded force/tactile/motion trials with calibration/timing evidence. The physical calibration and repeatability phase can then proceed. Until those measurements exist, it would be misleading to execute confirmation, claim a tactile advantage, or present synthetic motion as real-world validation.
