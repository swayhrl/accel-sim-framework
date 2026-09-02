# M2 HARD-gate validation summary

| Gate | Evidence | Result |
| --- | --- | --- |
| R2.0 identity | root request UID / child `get_original_mf()` source rule and bounded trace in `implementation/M2_IO_RESPONSE_RECOVERY_EVIDENCE.md` | PASS |
| R2.1 request/response ownership | dedicated candidate/issue/inflight path; response dispatch precedes conventional fill; default VecAdd 16/16/16 and conventional route 0 | PASS |
| R2.2 FIFO PIB/writeback | directed FIFO HOL and same-cycle release tests; runtime PIB 0, retirement 16, dependencies 16/16 | PASS |
| R2.3 cardinality | existing coalesced accesses grouped to unique 128B references; directed 1/2/4/32 and multi-sector cases; mode-specific completion count | PASS |
| R2.4 transient block | directed retry-to-Pending regression; no sticky lifetime block state | PASS |
| R2.5 access isolation | IO source path has no `l1_cache::access`/MSHR allocation; response routing counter conventional=0; MSHR full counters 0 | PASS |
| R2.6 real smoke / I13 | default 640-line-per-SM VecAdd PASS, no deadlock, all request/credit/PIB/dependency drain invariants close | PASS |
| I01-I11 | deterministic `dtc_l1_m1_common_test`: cold/valid/pending, width, partial hold, exact LRU, original physical fill, duplicate, HOL, same-cycle release | PASS |
| I12 | 1-line physical-pool VecAdd naturally reaches native deadlock detector; compact resource dump has free=0 and a partial IO entry | PASS (expected) |
| I14/I15 | cap=2 VecAdd: cap-full=1190, exact request/credit closure; IO issue queue contains one fixed issue attempt/SM/cycle | PASS |
| no traditional MSHR | deterministic 64-pending-entry high-MLP test exceeds 8/32 while Pending merge stays one lower miss; source and independent runtime MSHR counters confirm isolation | PASS |
| counters/parser/hygiene | strict IO summary parser PASS; release build, CTest, `git diff --check`, and closeout worktrees clean | PASS |

The tiny-pool abort is a required expected-resource classification, not a
success-path application result. The default configuration has no watchdog
event and completes normally.
