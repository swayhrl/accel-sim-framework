#!/usr/bin/env python3
"""Finite anti-cheat fixture: synthetic IDs only, real tiny CPU children, no production execution."""
import collections,copy,hashlib,json,os,pathlib,shutil,subprocess,sys,time,uuid
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit_common_v1 import Reader,AuditError,need,canonical,process_key,interval_checks
from audit_attempt_v1 import audit_attempt,admission_for,STAGE,PROFILE
from check_auto161_acceptance_v1 import audit
from check_production_preservation_v1 import preservation
from check_binary_attestation_v1 import check_binary_attestation
def save(p,x):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n')
def obj(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):
 p=pathlib.Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def ident(pid):
 s=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
 return {'pid':pid,'start_ticks':int(s[19]),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':s[0],'parent_pid':int(s[1])}
root=HERE/('fixture_'+str(time.time_ns()));root.mkdir()
pipeline=root/'pipeline';run=pipeline/'runs/run_synthetic';run.mkdir(parents=True)
for sub in ['rows','events']:(pipeline/sub).mkdir()
shutil.copyfile(HERE/'fixture_cpu_worker_v1.py',pipeline/'worker.py')
shutil.copyfile(HERE/'fixture_cpu_adapter_v1.py',pipeline/'adapter.py')
for name in ['core.py','orchestrator.py']:(pipeline/name).write_text('# SYNTHETIC FIXTURE SOURCE ONLY\n')
rows=[{'queue_id':'SYNTHETIC_AUDIT_%03d'%i,'next_step':'ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED','argv':['/synthetic/bin/test','--case',str(i)],'job_sha256':canonical({'synthetic_job':i}),'binary_sha256':'a'*64,'declared_identity_sha256':canonical({'identity':i}),'profile_families_nonexclusive':['SYNTHETIC_ONLY']} for i in range(161)]
for row in rows:
 job=root/'jobs'/(row['queue_id']+'.json');save(job,{'task':{'binary_sha256':row['binary_sha256'],'argv':row['argv']}});row['job_sha256']=sha(job);row['job_snapshot_path']=str(job)
scope=root/'SCOPE.json';save(scope,{'rows':rows});scope_sha=sha(scope)
accept=root/'ROOT_ACCEPTANCE.json';save(accept,{'frozen_ids':[x['queue_id'] for x in rows],'frozen_todo_sha256':scope_sha})
admissions=[admission_for(x,i,scope_sha) for i,x in enumerate(rows)]
save(pipeline/'FROZEN_ADMISSIONS.json',{'schema':'AUTO161_FROZEN_ADMISSIONS_V1','scope_ref':ref(scope),'count':161,'rows':admissions})
allow={'id':'fixture_cpu_metadata_v1','profile':PROFILE,'path':str(pipeline/'adapter.py'),'sha256':sha(pipeline/'adapter.py')}
save(pipeline/'ALLOWLIST.json',{'schema':'AUTO161_ADAPTER_ALLOWLIST_V1','metadata_adapter':allow,'artifact_producers':{}})
pins={name:sha(pipeline/name) for name in ['core.py','worker.py','orchestrator.py','ALLOWLIST.json','FROZEN_ADMISSIONS.json']}
approval={'schema':'AUTO161_ROOT_APPROVAL_V1','status':'APPROVED_PRIVATE_CPU_ONLY_EXACT161','scope_sha256':scope_sha,'root_acceptance_sha256':sha(accept),'max_workers':2,'max_attempts_per_fingerprint':3,'pins':pins}
save(pipeline/'ROOT_APPROVAL.json',approval);approval_sha=sha(pipeline/'ROOT_APPROVAL.json')
parent=ident(os.getpid());mono=time.monotonic_ns()
save(run/'RUN_IDENTITY.json',{'schema':'AUTO161_RUN_IDENTITY_V1','run_id':run.name,'orchestrator':parent,'started_unix':time.time(),'started_monotonic_ns':mono,'deadline_monotonic_ns':mono+3600*10**9,'approval_ref':ref(pipeline/'ROOT_APPROVAL.json'),'pins':pins})
events=[]
def event(kind,**fields):
 seq=len(events);p=pipeline/'events'/('%012d.json'%seq)
 save(p,{'schema':'AUTO161_EVENT_V1','sequence':seq,'prev_sha256':sha(events[-1]) if events else None,'kind':kind,'unix':time.time(),**fields});events.append(p)
event('FINITE_ROUND_START',run_id=run.name)
directories=[]
for ad,row in zip(admissions,rows):
 fp=canonical({'admission':ad['admission_sha256'],'stage':STAGE,'adapter_sha256':allow['sha256'],'artifacts':[],'missing_dependencies':[]})
 attempt_id=ad['admission_sha256'][:12]+'_'+fp[:12]+'_1'
 d=run/'rows'/ad['admission_sha256']/'attempts'/attempt_id;d.mkdir(parents=True);directories.append(d)
 ctx={'schema':'AUTO161_CONTEXT_V1','attempt_id':attempt_id,'nonce':uuid.uuid4().hex,'queue_id':row['queue_id'],'row_index':ad['row_index'],'scope_path':str(scope),'scope_sha256':scope_sha,'frozen_row_sha256':ad['frozen_row_sha256'],'admission_sha256':ad['admission_sha256'],'input_fingerprint':fp,'stage':STAGE,'adapter_id':allow['id'],'adapter_profile':PROFILE,'adapter_path':allow['path'],'adapter_source_sha256':allow['sha256'],'dependency_artifacts':[],'missing_dependency_sha256':[],'attempt_directory':str(d),'output_path':str(d/'RESULT.json'),'slot_id':0}
 save(d/'CONTEXT.json',ctx)
 intent={'schema':'AUTO161_INTENT_V1','attempt_id':attempt_id,'nonce':ctx['nonce'],'queue_id':row['queue_id'],'row_index':ad['row_index'],'admission_sha256':ad['admission_sha256'],'stage':STAGE,'input_fingerprint':fp,'adapter_id':allow['id'],'adapter_profile':PROFILE,'adapter_source_sha256':allow['sha256'],'runner_source_sha256':pins['worker.py'],'slot_id':0,'context_ref':ref(d/'CONTEXT.json')}
 save(d/'INTENT.json',intent)
 with (d/'stdout.log').open('wb') as out,(d/'stderr.log').open('wb') as err:
  p=subprocess.run([sys.executable,'-B',str(pipeline/'worker.py'),str(d/'CONTEXT.json')],stdout=out,stderr=err,timeout=10)
 assert p.returncode==0,(p.returncode,(d/'stderr.log').read_text())
 exe=obj(d/'EXECUTION.json');result=obj(d/'RESULT.json')
 ack={'schema':'AUTO161_ACK_V1','attempt_id':attempt_id,'queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'input_fingerprint':fp,'stage':STAGE,'accepted_result_status':result['status'],'next_stage':result['next_stage'],'execution_ref':ref(d/'EXECUTION.json'),'process_start_ref':ref(d/'PROCESS_START.json'),'result_ref':ref(d/'RESULT.json'),'intent_ref':ref(d/'INTENT.json'),'context_ref':ref(d/'CONTEXT.json'),'stdout_ref':ref(d/'stdout.log'),'stderr_ref':ref(d/'stderr.log'),'worker':exe['worker'],'parent':exe['parent'],'slot_id':0,'started_monotonic_ns':exe['started_monotonic_ns'],'ended_monotonic_ns':exe['ended_monotonic_ns'],'qualification_granted':False,'exact_trace_qualified':False,'ack_unix':time.time()}
 save(d/'ACK.json',ack);event('ACK_REOPEN_VERIFIED',attempt_id=attempt_id,queue_id=row['queue_id'],ack_ref=ref(d/'ACK.json'))
 save(pipeline/'rows'/ad['admission_sha256']/'STATE.json',{'schema':'AUTO161_ROW_STATE_V1','queue_id':row['queue_id'],'admission_sha256':ad['admission_sha256'],'status':result['next_stage'],'attempt_id':attempt_id,'input_fingerprint':fp,'latest_ack_ref':ref(d/'ACK.json'),'attempt_count':1,'stage_execution_complete':True,'exact_trace_qualified':False})
config={'fixture':True,'root':str(root),'scope_path':str(scope),'scope_sha256':scope_sha,'root_acceptance_path':str(accept),'root_acceptance_sha256':sha(accept)}
save(root/'FIXTURE_CONFIG.json',config)
report=audit(pipeline,run,approval_sha,config)
assert report['status']=='ACCEPTED_REAL_CPU_EXECUTION_COVERAGE_NOT_TRACE_QUALIFICATION',report['errors']
assert report['real_CPU_execution_covered_ids']==161 and report['trace_qualified']==0 and report['peak_verified_CPU_processes']==1
cases=[{'case':'161_unique_synthetic_IDs_161_real_CPU_children_full_independent_ACK_reopen','status':'PASS','coverage':161,'production_acceptance':False,'peak_CPU':1}]
# A manifest and an invented success summary cannot substitute for any execution.
for original,hidden in [(run/'rows',root/'HIDDEN_RUN_ROWS'),(pipeline/'rows',root/'HIDDEN_STATES'),(pipeline/'events',root/'HIDDEN_EVENTS')]:original.rename(hidden)
(pipeline/'rows').mkdir();(pipeline/'events').mkdir();shutil.copyfile(root/'HIDDEN_EVENTS/000000000000.json',pipeline/'events/000000000000.json')
save(run/'SUMMARY.json',{'accepted_stage_receipts':161,'status':'PASS','exact_trace_qualified':161})
listing=audit(pipeline,run,approval_sha,config);assert listing['status']=='REJECTED_OR_INCOMPLETE' and listing['real_CPU_execution_covered_ids']==0 and listing['trace_qualified']==0
cases.append({'case':'161_registration_plus_fake_stdout_summary_is_zero_real_coverage','status':'REJECTED_NOT_EXECUTED','coverage':0})
(run/'SUMMARY.json').unlink();shutil.rmtree(pipeline/'rows');shutil.rmtree(pipeline/'events')
for original,hidden in [(run/'rows',root/'HIDDEN_RUN_ROWS'),(pipeline/'rows',root/'HIDDEN_STATES'),(pipeline/'events',root/'HIDDEN_EVENTS')]:hidden.rename(original)
d=directories[0];ad=admissions[0];row=rows[0]
saved={p.name:p.read_bytes() for p in d.iterdir() if p.is_file()}
def restore():
 for p in d.iterdir():
  if p.is_file() and p.name not in saved:p.unlink()
 for name,body in saved.items():(d/name).write_bytes(body)
def reseal():
 intent=obj(d/'INTENT.json');intent['context_ref']=ref(d/'CONTEXT.json');save(d/'INTENT.json',intent)
 start=obj(d/'PROCESS_START.json');start['context_ref']=ref(d/'CONTEXT.json');save(d/'PROCESS_START.json',start)
 exe=obj(d/'EXECUTION.json')
 if (d/'RESULT.json').exists():exe['result_ref']=ref(d/'RESULT.json')
 save(d/'EXECUTION.json',exe)
 if (d/'ACK.json').exists():
  ack=obj(d/'ACK.json')
  for key,name in [('execution_ref','EXECUTION.json'),('process_start_ref','PROCESS_START.json'),('result_ref','RESULT.json'),('intent_ref','INTENT.json'),('context_ref','CONTEXT.json'),('stdout_ref','stdout.log'),('stderr_ref','stderr.log')]:
   if (d/name).exists():ack[key]=ref(d/name)
  save(d/'ACK.json',ack)
def change(name,fn):
 value=obj(d/name);fn(value);save(d/name,value)
def check_one():
 return audit_attempt(Reader([root]),d,ad,row,allow,pins['worker.py'],parent,live_probe=lambda pid:None,require_authority_projection=False)
def reject(label,mutate,reseal_refs=True):
 restore();mutate()
 if reseal_refs:reseal()
 try:out=check_one()
 except (AuditError,KeyError,ValueError,OSError,TypeError) as error:
  cases.append({'case':label,'status':'REJECTED','code':getattr(error,'code',type(error).__name__)});return
 assert not out['execution_covered'],(label,'was falsely accepted')
 cases.append({'case':label,'status':'NOT_COVERED','state':out['status']})
reject('unknown_adapter_ID',lambda:change('INTENT.json',lambda x:x.update(adapter_id='unknown')))
reject('wrong_adapter_profile',lambda:change('CONTEXT.json',lambda x:x.update(adapter_profile='ORDINARY_ADA7')))
reject('unknown_adapter_source_SHA',lambda:change('CONTEXT.json',lambda x:x.update(adapter_source_sha256='0'*64)))
reject('wrong_queue_ID',lambda:change('CONTEXT.json',lambda x:x.update(queue_id='another_job')))
reject('wrong_frozen_row_hash',lambda:change('CONTEXT.json',lambda x:x.update(frozen_row_sha256='0'*64)))
reject('wrong_input_fingerprint',lambda:change('CONTEXT.json',lambda x:x.update(input_fingerprint='0'*64)))
reject('intent_missing_execution_and_ACK',lambda:[(d/n).unlink() for n in ['EXECUTION.json','ACK.json']],False)
reject('failed_execution_missing_ACK_not_covered',lambda:((d/'ACK.json').unlink(),change('EXECUTION.json',lambda x:x.update(returncode=1,error='fixture failure')),save(d/'FAILURE.json',{'error':'fixture failure','unix':time.time()})),False)
reject('ACK_with_reused_PID_ticks',lambda:change('ACK.json',lambda x:x['worker'].update(start_ticks=x['worker']['start_ticks']+1)))
reject('RESULT_fake_pid',lambda:change('RESULT.json',lambda x:x['execution_evidence'].update(pid=999999999)))
reject('RESULT_gpu_execution_overclaim',lambda:change('RESULT.json',lambda x:x.update(gpu_executed=True)))
reject('RESULT_qualified_trace_overclaim',lambda:change('ACK.json',lambda x:x.update(exact_trace_qualified=True)))
reject('RESULT_legacy_profile_overclaim',lambda:change('RESULT.json',lambda x:x.update(actual_GPU_producer_profile_inferred_from_legacy55=True)))
reject('RESULT_stage_PASS_with_failed_check',lambda:change('RESULT.json',lambda x:(x.update(status='PASS'),x['checks'][0].update(passed=False))))
reject('RESULT_HOLD_hiding_failed_identity_check',lambda:change('RESULT.json',lambda x:x['checks'][0].update(passed=False)))
reject('RESULT_FAILED_cannot_have_success_ACK',lambda:change('RESULT.json',lambda x:x.update(status='FAILED')))
reject('RESULT_no_specific_missing_proof',lambda:change('RESULT.json',lambda x:x.update(missing_proofs=[])))
reject('RESULT_dependency_wrong_historical_identity',lambda:change('RESULT.json',lambda x:x['missing_proofs'][0]['binding'].update(binary_sha256='0'*64)))
reject('stdout_PASS_does_not_replace_RESULT',lambda:((d/'RESULT.json').unlink(),(d/'stdout.log').write_text('PASS TRACE_COMPLETE 161\n')),True)
reject('RESULT_evidence_path_escape',lambda:change('RESULT.json',lambda x:x['inputs'].append({'path':'/etc/passwd','bytes':1,'sha256':'0'*64})))
reject('ACK_cross_attempt_path',lambda:change('ACK.json',lambda x:x['process_start_ref'].update(path=str(directories[1]/'PROCESS_START.json'))),False)
reject('ACK_wrong_next_stage',lambda:change('ACK.json',lambda x:x.update(next_stage='TRACE_QUALIFIED')))
reject('malformed_file_ref_boolean_bytes',lambda:change('RESULT.json',lambda x:x['inputs'][0].update(bytes=True)))
restore()
# The body-size gate refuses hashing before consuming a byte budget.
limited=root/'SMALL_SIZE_LIMIT_FIXTURE';limited.write_bytes(b'x'*128)
limited_reader=Reader([root],max_file=64)
try:limited_reader.bytes(limited)
except AuditError as error:assert error.code=='LONG_BODY_NOT_HASHED' and limited_reader.total==0;cases.append({'case':'oversized_body_not_hashed','status':'REJECTED_BEFORE_READ'})
else:raise AssertionError('oversized body was read')
# An active PID number with different ticks is not the historical worker.
for name in ['EXECUTION.json','ACK.json']:(d/name).unlink()
start=obj(d/'PROCESS_START.json')
try:audit_attempt(Reader([root]),d,ad,row,allow,pins['worker.py'],parent,live_probe=lambda pid:dict(start['worker'],start_ticks=start['worker']['start_ticks']+1))
except AuditError as error:assert error.code=='REUSED_OR_DEAD_PID_CANNOT_BE_LIVE';cases.append({'case':'reused_live_PID_number_rejected','status':'REJECTED'})
else:raise AssertionError('reused live PID accepted')
restore()
for label,intervals in [
 ('CPU_gt2',[{'queue_id':str(i),'slot':i%2,'start':1,'end':10} for i in range(3)]),
 ('overlapping_same_job',[{'queue_id':'same','slot':i,'start':1,'end':10} for i in range(2)]),
 ('overlapping_same_slot',[{'queue_id':str(i),'slot':0,'start':1,'end':10} for i in range(2)])]:
 try:interval_checks(intervals)
 except AuditError as error:cases.append({'case':label,'status':'REJECTED','code':error.code})
 else:raise AssertionError(label+' accepted')
# Preservation uses only fake control files. Progress of an unrelated row is allowed.
fake_queue=root/'QUEUE.json';historical=[{'id':x['queue_id'],'status':'PENDING_SPECIALIST_EXTENSION','identity':i} for i,x in enumerate(rows)]
save(fake_queue,historical+[{'id':'FOREIGN','status':'RUNNING'}]);sdk=root/'SDK.py';sdk.write_text('# frozen SDK\n');ordinary=root/'ordinary.py';ordinary.write_text('# frozen worker\n');stop=root/'STOP';stop.write_text('old own STOP\n')
base=root/'BASELINE.json';save(base,{'historical161_rows':historical,'QUEUE_file_sha256_at_baseline':sha(fake_queue),'STOP_sha256':sha(stop),'current_SDK_controller_sha256':sha(sdk),'current_ordinary_worker_sha256':sha(ordinary)})
kwargs={'baseline_path':base,'baseline_sha':sha(base),'queue_path':fake_queue,'stop_path':stop,'sdk_path':sdk,'worker_path':ordinary}
preservation(Reader([root]),set(x['queue_id'] for x in rows),**kwargs)
live=obj(fake_queue);live[-1]['status']='COMMITTED_VERIFIED';save(fake_queue,live);stop.write_text('legitimate foreign advancement')
observed=preservation(Reader([root]),set(x['queue_id'] for x in rows),**kwargs);assert observed['global_QUEUE_hash_changed_observation'] and observed['STOP_hash_changed_observation']
cases.append({'case':'foreign_QUEUE_STOP_progress_observed_not_false_failure','status':'PASS'})
live[0]['status']='SEALED';save(fake_queue,live)
try:preservation(Reader([root]),set(x['queue_id'] for x in rows),**kwargs)
except AuditError as error:assert error.code=='HISTORICAL161_CHANGED';cases.append({'case':'historical161_mutation','status':'REJECTED'})
else:raise AssertionError('historical mutation accepted')
live[0]['status']='PENDING_SPECIALIST_EXTENSION';save(fake_queue,live);ordinary.write_text('# changed\n')
try:preservation(Reader([root]),set(x['queue_id'] for x in rows),**kwargs)
except AuditError as error:assert error.code=='EXISTING_ORDINARY_WORKER_CHANGED';cases.append({'case':'frozen_existing_worker_changed','status':'REJECTED'})
else:raise AssertionError('worker change accepted')
# Fake binary attestation metadata is independently joined, without reading bodies.
att=root/'BINARY_ATTEST.json';groups=collections.defaultdict(list)
for r in rows:groups[(r['argv'][0],r['binary_sha256'])].append(r['queue_id'])
att_obj={'schema':'EXACT161_CURRENT_BINARY_READONLY_ATTESTATION_V1','rows':[{'path':p,'resolved_path':p,'expected_sha256':h,'actual_sha256':h,'source_ids':ids,'status':'MATCH_CLOSED_CURRENT_BINARY','before':{'size':1},'after':{'size':1},'bytes':1} for (p,h),ids in groups.items()],'closed':True,'no_GPU':True,'no_CUDA_init_or_product_execution':True,'source_files_modified':False,'scope_sha256':scope_sha}
save(att,att_obj);check_binary_attestation(Reader([root]),att,rows,sha(att),scope_sha);cases.append({'case':'binary_path_SHA_sourceIDs_join','status':'PASS'})
att_obj['rows'][0]['source_ids']=att_obj['rows'][0]['source_ids'][:-1];save(att,att_obj)
try:check_binary_attestation(Reader([root]),att,rows,sha(att),scope_sha)
except AuditError as error:cases.append({'case':'binary_attestation_summary_true_but_missing_ID','status':'REJECTED','code':error.code})
else:raise AssertionError('binary summary lie accepted')
# Duplicate admissions remain invalid even if a fixture authority re-pins a bad manifest.
saved_ad=(pipeline/'FROZEN_ADMISSIONS.json').read_bytes();bad=obj(pipeline/'FROZEN_ADMISSIONS.json');bad['rows'][1]=bad['rows'][0];save(pipeline/'FROZEN_ADMISSIONS.json',bad)
new_approval=copy.deepcopy(approval);new_approval['pins']['FROZEN_ADMISSIONS.json']=sha(pipeline/'FROZEN_ADMISSIONS.json');save(pipeline/'ROOT_APPROVAL.json',new_approval)
try:audit(pipeline,run,sha(pipeline/'ROOT_APPROVAL.json'),config)
except AuditError as error:assert error.code=='DUPLICATE_OR_MODIFIED_ADMISSION';cases.append({'case':'duplicate_job_admission_despite_count161','status':'REJECTED'})
else:raise AssertionError('duplicate admission accepted')
(pipeline/'FROZEN_ADMISSIONS.json').write_bytes(saved_ad);save(pipeline/'ROOT_APPROVAL.json',approval)
result={'schema':'AUTO161_AUDIT_SYNTHETIC_QUALIFICATION_V1','status':'ALL_SMALL_SYNTHETIC_CHECKER_TESTS_PASS','cases':cases,'case_count':len(cases),'synthetic_real_CPU_attempts':161,'max_CPU_parallelism_actual':1,'real_production_161_executed':False,'new_GPU_or_simulator_executions':0,'production_QUEUE_STOP_workers_untouched':True,'fixture_directory':str(root),'positive_report':{'coverage':report['real_CPU_execution_covered_ids'],'trace_qualified':0,'production_acceptance':False},'checker_result_status_not_trace_qualification':True}
save(HERE/'AUDIT_SYNTHETIC_QUALIFICATION_V1.json',result)
print(json.dumps(result))
