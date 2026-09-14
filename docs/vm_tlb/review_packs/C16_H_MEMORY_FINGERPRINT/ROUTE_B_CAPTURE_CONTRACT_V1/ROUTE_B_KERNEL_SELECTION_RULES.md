# Route B kernel selection rules

Selection is frozen from a pre-outcome native census. A row is eligible only
when its model/revision, scenario, runtime implementation, input identity,
phase, and native-profile receipt equal the capture contract. Selectors may use
phase, exact kernel/function identity, implementation key, shape/dtype, launch
count, native duration, phase-duration fraction, and census-established
semantic identity. They must not use any NVBit outcome, address locality,
TLB/cache result, mechanism speedup, or post-capture quality result.

For each phase independently, group census rows by exact kernel identity plus
grid/block/shape/dtype. Rank group duration mass within that phase, choose the
smallest deterministic prefix reaching 70% mass or at least three classes when
available, and retain the highest-duration row of each distinct eligible class.
Ties sort by full mangled identity, then shape/dtype, then grid/block. Record
the complete ranked census and cutoff before static mapping.

- **Prefill:** apply the rule only to Prefill. Do not use Decode duration to
  select a Prefill kernel.
- **Decode:** apply the rule only to Decode. A high-duration Prefill kernel
  cannot stand in for Decode.
- **Diversity:** retain an actually observed representative from GEMM/GEMV,
  attention/KV, index/gather/scatter, and meaningful elementwise/reduction/
  normalization classes only when the exact census identifies that class. A
  missing class is recorded `ABSENT_IN_CENSUS`, never invented.
- **Current freeze:** no exact S0 phase-duration census exists, so this rule
  yields no selected representative kernel. The two rows below are coverage
  anchors, not mass-qualified selections.
