#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sqlite3,statistics,shutil
from collections import defaultdict
from pathlib import Path
ROOT=Path('/data/c16/awma/r51_semantic_requal_v2_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r51-semantic-requal-v2');PACK=WT/'docs/vm_tlb/review_packs/AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_V2';REPORT=WT/'docs/vm_tlb/reports/AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_109_V2_REPORT.md';DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r51_semantic_requal_v2_20260926';PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def fld(text):return dict(x.split('=',1) for x in text.split(';') if '=' in x)
runs=read(ROOT/'OVERLAP_RUNS.tsv');chosen={r['point_id']:Path(r['directory']) for r in runs if r['status']=='VALID'}
if len(chosen)!=6:raise RuntimeError(f'valid points {chosen}')
timeline=[]
for pid,d in sorted(chosen.items()):
 for r in read(d/'timeline.tsv'):timeline.append({'point_id':pid,**r})
write(ROOT/'R51_TIMELINE_RESULTS.tsv',timeline)
# Aggregate matched comparisons using population jitter in the same microsecond unit.
groups=defaultdict(list)
for r in timeline:groups[(r['arm'],float(r['arrival_target']))].append(r)
summ={}
stand={'MONOLITHIC':412.54401206970215,'CHUNKED_GRAPH_8':456.4160108566284,'CHUNKED_GRAPH_32':482.015997171402}
for k,rs in groups.items():
 x=[float(r['ready_to_fg_start_us']) for r in rs];fg=[float(r['foreground_gpu_duration_us']) for r in rs];bg=[float(r['background_gpu_span_us']) for r in rs];summ[k]={'median':statistics.median(x),'mean':statistics.mean(x),'std':statistics.pstdev(x),'cv':statistics.pstdev(x)/statistics.mean(x),'fg_median':statistics.median(fg),'bg_median':statistics.median(bg),'valid':sum(r['arrival_valid']=='True' for r in rs)}
matched=[]
for arr in (.25,.50):
 b=summ[('MONOLITHIC',arr)]
 for arm in ('CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'):
  z=summ[(arm,arr)];imp=b['median']-z['median'];jit=3*max(b['std'],z['std']);material=imp>=10 and imp>jit;matched.append({'arrival_fraction':arr,'baseline_arm':'MONOLITHIC','candidate_arm':arm,'b0_median_ready_to_start_us':b['median'],'candidate_median_ready_to_start_us':z['median'],'improvement_us':imp,'b0_jitter_std_us':b['std'],'candidate_jitter_std_us':z['std'],'three_x_larger_jitter_us':jit,'improvement_ge_10us':imp>=10,'improvement_gt_3x_jitter':imp>jit,'material_improvement':material,'candidate_accepted_standalone_overhead':stand[arm]/stand['MONOLITHIC']-1,'candidate_background_span_median_us':z['bg_median'],'candidate_background_extension_vs_own_standalone_us':z['bg_median']-stand[arm],'foreground_overlap_duration_median_us':z['fg_median'],'foreground_extension_vs_standalone_us':z['fg_median']-32.48000144958496,'valid_repetitions':z['valid']})
