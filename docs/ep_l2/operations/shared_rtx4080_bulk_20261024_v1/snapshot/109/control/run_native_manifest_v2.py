#!/usr/bin/env python3
import pathlib,os,json,subprocess,time,fcntl,re,signal,hashlib,datetime
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
import sys
queue=pathlib.Path(sys.argv[1]);batch=sys.argv[2]
jobs=json.loads(queue.read_text());summary=[]
jobs=[j for j in jobs if j.get('readiness','READY_NATIVE')=='READY_NATIVE']
def ticks(pid):return (pathlib.Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]
def query(args):return subprocess.check_output(['nvidia-smi']+args,text=True).strip()
def compute():
 raw=query(['--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
 return [x.strip() for x in raw.splitlines() if x.strip()]
for job in jobs:
 ident=re.sub(r'[^a-zA-Z0-9_.-]+','_',job['suite']+'_'+job['version']+'_'+job['program'])+'_'+hashlib.sha256(json.dumps(job,sort_keys=True).encode()).hexdigest()[:12]
 out=R/'attempts'/ident/'native_attempt001';out.mkdir(parents=True,exist_ok=False)
 while (R/'control/GPU_QUEUE_PAUSE').exists():time.sleep(5)
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
  assert all(x.split(',')[1].strip()=='/home/huangrulin/workspace/image-lab/envs/comfyui/bin/python' for x in baseline),baseline
  allowed={int(x.split(',')[0]) for x in baseline}
  assert all('/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py' in (pathlib.Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode() for pid in allowed)
  rec['baseline_compute']=baseline
  rec['baseline_service_start_ticks']={str(pid):ticks(pid) for pid in allowed}
  idle=[];stable=0;waitstart=time.monotonic()
  while stable<15:
   u=query(['--query-gpu=utilization.gpu','--format=csv,noheader,nounits']);idle.append({'unix':time.time(),'util':u})
   stable=stable+1 if u=='0' else 0
   assert time.monotonic()-waitstart<120,'NO_15S_IDLE_WINDOW_IN_120S'
   assert all(int(x.split(',')[0]) in allowed for x in compute()),'NEW_COMPUTE_PRESTART'
   time.sleep(1)
  rec['idle_gate']=idle
  assert hashlib.sha256(pathlib.Path(job['argv'][0]).read_bytes()).hexdigest()==job['binary_sha256']
  env=os.environ.copy();env.update(job.get('env',{}));env['PYTHONDONTWRITEBYTECODE']='1'
  for k in ['LD_PRELOAD','CUDA_INJECTION64_PATH']:env.pop(k,None)
  with (out/'stdout.log').open('x') as f:
   p=subprocess.Popen(job['argv'],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:os.nice(15))
   rec.update(pid=p.pid,start_ticks=ticks(p.pid));subprocess.run(['ionice','-c','2','-n','7','-p',str(p.pid)],capture_output=True)
   (out/'NATIVE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');start=time.monotonic()
   while p.poll() is None:
    for line in compute():
     if int(line.split(',')[0]) not in allowed|{p.pid}:rec['bounded_stop']='NEW_COMPUTE '+line
    mon=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
    for line in mon.stdout.splitlines():
     t=line.split()
     if len(t)>3 and t[1].isdigit() and int(t[1]) in allowed and t[3] not in ['0','-']:rec['bounded_stop']='RESIDENT_GPU_ACTIVE '+line
    if sum(x.stat().st_size for x in out.rglob('*') if x.is_file())>8*1024**3:rec['bounded_stop']='8GiB_NATIVE_OUTPUT_BOUND'
    if time.monotonic()-start>job.get('native_timeout_sec',600):rec['bounded_stop']='NATIVE_TIMEOUT'
    if rec.get('bounded_stop') and p.poll() is None:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=10)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    time.sleep(.2)
   rec.update(exit=p.returncode,wall_seconds=time.monotonic()-start)
  text=(out/'stdout.log').read_text(errors='replace')
  if 'postcheck_command' in job['correctness']:
   check=[x.replace('{attempt}',str(out)) for x in job['correctness']['postcheck_command']]
   c=subprocess.run(check,cwd=out,env=env,capture_output=True,text=True,timeout=job['correctness'].get('postcheck_timeout_sec',180))
   (out/'correctness.log').write_text(c.stdout+c.stderr)
   rec['postcheck']={'command':check,'exit':c.returncode,'stdout_sha256':hashlib.sha256((out/'correctness.log').read_bytes()).hexdigest()}
   passed=p.returncode==0 and c.returncode==0 and re.search(job['correctness'].get('postcheck_stdout_regex','Pass'),c.stdout) is not None
  else:
   passed=p.returncode==0 and re.search(job['correctness']['stdout_regex']+r'\s*(?:\n|$)',text) is not None and not re.search(r'NON.?FINITE|CUDA.*ERROR|MISMATCH',text,re.I)
  rec['status']='NATIVE_CORRECTNESS_PASS' if passed else 'NATIVE_FAILURE_RETAINED'
  rec['stdout_sha256']=hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest()
 except Exception as e:rec['status']='NATIVE_RESOURCE_OR_SETUP_HOLD';rec['error']=repr(e)
 finally:
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 rec['end_unix']=time.time();summary.append(rec)
 (out/'NATIVE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
 (R/('control/NATIVE_BATCH_'+batch+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
 print(job['program'],rec['status'],rec.get('exit'),flush=True)

