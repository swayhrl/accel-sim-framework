#!/usr/bin/env python3
import argparse,csv,json,sqlite3
from collections import defaultdict
from pathlib import Path
def fam(n):
 s=n.lower()
 if 'flash' in s or 'attention' in s:return 'ATTENTION_LIKE'
 if 'gemm' in s:return 'GEMM'
 if 'gemv' in s:return 'GEMV'
 if 'moe' in s or 'expert' in s or 'topk' in s or 'routing' in s:return 'MOE_DISPATCH_EXPERT'
 if 'reduce' in s:return 'REDUCTION'
 if 'copy' in s:return 'COPY'
 return 'OTHER'
def main():
 p=argparse.ArgumentParser();p.add_argument('--sqlite',type=Path,required=True);p.add_argument('--scenario',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(f'file:{a.sqlite}?mode=ro',uri=True); strings=dict(db.execute('select id,value from StringIds')); ranges=[]
 for st,en,text,tid in db.execute("select start,end,text,globalTid from NVTX_EVENTS where text like 'ATLAS_PHASE=%' order by start"):
  d=dict(x.split('=',1) for x in text.split(';'));ranges.append((st,en,tid,d['ATLAS_PHASE'],d.get('STEP','')))
 rt=defaultdict(list)
 for st,en,c,tid,nid in db.execute('select start,end,correlationId,globalTid,nameId from CUPTI_ACTIVITY_KIND_RUNTIME where correlationId is not null'):rt[c].append((st,en,tid))
 rows=[]
 q='select start,end,correlationId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start,end'
 for i,x in enumerate(db.execute(q)):
  st,en,c,gx,gy,gz,bx,by,bz,dn,sn,mn=x; phase='AUXILIARY';step='';method='OUTSIDE_ATLAS_RANGE'; rr=rt.get(c,[])
  if len(rr)==1:
   z=[r for r in ranges if r[2]==rr[0][2] and r[0]<=rr[0][0]<=r[1]]
   if len(z)==1:phase,step,method=z[0][3],z[0][4],'CUPTI_RUNTIME_TO_SAME_THREAD_NVTX'
  name=strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN';rows.append({'scenario':a.scenario,'global_index':i,'phase':phase,'decode_step':step,'function':name,'family':fam(name),'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}','duration_ns':en-st,'assignment':method})
 db.close(); fields=list(rows[0]);
 with (a.out/'ALL_LAUNCHES.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
 groups=defaultdict(lambda:[0,0])
 for r in rows:
  if r['phase'] in ('PREFILL','DECODE'):groups[(r['phase'],r['family'],r['function'],r['grid'],r['block'])][0]+=1;groups[(r['phase'],r['family'],r['function'],r['grid'],r['block'])][1]+=int(r['duration_ns'])
 total=sum(v[1] for v in groups.values()); out=[]
 for k,v in sorted(groups.items(),key=lambda x:-x[1][1]):out.append({'scenario':a.scenario,'phase':k[0],'family':k[1],'function':k[2],'grid':k[3],'block':k[4],'launch_count':v[0],'gpu_duration_ns':v[1],'gpu_time_share':v[1]/total})
 with (a.out/'NATIVE_CENSUS.tsv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
 print(json.dumps({'scenario':a.scenario,'ranges':len(ranges),'launches':len(rows),'attributed':sum(r['phase'] in ('PREFILL','DECODE') for r in rows),'gpu_duration_ns':total},sort_keys=True))
if __name__=='__main__':main()
