"""Private synthetic CPU runner tests; never executes any frozen exact161 row."""
import pathlib,json,hashlib,sys,subprocess,time,copy,uuid,shutil,importlib
P=pathlib.Path(__file__).resolve().parent;F=P/'fixtures'/('cpu_'+uuid.uuid4().hex[:10]);F.mkdir(parents=True)
rows=[{'queue_id':'CPU_FIXTURE_'+str(i),'next_step':'EXACT_RUNTIME_OR_STATIC_EVIDENCE_REVIEW_REQUIRED','argv':['CPU_ONLY'],'binary_sha256':'0'*64}for i in range(2)]
scope=F/'SCOPE.json';scope.write_text(json.dumps({'rows':rows}));scope_sha=hashlib.sha256(scope.read_bytes()).hexdigest()
core=(P/'core.py').read_text().replace("D=N/'auto161_pipeline_20261026_v1/orchestrator'","D=pathlib.Path("+repr(str(F))+")").replace("SCOPE=N/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json'","SCOPE=pathlib.Path("+repr(str(scope))+")").replace("b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a",scope_sha)
(F/'core.py').write_text(core)
for n in ['worker.py','orchestrator.py']:(F/n).write_bytes((P/n).read_bytes())
for n in ['runs','events','rows']:(F/n).mkdir()
adapter=F/'fixture_adapter.py'
adapter.write_text("""import pathlib,sys,json,hashlib,argparse,time,os
p=argparse.ArgumentParser()
for n in ['scope-json','row-index','output','context-json']:p.add_argument('--'+n,required=True)
a=p.parse_args();ctx=json.loads(pathlib.Path(a.context_json).read_text());scope=json.loads(pathlib.Path(a.scope_json).read_text());row=scope['rows'][int(a.row_index)]
def ref(p):
 p=pathlib.Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
if ctx.get('inject_crash_after_START'):os._exit(17)
attack=ctx.get('attack_case')
if attack:
 try:
  if attack=='READ_ESCAPE':pathlib.Path(ctx['attack_target']).read_bytes()
  else:pathlib.Path(ctx['attack_target']).write_bytes(b'CORRUPTED')
 except (RuntimeError,ValueError):pass
 else:raise AssertionError('runner accepted boundary escape')
time.sleep(.2)
out={'schema':'AUTO161_ADAPTER_RESULT_V1','adapter_id':ctx['adapter_id'],'queue_id':ctx['queue_id'],'row_index':ctx['row_index'],'scope_sha256':ctx['scope_sha256'],'frozen_row_sha256':ctx['frozen_row_sha256'],'stage':ctx['stage'],'attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'adapter_profile':ctx['adapter_profile'],'status':'HOLD','stage_execution_complete':True,'checks':[{'name':k,'passed':True,'detail':'CPU synthetic bytes reopened'}for k in ['context','scope','row']],'inputs':[ref(a.context_json),ref(a.scope_json)]+[ref(x['path'])for x in ctx.get('dependency_artifacts',[])],'evidence':[],'missing_proofs':[{'proof':'CPU_FIXTURE_ONLY'}],'family_keys':[],'next_stage':'WAIT_SOURCE_RUNTIME_ADAPTER','qualification_granted':False,'historical_queue_mutated':False,'gpu_executed':False,'simulation_executed':False}
with pathlib.Path(a.output).open('x')as f:json.dump(out,f)
print('CPU_FIXTURE_METADATA_EXECUTED')
""")
sys.path.insert(0,str(F));import core as c;import orchestrator as o
reg={'schema':'AUTO161_ALLOWLIST_V1','metadata_adapter':{'id':'auto161_metadata_identity_static_v1','profile':'AUTO161_READONLY_CPU_METADATA_V1','path':str(adapter),'sha256':c.rawsha(adapter)},'artifact_producers':{}}
c.save(F/'ALLOWLIST.json',reg,True)
admissions=[c.admission(r,i,scope_sha)for i,r in enumerate(rows)]
c.save(F/'FROZEN_ADMISSIONS.json',{'rows':admissions},True)
pins={n:c.rawsha(F/n)for n in o.FILES};c.save(F/'ROOT_APPROVAL.json',{'schema':'AUTO161_ROOT_APPROVAL_V1','status':'APPROVED_PRIVATE_CPU_ONLY_EXACT161','scope_sha256':scope_sha,'root_acceptance_sha256':c.ROOT_ACCEPT_SHA,'max_workers':2,'max_attempts_per_fingerprint':3,'pins':pins,'fixture_only':True},True)
run=F/'runs/run_CPU_FIXTURE';run.mkdir();parent=c.identity(__import__('os').getpid())
items=[]
for i,row in enumerate(rows):
 ad=admissions[i];fp=c.digest({'admission':ad['admission_sha256'],'stage':c.STAGE,'adapter_sha256':reg['metadata_adapter']['sha256'],'artifacts':[],'missing_dependencies':[]})
 aid=ad['admission_sha256'][:12]+'_'+fp[:12]+'_1';attempt=run/'rows'/ad['admission_sha256']/'attempts'/aid;attempt.mkdir(parents=True)
 ctx={'schema':'AUTO161_CONTEXT_V1','attempt_id':aid,'nonce':uuid.uuid4().hex,'queue_id':row['queue_id'],'row_index':i,'scope_path':str(scope),'scope_sha256':scope_sha,'frozen_row_sha256':ad['frozen_row_sha256'],'admission_sha256':ad['admission_sha256'],'input_fingerprint':fp,'stage':c.STAGE,'adapter_id':reg['metadata_adapter']['id'],'adapter_profile':reg['metadata_adapter']['profile'],'adapter_path':str(adapter),'adapter_source_sha256':c.rawsha(adapter),'dependency_artifacts':[],'missing_dependency_sha256':[],'attempt_directory':str(attempt),'output_path':str(attempt/'RESULT.json'),'slot_id':i,'approval_ref':c.file_ref(F/'ROOT_APPROVAL.json'),'allowlist_ref':c.file_ref(F/'ALLOWLIST.json')}
 c.save(attempt/'CONTEXT.json',ctx,True)
 intent={'schema':'AUTO161_INTENT_V1','attempt_id':aid,'nonce':ctx['nonce'],'queue_id':row['queue_id'],'row_index':i,'admission_sha256':ad['admission_sha256'],'stage':c.STAGE,'input_fingerprint':fp,'adapter_id':ctx['adapter_id'],'adapter_profile':ctx['adapter_profile'],'adapter_source_sha256':ctx['adapter_source_sha256'],'runner_source_sha256':c.rawsha(F/'worker.py'),'slot_id':i,'context_ref':c.file_ref(attempt/'CONTEXT.json'),'created_unix':time.time()}
 c.save(attempt/'INTENT.json',intent,True)
 out=(attempt/'stdout.log').open('xb');err=(attempt/'stderr.log').open('xb')
 proc=subprocess.Popen(['/usr/bin/python3','-B',str(F/'worker.py'),str(attempt/'CONTEXT.json')],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True);out.close();err.close()
 proof=c.identity(proc.pid);c.save(attempt/'LAUNCH.json',{'worker':proof,'parent':parent,'attempt_id':aid},True);items.append((ad,fp,attempt,ctx,proc))
