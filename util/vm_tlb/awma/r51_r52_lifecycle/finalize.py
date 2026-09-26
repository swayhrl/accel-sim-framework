#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sqlite3,statistics,shutil,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r51-r52-lifecycle-v1');PACK=WT/'docs/vm_tlb/review_packs/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1';REPORT=WT/'docs/vm_tlb/reports/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_109_V1_REPORT.md';DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r51_r52_lifecycle_qualification_20260926';PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def receipts():return {r['arm']:json.loads(r['receipt_json']) for r in read(ROOT/'BACKGROUND_STANDALONE_RUNS.tsv') if r['status']=='COMPLETE'}
rec=receipts();num=json.loads((ROOT/'NUMERIC_ATTEMPT_AUDIT.json').read_text());target=json.loads((ROOT/'TARGET_IDENTITY_RECEIPT.json').read_text());b0=rec['MONOLITHIC']['gpu_timing']['median_ms']
# Exact canary strata and stream IDs.
strata=[];low_ids=set();high_ids=set()
for arm in ('MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'):
 db=sqlite3.connect(f'file:{ROOT/"standalone"/arm/"canary.sqlite"}?mode=ro',uri=True);strings=dict(db.execute('select id,value from StringIds'));ranges=list(db.execute("select start,end,text from NVTX_EVENTS where text like 'R51_STANDALONE;%KIND=FORMAL%'"))
 if len(ranges)!=1:raise RuntimeError(f'{arm} standalone ranges {len(ranges)}')
 st0,en0,txt=ranges[0];groups={}
 for st,en,sid,gx,gy,gz,bx,by,bz,dn,sn,mn in db.execute('select start,end,streamId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL where start>=? and start<=? order by start',(st0,en0)):
  name=strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN';low_ids.add(sid);key=(name,sid,gx,gy,gz,bx,by,bz);z=groups.setdefault(key,[0,0]);z[0]+=1;z[1]+=en-st
 for k,v in groups.items():strata.append({'arm':arm,'function':k[0],'stream_id':k[1],'grid':f'{k[2]},{k[3]},{k[4]}','block':f'{k[5]},{k[6]},{k[7]}','launch_count':v[0],'gpu_duration_ns':v[1],'assignment':'KERNEL_START_WITHIN_STANDALONE_NVTX'})
 for sid,dn,sn,mn in db.execute('select distinct streamId,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL'):
  name=strings.get(dn) or strings.get(sn) or strings.get(mn) or ''
  if 'pytorch_flash::flash_fwd' in name:high_ids.add(sid)
 db.close()
write(ROOT/'NSYS_STANDALONE_STRATA.tsv',strata)
# Timing and correctness.
timing=[];corr=[]
audit_rows=num['attempts']
for arm in ('MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'):
 x=rec[arm];med=x['gpu_timing']['median_ms'];timing.append({'arm':arm,'chunks':x['chunks'],'status':'QUALIFIED' if arm=='MONOLITHIC' else 'DIAGNOSTIC_NUMERIC_CONTRACT_FAILED','median_gpu_ms':med,'min_gpu_ms':x['gpu_timing']['min_ms'],'max_gpu_ms':x['gpu_timing']['max_ms'],'cv':x['gpu_timing']['cv'],'samples_gpu_ms_json':json.dumps(x['gpu_timing']['samples_ms']),'overhead_vs_monolithic':med/b0-1,'output_sha256':x['correctness']['background_output_sha256']})
 if arm=='MONOLITHIC':corr.append({'arm':arm,'attempt':'B0_ORIGINAL','bitwise_to_b0':True,'different_elements':0,'max_abs':0.0,'graph_liveness':'NOT_APPLICABLE','qualification':'PASS'})
 else:
  n=x['chunks'];a=next(z for z in audit_rows if z.get('attempt')==1 and z.get('chunks')==n);g=next(z for z in audit_rows if z.get('attempt')=='GRAPH_LIVENESS' and z.get('chunks')==n);corr.append({'arm':arm,'attempt':'1_F_LINEAR_CHUNKS;2_API_EQUIVALENTS','bitwise_to_b0':False,'different_elements':a['different_elements'],'max_abs':a['max_abs'],'graph_liveness':'PASS_RECOMPUTES_CHUNKED_ALGORITHM' if all(g[k] for k in ('base_graph_equals_eager','changed_graph_equals_eager_chunked','changed_differs_from_base','restored_equals_base')) else 'FAIL','qualification':'SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED'})
