"""Exact61 CPU service. Root staging and independent review required."""
import pathlib,hashlib,sys
_C=pathlib.Path(__file__).with_name('sc_remote_common_v1.py')
_B=_C.read_bytes()
if hashlib.sha256(_B).hexdigest()!='4472b0ff40f6448dd67f78d861c0e7394d23bce5f48607985df11c01d8063cd5':raise RuntimeError('COMMON_RAW_PIN')
exec(compile(_B,str(_C),'exec'),globals())
import argparse,fcntl,signal,subprocess,threading,concurrent.futures,queue,select,ctypes,socket,traceback
D=pathlib.Path(__file__).resolve().parent
def cgpath():
 v=next(x.split(':',2)[2]for x in pathlib.Path('/proc/self/cgroup').read_text().splitlines()if x.startswith('0::'))
 return pathlib.Path('/sys/fs/cgroup')/v.lstrip('/')
def hard_service(a):
 c=cgpath();need(str(c).endswith('/sc-post59-'+a['run_id']+'.service'),'EXACT_SERVICE')
 need((c/'memory.max').read_text().strip()==str(10*G)and(c/'memory.swap.max').read_text().strip()=='0'and(c/'memory.oom.group').read_text().strip()=='1','HARD10G_SWAP0')
 q,p=(c/'cpu.max').read_text().split();need(q!='max'and int(q)<=8*int(p),'CPU_QUOTA8_SINGLE_SERVICE')
 return c
def ident(pid):
 try:
  v=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
  return int(pid),v[19],int(v[1])
 except(FileNotFoundError,ProcessLookupError):return None
def resident_rss(pid):
 for l in pathlib.Path('/proc',str(pid),'status').read_text().splitlines():
  if l.startswith('VmRSS:'):return int(l.split()[1])*1024
 return 0
def process_telemetry(known,limit=20,proc=pathlib.Path('/proc')):
 # Observations carry no ownership or future-cap inference and never signal a process.
 def snapshot(pid,rss=None):
  p=proc/str(pid);out=dict(pid=int(pid),ownership='UNATTRIBUTED_OBSERVATION_ONLY')
  try:
   before=(p/'stat').read_text().rsplit(')',1)[1].split();out['start_ticks']=before[19]
   if rss is None:
    rss=next((int(l.split()[1])*1024 for l in (p/'status').read_text().splitlines()if l.startswith('VmRSS:')),0)
   out['RSS_bytes']=rss
   try:
    with(p/'cmdline').open('rb')as f:raw=f.read(65537)
    if len(raw)<=65536:out['cmdline_sha256']=hashlib.sha256(raw).hexdigest()
    else:out['cmdline_read_status']='OVER_64KiB_NO_WHOLE_SHA_CLAIM'
   except(OSError,ValueError):out['cmdline_read_status']='UNREADABLE_UNKNOWN'
   after=(p/'stat').read_text().rsplit(')',1)[1].split()
   out['identity_read_status']='OBSERVED_STABLE'if before[19]==after[19]else'CHANGED_DURING_OBSERVATION_UNKNOWN'
  except(FileNotFoundError,ProcessLookupError):out['identity_read_status']='ABSENT_OR_EXITED_DURING_OBSERVATION'
  except(OSError,ValueError,IndexError):out['identity_read_status']='UNREADABLE_OR_MALFORMED_UNKNOWN'
  return out
 large=[];unreadable=0
 try:entries=list(proc.glob('[0-9]*/status'))
 except OSError:entries=[];unreadable+=1
 for p in entries:
  try:
   rss=next((int(l.split()[1])*1024 for l in p.read_text().splitlines()if l.startswith('VmRSS:')),0)
   if rss>128*2**20:large.append((rss,int(p.parent.name)))
  except(OSError,ValueError):unreadable+=1
 large.sort(reverse=True)
 return dict(role='BOUNDED_UNATTRIBUTED_TELEMETRY_ONLY',large_processes=[snapshot(pid,rss)for rss,pid in large[:limit]],large_count_observed=len(large),large_entries_omitted=max(0,len(large)-limit),unreadable_status_count=unreadable,previously_known=[snapshot(z['pid'])for z in known[:limit]],foreign_operations=0,foreign_future_caps_complete=False)
