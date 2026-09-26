#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,json,os,subprocess,time
from pathlib import Path
ROOT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926')
BIN=ROOT/'bin/model_derived_uvm';LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock');CAP=20*1024**3
def host_available():
 for line in Path('/proc/meminfo').read_text().splitlines():
  if line.startswith('MemAvailable:'):return int(line.split()[1])*1024
def gpu_free():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
def write(p,rows):
 keys=sorted({k for r in rows for k in r})
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(rows)
def main():
 kv=list(csv.DictReader((ROOT/'KV_LAYOUT_POINTS.tsv').open(),delimiter='\t'))
 points=[('D1','FULL',16381470720)]+[('D2',x['point_id'],int(x['total_kv_bytes'])) for x in kv]+[('D3','ACTUAL_DECODE8',13838323712)]
 plan=[]
 for pat,pid,b in points:
  for mode in ('M0','M1'):plan.append({'point_id':f'{pat}_{pid}_{mode}','pattern':pat,'layout_point':pid,'mode':mode,'allocated_bytes':b,'cold_runs':1,'immediate_repeat_runs':1,'status':'PLANNED'})
 write(ROOT/'RUN_MATRIX_PREREG.tsv',plan);results=[]
 for row in plan:
  d=ROOT/'runs'/row['point_id'];d.mkdir(parents=True,exist_ok=False);hav=host_available();gf=gpu_free()
  if int(row['allocated_bytes'])>CAP or hav<int(row['allocated_bytes'])+8*1024**3:
   results.append({**row,'status':'SAFETY_BLOCKED','host_available_before':hav,'gpu_free_before':gf});write(ROOT/'RUN_MATRIX.partial.tsv',results);continue
  lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
  cmd=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--sample=none','--output',str(d/'profile'),str(BIN),'--pattern',row['pattern'],'--point',row['layout_point'],'--mode',row['mode'],'--bytes',str(row['allocated_bytes']),'--root',str(ROOT),'--out',str(d)]
  start=time.time()
  try:
   with (d/'stdout.log').open('w') as so,(d/'stderr.log').open('w') as se:r=subprocess.run(cmd,stdout=so,stderr=se,timeout=1200)
   rc=r.returncode;status='COMPLETE' if rc==0 else 'FAILED'
  except subprocess.TimeoutExpired:rc=124;status='RUNTIME_CAP_REACHED'
  finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  if (d/'profile.nsys-rep').exists():
   with (d/'export.stderr').open('w') as se:subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(d/'profile.sqlite'),str(d/'profile.nsys-rep')],stdout=subprocess.DEVNULL,stderr=se)
  receipt={}
  for line in (d/'stdout.log').read_text(errors='replace').splitlines():
   if line.startswith('{'):
    try:receipt=json.loads(line)
    except json.JSONDecodeError:pass
  results.append({**row,'status':status,'returncode':rc,'elapsed_seconds':time.time()-start,'host_available_before':hav,'host_available_after':host_available(),'gpu_free_before':gf,'gpu_free_after':gpu_free(),'receipt_json':json.dumps(receipt,sort_keys=True)})
  write(ROOT/'RUN_MATRIX.partial.tsv',results);print(json.dumps({'finished':row['point_id'],'status':status,'elapsed':time.time()-start}),flush=True)
 write(ROOT/'RUN_MATRIX.tsv',results)
 print(json.dumps({'points':len(plan),'statuses':{s:sum(x['status']==s for x in results) for s in sorted(set(x['status'] for x in results))}},sort_keys=True))
if __name__=='__main__':main()
