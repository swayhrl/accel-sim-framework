#!/usr/bin/env python3
"""Synthetic fixture worker only; never imports production orchestrator or GPU libraries."""
import os,sys,pathlib,json,time,resource,runpy,hashlib
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,x):pathlib.Path(p).write_text(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n')
def ref(p):
 p=pathlib.Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def identity(pid):
 s=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
 return {'pid':pid,'start_ticks':int(s[19]),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'parent_pid':int(s[1]),'state':s[0]}
ctx=read(sys.argv[1]);d=pathlib.Path(ctx['attempt_directory']);intent=read(d/'INTENT.json')
affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity[0]});os.nice(15)
resource.setrlimit(resource.RLIMIT_CPU,(5,6));resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
me=identity(os.getpid());parent=identity(os.getppid());mono=time.monotonic_ns();wall=time.time();usage=resource.getrusage(resource.RUSAGE_SELF)
start={'schema':'AUTO161_PROCESS_START_V1','attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'worker':me,'parent':parent,'slot_id':ctx['slot_id'],'started_monotonic_ns':mono,'started_unix':wall,'adapter_source_sha256':ctx['adapter_source_sha256'],'runner_source_sha256':intent['runner_source_sha256'],'context_ref':ref(d/'CONTEXT.json')}
write(d/'PROCESS_START.json',start)
sys.argv=[ctx['adapter_path'],str(d/'CONTEXT.json')];runpy.run_path(ctx['adapter_path'],run_name='__main__')
after=resource.getrusage(resource.RUSAGE_SELF)
exe={'schema':'AUTO161_EXECUTION_V1','attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'worker':me,'parent':parent,'slot_id':ctx['slot_id'],'started_monotonic_ns':mono,'ended_monotonic_ns':time.monotonic_ns(),'started_unix':wall,'ended_unix':time.time(),'returncode':0,'error':None,'adapter_source_sha256':ctx['adapter_source_sha256'],'runner_source_sha256':intent['runner_source_sha256'],'cpu_user_seconds':after.ru_utime-usage.ru_utime,'cpu_system_seconds':after.ru_stime-usage.ru_stime,'max_rss_kib':after.ru_maxrss,'result_ref':ref(d/'RESULT.json')}
write(d/'EXECUTION.json',exe)
