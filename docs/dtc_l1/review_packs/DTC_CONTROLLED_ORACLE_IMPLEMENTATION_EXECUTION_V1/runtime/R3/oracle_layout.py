"""Final stage-root CPUtrue layout qualifier; no scientific model invocation."""
from pathlib import Path
import ast,hashlib,json,os,re,resource,socket,subprocess
P=Path;R=P(__file__).resolve().parents[1]
BASE=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')
BASE_SHA='fb246ce610a76a21ae86b36730283fa9fdd9f5d21e35fd76e2db17847f2b247d'
N=P('/root/data/ep_l2_dtc_l1_native_v2')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'IMMUTABLE_CPU_LAYOUT_RECEIPT_DIFFERS'
 else:
  with p.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
def initialize(specs,output_dir):
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert len(specs)==plan['expected_new_starts']
 assert R.stat().st_dev==2128 and sha(BASE)==BASE_SHA
 files={};links=[]
 for name in ['bin','lib']:
  p=R/'tools'/name;target=N/'tools'/name
  if p.exists()or p.is_symlink():assert p.is_symlink()and p.resolve()==target.resolve()
  else:p.symlink_to(target,target_is_directory=True)
  links.append(dict(path=str(p),target=str(target)))
 assert (R/'control/RESULT_ENGINE_PIN.json').is_file()
 paths=[R/'tools/bin/strace',R/'common-lib/ld-linux-x86-64.so.2',P('/usr/bin/true'),R/'control/RESULT_ENGINE_PIN.json']
 for s in specs:
  for row in s['runtime_files']:
   p=R/row['target'];assert p.resolve()==P(row['actual_realpath']).resolve()and sha(p)==row['sha256'];paths.append(p)
 for p in set(paths):files[str(p)]=dict(path=str(p),actual_realpath=str(p.resolve()),sha256=sha(p))
 lists=[];loader=str(R/'common-lib/ld-linux-x86-64.so.2')
 # --list is executed by the private ELF loader, never by the model entrypoint.
 targets={(str(R/'tools/bin/strace'),str(R/'tools/lib')+':'+str(R/'common-lib')),('/usr/bin/true',str(R/'DTC/env/lib'))}
 targets|={(s['native_simulator_argv'][0],str(R/'DTC/env/lib'))for s in specs}
 for target,libpath in sorted(targets):
  command=[loader,'--inhibit-cache','--library-path',libpath,'--list',target]
  value=subprocess.run(command,capture_output=True,text=True,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=15)
  assert value.returncode==0 and'not found'not in value.stdout+value.stderr,'FINAL_BINARY_ELF_DEPS_FAILED'
  for word in re.findall(r'(/[^\s()]+)',value.stdout):
   p=P(word)
   if p.is_file():files[str(p)]=dict(path=str(p),actual_realpath=str(p.resolve()),sha256=sha(p))
  lists.append(dict(argv=command,returncode=value.returncode,stdout=value.stdout,stderr=value.stderr,simulator_entrypoint_called=False))
 tree=ast.parse(BASE.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run_native')
 nodes=[next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==key for t in n.targets))for key in ['env','loader','argv']]
 output_dir=P(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
 assert output_dir.is_relative_to(R)and output_dir.stat().st_dev==2128
 cpu=next(c for c in reversed(plan['new_dispatcher_cpu_allowance'])if c not in plan['protected_cpu_ids'])
 rows=[]
 for s in specs:
  out=output_dir/s['cohort'];out.mkdir(exist_ok=True)
  for name in ['tmp','cache']:(out/name).mkdir(exist_ok=True)
  left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);ns={'ROOT':R,'s':s,'out':out,'str':str}
  exec(compile(ast.Module(body=nodes,type_ignores=[]),str(BASE)+':QUALIFIED_ORACLE_CPU_LAUNCHER','exec'),ns)
  env=ns['env'];env.update(s['original_environment']);env['DTC_AG7_GENERATION']='CPU_LAYOUT_NOT_A_SCIENTIFIC_UUID';env['DTC_AG7_PROGRESS_FD']=str(right.fileno())
  original=ns['argv'];positions=[i for i,a in enumerate(original)if a==s['native_simulator_argv'][0]];assert len(positions)==1
  argv=list(original);argv[positions[0]]='/usr/bin/true'
  assert all(a==b for i,(a,b)in enumerate(zip(argv,original))if i!=positions[0])
  def limits():
   os.setsid();os.sched_setaffinity(0,{cpu});resource.setrlimit(resource.RLIMIT_CORE,(0,0));lim=s['limits']['max_process_tree_vms_bytes'];resource.setrlimit(resource.RLIMIT_AS,(lim,lim));os.nice(10)
  try:value=subprocess.run(argv,cwd=out,env=env,pass_fds=(right.fileno(),),preexec_fn=limits,capture_output=True,text=True,timeout=15)
  finally:left.close();right.close()
  trace=out/'actual_file_process_network.log';assert value.returncode==0 and trace.exists()
  t=trace.read_text();assert '/usr/bin/true'in t and s['native_simulator_argv'][0]not in t and'connect('not in t
  receipt=dict(cohort=s['cohort'],plan_id=s['plan_id'],input_digest=s['input_digest'],mode=s['oracle_mode'],CPU_argv=argv,scientific_argv_not_executed=original,environment=env,cwd=str(out),cwd_device=2128,passed_progress_FD_open=True,affinity=[cpu],limits_AS_bytes=s['limits']['max_process_tree_vms_bytes'],payload='/usr/bin/true',returncode=value.returncode,simulator_started=False,scientific_UUID_allocated=False)
  put(out/'CPU_TRUE_RECEIPT.json',receipt)
  rows.append(dict(cohort=s['cohort'],receipt_path=str(out/'CPU_TRUE_RECEIPT.json'),receipt_sha256=sha(out/'CPU_TRUE_RECEIPT.json'),trace_path=str(trace),trace_sha256=sha(trace)))
 manifest=dict(schema='DTC_CONTROLLED_ORACLE_FINAL_HOST_LAYOUT_CPU_QUALIFICATION_V1',status='PASS',request=plan['request'],final_binary_layout_qualified=True,scientific_models_started=0,scientific_UUIDs_allocated=0,files=list(files.values()),directory_links=links,ELF_dependency_lists=lists,CPU_probes=rows,source_sha256=sha(__file__),base_launcher_source_sha256=BASE_SHA)
 target=R/'control/LAUNCHER_LAYOUT.fixed.json';put(target,manifest)
 return dict(path=str(target),sha256=sha(target))
