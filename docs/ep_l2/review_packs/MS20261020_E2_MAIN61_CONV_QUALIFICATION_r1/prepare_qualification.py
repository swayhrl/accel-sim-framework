"""E2 delta-specific 11+7 review and exact Conv specs, no build or native replay."""
from pathlib import Path
import sys,json,time,copy,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;PACKS=P.parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
import run as legacy
from headroom_config import options
OFF=PACKS/'MS20261020_E2_MAIN61_OFF_r1';TAKE=PACKS/'MS20261020_E2_TAKEOVER_r1'
PRIOR=PACKS/'MS20261020_E_NEW773_MAIN_SF_QUALIFICATION_r1';OLDG=PACKS/'MS20261020_E_NEW773_INTAKE_r1/gates'
A=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1/docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1')
NEW=PACKS/'MS20261020_E_WAD_ROLLBACK_NATIVE_REPAIR_r1/INDEPENDENT_NATIVE_RESULT.json'
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def prepare():
 release=read(A/'RELEASE.json');source=release['source_identity'];native=read(NEW);by={t['case']:t for t in native['tests']}
 assert len(by)==17 and native['candidate_source_identity']==source
 core=release['production_source_path'];delta=git(core,'diff','--name-only','27ec10bda848e4929181c60a7cbb40d6b007945c',source['core_source_commit'],'--','src','libcuda','CMakeLists.txt')
 assert delta=='src/gpgpu-sim/gpu-cache.cc'
 # Independently establish unchanged input/RO allocation, bank arbiter and directory code.
 unchanged={}
 for name in ['src/abstract_hardware_model.cc','src/cuda-sim','src/gpgpu-sim/ep-l2-ro-transactions.h','src/gpgpu-sim/l2cache.cc','src/gpgpu-sim/ep-l2-tvd-directory.h','src/gpgpu-sim/ep-l2-tvd-bank-identity.h']:
  old=git(core,'rev-parse','27ec10bda848e4929181c60a7cbb40d6b007945c:'+name);new=git(core,'rev-parse',source['core_source_commit']+':'+name);assert old==new;unchanged[name]=new
 scope=read(PRIOR/'RETAINED_COMPLETE_INPUT_SCOPE.json');scope.update(at_unix=time.time(),new_source_identity={k:source[k] for k in scope['new_source_identity']},previous_input_scope_chain=ref(PRIOR/'RETAINED_COMPLETE_INPUT_SCOPE.json'),new_producer_identity_review=ref(OFF/'PRODUCER_IDENTITY_REVIEW.json'),new_native_execution=ref(NEW),changed_input_interface_review='Only own-pending WAD check order changes in preview_access. Complete inputparser/ISA/address generator, trace framework and vendor unchanged; source-tree and archive-member identity proof retained. No new SASS numeric-data claim. E17 newly applicable affected native evidence covers dirty WAD128 own-pending retry/rollback, partial sectors, bank retry, physical clocks and combined RO; exact prior detailed-DRAM modes/hostprefill and input evidence are retained only for unchanged mechanisms. No prior full-app endpoint or OFF is inherited.')
 for t in scope['source_trees']:
  if t['new_commit']=='27ec10bda848e4929181c60a7cbb40d6b007945c':t['new_commit']=source['core_source_commit']
  t['new']=git(t['repository'],'rev-parse',t['new_commit']+':'+t['path']);assert t['new']==t['old'],t
 c.write_json(P/'RETAINED_COMPLETE_INPUT_SCOPE.json',scope)
 review=dict(schema='E2_MAIN61_NATIVE_DELTA_APPLICABILITY_REVIEW_V1',reviewed_by='E2',source_identity=source,at_unix=time.time(),changed_production_files=[delta],unchanged_source_objects=unchanged,production_delta=ref(TAKE/'PRODUCTION_DELTA.patch'),producer_identity_review=ref(OFF/'PRODUCER_IDENTITY_REVIEW.json'),current_E17=ref(NEW),archive_member_proof=ref(TAKE/'RECEIPT.json'),policy='Retain prior exact native assertions for unchanged functions. Do not inherit prior failed application or OFF. Replace prior same-case combined/observer executions with current E17 and add current dirty WAD/retry/rollback/bank evidence to affected gates. Extra r35 joint fixture remains FAILED/unqualified; no scope expansion.',new_native_runs=0,new_builds=0)
 c.write_json(P/'DELTA_APPLICABILITY_REVIEW.json',review)
 additions={
 'finite_wbuf':['new_dirty_WAD128_drain','new_FT_OFF_native_multi_consumer','new_legacy_credit_rollback'],
 'requester_exact_once':['new_bank_retry_one_token','new_combined_same_address','new_dirty_WAD128_drain'],
 'sector_reference_data':['new_dirty_bank_capacity_and_partial','new_TVD_credit_rollback','new_legacy_credit_rollback','new_combined_shared_pool'],
 'stale_fill':['new_combined_same_address','new_combined_host_update'],
 'resource_closure':['new_dirty_WAD128_drain','new_warm4096_WAD128_drain','new_combined_shared_pool','new_combined_native_ro_mux'],
 'wb_lifecycle':['new_dirty_WAD128_drain','new_TVD_credit_rollback','new_legacy_credit_rollback','new_combined_pinned_wb'],
 'bank_service':['new_A1_UID_Bank_mode1','new_A1_UID_Bank_mode2','new_dirty_bank_capacity_and_partial','new_bank_retry_one_token'],
 'physical_bank_clock':['new_warm4096_WAD128_drain','new_A1_UID_Bank_mode1','new_A1_UID_Bank_mode2'],
 'memcpy_payload_identity':['new_TVD_credit_rollback','new_legacy_credit_rollback'],
 'mode_legality':['new_FT_OFF_native_multi_consumer','new_combined_fallback'],
 'shared_payload_lifecycle':['new_dirty_WAD128_drain','new_TVD_credit_rollback','new_combined_shared_pool','new_combined_pinned_wb'],
 'shared_directory_cost_and_full':['new_dirty_WAD128_drain','new_dirty_bank_capacity_and_partial','new_combined_shared_pool'],
 'pinned_victim_wb_completion_identity':['new_combined_pinned_wb','new_dirty_WAD128_drain'],
 'ro_tag_reuse_late_sector_identity':['new_combined_same_address','new_combined_same_address_observer'],
 'ro_victim_same_address_and_host_invalidation':['new_combined_host_update','new_combined_same_address'],
 'backpressure_complete_quiescence':['new_dirty_WAD128_drain','new_bank_retry_one_token','new_combined_shared_pool','new_combined_native_ro_mux'],
 'tm_trigger_default_off_and_illegal_combinations':['new_combined_fallback','new_combined_host_update','new_FT_OFF_native_multi_consumer']}
 (P/'gates').mkdir(exist_ok=True)
 for f in OLDG.glob('*.json'):
  old=read(f);gate=old['gate'];retained=[];affected=[]
  for t in old['actual_cases']:
   replacement=by.get('new_'+t['case'])
   if replacement:affected.append(replacement);continue
   assert t['execution_expectation']=='PASS' and c.digest(t['raw_log'])==t['raw_log_sha256']
   assert c.digest(t['command'][0])==t['native_binary_sha256']
   retained.append(dict(t,applicability='RETAINED_UNCHANGED_ASSERTION_SCOPE_PLUS_CURRENT_WAD_DELTA_TESTS; not current-main full-application evidence'))
  affected=list({t['case']:t for t in affected+[by[n] for n in additions[gate]]}.values())
  for t in affected:
   assert t['actual_exit']==0 and t['expectation_verified'] and c.digest(t['raw_log'])==t['raw_log_sha256']
   assert all(ok and text in Path(t['raw_log']).read_text() for text,ok in t['terminal_checks'].items())
  record=dict(schema='E2_MAIN61_ORIGINAL_NATIVE_GATE_REVIEW_V1',gate=gate,status='PASS',production_driven=True,source_identity=source,reviewed_by='E2',reviewed_unix=time.time(),prior_gate_reference=ref(f),delta_applicability_review=ref(P/'DELTA_APPLICABILITY_REVIEW.json'),retained_unchanged_native_assertions=retained,current_affected_native=affected,current_native_manifest=ref(NEW),scope='Original frozen gate only; current WAD retry/rollback and bank/combined assertions supplement unchanged retained tests. No old main773 application or OFF qualification inherited. Additional B/C joint scenario not qualified.')
  c.write_json(P/'gates'/f.name,record)
 assert len(list((P/'gates').glob('*.json')))==17
 print('17_REVIEWED_NATIVE_GATES_NEW_SOURCE_OFF_STILL_REQUIRED')
