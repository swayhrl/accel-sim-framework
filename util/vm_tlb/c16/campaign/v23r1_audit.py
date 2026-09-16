import csv,json,re,struct,hashlib,os
from collections import Counter
from pathlib import Path
H=struct.Struct('<8sIIQQQ');R=struct.Struct('<6I32Q');target=os.environ['C16_V23R1_TARGET'];base=Path('/data/c16/deepseek_v23r1');root=base/f'{target}_formal_capture';static={int(x['nvbit_static_index']):x for x in csv.DictReader((base/f'{target}_static.tsv').open(),delimiter='\t')};term=re.compile(r'C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)')
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
rows=[];ctas=set();events=0
for d in sorted(root.glob('mref_*'),key=lambda p:int(p.name[5:])):
 i=int(d.name[5:]);b=(d/'trace.bin').read_bytes();magic,si,occ,count,overflow,keep=H.unpack_from(b)
 if magic!=b'C16WARP1' or si!=i or count!=keep or overflow or len(b)!=H.size+keep*R.size:raise SystemExit('container '+str(i))
 z=term.findall((d/'stdout.log').read_text());
 if len(z)!=1 or tuple(map(int,z[0]))!=(i,occ,keep,overflow):raise SystemExit('terminal '+str(i))
 ctx=json.loads((d/'ADDRESS_CONTEXT.json').read_text());ranges=[(x['class'],int(x['address_start_hex'],16),int(x['address_start_hex'],16)+int(x['storage_bytes'])) for x in ctx['ranges']];ads=[];cs=set();warps=set()
 for off in range(H.size,len(b),R.size):
  x=R.unpack_from(b,off);_,mask,cx,cy,cz,w,*vals=x;cs.add((cx,cy,cz));ctas.add((cx,cy,cz));warps.add(w)
  for lane,a in enumerate(vals):
   if mask>>lane&1:ads.append(a)
 membership=Counter()
 for a in ads:
  m=[name for name,lo,hi in ranges if lo<=a<hi];membership[m[0] if len(m)==1 else 'UNKNOWN_RUNTIME']+=1
 rows.append({'static_index':i,'is_load':static[i]['is_load']=='1','is_store':static[i]['is_store']=='1','records':keep,'overflow':overflow,'classification':'EXECUTED_SHARD' if keep else 'ZERO_EXECUTION_PROVEN','active_lane_events':len(ads),'cta_count':len(cs),'cta_x_min':min((x[0] for x in cs),default=None),'cta_x_max':max((x[0] for x in cs),default=None),'cta_y_min':min((x[1] for x in cs),default=None),'cta_y_max':max((x[1] for x in cs),default=None),'warps':sorted(warps),'membership':dict(membership),'unique_4k_pages':len({a>>12 for a in ads}),'unique_64k_pages':len({a>>16 for a in ads}),'unique_2m_pages':len({a>>21 for a in ads}),'unique_128b_lines':len({a>>7 for a in ads}),'trace_sha256':sha(d/'trace.bin'),'context_sha256':sha(d/'ADDRESS_CONTEXT.json')});events+=len(ads)
all_ok=len(rows)==len([x for x in static.values() if x['memory_space']=='GLOBAL' and x['has_mref']=='1']) and all(x['overflow']==0 for x in rows) and bool(ctas);r={'schema_version':1,'target':target,'static_direct_global_mref_count':len(rows),'executed_shards':sum(x['classification']=='EXECUTED_SHARD' for x in rows),'zero_shards':sum(x['classification']!='EXECUTED_SHARD' for x in rows),'overflow_total':sum(x['overflow'] for x in rows),'active_lane_events':events,'union_cta_count':len(ctas),'union_cta_x_min':min(x[0] for x in ctas),'union_cta_x_max':max(x[0] for x in ctas),'full_scope_gate':'PASS' if all_ok else 'FAIL','shards':rows}
(base/f'{target}_FORMAL_AUDIT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if not all_ok:raise SystemExit(1)
