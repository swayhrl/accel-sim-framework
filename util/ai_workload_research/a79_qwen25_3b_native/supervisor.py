"""Nonblocking campaign lock and independent NVML/resource supervision."""
import os,sys,pathlib,json,time,fcntl,subprocess,signal,statistics,traceback
import psutil,pynvml as nv
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1';P=OUT/'.private';TOOL=pathlib.Path(__file__).parent
START=1792983527;UUID='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59'
def save(path,value):
 tmp=path.with_suffix('.writing');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(path)
def disk_bytes():
 total=0
 for d,dirs,files in os.walk(ROOT):
  for name in files:
   f=pathlib.Path(d)/name
   try:total+=f.stat().st_size
   except FileNotFoundError:pass
 return total

def main():
 receipt={'status':'PRELOCK','supervisor_pid':os.getpid(),'GPU_seconds_limit':720,'whole_Goal_seconds_limit':2700,'VRAM_limit_MiB':15400,'RSS_tree_limit_bytes':16*1024**3,'new_disk_limit_bytes':3*1024**3,'samples':[],'children':[],'GPU_model_initializations':0,'lock_acquired':False,'lock_released':False,'NVML_contexts_cleared':False,'EXCLUSIVITY_EVIDENCE_COMPLETE':False}
 child=None;owned={os.getpid()};lock=None;held=None;handle=None
 def snapshot(phase):
  live={os.getpid()}
  if child is not None:
   try:live.update([child.pid]+[p.pid for p in psutil.Process(child.pid).children(recursive=True)])
   except psutil.NoSuchProcess:pass
  owned.update(live);rss=0
  for pid in live:
   try:rss+=psutil.Process(pid).memory_info().rss
   except psutil.NoSuchProcess:pass
  processes={}
  for kind,fn in [('compute',nv.nvmlDeviceGetComputeRunningProcesses),('graphics',nv.nvmlDeviceGetGraphicsRunningProcesses)]:
   for info in fn(handle):
    item=processes.setdefault(info.pid,{'pid':info.pid,'kinds':[],'usedGpuMemory':info.usedGpuMemory});item['kinds'].append(kind)
  external=[];unknown=[];ownmem=0
  for pid,item in processes.items():
   if pid not in owned:external.append(pid)
   if not psutil.pid_exists(pid) or item['usedGpuMemory'] is None or item['usedGpuMemory']==nv.NVML_VALUE_NOT_AVAILABLE:unknown.append(pid)
   elif pid in owned:ownmem+=item['usedGpuMemory']
  state='UNKNOWN' if unknown else 'OWN_LIVE_PID' if processes and not external else 'EXTERNAL_GPU_PID' if external else 'EMPTY'
  row={'wall_time':time.time(),'held_seconds':time.monotonic()-held,'phase':phase,'state':state,'live_own_pids':sorted(live),'gpu_processes':list(processes.values()),'external_gpu_pids':external,'unknown_gpu_pids':unknown,'own_NVML_MiB':ownmem/1024**2,'own_tree_RSS_bytes':rss,'own_new_disk_bytes':disk_bytes()};receipt['samples'].append(row);save(OUT/'GPU_RESOURCE_RECEIPT.json',receipt)
  if external:raise RuntimeError('GPU_RESOURCE_DEFERRED: external GPU PID present')
  if unknown:raise RuntimeError('GPU_EXCLUSIVITY_OBSERVABILITY_NO_GO: unknown NVML PID/memory')
  if ownmem>15400*1024**2:raise RuntimeError('BUDGET_STOP: own NVML VRAM cap')
  if rss>16*1024**3:raise RuntimeError('BUDGET_STOP: tree RSS cap')
  if row['own_new_disk_bytes']>3*1024**3:raise RuntimeError('BUDGET_STOP: new disk cap')
  if time.time()-START>2675:raise RuntimeError('BUDGET_STOP: whole Goal deadline with archival reserve')
  if row['held_seconds']>710:raise RuntimeError('BUDGET_STOP: GPU deadline with shutdown reserve')
  return row
 def stop_own():
  if child is not None and child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=3)
 try:
  assert time.time()-START<2400,'G0 consumed run/archival allowance'
  lock=open('/data/c16/locks/c16_gpu_campaign.lock','r')
  try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:
   receipt['status']='GPU_RESOURCE_DEFERRED';receipt['reason']='Nonblocking campaign lock conflict; no wait/poll, no CUDA or model initialization';return
  held=time.monotonic();receipt['lock_acquired']=True;receipt['lock_acquired_utc_epoch']=time.time()
  nv.nvmlInit();receipt['NVML_initialized']=True;handle=nv.nvmlDeviceGetHandleByUUID(UUID);name=nv.nvmlDeviceGetName(handle);receipt['device']={'UUID':nv.nvmlDeviceGetUUID(handle),'name':name,'total_MiB':nv.nvmlDeviceGetMemoryInfo(handle).total/1024**2};assert receipt['device']['UUID']==UUID and '4080' in name
  snapshot('PRE_MODEL_ADMISSION')
  for stage in ['G1','G2']:
   if stage=='G2':
    g1=json.loads((OUT/'raw/G1.json').read_text());assert g1['status']=='PASS';vals=[s['request_gpu_elapsed_ms'] for s in g1['points'][0]['formal_samples']];med=statistics.median(vals);mad=statistics.median(abs(x-med) for x in vals);assert mad/med<=0.05,'G1 stability gate failed';linked=abs(med/354.59820556640625-1)<=0.15
    gate={'G1':'PASS','median_ms':med,'MAD_ms':mad,'MAD_over_median':mad/med,'historical_relative_drift':med/354.59820556640625-1,'historical_link_status':'LINKED_HISTORICAL_TIMING_SCOPE' if linked else 'NEW_NATIVE_ONLY_UNLINKED_TO_HISTORICAL','criterion_frozen_before_run':True};save(OUT/'G1_GATE.json',gate)
    assert any(r.get('status')=='PASS_EXACT_2048' for r in json.loads((OUT/'INPUT_RECEIPT.json').read_text())['inputs'])
   context=P/stage;context.mkdir();(context/'tmp').mkdir();env=os.environ.copy();env.update({'A79_LOCK_OWNER':str(os.getpid()),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','VLLM_ENABLE_V1_MULTIPROCESSING':'0','PYTHONDONTWRITEBYTECODE':'1','TOKENIZERS_PARALLELISM':'false','CUDA_VISIBLE_DEVICES':'0','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','TORCHINDUCTOR_COMPILE_THREADS':'1','VLLM_NO_USAGE_STATS':'1','DO_NOT_TRACK':'1'})
   for key,sub in [('VLLM_CACHE_ROOT','vllm'),('VLLM_CONFIG_ROOT','vllm_config'),('TORCHINDUCTOR_CACHE_DIR','inductor'),('TRITON_CACHE_DIR','triton'),('CUDA_CACHE_PATH','cuda'),('XDG_CACHE_HOME','xdg'),('HF_HOME','hf'),('TORCH_HOME','torch'),('TORCH_EXTENSIONS_DIR','extensions'),('HOME','home'),('TMPDIR','tmp'),('NUMBA_CACHE_DIR','numba')]:env[key]=str(context/sub)
   logfile=(context/'worker.log').open('w');child=subprocess.Popen([sys.executable,str(TOOL/'worker.py'),stage],cwd=ROOT,env=env,stdout=logfile,stderr=subprocess.STDOUT,start_new_session=True);owned.add(child.pid);receipt['GPU_model_initializations']+=1;receipt['children'].append({'stage':stage,'pid':child.pid,'log':str(context/'worker.log'),'started_epoch':time.time()})
   while child.poll() is None:snapshot(stage);time.sleep(2)
   logfile.close();receipt['children'][-1]['exit_code']=child.returncode;receipt['children'][-1]['finished_epoch']=time.time()
   snapshot(stage+'_CHILD_EXIT')
   if child.returncode!=0:raise RuntimeError('CHILD_STOP: inspect preserved raw and private log')
   # Require empty compute/graphics contexts before creating the next fresh context.
   deadline=min(held+716,time.monotonic()+8)
   while True:
    row=snapshot(stage+'_CONTEXT_DRAIN')
    if row['state']=='EMPTY':break
    if time.monotonic()>=deadline:raise RuntimeError('GPU_CONTEXT_NOT_EMPTY_AFTER_CHILD_EXIT')
    time.sleep(1)
  receipt['status']='GPU_PHASES_COMPLETE'
 except BaseException as error:
  receipt['reason']=str(error);receipt['traceback']=traceback.format_exc()
  receipt['status']='GPU_RESOURCE_DEFERRED' if 'GPU_RESOURCE_DEFERRED' in str(error) else 'BUDGET_STOP' if 'BUDGET_STOP' in str(error) else 'ENGINEERING_STOP' if 'CHILD_STOP' in str(error) else 'IDENTITY_OR_INPUT_NO_GO'
  stop_own()
 finally:
  if child is not None:
   receipt['children'][-1]['exit_code']=child.poll()
  if handle is not None and held is not None:
   try:
    compute=nv.nvmlDeviceGetComputeRunningProcesses(handle);graphics=nv.nvmlDeviceGetGraphicsRunningProcesses(handle);remaining={x.pid for x in compute+graphics};receipt['final_GPU_pids']=sorted(remaining);receipt['own_GPU_contexts_cleared']=not bool(remaining & owned);receipt['NVML_contexts_cleared']=not remaining
   except Exception as error:receipt['final_NVML_error']=str(error)
  if held is not None:
   receipt['GPU_lock_held_seconds']=time.monotonic()-held;fcntl.flock(lock.fileno(),fcntl.LOCK_UN);receipt['lock_released']=True
  if lock is not None:lock.close()
  if receipt.get('NVML_initialized'):nv.nvmlShutdown()
  receipt['EXCLUSIVITY_EVIDENCE_COMPLETE']=bool(receipt['GPU_model_initializations']>0 and receipt['lock_released'] and receipt['NVML_contexts_cleared'] and all(c.get('exit_code') is not None for c in receipt['children']) and not any(s['external_gpu_pids'] or s['unknown_gpu_pids'] for s in receipt['samples']))
  receipt['whole_Goal_elapsed_seconds']=time.time()-START;save(OUT/'GPU_RESOURCE_RECEIPT.json',receipt)
  print(json.dumps({k:receipt.get(k) for k in ['status','reason','GPU_model_initializations','GPU_lock_held_seconds','lock_released','EXCLUSIVITY_EVIDENCE_COMPLETE']}),flush=True)
if __name__=='__main__':main()
