# EPL2_RTL_COST_TIMING_REFINEMENT_R2_BOUNDED

Final selected hardware: f54d3c054a6a03c85b40a1c5018751958c78a129.
Authority f2a2fec3ee5e1bb42aa298c84d25bdd9bd70e13e, section1.
R1 frozen09de19579c0708f6542dfd65e1f3aae8a9a8b841 and all original
RTL/tests/netlists/raw reports are preserved. Earlier qualified ed1c6ea12
variant and unsuccessful engineering attempts remain in their own paths.

Actual final three-mode full-capacity functional suites, GEN3 exhaustion,
Unified1024Tag/PID1167/bank3 boundary and original Lane3 byte vectors pass.
The R1 terminal counters AND cycles match exactly. Component proof scopes,
static hardwire invariants, source/binary/stimulus hashes and raw logs are in
[the final pack](../../../docs/ep_l2/review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1/README.md).
No whole-controller/post-map/whole-GPU or dynamic late rollback claim.

Same-library/SDC/effort three-mode actual synthesis and two-period STA are
complete: all modes remain TIMING_UNCLOSED at0.883392226ns AND2ns. Reset remains
timed; real reset buffers are area charged. No false/multicycle exception,
capacity reduction, GEN narrowing or extra stage/II change was introduced.
SRAM146KiB macro area/delay and external Tag/MSHR/NoC cost remain UNKNOWN.
No whole-slice PPA or current Lane5 performance pairing is qualified.

Read STRUCTURAL_PROOF.md, COVERAGE_R2.md, SYNTHESIS_ACCOUNTING_R2.md,
SIM_RTL_TIMING_DELTA.md, SOURCE_INDEX_R2.md and DC_HANDOFF_R2.md. Exact DC
scripts/filelists/constraints/library/unit/PVT entry is delivered; DC UNRUN.
No formal simulator changes or new application runs; TVD tests stay UNRUN.

T0 2026-10-17T17:30:58Z;4h checkpoint21:30:58Z;6h hard bound23:30:58Z.
Final artifacts: /workspace/ep_l2_potential20261017_lane5_results/
EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3. All resource leases release after
completion; no resident waiter. Own12GiB and48/40GiB disk/64GiB RAM protections
remained even after the shared policy was raised externally.
