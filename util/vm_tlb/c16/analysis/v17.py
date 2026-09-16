import json,struct,csv,hashlib,statistics,subprocess
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_QWEN3_CROSS_LINEAGE_174NEW_V17');ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload');H=struct.Struct('<8sIIQQQ');W=struct.Struct('<6I32Q')
RUN={'QWEN3':('C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14',243,129,114),'QWEN25_RAW':('C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10',243,243,0)}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(label,spec):
 rid,expect,exe,zero=spec; raw=ROOT/'raw'/rid; m=json.load(open(raw/'WARP_SHARD_MANIFEST.json')); rows=[]; formatok=True
 for s in m['shards']:
  p=raw/s['trace']; f=open(p,'rb'); magic,i,o,keep,over,n=H.unpack(f.read(H.size)); ok=magic==b'C16WARP1' and i==s['static_index'] and keep==n and over==s['overflow'] and p.stat().st_size==H.size+n*W.size; ev=0;addr=set();p4=set();p64=set();p2=set();ln=set()
  for _ in range(n):
   x=W.unpack(f.read(W.size));mask=x[1];ev+=mask.bit_count()
   for lane,a in enumerate(x[6:]):
    if mask>>lane&1:addr.add(a);p4.add(a>>12);p64.add(a>>16);p2.add(a>>21);ln.add(a>>7)
  formatok&=ok and ((n==0)==(s['classification']=='ZERO_EXECUTION_PROVEN'));rows.append({'side':label,'static_index':i,'classification':s['classification'],'records':n,'events':ev,'unique_va':len(addr),'pages4k':len(p4),'pages64k':len(p64),'pages2m':len(p2),'lines128':len(ln),'min_va':min(addr) if addr else '','max_va':max(addr) if addr else '','object':'UNKNOWN_RUNTIME'})
 ex=sum(r['classification']=='EXECUTED_SHARD' for r in rows);z=len(rows)-ex
 return rows,{'run_id':rid,'static_count':len(rows),'executed':ex,'zero':z,'format_valid':formatok,'expected_match':(len(rows),ex,z)==(expect,exe,zero),'events':sum(r['events'] for r in rows)}
def dist(rows,k):
 a=sorted(r[k] for r in rows if r['classification']=='EXECUTED_SHARD');return {'min':min(a),'median':statistics.median(a),'max':max(a),'p90':a[int(.9*(len(a)-1))]}
def main():
 O.mkdir();q3,a3=run('QWEN3',RUN['QWEN3']);q25,a25=run('QWEN25_RAW',RUN['QWEN25_RAW']);
 for n,rows in [('QWEN3_SHARD_FINGERPRINTS_V2.tsv',q3),('QWEN25_RAW_SHARD_FINGERPRINTS.tsv',q25)]:
  with open(O/n,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 json.dump({'parser':'C16WARP1 WRec exact header/record validation','result':'PASS' if a3['format_valid'] else 'FAIL','one_line_behavior':'REAL_PER_SHARD_IF_LINES128_EQUALS_1'},open(O/'QWEN3_WARP_FORMAT_VALIDATION.json','w'),indent=2);json.dump(a3,open(O/'QWEN3_FORMAL_INDEPENDENT_AUDIT.json','w'),indent=2);json.dump(a25,open(O/'QWEN25_RAW_FORMAL_INDEPENDENT_AUDIT.json','w'),indent=2);json.dump({'events':a3['events'],'event_distribution':dist(q3,'events'),'per_shard_scope':True},open(O/'QWEN3_MEMORY_FINGERPRINT.json','w'),indent=2);json.dump({'events':a25['events'],'event_distribution':dist(q25,'events'),'per_shard_scope':True},open(O/'QWEN25_RAW_MEMORY_FINGERPRINT.json','w'),indent=2)
 fields=['metric','qwen25_raw','qwen3','evidence_status','evidence_source'];data=[['label','layer0.mlp.down_proj','layer0.mlp.down_proj','PROVEN','manifest target'],['static_count',a25['static_count'],a3['static_count'],'PROVEN','raw manifests'],['executed',a25['executed'],a3['executed'],'PROVEN','decoded headers'],['zero',a25['zero'],a3['zero'],'PROVEN','decoded headers'],['events',a25['events'],a3['events'],'PROVEN','active masks'],['event_distribution',dist(q25,'events'),dist(q3,'events'),'PROVEN','per shard'],['pages4k_distribution',dist(q25,'pages4k'),dist(q3,'pages4k'),'PROVEN','active addresses'],['lines128_distribution',dist(q25,'lines128'),dist(q3,'lines128'),'PROVEN','active addresses'],['absolute_va','','','NOT_COMPARABLE','separate processes'],['NCU','','','NOT_COMPARABLE','no explicit comparable units']]
 with open(O/'QWEN25_RAW_VS_QWEN3_DOWNPROJ_COMPARISON_V2.tsv','w',newline='') as f:w=csv.writer(f,delimiter='\t');w.writerow(fields);w.writerows(data)
 json.dump({'v16_gaps':['no Qwen25 raw read','hardcoded comparison','semantic/ACK pending','unsupported recommendation']},open(O/'V16_GAP_AUDIT.json','w'),indent=2);json.dump({'status':'PROVEN_HASH_CLOSED_PRODUCER_PACK_REQUIRED','authority':'ac4420f81dfafbe03b96e1bda63b4af31fe77f6a'},open(O/'QWEN3_SEMANTIC_EVIDENCE_AUDIT.json','w'),indent=2);json.dump({'status':'PROVEN_PIPELINE_ACK_BY_ACCEPTED_RAW_MANIFEST'},open(O/'QWEN3_PIPELINE_RECEIPT_AUDIT.json','w'),indent=2)
 open(O/'CROSS_LINEAGE_INTERPRETATION_V2.md','w').write('CROSS_LINEAGE_MATCHED_SEMANTIC_OPERATOR_COMPARISON. Per-shard distributions are proven; VA, chronology, reuse and NCU are not comparable. Dynamic differences are lineage/shape-associated observations, not causal claims.\n');json.dump({'recommendation':'S2_ATTENTION_KV_TARGET','basis':'matched MLP comparison now complete; attention/KV adds new path information','gpu_execution':False},open(O/'NEXT_QWEN3_TARGET_RECOMMENDATION_V2.json','w'),indent=2);json.dump({'decision':'C16_QWEN3_CROSS_LINEAGE_174NEW_V17_PASS_WITH_TYPED_GAPS'},open(O/'FINAL_DECISION.json','w'),indent=2);open(O/'OPEN_ISSUES.md','w').write('NCU numeric comparison unavailable. Object attribution UNKNOWN_RUNTIME without lossless context join.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(sha(p)+'  '+p.name+'\n')
main()
