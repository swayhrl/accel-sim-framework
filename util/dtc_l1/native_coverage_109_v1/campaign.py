#!/usr/bin/env python3
"""Exclusive, bounded native producer; no simulation, no task preemption."""
import os
import datetime,fcntl,json,os,pathlib,random,subprocess,sys,time
repo=pathlib.Path(__file__).resolve().parents[3];src=pathlib.Path(__file__).parent
root=pathlib.Path(os.environ.get('DTC_NATIVE_ROOT','/data/c16/dtc_native_coverage_109_v1'));raw=root/'raw'
py='/data/c16/env/c16-py310/bin/python';ncu='/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu'
reg=json.loads((repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/PREREGISTRATION.json').read_text())
assert not (raw/'COMMANDS.jsonl').exists(), 'Refusing to overwrite prior campaign; use fresh DTC_NATIVE_ROOT'
env=os.environ.copy();env.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(tag,cmd,extra=None,timeout=180):
 e=env.copy();e.update(extra or {});start=now();t=time.monotonic()
 (raw/'PROGRESS.txt').write_text(f'{start} {tag}\n')
 with (raw/f'{tag}.log').open('w') as out:
  cp=subprocess.run(list(map(str,cmd)),env=e,cwd=root,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
 with (raw/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps(dict(tag=tag,command=list(map(str,cmd)),env_extra=extra,start_utc=start,end_utc=now(),elapsed_s=time.monotonic()-t,returncode=cp.returncode))+'\n')
 if cp.returncode:raise RuntimeError(f'{tag} failed exit={cp.returncode}, see raw log')
 print(tag,'PASS',flush=True)
 return (raw/f'{tag}.log').read_text()
def command(name,action):
 if name.startswith('LayerNorm'):
  return [py,src/'layernorm.py',action,'--rows',name.split('_')[1]],{}
 if name=='SpMV':
  d=root/'assets/parboil/datasets/spmv/small'
  return [root/'bin/spmv','-i',f'{d}/input/1138_bus.mtx,{d}/input/vector.bin','-o',raw/'spmv_actual.out'],{'DTC_ACTION':action}
 return [root/'bin/diagnostic',name,action],{}
def check_spmv(tag):
 run(tag,[py,src/'check_spmv.py',root/'assets/parboil/datasets/spmv/small/output/1138_bus.mtx.out',raw/'spmv_actual.out'])
lock=open('/data/c16/locks/c16_gpu_campaign.lock','a')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:sys.exit('GPU_BUSY_LOCK_HELD: CPU prep retained; no GPU work launched')
try:
 processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
 if processes:sys.exit('GPU_BUSY_COMPUTE_PROCESS: '+processes)
 (raw/'GPU_LOCK_START_UTC.txt').write_text(now()+'\n');(raw/'NVIDIA_SMI_PRE.txt').write_text(subprocess.check_output(['nvidia-smi','-q'],text=True))
 (raw/'PRODUCER_SOURCE_COMMIT.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True))
 names=reg['diagnostic_conditions']+['SpMV','LayerNorm_1024','LayerNorm_8192']
 for name in names:
  cmd,e=command(name,'profile');run('qualify_'+name,cmd,e)
 check_spmv('qualify_SpMV_check')
 for batch in range(7):
  order=names.copy();random.Random(109+batch).shuffle(order)
  for name in order:
   cmd,e=command(name,'timing');run(f'timing_b{batch}_{name}',cmd,e)
   if name=='SpMV':check_spmv(f'timing_b{batch}_SpMV_check')
 metrics=['l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum','l1tex__t_sector_hit_rate.pct','lts__t_sectors_srcunit_tex_op_read.sum','lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum','lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum','dram__bytes_read.sum','dram__bytes_write.sum','smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct','sm__warps_active.avg.pct_of_peak_sustained_active','gpu__time_duration.sum']
 query=(raw/'ncu_supported_metrics.txt').read_text()
 assert all(m in query for m in metrics),'requested metric not in installed supported list'
 (raw/'EXACT_METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
 for name in names:
  cmd,e=command(name,'profile');prefix=raw/f'ncu_{name}'
  run('profile_'+name,[ncu,'--profile-from-start','off','--target-processes','application-only','--replay-mode','application','--cache-control','none','--clock-control','none','--metrics',','.join(metrics),'-o',prefix]+cmd,e,timeout=300)
  text=run('export_'+name,[ncu,'--import',str(prefix)+'.ncu-rep','--csv','--page','raw','--print-units','base'])
  (raw/f'ncu_{name}.csv').write_text(text)
  if name=='SpMV':check_spmv('profile_SpMV_check')
 for name in ['SpMV','LayerNorm_1024','LayerNorm_8192']:
  cmd,e=command(name,'profile');prefix=raw/f'nsys_{name}'
  run('nsys_'+name,['/usr/local/bin/nsys','profile','--trace=cuda,nvtx','--sample=none','--capture-range=cudaProfilerApi','--capture-range-end=stop','-o',prefix]+cmd,e)
  run('nsys_export_'+name,['/usr/local/bin/nsys','export','--type','sqlite','--output',str(prefix)+'.sqlite',str(prefix)+'.nsys-rep'])
 (raw/'NATIVE_CAMPAIGN_COMPLETE').write_text(now()+'\n')
finally:
 (raw/'NVIDIA_SMI_POST.txt').write_text(subprocess.check_output(['nvidia-smi','-q'],text=True));(raw/'GPU_LOCK_END_UTC.txt').write_text(now()+'\n');fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
