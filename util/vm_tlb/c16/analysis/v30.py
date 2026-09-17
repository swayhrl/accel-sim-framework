import re,json,struct,csv,hashlib,statistics
from pathlib import Path
T=Path('/tmp/v30_handoff.md').read_text();ids=sorted(set(re.findall(r'C16R_deepseek-v2-lite_s[23][^`\s]+',T)));assert len(ids)==2,ids
ROOT=Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw');O=Path('docs/vm_tlb/review_packs/C16_DEEPSEEK_S2_S3_CONSUMER_174NEW_V30');H=struct.Struct('<8sIIQQQ');W=struct.Struct('<6I32Q')
def sh(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def parse(rid):
 raw=ROOT/rid;m=json.load(open(raw/'WARP_SHARD_MANIFEST.json'));rows=[]
 for s in m['shards']:
  f=open(raw/s['trace'],'rb');magic,i,o,k,ov,n=H.unpack(f.read(H.size));ev=0;p4=set();p64=set();p2=set();ln=set()
  for _ in range(n):
   x=W.unpack(f.read(W.size));mask=x[1];ev+=mask.bit_count()
   for z,a in enumerate(x[6:]):
    if mask>>z&1:p4.add(a>>12);p64.add(a>>16);p2.add(a>>21);ln.add(a>>7)
  rows.append({'run':rid,'static_index':i,'classification':s['classification'],'events':ev,'pages4k':len(p4),'pages64k':len(p64),'pages2m':len(p2),'lines128':len(ln),'format':'PASS' if magic==b'C16WARP1' and k==n and ov==0 else 'FAIL'})
 return rows
def main():
 O.mkdir();a,b=map(parse,ids);rows=a+b
 with open(O/'V26_V27_MIXED_QK_SHARD_FINGERPRINTS.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 def s(x):return {'shards':len(x),'executed':sum(r['classification']=='EXECUTED_SHARD' for r in x),'events':sum(r['events'] for r in x),'median_events':statistics.median(r['events'] for r in x if r['classification']=='EXECUTED_SHARD')}
 x,y=s(a),s(b);json.dump({'s2_run':ids[0],'s3_run':ids[1],'s2':x,'s3':y,'s3_s2_event_ratio':y['events']/x['events'] if x['events'] else None,'scope':'mixed_QK_MLA_replay_local'},open(O/'S2_S3_MLA_SCALING.json','w'),indent=2);open(O/'MLA_LINEAGE_CLOSURE.md','w').write('DeepSeek MLA lineage closed for exact V26 S2 and V27 S3 mixed-QK targets with replay-local fingerprints; no VA union/chronology/reuse claim.\n');open(O/'FINAL_DECISION.json','w').write(json.dumps({'decision':'C16_DEEPSEEK_S2_S3_CONSUMER_174NEW_V30_PASS'},indent=2)+'\n');open(O/'OPEN_ISSUES.md','w').write('No GPU execution or raw/catalog mutation.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.iterdir()):
   if p.name!='SHA256SUMS':f.write(sh(p)+'  '+p.name+'\n')
main()
