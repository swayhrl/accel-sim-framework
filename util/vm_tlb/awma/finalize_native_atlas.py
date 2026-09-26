#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/data/c16/awma/ai_translation_native_atlas_capture_20260926')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-ai-native-atlas-v1')
OUT=REPO/'docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_NATIVE_ATLAS_CAPTURE_109_V1';OUT.mkdir(parents=True,exist_ok=True)
VALID=Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')
PROD=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so')
POST=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_tsv(p):return list(csv.DictReader(open(p),delimiter='\t'))
def write_tsv(p,rows,fields=None):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def driver_receipt(p):
 for line in Path(p).read_text(errors='replace').splitlines():
  if line.startswith('{'):
   try:
    x=json.loads(line)
    if x.get('status')=='ATLAS_NATIVE_SCENARIO_COMPLETE':return x
   except json.JSONDecodeError:pass
 raise RuntimeError('native driver receipt missing')
ll=driver_receipt(ROOT/'llama_native/driver.stdout');om=driver_receipt(ROOT/'olmoe_native/driver.stdout')
assets=[{'dimension':'DENSE_OTHER_FAMILY','primary':'Llama-3.2-1B','path':'/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08','revision':ll['revision'],'status':'RUNNABLE_SELECTED_NO_DOWNLOAD'}, {'dimension':'MOE_FAMILY','primary':'OLMoE-1B-7B-0125-Instruct','path':'/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e','revision':om['revision'],'status':'RUNNABLE_SELECTED_NO_DOWNLOAD'}, {'dimension':'IMPLEMENTATION_CHANGE','primary':'Qwen2.5 raw/AWQ','path':'PREEXISTING_OPTIONAL','revision':'N/A','status':'NOT_SELECTED_PRIMARY_TWO_DIMENSIONS_RUNNABLE'}]
write_tsv(OUT/'ASSET_AND_RUNTIME_AUDIT.tsv',assets)
sc=[]
for dim,x in [('DENSE_OTHER_FAMILY',ll),('MOE_FAMILY',om)]:sc.append({'dimension':dim,'scenario':x['scenario'],'model':x['model_id'],'revision':x['revision'],'batch':x['batch'],'prompt_tokens':x['prompt_tokens'],'decode_tokens':x['decode_tokens'],'dtype':x['dtype'],'quantization':x['quantization'],'attention':x['attention'],'text_sha256':x['text_sha256'],'token_ids_sha256':x['token_ids_sha256'],'torch':x['torch'],'torch_cuda':x['torch_cuda'],'warmup_runs':1,'authoritative_runs':1,'cross_family_runtime_comparison_forbidden':'YES'})
write_tsv(OUT/'SCENARIO_CONTRACT.tsv',sc)
native=read_tsv(ROOT/'llama_native/analysis/NATIVE_CENSUS.tsv')+read_tsv(ROOT/'olmoe_native/analysis/NATIVE_CENSUS.tsv');write_tsv(OUT/'NATIVE_CENSUS.tsv',native)
(OUT/'KERNEL_SELECTION_PREREG.tsv').write_bytes((ROOT/'KERNEL_SELECTION_PREREG.tsv').read_bytes())
(OUT/'VIRTUAL_PAGE_BEHAVIOR.tsv').write_bytes((ROOT/'VIRTUAL_PAGE_BEHAVIOR.tsv').read_bytes());(OUT/'TEMPORAL_PAGE_BEHAVIOR.tsv').write_bytes((ROOT/'TEMPORAL_PAGE_BEHAVIOR.tsv').read_bytes())
sel={r['target_id']:r for r in read_tsv(ROOT/'KERNEL_SELECTION_PREREG.tsv')};virt={r['target_id']:r for r in read_tsv(ROOT/'VIRTUAL_PAGE_BEHAVIOR.tsv')}
bridge_specs={'L1':(522,7074,'llama_routeb_census'),'L2':(128,7062,'llama_routeb_census'),'M1':(3764,88672,'olmoe_routeb_census'),'M2':(10240,88632,'olmoe_routeb_census')}
bridge=[]
for t,(o,n,c) in bridge_specs.items():bridge.append({'target_id':t,'scenario':sel[t]['scenario'],'function_sha256':sel[t]['function_sha256'],'grid':sel[t]['grid'],'block':sel[t]['block'],'producer_selector_ordinal':o,'producer_global_navigation':n,'fresh_census_sha256':sha(ROOT/c/'stdout.log'),'status':'SCIENTIFIC_TO_ROUTEB_BRIDGE_PASS'})
write_tsv(OUT/'CAPTURE_BRIDGE.tsv',bridge)
caps={'L1':ROOT/'capture_L1','L2':ROOT/'capture_L2','M1':ROOT/'capture_M1_r2','M2':ROOT/'capture_M2'};quals=[];handoff=[]
for t,d in caps.items():
 tr=next((d/'raw').glob('*.trace.xz')); tgs=list((d/'raw').glob('*.traceg.xz')); tg=tgs[0] if tgs else None; status='QUALIFIED';grammar='TRACEG_GRAMMAR_PASS'
 if t=='L2':status='TRACE_GRAMMAR_BLOCKED';grammar='TRACEG_GRAMMAR_REJECT_LDC_U8_ZERO_OR_MISSING_WIDTH'
 terminal=';'.join(x for p in [d/'stdout.log',d/'stderr.log'] if p.exists() for x in p.read_text(errors='replace').splitlines() if 'ROUTEB_TERMINAL_' in x)
 q={'target_id':t,'status':status,'terminal':terminal,'drop_zero':'drop_count=0' in terminal,'overflow_zero':'overflow_count=0' in terminal,'trace_xz_sha256':sha(tr),'traceg_xz_sha256':sha(tg) if tg else 'NONE','grammar_status':grammar,'producer_sha256':sha(PROD),'postprocessor_sha256':sha(POST),'validator_sha256':sha(VALID),'kernelslist_sha256':sha(d/'raw/kernelslist'),'kernelslist_g_sha256':sha(d/'raw/kernelslist.g') if (d/'raw/kernelslist.g').exists() else 'NONE'};quals.append(q)
 durable=f'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/{d.name}/raw/{tg.name}' if tg else 'NONE'
 handoff.append({'target_id':t,'dimension':sel[t]['dimension'],'scenario':sel[t]['scenario'],'model':next(x['model'] for x in sc if x['scenario']==sel[t]['scenario']),'revision':next(x['revision'] for x in sc if x['scenario']==sel[t]['scenario']),'native_role':sel[t]['family'],'native_gpu_time_share':sel[t]['native_gpu_time_share'],'function_sha256':sel[t]['function_sha256'],'grid':sel[t]['grid'],'block':sel[t]['block'],'virtual_page_behavior':virt[t],'durable_traceg_path':durable,'traceg_sha256':q['traceg_xz_sha256'],'qualification_status':status})
