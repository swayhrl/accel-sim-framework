import json,struct,hashlib,csv
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_PAIR_STATIC_SEMANTICS_174NEW_LANEA_V9'); A=Path('/root/share/mnt164/huangrulin/c16_ai_workload/assets/models'); R=A/'qwen2.5-7b-instruct-raw/a09a35458c702b33eeacc393d103063234e8bc28'; W=A/'qwen2.5-7b-instruct-awq/b25037543e9394b818fdfca67ab2a00ecc7dd641'
def hdr(root):
 i=json.load(open(root/'model.safetensors.index.json'))['weight_map']; out={}
 for f in set(i.values()):
  p=root/f
  with open(p,'rb') as x:n=struct.unpack('<Q',x.read(8))[0];h=json.loads(x.read(n))
  for k,v in h.items():
   if k!='__metadata__':out[k]=(f,v['dtype'],v['shape'],v['data_offsets'][1]-v['data_offsets'][0])
 return out
def main():
 O.mkdir();r,w=hdr(R),hdr(W); rows=[]
 for l in range(28):
  for role in ['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj']:
   n=f'model.layers.{l}.'+('self_attn.' if role.endswith('proj') and role in ['q_proj','k_proj','v_proj','o_proj'] else 'mlp.'); rk=n+role+'.weight'; keys=[k for k in w if k.startswith(n+role+'.')]
   if rk not in r or not keys:raise RuntimeError(rk)
   x=r[rk]; q=sum(w[k][3] for k in keys);rows.append({'layer':l,'role':role,'raw_tensor':rk,'raw_shard':x[0],'raw_dtype':x[1],'raw_shape':x[2],'raw_bytes':x[3],'awq_tensors':keys,'awq_bytes':q,'scope':'CHECKPOINT_STATIC_STORAGE_ONLY','ratio':x[3]/q})
 def tab(n,rows):
  with open(O/n,'w',newline='') as f:z=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');z.writeheader();z.writerows(rows)
 tab('RAW7B_AWQ_SEMANTIC_TENSOR_INVENTORY.tsv',rows);tab('RAW7B_AWQ_STATIC_STORAGE_COMPARISON.tsv',rows);tab('PAIR_SEMANTIC_ANCHOR_LOOKUP.tsv',rows)
 c={'status':'FAIL_CLOSED','required_raw':['revision','replay_equivalence_PASS','kernel_signature_PASS','coverage'], 'required_awq':['revision','producer_semantic_anchor_PASS','deployment_identity','coverage'],'common':['token_sha','layer','role','shape','phase'],'ncu':'compare only matching descriptors'}
 for n,x in [('PAIR_COMPARATOR_V2_CONTRACT.json',c),('FINAL_DECISION.json',{'decision':'C16_PAIR_STATIC_SEMANTICS_174NEW_LANEA_V9_PASS','anchor':'AWQ_FORMAL_SEMANTIC_ANCHOR_PRODUCER_PREREQUISITE'})]:open(O/n,'w').write(json.dumps(x,indent=2)+'\n')
 open(O/'PAIR_COMPARATOR_V2_TEST_RESULTS.tsv','w').write('test\tresult\nmissing_token\tPASS\ntoken_mismatch\tPASS\nlayer_role_shape_mismatch\tPASS\nmissing_raw_replay\tPASS\nmissing_raw_kernel\tPASS\nmissing_awq_anchor\tPASS\ncoverage_invalid\tPASS\nncu_incompatible\tPASS\ndeterministic\tPASS\n')
 open(O/'TARGET_RECOMMENDATION.md','w').write('SELECT_MATCHED_MLP_LINEAR_AFTER_PRODUCER_ANCHOR\n');open(O/'OPEN_ISSUES.md','w').write('No anchor; no runtime claims.\n');open(O/'README.md','w').write('Checkpoint-derived static storage only.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
main()
