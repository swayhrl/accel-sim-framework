# R3A complete finite RTL qualification; timing unclosed

Source five-file hardware ac607192957cfd2d69d76bfbc73531b5dbe57523,
source release ref hrl/ep-l2-rtl-r3-metadata-cost-v1 at
b4d825b4e2cd7808fc5db2bd907d65fb3e1e9676. Its worktree and original
checkpoint are read-only; new evidence is published on the execution branch.
All14 accepted actual VVP binaries were decoded and SHA verified, all source
and generated fixtures checked. This is complete FINITE configured RTL test
qualification, not unbounded formal proof, target timing closure, officialSIM
release qualification or wholeGPU/app numerical qualification.

Actual gates: full1024/1168/128/GEN32 B16/U/S64 twelve-case base plus separate
GEN3 exhaustion; all3 actualLane3 ten-vector byte/snapshot comparisons(13
observations+10final lines each); all3 independent concurrent GEN+WB+rollback
cases; newly compiled actualA all3 same-bank different-row double-GEN plus
held snapshot/descriptor pin, Tag rebind, stale/late fill, WB bytes/drain;
highestPID1167/bank3/row291 real fullTag capacity and bank-compatible exhaustion
with108other-bank free, same held request resumes after credit, byteWB37,
exact3379cycles. The final boundary run completed under ordinary48GiB central
lease in1370.914seconds; earlier interrupted attempts remain INCOMPLETE.

Full base3 mode counter/cycle lines and highest boundary line equal frozenR2
exactly. Scoped actual small4Tag/32payload/GEN3 controller control/metadata cut
is4cycles only, excludes byte datapath outputs tested separately; common actual
word induction/all-index two-port GEN3/GEN32 proof retains explicit state/event
premises and same-slot lower priority. No full-controller/unbounded proof claimed.
The extra uninstantiated legacy slice_top source present in compile filelists is
also separately checked against the immutableR2 blob; all executions use the
actual full-top macro with SRAM/bank path, not that behavioral reference.

A actual sameLib/SDC/fast-clean cost table is already published in the second
checkpoint87e18bd5 and current actual_cost_r1. Areas B16/S64/U1437416.652 /
1478834.714 /1847603.016, U/B1.2853636. WNS−1.370226/−1.393728/−1.447954ns,
all2ns also negative. Partial controller/access cut only. SRAM146KiB and
traditionalTag/LRU/MSHR/NoC/queue costs UNKNOWN. All GEN32/state/port/storage
costs retained; two engines preserve simultaneous metadata writes even in one
bank. Native_gen when unconsumed may differ under port sharing; no accepted
cycle/II/order change. OriginalSIM timing/arbiter/approval differences remain.

PreciseA DC source entry already exists in frozenA tree:
rtl/ep_l2/flow/run_dc_r3.sh andrun_dc_r3.tcl, filelist.f/common.sdc.
Use RTL_REPO equal theA worktree (or exact b4d source checkout) and actualDB,
PVT/operating-condition/time-unit/input-cell/output-load values. DC isUNRUN
(absent); no fabricatedmacro/lib, timing exception, power or PNR is added.

This supplies a newly finite-qualified fallback while owner-removing finalB
e8d67d13 completes its own remaining byte/highest tests. Its three actualmaps
and two-periodSTA are complete, but B is NOT yet called fully qualified here.
No source change or B0 binary inheritance. No formalSIM/app or other project
was touched; shared20GiB/own12GiB and original48/40GiB/64GiB gates apply.
No47.5GiB exception was authorized or activated. Large exact binaries/netlists
remain in central workspace at receipt paths; no redundant largeGit copies.
