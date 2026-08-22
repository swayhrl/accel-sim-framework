# V100-compatible extension status

Status timestamp: 2026-08-22.  This document is a state snapshot, not a
substitute for the final strict extension audit.

## Dataset identity and isolation

The eight entries in
[`configs/c2p-cache/v100_extension_workloads.tsv`](../configs/c2p-cache/v100_extension_workloads.tsv)
are V100-generated traces.  The manifest records each command/input, input
SHA-256 when applicable, trace archive filename, archive SHA-256, and the
`kernelslist.g` path.  Per-trace generation provenance is staged under
`hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage/<case>/<case>/provenance.json`.

All eight independent uncapped baselines have both a normal simulator exit and
a `summary.txt` in `hw_run/c2p-v100-baseline-full-v1-20260822`.  These facts
establish compatibility only; they do not make the extension a member of the
canonical paper16 aggregate.

The canonical paper16 report, figures, R/S classification, and strict audit
remain separately qualified in `hw_run/c2p-paper16-analysis-final-v7-20260821`.
No extension result is read by the paper16 analysis scripts.

## Matrix state

Each fully qualified extension case needs seven modes (`baseline`, `oracle`,
`ideal`, `c2p`, `ata`, `ccd`, `ring`) at each of L2=200 and L2=50: fourteen
points per case, 112 total.  The table reports only outputs suitable for the
eventual strict audit; stale outputs from the superseded scheduler race are not
credited.

| Case | L2=200 state | L2=50 state | Credited points | Notes |
|---|---|---|---:|---|
| `c2p-ispass-bfs` | primary clean root, all 7 | primary clean root, all 7 | 14 | independently checked point outputs |
| `c2p-ispass-lps` | primary clean root, all 7 | primary clean root, all 7 | 14 | independently checked point outputs |
| `c2p-ispass-ray` | primary clean root, all 7 | primary clean root, all 7 | 14 | independently checked point outputs |
| `c2p-pannotia-fw-block` | primary clean root, all 7 | primary clean root, all 7 | 14 | independently checked point outputs |
| `c2p-ispass-lib` | repair clean root, all 7 | repair clean root, all 7 | 14 | repair root is authoritative |
| `c2p-pannotia-mis` | baseline complete | baseline complete | 2 | `summary.txt` was extracted from each normal `run.out` with the runner's exact parser; controller remains stopped |
| `c2p-pannotia-color-max` | not started | not started | 0 | deliberate scheduling hold |
| `c2p-pannotia-pagerank` | not started | not started | 0 | deliberate scheduling hold |

Thus **72/112** matrix points have audited point outputs.  The two
`mis/baseline` simulations finished normally while their controllers were
stopped.  To preserve them without allowing the next mode to start, their
`summary.txt` files were generated with the exact AWK parser embedded in
`run_c2p_cache_cases.sh`; both output files retain the normal-exit marker.
Their controllers are still stopped and cannot launch `oracle`.

## Current gates and required closeout

The final verifier is `scripts/analyze_c2p_v100_extension.py --strict`.  Its
required evidence includes archive and trace provenance, uncapped baselines,
all mode contracts, normal exits, nonzero execution, Oracle/Baseline equality,
remote-hit/L2-avoid conservation, Ring backpressure constraints, and exact
disjointness from the 16 canonical paper cases.  It intentionally remains
pending until all 112 points exist.

The queue is on an explicit user-directed hold.  No new mode or case may be
started until approval; the two already-started `mis` baselines were allowed to
finish and are now complete.  The precise process and resume procedure are in
`hw_run/c2p-v100-extension-execution-hold-20260822.md`.
