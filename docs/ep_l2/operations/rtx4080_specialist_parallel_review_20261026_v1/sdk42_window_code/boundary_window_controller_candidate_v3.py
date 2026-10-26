#!/usr/bin/env python3
"""One exact SDK42 default50k window then exact original33 resume. Preparation is inert."""
import pathlib,json,hashlib,os,sys,time,fcntl,contextlib,subprocess,shlex,ast,secrets,traceback,signal
D=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
JOBID='C8_SDK42_VECTOR_DEFAULT50000_SPECIALIST_A001'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x,exclusive=True):
 raw=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode();p=pathlib.Path(p)
 if exclusive:
  with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.tmp')
  with tmp.open('wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 assert p.read_bytes()==raw
def frozen_modules():
 phase=D/'PREIMAGE_phase_boundary_controller_candidate_v1.py'
 dispatch=D/'PREIMAGE_dispatch_finite_cpu2_36_candidate.py'
 ns={'__name__':'inert_frozen_phase','__file__':str(phase)}
 exec(compile(phase.read_text(),str(phase),'exec'),ns)
 ds={'__name__':'inert_frozen_dispatch','__file__':str(dispatch)}
 exec(compile(dispatch.read_text(),str(dispatch),'exec'),ds)
 ds['D']=D
 return ns,ds
def grant_gate(a,files):
 assert a.get('approved')is True and a.get('action')=='SDK42_50K_MICROWINDOW_THEN_EXACT33_ONCE'
 assert a.get('GPU_window_max_seconds')==900 and a.get('payload_max_bytes')==1073741824
 for n,key in files.items():assert a.get(key)==sha(D/n),'Root pin mismatch '+n
 for key in ['remote_window_job','remote_window_worker','remote_capture_approval']:
  assert isinstance(a.get(key),str)and a[key].startswith('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/sdk42_default50k_microwindow_20261026_v1/'),'missing exact remote path'
def check_queue(queue,before,closed=False):
 assert [x['id']for x in queue]==[x['id']for x in before['queue_baseline']],'queue identity/order delta'
 assert len({x['id']for x in queue})==len(queue)
 boundary=before['boundary_job']['id'];found=None
 for a,b in zip(queue,before['queue_baseline']):
  if a['id']==boundary:
   assert {k:v for k,v in a.items()if k not in('status','commit','end_unix')}==before['boundary_fixed']
   assert a['status']in('RUNNING','COMMITTED_VERIFIED'),'old boundary failed; no window or ordinary advance'
   if closed:assert a['status']=='COMMITTED_VERIFIED'
   found=a
  else:assert a==b,'original queue row drift '+a['id']
 assert found is not None
 pending=[x['id']for x in queue if x['id']in before['resume_ids']and x['status']=='PENDING']
 assert pending==before['resume_ids'] and len(pending)==33
 return found
def stop_create_or_check(path,own,phase):
 if pathlib.Path(path).exists():phase['stop_matches'](path,own);return
 with pathlib.Path(path).open('xb')as f:f.write(own);f.flush();os.fsync(f.fileno())
 phase['stop_matches'](path,own)
def resume_allowed(old_natural_stop,old_commit,cleanup,own_stop_exact):
 return bool(old_natural_stop and old_commit and cleanup.get('status')=='OWN_WINDOW_PROCESSES_ABSENT_AND_REMOTE_LEASES_IDLE'and own_stop_exact)
def independent_identity_gate(baseline,observed):
 for key in ['gpu_compute','exact_sdk_argv']:
  assert key in baseline and key in observed,'missing independent process baseline'
  assert {tuple(x)for x in observed[key]}<={tuple(x)for x in baseline[key]},'new '+key+' process identity after window'
 return True
def remote_check(a,before,cleanup=False,baseline=None):
 # Never signals anything. Independent process identities and original remote leases.
 expected={a['remote_window_worker']:a['window_worker_sha256'],a['remote_window_job']:a['window_job_sha256'],a['remote_capture_approval']:a['capture_approval_sha256']}
 frozen=load(D/'FROZEN_PENDING_33.json')
 for j in frozen['jobs']:expected[j['job_path']]=j['job_sha256'];expected[j['worker_script']]=j['worker_sha256']
 code="import pathlib,json,hashlib,fcntl,os,subprocess;expected="+repr(expected)+";hs=[];seen=[]\n"
 code+="try:\n"
 code+=" for n in ['/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','/data/c16/locks/c16_gpu_campaign.lock']:\n  f=open(n,'r+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(f)\n"
 code+=" for p,h in expected.items():assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h,p\n"
 code+=" observed={'gpu_compute':[],'exact_sdk_argv':[]}\n"
 code+=" def ticks(pid):return pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]\n"
 code+=" gpu_lines=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).splitlines()\n"
 code+=" for line in gpu_lines:\n  if line.strip():\n   pid=int(line.strip());observed['gpu_compute'].append([pid,ticks(pid)])\n"
 code+=" for p in pathlib.Path('/proc').iterdir():\n  if not p.name.isdigit():continue\n  try:cmd=[x for x in (p/'cmdline').read_bytes().split(b'\\0')if x]\n  except (FileNotFoundError,ProcessLookupError,PermissionError):continue\n  if cmd==[b'/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v3_vectorAdd']:\n   observed['exact_sdk_argv'].append([int(p.name),ticks(int(p.name))])\n"
 if cleanup:
  assert baseline is not None and set(baseline)=={'gpu_compute','exact_sdk_argv'},'independent prewindow baseline missing'
  code+=' baseline='+repr(baseline)+'\n'
  code+=" for key in ['gpu_compute','exact_sdk_argv']:\n  assert {tuple(x)for x in observed[key]}<={tuple(x)for x in baseline[key]},'new compute or bare SDK identity after window'\n"
  code+=" root=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/inflight/"+JOBID+"'); markers=[root/'PROCESS_START.json',root/'EXECUTION.json',root/'observer/PROCESS_START.json',root/'observer/EXECUTION.json']\n"
  code+=" for marker0 in markers:\n  marker=marker0 if marker0.exists()else pathlib.Path(str(marker0).replace('/nas_rtx4080/inflight/','/nas_rtx4080/objects/'))\n  if not marker.exists():continue\n  r=json.loads(marker.read_text())\n  for pkey,tkey in [('worker_pid','worker_start_ticks'),('capture_pid','capture_start_ticks')]:\n   if pkey not in r:continue\n   p=pathlib.Path('/proc',str(r[pkey]),'stat')\n   if p.exists():assert p.read_text().split(') ',1)[1].split()[19]!=str(r[tkey]),'window process still alive'\n"
  code+=" ancestors={os.getpid()};ap=os.getppid()\n while ap>1 and ap not in ancestors:\n  ancestors.add(ap)\n  try:ap=int(pathlib.Path('/proc',str(ap),'stat').read_text().split(') ',1)[1].split()[1])\n  except (FileNotFoundError,ProcessLookupError):break\n"
  code+=" for p in pathlib.Path('/proc').iterdir():\n  if not p.name.isdigit()or int(p.name)in ancestors:continue\n  try:cmd=(p/'cmdline').read_bytes().split(b'\\0')\n  except (FileNotFoundError,ProcessLookupError,PermissionError):continue\n  assert not any((b'"+JOBID+"'in x or x=="+repr(a['remote_window_worker'].encode())+")for x in cmd),'window command still alive'\n"
  # The inline checker embeds the literals itself in its -c argument, skip only its own PID above.
  code+=" print(json.dumps({'status':'OWN_WINDOW_PROCESSES_ABSENT_AND_REMOTE_LEASES_IDLE','observed':observed,'baseline':baseline}))\n"
 else:code+=" print(json.dumps({'status':'FILES_PINNED_AND_REMOTE_LEASES_IDLE','baseline':observed}))\n"
 code+="finally:\n for f in reversed(hs):fcntl.flock(f,fcntl.LOCK_UN);f.close()\n"
 r=subprocess.run(['ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=12','gpu109','python3 -B -c '+shlex.quote(code)],capture_output=True,text=True,timeout=45)
 assert r.returncode==0,('remote idle/cleanup not proven',r.stderr[-1600:])
 return json.loads(r.stdout)
def one_shot_intent(path,value):
 save(path,value,True)
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true',required=True);p.add_argument('--approval',required=True);p.add_argument('--approval-sha',required=True);args=p.parse_args()
 assert pathlib.Path(args.approval).resolve()==(D/'ROOT_WINDOW_APPROVAL_V1.json').resolve(),'fixed Root window grant path required for resume binding'
 assert sha(args.approval)==args.approval_sha
 a=load(args.approval)
 files={'boundary_window_controller_candidate_v3.py':'controller_sha256','capture_sdk42_default50k_nas_candidate_v2.py':'window_worker_sha256',JOBID+'.json':'window_job_sha256','dispatch_finite_resume33_candidate_v2.py':'resume_dispatcher_sha256','FROZEN_PENDING_33.json':'resume_snapshot_sha256','BOUNDARY_BEFORE_V1.json':'boundary_snapshot_sha256','OWN_STOP_AFTER_CURRENT.json':'own_stop_sha256','remote_watchdog_candidate.py':'watchdog_sha256','PREIMAGE_phase_boundary_controller_candidate_v1.py':'phase_preimage_sha256','PREIMAGE_dispatch_finite_cpu2_36_candidate.py':'dispatch_preimage_sha256'}
 grant_gate(a,files)
 assert sha(D/'ROOT_CAPTURE_APPROVAL_V1.json')==a['capture_approval_sha256']
 phase,dispatch=frozen_modules()
 before=load(D/'BOUNDARY_BEFORE_V1.json');old=before['old_dispatcher'];oldrun=pathlib.Path(before['old_run'])
 assert phase['same_alive'](old),'old dispatcher already changed; refresh exact boundary before STOP'
 queue=load(C/'QUEUE.json');check_queue(queue,before)
 run=D/'window_run';run.mkdir(exist_ok=False)
 own=(D/'OWN_STOP_AFTER_CURRENT.json').read_bytes();stop=C/'STOP_AFTER_CURRENT'
 stop_create_or_check(stop,own,phase)
 def state(status,**kw):save(run/'STATE.json',{'status':status,'unix':time.time(),**kw},False)
 deadline=time.time()+24*3600;state('WAIT_ORIGINAL_WHOLE_JOB_COMMIT_AND_NATURAL_STOP')
 try:
  while time.time()<deadline:
   phase['stop_matches'](stop,own)
   boundary=check_queue(load(C/'QUEUE.json'),before)
   if phase['same_alive'](old)or boundary['status']!='COMMITTED_VERIFIED':time.sleep(10);continue
   terminal=load(oldrun/'STATE.json')
   assert terminal.get('pid')==old['pid']and terminal.get('start_ticks')==old['start_ticks']and terminal['status']=='STOP_AFTER_CURRENT'
   phase['publication_closed'](boundary)
   try:
    with phase['leases']():
     phase['stop_matches'](stop,own);assert not phase['same_alive'](old)
     boundary=check_queue(load(C/'QUEUE.json'),before,True);closed=phase['publication_closed'](boundary)
     grant_gate(a,files);assert sha(D/'ROOT_CAPTURE_APPROVAL_V1.json')==a['capture_approval_sha256']
     preflight=remote_check(a,before,False);save(run/'WINDOW_PROCESS_BASELINE.json',preflight)
     one_shot_intent(run/'WINDOW_INTENT.json',{'job_id':JOBID,'Root_approval_sha256':args.approval_sha})
     window_end=time.time()+900
     def window_timeout(sig,frame):raise TimeoutError('window wall bound reached; independent cleanup still required')
     signal.signal(signal.SIGALRM,window_timeout);signal.setitimer(signal.ITIMER_REAL,840)
     result_status='FAILED_RETAINED';error=None;commit=None
     state('WINDOW_RUNNING_ORIGINAL33_UNCHANGED')
     try:
      job={'id':JOBID,'worker_script':a['remote_window_worker'],'worker_sha256':a['window_worker_sha256'],'job_path':a['remote_window_job']}
      with(run/'window.stderr.log').open('x')as err:
       rc,out=dispatch['run_remote'](job,{'job_sha256':a['window_job_sha256']},window_end,err)
      (run/'window.stdout.log').write_text(out)
      assert rc==0,'window worker/guard nonzero '+str(rc)
      sender=json.loads(out);assert sender.get('status')=='SENDER_COMPLETE'
      commit=dispatch['publish'](sender)
      check={'id':JOBID,'commit':commit}
      phase['publication_closed'](check)
      result_status='COMMITTED_VERIFIED'
     except Exception as e:error=repr(e)
     # A transport error never itself proves cleanup; failure may resume ordinary only after this separate check.
     cleanup=remote_check(a,before,True,preflight['baseline'])
     signal.setitimer(signal.ITIMER_REAL,0)
     assert time.time()<window_end,'whole window closure deadline exceeded; retained, Root reconcile'
     phase['stop_matches'](stop,own);check_queue(load(C/'QUEUE.json'),before,True)
     assert resume_allowed(True,True,cleanup,True)
     save(run/'WINDOW_TERMINAL.json',{'status':result_status,'error':error,'commit':commit,'independent_cleanup':cleanup,'original_boundary':closed,'original33_unchanged':True})
     one_shot_intent(run/'RESUME_INTENT.json',{'scope_sha256':a['resume_snapshot_sha256'],'selected_count':33,'window_status':result_status})
     phase['retire_stop'](stop,D/'OWN_STOP_RETIRED_AFTER_WINDOW.json',own)
     token=secrets.token_hex(24);env=os.environ.copy();env['RTX_CPU2_GATE_TOKEN']=token;env['PYTHONDONTWRITEBYTECODE']='1'
     with(run/'resume.stdout.log').open('xb')as out,(run/'resume.stderr.log').open('xb')as err:
      child=subprocess.Popen(['/usr/bin/python3','-B',str(D/'dispatch_finite_resume33_candidate_v2.py'),'--frozen33'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True)
     ci=phase['identity'](child.pid);assert ci and ci['state']!='Z'
    # Child waits for this gate before acquiring original dispatcher leases.
    save(D/'BATCH_LAUNCH_GATE.json',{'token':token,'pid':ci['pid'],'start_ticks':ci['start_ticks']})
    until=time.monotonic()+60
    while time.monotonic()<until:
     if(D/'NEW_BATCH_STARTED.json').exists():
      ack=load(D/'NEW_BATCH_STARTED.json');assert ack['pid']==ci['pid']and ack['start_ticks']==ci['start_ticks']and ack['launch_token']==token
      state('WINDOW_TERMINAL_EXACT33_RESUMED_ONCE',window_status=result_status,resume={'pid':ci['pid'],'start_ticks':ci['start_ticks']});return
     assert phase['same_alive'](ci),'resume exited before ACK; no automatic relaunch'
     time.sleep(.2)
    raise TimeoutError('resume ACK missing; no automatic relaunch')
   except BlockingIOError:state('WAIT_ORIGINAL_LEASES');time.sleep(10);continue
  raise TimeoutError('24h original boundary wait deadline')
 except BaseException as e:state('FAILED_RETAINED_NO_AUTORETRY',error=repr(e),traceback=traceback.format_exc());raise
if __name__=='__main__':main()
