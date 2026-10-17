# R2 qualification scope

The unchanged R1 full-size testbench is rerun against changed R2 RTL, plus the
unchanged Unified1024Tags/PID1167/bank3 full-boundary case and GEN3 test.
The old-red pin binary/source/receipt remain frozen in R1; new-green pin cases
run in the full regression (clean/dirty install, write, invalidate, unrelated
pin, release while blocked, rollback/drain). Historical old-red is not rerun.

Pinned Lane3 byte reference7000ec4892 and stimuli297e1d9547 are copied without
modification from Lane3 f3d89e77. The new adapter applies every numeric store
and read from its ten cases to the actual full-size RTL. It records actual
1024-bit outputs and immutable read snapshots, compares their byte ranges
against ByteReference, and checks all ten final lines. It does not label the
reference's own self-check as RTL proof.

Abstract Lane3 `observe` strings are NOT automatically assertions in the byte
adapter. Their lifecycle coverage comes from the actual base fixture:

|Lane3 observe intent|Actual base check|Limit|
|---|---|---|
|C03/C07 held response/pins/snapshot|CASE4 held response; CASE4b simultaneous pin cases; exact drain|not numerical whole-GPU proof|
|C04 lower_accept vs WAD done|CASE7 and CASE9 WAD128/129th|native external memory is outside RTL|
|C05 bank contention/stable victim/HOL|CASE3b real same/independent bank grants; CASE5 held native transaction|SIM arbitration differs, no cycle equivalence claim|
|C06 legal rollback|CASE5 pre-commit native_abort and exact reservation release|late dynamic rollback after destructive write UNQUALIFIED|
|C08 capacity+1|CASE9 B16/S64/U pressure and WAD129th; same held request resumes|finite directed scope|
|C09 stale incarnation|CASE8 stale live fill and reused WAD ticket|no unbounded generation wrap proof|
|C10 late fill/partial bytes|CASE3 protected dirty-byte late fill and fresh/stale fill cases|external native dirty mask assumed correct|

Selector unit tests compare balanced trees against an ascending golden scan
for empty/full/every-singleton/random vectors at292/128/16/64, and full1168-word
mux against known words for all2048 input index codes. These are real component
simulations, not evidence of full-system equivalence or post-map correctness.

Remaining scope: atomic/RO/TVD integration, legal dynamic late rollback,
whole-app numerical results, post-map equivalence, macro binding/layout/power
and current-SIM timing/throughput matching remain NOT_QUALIFIED/UNRUN.
