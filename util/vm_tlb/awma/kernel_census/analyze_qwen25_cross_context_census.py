#!/usr/bin/env python3
"""Correlation-first Lane F structural census consumer (offline; no GPU work)."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sqlite3
from collections import defaultdict
from pathlib import Path

try:
    from analyze_q05_s2_kernel_census_v2 import family
except ImportError:
    def family(name): return 'UNKNOWN'

KEY = ('phase', 'normalized_kernel_family', 'exact_implementation', 'grid', 'block')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse_nvtx(text): return dict(x.split('=',1) for x in text.split(';') if '=' in x)
def w(path, fields, rows):
    with Path(path).open('w', newline='') as f:
        z=csv.DictWriter(f, fieldnames=fields, delimiter='\t'); z.writeheader(); z.writerows(rows)

def one(scenario, run, raw_root):
    db=sqlite3.connect(f'file:{run}/census.sqlite?mode=ro', uri=True)
    strings=dict(db.execute('select id,value from StringIds'))
    ranges=[]
    for start,end,text,tid in db.execute("select start,end,text,globalTid from NVTX_EVENTS where text like 'C16_PHASE=%' order by start"):
        d=parse_nvtx(text); ranges.append(dict(start=start,end=end,tid=tid,phase=d['C16_PHASE'],step=d.get('STEP',''),label=text))
    runtime=defaultdict(list)
    for start,end,corr,tid,nid in db.execute('select start,end,correlationId,globalTid,nameId from CUPTI_ACTIVITY_KIND_RUNTIME where correlationId is not null'):
        runtime[corr].append((start,end,tid,strings.get(nid,'UNKNOWN_RUNTIME_API')))
    rows=[]
    q='select start,end,streamId,correlationId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start,end'
    for i,x in enumerate(db.execute(q)):
        st,en,stream,corr,gx,gy,gz,bx,by,bz,dn,sn,mn=x; rs=runtime.get(corr,[])
        phase='UNKNOWN'; step=''; method='UNKNOWN_NO_UNIQUE_CUPTI_RUNTIME'
        if len(rs)==1:
            rt=rs[0]; matching=[z for z in ranges if z['tid']==rt[2] and z['start']<=rt[0]<=z['end']]
            if len(matching)==1:
                phase=matching[0]['phase']; step=matching[0]['step']; method='CUPTI_CORRELATED_RUNTIME_START_IN_SAME_THREAD_NVTX'
            elif not matching:
                phase='AUXILIARY'; method='AUXILIARY_RUNTIME_START_OUTSIDE_ALL_C16_PHASE_RANGES'
            else: method='UNKNOWN_AMBIGUOUS_SAME_THREAD_NVTX'
        name=strings.get(dn) or strings.get(sn) or strings.get(mn) or 'UNKNOWN_KERNEL_NAME'
        rows.append(dict(scenario=scenario,global_launch_index=i,phase=phase,decode_step=step,assignment_method=method,runtime_correlation_id='' if corr is None else corr,start_ns=st,end_ns=en,duration_ns=en-st,stream=stream,grid=f'{gx},{gy},{gz}',block=f'{bx},{by},{bz}',exact_implementation=name,normalized_kernel_family=family(name)))
    db.close()
    raw=raw_root/scenario; raw.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0]); w(raw/'ALL_KERNEL_LAUNCHES.tsv',fields,rows)
    groups=defaultdict(lambda: [0,0,set()])
    perstep=defaultdict(lambda: defaultdict(int))
    for r in rows:
        k=tuple(r[k] for k in KEY); groups[k][0]+=1; groups[k][1]+=int(r['duration_ns']); groups[k][2].add(r['decode_step'])
        if r['phase']=='DECODE': perstep[k][r['decode_step']]+=1
    total=sum(int(r['duration_ns']) for r in rows)
    strata=[]; recurrence=[]
    for k,(count,dur,steps) in sorted(groups.items()):
        d=dict(zip(KEY,k)); d.update(launch_count=count,accumulated_gpu_duration_ns=dur,gpu_time_share=dur/total)
        if d['phase']=='DECODE':
            counts=list(perstep[k].values()); d.update(decode_step_count=len(counts),launches_per_decode_step_min=min(counts),launches_per_decode_step_max=max(counts),launches_per_decode_step_mean=sum(counts)/len(counts),recurrence_stable=min(counts)==max(counts))
            for step,c in sorted(perstep[k].items(),key=lambda t:int(t[0])): recurrence.append(dict(scenario=scenario,phase=d['phase'],normalized_kernel_family=d['normalized_kernel_family'],exact_implementation=d['exact_implementation'],grid=d['grid'],block=d['block'],decode_step=step,launch_count=c))
        else: d.update(decode_step_count='',launches_per_decode_step_min='',launches_per_decode_step_max='',launches_per_decode_step_mean='',recurrence_stable='')
        strata.append(d)
    w(raw/'STRATA.tsv',list(strata[0]),strata); w(raw/'PER_STEP_RECURRENCE.tsv',list(recurrence[0]) if recurrence else ['scenario'],recurrence)
    phase={}
    for p in sorted(set(r['phase'] for r in rows)):
        rr=[r for r in rows if r['phase']==p]; phase[p]={'launches':len(rr),'gpu_duration_ns':sum(int(r['duration_ns']) for r in rr),'gpu_time_share':sum(int(r['duration_ns']) for r in rr)/total}
    receipt={'scenario':scenario,'sqlite_sha256':sha(run/'census.sqlite'),'total_launches':len(rows),'total_gpu_duration_ns':total,'phase_summary':phase,'assignment_method_counts':{m:sum(r['assignment_method']==m for r in rows) for m in sorted(set(r['assignment_method'] for r in rows))},'nvtx_range_count':len(ranges),'method':'CUPTI correlation -> exactly one CPU runtime launch -> same-thread NVTX range containing runtime start; no GPU/NVTX wall-time overlap'}
    (raw/'SCENARIO_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return strata,recurrence,receipt

def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--raw-out',type=Path,required=True); p.add_argument('--review-out',type=Path,required=True); a=p.parse_args()
 mapping={'T256':'T256_D32_DERIVED_CONTROL','T8192':'T8192_D32_ACCEPTED_S3_TEXT','B4':'B4_T2048_D32_REPLICATED_CONTROL','D128':'T2048_D128_ACCEPTED_S2_TEXT'}
 all_s={}; all_r={}; receipts={}
 for d,s in mapping.items(): all_s[s],all_r[s],receipts[s]=one(s,a.root/d,a.raw_out)
 base=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-qwen25-cross-context-census-v1/docs/vm_tlb/review_packs/AWMA_QWEN25_STRUCTURAL_SIGNATURE_AND_SCENARIO_WEIGHT_V1/QWEN25_STRUCTURAL_AND_WEIGHTED_KERNEL_CATALOG_V1.tsv')
 b=[r for r in csv.DictReader(base.open(),delimiter='\t') if r['phase'] in ('PREFILL','DECODE') and r['exact_implementation'] not in ('','UNKNOWN')]
 bkeys={(r['phase'],r['normalized_kernel_family'],r['exact_implementation'],r['grid'],r['block']) for r in b}
 comparison=[]
 for s,strata in all_s.items():
  keys={tuple(r[k] for k in KEY) for r in strata}; add=keys-bkeys; removed=bkeys-keys
  verdict='REWEIGHT_ONLY' if not add and not removed else 'RESTRATIFY_REQUIRED'
  comparison.append(dict(scenario=s,verdict=verdict,baseline_strata=len(bkeys),scenario_strata=len(keys),new_exact_strata=len(add),missing_baseline_strata=len(removed),new_strata_gpu_time_share=sum(float(r['gpu_time_share']) for r in strata if tuple(r[k] for k in KEY) in add)))
  for r in strata: r['s2_catalog_join']='MATCH' if tuple(r[k] for k in KEY) in bkeys else 'NEW_OR_RESTRATIFIED'
 a.review_out.mkdir(parents=True,exist_ok=True)
 w(a.review_out/'SCENARIO_COMPARISON.tsv',list(comparison[0]),comparison)
 for s,x in all_s.items(): w(a.review_out/f'{s}_STRATA.tsv',list(x[0]),x)
 for s,x in all_r.items(): w(a.review_out/f'{s}_RECURRENCE.tsv',list(x[0]) if x else ['scenario'],x)
 (a.review_out/'RUN_RECEIPT.json').write_text(json.dumps({'stage':'AWMA_QWEN25_CROSS_CONTEXT_STRUCTURAL_CENSUS_V1','receipts':receipts,'baseline_catalog_sha256':sha(base),'content_scenario':'STOP_NO_SECOND_ACCEPTED_OR_EXPLICITLY_FROZEN_T2048_TEXT_PAYLOAD'},indent=2,sort_keys=True)+'\n')
 print(json.dumps(comparison,sort_keys=True))
if __name__=='__main__': main()
