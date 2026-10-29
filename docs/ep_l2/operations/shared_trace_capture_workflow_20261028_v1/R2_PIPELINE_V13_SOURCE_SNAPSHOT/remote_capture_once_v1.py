"""One exact frozen job per hard8/20GiB service. Never runs validator/POST/archive."""
import pathlib,sys,hashlib
_p=pathlib.Path(__file__).with_name('ordinary33_common_v1.py');_b=_p.read_bytes()
if hashlib.sha256(_b).hexdigest()!='1c3e485d9b25783a5bcbcbcba125af625fdf3d9388b7bb5f3b70b67b27ae178d':raise RuntimeError('COMMON_PIN')
C=type(sys)('o33common');C.__file__=str(_p);exec(compile(_b,str(_p),'exec'),C.__dict__)
import argparse,os,json,time,subprocess,threading,signal,socket,resource
D=pathlib.Path(__file__).resolve().parent
def ident(pid):
 try:
  q=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split();return int(pid),q[19],int(q[1])
 except(FileNotFoundError,ProcessLookupError):return None
def group(pid):
 s=next(l.split(':',2)[2]for l in pathlib.Path('/proc',str(pid),'cgroup').read_text().splitlines()if l.startswith('0::'));return pathlib.Path('/sys/fs/cgroup')/s.lstrip('/')
def rss(pid):
 return next((int(l.split()[1])*1024 for l in pathlib.Path('/proc',str(pid),'status').read_text().splitlines()if l.startswith('VmRSS:')),0)
def known_comfy_RSS_policy(a,z):
 r=a['Root_known_comfy_nonperformance_policy_ref'];p=C.readref(dict(path=r['remote_path'],bytes=r['bytes'],sha256=r['sha256']))
 C.need(p['schema']=='ROOT_KNOWN_COMFY_SHARED_NONPERFORMANCE_TRACE_POLICY_V1'and p['status']=='ROOT_APPROVED'and p['nonperformance_trace_only']is True and p['science_or_performance_granted']is False,'ROOT_KNOWN_COMFY_RSS_POLICY')
 c=p['known_comfy'];C.need(p['remote_boot_id']==a['remote_boot_id']and p['gpu_uuid']=='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59'and p['known_Comfy_RSS_growth_is_telemetry']is True,'EXACT_KNOWN_COMFY_RSS_POLICY')
 return z['pid']==c['pid']and z['start_ticks']==c['start_ticks']and z['cmdline_sha256']==c['cmdline_sha256']

def bounded_group_member(pid,target,bootstrap_pid,bootstrap_ticks,expected_max):
 q=ident(pid);b=ident(bootstrap_pid)
 if q is None or b is None or b[1]!=bootstrap_ticks:return False
 if group(bootstrap_pid)!=target or group(pid)!=target:return False
 if pid not in set(map(int,(target/'cgroup.procs').read_text().split())):return False
 if int((target/'memory.max').read_text())!=expected_max or(target/'memory.swap.max').read_text().strip()!='0'or(target/'memory.oom.group').read_text().strip()!='1':return False
 return ident(pid)==q and ident(bootstrap_pid)==b

_CPU_OBSERVED_KEYS=set()
_CPU_OBSERVATION_ERRORS=[]
def record_unknown_cpu(root,diag):
 # CPU RSS is an observation, never a GPU ownership grant or future RAM cap.
 key=(diag['pid'],diag['start_ticks'])
 if key in _CPU_OBSERVED_KEYS or len(_CPU_OBSERVED_KEYS)>=64:return
 _CPU_OBSERVED_KEYS.add(key)
 try:C.save(pathlib.Path(root)/('CPU_RAM_FIRST_OBSERVATION_'+str(diag['pid'])+'_'+str(diag['start_ticks'])+'.json'),dict(schema='BOUNDED_UNKNOWN_CPU_RAM_TELEMETRY_V1',first_observation_only=True,not_a_GPU_or_future_budget_grant=True,policy_sha256='c2a82cb5c89d4e6cdbc9fabf0106eed45a4acf3eb5602e01748ca763da17d49e',observation=diag,unix=time.time()))
 except OSError as e:_CPU_OBSERVATION_ERRORS.append(repr(e));del _CPU_OBSERVATION_ERRORS[:-8]

