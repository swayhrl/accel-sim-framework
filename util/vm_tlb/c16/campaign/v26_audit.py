import csv,json,re,struct,hashlib
from collections import Counter
from pathlib import Path
H=struct.Struct('<8sIIQQQ');R=struct.Struct('<6I32Q');base=Path('/data/c16/deepseek_v26');root=base/'QK_formal_capture_r3';static={int(x['nvbit_static_index']):x for x in csv.DictReader((base/'QK_static.tsv').open(),delimiter='\t')};term=re.compile(r'C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)')
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
rows=[];events=0;ctas=set()
for d in sorted(root.glob('mref_*'),key=lambda x:int(x.name[5:])):
 i=int(d.name[5:]);b=(d/'trace.bin').read_bytes();magic,si,occ,cnt,over,keep=H.unpack_from(b)
 if magic!=b'C16WARP1' or si!=i or cnt!=keep or over or len(b)!=H.size+keep*R.size:raise SystemExit('container')
 z=term.findall((d/'stdout.log').read_text());
 if len(z)!=1 or tuple(map(int,z[0]))!=(i,occ,keep,over):raise SystemExit('term')
 ctx=json.loads((d/'ADDRESS_CONTEXT.json').read_text());rg=[(x['class'],int(x['address_start_hex'],16),int(x['address_start_hex'],16)+int(x['storage_bytes'])) for x in ctx['ranges']];ads=[];cs=set()
 for off in range(H.size,len(b),R.size):
  x=R.unpack_from(b,off);_,mask,cx,cy,cz,w,*vals=x;cs.add((cx,cy,cz));ctas.add((cx,cy,cz))
  for lane,a in enumerate(vals):
   if mask>>lane&1:ads.append(a)
 mem=Counter()
 for a in ads:
  q=[n for n,l,u in rg if l<=a<u];mem[q[0] if len(q)==1 else 'UNKNOWN_RUNTIME']+=1
 rows.append({'static_index':i,'records':keep,'overflow':over,'classification':'EXECUTED_SHARD' if keep else 'ZERO_EXECUTION_PROVEN','active_lane_events':len(ads),'membership':dict(mem),'unique_4k_pages':len({a>>12 for a in ads}),'unique_64k_pages':len({a>>16 for a in ads}),'unique_2m_pages':len({a>>21 for a in ads}),'unique_128b_lines':len({a>>7 for a in ads}),'trace_sha256':sha(d/'trace.bin'),'context_sha256':sha(d/'ADDRESS_CONTEXT.json')});events+=len(ads)
r={'target':'layer0.self_attn.QK_matmul','evidence_class':'MIXED_PERSISTENT_CACHE_CONSUMER','static_direct_global_mref_count':len(rows),'executed_shards':sum(x['classification']=='EXECUTED_SHARD' for x in rows),'zero_shards':sum(x['classification']!='EXECUTED_SHARD' for x in rows),'overflow_total':sum(x['overflow'] for x in rows),'active_lane_events':events,'union_cta_count':len(ctas),'union_cta_x_min':min(x[0] for x in ctas),'union_cta_x_max':max(x[0] for x in ctas),'union_cta_z_values':sorted({x[2] for x in ctas}),'full_scope_gate':'PASS' if len(rows)==20 and not sum(x['overflow'] for x in rows) and ctas else 'FAIL','shards':rows}
(base/'QK_FORMAL_AUDIT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if r['full_scope_gate']!='PASS':raise SystemExit(1)
