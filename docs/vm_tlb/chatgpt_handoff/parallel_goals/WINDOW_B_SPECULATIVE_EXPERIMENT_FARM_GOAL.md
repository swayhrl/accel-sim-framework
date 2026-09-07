# Window B — speculative experiment farm goal

Status: **AUTHORIZED SPECULATIVE GOAL**.

## Purpose

Exploit the large host immediately for broad, parallel evidence gathering that does not alter Window A. Results are exploratory/speculative and may be rerun after A/C4 review.

## Recommended isolation

- Framework branch/worktree: `hrl/vm-spec-farm-v0` / `/workspace/worktrees/accel-sim-vm-spec-farm`
- Core branch/worktree: `hrl/vm-spec-farm-v0` / `/workspace/worktrees/gpgpu-sim-vm-spec-farm`
- Scratch root: `/workspace/vm-spec-farm/`

Core must start exactly from `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`.

Framework may start from the current parallel-handoff coordination head because the extra commits are docs-only relative to the accepted source. Record the exact branch point.

Never reuse Window A worktrees, build tree, active simulator binary, supervisor, or scratch.

## B0 — resource calibration and farm controller

1. Inventory CPU/physical-core/NUMA/RAM/storage topology.
2. Create a farm manifest/process registry.
3. Build/verify an isolated speculative simulator binary from the exact Core branch point.
4. Run bounded concurrency calibration at approximately 16/32/64/128 jobs, respecting `RESOURCE_AND_EXPERIMENT_FARM_POLICY.md`.
5. Freeze `FARM_CONCURRENCY_V1` at the observed throughput knee.
6. Implement automatic backpressure: if memory/I/O/authoritative-A pressure rises, reduce new-job launches rather than terminating the Goal.

Acceptance: reproducible launcher, unique scratch per run, no cross-window process interaction, no swap/resource hazard, stable concurrency cap.

## B1 — parallel immutable-trace mining

Shard by trace kernel/file with many workers. Do not run the timing simulator for metrics derivable from traces.

For all accepted compute-only prefill/decode1 kernels, produce reusable per-kernel/object metrics including:

- memory instructions and lane references;
- requested bytes;
- unique 32B sectors, 128B lines, 64KB pages, 2MB pages;
- WEIGHT/KV_CACHE/UNKNOWN breakdown;
- line/page hotness p50/p90/p99/max;
- load/store/atomic mix when decodable;
- stride/sequentiality summaries when exact decode supports them;
- page/line reuse summaries;
- kernel footprint.

Additionally produce cross-kernel/phase outputs:

- prior-kernel overlap;
- union working-set size over 1/4/16/64 consecutive kernels;
- Weight/KV/Unknown persistence/churn;
- translation reuse-distance or a clearly defined exact/approximate summary if computationally feasible;
- prefill vs decode1 footprint/working-set comparison.

Do not infer ACTIVITY/WORKSPACE classes not present in accepted metadata.

Acceptance: exact trace/list/object-map hashes bound, reducer conservation checks, deterministic rerun on a sample, no giant per-access Git artifact.

## B2 — broad VM one-factor-at-a-time sweeps

Use the accepted generic-M3 semantics and same real trace policy. Each `config × ROI` is one continuous simulator process.

Execute the matrix in `WINDOW_B_EXPERIMENT_MATRIX.md`:

- L1 TLB capacity;
- L2 TLB capacity;
- translation MSHR capacity;
- PWQ capacity;
- walker count;
- PWC capacity/mode;
- page-size diagnostics;
- ideal/no-translation controls.

Procedure:

1. bounded smoke for every generated config;
2. automatically fix local config/launcher errors and rerun the affected smoke;
3. after smoke passes, launch full decode1/prefill jobs subject to farm slots;
4. collect the same bounded memory-hierarchy telemetry where supported;
5. label every result `SPECULATIVE_DIAGNOSTIC` or `SPECULATIVE_CANDIDATE`.

Do not perform full Cartesian products in B2; vary one factor from the baseline at a time.

## B3 — L1/L2 cache exploratory sweeps

Run the cache matrix from `WINDOW_B_EXPERIMENT_MATRIX.md` while holding translation semantics fixed.

Validate every generated cache geometry from sets × line size × ways × partitions rather than trusting comments.

At minimum explore:

- L1D capacity;
- L2 capacity;
- L2 associativity;
- global-L1D bypass control;
- optional later TLB×L2 grid.

Collect TLB, L1D, L2, PTE/data contention, DRAM, and cross-layer telemetry so results can distinguish translation and cache bottlenecks.

## B4 — non-LLM translation controls

Inventory available compatible traces without touching DTC worktrees/processes. Select a diverse memory-intensive set, preferably including LUD, BFS, SpMV, GEMM and available PolyBench/other workloads where trace/config compatibility is proven.

For each selected workload run at least:

- generic baseline L2 TLB = 768;
- constrained L2 TLB = 256;
- expanded L2 TLB = 1536;
- ideal translation.

Use the same VM model/config family where semantically valid. Record trace provenance and reject incompatible ISA/config silently only after attempting a safe compatible path; do not mislabel mismatched traces as equivalent.

Goal: establish whether LLM translation working sets/interference/sensitivity differ materially from conventional workloads.

## B5 — optional TLB × L2 cache cross-product

After B2/B3 baseline rows exist and resources remain healthy, run:

- L2 TLB entries = 256 / 768 / 1536
- data L2 capacity = 1.5MB / 3MB / 6MB

for prefill and decode1 as independent continuous runs.

This 3×3 grid is allowed because it directly tests translation-capacity vs data-cache-capacity interaction. Do not expand to a large combinatorial design without evidence.

## B6 — speculative closeout

Create `docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/` with at least:

- `HOST_RESOURCE_INVENTORY.md`
- `FARM_CONCURRENCY_CALIBRATION.tsv`
- `RUN_REGISTRY.tsv`
- `TRACE_STATIC_KERNEL_STATS.tsv`
- `TRACE_REUSE_DISTANCE_SUMMARY.tsv` or explicit unavailable/approximate ledger
- `TRACE_KERNEL_WINDOW_WSS.tsv`
- `TRACE_CROSS_KERNEL_OVERLAP.tsv`
- `VM_SWEEP_RESULTS.tsv`
- `CACHE_SWEEP_RESULTS.tsv`
- `NON_LLM_COMPARISON.tsv`
- `TLB_L2_GRID.tsv` if run
- `SPECULATIVE_FINDINGS.md`
- `FAILED_OR_SUPERSEDED_RUNS.tsv`
- raw-log index with hashes/paths

`SPECULATIVE_FINDINGS.md` must separate measured facts, hypotheses, and candidates for formal rerun.

Normal STOP after B6. Do not merge into Window A.

## Problem-solving policy

Ordinary failures are to be solved. Examples: launcher race, stale scratch, config typo, parser exception, job crash, I/O saturation, NUMA imbalance, insufficient disk, one incompatible trace. Diagnose, repair, validate, and continue the Goal. Reduce concurrency or skip only an individually proven incompatible workload when a safe equivalent path does not exist; document why.
