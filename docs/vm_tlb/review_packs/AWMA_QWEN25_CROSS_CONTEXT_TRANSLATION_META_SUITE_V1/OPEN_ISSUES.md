# Open issues and decision boundaries

- Meta-suite coverage is structural Native GPU-time coverage. It does not
  demonstrate that one trace reproduces translation behavior across
  different input data, context length, batch, or Decode horizon.
- The cross-context census contains no accepted simulator-native trace
  qualification for new scenario extension targets. MISSING_SIM_TRACE in
  this pack is a planning class only; no capture is authorized.
- B4 Decode GEMV absence and GEMM appearance show a dispatch-family shift.
  The exact model operator relationship remains UNKNOWN without explicit
  producer semantics.
- Several high-mass Level 3 gaps remain after the minimum extension rule,
  notably additional B4 Decode GEMM/elementwise variants, D128 vectorized
  elementwise, and T8192 Prefill GEMM variants. They are listed in
  SCENARIO_HIGH_MASS_GAPS.tsv for a later evidence-driven expansion decision.
- The accepted authority has no second independently frozen T2048 content
  payload. The meta-suite cannot claim different-content portability at
  fixed context and batch from these inputs.
- Capture/simulation burden is a transparent grid/target-count proxy.
  It is not measured simulator wall time or GPU capture cost.
