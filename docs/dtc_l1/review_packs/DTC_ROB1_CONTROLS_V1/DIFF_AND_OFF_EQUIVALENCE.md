# Prepared diff and OFF equivalence

Status: PREPARED_NOT_TESTED / WAIT_AG4_TERMINAL_AUTHORITY.

No Core worktree was changed. `prepared/collector_quota.patch` is a reviewable proposed diff against c8090115bd57512b1b23fca7d925301fa620c751. Application, compilation and execution were deliberately not attempted while AG4 holds execution authority. This report makes no passing-test or binary-equivalence claim.

Allowed difference: one config scalar, option registration, pure bounded validation, and initial assignment of **only** the collection quota when nonzero. Explicit zero performs no assignment and keeps original `{4}`. All operation/response/WB/ref/fence bodies remain untouched. Nonzero rejects PAPER_IO/LEGACY/PAPER_BASE/MODERN_OO_SECTOR and nonfinite paths; the normal experiment uses finite PAPER_OO only. No change to production code, frozen AG4 identity, external checker or protected exports is allowed.

Prepared CPU coverage (`prepared/collector_quota_cpu.cc`): shared absolute-cycle1 cap including repeated calls, multiple entries and cross-cycle progress; conservation of requested sectors; ready/done edges; retries after synthetic WB rejection without re-collection; zero width resolution to4; invalid widths/modes and external path rejection by source guards. The helper test exercises actual `service_entry` and `service_quota`, but does **not** call actual operand-collector writeback, LD/ST constructor or option parser. After release, add the minimal linked integration smoke using actual config parser/constructor and actual WB-denial route, or qualify those paths using an accepted focused harness. Do not label the helper's synthetic WB-denial retry as production WB integration.

Post-release sequence, run only by registered roles after coordinator admission:

1. Apply and inspect diff in separate diagnostic Core derived from the fixed anchor; publish actual Core commit and source tree. Do not mutate c8090115/AG4.
2. Compile focused CPU code with C++17/assertions, execute negatives, record commands, stdout/stderr/exit/hash and actual source/binary identity. Expected aborts are explicit negative controls, not skipped failures.
3. Compare production and diagnostic-default0 directed traces plus explicit0 traces (state, sectors, edges, dependencies/ref lifetime, output counters). Compare default and explicit0 effective parser settings; check invalid flag errors. Equality has to be measured, not inferred from return0 or textual patch review.
4. Use only necessary default-OFF full calibration if required for diagnostic-binary result reuse, with fresh UUID and CAL reserve accounting (no more than4 total reserve, all failed starts count). Unit tests consume no full-run slots; they still need execution authority.
5. Register source/binary/config/file roles and GEMM/BICG exact input identity plus F, choose same timeout for each pair before any pair result, publish preregistration/fetch-back; only the coordinator can launch normal4/quota1 points.

C+ fairness needs a separate default-OFF fork of accepted Core6582b9d1 and focused address-index/cache integration tests only if AE is selected. Preserve existing architecture capacity/ways/whole-line pathway, compare default vs explicitOFF control, verify every bank for aligned and unaligned line addresses, S32/S64 equation/range and old full-line tags under collision, and reject invalid geometries. A C+ hash model test is prepared but unexecuted; no actual C+ implementation or equivalence is asserted.
