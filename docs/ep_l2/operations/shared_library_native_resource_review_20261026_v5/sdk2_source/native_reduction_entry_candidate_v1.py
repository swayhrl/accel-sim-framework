#!/usr/bin/env python3
"""Root-only exact SDK42 reduction Native backend. Inert until pinned --execute.
No preparation code grants authority. All execution paths, tools and scope are fixed.
"""
import pathlib,json,hashlib,os,time,subprocess,shlex,threading,fcntl,contextlib,ast,secrets,signal,shutil,traceback,sys
from native_boundary_state_machine_candidate_v1 import DEADLINE,SCOPE,remaining33,exclusive_owned_stop,retire_owned_stop
D=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
OLD=B/'private_candidates/sdk42_default50k_microwindow_20261026_v1'
EXEC=B/'private_candidates/sdk42_reduction_native_boundary_prepare_20261026_v2/execution'
REMOTE='/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/sdk42_reduction_native_boundary_prepare_20261026_v2/execution'
JOB='C8_SDK42_REDUCTION_DEFAULT65536_SPECIALIST_A001'
WORKER='capture_sdk42_reduction_c8_candidate_v1.py'
def load(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,obj):
 p=pathlib.Path(p);raw=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
 with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==raw
def identity(pid):
 try:
  t=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return {'pid':int(pid),'start_ticks':t[19],'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':t[0]}
 except (FileNotFoundError,ProcessLookupError):return None
def alive(x):
 y=identity(x['pid'])
 return bool(y and all(y[k]==x[k] for k in ('pid','start_ticks')) and y['state']!='Z')
def need(ok,why):
 if not ok:raise RuntimeError(why)
def approved(path,pin):
 p=pathlib.Path(path);need(p.resolve()==(D/'ROOT_NATIVE_ENTRY_APPROVAL_V1.json').resolve(),'fixed approval path')
 need(sha(p)==pin,'Root approval pin')
 a=load(p);need(a.get('fixture_only') is not True,'fixture approval forbidden in production')
 need(a.get('approved') is True and a.get('action')==SCOPE,'Root scope approval')
 need(a.get('original_deadline_unix')==DEADLINE,'deadline extension')
 need(a.get('allow_fresh_live_preflight') is True,'fresh runtime preflight not approved')
 need(a['code_manifest_sha256']==sha(D/'CODE_MANIFEST_V1.json'),'code manifest')
 for x in load(D/'CODE_MANIFEST_V1.json')['files']:
  q=D/x['path'];need(q.resolve().is_relative_to(D) and not q.is_symlink() and sha(q)==x['sha256'],'code drift '+x['path'])
 need(a['controller_sha256']==sha(__file__) and a['resume_dispatcher_sha256']==sha(D/'dispatch_remaining_original33_candidate_v1.py') and a['watchdog_sha256']==sha(D/'remote_watchdog_reduction_candidate_v1.py'),'controller/resume/watchdog explicit pins')
 need(a['oracle_sha256']==sha(EXEC/'sdk42_reduction_oracle_v1.py'),'oracle pin')
 need(a['job_sha256']==sha(EXEC/(JOB+'.json')) and a['worker_sha256']==sha(EXEC/WORKER) and a['package_manifest_sha256']==sha(EXEC/'PACKAGE_MANIFEST.json'),'execution package drift')
 need(sha(D/'preimages/FROZEN_PENDING_33.json')=='2da82e2dbad0247e81242a96d83a2d1c43252e3f60cb572ab2fd749fbd4f0ef2','original33 snapshot')
 return a
