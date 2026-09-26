#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,platform,subprocess
from pathlib import Path
import pyarrow.parquet as pq
from transformers import AutoTokenizer
ROOT=Path('/data/c16/awma/r53_online_workset_qualification_20260927');MODEL=ROOT/'model/Fast_dLLM_v2_1.5B_25093b6f';SRC=ROOT/'source/Fast-dLLM';ENV=ROOT/'env'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def jsha(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def main():
 tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,trust_remote_code=True);spec=[('GSM8K',ROOT/'data/gsm8k_740312ad/main/test-00000-of-00001.parquet','question','740312add88f781978c0658806c59bc2815b9866'),('HumanEval',ROOT/'data/humaneval_7dce6050/openai_humaneval/test-00000-of-00001.parquet','prompt','7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544')];rows=[];selected={}
 for domain,path,field,rev in spec:
  data=pq.read_table(path).to_pylist();cand=[]
  for i,r in enumerate(data):
   cid=f'gsm8k/main/test/{i}' if domain=='GSM8K' else r['task_id'];raw=r[field];key=hashlib.sha256((cid+'\n'+raw).encode()).hexdigest();cand.append((key,cid,raw,i))
  cand.sort();chosen=cand[:8];selected[domain]=[]
  for rank,(key,cid,raw,index) in enumerate(chosen):
   cohort='DISCOVERY' if rank<4 else 'HOLDOUT';instruction=(raw+'\n\nPlease reason step by step, and put your final answer within \\boxed{}.') if domain=='GSM8K' else ('Complete the following Python function. Return only the completed code; do not execute it.\n\n'+raw);rendered=tok.apply_chat_template([{'role':'user','content':instruction}],tokenize=False,add_generation_prompt=True);ids=tok(rendered,add_special_tokens=False)['input_ids'];row={'domain':domain,'cohort':cohort,'selection_rank':rank,'canonical_id':cid,'source_row_index':index,'selection_sha256':key,'raw_prompt_sha256':hashlib.sha256(raw.encode()).hexdigest(),'rendered_prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest(),'token_ids_sha256':jsha(ids),'token_count':len(ids),'raw_prompt':raw,'rendered_prompt':rendered,'token_ids_json':json.dumps(ids,separators=(',',':'))};rows.append(row);selected[domain].append(row)
 with (ROOT/'REQUEST_SELECTION.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 (ROOT/'selected_requests.json').write_text(json.dumps(selected,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
 model_files=[]
 for p in sorted(x for x in MODEL.rglob('*') if x.is_file() and '.cache' not in x.parts):model_files.append({'path':str(p.relative_to(MODEL)),'size':p.stat().st_size,'sha256':sha(p)})
 m={'status':'MODEL_PINNED','repo':'Efficient-Large-Model/Fast_dLLM_v2_1.5B','revision':'25093b6f63300adfd57f72145083c8a528fe4f16','revision_metadata':(MODEL/'.cache/huggingface/download/config.json.metadata').read_text().splitlines()[0],'model_root':str(MODEL),'files':model_files,'model_safetensors_sha256':sha(MODEL/'model.safetensors'),'source_repo':'NVlabs/Fast-dLLM','source_commit':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip(),'source_tree':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD^{tree}'],text=True).strip(),'generation_functions_blob':subprocess.check_output(['git','-C',str(SRC),'hash-object','v2/generation_functions.py'],text=True).strip()};(ROOT/'MODEL_ADMISSION_RECEIPT.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
 d={'status':'DATASETS_AND_REQUESTS_FROZEN_BEFORE_MODEL_TIMING','datasets':[{'repo':'openai/gsm8k','revision':spec[0][3],'config':'main','split':'test','rows':len(pq.read_table(spec[0][1])),'parquet_sha256':sha(spec[0][1])},{'repo':'openai/openai_humaneval','revision':spec[1][3],'split':'test','rows':len(pq.read_table(spec[1][1])),'parquet_sha256':sha(spec[1][1])}],'selection_rule':'SHA256(canonical_id + newline + exact_raw_prompt), first4 discovery next4 holdout','request_selection_sha256':sha(ROOT/'REQUEST_SELECTION.tsv'),'selected_requests_sha256':sha(ROOT/'selected_requests.json'),'humaneval_generated_code_execution':'PROHIBITED'};(ROOT/'DATASET_SNAPSHOT_RECEIPT.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
 freeze=subprocess.check_output([str(ENV/'bin/pip'),'freeze'],text=True);(ROOT/'environment_lock.txt').write_text(freeze);env={'status':'ISOLATED_ENVIRONMENT_PINNED','path':str(ENV),'python':platform.python_version(),'pip_freeze_sha256':sha(ROOT/'environment_lock.txt'),'c16_base_site_packages_read_only':'/data/c16/env/c16-py310/lib/python3.10/site-packages','accepted_c16_environment_modified':False};(ROOT/'RUNTIME_ENVIRONMENT_RECEIPT.json').write_text(json.dumps(env,indent=2,sort_keys=True)+'\n');print(json.dumps({'model':m['revision'],'requests':len(rows),'request_sha':d['request_selection_sha256'],'env_sha':env['pip_freeze_sha256']},sort_keys=True))
if __name__=='__main__':main()
