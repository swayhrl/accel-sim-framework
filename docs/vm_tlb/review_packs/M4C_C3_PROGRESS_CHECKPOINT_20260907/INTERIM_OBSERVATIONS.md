# Interim observations

All statements below are limited to terminal arms and existing final log
scalars. They are not C3 closeout conclusions and do not use the running
`prefill-paper` arm as a performance sample.

## OBSERVED_TERMINAL_RESULT — decode1 controls and VM profiles

- Evidence arms: `decode1-disabled`, `decode1-ideal`, `decode1-generic`,
  `decode1-paper` (all `TERMINAL_PASS`).
- Metric/scope: cycles and IPC in `C3_INTERIM_COMPARISON.tsv`.
- Observation: disabled and ideal have the same recorded 10,938,651 cycles and
  377.4279 IPC. Generic records 32,812,575 cycles / 125.8222 IPC; paper records
  34,438,514 cycles / 119.8818 IPC.
- Caveat: this establishes measured profile differences only; it does not by
  itself identify a causal TLB, walker, cache, or DRAM bottleneck.

## OBSERVED_TERMINAL_RESULT — decode1 generic versus paper counters

- Evidence arms: `decode1-generic`, `decode1-paper` (both `TERMINAL_PASS`).
- Metric/scope: generic/paper L1-TLB misses 69,483/57,926; L2-TLB misses
  23,805/22,408; PTE requests 15,798/15,786.
- Observation: paper has fewer recorded L1/L2 misses and near-equal PTE
  requests, while recording more cycles than generic.
- Caveat: these are cross-profile aggregate counters. No causal inference or
  paper-mechanism conclusion is made before C4's cross-layer evidence.

## INTERIM_SIGNAL — prefill terminal subset

- Evidence arms: `prefill-disabled`, `prefill-ideal`, `prefill-generic`
  (`TERMINAL_PASS`); `prefill-paper` is excluded (`RUNNING`).
- Metric/scope: cycles/IPC and generic VM counters in
  `C3_INTERIM_COMPARISON.tsv`.
- Observation: disabled and ideal both record 36,328,725 cycles / 507.9348
  IPC; generic records 45,976,701 cycles / 401.3472 IPC. Generic has
  1,246,241 L1-TLB misses, 56,467 L2-TLB misses, and 22,874 PTE requests.
- Caveat: `PREFILL_COMPARISON_INCOMPLETE`; no comparison involving paper is
  valid until its terminal gate passes.

## INTERIM_SIGNAL — phase-size context only

- Evidence arms: terminal `decode1-generic` and `prefill-generic`.
- Metric/scope: translation lookup requests 75,844,615 and 93,933,006,
  respectively; raw miss counts are in the TSV.
- Observation: the two ROIs have materially different aggregate translation
  volumes and raw TLB-miss counts, warranting phase-aware C4 analysis.
- Caveat: neither ROI length nor instruction normalization is inferred here;
  this is not a normalized cross-phase performance comparison.

## NOT_YET_COMPARABLE — active paper arm

- Evidence arm: `prefill-paper` (`RUNNING`).
- Scope: only `ACTIVE_ARM_LIVENESS.tsv` is admissible for this arm.
- Caveat: its started-marker/telemetry progress, PID state, CPU time, RSS, and
  log metadata are liveness-only and must not be used as IPC/cycle results.

## Counter and conservation review

- Evidence arms: terminal generic/paper arms.
- Metric/scope: `vm_object_attribution_conservation_pass` is `1` where the VM
  telemetry is enabled; each terminal arm satisfies the count/exit gate.
- Caveat: this checkpoint does not replace the formal parser's terminal C3
  closeout or C4 structured export validation.
