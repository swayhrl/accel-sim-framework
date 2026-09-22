#!/usr/bin/env python3
"""Build one Pipeline V1 staging bundle without mutating immutable raw evidence."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path

REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v40-publish-109-v1')
sys.path.insert(0,str(REPO/'util/vm_tlb/c16/data_plane'))
from pipeline import run_id
RAW=Path('/data/c16/olmoe_v40_publish_v1/re_audit'); AUTH=Path('/data/c16/olmoe_v40_publish_v1/selector_authority')
STAGING_ROOT=Path('/data/c16/olmoe_v40_publish_v1/staging'); READY=Path('/data/c16/olmoe_v40_publish_v1/ready')
ATTEMPTS=Path('/data/c16/olmoe_v40/typed_sweep/ATTEMPTS.jsonl')
TOOL=Path('/data/c16/tools/v40_p5_c16warp1/mem_trace.so'); MODEL=Path('/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
 rid=run_id('OLMoE-1B-7B-0125-Instruct','S2-T2048-D32','decode32','NVBit1771-C16WARP1','expert58-down-proj-actual-a')
 staging=STAGING_ROOT/rid
 if staging.exists() or (READY/rid).exists():raise SystemExit('run collision')
 staging.mkdir(parents=True)
 for src in (RAW/'FORMAL_243_SUMMARY.json',RAW/'FORMAL_243_ANALYSIS.json',RAW/'FORMAL_243_SHARDS.jsonl',RAW/'FORMAL_243_PER_SHARD_ANALYSIS.jsonl',RAW/'TYPED_CANARY_RECEIPT.json'):
  copy(src,staging/'re_audit'/src.name)
 for src in (AUTH/'SELECTOR_AUTHORITY_REPAIR_V1.json',AUTH/'VARIANT_A_COMPLETE_STATIC_SELECTOR.canonical_v1.json',Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')):
  copy(src,staging/'selector_authority'/src.name)
 for src in (TOOL,REPO/'util/vm_tlb/c16/olmoe_v40/c16warp1_v40_validator.py',REPO/'util/vm_tlb/c16/olmoe_v40/v40_formalize_243.py',REPO/'util/vm_tlb/c16/olmoe_v40/v40_analyze_243.py',REPO/'util/vm_tlb/c16/olmoe_v40/v40_selector_authority.py'):
  copy(src,staging/'software'/src.name)
 for item in (json.loads(x) for x in ATTEMPTS.read_text().splitlines() if x):
  root=Path(item['attempt_root']);base=staging/'shards'/f"static_{item['static_index']}"
  for name in ('trace.bin','ADDRESS_CONTEXT.json','SUPERVISOR_RECEIPT.json','result.json','stdout.log','stderr.log','output.sha256','C16WARP1_REAUDIT_VALIDATOR_RECEIPT.json'):
   copy(root/name,base/name)
 config=MODEL/'config.json'; gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'],text=True).splitlines()[0].split(', ')
 commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
 manifest={'schema_version':1,'run_id':rid,'created_at_utc':'2026-09-22T00:00:00+00:00','scientific_status':'FORMAL','producer':{'hostname':'109','gpu_name':gpu[0],'gpu_uuid':gpu[1],'driver':gpu[2],'cuda':'12.8'},'git':{'repository':'swayhrl/accel-sim-framework','commit':commit,'dirty':False},'model':{'model_id':'allenai/OLMoE-1B-7B-0125-Instruct','revision':'b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e','asset_receipt_sha256':sha(config)},'input':{'binding_id':'S2_TEXT_B1_T2048_D32_EXPERT58_INPUT','authority_status':'NODE164_AUTHORITY_REFERENCE','receipt_sha256':sha(Path('/data/c16/olmoe_v39r2/expert58_d32_input.pt')),'token_ids_sha256_or_semantic_hash':'S2_TEXT_B1_T2048_D32'},'scenario':{'batch':1,'prefill_tokens':2048,'decode_tokens':32,'input_class':'S2_TEXT','phase':'decode32'},'runtime':{'python':'c16-py310','torch':'BF16','transformers':'local','dtype':'bfloat16','attention_backend':'native'},'capture':{'instrument':'NVBit C16WARP1','tool_version':'1.7.7.1','tool_identity_sha256_if_applicable':sha(TOOL),'target':'layer1 expert58 down_proj actual-JIT variant A','exact_argv':'CPU re-audit of immutable V40 shards'},'artifacts':[]}
 path=staging/'RUN_MANIFEST.input.json';path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'run_id':rid,'staging':str(staging),'ready_root':str(READY),'manifest_input':str(path)}))
if __name__=='__main__':main()
