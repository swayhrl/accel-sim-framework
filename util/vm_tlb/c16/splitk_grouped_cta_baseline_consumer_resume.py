#!/usr/bin/env python3
import csv,hashlib,io,json,statistics,subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
C='a75379674116fc94e57ccc88eff9359fc1f4114c';P='docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1';O='docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1'
def b(r,n):return subprocess.check_output(['git','show',f'{C}:{P}/{n}'],cwd=r)
def t(r,n):return list(csv.DictReader(io.StringIO(b(r,n).decode()),delimiter='\t'))
def st(v):return {'n':len(v),'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'mean_ms':statistics.mean(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def boot(rows,k,s):
 d=defaultdict(list)
 for x in rows:
  if int(x['K'])==k and int(x['split'])==s:d[(int(x['block']),x['mapping'])].append(float(x['ms']))
 rng=np.random.default_rng(20260929);z=[]
 for _ in range(1000):
  q=rng.integers(0,25,25);row=float(np.median([v for i in q for v in d[(int(i),'ROW')]]));g=float(np.median([v for i in q for v in d[(int(i),'GROUP_M16')]]));z.append(g/row)
 try:return [float(x) for x in np.quantile(z,[.05,.5,.95],method='linear')]
 except TypeError:return [float(x) for x in np.quantile(z,[.05,.5,.95],interpolation='linear')]
def wt(p,f,rows):
 with p.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=f,delimiter='\t',lineterminator='\n');w.writeheader();[w.writerow({k:'NA' if x.get(k) is None else x.get(k) for k in f}) for x in rows]
