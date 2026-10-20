"""Prepare exact approved input/profile qualifications; no matrix adoption or application launch."""
from pathlib import Path
import copy,json,time,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from headroom_config import options
legacy=runner.legacy
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def main():
 coord=c.Coordinator();before=coord.snapshot();approval=read(P/'USER_APPROVED_REALLOCATION.json')
 assert approval['approved'] and approval['user_answer']=='批准这4项修订，执行仍须通过全部门禁'
 for key in ['approved_proposal','approved_exact_draft_matrix']:
  assert c.digest(approval[key]['path'])==approval[key]['sha256']
 proposal=read(approval['approved_proposal']['path']);matrix=read(approval['approved_exact_draft_matrix']['path']);c.policy_v2.validate_matrix(matrix)
 assert before['full_system_matrix']==proposal['original_matrix']
 rows=[];manifest_cache={}
 for change in proposal['changes']:
  w=change['workload'];profile=change['profile'];condition=change['proposed_condition_id'];cell=next(r for r in matrix['conditions'] if r['condition_id']==condition)
  assert not any(a['identity']['workload']=='FWT_7_21' and a['profile']==profile and a.get('actual_start') for a in before['attempts'])
  cfg=change['proposed_config'];assert c.digest(cfg['path'])==cfg['sha256']
  target=P.parent/'MS20261020_E2_MAIN_ROLLING_r1'/w;out=P/'APPROVED_CONTROLS'/condition;out.mkdir(parents=True,exist_ok=True)
  mode=read(P/profile/'PROFILE_QUALIFICATION_REVIEW.json');modeq=read(P/profile/'QUALIFICATION.json');qbase=read(target/'QUALIFICATION.json')
  assert qbase['source_identity']==modeq['source_identity']==change['source_identity']==before['final_source_identity']
  template=read(target/('S_SPEC.json' if profile=='S_COPY_FREE' else 'F_SPEC.json'))
  anchor_profile='S' if w=='dwt2d' else 'F'
  anchor=next(a for a in before['attempts'] if a['identity']['workload']==w and a['profile']==anchor_profile and a['state']=='COMPLETE_VALID')
  assert c.digest(anchor['receipt_path'])==anchor['receipt_sha256'];anchor_receipt=read(anchor['receipt_path'])
  assert anchor_receipt['independent_acceptance']=='PASS'
  selection=before['input_selections'][template['selection_id']]
  assert template['selection_id']==change['complete_input_selection_id'] and selection['sha256']==change['complete_input_selection_sha256']
  assert c.digest(selection['path'])==selection['sha256']
  assert selection['selection']['full_input_identity']['expected_full_instructions']==change['expected_full_instructions']
  sem=copy.deepcopy(qbase['supported_profiles']['S' if profile=='S_COPY_FREE' else 'F'])
  modesem=modeq['supported_profiles'][profile]
  for key in ['research_switches','feature_vector','ideal_vector','labels']:sem[key]=copy.deepcopy(modesem[key])
  assert tuple(sem['research_switches'][k] for k in ['W','V','T','M'])==tuple(cell[k] for k in ['W','V','T','M'])
  template['configs'][-1]['path']=cfg['path'];sem['effective_options']=options([a['path'] for a in template['configs']]);assert sem['effective_options']==change['effective_options']
  prior=qbase['supported_profiles']['S' if profile=='S_COPY_FREE' else 'F']['effective_options']
  diff={k:[prior.get(k),v] for k,v in sem['effective_options'].items() if prior.get(k)!=v}
  assert set(diff)<=set(sem['comparison_variable_options'])
  for case in mode['retained_independent_profile_cases']:
   assert case.get('actual_exit',case.get('exit_code'))==0
   assert c.digest(case['raw_log'])==case.get('raw_log_sha256',case.get('raw_SHA256'))
   assert not case.get('terminal_checks') or all(case['terminal_checks'].values())
  for artifact in ['NATIVE_INPUT_SEMANTICS.json','RETAINED_INPUT_SCOPE.json']:
   expected={'NATIVE_INPUT_SEMANTICS.json':'RETAINED_COMPLETE_INPUT_SEMANTICS_REVIEWED_NOT_RUNTIME_PASS','RETAINED_INPUT_SCOPE.json':'UNCHANGED_COMPLETE_INPUT_PARSER_AND_CONTENT_SCOPE'}
   assert read(target/artifact)['status']==expected[artifact]
  legacy.validate_config_closure(template);legacy.validate_trace_closure(template)
  if w not in manifest_cache:
   traces=legacy.asset_manifest(template['trace_files']);assets=legacy.asset_manifest(template['auxiliary_assets'])
   assert legacy.content_hash(traces)==change['trace_content_sha256']==template['identity']['trace_content_sha256']
   atomic=legacy.validate_atomic_input_scope(template,template['input_scope_admission'],traces)
   manifest_cache[w]=(traces,assets,atomic)
  traces,assets,atomic=manifest_cache[w]
  review=dict(schema='E2_APPROVED_EXACT_INPUT_PROFILE_REVIEW_V1',status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),workload=w,profile=profile,condition_id=condition,source_identity=qbase['source_identity'],user_approval=ref(P/'USER_APPROVED_REALLOCATION.json'),approved_config=cfg,research_switches=sem['research_switches'],labels=sem['labels'],ideal_vector=sem['ideal_vector'],effective_options=sem['effective_options'],nonresearch_changes=[],changed_research_options=diff,profile_native_review=ref(P/profile/'PROFILE_QUALIFICATION_REVIEW.json'),retained_independent_profile_cases=mode['retained_independent_profile_cases'],input_semantics=ref(target/'NATIVE_INPUT_SEMANTICS.json'),retained_input_scope=ref(target/'RETAINED_INPUT_SCOPE.json'),complete_input_selection=dict(id=template['selection_id'],**ref(selection['path'])),atomic_input_proof=atomic,existing_anchor=dict(attempt_id=anchor['attempt_id'],receipt=ref(anchor['receipt_path']),not_replayed=True),scientific_question=change['question'],qualification_boundary='Separate exact target input/profile review: mode-specific native assertions and unchanged producer implementation plus independently rehashed target full input, atomic/certificate semantics and exact approved options. Main S/F application validity alone does not qualify this profile.',new_native_invocations=0,new_builds=0,extra_joint_fixture_qualified=False,numeric_SASS_output_validated=False,matrix_adopted=False,launch_gate='PENDING_SAFE_STOPPED_MATRIX_ADOPTION_AND_ALL_LIVE_GATES')
  rp=out/'PROFILE_INPUT_REVIEW.json';c.write_json(rp,review)
  q=copy.deepcopy(qbase);q.update(schema='E2_APPROVED_ONE_INPUT_CONTROL_QUALIFICATION_V1',qualified_unix=time.time(),supported_profiles={profile:sem},profile_qualification_review=ref(rp),scope_note=w+'/'+profile+' only; exact approved config, original complete input and unchanged main61. Distinct mode-native and input review; no application validity inherited, no new native invocation or failed extra fixture promotion.')
  q['affected_additional_gates']+=['profile_specific_mode_and_input_semantics'];q['gates']['profile_specific_mode_and_input_semantics']=dict(status='PASS',production_driven=True,evidence_path=str(rp),evidence_sha256=c.digest(rp))
  qp=out/'QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp)
  spec=template;spec.update(profile=profile,profile_semantics=sem,labels=sem['labels'],qualification_id=qid,parser=q['terminal_parser'],condition_id=condition,budget_bucket=change['budget_bucket'],preparation_status='EXACT_INPUT_PROFILE_QUALIFIED_PENDING_APPROVED_MATRIX_ADOPTION')
  spec['identity'].update(feature_vector=sem['feature_vector'],ideal_vector=sem['ideal_vector']);configs=legacy.asset_manifest(spec['configs'],ordered=True)
  spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
  variables=sem['comparison_variable_options'];invariant=dict(source=q['source_identity'],trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in sem['effective_options'].items() if k not in variables},comparison_variable_options=sorted(variables))
  spec['comparison_invariants_sha256']=legacy.content_hash(invariant);assert spec['comparison_invariants_sha256']==anchor_receipt['comparison_invariants_sha256']
  sp=out/'SPEC.json';c.write_json(sp,spec);pairid='V2_CONTROL_'+w+'_'+anchor_profile+'_VS_'+profile+'_MAIN61'
  pair=dict(pair_id=pairid,left_run_key=anchor['run_key'],right_run_key=c.run_key(spec['identity']),mechanism='USER_APPROVED_EXACT_INPUT_CONTROL_NO_ANCHOR_REPLAY')
  queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=time.time(),specs=[ref(sp)],pairs=[pair]);queuepath=out/'QUEUE.json';c.write_json(queuepath,queue)
  c.write_json(out/'OFFLINE_PREFLIGHT.json',dict(status='PASS_PENDING_MATRIX_ADOPTION',at_unix=time.time(),configs=configs,auxiliary_assets=assets,traces=traces,complete_atomic_scope=atomic,comparison_invariants=invariant,anchor_attempt=anchor['attempt_id'],new_run_key=pair['right_run_key'],no_application_started=True))
  rows.append(dict(workload=w,profile=profile,condition_id=condition,old_unstarted_condition_id=change['old_unstarted_condition_id'],qualification=ref(qp),qualification_id=qid,spec=ref(sp),queue=ref(queuepath),review=ref(rp),control_pair_id=pairid,anchor_attempt=anchor['attempt_id'],expected_full_instructions=change['expected_full_instructions'],estimated_wall_seconds=change['estimated_wall_seconds'],estimated_result_bytes=change['estimated_result_bytes'],maximum_result_bytes=spec['maximum_result_bytes'],timeout_seconds=spec['timeout_seconds']))
  print('EXACT_TARGET_PROFILE_QUALIFIED_PENDING_MATRIX_ADOPTION',condition,qid,flush=True)
 after=coord.snapshot();assert after['full_system_matrix']==before['full_system_matrix']
 plan=dict(schema='E2_APPROVED_FOUR_CONTROL_PREPARATION_V1',at_unix=time.time(),user_approval=ref(P/'USER_APPROVED_REALLOCATION.json'),proposal=approval['approved_proposal'],approved_matrix=approval['approved_exact_draft_matrix'],profiles=rows,full_four_run_result_reservation_bytes=sum(r['maximum_result_bytes'] for r in rows),capacity_conditions=proposal['capacity_conditions_after_original_Conv_controls'],original_matrix_not_yet_adopted=True,no_full_application_started_by_preparation=True,launch_preconditions=approval['execution_conditions'],expected_total_after_six_Conv_and_four_approved=30,expected_remaining=10,T0=before['t0_unix'],start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE)
 c.write_json(P/'APPROVED_CONTROLS'/'PREPARATION_PLAN.json',plan)
if __name__=='__main__':main()
