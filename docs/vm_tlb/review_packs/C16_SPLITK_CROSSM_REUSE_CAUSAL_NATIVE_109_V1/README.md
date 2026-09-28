# C16 Split-K Cross-M Reuse Causal Native — Lane 7

Task: `C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1`

Status: CPU-only preparation complete; GPU execution is gated on Lane 8
`EARLY_GATE.json` having the exact decision
`READY_FOR_NATIVE_CAUSAL_SCREEN` and passing all bound-SHA checks.

Frozen matrix: `M=256`, `N=49152`, `K={2560,3072}`,
`split={8,1}`, `state={SHARED,PER_MTILE}`.  Every cell allocates sixteen
bit-identical weight-side replicas.  `SHARED` uses `replica_mask=0` and
`PER_MTILE` uses `replica_mask=15`; both states must use the same patched
extension binary and kernel path.

The scripts are deliberately split at the CUDA boundary:

- `scripts/crossm_contract.py` is standard-library-only and is safe before the gate.
- `scripts/build_isolated.sh` is only a recorded build recipe until the gate binds the source patch.
- `scripts/crossm_runner.py` imports Torch and the CUDA extension only in explicit GPU modes.

No Lane 4 partial result is an input to this pack.

