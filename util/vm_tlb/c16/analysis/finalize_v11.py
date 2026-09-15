import json,hashlib
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11')
d=json.loads((O/'FINAL_DECISION.json').read_text());d.update({'decision':'C16_UNIFIED_CONSUMER_174NEW_V11_PASS_WITH_SCOPED_GAPS','prospective_common_input':'V1_CANONICAL_TOKENIZER_MISMATCH_V2_CREATED','v1_preserved':True,'v2_path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2','qwen3_8b_ready':False,'qwen3_8b_gate':'V2_PROSPECTIVE_AUTHORITY_REVIEW_AND_FULL_BINARY_V10_CONSUMER_FINGERPRINT_REQUIRED','ncu_status':'NCU_NUMERIC_ANALYSIS_PENDING_DURABLE_EXPORT'})
(O/'FINAL_DECISION.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
with (O/'SHA256SUMS').open('w') as f:
 for p in sorted(O.iterdir()):
  if p.name!='SHA256SUMS':f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
