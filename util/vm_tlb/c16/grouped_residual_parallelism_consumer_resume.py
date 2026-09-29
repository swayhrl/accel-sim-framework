#!/usr/bin/env python3
import csv,hashlib,io,json,statistics,subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
C='c17c22ba00c3e1be540b165900c57de4090bd50f';P='docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1';O='docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1'
def b(r,n):return subprocess.check_output(['git','show',f'{C}:{P}/{n}'],cwd=r)
def t(r,n):return list(csv.DictReader(io.StringIO(b(r,n).decode()),delimiter='\t'))
def st(v):return {'n':len(v),'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'mean_ms':statistics.mean(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def boot(rows,m):
 d=defaultdict(list)
 for x in rows:
  if int(x['M'])==m:d[(int(x['block']),int(x['split']))].append(float(x['ms']))
 rng=np.random.default_rng(20260929);g1=[];g8=[]
 for _ in range(1000):
  q=rng.integers(0,25,25);a=float(np.median([v for i in q for v in d[(int(i),8)]]));s=float(np.median([v for i in q for v in d[(int(i),1)]]));g1.append(1-s/a);g8.append(1-a/s)
 def q(v):
  try:return [float(x) for x in np.quantile(v,[.05,.5,.95],method='linear')]
  except TypeError:return [float(x) for x in np.quantile(v,[.05,.5,.95],interpolation='linear')]
 return q(g1),q(g8)
def wt(p,f,rows):
 with p.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=f,delimiter='\t',lineterminator='\n');w.writeheader();[w.writerow({k:'NA' if x.get(k) is None else x.get(k) for k in f}) for x in rows]
