#!/usr/bin/env python3
import csv, pathlib, subprocess, sys
bin_path=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2])
points=[(4096,512),(4096,1024),(4096,2048),(16384,1024),(65536,512),(65536,1024),(262144,1024),(2097152,1024)]
rows=[];skips=[]
def run(state,stride,n,warps=1,policy='default',thrash=False,replicate=0):
 cmd=[str(bin_path),'--stride',str(stride),'--locations',str(n),'--samples','50','--steps','512','--warps',str(warps),'--seed',str(700000+stride+n+warps+replicate),'--policy',policy,'--warmup-batches','2']
 if thrash:cmd += ['--thrash-stride','4096','--thrash-locations','16384']
 p=subprocess.run(cmd,text=True,capture_output=True)
 if p.returncode:skips.append((state,stride,n,warps,policy,p.returncode,p.stderr.strip().replace('\n',' ')));return
 for r in csv.DictReader(p.stdout.splitlines(),delimiter='\t'):
  r.update(state=state,replicate=str(replicate));rows.append(r)
for s,n in points:
 run('WARM_REPEAT',s,n)
 run('INTERVENING_THRASH',s,n,thrash=True)
 run('CACHE_GLOBAL_VARIANT',s,n,policy='cg')
for s,n in [(4096,1024),(65536,1024),(262144,1024),(2097152,1024)]:
 for w in [1,2,4,8,16]:run('CONCURRENCY_SURFACE',s,n,warps=w)
for s,n in points:
 for rep in [1,2,3]:run('CROSS_PROCESS_REPEAT',s,n,replicate=rep)
cols=['state','replicate','stride_bytes','locations','bytes','warps','steps','samples','policy','warmup_batches','thrash_bytes','cycles_per_load','overhead_cycles']
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,delimiter='\t');w.writeheader();w.writerows(rows)
with (out.parent/'NATIVE_TLB_RECON_FOLLOWUP_SKIPS.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['state','stride','locations','warps','policy','returncode','detail']);w.writerows(skips)
