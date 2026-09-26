#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,json,os,subprocess,time
from pathlib import Path
ROOT=Path('/data/c16/awma/uvm_oversubscription_pilot_20260926'); BIN=ROOT/'uvm_pilot'; LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock'); CAP=20*1024**3
def host_available():
 for line in Path('/proc/meminfo').read_text().splitlines():
  if line.startswith('MemAvailable:'):return int(line.split()[1])*1024
def gpu_total():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.total','--format=csv,noheader,nounits'],text=True).strip())*1024**2
def gpu_free():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
def main():
 V=gpu_total(); ratios=[('R0',.75),('R1',.95),('R2',1.10),('R3',1.30)]; rows=[]
 for pat in ('P1','P2','P3'):
  for rid,r in ratios:
   b=min(int(V*r)//4096*4096,CAP)
   for mode in ('M0','M1'):
    planned='NOT_APPLICABLE_OVERSUBSCRIBED' if mode=='M1' and b>V else 'PLANNED'
    rows.append({'point_id':f'{pat}_{rid}_{mode}','pattern':pat,'ratio_id':rid,'target_ratio':r,'allocated_bytes':b,'actual_ratio':b/V,'mode':mode,'planned_status':planned,'cold_runs':1,'repeat_runs':1,'measured_run_cap_seconds':180,'host_headroom_required_bytes':8*1024**3})
 prereg=ROOT/'MATRIX_PREREG.tsv'
 with prereg.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 results=[]
 for row in rows:
  point=ROOT/'runs'/row['point_id']; point.mkdir(parents=True,exist_ok=False)
  if row['planned_status']!='PLANNED':results.append({**row,'status':row['planned_status'],'returncode':'','host_available_before':host_available(),'gpu_free_before':gpu_free()});continue
  hav=host_available();gfree=gpu_free()
  if hav<int(row['allocated_bytes'])+8*1024**3:results.append({**row,'status':'HOST_SAFETY_BLOCKED','returncode':'','host_available_before':hav,'gpu_free_before':gfree});continue
  if row['mode']=='M1' and int(row['allocated_bytes'])>gfree:results.append({**row,'status':'NOT_APPLICABLE_GPU_FREE_LIMIT','returncode':'','host_available_before':hav,'gpu_free_before':gfree});continue
  lock=open(LOCK,'w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  cmd=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx,osrt','--sample=none','--output',str(point/'profile'),str(BIN),'--pattern',row['pattern'],'--mode',row['mode'],'--bytes',str(row['allocated_bytes']),'--out',str(point)]
  start=time.time()
  try:
   with (point/'stdout.log').open('w') as so,(point/'stderr.log').open('w') as se:r=subprocess.run(cmd,stdout=so,stderr=se,timeout=420)
   rc=r.returncode;status='COMPLETE' if rc==0 else ('PREFETCH_NOT_APPLICABLE_RUNTIME' if rc==4 else 'FAILED')
  except subprocess.TimeoutExpired:rc=124;status='RUNTIME_CAP_REACHED'
  finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  if (point/'profile.nsys-rep').exists():
   subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(point/'profile.sqlite'),str(point/'profile.nsys-rep')],stdout=subprocess.DEVNULL,stderr=(point/'export.stderr').open('w'))
  receipt={}
  for line in (point/'stdout.log').read_text(errors='replace').splitlines():
   if line.startswith('{'):
    try:receipt=json.loads(line)
    except json.JSONDecodeError:pass
  results.append({**row,'status':status,'returncode':rc,'elapsed_seconds':time.time()-start,'host_available_before':hav,'host_available_after':host_available(),'gpu_free_before':gfree,'gpu_free_after':gpu_free(),'receipt_json':json.dumps(receipt,sort_keys=True)})
  with (ROOT/'RUN_MATRIX.partial.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=sorted({k for x in results for k in x}),delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(results)
 with (ROOT/'RUN_MATRIX.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=sorted({k for x in results for k in x}),delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(results)
 print(json.dumps({'physical_vram_bytes':V,'points':len(rows),'complete':sum(x['status']=='COMPLETE' for x in results),'statuses':{s:sum(x['status']==s for x in results) for s in sorted(set(x['status'] for x in results))}},sort_keys=True))
if __name__=='__main__':main()
