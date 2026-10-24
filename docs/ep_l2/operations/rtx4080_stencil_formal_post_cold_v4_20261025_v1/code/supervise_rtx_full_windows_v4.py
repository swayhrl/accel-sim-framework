"""Private exact all-member cold restore guard. Requires separate parent grant."""
import os,sys,json,pathlib,hashlib,time,signal,subprocess,stat,shutil,importlib.util
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
I='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';PREFIX=I+'_COLD_V2_'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 assert not p.exists();tmp=p.with_name(p.name+'.tmp')
 with tmp.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def proc(pid):
 s=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
 return dict(pid=int(pid),ticks=s[19],sid=int(s[3]),pgid=int(s[2]),state=s[0],rss=max(0,int(s[21]))*os.sysconf('SC_PAGE_SIZE'))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BOOT="import os,sys,ctypes;parent=int(sys.argv[1]);assert ctypes.CDLL(None).prctl(1,15,0,0,0)==0;assert os.getppid()==parent;fd=int(sys.argv[2]);token=os.read(fd,1);os.close(fd);sys.exit(125)if token!=b'G'else None;os.execv(sys.executable,[sys.executable,'-B',sys.argv[3],sys.argv[4]])"
def main():
 grantpath=pathlib.Path(sys.argv[1]);g=json.loads(grantpath.read_text());assert g['status']=='APPROVED_EXACT_STENCIL_ALL_MEMBER_COLD_V2'
 assert g['asset_id']==I and sha(pathlib.Path(__file__))==g['supervisor_sha256']
 worker=C/'restore_rtx_full_windows_v2.py';assert sha(worker)==g['worker_sha256']
 assert g['deadline_seconds']==21600
 for r in g['dependencies']:
  p=pathlib.Path(r['path']);assert p.stat().st_size==r['bytes']and sha(p)==r['sha256']
 assert sha(C/(I+'_POST_EPOCH4_SUPERVISOR_TERMINAL.json'))==g['post_terminal_sha256']
 assert json.loads((C/(I+'_POST_EPOCH4_SUPERVISOR_TERMINAL.json')).read_text())['status']=='PASS'
 authpath=C/'read_native_foreign_reserve_v1.py';assert sha(authpath)=='441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba';auth=module('auth',authpath)
 work=pathlib.Path(g['work']);assert work==N/(I+'_bounded_cold_v2')and not work.exists()
 assert pathlib.Path(g['candidate'])==work/'FINAL_CANDIDATE.json'
 assert not list(C.glob(PREFIX+'*')),'exact ABSENT cold attempt controls required'
 assert hasattr(os,'pidfd_open')and hasattr(signal,'pidfd_send_signal')
 stop=[];signal.signal(signal.SIGTERM,lambda s,f:stop.append(s));signal.signal(signal.SIGINT,lambda s,f:stop.append(s))
 p=None;identity=None;gatein=gateout=None;known={};start=time.monotonic();last=None;lastat=0;peakrss=peakdisk=0;failure=None;unresolved=[];dropped=0;observed_returncode=None
 def usage():
  total=0
  for q in list(work.glob('*'))+list(C.glob(PREFIX+'*')):
   try:s=q.stat()
   except OSError as e:
    if e.errno==2:continue
    raise
   assert stat.S_ISREG(s.st_mode);total+=s.st_size
  return total
 def guard(admit=False):
  nonlocal last,lastat,peakrss,peakdisk
  assert not stop and time.monotonic()-start<21600
  if last is None or time.monotonic()-lastat>=10:last=auth.snapshot();lastat=time.monotonic()
  used=usage();peakdisk=max(peakdisk,used);assert used<=128*2**20
  floor=5*2**30+last['sum_all_records_reserved_write_bytes']+2**30+64*2**20
  assert shutil.disk_usage(N).free>=floor+max(0,128*2**20-used)+(128*2**20 if admit else 0)
  return dict(used=used,floor=floor,authority=last,free=shutil.disk_usage(N).free)
 def refresh():
  if identity is None:return
  # New membership is admissible only while the unreaped original leader
  # still pins this exact PID/start/SID/PG. Otherwise known identities only.
  try:leader=proc(identity['pid'])
  except(FileNotFoundError,ProcessLookupError):return
  if any(leader[k]!=identity[k]for k in ['pid','ticks','sid','pgid']):return
  for f in pathlib.Path('/proc').glob('[0-9]*/stat'):
   try:q=proc(int(f.parent.name))
   except(FileNotFoundError,ProcessLookupError):continue
   if q['sid']==identity['sid']and q['pgid']==identity['pgid']and int(q['ticks'])>=int(identity['ticks']):known[q['pid']]=q
 def live():
  out=[]
  for q in list(known.values()):
   try:r=proc(q['pid'])
   except(FileNotFoundError,ProcessLookupError):continue
   if(r['ticks'],r['sid'],r['pgid'])==(q['ticks'],q['sid'],q['pgid'])and r['state']not in ['Z','X','x']:out.append(r)
  return out
 def sig(q,number):
  try:fd=os.pidfd_open(q['pid'])
  except ProcessLookupError:return
  try:
   try:r=proc(q['pid'])
   except(FileNotFoundError,ProcessLookupError):return
   if(r['ticks'],r['sid'],r['pgid'])==(q['ticks'],q['sid'],q['pgid'])and r['state']not in ['Z','X','x']:signal.pidfd_send_signal(fd,number)
  except ProcessLookupError:pass
  finally:os.close(fd)
 def cleanup():
  nonlocal identity
  if p is None:return []
  if identity is None:identity=proc(p.pid);known[p.pid]=identity
  # Stop creators before rediscovering the private-session descendants.
  end=time.monotonic()+3;previous=None
  while time.monotonic()<end:
   refresh();active=live()
   for q in active:sig(q,signal.SIGSTOP)
   identities={(q['pid'],q['ticks'])for q in active};stopped=True
   for q in active:
    try:rows=list(pathlib.Path('/proc',str(q['pid']),'task').glob('*/stat'));stopped=stopped and all(f.read_text().rsplit(')',1)[1].split()[0]in ['T','t','Z','X','x']for f in rows)
    except(FileNotFoundError,ProcessLookupError):pass
   if identities==previous and stopped:break
   previous=identities;time.sleep(.05)
  for number in [signal.SIGTERM,signal.SIGKILL]:
   refresh()
   for q in live():
    sig(q,number)
    if number==signal.SIGTERM:sig(q,signal.SIGCONT)
   end=time.monotonic()+3
   while time.monotonic()<end:
    refresh()
    if not live():break
    time.sleep(.05)
  refresh();left=live()
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:left.append({'pid':p.pid,'unreaped_direct_child':True})
  return left
 try:
  guard(True);gatein,gateout=os.pipe()
  with(C/(PREFIX+'STDOUT.log')).open('x')as log:
   p=subprocess.Popen([sys.executable,'-B','-c',BOOT,str(os.getpid()),str(gatein),str(worker),str(grantpath)],pass_fds=(gatein,),start_new_session=True,stdout=log,stderr=subprocess.STDOUT)
  identity=proc(p.pid);assert identity['sid']==identity['pgid']==p.pid;known[p.pid]=identity
  put(C/(PREFIX+'PROCESS_START.json'),dict(supervisor=proc(os.getpid()),worker=identity,grant_sha256=sha(grantpath)))
  assert not stop;os.write(gateout,b'G');os.close(gateout);gateout=None;os.close(gatein);gatein=None
  with(C/(PREFIX+'MONITOR.jsonl')).open('x')as log:
   while os.waitid(os.P_PID,p.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)is None:
    refresh();ps=live();rss=sum(q['rss']for q in ps)+proc(os.getpid())['rss'];peakrss=max(peakrss,rss);assert rss<=2*2**30
    r=guard();event=json.dumps(dict(unix=time.time(),RSS=rss,resource=r,processes=ps))+'\n'
    if log.tell()+len(event.encode())<=4*2**20:log.write(event);log.flush()
    else:dropped+=1
    time.sleep(.5)
  state=os.waitid(os.P_PID,p.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT);assert state.si_code==os.CLD_EXITED and state.si_status==0
  observed_returncode=state.si_status
  refresh();assert not live();guard()
  candidate=pathlib.Path(g['candidate']);result=json.loads(candidate.read_text());assert result['status']=='ALL_MANIFEST_MEMBERS_BOUNDED_NATIVE_COLD_RESTORE_PASS'
  final=C/(PREFIX+'PASS.json');binding={'status':'OBSERVED_WORKER_EXIT0_ALL_MANIFEST_COLD_COMPLETE','worker_returncode':observed_returncode,'worker_identity':identity,'grant_sha256':sha(grantpath),'candidate_sha256':sha(candidate),'output_path':str(final),'output_sha256':sha(candidate),'no_GPU_SIM_109_or_record_validator':True}
  put(C/(PREFIX+'CONTROLLER_COMPLETE.json'),binding);os.replace(candidate,final)
  # Reap and every success-qualification write remain inside this protected try.
  assert p.wait(timeout=3)==observed_returncode
  put(C/(PREFIX+'TERMINAL.json'),dict(status='PASS',failure=None,unresolved=[],worker_rc=observed_returncode,Native_peak_bytes=peakdisk,RSS_peak=peakrss,telemetry_dropped=dropped,polled_not_quota=True))
 except BaseException as e:
  failure=repr(e)
  for fd in [gatein,gateout]:
   if fd is not None:
    try:os.close(fd)
    except OSError:pass
  try:unresolved=cleanup()
  except BaseException as e:unresolved=[{'cleanup_error':repr(e)}]
  # Withdraw any unclosed public success artifacts, retaining their original
  # bytes as explicitly unqualified history. Failure overrides all candidates.
  retained=[];persistence_errors=[]
  sources=[pathlib.Path(g['candidate'])]+[C/(PREFIX+n)for n in ['CONTROLLER_COMPLETE.json','PASS.json','TERMINAL.json']]
  for source in sources:
   for current in [source,source.with_name(source.name+'.tmp')]:
    try:
     if current.exists():
      history=current.with_name(current.name+'.UNQUALIFIED_RETAINED')
      assert not history.exists();os.replace(current,history);retained.append(str(history))
    except BaseException as e:persistence_errors.append({'path':str(current),'error':repr(e)})
  note=dict(status='FAILED_RETAINED',failure=failure,unresolved_exact_own=unresolved,source_KEEP=True,unqualified_success_history=retained,persistence_errors=persistence_errors)
  for path,record in [(C/(PREFIX+'FAILURE.json'),note),(C/(PREFIX+'TERMINAL.json'),dict(status='FAILED_RETAINED',failure=failure,unresolved=unresolved,worker_rc=(p.returncode if p is not None and p.returncode is not None else observed_returncode),Native_peak_bytes=peakdisk,RSS_peak=peakrss,telemetry_dropped=dropped,polled_not_quota=True,unqualified_success_history=retained))]:
   try:put(path,record)
   except BaseException as e:persistence_errors.append({'path':str(path),'error':repr(e)})
  if persistence_errors:sys.stderr.write(json.dumps({'failure_metadata_not_fully_persisted':persistence_errors})+'\n')
  # Even if Native writes fail, this process never reports successful exit.
  raise SystemExit(1)
if __name__=='__main__':main()
