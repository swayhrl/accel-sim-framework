"""Narrow own-child exit race handling; no broad psutil exception suppression."""
from pathlib import Path
import os
class OwnLifecycle:
 def __init__(self,ps,root):
  self.ps=ps;self.root=root;self.worker=None;self.identities={root:ps.Process(root).create_time()};self.gpu_identities={}
 def bind_worker(self,pid):
  self.worker=pid;self.identities[pid]=self.ps.Process(pid).create_time()
 def healthy(self,pid):
  p=self.ps.Process(pid)
  return p.create_time()==self.identities[pid] and p.is_running() and p.status() not in ('zombie','dead')
 def rss(self,phase):
  ps=self.ps;gaps=[];censored=[];observed=[];live={self.root};rss=0
  try:processes=[ps.Process(self.root)]+ps.Process(self.root).children(recursive=True)
  except Exception as e:return live,0,['OWN_TREE:'+type(e).__name__],[],[]
  enumerated={p.pid for p in processes}
  for p in processes:
   pid=p.pid
   try:
    birth=p.create_time() # children() binds psutil Process creation identity during valid own enumeration.
    if pid in self.identities and self.identities[pid]!=birth:
     gaps.append('PID_REUSE_OR_IDENTITY_CONFLICT:'+str(pid));continue
    self.identities[pid]=birth
    try:
     current=ps.Process(pid)
     if current.create_time()!=birth:
      gaps.append('PID_REUSE_BEFORE_RSS:'+str(pid));continue
     value=p.memory_info().rss
    except ps.NoSuchProcess:
     # Only this precise exception is eligible, and only a current enumerated descendant.
     absent1=not ps.pid_exists(pid);absent2=False
     try:ps.Process(pid).create_time()
     except ps.NoSuchProcess:absent2=True
     except Exception as e:gaps.append('EXIT_RECHECK:'+str(pid)+':'+type(e).__name__)
     if pid in (self.root,self.worker) or pid not in enumerated or not absent1 or not absent2:
      gaps.append('UNCONFIRMED_OWN_EXIT:'+str(pid));continue
     censored.append(dict(pid=pid,creation_time=birth,enumerated_current_own_tree=True,
       classification='PENDING_OWN_EXITED_CHILD_RSS_RACE',rss_bytes=None,censored=True,
       disappearance_rechecked=True,original_process_not_reobserved=True))
     continue
    # Recheck birth after reading memory; an actually observed RSS is retained even if it then exits.
    try:
     if ps.Process(pid).create_time()!=birth:gaps.append('PID_REUSE_AFTER_RSS:'+str(pid));continue
    except ps.NoSuchProcess:
     if ps.pid_exists(pid):gaps.append('PID_IDENTITY_UNCERTAIN_AFTER_RSS:'+str(pid))
    rss+=value;live.add(pid);observed.append(dict(pid=pid,creation_time=birth,rss_bytes=value))
   except Exception as e:gaps.append('RSS_PID_'+str(pid)+':'+type(e).__name__)
  try:
   if not self.healthy(self.root):gaps.append('ROOT_NOT_HEALTHY')
   if phase=='WORKER' and (self.worker is None or not self.healthy(self.worker)):gaps.append('WORKER_NOT_HEALTHY')
   if censored and (self.worker is None or not self.healthy(self.worker)):gaps.append('EXIT_RACE_WITHOUT_HEALTHY_WORKER')
  except Exception as e:gaps.append('OWNER_HEALTH:'+type(e).__name__)
  return live,rss,gaps,censored,observed
 def gpu_identity_checks(self,row):
  for g in row['gpu_processes']:
   pid=g['pid']
   if pid is None:continue
   try:
    birth=self.ps.Process(pid).create_time()
    if pid in self.gpu_identities and self.gpu_identities[pid]!=birth:
     row['monitor_gaps'].append('GPU_PID_IDENTITY_CHANGED:'+str(pid))
    self.gpu_identities[pid]=birth
    if pid in row['known_own_pids']:
     if self.identities.get(pid)!=birth:row['monitor_gaps'].append('OWN_GPU_IDENTITY_CONFLICT:'+str(pid))
     if self.worker is not None and pid!=self.worker:row['monitor_gaps'].append('GPU_OWNER_NOT_SINGLE_WORKER:'+str(pid))
   except Exception as e:row['monitor_gaps'].append('GPU_IDENTITY_'+str(pid)+':'+type(e).__name__)
def finalize_races(row,gate_verified,runtime_policy_checked):
 candidates=row.get('rss_censored_observations',[])
 if not candidates:return
 if not gate_verified or not runtime_policy_checked or row['monitor_gaps'] or row['unknown_gpu_pids'] or row['invalid_pid_rows'] or row.get('unqualified_external_gpu_pids'):
  raise RuntimeError('Exit race cannot be accepted with independent resource/gate observation gap')
 for x in candidates:x['classification']='OWN_EXITED_CHILD_RSS_RACE'
 row['rss_observation_scope']='Sampled observed live RSS subtotal; exited-child RSS censored, never zero; not complete tree peak.'

class SessionMemory:
 """Read-only own SSH-session charged-memory high-water, supplementary to sampled RSS."""
 def __init__(self,root):
  import psutil
  self.root=root;self.ps=psutil
  self.relative=Path('/proc/self/cgroup').read_text().split('::',1)[1].strip()
  self.path=Path('/sys/fs/cgroup')/self.relative.lstrip('/')
  st=self.path.stat();self.inode=(st.st_dev,st.st_ino)
  if not self.path.name.startswith('session-') or not self.path.name.endswith('.scope') or st.st_uid!=0 or os.access(self.path,os.W_OK):
   raise RuntimeError('No root-owned isolated read-only SSH session scope')
  ancestors={root}|{p.pid for p in psutil.Process(root).parents()}
  initial={int(v) for v in (self.path/'cgroup.procs').read_text().split()}
  if not initial.issubset(ancestors):raise RuntimeError('Unrelated initial member in session memory scope')
  self.initial=sorted(initial);self.read(None)
 def read(self,worker):
  st=self.path.stat()
  if (st.st_dev,st.st_ino)!=self.inode:raise RuntimeError('Session cgroup identity changed')
  for pid in [self.root]+([worker] if worker is not None and self.ps.pid_exists(worker) else []):
   if Path('/proc',str(pid),'cgroup').read_text().split('::',1)[1].strip()!=self.relative:raise RuntimeError('Owner left session memory scope')
  return dict(path=str(self.path),device=st.st_dev,inode=st.st_ino,initial_members=self.initial,
    current_bytes=int((self.path/'memory.current').read_text()),kernel_charged_peak_bytes=int((self.path/'memory.peak').read_text()),
    configured_memory_max=(self.path/'memory.max').read_text().strip(),
    current_member_pids=[int(v) for v in (self.path/'cgroup.procs').read_text().split()],
    scope='Root-owned SSH session with only supervisor/ancestors initially; descendants inherit. Charged-memory peak retains exited tasks but is not summed RSS. No writable hard limit.')
