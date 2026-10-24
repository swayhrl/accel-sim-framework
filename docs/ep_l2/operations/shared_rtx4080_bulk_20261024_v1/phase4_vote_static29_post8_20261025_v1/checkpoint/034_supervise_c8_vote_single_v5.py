import pathlib,json,hashlib,subprocess,time,os,signal,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';N=R/'local_staging';PACKAGE=C/'C8_VOTE_SINGLE_REVIEW_PACKAGE_V5.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def rec(pid):
 try:
  d=pathlib.Path('/proc',str(pid));t=(d/'stat').read_text().split(') ',1)[1].split();return{'pid':pid,'ppid':int(t[1]),'pgid':int(t[2]),'start_ticks':t[19],'state':t[0],'RSS':int(t[21])*os.sysconf('SC_PAGE_SIZE')}
 except(FileNotFoundError,PermissionError,ProcessLookupError):return None
def descendants(pid):
 found={};pending=[pid]
 while pending:
  n=pending.pop()
  if n in found:continue
  q=rec(n)
  if not q:continue
  found[n]=q
  try:
   for t in pathlib.Path('/proc',str(n),'task').iterdir():
    try:pending+=list(map(int,(t/'children').read_text().split()))
    except(FileNotFoundError,PermissionError):pass
  except(FileNotFoundError,PermissionError):pass
 return found
def treebytes():
 n=0
 for p in N.rglob('*'):
  try:
   if p.is_file():n+=p.stat().st_size
  except FileNotFoundError:pass
 return n
def cleanup(seen,worker=None,jobroot=None,expected_argv=None):
 if worker:
  q=rec(worker.pid)
  if q and (q['pid'],q['start_ticks'])in seen:
   for pid,v in descendants(worker.pid).items():seen[(pid,v['start_ticks'])]=v
 if jobroot:
  for path in [jobroot/'PROCESS_START.json',jobroot/'observer/PROCESS_START.json']:
   try:
    r=json.loads(path.read_text());q=rec(r['capture_pid'])
    if q and q['start_ticks']==r['capture_start_ticks']:
     actual=[v.decode()for v in(pathlib.Path('/proc',str(q['pid']))/'cmdline').read_bytes().split(b'\0')if v]
     if actual==expected_argv:seen[(q['pid'],q['start_ticks'])]=q
   except(FileNotFoundError,ProcessLookupError,ValueError,KeyError):pass
 for sig in [signal.SIGTERM,signal.SIGKILL]:
  groups=set()
  for(pid,t),q in seen.items():
   v=rec(pid)
   if v and v['start_ticks']==t and v['pgid']==q['pgid']and v['state']!='Z':groups.add(v['pgid'])
  for pg in groups:
   try:os.killpg(pg,sig)
   except ProcessLookupError:pass
  time.sleep(3)
 unresolved=[]
 for(pid,t),q in seen.items():
  v=rec(pid)
  if v and v['start_ticks']==t and v['pgid']==q['pgid']and v['state']!='Z':unresolved.append(v)
 return unresolved

grantpath=C/'PARENT_C8_VOTE_SINGLE_JOB_APPROVAL_V1.json';grant=json.loads(grantpath.read_text());package=json.loads(PACKAGE.read_text())
assert grant['status']=='APPROVED_SINGLE_EXACT_VOTE_SNAPSHOT_JOB'and grant['supervisor_sha256']==sha(pathlib.Path(__file__))
assert grant['review_package_sha256']==sha(PACKAGE);worker=pathlib.Path(package['worker']['path']);assert sha(worker)==grant['worker_sha256']==package['worker']['sha256']
for dep in package['runtime_dependencies']:
 path=pathlib.Path(dep['source']);assert path.stat().st_size==dep['bytes']and sha(path)==dep['sha256']
