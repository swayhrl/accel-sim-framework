
"""One authorized exact current3 input. Remaining own budget subtracts measured subtree PSS."""
from pathlib import Path
import os,sys,json,time,hashlib,types,resource,subprocess,signal,shutil
A=Path(__file__).resolve().parent;G=2**30
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):
 with Path(p).open('x')as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def evaluate(mem_available,cg_rows,own_pss,disk_free,a):
 remaining=max(0,a['own_total_planning_bytes']-own_pss)
 peer=a['peer_SC_bridge_reserved_bytes']+a['metadata_reserved_bytes']
 host_required=a['host_floor_bytes']+remaining+peer;cg_required=a['cgroup_floor_bytes']+remaining+peer
 reasons=[]
 if own_pss>a['own_total_planning_bytes']:reasons.append('OWN_SUBTREE_PSS_OVER6GiB')
 if mem_available<host_required:reasons.append('HOST_REMAINING_BUDGET_HEADROOM')
 if disk_free<a['native_data_floor_bytes']:reasons.append('NATIVE_DATA_FLOOR')
 for r in cg_rows:
  if r['headroom']is not None and r['headroom']<cg_required:reasons.append('CG_REMAINING_BUDGET_HEADROOM:'+r['path'])
  if r['pressure'].get('full',0)>a['PSI_full_max']:reasons.append('PSI_FULL:'+r['path'])
  if r['pressure'].get('some',0)>a['PSI_some_max']:reasons.append('PSI_SOME:'+r['path'])
 return {'status':'PASS'if not reasons else'HOLD','reasons':reasons,'own_current_PSS_bytes':own_pss,'own_remaining_planning_bytes':remaining,'reserved_peer_and_metadata_bytes':peer,'host_required_bytes':host_required,'cgroup_required_raw_headroom_bytes':cg_required}
