"""Finite approved ten-condition feeder of the ORIGINAL single E controller.

No placeholder/source-candidate dispatch. Invoke only after exact new producer,
independent native/input/config qualification and sealed ready publication exist.
"""
from pathlib import Path
import argparse,copy,json,subprocess,sys,threading,time
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P))
import coordinator as c,capacity_policy as policy,runner,controller
from report import checkpoint,check_history

def read(p):return json.loads(Path(p).read_text())
def checked(a):
 p=Path(a['path']);c.require(c.digest(p)==a['sha256'],'changed artifact: '+str(p));return p

def published(commit,path):
 path=Path(path);c.require(subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+path.relative_to(ROOT).as_posix()])==path.read_bytes(),'unpublished execution artifact: '+str(path))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--execute-exact-approved-ten',action='store_true',required=True);ap.parse_args()
 coord=c.Coordinator();s=coord.snapshot();check_history(s);limits=policy.effective_limits(s)
 c.require(s['controller']['state']=='STOPPED' and s['uncertain_start_intents']==0,'original controller/intent not at safe boundary')
 c.require(policy.active(s) and 36<=s['actual_starts']<=46 and s['capacity_diagnostic_matrix']==policy.matrix(),'wrong approved phase')
 plan=read(P/'PLAN.json');ready=read(P/'EXECUTION_READY_REMOTE_READBACK.json');pub=ready['remote_commit']
 for path in [Path(__file__),P/'PLAN.json',P/'report.py',P/'USER_APPROVAL.json']:published(pub,path)
 c.require(plan['source_identity']['binary_sha256']!=policy.MAIN61 and len(plan['conditions'])==10 and len(plan['pairs'])==5,'five fresh-binary pairs required')
 c.require(plan['maximum_new_starts']==10 and plan['maximum_campaign_starts']==46 and plan['T0']==s['t0_unix'],'wrong campaign limits')
 c.require(time.time()<limits['start_deadline_unix'] and time.time()+10800<=limits['intake_deadline_unix'],'approved start/intake cutoff closed')
 qids=set();specs=[];common=None
 for row in plan['conditions']:
  specpath=checked(row['spec']);qpath=checked(row['qualification']);published(pub,specpath);published(pub,qpath)
  spec=read(specpath);q=read(qpath);qid=c.digest(qpath)
  c.require(qid==row['qualification_id']==spec['qualification_id'] and q['source_identity']==plan['source_identity'],'new qualification/source binding mismatch')
  c.require(spec['condition_id']==row['condition_id'] and c.run_key(spec['identity'])==row['run_key'],'wrong planned condition/run key')
  c.require(policy.is_capacity_spec(spec) and not spec.get('retry_previous_attempt') and not spec.get('retry_reason'),'capacity only; no automatic retry')
  contract=policy.qualification(q,c.digest);vector=(contract['common_capacity_vector'],contract['native_cache_geometry'])
  c.require(common is None or common==vector,'per-workload capacity tuning forbidden');common=vector
  c.require(spec['maximum_result_bytes']<=384*2**20 and spec['timeout_seconds']==10800,'endpoint bounds changed')
  matches=[a for a in s['attempts'] if a['run_key']==row['run_key']];c.require(len(matches)<=1,'repeat condition attempt exists')
  if not matches:specs.append(spec)
  if qid not in qids:
   c.require(coord.register_qualification(qpath)==qid,'registered qualification mismatch');coord.bind_capacity_runtime(qid);qids.add(qid)
 c.require(len(qids)==5,'five exact-input independent qualifications required')
 queue=checked(plan['queue']);published(pub,queue)
 data=read(c.SHARED/'RUN_REGISTRY.json');c.require(not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for r in data['runs'].values()),'existing E application owns original controller work')
 # Explicit imported parser/qualification publication is per new runtime; old
 # CLIENT scientific entries remain present as history and never get relabelled.
 cp=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(cp)
 client['capacity_diagnostic_runtime']=plan['source_identity'];client['capacity_diagnostic_status']='NEW_RUNTIME_INDEPENDENTLY_QUALIFIED_EXACT_FIVE_INPUTS'
 client['capacity_diagnostic_qualifications']=[row['qualification'] for row in plan['conditions'] if row['profile']==policy.OFF]
 c.write_json(cp,client);c.write_json(P/'CLIENT_EXECUTION_QUALIFIED.json',client)
 margin=plan['collector_and_metadata_planning_reserve_bytes'];used=c.output_usage();resources=c.local_resources();shadow=copy.deepcopy(data);shadow[c.FIELD]['target_simulators']=2
 pending=sum(max(0,r.get('disk_growth_bytes',c.FULL_GROWTH)-c.retained_tree_bytes(Path(r['result_directory']))) for r in data['runs'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN)
 c.require(used['new_bytes']+pending+sum(x['maximum_result_bytes'] for x in specs)+margin<=limits['additional_results_max_bytes'] and used['total_bytes']+pending+sum(x['maximum_result_bytes'] for x in specs)+margin<=limits['old_plus_new_results_max_bytes'],'remaining batch plus collector exceeds cumulative generation budget')
 slots=1;why='No pending condition'
 if specs:
  first=specs[0];c.resource_gate(shadow,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,used)
  slots=2;why='Current two-slot forecast passes; original per-launch transaction remains final'
  forecast=copy.deepcopy(shadow);forecast['runs']['READONLY_FORECAST_NOT_LEASE']=dict(status='RESERVED',host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=first['memory_bytes'],disk_growth_bytes=first['maximum_result_bytes'],monitor_reserve_bytes=2*c.GIB,result_directory=str(c.OUTPUT/'CAPACITY_FORECAST_NO_WRITES'),scan=False)
  try:c.resource_gate(forecast,'simulation',1,max(x['memory_bytes'] for x in specs),max(x['maximum_result_bytes'] for x in specs),resources,used)
  except ValueError as e:slots=1;why=str(e)
 with coord.locked() as (data,item):
  c.require(item['controller']['state']=='STOPPED','controller raced admission')
  item['target_simulators']=slots
 c.write_json(P/'QUALIFIED_BATCH_ADMISSION.json',dict(status='PASS_NO_APPLICATION_STARTED_BY_ADMISSION',at_unix=time.time(),source_identity=plan['source_identity'],actual=s['actual_starts'],remaining=s['remaining_start_capacity'],slots=slots,two_slot_reason=why,resources=resources,output_usage=used,collector_margin_bytes=margin,qualification_ids=sorted(qids),pending_conditions=[x['condition_id'] for x in specs]))
 checkpoint('CAPACITY_NEW_RUNTIME_QUALIFIED_BATCH_ADMISSION',extra=[P/'CLIENT_EXECUTION_QUALIFIED.json',P/'QUALIFIED_BATCH_ADMISSION.json'])
 original_roll=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original_roll(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 original_execute=controller.execute;preflight_lock=threading.Lock()
 def guarded_execute(spec,coord):
  with preflight_lock:
   now=coord.snapshot();check_history(now);c.require(now['actual_starts']<46,'approved total46 exhausted');policy.bucket_guard(now,spec)
   current=read(c.SHARED/'RUN_REGISTRY.json');r=c.local_resources();u=c.output_usage();future=sum(max(0,v.get('disk_growth_bytes',c.FULL_GROWTH)-c.retained_tree_bytes(Path(v['result_directory']))) for v in current['runs'].values() if v['status'] in c.ACTIVE and v.get('experiment_id')==c.CAMPAIGN)
   future+=sum(v.get('result_growth_bytes',0) for v in current['resource_leases'].values() if v['status'] in c.ACTIVE and v.get('experiment_id')==c.CAMPAIGN)
   c.require(u['new_bytes']+future+spec['maximum_result_bytes']+margin<=limits['additional_results_max_bytes'] and u['total_bytes']+future+spec['maximum_result_bytes']+margin<=limits['old_plus_new_results_max_bytes'],'collector/metadata cumulative result reserve unavailable')
   c.resource_gate(current,'simulation',1,spec['memory_bytes'],spec['maximum_result_bytes'],r,u)
   c.write_json(P/(spec['condition_id']+'_ACTUAL_PRESTART_REVIEW.json'),dict(status='PASS_BEFORE_ORIGINAL_INSPECT_RESERVE_AND_POPEN',at_unix=time.time(),actual_starts=now['actual_starts'],source_identity=plan['source_identity'],identity=spec['identity'],qualification_id=spec['qualification_id'],resources=r,usage=u,pending_bytes=future,collector_margin_bytes=margin,controller=now['controller'],no_retries=True))
  return original_execute(spec,coord)
 controller.execute=guarded_execute
 result=controller.step(coord,queue);c.write_json(P/'CONTROLLER_RESULT.json',result)
 checkpoint('CAPACITY_CONTROLLER_TERMINAL',extra=[P/'CONTROLLER_RESULT.json',*P.glob('*_ACTUAL_PRESTART_REVIEW.json'),*P.glob('*_D_DELIVERY_RECEIPT.json')])
 now=coord.snapshot();print(json.dumps(dict(status='FIVE_DIAGNOSTIC_PAIRS_CURRENT_ACCEPTED' if all(now['accepted_pairs'].get(x['pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for x in plan['pairs']) else 'PRECISE_LEGAL_STOP_NO_AUTOMATIC_RETRY',actual=now['actual_starts'],remaining=now['remaining_start_capacity'],controller=now['controller'],result=result)),flush=True)
if __name__=='__main__':main()
