#!/usr/bin/env python3
"""CPU-only exact R27R2 varied token-bank construction."""
import argparse,csv,hashlib,json,sys
from pathlib import Path
import torch,transformers
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(memoryview(t.contiguous().view(torch.uint8).numpy())).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parquet',required=True);ap.add_argument('--model',required=True);ap.add_argument('--out',required=True);ap.add_argument('--pyarrow-site',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 # Preserve the accepted torch/transformers imports; append only the existing CPU pyarrow environment.
 sys.path.append(a.pyarrow_site);import pyarrow,pyarrow.parquet as pq
 p=Path(a.parquet)
 if p.stat().st_size!=6357543 or sha(p)!='e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7':raise SystemExit('parquet identity mismatch')
 table=pq.read_table(p,columns=['text']);values=table.column('text').to_pylist()
 if any(x is None or not isinstance(x,str) for x in values):raise SystemExit('non-string/null text row')
 joined='\n'.join(values);joined_bytes=joined.encode('utf-8');text_sha=hashlib.sha256(joined_bytes).hexdigest()
 tok=transformers.AutoTokenizer.from_pretrained(a.model,local_files_only=True,use_fast=True)
 encoded=tok(joined,add_special_tokens=False,return_attention_mask=False,return_token_type_ids=False)
 ids=encoded['input_ids'];required=33*128*128
 if len(ids)<required:raise SystemExit(f'insufficient tokens {len(ids)}')
 bank=torch.tensor(ids[:required],dtype=torch.int64).reshape(33,128,128).contiguous()
 bank_sha=tsha(bank);raw=out/'TOKEN_BANK_INT64.bin';raw.write_bytes(memoryview(bank.view(torch.uint8).numpy()))
 torch.save({'schema':'R27R2_TOKEN_BANK_V1','bank':bank,'bank_sha256':bank_sha,'source_parquet_sha256':sha(p),'joined_text_sha256':text_sha},out/'TOKEN_BANK.pt')
 windows=[];seen=set()
 for step in range(33):
  for row in range(128):
   w=bank[step,row];h=tsha(w);windows.append({'step':step,'row':row,'window_sha256':h,'first_token':int(w[0]),'last_token':int(w[-1])});seen.add(h)
 if len(seen)!=4224:raise SystemExit(f'duplicate windows unique={len(seen)}')
 with (out/'WINDOW_BINDINGS.tsv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(windows[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(windows)
 steps=[]
 for step in range(33):steps.append({'step':step,'step_tensor_sha256':tsha(bank[step]),'input_B128_sha256':tsha(bank[step,:,:127].contiguous()),'labels_B128_sha256':tsha(bank[step,:,1:].contiguous()),'next_loss_only':step==32})
 with (out/'STEP_BINDINGS.tsv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(steps[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(steps)
 model=Path(a.model);payload={n:sha(model/n) for n in ('tokenizer.json','tokenizer_config.json','special_tokens_map.json')}
 authority={'schema':'R27R2_TOKEN_BANK_AUTHORITY_V1','status':'R27R2_TOKEN_BANK_QUALIFIED','parquet':{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'rows':len(values)},'text':{'join':'single LF between every physical-order row, retaining empty rows','utf8_bytes':len(joined_bytes),'sha256':text_sha,'null_rows':0},'tokenizer':{'model_path':a.model,'class':tok.__class__.__name__,'transformers_version':transformers.__version__,'pyarrow_version':pyarrow.__version__,'add_special_tokens':False,'payload_sha256':payload},'tokens':{'total_count':len(ids),'selected_offset':0,'selected_count':required},'bank':{'shape':[33,128,128],'dtype':'torch.int64','bytes':bank.numel()*bank.element_size(),'sha256':bank_sha,'raw_path':str(raw),'raw_sha256':sha(raw),'pt_path':str(out/'TOKEN_BANK.pt'),'pt_sha256':sha(out/'TOKEN_BANK.pt'),'unique_windows':len(seen),'window_count':4224},'semantics':{'step_indices':'0..32','input':'bank[k,0:B,0:127]','labels':'bank[k,0:B,1:128]','next_loss_step':32,'GPU_full_bank_mirror':False}}
 (out/'BANK_AUTHORITY.json').write_text(json.dumps(authority,indent=2,sort_keys=True)+'\n')
 print(json.dumps(authority,indent=2,sort_keys=True))
if __name__=='__main__':main()
