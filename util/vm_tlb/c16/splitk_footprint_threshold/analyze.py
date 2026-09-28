#!/usr/bin/env python3
"""CPU-only descriptive analysis for the K footprint threshold producer."""
import argparse,csv,hashlib,io,json,shutil,statistics,subprocess
from pathlib import Path
from contracts import *

ENDPOINT='1544018d967003c2825eb69f56440f641f5f5581';EP='docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def tsv(p,fields,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore',lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:('NA' if r.get(k) in (None,'') else r.get(k)) for k in fields})
def show(repo,path):return subprocess.check_output(['git','-C',str(repo),'show',f'{ENDPOINT}:{EP}/{path}'],text=True)
def stats(v):return {'n':len(v),'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'mean_ms':statistics.mean(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def parse_ncu(path,k,arm):
 records=list(csv.reader(open(path,newline='')));h,u=records[0],records[1];out=[]
 for vals in records[2:]:
  if not vals or not vals[0] or len(vals)!=len(h):continue
  d,unit=dict(zip(h,vals)),dict(zip(h,u))
  if not d.get('Kernel Name'):continue
  num=lambda key:float(d[key].replace(',','')) if '.' in d[key] else int(d[key].replace(',',''));name=d['Kernel Name'];kind='GEMM' if 'gemm_forward' in name else 'REDUCTION' if 'reduce_kernel' in name else 'OTHER'
  out.append({'point':point_name(k),'K':k,'arm':arm,'kernel_order':len(out),'kernel_kind':kind,'kernel_name':name,'grid_size':d['Grid Size'],'block_size':d['Block Size'],'l1tex_bytes':int(num('l1tex__t_bytes.sum')),'lts_bytes':int(num('lts__t_bytes.sum')),'dram_bytes':int(num('dram__bytes.sum')),'duration_ns':int(num('gpu__time_duration.sum')),'registers_per_thread':int(num('launch__registers_per_thread')),'static_shared_bytes':int(num('launch__shared_mem_per_block_static')),'dynamic_shared_bytes':int(num('launch__shared_mem_per_block_dynamic')),'l1tex_unit':unit['l1tex__t_bytes.sum'],'lts_unit':unit['lts__t_bytes.sum'],'dram_unit':unit['dram__bytes.sum'],'duration_unit':unit['gpu__time_duration.sum']})
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 q=load(a.raw/'qualification.json');launch=load(a.raw/'launch_audit.json');timing=load(a.raw/'timing_samples.json');gate=load(a.repo/'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1/STATIC_GATE_BINDING.json')
 if q['status']!='PASS' or launch['status']!='PASS' or timing['status']!='PASS' or gate['gate_status']!='SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN':raise RuntimeError('gates')
 samples=timing['samples'];correct=q['correctness'];rows=[];series=[];statmap={}
 ncu=[];ncu_summary={}
 for k in KS:
  point=point_name(k);med={}
  for arm in ('A','B'):
   vals=[x['ms'] for x in samples if x['K']==k and x['arm']==arm]
   if len(vals)!=50:raise RuntimeError(f'samples {k}/{arm}')
   s=stats(vals);med[arm]=s['median_ms'];statmap[(k,arm)]=s;rows.append({'point':point,'K':k,'arm':arm,**s})
   pr=parse_ncu(a.raw/f'ncu_K{k}_{arm}.csv',k,arm);ncu+=pr
   if len(pr)!=(2 if arm=='A' else 1):raise RuntimeError(f'ncu count {k}/{arm}')
   ncu_summary[(k,arm)]={'dram_bytes_total':sum(x['dram_bytes'] for x in pr),'lts_bytes_total':sum(x['lts_bytes'] for x in pr),'l1tex_bytes_total':sum(x['l1tex_bytes'] for x in pr),'duration_ns_total':sum(x['duration_ns'] for x in pr),'reduction_dram_bytes':sum(x['dram_bytes'] for x in pr if x['kernel_kind']=='REDUCTION')}
  fp=next(x for x in gate['footprint_rows'] if int(x['K'])==k);gain=1-med['B']/med['A'];series.append({'point':point,'K':k,'source':'NEW_NATIVE','full_w4_bytes':int(fp['full_w4_bytes']),'full_over_l2':float(fp['full_over_l2']),'split8_static_bytes':int(fp['split8_static_bytes']),'A_median_ms':med['A'],'A_cv':statmap[(k,'A')]['cv'],'B_median_ms':med['B'],'B_cv':statmap[(k,'B')]['cv'],'split1_gain':gain,'A_dram_bytes':ncu_summary[(k,'A')]['dram_bytes_total'],'B_dram_bytes':ncu_summary[(k,'B')]['dram_bytes_total'],'B_over_A_dram':ncu_summary[(k,'B')]['dram_bytes_total']/ncu_summary[(k,'A')]['dram_bytes_total'],'A_reduction_dram_bytes':ncu_summary[(k,'A')]['reduction_dram_bytes']})
 ep_t=list(csv.DictReader(io.StringIO(show(a.repo,'W4_TIMING_SUMMARY.tsv')),delimiter='\t'));ep_cells={r['cell']:r for r in ep_t if r['record_type']=='CELL' and r['point']=='EXPAND_M256'};cells={key:float(value['median_ms']) for key,value in ep_cells.items()};ep_n=json.loads(show(a.repo,'NCU_SUMMARY.json'))['profiles'];ep_kernels=list(csv.DictReader(io.StringIO(show(a.repo,'NCU_KERNEL_ROWS.tsv')),delimiter='\t'));ep_reduction=sum(int(r['dram_bytes']) for r in ep_kernels if r['track']=='W4' and r['point']=='EXPAND_M256' and r['cell']=='A_W' and r['kernel_kind']=='REDUCTION');full=12288*25536;split8=12288*3552
 series.append({'point':'K12288','K':12288,'source':'ACCEPTED_ENDPOINT_1544018D','full_w4_bytes':full,'full_over_l2':full/L2_BYTES,'split8_static_bytes':split8,'A_median_ms':cells['A_W'],'A_cv':float(ep_cells['A_W']['cv']),'B_median_ms':cells['B_W'],'B_cv':float(ep_cells['B_W']['cv']),'split1_gain':1-cells['B_W']/cells['A_W'],'A_dram_bytes':ep_n['W4:EXPAND_M256:A_W']['dram_bytes_total'],'B_dram_bytes':ep_n['W4:EXPAND_M256:B_W']['dram_bytes_total'],'B_over_A_dram':ep_n['W4:EXPAND_M256:B_W']['dram_bytes_total']/ep_n['W4:EXPAND_M256:A_W']['dram_bytes_total'],'A_reduction_dram_bytes':ep_reduction})
 tsv(a.out/'CORRECTNESS.tsv',['point','K','a_sha256','b_sha256','shape','dtype','all_finite','max_abs','mean_abs','relative_l2','changed_element_count','element_count','rtol','atol','pass'],correct)
 tsv(a.out/'LAUNCH_AUDIT.tsv',['point','arm','order','kernel_kind','kernel_name','grid','block','registers_per_thread','static_shared_bytes','dynamic_shared_bytes','scratch_shape','scratch_bytes','reduction_expected','pass'],launch['rows'])
 tsv(a.out/'TIMING_SAMPLES.tsv',['point','K','arm','block','position','sample_in_arm','ms'],samples);tsv(a.out/'TIMING_SUMMARY.tsv',['point','K','arm','n','min_ms','median_ms','max_ms','mean_ms','cv'],rows)
 tsv(a.out/'NCU_KERNEL_ROWS.tsv',['point','K','arm','kernel_order','kernel_kind','kernel_name','grid_size','block_size','l1tex_bytes','lts_bytes','dram_bytes','duration_ns','registers_per_thread','static_shared_bytes','dynamic_shared_bytes','l1tex_unit','lts_unit','dram_unit','duration_unit'],ncu)
 dump(a.out/'NCU_SUMMARY.json',{'status':'PASS','profiles':{f'K{k}:{arm}':v for (k,arm),v in ncu_summary.items()},'contract':{'profiles':8,'replay_mode':'application','cache_control':'none','metrics':['l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum','gpu__time_duration.sum'],'tensor_attribution':'FORBIDDEN'}});tsv(a.out/'K_THRESHOLD_SERIES.tsv',['point','K','source','full_w4_bytes','full_over_l2','split8_static_bytes','A_median_ms','A_cv','B_median_ms','B_cv','split1_gain','A_dram_bytes','B_dram_bytes','B_over_A_dram','A_reduction_dram_bytes'],series)
 source_commit=(a.raw/'PRODUCER_SOURCE_COMMIT.txt').read_text().strip();manifest=load(a.out/'SOURCE_AND_RUN_MANIFEST.json');manifest.update({'status':'PASS_COMPLETED','producer_source_commit':source_commit,'static_gate_binding_sha256':sha(a.out/'STATIC_GATE_BINDING.json'),'timing_samples':400,'ncu_profiles':8});dump(a.out/'SOURCE_AND_RUN_MANIFEST.json',manifest)
 dump(a.out/'GPU_LOCK_RECEIPT.json',{'status':'PASS','lock_path':'/data/c16/locks/c16_gpu_campaign.lock','start_utc':(a.raw/'GPU_LOCK_START_UTC.txt').read_text().strip(),'end_utc':(a.raw/'GPU_LOCK_END_UTC.txt').read_text().strip(),'gpu_identity':(a.raw/'GPU_IDENTITY.txt').read_text().strip(),'producer_source_commit':source_commit,'release':'RELEASED_BEFORE_CPU_ANALYSIS','nvidia_smi_pre_sha256':sha(a.raw/'NVIDIA_SMI_PRE.txt'),'nvidia_smi_post_sha256':sha(a.raw/'NVIDIA_SMI_POST.txt')})
 lines=['# 科学解释（producer描述性）','', '固定M=256、N=49152，仅改变K；所有新K的grid、scratch与reduction合同相同。K=12288直接引用accepted endpoint，未重跑。','']
 for r in series:lines.append(f"- K={r['K']}：full/L2={r['full_over_l2']:.3f}，split1 gain={100*r['split1_gain']:.3f}%，B/A DRAM={r['B_over_A_dram']:.3f}。")
 lines+=['','重点的K2560(<L2)与K3072(>L2)之间趋势只作描述；是否支持容量工作集机制由Lane6独立consumer重算。这里不声称硬64MiB阈值、具体tensor归因或唯一L2因果，也不自动触发SASS/Accel-Sim。',''];(a.out/'SCIENTIFIC_INTERPRETATION.md').write_text('\n'.join(lines))
 dump(a.out/'FINAL_DECISION.json',{'decision':'PRODUCER_THRESHOLD_SERIES_PASS_PENDING_LANE6','run_id':a.raw.parent.name,'new_K':list(KS),'accepted_endpoint_K':12288,'correctness':'PASS_ALL_NEW_K','launch':'PASS_ALL_NEW_K','timing_samples':400,'ncu_profiles':8,'automatic_sass_or_simulation':False,'claim_boundary':'GPT-3 public-shape W4 mechanism proxy; fixed M/N/split/state; descriptive threshold trend only'})
 (a.out/'NEXT_174_CONSUMER_CONTRACT.md').write_text(f"# Lane6 threshold consumer contract\n\n- RUN_ID: `{a.raw.parent.name}`\n- producer source commit: `{source_commit}`\n- producer science commit: `TO_BE_BOUND`\n- new K rows: 2048,2560,3072,4096; accepted endpoint K=12288 from `{ENDPOINT}`\n- recompute correctness, launch, timing, NCU and K threshold series directly; producer interpretation is not calculation authority\n- no automatic SASS or Accel-Sim\n")
 (a.out/'README.md').write_text(f"# Split-K footprint threshold native producer\n\nRUN_ID: `{a.raw.parent.name}`\n\nStatus: `PRODUCER_THRESHOLD_SERIES_PASS_PENDING_LANE6`; four new K values, 400 samples and eight NCU profiles.\n")
 for pth in sorted(a.raw.glob('ncu_*.csv')):shutil.copy2(pth,a.out/f'RAW_{pth.name}')
 raw=[]
 for pth in sorted(a.raw.rglob('*')):
  if pth.is_file() and pth.name!='RAW_MANIFEST.json':raw.append({'artifact':pth.relative_to(a.raw).as_posix(),'path':str(pth),'bytes':pth.stat().st_size,'sha256':sha(pth),'committed_copy':f'RAW_{pth.name}' if pth.name.startswith('ncu_') and pth.suffix=='.csv' else 'INDEX_ONLY'})
 tsv(a.out/'RAW_INDEX.tsv',['artifact','path','bytes','sha256','committed_copy'],raw);print(json.dumps({'status':'PASS_ANALYSIS','series_rows':len(series),'samples':len(samples),'ncu_profiles':8,'source_commit':source_commit}))
if __name__=='__main__':main()
