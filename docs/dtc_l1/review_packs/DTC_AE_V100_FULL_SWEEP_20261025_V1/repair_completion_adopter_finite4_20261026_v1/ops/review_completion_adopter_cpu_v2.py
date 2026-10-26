"""Independent guard/delegation fixture. Never runs model, archive, or real finish."""
import pathlib,json,hashlib,importlib.util,tempfile,types,copy,fcntl,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');SOURCE=F/'ops/repair_completion_adopter_v1.py';REALR=F/'validation'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def dump(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,sort_keys=True)+'\n')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
source_sha=sha(SOURCE);checks=[]
def ok(n,v):assert v,n;checks.append(n)
with tempfile.TemporaryDirectory(prefix='INDEPENDENT_ADOPTER_CPU_',dir=F/'ops') as td:
 top=P(td)
 def setup(label):
  m=load('independent_adopter_'+label,SOURCE);m.R=top/label;m.O=m.R/'ops';m.BINDING=m.O/'binding.json';dump(m.BINDING,{'CPU_FIXTURE':True});m.model_state=lambda pid,start:'RECORDED_GENERATION_GONE';m.launcher_absent=lambda pid:True;cell=m.CELLS[0];uid='00000000-0000-4000-a000-000000000001';out=m.R/'DTC/run/results'/uid
  (m.R/'DTC/control').mkdir(parents=True);(m.R/'analysis').mkdir(parents=True);(m.R/'tools').symlink_to(REALR/'tools')
  spec={'request':m.REQ,'cohort':cell,'program':'myocyte'};sp=m.R/'control/specs'/(cell+'.json');dump(sp,spec);ip=m.R/'control/qualification_ledger'/(cell+'.INTENT.json');dump(ip,{'cohort':cell,'uuid':uid,'output':str(out)});done={'cohort':cell,'uuid':uid,'output':str(out),'stop_reason':None,'launcher_wait_returncode':0,'native_simulator_observed':True,'actual_simulator_wait_and_file_evidence':'actual_file_process_network.log','launcher_is_strace_parent_of_native_simulator':True};dp=ip.with_name(cell+'.DONE.json');dump(dp,done);dump(out/'NATIVE_EXIT.json',done);dump(out/'NATIVE_LAUNCH.json',{'launcher_pid':900000002});dump(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':900000001,'start_ticks':123})
  row={'uuid':uid,'intent_sha256':sha(ip),'execution_receipt':copy.deepcopy(done)};q={'consumed':{cell:row},'admitted_specs':{cell:sha(sp)}};engine=types.SimpleNamespace(registered=lambda:({}, {},q,{}));point={'uuid':uid,'spec_sha256':sha(sp),'intent_sha256':sha(ip),'launch_sha256':sha(out/'NATIVE_LAUNCH.json'),'pid_receipt_sha256':sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'),'model_pid':900000001,'model_start_ticks':123,'launcher_pid':900000002};b={'points':{cell:point}};proof={'cohort':cell,'uuid':uid,'accepted_cycles':None,'correctness_validation_passed':True,'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','strict_overlay_sha256':sha(REALR/'tools/repair_strict_v1.py')};calls=[]
  archive={'receipt':{'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','cohort':cell},'independently_verified_restored_entries':1};outbox=types.SimpleNamespace(verify=lambda c:copy.deepcopy(archive));strict=types.SimpleNamespace(terminal=lambda c:copy.deepcopy(proof));ops=load('independent_frozen_finish_'+label,REALR/'tools/repair_ops_v1.py');ops.R=m.R
  def strict_load(name,file):
   assert file=='repair_strict_v1.py';calls.append('strict');return strict
  ops.load=strict_load
  def fake_archive(c):calls.append('archive');dump(m.R/'control'/(cell+'_ARCHIVE_RECEIPT.json'),archive['receipt']);return copy.deepcopy(archive)
  ops.archive_closed=fake_archive
  return types.SimpleNamespace(m=m,cell=cell,out=out,sp=sp,ip=ip,dp=dp,done=done,row=row,q=q,b=b,point=point,engine=engine,outbox=outbox,strict=strict,ops=ops,proof=proof,calls=calls)
 def reject(label,mutate):
  f=setup(label);mutate(f)
  try:f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)
  except (AssertionError,RuntimeError):ok(label,not f.calls and not (f.m.R/'analysis'/(f.cell+'.RESULT.json')).exists())
  else:raise AssertionError(label+' not rejected')
 f=setup('positive');r=f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops);ok('actual_frozen_finish_delegated_strict_then_archive_then_RESULT',f.calls==['strict','archive'] and r['state']=='EXISTING_FROZEN_FINISH_RESULT_AND_ARCHIVE_VERIFIED');ok('current_executor_adoption_receipt_separate_from_canonical',read(f.m.adoption_path(f.cell))['new_INTENT_or_DONE_or_wait_status_created'] is False)
 rp=f.m.R/'analysis'/(f.cell+'.RESULT.json');rb=rp.read_bytes();f.calls.clear();r=f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops);ok('existing_positive_reverified_no_overwrite_no_rearchive',rp.read_bytes()==rb and not f.calls)
 f=setup('missingDONE');f.dp.unlink();ok('missingDONE_waits_no_finish',f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)['state']=='WAIT_REAL_DONE_AND_EXECUTION_RECEIPT' and not f.calls)
 f=setup('missingWaitReceipt');del f.row['execution_receipt'];ok('missingRegisteredWaitReceipt_waits_no_finish',f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)['state']=='WAIT_REAL_DONE_AND_EXECUTION_RECEIPT' and not f.calls)
 reject('wrongUUID',lambda f:f.row.update(uuid='wrong'))
 reject('wrongIntentSHA',lambda f:f.row.update(intent_sha256='0'*64))
 reject('wrongSpecSHA',lambda f:f.point.update(spec_sha256='0'*64))
 reject('wrongLaunchIdentity',lambda f:f.point.update(launcher_pid=123))
 reject('wrongNativeExit',lambda f:dump(f.out/'NATIVE_EXIT.json',dict(f.done,launcher_wait_returncode=1)))
 def bad_done(f,k,v):
  d=dict(f.done);d[k]=v;dump(f.dp,d);dump(f.out/'NATIVE_EXIT.json',d);f.row['execution_receipt']=d
 reject('rcMinus15_rejected',lambda f:bad_done(f,'launcher_wait_returncode',-15))
 reject('stopReason_rejected',lambda f:bad_done(f,'stop_reason','RESOURCE_HOLD'))
 reject('unobservedSimulator_rejected',lambda f:bad_done(f,'native_simulator_observed',False))
 reject('wrongOutput_rejected',lambda f:bad_done(f,'output','/tmp/foreign'))
 f=setup('liveModel');f.m.model_state=lambda p,s:'RECORDED_GENERATION_ALIVE_OR_ZOMBIE';ok('liveGeneration_orZombie_waits',f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)['state']=='WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT' and not f.calls)
 f=setup('liveLauncher');f.m.launcher_absent=lambda p:False;ok('presentLauncherPID_even_reused_waits',f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)['state']=='WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT' and not f.calls)
 def sentinel(f):
  s=read(f.sp);s['validation_kind']='COMPONENT_SENTINEL_NOT_FORMAL';dump(f.sp,s);f.point['spec_sha256']=f.q['admitted_specs'][f.cell]=sha(f.sp)
 reject('sentinel_excluded_even_with_validSHA',sentinel)
 f=setup('outsideFinite4')
 try:f.m.context('E2-OUTSIDE',f.b,f.engine)
 except AssertionError:ok('outsideFinite4_rejected',True)
 else:raise AssertionError('outsidefinite4')
 reject('archived_without_originalproof_rejected',lambda f:dump(f.m.R/'control'/(f.cell+'_ARCHIVE_RECEIPT.json'),{'CPU_FIXTURE':True}))
 def conflict(f):dump(f.m.R/'analysis'/(f.cell+'.RESULT.json'),{'cohort':f.cell,'uuid':f.row['uuid'],'state':'ENGINEERING_ISSUE'})
 f=setup('existingConflict');conflict(f);path=f.m.R/'analysis'/(f.cell+'.RESULT.json');prior=path.read_bytes()
 try:f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)
 except AssertionError:ok('conflicting_existing_RESULT_preserved',path.read_bytes()==prior and not f.calls)
 else:raise AssertionError('conflictaccepted')
 f=setup('sharedPointLock');lockpath=f.m.R/'analysis/postprocess_v2'/(f.cell+'.METADATA_CONSUMER.lock');lockpath.parent.mkdir(parents=True)
 with lockpath.open('a+b') as fd:
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);ok('sameV2_pointlock_busy_returnsWAIT_no_finish',f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)['state']=='WAIT_SHARED_V2_POINT_LOCK' and not f.calls)
 f=setup('strictReject')
 def strict_raise(c):raise AssertionError('CPU injected wrong full population/runtime/source/trace')
 f.strict.terminal=strict_raise
 try:f.m.execute_point(f.cell,f.b,f.engine,f.outbox,f.strict,f.ops)
 except AssertionError:ok('delegated_strict_reject_preserved_noArchive_noRESULT',f.calls==['strict'] and not (f.m.R/'analysis'/(f.cell+'.RESULT.json')).exists())
 else:raise AssertionError('strictrejectignored')
assert sha(SOURCE)==source_sha
receipt={'schema':'INDEPENDENT_COMPLETION_ADOPTER_SOURCE_AND_PRIVATE_GUARD_CPU_REVIEW_V2','status':'PASS','wrapper_path':str(SOURCE),'wrapper_sha256':source_sha,'check_count':len(checks),'checks':checks,'actual_frozen_finish_path':str(REALR/'tools/repair_ops_v1.py'),'actual_frozen_finish_sha256':sha(REALR/'tools/repair_ops_v1.py'),'fixture_scope':'Actual adopter context/inspect/completed/execute_point and actual frozen finish_evidence; only private temporary files. Strict and outbox delegated to mocks for guard tests. Independent real myocyte strict replay is recorded separately; mocks never claim scientific PASS.','real_model_starts':0,'actual_RESULT_or_archive_or_authority_changes':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};dest=F/'ops/REPAIR_COMPLETION_ADOPTER_INDEPENDENT_GUARD_REVIEW_V2.json'
with dest.open('x') as s:json.dump(receipt,s,sort_keys=True,indent=2);s.write('\n')
print(json.dumps({'status':'PASS','checks':len(checks),'receipt':str(dest),'sha256':sha(dest)},indent=2))
