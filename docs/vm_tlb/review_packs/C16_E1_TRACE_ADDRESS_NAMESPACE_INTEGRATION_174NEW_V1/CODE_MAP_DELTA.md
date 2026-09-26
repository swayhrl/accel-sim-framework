# Code map delta

Core integration branch:

- `oracle_elastic_residency.{h,cc}`: default-off bounded address observer.
- `gpu-cache.{h,cc}` / `gpu-sim.cc`: observer config, exact-address filter, L2-entry/oracle observations.
- `abstract_hardware_model.cc`: coalesced `mem_access_t` observation.
- `mem_fetch.cc`: constructed-request observation.
- directed tests: observer serialization and protected-sector fill accounting.

Framework integration branch:

- `trace_parser.cc`: parsed-lane observation.
- `trace_driven.cc`: SM89-to-accepted-Ampere parser adapter and instruction-operand observation.
- `e1_trace_namespace_integration.py`: authority validation, deterministic sidecar generation, real-artifact extraction, full-bundle opcode audit and observer verification.
- `oracle_sidecar_activation_canary.cc`: actual Core sidecar/parser/lookup target and exclusion test.
- SM89 trace config copied byte-for-byte from the accepted RTX4080 platform authority.

All additions are opt-in diagnostics or integration tooling. Quota, admission denial, victim selection, hit promotion, protected lifetime and baseline queue semantics are unchanged.
