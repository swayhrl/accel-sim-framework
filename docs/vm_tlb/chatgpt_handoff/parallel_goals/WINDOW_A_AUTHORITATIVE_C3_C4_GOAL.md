# Window A — authoritative C3/C4 goal

Status: **AUTHORIZED AUTHORITATIVE GOAL**.

## Purpose

Continue the already-running formal M4C lineage without invalidating completed work. Finish the final C3 arm(s), close C3 at 8/8, execute C4 export/offline locality/baseline characterization, create a review pack, then STOP before C5.

## Frozen formal anchors

- Framework source: `a7c0759be7f293ed0d5e2179c62094b6de49c1e8`
- Core source: `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- Simulator binary SHA-256: `100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda`
- Core-local runtime SHA-256: `fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a`

Do not replace these with this coordination branch or any B/C branch.

## A0 — admission/resume

Read the current C3 supervisor/manifests/logs and determine the exact terminal state. If `prefill-paper` is already complete, do not restart it; validate the existing run and continue to A1. If still active, leave it untouched and monitor through the existing supervisor.

## A1 — C3 8/8 terminal closeout

For every arm require:

- `simulator_exit_status = 0`;
- `processing_kernel_markers` / started-kernel marker count equals immutable list count;
- telemetry-kernel-record count equals immutable list count;
- formal parser / `summarize_m4c_runs.py --require-level 2` gate PASS;
- VM/PTE/waiter/object conservation required by the profile;
- exact source/binary/config/list/object-map provenance.

Never use a `Processing kernel` marker count alone as proof of completion.

Correct the final documentation so the historical host-CUDA runtime attribution is explicitly superseded by direct Core-local `/proc/<pid>/maps` evidence. Do not rewrite existing formal `RUN_MANIFEST.tsv` files.

## A2 — C4 structured export

Use existing C3 logs only. No replay merely for export.

Produce provenance-bound structured outputs for at least:

- performance/cycles/IPC;
- global and object-specific L1/L2 TLB;
- MSHR/PWQ/walker/PWC/PTE/latency;
- L2-TLB incoming-object -> victim-object replacement;
- L1D object outcomes and pressure;
- data-L2/PTE request-class outcomes and replacement;
- L2 queue pressure;
- DRAM request-class totals;
- native global channel/bank/read/write/latency/row-locality;
- translation × L1D × L2 cross-layer matrices;
- per-kernel and `L1D_ACCESS_ATTEMPT_WINDOW` summaries.

Do not reinterpret `L1D_ACCESS_ATTEMPT_WINDOW` as a unique-coalesced-transaction window.

## A3 — offline immutable-trace locality

Run exact/offline analyses on the immutable trace/list/object maps. This work may shard by trace kernel because it does not rely on simulator state.

At minimum retain:

- unique 32B sectors;
- unique 128B lines;
- unique 64KB/2MB pages;
- requested bytes/references;
- object breakdown;
- hotness quantiles;
- per-kernel footprint;
- prior/cross-kernel overlap available from the accepted analyzer.

Window B may produce richer speculative offline analyses; A must not silently import them as formal C4 evidence. It may cite them separately after review.

## A4 — baseline characterization

Create machine-readable prefill/decode1 tables answering:

1. performance slowdown vs VM-disabled and ideal-identity controls;
2. L1/L2 TLB hit/miss and translation resource pressure;
3. Weight/KV/UNKNOWN shares, misses, walks, PTE traffic, latency;
4. L2-TLB replacement interference, especially non-weight -> Weight;
5. PTE/data L2 contention and data-L2 pollution evidence;
6. prefill vs decode1 differences;
7. generic-M3 vs paper-platform-shell differences;
8. cache/memory hierarchy context sufficient to distinguish translation bottlenecks from L1/L2/DRAM bottlenecks.

Separate measured fact, inference, paper comparison, and unknown.

## A5 — review pack and normal STOP

Create/update an authoritative review pack containing at least:

- `FORMAL_RUN_MATRIX.tsv`
- `BASELINE_CONFIG_MATRIX.tsv`
- `OBJECT_VM_STATS.tsv`
- `L2_TLB_REPLACEMENT_MATRIX.tsv`
- `LATENCY_SUMMARY.tsv`
- L1D/L2/DRAM structured tables required by the telemetry addendum
- `TRACE_LOCALITY_OFFLINE.tsv`
- `C3_CLOSEOUT.md`
- `CHARACTERIZATION_FINDINGS.md`
- `OPEN_ISSUES.md`
- raw-log index with hashes/paths, not raw logs in Git

Then update the Codex handoff report and STOP for ChatGPT review.

## Explicitly forbidden before STOP

- C5 sensitivity sweeps;
- M4B-P sub-entry experiments;
- M4B-S Segmentation experiments;
- synthetic KV / M5;
- use of B/C code/results as formal evidence without review.

## Problem-solving policy

Do not stop for ordinary exporter/parser/path/scratch/documentation issues. Diagnose, fix Framework-side tooling, validate against immutable existing logs, and continue. If a tooling fix changes only post-processing, never claim it changed the formal simulator run itself.
