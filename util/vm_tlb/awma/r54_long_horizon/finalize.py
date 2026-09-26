#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,platform,shutil,sqlite3,subprocess
from pathlib import Path
ROOT=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-long-horizon-v1');MODEL=ROOT/'model/Qwen3_5_0_8B_c6046cd1';ENV=ROOT/'env';TSRC=ROOT/'source/transformers-main';PACK=WT/'docs/vm_tlb/review_packs/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1';REPORT=WT/'docs/vm_tlb/reports/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_109_V1_REPORT.md';DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r54_checkpoint_lifecycle_20260927';PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
can=json.loads((ROOT/'R54_FASTPATH_CANARY_RECEIPT.json').read_text());subprocess.run(['nsys','export','--type','sqlite','--force-overwrite','true','--output',str(ROOT/'raw/fastpath_r1/fastpath.sqlite'),str(ROOT/'raw/fastpath_r1/fastpath.nsys-rep')],check=True,stdout=subprocess.DEVNULL)
db=sqlite3.connect(f'file:{ROOT/"raw/fastpath_r1/fastpath.sqlite"}?mode=ro',uri=True);strings=dict(db.execute('select id,value from StringIds'));ks=[]
for x in db.execute('select gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,count(*) from CUPTI_ACTIVITY_KIND_KERNEL group by gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName order by count(*) desc limit 30'):
 gx,gy,gz,bx,by,bz,dn,sn,n=x;ks.append({'function':strings.get(dn) or strings.get(sn) or 'UNKNOWN','grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}','launch_count':n})