def resources(a,jid,limits,cg,own):
 known={}
 for z in a['known_remote_residents']:
  q=ident(z['pid']);C.need(q is not None and q[1]==z['start_ticks'],'KNOWN_RESIDENT_IDENTITY')
  p=pathlib.Path('/proc',str(q[0]));C.need(hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==z['cmdline_sha256']and ident(q[0])==q,'KNOWN_RESIDENT_IDENTITY_DRIFT')
  comfy=known_comfy_RSS_policy(a,z)
  C.need(comfy or rss(q[0])<=z['baseline_RSS_bytes']+256*2**20,'KNOWN_NONCOMFY_RESIDENT_RAM_DRIFT');known[q[0]]=True
 CPU6=C.rawmodule(D/'exact_sc_cpu6_peer_v4.py','db4329bfe1d163b2fa188be90b625f95c915b75c81d0984b02ad61e62afde3f9','exactCPU6peer');cpu6=CPU6.inspect(a)
 peer=None;active=False;peerMembers=[]
 if a['SC_POST_peer_locator']is not None:
  state=peer_preflight(a);peer=state.get('peer');p=pathlib.Path(peer['cgroup'])if peer else None
  if state['status']=='SC_ACTIVE_WAIT':
   active=True;peerMembers=list(map(int,(p/'cgroup.procs').read_text().split()));known.update({n:True for n in peerMembers})
 if limits['require_SC_POST_inactive']:C.need(not active,'SERIAL20G_WAITS_FOR_ACTIVE_SC_CLOSURE')
 C.need(not(active and cpu6['active']),'CPU6_AND_LEGACY_SC10_SIMULTANEOUS_NOT_APPROVED')
 if active:
  C.need(a['Root_active_SC_mutual_coexistence_ref']is not None,'ACTIVE_SC_SCOPE_NOT_ADMITTED_NEW_CAPTURE')
  mutual=C.validate_mutual(a,C.readref(dict(path=a['Root_active_SC_mutual_coexistence_ref']['remote_path'],bytes=a['Root_active_SC_mutual_coexistence_ref']['bytes'],sha256=a['Root_active_SC_mutual_coexistence_ref']['sha256'])));C.need(limits['memory_max_bytes']<=mutual['capture_memory_bytes'],'EXACT_MUTUAL_PEER_ADMISSION')
 for p in pathlib.Path('/proc').glob('[0-9]*/status'):
  pid=int(p.parent.name)
  if pid in own or pid in known:continue
  try:
   used=rss(pid)
   if used>128*2**20:
    me=ident(os.getpid());trusted=me is not None and bounded_group_member(pid,cg,me[0],me[1],limits['memory_max_bytes'])
    if not trusted and active:trusted=bounded_group_member(pid,pathlib.Path(peer['cgroup']),peer['pid'],peer['start_ticks'],10*C.G)
    if not trusted and cpu6['active']:trusted=bounded_group_member(pid,pathlib.Path(cpu6['cgroup']),cpu6['pid'],cpu6['start_ticks'],cpu6['memory_max_bytes'])
    if not trusted:
     q=ident(pid);diag=dict(pid=pid,start_ticks=None if q is None else q[1],RSS_bytes=used,cgroup=str(group(pid)),cmdline_sha256=hashlib.sha256((p.parent/'cmdline').read_bytes()).hexdigest())
     record_unknown_cpu(D/'runs'/a['campaign_id']/jid,diag)
  except(FileNotFoundError,ProcessLookupError):pass
 available=int(next(l.split()[1]for l in pathlib.Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')))*1024
 own_remaining=max(0,limits['memory_max_bytes']-int((cg/'memory.current').read_text()));other=10*C.G if active else 0
 verdict=C.physical_ram(available,own_remaining,other+cpu6['remaining_bytes'],headroom_bytes=cpu6['physical_headroom_bytes']);verdict['exact_CPU6_peer']=cpu6;verdict['remote_foreign_future_cap_authority_complete']=False
 C.need(shutil.disk_usage(C.RB).free>=20*C.G+limits['capture_max_bytes'],'NAS_FLOOR_PLUS_CAPTURE_BOUND');C.need(shutil.disk_usage('/data/c16').free>=5*C.G+64*2**20,'109_CONTROL_FLOOR')
 verdict['unknown_CPU_telemetry_keys_observed']=len(_CPU_OBSERVED_KEYS);verdict['CPU_observation_write_errors']=list(_CPU_OBSERVATION_ERRORS);verdict['unknown_CPU_RSS_does_not_grant_GPU_or_future_RAM']=True
 return verdict
import shutil
def live_peer_from_locator(a):
 loc=a['SC_POST_peer_locator'];C.need(loc is not None,'SC_LOCATOR_REQUIRED')
 C.need(a['Root_active_SC_mutual_coexistence_ref']is not None,'ROOT_STATIC_MUTUAL_REQUIRED')
 rr=a['Root_active_SC_mutual_coexistence_ref']
 # Static Root metadata has both fixed NAS aliases; select this host's alias.
 m=C.readref(dict(path=rr['remote_path'],bytes=rr['bytes'],sha256=rr['sha256']));C.validate_mutual(a,m)
 sc=pathlib.Path(loc['remote_runtime_root']);sr=sc/'runs'/loc['run_id']
 expected=sr/'REMOTE_START.json';C.need(pathlib.Path(loc['remote_path'])==expected,'EXACT_SC_LOCATOR_PATH')
 def small(p):
  C.no_links(p)
  with p.open('rb')as f:
   b=os.fstat(f.fileno());C.need(0<b.st_size<=262144,'SC_SMALL_METADATA');raw=f.read(262145);z=os.fstat(f.fileno())
  key=lambda v:(v.st_dev,v.st_ino,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
  C.need(key(b)==key(z)and len(raw)==b.st_size,'SC_METADATA_SAMEFD')
  return raw
 sb=small(sr/'ROOT_SCOPE.raw.json');scope=json.loads(sb);scope_sha=hashlib.sha256(sb).hexdigest()
 C.need(scope['schema']=='ROOT_SC_REMOTE_POST_RESUME59_SCOPE_V2'and scope['status']=='ROOT_APPROVED_CPU_ONLY','SC_ROOT_SCOPE_SCHEMA')
 C.need(scope['run_id']==loc['run_id']and scope['code_manifest_sha256']==loc['code_manifest_sha256']==m['SC_code_manifest_sha256'],'SC_EXACT_RUN_CODE')
 C.need(scope['remote_runtime_root']==str(sc)and scope['Native_runtime_root']==loc['native_runtime_root']and scope['remote_boot_id']==a['remote_boot_id'],'SC_ROOTS_BOOT')
 C.need(hashlib.sha256(small(sc/'CODE_MANIFEST.json')).hexdigest()==loc['code_manifest_sha256'],'SC_FROZEN_CODE_MANIFEST')
 start=json.loads(small(expected));C.need(start['scope_sha256']==scope_sha and len(start['owner'])==3,'SC_START_SCOPE_OWNER')
 pid,tick,parent=start['owner'];peer=dict(pid=pid,start_ticks=tick,cgroup=start['cgroup'])
 q=ident(pid);cg=pathlib.Path(peer['cgroup'])
 if q is not None:
  C.need(q[1]==tick and group(pid)==cg,'SC_PEER_IDENTITY_CHANGED')
  argv=[os.fsdecode(v)for v in pathlib.Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')if v]
  want=['/usr/bin/python3','-I','-S','-B',str(sc/'remote_post61_v1.py'),'--run',loc['run_id'],'--scope-sha',scope_sha,'--code-sha',loc['code_manifest_sha256']]
  C.need(argv==want and C.sha(pathlib.Path('/proc',str(pid),'exe'))==a['remote_interpreter_sha256'],'SC_EXACT_ACTUAL_ARGV_ELF')
  C.need(ident(pid)==q,'SC_SAME_PID_TICKS_AFTER_METADATA')
 C.need(str(cg).endswith('/sc-post59-'+loc['run_id']+'.service')and cg.is_relative_to(pathlib.Path('/sys/fs/cgroup')),'SC_EXACT_UNIT_CGROUP')
 return peer
def peer_preflight(a):
 # Fixed Root start locator avoids circular rawscope hashes; every live identity
 # is joined to its actual argv/ELF/boot/cgroup before any exemption or wait.
 if a['SC_POST_peer_locator']is None:return dict(status='SC_CLOSED',reason='ROOT_SCOPE_DECLARED_NO_CURRENT_SC_PEER',peer=None)
 peer=live_peer_from_locator(a);p=pathlib.Path(peer['cgroup']);q=ident(peer['pid'])
 if q is not None:
  C.need(q[1]==peer['start_ticks']and group(q[0])==p,'SC_PEER_IDENTITY_CHANGED')
  C.need(int((p/'memory.max').read_text())==10*C.G and(p/'memory.swap.max').read_text().strip()=='0'and(p/'memory.oom.group').read_text().strip()=='1','SC_PEER_HARD10_SWAP0')
  quota,period=(p/'cpu.max').read_text().split();C.need(quota!='max'and int(quota)<=8*int(period),'SC_CPU_MAX800')
 if p.exists():
  ev=dict(line.split()for line in(p/'cgroup.events').read_text().splitlines());C.need(ev.get('populated')in ['0','1'],'SC_CGROUP_POPULATED_GRAMMAR');populated=ev['populated']=='1'
 else:C.need(q is None,'SC_LIVE_PROCESS_WITHOUT_BOUND_CGROUP');populated=False
 return dict(status='SC_ACTIVE_WAIT'if q is not None or populated else'SC_CLOSED',peer=peer,kernel_parent_present=q is not None,cgroup_populated=populated)

def observe_shared(root,a,scope_sha,code_sha,jid):
 start=json.loads((root/'REMOTE_START.json').read_bytes());who=start['owner'];q=ident(who[0]);C.need(q is not None and q[1]==who[1]and start['scope_sha256']==scope_sha,'SHARED_OBSERVER_LIVE_SERVICE')
 expected=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',scope_sha,'--code-sha',code_sha]
 actual=[os.fsdecode(x)for x in pathlib.Path('/proc',str(who[0]),'cmdline').read_bytes().split(b'\0')if x]
 C.need(actual==expected and C.sha(pathlib.Path('/proc',str(who[0]),'exe'))==a['remote_interpreter_sha256']and str(group(who[0]))==start['cgroup'],'SHARED_OBSERVER_ARGV_ELF_CGROUP')
 row=json.loads((root/'SHARED_COMFY_LOCK_HELD.json').read_bytes());Canon=C.rawmodule(D/'canonical_comfy_fd_v1.py',C.code_check(D,code_sha)['files']['canonical_comfy_fd_v1.py']['sha256'],'canonicalObserver')
 Canon.verify_remote(row['descriptor'],dict(Root_sha256=scope_sha,campaign_id=a['campaign_id'],job_id=jid),who)
 return dict(scope_sha256=scope_sha,job_id=jid,canonical_fd_actual_verified=True,shared_receipt_sha256=C.sha(root/'SHARED_COMFY_LOCK_HELD.json'),owner=who)

def observer(root,a,scope_sha,code_sha,jid):
 z=json.loads((root/'REMOTE_CLOSED_PROPOSAL.json').read_bytes());s=json.loads((root/'REMOTE_START.json').read_bytes());q=ident(s['owner'][0])
 C.need(s['scope_sha256']==z['scope_sha256']==scope_sha and q is not None and q[1]==s['owner'][1],'OBSERVE_SCOPE_OWNER')
 cmd=[v.decode()for v in pathlib.Path('/proc',str(q[0]),'cmdline').read_bytes().split(b'\0')if v]
 expected=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',scope_sha,'--code-sha',code_sha]
 C.need(cmd==expected and C.sha(pathlib.Path('/proc',str(q[0]),'exe'))==a['remote_interpreter_sha256'],'OBSERVE_EXACT_ARGV_AND_ELF');cg=group(q[0]);C.need(str(cg)==s['cgroup']and str(cg).endswith('/ordinary33-'+a['campaign_id']+'-'+str(a['ordered_job_ids'].index(jid))+'.service'),'OBSERVE_EXACT_CGROUP')
 C.need(set(map(int,(cg/'cgroup.procs').read_text().split()))=={q[0]}and z['owned_descendants']==[]and z['remote_GPU_LOCAL_IO_closed']is True,'OBSERVE_ALL_OWNED_AND_LEASES_CLOSED')
 return dict(scope_sha256=scope_sha,job_id=jid,proposal_sha256=C.sha(root/'REMOTE_CLOSED_PROPOSAL.json'),owned_closed=True,owner=s['owner'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--campaign',required=True);p.add_argument('--job-id',required=True);p.add_argument('--scope-sha',required=True);p.add_argument('--code-sha',required=True);p.add_argument('--blocker-preflight',action='store_true');p.add_argument('--observe-shared',action='store_true');p.add_argument('--observe',action='store_true');p.add_argument('--peer-preflight',action='store_true');x=p.parse_args()
 C.need(D==C.RB,'STAGED_REMOTE_CODE');mf=C.code_check(D,x.code_sha);root=C.RB/'runs'/x.campaign/x.job_id;sf=root/'ROOT_SCOPE.raw.json';a=C.readref(dict(path=str(sf),bytes=sf.stat().st_size,sha256=x.scope_sha));AL=json.loads((D/'ALLOWLIST33.json').read_bytes());j,limits=C.job_parameters(a,AL,x.job_id)
 C.need(a['campaign_id']==x.campaign and a['remote_host']==socket.gethostname()and a['remote_boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'REMOTE_HOST_BOOT')
 if x.peer_preflight:
  C.validate_scope(a,AL);print(json.dumps(dict(scope_sha256=x.scope_sha,job_id=x.job_id,**peer_preflight(a))));return
 if x.blocker_preflight:
  C.validate_scope(a,AL);Canon=C.rawmodule(D/'canonical_comfy_fd_v1.py',mf['files']['canonical_comfy_fd_v1.py']['sha256'],'canonicalBlockerProbe');print(json.dumps(dict(scope_sha256=x.scope_sha,job_id=x.job_id,blocked=Canon.blocker_active(a))));return
 if x.observe_shared:print(json.dumps(observe_shared(root,a,x.scope_sha,x.code_sha,x.job_id)));return
 if x.observe:print(json.dumps(observer(root,a,x.scope_sha,x.code_sha,x.job_id)));return
 C.need(C.sha(pathlib.Path('/proc/self/exe'))==a['remote_interpreter_sha256'],'EXACT_REMOTE_PYTHON_ELF');C.need(resource.getrlimit(resource.RLIMIT_AS)==(resource.RLIM_INFINITY,resource.RLIM_INFINITY),'CUDA_VIRTUAL_AS_MUST_NOT_BE_CPU_POST_AS_CAP');C.validate_scope(a,AL);Lease,O=C.dependencies(D,mf);os.umask(0o077);os.nice(15);os.sched_setaffinity(0,set(a['remote_cpu_ids']));O.set_subreaper();me=O.ident(os.getpid());cg=group(me[0]);unit='ordinary33-'+x.campaign+'-'+str(a['ordered_job_ids'].index(x.job_id))+'.service'
 C.need(str(cg).endswith('/'+unit)and int((cg/'memory.max').read_text())==limits['memory_max_bytes']and(cg/'memory.swap.max').read_text().strip()=='0'and(cg/'memory.oom.group').read_text().strip()=='1','HARD8_OR20G_SWAP0')
 q,period=(cg/'cpu.max').read_text().split();C.need(q!='max'and int(q)<=2*int(period),'CPU_QUOTA2')
 C.save(root/'REMOTE_START.json',dict(owner=me,cgroup=str(cg),scope_sha256=x.scope_sha,job_id=x.job_id))
 stop=threading.Event();last=[0.];seq=[0];heartbeat_state=dict(last_read_unix=None,last_read_monotonic=None,last_seq=0,last_kind=None,first_stop=None,reader_exception=None)
 def stopped(reason,detail=None):
  if heartbeat_state['first_stop']is None:heartbeat_state['first_stop']=dict(reason=reason,detail=detail,unix=time.time(),monotonic=time.monotonic())
  stop.set()
 def heartbeat():
  try:
   for line in sys.stdin.buffer:
    C.need(len(line)<=4096,'FRAME_SIZE');v=json.loads(line);C.need(v['scope_sha256']==x.scope_sha and v['job_id']==x.job_id and v['seq']==seq[0]+1,'FRAME_BINDING');seq[0]=v['seq']
    heartbeat_state.update(last_read_unix=time.time(),last_read_monotonic=time.monotonic(),last_seq=seq[0],last_kind=v['kind'],native_sent_unix=v.get('sent_unix'),native_stop_reason=v.get('stop_reason'))
    if v['kind']=='STOP':stopped('NATIVE_STOP_FRAME',v.get('stop_reason'));return
    C.need(v['kind']=='BEAT','FRAME_KIND');last[0]=time.monotonic()
  except BaseException as e:heartbeat_state['reader_exception']=dict(error=repr(e),traceback=__import__('traceback').format_exc());stopped('HEARTBEAT_READER_EXCEPTION',repr(e))
  finally:
   if not stop.is_set():stopped('NATIVE_STDIN_EOF')
 heartbeat_reader=threading.Thread(target=heartbeat,daemon=False);heartbeat_reader.start()
 for s in [signal.SIGTERM,signal.SIGHUP,signal.SIGINT]:signal.signal(s,lambda sig,f:stopped('REMOTE_SIGNAL_'+str(sig)))
 def check():
  reason=None
  if stop.is_set():reason=heartbeat_state['first_stop']['reason']if heartbeat_state['first_stop']else'EXTERNAL_STOP_EVENT'
  elif last[0]<=0:reason='NO_INITIAL_HEARTBEAT'
  elif time.monotonic()-last[0]>=10:reason='HEARTBEAT_READ_GAP_GE10S'
  elif time.time()>=C.DEADLINE:reason='ORIGINAL_SCOPE_DEADLINE'
  if reason is not None:
   p=root/'REMOTE_FIRST_STOP_DIAGNOSTIC.json'
   if not p.exists():C.save(p,dict(scope_sha256=x.scope_sha,job_id=x.job_id,reason=reason,heartbeat=heartbeat_state,last_read_age_seconds=None if last[0]<=0 else time.monotonic()-last[0],observed_unix=time.time(),original_absolute_deadline=C.DEADLINE,raw_frame_or_nonce_included=False))
   raise RuntimeError('HEARTBEAT_OR_DEADLINE:'+reason)
 end=time.monotonic()+10
 while not last[0]:C.need(time.monotonic()<end and not stop.is_set(),'INITIAL_HEARTBEAT');time.sleep(.05)
 proc=None;h=None;shared=None;leaf_started=False;error=None;status='CAPTURE_INCOMPLETE_RETAINED'
 try:
  check();Canon=C.rawmodule(D/'canonical_comfy_fd_v1.py',mf['files']['canonical_comfy_fd_v1.py']['sha256'],'canonicalFDguard')
  shared=Canon.production_guard(a,dict(Root_sha256=x.scope_sha,campaign_id=a['campaign_id'],job_id=x.job_id));busy_started=None
  while True:
   check()
   if not Canon.blocker_active(a):
    if busy_started is None:busy_started=time.monotonic()
    if shared.try_acquire():break
    C.need(time.monotonic()-busy_started<a['canonical_shared_wait_seconds'],'SHARED_COMFY_BUSY_DEFERRED')
   time.sleep(.25)
  C.save(root/'SHARED_COMFY_LOCK_HELD.json',dict(scope_sha256=x.scope_sha,job_id=x.job_id,owner=me,descriptor=shared.descriptor,queue_before=shared.queue_before,queue_after=shared.queue_after))
  while not(root/'NATIVE_ASSET4_READY.json').exists():check();time.sleep(.1)
  ready=json.loads((root/'NATIVE_ASSET4_READY.json').read_bytes());C.need(ready['scope_sha256']==x.scope_sha and ready['job_id']==x.job_id and ready['shared_receipt_sha256']==C.sha(root/'SHARED_COMFY_LOCK_HELD.json'),'NATIVE_READY_AFTER_SHARED_CANONICAL')
  check();resources(a,x.job_id,limits,cg,{me[0]});h=Lease.GuardLeases(Lease.PRODUCTION_PATHS,dict(Root_sha256=x.scope_sha,campaign_id=x.campaign,job_id=x.job_id))
  C.save(root/'GPU_LOCAL_IO_LEASES.json',h.descriptor)
  args=['/usr/bin/python3','-I','-S','-B',str(D/'capture_only_leaf_v1.py'),str(D/j['job_relative']),str(root/'capture'),str(sf),x.scope_sha,x.code_sha,x.job_id]
  env={k:v for k,v in os.environ.items()if k not in ['LD_PRELOAD','CUDA_INJECTION64_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE']};env.update(h.environment(),PYTHONDONTWRITEBYTECODE='1');env.update(shared.environment())
  tmp=root/'private_tmp';tmp.mkdir();(tmp/'cuda_cache').mkdir();(tmp/'xdg').mkdir();env.update(TMPDIR=str(tmp),TMP=str(tmp),TEMP=str(tmp),CUDA_CACHE_PATH=str(tmp/'cuda_cache'),XDG_CACHE_HOME=str(tmp/'xdg'))
  with(root/'leaf.stdout.log').open('xb')as out,(root/'leaf.stderr.log').open('xb')as err:
   leaf_started_monotonic=time.monotonic();leaf_started=True;proc=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=out,stderr=err,pass_fds=tuple(h.fds)+(shared.fd,),env=env)
   C.save(root/'LEAF_START.json',dict(owner=O.ident(proc.pid),argv=args));last_resource=0
   while proc.poll()is None:
    C.need(time.monotonic()-leaf_started_monotonic<=limits['capture_timeout_sec'],'PILOT_CASE_TOTAL_LEAF_WALL_BOUND');check()
    if time.monotonic()-last_resource>=5:resources(a,x.job_id,limits,cg,{me[0],*[v[0]for v in O.children(me)]});last_resource=time.monotonic()
    time.sleep(.2)
   rc=proc.wait();left=O.children(me);C.need(not left,'LEAF_LEFT_OWNED_DESCENDANTS')
  if rc==0 and a['queue_stage']=='NATIVE_QA'and(root/'capture/NATIVE_QA_RESULT.json').exists():
   q=json.loads((root/'capture/NATIVE_QA_RESULT.json').read_bytes());C.need(q['status']=='NATIVE_QA_PASS_NOT_CAPTURED'and q['job_id']==x.job_id,'ACTUAL_QA_LEAF');status='NATIVE_QA_PASS_NOT_CAPTURED'
  elif rc==0 and(root/'capture/LEAF_CAPTURED.json').exists():status='CAPTURED_POST_PENDING'
  elif(root/'capture/FAILURE.json').exists():
   f=json.loads((root/'capture/FAILURE.json').read_bytes());status=f['status'];error=f['error']
  else:error='leaf did not positively close'
 except BaseException as e:error=repr(e);status='CAPTURE_ADMISSION_DEFERRED_BEFORE_GPU'if not leaf_started else'RESOURCE_HOLD_RETAINED'if any(k in str(e)for k in ['RAM','RESOURCE','RESIDENT','SERIAL','LARGE_REMOTE','FLOOR','HARD8'])else'CAPTURE_INCOMPLETE_RETAINED'
 finally:
  stop.set()
  try:
   if O.children(me):O.cleanup(me)
   O.reap();C.need(not O.children(me),'OWNED_CLOSURE')
   if h is not None:h.close_after_closed(lambda:O.children(me))
   if shared is not None:shared.close_after_closed(lambda:O.children(me))
  except BaseException as closure_error:
   if h is not None:h.hold_unknown(root/'REMOTE_HOLD_UNKNOWN.json',closure_error,lambda:O.children(me))
   if shared is not None and shared.fd is not None:O.hold(root/'REMOTE_SHARED_HOLD_UNKNOWN.json',closure_error,[shared.fd])
   raise
 if status=='CAPTURED_POST_PENDING':
  leaf=json.loads((root/'capture/LEAF_CAPTURED.json').read_bytes());C.save(root/'CAPTURED_POST_PENDING.json',C.post_binding(a,x.job_id,root/'capture',leaf))
 C.save(root/'REMOTE_CLOSED_PROPOSAL.json',dict(stage=a['queue_stage'],scope_sha256=x.scope_sha,job_id=x.job_id,status=status,error=error,owner=me,owned_descendants=[],remote_GPU_LOCAL_IO_closed=True,source_KEEP=True,full_record_POST_archive_complete=False))
 while not(root/'NATIVE_CLEANUP_ACK.json').exists():time.sleep(.1)
 ack=json.loads((root/'NATIVE_CLEANUP_ACK.json').read_bytes());C.need(ack['scope_sha256']==x.scope_sha and ack['proposal_sha256']==C.sha(root/'REMOTE_CLOSED_PROPOSAL.json'),'EXACT_ACK')
 C.save(root/'REMOTE_ACK_CONSUMED.json',dict(scope_sha256=x.scope_sha,ACK_sha256=C.sha(root/'NATIVE_CLEANUP_ACK.json'),owner=me))
 heartbeat_reader.join(timeout=10);C.need(not heartbeat_reader.is_alive(),'HEARTBEAT_READER_NOT_CLOSED_AFTER_NATIVE_EOF')
if __name__=='__main__':main()
