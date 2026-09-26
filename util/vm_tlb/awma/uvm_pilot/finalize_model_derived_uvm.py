#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,math,shutil
from collections import Counter
from pathlib import Path
RAW=Path('/data/c16/awma/uvm_model_derived_characterization_20260926')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-uvm-model-derived-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1'
REPORT=WT/'docs/vm_tlb/reports/AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_109_V1_REPORT.md'
DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/uvm_model_derived_characterization_20260926'
PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)

# Routing summary: actual decode events only; no synthetic routes.
route=[json.loads(x) for x in (RAW/'routing/ROUTE_TRACE.jsonl').read_text().splitlines()]
dec=[x for x in route if x['phase']=='DECODE'];counts=Counter(i for e in dec for i in e['expert_ids']);n=sum(counts.values());entropy=-sum(v/n*math.log2(v/n) for v in counts.values())
rows=[]
prev=None
for step in range(1,9):
 ids=[i for e in dec if e['decode_step']==step for i in e['expert_ids']];s=set(ids);j='N/A' if prev is None else f'{len(s&prev)/len(s|prev):.9f}'
 rows.append({'scope':f'DECODE_STEP_{step}','route_events':sum(e['decode_step']==step for e in dec),'expert_choices':len(ids),'distinct_experts':len(s),'normalized_entropy':'','top8_coverage':'','top16_coverage':'','top32_coverage':'','previous_step_set_jaccard':j,'authority_sha256':sha(RAW/'routing/ROUTE_TRACE.jsonl')});prev=s
rows.insert(0,{'scope':'DECODE_OVERALL','route_events':len(dec),'expert_choices':n,'distinct_experts':len(counts),'normalized_entropy':f'{entropy/math.log2(64):.9f}','top8_coverage':f'{sum(v for _,v in counts.most_common(8))/n:.9f}','top16_coverage':f'{sum(v for _,v in counts.most_common(16))/n:.9f}','top32_coverage':f'{sum(v for _,v in counts.most_common(32))/n:.9f}','previous_step_set_jaccard':'N/A','authority_sha256':sha(RAW/'routing/ROUTE_TRACE.jsonl')})
write(RAW/'REAL_ROUTING_BEHAVIOR.tsv',rows)

m=read(RAW/'RUN_MATRIX.tsv');e={x['point_id']:x for x in read(RAW/'UVM_EVENT_MATRIX.tsv')};summary=[]
for x in m:
 r=json.loads(x['receipt_json']);z=e[x['point_id']]
 summary.append({'point_id':x['point_id'],'pattern':x['pattern'],'layout_point':x['layout_point'],'mode':x['mode'],'allocated_bytes':x['allocated_bytes'],'cold_gpu_ms':r['cold_gpu_ms'],'repeat_gpu_ms':r['repeat_gpu_ms'],'cold_repeat_ratio':f"{r['cold_gpu_ms']/r['repeat_gpu_ms']:.6f}",'migration_bytes':z['migration_bytes'],'htod_bytes':z['htod_bytes'],'dtoh_bytes':z['dtoh_bytes'],'prefetch_runtime_calls':z['prefetch_runtime_calls'],'fault_counters':'UNAVAILABLE'})
write(RAW/'MODEL_DERIVED_RESULT_SUMMARY.tsv',summary)

