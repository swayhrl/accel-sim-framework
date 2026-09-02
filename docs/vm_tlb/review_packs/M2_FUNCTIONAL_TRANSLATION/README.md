# M2 functional translation review pack

Status: `PASS` (G2-CLOSEOUT).  This pack closes the M2 functional model only:
resident deterministic mappings, finite TLB/MSHR/PWQ/walker resources, and a
fixed-latency walk.  It deliberately does not claim PTE L2/DRAM timing; that
is M3 work.

Validated source anchors are Core
`e7999554200760b31b4efe16d98e050370e1ea71` and Framework source
`4012be3606c300d11e7b34826ee1cb22b0852b93`.  The Framework source anchor is
the dependency-generation repair used by the cold validation build; later
Framework commits in this pack are evidence/documentation only.

| Gate | Result | Evidence |
| --- | --- | --- |
| G2-1 mapper + finite L1/L2 | PASS | [G2_1_MAPPER_TLB.md](G2_1_MAPPER_TLB.md) |
| G2-2 MSHR merge/backpressure | PASS | [G2_2_MSHR.md](G2_2_MSHR.md) |
| G2-3 PWQ + walkers | PASS | [G2_3_PWQ_WALKERS.md](G2_3_PWQ_WALKERS.md) |
| G2-4 replay/store/atomic | PASS | [G2_4_RUNNING.md](G2_4_RUNNING.md) |
| Runtime allocation diagnosis | PASS | [../M2_RUNTIME_MEMORY_DIAG/README.md](../M2_RUNTIME_MEMORY_DIAG/README.md) |

Closeout artifacts:

- [Directed expected-versus-actual matrix](DIRECTED_TEST_MATRIX.md)
- [Conservation and invariant report](INVARIANT_REPORT.md)
- [Integrated smoke and sensitivity summary](INTEGRATED_VALIDATION.md)
- [Raw evidence index](RAW_LOG_INDEX.tsv)

The cold rebuild, all directed tests, disabled/ideal transparency comparison,
and real functional replays finished without a deadlock, request loss,
duplicate wakeup, duplicate store/atomic side effect, or non-quiescent
translation state.  G3-0 may begin from this frozen M2 source state.
