from pathlib import Path
import subprocess,os,time,json,hashlib,fcntl,signal,shutil,resource
R=Path('/data/c16/ada_call_snapshot_nn_20261024_v1');S=json.loads((R/'control/CAPTURE_PAIR_SPEC_A3_V1.json').read_text())
ROOT=R/'attempts/pair_A3_v1';ROOT.mkdir(parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 with p.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def ticks(pid):return (Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]
def query(f):return subprocess.check_output(['nvidia-smi','--query-gpu='+f,'--format=csv,noheader,nounits'],text=True).strip()
def procs():
 lines=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'],text=True).splitlines()
 return {int(x.split(', ')[0]):x.split(', ')[1:]for x in lines if x.strip()}
for p,h in S['pins'].items():assert sha(p)==h
lock=open('/data/c16/locks/c16_gpu_campaign.lock','a');fcntl.flock(lock,fcntl.LOCK_EX)
try:
 assert query('uuid')=='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59'
 baseline=procs();bt={}
 for pid,row in baseline.items():
  cmd=(Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  assert row[0]=='/home/huangrulin/workspace/image-lab/envs/comfyui/bin/python'and '/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py'in cmd
  bt[pid]=ticks(pid)
 def guard(own=None):
  v=os.statvfs(R);assert v.f_frsize*v.f_bavail>=S['limits']['min_free_bytes']
  for pid,row in procs().items():assert pid==own or(pid in baseline and ticks(pid)==bt[pid]and float(row[1])<=float(baseline[pid][1])+256),'foreign compute changed'
  assert float(query('memory.free'))>=512
 stable=0;deadline=time.monotonic()+120
 while stable<15:
  guard();stable=stable+1 if float(query('utilization.gpu'))==0 else 0
  assert time.monotonic()<deadline;time.sleep(1)
 put(ROOT/'GPU_GATE.json',{'gpu':query('uuid,name,driver_version,memory.total,memory.free'),'baseline':baseline,'baseline_start_ticks':bt,'idle_zero_seconds':15,'cooperative_lock':True})
 results=[]
 for mode in ['observer','trace']:
  a=ROOT/mode;a.mkdir();shutil.copyfile(S['tool'],a/'TOOL_USED.so')
  for row in S['inputs']:
   dst=a/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['source'],dst);assert sha(dst)==row['sha256']
  env=os.environ.copy()
  for k in list(env):
   if k.startswith(('ADA_','NVBIT_','TRACE_','TOOL_','DYNAMIC_','C16_','INSTR_'))or k in ['LD_PRELOAD','CUDA_INJECTION64_PATH']:env.pop(k,None)
  env.update(PATH='/usr/local/cuda-12.8/bin:'+env.get('PATH',''),CUDA_VISIBLE_DEVICES=query('uuid'),NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',LD_PRELOAD=str(a/'TOOL_USED.so')+':libcuda.so.1',ACTIVE_FROM_START='1',TOOL_COMPRESS='1',TRACE_FILE_COMPRESS='1',ADA_SEMANTIC_MAP=str(Path(S['map_root'])/'semantic-map.tsv'),INSTR_BEGIN='0',INSTR_END='4294967295',C16_EXACT_ROOT_FUNCTION_ONLY='1',C16_USE_NVBIT_STATIC_INDEX='0',ENABLE_SPINLOCK_FAST_FORWARD='0',TERMINATE_UPON_LIMIT='0',EXCLUDE_PRED_OFF='0',ADA_INPUT_SNAPSHOT='1',ADA_INPUT_MAX_COPY_BYTES='342112',ADA_INPUT_MAX_TOTAL_BYTES='342112')
  if mode=='observer':env['ADA_INPUT_SNAPSHOT_ONLY']='1'
  control_env={k:v for k,v in env.items()if k.startswith(('ADA_','NVBIT_','TRACE_','TOOL_','DYNAMIC_','C16_','INSTR_'))or k in ['LD_PRELOAD','CUDA_INJECTION64_PATH','CUDA_VISIBLE_DEVICES','NVDISASM','PATH']}
  args=S['task']['argv'];rec={'argv':args,'mode':mode,'binary_sha256':sha(args[0]),'tool_sha256':sha(a/'TOOL_USED.so'),'map_manifest_sha256':sha(Path(S['map_root'])/'manifest.json'),'control_env':control_env,'spec_sha256':sha(R/'control/CAPTURE_PAIR_SPEC_A3_V1.json'),'started_unix':time.time(),'scope':'PRIVATE_NN_INPUT_OUTPUT_TYPED_CALL_PRODUCER_CANDIDATE_NOT_FORMAL_NOT_SIM'}
  def child_limits():resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]))
  with(a/'stdout.log').open('xb')as out,(a/'stderr.log').open('xb')as err:
   p=subprocess.Popen(args,cwd=a,env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=child_limits)
   rec.update(pid=p.pid,start_ticks=ticks(p.pid));start=time.monotonic();reason=None;peakrss=0;peakbytes=0
   try:
    while p.poll()is None:
     guard(p.pid)
     size=sum(x.stat().st_size for x in a.rglob('*')if x.is_file());peakbytes=max(peakbytes,size)
     if size>S['limits']['output_each_bytes']:raise RuntimeError('own output cap')
     try:rss=int(next(x.split()[1]for x in (Path('/proc')/str(p.pid)/'status').read_text().splitlines()if x.startswith('VmRSS:')))*1024
     except (FileNotFoundError,StopIteration):
      if p.poll()is not None:break
      raise
     peakrss=max(peakrss,rss)
     if rss>S['limits']['RSS_each_bytes']:raise RuntimeError('own RSS cap')
     if time.monotonic()-start>S['limits']['wall_each_s']:raise RuntimeError('own wall cap')
     time.sleep(.1)
   except BaseException as error:
    reason=repr(error)
    if p.poll()is None:os.killpg(p.pid,signal.SIGKILL);p.wait()
   rc=p.wait()
  rec.update(exit_code=rc,stop_reason=reason,elapsed=time.monotonic()-start,peak_rss_bytes=peakrss,peak_output_bytes=peakbytes)
  put(a/'EXECUTION.json',rec);results.append(rec)
  if rc!=0 or reason is not None:break
 guard();put(ROOT/'RESULTS.json',{'GPU_ONLY_NOT_SIM':True,'formal_bulk_admission':False,'results':results,'source_KEEP':True})
 print(json.dumps(results))
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