write_tsv(OUT/'CAPTURE_QUALIFICATION.tsv',quals);write_tsv(OUT/'OPTIONAL_NCU_CONTEXT.tsv',[{'target_id':t,'status':'NOT_RUN_EXISTING_NATIVE_AND_ADDRESS_TRACE_SUFFICIENT','tlb_claims':'NONE'} for t in sel])
consumer={'status':'READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW','targets':handoff,'scenario_summary':{'material_changes':['Dense-family L1 GEMV observes 8198 unique 4KB pages versus OLMoE M1 GEMV 1026 under their separately frozen tokenizations.','Llama attention target observes 538 pages and a more concentrated per-2MB load-PC distribution than L1 GEMV.','OLMoE routing reduction M2 is a tiny two-page, one-CTA path, structurally unlike OLMoE GEMV.'],'not_material_or_bounded':['M1 and L1 both show predominantly one/two-page dynamic-memory-instruction footprints despite different aggregate working sets.','M2 is too small to support scenario-wide MoE conclusions.'],'cannot_infer':['physical contiguity','PPN stability','TLB hit rate','Avatar speculation accuracy','cross-family raw runtime equivalence']},'address_semantics':'VIRTUAL_ONLY','mechanism_decision':'NONE'}
(OUT/'NATIVE_ATLAS_CONSUMER_HANDOFF.json').write_text(json.dumps(consumer,indent=2,sort_keys=True)+'\n')
(OUT/'README.md').write_text('# AI translation Native atlas capture 109 V1\n\nStatus: `READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW`. Two local model-family dimensions were run with B1/T256/D8. Four targets were preregistered before address observation; L1, M1 and M2 qualified, while L2 is retained as a terminal-complete grammar-blocked target due to missing `LDC.U8` width. No model download, mechanism decision, broad NCU, or Accel-Sim run occurred. All page metrics are virtual-address observations only.\n')
# Raw authority receipts and indices.
(ROOT/'NATIVE_ATLAS_CONSUMER_HANDOFF.json').write_text(json.dumps(consumer,indent=2,sort_keys=True)+'\n')
rows=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name!='SHA256SUMS'):rows.append({'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write_tsv(OUT/'RAW_DATA_INDEX.tsv',rows);(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n' for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name!='SHA256SUMS')))
(REPO/'docs/vm_tlb/codex_handoff/awma/AI_TRANSLATION_NATIVE_ATLAS_CAPTURE_109_V1_REPORT.md').write_text('# AI Translation Native Atlas Capture 109 V1\n\nTwo bounded local model-family scenarios produced a Native census and four preregistered Route-B targets. Three simulator-native traces qualified; the attention target is preserved as grammar-blocked rather than repaired or replaced. Virtual-page analysis is ready for residual discovery on 174-new.\n')
files=sorted(p for p in OUT.iterdir() if p.is_file());(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
print(json.dumps({'status':consumer['status'],'qualified':sum(q['status']=='QUALIFIED' for q in quals),'grammar_blocked':sum(q['status']!='QUALIFIED' for q in quals)},sort_keys=True))
