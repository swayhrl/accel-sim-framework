"""One finite declared frontend transition; model processes are never attached."""
import pathlib,json,hashlib,subprocess,os,time,datetime,importlib.util,zlib
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def stat(pid):
 try:
  s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return {'pid':pid,'start_ticks':int(s[19]),'ppid':int(s[1]),'state':s[0]}
 except FileNotFoundError:return None
def live(pid,ticks):
 r=stat(pid);return r is not None and r['start_ticks']==ticks and r['state'] not in ['Z','X']
def natural(cell,row):
 p=T/'control/qualification_ledger'/(cell+'.DONE.json')
 if not p.exists():return False
 d=read(p);assert d['uuid']==row['uuid'];assert not live(row['model_pid'],row['model_start_ticks'])
 if d['stop_reason'] is not None or d['launcher_wait_returncode']:
  sp=importlib.util.spec_from_file_location('closed_target_exact_negative_review',T/'tools/sweep_failure_review_runtime_assert_v1.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f);classification=f.classify(cell);assert classification['accepted_cycles'] is None and classification['scientific_acceptance'] is False
 return True
def override_samples(path):
 d=zlib.decompressobj(16+zlib.MAX_WBITS);buf=b''
 with P(path).open('rb') as f:
  for chunk in iter(lambda:f.read(65536),b''):
   buf+=d.decompress(chunk)
   while b'\n' in buf:
    line,buf=buf.split(b'\n',1);r=json.loads(line)
    if 'live_RAM_guard_override' in r:yield r
def verify_sample(r,cell,target,ack,plan_sha,patch_sha):
 x=r['live_RAM_guard_override'];assert x['schema']=='LIVE_RAM_GUARD_OVERRIDE_V1' and x['profile']=='HOST_RUNTIME_ACTUAL_RAM_R12_V1' and x['plan_sha256']==plan_sha and x['patch_source_sha256']==patch_sha and x['cohort']==cell and x['uuid']==target['uuid'] and (x['frontend_pid'],x['frontend_start_ticks'])==(target['frontend_pid'],target['frontend_start_ticks']);s=x['override_resource_sample'];assert s['sample_begin_monotonic_ns']>=ack['patch_monotonic_ns'] and s['sample_end_monotonic_ns']>=s['sample_begin_monotonic_ns'] and s['sample_end_monotonic_ns']<=time.monotonic_ns();assert (s['frontend_pid'],s['frontend_start_ticks'])==(target['frontend_pid'],target['frontend_start_ticks']);v=s['cgroup_memory_stat_for_credit'];clean=max(0,v['file']-v['shmem']-v['file_mapped']-v['file_dirty']-v['file_writeback']);credit=max(0,min(v['inactive_file'],clean)-8*G);eff=None if s['cgroup_memory_max']=='max' else int(s['cgroup_memory_max'])-s['cgroup_memory_current']+credit;assert credit==s['cgroup_reclaimable_clean_inactive_file_credit_bytes'] and eff==s['cgroup_effective_headroom_bytes'];expected=s['host_MemAvailable_bytes']>=64*G and (eff is None or eff>=48*G);assert expected==x['effective_physical_RAM_pass']==r['physical_RAM_pass'] and expected;assert x['scope']=='RUNTIME_ACTUAL_HEADROOM_ONLY';assert r['host_execution_accounting']==target['original_host_profile'];return True
def main():
 assert not (T/'control/LIVE_RAM_OVERRIDE_ACTIVATION_BARRIER_R12B.json').exists(),'Never blindly repeat a completed transition'
 planpath=T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json';plan=read(planpath);plan_sha=sha(planpath);patch=T/'tools/sweep_live_ram_override_v1.py';patch_sha=sha(patch);pub=read(T/'control/CONTINUATION_R12_PUBLICATION_READBACK.json');qa=read(T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json');extension=read(T/'control/CONTINUATION_R12B_PUBLICATION_READBACK.json');extension_qa=read(T/'control/CONTINUATION_R12B_ZERO_MODEL_QUALIFICATION.json');assert extension['verified'] and extension_qa['status']=='PASS' and extension['qualification_sha256']==sha(T/'control/CONTINUATION_R12B_ZERO_MODEL_QUALIFICATION.json') and extension_qa['apply_driver_sha256']==sha(__file__);assert pub['verified'] and qa['status']=='PASS' and qa['live_override_plan_sha256']==plan_sha and qa['patch_source_sha256']==plan['patch_source_sha256']==patch_sha and pub['qualification_sha256']==sha(T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json')
 assert not (T/'control/CONTROLLER_START_R12.json').exists() and not (T/'control/ABORT').exists();old=read(T/'control/CONTROLLER_LAUNCH_R11.json');assert not live(old['pid'],old['start_ticks'])
 sp=importlib.util.spec_from_file_location('R12_live_override_authority',T/'tools/sweep_native_cap1m.py');n=importlib.util.module_from_spec(sp);sp.loader.exec_module(n);profile=dict(plan,plan_sha256=plan_sha,qualification_sha256=sha(T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json'),publication_commit=pub['commit']);q=n.read_current_authority()[0]['registered_future_requests'][REQ]
 if 'live_RAM_guard_override_profile' in q:assert q['live_RAM_guard_override_profile']==profile
 else:
  def register(reg):
   row=reg['registered_future_requests'][REQ];assert 'live_RAM_guard_override_profile' not in row;row['live_RAM_guard_override_profile']=profile;row.setdefault('live_RAM_guard_override_history',[]).append({'plan_sha256':plan_sha,'patch_source_sha256':patch_sha,'publication_commit':pub['commit'],'spent_prefix':len(row['consumed']),'model_retries':0})
  n.update_authority(register);put(T/'control/LIVE_RAM_OVERRIDE_AUTHORITY_REGISTERED_R12.json',{'profile':profile,'models_started':0,'models_signaled':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 receipts=[]
 for cell,target in plan['targets'].items():
  ackpath=T/'control/live_ram_override'/(cell+'.ACK.json')
  if natural(cell,target):receipts.append({'cohort':cell,'state':'ORIGINAL_NATURAL_DONE_BEFORE_TRANSITION'});continue
  if ackpath.exists():
   ack=read(ackpath);assert ack['plan_sha256']==plan_sha and ack['patch_source_sha256']==patch_sha;continue
  assert live(target['frontend_pid'],target['frontend_start_ticks']) and live(target['model_pid'],target['model_start_ticks']);proc=P('/proc')/str(target['frontend_pid']);cmd=(proc/'cmdline').read_bytes();assert b'sweep_frontend_host_v' in cmd and b'run-native' in cmd and cell.encode() in cmd;out=T/'DTC/run/results'/target['uuid'];trace=stat(read(out/'NATIVE_LAUNCH.json')['launcher_pid']);assert trace and trace['ppid']==target['frontend_pid'] and target['frontend_pid']!=target['model_pid'];intent=T/'control/live_ram_override'/(cell+'.DEBUG_DELIVERY_INTENT.json');assert not intent.exists(),'Prior pending call cannot be retried without review'
  errorpath=T/'control/live_ram_override'/(cell+'.ERROR.txt');stub=("try:\n import pathlib,traceback\n ns={'__file__':"+repr(str(patch))+",'__name__':'qualified_live_RAM_override'}\n exec(compile(pathlib.Path("+repr(str(patch))+").read_bytes(),"+repr(str(patch))+",'exec'),ns)\n ns['apply']()\nexcept BaseException:\n pathlib.Path("+repr(str(errorpath))+").write_text(traceback.format_exc())\n").encode()+b'\0';assert len(stub)<4096;stubpath=T/'control/live_ram_override'/(cell+'.stub.bin');stubpath.write_bytes(stub);gdbfile=T/'control/live_ram_override'/(cell+'.gdb');gdbfile.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf=(void*)mmap((void*)0,4096,3,34,-1,0)\nrestore '+str(stubpath)+' binary $buf\nset $queued=(int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n');put(intent,{'cohort':cell,'target':target,'plan_sha256':plan_sha,'patch_source_sha256':patch_sha,'stub_sha256':sha(stubpath),'gdb_commands_sha256':sha(gdbfile),'models_attached':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});began=time.monotonic()
  result=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p',str(target['frontend_pid']),'-x',str(gdbfile)],capture_output=True,text=True,timeout=plan['maximum_debugger_attach_seconds']);duration=time.monotonic()-began;log={'cohort':cell,'returncode':result.returncode,'duration_seconds':duration,'stdout':result.stdout,'stderr':result.stderr,'frontend_pid':target['frontend_pid'],'model_processes_attached':0};put(T/'control/live_ram_override'/(cell+'.DEBUG_DELIVERY_RESULT.json'),log);assert result.returncode==0 and 'QUEUED=0' in result.stdout
  end=time.monotonic()+3
  while not ackpath.exists() and not errorpath.exists() and time.monotonic()<end:time.sleep(.02)
  assert ackpath.exists() and not errorpath.exists(),errorpath.read_text() if errorpath.exists() else 'Pending callback ACK missing;no retry';ack=read(ackpath);assert ack['before_resource_function']==target['expected_resource_function_code_identity'] and ack['plan_sha256']==plan_sha and ack['patch_source_sha256']==patch_sha and ack['model_generation_preserved'];assert live(target['model_pid'],target['model_start_ticks']) or natural(cell,target);print(json.dumps({'state':'FRONTEND_RAM_LOOKUP_TRANSITION_ACKNOWLEDGED','cohort':cell,'debugger_seconds':duration,'same_model_generation_preserved':True}),flush=True)
 pending=set(plan['targets']);rows={};deadline=time.monotonic()+45
 while pending and time.monotonic()<deadline:
  for cell in list(pending):
   target=plan['targets'][cell];ackpath=T/'control/live_ram_override'/(cell+'.ACK.json')
   if natural(cell,target):
    dp=T/'control/qualification_ledger'/(cell+'.DONE.json');d=read(dp);failed=d['stop_reason'] is not None or d['launcher_wait_returncode']!=0;rows[cell]={'state':'ORIGINAL_CLASSIFIED_UNACCEPTED_DONE' if failed else 'ORIGINAL_NATURAL_DONE','cohort':cell,'uuid':target['uuid'],'done_path':str(dp),'done_sha256':sha(dp)}
    if failed:
     cp=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json');rows[cell].update(classification_path=str(cp),classification_sha256=sha(cp))
    pending.remove(cell);continue
   if not ackpath.exists():continue
   ack=read(ackpath);path=T/'DTC/run/results'/target['uuid']/'RESOURCE_SAMPLES.jsonl.gz'
   for sample in override_samples(path):
    verify_sample(sample,cell,target,ack,plan_sha,patch_sha);proofpath=T/'control/live_ram_override'/(cell+'.FIRST_OVERRIDE_SAMPLE.json');put(proofpath,sample);rows[cell]={'state':'OVERRIDE_RESOURCE_SAMPLE_OBSERVED','cohort':cell,'uuid':target['uuid'],'ack_path':str(ackpath),'ack_sha256':sha(ackpath),'sample_proof_path':str(proofpath),'sample_proof_sha256':sha(proofpath),'model_pid':target['model_pid'],'model_start_ticks':target['model_start_ticks']};pending.remove(cell);break
  if pending:time.sleep(.25)
 assert not pending,('No new dispatch until all live first samples observed',sorted(pending));put(T/'control/LIVE_RAM_OVERRIDE_ACTIVATION_BARRIER_R12B.json',{'status':'ALL_LIVE_TARGET_RAM_OVERRIDES_OBSERVED_OR_ORIGINAL_CLOSED_DONE','plan_sha256':plan_sha,'patch_source_sha256':patch_sha,'rows':rows,'closed_target_extension_publication_commit':extension['commit'],'target_count':len(plan['targets']),'original_closed_unaccepted_targets':sum(r['state']=='ORIGINAL_CLASSIFIED_UNACCEPTED_DONE' for r in rows.values()),'actual_live_runtime_overrides_observed':sum(r['state']=='OVERRIDE_RESOURCE_SAMPLE_OBSERVED' for r in rows.values()),'original_natural_done_targets':sum(r['state']=='ORIGINAL_NATURAL_DONE' for r in rows.values()),'model_processes_attached':0,'model_restarts':0,'model_signals':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print(json.dumps({'barrier':'PASS','target_count':len(rows),'live_samples':sum(r['state']=='OVERRIDE_RESOURCE_SAMPLE_OBSERVED' for r in rows.values()),'models_restarted':0}),flush=True)
if __name__=='__main__':main()
