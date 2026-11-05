"""V9 serial profiler-wrapper and actual-model PID ownership."""
import os,sys,json,time,secrets,subprocess,signal,hashlib,re
from pathlib import Path
from types import SimpleNamespace as NS
from persistence import save_json
from shared_gate import identity,same
from resource_monitor import MonitorStop,disk_bytes
from rss_lifecycle import OwnLifecycle,SessionMemory
def alive(ps,pid):
 try:return ps.Process(pid).is_running() and ps.Process(pid).status() not in ('zombie','dead')
 except ps.NoSuchProcess:return False
def bind_actual(x):
 s=x.s;state=s.v9state;p=state['context']/'WORKER_IDENTITY.json'
 if not p.exists():return False
 v=json.loads(p.read_text())
 if v['nonce']!=state['nonce'] or v['task']!=state['task'] or v['supervisor_pid']!=s.pid:raise MonitorStop('GPU_RESOURCE_DEFERRED','Worker nonce/task/owner mismatch')
 if v['worker_sha256']!=hashlib.sha256((Path(x.cfg['tool'])/'worker.py').read_bytes()).hexdigest():raise MonitorStop('NUMERIC_OR_RUNTIME_NO_GO','Worker source mismatch')
 pid=v['identity']['pid']
 if not alive(s.ps,pid):return False
 if not same(identity(pid),v['identity']):raise MonitorStop('GPU_RESOURCE_DEFERRED','Worker incarnation mismatch')
 if pid not in {p.pid for p in s.ps.Process(s.pid).children(recursive=True)}:raise MonitorStop('GPU_RESOURCE_DEFERRED','Worker outside dispatcher tree')
 if state.get('actual_pid') not in [None,pid]:raise MonitorStop('GPU_RESOURCE_DEFERRED','Unexpected profiler app replay PID')
 state['actual_pid']=pid;state['actual_identity']=v['identity'];state['actual_ps_birth']=s.ps.Process(pid).create_time();x.owned.add(pid);x.lifecycle.bind_worker(pid);x.r['children'][-1]['actual_worker']=v
 return True
def own_gpu(x):
 return [int(v.pid) for v in x.s.nv.nvmlDeviceGetComputeRunningProcesses(x.handle) if int(v.pid) in x.owned]
def query_metrics(x):
 cfg=x.cfg;s=x.s;p=Path(cfg['out'])/'raw/NCU_METRIC_QUERY.txt';err=p.with_suffix('.stderr.txt')
 command=[cfg['ncu'],'--query-metrics','--query-metrics-mode','all','--devices','0']
 with p.open('w') as f,err.open('w') as e:
  child=subprocess.Popen(command,stdout=f,stderr=e,start_new_session=True);x.owned.add(child.pid)
  try:x.lifecycle.bind_worker(child.pid)
  except s.ps.NoSuchProcess:
   if child.poll() is None:raise
   x.lifecycle.bind_worker(s.pid)
  started=time.monotonic()
  try:
   while child.poll() is None:
    x.snapshot('TOOL_QUERY')
    if time.monotonic()-started>20:s.terminate(child);break
    s.sleep(.25)
  finally:
   if child.poll() is None:s.terminate(child)
   x.lifecycle.bind_worker(s.pid)
 if own_gpu(x):raise MonitorStop('GPU_RESOURCE_DEFERRED','NCU query context unresolved')
 x.snapshot('TOOL_QUERY_DONE')
 names=set(re.findall(r'\b[a-z][a-z0-9_]*__[A-Za-z0-9_.]+',p.read_text(errors='replace')))
 groups=[['gpu__time_duration.sum'],['dram__bytes_read.sum'],['dram__bytes_write.sum'],['lts__t_sectors_op_read.sum','lts__t_sectors_srcunit_tex_op_read.sum','lts__t_bytes.sum'],['sm__throughput.avg.pct_of_peak_sustained_elapsed'],['sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed','sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active','smsp__inst_executed_pipe_tensor.sum'],['sm__warps_active.avg.pct_of_peak_sustained_active']]
 selected=[next((v for v in options if v in names),None) for options in groups];selected=[v for v in selected if v]
 result=dict(command=command,exit_code=child.returncode,queried_names=len(names),selected=selected,raw_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),clock='none',cache='none',replay='kernel',graph='node',launch_count=1,coverage='Firstmatchingdense node in firstDecodeGraph,not applicationtraffic')
 save_json(Path(cfg['out'])/'raw/NCU_METRIC_SELECTION.json',result);return result
