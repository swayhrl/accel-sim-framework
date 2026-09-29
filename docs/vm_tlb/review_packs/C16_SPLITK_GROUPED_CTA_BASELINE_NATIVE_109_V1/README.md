# C16 Split-K Grouped CTA Baseline Native — Lane 7

Task: `C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1`

Status: CPU-only preparation in progress.  CUDA initialization, extension
import, and GPU lock acquisition remain disabled until Lane 8 publishes an
`EARLY_GATE.json` with exact status
`READY_FOR_GROUPED_CTA_NATIVE_BASELINE` and every bound SHA verifies.

Frozen matrix: `M=256`, `N=49152`, `K={3072,4096}`,
`split={8,1}`, `mapping={ROW,GROUP_M16}`.  No other point is authorized.

No Lane 4 partial result is an input to this pack.
