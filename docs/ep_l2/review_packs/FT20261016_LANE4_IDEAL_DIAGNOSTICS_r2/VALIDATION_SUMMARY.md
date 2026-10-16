# Executed validation

- Historical candidate Release build: PASS. VectorAdd all-OFF: 73873 cycles,
  56000000 instructions; exactly matches retained parent equivalence evidence.
- Integrated Lane 1 plus diagnostics Release target: PASS; assertions enabled
  in actual compile_commands (`-O3 -g3`, no `-DNDEBUG`). The producing
  commits are frozen before configure/build and unchanged at the postcheck.
  This candidate consumes Lane1 runtime-ready Core 126394be46b15f55b9756d43eb9ca9a9baae1c84.
- Latest candidate: 12 production-driven C++ executable/config invocations
  PASS. This includes the original finite/unified WB suite, ordinary descriptor
  and WAD regressions, I_WB, I_WB_META, metadata pressure, read-reference checks
  and the read-reference checks above actual finite WBUF16, plus four original
  real-partition finite/unified C8/C16 lifetime/response regressions.
- Six illegal CLI configurations: PASS_EXPECTED_REJECTION. No workload ran in
  these expected-abort cases. Exact commands and overlays are retained.
- 16 parser/config adapter tests: PASS. Synthetic parser fixtures are
  parser tests only, not performance or independent model qualification.
- Two full-application historical pilot modes: COMPLETE_VALID, exact pinned
  source/binary/config/trace, native exit and 64-slice terminal closure. One
  exact duplicate claim returned the existing result and launched no process.
- B16 application matrix: NOT_RUN. Own candidate is not a qualified shared
  release and cannot reuse a different binary's B16 row as an exact match.

Raw logs stay at their indexed result roots. Reparse artifacts are separate;
the earlier retained raw/run_status evidence is not overwritten. Early config
lexing and quota refusals did not start a workload and are not performance rows.
The retained illegal-mode harness note explains an initial overly strict log
postcheck (required a literal Assertion word); the exact abort reason and all
six cases were then rechecked. This was not a failed application simulation.
