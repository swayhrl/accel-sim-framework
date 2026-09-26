#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,json,os,subprocess,time,torch
from pathlib import Path
ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-p1-p2-native-qualification-v1');HARNESS=WT/'util/vm_tlb/awma/p1_p2_native/p1_p2_native_harness.py';PY='/data/c16/env/c16-py310/bin/python';LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock');PAYLOAD=ROOT/'input/QWEN25_0P5B_P1_P2_QKV.pt'
def smi():
 q=['nvidia-smi','--query-gpu=timestamp,temperature.gpu,clocks.current.sm,power.draw,clocks_throttle_reasons.active','--format=csv,noheader,nounits'];return subprocess.check_output(q,text=True).strip()
def parse_stdout(p):
 r=None
 for line in p.read_text(errors='replace').splitlines():
  if line.startswith('{'):
   try:r=json.loads(line)
   except json.JSONDecodeError:pass
 return r
def write(rows):
 keys=sorted({k for r in rows for k in r})
 with (ROOT/'RUN_MATRIX.partial.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)
def one(spec,rows):
 for old in rows:
  if (old.get('point_id')==spec['point_id'] or old.get('point_id','').startswith(spec['point_id']+'_R')) and old.get('status')=='COMPLETE':return old
 pid=spec['point_id'];d=ROOT/'runs'/pid
 if d.exists() and (d/'formal.stdout').exists() and (d/'canary.sqlite').exists():
  receipt=parse_stdout(d/'formal.stdout')
  if receipt:
   row={**spec,'args_json':json.dumps(spec.get('args',[]),default=str),'status':'COMPLETE','elapsed_seconds':'RECOVERED_AFTER_RECEIPT_SERIALIZATION_FIX','smi_before':'RECORDED_IN_FAILED_PARENT_PROCESS_NOT_SERIALIZED','smi_after':'RECORDED_IN_FAILED_PARENT_PROCESS_NOT_SERIALIZED','receipt_json':json.dumps(receipt,sort_keys=True),'engineering_recovery':'GPU run not repeated; recovered complete formal stdout and canary sqlite'};rows.append(row);write(rows);print(json.dumps({'point':pid,'status':'COMPLETE_RECOVERED'}),flush=True);return row
 if d.exists():pid=pid+'_R1';spec={**spec,'point_id':pid,'supersedes':str(d)};d=ROOT/'runs'/pid
 d.mkdir(parents=True,exist_ok=False);base=[PY,str(HARNESS),'--candidate',spec['candidate'],'--payload',str(PAYLOAD),'--arm',spec['arm'],'--output',str(d/'target_output.pt')]
 for k,v in spec.get('args',[]):base += [k,str(v)]
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX);pre=smi();start=time.time()
 try:
  can=base+['--warmups','0','--reps','1'];ns=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--sample=none','--output',str(d/'canary'),*can]
  with (d/'canary.stdout').open('w') as so,(d/'canary.stderr').open('w') as se:c=subprocess.run(ns,stdout=so,stderr=se,timeout=300)
  if c.returncode:raise RuntimeError(f'canary rc={c.returncode}')
  subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(d/'canary.sqlite'),str(d/'canary.nsys-rep')],check=True,stdout=subprocess.DEVNULL,stderr=(d/'export.stderr').open('w'))
  formal=base+['--warmups','2','--reps','7']
  with (d/'formal.stdout').open('w') as so,(d/'formal.stderr').open('w') as se:f=subprocess.run(formal,stdout=so,stderr=se,timeout=300)
  if f.returncode:raise RuntimeError(f'formal rc={f.returncode}')
  receipt=parse_stdout(d/'formal.stdout');status='COMPLETE' if receipt else 'RECEIPT_MISSING'
 except Exception as e:receipt=None;status='FAILED';(d/'runner_error.txt').write_text(type(e).__name__+': '+str(e)+'\n')
 finally:post=smi();fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 row={**spec,'args_json':json.dumps(spec.get('args',[]),default=str),'status':status,'elapsed_seconds':time.time()-start,'smi_before':pre,'smi_after':post,'receipt_json':json.dumps(receipt,sort_keys=True) if receipt else ''};rows.append(row);write(rows);print(json.dumps({'point':pid,'status':status}),flush=True);return row
def main():
 ROOT.mkdir(parents=True,exist_ok=True);rows=list(csv.DictReader((ROOT/'RUN_MATRIX.partial.tsv').open(),delimiter='\t')) if (ROOT/'RUN_MATRIX.partial.tsv').exists() else []
 for arm in ('STOCK_FLASH_SDPA','PADDED_B4_FLASH_SDPA'):
  for b in (1,4):
   r=one({'point_id':f'P1_{arm}_B{b}','candidate':'P1','arm':arm,'args':[('--batch',b)]},rows)
   if r['status']!='COMPLETE':raise SystemExit(f"P1 point failed {r['point_id']}")
 stock1=torch.load(ROOT/'runs/P1_STOCK_FLASH_SDPA_B1/target_output.pt',map_location='cpu',weights_only=True);stock4=torch.load(ROOT/'runs/P1_STOCK_FLASH_SDPA_B4/target_output.pt',map_location='cpu',weights_only=True)
 if not torch.equal(stock1,stock4):
  for b in (1,4):
   r=one({'point_id':f'P1_FIXED_SPLIT_TRITON_256_B{b}','candidate':'P1','arm':'FIXED_SPLIT_TRITON_256','args':[('--batch',b)]},rows)
   if r['status']!='COMPLETE':raise SystemExit(f"P1 diagnostic failed {r['point_id']}")
 for top in (256,128):
  idx=ROOT/'runs'/f'P2_ONLINE_EAGER_K{top}'/'paired_indices.pt'
  online=one({'point_id':f'P2_ONLINE_EAGER_K{top}','candidate':'P2','arm':'ONLINE_EAGER','args':[('--top-pages',top),('--indices',idx)]},rows)
  if online['status']!='COMPLETE':raise SystemExit(f'P2 online K{top} failed')
  ready=one({'point_id':f'P2_READY_INDEX_K{top}','candidate':'P2','arm':'READY_INDEX','args':[('--top-pages',top),('--indices',idx)]},rows)
  if ready['status']!='COMPLETE':raise SystemExit(f'P2 ready K{top} failed')
  strong=one({'point_id':f'P2_STRONG_COMPILE_FULL_K{top}','candidate':'P2','arm':'STRONG_COMPILE_FULL','args':[('--top-pages',top),('--indices',idx)]},rows)
  if strong['status']!='COMPLETE':
   strong=one({'point_id':f'P2_STRONG_CUDA_GRAPH_K{top}','candidate':'P2','arm':'STRONG_CUDA_GRAPH','args':[('--top-pages',top),('--indices',idx)]},rows)
  if strong['status']!='COMPLETE':print(json.dumps({'p2_strong_baseline':'UNAVAILABLE_AFTER_TWO_SURGICAL_ATTEMPTS','top':top}),flush=True)
 write(rows);os.replace(ROOT/'RUN_MATRIX.partial.tsv',ROOT/'RUN_MATRIX.tsv');print(json.dumps({'points':len(rows),'complete':sum(x['status']=='COMPLETE' for x in rows)},sort_keys=True))
if __name__=='__main__':main()