write(ROOT/'BACKGROUND_STANDALONE_TIMING.tsv',timing);write(ROOT/'BACKGROUND_CORRECTNESS.tsv',corr)
stream={'status':'DISTINCT_PRIORITY_LEVELS_AVAILABLE_BUT_OVERLAP_NOT_RUN','cuda_priority_least_low':rec['MONOLITHIC']['stream_priority_least'],'cuda_priority_greatest_high':rec['MONOLITHIC']['stream_priority_greatest'],'distinct_priority_levels':rec['MONOLITHIC']['stream_priority_least']!=rec['MONOLITHIC']['stream_priority_greatest'],'created_low_stream_handles':sorted({x['low_stream_handle'] for x in rec.values()}),'created_high_stream_handles':sorted({x['high_stream_handle'] for x in rec.values()}),'nsys_background_stream_ids':sorted(low_ids),'nsys_foreground_flash_stream_ids':sorted(high_ids),'note':'NSYS observed both streams during standalone canary initialization/main range; no formal overlap timeline was launched after safe-point numeric gate failed'};(ROOT/'STREAM_PRIORITY_RECEIPT.json').write_text(json.dumps(stream,indent=2,sort_keys=True)+'\n')
# Freeze the intended overlap contract before deciding not to enter it.
srcdir=WT/'util/vm_tlb/awma/r51_r52_lifecycle';prereg={'stage':'AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1','status':'FROZEN_PRE_OVERLAP_THEN_STOPPED_AT_NUMERIC_GATE','accepted_base':'ce5918d837b76e95ad4000c50bbe1465707a2ebd','handoff_commit':'246eb3789243718f2bdc794ac6651cee2e1a593f','literature_commit':'d6a10f0209a024edb4612b1f53edb61d6e39bd18','background':{'semantic_role':'LM_HEAD_BACKGROUND','model':'Qwen/Qwen2.5-0.5B-Instruct','revision':target['revision'],'scenario':'S2_TEXT','decode_step':16,'hidden_sha256':target['background_hidden_sha256'],'weight_sha256':target['background_weight_sha256'],'output_sha256':target['background_output_sha256'],'shape':target['background_weight_shape'],'monolithic_median_ms':b0,'eligibility_min_ms':0.150,'historical_grid_clue':'18992,1,1 block=8,8,1 operator_role historically UNKNOWN','current_semantic_replay_identity':'exact standalone strata'},'foreground':{'role':target['foreground_role'],'q_sha256':target['foreground_q_sha256'],'k_sha256':target['foreground_k_sha256'],'v_sha256':target['foreground_v_sha256'],'output_sha256':target['foreground_output_sha256'],'accepted_standalone_median_ms':0.03248000144958496},'arms':['MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'],'chunk_counts':[8,32],'arrival_fractions':[0.25,0.50],'arrival_tolerance_fraction':0.10,'warmups':2,'measured_repetitions':7,'canary_per_point':1,'retry_per_point':1,'handoff_material_min_us':10.0,'jitter_gate':'improvement > 3x larger latency jitter envelope','low_cost_overhead_max':0.05,'formal_timeline':'NSYS/CUPTI unified timeline','numeric_gate_result':'B8_B32_FAILED_BITWISE_AFTER_TWO_ATTEMPTS; FORMAL_OVERLAP_NOT_AUTHORIZED','source_sha256':{p.name:sha(p) for p in sorted(srcdir.glob('*.py'))},'prohibitions':['no model download','no driver patch','no parameter sweep','no Accel-Sim','no node174 execution','no NVBit full trace']};(ROOT/'PREREGISTRATION.json').write_text(json.dumps(prereg,indent=2,sort_keys=True)+'\n')
# Explicit empty/non-entry result tables.
write(ROOT/'R51_TIMELINE_RESULTS.tsv',[{'status':'NOT_RUN_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED','arm':'N/A','arrival_fraction':'N/A','rep':'N/A','t_bg_start_ns':'N/A','t_ready_ns':'N/A','t_submit_end_ns':'N/A','t_fg_first_kernel_start_ns':'N/A','t_fg_last_kernel_end_ns':'N/A','t_bg_end_ns':'N/A','ready_to_fg_start_us':'N/A','submit_to_fg_start_us':'N/A','foreground_completion_from_ready_us':'N/A','background_chunk_at_fg_start':'N/A','gpu_overlap':'N/A'}])
write(ROOT/'R51_MATCHED_COMPARISON.tsv',[{'status':'NOT_RUN_NUMERIC_GATE','arrival_fraction':'0.25/0.50_FROZEN','monolithic_median_ready_to_start_us':'N/A','best_chunked_arm':'N/A','best_chunked_median_ready_to_start_us':'N/A','improvement_us':'N/A','materiality':'NOT_EVALUATED','standalone_overhead':'B8=%.9f;B32=%.9f'%(rec['CHUNKED_GRAPH_8']['gpu_timing']['median_ms']/b0-1,rec['CHUNKED_GRAPH_32']['gpu_timing']['median_ms']/b0-1)}])
(ROOT/'R52_INVALIDATION_AUTHORITY_AUDIT.md').write_text('''# R52 invalidation authority audit

Decision: `R52_NO_REAL_INVALIDATION_AUTHORITY`.

The accepted review packs, codex handoffs, and `/data/c16/awma` namespaces were searched for task creation, earliest online invalidation, completion, and valid-consumer dependency records. The only speculative-labelled accepted material is M4B simulator/offline opportunity analysis; it has no native online invalidation lifecycle and cannot be promoted. No local speculative-model workload or cancellation trace satisfies the four-field authority contract. No model was downloaded or built.
''')
write(ROOT/'R52_CANCEL_WINDOW_DIAGNOSTIC.tsv',[{'status':'R52_SYNTHETIC_CANCEL_WINDOW_DIAGNOSTIC_NOT_EXECUTED_R51_TIMELINE_UNAVAILABLE','arm':'N/A','arrival_fraction':'0.25/0.50_FROZEN','hypothetical_invalidation_ns':'N/A','remaining_background_gpu_us':'N/A','time_to_next_safe_point_us':'N/A','fraction_after_boundary':'N/A','claim_boundary':'NO_AI_WORKLOAD_OR_CAPABILITY_CLAIM'}])
(ROOT/'SOURCE_AND_CLOSEST_WORK_AUDIT.md').write_text('''# Source and closest-work audit

- Background semantics are closed by an exact hook on `model.get_output_embeddings()` at accepted Qwen S2 decode step16; the replay selects the same `internal::gemvx` grid `18992,1,1`, block `8,8,1` that was previously only an UNKNOWN-role clue.
- Foreground reuses the accepted P1 layer-12 Flash-SDPA B1 tensors/output without contract drift.
- CUDA exposes priority range low `0` to high `-5`; distinct streams and NSYS stream IDs are recorded.
- LithOS kernel atomization, GPREEMPT driver timeslicing, ExpertPlex cooperative tile handoff, MPK task graphs, and PipeThreader reduction/pipeline decomposition are the closest software/system capabilities in Round-05 (`d6a10f02...`). This stage does not claim a residual against them because its own required strong software baseline failed the exact output gate.
- No driver change, general scheduler, hardware mechanism, model download, NCU, NVBit full trace, Accel-Sim, or node174 task was used.
''')
(ROOT/'R51_DECISION.md').write_text('''# R51 decision

`R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED`

The real lm_head background is qualified and long enough: B0 median is 412.544 us and its exact runtime identity is the historical 18992-grid GEMV. However, output-row decomposition changes library dispatch and breaks the required bitwise contract: B8 differs in 135 FP16 elements and B32 in 151, each with maximum absolute difference 0.0078125. All bounded second-attempt API equivalents select the same differing arithmetic. CUDA Graph liveness passes for the chunked algorithm itself, but restoring/recomputing the wrong contract does not qualify it.

The diagnostic B8/B32 medians are 456.416/482.016 us (10.635%/16.840% overhead), but these numbers cannot be used to claim a latency-throughput tradeoff because the outputs are not the same B0 contract. Formal overlap timing was therefore not launched.
''')
write(ROOT/'R51_R52_DECISION_MATRIX.tsv',[{'candidate':'R51','semantic_identity':'QUALIFIED_LM_HEAD','software_baseline':'FAILED_EXACT_NUMERIC_CONTRACT','formal_timeline':'NOT_RUN','material_residual':'NOT_EVALUATED','closest_work':'LithOS;GPREEMPT;ExpertPlex;MPK;PipeThreader','decision':'R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED','next_action':'STOP_NO_ARCH_REVIEW'},{'candidate':'R52','semantic_identity':'NO_REAL_INVALIDATION_AUTHORITY','software_baseline':'SHARED_R51_FAILED_BEFORE_TIMELINE','formal_timeline':'NOT_RUN','material_residual':'NOT_EVALUATED','closest_work':'PipeInfer;SMART','decision':'R52_NO_REAL_INVALIDATION_AUTHORITY','next_action':'STOP_NO_SYNTHETIC_AI_CLAIM'}])
(ROOT/'FINAL_DECISION.md').write_text('''# Final decision

`R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1`

R51 closes the real lm_head and foreground identities, runtime kernel identity, standalone duration, stream-priority capability, and graph liveness. It cannot enter formal handoff timing because both pre-registered chunked safe-point arms fail the strict output contract after the two allowed implementation attempts. R52 has no real online invalidation authority, and no matched R51 timeline exists from which to compute the synthetic cancel-window diagnostic. No architecture-review candidate is emitted.
''')
(ROOT/'README.md').write_text(f'''# AWMA R51/R52 task-lifecycle handoff qualification V1

Final state: `R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1`.

R51 background identity is a real Qwen lm_head and passes the >=150 us eligibility gate, but B8/B32 fail the exact output contract; formal overlap timing stops before entry. R52 has no real invalidation authority.

Review `FINAL_DECISION.md`, `R51_DECISION.md`, `BACKGROUND_CORRECTNESS.tsv`, `BACKGROUND_STANDALONE_TIMING.tsv`, `NUMERIC_ATTEMPT_AUDIT.json`, and `NSYS_STANDALONE_STRATA.tsv`.

Durable authority: `{DUR}`.
''');(ROOT/'REPORT.md').write_text((ROOT/'README.md').read_text()+'\nScientific STOP occurred at the strong-software numeric gate.\n')
# Raw authority and compact pack.
idx=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json')):idx.append({'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(ROOT/'RAW_DATA_INDEX.tsv',idx);final={'stage':'AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1','final_state':'R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1','r51_decision':'R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED','r52_decision':'R52_NO_REAL_INVALIDATION_AUTHORITY','background_role':'LM_HEAD_BACKGROUND','monolithic_median_us':b0*1000,'formal_overlap_points':0,'ncu':'NOT_RUN','node164_authority':DUR,'raw_index_sha256':sha(ROOT/'RAW_DATA_INDEX.tsv'),'preregistration_sha256':sha(ROOT/'PREREGISTRATION.json')};(ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n')
compact=['README.md','REPORT.md','SOURCE_AND_CLOSEST_WORK_AUDIT.md','TARGET_IDENTITY_RECEIPT.json','PREREGISTRATION.json','BACKGROUND_CORRECTNESS.tsv','BACKGROUND_STANDALONE_TIMING.tsv','STREAM_PRIORITY_RECEIPT.json','NUMERIC_ATTEMPT_AUDIT.json','NSYS_STANDALONE_STRATA.tsv','R51_TIMELINE_RESULTS.tsv','R51_MATCHED_COMPARISON.tsv','R51_DECISION.md','R52_INVALIDATION_AUTHORITY_AUDIT.md','R52_CANCEL_WINDOW_DIAGNOSTIC.tsv','R51_R52_DECISION_MATRIX.tsv','FINAL_DECISION.md','RAW_DATA_INDEX.tsv','FINAL_RECEIPT.json']
for n in compact:shutil.copy2(ROOT/n,PACK/n)
for p in PACK.glob('*.tsv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
pack_files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!='SHA256SUMS');(PACK/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in pack_files));shutil.copy2(PACK/'SHA256SUMS',ROOT/'SHA256SUMS')
REPORT.write_text('# AWMA R51/R52 task-lifecycle qualification 109 V1 report\n\nFinal state: `R51_R52_NATIVE_QUALIFICATION_INCOMPLETE_V1`. Scientific STOP: exact safe-point output contract could not be closed. Review pack: `docs/vm_tlb/review_packs/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1/`.\n');print(json.dumps(final,sort_keys=True))
