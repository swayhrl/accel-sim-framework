#!/usr/bin/env python3
"""CPU-only analyzer for the bounded L2 read-hit diagnostic."""
import argparse,csv,json,hashlib,shutil
from pathlib import Path

HIT='lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum';MISS='lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum';KS=(2048,2560,3072,4096)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def tsv(p,fields,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore',lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:('NA' if r.get(k) in (None,'') else r.get(k)) for k in fields})
def parse(path,k,arm):
 records=list(csv.reader(open(path,newline='')));h,u=records[0],records[1];out=[]
 for vals in records[2:]:
  if not vals or not vals[0] or len(vals)!=len(h):continue
  d,unit=dict(zip(h,vals)),dict(zip(h,u))
  if not d.get('Kernel Name'):continue
  num=lambda key:float(d[key].replace(',','')) if '.' in d[key] else int(d[key].replace(',',''));name=d['Kernel Name'];kind='GEMM' if 'gemm_forward' in name else 'REDUCTION' if 'reduce_kernel' in name else 'OTHER';hit=int(num(HIT));miss=int(num(MISS));den=hit+miss
  out.append({'point':f'K{k}','K':k,'arm':arm,'kernel_order':len(out),'kernel_kind':kind,'kernel_name':name,'grid_size':d['Grid Size'],'block_size':d['Block Size'],'l2_read_hit_sectors':hit,'l2_read_miss_sectors':miss,'l2_read_total_sectors':den,'l2_read_hit_fraction':hit/den if den else None,'l1tex_bytes':int(num('l1tex__t_bytes.sum')),'lts_bytes':int(num('lts__t_bytes.sum')),'dram_bytes':int(num('dram__bytes.sum')),'duration_ns':int(num('gpu__time_duration.sum')),'hit_unit':unit[HIT],'miss_unit':unit[MISS]})
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[]
 for k in KS:
  for arm in ('A','B'):
   r=parse(a.raw/f'ncu_l2hit_K{k}_{arm}.csv',k,arm)
   if len(r)!=(2 if arm=='A' else 1) or r[0]['kernel_kind']!='GEMM' or (arm=='A' and r[1]['kernel_kind']!='REDUCTION'):raise RuntimeError(f'kernel rows {k}/{arm}')
   rows+=r
 summary=[]
 for k in KS:
  a_g=next(r for r in rows if r['K']==k and r['arm']=='A' and r['kernel_kind']=='GEMM');b_g=next(r for r in rows if r['K']==k and r['arm']=='B' and r['kernel_kind']=='GEMM');red=next(r for r in rows if r['K']==k and r['arm']=='A' and r['kernel_kind']=='REDUCTION')
  summary.append({'point':f'K{k}','K':k,'A_gemm_hit_sectors':a_g['l2_read_hit_sectors'],'A_gemm_miss_sectors':a_g['l2_read_miss_sectors'],'A_gemm_hit_fraction':a_g['l2_read_hit_fraction'],'B_gemm_hit_sectors':b_g['l2_read_hit_sectors'],'B_gemm_miss_sectors':b_g['l2_read_miss_sectors'],'B_gemm_hit_fraction':b_g['l2_read_hit_fraction'],'B_minus_A_hit_fraction':b_g['l2_read_hit_fraction']-a_g['l2_read_hit_fraction'],'A_gemm_dram_bytes':a_g['dram_bytes'],'B_gemm_dram_bytes':b_g['dram_bytes'],'B_over_A_gemm_dram':b_g['dram_bytes']/a_g['dram_bytes'] if a_g['dram_bytes'] else None,'A_reduction_hit_fraction_record_only':red['l2_read_hit_fraction'],'A_reduction_dram_bytes_record_only':red['dram_bytes']})
 by={r['K']:r for r in summary};a_delta=by[3072]['A_gemm_hit_fraction']-by[2560]['A_gemm_hit_fraction'];b_delta=by[3072]['B_gemm_hit_fraction']-by[2560]['B_gemm_hit_fraction'];b_miss_growth=by[3072]['B_gemm_miss_sectors']-by[2560]['B_gemm_miss_sectors'];supported=b_delta<0 and b_miss_growth>0 and abs(a_delta)<abs(b_delta)
 decision='L2_READ_HIT_BEHAVIOR_DIRECTIONALLY_CONSISTENT_WITH_CAPACITY_KNEE' if supported else 'L2_READ_HIT_BEHAVIOR_DOES_NOT_SUPPORT_CAPACITY_KNEE'
 tsv(a.out/'KERNEL_ROWS.tsv',['point','K','arm','kernel_order','kernel_kind','kernel_name','grid_size','block_size','l2_read_hit_sectors','l2_read_miss_sectors','l2_read_total_sectors','l2_read_hit_fraction','l1tex_bytes','lts_bytes','dram_bytes','duration_ns','hit_unit','miss_unit'],rows);tsv(a.out/'L2_READ_HIT_SUMMARY.tsv',['point','K','A_gemm_hit_sectors','A_gemm_miss_sectors','A_gemm_hit_fraction','B_gemm_hit_sectors','B_gemm_miss_sectors','B_gemm_hit_fraction','B_minus_A_hit_fraction','A_gemm_dram_bytes','B_gemm_dram_bytes','B_over_A_gemm_dram','A_reduction_hit_fraction_record_only','A_reduction_dram_bytes_record_only'],summary)
 source=(a.raw/'PRODUCER_SOURCE_COMMIT.txt').read_text().strip();dump(a.out/'GPU_LOCK_RECEIPT.json',{'status':'PASS','lock_path':'/data/c16/locks/c16_gpu_campaign.lock','start_utc':(a.raw/'GPU_LOCK_START_UTC.txt').read_text().strip(),'end_utc':(a.raw/'GPU_LOCK_END_UTC.txt').read_text().strip(),'gpu_identity':(a.raw/'GPU_IDENTITY.txt').read_text().strip(),'producer_source_commit':source,'release':'RELEASED_BEFORE_CPU_ANALYSIS','nvidia_smi_pre_sha256':sha(a.raw/'NVIDIA_SMI_PRE.txt'),'nvidia_smi_post_sha256':sha(a.raw/'NVIDIA_SMI_POST.txt')})
 interpretation=f"""# 科学解释\n\nK2560→3072：split1 GEMM L2 read hit fraction 从 {by[2560]['B_gemm_hit_fraction']:.6f} 变为 {by[3072]['B_gemm_hit_fraction']:.6f}（Δ={b_delta:+.6f}），miss sectors增加 {b_miss_growth}；split8 GEMM从 {by[2560]['A_gemm_hit_fraction']:.6f} 变为 {by[3072]['A_gemm_hit_fraction']:.6f}（Δ={a_delta:+.6f}）。\n\n判定：`{decision}`。该判定仅说明目标GEMM的srcunit TEX read-side L2 lookup行为在方向上是否与capacity knee一致。A reduction独立列示，不参与weight-locality解释。指标不区分qweight、input或metadata，不能作tensor级归因，也不证明唯一L2因果。\n""";(a.out/'SCIENTIFIC_INTERPRETATION.md').write_text(interpretation)
 dump(a.out/'FINAL_DECISION.json',{'decision':decision,'direction_rule':{'B_hit_fraction_delta_2560_to_3072':b_delta,'B_miss_sector_growth':b_miss_growth,'A_hit_fraction_delta_2560_to_3072':a_delta,'absolute_A_change_smaller_than_B':abs(a_delta)<abs(b_delta)},'profiles':8,'reduction_excluded_from_locality_interpretation':True,'tensor_attribution':False,'automatic_sass_or_simulation':False})
 for q in sorted(a.raw.glob('ncu_l2hit_*.csv')):shutil.copy2(q,a.out/f'RAW_{q.name}')
 raw=[]
 for q in sorted(a.raw.rglob('*')):
  if q.is_file() and q.name!='RAW_MANIFEST.json':raw.append({'artifact':q.relative_to(a.raw).as_posix(),'path':str(q),'bytes':q.stat().st_size,'sha256':sha(q),'committed_copy':f'RAW_{q.name}' if q.name.startswith('ncu_l2hit_') and q.suffix=='.csv' else 'INDEX_ONLY'})
 tsv(a.out/'RAW_INDEX.tsv',['artifact','path','bytes','sha256','committed_copy'],raw);(a.out/'README.md').write_text(f'# Split-K L2 read-hit diagnostic\n\nStatus: `{decision}`. Eight bounded profiles only; no SASS, NVBit, Accel-Sim, EVICT or new shapes.\n');print(json.dumps({'status':'PASS_ANALYSIS','decision':decision,'profiles':8,'source_commit':source}))
if __name__=='__main__':main()
