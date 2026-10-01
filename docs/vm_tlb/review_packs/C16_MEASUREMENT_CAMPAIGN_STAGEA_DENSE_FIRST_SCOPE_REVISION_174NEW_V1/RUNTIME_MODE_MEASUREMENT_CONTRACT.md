# Runtime-mode measurement contract — prospective Tier0 only

Qwen BF16 and Qwen AWQ Graph OFF/ON passed the frozen graph-mode correctness comparison in runtime canary `3f62f909a474e4c56695ffacf36ddcb5d7b5f147` (`GRAPH_OFF_ON_CORRECTNESS.tsv`). This does **not** repair AWQ V1 observer non-neutrality; MP05 still needs an independent Observer V2 runtime PASS. OLMoE failed and is excluded. The roles below do not authorize 109 execution.

| Mode / run | Permitted authority | Not permitted |
|---|---|---|
| Graph OFF, instrumentation ON | semantic NVTX chronology; module/operator attribution; lightweight NSYS `cuda,nvtx` correlation; kernel inventory, shape/order, launch-gap chronology; diagnostic local wall decomposition | standalone architecture claim; authoritative request timing from instrumented wall; direct local-time mapping to Graph ON |
| Graph OFF, instrumentation OFF | native CUDA-event request timing on the same qualified input/runtime | module/operator attribution absent from this uninstrumented arm |
| Graph ON, instrumentation OFF | mature strong-software control and native whole-request timing control | inference of Graph-ON per-range times from Graph-OFF ranges |
| Instrumented wall, either eligible mode | observer neutrality check only | scientific native timing endpoint |

The Tier0 allowlist is native CUDA-event request timing, Graph OFF/ON strong control, NVTX, one lightweight NSYS `cuda,nvtx` capture as contractually bounded, kernel inventory, shape/order, and launch-gap chronology. No NCU, NVBit, SASS, or Accel-Sim. BF16 may use accepted V1 observer; AWQ may use V2 only after its canary PASS. Source qualification `f63d39c8d90ced038445c264fa8242c524a1aa6f` is not that PASS.

For DQ1/DQ4a, derive candidate local wall weight only from correlated intervals inside the same natural parent request; use a wall **union**, not a sum of overlapping module/kernel durations. For DQ2, compare B1/B4 on their matched request definitions and report effective M, shape, backend, and kernel identity. For DQ3, a memory/service hypothesis requires native timing exposure; bytes or traffic alone do not give service time. No direct subtraction between Graph-OFF semantic-range time and Graph-ON whole-request time is a local causal estimate. The original graph control can instead falsify an apparent Graph-OFF gap: if Graph ON absorbs at least 85% under a prospectively matched estimator, STOP that direction. A Graph-OFF launch/dispatch artifact is not a hardware problem.

The future 109 contract must freeze input IDs, native endpoints, matched denominator for the 85% rule, graph/observer mode, allowed capture count, correctness/kernel identity, and point budget before launch. If these cannot be made commensurate, mark the gap `NOT_IDENTIFIABLE` and do not use the 85% arithmetic to assert survival. A correctness or observer-neutrality failure is a STOP, not a prompt to change tolerance.