def kernel():
 mem=int(next(l.split()[1]for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')))*1024
 part=next(l.split(':',2)[2]for l in Path('/proc/self/cgroup').read_text().splitlines()if l.startswith('0::'))
 base=Path('/sys/fs/cgroup');p=base/part.lstrip('/');rows=[]
 while True:
  if(p/'memory.max').exists():
   maximum=(p/'memory.max').read_text().strip();current=int((p/'memory.current').read_text());pressure={}
   for l in(p/'memory.pressure').read_text().splitlines():
    w=l.split();pressure[w[0]]=float(next(t.split('=')[1]for t in w[1:]if t.startswith('avg10=')))
   rows.append({'path':str(p),'memory_max':maximum,'memory_current':current,'headroom':None if maximum=='max'else int(maximum)-current,'pressure':pressure})
  if p==base:break
  p=p.parent
 return {'MemAvailable_bytes':mem,'cgroup_rows':rows,'native_data_free_bytes':shutil.disk_usage('/root/data').free}
def subtree_pss(O,me):
 members=[me]+O.children(me);rows=[];total=0
 for x in members:
  before=O.ident(x[0])
  if before is None or before[1]!=x[1]:
   rows.append({'identity':x,'PSS_bytes':0,'basis':'already_disappeared_zero_credit'});continue
  try:
   text=Path('/proc',str(x[0]),'smaps_rollup').read_text()
   val=int(next(l.split()[1]for l in text.splitlines()if l.startswith('Pss:')))*1024
  except(FileNotFoundError,ProcessLookupError):
   rows.append({'identity':x,'PSS_bytes':0,'basis':'disappeared_during_read_zero_credit'});continue
  after=O.ident(x[0])
  if after is None or after[1]!=x[1]:val=0;basis='disappeared_or_replaced_zero_credit'
  else:basis='same_PID_start_ticks_pre_post'
  telemetry={}
  if val:
   try:
    status=Path('/proc',str(x[0]),'status').read_text()
    for line in status.splitlines():
     if line.split(':',1)[0]in('VmPeak','VmSize','VmHWM','VmRSS'):
      telemetry[line.split(':',1)[0]+'_bytes']=int(line.split()[1])*1024
   except(FileNotFoundError,ProcessLookupError):pass
  total+=val;rows.append({'identity':x,'PSS_bytes':val,'basis':basis,'sampled_proc_status':telemetry})
 return total,rows
def snapshot(O,me,a):
 own,rows=subtree_pss(O,me);k=kernel();v=evaluate(k['MemAvailable_bytes'],k['cgroup_rows'],own,k['native_data_free_bytes'],a)
 return {'unix':time.time(),'monotonic':time.monotonic(),'watcher':me,'own_members':rows,'kernel':k,'verdict':v}
def join_tracked(p,identity,O,stop):
 """No generic waitpid/cleanup before the exact Popen child has been waited."""
 actions=[]
 if stop and p.poll()is None:
  O.send(identity,signal.SIGTERM);actions.append('PIDFD_TERM_TRACKED_RUNNER')
 try:rc=p.wait(timeout=5 if stop else None)
 except subprocess.TimeoutExpired:
  O.send(identity,signal.SIGKILL);actions.append('PIDFD_KILL_TRACKED_RUNNER');rc=p.wait(timeout=5)
 actions.append('POPEN_WAITED_TRACKED_RUNNER')
 return rc,actions
def owned_module(a):
 p=Path(a['owned_helper_path']);b=p.read_bytes()
 if hashlib.sha256(b).hexdigest()!=a['owned_helper_sha256']:raise RuntimeError('owned helper drift')
 m=types.ModuleType('current3_exact_owned');m.__file__=str(p);exec(compile(b,str(p),'exec'),m.__dict__);return m
def main():
 a=json.loads((A/'ROOT_PREPARED_POLICY.json').read_text())
 pins=A/'PREPARED_RUN_PINS.json';runner=A/'run_fixed_full_index.py'
 assert sha(runner)==a['runner_sha256']and sha(pins)==a['pins_sha256']
 assert a['status']=='PREPARED_AWAITING_ROOT_EXACT_CURRENT3_RELEASE_NOT_EXECUTABLE'
 release=json.loads((A/'ROOT_EXACT_FUNCTIONAL_ONCE_RELEASE.json').read_text())
 assert release['status']=='ROOT_EXPLICIT_EXACT_CURRENT3_ONCE_RELEASED'
 assert release['policy_sha256']==sha(A/'ROOT_PREPARED_POLICY.json')
 assert release['watcher_sha256']==sha(__file__)
 assert release['runner_sha256']==sha(runner)
 assert release['pins_sha256']==sha(pins)
 a['outer_absolute_deadline_unix']=release['absolute_deadline_unix']
 assert 0<a['outer_absolute_deadline_unix']-time.time()<=a['outer_max_seconds']
 assert time.time()<a['outer_absolute_deadline_unix']
 assert not(A/'WATCHER_START.json').exists(),'one fixed attempt only'
 O=owned_module(a);O.set_subreaper();me=O.ident(os.getpid())
 resource.setrlimit(resource.RLIMIT_AS,(512*2**20,4*G));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{496})
 save(A/'WATCHER_START.json',{'watcher':me,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'policy_sha256':sha(A/'ROOT_PREPARED_POLICY.json'),'watcher_sha256':sha(__file__),'unix':time.time(),'new_authorization_only':True})
 first=snapshot(O,me,a);save(A/'INITIAL_RESOURCE_SNAPSHOT.json',first)
 if first['verdict']['status']!='PASS':
  save(A/'WATCHER_TERMINAL.json',{'status':'PRELAUNCH_RESOURCE_HOLD_NO_MODEL_ATTEMPT','failure_snapshot':first,'all_owned_closed':not O.children(me),'science_or_performance':False});return 2
 stops=[];p=None;joined=False;reason=None;failure=None;actions=[];last_saved=0;count=0;peak_own_PSS=0;observed_process_peaks={}
 for sig in(signal.SIGTERM,signal.SIGINT,signal.SIGHUP):signal.signal(sig,lambda s,f:stops.append(s))
 with(A/'RUNNER.stdout.log').open('xb')as out,(A/'RUNNER.stderr.log').open('xb')as err:
  p=subprocess.Popen(['/usr/bin/python3','-I','-S','-B',str(runner),'--run-reviewed'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,start_new_session=True,env={'PATH':'/usr/bin:/bin','HOME':'/root','LANG':'C','PYTHONDONTWRITEBYTECODE':'1'})
  identity=O.ident(p.pid);save(A/'RUNNER_START.json',{'watcher':me,'runner':identity,'unix':time.time()})
  try:
   while p.poll()is None:
    current=snapshot(O,me,a);count+=1
    peak_own_PSS=max(peak_own_PSS,current['verdict']['own_current_PSS_bytes'])
    for member in current['own_members']:
     key=str(member['identity'][0])+':'+member['identity'][1]
     row=observed_process_peaks.setdefault(key,{'identity':member['identity'],'sampled_peak_PSS_bytes':0,'sampled_proc_status_peaks':{}})
     row['sampled_peak_PSS_bytes']=max(row['sampled_peak_PSS_bytes'],member['PSS_bytes'])
     for name,value in member.get('sampled_proc_status',{}).items():row['sampled_proc_status_peaks'][name]=max(row['sampled_proc_status_peaks'].get(name,0),value)
    if current['verdict']['status']!='PASS':reason='RESOURCE_HOLD';failure=current
    if time.time()>=a['outer_absolute_deadline_unix']:reason='OUTER_EXACT_POLICY_BOUND';failure=current
    if stops:reason='WATCHER_SIGNAL_'+str(stops[-1]);failure=current
    if reason:
     save(A/'EXACT_STOP_SNAPSHOT.json',{'reason':reason,'snapshot':failure});break
    if time.monotonic()-last_saved>=15:
     save(A/('RESOURCE_SNAPSHOT_%04d.json'%count),current);last_saved=time.monotonic()
    time.sleep(1)
   rc,actions=join_tracked(p,identity,O,reason is not None);joined=True
   actions.append('ONLY_NOW_ORPHAN_CLEANUP')
   cleaned=O.cleanup(me)if O.children(me)else[]
   O.reap();assert not O.children(me)
  except BaseException as error:
   reason='WATCHER_EXCEPTION '+repr(error)
   save(A/'WATCHER_EXCEPTION.json',{'reason':reason,'runner':identity,'last_snapshot':locals().get('current')})
   rc,actions=join_tracked(p,identity,O,True);joined=True;actions.append('ONLY_NOW_ORPHAN_CLEANUP')
   cleaned=O.cleanup(me)if O.children(me)else[];O.reap()
  result=A/'full_run_a001/RESULT.json';model= json.loads(result.read_text())if result.exists()else None
  status='PASS_EXACT_FULL_INPUT_FUNCTIONAL'if reason is None and rc==0 and model and model['status']=='PASS_EXACT_FULL_INPUT_FUNCTIONAL'else'FAILED_OR_BOUNDED_INCOMPLETE'
  terminal={'schema':'CURRENT3_EXACT_TRACKED_EXIT_AND_OWNED_TERMINAL_V2','status':status,'watcher':me,'runner':identity,'runner_returncode':rc,'stop_reason':reason,'tracked_runner_joined_before_cleanup':joined,'ordered_actions':actions,'orphan_cleanup_identities':cleaned,'all_owned_closed':not O.children(me),'resource_samples':count,'sampled_peak_own_PSS_bytes':peak_own_PSS,'sampled_process_peaks':observed_process_peaks,'telemetry_limit':'sampled kernel VmPeak/HWM are retained when process is alive at1sec interval; not guaranteed final lifetime peak','model_result':str(result)if model else None,'model_status':model['status']if model else None,'unix':time.time(),'science_or_performance_qualification':False,'A001_not_rewritten':True,'no_auto_retry':True}
  save(A/'WATCHER_TERMINAL.json',terminal);print(json.dumps(terminal),flush=True)
  return 0 if status=='PASS_EXACT_FULL_INPUT_FUNCTIONAL'else 2
if __name__=='__main__':sys.exit(main())
