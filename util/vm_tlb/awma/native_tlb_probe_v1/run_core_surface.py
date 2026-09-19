#!/usr/bin/env python3
import csv, pathlib, statistics, subprocess, sys

bin_path=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2]); summary=pathlib.Path(sys.argv[3]); knees=pathlib.Path(sys.argv[4])
strides=[4096,16384,65536,262144,2097152]
locations=[16,32,64,128,256,512,1024,2048,4096,8192,16384,32768]
rows=[]; skips=[]
for stride in strides:
 for n in locations:
  cmd=[str(bin_path),'--stride',str(stride),'--locations',str(n),'--samples','50','--steps','512','--warps','1','--seed',str(1000003+stride+n),'--policy','default','--warmup-batches','1']
  p=subprocess.run(cmd,text=True,capture_output=True)
  if p.returncode:
   skips.append((stride,n,p.returncode,p.stderr.strip().replace('\n',' '))); continue
  rs=list(csv.DictReader(p.stdout.splitlines(),delimiter='\t'))
  for r in rs:r['state']='CORE';rows.append(r)
cols=['state','stride_bytes','locations','bytes','warps','steps','samples','policy','warmup_batches','thrash_bytes','cycles_per_load','overhead_cycles']
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,delimiter='\t');w.writeheader();w.writerows(rows)
groups={}
for r in rows:groups.setdefault((r['stride_bytes'],r['locations']),[]).append(float(r['cycles_per_load']))
def q(x,p):
 x=sorted(x);return x[round((len(x)-1)*p)]
summary_rows=[]
for (stride,n),x in sorted(groups.items(),key=lambda z:(int(z[0][0]),int(z[0][1]))):
 summary_rows.append({'stride_bytes':stride,'locations':n,'bytes':int(stride)*int(n),'samples':len(x),'median_cycles_per_load':statistics.median(x),'p10':q(x,.1),'p90':q(x,.9),'min':min(x),'max':max(x)})
with summary.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary_rows[0]) if summary_rows else ['stride_bytes'],delimiter='\t');w.writeheader();w.writerows(summary_rows)
with knees.open('w') as f:
 f.write('# Candidate knees — reconnaissance only\n\n')
 f.write('A candidate is a >30% adjacent median change in the dependent-chain surface. It is not assigned to a TLB level.\n\n')
 for stride in strides:
  x=[r for r in summary_rows if int(r['stride_bytes'])==stride]
  for a,b in zip(x,x[1:]):
   ratio=b['median_cycles_per_load']/a['median_cycles_per_load'] if a['median_cycles_per_load'] else 0
   if ratio>=1.3 or ratio<=.77:f.write(f'- stride {stride}: {a["locations"]}→{b["locations"]}, {a["median_cycles_per_load"]:.1f}→{b["median_cycles_per_load"]:.1f} cycles/load (ratio {ratio:.2f})\n')
 f.write('\n## Safe-capacity skips\n')
 for s,n,rc,msg in skips:f.write(f'- stride={s}, locations={n}, rc={rc}: {msg}\n')