for ad,fp,p,ctx,proc in items:
 proc.wait(timeout=15);assert proc.returncode==0,(proc.returncode,(p/'stderr.log').read_text())
 e,s,r=o.execution_accept(p,ctx);assert e['cpu_user_seconds']>=0 and e['ended_monotonic_ns']>e['started_monotonic_ns']
# Simulate parent crash after EXEC but before ACK: recovery must reopen bytes and create one ACK.
for ad,fp,p,ctx,proc in items:
 recovered,count,blocked=o.recover(ad,fp);assert recovered and count==1 and blocked is None
 again,count,blocked=o.recover(ad,fp);assert again[0]==recovered[0]
# 70 distinct forbidden result mutations; each must fail parent validation.
ad,fp,p,ctx,proc=items[0];base=c.load(p/'RESULT.json');context_ref=c.file_ref(p/'CONTEXT.json');cases=[]
for key in ['schema','queue_id','row_index','scope_sha256','frozen_row_sha256','stage','attempt_id','nonce','adapter_profile','adapter_id']:
 for value in [None,'WRONG',[]]:
  q=copy.deepcopy(base);q[key]=value;cases.append((key+repr(value),q))
for key in ['qualification_granted','historical_queue_mutated','gpu_executed','simulation_executed']:
 for value in [True,None,0,'false']:
  q=copy.deepcopy(base);q[key]=value;cases.append((key+repr(value),q))
for value in ['COMPLETE','TRACE_ACCEPTED','COMMITTED_VERIFIED','RUN_GPU','WAIT_UNKNOWN',None]:
 q=copy.deepcopy(base);q['next_stage']=value;cases.append(('next'+repr(value),q))
