"""Finite sequence through ORIGINAL controller.step; no second live controller/registry."""
from pathlib import Path
import sys,json,copy,time,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from controller import step
from publish_state import checkpoint

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def conditions(rows):return [dict(workload=r['workload'],condition_ids=['V2_'+r['workload']+'_S','V2_'+r['workload']+'_F'],queue=r['queue']) for r in rows]
def choose_slots(coord,row):
 # Read-only concrete admission forecast; pinned gate is repeated by each actual runner launch.
 data=read(c.SHARED/'RUN_REGISTRY.json');s=coord.snapshot();assert s['controller']['state']=='STOPPED';assert not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for r in data['runs'].values())
 resources=c.local_resources();usage=c.output_usage();spec=read(read(row['queue']['path'])['specs'][0]['path']);growth=spec['maximum_result_bytes'];memory=spec['memory_bytes'];data[c.FIELD]['target_simulators']=2
 c.resource_gate(data,'simulation',1,memory,growth,resources,usage)
 shadow=copy.deepcopy(data);shadow['runs']['E2_READ_ONLY_FORECAST_NOT_A_LEASE']=dict(status='RESERVED',scan=False,host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=memory,disk_growth_bytes=growth,monitor_reserve_bytes=c.disk_policy.lease_policy(s)['monitor_reserve_bytes'],result_directory=str(c.OUTPUT/'E2_FORECAST_NONEXISTENT'))
 slots=2;two_reason='original gate admits both conservative reservations'
 try:c.resource_gate(shadow,'simulation',1,memory,growth,resources,usage)
 except ValueError as error:slots=1;two_reason=str(error)
 audit=dict(at_unix=time.time(),status='CONCRETE_ADMISSION_FORECAST_NOT_A_LEASE',workload=row['workload'],slots=slots,maximum=2,resources=resources,output_usage=usage,two_slot_reason=two_reason,source_identity=s['final_source_identity'],per_run_memory_bytes=memory,per_run_result_growth_bytes=growth,workspace_policy=coord.work_disk_policy(),source_config_input_rehashed_below=True)
 # No quota override: only choose 1 or 2 within original E policy; every Popen obtains original central lease.
 with coord.locked() as (data,item):
  assert item['controller']['state']=='STOPPED';item['target_simulators']=slots;item.setdefault('main_batch_admission_history',[]).append(audit)
 return audit

def adopt(plan,publication):
 coord=c.Coordinator();gate=read(P/'FWT_INDEPENDENT_TERMINAL_AUDIT.json');assert gate['may_continue_original_main'] is True
 assert c.digest(plan['new_matrix']['path'])==plan['new_matrix']['sha256'];matrix=read(plan['new_matrix']['path']);c.policy_v2.validate_matrix(matrix)
 with coord.locked() as (data,item):
  assert item['controller']['state']=='STOPPED' and item['final_source_identity']==plan['source_identity'];assert item['actual_starts']<=40 and item['uncertain_start_intents']==0
  old=item['full_system_matrix']
  if old['sha256']!=plan['new_matrix']['sha256']:
   assert old['sha256']==plan['original_matrix']['sha256'];item.setdefault('matrix_priority_revision_history',[]).append(dict(previous=copy.deepcopy(old),publication=publication,reason=plan['priority_reason'],at_unix=time.time(),allocation_unchanged=True))
   item['full_system_matrix']=dict(path=plan['new_matrix']['path'],sha256=plan['new_matrix']['sha256'],matrix=matrix,D_publication=old['D_publication'],E_priority_publication=publication,status='ORIGINAL32_ONLY_EXECUTION_PRIORITIES_UPDATED')
  item['target_simulators']=2
 cp=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(cp)
 for r in plan['conditions']:
  if not any(x['qualification_id']==r['qualification_id'] for x in client['current_qualifications']):client['current_qualifications'].append(dict(path=r['qualification']['path'],qualification_id=r['qualification_id'],qualification_sha256=r['qualification_id'],workload=r['workload']))
 client['terminal_adapter_qualified_scope']='MAIN61_ORIGINAL_MAIN_S_F_ONLY_CONV_FWT_VECTOR_CFD_DWT_SAD; EXTRA_JOINT_AND_UNIMPLEMENTED_ABLATIONS_NOT_QUALIFIED';c.write_json(cp,client);c.write_json(P/'CLIENT_MAIN_READY.json',client)