bridge=json.loads((RAW/'PYTORCH_MANAGED_TENSOR_BRIDGE_STATUS.json').read_text())
(RAW/'SYNTHETIC_VS_MODEL_DERIVED.md').write_text('''# Synthetic versus model-derived boundary

The accepted feasibility pilot used invented dense, growing-prefix, and rotating-expert laws at four artificial VRAM ratios. This continuation replaces sizes and ordering with local model authorities, but remains a replay rather than framework execution.

- D1 uses every Qwen3-8B tensor byte size and the frozen safetensors inventory order (399 tensors, 16,381,470,720 bytes). It does not execute Qwen operators.
- D2 uses the exact Llama-3.2-1B KV dimensions and exact byte accounting at fixed context 4096 while changing concurrency only. Access is a 256-token-block sequential prefix replay, so layout is exact and access timing is approximate.
- D3 uses the actual OLMoE decode route sequence, exact top-8 expert IDs, exact expert tensor regions, and exact non-expert pressure. It replays memory touches and does not execute expert GEMMs.
- The bounded PyTorch managed-tensor bridge did not compile because the extension compile command lacked a CUDA runtime header include path. Per preregistration it was not retried.

Therefore these results support model-derived UVM replay claims only. They are not measurements of end-to-end LLM serving, real framework allocation, GPU faults, TLB misses, PPN continuity, or migration page size.
''')
(RAW/'CLOSEST_WORK_SCREEN.md').write_text('''# Closest-work screen

- Shao et al., *Oversubscribing GPU Unified Virtual Memory: Implications and Suggestions* (ICPE 2022), https://doi.org/10.1145/3489525.3511691 — already establishes access-pattern and prefetch sensitivity under UVM oversubscription.
- Allen and Ge, *Demystifying GPU UVM Cost with Deep Runtime and Workload Analysis* (IPDPS 2021), https://doi.org/10.1109/IPDPS49936.2021.00055 — already analyzes migration/fault overhead and counterproductive prefetch behavior.
- Jones et al., *HELM* (SC 2025), https://doi.org/10.1145/3712285.3759812 — telemetry-driven UVM characterization and policy selection are existing work; this run lacks HELM-style dedicated fault telemetry.
- Jung et al., *DeepUM: Tensor Migration and Prefetching in Unified Memory* (ASPLOS 2023), https://doi.org/10.1145/3575693.3575736 — tensor-aware UVM prefetch and migration for DNNs are existing mechanism territory.
- Sheng et al., *FlexGen* (ICML 2023), https://proceedings.mlr.press/v202/sheng23a.html, and Jiang et al., *NEO* (2024), https://arxiv.org/abs/2411.01142 — weight/KV placement and CPU offload for constrained LLM inference are established.
- Kim et al., *ES-MoE* (ICML 2024), https://proceedings.mlr.press/v235/kim24w.html, and Zhou et al., *FloE* (ICML 2025), https://proceedings.mlr.press/v267/zhou25j.html — expert offload, overlap, and sparse expert residency are established. Sparse activation itself is not treated as novelty here.

Screen result: the observed KV oversubscription transition and current-step-prefetch penalty are concrete, but not distinct from known UVM/offloading problems. The resident actual-route MoE replay does not expose a new oversubscribed regime.
''')
(RAW/'FINAL_DECISION.md').write_text('''# Final decision

`MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM`

Evidence:

- All 10 preregistered cold/repeat points completed under the GPU lock and 20 GiB cap.
- D1 shows the expected cold placement cost and fast resident repeat for a 16.381 GB exact-metadata tensor stream.
- D2 has a sharp, reproducible migration-volume transition at 18.790 GB (1.094x physical VRAM): M0 moves 195.007 GB and M1 moves 270.169 GB. Current-step prefetch worsens both migration volume and time at this point. This is a useful platform boundary, but it is an instance of known UVM oversubscription/prefetch behavior and known KV placement pressure, not a distinct research problem.
- D3 actual routing has high dispersion (64/64 experts observed; normalized entropy 0.9851). The complete OLMoE footprint is only 13.838 GB and remains resident on this 16 GB device, so it provides no natural expert-oversubscription problem. No artificial scaling was introduced.
- The one bounded managed-PyTorch bridge attempt is `NOT_READY`, so end-to-end framework behavior is not established.
- Fault counters are unavailable; no fault/TLB/PPN/page-size mechanism is inferred.

No problem card is emitted and no UVM mechanism development is authorized by this result.
''')
(RAW/'PYTORCH_MANAGED_TENSOR_BRIDGE_STATUS.md').write_text(f'''# PyTorch managed-tensor bridge status

Status: `{bridge['status']}`. Exactly one bounded attempt was made for a 4096x4096 BF16 managed weight followed by `torch.mv`. Compilation stopped before GPU execution because `cuda_runtime_api.h` was absent from the extension compiler include path. The attempt was not retried, and no allocator/framework modification was made.

Attempt source SHA256: `{bridge['source_sha256']}`.
''')
(RAW/'SYSTEM_SAFETY_RECEIPT.tsv').write_text('gate\tresult\tevidence\nGPU_LOCK\tPASS\tEach profile point and the routing capture acquired /data/c16/locks/c16_gpu_campaign.lock\nMAX_ALLOCATION\tPASS\t18790481920 bytes < 20 GiB\nHOST_HEADROOM\tPASS\tRunner required allocation + 8 GiB MemAvailable before each point\nMODEL_DOWNLOAD\tPASS\tlocal_files_only or metadata-only local paths; no download\nFAULT_INFERENCE_BOUNDARY\tPASS\tGPU/CPU fault counters marked UNAVAILABLE\n')
(RAW/'SOURCE_ANCHORS.md').write_text('''# Source anchors and change scope

- Accepted pilot: `hrl/awma-ai-uvm-oversubscription-feasibility-pilot-v1@368b7043c70c1274f29153b5d5a665d1742aeacb`.
- Accepted continuation handoff: `hrl/awma-post-novelty-reset-handoff-v1@9e230e5bf8a5ad7b425d1d90c852f6771e200521`.
- Execution branch: `hrl/awma-ai-uvm-model-derived-characterization-v1`, branched from the accepted pilot.
- Local model revisions, config hashes, safetensors file hashes, and per-tensor identities are in `MODEL_ASSET_METADATA.tsv` and `MODEL_ASSET_SUMMARY.tsv`.
- Frozen route authority is hash-bound in `PREREG_FREEZE_RECEIPT.json`.

Changed code is confined to `util/vm_tlb/awma/uvm_pilot/`: local metadata extraction, one read-only route capture, preregistration freeze, a model-derived managed-memory replay harness, sequential locked runner, telemetry analysis, one bounded bridge attempt, and finalization. No accepted baseline, simulator, model, or UVM mechanism semantics were modified.
''')
(RAW/'VALIDATION_SUMMARY.md').write_text('''# Validation summary

- `VERIFIED_RUN`: 10/10 preregistered matrix points completed, each with exactly one cold run and one immediate repeat in-process.
- `VERIFIED_RUN`: all actual GPU work acquired `/data/c16/locks/c16_gpu_campaign.lock`.
- `VERIFIED_RUN`: maximum allocation was 18,790,481,920 bytes, below the 20 GiB cap; the host-headroom gate passed before every point.
- `VERIFIED_RUN`: NSYS SQLite exported for all 10 points; CUPTI migration memcpy activity and NVTX ranges were joined into event/step tables.
- `VERIFIED_RUN`: source and node164 copies both pass every entry in `RAW_DATA_INDEX.tsv`; compact authority hashes pass `SHA256SUMS`.
- `VERIFIED_RUN`: Python sources pass `py_compile`, CUDA harness compiles with CUDA 12.8, and `git diff --check` passes.
- `UNKNOWN`: dedicated GPU/CPU fault counters remain unavailable. No TLB, PPN, page-size, shootdown, or fault-count claim is made.
''')
(RAW/'OPEN_ISSUES.md').write_text('''# Open issues

1. The bounded PyTorch managed tensor bridge is `NOT_READY`: the single extension attempt lacked `cuda_runtime_api.h` on its compiler include path. This is an integration gap, not evidence about PyTorch/UVM performance.
2. D2 has exact KV byte/layout accounting but an approximate 256-token-block sequential access replay. End-to-end scheduling, allocator, attention compute, and serving concurrency are not modeled.
3. OLMoE is naturally resident on this RTX 4080. A larger *runnable and already local* MoE would be required to study natural expert oversubscription without artificial scaling; this stage does not authorize that follow-up.
4. Fault/TLB/PPN/page-size telemetry remains unavailable and must not be inferred from migration memcpy records.
''')

