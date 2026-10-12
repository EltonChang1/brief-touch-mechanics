# Saved result snapshots

Published on **12 October 2026**. The [execution report](../execution-report.md) interprets these results; the [run guide](../running-experiment.md) gives reproduction commands.

| Snapshot | Contents | Scope |
| --- | --- | --- |
| [Synthetic pilot](synthetic-pilot-v1/summary.json) | All eight method scores, per-group scores, paired intervals, configuration and input/source-code hashes | Software exercise only; no physical claims |
| [Predictions](synthetic-pilot-v1/predictions.csv) / [episodes](synthetic-pilot-v1/episodes.json) | 1,280 predictions for 160 queries; ten whole-group holdouts and their support/query assignments | Same verified synthetic run |
| [Synthetic provenance](synthetic-pilot-v1/provenance.json) | Original and exported output hashes, exact reproduction checks and initial-run equivalence | Summary paths normalized to repository-relative paths |
| [HaTT audit](hatt-audit/audit.json) / [archive index](hatt-audit/archive-index.json) | Nine-file channel audit, source hashes and 300-entry archive inventory | Access/schema check; physical measurement gate not passed |
| [HaTT provenance](hatt-audit/provenance.json) | Snapshot hashes, source attribution and cached-file integrity checks | Metadata only |

These are historical snapshots. Git attributes preserve snapshot bytes so recorded SHA-256 hashes survive cloning. Compare the saved source hashes with the code when reproducing them after future changes. The initial and verified synthetic evaluations had identical scores, so one verified result set is published. Synthetic signals and working runs remain ignored under `runs/`; HaTT XML recordings, toolkit code and source documentation remain ignored under `data/` under the original source license.
