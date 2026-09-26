#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,json,subprocess,time
from pathlib import Path
ROOT=Path('/data/c16/awma/r51_semantic_requal_v2_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r51-semantic-requal-v2');H=WT/'util/vm_tlb/awma/r51_r52_lifecycle/harness.py';PARSE=WT/'util/vm_tlb/awma/r51_semantic_requal_v2/parse_timeline.py';PAY=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926/input/R51_TARGET_PAYLOAD.pt');PY='/data/c16/env/c16-py310/bin/python';LOCK='/data/c16/locks/c16_gpu_campaign.lock';B0=0.41254401206970215
def receipt(p):
 z=None
 for x in p.read_text(errors='replace').splitlines():
  if x.startswith('{'):
   try:z=json.loads(x)
   except json.JSONDecodeError:pass
 return z
def parse_summary(cmd,log):
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);log.write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(f'parser rc={r.returncode}')
 return json.loads([x for x in r.stdout.splitlines() if x.startswith('{')][-1])
def gpu_run(cmd,so,se,timeout=300):
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:return subprocess.run(cmd,stdout=so.open('w'),stderr=se.open('w'),timeout=timeout)
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
def main():
 sem={r['arm']:r['output_sha256'] for r in csv.DictReader((ROOT/'SEMANTIC_EQUIVALENCE_RESULTS.tsv').open(),delimiter='\t') if r['step']=='16'};rows=[]
 for arm in ('MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'):
  short={'MONOLITHIC':'B0','CHUNKED_GRAPH_8':'B8','CHUNKED_GRAPH_32':'B32'}[arm]
  for arr in (.25,.50):
   pid=f'{short}_A{int(arr*100)}';d=ROOT/'timeline'/pid;d.mkdir(parents=True,exist_ok=False);base=[PY,str(H),'--payload',str(PAY),'--mode','overlap','--arm',arm,'--arrival',str(arr),'--monolithic-median-ms',str(B0)]
   can=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--cuda-graph-trace=node','--sample=none','--output',str(d/'canary'),*base,'--warmups','0','--reps','1'];r=gpu_run(can,d/'canary.stdout',d/'canary.stderr')
   if r.returncode:raise RuntimeError(f'{pid} canary rc={r.returncode}')
   subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(d/'canary.sqlite'),str(d/'canary.nsys-rep')],check=True,stdout=subprocess.DEVNULL,stderr=(d/'canary_export.stderr').open('w'))
   adjust=0.0;chosen=None
   for attempt in (0,1):
    rd=d if attempt==0 else ROOT/'timeline'/(pid+'_RETRY1');rd.mkdir(parents=True,exist_ok=attempt==0);formal=['nsys','profile','--force-overwrite=true','--trace=cuda,nvtx','--cuda-graph-trace=node','--sample=none','--output',str(rd/'formal'),*base,'--spin-adjust-us',str(adjust),'--warmups','2','--reps','7'];r=gpu_run(formal,rd/'formal.stdout',rd/'formal.stderr')
    if r.returncode:raise RuntimeError(f'{pid} formal attempt{attempt} rc={r.returncode}')
    rcpt=receipt(rd/'formal.stdout')
    if not rcpt or not rcpt['correctness']['foreground_bitwise'] or rcpt['correctness']['background_output_sha256']!=sem[short]:raise RuntimeError(f'{pid} output contract mismatch attempt{attempt}')
    subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(rd/'formal.sqlite'),str(rd/'formal.nsys-rep')],check=True,stdout=subprocess.DEVNULL,stderr=(rd/'formal_export.stderr').open('w'))
    summ=parse_summary([PY,str(PARSE),'--sqlite',str(rd/'formal.sqlite'),'--arm',arm,'--arrival',str(arr),'--b0-ms',str(B0),'--out',str(rd/'timeline.tsv')],rd/'parse.log');rows.append({'point_id':pid,'attempt':attempt,'arm':arm,'arrival':arr,'spin_adjust_us':adjust,'status':'VALID' if summ['all_valid'] else 'INVALID_ARRIVAL','summary_json':json.dumps(summ,sort_keys=True),'receipt_json':json.dumps(rcpt,sort_keys=True),'directory':str(rd)})
    if summ['all_valid']:chosen=rd;break
    adjust+=(arr-summ['actual_fraction_median'])*B0*1000
   if chosen is None:raise RuntimeError(f'{pid} arrival invalid after retry')
   print(json.dumps({'point':pid,'status':'VALID','directory':str(chosen)}),flush=True)
 with (ROOT/'OVERLAP_RUNS.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
