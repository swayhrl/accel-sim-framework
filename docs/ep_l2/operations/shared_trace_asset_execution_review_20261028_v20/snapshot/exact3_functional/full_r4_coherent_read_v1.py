"""Read-only coherent full-R4 observation under the existing short metadata mutex; no experiment lease."""
from pathlib import Path
import os,fcntl,signal,time,stat,hashlib,json
LOCK=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/REGISTRY_UPDATE.lock')
REG=LOCK.with_name('NATIVE_SCIENCE_REGISTRY.json')
EPOCH=LOCK.parent.parent/'CURRENT_SCIENCE_EPOCH.json'
def need(v,m):
 if not v:raise RuntimeError('FULL_R4_COHERENT_READ:'+m)
def raw(p,cap=8*2**20):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode) and a.st_size<=cap,'bounded metadata');b=os.read(fd,cap+1);z=os.fstat(fd);q=p.stat()
  sig=lambda t:(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
  need(sig(a)==sig(z)==sig(q) and len(b)==a.st_size,'same FD bytes');return b
 finally:os.close(fd)
def collect(O,policy):
 need(not LOCK.is_symlink(),'exact existing metadata mutex');fd=os.open(LOCK,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);st=os.fstat(fd)
 need(stat.S_ISREG(st.st_mode) and st.st_size==0,'existing zero-byte metadata mutex')
 started=time.monotonic();locked=False;old_handler=signal.getsignal(signal.SIGALRM);old_timer=signal.getitimer(signal.ITIMER_REAL)
 need(old_timer[0]==0,'no nested alarm');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('FULL_R4_SHORT_READ_8S_BOUND')))
 try:
  while True:
   need(time.monotonic()-started<3,'short metadata lock acquisition3s bound')
   try:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB);locked=True;break
   except BlockingIOError:time.sleep(.02)
  held_start=time.monotonic();signal.setitimer(signal.ITIMER_REAL,8)
  before=raw(REG);epoch=raw(EPOCH);e=json.loads(epoch)
  need(hashlib.sha256(before).hexdigest()==e['native_registry_sha256'],'coherent original epoch/registry ABI')
  old=O.collect(policy) # Original source, checks, identity/progress/profile proofs and full planning unchanged.
  after=raw(REG);need(after==before and raw(EPOCH)==epoch,'cooperating writer ABI preserves coherent snapshot')
  need(old['foreign_observation']['registry_ref']['sha256']==hashlib.sha256(before).hexdigest(),'actual observer used same registry')
  held_seconds=time.monotonic()-held_start
 finally:
  signal.setitimer(signal.ITIMER_REAL,0)
  if locked:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd);signal.signal(signal.SIGALRM,old_handler)
 # Strict fresh kernel memory snapshot and own9 evaluation happen after releasing the control mutex.
 memory=O.mod(policy['V9_memory_module_ref']['path'],'original_V9_after_coherent_read',policy['V9_memory_module_ref']['sha256'])
 fresh=memory.collect();old['original_kernel_snapshot_under_short_read_lock']=old['kernel_snapshot'];old['kernel_snapshot']=fresh
 old['coherent_short_read_lock']=dict(path=str(LOCK),mode='LOCK_SH',acquire_seconds=held_start-started,held_seconds=held_seconds,held_seconds_max=8,registry_raw_sha256=hashlib.sha256(before).hexdigest(),registry_bytes=len(before),epoch_raw_sha256=hashlib.sha256(epoch).hexdigest(),same_registry_start_end=True,lock_released_before_fresh_kernel_and_exact9_evaluate=True,foreign_experiment_or_long_qualification_lock_acquired=False,registry_or_epoch_modified=False,original_full_R4_observer_unmodified=True)
 return old
