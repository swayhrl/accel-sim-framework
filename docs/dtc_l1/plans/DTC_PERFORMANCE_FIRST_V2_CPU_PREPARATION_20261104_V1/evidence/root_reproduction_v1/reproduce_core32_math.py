"""CPU-only numeric reproduction from frozen integer-cycle rows; no model actions."""
import argparse,csv,json,math,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--native-source-pins');p.add_argument('--output',required=True);a=p.parse_args()
rows=list(csv.DictReader(Path(a.csv).open(newline='')));assert len(rows)==64
seen=set();groups={};identities={}
for r in rows:
 key=(r['input_digest'],r['profile']);assert key not in seen;seen.add(key)
 identities.setdefault(r['profile'],set()).add(r['input_digest'])
 c0,d0,c,d=map(int,(r['CH_P0'],r['DH_P0'],r['CH_F'],r['DH_F']));assert min(c0,d0,c,d)>0
 v=dict(S_CH=c0/c,S_DH=d0/d,R_P0=c0/d0,R=c/d,I=(d0/d)/(c0/c))
 for k,x in v.items():assert math.isclose(x,float(r[k]),rel_tol=1e-12);groups.setdefault(r['profile'],{}).setdefault(k,[]).append(x)
assert set(identities)=={'F128','F256'}and identities['F128']==identities['F256']and len(identities['F128'])==32
stats={F:{k:dict(n=len(x),GM=math.exp(math.fsum(math.log(t)for t in x)/len(x)),positive=sum(t>1 for t in x),zero=sum(t==1 for t in x),negative=sum(t<1 for t in x))for k,x in z.items()}for F,z in groups.items()}
checked=0
if a.native_source_pins:
 pins=json.loads(Path(a.native_source_pins).read_bytes());assert len(pins)==192
 for r in pins:
  b=Path(r['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'];v=json.loads(b);assert int(v['cycles'])==r['cycles'];checked+=1
out=dict(kind='CPU_ONLY_FIXED_CORE32_MATH_REPRODUCTION',source_csv_sha256=hashlib.sha256(Path(a.csv).read_bytes()).hexdigest(),programs=32,rows=64,source_RESULT_SHA_and_cycles_verified=checked,summary=stats,new_models=0,new_scientific_requests=0)
dest=Path(a.output);assert not dest.exists(),'Use a new output file; never overwrite evidence'
with dest.open('x')as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(out))
