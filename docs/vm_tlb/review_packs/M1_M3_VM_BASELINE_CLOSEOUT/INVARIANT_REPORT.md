# Frozen invariants

| Invariant | Evidence | Result |
| --- | --- | --- |
| Raw/coalesced SimVA is never masked/canonicalized | G3-2B width test and source contract | PASS |
| Functional data mapping is identity-like SimPA=SimVA | M1 and G3-4A directed tests | PASS |
| One active walk per translation key; new waiter may merge | M2/G3-5 directed tests | PASS |
| Registered/in-flight same waiter does not re-probe or consume a second port | M2-RF and G3-4B exact tests | PASS |
| PTE traffic is physical and non-recursive | G3-1/G3-2 tests and real logs | PASS |
| Response association and PTE conservation | G3-2 and PTE conservation report | PASS |
| No duplicate wakeup/store/atomic side effect | G2-4 and M2 regressions | PASS |
| Timing intervals monotonic/non-negative | G3-5A analytical test and controller assertions | PASS |
| End-of-run MSHR/PWQ/walker quiescence | LUD/BFS end statistics | PASS |
