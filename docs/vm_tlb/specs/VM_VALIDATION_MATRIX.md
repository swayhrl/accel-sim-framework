# VM validation matrix (M1)

| Check | Evidence | Result |
| --- | --- | --- |
| Mapper/page helpers | `tests/vm_core_m1_test.cc` | PASS |
| QV100 disabled vs ideal | LUD-64, key non-VM stats diff | PASS |
| RTX3070 disabled vs ideal | LUD-64, unchanged config | PASS |
| Irregular disabled vs ideal | Rodinia BFS-4096 / QV100 | PASS |
| VM-disabled vs frozen S1-B0 | QV100/RTX values | PASS |
| Ideal stalls | `vm_translation_stall_cycles=0` | PASS |

All comparisons use exact equality for instruction/cycle/IPC, L1D, L2, and
DRAM counters; no tolerance is used.
