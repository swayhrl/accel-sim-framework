#!/usr/bin/env python3
"""Fixed readonly CPU adapter runner. No shell or arbitrary command interface."""
import pathlib,sys,os,json,time,resource,fcntl,runpy,traceback,signal
sys.dont_write_bytecode=True
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import core as c
def boundary(attempt):
 std=[pathlib.Path('/usr/lib/python3.10'),pathlib.Path('/usr/local/lib/python3.10'),pathlib.Path(sys.base_prefix)/'lib/python3.10']
 def inside(path,roots):
  if isinstance(path,int):return True
  p=pathlib.Path(os.fsdecode(path)).absolute()
  if '..'in p.parts:return False
  p=p.resolve(strict=False)
  return any(p==r.resolve(strict=False) or r.resolve(strict=False) in p.parents for r in roots)
 def hook(event,args):
  if event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.__new__','socket.connect','ctypes.dlopen']:raise RuntimeError('CPU_ONLY_FORBIDDEN '+event)
  if event=='import'and args[0].split('.')[0]in ['torch','cupy','pycuda','numba','tensorflow']:raise RuntimeError('GPU_IMPORT_FORBIDDEN')
  if event=='open':
   p,mode,flags=args;write=(isinstance(mode,str)and any(x in mode for x in 'wax+'))or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
   if write:c.need(inside(p,[attempt]),'adapter write outside attempt')
   elif not isinstance(p,int):
    text=os.fsdecode(p);c.need(inside(p,[c.N,*std])or text in ['/dev/null','/proc/sys/kernel/random/boot_id','/proc/self/stat',f'/proc/{os.getpid()}/stat'],'adapter read outside frozen/private metadata')
  elif event in ['os.mkdir','os.remove','os.rmdir','os.chmod','os.chown','os.utime']:c.need(inside(args[0],[attempt]),'adapter mutation outside attempt')
  elif event in ['os.rename','os.link','os.symlink']:c.need(inside(args[0],[attempt])and inside(args[1],[attempt]),'adapter rename outside attempt')
 sys.addaudithook(hook)
def main():
 c.need(len(sys.argv)==2,'fixed context argument required');ctxpath=c.secure_file(sys.argv[1]);ctx=c.load(ctxpath);attempt=pathlib.Path(ctx['attempt_directory'])
 c.need(ctxpath==attempt/'CONTEXT.json'and attempt.is_relative_to(c.D/'runs'),'private attempt path')
 c.need(ctx['stage']==c.STAGE and ctx['adapter_profile']=='AUTO161_READONLY_CPU_METADATA_V1','unapproved stage/profile')
 intent=c.load(attempt/'INTENT.json');c.need(intent['context_ref']==c.file_ref(ctxpath),'context drift')
 approval=c.load(c.verify_ref(ctx['approval_ref']))
 c.need(approval['status']=='APPROVED_PRIVATE_CPU_ONLY_EXACT161'and approval['scope_sha256']==ctx['scope_sha256']==c.SCOPE_SHA,'Root CPU approval required by worker')
 for name in ['core.py','worker.py','orchestrator.py','FROZEN_ADMISSIONS.json']:c.need(c.rawsha(c.D/name)==approval['pins'][name],'worker approval pin '+name)
 allowfile=c.verify_ref(ctx['allowlist_ref']);c.need(c.rawsha(allowfile)==approval['pins']['ALLOWLIST.json'],'frozen allowlist approval pin');allow=c.load(allowfile)['metadata_adapter']
 for key,field in [('adapter_id','id'),('adapter_profile','profile'),('adapter_path','path'),('adapter_source_sha256','sha256')]:c.need(ctx[key]==allow[field],'unapproved fixed adapter '+key)
 c.secure_file(ctx['adapter_path'])
 c.need(c.rawsha(ctx['adapter_path'])==ctx['adapter_source_sha256'],'adapter source changed')
 c.need(c.rawsha(__file__)==intent['runner_source_sha256'],'runner changed')
 slot=ctx['slot_id'];c.need(type(slot)is int and 0<=slot<2,'CPU slot')
 held=(c.D/f'CPU_SLOT_{slot}.lock').open('a');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
 affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity[slot%len(affinity)]});os.nice(19)
 resource.setrlimit(resource.RLIMIT_CPU,(45,46));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024**2,16*1024**2))
 start=c.identity(os.getpid());parent=c.identity(os.getppid());mono=time.monotonic_ns();wall=time.time();usage=resource.getrusage(resource.RUSAGE_SELF)
 startobj={'schema':'AUTO161_PROCESS_START_V1','attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'worker':start,'parent':parent,'slot_id':slot,'started_monotonic_ns':mono,'started_unix':wall,'adapter_source_sha256':ctx['adapter_source_sha256'],'runner_source_sha256':intent['runner_source_sha256'],'context_ref':c.file_ref(ctxpath)}
 c.save(attempt/'PROCESS_START.json',startobj,True)
 boundary(attempt);rc=0;error=None
 try:
  sys.argv=[ctx['adapter_path'],'--scope-json',ctx['scope_path'],'--row-index',str(ctx['row_index']),'--output',str(attempt/'RESULT.json'),'--context-json',str(ctxpath)]
  runpy.run_path(ctx['adapter_path'],run_name='__main__')
 except SystemExit as exc:rc=exc.code if type(exc.code)is int else 1
 except BaseException as exc:rc=1;error=repr(exc);traceback.print_exc()
 end=time.monotonic_ns();after=resource.getrusage(resource.RUSAGE_SELF)
 obj={'schema':'AUTO161_EXECUTION_V1','attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'worker':start,'parent':parent,'slot_id':slot,'started_monotonic_ns':mono,'ended_monotonic_ns':end,'started_unix':wall,'ended_unix':time.time(),'returncode':rc,'error':error,'adapter_source_sha256':ctx['adapter_source_sha256'],'runner_source_sha256':intent['runner_source_sha256'],'cpu_user_seconds':after.ru_utime-usage.ru_utime,'cpu_system_seconds':after.ru_stime-usage.ru_stime,'max_rss_kib':after.ru_maxrss,'result_ref':c.file_ref(attempt/'RESULT.json')if(attempt/'RESULT.json').exists()else None}
 c.save(attempt/'EXECUTION.json',obj,True)
 return rc
if __name__=='__main__':sys.exit(main())
