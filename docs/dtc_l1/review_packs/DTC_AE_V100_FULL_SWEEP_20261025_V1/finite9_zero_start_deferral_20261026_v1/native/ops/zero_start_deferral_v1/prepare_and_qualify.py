import pathlib,json,hashlib,importlib.util,copy,tempfile,datetime,os
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');X=F/'validation_remaining_failure_v1';N=P('/root/data/ep_l2_dtc_l1_native_v2');D=F/'ops/zero_start_deferral_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=load('qualified_finite9_adapter',D/'adapter.py');n=load('finite9_qauthority',T/'tools/sweep_native_cap1m.py');reg,epoch=n.read_current_authority();batch=read(T/'analysis/BATCH_STATE.json');lease=read(T/'control/BATCH_LEASE.json');points={};back=D/'preserved_zero_start_preimages';back.mkdir(exist_ok=True)
for req,root in[('DTC_AE_V100_FULL_SWEEP_20261025_V1',T),('DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1',X)]:
 q=reg['registered_future_requests'][req]
 for c in batch['blocked'][req]:
  rp=root/'analysis'/(c+'.RESULT.json');r=read(rp);item=dict(request=req,root=str(root),RESULT_sha256=sha(rp),spec_sha256=q['admitted_specs'][c],exact_error=r['error']);assert a.is_exact_hold(r);a.unspent(c,item,reg);assert c not in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert not(root/'analysis/zero_start_preimages_R19'/rp.name).exists();dst=back/rp.name
  if dst.exists():assert dst.read_bytes()==rp.read_bytes()
  else:dst.write_bytes(rp.read_bytes())
  points[c]=item
