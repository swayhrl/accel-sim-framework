import json,csv,hashlib
from pathlib import Path
from tokenizers import Tokenizer
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload'); A=Path('/tmp/c16-v11-authority'); O=Path('docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11')
slug={'Llama-3.2-1B':'llama-3.2-1b','Qwen2.5-0.5B-Instruct':'qwen2.5-0.5b-instruct','Qwen2.5-7B raw':'qwen2.5-7b-instruct-raw','Qwen2.5-7B AWQ':'qwen2.5-7b-instruct-awq','Qwen3-8B':'qwen3-8b','DeepSeek-V2-Lite':'deepseek-v2-lite'}
def main():
 p=A/'docs/vm_tlb/review_packs/C16_PROSPECTIVE_COMMON_INPUT_174NEW_LANEB_V8/PROSPECTIVE_BINDING_INDEX.tsv'; rows=list(csv.DictReader(open(p),delimiter='\t')); out=[]; v2=ROOT/'provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2'
 if v2.exists(): raise RuntimeError('V2 already exists; no overwrite')
 v2.mkdir(parents=True)
 for r in rows:
  x=json.load(open(r['payload_path'])); src=(A/'docs/vm_tlb/assets/c16/prospective_common_input_v1'/(r['source_class']+'.txt')).read_text(); tok=Tokenizer.from_file(str(ROOT/'assets/models'/slug[r['model_label']]/r['revision']/'tokenizer.json')); ids=tok.encode(src,add_special_tokens=False).ids[:int(r['context_tokens'])]; ok=ids==x['token_ids'][0]; v={'supersedes':'V1_PROSPECTIVE_AXIS_ONLY','model_id':r['model_id'],'revision':r['revision'],'scenario':r['scenario'],'token_ids':[ids]*int(r['batch']),'add_special_tokens':False}; fn=slug[r['model_label']]+'__'+r['scenario']+'.json'; (v2/fn).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');out.append({'model':r['model_label'],'scenario':r['scenario'],'result':'PASS' if ok else 'FAIL','expected_sha':r['token_sequence_sha256'],'actual_sha':hashlib.sha256(json.dumps([ids],separators=(',',':')).encode()).hexdigest(),'source_prefix_bytes':len(src.encode())})
 with open(O/'CANONICAL_TOKENIZER_42_VALIDATION.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
 d={'status':'V1_CANONICAL_TOKENIZER_VALIDATED' if all(x['result']=='PASS' for x in out) else 'V1_CANONICAL_TOKENIZER_MISMATCH_V2_REQUIRED','bindings':len(out),'wheel_sha256':'1fd9fee817f655a8f50049f685e224828abfadd436b8ff67979fc1d054b435f1'};open(O/'PROSPECTIVE_TOKENIZER_VALIDATION.json','w').write(json.dumps(d,indent=2)+'\n')
main()
