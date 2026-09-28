# C16 Split-K Cross-M Reuse Causal Native — Lane 7

Task: `C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1`

Status: complete (`STRONG_SUPPORT_CROSS_M_WEIGHT_SIDE_REUSE`).  Lane 8 gate
commit `bc82d767c27e55c8bc06f5bf8830ccf752838d24` carried the exact decision
`READY_FOR_NATIVE_CAUSAL_SCREEN`; all bound SHAs were verified before GPU use.

Frozen matrix: `M=256`, `N=49152`, `K={2560,3072}`,
`split={8,1}`, `state={SHARED,PER_MTILE}`.  Every cell allocates sixteen
bit-identical weight-side replicas.  `SHARED` uses `replica_mask=0` and
`PER_MTILE` uses `replica_mask=15`; both states must use the same patched
extension binary and kernel path.

The scripts are deliberately split at the CUDA boundary:

- `scripts/crossm_contract.py` is standard-library-only and is safe before the gate.
- `scripts/build_isolated.sh` is only a recorded build recipe until the gate binds the source patch.
- `scripts/crossm_runner.py` imports Torch and the CUDA extension only in explicit GPU modes.

The single locked campaign ran from `2026-09-28T17:14:08Z` through
`2026-09-28T17:14:35Z`, returned zero, and released the lock.  All same-split
SHARED/PER_MTILE outputs were bitwise equal and both A/B comparisons passed the
frozen tolerance.  Each cell has 50 timing samples and one bounded NCU profile.

Key GEMM-only causal deltas (SHARED minus PER_MTILE hit rate) are 67.69 pp and
55.03 pp at K2560 for split8/split1, and 67.41 pp and 27.93 pp at K3072.
PER_MTILE/SHARED DRAM ratios are respectively 5.51x, 5.93x, 6.11x, and 1.77x.
Module timing ratios are 1.72x, 3.39x, 1.91x, and 2.59x.  Reduction rows are
kept separate and excluded from the weight-locality interpretation.

Recommended reading order:

1. `SOURCE_AND_GATE.json` and `BUILD_RECEIPT.json`
2. `CORRECTNESS.tsv`, `LAUNCH_AUDIT.tsv`, and `REPLICA_BINDINGS.tsv`
3. `REUSE_CAUSAL_SUMMARY.tsv` and `SCIENTIFIC_INTERPRETATION.md`
4. `RAW_INDEX.tsv` and `SHA256SUMS`

No Lane 4 partial result was accessed.  No EVICT state, extra shape/split/K,
SASS capture, or Accel-Sim run was added.
