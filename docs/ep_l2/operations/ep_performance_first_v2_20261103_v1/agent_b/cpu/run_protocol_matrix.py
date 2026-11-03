from pathlib import Path
import subprocess,json,time,os,resource,hashlib
C=Path(__file__).resolve().parent;rows=[]
def cap():
 os.sched_setaffinity(0,{28});os.nice(10);resource.setrlimit(resource.RLIMIT_AS,(2<<30,2<<30));resource.setrlimit(resource.RLIMIT_CPU,(30,30));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
cases=[(m,'normal')for m in [850,1020,1132,1275,1700]]+[(m,c)for m in [1275,1700]for c in ['dual','queue_full','pinned','stale_uid','wrong_address','return_full']]
for mhz,case in cases:
 cfg=C/f'cpu_WV_{mhz}.config'
 if case=='return_full':
  text=cfg.read_text().replace('-gpgpu_dram_return_queue_size 192','-gpgpu_dram_return_queue_size 4').replace('-gpgpu_dram_partition_queues 64:128:64:64','-gpgpu_dram_partition_queues 64:128:1:64');cfg=C/('return_full_'+str(mhz)+'.config');cfg.write_text(text)
 if case=='queue_full':
  text=cfg.read_text().replace('-dram_latency 100','-dram_latency 0');cfg=C/('queue_pressure_'+str(mhz)+'.config');cfg.write_text(text)
 args=[str(C/'new_protocol_matrix'),str(cfg),str(mhz),'360',case];t=time.monotonic();p=subprocess.run(args,capture_output=True,text=True,cwd=C,timeout=35,preexec_fn=cap,env=dict(os.environ,EPL2_LIFE_WIRE='SUMMARY_STAGE',EPL2_DETACH_DIAG='0',EPL2_TAGPRESSURE_DIAG='0',EPL2_TAG_LIFETIME='0',EP_L2_EVENT_TIMELINE='0',OMP_NUM_THREADS='1'))
 label=str(mhz)+'_'+case;out=C/'protocol_runs'/(label+'.stdout');err=C/'protocol_runs'/(label+'.stderr');out.write_text(p.stdout);err.write_text(p.stderr)
 r=dict(mhz=mhz,case=case,returncode=p.returncode,PASS=p.returncode==(86if case in ['stale_uid','wrong_address']else 0),seconds=time.monotonic()-t,last_stdout=p.stdout[-600:],last_stderr=p.stderr[-800:],stdout_ref=dict(path=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest()),stderr_ref=dict(path=str(err),sha256=hashlib.sha256(err.read_bytes()).hexdigest()),fixture_config=str(cfg));rows.append(r);print(json.dumps({k:v for k,v in r.items()if k in ['mhz','case','returncode','PASS','last_stdout','last_stderr']}))
x=dict(schema='EP_CROSS_CLOCK_NEW_SOURCE_REAL_WB_PROTOCOL_MATRIX_V1',status='PASS'if all(r['PASS']for r in rows)else'PARTIAL',rows=rows,passed=sum(r['PASS']for r in rows),total=len(rows),new_source_core='862376f62ab19f9a677abe31c6a422028b44fcd0',model_starts=0,Trace_body_reads=0)
(C/'CPU_PROTOCOL_AND_FREQUENCY_MATRIX.json').write_text(json.dumps(x,indent=2)+'\n')
