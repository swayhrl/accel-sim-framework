"""AG5 CPU-only owned-process guard; no simulator invocation capability.

No CLI. PTRACE_TRACEME only, never attach. A pre-exec seccomp TRACE filter
stops mapping-changing syscalls for complete before/after maps; fork/exec/
clone/exit events keep every owned descendant in scope. Unknown maps reject.
This repair publishes no performance dispatcher or simulator start path.
"""
import ctypes,os,signal,time,json,platform
from pathlib import Path
from mapping_roles import Sequence,validate_manifest,verify_file,require,Reject,sha
from common import write,now
import oom_watchdog
from ownership import Ownership,identity,CONFIRM_SECONDS

ROOT=Path('/workspace/dtc-lane-ag5-retired-pid-repair-174-v1')
MAP_SYSCALLS=(9,10,11,25,30,67,329) # mmap,mprotect,munmap,mremap,shmat,shmdt,pkey_mprotect
OPTIONS=1|2|4|8|16|64|128|0x100000
class Regs(ctypes.Structure):
 _fields_=[(n,ctypes.c_ulonglong) for n in 'r15 r14 r13 r12 rbp rbx r11 r10 r9 r8 rax rcx rdx rsi rdi orig_rax rip cs eflags rsp ss fs_base gs_base ds es fs gs'.split()]
class Filter(ctypes.Structure):
 _fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint)]
class Program(ctypes.Structure):
 _fields_=[('length',ctypes.c_ushort),('filter',ctypes.POINTER(Filter))]

def filter_program():
 rows=[(0x20,0,0,4),(0x15,1,0,0xc000003e),(0x06,0,0,0x80000000),(0x20,0,0,0)]
 for nr in MAP_SYSCALLS:rows.extend([(0x15,0,1,nr),(0x06,0,0,0x7ff00000)])
 rows.append((0x06,0,0,0x7fff0000))
 array=(Filter*len(rows))(*(Filter(*r) for r in rows))
 return array,Program(len(rows),array)

