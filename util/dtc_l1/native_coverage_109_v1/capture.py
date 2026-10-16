#!/usr/bin/env python3
"""Capture full small producers, including warmups and initialization kernels."""
import argparse,datetime,fcntl,hashlib,json,os,pathlib,signal,subprocess,time
args=argparse.ArgumentParser();args.add_argument('--ld-preload-repair',action='store_true');args=args.parse_args()
repo=pathlib.Path(__file__).resolve().parents[3];src=pathlib.Path(__file__).parent
root=pathlib.Path('/data/c16/dtc_native_coverage_109_v1');raw=root/'raw';py='/data/c16/env/c16-py310/bin/python'
tr=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-simcompat-v1/util/tracer_nvbit/tracer_tool');tool=tr/'tracer_tool.so';post=tr/'traces-processing/post-traces-processing'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt={'tool':str(tool),'tool_sha256':sha(tool),'postprocessor_sha256':sha(post),'tracer_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=tr,text=True).strip(),'producer_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'capture_policy':'ACTIVE_FROM_START=1; all initialization/warmup/ROI kernels, no opcode/root-function filter, no prefix slicing','kernel_roi':'last of four complete operator instances; first three are warmups','attempts':[]}
lock=open('/data/c16/locks/c16_gpu_campaign.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'GPU_BUSY'
 receipt['lock_start_utc']=now()
 for name in ['SpMV','LayerNorm_1024']:
  out=root/('traces_preload_repair' if args.ld_preload_repair else 'traces')/name;out.mkdir(parents=True,exist_ok=False)
  env=os.environ.copy();env.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CUDA_INJECTION64_PATH=str(tool),TRACES_FOLDER=str(out),ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',DTC_ACTION='capture')
  if args.ld_preload_repair:env.pop('CUDA_INJECTION64_PATH',None);env['LD_PRELOAD']=str(tool)
  if name=='SpMV':
   d=root/'assets/parboil/datasets/spmv/small';cmd=[str(root/'bin/spmv'),'-i',f'{d}/input/1138_bus.mtx,{d}/input/vector.bin','-o',str(out/'actual.out')]
  else:cmd=[py,str(src/'layernorm.py'),'capture','--rows','1024']
  a=dict(loading=('LD_PRELOAD_ONLY_BOUNDED_REPAIR' if args.ld_preload_repair else 'CUDA_INJECTION64_PATH'),case=name,start_utc=now(),command=cmd,output=str(out));receipt['attempts'].append(a)
  with (out/'capture.log').open('w') as f:
   p=subprocess.Popen(cmd,env=env,cwd=out,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);t=time.monotonic()
   while p.poll() is None:
    size=sum(x.stat().st_size for x in out.rglob('*') if x.is_file())
    if time.monotonic()-t>240 or size>4*1024**3:
     os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10);a['bounded_stop']='240s/4GiB bound';break
    time.sleep(1)
   a['returncode']=p.returncode;a['elapsed_s']=time.monotonic()-t
  a['end_utc']=now()
  if p.returncode!=0:
   a['status']='CAPTURE_GAP_RETAINED';print(name,a,flush=True);continue
  with (out/'postprocess.log').open('w') as f:
   cp=subprocess.run([str(post),str(out/'traces')],stdout=f,stderr=subprocess.STDOUT,timeout=180)
  a['postprocess_returncode']=cp.returncode
  lists=list(out.rglob('kernelslist.g'));members=list(out.rglob('*.traceg*'));a['traceg_members']=len(members)
  a['status']='CAPTURE_POSTPROCESS_PASS' if cp.returncode==0 and lists and members else 'POSTPROCESS_GAP_RETAINED'
  if name=='SpMV':
   cp=subprocess.run([py,str(src/'check_spmv.py'),str(root/'assets/parboil/datasets/spmv/small/output/1138_bus.mtx.out'),str(out/'actual.out')],capture_output=True,text=True);(out/'correctness.log').write_text(cp.stdout+cp.stderr);assert cp.returncode==0
  a['files']=[dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.rglob('*')) if p.is_file()]
  print(name,a['status'],a['traceg_members'],'members',flush=True)
finally:
 receipt['lock_end_utc']=now();fcntl.flock(lock,fcntl.LOCK_UN);lock.close();(raw/('CAPTURE_PRELOAD_REPAIR_RECEIPT.json' if args.ld_preload_repair else 'CAPTURE_RECEIPT.json')).write_text(json.dumps(receipt,indent=2)+'\n')