def execute_tasks(x):
 cfg=x.cfg;s=x.s
 if cfg.get('v10_dispatch'):
  from v10_dispatch import execute_v10
  return execute_v10(x)
 for task in cfg['worker_tasks']:
  if s.mono()-x.held>cfg['held_seconds_max']-150:x.r.setdefault('optional_skips',[]).append(dict(task=task,reason='Budgetreserve'));break
  if task.startswith('NCU') and not s.v9state.get('metric_plan'):s.v9state['metric_plan']=query_metrics(x)
  s.v9state['next_task']=task;x.child=s.spawn();x.owned.add(x.child.pid);x.lifecycle.bind_worker(x.child.pid)
  x.r['worker_launches']+=1;x.r['children'].append(dict(task=task,launcher_pid=x.child.pid,start_epoch=s.wall(),launch=s.v9state['launch']))
  start=s.mono();bound=False
  while x.child.poll() is None:
   state=s.v9state
   if not bound:bound=bind_actual(x)
   finish=state['context']/'WORKER_FINISHED.json';finished=False
   if finish.exists():
    v=json.loads(finish.read_text());finished=v.get('nonce')==state['nonce'] and v.get('task')==task
   if finished and not own_gpu(x):
    x.lifecycle.bind_worker(x.child.pid if alive(s.ps,x.child.pid) else s.pid)
    row=x.snapshot('PROFILER_CPU_DRAIN')
    if row['own_NVML_bytes']:raise MonitorStop('GPU_RESOURCE_DEFERRED','CUDA work after context drain')
   else:
    row=x.snapshot('WORKER' if bound else 'WORKER_BOOTSTRAP')
    if not bound and row['own_NVML_bytes']:raise MonitorStop('GPU_RESOURCE_DEFERRED','CUDA before actual PID binding')
   if not bound and s.mono()-start>90:s.terminate(x.child);x.r['children'][-1]['bootstrap_timeout']=True;break
   s.sleep(.25 if not bound else cfg['monitor_seconds'])
  x.r['children'][-1].update(exit_code=x.child.returncode,finish_epoch=s.wall())
  if own_gpu(x):raise MonitorStop('GPU_RESOURCE_DEFERRED','Profiler context not drained')
  x.lifecycle.bind_worker(s.pid);x.snapshot('WORKER_EXIT');result=s.worker_result()
  x.r['children'][-1].update(model_initializations=result.get('model_initializations',0),result_status=result.get('status'),error=result.get('error'));x.save()
  if task=='CURVE':
   counts=result.get('point_completion',{})
   if result.get('status')!='V9_WORKER_COMPLETE' or len(counts)!=18 or not all(n>=5 for n in counts.values()):raise MonitorStop('NUMERIC_OR_RUNTIME_NO_GO','Nativecurvefailed')
  elif result.get('validity_stop'):raise MonitorStop('NUMERIC_OR_RUNTIME_NO_GO','Fundamental model/input/backend validity')
  elif x.child.returncode!=0 or result.get('status')!='V9_WORKER_COMPLETE':x.r.setdefault('optional_failures',[]).append(dict(task=task,exit_code=x.child.returncode,result_status=result.get('status'),error=result.get('error'),contexts_drained=True))
  x.r['GPU_model_initializations']=sum(v.get('model_initializations',0) for v in x.r['children']);x.save()
 x.r['status']='V9_STUDY_COMPLETE'
