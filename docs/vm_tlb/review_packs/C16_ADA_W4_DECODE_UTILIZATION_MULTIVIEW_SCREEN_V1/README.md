# C16 Ada W4 decode utilization multiview screen

## Outcome

**PASS / STOP after one surviving question.** Batch-1 Qwen2.5-7B AWQ decode on the accepted RTX 4080 path is not adequately described by one memory-bound, compute-bound, or SM-utilization label. The W4 projections combine 6.25% useful M-tile fill with role-dependent CTA supply, measured long-scoreboard exposure, and measured cache/DRAM service. Small reduction, elementwise, and attention-combine kernels are primarily geometry/launch-granularity limited, but their whole-decode weights are small.

Only gate/up sibling concurrency remains worth validating. Its legal no-contention ceiling is 7.8931% of whole decode and the existing headroom consumer already published the minimal 109 contract. This screen creates no new contract and runs no GPU work.

## Read order

1. `ADA_W4_KERNEL_GEOMETRY.tsv`
2. `UTILIZATION_MULTIVIEW.tsv`
3. `ORACLE_HEADROOM.tsv`
4. `STRONG_KERNEL_NEIGHBOR_AUDIT.md`
5. `TOP_TWO_REMAINING_PROBLEMS.md`
6. `FINAL_DECISION.json`

## Method boundary

The eight-view principle is adapted from arXiv:2609.12923, but no H100, GMMA m64, 132-SM, occupancy, stall, or throughput number is transferred. Ada facts come from the accepted AutoAWQ source, accepted RTX 4080 launch records, and existing NCU/timeline authorities.

`active_warps_per_SM_equivalent` is the accepted NCU achieved-occupancy percentage multiplied by NVIDIA's 48-warp Ada architectural ceiling. It is a measured warp-equivalent under the NCU metric's denominator, not a resource ceiling or a spatial chip average. Resource-limited occupancy stays `UNKNOWN` because the accepted NCU set lacks occupancy-limiter counters; registers/shared-memory are not silently converted through undocumented allocation granularities.

Service bytes in `UTILIZATION_MULTIVIEW.tsv` are exact per-kernel rows from the `CONTROL_GUD84`, layer-0, D3, BASE NCU profiles. Kernel durations and gaps are independent means over 112 calls in the accepted formal timeline. These denominators are stated rather than blended.

The M1/M256 semantic NCU authority is used as a kernel-selection guard: RAW FP16 changes from GEMV at M1 to CUTLASS GEMM at M256, whereas AWQ keeps `m16n128k32`; AWQ L1/L2 traffic rises from 46.83/40.92 MB at M1 to 1294.86/1159.10 MB at M256. Cache state makes DRAM totals non-comparable across unrelated profiles, so no cross-profile DRAM causal claim is made.

## Provenance

- Formal timeline producer: `071297ae7f4aa772a27fae0cf31ad47ab7d967be`.
- FFN headroom consumer: `30b3016a7ad5b5ef86a3494c784e072938dee6c5`.
- Accepted AutoAWQ source: `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`, blob `98f49efac8626388039912e6aabc8a84d9f8303b`.
- E1 semantic NCU V2 consumer: `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`.
- Existing operator-family, split1/split8, grouped/swizzled and launch authorities are consumed from the repository review packs; none is rerun.
