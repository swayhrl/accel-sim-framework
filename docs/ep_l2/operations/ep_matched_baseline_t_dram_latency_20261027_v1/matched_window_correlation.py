#!/usr/bin/env python3
"""Passive, exact-boundary WINDOW_SET/STAGE join. Counts never prorated."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,csv,hashlib
P=pathlib.Path;J=P('/root/data/ep_l2_matched_baseline_t_dram_latency_20261027_v1')
STAGES='L1_ACCESS L1_MISS L1_MERGE L1_MISSQ_BLOCK L1_SEND ICNT_INJECT_ACCEPT ICNT_INJECT_DENY L2_INGRESS FRONTEND_HEAD FRONTEND_DENY FRONTEND_COMMIT TVD_EARLY LOWER_QUEUE_BLOCK L2_MISSQ_BLOCK DRAM_ACCEPT DRAM_RETURN RO_READY_EVENT RESPONSE_ACCEPT DRAM_SERVICE'.split()
def write(p,rows):
 with p.open('x',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 manifest=json.loads((J/'analysis/FINAL_SIX_INPUTS.json').read_text());out=J/'analysis/FINAL_SIX_ACCEPTED';by={};stages=[]
 for c in manifest['cases']:
  raw=P(c['raw_path']);assert hashlib.sha256(raw.read_bytes()).hexdigest()==c['raw_sha256']
  for line in raw.open():
   if not line.startswith('EPL2LIFEV1|WINDOW_STAGE|'):continue
   fields=dict(x.split('=',1)for x in line.strip().split('|')[2:]);counts=list(map(int,fields['c'].split(',')));assert len(counts)==len(STAGES)and int(fields['invalid'])==0
   k=(c['label'],int(fields['slice']),int(fields['begin']),int(fields['end']));row=dict(label=k[0],slice=k[1],begin_L2_tick=k[2],end_L2_tick=k[3],begin_core_cycle=int(fields['begin_gpu']),end_core_cycle=int(fields['end_gpu']),**dict(zip(STAGES,counts)))
   assert k not in by or by[k]==row;by[k]=row
 stages=list(by.values());write(out/'LIFE_WINDOW_STAGE.csv',stages)
 rows=[]
 with(out/'LIFE_WINDOW_SET.csv').open()as f:
  for r in csv.DictReader(f):
   area=list(map(int,r['reserved_area_R0_to_R8'].split(',')));k=(r['label'],int(r['slice']),int(r['begin_L2_tick']),int(r['end_L2_tick']));s=by[k]
   assert int(r['begin_core_cycle'])==s['begin_core_cycle']and int(r['end_core_cycle'])==s['end_core_cycle']
   rows.append(dict(label=k[0],slice=k[1],set=int(r['set']),begin_core_cycle=s['begin_core_cycle'],end_core_cycle=s['end_core_cycle'],positive_reserved_set_L2_ticks=sum(area[1:]),reserved_Tag_L2_tick_area=sum(i*n for i,n in enumerate(area)),all8_reserved_set_L2_ticks=area[8],NEW_UNIQUE=int(r['NEW_UNIQUE']),NEW_WITH_PENDING=int(r['NEW_WITH_PENDING']),NEW_WITH_ELIGIBLE=int(r['NEW_WITH_ELIGIBLE']),REENTER=int(r['REENTER']),same_slice_LOWER_QUEUE_BLOCK=s['LOWER_QUEUE_BLOCK'],same_slice_L2_MISSQ_BLOCK=s['L2_MISSQ_BLOCK'],same_slice_FRONTEND_DENY=s['FRONTEND_DENY'],RAW_FAIL_HEAD=int(r['RAW_FAIL_HEAD']),causal_per_Tag_linkage='NOT_INSTRUMENTED',same_slice_counts_repeated_across_sets='DO_NOT_SUM'))
 write(out/'PER_SET_WINDOW_CORRELATION.csv',rows)
 top=[]
 for label in sorted({r['label']for r in rows}):top.extend(sorted((r for r in rows if r['label']==label),key=lambda r:r['reserved_Tag_L2_tick_area'],reverse=True)[:5])
 write(out/'TOP_RESERVATION_WINDOWS.csv',top)
 print(json.dumps({'status':'EXACT_BOUNDARY_WINDOW_SET_STAGE_CORRELATION_ONLY','stage_windows':len(stages),'set_windows':len(rows),'new_starts':0,'slice_counts_not_attributed_to_individual_set_or_summed_per_set':True}))
if __name__=='__main__':main()
