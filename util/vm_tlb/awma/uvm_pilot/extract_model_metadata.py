#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re
from pathlib import Path
from safetensors import safe_open
ROOT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926');ROOT.mkdir(parents=True,exist_ok=True)
def child(p):
 ds=sorted(x for x in p.iterdir() if x.is_dir());return ds[0] if ds else p
MODELS=[('DENSE_SELECTED','Qwen3-8B',child(Path('/data/c16/models/.incoming/qwen3_8b'))),('KV_SELECTED','Llama-3.2-1B',Path('/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08')),('MOE_SELECTED','OLMoE-1B-7B',Path('/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e')),('MOE_LARGER_AUDIT','DeepSeek-V2-Lite',child(Path('/data/c16/models/.incoming/deepseek_v2_lite')))]
SZ={'F64':8,'F32':4,'F16':2,'BF16':2,'I64':8,'I32':4,'I16':2,'I8':1,'U8':1,'BOOL':1}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
rows=[];summaries=[]
for role,name,path in MODELS:
 cfg=json.loads((path/'config.json').read_text());files=sorted(path.glob('*.safetensors'));tmp=[]
 for fp in files:
  fsha=sha(fp)
  with safe_open(fp,framework='pt',device='cpu') as sf:
   for key in sf.keys():
    sl=sf.get_slice(key);shape=list(sl.get_shape());dtype=str(sl.get_dtype()).replace('torch.','').upper();n=1
    for x in shape:n*=x
    b=n*SZ.get(dtype,0);lm=re.search(r'(?:layers|layer)\.(\d+)',key);em=re.search(r'experts?\.(\d+)',key);expert=('expert' in key.lower() and ('weight' in key.lower() or 'w1' in key.lower() or 'w2' in key.lower() or 'w3' in key.lower()))
    tmp.append({'asset_role':role,'model':name,'revision':path.name,'model_path':str(path),'tensor_name':key,'tensor_pattern':re.sub(r'\.(\d+)\.',r'.{N}.',key),'shape':json.dumps(shape,separators=(',',':')),'dtype':dtype,'byte_count':b,'layer_id':lm.group(1) if lm else 'N/A','expert_id':em.group(1) if em else 'N/A','tensor_group':'EXPERT' if expert else 'NON_EXPERT','source_file':fp.name,'source_file_sha256':fsha})
 total=sum(x['byte_count'] for x in tmp);expert=sum(x['byte_count'] for x in tmp if x['tensor_group']=='EXPERT');non=total-expert
 for x in tmp:x.update(total_parameter_bytes=total,expert_pool_bytes=expert,non_expert_bytes=non)
 rows+=tmp;summaries.append({'asset_role':role,'model':name,'revision':path.name,'model_path':str(path),'model_type':cfg.get('model_type'),'tensor_count':len(tmp),'total_parameter_bytes':total,'expert_pool_bytes':expert,'non_expert_bytes':non,'config_sha256':sha(path/'config.json'),'runnable_preexisting':'YES' if role in ('KV_SELECTED','MOE_SELECTED') else 'METADATA_ONLY'})
with (ROOT/'MODEL_ASSET_METADATA.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
with (ROOT/'MODEL_ASSET_SUMMARY.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]),delimiter='\t');w.writeheader();w.writerows(summaries)
llama=MODELS[1][2];cfg=json.loads((llama/'config.json').read_text());layers=cfg['num_hidden_layers'];kvh=cfg['num_key_value_heads'];hd=cfg.get('head_dim',cfg['hidden_size']//cfg['num_attention_heads']);bpe=2;bpt=layers*kvh*hd*2*bpe;context=4096;V=17171480576;points=[]
for pid,ratio in [('RESIDENT',.75),('NEAR_CAPACITY',.95),('MILD_OVERSUB',1.10)]:
 conc=max(1,int((V*ratio)//(context*bpt)));total=conc*context*bpt;points.append({'point_id':pid,'layers':layers,'kv_heads':kvh,'head_dim':hd,'dtype_bytes':bpe,'k_and_v':2,'bytes_per_token_sequence':bpt,'context_tokens':context,'concurrent_sequences':conc,'total_kv_bytes':total,'actual_vram_ratio':total/V,'variable':'CONCURRENCY_ONLY','access_fidelity':'LAYOUT_EXACT_ACCESS_APPROXIMATE'})
with (ROOT/'KV_LAYOUT_POINTS.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(points[0]),delimiter='\t');w.writeheader();w.writerows(points)
print(json.dumps({'models':summaries,'kv_points':points},sort_keys=True))
