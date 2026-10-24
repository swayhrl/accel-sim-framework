import fcntl,hashlib,json,os,pathlib,subprocess,time
R=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
A=R/'attempts'/'vector4m_v6_attempt1';A.mkdir(exist_ok=False)
lock=open('/data/c16/locks/c16_gpu_campaign.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,utilization.gpu,memory.used','--format=csv,noheader'],text=True)
(A/'GPU_BEFORE.txt').write_text(gpu)
if 'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59' not in gpu:raise RuntimeError('wrong GPU')
procs=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
(A/'PROCESSES_BEFORE.txt').write_text(procs)
for line in procs.splitlines():
    pid=int(line.split(',')[0]);cmd=pathlib.Path('/proc/%d/cmdline'%pid).read_bytes().replace(b'\0',b' ').decode()
    if 'ComfyUI' not in cmd and 'Comfyui' not in cmd:raise RuntimeError('unknown compute process '+cmd)
for i in range(5):
    util=int(subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu','--format=csv,noheader,nounits'],text=True).strip())
    if util>10:raise RuntimeError('GPU busy')
    time.sleep(3)
tool=R/'producer'/'producer.so';binary=pathlib.Path('/data/c16/rtx4080_asset_pilot_20261024_v1/bin/vectorAdd')
env=os.environ.copy();env.update(PATH='/usr/local/cuda-12.8/bin:'+env['PATH'],NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',LD_PRELOAD=str(tool)+':libcuda.so.1',ACTIVE_FROM_START='1',TOOL_COMPRESS='1',TRACE_FILE_COMPRESS='1',ADA_SEMANTIC_MAP=str(R/'vector-map'/'semantic-map.tsv'))
for x in ['DYNAMIC_KERNEL_RANGE','INSTR_BEGIN','INSTR_END','C16_EXACT_ROOT_FUNCTION_ONLY','ENABLE_SPINLOCK_FAST_FORWARD']:env.pop(x,None)
with open(A/'stdout.log','xb') as so,open(A/'stderr.log','xb') as se:
    t=time.time();p=subprocess.Popen([str(binary)],cwd=A,env=env,stdout=so,stderr=se)
    receipt={'pid':p.pid,'start_ticks':pathlib.Path('/proc/%d/stat'%p.pid).read_text().split()[21],'started':t,'tool_sha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
    try:rc=p.wait(timeout=180)
    except subprocess.TimeoutExpired:p.terminate();rc=p.wait(timeout=20)
receipt.update(exit_code=rc,elapsed=time.time()-t);(A/'EXECUTION.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
