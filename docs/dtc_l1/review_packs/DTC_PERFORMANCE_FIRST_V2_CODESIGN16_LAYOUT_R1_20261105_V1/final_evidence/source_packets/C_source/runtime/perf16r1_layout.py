"""Exact immutable host launcher layout; CPU /usr/bin/true only, never a model."""
from pathlib import Path
import ast,copy,hashlib,json,os,resource,socket,subprocess
R=Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1');REQ='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1';AUTH='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe'
BASE=Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');BASE_SHA='fb246ce610a76a21ae86b36730283fa9fdd9f5d21e35fd76e2db17847f2b247d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def exact_write(p,b):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists()or p.is_symlink():assert p.is_file()and p.read_bytes()==b,'EXISTING_LAYOUT_FILE_DIFFERS_NO_OVERWRITE:'+str(p)
 else:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def jsonbytes(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def launcher_contract(spec,output,generation,progress_fd):
 assert sha(BASE)==BASE_SHA
 root=ast.parse(BASE.read_bytes());fn=next(x for x in root.body if isinstance(x,ast.FunctionDef)and x.name=='run_native')
 wanted=[]
 for key in ['env','loader','argv']:
  node=next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==key for t in n.targets));wanted.append(node)
 ns={'ROOT':R,'s':spec,'out':Path(output),'str':str};exec(compile(ast.Module(body=wanted,type_ignores=[]),str(BASE)+':EXACT_LAUNCHER_CONTRACT_CPU','exec'),ns);env=ns['env']
 for k in ['DTC_AG7_POLICY_B_PROGRESS','DTC_AG7_INPUT_SHA','DTC_AG7_ROI_SHA']:env[k]=spec['original_environment'][k]
 env['DTC_AG7_GENERATION']=generation;env['DTC_AG7_PROGRESS_FD']=str(progress_fd)
 return ns['argv'],env

def validate(ref):
 assert Path(ref['path']).resolve()==(R/'control/LAUNCHER_LAYOUT.fixed.json').resolve()and sha(ref['path'])==ref['sha256'];v=read(ref['path'])
 assert v['schema']=='DTC_CODESIGN16_LAYOUT_R1_HOST_LAUNCHER_CLOSURE_V1'and v['request']==REQ and v['authority_commit']==AUTH and v['scientific_models_started']==0
 assert v['base_native_source_sha256']==BASE_SHA==sha(BASE)
 for row in v['directory_links']:
  p=Path(row['path']);assert p.is_symlink()and os.readlink(p)==row['symlink_target']and str(p.resolve())==row['resolved_target']
 for row in v['files']:assert sha(row['path'])==row['sha256']and str(Path(row['path']).resolve())==row['actual_realpath']
 assert len(v['CPU_probes'])==16 and {r['returncode']for r in v['CPU_probes']}=={0}
 for row in v['CPU_probes']:
  assert row['payload']=='/usr/bin/true'and row['simulator_started']is False
  for f in row['evidence_files']:assert sha(f['path'])==f['sha256']
 return dict(schema=v['schema'],request=REQ,layout_sha256=ref['sha256'],source_dependencies=len(v['files']),CPU_true_passes=16,scientific_models_started=0)