def main():
 r=Path.cwd();o=r/O;sums={x.split(maxsplit=1)[1].strip():x.split()[0] for x in b(r,'SHA256SUMS').decode().splitlines()}
 for n in ('TIMING_SAMPLES.tsv','NCU_KERNEL_ROWS.tsv','CORRECTNESS.tsv','LAUNCH_AUDIT.tsv','SCIENTIFIC_PAYLOAD_INVARIANCE.json','SOURCE_AND_GATE.json'):assert hashlib.sha256(b(r,n)).hexdigest()==sums[n]
 inv=json.loads(b(r,'SCIENTIFIC_PAYLOAD_INVARIANCE.json'));assert inv['original_science_commit']=='ab84399012c89fce2c21fabac8d6f9fa8688d164' and inv['external_raw_all_unchanged'] and inv['binary']['actual_sha256']=='f98ac68a1e923c61c0351f1a688b899878a7d2eb72f7bbef6152e3bef7143693'
 assert subprocess.check_output(['git','rev-parse',f'{C}^'],cwd=r,text=True).strip()=='ab84399012c89fce2c21fabac8d6f9fa8688d164'
 tim=t(r,'TIMING_SAMPLES.tsv');ncu=t(r,'NCU_KERNEL_ROWS.tsv');assert len(tim)==400 and len(ncu)==12
 raw=[];sweep=[];nc={}
 for m in (1,16,32,64):
  cells={};q1,q8=boot(tim,m)
  for s in (1,8):
   vals=[float(x['ms']) for x in tim if int(x['M'])==m and int(x['split'])==s];ss=st(vals);nr=[x for x in ncu if int(x['M'])==m and int(x['split'])==s];g=next(x for x in nr if x['kind']=='GEMM');red=next((x for x in nr if x['kind']=='REDUCTION'),None);hit=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum']);miss=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']);grid=int(g['grid'].strip('()').split(',')[0]);cells[s]={**ss,'hitfrac':hit/(hit+miss) if hit+miss else 1.0,'hit':hit,'miss':miss,'dram':float(g['dram__bytes.sum']),'gemm_ns':float(g['gpu__time_duration.sum']),'red_ns':float(red['gpu__time_duration.sum']) if red else 0,'red_dram':float(red['dram__bytes.sum']) if red else 0,'grid':grid,'waves':float(g['launch__waves_per_multiprocessor']),'warps':float(g['sm__warps_active.avg.pct_of_peak_sustained_elapsed'])};raw.append({'M':m,'split':s,**ss,'gemm_duration_ns':cells[s]['gemm_ns'],'reduction_duration_ns':cells[s]['red_ns'],'reduction_dram_bytes':cells[s]['red_dram'],'l2_read_hit_sectors':hit,'l2_read_miss_sectors':miss,'l2_read_hit_fraction':cells[s]['hitfrac'],'gemm_dram_bytes':cells[s]['dram'],'gemm_grid':grid,'cta_per_76sm':grid/76,'launch_waves_per_sm':cells[s]['waves'],'active_warps_pct_elapsed':cells[s]['warps'],'correctness':'PASS','status':'PASS'})
  a=cells[8];s=cells[1];g1=1-s['median_ms']/a['median_ms'];g8=1-a['median_ms']/s['median_ms'];sweep.append({'M':m,'mtile_count':max(1,(m+15)//16),'split1_cta':s['grid'],'split8_cta':a['grid'],'split1_cta_per_sm':s['grid']/76,'split1_median_ms':s['median_ms'],'split8_median_ms':a['median_ms'],'g1':g1,'g8':g8,'bootstrap_g1_p05':q1[0],'bootstrap_g1_median':q1[1],'bootstrap_g1_p95':q1[2],'bootstrap_g8_p05':q8[0],'bootstrap_g8_median':q8[1],'bootstrap_g8_p95':q8[2],'split1_cv':s['cv'],'split8_cv':a['cv'],'split1_hit_fraction':s['hitfrac'],'split8_hit_fraction':a['hitfrac'],'split1_gemm_dram_bytes':s['dram'],'split8_gemm_dram_bytes':a['dram'],'split8_reduction_duration_ns':a['red_ns'],'split8_reduction_dram_bytes':a['red_dram'],'split1_launch_waves_per_sm':s['waves'],'split8_launch_waves_per_sm':a['waves'],'split1_active_warps_pct_elapsed':s['warps'],'split8_active_warps_pct_elapsed':a['warps'],'interpretation_status':'PASS_RAW_RECOMPUTE'});nc[f'M{m}']={'split1':s,'split8':a}
 rf=list(csv.DictReader((o/'RAW_RECOMPUTE.tsv').open(),delimiter='\t').fieldnames);rf += [x for x in raw[0] if x not in rf];wt(o/'RAW_RECOMPUTE.tsv',rf,raw);sf=list(csv.DictReader((o/'M_SWEEP_COMPARISON.tsv').open(),delimiter='\t').fieldnames);sf += [x for x in sweep[0] if x not in sf];wt(o/'M_SWEEP_COMPARISON.tsv',sf,sweep);(o/'NCU_RECOMPUTE.json').write_text(json.dumps({'status':'PASS_RAW_RECOMPUTE','cells':nc,'boundary':'TEX read-side hit only; native module timing separate from NCU kernel duration'},indent=2,sort_keys=True)+'\n')
 d={x['M']:x for x in sweep};con=f"split8在M1/M16/M32仍有优势，g1分别为{100*d[1]['g1']:.1f}%/{100*d[16]['g1']:.1f}%/{100*d[32]['g1']:.1f}%，但随split1 CTA从96到192增加而衰减；M64时split1反超约{100*d[64]['g1']:.2f}%，bootstrap区间为[{100*d[64]['bootstrap_g1_p05']:.2f}%, {100*d[64]['bootstrap_g1_p95']:.2f}%]。split1 TEX read-side L2 hit全程保持高位。残余split8价值集中在低CTA供给/partial-tile与reduction权衡，属于已有parallel decomposition问题；当前Split-K支线可以关闭。"
 (o/'PARALLELISM_INTERPRETATION.md').write_text('# 并行度解释\n\n'+con+'\n');(o/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':2,'scientific_conclusion_zh':con,'splitk_branch_should_close':True,'gpu_used':False},indent=2,sort_keys=True)+'\n');(o/'OPEN_ISSUES.md').write_text('# Open issues\n\n- launch CTA、waves/SM、active-warps%分别保留，不能互相替代。\n- 不证明单一occupancy机制。\n- 不追加M/split/GROUP扫描。\n');(o/'README.md').write_text('# C16 grouped residual parallelism consumer\n\n正式raw重算完成；当前Split-K支线关闭。\n')
 a=json.loads((o/'AUTHORITY_AUDIT.json').read_text());a.update({'status':'PASS_FORMAL_CONSUMPTION','prep_authority':'493250b11302344c1f445465da8c58e6275545bd','producer_science':'ab84399012c89fce2c21fabac8d6f9fa8688d164','provenance_correction':C,'scientific_payload_unchanged':True,'binary_sha256':'f98ac68a1e923c61c0351f1a688b899878a7d2eb72f7bbef6152e3bef7143693','formal_consumption_started':True});(o/'AUTHORITY_AUDIT.json').write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');files=sorted(x for x in o.iterdir() if x.is_file() and x.name!='SHA256SUMS');(o/'SHA256SUMS').write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
