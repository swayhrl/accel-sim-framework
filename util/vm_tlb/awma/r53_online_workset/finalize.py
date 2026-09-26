#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,json,os,platform,shutil,subprocess
from pathlib import Path
ROOT=Path('/data/c16/awma/r53_online_workset_qualification_20260927');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r53-online-workset-v1');PACK=WT/'docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1';REPORT=WT/'docs/vm_tlb/reports/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_109_V1_REPORT.md';DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r53_online_workset_qualification_20260927';PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
# Correct evidence labels after semantic result: failed packed rows cannot be called legally omittable.
led=[]
with gzip.open(ROOT/'LEGAL_WORK_LEDGER.tsv.gz','rt') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if r['arm']=='A1_PACKED' and r['evidence_class']=='LEGALLY_OMITTABLE_IN_SCOPE':r['evidence_class']='PASSIVE_EXECUTION_CANDIDATE';r['notes']='PACKED_OMISSION_CHANGED_TRAJECTORY_NOT_LEGAL'
  led.append(r)
with gzip.open(ROOT/'LEGAL_WORK_LEDGER.tsv.gz','wt',newline='') as f:w=csv.DictWriter(f,fieldnames=list(led[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(led)
eq=read(ROOT/'A0_A1_SEMANTIC_EQUIVALENCE.tsv');work=read(ROOT/'LEGAL_WORK_SUMMARY.tsv');base={(r['domain'],r['arm']):r for r in work};workout=[]
for r in work:
 a0=base[(r['domain'],'A0')];red=1-int(r['input_token_rows'])/int(a0['input_token_rows']);sem=next((x['status'] for x in eq if x['domain']==r['domain'] and x['a1_arm']==r['arm']), 'AUTHORITY' if r['arm']=='A0' else 'N/A');workout.append({**r,'token_row_reduction_vs_a0':red,'semantic_status':sem,'legally_omittable_rows':0 if sem!='PASS' or red==0 else 'REVIEW'})
write(ROOT/'DISCOVERY_WORKSET_RESULTS.tsv',workout)
tim=[]
for dom in ('GSM8K','HumanEval'):
 for arm in ('A0_PINNED_OFFICIAL_BATCHED_REFERENCE','A1_STRONG_SEMANTIC_WORKSET_SOFTWARE'):tim.append({'domain':dom,'arm':arm,'status':'NOT_RUN_SEMANTIC_GATE_STOP','warmups':0,'measured_repetitions':0,'reason':'packed A1 changed discrete trajectory; safe-bucket repair preserved trajectory but reduced no work'})
write(ROOT/'DISCOVERY_TIMING_RESULTS.tsv',tim);write(ROOT/'NSYS_DISCOVERY_SUMMARY.tsv',[{'domain':'GSM8K','arm':'A0/A1','status':'NOT_RUN_SEMANTIC_GATE_STOP','gpu_union_busy_ns':'N/A','kernel_launch_count':'N/A','graph_launch_count':'N/A','reason':'formal discovery not authorized'},{'domain':'HumanEval','arm':'A0/A1','status':'NOT_RUN_SEMANTIC_GATE_STOP','gpu_union_busy_ns':'N/A','kernel_launch_count':'N/A','graph_launch_count':'N/A','reason':'formal discovery not authorized'}])
model=json.loads((ROOT/'MODEL_ADMISSION_RECEIPT.json').read_text());data=json.loads((ROOT/'DATASET_SNAPSHOT_RECEIPT.json').read_text());b4=json.loads((ROOT/'B4_RESOURCE_CANARY.json').read_text())
(ROOT/'PREREGISTRATION.json').write_text(json.dumps({'stage':'AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1','status':'FROZEN_BEFORE_FORMAL_TIMING; FORMAL_STOPPED_AT_SEMANTIC_GATE','accepted_base':'db2000f7222030282f788bd009243ab1a43ed867','handoff_commit':'4ce1e7ad04d552fa044b173ad76a1005237a0762','source_commit':model['source_commit'],'model_revision':model['revision'],'dataset_revisions':{x['repo']:x['revision'] for x in data['datasets']},'request_selection_sha256':data['request_selection_sha256'],'concurrency':4,'b2_fallback':'ONLY_IF_B4_OOM_NOT_TRIGGERED','policy':{'dtype':'bfloat16','block_size':32,'small_block_size':8,'threshold':.9,'temperature':0.0,'top_p':.95,'use_block_cache':True,'max_new_tokens':512,'stop_eos':True},'arms':['A0_PINNED_OFFICIAL_BATCHED_REFERENCE','A1_STRONG_SEMANTIC_WORKSET_SOFTWARE'],'semantic_contract':'R53_FIXED_DECODER_CACHE_TRAJECTORY_V1','measurement_if_gate_passed':{'canary':1,'warmups':2,'repetitions':7,'paired_interleaved':True,'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock'},'performance_gate':'end-to-end >=5% and >3x larger jitter','hardening_limit':2,'no_parameter_sweep':True,'humaneval_code_execution':'PROHIBITED'},indent=2,sort_keys=True)+'\n')
(ROOT/'SEMANTIC_TRAJECTORY_SCHEMA.md').write_text('''# Semantic trajectory schema

The canonical comparison projects each request event onto: request ID, logical step, block/subblock, cohort ID, request-finished transition, frozen cohort full-refresh/reuse decision, cache epoch/action, committed positions/token IDs, forced-commit positions, stop transition, and next-block seed. Final token and rendered-text hashes are additional gates. Execution-only `REUSE_PACKED` normalizes to semantic `REUSE`; input rows, packing bytes and buckets remain work ledger fields, not algorithm state.
''')
(ROOT/'PRE_EXECUTION_INVENTORY.md').write_text('''# Pre-execution inventory

- Node109 RTX4080, driver 580.178.04, 16,376 MiB; GPU initially idle.
- `/data/c16` had about 291 GiB free; host had about 60 GiB available.
- Dedicated R53 environment created under the stage root; accepted C16 environment, system CUDA and driver were not modified.
- Direct Hugging Face endpoint timed out; exact-revision download used `hf-mirror.com`, whose response bound `X-Repo-Commit` to the required revision.
- B1 short canary passed. B4 full 512-token canary passed with peak allocated/reserved about 3.26/3.48 GB, so B2 fallback was not activated.
- HumanEval generated code was never executed.
''')
env=json.loads((ROOT/'RUNTIME_ENVIRONMENT_RECEIPT.json').read_text());env.update({'torch':'2.5.1+cu124','torch_cuda':'12.4','transformers':'4.53.1','datasets':'2.14.6','pyarrow':'18.0.0','triton':'3.1.0','accelerate':'1.1.1','peft':'0.21.0','gpu':'NVIDIA GeForce RTX 4080','driver':'580.178.04','dependency_fix_count':1,'dependency_fix':'isolated local version overlay; direct HF transport replaced by exact-revision mirror'});(ROOT/'RUNTIME_ENVIRONMENT_RECEIPT.json').write_text(json.dumps(env,indent=2,sort_keys=True)+'\n')
(ROOT/'R53_SOURCE_AND_CLOSEST_WORK_AUDIT.md').write_text('''# R53 source and closest-work audit

Pinned `NVlabs/Fast-dLLM@a9b81e4c...`; `v2/generation_functions.py` blob is `76fc22d1...`. Official A0 output matches the instrumented A0 exactly in both discovery domains. Fast-dLLM v2 already removes finished requests at block boundaries and uses cohort-wide refresh decisions. dInfer, dLLM-Serve, BlockServe, Sangam, BiCache and FluxServe already cover broad packing/batching/cache/graph ideas.

The direct A1 packing attempt reduced executed token rows by about 12.3% on GSM8K and 21.6% on HumanEval, but changed forced commits, complete discrete trajectories, and final tokens. The one allowed safe-bucket repair preserved the trajectory exactly but restored A0's forward/token-row work. Thus the apparent reduction is an algorithm-visible numerical/trajectory change, not a legal mapping gain. No hardware capability claim follows.
''')
(ROOT/'R53_DECISION.md').write_text('''# R53 decision

`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`

A0 instrumentation exactly reproduces official Fast-dLLM v2 outputs. Packed A1 omits passive reuse rows and lowers token-row execution, but changes forced-commit position/token decisions and final output trajectories in both GSM8K and HumanEval. The only permitted correctness repair keeps the physical safe bucket/cohort shape; it restores exact trajectories and outputs but provides zero forward/token-row reduction. Therefore no semantically legal work reduction survives, and formal timing, diagnostic D and holdout are prohibited.
''');(ROOT/'FINAL_DECISION.md').write_text('# Final decision\n\n`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`\n\nThe observed work reduction requires a different discrete decoder/cache trajectory. No formal performance or architecture residual is claimed. No R54/R55 work was started.\n');(ROOT/'README.md').write_text(f'# AWMA R53 online legal-workset qualification V1\n\nFinal state: `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`. Packed execution reduced rows only by changing the frozen trajectory; the safe repair preserved semantics but saved no work.\n\nDurable authority: `{DUR}`.\n');(ROOT/'REPORT.md').write_text((ROOT/'README.md').read_text())
# Raw index excludes the isolated environment and source git object database; package/source/model manifests bind them.
idx=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file()):
 rel=p.relative_to(ROOT)
 if rel.name in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json') or rel.parts[0]=='env' or '.git' in rel.parts:continue
 idx.append({'relative_path':str(rel),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(ROOT/'RAW_DATA_INDEX.tsv',idx);receipt={'stage':'AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1','final_state':'R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1','model_revision':model['revision'],'concurrency':4,'a0_official_match':True,'packed_a1_semantic_match':False,'safe_bucket_semantic_match':True,'safe_bucket_legal_work_reduction':False,'formal_discovery_points':0,'diagnostic_d':'NOT_TRIGGERED','holdout':'NOT_TRIGGERED','node164_authority':DUR,'raw_index_sha256':sha(ROOT/'RAW_DATA_INDEX.tsv')};(ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
compact=['README.md','REPORT.md','R53_SOURCE_AND_CLOSEST_WORK_AUDIT.md','PRE_EXECUTION_INVENTORY.md','MODEL_ADMISSION_RECEIPT.json','RUNTIME_ENVIRONMENT_RECEIPT.json','DATASET_SNAPSHOT_RECEIPT.json','REQUEST_SELECTION.tsv','PREREGISTRATION.json','SEMANTIC_TRAJECTORY_SCHEMA.md','LEGAL_WORK_LEDGER.tsv.gz','LEGAL_WORK_SUMMARY.tsv','A0_A1_SEMANTIC_EQUIVALENCE.tsv','DISCOVERY_TIMING_RESULTS.tsv','DISCOVERY_WORKSET_RESULTS.tsv','NSYS_DISCOVERY_SUMMARY.tsv','R53_DECISION.md','FINAL_DECISION.md','RAW_DATA_INDEX.tsv','FINAL_RECEIPT.json']
for n in compact:shutil.copy2(ROOT/n,PACK/n)
for p in PACK.glob('*.tsv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
# Preserve raw prompts byte-for-byte in raw authority; JSON-escape only the Git review copy.
q=read(PACK/'REQUEST_SELECTION.tsv')
for r in q:r['raw_prompt']=json.dumps(r['raw_prompt'],ensure_ascii=False);r['rendered_prompt']=json.dumps(r['rendered_prompt'],ensure_ascii=False)
write(PACK/'REQUEST_SELECTION.tsv',q)
(PACK/'COMPACT_NORMALIZATION.md').write_text('# Compact normalization\n\nRaw `REQUEST_SELECTION.tsv` retains exact multiline dataset text, including source trailing spaces. The Git review copy JSON-escapes `raw_prompt` and `rendered_prompt` only; decoding yields the exact original strings. Dataset receipt hashes bind the raw authority.\n')
files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!='SHA256SUMS');(PACK/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
raw_files=sorted(ROOT/n for n in compact);(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in raw_files))
REPORT.write_text('# AWMA R53 online workset qualification 109 V1 report\n\nFinal state: `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`. Review pack: `docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/`.\n');print(json.dumps(receipt,sort_keys=True))