def initialize(specs,output_dir):
 output_dir=Path(output_dir);assert len(specs)==16
 existing=R/'control/LAUNCHER_LAYOUT.fixed.json'
 if existing.exists():
  ref=dict(path=str(existing),sha256=sha(existing));validate(ref);return ref
 output_dir.mkdir(parents=True,exist_ok=True)
 links=[];files={}
 for name in ['bin','lib']:
  p=R/'tools'/name;target=Path('/root/data/ep_l2_dtc_l1_native_v2/tools')/name;p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists()or p.is_symlink():assert p.is_symlink()and p.resolve()==target.resolve(),'LAUNCHER_DIR_LINK_DIFFERENT_NO_OVERWRITE'
  else:p.symlink_to(target,target_is_directory=True)
  links.append(dict(path=str(p),symlink_target=os.readlink(p),resolved_target=str(p.resolve())))
 paths=[R/'tools/bin/strace',R/'common-lib/ld-linux-x86-64.so.2',Path('/usr/bin/true'),*sorted((R/'tools/lib').iterdir())]
 for p in paths:
  assert p.is_file()and p.read_bytes()[:4]==b'\x7fELF','EXPECTED_ELF_DEPENDENCY:'+str(p);files[str(p)]=dict(path=str(p),actual_realpath=str(p.resolve()),sha256=sha(p))
 loader=str(R/'common-lib/ld-linux-x86-64.so.2');lists=[]
 for target,libpath in [(str(R/'tools/bin/strace'),str(R/'tools/lib')+':'+str(R/'common-lib')),('/usr/bin/true',str(R/'DTC/env/lib'))]:
  argv=[loader,'--inhibit-cache','--library-path',libpath,'--list',target];run=subprocess.run(argv,text=True,capture_output=True,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=15);assert run.returncode==0 and'not found'not in run.stdout+run.stderr,'ELF_DEPENDENCY_CLOSURE_FAILED'
  import re
  for word in re.findall(r'(/[^\s()]+)',run.stdout):
   p=Path(word)
   if p.is_file():files[str(p)]=dict(path=str(p),actual_realpath=str(p.resolve()),sha256=sha(p))
  lists.append(dict(argv=argv,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
 exact_write(output_dir/'ELF_DEPENDENCY_LISTS.json',jsonbytes(lists));probes=[]
 allowed=sorted(os.sched_getaffinity(0));cpu=next((c for c in reversed(allowed)if c not in set(range(32,64))|set(range(288,320))|{2,258}),allowed[-1])
 for spec in specs:
  out=output_dir/spec['cohort'];out.mkdir(exist_ok=True);(out/'tmp').mkdir(exist_ok=True);(out/'cache').mkdir(exist_ok=True);left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM)
  scientific_argv,env=launcher_contract(spec,out,'CPU_LAYOUT_PROBE_NOT_A_SCIENCE_UUID',right.fileno());argv=list(scientific_argv);indices=[i for i,a in enumerate(argv)if a==spec['native_simulator_argv'][0]];assert len(indices)==1;argv[indices[0]]='/usr/bin/true';assert len(argv)==len(scientific_argv)and all(a==b for i,(a,b)in enumerate(zip(argv,scientific_argv))if i!=indices[0])
  def limits():
   os.setsid();os.sched_setaffinity(0,{cpu});resource.setrlimit(resource.RLIMIT_CORE,(0,0));limit=spec['limits']['max_process_tree_vms_bytes'];resource.setrlimit(resource.RLIMIT_AS,(limit,limit));os.nice(10)
  try:run=subprocess.run(argv,cwd=out,env=env,pass_fds=(right.fileno(),),preexec_fn=limits,text=True,capture_output=True,timeout=15)
  finally:left.close();right.close()
  assert run.returncode==0,'FULL_CPU_NATIVE_LAUNCHER_CHAIN_FAILED';trace=out/'actual_file_process_network.log';assert trace.exists()and'/usr/bin/true'in trace.read_text()and spec['native_simulator_argv'][0]not in trace.read_text(),'CPU_MUST_NOT_EXECUTE_SCIENTIFIC_SIMULATOR'
  receipt=dict(cohort=spec['cohort'],program=spec['program'],profile=spec['profile'],payload='/usr/bin/true',returncode=0,scientific_argv=scientific_argv,CPU_argv=argv,cwd=str(out),environment=env,passed_progress_fd_was_open=True,actual_CPU_affinity=[cpu],effective_RLIMIT_AS_bytes=spec['limits']['max_process_tree_vms_bytes'],stdout=run.stdout,stderr=run.stderr,simulator_started=False,qualification_only_not_actual_ROI_or_guard=True)
  exact_write(out/'CPU_TRUE_RECEIPT.json',jsonbytes(receipt));probes.append(dict(cohort=spec['cohort'],payload='/usr/bin/true',returncode=0,simulator_started=False,evidence_files=[dict(path=str(p),sha256=sha(p))for p in [trace,out/'CPU_TRUE_RECEIPT.json']]))
 # Include the exact immutable dependency/list proof, not an inferred package name.
 files[str(output_dir/'ELF_DEPENDENCY_LISTS.json')]=dict(path=str(output_dir/'ELF_DEPENDENCY_LISTS.json'),actual_realpath=str((output_dir/'ELF_DEPENDENCY_LISTS.json').resolve()),sha256=sha(output_dir/'ELF_DEPENDENCY_LISTS.json'))
 manifest=dict(schema='DTC_CODESIGN16_LAYOUT_R1_HOST_LAUNCHER_CLOSURE_V1',request=REQ,authority_commit=AUTH,base_native_source_path=str(BASE),base_native_source_sha256=BASE_SHA,directory_links=links,files=list(files.values()),CPU_probes=probes,scientific_models_started=0,CPU_payload_not_a_scientific_canary=True,full_model_runtime_PID_progress_guard_qualification_still_required=True)
 p=R/'control/LAUNCHER_LAYOUT.fixed.json';exact_write(p,jsonbytes(manifest));ref=dict(path=str(p),sha256=sha(p));validate(ref);return ref


def validate_native_cwd(ref):
 assert Path(ref['path']).resolve()==(R/'control/LAUNCHER_NATIVE_CWD_QUALIFICATION.fixed.json').resolve()and sha(ref['path'])==ref['sha256']
 v=read(ref['path']);assert v['schema']=='DTC_CODESIGN16_LAYOUT_R1_NATIVE_CWD_CPU_QUALIFICATION_V1'and v['request']==REQ and v['authority_commit']==AUTH and v['CPU_native_true_passes']==16 and v['native_cwd_device']==2128 and v['scientific_models_started']==v['scientific_UUIDs_allocated']==0
 assert len(v['rows'])==16 and len({r['cohort']for r in v['rows']})==16
 for row in v['rows']:
  assert row['returncode']==0 and row['payload']=='/usr/bin/true'and row['cwd_device']==2128 and row['simulator_started']is False and row['scientific_UUID_allocated']is False
  for f in row['evidence_files']:assert sha(f['native_path'])==f['sha256']==sha(f['archive_evidence_path'])
 return dict(schema=v['schema'],native_cwd_SHA256=ref['sha256'],CPU_native_true_passes=16,scientific_models_started=0,future_scientific_UUID_cwd_still_requires_actual_launch=True)
