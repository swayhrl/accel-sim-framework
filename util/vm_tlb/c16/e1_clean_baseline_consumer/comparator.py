#!/usr/bin/env python3
"""Independent CPU consumer for C16 E1 clean-baseline timing evidence."""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import defaultdict
from pathlib import Path

IMPL=('RAW_BF16','RAW_FP16','AWQ_FP16_INPUT')
class ContractError(ValueError): pass
def stats(values):
 if not values or any(not math.isfinite(x) or x<=0 for x in values):raise ContractError('nonpositive/nonfinite timing sample')
 mean=statistics.fmean(values);return {'min_ms':min(values),'median_ms':statistics.median(values),'max_ms':max(values),'mean_ms':mean,'cv':statistics.pstdev(values)/mean,'sample_count':len(values)}
def samples(row):
 raw=row.get('timing_samples_ms',row.get('samples_ms',''))
 if isinstance(raw,list):return [float(x) for x in raw]
 try:return [float(x) for x in json.loads(raw)]
 except json.JSONDecodeError:return [float(x) for x in raw.split(',') if x]
def canonical_rows(rows):
 out=[]
 for row in rows:
  role=row.get('role',''); m=int(row.get('M','')); impl=row.get('implementation','')
  if not role or m not in (1,256) or impl not in IMPL:raise ContractError('invalid role/M/implementation')
  item={'role':role,'M':m,'implementation':impl,'activation_sha256':row.get('activation_sha256',''),'activation_dtype':row.get('activation_dtype',''),'weight_dtype':row.get('weight_dtype',''),'path_fingerprint':row.get('path_fingerprint',''),'samples':samples(row)}
  if not item['activation_sha256'] or not item['path_fingerprint']:raise ContractError('missing activation SHA/path fingerprint')
  item.update(stats(item.pop('samples')));out.append(item)
 return out
def analyze(rows,authority_regeneration_pass):
 if authority_regeneration_pass is not True:raise ContractError('authority regeneration not PASS')
 rows=canonical_rows(rows); groups={(r['role'],r['M'],r['implementation']):r for r in rows}
 expected={(r['role'],m,i) for r in rows for m in (1,256) for i in IMPL}
 if set(groups)!=expected:raise ContractError('matrix incomplete/duplicate')
 ratios=[]; interactions=[]; materials={}
 for role in sorted({r['role'] for r in rows}):
  awq_by_m={}
  for m in (1,256):
   bf,fp,aw=(groups[role,m,i] for i in IMPL)
   if fp['activation_sha256']!=aw['activation_sha256'] or fp['activation_dtype']!='FP16' or aw['activation_dtype']!='FP16':raise ContractError('RAW_FP16/AWQ activation-byte contract failure')
   if bf['activation_dtype']!='BF16' or bf['weight_dtype']!='BF16' or fp['weight_dtype']!='FP16':raise ContractError('RAW dtype identity failure')
   rd=fp['median_ms']/bf['median_ms'];ra=aw['median_ms']/fp['median_ms'];effect=abs(ra-1);disp=math.sqrt(fp['cv']**2+aw['cv']**2);mat=effect>=.05 and effect>disp
   ratios.append({'role':role,'M':m,'R_dtype':rd,'R_awq':ra,'awq_effect_abs':effect,'pair_dispersion':disp,'material_awq_effect':mat});awq_by_m[m]=ra;materials[m]=mat
  interaction=math.log(awq_by_m[256])-math.log(awq_by_m[1]);interactions.append({'role':role,'R_awq_M1':awq_by_m[1],'R_awq_M256':awq_by_m[256],'interaction_I':interaction,'abs_I':abs(interaction),'passes_materiality_any_M':materials[1] or materials[256]})
 eligible=[x for x in interactions if x['passes_materiality_any_M']]
 selected=max(eligible,key=lambda x:x['abs_I'])['role'] if eligible else None
 return {'status':'PASS','point_statistics':rows,'ratios':ratios,'interactions':interactions,'ncu_selection':{'selected_role':selected,'rule':'max abs(I) among roles with a material AWQ-vs-RAW_FP16 effect','ncu_entry_eligible':selected is not None},'materiality_rule':{'median_effect_at_least':.05,'strictly_greater_than_combined_pair_cv':True}}
def load_tsv(path):
 with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--timing-tsv',type=Path,required=True);p.add_argument('--authority-regeneration',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(); regen=json.loads(a.authority_regeneration.read_text()).get('status')=='PASS';result=analyze(load_tsv(a.timing_tsv),regen);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','selected_role':result['ncu_selection']['selected_role']}))
if __name__=='__main__':main()
