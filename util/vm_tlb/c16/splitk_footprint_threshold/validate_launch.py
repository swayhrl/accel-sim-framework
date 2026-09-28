#!/usr/bin/env python3
import argparse,json,sqlite3
from pathlib import Path
from contracts import expected_rows
def main():
 p=argparse.ArgumentParser();p.add_argument('--sqlite',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();db=sqlite3.connect(a.sqlite);exp={(r['point'],r['arm']):r for r in expected_rows()}
 ranges=list(db.execute("select start,end,coalesce(text,(select value from StringIds where id=textId)) from NVTX_EVENTS where coalesce(text,(select value from StringIds where id=textId)) like 'C16_SPLITK_THRESHOLD_AUDIT_%' order by start"));kernels=list(db.execute("select k.start,k.end,s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,k.registersPerThread,k.staticSharedMemory,k.dynamicSharedMemory from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName order by k.start"));rows=[]
 for start,end,label in ranges:
  point,arm=label.removeprefix('C16_SPLITK_THRESHOLD_AUDIT_').rsplit('_',1);selected=[k for k in kernels if k[0]>=start and k[1]<=end];contract=exp[(point,arm)];want=[('GEMM',contract['gemm_grid'],(32,2,1))]+([('REDUCTION',contract['reduction_grid'],(32,4,1))] if arm=='A' else [])
  if len(selected)!=len(want):raise RuntimeError(f'launch count {point}/{arm}')
  for order,(k,w) in enumerate(zip(selected,want)):
   kind='GEMM' if 'gemm_forward' in k[2] else 'REDUCTION' if 'reduce_kernel' in k[2] else 'OTHER';passed=kind==w[0] and k[3]==w[1] and (k[6],k[7],k[8])==w[2];row={'point':point,'arm':arm,'order':order,'kernel_kind':kind,'kernel_name':k[2],'grid':[k[3],k[4],k[5]],'block':[k[6],k[7],k[8]],'registers_per_thread':k[9],'static_shared_bytes':k[10],'dynamic_shared_bytes':k[11],'scratch_shape':contract['scratch_shape'],'scratch_bytes':contract['scratch_bytes'],'reduction_expected':contract['reduction_expected'],'pass':passed};rows.append(row)
   if not passed:raise RuntimeError(row)
 if len(ranges)!=8 or len(rows)!=12:raise RuntimeError(f'coverage {len(ranges)}/{len(rows)}')
 a.output.write_text(json.dumps({'status':'PASS','range_count':len(ranges),'rows':rows},indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS_LAUNCH_AUDIT','ranges':len(ranges),'kernels':len(rows)}))
if __name__=='__main__':main()
