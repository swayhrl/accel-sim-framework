"""Prepare original four MAIN S/F inputs from retained complete proofs; no simulator."""
from pathlib import Path
import json,sys,copy,time,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;PACKS=P.parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
import run as legacy
from headroom_config import options
COMPAT=PACKS/'MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1';CONV=PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1';BASE=PACKS/'MS20261020_E_MAIN_SF_QUALIFICATION_r1';REV=PACKS/'MS20261020_E_REMAINING_SIX_ORACLE_REVIEW_r1'
SELS={'vectorAdd_4M':'D_V2_vectorAdd_4M','cfd_097k':'D_V2_cfd_097k','dwt2d':'D_V1_dwt2d','sad':'D_V2_sad'}
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p.resolve()),sha256=c.digest(p))
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def main():
 coord=c.Coordinator();snap=coord.snapshot();source=snap['final_source_identity'];assert source['core_source_commit']=='d010911e3174a3764791183cd108fe4664ba8731'
 baseline=dict(at_unix=time.time(),actual_starts=snap['actual_starts'],T0=snap['t0_unix'],controller=snap['controller'],output_usage=c.output_usage(),resources=c.local_resources(),source_identity=source,original_matrix=snap['full_system_matrix'])
 baseline=read(P/'CONTINUATION_BASELINE.json') if (P/'CONTINUATION_BASELINE.json').exists() else baseline;c.write_json(P/'CONTINUATION_BASELINE.json',baseline);(P/'configs').mkdir(exist_ok=True);allrows=[]
 for workload,sid in SELS.items():
  wp=P/workload;wp.mkdir(exist_ok=True);selected=snap['input_selections'][sid];assert c.digest(selected['path'])==selected['sha256'];inp=selected['selection']['full_input_identity'];src=inp['runtime_independent_input_source']
  traces=legacy.asset_manifest(src['trace_files']);assert legacy.content_hash(traces)==inp['trace_content_sha256'];legacy.validate_trace_closure(dict(trace_files=src['trace_files'],entry_trace_name=src['entry_trace_name']))
  review=read(REV/(workload+'_INPUT_REVIEW.json'));assert review['trace_content_sha256']==inp['trace_content_sha256']
  candidate=read(review['candidate_path']);assert c.digest(review['candidate_path'])==review['candidate_sha256']
  manifest=Path(review['manifest_path']);assert c.digest(manifest)==review['manifest_sha256'];ranges=manifest.parent/'certified_ranges.csv';assert c.digest(ranges)==review['artifacts']['certified_ranges.csv']['sha256']
  for name,row in review['artifacts'].items():assert c.digest(manifest.parent/name)==row['sha256']
  scope=copy.deepcopy(read(CONV/'RETAINED_COMPLETE_INPUT_SCOPE.json'))
  if workload=='dwt2d':
   original=PACKS/'MS20261020_E_NEW_INPUT_NATIVE_SCOPE_r1/SCOPE.json';old=read(original);w=next(w for w in old['workloads'] if w['selection_id']==sid);assert w['status']=='COMPLETE_ORIGINAL_NATIVE_NONATOMIC_BYTE_AND_ZERO_MASK_SCOPE_PASS' and w['trace_manifest']==traces
   assert all(x['atomic_absence'] and x['status']=='COMPLETE_NATIVE_OPCODE_COVERAGE' for x in w['files']);assert sum(x['active_lane_instruction_records'] for x in w['files'])==inp['expected_full_instructions']
   oldid={k:old['source_identity'][k] for k in scope['new_source_identity']};producer='75707624b980df5e3bbb809c76a31cf1b34501a1'
   atomic=dict(schema='E2_NORMALIZED_RETAINED_DWT_COMPLETE_INPUT_PROOF_V1',status='COMPLETE_NATIVE_OPCODE_AUDIT',input_scope='COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS',identity=dict(oldid,trace_content_sha256=inp['trace_content_sha256'],workload=workload),producer_publication=producer,tool_sha256=old['tool_sha256'],trace_content_manifest=traces,global_atomic_records_with_repeats=0,shared_atomic_records_with_repeats=0,trace_files=w['files'],complete_byte_and_zero_mask_scope='PASS_FROM_RETAINED_COMPLETE_DWT_ROW',original_report=ref(original),normalization='Only completed DWT row normalized for existing runner contract. Aggregate BTREE/DWT report remains FAILED due to Btree; Btree not promoted.')
   ap=wp/'ATOMIC_SCOPE.json';c.write_json(ap,atomic);scope.update(original_source_identity=oldid,original_producer_publication=producer,retained_atomic_report_sha256=[c.digest(ap)],retained_native_byte_proof_sha256=None)
   for tree in scope['source_trees']:
    tree['old_commit']=oldid['framework_source_commit'] if tree['path'].startswith('gpu-simulator/') else oldid['core_source_commit'];tree['old']=git(tree['repository'],'rev-parse',tree['old_commit']+':'+tree['path']);assert tree['old']==tree['new']
   byte_evidence=ref(original)
  else:
   ap=PACKS/'FT20261017_LANE5_A1_B1_ELEVEN_GATES_r1'/(workload+'_ATOMIC_SCOPE_r1.json');atomic=read(ap);assert atomic['status']=='COMPLETE_NATIVE_OPCODE_AUDIT' and atomic['trace_content_manifest']==traces;assert c.digest(ap) in scope['retained_atomic_report_sha256'];assert sum(x['active_lane_instruction_records'] for x in atomic['trace_files'])==inp['expected_full_instructions'];byte_evidence=ref(ap)
  scope.update(at_unix=time.time(),scope='Original complete byte/opcode/native-format evidence retained for this registered input; no prior runtime acceptance inherited.',current_workload=workload,complete_native_input_proof=byte_evidence)
  scopepath=wp/'RETAINED_INPUT_SCOPE.json';scope=read(scopepath) if scopepath.exists() else scope;c.write_json(scopepath,scope)
  admiss=dict(application_input_scope='FULL_NATIVE_NONATOMIC_ONLY',atomic_input_auditor_sha256=atomic['tool_sha256'],producer_publication_commit=atomic['producer_publication'],retained_input_scope=ref(scopepath),complete_native_input_proof=byte_evidence)
  semantic=dict(status='RETAINED_COMPLETE_INPUT_SEMANTICS_REVIEWED_NOT_RUNTIME_PASS',workload=workload,source_identity=source,proof=byte_evidence,source_tree_binding=ref(scopepath),preregistration=dict(path=selected['path'],sha256=selected['sha256']),capture_provenance=src.get('capture_provenance'),source_revision=src.get('source_revision'),scope='Frozen complete trace replay. Capture/source gaps remain disclosed; no from-source reproduction or numeric SASS output claim. Input was preregistered before new candidate performance.',expected_full_instructions=inp['expected_full_instructions'],input_oracle_review=ref(REV/(workload+'_INPUT_REVIEW.json')))
  sempath=wp/'NATIVE_INPUT_SEMANTICS.json';c.write_json(sempath,semantic)
  q=read(COMPAT/'convolutionSeparable_QUALIFICATION.json');q.update(schema='E2_ORIGINAL_MAIN_INPUT_SF_QUALIFICATION_V1',qualified_unix=(read(wp/'QUALIFICATION.json')['qualified_unix'] if (wp/'QUALIFICATION.json').exists() else time.time()),input_selection_id=sid,input_scope_admission=admiss,scope_note=f'Exact main61 original11+7/OFF/native17 source gates reused for original preregistered {workload} full S/F. Complete input proof and unchanged source trees independently bound. Trace-model closed-world certificate specific to this input; all fixed W/V/T/M semantics unchanged. No old application endpoint inherited; extra joint fixture stays unqualified. Capture/source revision gaps disclosed by original preregistration remain frozen-trace reproducibility limits. No numeric SASS output validation claim.')
  template={profile:read(CONV/('convolutionSeparable_'+profile+'_SPEC.json')) for profile in ['S','F']};specs={}
  for profile in ['S','F']:
   spec=copy.deepcopy(template[profile]);sem=copy.deepcopy(spec['profile_semantics']);rr=sem['readonly_input_review'];rr.update(certified_model_lines=review['counts'].get('CERTIFIED_RO',{}).get('lines',0),commandlist=src['entry_trace_path'],commandlist_sha256=c.digest(src['entry_trace_path']),input_review_path=str(REV/(workload+'_INPUT_REVIEW.json')),input_review_sha256=c.digest(REV/(workload+'_INPUT_REVIEW.json')),manifest_path=str(manifest),manifest_sha256=c.digest(manifest),ranges_path=str(ranges),ranges_sha256=c.digest(ranges),trace_content_sha256=inp['trace_content_sha256'])
   cfg=P/'configs'/(workload+'_'+profile+'.config');content=(BASE/'configs'/('convolutionSeparable_'+profile+'.config')).read_text()
   content=content.replace('convolutionSeparable_r1/oracle','PLACEHOLDER_ORACLE') if profile=='F' else content
   if profile=='F':
    previous=template[profile]['profile_semantics']['readonly_input_review'];content=(BASE/'configs'/('convolutionSeparable_'+profile+'.config')).read_text().replace(previous['manifest_path'],str(manifest)).replace(previous['manifest_sha256'],c.digest(manifest)).replace(previous['ranges_path'],str(ranges)).replace(previous['ranges_sha256'],c.digest(ranges))
   cfg.write_text(content);spec['configs'][-1]['path']=str(cfg);sem['effective_options']=options([x['path'] for x in spec['configs']]);q['supported_profiles'][profile]=sem
   spec.update(parser=q['terminal_parser'],profile_semantics=sem,selection_id=sid,condition_id='V2_'+workload+'_'+profile,comparison_group='V2_MAIN_'+workload,budget_bucket='seven_workload_common_S_F',input_scope_admission=admiss,atomic_input_scope=ref(ap),auxiliary_assets=[dict(name='readonly_manifest.json',path=str(manifest)),dict(name='readonly_ranges.csv',path=str(ranges)),dict(name='atomic_scope.json',path=str(ap.resolve())),dict(name='native_input_semantics.json',path=str(sempath)),dict(name='current_input_scope_binding.json',path=str(scopepath))],trace_files=src['trace_files'],entry_trace_name=src['entry_trace_name'],preparation_status='E_QUALIFIED_ORIGINAL_MAIN_INPUT_READY')
   for k in ['native_legacy_semantic_proof','contingency_review','previous_failed_revision_retained']:spec.pop(k,None)
   spec['identity'].update(workload=workload,trace_content_sha256=inp['trace_content_sha256']);specs[profile]=spec
  qp=wp/'QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp);entries=[];keys=[]
  for profile,spec in specs.items():
   spec['qualification_id']=qid;configs=legacy.asset_manifest(spec['configs'],ordered=True);assets=legacy.asset_manifest(spec['auxiliary_assets']);spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']));changes=spec['profile_semantics']['comparison_variable_options'];effective=spec['profile_semantics']['effective_options']
   spec['comparison_invariants_sha256']=legacy.content_hash(dict(source=source,trace=inp['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in changes},comparison_variable_options=sorted(changes)))
   atomic_review=legacy.validate_atomic_input_scope(spec,admiss,traces);sp=wp/(profile+'_SPEC.json');c.write_json(sp,spec);audit=runner.inspect(spec,coord);c.write_json(wp/(profile+'_PREFLIGHT.json'),dict(audit,complete_atomic_scope=atomic_review));entries.append(ref(sp));keys.append(c.run_key(spec['identity']))
  queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=1792433922.9336863,specs=entries,pairs=[dict(pair_id='V2_MAIN_'+workload+'_S_F_MAIN61',left_run_key=keys[0],right_run_key=keys[1],mechanism='PREREGISTERED_MAIN_S_VS_FIXED_W_V_T_M_SAME_MAIN61')]);queuepath=wp/'QUEUE.json';c.write_json(queuepath,queue)
  allrows.append(dict(workload=workload,selection_id=sid,qualification=ref(qp),qualification_id=qid,queue=ref(queuepath),expected_full_instructions=inp['expected_full_instructions'],trace_bytes=sum(t['bytes'] for t in traces),kernel_instances=atomic.get('ordered_kernel_instances',len(atomic.get('trace_files',[]))),runtime_result_cap_per_attempt=384*2**20))
  print('QUALIFIED',workload,qid,flush=True)
 old=snap['full_system_matrix'];matrix=copy.deepcopy(old['matrix']);order=list(SELS)
 for cell in matrix['conditions']:
  if cell['workload'] in order and cell['group']=='MAIN':cell['priority']=2+order.index(cell['workload'])
  elif cell['group']!='MAIN':cell['priority']=10+cell.get('priority',0)
 c.policy_v2.validate_matrix(matrix);c.write_json(P/'MATRIX_32_PRIORITY_REVISION.json',matrix)
 plan=dict(schema='E2_ORIGINAL_MAIN_ROLLING_PLAN_V1',at_unix=time.time(),prepared_by='E2',source_identity=source,original_matrix=old,new_matrix=ref(P/'MATRIX_32_PRIORITY_REVISION.json'),priority_order=order,priority_reason='Vector56M instructions first (known OFF cost689.6s), then CFD143M, DWT149M, SAD158M. Full raw-byte sizes and kernel counts published as secondary cost proxies. Original MAIN conditions precede unsupported/unqualified ablations. No use of observed candidate F speedup for ordering; original seven-input denominator/Btree HOLD retained.',conditions=allrows,maximum_actual_starts=40,contingency_used=8,contingency_remaining=0,planned_new_starts=8,expected_cumulative_after=20,no_native_rebuild_or_replay=True,default_max_simulators=2,live_admission_each_batch=True,user_authorization='Continue original E2 campaign; rolling original MAIN S/F, public priorities, original T0/40/resource policies. Independent exploration requires separate eligibility and remaining budget.')
 c.write_json(P/'PLAN.json',plan)
 print('FOUR_MAIN_PAIRS_READY_NO_APPLICATION_STARTS')
if __name__=='__main__':main()
