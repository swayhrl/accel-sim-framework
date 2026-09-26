#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,json,subprocess,time
from pathlib import Path
ROOT=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r51-r52-lifecycle-v1');H=WT/'util/vm_tlb/awma/r51_r52_lifecycle/harness.py';P=ROOT/'input/R51_TARGET_PAYLOAD.pt';PY='/data/c16/env/c16-py310/bin/python';LOCK='/data/c16/locks/c16_gpu_campaign.lock'
def parse(p):
 out=None
 for x in p.read_text(errors='replace').splitlines():
  if x.startswith('{'):
   try:out=json.loads(x)
   except json.JSONDecodeError:pass
 return out
def main():
 rows=[]
 for arm in ('MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'):
  d=ROOT/'standalone'/arm;d.mkdir(parents=True,exist_ok=False);base=[PY,str(H),'--payload',str(P),'--mode','standalone','--arm',arm]
  lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX);start=time.time()
  try:
   with (d/'canary.stdout').open('w') as so,(d/'canary.stderr').open('w') as se:r=subprocess.run(['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--cuda-graph-trace=node','--sample=none','--output',str(d/'canary'),*base,'--warmups','0','--reps','1'],stdout=so,stderr=se,timeout=300)
   if r.returncode:raise RuntimeError(f'canary rc={r.returncode}')
   with (d/'formal.stdout').open('w') as so,(d/'formal.stderr').open('w') as se:r=subprocess.run([*base,'--warmups','2','--reps','7'],stdout=so,stderr=se,timeout=300)
   if r.returncode:raise RuntimeError(f'formal rc={r.returncode}')
   receipt=parse(d/'formal.stdout');status='COMPLETE' if receipt else 'RECEIPT_MISSING'
  except Exception as e:receipt=None;status='FAILED';(d/'runner_error.txt').write_text(type(e).__name__+': '+str(e)+'\n')
  finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  if (d/'canary.nsys-rep').exists():subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(d/'canary.sqlite'),str(d/'canary.nsys-rep')],check=True,stdout=subprocess.DEVNULL,stderr=(d/'export.stderr').open('w'))
  rows.append({'arm':arm,'status':status,'elapsed_seconds':time.time()-start,'receipt_json':json.dumps(receipt,sort_keys=True) if receipt else ''});print(json.dumps({'arm':arm,'status':status}),flush=True)
 with (ROOT/'BACKGROUND_STANDALONE_RUNS.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 if any(r['status']!='COMPLETE' for r in rows):raise SystemExit(2)
 rec={r['arm']:json.loads(r['receipt_json']) for r in rows};b0=rec['MONOLITHIC']['gpu_timing']['median_ms']
 if b0<0.150:raise SystemExit('R51_NOT_QUALIFIED_NO_LONG_REAL_BACKGROUND')
 for arm,x in rec.items():
  if not x['correctness']['background_bitwise']:raise SystemExit(f'{arm} numeric contract failed')
  if arm!='MONOLITHIC' and not all(x['graph_liveness'][k] for k in ('base_bitwise_reference','changed_graph_bitwise_eager','changed_differs_from_base','restored_bitwise_reference')):raise SystemExit(f'{arm} graph liveness failed')
 print(json.dumps({'status':'STANDALONE_QUALIFIED','monolithic_median_ms':b0,'medians':{a:x['gpu_timing']['median_ms'] for a,x in rec.items()}},sort_keys=True))
if __name__=='__main__':main()
