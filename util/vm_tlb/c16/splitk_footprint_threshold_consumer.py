#!/usr/bin/env python3
import csv,hashlib,io,json,statistics,subprocess
from pathlib import Path
from collections import defaultdict
import numpy as np

STATIC='c72d28b17247f25d0c3613604ab6cab1737666e0';NATIVE='b17193ff6b3786fd01d5bfe83b5c1a0a03859729';END='1544018d967003c2825eb69f56440f641f5f5581'
SP='docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1';NP='docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1';EP='docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1';OUT='docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1';L2=67108864
def b(repo,c,p):return subprocess.check_output(['git','show',f'{c}:{p}'],cwd=repo)
def t(repo,c,p):return list(csv.DictReader(io.StringIO(b(repo,c,p).decode()),delimiter='\t'))
def st(v):return {'n':len(v),'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'mean_ms':statistics.mean(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def boot(rows,point):
 d=defaultdict(list)
 for r in rows:
  if r['point']==point:d[(int(r['block']),r['arm'])].append(float(r['ms']))
 rng=np.random.default_rng(20260928);x=[]
 for _ in range(1000):
  q=rng.integers(0,25,25);a=float(np.median([v for i in q for v in d[(int(i),'A')]]));bb=float(np.median([v for i in q for v in d[(int(i),'B')]]));x.append(1-bb/a)
 try:return [float(z) for z in np.quantile(x,[.05,.5,.95],method='linear')]
 except TypeError:return [float(z) for z in np.quantile(x,[.05,.5,.95],interpolation='linear')]
def wt(p,fields,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();[w.writerow({k:'NA' if r.get(k) is None else r.get(k) for k in fields}) for r in rows]
def main():
 repo=Path.cwd();out=repo/OUT;out.mkdir(parents=True,exist_ok=True)
 assert subprocess.check_output(['git','rev-parse',f'{STATIC}^{{tree}}'],cwd=repo,text=True).strip()=='b7d8654f47023e80389e7dd8e78b907c41983bf9'
 assert subprocess.check_output(['git','rev-parse',f'{NATIVE}^{{tree}}'],cwd=repo,text=True).strip()=='2a6e42fab5cd8b03c01d900d59f0abd5df355c1f'
 foot=t(repo,STATIC,f'{SP}/PER_SPLIT_FOOTPRINT.tsv');tim=t(repo,NATIVE,f'{NP}/TIMING_SAMPLES.tsv');ncu=t(repo,NATIVE,f'{NP}/NCU_KERNEL_ROWS.tsv');corr=t(repo,NATIVE,f'{NP}/CORRECTNESS.tsv');launch=t(repo,NATIVE,f'{NP}/LAUNCH_AUDIT.tsv')
 ss={x.split(maxsplit=1)[1].strip():x.split(maxsplit=1)[0] for x in b(repo,STATIC,f'{SP}/SHA256SUMS').decode().splitlines()};ns={x.split(maxsplit=1)[1].strip():x.split(maxsplit=1)[0] for x in b(repo,NATIVE,f'{NP}/SHA256SUMS').decode().splitlines()}
 assert hashlib.sha256(b(repo,STATIC,f'{SP}/PER_SPLIT_FOOTPRINT.tsv')).hexdigest()==ss['PER_SPLIT_FOOTPRINT.tsv']
 for name in ('TIMING_SAMPLES.tsv','NCU_KERNEL_ROWS.tsv','CORRECTNESS.tsv','LAUNCH_AUDIT.tsv'):assert hashlib.sha256(b(repo,NATIVE,f'{NP}/{name}')).hexdigest()==ns[name]
 assert len(tim)==400 and all(r['pass']=='True' for r in corr+launch)
 fmap={}
 for k in (2048,2560,3072,4096):
  full=next(r for r in foot if int(r['K'])==k and int(r['split_k_iters'])==1);local=next(r for r in foot if int(r['K'])==k and int(r['split_k_iters'])==8 and int(r['split_z'])==0);fmap[k]=(int(full['total_unique_bytes']),int(local['total_unique_bytes']))
 rows=[];ncuj={}
 for k in (2048,2560,3072,4096):
  point=f'K{k}';cells={a:st([float(r['ms']) for r in tim if r['point']==point and r['arm']==a]) for a in ('A','B')};gain=1-cells['B']['median_ms']/cells['A']['median_ms'];q=boot(tim,point);nr=[r for r in ncu if r['point']==point];ag=sum(int(r['dram_bytes']) for r in nr if r['arm']=='A' and r['kernel_kind']=='GEMM');ar=sum(int(r['dram_bytes']) for r in nr if r['arm']=='A' and r['kernel_kind']=='REDUCTION');bd=sum(int(r['dram_bytes']) for r in nr if r['arm']=='B');full,local=fmap[k]
  row={'K':k,'point':point,'full_footprint_bytes':full,'full_footprint_l2':full/L2,'split8_local_bytes':local,'split8_local_l2':local/L2,'gain':gain,'bootstrap_p05':q[0],'bootstrap_median':q[1],'bootstrap_p95':q[2],'A_total_dram':ag+ar,'A_gemm_dram':ag,'A_reduction_dram':ar,'B_gemm_dram':bd,'B_A_total_dram_ratio':bd/(ag+ar),'B_A_gemm_only_ratio':bd/ag,'B_dram_per_full_footprint':bd/full,'A_gemm_dram_per_full_footprint':ag/full,'A_median_ms':cells['A']['median_ms'],'B_median_ms':cells['B']['median_ms'],'timing_ratio_B_A':cells['B']['median_ms']/cells['A']['median_ms']}
  for a in ('A','B'):
   for x,v in cells[a].items():row[f'{a}_{x}']=v
  rows.append(row);ncuj[point]={'A_total':ag+ar,'A_gemm':ag,'A_reduction':ar,'B_gemm':bd}
 fields=list(rows[0]);wt(out/'NEW_K_RECOMPUTE.tsv',fields,rows)
 # accepted K12288 endpoint from earlier raw W4 samples, no threshold bootstrap
 et=t(repo,END,f'{EP}/W4_TIMING_SAMPLES.tsv');en=t(repo,END,f'{EP}/NCU_KERNEL_ROWS.tsv');vals={a:st([float(r['ms']) for r in et if r['point']=='EXPAND_M256' and r['arm']==a and r['state']=='W']) for a in ('A','B')};er=[r for r in en if r['track']=='W4' and r['point']=='EXPAND_M256' and r['state']=='WARM_SAME_ARM'];ag=sum(int(r['dram_bytes']) for r in er if r['arm']=='A' and r['kernel_kind']=='GEMM');ar=sum(int(r['dram_bytes']) for r in er if r['arm']=='A' and r['kernel_kind']=='REDUCTION');bd=sum(int(r['dram_bytes']) for r in er if r['arm']=='B');endpoint={'K':12288,'point':'K12288_ACCEPTED_ENDPOINT','full_footprint_bytes':313786368,'full_footprint_l2':4.67578125,'split8_local_bytes':43646976,'split8_local_l2':0.650390625,'gain':1-vals['B']['median_ms']/vals['A']['median_ms'],'A_median_ms':vals['A']['median_ms'],'B_median_ms':vals['B']['median_ms'],'A_total_dram':ag+ar,'A_gemm_dram':ag,'A_reduction_dram':ar,'B_gemm_dram':bd,'B_A_total_dram_ratio':bd/(ag+ar),'B_A_gemm_only_ratio':bd/ag,'bootstrap_status':'NOT_INCLUDED_OLD_CAMPAIGN'};wt(out/'ACCEPTED_ENDPOINT_RECOMPUTE.tsv',list(endpoint),[endpoint])
 series=rows+[endpoint];comp=[]
 for i,r in enumerate(series):
  prev=series[i-1] if i else None;comp.append({**r,'K_growth_from_prev':None if not prev else r['K']/prev['K'],'B_dram_growth_from_prev':None if not prev else r['B_gemm_dram']/prev['B_gemm_dram'],'A_dram_growth_from_prev':None if not prev else r['A_total_dram']/prev['A_total_dram'],'B_timing_growth_from_prev':None if not prev else r['B_median_ms']/prev['B_median_ms'],'A_timing_growth_from_prev':None if not prev else r['A_median_ms']/prev['A_median_ms']})
 wt(out/'CAPACITY_THRESHOLD_COMPARISON.tsv',list(comp[0])+['K_growth_from_prev','B_dram_growth_from_prev','A_dram_growth_from_prev','B_timing_growth_from_prev','A_timing_growth_from_prev'],comp)
 jump=rows[2]['B_gemm_dram']/rows[1]['B_gemm_dram'];ajump=rows[2]['A_total_dram']/rows[1]['A_total_dram'];kg=3072/2560;tjump=rows[2]['B_median_ms']/rows[1]['B_median_ms']
 audit={'status':'PASS','static_commit':STATIC,'native_commit':NATIVE,'accepted_endpoint_commit':END,'timing_rows':len(tim),'correctness_all_pass':True,'launch_all_pass':True,'gpu_used':False,'lane4_partial_accessed':False};(out/'AUTHORITY_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n');(out/'NCU_RECOMPUTE.json').write_text(json.dumps({'status':'PASS_RAW_ROWS','new_k':ncuj,'accepted_endpoint':{'A_total':ag+ar,'B_gemm':bd},'claim_boundary':'kernel totals; no tensor attribution or unique L2 causality'},indent=2,sort_keys=True)+'\n')
 conclusion=f'K2560到3072仅增长20%，split1 DRAM却增长{jump:.2f}倍，split8总DRAM仅增长{ajump:.2f}倍；split1 median timing同步增长{tjump:.2f}倍。连续K序列显示split1收益随K总体恶化并在K4096附近接近翻转，K12288延续为强负收益。工作集容量是重要因素，但64MiB不是硬阈值，也不能把全部DRAM归为qweight或唯一归因L2。'
 (out/'MECHANISM_INTERPRETATION.md').write_text('# 机制解释\n\n'+conclusion+'\n\n建议后续只做K4096 M256 N49152 split1/split8 paired capacity counterfactual；本consumer不执行。\n');(out/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':1,'scientific_conclusion_zh':conclusion,'K2560_to_3072':{'K_growth':kg,'split1_dram_growth':jump,'split8_total_dram_growth':ajump,'split1_timing_growth':tjump},'recommendation_zh':'建议K4096 paired capacity counterfactual，不自动执行SASS/Accel-Sim','gpu_used':False},indent=2,sort_keys=True)+'\n');(out/'OPEN_ISSUES.md').write_text('# Open issues\n\n- 64MiB不是硬阈值。\n- NCU无tensor级归因。\n- CTA调度、替换策略和唯一L2因果未证明。\n')
 (out/'README.md').write_text('# C16 split-K工作集容量阈值独立consumer\n\n从Lane7基础timing/NCU行与Lane8静态footprint独立重算。主结论见MECHANISM_INTERPRETATION.md和FINAL_DECISION.json。\n')
 files=sorted(x for x in out.iterdir() if x.is_file() and x.name!='SHA256SUMS');(out/'SHA256SUMS').write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
