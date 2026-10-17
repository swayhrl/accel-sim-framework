# Lane2 — bounded RTL R2 delivered; timing remains unclosed

Authority f2a2fec3ee5e1bb42aa298c84d25bdd9bd70e13e section1. T0
2026-10-17T17:30:58Z. New bounded Goal; original Lane2 history retained.
Canonical five-file hardware source f54d3c054a6a03c85b40a1c5018751958c78a129.

Selected final variant: balanced bank-compatible1168-slot allocation,
16-word metadata/Tag-map masks, GEN32 prefix, real charged reset distribution,
and proved B16/S64 fixed map/owner/role hardwires. No capacity/bank service/
lifecycle/clock stage/II changes relative to R1. Unified retains dynamic state.

|Mode|Reference standard-cell area|Change vs R1|WNS0.883392226ns|WNS2ns|
|---|---:|---:|---:|---:|
|B16|1598557.058|-22.774%|-1.413025|-0.296418|
|S64|1627498.656|-23.269%|-1.400875|-0.284268|
|UNIFIED|2432606.442|-3.672%|-1.700971|-0.584364|

Actual full-size base/pin/adjacent grant/WAD129th/stale/backpressure and GEN3,
Unified1024Tag/PID1167/bank3 test and all three Lane3 actual byte suites PASS.
R1 terminal counters/cycles are identical; helper and scoped word/reset/Tagmap
proofs are attached. No whole-controller/global/post-map/whole-GPU proof;
dynamic late rollback after destructive commit remains unqualified.

All three modes use identical Nangate typical1.1V25C/library/SDC/ABC effort.
All target and2ns timing FAIL, ordinary FF data paths also unclosed. Real
buffers and control metadata are charged. SRAM146KiB macro delay/area and
native Tag/LRU/MSHR/dirty-byte/NoC costs UNKNOWN. No whole-slice PPA/net-benefit
or current SIM performance pairing. Existing SIM/RTL II4/II3/copy/return/
arbitration/native-approval gaps remain. Lane1 timing proposals are separate;
no official SIM change or Lane5 application launched.

Exact sameRTL DC entry/filelist/constraints/DB/PVT/units handoff is ready;
dc_shell absent: DC UNRUN. Power and post-layout UNRUN. No additional stage
or throughput change is silently inferred from negative STA.

R1 frozen09de:177 public assets,21 original large archives and5 accepted
functional binaries verified unchanged read-only. Earlier qualified ed1
variant and trial failures/time/resource stops are preserved and classified.
TVD/common/structural Core remain be5dcbe1/099aeb5a/26ed1da6 clean; TVD r14
three tests NOT_COMPILED_NOT_RUN. No complete TVD claim.

Central admission and leases were used; own12GiB,workspace48GiB/Share40GiB/
availableRAM64GiB floors retained despite newer shared16GiB policy. No
Storage-Ops/delete/migration or foreign process/data/quota action; no waiter.

Review pack: [RTL_COST_TIMING_REFINEMENT_R2_r1](../../../review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1/README.md).
Precise source/config/binary/trace/library/SDC/tool/netlist identities are in
RTL_COST_R2_RECEIPT and per-run raw receipts. Read the enclosing Git commit as
the publication identity; hardware identity is the immutable source above.

Artifact publication e0dd39baa19600512164cb0099bdb6bc3c5524a4 has exact
GitHub readback of all3 heads, all327 pack blob identities and selected file
bytes. The review pack is immutable. See RTL_R2_PUBLICATION_CLOSEOUT_r1.json
for that readback and final resource audit charging all3 worktree copies and
actual new Git object disk bytes; all own leases are released. This final
metadata commit is separately read back by the publisher. No waiter remains.