assert len(points)==9 and sum(v['root']==str(X)for v in points.values())==3
plan=dict(schema='FINITE9_EXACT_PAIRED_ADMISSION_ZERO_START_DEFERRAL_V1',parent_path=str(a.CONT),parent_sha256=a.EXPECTED,parent_pid=lease['pid'],parent_start_ticks=lease['start_ticks'],points=points,current_paired_check_path=str(F/'analysis/R19_BLOCKED_ZERO_START_CURRENT_PAIRED_CHECK_20261026_V1.json'),current_paired_check_sha256=sha(F/'analysis/R19_BLOCKED_ZERO_START_CURRENT_PAIRED_CHECK_20261026_V1.json'),scientific_starts_by_operation=0,original_spent_unchanged=True);put(D/'PLAN.json',plan);checks=[]
def check(name,fn):fn();checks.append(dict(name=name,status='PASS'))
with tempfile.TemporaryDirectory(prefix='CPU_',dir=D)as td:
 root=P(td);req='CPU_SCOPE';cell='CPU_COHORT';ip=root/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');rp=root/'analysis'/(cell+'.RESULT.json');backup=root/'backup';backup.mkdir();bad=dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=cell,error=a.SIGNATURE);put(rp,bad);(backup/rp.name).write_bytes(rp.read_bytes());put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}));p=dict(request=req,root=str(root),RESULT_sha256=sha(rp),spec_sha256='CPU_SPEC',exact_error=bad['error']);regs=dict(registered_future_requests={req:dict(admitted_specs={cell:'CPU_SPEC'},consumed={},sealed=[])});auth=lambda:(regs,{});original=lambda fn,c:fn(c);wrapped=a.make_wrapper(original,{cell:p},auth)
 def assert_true(v):assert v
 def rejects(fn):
  try:fn()
  except(RuntimeError,FileNotFoundError):return
  raise AssertionError('expected guard rejection')
 for state in sorted(a.STATES):
  result=dict(bad,state=state);check('exact '+state+' unspent HOLD defers',lambda result=result:assert_true(wrapped(lambda c:result,cell)['state']=='ADMISSION_DEFERRED_ZERO_START'))
 for label,result in[('wrong reason',dict(bad,error=a.SIGNATURE.replace('admission HOLD','different HOLD'))),('wrong type',dict(bad,error=a.SIGNATURE.replace('RuntimeError','AssertionError'))),('retry true',dict(bad,error=a.SIGNATURE.replace('false','true'))),('wrong status',dict(bad,error=a.SIGNATURE.replace('"HOLD"','"PASS"'))),('native failure',dict(state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY',error=a.SIGNATURE)),('success',dict(state='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'))]:check(label+' unchanged',lambda result=result:assert_true(wrapped(lambda c:result,cell)is result))
 check('non-target untouched',lambda:assert_true(wrapped(lambda c:bad,'OTHER')is bad))
 for label,result in[('wrong result cohort',dict(bad,cohort='OTHER')),('embedded unrelated exception',dict(bad,error='other failure embedding '+a.SIGNATURE))]:check(label+' unchanged',lambda result=result:assert_true(wrapped(lambda c:result,cell)is result))
 regs['registered_future_requests'][req]['consumed'][cell]={'uuid':'CPU'};check('spent UUID cannot defer',lambda:assert_true(wrapped(lambda c:bad,cell)is bad));regs['registered_future_requests'][req]['consumed'].clear()
 put(ip,dict(CPU=True));check('INTENT cannot defer',lambda:assert_true(wrapped(lambda c:bad,cell)is bad));ip.unlink();put(dp,dict(CPU=True));check('DONE cannot defer',lambda:assert_true(wrapped(lambda c:bad,cell)is bad));dp.unlink()
 regs['registered_future_requests'][req]['sealed']=[cell];check('sealed cannot defer',lambda:assert_true(wrapped(lambda c:bad,cell)is bad));regs['registered_future_requests'][req]['sealed']=[]
 regs['registered_future_requests'][req]['admitted_specs'][cell]='DRIFT';check('spec drift cannot defer',lambda:assert_true(wrapped(lambda c:bad,cell)is bad));regs['registered_future_requests'][req]['admitted_specs'][cell]='CPU_SPEC'
 def fixture():return dict(safe_call=original),dict(blocked={req:{cell,'KEEP'}},results={req:{cell:copy.deepcopy(bad),'KEEP':dict(state='KEEP')}},running={},cooldown={'KEEP':999})
 localplan=dict(points={cell:p});g,l=fixture();before_reg=copy.deepcopy(regs);before_file=rp.read_bytes();transition=a.state_transition(g,l,localplan,auth,backup);assert l['blocked'][req]=={'KEEP'}and l['results'][req]=={'KEEP':{'state':'KEEP'}}and regs==before_reg and rp.read_bytes()==before_file and l['cooldown']['KEEP']==999 and g['safe_call'](lambda c:bad,cell)['state']=='ADMISSION_DEFERRED_ZERO_START';checks.append(dict(name='real finite metadata transition preserves other rows/authority/files; installs working deferral',status='PASS'))
 for kind in['active_future','missing_block','wrong_RESULT','active_claim','preimage_collision','spent','missing_audit_copy']:
  g,l=fixture();saved=rp.read_bytes();audit=(backup/rp.name).read_bytes()
  if kind=='active_future':l['running']={'f':{'cell':cell}}
  if kind=='missing_block':l['blocked'][req].remove(cell)
  if kind=='wrong_RESULT':put(rp,dict(bad,error='different'))
  if kind=='active_claim':put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={cell:{'CPU':1}}))
  if kind=='preimage_collision':put(root/'analysis/zero_start_preimages_R19'/rp.name,bad)
  if kind=='spent':regs['registered_future_requests'][req]['consumed'][cell]={'uuid':'CPU'}
  if kind=='missing_audit_copy':(backup/rp.name).unlink()
  before=copy.deepcopy(l);rejects(lambda:a.state_transition(g,l,localplan,auth,backup));assert l==before and g['safe_call']is original;checks.append(dict(name=kind+' transition rejected before mutation',status='PASS'));rp.write_bytes(saved);(backup/rp.name).write_bytes(audit);put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}));regs['registered_future_requests'][req]['consumed'].clear();target=root/'analysis/zero_start_preimages_R19'/rp.name
  if target.exists():target.unlink()
 for mode in['before_open','after_partial_write','fsync_failure']:
  g,l=fixture();before=copy.deepcopy(l);ackpath=root/('ACK_'+mode+'.json')
  def failing_writer(path,value,created):
   if mode!='before_open':
    with path.open('x')as f:created[0]=True;f.write('partial')
   raise OSError('CPU injected '+mode)
  try:a.transition_and_ack(g,l,localplan,auth,backup,ackpath,dict(CPU=True),failing_writer)
  except OSError:pass
  else:raise AssertionError('ACK failure missing')
  assert l==before and g['safe_call']is original and not ackpath.exists()and rp.read_bytes()==before_file;checks.append(dict(name=mode+' fully rolls back scheduling and wrapper, cleans own partial ACK',status='PASS'))
 g,l=fixture();ackpath=root/'ACK_success.json';ack=a.transition_and_ack(g,l,localplan,auth,backup,ackpath,dict(CPU=True));assert read(ackpath)==ack and l['blocked'][req]=={'KEEP'};checks.append(dict(name='metadata transition plus fsynced actual CPU ACK succeeds',status='PASS'))
proof=dict(schema='FINITE9_METADATA_DEFERRAL_CPU_QUALIFICATION_V1',status='PASS',adapter_sha256=sha(D/'adapter.py'),plan_sha256=sha(D/'PLAN.json'),driver_sha256=sha(__file__),checks=checks,check_count=len(checks),real_scientific_starts=0,production_authority_or_model_or_active_RESULT_mutations=0,actual_parent_pendingcall_path='Previously qualified GDB mmap/Py_AddPendingCall carrier; production activation requires actual exact-main-frame ACK.',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(D/'CPU_QUALIFICATION.json',proof);print(json.dumps(dict(status='PASS',checks=len(checks),points=len(points),adapter_sha256=proof['adapter_sha256'],plan_sha256=proof['plan_sha256'],qualification_sha256=sha(D/'CPU_QUALIFICATION.json'))))
