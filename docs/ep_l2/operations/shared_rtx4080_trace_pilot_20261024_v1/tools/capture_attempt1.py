#!/usr/bin/env python3
import pathlib,subprocess,json,os,time,fcntl,hashlib,signal,datetime
R=pathlib.Path('/data/c16/rtx4080_asset_pilot_20261024_v1')
T=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-simcompat-v1/util/tracer_nvbit/tracer_tool')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def query(args):return subprocess.check_output(['nvidia-smi']+args,text=True).strip()
def procs():
 s=query(['--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
 return [x.strip() for x in s.splitlines() if x.strip()]
def ticks(pid):return pathlib.Path('/proc/%s/stat'%pid).read_text().split(') ',1)[1].split()[19]
def save(): (R/'evidence/PILOT_RUN_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
def run(cmd,out,env=None,limit=240):
 a={'command':cmd,'start_utc':now(),'output':str(out)}
 with out.open('w') as f:
  p=subprocess.Popen(['nice','-n','15','ionice','-c','2','-n','7']+cmd,cwd=out.parent,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  a.update(pid=p.pid,start_ticks=ticks(p.pid));save();start=time.monotonic()
  while p.poll() is None:
   seen=procs()
   for line in seen:
    pid=int(line.split(',')[0])
    if pid not in [257500,p.pid]:
     a['bounded_stop']='new compute process '+line
   smon=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
   for line in smon.stdout.splitlines():
    parts=line.split()
    if len(parts)>3 and parts[1]=='257500' and parts[3] not in ['-','0']:
     a['bounded_stop']='baseline service GPU activity '+line
   if time.monotonic()-start>limit:a['bounded_stop']='time bound'
   if sum(x.stat().st_size for x in (R/'capture').rglob('*') if x.is_file())>1024**3:a['bounded_stop']='1GiB producer bound'
   if a.get('bounded_stop') and p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   time.sleep(.1)
  a.update(returncode=p.returncode,elapsed_s=time.monotonic()-start,end_utc=now())
 return a
rec={'identity':'CUDA_SAMPLES_DB3EEA_VECTORADD_4M_SM89_PILOT_V1','start_utc':now(),'purpose':'producer correctness/full SASS trace pipeline only; no performance/scientific simulation qualification','policy_deviation':'Independent pilot permits known resident idle ComfyUI; original DTC no-compute assert not changed; parent explicitly authorized cooperative lock +15s idle +abort own process on competing activity','bounds':{'native_processes':1,'capture_processes':1,'capture_wall_s':240,'capture_bytes':1024**3},'gpu':query(['--query-gpu=name,uuid,driver_version,memory.total','--format=csv']),'idle_samples':[],'attempts':[]}
lock=open('/data/c16/locks/c16_gpu_campaign.lock','a')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 rec['baseline_compute']=procs()
 assert all(int(x.split(',')[0])==257500 for x in rec['baseline_compute']),rec['baseline_compute']
 rec['baseline_comfyui_start_ticks']=ticks(257500)
 for i in range(15):
  u=query(['--query-gpu=utilization.gpu','--format=csv,noheader,nounits'])
  pp=procs();rec['idle_samples'].append({'utc':now(),'gpu_utilization':u,'compute':pp});save()
  assert u=='0' and all(int(x.split(',')[0])==257500 for x in pp),'GPU_NOT_IDLE'
  time.sleep(1)
 (R/'capture').mkdir(exist_ok=False)
 rec['attempts'].append(run([str(R/'bin/vectorAdd')],R/'evidence/native.log',limit=60));save()
 assert rec['attempts'][-1]['returncode']==0 and 'Test PASSED' in (R/'evidence/native.log').read_text()
 env=os.environ.copy()
 for key in list(env):
  if key.startswith(('DYNAMIC_','KERNEL_','TRACE_','TOOL_','NVBIT_')) or key in ['CUDA_INJECTION64_PATH','LD_PRELOAD','ACTIVE_FROM_START']:env.pop(key,None)
 env.update(LD_PRELOAD=str(T/'tracer_tool.so')+':libcuda.so.1',TRACES_FOLDER=str(R/'capture'),ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',PATH='/usr/local/cuda-12.8/bin:'+env.get('PATH',''),NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 rec['capture_environment']={k:env[k] for k in ['LD_PRELOAD','TRACES_FOLDER','ACTIVE_FROM_START','TRACE_FILE_COMPRESS','TOOL_COMPRESS','DYNAMIC_KERNEL_RANGE','NVDISASM']}
 rec['attempts'].append(run([str(R/'bin/vectorAdd')],R/'capture/capture.log',env));save()
 assert rec['attempts'][-1]['returncode']==0 and 'Test PASSED' in (R/'capture/capture.log').read_text()
 with (R/'evidence/postprocess.log').open('w') as f:
  cp=subprocess.run([str(T/'traces-processing/post-traces-processing'),str(R/'capture/traces')],stdout=f,stderr=subprocess.STDOUT,timeout=180)
 rec['postprocess_returncode']=cp.returncode
 assert cp.returncode==0
 rec['status']='CAPTURE_POSTPROCESS_PASS'
except Exception as e:
 rec['status']='FAILED_OR_RESOURCE_HOLD_RETAINED';rec['error']=repr(e);raise
finally:
 rec['end_utc']=now();save();fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
print(rec['status'],flush=True)