decision='MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM'
readme=f'''# AWMA AI UVM model-derived characterization V1

Final decision: `{decision}`.

This review replaces synthetic laws with exact local model metadata, exact Llama KV accounting, and an actual frozen OLMoE route sequence. It finds a real KV migration cliff just above VRAM, but closest-work screening shows no distinct problem beyond existing UVM/offloading work. The OLMoE model is naturally resident, and the bounded PyTorch managed-tensor bridge is not ready.

Durable raw authority: `{DUR}`.

Review order: `FINAL_DECISION.md`, `MODEL_DERIVED_RESULT_SUMMARY.tsv`, `REAL_ROUTING_BEHAVIOR.tsv`, `SYNTHETIC_VS_MODEL_DERIVED.md`, `CLOSEST_WORK_SCREEN.md`, then `VALIDATION_SUMMARY.md` and `OPEN_ISSUES.md`. Source/base provenance and the path-scoped diff summary are in `SOURCE_ANCHORS.md`; raw identities are in `RAW_DATA_INDEX.tsv`. `COMPACT_NORMALIZATION.md` explains the Git-copy LF normalization and compact `SHA256SUMS`.
'''
(RAW/'README.md').write_text(readme);(RAW/'REPORT.md').write_text(readme+'\nSee `FINAL_DECISION.md` for evidence and inference limits.\n')

