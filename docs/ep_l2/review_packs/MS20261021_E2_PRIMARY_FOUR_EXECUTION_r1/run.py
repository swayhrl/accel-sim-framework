"""Finite PRIMARY FOUR feeder; original sole controller owns every actual start."""
from pathlib import Path
import json,sys,time,copy,subprocess,threading
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P))
import coordinator as c,runner,controller
from report import checkpoint

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def published(commit,path):
 path=Path(path);assert subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+str(path.relative_to(ROOT))])==path.read_bytes()
def main():
 coord=c.Coordinator();s=coord.snapshot();plan=read(P/'PLAN.json');approval=read(P/'USER_APPROVAL.json');base=read(P/'BASELINE.json');publication=read(P/'EXECUTION_READY_REMOTE_READBACK.json')['remote_commit']
 for path in [Path(__file__),P/'report.py',P/'prepare.py',P/'PLAN.json',P/'SOURCE_NATIVE_APPLICABILITY.json',P/'USER_APPROVAL.json']:published(publication,path)
 assert approval['approved'] and approval['only_primary'] and approval['maximum_new_actual_starts']==4
 assert s['actual_starts']==32 and s['remaining_start_capacity']==8 and s['uncertain_start_intents']==0 and s['controller']['state']=='STOPPED'
 assert s['full_system_matrix']==base['full_system_matrix'] and s['t0_unix']==plan['T0']==1792414193
 assert time.time()<c.START_DEADLINE and time.time()+10800<=c.INTAKE_DEADLINE
 for artifact in [plan['matrix'],plan['queue']]:assert c.digest(artifact['path'])==artifact['sha256'];published(publication,artifact['path'])
 matrix=read(plan['matrix']['path']);c.policy_v2.validate_matrix(matrix)
 before={r['condition_id']:r for r in s['full_system_matrix']['matrix']['conditions']};after={r['condition_id']:r for r in matrix['conditions']}
 assert set(before)-set(after)=={'V2_FWT_7_21_F_MINUS_W','V2_btree_F'}
 assert set(after)-set(before)=={'V2_dwt2d_F_MINUS_R','V2_vectorAdd_4M_F_RESOURCE_RETRY'}
 assert all(before[k]==after[k] for k in set(before)&set(after))
 for old in set(before)-set(after):assert not any(a.get('actual_start') and a['identity']['workload']==before[old]['workload'] and a['profile']==before[old]['profile'] for a in s['attempts'])
 data=read(c.SHARED/'RUN_REGISTRY.json');assert not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for group in ['runs','resource_leases'] for r in data[group].values())
 resources=c.local_resources();usage=c.output_usage();first=read(plan['profiles'][0]['spec']['path']);view=copy.deepcopy(data);view[c.FIELD]['target_simulators']=2
 margin=plan['collector_and_metadata_planning_reserve_bytes'];assert usage['new_bytes']+plan['maximum_total_result_bytes']+margin<=6*c.GIB and usage['total_bytes']+plan['maximum_total_result_bytes']+margin<=20*c.GIB
 c.resource_gate(view,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 shadow=copy.deepcopy(view);shadow['runs']['PRIMARY_FORECAST_NOT_LEASE']=dict(status='RESERVED',host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=first['memory_bytes'],disk_growth_bytes=first['maximum_result_bytes'],monitor_reserve_bytes=2*c.GIB,result_directory=str(c.OUTPUT/'NONEXISTENT_PRIMARY_FORECAST'),scan=False)
 slots=2;reason='Two real resource reservations forecast PASS'
 try:c.resource_gate(shadow,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 except ValueError as error:slots=1;reason=str(error)
 for row in plan['profiles']:
  for key in ['spec','qualification']:
   a=row[key];assert c.digest(a['path'])==a['sha256'];published(publication,a['path'])
  if row['review']:published(publication,row['review']['path'])
  spec=read(row['spec']['path']);existing=[a for a in s['attempts'] if a['run_key']==row['run_key']]
  if row['workload']=='vectorAdd_4M':assert len(existing)==1 and existing[0]['attempt_id']==spec['retry_previous_attempt']=='E014_7a67cdcb' and existing[0]['state']=='RESOURCE_LIMIT'
  else:assert not existing
  if row['new_qualification']:assert coord.register_qualification(row['qualification']['path'])==row['qualification_id']
  coord.require_no_hold(coord.snapshot(),row['qualification_id'])
 with coord.locked() as (all_data,item):
  assert item['controller']['state']=='STOPPED' and item['actual_starts']==32 and item['full_system_matrix']==base['full_system_matrix']
  history=dict(previous=copy.deepcopy(item['full_system_matrix']),user_approval=ref(P/'USER_APPROVAL.json'),publication=publication,at_unix=time.time(),exact_changes=approval['exact_changes'],actual_starts=32,remaining=8,T0=item['t0_unix'],reservations_unchanged=copy.deepcopy(item['reservations']),reason='Only explicit PRIMARY FOUR two-row substitution; all other30rows and original group budgets unchanged.')
  item.setdefault('user_approved_matrix_revision_history',[]).append(history)
  item['full_system_matrix']=dict(path=plan['matrix']['path'],sha256=plan['matrix']['sha256'],matrix=matrix,D_publication=history['previous']['D_publication'],E_user_approved_revision_publication=publication,status='USER_APPROVED_PRIMARY_FOUR_EXACT_TWO_ROW_REALLOCATION')
  item['target_simulators']=slots
 clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(clientpath)
 for row in plan['profiles']:
  if not any(q['qualification_id']==row['qualification_id'] for q in client['current_qualifications']):client['current_qualifications'].append(dict(path=row['qualification']['path'],qualification_id=row['qualification_id'],qualification_sha256=row['qualification_id'],workload=row['workload'],profile=row['profile']))
 client['terminal_adapter_qualified_scope']+=';PRIMARY_FOUR_DWT_R0_VECTOR_F_RETRY_CONV_S_F_L2_DATA_FREE';c.write_json(clientpath,client);c.write_json(P/'CLIENT_PRIMARY_READY.json',client)
 audits=[]
 for row in plan['profiles']:
  audit=runner.inspect(read(row['spec']['path']),coord);assert audit['expected_full_instructions']==row['expected_instructions'] and audit['run_key']==row['run_key'];audits.append(dict(condition=row['condition_id'],audit=audit))
 ap=P/'QUALIFIED_ADMISSION.json';c.write_json(ap,dict(status='PASS',at_unix=time.time(),slots=slots,two_slot_reason=reason,resources=resources,output_usage=usage,margin_bytes=margin,audits=audits,actual_starts=32,remaining=8,history=history,no_starts_by_adoption=True))
 checkpoint('PRIMARY_FOUR_QUALIFIED_ADMISSION_NO_START',extra=[ap,P/'CLIENT_PRIMARY_READY.json'])
 notice=dict(status='PRIMARY_FOUR_APPROVED_AND_QUALIFIED',E_publication=read(P/'PRIMARY_FOUR_QUALIFIED_ADMISSION_NO_START_REMOTE_READBACK.json')['remote_commit'],conditions=[r['condition_id'] for r in plan['profiles']],pair_ids=[r['pair_id'] for r in plan['profiles']],maximum_new_starts=4,only_primary=True,other_old_failures_and_HOLD_preserved=True)
 for channel in [c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]:c.write_json(channel/'E2_TO_A2_D_PRIMARY_FOUR_QUALIFIED.json',notice)
 original_roll=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original_roll(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 original_execute=controller.execute;admission_lock=threading.Lock()
 def guarded_execute(spec,coord):
  # Extra resource/batch-boundary checks only; original execute still performs
  # full inspection, lease, final Popen checks, durable wait and all acceptance.
  with admission_lock:
   state=coord.snapshot();assert state['actual_starts']<36 and len(state['attempts'][32:])<4
   current=read(c.SHARED/'RUN_REGISTRY.json');res=c.local_resources();used=c.output_usage();pending=sum(max(0,r.get('disk_growth_bytes',c.FULL_GROWTH)-c.retained_tree_bytes(Path(r['result_directory']))) for r in current['runs'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN)
   assert used['new_bytes']+pending+spec['maximum_result_bytes']+margin<=6*c.GIB and used['total_bytes']+pending+spec['maximum_result_bytes']+margin<=20*c.GIB,'Collector/metadata generation margin insufficient; no start'
   # Quota may be occupied by another worker about to reserve; the canonical
   # original transaction below is final and never bypasses an admission.
   c.resource_gate(current,'simulation',1,spec['memory_bytes'],spec['maximum_result_bytes'],res,used)
   c.write_json(P/(spec['condition_id']+'_ACTUAL_PRESTART_RESOURCE_REVIEW.json'),dict(status='PASS_BEFORE_ORIGINAL_EXECUTE',at_unix=time.time(),actual=state['actual_starts'],source=state['final_source_identity'],spec_identity=spec['identity'],qualification=spec['qualification_id'],resources=res,usage=used,pending_result_reserve_bytes=pending,collector_metadata_reserve_bytes=margin,maximum_result_bytes=spec['maximum_result_bytes'],controller=state['controller']))
  return original_execute(spec,coord)
 controller.execute=guarded_execute
 result=controller.step(coord,plan['queue']['path']);rp=P/'CONTROLLER_RESULT.json';c.write_json(rp,result)
 extra=[rp,*P.glob('*_ACTUAL_PRESTART_RESOURCE_REVIEW.json'),*P.glob('*_D_DELIVERY_RECEIPT.json')]
 checkpoint('PRIMARY_FOUR_TERMINAL',extra=extra)
 state=coord.snapshot();print(json.dumps(dict(status='ALL_FOUR_CURRENT_ACCEPTED' if all(state['accepted_pairs'].get(r['pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for r in plan['profiles']) else 'LEGAL_STOP_OR_PRECISE_FAILURE_NO_REPLAY',actual=state['actual_starts'],remaining=state['remaining_start_capacity'],controller=state['controller'],result=result)),flush=True)
if __name__=='__main__':main()