def resource_gate(a,cg,owned,local_root,local_helper,byte_helper):
 need(hard_service(a)==cg,'ACTUAL_SINGLE_OWN_HARD10_SERVICE')
 m={}
 for l in pathlib.Path('/proc/meminfo').read_text().splitlines():
  k,v=l.split(':',1);m[k]=int(v.split()[0])*1024
 need(a['execution_mode']=='CPU_ONLY_NO_GPU_COACTIVITY'and not a['peer_POST_reservations'],'NO_GPU_OR_OTHER_POST_PEER_ADMISSION_IN_THIS_RUN')
 telemetry=process_telemetry(a['known_remote_residents'],a['remote_large_process_telemetry_limit']);local_space=local_helper.space(a,local_root,byte_helper.owned_output_bytes)
 need(hard_service(a)==cg,'HARD_SERVICE_STILL_EXACT')
 current=int((cg/'memory.current').read_text())
 try:out=memory_verdict(m['MemAvailable'],max(0,10*G-current),0,8*G)
 except PhysicalRAMShortage as shortage:shortage.detail['process_telemetry']=telemetry;raise
 out['local_ssd_space']=local_space;out['process_telemetry']=telemetry;out['execution_mode']='CPU_ONLY_NO_GPU_COACTIVITY'
 need(shutil.disk_usage(RS).free>=20*G+a['own_output_cap_bytes'],'NAS_PENDING_FLOOR')
 need(shutil.disk_usage('/data/c16').free>=5*G+64*2**20,'109_ACTUAL_DISK_FLOOR')
 return out
def observation_identity(s,a,scope_sha,q,actual_cgroup,cmdline,exe_sha):
 need(q is not None and q[0]==s['owner'][0]and q[1]==s['owner'][1],'OBSERVE_ORIGINAL_BOOTSTRAP')
 expected=['/usr/bin/python3','-I','-S','-B',str(RB/'remote_post61_v1.py'),'--run',a['run_id'],'--scope-sha',scope_sha,'--code-sha',a['code_manifest_sha256']]
 need(cmdline==expected and exe_sha==a['remote_tool_sha256']['/usr/bin/python3'],'OBSERVE_EXACT_ARGV_ELF')
 need(actual_cgroup==s['cgroup']and actual_cgroup.startswith('/sys/fs/cgroup/')and actual_cgroup.endswith('/sc-post59-'+a['run_id']+'.service'),'OBSERVE_REAL_SERVICE_CGROUP')
 return True