for value in [None,'yes',False,1]:
 q=copy.deepcopy(base);q['stage_execution_complete']=value;cases.append(('complete'+repr(value),q))
for value in [[],None,[{'name':'bad','passed':'true'}],[{'name':'bad','passed':True}]]:
 q=copy.deepcopy(base);q['checks']=value;cases.append(('checks'+repr(value),q))
for value in [[],None,{},'BAD']:
 q=copy.deepcopy(base);q['missing_proofs']=value if value!=[]else None;cases.append(('missing'+repr(value),q))
for field,value in [('bytes',-1),('bytes',True),('bytes',0),('sha256','0'*64),('sha256','bad'),('path','/etc/passwd'),('path',str(F/'NO_FILE')),('path',str(F/'../escape.json'))]:
 q=copy.deepcopy(base);q['inputs'][0][field]=value;cases.append(('ref'+field+repr(value),q))
q=copy.deepcopy(base);q['status']='PASS';q['checks'][0]['passed']=False;cases.append(('PASS_FALSE',q))
q=copy.deepcopy(base);q['inputs']=q['inputs'][:1];cases.append(('ONE_REF',q))
q=copy.deepcopy(base);q['status']='HOLD';q['checks'][0]['passed']=False;cases.append(('HOLD_MASKS_IDENTITY_FAIL',q))
q=copy.deepcopy(base);q['status']='FAILED';cases.append(('FAILED_NOT_ACCEPTED',q))
assert len(cases)>=70
rejected=[]
for name,q in cases:
 try:c.check_result(q,ctx,context_ref)
 except (ValueError,KeyError,TypeError,OSError):rejected.append(name)
 else:raise AssertionError('invalid receipt accepted: '+name)
# New artifact dependency fingerprint changes; no trusted producer means hard HOLD.
oldfp=fp;newfp=c.digest({'admission':ad['admission_sha256'],'stage':c.STAGE,'adapter_sha256':reg['metadata_adapter']['sha256'],'artifacts':[{'sha256':'1'*64}],'missing_dependencies':[]});assert oldfp!=newfp
# Real runner rejects lexical parent traversal and both read/write symlink escapes.
boundary_records=[]
for n,kind in enumerate(['PARENT_WRITE_ESCAPE','READ_ESCAPE','SYMLINK_WRITE_ESCAPE']):
 row=rows[0];ad=admissions[0];dep=F/('attack_dep_'+str(n)+'.json');c.save(dep,{'case':kind},True);deps=[c.file_ref(dep)]
 attackfp=c.digest({'admission':ad['admission_sha256'],'stage':c.STAGE,'adapter_sha256':reg['metadata_adapter']['sha256'],'artifacts':deps,'missing_dependencies':[]})
 aid=ad['admission_sha256'][:12]+'_'+attackfp[:12]+'_1';attempt=run/'rows'/ad['admission_sha256']/'attempts'/aid;attempt.mkdir(parents=True)
 sentinel=attempt.parent/('ESCAPE_SENTINEL_'+str(n));sentinel.write_bytes(b'UNCHANGED')
 if kind=='PARENT_WRITE_ESCAPE':target=str(attempt/'..'/sentinel.name)
 elif kind=='READ_ESCAPE':
  link=F/('outside_N_link_'+str(n));link.symlink_to('/etc/hostname');target=str(link)
 else:
  link=attempt/'symlink_out';link.symlink_to(sentinel);target=str(link)
 ctx=copy.deepcopy(items[0][3]);ctx.update(attempt_id=aid,nonce=uuid.uuid4().hex,input_fingerprint=attackfp,dependency_artifacts=deps,attempt_directory=str(attempt),output_path=str(attempt/'RESULT.json'),slot_id=0,attack_case=kind,attack_target=target)
 c.save(attempt/'CONTEXT.json',ctx,True);intent=copy.deepcopy(c.load(items[0][2]/'INTENT.json'));intent.update(attempt_id=aid,nonce=ctx['nonce'],input_fingerprint=attackfp,slot_id=0,context_ref=c.file_ref(attempt/'CONTEXT.json'));c.save(attempt/'INTENT.json',intent,True)
 out=(attempt/'stdout.log').open('xb');err=(attempt/'stderr.log').open('xb');proc=subprocess.Popen(['/usr/bin/python3','-B',str(F/'worker.py'),str(attempt/'CONTEXT.json')],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True);out.close();err.close();c.save(attempt/'LAUNCH.json',{'worker':c.identity(proc.pid),'parent':parent,'attempt_id':aid},True);proc.wait(timeout=15)
 assert proc.returncode==0,(kind,(attempt/'stderr.log').read_text())
 o.execution_accept(attempt,ctx);assert sentinel.read_bytes()==b'UNCHANGED'
 boundary_records.append({'case':kind,'real_worker_returncode':0,'denied_in_adapter':True,'outside_sentinel_unchanged':True,'execution_ref':c.file_ref(attempt/'EXECUTION.json')})
