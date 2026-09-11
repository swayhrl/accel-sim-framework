# C13 minimal diagnostics — final report

Status: `C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW`

## Evidence boundary

- Each C13 result is accepted only after runner terminal validation, immutable raw-log SHA recheck, accepted operator-map marker identity, exact per-kernel cycle closure, and cumulative `vm_*` delta-to-terminal closure.
- The C12 F0/F7 reference rows remain immutable. Capacity rows B/C are `DIAGNOSTIC_NON_EQUAL_BUDGET`; no C13 diagnostic result rewrites the C12 fair matrix.
- Operator labels use the accepted direct/semantic/heuristic/unresolved map. No execution-order inference or trace re-scan is used.

## Terminal C13 evidence currently admitted

- `C13-CAP-P320`
- `C13-CAP-P768S10`
- `C13-LAT-D11`
- `C13-LAT-P8`
- `C13-LAT-P9`
- `C13-SEL-D10`
- `C13-SEL-D10-CTRL-NEWBIN`
- `C13-SEL-P10`
- `C13-SEL-P10-CTRL-NEWBIN`

## MEASURED_C13_DIAGNOSTIC_FACT — H3 fine Segment latency

- Prefill Lseg=8: candidate-minus-F0 cycles = `-2551028` (positive simulated-cycle gain).
- Prefill Lseg=9: candidate-minus-F0 cycles = `-1583279` (positive simulated-cycle gain).
- Decode1 Lseg=11: candidate-minus-F0 cycles = `-24692` (positive simulated-cycle gain).
- `LATENCY_FINE_SWEEP.tsv` combines these new measured points with immutable C12 F7 L5/L10/L20 only after common trace/map identity checks. The prior 8.755/10.827 values remain `EMPIRICAL_INTERPOLATION_ONLY`, not substituted measurements.
- The new Prefill L9 gain and immutable L10 regression empirically bracket the crossover as `9 < Lseg* < 10`; therefore the prior 8.755 numeric interpolation is revised, not used as a measured crossover. Decode1 L11 remains a gain while immutable L20 regresses, so its prior 10.827 numeric interpolation is likewise not supported as a precise crossover; the current measured bracket is `11 < Lseg* < 20`.

## MEASURED_C13_DIAGNOSTIC_FACT — H2 exact-remainder 2×2

- B-A: cycles `-112827`; L2 misses `-11836`; walks `-3136`; PTE DRAM responses `-2708`; requester translation latency `-6951930`.
- C-A: cycles `-431638`; L2 misses `-37644`; walks `-18583`; PTE DRAM responses `-6703`; requester translation latency `-23118509`.
- D-B: cycles `+993477`; L2 misses `+87528`; walks `+16069`; PTE DRAM responses `+23794`; requester translation latency `+30285115`.
- D-C: cycles `+1312288`; L2 misses `+113336`; walks `+31516`; PTE DRAM responses `+27789`; requester translation latency `+46451694`.
- Cycle interaction `(D-B)-(C-A)` = `+1425115`, explicitly `DIAGNOSTIC_INTERACTION_ONLY`.
- The exact320/no-Segment B-A observation reduces rather than increases walks/PTE DRAM. It therefore does not support attributing a Prefill traditional-walk/PTE-DRAM increase primarily to the exact-remainder 768→320 capacity change; the non-equal-budget interaction does not identify a unique cause.

## MEASURED_C13_DIAGNOSTIC_FACT — H1 object-selective Segment

- C13-SEL-P10 vs same-new-binary C13-SEL-P10-CTRL-NEWBIN: cycles `+143881`; L2 misses `+9668`; walks `+8016`; PTE DRAM `+2021`; Segment hits `-16445476`.
  - kernel 691 cycle delta `+126026`; Embedding/Output aggregate `+129646`; FFN `+601`; Attention Projection `+13380`.
- C13-SEL-D10 vs same-new-binary C13-SEL-D10-CTRL-NEWBIN: cycles `+38843`; L2 misses `+8031`; walks `+8016`; PTE DRAM `+2055`; Segment hits `-4226749`.
- Relative only to its same-new-binary control, excluding the tied Embedding/Output Weight range regresses both Prefill (`+143881` cycles) and Decode1 (`+38843` cycles). Prefill kernel 691 regresses by `+126026` cycles, while FFN MLP changes by `+601` and Attention Projection by `+13380`; this does not support H1 recovery of kernel 691, a Prefill turnaround, or a phase-direction reversal.

## SUPPORTED_C13_MECHANISM_SIGNAL

- The controlled tables support only associations between measured eligibility/capacity/latency changes and observed cycles/translation/cache telemetry. They do not establish a unique critical-path causal chain.
- Whether a phase-aware object policy is warranted is evaluated from the same-new-binary selective pairs, not from cross-binary historical speedups.

## DIAGNOSTIC_INTERACTION_ONLY

- The 2×2 capacity interaction is a local measured decomposition for this Prefill setup. It is not an equal-budget result or a general architecture law.

## UNRESOLVED

- Cache/translation counter association cannot by itself prove which downstream queue, memory response, or critical path caused a cycle change.
- Any operator class whose accepted map evidence is heuristic or unresolved remains so; no C13 result upgrades its semantic evidence tier.