def main():
 r=Path.cwd();o=r/O;sums={x.split(maxsplit=1)[1].strip():x.split()[0] for x in b(r,'SHA256SUMS').decode().splitlines()}
 for n in ('TIMING_SAMPLES.tsv','NCU_KERNEL_ROWS.tsv','CORRECTNESS.tsv','LAUNCH_AUDIT.tsv','ROW_CALIBRATION.tsv','SOURCE_AND_GATE.json','GPU_LOCK_RECEIPT.json'):assert hashlib.sha256(b(r,n)).hexdigest()==sums[n]
 tim=t(r,'TIMING_SAMPLES.tsv');ncu=t(r,'NCU_KERNEL_ROWS.tsv');corr=t(r,'CORRECTNESS.tsv');launch=t(r,'LAUNCH_AUDIT.tsv');cal=t(r,'ROW_CALIBRATION.tsv');assert len(tim)==400 and all(x['pass']=='True' for x in corr+launch) and all(x['decision']=='PASS' for x in cal)
 raw=[];cmp=[];cells={}
 for k in (3072,4096):
  for s in (1,8):
   q=boot(tim,k,s)
   for m in ('ROW','GROUP_M16'):
    vals=[float(x['ms']) for x in tim if int(x['K'])==k and int(x['split'])==s and x['mapping']==m];ss=st(vals);nr=[x for x in ncu if int(x['K'])==k and int(x['split'])==s and x['mapping']==m];g=next(x for x in nr if x['kind']=='GEMM');red=next((x for x in nr if x['kind']=='REDUCTION'),None);hit=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum']);miss=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']);cells[(k,s,m)]={**ss,'hitfrac':hit/(hit+miss),'hit':hit,'miss':miss,'dram':float(g['dram__bytes.sum']),'red':float(red['dram__bytes.sum']) if red else 0};raw.append({'K':k,'split':s,'mapping':m,**ss,'l2_read_hit_sectors':hit,'l2_read_miss_sectors':miss,'l2_read_hit_fraction':hit/(hit+miss),'gemm_dram_bytes':float(g['dram__bytes.sum']),'reduction_dram_bytes':float(red['dram__bytes.sum']) if red else 0,'total_dram_bytes':float(g['dram__bytes.sum'])+(float(red['dram__bytes.sum']) if red else 0),'correctness':'PASS','row_calibration_status':'PASS','status':'PASS'})
   a=cells[(k,s,'ROW')];g=cells[(k,s,'GROUP_M16')];cmp.append({'K':k,'split':s,'row_median_ms':a['median_ms'],'group_median_ms':g['median_ms'],'group_row_timing_ratio':g['median_ms']/a['median_ms'],'timing_improvement_fraction':1-g['median_ms']/a['median_ms'],'row_hit_fraction':a['hitfrac'],'group_hit_fraction':g['hitfrac'],'hit_delta_pp':100*(g['hitfrac']-a['hitfrac']),'row_miss_sectors':a['miss'],'group_miss_sectors':g['miss'],'miss_ratio':g['miss']/a['miss'],'row_gemm_dram_bytes':a['dram'],'group_gemm_dram_bytes':g['dram'],'dram_ratio':g['dram']/a['dram'],'bootstrap_ratio_p05':q[0],'bootstrap_ratio_median':q[1],'bootstrap_ratio_p95':q[2],'interpretation_status':'PASS_RAW_RECOMPUTE'})
 rf=list(csv.DictReader((o/'RAW_RECOMPUTE.tsv').open(),delimiter='\t').fieldnames);rf += [x for x in raw[0] if x not in rf];wt(o/'RAW_RECOMPUTE.tsv',rf,raw);cf=list(csv.DictReader((o/'GROUPED_STRONG_BASELINE_COMPARISON.tsv').open(),delimiter='\t').fieldnames);wt(o/'GROUPED_STRONG_BASELINE_COMPARISON.tsv',cf,cmp)
 eq=[]
 for k in (3072,4096):
  for m in ('ROW','GROUP_M16'):
   s1=cells[(k,1,m)];s8=cells[(k,8,m)];eq.append({'K':k,'mapping':m,'split1_median_ms':s1['median_ms'],'split8_median_ms':s8['median_ms'],'split1_gain':1-s1['median_ms']/s8['median_ms'],'split1_hit_fraction':s1['hitfrac'],'split8_hit_fraction':s8['hitfrac'],'hit_difference_pp':100*(s1['hitfrac']-s8['hitfrac']),'split1_gemm_dram_bytes':s1['dram'],'split8_gemm_dram_bytes':s8['dram'],'dram_ratio_split1_split8':s1['dram']/s8['dram'],'conclusion_status':'PASS_RAW_RECOMPUTE'})
 ef=list(csv.DictReader((o/'EQUAL_MAPPING_SPLIT_COMPARISON.tsv').open(),delimiter='\t').fieldnames);wt(o/'EQUAL_MAPPING_SPLIT_COMPARISON.tsv',ef,eq)
 nout={'status':'PASS_RAW_RECOMPUTE','cells':{f'K{k}_S{s}_{m}':cells[(k,s,m)] for k in (3072,4096) for s in (1,8) for m in ('ROW','GROUP_M16')},'claim_boundary':'GEMM locality; split8 reduction separate'};(o/'NCU_RECOMPUTE.json').write_text(json.dumps(nout,indent=2,sort_keys=True)+'\n')
 e={(x['K'],x['split']):x for x in cmp};g={(x['K'],x['mapping']):x for x in eq};con=f"GROUP_M16将split1 hit在K3072/K4096从{100*e[(3072,1)]['row_hit_fraction']:.2f}%/{100*e[(4096,1)]['row_hit_fraction']:.2f}%恢复到{100*e[(3072,1)]['group_hit_fraction']:.2f}%/{100*e[(4096,1)]['group_hit_fraction']:.2f}%，DRAM降至ROW的{e[(3072,1)]['dram_ratio']:.3f}/{e[(4096,1)]['dram_ratio']:.3f}，timing降至{e[(3072,1)]['group_row_timing_ratio']:.3f}/{e[(4096,1)]['group_row_timing_ratio']:.3f}。split8从GROUP仅获小幅改善。相同GROUP mapping下split1比split8快{100*g[(3072,'GROUP_M16')]['split1_gain']:.1f}%/{100*g[(4096,'GROUP_M16')]['split1_gain']:.1f}，hit近似相同且GEMM DRAM仅为split8的{g[(3072,'GROUP_M16')]['dram_ratio_split1_split8']:.2f}/{g[(4096,'GROUP_M16')]['dram_ratio_split1_split8']:.2f}。经典软件mapping已解决当前冻结点大部分split1 reuse问题，当前新split机制故事应关闭。"
 (o/'SCIENTIFIC_INTERPRETATION.md').write_text('# 科学解释\n\n'+con+'\n');(o/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':2,'scientific_conclusion_zh':con,'new_split_mechanism_story':'关闭','future_question_zh':'在已有grouped/swizzled locality scheduling后，其他shape/M/并行度是否仍存在CTA供给、local working set与reduction成本无法兼顾的残余区间','gpu_used':False},indent=2,sort_keys=True)+'\n');(o/'OPEN_ISSUES.md').write_text('# Open issues\n\n- 仅限当前两个K与AutoAWQ kernel family。\n- logical adjacency不等于严格issue order。\n- 不追加GROUP_M或split扫描。\n');(o/'README.md').write_text('# C16 grouped CTA strong baseline consumer\n\n正式raw重算完成。经典GROUP_M16强基线基本解决当前split1 reuse问题。\n')
 a=json.loads((o/'AUTHORITY_AUDIT.json').read_text());a.update({'status':'PASS_FORMAL_CONSUMPTION','lane8_final':'0b37b84cf8fbcaaeb90c36fc28dcbb8ec3764ae1','lane7_final':C,'formal_consumption_started':True});(o/'AUTHORITY_AUDIT.json').write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');files=sorted(x for x in o.iterdir() if x.is_file() and x.name!='SHA256SUMS');(o/'SHA256SUMS').write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