# Index raw authority before copying compact artifacts; omit the index itself to avoid recursion.
idx=[]
for p in sorted(x for x in RAW.rglob('*') if x.is_file() and x.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json')):
 idx.append({'relative_path':str(p.relative_to(RAW)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(RAW/'RAW_DATA_INDEX.tsv',idx)
(RAW/'SHA256SUMS').write_text(''.join(f"{sha(p)}  {p.name}\n" for p in sorted([RAW/'MODEL_ASSET_METADATA.tsv',RAW/'MODEL_DERIVED_PATTERN_PREREG.tsv',RAW/'REAL_ROUTING_BEHAVIOR.tsv',RAW/'RUN_MATRIX.tsv',RAW/'UVM_EVENT_MATRIX.tsv',RAW/'STEPWISE_BEHAVIOR.tsv',RAW/'FINAL_DECISION.md',RAW/'RAW_DATA_INDEX.tsv'])))
receipt={'stage':'AWMA_AI_UVM_MODEL_DERIVED_CHARACTERIZATION_V1','decision':decision,'matrix_points':len(m),'complete_points':sum(x['status']=='COMPLETE' for x in m),'max_allocation_bytes':max(int(x['allocated_bytes']) for x in m),'node164_authority':DUR,'raw_index_sha256':sha(RAW/'RAW_DATA_INDEX.tsv'),'prereg_freeze_sha256':sha(RAW/'PREREG_FREEZE_RECEIPT.json'),'bridge_status':bridge['status'],'fault_counters':'UNAVAILABLE'}
(RAW/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')

compact=['README.md','SOURCE_ANCHORS.md','VALIDATION_SUMMARY.md','OPEN_ISSUES.md','MODEL_ASSET_METADATA.tsv','MODEL_ASSET_SUMMARY.tsv','KV_LAYOUT_POINTS.tsv','MODEL_DERIVED_PATTERN_PREREG.tsv','PREREG_FREEZE_RECEIPT.json','REAL_ROUTING_BEHAVIOR.tsv','RUN_MATRIX_PREREG.tsv','RUN_MATRIX.tsv','MODEL_DERIVED_RESULT_SUMMARY.tsv','UVM_EVENT_MATRIX.tsv','STEPWISE_BEHAVIOR.tsv','SYNTHETIC_VS_MODEL_DERIVED.md','PYTORCH_MANAGED_TENSOR_BRIDGE_STATUS.json','PYTORCH_MANAGED_TENSOR_BRIDGE_STATUS.md','CLOSEST_WORK_SCREEN.md','FINAL_DECISION.md','SYSTEM_SAFETY_RECEIPT.tsv','RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json','REPORT.md']
for n in compact:shutil.copy2(RAW/n,PACK/n)
# Raw CSV authorities retain Python csv.writer CRLF bytes and are already hash-closed.
# Normalize only Git review TSV presentation copies so repository whitespace checks pass.
for p in PACK.glob('*.tsv'):
 p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
(PACK/'COMPACT_NORMALIZATION.md').write_text('''# Compact-copy normalization

The node164 raw TSV authorities retain their original Python `csv.writer` CRLF bytes and are identified by `RAW_DATA_INDEX.tsv`. Git review-pack TSV copies are byte-normalized from CRLF to LF only; field content is unchanged. `SHA256SUMS` in this directory binds the normalized compact copies, while the durable raw directory's `SHA256SUMS` binds raw bytes.
''')
compact_hashed=['MODEL_ASSET_METADATA.tsv','MODEL_DERIVED_PATTERN_PREREG.tsv','REAL_ROUTING_BEHAVIOR.tsv','RUN_MATRIX.tsv','UVM_EVENT_MATRIX.tsv','STEPWISE_BEHAVIOR.tsv','FINAL_DECISION.md','RAW_DATA_INDEX.tsv']
(PACK/'SHA256SUMS').write_text(''.join(f"{sha(PACK/n)}  {n}\n" for n in compact_hashed))
REPORT.write_text(f'''# AWMA AI UVM model-derived characterization 109 V1 report

Decision: `{decision}`. Ten preregistered model-derived replay points completed. Exact results and limitations are in `{PACK.relative_to(WT)}`; durable raw authority is `{DUR}`.
''')
print(json.dumps(receipt,sort_keys=True))
