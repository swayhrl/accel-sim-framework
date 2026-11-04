from pathlib import Path
import json,hashlib,os,subprocess,resource,re,types,datetime
R=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1');O=A/'engineering_incidents/launcher_runtime_missing_v1';(O/'cpu_tmp').mkdir(exist_ok=True);(O/'cpu_cache').mkdir(exist_ok=True);(O/'cpu_cwd').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),actual_realpath=str(Path(p).resolve()),sha256=sha(p))
# Read-only fresh legal CPU inventory, private module; no authority/dispatcher call.
p=R/'tools/perf16_resources.py';m=types.ModuleType('launcher_cpu_readonly_resources');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);sample=m.sample_system();assert sample['cpu_allowed'];cpu=sample['cpu_allowed'][0]
env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH=str(R/'DTC/env/lib'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TMPDIR=str(O/'cpu_tmp'),TMP=str(O/'cpu_tmp'),TEMP=str(O/'cpu_tmp'),XDG_CACHE_HOME=str(O/'cpu_cache'))
def limits():
 os.nice(19);os.sched_setaffinity(0,{cpu});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(15,15))
records=[]
def run(name,argv):
 r=subprocess.run([str(x)for x in argv],cwd=O/'cpu_cwd',env=env,capture_output=True,text=True,preexec_fn=limits,timeout=25);(O/(name+'.stdout.log')).write_text(r.stdout);(O/(name+'.stderr.log')).write_text(r.stderr);records.append(dict(name=name,argv=[str(x)for x in argv],returncode=r.returncode,stdout=pin(O/(name+'.stdout.log')),stderr=pin(O/(name+'.stderr.log')),CPU_only=True));assert r.returncode==0,(name,r.returncode,r.stderr);return r
loader=R/'common-lib/ld-linux-x86-64.so.2';tracer=R/'tools/bin/strace';spec=json.loads(next((R/'control/specs').glob('*.json')).read_text());model=Path(spec['native_simulator_argv'][0]);assert sha(model)==spec['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
run('TRACER_ELF_DYNAMIC',['/usr/bin/readelf','-d',tracer]);run('MODEL_ELF_DYNAMIC_READONLY',['/usr/bin/readelf','-d',model]);run('MODEL_ELF_PROGRAM_HEADERS_READONLY',['/usr/bin/readelf','-l',model])
trace_list=run('TRACER_DEPENDENCY_LIST',[loader,'--inhibit-cache','--library-path',str(R/'tools/lib')+':'+str(R/'common-lib'),'--list',tracer]);model_list=run('MODEL_DEPENDENCY_LIST_NO_ENTRY',[loader,'--inhibit-cache','--library-path',R/'DTC/env/lib','--list',model])
assert 'not found'not in trace_list.stdout+trace_list.stderr+model_list.stdout+model_list.stderr
closures={}
for label,result in [('TRACER',trace_list),('MODEL_NO_ENTRY',model_list)]:
 paths=[]
 for line in result.stdout.splitlines():
  found=re.findall(r'(/[^\s]+)\s+\(0x[0-9a-fA-F]+\)',line)
  paths.extend(found)
 assert paths,(label,result.stdout);closures[label]=[pin(p)for p in sorted(set(paths))]
traceout=O/'CPU_TRUE_STRACE.log';assert not traceout.exists(),'CPU diagnostic output exists; preserve and choose a new namespace'
actual=[loader,'--library-path',str(R/'tools/lib')+':'+str(R/'common-lib'),tracer,'-f','-e','trace=%file,process,network','-o',traceout,'--',loader,'--inhibit-cache','--library-path',R/'DTC/env/lib','/usr/bin/true']
run('ACTUAL_STRACE_CPU_TRUE',actual);text=traceout.read_text();assert'/usr/bin/true'in text and'exited with 0'in text and'accel-sim.out'not in text
before=json.loads((O/'BEFORE_REPAIR_EVIDENCE.json').read_text())
for x in before['fixed_assets_to_preserve']:assert sha(x['path'])==x['sha256'],'PINNED_OR_SCIENTIFIC_ASSET_MODIFIED'
# All declared model-side runtime files remain exact, independently of new tools links.
model_runtime=[]
for x in spec['runtime_files']:
 q=R/x['target'];assert q.resolve()==Path(x['actual_realpath']).resolve()and sha(q)==x['sha256'];model_runtime.append(dict(target=str(q),actual_realpath=str(q.resolve()),sha256=x['sha256']))
(O/'CPU_VALIDATION.json').write_text(json.dumps(dict(schema='DTC_LAUNCHER_RUNTIME_LAYOUT_CPU_QUALIFICATION_V1',status='PASS_LAUNCHER_CLOSURE_AND_CPU_TRUE_ONLY',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,ELF_dependency_closures=closures,model_declared_runtime_files_verified=model_runtime,actual_CPU_true_trace=pin(traceout),tracer=pin(tracer),loader=pin(loader),model_ELF_readonly=pin(model),cpu=cpu,nice=19,RLIMIT_AS_bytes=2*1024**3,RLIMIT_CPU_seconds=15,actual_simulator_model_main_executions=0,new_scientific_requests_or_credits=0,original16_retries=0,model_dependencies_resolved_not_executed=True,limitations=['CPU true does not validate simulator main, trace parsing, DTC progress producer or scientific numerical correctness','loader --list resolves ELF dependencies only; dlopen/runtime paths not exercised by a full model remain a future authorized qualification concern','original16 launcher127 identities remain consumed negative; layout repair does not rehabilitate their performance'],all_existing_fixed_assets_preserved=True),indent=2)+'\n')
print(json.dumps(dict(status='PASS_LAUNCHER_CLOSURE_AND_CPU_TRUE_ONLY',cpu=cpu,tracer_libs=len(closures['TRACER']),model_libs=len(closures['MODEL_NO_ENTRY']),actual_strace_true_RC=0,model_main_executions=0,original16_retries=0)))
