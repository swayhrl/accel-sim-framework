#!/usr/bin/env python3
import csv,pathlib,statistics,sys
root=pathlib.Path(sys.argv[1]); core=root/'raw/NATIVE_TLB_RECON_RAW_CORE.tsv'; follow=root/'raw/NATIVE_TLB_RECON_FOLLOWUPS.tsv'
rows=[]
for p in [core,follow]:
 with p.open() as f: rows += list(csv.DictReader(f,delimiter='\t'))
def q(x,p): x=sorted(x);return x[round((len(x)-1)*p)]
groups={}
for r in rows:
 k=(r.get('state','CORE'),r['stride_bytes'],r['locations'],r['warps'],r['policy'],r.get('replicate','0'));groups.setdefault(k,[]).append(float(r['cycles_per_load']))
o=[]
for k,x in sorted(groups.items()):o.append(dict(state=k[0],stride_bytes=k[1],locations=k[2],warps=k[3],policy=k[4],replicate=k[5],samples=len(x),median=statistics.median(x),p10=q(x,.1),p90=q(x,.9),minimum=min(x),maximum=max(x)))
with (root/'NATIVE_TLB_RECON_SUMMARY.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(o[0]),delimiter='\t');w.writeheader();w.writerows(o)
rep=[]
for s,n in [(4096,512),(4096,1024),(4096,2048),(16384,1024),(65536,512),(65536,1024),(262144,1024),(2097152,1024)]:
 vals=[r['median'] for r in o if r['state']=='CROSS_PROCESS_REPEAT' and r['stride_bytes']==str(s) and r['locations']==str(n)]
 if vals: rep.append(dict(stride_bytes=s,locations=n,processes=len(vals),median=statistics.median(vals),minimum=min(vals),maximum=max(vals),cv=(statistics.pstdev(vals)/statistics.mean(vals) if statistics.mean(vals) else 0)))
with (root/'NATIVE_TLB_RECON_REPEATABILITY.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rep[0]) if rep else ['stride_bytes'],delimiter='\t');w.writeheader();w.writerows(rep)
(root/'NATIVE_TLB_RECON_LIMITATIONS.md').write_text('''# Limitations\n\nThis is dependent global-memory timing on an RTX4080, with a register-only timing control. Address spacing is an experiment parameter, not a claimed hardware page size. `cg` is an explicit PTX cache-global load policy variant; it does not isolate TLB latency. The intervening chain is a recorded randomized address-space disturbance, not a TLB flush. No simulator constants are modified.\n''')
