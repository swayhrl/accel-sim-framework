from pathlib import Path
import sys,os,json,subprocess,hashlib,resource,time,datetime
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1/agents/C_codesign_v1');tmp=O/'private_cpu';tmp.mkdir(exist_ok=True);os.nice(10);blocked={2,258}|set(range(32,64))|set(range(288,320))
def siblings(c):
 out=set()
 try:
  for x in Path('/sys/devices/system/cpu/cpu'+str(c)+'/topology/thread_siblings_list').read_text().strip().split(','):
   if '-'in x:a,b=map(int,x.split('-'));out.update(range(a,b+1))
   else:out.add(int(x))
 except OSError:out.add(c)
 return out
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes()
  if b'accel-sim.out'in cmd and b'-trace'in cmd:
   aff=os.sched_getaffinity(int(p.name))
   if len(aff)==1:
    for c in aff:blocked|=siblings(c)
 except (OSError,ValueError):pass
cpu=max(set(os.sched_getaffinity(0))-blocked);os.sched_setaffinity(0,{cpu})
header=Path('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dtc-l1-common.h');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(header)=='dab2df3ec8e1fd1c8953ac146eba3c93906c84af8cce66051e5728afe9963fa1';src=O/'codesign_lifecycle_cpu.cpp';binary=tmp/'codesign_lifecycle_cpu'
def limits():resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CPU,(60,60))
env=dict(os.environ,TMPDIR=str(tmp));cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-I'+str(header.parent),str(src),'-o',str(binary)];t=time.monotonic();build=subprocess.run(cmd,capture_output=True,text=True,env=env,preexec_fn=limits,timeout=90);(O/'CPU_COMPILE.stdout').write_text(build.stdout);(O/'CPU_COMPILE.stderr').write_text(build.stderr);assert build.returncode==0,build.stderr
run=subprocess.run([str(binary)],capture_output=True,text=True,env=env,preexec_fn=limits,timeout=90);(O/'CPU_LIFECYCLE.stdout.jsonl').write_text(run.stdout);(O/'CPU_LIFECYCLE.stderr').write_text(run.stderr);assert run.returncode==0,(run.returncode,run.stderr,run.stdout[-1000:]);rows=[json.loads(x)for x in run.stdout.splitlines()];assert len(rows)==19
negative=[]
for flag in ['duplicate_return','stale_generation']:
 r=subprocess.run([str(binary),flag],capture_output=True,text=True,env=env,preexec_fn=limits,timeout=60);assert r.returncode==-6,(flag,r.returncode,r.stdout,r.stderr);(O/('CPU_NEGATIVE_'+flag+'.stderr')).write_text(r.stderr);negative.append(dict(case=flag,expected='SIGABRT_original_assertion',returncode=r.returncode,passed=True))
result=dict(status='PASS_BOUNDED_ORIGINAL_HEADER_CPU_ONLY',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),positive_cases=rows,positive_case_count=len(rows),negative_guards=negative,header_path=str(header),header_sha256=sha(header),source_sha256=sha(src),compile_command=cmd,compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],one_cpu=cpu,nice=10,child_AS_limit_bytes=1024**3,elapsed_seconds=time.monotonic()-t,model_starts=0,trace_or_live_raw_reads=0,service_test_ticks_not_workload_performance=True,production_single_partial_guard_respected_by_explicit_eligible_retire=True,no_universal_liveness_or_fullapplication_correctness_claim=True);assert sha(header)==result['header_sha256'];(O/'CPU_LIFECYCLE_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('HEADER_CPU',len(rows),len(negative),'cpu',cpu,'elapsed',result['elapsed_seconds'])
