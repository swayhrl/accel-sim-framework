"""Replay the R8 spent prefix and every later R9/R6 actual parent join."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');CUTCP='af7320f9d9dc6629'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def check_parent(cell,intent,r9,r6):
 expected=r6 if cell.startswith('E2-AEV100-'+CUTCP+'-') else r9
 assert intent['batch_lease_pid']==expected['pid'] and intent['batch_lease_start_ticks']==expected['start_ticks'],'new attempt has an unqualified parent generation'
 return 'R6_REVIEWED_CUTCP' if expected is r6 else 'R9_WORKINGSET40_FINITE_PARENT'
def verify(q):
 pub=read(T/'control/CONTINUATION_R9_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json');r9=read(T/'control/CONTROLLER_LAUNCH_R9.json');r6=read(T/'control/CONTROLLER_LAUNCH_R6.json');source=T/'tools/revision9/sweep_controller.py'
 assert pub['verified'] and qual['status']=='PASS' and pub['controller_sha256']==qual['controller_sha256']==r9['controller_sha256']==sha(source) and pub['qualification_sha256']==sha(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json')
 amendments=[r for r in q['operational_continuations'] if r['revision']=='R9_WORKINGSET40_AND_TYPED_COPY_WAIT'];assert len(amendments)==1 and amendments[0]['controller_sha256']==sha(source) and amendments[0]['publication_commit']==pub['commit'] and amendments[0]['model_retries']==0
 before=read(T/'control/REQUEST_BEFORE_CONTINUATION_R9.json');assert len(before['consumed'])==141
 s=importlib.util.spec_from_file_location('R9_prior_R8_scheduler_replay',T/'tools/host_scheduler_r8_provenance_v1.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old);prefix_proof=old.verify(before)
 for c,row in before['consumed'].items():assert all(q['consumed'][c][k]==v for k,v in row.items()),'prior spent identity/receipt changed'
 transport=read(T/'control/R8_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R9.json');assert transport['signals_to_scientific_models']==transport['signals_to_original_frontends']==0 and transport['authority_writer_serialized_quiescent_retirement'] and all(r['preserved_or_naturally_closed'] for r in transport['active_generations_after'])
 counts={};joined=[]
 for cell in sorted(set(q['consumed'])-set(before['consumed'])):
  row=q['consumed'][cell];ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);assert sha(ip)==row['intent_sha256'] and intent['uuid']==row['uuid'];kind=check_parent(cell,intent,r9,r6);counts[kind]=counts.get(kind,0)+1;joined.append({'cohort':cell,'uuid':row['uuid'],'scheduler':kind,'parent_pid':intent['batch_lease_pid'],'parent_start_ticks':intent['batch_lease_start_ticks']})
 return {'status':'CURRENT_CONSUMED_SCHEDULER_SOURCE_AND_ACTUAL_PARENT_LEASE_JOINS_REPLAYED','prefix_spent_rows_preserved':141,'R8_prefix_replay':prefix_proof,'current_consumed':len(q['consumed']),'later_parent_counts':counts,'later_attempts':joined,'R9_source_sha256':sha(source),'R9_publication_commit':pub['commit'],'R9_qualification_sha256':sha(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json'),'model_retries':0,'scientific_acceptance_granted_by_this_check':False}
