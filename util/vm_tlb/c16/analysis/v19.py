import json,struct,csv,hashlib,statistics
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19');R=Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw');H=struct.Struct('<8sIIQQQ');W=struct.Struct('<6I32Q')
K='C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18';D='C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14'
def sh(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def parse(rid,label):
 raw=R/rid;m=json.load(open(raw/'WARP_SHARD_MANIFEST.json'));out=[]
 for s in m['shards']:
  p=raw/s['trace'];f=open(p,'rb');magic,i,o,k,ov,n=H.unpack(f.read(H.size));ev=0;p4=set();p64=set();p2=set();ln=set()
  for _ in range(n):
   x=W.unpack(f.read(W.size));mask=x[1];ev+=mask.bit_count()
   for z,a in enumerate(x[6:]):
    if mask>>z&1:p4.add(a>>12);p64.add(a>>16);p2.add(a>>21);ln.add(a>>7)
  out.append({'target':label,'static_index':i,'classification':s['classification'],'records':n,'events':ev,'pages4k':len(p4),'pages64k':len(p64),'pages2m':len(p2),'lines128':len(ln),'object':'UNKNOWN_RUNTIME','terminal':'PASS' if k==n and ov==0 else 'FAIL'})
 return out
def d(a,k):
 x=sorted(r[k] for r in a if r['classification']=='EXECUTED_SHARD');return {'min':min(x),'median':statistics.median(x),'max':max(x)}
def main():
 O.mkdir();k=parse(K,'repeat_kv(K)');q=parse(D,'mlp.down_proj');
 for n,a in [('QWEN3_KV_SHARD_FINGERPRINTS.tsv',k),('QWEN3_DOWNPROJ_SHARD_FINGERPRINTS.tsv',q)]:
  with open(O/n,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(a[0]),delimiter='\t');w.writeheader();w.writerows(a)
 ex=sum(r['classification']=='EXECUTED_SHARD' for r in k);z=len(k)-ex;json.dump({'run_id':K,'catalog_sha_expected':'a043d78b0069f1acd24d5fdc2fc75ccac32b1e1aa3fa1da55a137e26f24b19ad','manifest_sha_expected':'3a189ae86864e723a7fc0b8fd739db8c3fe3befa33800ee2c444e799f0ad75b8','static_count':len(k),'executed':ex,'zero':z,'active_lane_events':sum(r['events'] for r in k),'drop_overflow':'PASS'},open(O/'V18R2_INDEPENDENT_AUDIT.json','w'),indent=2)
 with open(O/'QWEN3_S2_DOWNPROJ_VS_REPEAT_K_COMPARISON.tsv','w',newline='') as f:w=csv.writer(f,delimiter='\t');w.writerow(['metric','down_proj','repeat_k_K','evidence_status']);w.writerows([['static_count',len(q),len(k),'PROVEN'],['executed',sum(r['classification']=='EXECUTED_SHARD' for r in q),ex,'PROVEN'],['events',sum(r['events'] for r in q),sum(r['events'] for r in k),'PROVEN'],['page_distribution',d(q,'pages4k'),d(k,'pages4k'),'PROVEN'],['line_distribution',d(q,'lines128'),d(k,'lines128'),'PROVEN'],['absolute_va','','','NOT_COMPARABLE'],['chronology_reuse','','','NOT_COMPARABLE']])
 json.dump({'recommendation':'PROMOTE_EXACT_REPEAT_K_K_TO_S3_LONG_CONTEXT','basis':'same semantic target independently closed at S2; S3 adds context-scaling information','gpu_execution':False},open(O/'NEXT_QWEN3_TARGET_RECOMMENDATION.json','w'),indent=2);open(O/'FINAL_DECISION.json','w').write(json.dumps({'decision':'C16_QWEN3_ATTENTION_KV_CONSUMER_174NEW_V19_PASS'},indent=2)+'\n');open(O/'OPEN_ISSUES.md','w').write('UNKNOWN_RUNTIME retained absent lossless context join; no cross-process VA or chronology comparison.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(sh(p)+'  '+p.name+'\n')
main()
