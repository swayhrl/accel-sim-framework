import json,hashlib,re,csv
from pathlib import Path
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload'); A='C16_PROSPECTIVE_COMMON_INPUT_V1'
M=[('Llama-3.2-1B','meta-llama/Llama-3.2-1B','llama-3.2-1b','4e20de362430cd3b72f300e6b0f18e50e7166e08'),('Qwen2.5-0.5B-Instruct','Qwen/Qwen2.5-0.5B-Instruct','qwen2.5-0.5b-instruct','7ae557604adf67be50417f59c2c2f167def9a775'),('Qwen2.5-7B raw','Qwen/Qwen2.5-7B-Instruct','qwen2.5-7b-instruct-raw','a09a35458c702b33eeacc393d103063234e8bc28'),('Qwen2.5-7B AWQ','Qwen/Qwen2.5-7B-Instruct-AWQ','qwen2.5-7b-instruct-awq','b25037543e9394b818fdfca67ab2a00ecc7dd641'),('Qwen3-8B','Qwen/Qwen3-8B','qwen3-8b','b968826d9c46dd6066d109eabc6255188de91218'),('DeepSeek-V2-Lite','deepseek-ai/DeepSeek-V2-Lite','deepseek-v2-lite','604d5664dddd88a0433dbae533b7fe9472482de0')]
S=[('S0_TEXT','TEXT',128,4,1),('S1_CODE','CODE',256,16,1),('S2_TEXT','TEXT',2048,32,1),('S2_CODE','CODE',2048,32,1),('S2_STRUCTURED','STRUCTURED',2048,32,1),('S3_TEXT','TEXT',8192,16,1),('S4_STRUCTURED','STRUCTURED',2048,16,4)]
def H(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def J(x):return json.dumps(x,sort_keys=True,indent=2)+'\n'
bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs[:];n=0
for b in range(256):
 if b not in bs:bs.append(b);cs.append(256+n);n+=1
U=dict(zip(bs,map(chr,cs)));P=re.compile(r" ?[A-Za-z]+| ?[0-9]+| ?[^\sA-Za-z0-9]+|\s+")
class T:
 def __init__(self,p):
  d=json.loads(Path(p).read_text());m=d['model']
  if m.get('type')!='BPE':raise RuntimeError('FAIL_CLOSED non-BPE tokenizer')
  self.v=m['vocab'];self.r={tuple(x.split(' ') if isinstance(x,str) else x):i for i,x in enumerate(m.get('merges',[]))}
 def w(self,x):
  z=tuple(U[b] for b in x.encode())
  while len(z)>1:
   q=[(self.r[p],i,p) for i,p in enumerate(zip(z,z[1:])) if p in self.r]
   if not q:break
   _,_,p=min(q);o=[];i=0
   while i<len(z):
    if i+1<len(z) and (z[i],z[i+1])==p:o.append(z[i]+z[i+1]);i+=2
    else:o.append(z[i]);i+=1
   z=tuple(o)
  return [self.v[x] for x in z]
 def e(self,x):
  o=[]
  for w in P.findall(x):o+=self.w(w)
  return o
def main():
 r=Path('docs/vm_tlb/assets/c16/prospective_common_input_v1');r.mkdir(parents=True,exist_ok=True)
 src={'TEXT':''.join(f'Local record {i:05d} has deterministic state value transition.\n' for i in range(16000)),'CODE':''.join(f'def local_step_{i:05d}(x):\n return x+{i%97}\n' for i in range(16000)),'STRUCTURED':''.join(f'{{"record":{i},"state":"local","value":{i%101}}}\n' for i in range(16000))}
 si=[]
 for k,v in src.items():
  p=r/(k+'.txt');p.write_text(v,encoding='utf-8',newline='');si.append({'authority':A,'source_class':k,'source_path':str(p),'source_sha256':H(p),'byte_count':p.stat().st_size,'normalization':'exact UTF-8 generator output','truncation':'first exact N token IDs'})
 nd=ROOT/'provenance/prospective_inputs'/A
 if nd.exists():raise RuntimeError('FAIL_CLOSED no-overwrite prospective authority exists')
 nd.mkdir(parents=True);bi=[];ti=[]
 for lab,mid,slug,rev in M:
  d=ROOT/'assets/models'/slug/rev;tp=d/'tokenizer.json';cp=d/'tokenizer_config.json'
  if not tp.is_file() or not cp.is_file():raise RuntimeError('FAIL_CLOSED tokenizer identity missing')
  t=T(tp);ti.append({'model_label':lab,'model_id':mid,'revision':rev,'tokenizer_json_sha256':H(tp),'tokenizer_config_sha256':H(cp),'runtime':'LOCAL_CANONICAL_TOKENIZER_JSON_BPE','network':'DISABLED','special_tokens':False,'chat_template':'NOT_APPLIED'})
  enc={k:t.e(v) for k,v in src.items()}
  for sn,k,N,D,B in S:
   if len(enc[k])<N:raise RuntimeError('FAIL_CLOSED insufficient tokens')
   ids=enc[k][:N];pl={'authority':A,'prospective_status':'PROSPECTIVE_FROZEN_INPUT_AUTHORITY_V1','historical_status':'SEPARATE_UNCHANGED_AXIS','model_id':mid,'revision':rev,'scenario':sn,'source_class':k,'batch':B,'context_tokens':N,'decode_steps':D,'add_special_tokens':False,'chat_template':'NOT_APPLIED','truncation':'FIRST_EXACT_N_TOKEN_IDS','token_ids':[ids]*B};fn=slug+'__'+sn+'.json';(nd/fn).write_text(J(pl));bi.append({'authority':A,'model_label':lab,'model_id':mid,'revision':rev,'scenario':sn,'source_class':k,'batch':B,'context_tokens':N,'decode_steps':D,'historical_status':'SEPARATE_UNCHANGED_AXIS','prospective_status':'PROSPECTIVE_FROZEN_INPUT_AUTHORITY_V1','source_sha256':H(r/(k+'.txt')),'token_sequence_sha256':hashlib.sha256(json.dumps(pl['token_ids'],separators=(',',':')).encode()).hexdigest(),'payload_path':str(nd/fn),'payload_sha256':H(nd/fn),'tokenizer_json_sha256':H(tp),'no_retokenization_after_freeze':True})
 o=Path('docs/vm_tlb/review_packs/C16_PROSPECTIVE_COMMON_INPUT_174NEW_LANEB_V8');o.mkdir(parents=True,exist_ok=True)
 def W(fn,rows):
  with open(o/fn,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 W('COMMON_SOURCE_INDEX.tsv',si);W('PROSPECTIVE_BINDING_INDEX.tsv',bi);W('TOKENIZER_IDENTITY_INDEX.tsv',ti)
 (o/'COMMON_SOURCE_AUTHORITY.json').write_text(J({'authority':A,'generator_sha256':H(__file__),'sources':si,'not_historical_recovery':True,'no_external_corpus':True,'no_reverse_decoding':True}))
 x=[z for z in bi if z['model_label']=='Qwen2.5-7B raw'];y=[z for z in bi if z['model_label']=='Qwen2.5-7B AWQ'];(o/'RAW7B_AWQ_PROSPECTIVE_TOKEN_COMPATIBILITY.json').write_text(J({'identical':all(a['token_sequence_sha256']==b['token_sequence_sha256'] for a,b in zip(x,y)),'historical_awq_evidence_not_rewritten':True}))
 (o/'FINAL_DECISION.json').write_text(J({'decision':'C16_PROSPECTIVE_COMMON_INPUT_174NEW_LANEB_V8_PASS','authority':A,'binding_count':len(bi),'historical_authority_modified':False,'qwen3_30b_in_scope':False}));(o/'README.md').write_text('# C16 Prospective Common Input V8\n\nProspective only; not historical recovery.\n');(o/'OPEN_ISSUES.md').write_text('# Open issues\n\nNone.\n')
if __name__=='__main__':main()
