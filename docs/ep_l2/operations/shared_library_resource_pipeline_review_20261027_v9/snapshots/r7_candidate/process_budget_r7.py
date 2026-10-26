"""Explicit R7 process-AS mode; never a fallback for missing cgroup."""
from pathlib import Path
import os,json,hashlib,resource,subprocess,time,fcntl,signal,threading
GIB=2**30;MIB=2**20;MODE='EXPLICIT_PROCESS_AS_R7';CHILD=384*MIB
PAIRS=[['EP','EP_R5'],['DTC','DTC_DM'],['DTC','DTC_DH'],['DTC','DTC_CM'],['DTC','DTC_CH']]
def need(x,m):
 if not x:raise RuntimeError('R7_PROCESS_BUDGET_HOLD_'+m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def ticks(pid):return Path('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split()[19]
def live(row):
 try:
  f=Path('/proc/'+str(row['pid'])+'/stat').read_text().split(') ',1)[1].split();return f[19]==str(row['start_ticks'])and f[0]not in ['Z','X']
 except(FileNotFoundError,ProcessLookupError):return False
def validate(r,spec,v):
 b=v['r7_process_budget']
 need(b==dict(parent_AS_bytes=4*GIB,runner_AS_bytes=3*GIB,CPP_each_AS_bytes=CHILD,max_CPP=10,max_live_ready_actors=12,max_total_PID_actors_including_aux=14,steady_core_VM_bytes=11*GIB-256*MIB,conservative_fork_VM_bytes=16*GIB,cpu_ids=[0,1],nice_at_least=15,aux_warm_before_next_session=True),'EXACT_BUDGET_NOT_8G_CGROUP')
 need(list(sorted(os.sched_getaffinity(0)))==b['cpu_ids']and os.getpriority(os.PRIO_PROCESS,0)>=15,'EXACT_PARENT_CPU_NICE')
 soft,hard=resource.getrlimit(resource.RLIMIT_AS);need(soft!=resource.RLIM_INFINITY and hard!=resource.RLIM_INFINITY and soft<=4*GIB and hard<=4*GIB,'PARENT_HARD_AS_REQUIRED')
 ref=spec['r7_process_budget_approval_ref'];raw=r.bounded_metadata_raw(ref['path'],4*MIB);need(digest(raw)==ref['sha256']and len(raw)==ref['bytes'],'ROOT_APPROVAL_REF')
 a=json.loads(raw);expected='ROOT_APPROVED_R7_EXACT_PROCESS_AS_BUDGET'if r.profile()['execution_scope']=='PRODUCTION'else'QUALIFICATION_ONLY_R7_PROCESS_AS_SHADOW'
 need(a['schema']=='SM70_R7_EXACT_PROCESS_AS_APPROVAL_V1'and a['status']==expected,'EXPLICIT_NEW_APPROVAL_REQUIRED')
 need(a['code_version_id']==r.code_manifest()['code_version_id']and a['integration_id']==spec['integration_id']and a['policy_sha256']==digest(canon(v)),'ROOT_CODE_POLICY_SCOPE')
 need(a['host']==os.uname().nodename and a['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()and a['budget']==b and a['capsule_sha256']==v['capsule_sha256'],'ROOT_HOST_CPU_CAPSULE')
 need(a['mode']==MODE and a['not_cgroup8GiB']is True and a['scientific_starts_authorized']is False,'MODE_NOT_SILENT_FALLBACK')
 if r.profile()['execution_scope']=='PRODUCTION':
  p=Path(ref['path']);need(p==Path(r.profile()['native_work_root'])/'authority'/('R7_PROCESS_'+spec['integration_id']+'.json')and not p.is_symlink()and p.stat().st_uid==0 and p.stat().st_mode&0o022==0,'ROOT_APPROVAL_NATIVE_AUTHORITY')
 return b
def parent_enter(client):
 r=client.r;root=r.library_root()/'receipts/v3_ledgers'/r._r6_spec['integration_id'];root.mkdir(parents=True,exist_ok=True)
 client._r7_lock=(root/'R7_OWN_RUNNER.lock').open('a+b');fcntl.flock(client._r7_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 client._r7_state=root/'R7_OWN_RUNNER_STATE.json'
 try:
  if client._r7_state.exists():
   old=json.loads(client._r7_state.read_bytes());need(not any(live(x)for x in old.get('actors',[])),'PREVIOUS_RUNNER_OR_CPP_STILL_LIVE')
   need(old.get('inventory_complete')is True,'PREVIOUS_UNKNOWN_INVENTORY_ROOT_RECONCILIATION')
  client._r7_state.write_bytes(canon(dict(status='STARTING',actors=[],inventory_complete=True,run_id=client.run_id,spawn_begun=False)))
 except BaseException:
  fcntl.flock(client._r7_lock,fcntl.LOCK_UN);client._r7_lock.close();del client._r7_lock;raise

def parent_started(client):
 client._r7_state.write_bytes(canon(dict(status='RUNNER_EXEC_CHAIN_STARTED',actors=[dict(pid=client.p.pid,start_ticks=client.ticks)],inventory_complete=False,run_id=client.run_id,spawn_begun=True)))
def parent_update(client,audit):
 need(ticks(client.p.pid)==client.ticks and str(Path('/proc/'+str(client.p.pid)+'/exe').resolve())=='/usr/bin/python3.10','EXEC_CHAIN_CLOSED_PYTHON_IDENTITY')
 argv=Path('/proc/'+str(client.p.pid)+'/cmdline').read_bytes().split(b'\0');argv=[x.decode()for x in argv if x]
 need(argv==['/usr/bin/python3','-I','-S','-B',str(client.r.PACKAGE/'consumer_runner_r6.py')],'FIXED_PRLIMIT_TO_PYTHON_TO_RUNNER')
 need(resource.prlimit(client.p.pid,resource.RLIMIT_AS)==(3*GIB,3*GIB),'RUNNER_HARD_AS')
 need(audit['mode']==MODE and len(audit['actors'])==10,'ALL10_ACTUAL_BUDGET_AUDIT')
 client._r7_actual_actors=audit['actors']
 actors=[dict(pid=client.p.pid,start_ticks=client.ticks)]+client._r7_actual_actors
 client._r7_state.write_bytes(canon(dict(status='READY',actors=actors,inventory_complete=True,run_id=client.run_id,audit=audit)))
def parent_exit(client):
 if not hasattr(client,'_r7_lock'):return
 actors=[dict(pid=client.p.pid,start_ticks=client.ticks)]if hasattr(client,'p')else[]
 actors+=getattr(client,'_r7_actual_actors',getattr(client,'owned_progress',[]))
 complete=hasattr(client,'owned')or getattr(client,'_r7_failure_inventory_complete',False)or not hasattr(client,'p')
 client._r7_state.write_bytes(canon(dict(status='CLOSED'if(client.dir/'CLOSED.json').exists()else'FAILED_NOT_DUAL_PASS',actors=actors,inventory_complete=complete,run_id=client.run_id,matching_live=[x for x in actors if live(x)])))
 fcntl.flock(client._r7_lock,fcntl.LOCK_UN);client._r7_lock.close();del client._r7_lock
class FixedELFPopen:
 def __init__(self,A,capsule,emit,child_cap=CHILD):
  need(type(child_cap)is int and 0<child_cap<=CHILD,'CHILD_CAP_NO_EXPANSION')
  self.A=A;self.root=Path(capsule).resolve();self.emit=emit;self.cap=child_cap;self.original=subprocess.Popen;self.records=[];self.objects=[];self.aux=[];self.serial=threading.Lock();self.constructing=False
  c=json.loads((self.root.parent/'CONSUMER_CAPSULE.json').read_bytes());self.pins=c['files']
  self.sequence=[]
  for profile,cfg in PAIRS:self.sequence += [[str(self.root/profile/'record_frontend')],[str(self.root/profile/'decoder_frontend'),str(self.root/cfg/'decoder_reachable.config')]]
 def __call__(self,args,*pos,**kw):
  with self.serial:
   need(not self.constructing and len(self.records)<10,'SERIAL_AT_MOST10');self.constructing=True
   try:
    expected=self.sequence[len(self.records)];need(type(args)is list and args==expected and not pos and not kw.get('shell',False)and kw.get('executable')is None,'FIXED_ELF_EXACT_ARGV_ONLY')
    path=Path(args[0]);rel=str(path.relative_to(self.root));raw=path.read_bytes();need(not path.is_symlink()and len(raw)==self.pins[rel]['bytes']and digest(raw)==self.pins[rel]['sha256'],'ELF_PIN')
    old=kw.pop('preexec_fn',None);need(old is None or old is self.A.cpu_only_child_limits,'NO_UNKNOWN_PREEXEC')
    def limits():
     if old is not None:old()
     soft,hard=resource.getrlimit(resource.RLIMIT_AS);cap=min(self.cap,soft if soft!=resource.RLIM_INFINITY else self.cap,hard if hard!=resource.RLIM_INFINITY else self.cap)
     resource.setrlimit(resource.RLIMIT_AS,(cap,cap));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    p=self.original(args,**dict(kw,preexec_fn=limits));self.objects.append(p)
    row=dict(pid=p.pid,start_ticks=ticks(p.pid),argv=args,ELF_sha256=digest(raw),requested_cap_bytes=self.cap)
    self.records.append(row);self.emit(dict(status='R7_CHILD_PROGRESS',owned=row))
    before=ticks(p.pid);lim=resource.prlimit(p.pid,resource.RLIMIT_AS);need(before==ticks(p.pid)==row['start_ticks']and lim==(self.cap,self.cap),'ACTUAL_CHILD_HARD_AS')
    need(live(row),'CHILD_RESOURCE_START_FAILURE');row['observed_RLIMIT_AS']=list(lim);return p
   finally:self.constructing=False
 def aux_warm(self,s):
  s.configure_headers({}) # metadata-only constructor handshake; no record or object.
  s.reset();s.current_header_context=None
  observed={};deadline=time.monotonic()+5
  while True:
   found=[];front=[s.p.pid,s.p2.pid]
   while front:
    parent=front.pop()
    try:children=Path('/proc/'+str(parent)+'/task/'+str(parent)+'/children').read_text().split()
    except FileNotFoundError:children=[]
    for value in children:
     pid=int(value)
     try:
      f=Path('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split();row=dict(pid=pid,start_ticks=f[19],parent=parent,state=f[0])
      if f[0]not in ['Z','X']:
       exe=str(Path('/proc/'+str(pid)+'/exe').resolve());need(exe in ['/usr/bin/dash','/usr/bin/cat','/bin/dash','/bin/cat'],'UNKNOWN_CPP_DESCENDANT')
       need(resource.prlimit(pid,resource.RLIMIT_AS)[1]<=self.cap,'AUX_INHERITED_AS');row.update(exe=exe,AS_hard=resource.prlimit(pid,resource.RLIMIT_AS)[1]);found.append(row);front.append(pid)
      observed[(pid,f[19])]=row
     except(FileNotFoundError,ProcessLookupError):pass
   need(len(observed)<=2,'AT_MOST_SHELL_CAT')
   if not found:break
   need(time.monotonic()<deadline,'AUX_STILL_LIVE_RESOURCE_HOLD');time.sleep(.01)
  need(s.profile=='EP'or not observed,'DTC_TRACEZ_SENTINEL_NO_AUX')
  self.aux.append(dict(profile=s.profile,configuration_profile=s.configuration_profile,zero_header_handshake_metadata_only=True,real_object_headers_still_required=True,observed=list(observed.values()),all_observed_aux_terminal=True));self.emit(dict(status='R7_AUX_PROGRESS',audit=self.aux[-1]))
 def audit(self):
  need(len(self.records)==10 and len(self.aux)==5,'EXACT10_CPP_5_WARMUPS')
  for row in self.records:need(live(row)and resource.prlimit(row['pid'],resource.RLIMIT_AS)==(self.cap,self.cap),'READY_ACTORS_LIVE_HARD_AS')
  return dict(mode=MODE,actors=self.records,aux=self.aux,CPP10_hard_AS_bytes=self.cap,steady_core_VM_bytes=11*GIB-256*MIB,one_fork_with9_CPP_conservative_VM_bytes=4*GIB+3*GIB+9*CHILD+3*GIB,conservative_with2_aux_VM_bytes=4*GIB+3*GIB+9*CHILD+3*GIB+2*CHILD,declared_VM_bound=16*GIB,not_physical_cgroup_bound=True,serialized_CPP_construction=True)
 def cleanup(self):
  for p,row in zip(self.objects,self.records):
   try:
    if p.stdin:p.stdin.close()
    p.wait(timeout=2)
   except Exception:
    try:
     fd=os.pidfd_open(p.pid);need(ticks(p.pid)==row['start_ticks'],'OWN_PID_IDENTITY')
     try:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
     finally:os.close(fd)
     p.wait(timeout=2)
    except(ProcessLookupError,FileNotFoundError):pass
  return dict(actors=self.records,inventory_complete=(len(self.aux)==5 or not any(x['argv'][0].endswith('/EP/decoder_frontend')for x in self.records)),all_created_CPP_terminal=all(not live(x)for x in self.records))
