"""Finite approved queue feed, using the original sole controller at a stopped boundary."""
from pathlib import Path
import copy,json,sys,time,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P))
import coordinator as c,runner,controller
from report_approved_controls import checkpoint
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def published_bytes(commit,path):
 assert subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+str(Path(path).relative_to(ROOT))])==Path(path).read_bytes()
def adopt(coord,plan,publication):
 approval=read(plan['user_approval']['path']);assert approval['approved']
 for artifact in [plan['user_approval'],plan['proposal'],plan['approved_matrix']]:
  assert c.digest(artifact['path'])==artifact['sha256'];published_bytes(publication,artifact['path'])
 proposal=read(plan['proposal']['path']);matrix=read(plan['approved_matrix']['path']);cells=c.policy_v2.validate_matrix(matrix)
 s=coord.snapshot();assert s['actual_starts']==26 and s['remaining_start_capacity']==14 and s['controller']['state']=='STOPPED'
 assert s['t0_unix']==plan['T0'] and s['uncertain_start_intents']==0
 assert s['full_system_matrix']==proposal['original_matrix']
 assert all(s['accepted_pairs'].get(r['control_pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for r in read(P/'ADMISSION_PLAN.json')['profiles'])
 for change in proposal['changes']:
  assert not any(a.get('actual_start') and a['identity']['workload']=='FWT_7_21' and a['profile']==change['profile'] for a in s['attempts'])
 before={r['condition_id']:r for r in s['full_system_matrix']['matrix']['conditions']};after={r['condition_id']:r for r in cells}
 replaced={r['old_unstarted_condition_id'] for r in proposal['changes']};added={r['proposed_condition_id'] for r in proposal['changes']}
 assert set(before)-set(after)==replaced and set(after)-set(before)==added
 assert all(before[k]==after[k] for k in set(before)&set(after))
 usage=c.output_usage();capacity=plan['capacity_conditions'];reserve=plan['full_four_run_result_reservation_bytes']
 assert reserve==1610612736 and usage['new_bytes']<=capacity['new_result_bytes_must_be_at_most'] and usage['total_bytes']<=capacity['old_plus_new_result_bytes_must_be_at_most']
 assert time.time()<c.START_DEADLINE and time.time()+10800<=c.INTAKE_DEADLINE
 data=read(c.SHARED/'RUN_REGISTRY.json');assert not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for r in data['runs'].values())
 for row in plan['profiles']:
  for key in ['spec','qualification','queue','review']:
   artifact=row[key];assert c.digest(artifact['path'])==artifact['sha256'];published_bytes(publication,artifact['path'])
 # Only the exact already-published matrix record changes; old scientific attempts and budgets are retained.
 with coord.locked() as (data,item):
  assert item['controller']['state']=='STOPPED' and item['actual_starts']==26 and item['full_system_matrix']==proposal['original_matrix']
  old=copy.deepcopy(item['full_system_matrix'])
  history=dict(previous=old,user_approval=plan['user_approval'],proposal=plan['proposal'],publication=publication,at_unix=time.time(),exact_replacements=proposal['changes'],actual_starts=26,remaining=14,T0=item['t0_unix'],reservations_unchanged=copy.deepcopy(item['reservations']),reason='User explicitly approved four unstarted FWT control slots for exact DWT/CFD diagnostics; complete four-run capacity and six Conv controls accepted.')
  item.setdefault('user_approved_matrix_revision_history',[]).append(history)
  item['full_system_matrix']=dict(path=plan['approved_matrix']['path'],sha256=plan['approved_matrix']['sha256'],matrix=matrix,D_publication=old['D_publication'],E_user_approved_revision_publication=publication,status='USER_APPROVED_EXACT_FOUR_DWT_CFD_CONTROL_REALLOCATION')
 clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(clientpath)
 for row in plan['profiles']:
  if not any(q['qualification_id']==row['qualification_id'] for q in client['current_qualifications']):client['current_qualifications'].append(dict(path=row['qualification']['path'],qualification_id=row['qualification_id'],qualification_sha256=row['qualification_id'],workload=row['workload'],profile=row['profile']))
 client['terminal_adapter_qualified_scope']+=';USER_APPROVED_DWT_S_COPY_FREE_W_ONLY_CFD_F_MINUS_V_F_MINUS_R';c.write_json(clientpath,client);c.write_json(P/'APPROVED_CONTROLS/CLIENT_APPROVED_READY.json',client)
 receipt=dict(schema='E2_USER_APPROVED_EXACT_MATRIX_ADOPTION_V1',status='ADOPTED',at_unix=time.time(),user_approval=plan['user_approval'],proposal=plan['proposal'],matrix=plan['approved_matrix'],publication=publication,history=history,output_usage=usage,full_four_run_reserved_capacity_bytes=reserve,actual_starts=26,remaining=14,no_new_starts_by_adoption=True,original_T0=s['t0_unix'],original_reservations=s['reservations'],source_identity=s['final_source_identity'],original_limits_unchanged=True)
 c.write_json(P/'APPROVED_CONTROLS/MATRIX_ADOPTION_RECEIPT.json',receipt)
 checkpoint('APPROVED_FOUR_MATRIX_ADOPTED_NO_NEW_START',extra=[P/'APPROVED_CONTROLS/MATRIX_ADOPTION_RECEIPT.json',P/'APPROVED_CONTROLS/CLIENT_APPROVED_READY.json'])
def main():
 coord=c.Coordinator();plan=read(P/'APPROVED_CONTROLS/PREPARATION_PLAN.json');publication=read(P/'APPROVED_CONTROLS/EXECUTION_READY_REMOTE_READBACK.json')['remote_commit']
 for path in [Path(__file__),P/'report_approved_controls.py',P/'APPROVED_CONTROLS/PREPARATION_PLAN.json']:published_bytes(publication,path)
 adopt(coord,plan,publication)
 original=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 for number in range(2):
  rows=plan['profiles'][number*2:number*2+2];s=coord.snapshot();assert s['controller']['state']=='STOPPED'
  specs=[];pairs=[];audits=[]
  for row in rows:
   assert c.digest(row['spec']['path'])==row['spec']['sha256'] and c.digest(row['queue']['path'])==row['queue']['sha256']
   spec=read(row['spec']['path']);audit=runner.inspect(spec,coord);assert not any(a['run_key']==audit['run_key'] for a in s['attempts'])
   assert audit['expected_full_instructions']==row['expected_full_instructions']
   q=read(row['queue']['path']);specs+=q['specs'];pairs+=q['pairs'];audits.append(dict(condition_id=row['condition_id'],audit=audit))
  data=read(c.SHARED/'RUN_REGISTRY.json');resources=c.local_resources();usage=c.output_usage();first=read(rows[0]['spec']['path']);data[c.FIELD]['target_simulators']=2
  c.resource_gate(data,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
  shadow=copy.deepcopy(data);shadow['runs']['E2_APPROVED_FORECAST_NOT_LEASE']=dict(status='RESERVED',host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=first['memory_bytes'],disk_growth_bytes=first['maximum_result_bytes'],monitor_reserve_bytes=2*c.GIB,result_directory=str(c.OUTPUT/'NONEXISTENT_APPROVED_FORECAST'),scan=False)
  slots=2;reason='Both original conservative reservations admitted'
  try:c.resource_gate(shadow,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
  except ValueError as error:slots=1;reason=str(error)
  with coord.locked() as (all_data,item):assert item['controller']['state']=='STOPPED';item['target_simulators']=slots
  qp=P/('APPROVED_CONTROLS/BATCH_'+str(number+1)+'_QUEUE.json');c.write_json(qp,dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=plan['at_unix'],specs=specs,pairs=pairs))
  ap=P/('APPROVED_CONTROLS/BATCH_'+str(number+1)+'_PRELAUNCH.json');c.write_json(ap,dict(status='PASS',at_unix=time.time(),slots=slots,two_slot_reason=reason,resources=resources,output_usage=usage,audits=audits,queue=ref(qp)))
  checkpoint('APPROVED_CONTROLS_BATCH_'+str(number+1)+'_QUALIFIED_ADMISSION',extra=[qp,ap])
  result=controller.step(coord,qp);rp=P/('APPROVED_CONTROLS/BATCH_'+str(number+1)+'_CONTROLLER_RESULT.json');c.write_json(rp,result)
  checkpoint('APPROVED_CONTROLS_BATCH_'+str(number+1)+'_TERMINAL',extra=[rp])
  if not all(coord.snapshot()['accepted_pairs'].get(r['control_pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for r in rows):
   print('AFFECTED_APPROVED_BATCH_NEEDS_EXACT_REVIEW_NO_REPLAY',flush=True);return
 print('FOUR_APPROVED_CONTROLS_ACCEPTED_NO_EXTRA_STARTS',flush=True)
if __name__=='__main__':main()