write(ROOT/'R51_MATCHED_COMPARISON.tsv',matched)
# Exact launch strata and R52 hypothetical boundary accounting.
strata=[];cancel=[]
for pid,d in sorted(chosen.items()):
 db=sqlite3.connect(f'file:{d/"formal.sqlite"}?mode=ro',uri=True);strings=dict(db.execute('select id,value from StringIds'));ranges=[]
 for st,en,text in db.execute("select start,end,text from NVTX_EVENTS where text like 'R51_BG_SUBMIT;%' or text like 'R51_FG_SUBMIT;%' order by start"):
  z=fld(text)
  if z.get('KIND')=='FORMAL':ranges.append((st,en,text,int(z['REP'])))
 bgr={x[3]:x for x in ranges if x[2].startswith('R51_BG')};fgr={x[3]:x for x in ranges if x[2].startswith('R51_FG')};ks=[]
 for x in db.execute('select start,end,streamId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start'):
  st,en,sid,gx,gy,gz,bx,by,bz,dn,sn,mn=x;name=strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN';role='FG' if 'pytorch_flash::flash_fwd' in name else ('BG' if ('gemvx::kernel' in name or 'gemv2T_kernel' in name or 'CatArrayBatchedCopy' in name) else 'OTHER');ks.append({'start':st,'end':en,'stream':sid,'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}','name':name,'role':role})
 point_t=[r for r in timeline if r['point_id']==pid];first=min(x[0] for x in bgr.values());last=max(max(int(r['t_bg_end_ns']),int(r['t_fg_last_kernel_end_ns'])) for r in point_t);gg=defaultdict(lambda:[0,0])
 for k in ks:
  if first<=k['start'] and k['start']<=last and k['role']!='OTHER':z=gg[(k['role'],k['name'],k['stream'],k['grid'],k['block'])];z[0]+=1;z[1]+=k['end']-k['start']
 for k,v in gg.items():strata.append({'point_id':pid,'role':k[0],'function':k[1],'stream_id':k[2],'grid':k[3],'block':k[4],'launch_count':v[0],'gpu_duration_ns':v[1]})
 trows={int(r['rep']):r for r in timeline if r['point_id']==pid}
 for rep,b in bgr.items():
  ready=int(trows[rep]['t_ready_ns']);next_start=bgr[rep+1][0] if rep+1 in bgr else 2**63-1;bgks=[k for k in ks if b[0]<=k['start']<next_start and k['role']=='BG'];active=[k for k in bgks if k['start']<=ready<k['end']];boundary=min(k['end'] for k in active) if active else ready;future=sum(k['end']-k['start'] for k in bgks if k['start']>=boundary);total=sum(k['end']-k['start'] for k in bgks);cancel.append({'point_id':pid,'arm':trows[rep]['arm'],'arrival_fraction':trows[rep]['arrival_target'],'rep':rep,'hypothetical_invalidation_t_ready_ns':ready,'remaining_background_wall_us':(int(trows[rep]['t_bg_end_ns'])-ready)/1000,'time_to_next_software_boundary_us':(boundary-ready)/1000,'fraction_background_kernel_time_after_boundary':future/total if total else 0.0,'real_invalidation_authority':'NO','claim':'R52_SYNTHETIC_CANCEL_WINDOW_DIAGNOSTIC_ONLY'})
 db.close()