def main():
 coord=c.Coordinator();plan=read(P/'PLAN.json');pub=read(P/'PRELAUNCH_REMOTE_READBACK.json')['remote_commit']
 for f in [P/'PLAN.json',P/'rolling_main.py',P/'publish_state.py',P/'MATRIX_32_PRIORITY_REVISION.json']:
  assert subprocess.check_output(['git','-C',str(ROOT),'show',pub+':'+f.relative_to(ROOT).as_posix()])==f.read_bytes()
 adopt(plan,pub)
 rows=plan['conditions']
 for i,row in enumerate(rows):
  snap=coord.snapshot();pairid='V2_MAIN_'+row['workload']+'_S_F_MAIN61'
  if snap['accepted_pairs'].get(pairid,{}).get('status')=='CURRENT_ACCEPTED':continue
  assert snap['final_source_identity']==plan['source_identity'];assert c.digest(row['queue']['path'])==row['queue']['sha256'];assert c.digest(row['qualification']['path'])==row['qualification']['sha256']
  queue=read(row['queue']['path']);audit=[]
  for e in queue['specs']:
   assert c.digest(e['path'])==e['sha256'];spec=read(e['path']);fresh=runner.inspect(spec,coord);atomic=runner.legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],fresh['traces']);audit.append(dict(run_key=fresh['run_key'],source_binary_config_input_audit=fresh,atomic_scope=atomic))
  try:admission=choose_slots(coord,row)
  except ValueError as error:
   c.write_json(P/(row['workload']+'_ADMISSION_BLOCK.json'),dict(status='NO_START_RESOURCE_EVENT_REQUIRED',reason=str(error),at_unix=time.time(),actual_starts=coord.snapshot()['actual_starts']))
   checkpoint('MAIN_'+row['workload']+'_ADMISSION_BLOCK',conditions(rows[i:]),extra_paths=[P/(row['workload']+'_ADMISSION_BLOCK.json')]);return
  ap=P/(row['workload']+'_ACTUAL_PRELAUNCH_AUDIT.json');c.write_json(ap,dict(admission=admission,complete_inputs=audit,source_identity=snap['final_source_identity'],next=conditions(rows[i:])))
  checkpoint('MAIN_'+row['workload']+'_QUALIFIED_ADMISSION',conditions(rows[i:]),extra_paths=[ap,P/'CLIENT_MAIN_READY.json'])
  result=step(coord,row['queue']['path']);rp=P/(row['workload']+'_CONTROLLER_RESULT.json');c.write_json(rp,result);now=coord.snapshot();pair=now['accepted_pairs'].get(pairid);accepted=bool(pair and pair['status']=='CURRENT_ACCEPTED')
  failures=[a for a in now['attempts'] if a['identity']['workload']==row['workload'] and a['identity']['binary_sha256']==plan['source_identity']['binary_sha256'] and a['state']=='FAILED']
  event='MAIN_'+row['workload']+('_PAIR_CURRENT_ACCEPTED' if accepted else '_EXACT_RESULT_NOT_ACCEPTED')
  checkpoint(event,conditions(rows[i+1:]),[pairid] if accepted else [],[rp])
  if failures:
   print(json.dumps(dict(status='AFFECTED_SOURCE_OR_ENGINEERING_REVIEW_REQUIRED_NO_FURTHER_ADMISSION',workload=row['workload'],next=conditions(rows[i+1:]))),flush=True);return
  if not accepted and result.get('applications_started_by_this_step',0)==0:return
 print(json.dumps(dict(status='ORIGINAL_FOUR_AVAILABLE_MAIN_PAIRS_PROCESSED',actual_starts=coord.snapshot()['actual_starts'],remaining=coord.snapshot()['remaining_start_capacity'])),flush=True)
if __name__=='__main__':main()