def observe(root,scope_sha):
 sf=root/'ROOT_SCOPE.raw.json';a=readref(dict(path=str(sf),bytes=sf.stat().st_size,sha256=scope_sha))
 need(a['run_id']==root.name and a['status']=='ROOT_APPROVED_CPU_ONLY'and a['schema']=='ROOT_SC_CPU_ONLY_REMAINING_SCOPE_V10','OBSERVE_SCOPE_AUTHORITY')
 need(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==a['remote_boot_id'],'OBSERVE_SAME_REMOTE_BOOT')
 s=json.loads((root/'REMOTE_START.json').read_bytes());need(s['scope_sha256']==scope_sha,'OBSERVE_SCOPE')
 z=json.loads((root/'REMOTE_CLOSED_PROPOSAL.json').read_bytes());need(z['scope_sha256']==scope_sha and z['owned_descendants']==[],'POSITIVE_CLOSURE')
 q=ident(s['owner'][0]);pid=s['owner'][0];proc=pathlib.Path('/proc',str(pid));cgpart=next(x.split(':',2)[2]for x in (proc/'cgroup').read_text().splitlines()if x.startswith('0::'));actual_cgroup=str(pathlib.Path('/sys/fs/cgroup')/cgpart.lstrip('/'));cmdline=[v.decode()for v in (proc/'cmdline').read_bytes().split(b'\0')if v];observation_identity(s,a,scope_sha,q,actual_cgroup,cmdline,digest(proc/'exe'))
 cg=pathlib.Path(s['cgroup']);members=set(map(int,(cg/'cgroup.procs').read_text().split()))
 need(members=={s['owner'][0]},'EXACT_SERVICE_CLOSED_EXCEPT_BOOTSTRAP')
 for x in z['started']:
  now=ident(x[0]);need(now is None or now[1]!=x[1],'STARTED_ACTOR_STILL_LIVE')
 return dict(schema='SC_REMOTE_POST61_CLOSURE_OBSERVATION_V1',scope_sha256=scope_sha,proposal_sha256=digest(root/'REMOTE_CLOSED_PROPOSAL.json'),owner=s['owner'],owned_closed=True,service_members=sorted(members))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--scope-sha',required=True);ap.add_argument('--code-sha',required=True);ap.add_argument('--observe',action='store_true');x=ap.parse_args()
 code_check(D,x.code_sha);root=RB/'runs'/x.run;need(pathlib.Path(__file__).resolve().parent==RB,'ROOT_STAGED_REMOTE_CODE')
 if x.observe:print(json.dumps(observe(root,x.scope_sha)));return
 sf=root/'ROOT_SCOPE.raw.json';a=validate_scope(readref(dict(path=str(sf),bytes=sf.stat().st_size,sha256=x.scope_sha)))
 need(a['run_id']==x.run,'EXACT_RUN');need(socket.gethostname()==a['remote_host']and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==a['remote_boot_id'],'ROOT_REMOTE_HOST_BOOT');cg=hard_service(a);need(set(a['remote_cpu_ids'])<=os.sched_getaffinity(0),'ALLOWED_CPUS');os.sched_setaffinity(0,set(a['remote_cpu_ids']));os.nice(15)
 resource.setrlimit(resource.RLIMIT_AS,(2*G,2*G));resource.setrlimit(resource.RLIMIT_CORE,(0,0));need(ctypes.CDLL(None).prctl(36,1,0,0,0)==0,'SUBREAPER')
 os.umask(0o077);need(not(root/'REMOTE_START.json').exists(),'NEW_RUN_ONLY')
 mf=json.loads((D/'CODE_MANIFEST.json').read_bytes());r=mf['files']['owned_runtime_v1.py'];O=pinned_module(D/'owned_runtime_v1.py',r['sha256'],'exact_owned')
 me=O.ident(os.getpid());save(root/'REMOTE_START.json',dict(owner=me,cgroup=str(cg),scope_sha256=x.scope_sha,unix=time.time()))
 stop=threading.Event();last=[0.];seq=[0]
 def beats():
  try:
   for line in sys.stdin.buffer:
    need(len(line)<=4096,'FRAME_BOUND');v=json.loads(line);need(v['scope_sha256']==x.scope_sha and v['seq']==seq[0]+1,'FRAME_SCOPE_SEQUENCE');seq[0]=v['seq']
    if v['kind']=='STOP':stop.set();return
    need(v['kind']=='BEAT','FRAME_KIND');last[0]=time.monotonic()
  finally:stop.set()
 beats_thread=threading.Thread(target=beats,daemon=True);beats_thread.start()
 for sig in [signal.SIGTERM,signal.SIGHUP,signal.SIGINT]:signal.signal(sig,lambda s,f:stop.set())
 cpu_slots=queue.Queue();[cpu_slots.put(c)for c in a['remote_cpu_ids']];worker_cpu=threading.local()
 error_lock=threading.Lock()
 def record_first_exception(e):
  with error_lock:
   if not(root/'FIRST_EXCEPTION.json').exists():
    tb=traceback.extract_tb(e.__traceback__);caller=dict(file=tb[-1].filename,line=tb[-1].lineno,function=tb[-1].name)if tb else None
    save(root/'FIRST_EXCEPTION.json',dict(error=str(e),error_repr=repr(e),traceback=traceback.format_exc(),caller=caller,scope_sha256=x.scope_sha))
 started=[];records={};deadline=time.monotonic()+max(0,DEADLINE-time.time());last_resource=[0.];mutex=threading.Lock()
 ob=mf['files']['owned_output_bytes_v1.py'];B=pinned_module(D/'owned_output_bytes_v1.py',ob['sha256'],'exact_owned_output_bytes')
 ls=mf['files']['local_ssd_scratch_v1.py'];L=pinned_module(D/'local_ssd_scratch_v1.py',ls['sha256'],'exact_local_ssd_scratch');local_root=None
 output_mutex=threading.Lock();last_output=[float('-inf')]
 def output_cap(force=False):
  if not output_mutex.acquire(blocking=force):return
  try:
   if force or time.monotonic()-last_output[0]>=a['output_cap_interval_seconds']:
    last_output[0]=time.monotonic();need(B.owned_output_bytes(root)<=a['own_output_cap_bytes'],'OWN_OUTPUT_CAP')
  finally:output_mutex.release()
 pa=mf['files']['owned_post_pause_v1.py'];P=pinned_module(D/'owned_post_pause_v1.py',pa['sha256'],'exact_owned_pause')
 pause=P.OwnedPostPause(O,me,a['max_memory_pause_seconds'],log=lambda event,**v:save(root/('MEMORY_PAUSE_'+str(time.time_ns())+'.json'),dict(event=event,unix=time.time(),**v)))
 def check_control():
  need(not stop.is_set()and last[0]>0 and time.monotonic()-last[0]<10,'HEARTBEAT_OR_STOP')
  need(time.time()<DEADLINE and time.monotonic()<deadline,'ORIGINAL_DEADLINE')
 def probe_resources():return resource_gate(a,cg,{me[0],*[q[0]for q in O.children(me)]},local_root,L,B)
 def check():
  check_control()
  with mutex:
   if time.monotonic()-last_resource[0]>=5:
    try:v=probe_resources()
    except PhysicalRAMShortage:v=pause.wait_until(probe_resources,check_control,PhysicalRAMShortage)
    save(root/('RESOURCE_'+str(time.time_ns())+'.json'),v);last_resource[0]=time.monotonic()
  output_cap()
 def one_body(item):
  index,n=item;check();kdir=root/('kernel_%04d'%index);kdir.mkdir();source=RS/'traces'/n;no_links(source);before=source.stat();out=kdir/n.replace('.trace.xz','.traceg.xz');work=L.work(a,local_root,index);post_start=time.monotonic()
  cpu=worker_cpu.value
  args=['/usr/bin/taskset','-c',str(cpu),'/usr/bin/nice','-n','15','/usr/bin/prlimit','--as=1610612736:1610612736','--core=0:0','--','/usr/bin/python3','-I','-S','-B',str(D/'postprocess_nas_sharded_v4.py'),str(source),str(out),str(work),'--cta-span','64','--scratch-budget',str(a['per_worker_scratch_budget_bytes'])]
  with(kdir/'stdout.log').open('xb')as so,(kdir/'stderr.log').open('xb')as se:
   with mutex:
    check_control()
    p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=so,stderr=se,start_new_session=True,env=dict(PATH='/usr/bin:/bin',LC_ALL='C',TMPDIR=str(kdir),PYTHONDONTWRITEBYTECODE='1'))
    pi=O.ident(p.pid);need(pi is not None,'CHILD_START_IDENTITY');started.append(pi);save(kdir/'START.json',dict(owner=pi,argv=args,scope_sha256=x.scope_sha))
   while p.poll()is None:check();time.sleep(.2)
   need(p.wait()==0,'POST_NONZERO')
  check();r=json.loads((work/'GROUP_RECEIPT.json').read_bytes());v=normalize_result(n,r,a,root)
  after=source.stat();need((before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_size,after.st_mtime_ns,after.st_ctime_ns),'SOURCE_DRIFT')
  need(digest(out)==r['grouped_sha256']and out.stat().st_size==r['grouped_bytes'],'CLOSED_GROUP_FULL_SHA')
  receipt=L.export_evidence(work,kdir/'EVIDENCE');need(json.loads(receipt.read_bytes())==r,'NAS_RECEIPT_RAW_BINDING');v['raw_receipt_ref']=ref(receipt);v['checkpoint_ref']=ref(kdir/'EVIDENCE/CHECKPOINT.json');v['local_scratch_manifest_ref']=ref(kdir/'EVIDENCE/LOCAL_SCRATCH_MEMBERS.json');v['post_wall_seconds']=time.monotonic()-post_start;save(kdir/'NORMALIZED_CLOSED.json',v);records[n]=ref(kdir/'NORMALIZED_CLOSED.json')
  if a['cleanup_own_local_scratch_after_NAS_closed']:L.cleanup(a,local_root,index,work,x.scope_sha,kdir/'EVIDENCE',kdir/'NORMALIZED_CLOSED.json')
 def one(item):
  try:return one_body(item)
  except BaseException as e:record_first_exception(e);raise
 error=None
 try:
  local_root=L.setup(a,x.scope_sha)
  end=time.monotonic()+10
  while not last[0]:need(time.monotonic()<end and not stop.is_set(),'INITIAL_HEARTBEAT');time.sleep(.02)
  need(digest(D/'postprocess_nas_sharded_v4.py')==POST_SHA,'ORIGINAL5D')
  for p,h in a['remote_tool_sha256'].items():need(p in ['/usr/bin/taskset','/usr/bin/nice','/usr/bin/prlimit','/usr/bin/python3','/usr/bin/sort']and digest(pathlib.Path(p).resolve())==h,'REMOTE_TOOL_SHA')
  need(set(a['remote_tool_sha256'])=={'/usr/bin/taskset','/usr/bin/nice','/usr/bin/prlimit','/usr/bin/python3','/usr/bin/sort'},'COMPLETE_TOOL_PINS')
  lock=pathlib.Path(a['remote_asset_POST_lock']);need(lock==pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/asset_operations')/JOB/'POST.lock','EXACT_ASSET_IO_LOCK')
  fd=os.open(lock,os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  check()
  with concurrent.futures.ThreadPoolExecutor(max_workers=8,initializer=lambda:setattr(worker_cpu,'value',cpu_slots.get()))as pool:
   futures=[pool.submit(one,z)for z in enumerate(a['selected'])]
   for future in concurrent.futures.as_completed(futures):
    try:future.result()
    except BaseException:stop.set();O.cleanup(me);raise
  output_cap(force=True)
 except BaseException as e:record_first_exception(e);error=repr(e)
 finally:
  stop.set()
  if O.children(me):O.cleanup(me)
  O.reap();need(not O.children(me),'OWNED_CLOSURE')
  if 'fd'in locals():os.close(fd)
 proposal=dict(schema='SC_REMOTE_POST61_CLOSED_PROPOSAL_V1',scope_sha256=x.scope_sha,owner=me,owned_descendants=[],started=started,closed_refs=records,status='ALL_REMAINING_SELECTED_CLOSED'if error is None and len(records)==len(a['selected']) else'FAILED_RETAINED',error=error,source_KEEP=True,archive_COMPLETE=False)
 save(root/'REMOTE_CLOSED_PROPOSAL.json',proposal)
 # Bootstrap stays alive for an independent observation. Missing ACK never invents closure.
 while not(root/'NATIVE_CLEANUP_ACK.json').exists():time.sleep(.1)
 ack=json.loads((root/'NATIVE_CLEANUP_ACK.json').read_bytes());need(ack['scope_sha256']==x.scope_sha and ack['proposal_sha256']==digest(root/'REMOTE_CLOSED_PROPOSAL.json'),'EXACT_ACK')
 save(root/'REMOTE_ACK_CONSUMED.json',dict(scope_sha256=x.scope_sha,ACK_sha256=digest(root/'NATIVE_CLEANUP_ACK.json'),owner=me))
 beats_thread.join(timeout=10)
 if beats_thread.is_alive():
  try:save(root/'REMOTE_READER_EOF_HOLD.json',dict(scope_sha256=x.scope_sha,error='Native stdin EOF not received after ACK consumption',no_new_work=True))
  except BaseException:pass
  while beats_thread.is_alive():beats_thread.join(timeout=1)
 if error is not None:raise RuntimeError(error)
if __name__=='__main__':main()