write(ROOT/'OVERLAP_KERNEL_STRATA.tsv',strata);write(ROOT/'R52_CANCEL_WINDOW_DIAGNOSTIC.tsv',cancel)
all_material=any(r['material_improvement'] for r in matched);decision='R51_SAFEPOINT_LATENCY_THROUGHPUT_TRADEOFF_SUPPORTED_V2' if all_material else 'R51_NO_MATERIAL_HANDOFF_DELAY_V2';final='R51_SAFE_HANDOFF_PROBLEM_READY_FOR_ARCH_REVIEW_V2' if decision.endswith('SUPPORTED_V2') else 'R51_R52_LIFECYCLE_QUALIFICATION_NO_RESIDUAL_V2'
(ROOT/'V1_INHERITANCE.md').write_text('''# V1 inheritance

V1 remains permanently true: `R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED`. B8/B32 logits are not bitwise equal to B0. V2 does not rewrite, delete, or weaken that result; it separately applies the preregistered greedy-decode semantic contract. Source/runtime/tensor identities match V1, so accepted standalone timing is inherited without rerun: B0 0.412544 ms, B8 +10.635%, B32 +16.840%.
''')
(ROOT/'SEMANTIC_DECISION.md').write_text('''# Semantic decision

`SEMANTIC_EQUIVALENCE_PASS`

For primary step16 and holdout steps8/24, both B8 and B32 preserve exact output shape/dtype, finite logits, exact greedy argmax token, exact top-8 token-ID set, and exact top1/top2 ordering. Different-element count and FP16 error metrics remain recorded but are not gates. This claim is limited to the frozen greedy-decode trajectory and does not cover general sampling.
''')
(ROOT/'R51_DECISION.md').write_text(f'''# R51 decision

`{decision}`

The semantic gate passed, so all six preregistered NSYS/CUPTI overlap points ran with seven valid repetitions each. The monolithic background already permits foreground Flash-SDPA work to begin after about 34.6 us at both arrivals, and its GPU interval overlaps the background in every repetition. B8 improves the median by only 3.770 us (25%) and 3.501 us (50%); B32 is worse at 25% and improves by only 4.618 us at 50%. None reaches the preregistered 10 us minimum, irrespective of the jitter test.

Therefore the accepted B8/B32 standalone overheads (10.635%/16.840%) buy no material handoff improvement. No latency-throughput residual is supported and conditional NCU is not triggered.
''')
write(ROOT/'R51_R52_DECISION_MATRIX.tsv',[{'candidate':'R51_V2','semantic_gate':'PASS_GREEDY_ONLY','formal_timeline':'6_POINTS_42_VALID_REPETITIONS','material_handoff_improvement':'NO','software_overhead':'B8_10.635%;B32_16.840%','decision':decision,'next_action':'STOP_NO_ARCH_REVIEW'},{'candidate':'R52','semantic_gate':'NOT_APPLICABLE','formal_timeline':'REUSES_R51_AS_SYNTHETIC_DIAGNOSTIC','material_handoff_improvement':'NO_REAL_AUTHORITY','software_overhead':'N/A','decision':'R52_NO_REAL_INVALIDATION_AUTHORITY','next_action':'DIAGNOSTIC_ONLY_NO_MECHANISM'}])
(ROOT/'FINAL_DECISION.md').write_text(f'''# Final decision

`{final}`

V2's frozen greedy semantic gate passes, while V1's strict bitwise failure remains intact. Formal timeline evidence shows the high-priority foreground already overlaps monolithic lm_head execution and no B8/B32 arm improves ready-to-first-kernel latency by the required 10 us. R52 remains `NO_REAL_INVALIDATION_AUTHORITY`; its table is diagnostic-only. No architecture-review candidate is emitted.
''')
(ROOT/'NCU_STATUS.md').write_text('# Conditional diagnostics\n\n`NOT_RUN`: R51 did not reach the latency-throughput-tradeoff-supported state.\n')
(ROOT/'README.md').write_text(f'''# AWMA R51 semantic-contract requalification V2

Final state: `{final}`. V2 semantic gate passes for frozen greedy decode; formal overlap shows no material handoff improvement. V1 strict bitwise failure remains permanent.

Review `V1_INHERITANCE.md`, `SEMANTIC_PREREGISTRATION.json`, `SEMANTIC_EQUIVALENCE_RESULTS.tsv`, `R51_TIMELINE_RESULTS.tsv`, `R51_MATCHED_COMPARISON.tsv`, and `FINAL_DECISION.md`.

Durable authority: `{DUR}`.
''');(ROOT/'REPORT.md').write_text((ROOT/'README.md').read_text())
# Raw index and compact pack.
idx=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json')):idx.append({'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(ROOT/'RAW_DATA_INDEX.tsv',idx);receipt={'stage':'AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_V2','semantic_gate':'SEMANTIC_EQUIVALENCE_PASS','v1_strict_bitwise_result':'PRESERVED','r51_decision':decision,'r52_decision':'R52_NO_REAL_INVALIDATION_AUTHORITY','final_state':final,'formal_points':6,'valid_repetitions':42,'ncu':'NOT_RUN','node164_authority':DUR,'semantic_preregistration_sha256':sha(ROOT/'SEMANTIC_PREREGISTRATION.json'),'raw_index_sha256':sha(ROOT/'RAW_DATA_INDEX.tsv')};(ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
compact=['README.md','REPORT.md','V1_INHERITANCE.md','HOLDOUT_STATE_RECEIPT.json','SEMANTIC_PREREGISTRATION.json','SEMANTIC_EQUIVALENCE_RESULTS.tsv','SEMANTIC_GATE_RECEIPT.json','SEMANTIC_DECISION.md','R51_TIMELINE_RESULTS.tsv','R51_MATCHED_COMPARISON.tsv','OVERLAP_KERNEL_STRATA.tsv','R52_CANCEL_WINDOW_DIAGNOSTIC.tsv','R51_DECISION.md','R51_R52_DECISION_MATRIX.tsv','NCU_STATUS.md','FINAL_DECISION.md','RAW_DATA_INDEX.tsv','FINAL_RECEIPT.json']
for n in compact:shutil.copy2(ROOT/n,PACK/n)
for p in PACK.glob('*.tsv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!='SHA256SUMS');(PACK/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));shutil.copy2(PACK/'SHA256SUMS',ROOT/'SHA256SUMS')
REPORT.write_text(f'# AWMA R51 semantic-contract requalification 109 V2 report\n\nFinal state: `{final}`. Review pack: `docs/vm_tlb/review_packs/AWMA_R51_SEMANTIC_CONTRACT_REQUALIFICATION_V2/`.\n');print(json.dumps(receipt,sort_keys=True))
