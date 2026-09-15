# Current simulation entry points

This is a code-level inventory; no simulator was launched.

| Stage | Entry point | Evidence-backed contract | Today |
|---|---|---|---|
| Trace replay/conversion | `util/vm_tlb/run_m4c_replay.sh` | accepts `--trace-list`, `--trace-dir`; list entries must match safe `*.traceg.xz`; creates symlinks and isolated `gpgpusim.config` | Not runnable in this fresh worktree: no executable `accel-sim.out` found. It becomes runnable only after a valid traceg list, binary, and roots are supplied; no C16 conversion is present |
| Historical C12 replay | `util/vm_tlb/c12_c5_replay.py` | matrix/command manifests bind old framework/core/binary/config/trace hashes; emits validation and summaries | Legacy/reference-only until old identities and `/workspace` layout are re-established |
| Simulator config | `M4C_*` and `M4B_*` overlays + Core `SM86_RTX3070` base/trace configs | launcher concatenates overlays; profile selects disabled/ideal/generic/paper/subentry/Segment | Current code path; configuration semantics need smoke validation |
| TLB/PTW extraction | `util/vm_tlb/export_m4c_telemetry.py` | parses simulator `m4c_telemetry*` records and writes L1/L2/queue/DRAM/cross-layer TSVs | Runnable only on a completed compatible log |
| Segment/Selective analysis | `analyze_m4c_trace_locality.py`; Segment map/configs | offline decoder computes page/cache-line footprints from traceg and object map; simulator Segment profile uses immutable map | Analyzer current; C16 inputs need conversion and range-order proof |
| Cache analysis | `c12_cache_behavior_checkpoint.py` (historical C12 logs) and exported M4C L1D/L2 tables | consumes telemetry log lines; emits hit/miss/reservation and replacement matrices | Historical extractor requires old logs; modern extractor is `export_m4c_telemetry.py` |
| Finalize/post-processing | `c12_c5_finalize.py`, `summarize_m4c_runs.py` | summarize validated run roots into TSV/MD | Finalizer legacy; summarizer current for modern run-dir schema |

The strongest code-defined modern path is: valid `traceg.xz` list + trace directory + separately built simulator → `run_m4c_replay.sh` → simulator log/RUN_MANIFEST → `export_m4c_telemetry.py` → `summarize_m4c_runs.py`. It is not runnable today in this fresh worktree because no executable simulator is present. No run was performed in this inventory.
