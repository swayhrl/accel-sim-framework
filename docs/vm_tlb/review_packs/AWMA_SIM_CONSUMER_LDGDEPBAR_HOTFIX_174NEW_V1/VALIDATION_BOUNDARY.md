# Validation boundary

Only `util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc` semantic classification changed.

- Exact `base_opcode(opcode) == "LDGDEPBAR"` returns no access kind.
- Existing atomic, read, write, memory-space, width, and address validation rules are unchanged.
- `LDG.E.32 width=0` and `LDGSTS width=0` remain rejected by the same fail-closed rule.
- `gpu-simulator/trace-parser/trace_parser.cc` is frozen and unmodified.
- The accepted `SIM_BASELINE_ID` and producer trace data remain unchanged.

This pack makes no claim that arbitrary `LD*` width-zero instructions are valid. It documents a CPU-only consumer validator correction. No simulation input was admitted and no replay was run.