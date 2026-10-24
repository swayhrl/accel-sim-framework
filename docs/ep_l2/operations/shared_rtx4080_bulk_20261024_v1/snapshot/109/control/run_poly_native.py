#!/usr/bin/env python3
import pathlib,os,json,subprocess,time,fcntl,re,signal,hashlib,datetime
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
queue=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/manifests/POLYBENCH_QUEUE_V3.json')
jobs=json.loads(queue.read_text());summary=[]
def ticks(pid):return (pathlib.Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]
def query(args):return subprocess.check_output(['nvidia-smi']+args,text=True).strip()
def compute():
 raw=query(['--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
 return [x.strip() for x in raw.splitlines() if x.strip()]
for job in jobs:
 ident='polybench_1_0_'+job['program']
 out=R/'attempts'/ident/'native_attempt001';out.mkdir(parents=True,exist_ok=False)
 rec={'task':job,'attempt':'native_attempt001','output':str(out),'start_unix':time.time(),'gpu':query(['--query-gpu=name,uuid,driver_version','--format=csv'])}
 lock=open('/data/c16/locks/c16_gpu_campaign.lock','a')
 try:
  # Never busy-wait or bypass cooperative lock. A waiting worker owns no GPU.
  waited=0
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:
    if waited>=1800:raise RuntimeError('GPU_LOCK_BUSY_1800S')
    time.sleep(5);waited+=5
  rec['lock_wait_s']=waited;baseline=compute()
  assert all(int(x.split(',')[0])==257500 for x in baseline),baseline
  rec['baseline_compute']=baseline
  if baseline:rec['baseline_service_start_ticks']=ticks(257500)
  idle=[]
  for _ in range(5):
   u=query(['--query-gpu=utilization.gpu','--format=csv,noheader,nounits']);idle.append({'unix':time.time(),'util':u})
   assert u=='0','GPU_NOT_IDLE'
   assert all(int(x.split(',')[0])==257500 for x in compute()),'NEW_COMPUTE_PRESTART'
   time.sleep(1)
  rec['idle_gate']=idle
  assert hashlib.sha256(pathlib.Path(job['argv'][0]).read_bytes()).hexdigest()==job['binary_sha256']
  env=os.environ.copy()
  for k in ['LD_PRELOAD','CUDA_INJECTION64_PATH']:env.pop(k,None)
  with (out/'stdout.log').open('x') as f:
   p=subprocess.Popen(job['argv'],cwd=job['cwd'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:os.nice(15))
   rec.update(pid=p.pid,start_ticks=ticks(p.pid));subprocess.run(['ionice','-c','2','-n','7','-p',str(p.pid)],capture_output=True)
   (out/'NATIVE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');start=time.monotonic()
   while p.poll() is None:
    for line in compute():
     if int(line.split(',')[0]) not in [257500,p.pid]:rec['bounded_stop']='NEW_COMPUTE '+line
    mon=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
    for line in mon.stdout.splitlines():
     t=line.split()
     if len(t)>3 and t[1]=='257500' and t[3] not in ['0','-']:rec['bounded_stop']='RESIDENT_GPU_ACTIVE '+line
    if time.monotonic()-start>job.get('native_timeout_sec',600):rec['bounded_stop']='NATIVE_TIMEOUT'
    if rec.get('bounded_stop') and p.poll() is None:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=10)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    time.sleep(.2)
   rec.update(exit=p.returncode,wall_seconds=time.monotonic()-start)
  text=(out/'stdout.log').read_text(errors='replace')
  passed=p.returncode==0 and re.search(job['correctness']['stdout_regex']+r'\s*(?:\n|$)',text) is not None and not re.search(r'NON.?FINITE|CUDA.*ERROR|MISMATCH',text,re.I)
  rec['status']='NATIVE_CORRECTNESS_PASS' if passed else 'NATIVE_FAILURE_RETAINED'
  rec['stdout_sha256']=hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest()
 except Exception as e:rec['status']='NATIVE_RESOURCE_OR_SETUP_HOLD';rec['error']=repr(e)
 finally:
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 rec['end_unix']=time.time();summary.append(rec)
 (out/'NATIVE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
 (R/'control/POLYBENCH_NATIVE_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(job['program'],rec['status'],rec.get('exit'),flush=True)

