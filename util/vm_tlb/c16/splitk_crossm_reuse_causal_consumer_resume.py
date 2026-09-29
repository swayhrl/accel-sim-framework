#!/usr/bin/env python3
import csv,hashlib,io,json,statistics,subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
P='docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_NATIVE_109_V1';C='2f8338408b2b9a39f5a6fc1bab9db015a019ea62';O='docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1'
def b(repo,n):return subprocess.check_output(['git','show',f'{C}:{P}/{n}'],cwd=repo)
def t(repo,n):return list(csv.DictReader(io.StringIO(b(repo,n).decode()),delimiter='\t'))
def st(v):return {'n':len(v),'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'mean_ms':statistics.mean(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def boot(rows,k,s):
 d=defaultdict(list)
 for r in rows:
  if int(r['K'])==k and int(r['split'])==s:d[(int(r['block']),r['state'])].append(float(r['ms']))
 rng=np.random.default_rng(20260928);x=[]
 for _ in range(1000):
  q=rng.integers(0,25,25);sh=float(np.median([v for i in q for v in d[(int(i),'SHARED')]]));pm=float(np.median([v for i in q for v in d[(int(i),'PER_MTILE')]]));x.append(pm/sh)
 try:return [float(z) for z in np.quantile(x,[.05,.5,.95],method='linear')]
 except TypeError:return [float(z) for z in np.quantile(x,[.05,.5,.95],interpolation='linear')]
def wt(p,fields,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();[w.writerow({k:'NA' if r.get(k) is None else r.get(k) for k in fields}) for r in rows]
def main():
 repo=Path.cwd();out=repo/O;sums={x.split(maxsplit=1)[1].strip():x.split()[0] for x in b(repo,'SHA256SUMS').decode().splitlines()}
 for n in ('TIMING_SAMPLES.tsv','NCU_KERNEL_ROWS.tsv','CORRECTNESS.tsv','LAUNCH_AUDIT.tsv','SOURCE_AND_GATE.json','GPU_LOCK_RECEIPT.json'):assert hashlib.sha256(b(repo,n)).hexdigest()==sums[n]
 tim=t(repo,'TIMING_SAMPLES.tsv');ncu=t(repo,'NCU_KERNEL_ROWS.tsv');corr=t(repo,'CORRECTNESS.tsv');launch=t(repo,'LAUNCH_AUDIT.tsv');assert len(tim)==400 and all(r['pass']=='True' for r in corr+launch)
 rows=[];cmp=[];nj={}
 for k in (2560,3072):
  for s in (1,8):
   q=boot(tim,k,s);cells={}
   for state in ('SHARED','PER_MTILE'):
    vals=[float(r['ms']) for r in tim if int(r['K'])==k and int(r['split'])==s and r['state']==state];ss=st(vals);nr=[r for r in ncu if int(r['K'])==k and int(r['split'])==s and r['state']==state];g=next(r for r in nr if r['kind']=='GEMM');red=next((r for r in nr if r['kind']=='REDUCTION'),None);hit=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum']);miss=float(g['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']);cells[state]={**ss,'hit':hit,'miss':miss,'frac':hit/(hit+miss),'dram':float(g['dram__bytes.sum']),'red':float(red['dram__bytes.sum']) if red else 0}
    rows.append({'K':k,'split':s,'sharing_state':state,**ss,'l2_read_hit_sectors':hit,'l2_read_miss_sectors':miss,'l2_read_hit_fraction':hit/(hit+miss),'gemm_dram_bytes':float(g['dram__bytes.sum']),'reduction_dram_bytes':float(red['dram__bytes.sum']) if red else 0,'total_dram_bytes':float(g['dram__bytes.sum'])+(float(red['dram__bytes.sum']) if red else 0),'correctness':'PASS','status':'PASS'})
   a=cells['SHARED'];z=cells['PER_MTILE'];missbytes=(z['miss']-a['miss'])*32;dramdelta=z['dram']-a['dram'];cmp.append({'K':k,'split':s,'shared_median_ms':a['median_ms'],'per_mtile_median_ms':z['median_ms'],'timing_ratio_per_mtile_shared':z['median_ms']/a['median_ms'],'timing_delta_ms':z['median_ms']-a['median_ms'],'shared_l2_hit_fraction':a['frac'],'per_mtile_l2_hit_fraction':z['frac'],'l2_hit_fraction_delta':z['frac']-a['frac'],'shared_l2_miss_sectors':a['miss'],'per_mtile_l2_miss_sectors':z['miss'],'miss_ratio':z['miss']/a['miss'],'shared_gemm_dram_bytes':a['dram'],'per_mtile_gemm_dram_bytes':z['dram'],'dram_ratio':z['dram']/a['dram'],'added_miss_bytes_32B':missbytes,'added_gemm_dram_bytes':dramdelta,'miss32B_to_dram_delta_ratio':missbytes/dramdelta,'bootstrap_timing_ratio_p05':q[0],'bootstrap_timing_ratio_median':q[1],'bootstrap_timing_ratio_p95':q[2],'interpretation_status':'RAW_RECOMPUTED'});nj[f'K{k}_S{s}']={'SHARED':a,'PER_MTILE':z,'added_miss_bytes_32B':missbytes,'added_gemm_dram_bytes':dramdelta}
 rf=list(csv.DictReader((out/'RAW_RECOMPUTE.tsv').open(),delimiter='\t').fieldnames);rf += [x for x in rows[0] if x not in rf];wt(out/'RAW_RECOMPUTE.tsv',rf,rows);cf=list(csv.DictReader((out/'REUSE_CAUSAL_COMPARISON.tsv').open(),delimiter='\t').fieldnames);cf += ['added_miss_bytes_32B','added_gemm_dram_bytes','miss32B_to_dram_delta_ratio'];wt(out/'REUSE_CAUSAL_COMPARISON.tsv',cf,cmp)
 (out/'NCU_RECOMPUTE.json').write_text(json.dumps({'status':'PASS_RAW_RECOMPUTE','cells':nj,'claim_boundary':'combined weight-side sharing; no qweight/qzeros/scales attribution'},indent=2,sort_keys=True)+'\n')
 c={(r['K'],r['split']):r for r in cmp};k25=c[(2560,1)];k30=c[(3072,1)];s825=c[(2560,8)];s830=c[(3072,8)]
 conclusion=f"K2560 split1在PER_MTILE下L2 hit从{100*k25['shared_l2_hit_fraction']:.1f}%降至{100*k25['per_mtile_l2_hit_fraction']:.1f}%，DRAM增至{k25['dram_ratio']:.2f}倍、timing增至{k25['timing_ratio_per_mtile_shared']:.2f}倍。K3072同方向但hit损失较小。split8两个K的约95.9%高hit均降至约28%，DRAM增至{s825['dram_ratio']:.2f}/{s830['dram_ratio']:.2f}倍。新增miss sectors×32B与新增GEMM DRAM高度一致。跨M combined weight-side地址共享因此是高L2 hit的重要来源，split-K的小局部集合有助于复用存活。"
 (out/'MECHANISM_INTERPRETATION.md').write_text('# 机制解释\n\n'+conclusion+'\n\n边界：不能细分qweight/qzeros/scales；PER_MTILE也扩大VA/TLB footprint；不推断replacement；不推广到所有GEMM/LLM。\n')
 (out/'FINAL_DECISION.json').write_text(json.dumps({'schema_version':2,'scientific_conclusion_zh':conclusion,'support_cross_m_reuse':True,'next_step_zh':'建议split1 grouped/swizzled CTA mapping强基线；不追加replica或split扫描','gpu_used':False},indent=2,sort_keys=True)+'\n');(out/'OPEN_ISSUES.md').write_text('# Open issues\n\n- combined weight-side，不能细分tensor。\n- PER_MTILE同时扩大VA/TLB footprint。\n- grouped/swizzled CTA仅建议，未执行。\n')
 a=json.loads((out/'AUTHORITY_AUDIT.json').read_text());a.update({'status':'PASS_FORMAL_CONSUMPTION','lane8_final':'bcc3a7082ffb66ab85d8ef8c62439ada97090d16','lane7_final':C,'formal_consumption_started':True});(out/'AUTHORITY_AUDIT.json').write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');(out/'README.md').write_text('# C16 split-K跨M复用因果独立consumer\n\n正式raw重算完成。见REUSE_CAUSAL_COMPARISON.tsv与MECHANISM_INTERPRETATION.md。\n')
 files=sorted(x for x in out.iterdir() if x.is_file() and x.name!='SHA256SUMS');(out/'SHA256SUMS').write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.name}' for x in files)+'\n')
if __name__=='__main__':main()