db.close();write(ROOT/'FASTPATH_KERNEL_STRATA.tsv',ks)
model_files=[]
for p in sorted(x for x in MODEL.rglob('*') if x.is_file() and '.cache' not in x.parts):model_files.append({'path':str(p.relative_to(MODEL)),'size':p.stat().st_size,'sha256':sha(p)})
(ROOT/'MODEL_ADMISSION_RECEIPT.json').write_text(json.dumps({'status':'MODEL_PINNED','repo':'Qwen/Qwen3.5-0.8B','revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb','metadata_revision':(MODEL/'.cache/huggingface/download/config.json.metadata').read_text().splitlines()[0],'model_safetensors_sha256':sha(MODEL/'model.safetensors-00001-of-00001.safetensors'),'files':model_files},indent=2,sort_keys=True)+'\n')
(ROOT/'environment_lock.txt').write_text(subprocess.check_output([str(ENV/'bin/pip'),'freeze'],text=True));runtime={'status':'R54_RUNTIME_FASTPATH_NOT_QUALIFIED','python':platform.python_version(),'torch':'2.5.1+cu124','torch_cuda':'12.4','transformers_source_commit':subprocess.check_output(['git','-C',str(TSRC),'rev-parse','HEAD'],text=True).strip(),'transformers_source_tree':subprocess.check_output(['git','-C',str(TSRC),'rev-parse','HEAD^{tree}'],text=True).strip(),'transformers_version':'5.18.0.dev0','system_cuda':'12.8','driver':'580.178.04','isolated_environment':str(ENV),'environment_lock_sha256':sha(ROOT/'environment_lock.txt'),'fixes':[{'id':1,'action':'install Transformers main commit to obtain qwen3_5 architecture','result':'PASS'},{'id':2,'action':'causal-conv1d build','result':'FAIL CUDA mismatch in isolated build environment (CUDA12.8 vs build torch CUDA13.0)'}],'missing_optimized_packages':['causal_conv1d','flash-linear-attention'],'fallback_observed':['causal_conv1d_fn -> reference PyTorch','chunk_gated_delta_rule -> reference PyTorch']};(ROOT/'RUNTIME_FASTPATH_RECEIPT.json').write_text(json.dumps(runtime,indent=2,sort_keys=True)+'\n')
(ROOT/'PRE_EXECUTION_INVENTORY.md').write_text('''# Pre-execution inventory

Node109 RTX4080/SM89, driver 580.178.04, and adequate disk/memory were confirmed. A dedicated R54 env was created; C16/R53 environments, system CUDA and driver were untouched. The exact Qwen3.5 snapshot was fetched through the revision-preserving mirror transport after direct Hub access stalled. The initial NSYS invocation before script upload is retained as an empty engineering failure; `fastpath_r1` is the only actual model canary.
''')
(ROOT/'R54_SOURCE_AND_CLOSEST_WORK_AUDIT.md').write_text('''# R54 source and closest-work audit

Round07 identifies Marconi, Sparse Prefix Caching, Tail-Replay, TreeWY, persistent-state accelerators and DAMP as closest work. This stage reached no lifecycle-cost conclusion because the optimized GDN runtime gate failed. Source inspection of Qwen3.5 shows fast kernels are supplied through `causal_conv1d` and `fla` hub-kernel paths; both were absent at runtime, and the executed canary explicitly reported reference fallback. Slow fallback timing is not used as R54 evidence.
''')
(ROOT/'R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md').write_text('''# R55 platform and closest-work audit

Source-only audit based on Round07: Transformer Engine NVFP4 requires rowwise/columnwise quantized layouts and scales; transposition-invariant FP4 directly addresses transpose-scale inconsistency; NVIDIA NVFP4 pretraining and Quartet II cover stable low-precision training; MOSS covers online scaling/dequantization overhead. RTX4080 lacks NVFP4-native hardware behavior, so no R55 GPU performance experiment was run and no platform throughput claim is made.
''')
(ROOT/'PREFIX_FIXTURE_RECEIPT.json').write_text(json.dumps({'status':'NOT_RUN_RUNTIME_FASTPATH_GATE','r53_request_authority':'843ad43ad33153bf73a0e51aed6d8ac309356cae','reason':'no checkpoint performance work after fallback admission failure'},indent=2,sort_keys=True)+'\n')
write(ROOT/'R54_EXACT_STATE_SCHEMA.tsv',[{'status':'NOT_ENUMERATED_RUNTIME_FASTPATH_GATE','layer_index':'N/A','layer_type':'N/A','field_name':'N/A','shape':'N/A','dtype':'N/A','device':'N/A','logical_bytes':'N/A','storage_bytes':'N/A','mutable':'N/A','exact_continuation_required':'N/A','state_class':'N/A','snapshot_inclusion':'N/A','evidence':'runtime performance gate failed before state authority instrumentation'}])
(ROOT/'PREREGISTRATION.json').write_text(json.dumps({'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1','status':'NOT_ENTERED_RUNTIME_FASTPATH_GATE','model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb','planned_arms':['P0','P1_D512','P2_D512','P1_D2048','P2_D2048'],'planned_prefix_tokens':4096,'planned_chunk_tokens':512,'planned_repetitions':7,'materiality':'>=5% and >3x jitter','prohibited':'slow fallback timing'},indent=2,sort_keys=True)+'\n')
for n,cols in [('SEMANTIC_QUALIFICATION.tsv',['condition','status','reason']),('SNAPSHOT_PRODUCTION_TIMING.tsv',['arm','status','reason']),('SNAPSHOT_COPY_ACCOUNTING.tsv',['arm','status','reason']),('RESTORE_SEMANTIC_RESULTS.tsv',['condition','status','reason']),('RESTORE_TIMING.tsv',['condition','status','reason']),('AMORTIZATION_RESULTS.tsv',['scenario','status','reason'])]:write(ROOT/n,[{c:('NOT_RUN' if c=='status' else ('RUNTIME_FASTPATH_NOT_QUALIFIED' if c=='reason' else 'N/A')) for c in cols}])
(ROOT/'R54_DECISION.md').write_text('''# R54 decision

`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`

The exact Qwen3.5 model loaded and executed, but the actual Gated-DeltaNet canary reported reference PyTorch fallback for both causal convolution and chunk gated-delta rule. Transformers source inspection confirms those are the fallback implementations. Two bounded repairs were exhausted: installing a source-pinned Transformers version enabled Qwen3.5 architecture support, while causal-conv1d build failed on a CUDA/toolchain mismatch. Flash-linear-attention remained unavailable. No slow fallback checkpoint timing is claimed.
''')
(ROOT/'FINAL_DECISION.md').write_text('# Final decision\n\n`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`\n\nNo checkpoint production, restore, amortization, holdout, NCU, node174 or R55 GPU performance work ran after fast-path failure.\n');(ROOT/'README.md').write_text(f'# AWMA R54 exact recurrent checkpoint lifecycle V1\n\nFinal state: `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`. Exact model load succeeded but GDN used documented reference fallbacks; performance lifecycle science stopped before state/timing phases.\n\nDurable authority: `{DUR}`.\n');(ROOT/'REPORT.md').write_text((ROOT/'README.md').read_text())
idx=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file()):
 rel=p.relative_to(ROOT)
 if rel.name in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json') or rel.parts[0]=='env' or '.git' in rel.parts:continue
 idx.append({'relative_path':str(rel),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(ROOT/'RAW_DATA_INDEX.tsv',idx);final={'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1','final_state':'R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1','model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb','fastpath_canary':can,'node164_authority':DUR,'raw_index_sha256':sha(ROOT/'RAW_DATA_INDEX.tsv'),'checkpoint_timing_points':0};(ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n')
compact=['README.md','REPORT.md','PRE_EXECUTION_INVENTORY.md','R54_SOURCE_AND_CLOSEST_WORK_AUDIT.md','R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md','MODEL_ADMISSION_RECEIPT.json','RUNTIME_FASTPATH_RECEIPT.json','R54_FASTPATH_CANARY_RECEIPT.json','FASTPATH_KERNEL_STRATA.tsv','PREFIX_FIXTURE_RECEIPT.json','R54_EXACT_STATE_SCHEMA.tsv','PREREGISTRATION.json','SEMANTIC_QUALIFICATION.tsv','SNAPSHOT_PRODUCTION_TIMING.tsv','SNAPSHOT_COPY_ACCOUNTING.tsv','RESTORE_SEMANTIC_RESULTS.tsv','RESTORE_TIMING.tsv','AMORTIZATION_RESULTS.tsv','R54_DECISION.md','FINAL_DECISION.md','RAW_DATA_INDEX.tsv','FINAL_RECEIPT.json']
for n in compact:shutil.copy2(ROOT/n,PACK/n)
for p in PACK.glob('*.tsv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!='SHA256SUMS');(PACK/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));raw_files=sorted(ROOT/n for n in compact);(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in raw_files));REPORT.write_text('# AWMA R54 exact recurrent checkpoint lifecycle 109 V1 report\n\nFinal state: `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`.\n');print(json.dumps(final,sort_keys=True))
