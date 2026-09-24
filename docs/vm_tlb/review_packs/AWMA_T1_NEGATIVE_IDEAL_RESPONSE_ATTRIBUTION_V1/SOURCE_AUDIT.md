# Source audit

The attribution runtime starts from the exact V3 runtime source and applies
`T1_ATTRIBUTION_TELEMETRY.patch` only.

The patch is observational:

- adds an unused-by-control `m_vm_translation_ready_cycle` field to the existing
  coalesced access telemetry carrier;
- records READY only after the frozen controller has returned `READY` at an
  existing V1 observation point;
- records admission only after the frozen cache/interconnect admission decision
  succeeds;
- accumulates counters and true-cycle histograms behind an opt-in environment
  variable;
- records instruction/CTA progress and data DRAM response boundaries without
  feeding any value back into simulated state.

The patch does not modify `vm_translation.cc`, translation lookup/MSHR/PTW/PWC/
PTE behavior, candidate predicates, scan direction, READY ownership,
`consume_ready`, downstream admission/arbitration, cache keys, physical
addresses, or memory partition mapping.

Patch application against the frozen V3 runtime source: `PASS`.
Compilation of GPGPU-Sim and Accel-Sim unified binary: `PASS`.

Scientific neutrality is not inferred from source shape: the final gate requires
the instrumented 10/80 and ideal cycles to exactly equal their accepted values.
