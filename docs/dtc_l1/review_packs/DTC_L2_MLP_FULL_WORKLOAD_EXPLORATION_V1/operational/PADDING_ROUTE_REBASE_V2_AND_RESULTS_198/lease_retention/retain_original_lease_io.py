"""Retain existing owner IO objects only; importing has no side effects.
No open, dup, flock, close, signal, registry, lease or frozen-source mutation.
Existing-owner main-thread pending callback is the only production entry.
"""
import gc,hashlib,io,json,os,pathlib,sys,threading
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MARKER='DTC_L2_MLP_ORIGINAL_LEASE_IO_RETENTION_V1'
def ticks(pid):return int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def validate_object(obj,fd,path,pid):
 assert isinstance(obj,io.BufferedIOBase) and not obj.closed,'Original live buffered open object required'
 assert obj.fileno()==fd,'Original FD mismatch'
 assert P(os.fspath(obj.name))==P(path),'Original IO name mismatch'
 assert os.readlink('/proc/self/fd/'+str(fd))==str(path),'FD target mismatch'
 st=os.fstat(fd);target=os.stat(path);assert (st.st_dev,st.st_ino)==(target.st_dev,target.st_ino)
 rows=(P('/proc/self/fdinfo')/str(fd)).read_text().splitlines()
 locks=[line.split()for line in rows if line.startswith('lock:')]
 assert any('FLOCK'in row and 'WRITE'in row and str(pid)in row for row in locks),'Existing owner FLOCK missing'
 return dict(fd=fd,path=str(path),object_id=id(obj),object_type=type(obj).__name__,device=st.st_dev,inode=st.st_ino)
def retain_objects(objects,targets,expected_pid,expected_ticks,marker=MARKER,namespace=None):
 assert threading.current_thread()is threading.main_thread(),'Main-thread pending callback required'
 assert os.getpid()==expected_pid and ticks(os.getpid())==expected_ticks,'Wrong original owner generation'
 assert set(objects)==set(targets) and len(targets)==2
 ns=vars(sys.modules['__main__'])if namespace is None else namespace
 proof=[validate_object(objects[fd],fd,path,expected_pid)for fd,path in sorted(targets.items())]
 if marker in ns:
  old=ns[marker];assert old['owner_pid']==expected_pid and old['owner_start_ticks']==expected_ticks
  assert all(old['objects'][fd]is objects[fd]for fd in targets),'Marker differs from original IO objects'
  return dict(old['proof'],idempotent=True)
 result=dict(status='ORIGINAL_OWNER_LEASE_IO_STRONGLY_RETAINED',owner_pid=expected_pid,owner_start_ticks=expected_ticks,objects=proof,no_open_dup_flock_close_or_signal=True)
 ns[marker]=dict(objects=dict(objects),owner_pid=expected_pid,owner_start_ticks=expected_ticks,proof=result)
 return result
def discover_original_objects(source_path,targets):
 frames=[];frame=sys._current_frames()[threading.main_thread().ident]
 while frame is not None:
  if frame.f_code.co_name=='main'and P(frame.f_code.co_filename)==P(source_path):frames.append(frame)
  frame=frame.f_back
 assert len(frames)<=1,'Ambiguous original main frame'
 if frames:
  local=frames[0].f_locals;objects={3:local['owner'],4:local['held']}
  assert set(objects)==set(targets)
  return objects,'ORIGINAL_R20_MAIN_LOCALS'
 # main may have returned into threading._shutdown. Never manufacture a new
 # file object: use only still-live original buffered IO wrappers tracked by GC.
 found={fd:[]for fd in targets}
 for obj in gc.get_objects():
  if not isinstance(obj,io.BufferedIOBase):continue
  try:
   if not obj.closed and obj.fileno()in found and P(os.fspath(obj.name))==P(targets[obj.fileno()]):found[obj.fileno()].append(obj)
  except (OSError,ValueError,TypeError):pass
 assert all(len(v)==1 for v in found.values()),'Original IO object gone or ambiguous; cannot reacquire lease'
 return {fd:v[0]for fd,v in found.items()},'GC_ORIGINAL_BUFFERED_IO_ONLY'
def apply_in_owner():
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes())
 assert os.getpid()==plan['parent_pid']==1498278 and ticks(os.getpid())==plan['parent_start_ticks']==977758783
 source=P(plan['parent_controller_path']);assert sha(source)==plan['parent_controller_sha256']
 targets={3:P('/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock'),4:P('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock')}
 objects,discovery=discover_original_objects(source,targets)
 proof=retain_objects(objects,targets,plan['parent_pid'],plan['parent_start_ticks'])
 return dict(proof,discovery=discovery,original_controller_sha256=plan['parent_controller_sha256'])
