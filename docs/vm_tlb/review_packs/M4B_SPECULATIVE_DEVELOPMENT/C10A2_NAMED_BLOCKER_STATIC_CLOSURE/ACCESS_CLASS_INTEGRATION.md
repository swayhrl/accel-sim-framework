# B4 — production access-class integration

The source audit found one production controller caller:
`ldst_unit::memory_cycle` in `src/gpgpu-sim/shader.cc`. It owns the
authoritative `warp_inst_t`; it now passes:

| Instruction predicate | Explicit enum | Segment consequence |
| --- | --- | --- |
| `inst.isatomic()` | `TRANSLATION_ACCESS_ATOMIC` | conventional path only |
| else `inst.is_store()` | `TRANSLATION_ACCESS_WRITE` | conventional path only |
| otherwise | `TRANSLATION_ACCESS_READ` | may use registered descriptor |

The internal PTE path in `gpgpu_sim::icnt_cycle` is physical/bypass and never
calls `translation_controller::translate`; it therefore cannot recursively
gain the default READ classification. Legacy unit-test callers may retain the
API default only as documented compatibility callers, not production
simulation.

Segment service receives the saved enum in `lookup_operation` and calls a
descriptor only when it is `READ`. The object map remains telemetry-only;
no `OBJECT_WEIGHT` condition is a Segment eligibility predicate. The complete
source audit ledger is `SOURCE_CALLSITE_LEDGER.tsv`.
