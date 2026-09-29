# C16 Grouped Residual Parallelism Native — Lane 7

Task: `C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1`

Status: complete.  Final decision:
`LOW_CTA_SUPPLY_RESIDUAL_WITH_M64_CROSSOVER`.

Lane 8 gate commit `f6bad36a0ee49e718df268421e96593c94756b77` published
`READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN`; every bound SHA verified before
GPU use.  The single lock interval was `2026-09-29T05:16:29Z` through
`2026-09-29T05:16:51Z`, exited zero, and released normally.

Frozen matrix: `K=4096`, `N=12288`, `M={1,16,32,64}`, `split={8,1}`,
mapping `GROUP_FULL_M`.

Split8 was 55.9%, 46.6%, and 21.4% faster at M1/M16/M32, but split1 became
4.93% faster at M64.  Split1 L2 read hit remained 100% at every point.  NCU
launch waves and active-warps measurements rose with CTA supply and corroborate
the launch-level proxy.  The residual is therefore a low-CTA-supply / partial
tile / reduction tradeoff, not a cache-capacity mechanism.

Recommended reading: `SOURCE_AND_GATE.json`, `METRIC_SELECTION.json`,
`CORRECTNESS.tsv`, `LAUNCH_AUDIT.tsv`, `RESIDUAL_PARALLELISM_SUMMARY.tsv`, and
`SCIENTIFIC_INTERPRETATION.md`.

No Lane 4 partial result was accessed.  No GROUP_M/split/shape sweep, replica,
EVICT, SASS capture, or Accel-Sim run was added.