def finalize():
 coord=c.Coordinator();snap=coord.snapshot();release=read(A/'RELEASE.json');source=release['source_identity'];assert snap['final_source_identity']==source and snap['controller']['state']=='STOPPED'
 record=snap['native_off_controls_by_binary'][source['binary_sha256']];off=record['result'];assert off['status']=='COMPLETE_VALID' and c.digest(off['path'])==off['sha256']
 actual=read(off['path']);cp=read(OFF/'CHECKPOINT.json');assert actual['source_identity']==source and actual['old_all_off_equivalence']=='PASS' and actual['actual_metrics']==dict(cycle=73873,insn=56000000) and actual['seven_csv_sha256']==cp['csv_sha256']
 gate=dict(schema='E2_MAIN61_ORIGINAL_OFF_ACTUAL_GATE_V1',gate='old_all_off_equivalence',status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),source_identity=source,control_result=off,actual_metrics=actual['actual_metrics'],seven_csv_sha256=actual['seven_csv_sha256'],scope='New main61 actual full vectorAdd4M baseline equivalence, native exit0,73873cycles/56000000insn,64sliceclosure,sevenCSVbyteequal; original contingency8 charged one; qualification control only.')
 c.write_json(P/'gates/old_all_off_equivalence.json',gate)
 q=read(PRIOR/'convolutionSeparable_QUALIFICATION.json');q.update(schema='E2_MAIN61_INDEPENDENT_ORIGINAL11_PLUS7_QUALIFICATION_V1',source_identity=source,binary_path=release['binary_path'],qualified_unix=time.time(),status='INDEPENDENTLY_QUALIFIED',supersedes_held_registration='NEW_SOURCE_ONLY; every prior qualification/HOLD/failure/withdrawal preserved',native_execution_receipt=ref(NEW),producer_fixture_scope=dict(production_main_source=source['core_source_commit'],independent_E17_exact_current_archive=True,fixture_only_repair='E test-only injected-read completion with original rollback/data/drain assertions unchanged',retained_unaffected_evidence=ref(P/'DELTA_APPLICABILITY_REVIEW.json')))
 for name in q['gates']:
  path=P/'gates'/(name+'.json');assert read(path)['status']=='PASS';q['gates'][name]=dict(status='PASS',production_driven=True,evidence_path=str(path),evidence_sha256=c.digest(path))
 q['default_off_equivalence']=q['gates']['old_all_off_equivalence'];q['producer_release']=dict(**ref(A/'RELEASE.json'),publication_commit='44ebe13890c8e0402895e890cf2000d01513f836',source_identity=source)
 q['build_log']=release['build_log'];q['producer_test_manifest']=release['producer_test_manifest'];q['input_scope_admission']['retained_input_scope']=ref(P/'RETAINED_COMPLETE_INPUT_SCOPE.json')
 q['scope_note']='Formal A2 exact d010/main61. E17/26 actual independent affected-native retained, original source-disjoint detailed DRAM/RO modes and hostprefill/ref tests revalidated by delta/tree/archive review. New-source OFF actual full baseline equivalence. Original11+7 minimum gates only, S/F for complete convolutionSeparable, fixed1168 W/V/T/M and certified TRACE_MODEL_CLOSED_WORLD RO. Extra r35 joint scenario remains failed/unqualified; no numeric SASS data-value claim, no cross-binary OFF/endpoint inheritance.'
 # Limit independent qualification to the first authorized paired input and profiles.
 q['supported_profiles']={k:q['supported_profiles'][k] for k in ['S','F']}
 qp=P/'convolutionSeparable_QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp);rows=[];keys=[]
 for profile in ['S','F']:
  spec=read(PACKS/'MS20261020_E_WAD_ROLLBACK_NATIVE_REPAIR_r1'/('NEXT_CONV_'+profile+'_SPEC_DRAFT.json'))
  for k in ['preparation_status','required_input_scope_rebinding']:spec.pop(k,None)
  spec.update(qualification_id=qid,input_scope_admission=q['input_scope_admission'],preparation_status='FORMAL_SOURCE_OFF_AND_18_GATES_PASSED_READY_FOR_ORIGINAL_CONTROLLER')
  for asset in spec['auxiliary_assets']:
   if asset['name']=='current_input_scope_binding.json':asset['path']=str(P/'RETAINED_COMPLETE_INPUT_SCOPE.json')
  configs=legacy.asset_manifest(spec['configs'],ordered=True);assets=legacy.asset_manifest(spec['auxiliary_assets']);traces=legacy.asset_manifest(spec['trace_files'])
  spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
  effective=options([x['path'] for x in spec['configs']]);assert effective==spec['profile_semantics']['effective_options'];assert spec['profile_semantics']==q['supported_profiles'][profile]
  changes=spec['profile_semantics']['comparison_variable_options'];invariant=dict(source=source,trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in changes},comparison_variable_options=sorted(changes))
  spec['comparison_invariants_sha256']=legacy.content_hash(invariant)
  atomic=legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],traces);originalclient=read(c.SHARED/'CLIENT_CONTRACT.json')
  legacy.validate_native_legacy_semantic_proof(spec,spec['input_scope_admission'],traces,binding=originalclient['native_legacy_semantic_proof'])
  sp=P/('convolutionSeparable_'+profile+'_SPEC.json');c.write_json(sp,spec);audit=runner.inspect(spec,coord)
  c.write_json(P/('convolutionSeparable_'+profile+'_PREFLIGHT.json'),dict(audit,complete_atomic_scope=atomic));rows.append(ref(sp));keys.append(c.run_key(spec['identity']))
 queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=1792433922.9336863,specs=rows,pairs=[dict(pair_id='V2_MAIN_convolutionSeparable_S_F_MAIN61',left_run_key=keys[0],right_run_key=keys[1],mechanism='TRADITIONAL_STATIC_WB16_VS_FIXED_W_V_T_M_1168_SAME_MAIN61')])
 c.write_json(P/'convolutionSeparable_QUEUE.json',queue)
 c.write_json(P/'QUALIFICATION_RECEIPT.json',dict(status='INDEPENDENT_ORIGINAL11_PLUS7_PASS_CONV_SF_READY',source_identity=source,at_unix=time.time(),actual_starts=snap['actual_starts'],original_OFF=off,qualification_id=qid,qualification=ref(qp),queue=ref(P/'convolutionSeparable_QUEUE.json'),no_FWT_queue_or_dispatch=True))
 print(json.dumps(dict(status='MAIN61_OFF_AND18GATES_PASS_CONV_READY',qualification_id=qid)))
if __name__=='__main__':
 {'prepare':prepare,'finalize':finalize}[sys.argv[1]]()
