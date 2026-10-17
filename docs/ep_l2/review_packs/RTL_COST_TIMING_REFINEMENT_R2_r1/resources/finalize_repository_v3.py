from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2-fanout-v3');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3');pack=art/'PUBLIC_REVIEW_PACK_R2';rel='docs/ep_l2/review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1';target=repo/rel
r=json.loads((pack/'RTL_COST_R2_RECEIPT.json').read_text());assert r['status']=='FUNCTIONAL_THREE_MODE_MAP_STA_COMPLETE_TIMING_UNCLOSED'
assert not target.exists()
# No changing hardware after qualified/mapped f54: compare all five actual RTL blobs.
for f in r['source_files']:
 assert hashlib.sha256((repo/f['path']).read_bytes()).hexdigest()==f['sha256']
readme='''# EPL2_RTL_COST_TIMING_REFINEMENT_R2_BOUNDED

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
'''
(repo/'rtl/ep_l2/r2/README.md').write_text(readme)
shutil.copyfile(repo/'rtl/ep_l2/r2/README.md',pack/'contracts_and_proofs/README.md')
status='''# Lane2 — bounded RTL R2 delivered; timing remains unclosed

Authority f2a2fec3ee5e1bb42aa298c84d25bdd9bd70e13e section1. T0
2026-10-17T17:30:58Z. New bounded Goal; original Lane2 history retained.
Canonical five-file hardware source f54d3c054a6a03c85b40a1c5018751958c78a129.

Selected final variant: balanced bank-compatible1168-slot allocation,
16-word metadata/Tag-map masks, GEN32 prefix, real charged reset distribution,
and proved B16/S64 fixed map/owner/role hardwires. No capacity/bank service/
lifecycle/clock stage/II changes relative to R1. Unified retains dynamic state.

|Mode|Reference standard-cell area|Change vs R1|WNS0.883392226ns|WNS2ns|
|---|---:|---:|---:|---:|
'''
for x in r['modes']:status+=f"|{x['mode']}|{x['R2_area']:.3f}|{x['area_change_percent']:.3f}%|{x['R2_target_WNS_ns']:.6f}|{x['R2_2ns_WNS_ns']:.6f}|\n"
status+='''
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
'''
status_path=repo/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane2';(status_path/'STATUS.md').write_text(status)
r.update(cross_mode_partial_area_ratios=json.loads((pack/'CROSS_MODE_AREA_RATIOS.json').read_text()),review_pack=rel,publication_identity='enclosing Git commit; exact remote readback is recorded by publisher outside the commit to avoid self-hash circularity',publication_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),Goal_scope='bounded engineering exploration completed, negative timing outcome retained; no resident waiter',mandatory_functional_final_receipt='functional_and_diagnosis/qualification-vector/unified-last-physical/FUNCTIONAL_RECEIPT.json')
for dest in (pack/'RTL_COST_R2_RECEIPT.json',pack/'RECEIPT.json',status_path/'RECEIPT.json'):dest.write_text(json.dumps(r,indent=2)+'\n')
files=sorted(p for p in pack.rglob('*') if p.is_file() and p.name!='SHA256SUMS');(pack/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(pack))+'\n' for p in files))
shutil.copytree(pack,target)
for line in (target/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);assert hashlib.sha256((target/n).read_bytes()).hexdigest()==h
print(json.dumps({'public_review_pack':str(target),'file_count':len(files)+1,'size_bytes':sum(p.stat().st_size for p in target.rglob('*') if p.is_file()),'canonical_hardware':r['canonical_RTL_commit']}))