def real_services(cfg,tool):
 import psutil,pynvml
 state={};pid=os.getpid();lifecycle=OwnLifecycle(psutil,pid);session=SessionMemory(pid)
 def terminate(child):
  candidates=[]
  try:
   parent=psutil.Process(child.pid);candidates=parent.children(recursive=True)+[parent]
  except psutil.NoSuchProcess:pass
  actual=state.get('actual_pid')
  if actual is not None:
   try:
    p=psutil.Process(actual)
    if p.create_time()==state.get('actual_ps_birth') and same(identity(actual),state.get('actual_identity',{})):candidates.append(p)
   except psutil.NoSuchProcess:pass
  unique={p.pid:p for p in candidates}
  for p in reversed(list(unique.values())):
   try:p.terminate()
   except psutil.NoSuchProcess:pass
  try:child.wait(timeout=3)
  except subprocess.TimeoutExpired:pass
  for p in unique.values():
   try:
    if p.is_running() and p.status()!='zombie':p.kill()
   except psutil.NoSuchProcess:pass
  try:child.wait(timeout=2)
  except subprocess.TimeoutExpired:raise RuntimeError('Own profiler launcher failed to terminate')
 def spawn():
  task=state['next_task'];context=Path(cfg['out'])/'.private'/task;context.mkdir(exist_ok=False);(context/'tmp').mkdir()
  if state.get('log'):state['log'].close()
  state.pop('finished_seen',None)
  state.update(task=task,context=context,nonce=secrets.token_hex(24),actual_pid=None)
  env=os.environ.copy();env.update(WEIGHT_PROBE_LOCK_OWNER=str(pid),V9_WORKER_NONCE=state['nonce'],HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',VLLM_ENABLE_V1_MULTIPROCESSING='0',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',TORCHINDUCTOR_COMPILE_THREADS='1',VLLM_NO_USAGE_STATS='1',DO_NOT_TRACK='1')
  for key,sub in [('VLLM_CACHE_ROOT','vllm'),('VLLM_CONFIG_ROOT','vllm_config'),('TORCHINDUCTOR_CACHE_DIR','inductor'),('TRITON_CACHE_DIR','triton'),('CUDA_CACHE_PATH','cuda'),('XDG_CACHE_HOME','xdg'),('HF_HOME','hf'),('TORCH_HOME','torch'),('TORCH_EXTENSIONS_DIR','extensions'),('HOME','home'),('TMPDIR','tmp'),('NUMBA_CACHE_DIR','numba')]:env[key]=str(context/sub)
  command=[sys.executable,str(tool/'worker.py'),task]
  if task=='NSYS':command=[cfg['nsys'],'profile','--trace=cuda,nvtx','--sample=none','--cpuctxsw=none','--python-sampling=false','--gpu-metrics-devices=none','--cuda-graph-trace=node','--capture-range=cudaProfilerApi','--capture-range-end=stop','--kill=none','--force-overwrite=true','--export=sqlite','--output',str(context/'trace')]+command
  elif task.startswith('NCU') or task.startswith('PILOT') or task.startswith('LOCAL'):
   plan=state.get('metric_plan',{})
   if not plan.get('selected'):env['V9_OPTIONAL_SKIP_REASON']='No queried supported NCU metrics'
   else:command=[cfg['ncu'],'--target-processes','application-only','--graph-profiling','node','--replay-mode','kernel','--profile-from-start','no','--nvtx','--kernel-name-base','demangled','--rename-kernels','off','--filter-mode','global','--kernel-name','regex:.*(internal::gemvx::kernel<|cutlass::Kernel2<.*gemm).*','--nvtx-include','decodeGraph/' if task.startswith('NCU') else 'v11Local/','--launch-skip',str(69 if task.endswith('L17') else 1 if task.startswith('NCU') else 0),'--launch-count',str(3 if task.startswith('NCU') else 10 if task.startswith('LOCAL') else 1),'--kill','no','--clock-control','none','--cache-control','none','--pipeline-boost-state','dynamic','--disable-extra-suffixes','--metrics',','.join(plan['selected']),'--force-overwrite','--export',str(context/'metrics')]+command
  state['launch']=dict(task=task,command=command,nonce=state['nonce'],scope='SYNTHETIC_PROFILED_PROXY' if task.startswith('PILOT') else 'SYNTHETIC_NATIVE_PROXY' if task=='MICRO' else 'Nativecurve' if task=='CURVE' else 'PROFILED_NOT_FORMAL' if task in ['NSYS','NCU_B1','NCU_B2'] else 'ALTERED_EAGER_NOT_NATIVE',clock_control='none',prefix_cache=False)
  save_json(context/'LAUNCH.json',state['launch']);state['log']=(context/'worker.log').open('w')
  return subprocess.Popen(command,cwd=cfg['root'],env=env,stdout=state['log'],stderr=subprocess.STDOUT,start_new_session=True)
 def result():
  p=Path(cfg['out'])/'raw'/(state['task']+'.json')
  return json.loads(p.read_text()) if p.exists() else dict(status='TOOL_LAUNCH_FAILED',model_initializations=0,error='No target worker result;seeprofilerlog')
 return NS(pid=pid,nv=pynvml,ps=psutil,wall=time.time,mono=time.monotonic,sleep=time.sleep,disk=lambda:disk_bytes(cfg['root']),open_lock=lambda p:open(p,'r'),flock=__import__('fcntl').flock,spawn=spawn,terminate=terminate,worker_result=result,lifecycle=lifecycle,session_memory=session,v9state=state)