batch_deadline=time.time()+package['policy']['deadline_seconds'];results=[]
stop_requested=[]
def interrupted(signum,frame):stop_requested.append({'signal':signum,'unix':time.time()})
signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
for item in package['jobs']:
 assert time.time()<batch_deadline and not stop_requested
 job=pathlib.Path(item['path']);assert sha(job)==item['sha256']==grant['jobs'][item['id']]
 root=N/'inflight'/item['id'];assert not root.exists()and treebytes()<2*2**30 and shutil.disk_usage(N).free>20*2**30
 seen={};p=None;failure=None;expected_argv=json.loads(job.read_text())['task']['argv'];started=time.time();deadline=min(batch_deadline,started+600);peak=treebytes()
 try:
  with(C/(item['id']+'_STDOUT.log')).open('x')as out,(C/(item['id']+'_STDERR.log')).open('x')as err:
   p=subprocess.Popen(['python3','-B',str(worker),str(job)],stdout=out,stderr=err,start_new_session=True)
   immediate=rec(p.pid);assert immediate;seen[(p.pid,immediate['start_ticks'])]=immediate
   ident={'supervisor_pid':os.getpid(),'pid':p.pid,'start_ticks':rec(p.pid)['start_ticks'],'deadline_unix':deadline,'worker_sha256':sha(worker),'job_sha256':sha(job),'approval_sha256':sha(grantpath),'all_phases_monitored':True};save(C/(item['id']+'_SUPERVISOR_START.json'),ident)
   while p.poll()is None:
    observed=descendants(p.pid)
    for pid,q in observed.items():seen[(pid,q['start_ticks'])]=q
    rss=sum(q['RSS']for q in observed.values())+rec(os.getpid())['RSS']
    used=treebytes();peak=max(peak,used)
    if time.time()>deadline or used>2*2**30 or shutil.disk_usage(N).free<20*2**30 or rss>2*2**30 or stop_requested:failure={'reason':'allphase deadline/budget/free threshold','used':used};break
    time.sleep(.2)
   if failure:cleanup(seen,p,root,expected_argv)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:cleanup(seen,p,root,expected_argv);failure=dict(failure or{},unresolved_kernel_exit=True)
   out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
  assert not failure and p.returncode==0,(failure,p.returncode)
  sender=json.loads((C/(item['id']+'_STDOUT.log')).read_text());assert sender['status']=='LOCAL_STAGING_SENDER_COMPLETE_NOT_ARCHIVED'
  manifest=root/'SENDER_MANIFEST.json';assert sha(manifest)==sender['sender_manifest_sha256'];m=json.loads(manifest.read_text());expected={x['path']for x in m['files']}|{'SENDER_MANIFEST.json'}
  assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()or p.is_symlink()}==expected
  for x in m['files']:
   f=root/x['path'];assert f.is_file()and not f.is_symlink()and f.stat().st_size==x['bytes']
   with f.open('rb')as h:os.fsync(h.fileno())
   assert sha(f)==x['sha256']
  assert treebytes()<=2*2**30 and shutil.disk_usage(N).free>20*2**30
  assert not stop_requested,'stop requested before LOCAL_CLOSED publication'
  receipt={'status':'LOCAL_CLOSED_NOT_ARCHIVED_NOT_FORMAL','id':item['id'],'sender':sender,'all_files_fsync_reopen_fullSHA':True,'files':len(m['files']),'bytes':sum(x['bytes']for x in m['files']),'source_KEEP':True,'old55_objects_unchanged':True,'new_source_workload_coverage_increment':1,'observer_trace_identity':json.loads((root/'INPUT_SNAPSHOT_PAIR_IDENTITY.json').read_text()),'supervisor':ident,'owned_process_identities':list(seen.values()),'peak_polled_total_staging_bytes':peak,'ended':time.time()}
  save(C/(item['id']+'_LOCAL_CLOSED.json'),receipt);results.append({'id':item['id'],'status':receipt['status'],'bytes':receipt['bytes']})
 except BaseException as e:
  unresolved=cleanup(seen,p,root,expected_argv);save(C/(item['id']+'_SUPERVISOR_FAILURE.json'),{'error':repr(e),'unresolved_exact_own_processes':unresolved,'traceback':traceback.format_exc(),'source_KEEP':True,'GPU_rerun':False,'formal_count_increment':0});raise
save(C/'C8_VOTE_SINGLE_LOCAL_RESULTS_V1.json',{'status':'ONE_EXACT_LOCAL_PAIR_COMPLETE_NOT_ARCHIVED','results':results,'source_KEEP':True,'new_source_workload_coverage_increment':1})
