#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,sqlite3,statistics
from pathlib import Path
def fields(text):return dict(x.split('=',1) for x in text.split(';') if '=' in x)
def main():
 p=argparse.ArgumentParser();p.add_argument('--sqlite',type=Path,required=True);p.add_argument('--arm',required=True);p.add_argument('--arrival',type=float,required=True);p.add_argument('--b0-ms',type=float,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();db=sqlite3.connect(f'file:{a.sqlite}?mode=ro',uri=True);strings=dict(db.execute('select id,value from StringIds'));bg=[];fg=[]
 for st,en,text,tid in db.execute("select start,end,text,globalTid from NVTX_EVENTS where text like 'R51_%SUBMIT;%' order by start"):
  z=fields(text)
  if z.get('KIND')!='FORMAL':continue
  item={'start':st,'end':en,'text':text,'tid':tid,'rep':int(z['REP'])}
  (bg if text.startswith('R51_BG_SUBMIT') else fg).append(item)
 if len(bg)!=7 or len(fg)!=7:raise RuntimeError(f'range count bg={len(bg)} fg={len(fg)}')
 kernels=[]
 for x in db.execute('select start,end,correlationId,streamId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start'):
  st,en,c,sid,gx,gy,gz,bx,by,bz,dn,sn,mn=x;kernels.append({'start':st,'end':en,'corr':c,'stream':sid,'grid':f'{gx},{gy},{gz}','block':f'{bx},{by},{bz}','name':strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN'})
 rows=[];b0ns=a.b0_ms*1e6
 for i,b in enumerate(sorted(bg,key=lambda x:x['rep'])):
  f=next(x for x in fg if x['rep']==b['rep']);next_start=sorted(bg,key=lambda x:x['rep'])[i+1]['start'] if i+1<len(bg) else 2**63-1;window=[k for k in kernels if b['start']<=k['start']<next_start];fgks=[k for k in window if 'pytorch_flash::flash_fwd' in k['name']];bgks=[k for k in window if ('gemvx::kernel' in k['name'] or 'gemv2T_kernel' in k['name'] or 'CatArrayBatchedCopy' in k['name'])]
  if not fgks or not bgks:raise RuntimeError(f'rep{b["rep"]} kernels bg={len(bgks)} fg={len(fgks)}')
  bgstart=min(k['start'] for k in bgks);bgend=max(k['end'] for k in bgks);fgstart=min(k['start'] for k in fgks);fgend=max(k['end'] for k in fgks);ready=f['start'];submit=f['end'];actual=(ready-bgstart)/b0ns;valid=(a.arrival-.10)<=actual<=(a.arrival+.10) and bgstart<=ready<bgend
  overlap=any(max(k['start'],q['start'])<min(k['end'],q['end']) for k in bgks for q in fgks);active=[(j,k) for j,k in enumerate(bgks) if k['start']<=fgstart<k['end']]
  if active:chunk=f'OVERLAP_BG_KERNEL_{active[0][0]}:{active[0][1]["grid"]}'
  else:
   prev=[(j,k) for j,k in enumerate(bgks) if k['end']<=fgstart];nxt=[(j,k) for j,k in enumerate(bgks) if k['start']>=fgstart];chunk=f'SAFE_BOUNDARY_AFTER_{prev[-1][0] if prev else "NONE"}_BEFORE_{nxt[0][0] if nxt else "NONE"}'
  rows.append({'arm':a.arm,'arrival_target':a.arrival,'rep':b['rep'],'t_bg_start_ns':bgstart,'t_ready_ns':ready,'t_submit_end_ns':submit,'t_fg_first_kernel_start_ns':fgstart,'t_fg_last_kernel_end_ns':fgend,'t_bg_end_ns':bgend,'actual_arrival_fraction_of_b0':actual,'arrival_valid':valid,'background_active_at_ready':bgstart<=ready<bgend,'ready_to_fg_start_us':(fgstart-ready)/1000,'submit_to_fg_start_us':(fgstart-submit)/1000,'ready_to_fg_complete_us':(fgend-ready)/1000,'foreground_gpu_duration_us':(fgend-fgstart)/1000,'background_gpu_span_us':(bgend-bgstart)/1000,'background_completion_extension_us':(bgend-bgstart)/1000-a.b0_ms*1000,'background_kernel_at_fg_start':chunk,'gpu_interval_overlap':overlap,'background_kernel_count':len(bgks),'foreground_kernel_count':len(fgks),'background_stream_ids':','.join(map(str,sorted(set(k['stream'] for k in bgks)))),'foreground_stream_ids':','.join(map(str,sorted(set(k['stream'] for k in fgks))))})
 db.close();a.out.parent.mkdir(parents=True,exist_ok=True)
 with a.out.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 valid=[r for r in rows if r['arrival_valid']];summary={'arm':a.arm,'arrival':a.arrival,'repetitions':len(rows),'valid_repetitions':len(valid),'actual_fraction_median':statistics.median(r['actual_arrival_fraction_of_b0'] for r in rows),'ready_to_start_median_us':statistics.median(r['ready_to_fg_start_us'] for r in valid) if valid else None,'all_valid':len(valid)==7};print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
