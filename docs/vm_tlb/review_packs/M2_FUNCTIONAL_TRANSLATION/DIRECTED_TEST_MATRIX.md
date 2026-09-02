# M2 directed expected-versus-actual matrix

All commands used `g++ -std=c++11 -Wall -Wextra -Isrc`, linked
`src/gpgpu-sim/vm_translation.cc`, and exited zero.  Raw terminal captures are
listed in [RAW_LOG_INDEX.tsv](RAW_LOG_INDEX.tsv).

| Test | Expected machine-checkable result | Actual | Result |
| --- | --- | --- | --- |
| `vm_core_m1_test` | SimVA/SimPA boundary and disabled/ideal semantics | `PASS` | PASS |
| `vm_m2_g2_1_test` | cold/hit, finite L1/L2 evictions, shared L2, size tags, port stall | `PASS` | PASS |
| `vm_m2_g2_2_test` | one active key, merge exactly once, full backpressure, release/wakeup conservation | `PASS` | PASS |
| `vm_m2_g2_3_test` | finite PWQ and walker limit, no early completion, starts=completions | `PASS` | PASS |
| `vm_m2_g2_4_test` | pending/replay, same UID once, store and atomic exactly once, cross-page behavior | `PASS` | PASS |

The individual gate documents record the exact expected counts exercised by
each test.  In particular, G2-2 proves one allocation/two waiters/one merge/
two wakeups for a same-key pair, and G2-3 proves queue backpressure plus a
one-walker, latency-three sequence.  Thus the four closeout invariants are
not inferred from runtime counters alone.

## Transparency regression

The final cold RTX3070 LUD replay compared VM-disabled with VM-ideal-identity
using the same binary/configuration/trace.  After excluding the expected
VM-mode and host-rate/time fields, the normalized architecture-statistics diff
was empty.  See `D5_POSTFIX_M1_TRANSPARENCY.diff` in the M2-D raw index.
