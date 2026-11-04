"""Real flock regression in an isolated CPU sandbox; never touches native authority."""
from pathlib import Path
import ast,copy,fcntl,hashlib,json,multiprocessing as mp,time,types
O=Path(__file__).resolve().parent
RUNTIME=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
ROOT=O/'cpu_lock_fixture'
ROOT.mkdir(exist_ok=True);(ROOT/'control/specs').mkdir(parents=True,exist_ok=True)
LOCK=ROOT/'REGISTRY_UPDATE.lock'
SOURCE=O/'perf16_native.py';OLD=O/'ORIGINAL_perf16_native_635149.py'
RESOURCE=RUNTIME/'tools/perf16_resources.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
cohort='E2-DTCPFV2-d984ea5475a581ad-DH-PHYS768-OOPIB192-V1'
original=RUNTIME/'control/specs'/(cohort+'.json');raw=original.read_bytes()
canon=ROOT/'control/specs'/(cohort+'.json');canon.write_bytes(raw);alias=ROOT/'control'/(cohort+'_SPEC.json');alias.write_bytes(raw)
EVIDENCE=ROOT/'TYPED_SAFETY_EVIDENCE.json';EVIDENCE.write_text('{"CPU_fixture_only":true}\n')

def extracted(path,name,namespace):
 tree=ast.parse(path.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path)+':CPU_AST_FUNCTION_ONLY','exec'),namespace);return namespace[name]

def worker(conn,mode):
 start=time.monotonic();calls=[];reentry=[]
 def forbid(*args,**kwargs):reentry.append(True);raise AssertionError('FORBIDDEN_AUTHORITY_OR_SPEC_REENTRY')
 ns={'R':ROOT,'REQ':REQ,'read':read,'sha':sha,'registered':forbid,'spec_for':forbid,'authority':forbid}
 pure_ns={'REQ':REQ,'sha':sha,'VARIANT_TOKENS':{'PHYS768_OOPIB192_TAG64x8':'unused','PHYS1024_OOPIB192_TAG64x8':'unused'}}
 ns['admission_hold']=extracted(RESOURCE,'admission_hold',pure_ns)
 guard=extracted(SOURCE,'guard_model_mutation',ns)
 spec=read(canon);own={'request':REQ,'state':'ARMED','budget':16,'remaining':16,'consumed':{},'admitted_specs':{cohort:sha(canon)},'admission_holds':{}}
 current={'registered_future_requests':{REQ:own,'FOREIGN_OPTIONAL_FIELDS':{'budget':7,'opaque_history':{'UUID':'CPU_PEER_SENTINEL'}}},'old_source_history':['CPU_HISTORY_SENTINEL'],'qualification_history':['CPU_HISTORY_SENTINEL']}
 if mode in ['PROFILE_HOLD','COHORT_HOLD']:
  own['admission_holds'][spec['profile']if mode=='PROFILE_HOLD'else cohort]={'classification':'CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD','decided_by':'DTC_MAIN','profile':spec['profile'],'reason':'CPU fixture only, no actual safety decision','created_utc':'CPU_ONLY','request':REQ,'evidence_path':str(EVIDENCE),'evidence_sha256':sha(EVIDENCE)}
 if mode=='BAD_SPEC_SHA':own['admitted_specs'][cohort]='0'*64
 if mode=='CONSUMED_COMPLETION':own['consumed'][cohort]={'uuid':'CPU_ONLY_NOT_A_NATIVE_UUID'};own['state']='STOP_UNACCEPTED_WITH_UNUSED_CREDITS';own['admission_holds'][spec['profile']]={'intentionally_irrelevant_consumed_fixture':True}
 before=copy.deepcopy(current)
 try:
  with LOCK.open('a+b')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);conn.send({'state':'LOCK_EX_HELD','pid':__import__('os').getpid()});assert conn.recv()=='PROCEED_AFTER_COMPETING_LOCK_CHECK'
   try:guard(current,cohort,lambda cur:calls.append('ONLY_CPU_MUTATOR_CALLED'));status='MUTATOR_ALLOWED'
   except AssertionError as exc:status='GUARD_REFUSED';reason=str(exc)
   result={'mode':mode,'status':status,'reason':locals().get('reason'),'mutator_calls':len(calls),'authority_or_spec_reentry_calls':len(reentry),'whole_mock_registry_unchanged':current==before,'elapsed_seconds':time.monotonic()-start,'parent_lock_proof_before_guard':True,'actual_resource_admission_hold_source_sha256':sha(RESOURCE),'actual_native_or_registry_calls':0}
  conn.send(result)
 except BaseException as exc:conn.send({'mode':mode,'unexpected_error':repr(exc)})
 finally:conn.close()

