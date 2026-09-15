import json,csv,hashlib
from pathlib import Path
from tokenizers import Tokenizer
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload'); A=Path('/tmp/c16-v11-authority'); O=Path('docs/vm_tlb/review_packs/C16_QWEN3_AUTHORIZATION_174NEW_V12'); V=ROOT/'provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2'
slugs={'meta-llama/Llama-3.2-1B':'llama-3.2-1b','Qwen/Qwen2.5-0.5B-Instruct':'qwen2.5-0.5b-instruct','Qwen/Qwen2.5-7B-Instruct':'qwen2.5-7b-instruct-raw','Qwen/Qwen2.5-7B-Instruct-AWQ':'qwen2.5-7b-instruct-awq','Qwen/Qwen3-8B':'qwen3-8b','deepseek-ai/DeepSeek-V2-Lite':'deepseek-v2-lite'}
def main():
 O.mkdir();rows=[]
 for p in sorted(V.glob('*.json')):
  x=json.load(open(p));src=(A/'docs/vm_tlb/assets/c16/prospective_common_input_v1'/({'S0_TEXT':'TEXT','S1_CODE':'CODE','S2_TEXT':'TEXT','S2_CODE':'CODE','S2_STRUCTURED':'STRUCTURED','S3_TEXT':'TEXT','S4_STRUCTURED':'STRUCTURED'}[x['scenario']]+'.txt')).read_text();tok=Tokenizer.from_file(str(ROOT/'assets/models'/slugs[x['model_id']]/x['revision']/'tokenizer.json'));ids=tok.encode(src,add_special_tokens=False).ids[:len(x['token_ids'][0])];rows.append({'payload':p.name,'result':'PASS' if ids==x['token_ids'][0] else 'FAIL'})
 with open(O/'V2_CANONICAL_REVALIDATION.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=['payload','result'],delimiter='\t');w.writeheader();w.writerows(rows)
 ok=all(x['result']=='PASS' for x in rows); auth={'decision':'QWEN3_EXECUTION_AUTHORIZED' if ok else 'QWEN3_EXECUTION_NOT_AUTHORIZED','v2_bindings':len(rows),'v2_status':'V2_CANONICAL_TOKENIZER_VALIDATED' if ok else 'FAIL','execution_mode':'EXACT_SEMANTIC_LAYER_STREAMING_REPLAY','gpu_capacity':'EXECUTION_MODE_SELECTOR','producer_runtime_api_issues':'PREFLIGHT_NOT_SCIENTIFIC_BLOCKER','scenario_policy':['S2','S3'],'stop_conditions':['hash_mismatch','terminal_failure','overflow_drop','semantic_anchor_failure'],'qwen3_30b':'OUT_OF_SCOPE'}
 open(O/'QWEN3_EXECUTION_AUTHORIZATION.json','w').write(json.dumps(auth,indent=2)+'\n');open(O/'FINAL_DECISION.json','w').write(json.dumps({'decision':'C16_QWEN3_AUTHORIZATION_174NEW_V12_PASS' if ok else 'FAIL_CLOSED','qwen3_8b_ready':ok},indent=2)+'\n');open(O/'POLICY.md','w').write('No GPU execution in authorization. Native full resident only if preflight proves feasible; else exact semantic layer streaming replay.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
main()