def run_guarded(argv,env,manifests,destination,purpose,timeout,capability=None,observer=None):
 require(platform.machine()=='x86_64','UNQUALIFIED_ARCHITECTURE')
 target=str(Path(argv[0]).resolve());require(target in manifests,'TARGET_NOT_REGISTERED')
 require(purpose=='CPU_FIXTURE','CPU_ONLY_NO_SIMULATION_DISPATCH')
 require(target==str(ROOT/'build/ag5-cpu-authority'),'CPU_TARGET_NOT_FIXED_FIXTURE')
 registry={path:validate_manifest(m) for path,m in manifests.items()}
 dest=Path(destination);dest.mkdir(parents=True,exist_ok=False)
 for m in manifests.values():require(m['frozen_monotonic_ns']<time.monotonic_ns(),'MANIFEST_NOT_PRE_FORK')
 write(dest/'START.json',dict(utc=now(),purpose=purpose,argv=argv,environment=env,manifests_sha={k:__import__('hashlib').sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for k,v in manifests.items()},fork_before=False),exclusive=True)
 c=ctypes.CDLL(None,use_errno=True);c.ptrace.restype=ctypes.c_long
 def ptr(request,pid,data=0):
  ctypes.set_errno(0);r=c.ptrace(request,pid,ctypes.c_void_p(0),data)
  if r==-1 and ctypes.get_errno():raise OSError(ctypes.get_errno(),'owned ptrace '+str(request))
  return r
 array,program=filter_program()
 out=os.open(dest/'stdout',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);err=os.open(dest/'stderr',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 oom_baseline={k:int(v) for k,v in (line.split() for line in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())}
 eventlog=(dest/'MAP_EVENTS.jsonl').open('x');mapsdir=dest/'maps';mapsdir.mkdir()
 fork_ns=time.monotonic_ns()
 try:pid=os.fork()
 except BaseException as exc:
  os.close(out);os.close(err);eventlog.close()
  terminal=dict(utc=now(),status='STOP_GUARDED_PROCESS',purpose=purpose,root_pid=None,returncode=None,forced_reason='FORK_FAILED:'+repr(exc),identity_pass=False,owned_children_live=0,simulator_starts=0,actual_fork_children=0)
  write(dest/'TERMINAL.json',terminal,exclusive=True);return terminal
 if pid==0:
  try:
   os.chdir(dest);os.dup2(out,1);os.dup2(err,2)
   if c.ptrace(0,0,None,None)==-1:os._exit(125)
   if c.prctl(38,1,0,0,0)!=0:os._exit(124) # NO_NEW_PRIVS
   if c.prctl(22,2,ctypes.byref(program),0,0)!=0:os._exit(123)
   os.execve(target,list(map(str,argv)),env)
  except BaseException:os._exit(126)
 os.close(out);os.close(err)
 alive={pid};states={};exits={};exit_instances=[];main_rc=None;forced=None;frames=0;started=time.monotonic();last_sample=started-10;last_oom=started-.25
 error=None;main_identity=False;quarantined=[];watch=None;ownership=None;inherited={};events_since_observer=0
 # Only current unreaped instances are dispatchable. Fork inheritance is copied
 # at the proven parent event, so a reaped parent cannot lend stale PID state.
 def retire(tid,rc):
  exit_instances.append(dict(pid=tid,start_ticks=ownership.confirmed[tid]['start_ticks'],returncode=rc))
  ownership.retire(tid);alive.discard(tid);states.pop(tid,None);inherited.pop(tid,None)
  quarantined[:]=[q for q in quarantined if q[0]!=tid]
 def confirm(parent,newpid,event):
  proof=ownership.confirm(parent,newpid,event);alive.add(newpid)
  parent_state=states[parent]
  inherited[newpid]=dict(parent_pid=parent,parent_start_ticks=proof['parent_start_ticks'],child_start_ticks=proof['child_start_ticks'],exe=parent_state['exe'],closed=parent_state['closed'],ever=set(parent_state['sequence'].ever),cache_disappearances=parent_state['sequence'].cache_disappearances)
  return proof
 def image(tid,exe=None):
  exe=exe or os.readlink(f'/proc/{tid}/exe');require(exe in manifests,'UNKNOWN_EXEC_IMAGE:'+exe)
  seq=Sequence(manifests[exe]);states[tid]=dict(exe=exe,start_ticks=ownership.confirmed[tid]['start_ticks'],sequence=seq,pending_exit=False,closed=False,last_paths=set(),mapping_nr=None)
  return states[tid]
 def capture(tid,stage):
  nonlocal frames,main_identity
  require(frames<250000,'MAPPING_EVIDENCE_BOUND_250000')
  st=states[tid];text=Path(f'/proc/{tid}/maps').read_text();exe=os.readlink(f'/proc/{tid}/exe')
  v=st['sequence'].observe(text,exe);paths=set(v['files']);removed=sorted(st['last_paths']-paths)
  if st['closed']:
   require({p for p,e in registry[exe].items() if e['role'].startswith('ELF_')}<=paths,'REGISTERED_ELF_DISAPPEARED_AFTER_STARTUP')
  if set(registry[exe])<=st['sequence'].ever and st['sequence'].cache_disappearances>=1 and '/etc/ld.so.cache' not in paths:
   st['closed']=True
   if tid==pid:main_identity=True
  st['last_paths']=paths
  name=f'{frames:06d}_pid{tid}.maps';(mapsdir/name).write_text(text)
  eventlog.write(json.dumps(dict(utc=now(),monotonic_ns=time.monotonic_ns(),pid=tid,exe=exe,stage=stage,mapping_syscall=st['mapping_nr'],maps=name,maps_sha256=sha(mapsdir/name),cache_present='/etc/ld.so.cache' in paths,removed_files=removed,startup_closed=st['closed'],validated_files=sorted(paths)))+'\n');eventlog.flush();frames+=1
 def resume(tid,syscall_exit=False,signum=0):
  ownership.same(tid)
  require(states[tid]['start_ticks']==ownership.confirmed[tid]['start_ticks'],'STALE_IMAGE_GENERATION')
  ptr(24 if syscall_exit else 7,tid,signum)
 def periodic():
  nonlocal last_oom,last_sample
  instant=time.monotonic()
  if observer and instant-last_oom>=.25:
   reason=observer(pid,instant-last_sample>=10,ownership)
   last_oom=instant
   if instant-last_sample>=10:last_sample=instant
   if reason:raise Reject(reason)
 try:
  write(dest/'FORK_CHILD.json',dict(pid=pid,fork_monotonic_ns=fork_ns,requested_executable=target,purpose=purpose,real_simulator=purpose=='SIMULATION'),exclusive=True)
  child,status=os.waitpid(pid,0)
  if os.WIFEXITED(status) or os.WIFSIGNALED(status):
   alive.remove(pid);main_rc=os.waitstatus_to_exitcode(status);exits[pid]=main_rc
   raise Reject('INITIAL_EXEC_OR_SECCOMP_SETUP_FAILED:'+str(main_rc))
  require(os.WIFSTOPPED(status) and os.WSTOPSIG(status)==signal.SIGTRAP,'INITIAL_EXEC_TRAP_REQUIRED')
  ticks=int(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19])
  write(dest/'CHILD.json',dict(pid=pid,start_ticks=ticks,fork_monotonic_ns=fork_ns,purpose=purpose,actual_fork=True,real_simulator=purpose=='SIMULATION'),exclusive=True)
  ownership=Ownership(pid)
  watch=oom_watchdog.start(pid,dest/'OOM_MONITOR.jsonl',baseline=oom_baseline)
  ptr(0x4200,pid,OPTIONS);image(pid);capture(pid,'INITIAL_EXEC');resume(pid)
  while alive:
   if watch[2]['reason']:raise Reject(watch[2]['reason'])
   instant=time.monotonic()
   if instant-started>timeout:raise Reject('TIMEOUT_'+str(timeout))
   ownership.check_deadlines()
   # Finite drain batch bounds observer latency without forgetting a consumed event.
   if events_since_observer>=256:
    periodic();events_since_observer=0
   ready=next((i for i,(qpid,_) in enumerate(quarantined) if qpid in ownership.confirmed),None)
   if ready is None:child,status=os.waitpid(-1,os.WNOHANG|0x40000000)
   else:child,status=quarantined.pop(ready)
   if child==0:
    periodic();events_since_observer=0;time.sleep(.001);continue
   events_since_observer+=1
   if child not in ownership.confirmed:
    require(os.WIFSTOPPED(status),'UNCONFIRMED_NONSTOP_WAIT_STATUS')
    ownership.quarantine(child,'ACTUAL_WAIT_STOP_BEFORE_PARENT_EVENT')
    quarantined.append((child,status))
    eventlog.write(json.dumps(dict(utc=now(),quarantined_wait_pid=child,status=status,reason='kernel child stop may precede parent fork event; no resume/signal before ownership confirmation'))+'\n');eventlog.flush()
    continue
   if os.WIFEXITED(status) or os.WIFSIGNALED(status):
    rc=os.waitstatus_to_exitcode(status);exits[child]=rc
    st=states.get(child)
    retire(child,rc)
    if child==pid:main_rc=rc
    require(rc==0,'NONZERO_OWNED_PROCESS_EXIT:'+str(child)+':'+str(rc))
    require(st and st['closed'],'PROCESS_EXIT_WITHOUT_EARLY_IDENTITY_CLOSURE')
    continue
   require(os.WIFSTOPPED(status),'UNKNOWN_WAIT_STATUS')
   ownership.same(child)
   sig=os.WSTOPSIG(status);event=status>>16
   if child not in states:
    # New fork/clone begins with inherited confirmed image; an exec creates its own sequence.
    exe=os.readlink(f'/proc/{child}/exe');image(child,exe)
    parent_state=inherited.pop(child,None)
    require(parent_state and parent_state['exe']==exe,'INHERITED_IMAGE_PARENT_MISMATCH')
    require(parent_state['child_start_ticks']==ownership.confirmed[child]['start_ticks'],'INHERITED_IMAGE_GENERATION_MISMATCH')
    states[child]['closed']=parent_state['closed'];states[child]['sequence'].ever=set(parent_state['ever']);states[child]['sequence'].cache_disappearances=parent_state['cache_disappearances']
    ptr(0x4200,child,OPTIONS);capture(child,'INHERITED_FORK_CLONE_STOP')
   st=states[child]
   require(st['start_ticks']==ownership.confirmed[child]['start_ticks'],'STALE_IMAGE_GENERATION')
   if sig==(signal.SIGTRAP|0x80):
    require(st['pending_exit'],'UNEXPECTED_SYSCALL_STOP');capture(child,'MAPPING_SYSCALL_EXIT');st['pending_exit']=False;resume(child)
   elif sig==signal.SIGTRAP and event==7: # seccomp entry
    regs=Regs();ptr(12,child,ctypes.byref(regs));nr=int(regs.orig_rax);require(nr in MAP_SYSCALLS,'SECCOMP_RULE_MISMATCH')
    st['mapping_nr']=nr;capture(child,'MAPPING_SYSCALL_ENTRY');st['pending_exit']=True;resume(child,True)
   elif sig==signal.SIGTRAP and event in (1,2,3):
    new=ctypes.c_ulonglong();ptr(0x4201,child,ctypes.byref(new));newpid=int(new.value);proof=confirm(child,newpid,event)
    eventlog.write(json.dumps(dict(utc=now(),**proof))+'\n');eventlog.flush();resume(child)
   elif sig==signal.SIGTRAP and event==4:
    image(child);capture(child,'EXEC_EVENT');resume(child)
   elif sig==signal.SIGTRAP and event==6:
    capture(child,'PRE_EXIT_EVENT');require(st['closed'],'EARLY_IDENTITY_NOT_CLOSED_BEFORE_EXIT');resume(child)
   elif sig==signal.SIGSTOP:resume(child)
   else:
    eventlog.write(json.dumps(dict(pid=child,signal_delivery=sig,utc=now()))+'\n');eventlog.flush();resume(child,signum=sig)
  require(not quarantined,'UNCONFIRMED_FORK_OWNERSHIP')
  require(main_rc==0 and main_identity,'MAIN_EXIT_OR_IDENTITY_FAILED')
  for m in manifests.values():
   for entry in m['files']:verify_file(entry)
 except BaseException as exc:
  error=repr(exc);forced=str(exc)
 finally:
  # Drain parent-event proof even on STOP, before signalling any new PID.
  # Every signal targets an unreaped, exact, event-confirmed process instance.
  cleanup_deadline=time.monotonic()+CONFIRM_SECONDS
  signalled=set()
  while alive or quarantined or (ownership and ownership.pending):
   try:child,status=os.waitpid(-1,os.WNOHANG|0x40000000)
   except ChildProcessError:
    alive.clear();break
   if child==0:
    for current in list(alive):
     instance=(current,ownership.confirmed[current]['start_ticks']) if ownership and current in ownership.confirmed else None
     if instance in signalled:continue
     try:
      require(ownership is not None,'CLEANUP_ROOT_IDENTITY_UNCONFIRMED')
      ownership.same(current)
      os.kill(current,signal.SIGKILL);signalled.add(instance)
     except ProcessLookupError:pass
     except Reject as exc:
      error=error or str(exc);forced=forced or str(exc)
    if time.monotonic()>cleanup_deadline:
     error=error or 'CLEANUP_PENDING_PARENT_EVENT_UNRESOLVED';forced=forced or error;break
    time.sleep(.001);continue
   if os.WIFSTOPPED(status):
    event=status>>16
    if child in ownership.confirmed:ownership.same(child)
    if child in ownership.confirmed and event in (1,2,3):
     new=ctypes.c_ulonglong();ptr(0x4201,child,ctypes.byref(new));newpid=int(new.value)
     proof=confirm(child,newpid,event)
     quarantined=[q for q in quarantined if q[0]!=newpid]
     eventlog.write(json.dumps(dict(utc=now(),stage='STOP_CLEANUP_PARENT_EVENT',**proof))+'\n');eventlog.flush()
    if child in ownership.confirmed:
     if ownership:ownership.same(child)
     ptr(7,child,signal.SIGKILL)
    else:
     ownership.quarantine(child,'CLEANUP_WAIT_STOP');quarantined.append((child,status))
   elif os.WIFEXITED(status) or os.WIFSIGNALED(status):
    require(ownership is not None and child in ownership.confirmed,'CLEANUP_UNCONFIRMED_EXIT')
    exits[child]=os.waitstatus_to_exitcode(status);retire(child,exits[child])
  if watch is not None:
   oom_watchdog.finish(watch)
   if watch[2]['reason']:
    error=error or watch[2]['reason'];forced=watch[2]['reason']
  eventlog.close()
  terminal=dict(utc=now(),status='PASS_GUARDED_NATURAL_EXIT0' if error is None else 'STOP_GUARDED_PROCESS',purpose=purpose,root_pid=pid,returncode=main_rc,forced_reason=forced,exception=error,identity_pass=main_identity and error is None,owned_process_exits=exits,owned_process_exit_instances=exit_instances,owned_children_live=len(alive),ownership=ownership.snapshot() if ownership else None,unconfirmed_wait_pids=[v[0] for v in quarantined],snapshots=frames,simulator_starts=0,wall_seconds_nonperformance=time.monotonic()-started)
  write(dest/'TERMINAL.json',terminal,exclusive=True)
 return terminal