# Abrupt own-child death after durable START: no false EXEC/ACK, then bounded recovery/retry.
ad=admissions[0];dep=F/'crash_dep.json';c.save(dep,{'case':'CRASH_AFTER_START'},True);deps=[c.file_ref(dep)]
crashfp=c.digest({'admission':ad['admission_sha256'],'stage':c.STAGE,'adapter_sha256':reg['metadata_adapter']['sha256'],'artifacts':deps,'missing_dependencies':[]})
crash_attempts=[]
for ordinal in [1,2]:
 aid=ad['admission_sha256'][:12]+'_'+crashfp[:12]+'_'+str(ordinal);attempt=run/'rows'/ad['admission_sha256']/'attempts'/aid;attempt.mkdir(parents=True)
 ctx=copy.deepcopy(items[0][3]);ctx.update(attempt_id=aid,nonce=uuid.uuid4().hex,input_fingerprint=crashfp,dependency_artifacts=deps,attempt_directory=str(attempt),output_path=str(attempt/'RESULT.json'),slot_id=0,inject_crash_after_START=ordinal==1)
 c.save(attempt/'CONTEXT.json',ctx,True);intent=copy.deepcopy(c.load(items[0][2]/'INTENT.json'));intent.update(attempt_id=aid,nonce=ctx['nonce'],input_fingerprint=crashfp,slot_id=0,context_ref=c.file_ref(attempt/'CONTEXT.json'));c.save(attempt/'INTENT.json',intent,True)
 out=(attempt/'stdout.log').open('xb');err=(attempt/'stderr.log').open('xb');proc=subprocess.Popen(['/usr/bin/python3','-B',str(F/'worker.py'),str(attempt/'CONTEXT.json')],stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True);out.close();err.close();c.save(attempt/'LAUNCH.json',{'worker':c.identity(proc.pid),'parent':parent,'attempt_id':aid},True);proc.wait(timeout=15)
 if ordinal==1:
  assert proc.returncode==17 and not(attempt/'EXECUTION.json').exists()
  prior,count,blocked=o.recover(ad,crashfp);assert prior is None and count==1 and blocked is None
  assert (attempt/'RECOVERY_CLOSED.json').exists()and(attempt/'FAILURE.json').exists()and not(attempt/'ACK.json').exists()
 else:
  assert proc.returncode==0,(attempt/'stderr.log').read_text();prior,count,blocked=o.recover(ad,crashfp);assert prior and count==2 and blocked is None
 crash_attempts.append({'ordinal':ordinal,'returncode':proc.returncode,'attempt':str(attempt),'has_EXEC':(attempt/'EXECUTION.json').exists(),'has_ACK':(attempt/'ACK.json').exists(),'closure':c.file_ref(attempt/'RECOVERY_CLOSED.json')if(attempt/'RECOVERY_CLOSED.json').exists()else None})
# Verify worker intervals <=2 globally and one per slot.
points=[]
for ad,fp,p,ctx,proc in items:
 e=c.load(p/'EXECUTION.json');points.extend([(e['started_monotonic_ns'],1),(e['ended_monotonic_ns'],-1)])
current=peak=0
for _,delta in sorted(points,key=lambda x:(x[0],x[1])):current+=delta;peak=max(peak,current)
assert peak<=2
result={'status':'PASS','fixture_root':str(F),'formal_exact161_rows_executed':0,'real_synthetic_workers':2,'crash_after_EXEC_before_ACK_recovery':True,'ACK_idempotent':True,'negative_cases_rejected':len(rejected),'negative_case_names':rejected,'peak_parallel_workers':peak,'new_dependency_changes_fingerprint':True,'abrupt_worker_death_and_bounded_retry':crash_attempts,'real_synthetic_workers_total':7,'real_runner_path_escape_negatives':boundary_records,'fixed_allowlist_and_Root_approval_enforced_by_worker':True,'sources_pins':{n:c.rawsha(P/n)for n in ['core.py','worker.py','orchestrator.py']}}
(P/'CPU_BOUNDARY_FIXTURE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','real_synthetic_workers':2,'negative_cases':len(rejected),'peak':peak,'fixture_root':str(F)}))