@contextlib.contextmanager
def leases(names):
 hs={}
 try:
  for name in names:
   f=(C/name).open('r+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BaseException:f.close();raise
   hs[name]=f
  yield hs
 finally:
  for f in reversed(list(hs.values())):
   if not f.closed:fcntl.flock(f,fcntl.LOCK_UN);f.close()
def publication_closed(row):
 commit=row['commit'];asset=row['id'];obj=B/'objects'/asset
 need(commit['status']=='COMMITTED_VERIFIED' and commit['asset_id']==asset and commit['object_path']==str(obj),'commit identity')
 need(load(B/'receipts'/(asset+'_RECEIVER_READBACK.json'))==commit,'receiver readback')
 need(sha(obj/'MANIFEST.json')==commit['manifest_sha256'],'manifest')
 need(all(load(obj/'COMMIT.json').get(k)==v for k,v in commit.items() if k!='object_path'),'on disk commit')
 need([x for x in load(B/'catalog/ASSETS.json')['objects'] if x['asset_id']==asset]==[commit],'unique catalog membership')
 return commit
def pinned_archive():
 # Only these original functions are imported; never the old hardcoded main/controller.
 src=(D/'preimages/dispatch_finite_resume33_candidate_v2.py').read_text();tree=ast.parse(src)
 names={'save','sha','publish','update_job','scope_jobs','run_remote'}
 defs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
 ns=dict(pathlib=pathlib,json=json,time=time,hashlib=hashlib,fcntl=fcntl,os=os,subprocess=subprocess,threading=threading,shlex=shlex,traceback=traceback,shutil=shutil,D=D,C=C,B=B,IDENTITY_KEYS=('id','type','worker_script','worker_sha256','job_path'))
 exec(compile(ast.Module(body=defs,type_ignores=[]),'pinned_archive_functions','exec'),ns)
 return ns
def queue33(frozen):
 q=load(C/'QUEUE.json');ids=[x['id'] for x in q];need(len(ids)==len(set(ids)),'duplicate queue')
 by={x['id']:x for x in q};out=[]
 for old in frozen:
  x=by[old['id']]
  need(all(x.get(k)==old.get(k) for k in ('id','type','worker_script','worker_sha256','job_path')),'original33 identity drift')
  out.append(x)
 return out
def run_probe(code):
 r=subprocess.run(['ssh','-n','-o','BatchMode=yes','-o','ConnectTimeout=12','gpu109','python3 -B -c '+shlex.quote(code)],capture_output=True,text=True,timeout=45)
 need(r.returncode==0,'independent109 probe failed '+r.stderr[-1800:]);return json.loads(r.stdout)
def probe_source(expected,post=False,baseline=None,cleanup_ids=None,elf=None):
 # Fixed CPU/driver-query probe, only called after Root execute and prior scope closure.
 return """import pathlib,json,os,fcntl,hashlib,subprocess
os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
expected=EXEXPECTED
post=EXPOST
baseline=EXBASE
cleanup_ids=EXIDS
elf=EXELF
hs=[]
def ident(pid):
 try:
  x=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return [int(pid),x[19]]
 except (FileNotFoundError,ProcessLookupError):return None
try:
 for n in ['/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','/data/c16/locks/c16_gpu_campaign.lock']:
  f=open(n,'r+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(f)
 for x in expected:
  p=pathlib.Path(x['path']);assert str(p.resolve())==x['canonical_path']
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  assert h.hexdigest()==x['sha256'],x['path']
 if elf:
  assert os.environ.get('LD_LIBRARY_PATH','')==elf['LD_LIBRARY_PATH']
  output=subprocess.check_output(['/usr/bin/readelf','-h','-d','/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v4_reduction'],timeout=10,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
  assert hashlib.sha256(output).hexdigest()==elf['stdout_sha256'],'fresh ELF metadata drift'
 boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 lines=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True,timeout=10).splitlines()
 gpu=[]
 for line in lines:
  if not line.strip():continue
  i=ident(int(line));assert i
  cmd=pathlib.Path('/proc',str(i[0]),'cmdline').read_bytes()
  assert b'ComfyUI/main.py' in cmd,'foreign GPU work active'
  gpu.append(i)
 target=[];scope=[]
 ancestors={os.getpid()};p=os.getppid()
 while p>1 and p not in ancestors:
  ancestors.add(p)
  try:p=int(pathlib.Path('/proc',str(p),'stat').read_text().split(') ',1)[1].split()[1])
  except (FileNotFoundError,ProcessLookupError):break
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name) in ancestors:continue
  try:argv=[x for x in (p/'cmdline').read_bytes().split(b'\\0') if x]
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if argv==[b'/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v4_reduction']:target.append(ident(int(p.name)))
  if any(b'sdk42_reduction_native_boundary_prepare_20261026_v2' in x or b'C8_SDK42_REDUCTION_DEFAULT65536_SPECIALIST_A001' in x for x in argv):scope.append(ident(int(p.name)))
 assert not target and not scope,'reduction/guard scope process remains'
 if post:
  assert boot==baseline['boot_id'] and set(map(tuple,gpu))<=set(map(tuple,baseline['gpu_compute']))
  for x in cleanup_ids:
   assert ident(x['pid'])!=[x['pid'],str(x['start_ticks'])],'owned descendant still alive'
 print(json.dumps({'status':'POST_INDEPENDENT_CLEAN' if post else 'PRE_INDEPENDENT_IDLE','boot_id':boot,'gpu_compute':gpu,'exact_target':target,'scope_processes':scope,'unix':__import__('time').time()}))
finally:
 for f in reversed(hs):fcntl.flock(f,fcntl.LOCK_UN);f.close()
""".replace('EXEXPECTED',repr(expected)).replace('EXPOST',repr(post)).replace('EXBASE',repr(baseline)).replace('EXIDS',repr(cleanup_ids or [])).replace('EXELF',repr(elf))
class Production:
 def __init__(self,a,pin):
  self.a=a;self.pin=pin;self.frozen=load(D/'preimages/FROZEN_PENDING_33.json')['jobs']
  self.run=D/'entry_run';self.run.mkdir(exist_ok=False);self.own=None;self.base=None;self.hs=None
  self.archive=pinned_archive()
 def record(self,stage,**data):save(self.run/(str(time.time_ns())+'_'+stage+'.json'),dict(stage=stage,unix=time.time(),**data))
 def wait(self):
  need(time.time()<DEADLINE-120,'original deadline exhausted');time.sleep(2)
 def prior(self):
  while True:
   if not (OLD/'window_run/WINDOW_TERMINAL.json').exists() or not (OLD/'NEW_BATCH_STARTED.json').exists():self.wait();continue
   terminal=load(OLD/'window_run/WINDOW_TERMINAL.json');st=load(OLD/'window_run/STATE.json');ack=load(OLD/'NEW_BATCH_STARTED.json')
   if st['status']!='WINDOW_TERMINAL_EXACT33_RESUMED_ONCE':self.wait();continue
   need(terminal['independent_cleanup']['status']=='OWN_WINDOW_PROCESSES_ABSENT_AND_REMOTE_LEASES_IDLE','SDK cleanup unknown')
   need(ack['selected_ids']==[x['id'] for x in self.frozen] and ack['deadline_unix']==DEADLINE,'old33 ACK scope/deadline')
   need(all(st['resume'][k]==ack[k] for k in ('pid','start_ticks')),'SDK final/ACK mismatch')
   oldid=load(OLD/'ROOT_ARMED_LAUNCH_V1.json')['controller']
   if alive(oldid):self.wait();continue
   need(alive(ack),'old33 dispatcher no longer live; fresh Root boundary required')
   need(load(pathlib.Path(ack['run_directory'])/'IDENTITY.json')['deadline_unix']==DEADLINE,'old33 identity deadline')
   self.oldack=ack;self.record('PRIOR_CLOSED',terminal=terminal,ack=ack,old_controller=oldid);return
 def stop_and_boundary(self):
  stop=C/'STOP_AFTER_CURRENT'
  while stop.exists():
   if not getattr(self,'foreign_stop_wait_recorded',False):self.record('WAIT_FOREIGN_STOP');self.foreign_stop_wait_recorded=True
   self.wait()
  self.stop_payload={'schema':'REDUCTION_SCOPE_OWN_STOP_V1','owner':SCOPE,'Root_approval_sha256':self.pin,'nonce':secrets.token_hex(24),'original33_pid':self.oldack['pid'],'original33_start_ticks':self.oldack['start_ticks'],'deadline_unix':DEADLINE}
  with leases(['RTX4080_QUEUE.lock']):
   self.own=exclusive_owned_stop(stop,self.stop_payload);self.before=queue33(self.frozen)
   self.record('OWN_STOP_CREATED',identity=self.own,before=self.before)
  while alive(self.oldack):self.check_stop();self.wait()
  state=load(pathlib.Path(self.oldack['run_directory'])/'STATE.json')
  need(state['status']=='STOP_AFTER_CURRENT' and all(state[k]==self.oldack[k] for k in ('pid','start_ticks')),'old33 not natural STOP')
  self.check_stop();after=queue33(self.frozen);changes=[]
  for old,new in zip(self.before,after):
   if old==new:continue
   need(old['status'] in ('RUNNING','PENDING') and new['status']=='COMMITTED_VERIFIED','old33 failed/drifted during boundary')
   publication_closed(new);changes.append(new['id'])
  need(len(changes)<=1 and all(x['status']!='RUNNING' for x in after),'unclosed/extra boundary jobs')
  self.record('ORIGINAL33_NATURAL_BOUNDARY_CLOSED',changes=changes,state=state)
 def check_stop(self):
  p=C/'STOP_AFTER_CURRENT';st=p.lstat()
  need(not p.is_symlink() and (st.st_ino,st.st_dev)==(self.own['inode'],self.own['dev']) and p.read_bytes().hex()==self.own['raw'],'STOP no longer exact own')
 def fresh(self):
  self.check_stop();need(not alive(self.oldack),'old33 returned')
  self.activation_request={'schema':'REDUCTION_ENTRY_FRESH_RUNTIME_REQUEST_V1','scope':SCOPE,'job_id':JOB,'entry':{k:identity(os.getpid())[k] for k in ('pid','start_ticks','boot_id')},'entry_approval_sha256':self.pin,'own_stop_identity':self.own,'runtime_baseline_sha256':self.a['runtime_baseline_sha256'],'challenge':secrets.token_hex(32),'absolute_deadline_unix':min(time.time()+3600,DEADLINE-120)}
  save(self.run/'RUNTIME_ADMISSION_REQUEST.json',self.activation_request)
  p=D/'ROOT_ACTIVATION_RUNTIME_ADMISSION_V1.json'
  until=time.monotonic()+180
  while not p.exists():
   need(time.monotonic()<until,'fresh Root activation receipt absent; own STOP retained');self.wait()
  runtime=load(p)
  issuer_cfg=load(D/'ROOT_ISSUER_APPROVAL_V1.json')
  need(issuer_cfg.get('approved') is True and issuer_cfg.get('action')=='ISSUE_ONE_REDUCTION_ENTRY_FRESH_READONLY_RUNTIME_ADMISSION_V1','independent issuer authority absent')
  need(issuer_cfg['entry_approval_sha256']==self.pin and issuer_cfg['issuer_source_sha256']==self.a['issuer_source_sha256'] and issuer_cfg['runtime_baseline_sha256']==self.a['runtime_baseline_sha256'] and issuer_cfg['issuer_authority_id']==self.a['issuer_authority_id'],'issuer delegation mismatch')
  need(runtime['issuer_source_sha256']==sha(D/'runtime_admission_issuer_candidate_v1.py')==self.a['issuer_source_sha256'] and runtime['issuer_approval_sha256']==sha(D/'ROOT_ISSUER_APPROVAL_V1.json'),'issuer source/approval changed')
  need(runtime['request_sha256']==sha(self.run/'RUNTIME_ADMISSION_REQUEST.json') and runtime['challenge']==self.activation_request['challenge'] and runtime['entry_identity']==self.activation_request['entry'],'runtime request/entry identity binding')
  need(runtime['runtime_baseline_sha256']==sha(D/'ROOT_EXPECTED_RUNTIME_BASELINE_V1.json')==self.a['runtime_baseline_sha256'],'immutable runtime baseline changed')
  need(time.time()<runtime['expires_unix']<=runtime['unix']+30,'runtime TTL')
  need(runtime.get('loaded_gpu_modules_inspected') is False,'disk proof must not claim loaded GPU modules')
  need(runtime.get('native_entry_Root_approval_sha256')==self.pin and runtime.get('activation_nonce')==self.a['activation_nonce'],'Root activation receipt binding')
  self.record('ROOT_ACTIVATION_RUNTIME_RECEIPT_REOPEN',path=str(p),sha256=sha(p))
  need(runtime.get('fixture_only') is not True,'fixture proof forbidden in production')
  need(runtime.get('approved') is True and runtime.get('scope')==SCOPE and runtime.get('status')=='ROOT_FRESH_EXACT_BINARY_ELF_LIBRARY_RUNTIME_ADMITTED','Root runtime admission missing')
  need(0<=time.time()-runtime['unix']<=30,'runtime admission stale')
  need(runtime['worker_sha256']==self.a['worker_sha256'] and runtime['binary_sha256']=='cdcf7c2abc6cd73afadb2d4e6bce2eb0b06e22d4728b6e6b0df7c04be73cadcf','runtime code identity')
  need(runtime.get('full_foreign_reservations_accounted') is True and runtime.get('resource_admitted') is True,'all-project reservation decision absent')
  foreign=[]
  for f in runtime['foreign_registry_refs']:
   need(sha(f['path'])==f['sha256'],'foreign reservation snapshot stale');foreign.append(f)
  need(foreign,'empty foreign reservation report')
  need(shutil.disk_usage(C).free>=5*1024**3 and shutil.disk_usage(B).free>=5*1024**3,'physical5GiB floor')
  expected=runtime['remote_code_ELF_library_file_refs'];need(len(expected)>=8,'fresh source/ELF/library path set incomplete')
  required={REMOTE+'/'+WORKER:self.a['worker_sha256'],REMOTE+'/'+JOB+'.json':self.a['job_sha256'],
   '/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v4_reduction':'cdcf7c2abc6cd73afadb2d4e6bce2eb0b06e22d4728b6e6b0df7c04be73cadcf',
   '/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2/producer.so':'c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'}
  for x in load(EXEC/(JOB+'.json'))['task']['source_files']:required[x['path']]=x['sha256']
  need(runtime.get('ELF_NEEDED_and_load_paths_closed') is True and runtime.get('library_resolutions'),'fresh loader/library mapping absent')
  for x in runtime['library_resolutions']:required[x['path']]=x['sha256']
  required['/usr/bin/readelf']=runtime['readelf_tool_sha256']
  got={x['path']:x['sha256'] for x in expected};need(all(got.get(p)==h for p,h in required.items()),'remote worker/job missing')
  self.expected=expected;self.base=run_probe(probe_source(expected,elf=runtime['fresh_readelf']))
  need(0<=time.time()-runtime['unix']<=30,'runtime proof expired during fresh code/lease probe')
  self.record('FRESH_ADMISSION',runtime=runtime,baseline=self.base,foreign=foreign)
  save(self.run/'RUNTIME_ADMISSION_CONSUMED_ACK.json',{'request_sha256':sha(self.run/'RUNTIME_ADMISSION_REQUEST.json'),'runtime_sha256':sha(p),'entry':self.activation_request['entry'],'challenge':self.activation_request['challenge']})
  self.selected=remaining33(load(C/'QUEUE.json'),self.frozen)
 def activate(self):
  self.end=min(time.time()+3600,DEADLINE-120,getattr(self,'activation_request',{}).get('absolute_deadline_unix',DEADLINE));need(self.end-time.time()>180,'insufficient finite window')
  self.record('WINDOW_INTENT',selected_ids=self.selected,window_end=self.end);self.effect_started=True
  grant={'approved':True,'action':'SDK42_REDUCTION_DEFAULT65536_C8_OBSERVER_AND_CAPTURE_ONCE','not_before_unix':time.time(),'expires_unix':self.end,'worker_sha256':self.a['worker_sha256'],'job_sha256':self.a['job_sha256'],'oracle_sha256':self.a['oracle_sha256'],'GPU_window_max_seconds':3600,'payload_max_bytes':1073741824,'package_manifest_sha256':self.a['package_manifest_sha256'],'native_entry_Root_approval_sha256':self.pin}
  save(EXEC/'ROOT_CAPTURE_APPROVAL_V1.json',grant);self.record('GRANT_ACTIVATED_ONLY_AT_BOUNDARY',grant=grant)
 def run_window(self):
  code=(D/'remote_watchdog_reduction_candidate_v1.py').read_text()
  args=[REMOTE+'/'+WORKER,self.a['worker_sha256'],REMOTE+'/'+JOB+'.json',self.a['job_sha256'],str(self.end),str(min(3540,self.end-time.time()-30))]
  command='exec python3 -B -c '+shlex.quote(code)+' '+' '.join(map(shlex.quote,args))
  from heartbeat_transport_v1 import run
  argv=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=12','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=3','gpu109',command]
  with (self.run/'window.stderr.log').open('x') as err:
   rc,text,transport=run(argv,self.end,err,lambda:shutil.disk_usage(C).free>=5*1024**3 and shutil.disk_usage(B).free>=5*1024**3)
  (self.run/'window.stdout.log').write_text(text)
  self.rc=rc;self.transport=transport
  try:self.sender=json.loads(text)
  except ValueError:self.sender={}
  self.guard_closed=transport is None and ((self.rc==0 and self.sender.get('status') in ('SENDER_COMPLETE','FAILED_RETAINED','PENDING_SPECIALIST_EXTENSION')) or (self.rc in (74,75) and self.sender.get('owned_cleanup') is not None))
  if any(x in str(self.sender.get('error','')) for x in ('identity unknown','outside owned','metadata unavailable','monitor stalled')):self.guard_closed=False
  self.record('WINDOW_RETURN',returncode=self.rc,transport=transport,guard_closed=self.guard_closed,sender=self.sender)
 def cleanup(self):
  ids=list(self.sender.get('owned_cleanup',[]))
  # Independently re-open actual capture/observer markers and check all recorded identities.
  root=B/'inflight'/JOB
  for rel in ['PROCESS_START.json','EXECUTION.json','observer/PROCESS_START.json','observer/EXECUTION.json']:
   p=root/rel
   if not p.exists():continue
   x=load(p)
   for a,b in [('worker_pid','worker_start_ticks'),('capture_pid','capture_start_ticks')]:
    if a in x:ids.append({'pid':x[a],'start_ticks':x[b]})
  post=run_probe(probe_source([],True,self.base,ids))
  need(post['status']=='POST_INDEPENDENT_CLEAN','post cleanup incomplete')
  self.record('INDEPENDENT_POST_CLEANUP',post=post,recorded_identities=ids,guard_closed=self.guard_closed)
  need(self.guard_closed,'guard closure unknown despite idle probe; retain STOP, Root reconcile')
 def publish(self):
  self.check_stop();need(time.time()<self.end-10,'window publication budget exhausted')
  self.result='FAILED_RETAINED'
  if self.rc==0 and self.sender.get('status')=='SENDER_COMPLETE':
   need(self.sender['asset_id']==JOB,'unexpected sender asset')
   def timeout(sig,frame):raise TimeoutError('whole reduction window publication deadline')
   previous=signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,max(1,self.end-time.time()-5))
   try:
    commit=self.archive['publish'](self.sender);publication_closed({'id':JOB,'commit':commit})
    self.result='COMMITTED_VERIFIED';self.record('REDUCTION_PUBLISHED_CLOSED',commit=commit)
   finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
  self.record('WINDOW_TERMINAL',status=self.result)
 def spawn_resume(self):
  self.check_stop();need(remaining33(load(C/'QUEUE.json'),self.frozen)==self.selected,'pending subset drift')
  plan={'selected_ids':self.selected,'deadline_unix':DEADLINE,'Root_approval_sha256':self.pin,'Root_approval_path':str(D/'ROOT_NATIVE_ENTRY_APPROVAL_V1.json'),'token':secrets.token_hex(24),'resume_source_sha256':sha(D/'dispatch_remaining_original33_candidate_v1.py'),'original33_snapshot_sha256':'2da82e2dbad0247e81242a96d83a2d1c43252e3f60cb572ab2fd749fbd4f0ef2'}
  save(self.run/'RESUME_PLAN.json',plan);self.token=plan['token']
  self.record('RESUME_ONE_SHOT_INTENT',plan=plan)
  env=os.environ.copy();env.update(RTX_REDUCTION_RESUME_TOKEN=self.token,PYTHONDONTWRITEBYTECODE='1')
  with (self.run/'resume.stdout.log').open('x') as out,(self.run/'resume.stderr.log').open('x') as err:
   child=subprocess.Popen([sys.executable,'-B',str(D/'dispatch_remaining_original33_candidate_v1.py'),'--plan',str(self.run/'RESUME_PLAN.json')],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True)
  self.child=identity(child.pid);need(self.child,'resume child missing')
  # Child receives DISPATCHER while parent retains SOURCE/TARGET/QUEUE and exact own STOP.
  h=self.hs['RTX4080_DISPATCHER.lock'];fcntl.flock(h,fcntl.LOCK_UN);h.close()
  until=time.monotonic()+60
  while not (self.run/'RESUME_READY_WAIT_STOP_RETIRE.json').exists():
   need(time.monotonic()<until and alive(self.child),'resume READY absent; no relaunch');time.sleep(.1)
  ready=load(self.run/'RESUME_READY_WAIT_STOP_RETIRE.json')
  need(all(ready[k]==self.child[k] for k in ('pid','start_ticks','boot_id')) and ready['token']==self.token and ready['dispatcher_lease_owned'] is True,'READY identity')
  from resume_gate_v1 import lease_owned_by
  need(alive(self.child) and lease_owned_by(self.child['pid'],C/'RTX4080_DISPATCHER.lock'),'child dispatcher lease not independently observed')
  self.record('CHILD_READY_STOP_STILL_OWN',ready=ready)
  retire_owned_stop(C/'STOP_AFTER_CURRENT',self.run/'OWN_STOP_RETIRED.json',self.own)
  save(self.run/'RESUME_RUN_GATE.json',dict(self.child,token=self.token,deadline_unix=DEADLINE))
 def ack(self):
  until=time.monotonic()+60
  while not (self.run/'REMAINING33_NEW_ACK.json').exists():
   need(time.monotonic()<until and alive(self.child),'new ACK absent; no relaunch');time.sleep(.1)
  ack=load(self.run/'REMAINING33_NEW_ACK.json')
  need(all(ack[k]==self.child[k] for k in ('pid','start_ticks','boot_id')) and ack['token']==self.token and ack['selected_ids']==self.selected and ack['deadline_unix']==DEADLINE,'new ACK mismatch')
  self.record('COMPLETE_REMAINING_ORIGINAL33_RESUMED_ONCE',ack=ack)
