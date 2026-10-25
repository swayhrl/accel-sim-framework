"""Independently bind preserved147prefix and later R10/R6 parent generations."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');CUTCP='af7320f9d9dc6629'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def check_parent(cell,intent,r10,r6):
 expected=r6 if cell.startswith('E2-AEV100-'+CUTCP+'-') else r10;assert (intent['batch_lease_pid'],intent['batch_lease_start_ticks'])==(expected['pid'],expected['start_ticks']);return 'R6_REVIEWED_CUTCP' if expected is r6 else 'R10_ALL_REMAINING_RESOURCE_GATED_PARENT'
def verify(q):
 pub=read(T/'control/CONTINUATION_R10_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R10_ZERO_MODEL_QUALIFICATION.json');r10=read(T/'control/CONTROLLER_LAUNCH_R10.json');r6=read(T/'control/CONTROLLER_LAUNCH_R6.json');source=T/'tools/revision10/sweep_controller.py';assert pub['verified'] and qual['status']=='PASS' and pub['controller_sha256']==qual['controller_sha256']==r10['controller_sha256']==sha(source) and pub['qualification_sha256']==sha(T/'control/CONTINUATION_R10_ZERO_MODEL_QUALIFICATION.json')
 before=read(T/'control/REQUEST_BEFORE_CONTINUATION_R10.json');assert len(before['consumed'])==147;s=importlib.util.spec_from_file_location('R10_prior_R9_scheduler_replay',T/'tools/host_scheduler_r9_provenance_v1.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old);prefix_proof=old.verify(before)
 for c,row in before['consumed'].items():assert all(q['consumed'][c][k]==v for k,v in row.items())
 amendments=[r for r in q['operational_continuations'] if r['revision']=='R10_ALL_REMAINING_RESOURCE_GATED'];assert len(amendments)==1 and amendments[0]['controller_sha256']==sha(source) and amendments[0]['publication_commit']==pub['commit'] and amendments[0]['model_retries']==0
 pp=T/'control/ALL_REMAINING_DISPATCH_POLICY_R10.json';p=read(pp);assert q['all_remaining_dispatch_policy']==dict(p,policy_sha256=sha(pp)) and p['maximum_jobs']==288 and p['host_plan_sha256']==sha(T/'control/HOST_EXECUTION_PLAN_V2.json') and qual['policy_sha256']==sha(pp) and qual['classifier_sha256']==sha(T/'tools/sweep_failure_review_telemetry_v1.py')
 transport=read(T/'control/R9_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R10.json');assert transport['signals_to_scientific_models']==transport['signals_to_original_frontends']==0 and transport['authority_writer_serialized_quiescent_retirement'] and all(r['preserved_or_naturally_closed'] for r in transport['active_generations_after'])
 counts={};joined=[]
 for cell in sorted(set(q['consumed'])-set(before['consumed'])):
  row=q['consumed'][cell];ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');i=read(ip);assert sha(ip)==row['intent_sha256'] and i['uuid']==row['uuid'];kind=check_parent(cell,i,r10,r6);counts[kind]=counts.get(kind,0)+1;joined.append({'cohort':cell,'uuid':row['uuid'],'scheduler':kind,'parent_pid':i['batch_lease_pid'],'parent_start_ticks':i['batch_lease_start_ticks']})
 return {'status':'CURRENT_CONSUMED_SCHEDULER_SOURCE_AND_ACTUAL_PARENT_LEASE_JOINS_REPLAYED','prefix_spent_rows_preserved':147,'R9_prefix_replay':prefix_proof,'current_consumed':len(q['consumed']),'later_parent_counts':counts,'later_attempts':joined,'R10_source_sha256':sha(source),'R10_publication_commit':pub['commit'],'dispatch_policy_sha256':sha(pp),'model_retries':0,'scientific_acceptance_granted_by_this_check':False}
