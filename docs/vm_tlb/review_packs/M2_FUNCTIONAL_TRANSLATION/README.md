# M2 functional translation review pack

Status: `PASS (M2-RF) — STOP FOR CHATGPT REVIEW`.  This pack closes the M2 functional model only:
resident deterministic mappings, finite TLB/MSHR/PWQ/walker resources, and a
fixed-latency walk.  It deliberately does not claim PTE L2/DRAM timing; that
is M3 work.

Validated repaired source anchor is Core
`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`; Framework handoff is
`e6b8d6b6034acd34f5f5176c3b0f4c3a865c09dc`.  The Framework source anchor
`4012be3606c300d11e7b34826ee1cb22b0852b93` remains the dependency-generation
repair used by the cold validation build.

| Gate | Result | Evidence |
| --- | --- | --- |
| G2-1 mapper + finite L1/L2 | PASS | [G2_1_MAPPER_TLB.md](G2_1_MAPPER_TLB.md) |
| G2-2 MSHR merge/backpressure | PASS | [G2_2_MSHR.md](G2_2_MSHR.md) |
| G2-3 PWQ + walkers | PASS | [G2_3_PWQ_WALKERS.md](G2_3_PWQ_WALKERS.md) |
| G2-4 replay/store/atomic | PASS | [G2_4_RUNNING.md](G2_4_RUNNING.md) |
| M2-RF registered-waiter retry repair | PASS | [M2_RF_REPAIR.md](M2_RF_REPAIR.md) |
| Runtime allocation diagnosis | PASS | [../M2_RUNTIME_MEMORY_DIAG/README.md](../M2_RUNTIME_MEMORY_DIAG/README.md) |

Closeout artifacts:

- [Source anchors](SOURCE_ANCHORS.md), [commit history](COMMIT_HISTORY.md), and [changed files](CHANGED_FILES.md)
- [Directed expected-versus-actual matrix](DIRECTED_TEST_MATRIX.md)
- [Conservation and invariant report](INVARIANT_REPORT.md) and [validation summary](VALIDATION_SUMMARY.md)
- [Integrated smoke and sensitivity summary](INTEGRATED_VALIDATION.md)
- [Open issues / frozen boundary](OPEN_ISSUES.md)
- [Raw evidence index](RAW_LOG_INDEX.tsv)

The cold rebuild, all directed tests, disabled/ideal transparency comparison,
and real functional replays finished without a deadlock, request loss,
duplicate wakeup, duplicate store/atomic side effect, or non-quiescent
translation state.  The RF repair additionally proves that registered pending
waiters do not pollute TLB port/probe/miss counters.  M3 remains paused until
independent ChatGPT review accepts this repaired M2 baseline.
