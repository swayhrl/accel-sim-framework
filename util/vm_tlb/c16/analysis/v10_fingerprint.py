import json,struct,csv
from pathlib import Path
O=Path('docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11');R=Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw'); H=struct.Struct('<8sIIQQQ'); Q=struct.Struct('<6I32Q')
ids=['C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj_20260916T001000Z_aa10aa10aa10','C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10']
rows=[]
for rid in ids:
 m=json.load(open(R/rid/'WARP_SHARD_MANIFEST.json'))
 for s in m['shards']:
  p=R/rid/s['trace']; f=open(p,'rb'); magic,i,o,c,over,n=H.unpack(f.read(H.size));ev=0;va=set();p4=set();p64=set();p2=set();ln=set()
  for z in range(n):
   x=Q.unpack(f.read(Q.size)); mask=x[1]
   for a,v in enumerate(x[6:]):
    if mask>>a&1:ev+=1;va.add(v);p4.add(v>>12);p64.add(v>>16);p2.add(v>>21);ln.add(v>>7)
  rows.append({'run':rid,'static_index':s['static_index'],'classification':s['classification'],'active_lane_events':ev,'unique_va':len(va),'pages4k':len(p4),'pages64k':len(p64),'pages2m':len(p2),'lines128':len(ln),'object':'UNKNOWN_RUNTIME'})
with open(O/'V10_FORMAL_MEMORY_FINGERPRINT.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
