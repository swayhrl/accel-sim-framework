import pathlib,json,hashlib,subprocess,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
D.mkdir();(D/'tools').mkdir();(D/'control').mkdir()
for p in sorted((T/'tools').glob('*.py')):shutil.copyfile(p,D/'tools'/p.name)
for p in sorted((T/'control').glob('*.json')):
 if p.name.startswith('PREIMAGE_'):continue
 shutil.copyfile(p,D/'control'/p.name)
readme='''# Three short-workload matched-hash workflow

User instruction on2026-10-24: run three short workloads with the same comparison and organize the process. This is one finite DTC-MAIN campaign, at most12 fresh complete-input native starts, no retries or workload cascade. It does not reopen completed GEMM or old AG8R1.

## Fixed selection before results

NN, DWT2D and MRI-Q are the three smallest original OO cycle counts among the original eight workloads without input-interpretation HOLD, excluding previously studied GEMM. Original OO cycles are6132,237887,361439 respectively; these are selection provenance, not predictions of current wall time. Full input populations:NN1kernel/168CTA/1,284,872instructions;DWT2D10kernels/4,654CTA/148,684,429instructions;MRI-Q4kernels/390CTA/1,411,757,056instructions. Every input member was fully SHA256 rehashed on the genuine164 mount and joined to the original body audit before any model start. Do not infer dataset shape or capture-native values from a filename.

## Same scientific intervention

Each workload runs DM(DTC AE0),DH(DTC AE1),CM(conventional linear),CH(conventional bank-preserving XOR), in that order. Binary, library, source and four configuration byte sequences are identical to completed GEMM; only the whole input, bound progress identities and output directory change. Volta-based FAST64 has64SM,1410:1410:1410:850 clocks,20memory controllers, and custom traditional/DTC L1. It is not a stock V100. Within each design the only effective option difference is the selected hash. Cross-design tag geometries, active ownership resources, timing paths and96vs128KiB unified option remain different. Zero extra modeled XOR latency remains an assumption, no PPA/equal-area/unique-DTC causality claim.

## Finite native process

1. COPY_ONLY input readiness and complete original member/command/body-audit identity.
2. Exact four-cell specs and explicit one-start budgets, current resource admission and one central epoch2 registry/lock.
3. Preserve the existing asset-query router and all previous science dispatch through the predecessor frontend. Add only12 exact cohort names under the same native entry.
4. Run one point on174-new ext4 with the same authenticated semantic progress and original BA resource policy. No old174 scientific execution. One CPU,16GiB address limit,21600s upper wall bound;32MiB output cap tightens the previous64MiB. All12 result+restore caps and256MiB spool reserve1GiB;7GiB floor,1GiB unknown-project headroom and current active-peer reservations remain.
5. Join actual mapped binary/argv/input file opens/progress and closed raw SHA. Verify every kernel in order, its full instructions, cumulative CTA and final lifecycle/ownership conservation; DTC uses unchanged BA full-input strict. Partial completion is never a result.
6. Qualify then archive through the pinned bundle engine to genuine164. Reopen whole-file SHA, independently restore onto174-new ext4 and compare all entries before the next model. Keep all source outputs. Native174-new restore is not native164 execution.
7. Report each workload's CM/CH and DM/DH cycle ratios and interactionR=(DM/DH)/(CM/CH). Keep zero, neutral and adverse outcomes. Do not pool historical cycles into current comparison or turn three convenience-selected small inputs into suite-wide claims.

## Qualification and outcome status

20 zero-model checks pass, including real closed GEMM replay through the new population parser, two-kernel boundary fixtures with expected rejections, all12 input/config bindings, single-option pair differences and current peer-reservation guards. The launcher now takes its first original-policy resource sample immediately after binding the native model; this lets short NN retain an observed resource decision. The BA decision algorithm and10s subsequent sampling interval are unchanged.

At this preregistration no model has started. Final result and reusable operational notes will be appended after the finite campaign. Englishv0.23 remains the last user-confirmed paper mother; the actual package is unavailable. Original44, old accepted/negative/HOLD, old AG8R1 and completed GEMM identities remain preserved.

Runtime:/root/data/dtc_main_short3_20261024_v1. Sole entry:/root/data/ep_l2_dtc_l1_native_v2/bin/native. Request:DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1. Branch:hrl/dtc-aefair-short3-174new-20261024-v1.
'''
(D/'README.md').write_text(readme)
(F/'DTC_MAIN_ACTIVE_GOAL.md').write_text('''# DTC-MAIN current finite Goal: three short matched-hash workloads

User authorized three short workloads on2026-10-24. Current finite request:DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1;NN,DWT2D,MRI-Q, each DM,DH,CM,CH, at most12 fresh native starts. Runtime:/root/data/dtc_main_short3_20261024_v1. Report/flow:docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1/README.md. No model has started at preregistration. Use the sole174-new epoch2 entry, preserve asset/peer routes, archive164 and independently restore before next point. No workload cascade or automatic retry.

Prior GEMM Goal is complete,4/4 consumed and unchanged;report:docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_EPOCH2_20261023_V1/final/SCIENTIFIC_REPORT.md. Historical AG8R1 remains2/2 consumed, F=null/O provisional; all accepted/negative/HOLD and Englishv0.23 mother identity remain. The new goal grants no other starts or paper promotion.
''')
subprocess.run(['git','-C',str(F),'diff','--check'],check=True)
subprocess.run(['git','-C',str(F),'add','DTC_MAIN_ACTIVE_GOAL.md',str(D.relative_to(F))],check=True)
subprocess.run(['git','-C',str(F),'commit','-m','Preregister three short complete-input matched hash comparisons'],check=True)
head=subprocess.check_output(['git','-C',str(F),'rev-parse','HEAD'],text=True).strip()
bundle=T/'control/short3_preregistration.bundle'
subprocess.run(['git','-C',str(F),'bundle','create',str(bundle),'hrl/dtc-aefair-short3-174new-20261024-v1','^db58c292d1304a7164587158245ccfbb69334ed9'],check=True)
print('COMMIT',head,'BUNDLE',str(bundle))
