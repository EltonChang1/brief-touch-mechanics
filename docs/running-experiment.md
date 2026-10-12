# Run the experiment software

The implemented runner covers the controlled **force pilot** and analytical one-dimensional motion checks. It does not collect hardware data, open confirmation cohorts, or establish real motion/task results. The [execution report](execution-report.md) records what has actually run.

The [saved result snapshots](results/README.md) contain the completed synthetic scores, per-query predictions, holdout assignments and HaTT audit metadata. They can be inspected directly after cloning; raw recordings and generated run directories remain ignored.

## Install and verify

From this repository in PowerShell:

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -e .
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Use `uv lock` / `uv sync` if you prefer the checked-in lockfile. NumPy is the only runtime dependency. The tests use Python's standard-library unittest.

## Reproduce the software exercise

```powershell
.venv\Scripts\brief-touch.exe demo --out runs\my-synthetic-check
.venv\Scripts\brief-touch.exe audit runs\my-synthetic-check\data\manifest.json
```

Output directories must be new; runs are not overwritten. The demo generates 450 toy trials with deliberately identifiable Coulomb coefficients. It evaluates B0, B1, B2, B3, T1, T2, the extended calibration R, and a wrong-surface tactile control. Its scores test software operation, not real material behavior or robotics usefulness.

Each evaluation saves:

- `summary.json`: source type, group-level force errors, paired group-bootstrap intervals, draft target checks, input/source-code hashes and runtime versions. Pilot intervals are exploratory and do not refit training models in each bootstrap.
- `predictions.csv`: each query's estimated coefficient, commanded-condition force prediction and scored error.
- `episodes.json`: whole-group train/holdout membership and explicit brief, extended and query trial IDs.

The published [verified summary](results/synthetic-pilot-v1/summary.json), [predictions](results/synthetic-pilot-v1/predictions.csv) and [episodes](results/synthetic-pilot-v1/episodes.json) came from the default ten-group configuration. Compare numerical scores and episode assignments when reproducing the run. Input paths change with the output directory, and generated NPZ file hashes may differ with archive metadata/runtime versions; the snapshot preserves the original inputs' hashes. [Snapshot provenance](results/synthetic-pilot-v1/provenance.json) records an exact reevaluation of those original inputs on 12 October 2026.

Ridge regularization and spectral bands are fixed in the pilot config. No outer-fold query score selects features or hyperparameters. Query force labels enter scoring after that group's estimators are fitted. B0 uses no new-surface support; force/tactile interfaces remain distinct. The wrong-surface control is a secondary diagnostic, never training input or a selected replacement.

## Audit the official HaTT source

```powershell
.venv\Scripts\python.exe tools\audit_hatt.py
```

This downloads only the declared development specimens **ABS Plastic, Aluminum and Book**, using range requests to the official UPenn archive. It preserves the license and manual, checks extracted ZIP lengths and CRCs, hashes raw files, and reports XML channel counts, units and extrema. Repeated runs verify cached source bytes.

Raw HaTT files and the original notices stay in ignored `data/hatt-audit/`. Do not redistribute them as repository assets. The [official license](https://repository.upenn.edu/bitstreams/c3c70778-1c6e-412b-8e99-8c5e57aa7a33/download) governs use and attribution. The audit is an access/schema check; it does not approve native rates, calibration, timing or steady sliding. No HaTT force benchmark has been scored.

The metadata-only [saved audit](results/hatt-audit/audit.json), [archive index](results/hatt-audit/archive-index.json) and [provenance](results/hatt-audit/provenance.json) preserve the completed findings in Git without copying restricted source files.

## Prepare real collection

The generated [450-trial schedule](../configs/pilot-collection.csv) contains planned rows and randomized repetition order within each group/speed/load block. Its group IDs are placeholders: assign actual independent specimens/manufacturing groups before collection. Follow the plan's session blocking and spread repetitions across sessions where practical; acquire only after calibration passes.

To generate a separate schedule:

```powershell
.venv\Scripts\brief-touch.exe prepare-collection --out configs\another-pilot.csv --groups 10
```

Record pad, session, calibration, contact location, raw file and acquisition order. The runner currently requires one specimen per independent group, a complete nine-condition/five-repeat grid, and one pad throughout. Missing cells or duplicate coupons require an explicitly revised allocation, rather than automatic omission.

## Ingest calibrated recordings

Keep original CSV logs immutable. Copy and fill [the calibration template](../templates/calibration.json) with measured matrix/bias, actual force-frame convention, column mappings and unit conversions. Its identity/sign example is not a bench calibration.

```powershell
.venv\Scripts\brief-touch.exe import-csv data\raw\trial.csv --calibration data\calibration\bench.json --out data\pilot\trial.npz
```

The converter writes an NPZ and a provenance sidecar with source/calibration/output SHA-256 digests. It refuses overwrite. It does not infer time offsets, resample channels, certify sliding or turn template coefficients into verified calibration. It expects already aligned channels; preserve acquisition-rate/timing evidence separately.

The initial data contract requires scalar, uniformly sampled, finite channels:

| NPZ key | Units / convention |
| --- | --- |
| `time_s` | Common verified time base, seconds |
| `normal_force_n` | Normal contact load, N |
| `tangential_force_n` | Force on the moving body, N |
| `velocity_m_s` | Signed actual interface sliding velocity, m/s |
| `tactile_m_s2` | Declared accelerometer channel, m/s² |

This first implementation supports one acceleration channel. Other tactile modalities need a separately declared feature/units adapter; arbitrary tactile images cannot be loaded as acceleration. Different native channel rates require a verified alignment/resampling adapter before this uniform-rate contract, with native tactile bandwidth retained in the feature checks.

A real manifest follows the generated synthetic manifest's structure, but sets `source_kind` to `real`. Every trial needs source hash, group/specimen/trial identities, nominal conditions, repetition, a predefined valid-window start, sample rate, sliding verification and pad/session/calibration IDs. Declare exact SI units and `force_frame: force_on_moving_body`.

Add four `measurement_evidence` entries: `force_calibration`, `timing_alignment`, `sliding_verification`, and `contact_geometry`. Each needs `status: verified`, a `path` relative to the manifest, and the evidence file's `sha256`. Fill the [measurement audit template](../templates/measurement-audit.json) from physical checks. The software verifies references and hashes; the experiment owner must establish the physical validity of those reports. A boolean or a hash is not metrological proof.

Only after that gate:

```powershell
.venv\Scripts\brief-touch.exe audit data\pilot\manifest.json
.venv\Scripts\brief-touch.exe evaluate-pilot data\pilot\manifest.json --out runs\real-force-pilot
```

The query predictor uses nominal commanded load/speed, not measured future force/load/velocity. Support is cropped to its allowed half-open interval before features. The default spectral bands require a sample rate of at least 800 Hz; use native tactile bandwidth to set valid bands before confirmation.

## Motion and later gates

`brief_touch.dynamics` exposes `coast`, `stop_error`, and `release_speed` for physical-unit rollouts, explicit failure penalties and bounded launch commands. These functions consume initial state and physical parameters, not future measured trajectories. They are analytically verified software primitives, not a real movement benchmark.

Complete the force pilot, choose a confirmation sample size, and freeze the protocol before building a confirmation runner. Real motion acquisition, an engine adapter and robot control remain later gated work. The current runner explicitly rejects `cohort: confirmation` so development cannot silently score reserved data.