def flow(be):
 be.prior();be.stop_and_boundary()
 # Retry only leases. Never retry/recreate grant/window/resume after an effect intent.
 while True:
  try:
   with leases(['RTX4080_DISPATCHER.lock','RTX4080_SOURCE.lock','RTX4080_TARGET.lock','RTX4080_QUEUE.lock']) as hs:
    be.hs=hs;be.fresh();be.activate();be.run_window();be.cleanup();be.publish();be.spawn_resume()
   break
  except BlockingIOError:
   if getattr(be,'effect_started',False):raise
   be.wait();continue
 be.ack()
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true',required=True);p.add_argument('--approval',required=True);p.add_argument('--approval-sha',required=True);a=p.parse_args()
 cfg=approved(a.approval,a.approval_sha)
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
 private=(D/'NATIVE_ENTRY_PRIVATE.lock').open('a');fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB)
 be=Production(cfg,a.approval_sha)
 def interrupted(sig,frame):raise InterruptedError('Native entry signal '+str(sig))
 for sig in (signal.SIGTERM,signal.SIGHUP):signal.signal(sig,interrupted)
 try:flow(be)
 except BaseException as e:
  if be.own is not None and not (C/'STOP_AFTER_CURRENT').exists():
   try:be.own=exclusive_owned_stop(C/'STOP_AFTER_CURRENT',be.stop_payload);be.record('OWN_STOP_RESTORED_UNKNOWN_HANDOFF')
   except FileExistsError:pass
  be.record('FAILED_RETAINED_NO_AUTO_RETRY_NO_FOREIGN_SIGNAL',error=repr(e),traceback=traceback.format_exc());raise
if __name__=='__main__':main()
