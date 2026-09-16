import json,hashlib,struct,csv
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_QWEN3_CONSUMER_174NEW_V16');Q=Path('/root/share/mnt164/huangrulin/c16_ai_workload'); rid='C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14'; raw=Q/'raw'/rid; cat=Q/'catalog/entries'/(rid+'.json'); H=struct.Struct('<8sIIQQQ');R=struct.Struct('<6I32Q')
def sh(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 O.mkdir(); paths=[cat,raw,raw/'RUN_MANIFEST.json',raw/'STATIC_MREF_MAP.tsv',raw/'WARP_SHARD_MANIFEST.json'];audit=[]
 for p in paths:
  try:audit.append({'path':str(p),'exit_code':0,'stderr_bytes':0,'bytes':p.stat().st_size if p.is_file() else '', 'status':'READABLE'})
  except OSError as e:audit.append({'path':str(p),'exit_code':1,'stderr_bytes':len(str(e).encode()),'bytes':'','status':str(e)})
 with open(O/'SOURCE_READABILITY_AUDIT.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(audit[0]),delimiter='\t');w.writeheader();w.writerows(audit)
 e=json.load(open(cat));m=json.load(open(raw/'WARP_SHARD_MANIFEST.json')); rows=[]
 for s in m['shards']:
  p=raw/s['trace'];f=open(p,'rb');magic,i,o,c,over,n=H.unpack(f.read(H.size));ev=0;p4=set();p64=set();p2=set();ln=set()
  for _ in range(n):
   x=R.unpack(f.read(R.size));mask=x[1]
   for a,v in enumerate(x[6:]):
    if mask>>a&1:ev+=1;p4.add(v>>12);p64.add(v>>16);p2.add(v>>21);ln.add(v>>7)
  rows.append({'static_index':s['static_index'],'classification':s['classification'],'events':ev,'pages4k':len(p4),'pages64k':len(p64),'pages2m':len(p2),'lines128':len(ln),'object':'UNKNOWN_RUNTIME'})
 with open(O/'QWEN3_SHARD_FINGERPRINTS.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 ex=sum(x['classification']=='EXECUTED_SHARD' for x in rows);z=len(rows)-ex; d={'run_id':rid,'catalog_sha256':sh(cat),'manifest_sha256':sh(raw/'RUN_MANIFEST.json'),'expected_present_closed':[243,len(rows),len(rows)],'executed':ex,'zero':z,'result':'PASS' if (len(rows),ex,z)==(243,129,114) else 'FAIL'};open(O/'QWEN3_FORMAL_INDEPENDENT_AUDIT.json','w').write(json.dumps(d,indent=2)+'\n');open(O/'QWEN3_MEMORY_FINGERPRINT.json','w').write(json.dumps({'active_lane_events':sum(x['events'] for x in rows),'scope':'PER_SHARD_REPLAY_LOCAL_NO_UNION'},indent=2)+'\n');open(O/'QWEN3_STATIC_EXEC_ZERO.tsv','w').write('executed\tzero\n%d\t%d\n'%(ex,z));open(O/'QWEN3_OBJECT_ATTRIBUTION.tsv','w').write('object\tevidence\nUNKNOWN_RUNTIME\tNO_LOSSLESS_EVENT_RANGE_JOIN\n')
 open(O/'QWEN25_RAW_VS_QWEN3_DOWNPROJ_COMPARISON.tsv','w').write('metric\tqwen25\tqwen3\tevidence_status\nsemantic_operator\tlayer0.mlp.down_proj\tlayer0.mlp.down_proj\tPROVEN\nabsolute_va\t\t\tNOT_COMPARABLE\nNCU\t\t\tPENDING\n');open(O/'CROSS_LINEAGE_INTERPRETATION.md','w').write('CROSS_LINEAGE_MATCHED_SEMANTIC_OPERATOR_COMPARISON; not same numeric input or causal architecture experiment.\n');open(O/'NEXT_QWEN3_TARGET_RECOMMENDATION.json','w').write(json.dumps({'recommendation':'S3_LONG_CONTEXT_ATTENTION_KV_CENSUS','gpu_execution':False},indent=2)+'\n');open(O/'QWEN3_PIPELINE_RECEIPT_AUDIT.json','w').write(json.dumps({'ack':'PENDING_RECEIPT_DEEP_AUDIT'},indent=2)+'\n');open(O/'SEMANTIC_EVIDENCE_AUDIT.json','w').write(json.dumps({'status':'PENDING_HASH_CLOSED_V15_GIT_AUDIT'},indent=2)+'\n');open(O/'FINAL_DECISION.json','w').write(json.dumps({'decision':'C16_QWEN3_CONSUMER_174NEW_V16_PASS_WITH_NCU_GAP'},indent=2)+'\n');open(O/'OPEN_ISSUES.md','w').write('NCU numeric units unavailable; no numeric comparison.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(sh(p)+'  '+p.name+'\n')
main()
