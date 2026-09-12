# Memory-Space Admission Semantics

The current full tracer serializes a memory reference address but no independent MREF memory-space tag. Lane H therefore infers space only from explicit, unambiguous opcode prefixes; all other cases remain `UNKNOWN_SPACE`.

| Decoded space | Opcode evidence accepted now | Output address domain | `tlb_eligible` | GPU-VA 4KiB/64KiB page metrics |
|---|---|---|---|---|
| `GLOBAL` | `LDG*`, `STG*`, excluding mixed `LDGSTS*` | `GPU_VA_OBSERVED` | `TRUE` | Included |
| `LOCAL` | `LDL*`, `STL*` | `GPU_LOCAL_ADDRESS_OBSERVED` | `UNKNOWN` | `NA` |
| `SHARED` | `LDS*`, `STS*` | `GPU_SHARED_ADDRESS_OBSERVED` | `FALSE` | `NA` — never treated as GPU VA |
| `UNKNOWN_SPACE` | generic LD/ST, atomics, surfaces, mixed/unsupported opcodes | `UNKNOWN_ADDRESS_DOMAIN` | `UNKNOWN` | `NA` |

The runtime object map indexes directly observed global allocation ranges. It is applied only to `GLOBAL` events with a `BOUND` temporal snapshot; LOCAL, SHARED, and UNKNOWN_SPACE events are always `UNKNOWN_RUNTIME` even if their numeric address overlaps a global allocation range.

128B-line and sector counts remain separate by `memory_space` and `address_domain`. If `--modulo-projection-set-count N` is requested, the reported value is exactly the **modulo line-set projection proxy** `line_number % N` for GLOBAL rows only. It is not a measured hardware cache-set mapping or cache hash.
