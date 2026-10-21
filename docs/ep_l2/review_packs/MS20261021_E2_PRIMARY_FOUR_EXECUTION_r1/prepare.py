"""Independent exact profile/input preparation; no application or native execution."""
from pathlib import Path
import copy,json,sys,time,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3];PACKS=P.parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from headroom_config import options
R=PACKS/'MS20261021_E2_LIMITED_FEASIBILITY_r1';OLD=PACKS/'MS20261020_E2_CONTROLS_QUALIFICATION_r1'
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def main():
 coord=c.Coordinator();s=coord.snapshot();base=read(P/'BASELINE.json');approval=read(P/'USER_APPROVAL.json')
 assert approval['approved'] and approval['only_primary'] and s['actual_starts']==32 and s['controller']['state']=='STOPPED'
 assert s['full_system_matrix']==base['full_system_matrix'] and s['t0_unix']==1792414193
 assert not (P/'PLAN.json').exists(),'Reuse published preparation; do not create new qualification hashes.'
 ar=read(R/'A2_STATIC_REVIEW.json');assert ar['source_identity']==s['final_source_identity']
 core=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r39-own-pending-v1')
 for rel,versions in ar['unchanged_source_blobs'].items():
  for commit,blob in versions.items():assert subprocess.check_output(['git','-C',str(core),'rev-parse',commit+':'+rel],text=True).strip()==blob
 assert c.digest(ar['retained_evidence_catalog']['path'])==ar['retained_evidence_catalog']['sha256']
 catalog=read(ar['retained_evidence_catalog']['path']);selected={}
 for e in ar['small_retained_native_evidence']:
  if e['case'] not in ['S_L2_DATA_FREE_local','S_L2_DATA_FREE_ROP7','F_data_free']:continue
  assert c.digest(e['raw']['path'])==e['raw']['sha256'] and e['expected_terminal'] in Path(e['raw']['path']).read_text()
  match=[]
  for group in catalog.values():
   if not isinstance(group,dict):continue
   for t in group.get('tests',[]):
    if t.get('case')==e['case'] and t.get('raw_log',{}).get('sha256')==e['raw']['sha256'] and (e['case']!='F_data_free' or group['source_identity']['core_source_commit']=='27ec10bda848e4929181c60a7cbb40d6b007945c'):
     assert t['actual_exit']==0 and c.digest(t['raw_log']['path'])==e['raw']['sha256'] and c.digest(group['receipt']['path'])==group['receipt']['sha256'];match.append(dict(test=t,execution_receipt=group['receipt'],executed_source_identity=group['source_identity']))
  assert match;e=copy.deepcopy(e);e['verified_historical_execution']=match;selected[e['case']]=e
 mainpath=Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r41/accel-sim.out');archive=Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r40/libgpgpusim.a')
 assert c.digest(mainpath)==s['final_source_identity']['binary_sha256'] and c.digest(archive)=='3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8'
 source_review=dict(status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),source_identity=s['final_source_identity'],prior_static_review=ref(R/'A2_STATIC_REVIEW.json'),latest_A2='7c8425da0a77639add9fe13a15fc41b343600ff7',unchanged_source_blobs=ar['unchanged_source_blobs'],delta_disposition=ar['delta_disposition'],current_E17_delta=ref(PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/DELTA_APPLICABILITY_REVIEW.json'),selected_actual_native_cases=selected,main=ref(mainpath),archive=ref(archive),whole_source_equality_claim=False,new_native_calls=0,new_builds=0,extra_C_joint_fixture_qualified=False,scope='Exact source-disjoint finite-service assertions plus separately current tested WAD delta; never raw PASS text alone or a cross-binary application anchor.')
 c.write_json(P/'SOURCE_NATIVE_APPLICABILITY.json',source_review)
 matrix=read(approval['approved_matrix']['path']);c.policy_v2.validate_matrix(matrix);rows=[]
 configs=read(R/'DRAFT_CONFIGURATION_IDENTITY_REVIEW.json')['candidates'];cfgs={r['candidate']:r for r in configs}
 inputs={};convq=PACKS/'MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1/convolutionSeparable_QUALIFICATION.json'
 definitions=[('dwt2d','F_MINUS_R','V2_dwt2d_F_MINUS_R',PACKS/'MS20261020_E2_MAIN_ROLLING_r1/dwt2d/F_SPEC.json',PACKS/'MS20261020_E2_MAIN_ROLLING_r1/dwt2d/QUALIFICATION.json','DWT_F_MINUS_R','E018_67a874f4'),('vectorAdd_4M','F','V2_vectorAdd_4M_F_RESOURCE_RETRY',PACKS/'MS20261020_E2_MAIN_ROLLING_r1/vectorAdd_4M/F_SPEC.json',PACKS/'MS20261020_E2_MAIN_ROLLING_r1/vectorAdd_4M/QUALIFICATION.json',None,'E013_33cffb17'),('convolutionSeparable','S_L2_DATA_FREE','V2_convolutionSeparable_S_L2_DATA_FREE',PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/convolutionSeparable_S_SPEC.json',convq,'Conv_S_L2_DATA_FREE','E010_1108e4d2'),('convolutionSeparable','F_L2_DATA_FREE','V2_convolutionSeparable_F_L2_DATA_FREE',PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/convolutionSeparable_F_SPEC.json',convq,'Conv_F_L2_DATA_FREE','E009_76e25c1e')]
 for w,profile,condition,template,qpath,cfgname,anchor_id in definitions:
  out=P/condition;out.mkdir(exist_ok=True);spec=read(template);qbase=read(qpath);assert qbase['source_identity']==s['final_source_identity']
  cell=next(r for r in matrix['conditions'] if r['condition_id']==condition)
  anchor=s['accepted_results'][anchor_id];assert c.digest(anchor['path'])==anchor['sha256'];anchor_receipt=read(anchor['path']);assert anchor_receipt['independent_acceptance']=='PASS'
  oldprofile=spec['profile'];sem=copy.deepcopy(qbase['supported_profiles'][oldprofile]);selected_mode=[]
  if profile=='F_MINUS_R':
   mode=read(OLD/'F_MINUS_R/PROFILE_QUALIFICATION_REVIEW.json');modeq=read(OLD/'F_MINUS_R/QUALIFICATION.json');assert modeq['source_identity']==s['final_source_identity']
   for key in ['research_switches','feature_vector','ideal_vector','labels']:sem[key]=copy.deepcopy(modeq['supported_profiles'][profile][key])
   selected_mode=mode['retained_independent_profile_cases']
   for e in selected_mode:
    assert e.get('actual_exit',e.get('exit_code'))==0 and c.digest(e['raw_log'])==e.get('raw_log_sha256',e.get('raw_SHA256'))
   assert tuple(sem['research_switches'][k] for k in ['W','V','T','M'])==(1,1,0,0)
  elif profile.endswith('L2_DATA_FREE'):
   sem['ideal_vector']['l2_data_free']=True;sem['labels'].update(diagnostic=True,subset=profile)
   selected_mode=[selected['F_data_free']] if profile.startswith('F_') else [selected['S_L2_DATA_FREE_local'],selected['S_L2_DATA_FREE_ROP7']]
  if cfgname:
   cp=cfgs[cfgname]['overlay'];assert c.digest(cp['path'])==cp['sha256'];spec['configs'][-1]['path']=cp['path']
  effective=options([x['path'] for x in spec['configs']]);prior=qbase['supported_profiles'][oldprofile]['effective_options'];diff={k:[prior.get(k),v] for k,v in effective.items() if prior.get(k)!=v};assert set(diff)<=set(sem['comparison_variable_options'])
  sem['effective_options']=effective
  selection=s['input_selections'][spec['selection_id']];assert c.digest(selection['path'])==selection['sha256']
  if w not in inputs:
   traces=runner.legacy.asset_manifest(spec['trace_files']);assert runner.legacy.content_hash(traces)==spec['identity']['trace_content_sha256']==selection['selection']['full_input_identity']['trace_content_sha256']
   atomic=runner.legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],traces);inputs[w]=(traces,atomic)
  traces,atomic=inputs[w];runner.legacy.validate_config_closure(spec);runner.legacy.validate_trace_closure(spec)
  for gate in qbase['gates'].values():assert c.digest(gate['evidence_path'])==gate['evidence_sha256'] and gate['status']=='PASS'
  if profile!='F':
   review=dict(schema='E2_PRIMARY_EXACT_PROFILE_INPUT_REVIEW_V1',status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),source_identity=s['final_source_identity'],workload=w,profile=profile,condition=condition,user_approval=ref(P/'USER_APPROVAL.json'),source_native_applicability=ref(P/'SOURCE_NATIVE_APPLICABILITY.json'),selected_mode_native_evidence=selected_mode,labels=sem['labels'],ideal_vector=sem['ideal_vector'],research_switches=sem['research_switches'],effective_options=effective,changed_research_options=diff,nonresearch_changes=[],full_input_selection=dict(id=spec['selection_id'],**ref(selection['path'])),atomic_input_review=atomic,expected_instructions=selection['selection']['full_input_identity']['expected_full_instructions'],anchor=anchor,anchor_not_rerun=True,no_new_native_or_build=True,no_extra_joint_fixture_promotion=True)
   rp=out/'PROFILE_INPUT_REVIEW.json';c.write_json(rp,review);q=copy.deepcopy(qbase);q.update(schema='E2_PRIMARY_EXACT_ONE_PROFILE_QUALIFICATION_V1',qualified_unix=time.time(),supported_profiles={profile:sem},profile_qualification_review=ref(rp),input_selection_id=spec['selection_id'],scope_note=w+'/'+profile+' only, exact main61 complete input/options/oracle. Source-equivalent actual mode-specific finite evidence plus currentE17 delta independently reviewed; all shared gates preserved; not application-validity substitution or new native invocation.')
   q['affected_additional_gates']=list(q['affected_additional_gates'])+['profile_specific_mode_and_input_semantics'];q['gates']['profile_specific_mode_and_input_semantics']=dict(status='PASS',production_driven=True,evidence_path=str(rp),evidence_sha256=c.digest(rp))
   if profile.endswith('L2_DATA_FREE'):
    gate_name='full_data_free_finite_residual_service' if profile.startswith('F_') else 'S_data_free_finite_residual_service'
    gp=out/'FINITE_RESIDUAL_SERVICE_GATE.json';c.write_json(gp,dict(gate=gate_name,status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),source_identity=s['final_source_identity'],actual_retained_native=selected_mode,source_equivalence=ref(P/'SOURCE_NATIVE_APPLICABILITY.json'),obligations=['finite1168 payload/1024tags/4banks','D512 Line128 WAD128 peraddress32 finite','real metadata query,version/reference data,ROidentity,dirtyWB/ICNT/backpressure/realresponse/ROP remain','data service grants exempt; diagnostic/hardware-ineligible labels mandatory','S fixedcopylatch remains; F current WAD delta independently exercised'],new_native_runs=0,not_waived_by_SF_validity=True))
    q['affected_additional_gates'].append(gate_name);q['gates'][gate_name]=dict(status='PASS',production_driven=True,evidence_path=str(gp),evidence_sha256=c.digest(gp))
   qp=out/'QUALIFICATION.json';c.write_json(qp,q);qid=c.digest(qp)
  else:
   q=qbase;qp=qpath;qid=spec['qualification_id'];assert c.digest(qp)==qid and qid in s['qualifications'];rp=None
  c.policy_v2.combination_qualification(q,c.digest)
  spec.update(profile=profile,profile_semantics=sem,labels=sem['labels'],qualification_id=qid,parser=q['terminal_parser'],condition_id=condition,budget_bucket=c.policy_v2.GROUP_BUCKET[cell['group']],maximum_result_bytes=384*2**20,preparation_status='INDEPENDENT_EXACT_PROFILE_QUALIFIED_AWAIT_PUBLISHED_APPROVED_DISPATCH')
  spec['identity'].update(feature_vector=sem['feature_vector'],ideal_vector=sem['ideal_vector'])
  assets=runner.legacy.asset_manifest(spec['auxiliary_assets']);cfgmanifest=runner.legacy.asset_manifest(spec['configs'],ordered=True);spec['identity']['runtime_config_sha256']=runner.legacy.content_hash(dict(ordered_configs=cfgmanifest,auxiliary_assets=assets,environment=spec['environment']))
  variables=sem['comparison_variable_options'];invariant=dict(source=q['source_identity'],trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in variables},comparison_variable_options=sorted(variables));spec['comparison_invariants_sha256']=runner.legacy.content_hash(invariant);assert spec['comparison_invariants_sha256']==anchor_receipt['comparison_invariants_sha256']
  history=[a for a in s['attempts'] if a['run_key']==c.run_key(spec['identity'])]
  if w=='vectorAdd_4M':
   assert len(history)==1 and history[-1]['attempt_id']=='E014_7a67cdcb' and history[-1]['state']=='RESOURCE_LIMIT';spec.update(retry_previous_attempt='E014_7a67cdcb',retry_reason='Explicit PRIMARY FOUR user approval, replace unstarted V2_btree_F MAIN row; prior E014 true workspace guard exit-15/wait15 remains charged, invalid and immutable. One new VectorF attempt; reuse current accepted S without rerun.')
  else:assert not history
  sp=out/'SPEC.json';c.write_json(sp,spec);pairid=('V2_MAIN_vectorAdd_4M_S_F_MAIN61_RESOURCE_RETRY' if w=='vectorAdd_4M' else 'V2_CONTROL_'+w+'_'+('F' if profile in ['F_MINUS_R','F_L2_DATA_FREE'] else 'S')+'_VS_'+profile+'_MAIN61')
  c.write_json(out/'OFFLINE_INPUT_CONFIG_REVIEW.json',dict(status='PASS_NO_REGISTRATION_OR_START',at_unix=time.time(),identity=spec['identity'],configs=cfgmanifest,auxiliary_assets=assets,traces=traces,atomic_scope=atomic,comparison_invariants=invariant,anchor_receipt=anchor))
  rows.append(dict(workload=w,profile=profile,condition_id=condition,qualification=ref(qp),qualification_id=qid,new_qualification=(profile!='F'),spec=ref(sp),review=ref(rp) if rp else None,expected_instructions=selection['selection']['full_input_identity']['expected_full_instructions'],run_key=c.run_key(spec['identity']),anchor_attempt=anchor_id,pair_id=pairid,pair=dict(pair_id=pairid,left_run_key=anchor['run_key'],right_run_key=c.run_key(spec['identity']),mechanism='USER_APPROVED_PRIMARY_FOUR_EXACT_PROFILE; full finite terminal; existing anchor not replayed'),maximum_result_bytes=384*2**20))
 qp=P/'QUEUE.json';c.write_json(qp,dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=time.time(),specs=[r['spec'] for r in rows],pairs=[r['pair'] for r in rows]))
 c.write_json(P/'PLAN.json',dict(schema='E2_PRIMARY_FOUR_EXECUTION_PLAN_V1',at_unix=time.time(),user_approval=ref(P/'USER_APPROVAL.json'),baseline=ref(P/'BASELINE.json'),matrix=approval['approved_matrix'],profiles=rows,queue=ref(qp),maximum_new_starts=4,maximum_total_result_bytes=4*384*2**20,collector_and_metadata_planning_reserve_bytes=32*2**20,timeout_seconds=10800,max_concurrency=2,T0=s['t0_unix'],start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE))
 assert c.digest(c.SHARED/'RUN_REGISTRY.json')==base['registry_sha256']
 print(json.dumps(dict(status='FOUR_PREPARED_NO_REGISTRATION_OR_NATIVE_OR_APPLICATION_START',profiles=[dict(condition=r['condition_id'],qid=r['qualification_id']) for r in rows])),flush=True)
if __name__=='__main__':main()
