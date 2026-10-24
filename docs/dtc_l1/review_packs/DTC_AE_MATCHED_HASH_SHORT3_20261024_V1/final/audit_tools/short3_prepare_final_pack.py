"""Build reviewable final evidence, report and operational notes from qualified data."""
import pathlib,json,shutil,subprocess,hashlib,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1';N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def main():
 r=read(T/'analysis/COMPLETE_RESULT.json');assert r['status']=='ALL_12_WHOLE_INPUT_POINTS_STRICT_ARCHIVE_RESTORE_RECHECKED'
 final=D/'final';final.mkdir()
 cp(T/'analysis/COMPLETE_RESULT.json',final/'COMPLETE_RESULT.json')
 cp(T/'analysis/PAIRED_COUNTERS.json',final/'PAIRED_COUNTERS.json')
 request=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 for row in r['points']:
  cell=row['cohort'];e=final/'evidence'/cell;e.mkdir(parents=True)
  intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output'])
  for name in ['AEFAIR_STRICT.json','NATIVE_EXIT.json','NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:cp(out/name,e/name)
  for name in ['INTENT','DONE']:cp(T/'control/qualification_ledger'/(cell+'.'+name+'.json'),e/(name+'.json'))
  cp(T/'control'/(cell+'_SPEC.json'),e/'ORIGINAL_SPEC.json')
  cp(T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json'),e/'SCIENCE_QUALIFICATION.json')
  cp(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'),e/'ARCHIVE_RECEIPT.json')
  bundle=P(row['archive']['target_mount_path'])
  for name in ['SOURCE_MANIFEST.json','ARCHIVE_INDEX.json','COMMIT.json','PATH_MAP.json','RESTORE_VERIFIED_NATIVE_TARGET.json']:cp(bundle/name,e/('archive_'+name))
  for i,conf in enumerate(read(T/'control'/(cell+'_SPEC.json'))['configs']):cp(P(conf['path']),e/f'config-{i}.config')
 for p in (T/'control').glob('*.json'):
  if p.name.startswith('PREIMAGE_'):continue
  cp(p,final/'authority'/p.name)
 for folder in ['release','release_floor5_v3']:
  for p in (T/'control'/folder).glob('*.json'):cp(p,final/'authority'/folder/p.name)
 for p in [N/'control/CURRENT_SCIENCE_EPOCH.json',N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json']:cp(p,final/'authority'/('CURRENT_'+p.name))
 cp(N/'bin/native',final/'authority/CURRENT_NATIVE_ENTRY.sh')
 for p in (T/'tools').glob('*.py'):cp(p,final/'audit_tools'/p.name)
 for p in (T/'audit_sources').glob('*.py'):cp(p,final/'audit_tools/preparation_sources'/p.name)
 table='| Workload | CM | CH | DM | DH | C+ cycles reduction | DTC cycles reduction | R |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
 for s in r['summaries']:
  c=s['cycles'];table+=f"| {s['workload']} | {c['CM']:,} | {c['CH']:,} | {c['DM']:,} | {c['DH']:,} | {100*s['conventional_cycle_reduction']:.6f}% | {100*s['DTC_AE_cycle_reduction']:.6f}% | {s['interaction_R']:.9f} |\n"
 table+='\nThe paired counter file compares existing printed exports only within the same design. Ordinary L1D-array counters and DTC logical Tag counters have different populations across designs; missing fields remain UNAVAILABLE rather than zero. No unique causal explanation is assigned from these diagnostics.\n'
 report='''# Three short workloads: matched traditional-cache hash versus DTC AE

2026-10-24. DTC-MAIN, sole174-new epoch2 native science entry. The requested three short workloads have each completed four fresh whole-input model runs. All12 passed exact whole-input scientific acceptance, genuine164 full-result archive verification and independent174-new ext4 restore; the complete consumer repeated every strict check and archive/restore entry check.12/12 starts consumed,0remaining,0scientific retries. Source outputs remain SOURCE_KEEP.

## Results

CM is conventional linear;CH conventional bank-preserving XOR;DM DTC AE0;DH DTC AE1. Cycle reduction is1-ON/OFF. Speedups areCM/CH andDM/DH;interactionR=(DM/DH)/(CM/CH).R compares within-design effects under the stated differing geometries, not equal-area unique-DTC causality.

'''+table+'''
The full exact fractions, per-kernel populations, identities and immutable archive roots are in COMPLETE_RESULT.json. The previous independent GEMM comparison remains CM1,511,333/CH1,395,216/DM1,071,405/DH826,089, conventional7.683085% and DTC22.896664% fewer cycles,R1.197314142. It is historical context for these new results, never pooled into the frozen old AG8R1 selection or relabeled as one of these three inputs.

## Input and platform scope

NN(nearest neighbor),DWT2D andMRI-Q were fixed before outcomes as the three lowest original OO cycle counts among the eight original workloads without input-interpretation HOLD, excluding already-studied GEMM. This is a convenience sample of short complete historical inputs, not a randomized holdout or representative benchmark suite. Full trace members were SHA256 rehashed on genuine164 and joined to the original whole-body audit before launching. NN:1kernel/168CTA/1,284,872instructions;DWT2D:10kernels/4,654CTA/148,684,429instructions;MRI-Q:4kernels/390CTA/1,411,757,056instructions. No kernel truncation or instruction-limit termination was used.

All12 use exactly the completed GEMM binary ab6c717dcbe7932af8bbb6dfbad0b1df9ec0ba447c067085cb92855fb8628a8e,Core2e3bef4364e578cddd0e881c0baace2e51c55930,Frameworkcfd3ff56d7ba6642dab6c7710ec4f6065168174e,library/toolchain and four configuration byte sequences. Platform is Volta-basedFAST64:64SM,1410:1410:1410:850 clocks and20memory controllers, with custom cache models; it is not a stockV100. ConventionalC+ uses32setsx24ways normal96KiB;DTC uses64setsx8ways logical Tag,80KiB physical pool+16KiB ordinary sector array and activeOO128. Cross-design Tag/PIB/service paths and unified96vs128KiB options differ. Both XOR variants are the same bank-preserving row-hash family but different set counts imply different address-to-set functions. Extra modeled hash delay iszero by assumption. Physical equal-area/PPA/hash delay, native numerical values and broad workload generality remain unproven.

## Execution, acceptance and engineering corrections

Every model used one CPU,16GiB address-space limit,21600s upper wall bound and a tightened32MiB result cap. The original BA authenticated semantic progress/resource decision modules were retained. The first original-policy sample is taken immediately after binding a short-lived model, with subsequent10s sampling unchanged. The complete audit records resource warnings and maximum sampling gaps; warning-only shared IO is not a scientific null result or evidence of process-exclusive IO attribution. Any STOP would disqualify performance; none of the accepted12 has a STOP.

Two workflow defects were corrected with preserved preimages. The first metadata worker lacked the central-registry path mapping and stopped before any INTENT/model fork. The new path now resolves to the same sole central authority. The second worker completed NN-DM naturally, then the independent strict check held because generated expected metadata retained GEMM's trace path and line-split a quoted multiline DRAM timing string. Actual original input/argv/config bytes were correct. The separate pinned resolver parses the unchanged config with quoted multiline semantics and binds trace from unchanged argv. Exactly those two expected metadata fields change; all original specs and consumed runtime identities remain immutable. The existing NN-DM output was independently revalidated, archived and restored, thenR3 continued exactly11 never-started cells. No model rerun/refund, added budget, input substitution or simulation-parameter tuning occurred. The original two stopped metadata controllers and their evidence remain preserved.

Per kernel, acceptance verifies ordered names/UIDs/exact input opens/all original commands and memcpy, full active instructions/cumulative CTA, exact270 effective options, natural process+semantic terminal, ownership drains and conservation. DTC calls the unchanged BA full-input parser. Whole raw SHA, actual mapped binary/argv/runtime pins and original resource policy join every result to its one consumed UUID. Archive uses the pinned immutable bundle protocol, whole-file reopen SHA and independent native restore before the next INTENT. Native174-new restore is not native164 execution.

## Preserved scientific history and delivery

All prior native requests, old scientific histories, original onboarding manifest and completed GEMM review pack remain unchanged. Original44 roles and HOLDs, negativeBICG/GESUMMV, originalHotspot/2D/Btree/LUD interpretation limits, modern128KiB physical-accountingHOLD and oldAG8R1 remain. Englishv0.23 is the last user-confirmed paper mother; its actual package is unavailable and no manuscript promotion or invented DC/PPA figures occurs.

Every raw point already has a complete verified genuine164 archive and independent native restore, indexed here. This source scientific commit will also be exported with exact runtime/config/protocol evidence in a separate COPY_ONLY final review bundle. A later receipt closes that delivery step without a self-referential archive. No further scientific starts are authorized by this completed request.
'''
 report=report.replace('thenR3 continued exactly11 never-started cells.','thenR3 resumed the original unused list. After11 models were accepted, a COPY_ONLY archive call returned shared-lockEAGAIN and the controller preserved/sealed the one unused cell. The same closedCM output was subsequently archived/restored; separately identifiedR4 skipped all11spent UUIDs and started only original unusedMRI-Q-CH. The final outbox uses bounded COPY_ONLY lock waiting. The exact owner of the original lock is not inferred from genericEAGAIN.')
 (final/'SCIENTIFIC_REPORT.md').write_text(report)
 storage_note='''\n## User storage policy applied at a closed-model boundary\n\nThe user explicitly replaced the roughly10GB admission barrier with a5GiB local safety margin and authorized migration of our own assets to genuine164 followed by verified local reclaim if needed. The separately qualified/publishedV3 target profile uses an exclusive>5GiB safety floor including monitor and unknown-project cushion, plus only exact bounded own writes and active registered foreign writes. With the conservative1GiB own result/restore/spool reservation and no active peers, admission is>6GiB. The exact BA runtime decision class already had a5GiB floor and stays unchanged. Target paired admission and outbox accounting now use the same floor without extra hardwired cushion guesses.\n\nOnly the finite metadata controller was held;MRI-Q-DH and its launch-time guard ran to natural completion. The operational profile was then activated before its archive and before the two unused conventionalMRI-Q models. No model was paused/restarted, no config/input/authorization spec changed, and budget remains12. Per-point launch receipts distinguish the first10 old operational launches from the final2 V3 launches.15 zero-model storage checks and exact source/publication pins are retained. Full actual resource traces are archived, and every accepted point passes the unchanged BA runtime decisions plus its stated operational profile. The admission update changes no simulated performance parameter.\n\n174-new and164 are fast/slow tiers of one logical asset pool. Inputs already read directly from genuine164. Safe local reclaim requires our own closed asset, immutable full-SHA archive and independent restore verification, durable custody/tier mapping and corrected consumer references before removing exact local objects. Preserve historical scientific identities and live/peer assets. No local deletion was needed or performed in this campaign;all originals remain SOURCE_KEEP.\n'''
 with (final/'SCIENTIFIC_REPORT.md').open('a') as f:f.write(storage_note)
 ops='''# Reusable complete-input matched-hash workflow

The three-input campaign is complete. Its cohort names are spent and cannot be rerun. This checklist is for preparing a future separately scoped request when the user's ongoing test-set organization is ready; it is not a dispatcher or new start authorization.

1. Name the exact workload, dataset variant and whole original kernelslist. COPY_ONLY asset readiness supplies genuine164 roots, exact ordered members and full SHA provenance. Keep original and derived inputs distinct. An asset being readable does not clear input/format scientific HOLD or qualify a current source.
2. Join full body audit to every member:kernel names,order,binary/tracer version,complete CTA/warps and active-thread instructions. Freeze all memcpy commands. Do not infer input shape from filenames or use a partial-kernel/sample subset as a whole workload.
3. Fix DM/DH/CM/CH from the same qualified binary/toolchain and four configuration byte sequences. Derive effective option expectations with quoted multiline config parsing plus exact argv; do not inherit -trace from the previous workload. Diff pairs:DM/DH onlytag_hash_bankrow;CM/CH onlydl1 hash selector. Store request/spec/config/runtime/input SHA and the intended scope before starting.
4. Use one central epoch2 authority and global science lock. In an isolated workspace, explicitly verify control/science_authority and current-epoch paths resolve to the same sole authority. Extend the existing native frontend with only exact new cohort names; retain COPY_ONLY asset and all peer/predecessor routes. Count each model at INTENT beforefork. A metadata/preflight repair never deletes a consumed INTENT or creates scientific credit.
5. Admit current physical resources with original BA semantic progress/ownership/OOM/swap/memory guards and warning-only IO semantics. Reserve all bounded result+restore growth against one physical disk pool, active registered peers and unknown-project headroom. Capture an original-policy sample immediately after short-model binding. Serialize this finite cohort; no autonomous suite expansion or retry.
6. After natural exit, independently validate every kernel and exact commands/options/full populations, mapped process/argv/input opens, semantic NATURAL and closed raw SHA. Verify conventional lifecycle and unchanged BA DTC conservation. Keep failed/STOP evidence, but never promote partial cycles. If only an expectation/parser bug is proven from frozen input/config, correct postprocessing transparently and revalidate the same closed run; do not rerun the model.
7. Archive accepted full raw output to genuine164 with immutable COMMIT-last protocol. Reopen whole archive SHA, independently restore on174-new ext4 and compare content/metadata/symlink targets. Complete this before the next INTENT; preserve source outputs. Archive receipts do not confer scientific acceptance.
8. Report per-workloadCM/CH,DM/DH andR=(DM/DH)/(CM/CH), preserving zero and adverse outcomes. Keep historical GEMM and independently derived inputs scoped separately. Cross-design geometry, modeledzero hash latency and Volta-basedFAST64 boundaries must accompany claims. New datasets need their own finite registered request and exact source/input qualification.

Audit entry for this completed campaign:tools/short3_complete_audit.py. It is read-only over science and verifies12 strict results and all archive/native restore entries; it exclusively writes a new analysis record, so inspect an existing record instead of rerunning it blindly. COMPLETE_RESULT.json and per-point evidence provide all UUIDs, raw/strict SHA, immutable archive roots and recovery paths. Raw logs/traces/binaries remain outside Git. Final review recovery receipt records the additional COPY_ONLY protocol/runtime bundle.
'''
 (final/'WORKFLOW.md').write_text(ops)
 with (final/'WORKFLOW.md').open('a') as f:f.write('\nCurrent storage policy:5GiB exclusive local safety margin includes monitor/unknown cushion;reserve exact bounded own and registered foreign writes separately. Treat174-new/164 as fast/slow capacity tiers. Migrate our closed assets with fullSHA/native restore and custody/reference checks before exact local reclaim. The native5GiB floor still applies to local writes. No reclaim was necessary in this pilot.\n')
 intake={'schema':'DTC_FUTURE_WHOLE_WORKLOAD_INTAKE_TEMPLATE_V1','template_only_not_a_run_request':True,'workload':None,'dataset_variant_id':None,'asset_catalog_id':None,'capture_architecture_and_tracer_version':None,'input_source_and_shape_evidence':None,'original_kernelslist_path':None,'original_kernelslist_sha256':None,'whole_ordered_commands_including_memcpy':[],'immutable_true164_input_root':None,'native_compatibility_path':None,'ordered_kernel_body_audit_rows':[],'required_per_kernel_fields':['ordinal','original_path','sha256','kernel_name','binary_version','trace_version','complete_CTA','active_thread_instructions','whole_warp_grid_terminal_EXIT_coverage','memory_path_and_opcode_applicability'],'whole_input_totals':{'kernels':None,'CTA':None,'active_thread_instructions':None},'source_and_runtime_compatibility_qualification':None,'scientific_input_HOLD_or_known_limits':[],'capture_native_numerical_value_evidence':'UNPROVEN_UNLESS_SEPARATELY_PROVIDED','suggested_four_arms':['CM','CH','DM','DH'],'fixed_platform_and_byte_identical_config_family':None,'finite_new_request_id_and_start_budget':None,'resource_and_output_cap_profile':None,'scientific_starts_granted_by_this_template':0}
 (final/'WORKLOAD_INTAKE_TEMPLATE.json').write_text(json.dumps(intake,indent=2)+'\n')
 (F/'DTC_MAIN_ACTIVE_GOAL.md').write_text('''# DTC-MAIN three short-workload Goal: science complete

RequestDTC_AEFAIR_SHORT3_EPOCH2_20261024_V1 is COMPLETE:NN,DWT2D,MRI-Q eachDM,DH,CM,CH;12unique complete native starts consumed,0remaining,0scientific retries. All12 strict results, genuine164 raw archives and independent174-new restores have been replayed and checked. All simulator and metadata-controller generations are gone. Runtime:/root/data/dtc_main_short3_20261024_v1. Report:docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1/final/SCIENTIFIC_REPORT.md;reusable workflow:final/WORKFLOW.md. Remaining work at this science-commit timestamp is COPY_ONLY final review recovery and publication, no simulations.

Preserve stopped pre-fork metadata controller and later expected-option metadata correction; actual configs/input/argv and original specs never changed. Existing NN-DM was postprocessed without a model rerun; continuation launched only11 unused cells. Preserve asset router, oldGEMM4/4 and historicalAG8R1/accepted/negative/HOLD. Englishv0.23 remains last confirmed mother, actual package unavailable. DTC-MAIN is the sole permanent user lane; this completed finite request grants no other workload starts.
''')
 subprocess.run(['git','-C',str(F),'diff','--check'],check=True)
 subprocess.run(['git','-C',str(F),'add','DTC_MAIN_ACTIVE_GOAL.md',str(D.relative_to(F))],check=True)
 subprocess.run(['git','-C',str(F),'commit','-m','Record three short full-workload matched hash results and workflow'],check=True)
 commit=subprocess.check_output(['git','-C',str(F),'rev-parse','HEAD'],text=True).strip();tree=subprocess.check_output(['git','-C',str(F),'rev-parse','HEAD^{tree}'],text=True).strip()
 proof={'commit':commit,'tree':tree,'report_sha256':sha(final/'SCIENTIFIC_REPORT.md'),'result_sha256':sha(final/'COMPLETE_RESULT.json'),'scope':'Scientific evidence complete; final COPY_ONLY review recovery pending'}
 with (T/'analysis/FINAL_SCIENCE_COMMIT.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
 subprocess.run(['git','-C',str(F),'bundle','create',str(T/'analysis/short3_final_science.bundle'),'hrl/dtc-aefair-short3-174new-20261024-v1','^a451357890324f60db5108e7322f852ca4de4f25'],check=True)
 print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