if __name__=='__main__':
 checks=[];results=[]
 def ck(name,value):assert value,name;checks.append({'check':name,'PASS':True})
 ctx=mp.get_context('fork')
 for mode in ['PASS','PROFILE_HOLD','COHORT_HOLD','BAD_SPEC_SHA','CONSUMED_COMPLETION']:
  parent,child=ctx.Pipe();proc=ctx.Process(target=worker,args=(child,mode),name='CPU_ONLY_FLOCK_REGRESSION_'+mode);proc.start();child.close();assert parent.poll(5),'child lock not acquired';first=parent.recv();ck(mode+'_actual_child_LOCK_EX',first['state']=='LOCK_EX_HELD')
  with LOCK.open('a+b')as competitor:
   blocked=False
   try:fcntl.flock(competitor,fcntl.LOCK_SH|fcntl.LOCK_NB)
   except BlockingIOError:blocked=True
   ck(mode+'_different_process_shared_lock_is_blocked',blocked)
  parent.send('PROCEED_AFTER_COMPETING_LOCK_CHECK');ready=parent.poll(5)
  if not ready:
   # This PID is exclusively this sandbox CPU fixture, never an owner/frontend/model.
   proc.terminate();proc.join();raise AssertionError('CPU_FIXTURE_GUARD_LOCK_REENTRY_TIMEOUT:'+mode)
  result=parent.recv();proc.join(5);ck(mode+'_child_exited_normally_no_deadlock',proc.exitcode==0 and'error'not in result and'unexpected_error'not in result);ck(mode+'_no_nested_authority_or_spec_reader',result['authority_or_spec_reentry_calls']==0);ck(mode+'_whole_mock_registry_unchanged',result['whole_mock_registry_unchanged']);allow=mode in ['PASS','CONSUMED_COMPLETION'];ck(mode+'_mutator_exact_expected_path',result['mutator_calls']==int(allow)and result['status']==('MUTATOR_ALLOWED'if allow else'GUARD_REFUSED'));results.append(result)
 # Production originals are evidence, not installation targets.
 ck('old_actual_native_source_still_635149',sha(RUNTIME/'tools/perf16_native.py')=='635149a0085f9bb4c12228c50615ad7a3b82868192cc36bd6cabab8561cf4b8c')
 ck('original_canonical_bytes_unchanged',original.read_bytes()==raw)
 report={'schema':'DTC_CODESIGN16_PRE_INTENT_LOCK_FORWARD_CPU_V1','status':'PASS_REAL_CROSS_PROCESS_SANDBOX_FLOCK_REGRESSION_ONLY','new_native_source_sha256':sha(SOURCE),'original_source_sha256':sha(OLD),'resource_helper_source_sha256':sha(RESOURCE),'actual_source_spec':{'path':str(original),'sha256':hashlib.sha256(raw).hexdigest()},'checks':checks,'count':len(checks),'results':results,'real_authority_files_accessed_or_written':False,'real_native_source_installed_by_C':False,'new_science_consumptions_or_model_starts':0,'old_frozen_C_package_modified':False}
 (O/'CPU_LOCK_REGRESSION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'cases':len(results),'new_source_sha256':sha(SOURCE)}))
