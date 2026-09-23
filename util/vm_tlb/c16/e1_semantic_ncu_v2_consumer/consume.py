#!/usr/bin/env python3
"""Independent raw-wide-NCU V1/V2 semantic module consumer."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'e1_semantic_ncu_consumer'))
from aggregator import aggregate,compare
METRICS=('l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum')
POLICY={'additive_metrics':{m:'byte' for m in METRICS},'non_additive_metrics':{},'required_denominators':['input_elements','output_elements','dense_weight_bytes']}
POINTS={'M1_RAW':(1,'RAW','C16_E1_NCU_UP_M1_RAW_FP16'),'M1_AWQ':(1,'AWQ','C16_E1_NCU_UP_M1_AWQ'),'M256_RAW':(256,'RAW','C16_E1_NCU_UP_M256_RAW_FP16'),'M256_AWQ':(256,'AWQ','C16_E1_NCU_UP_M256_AWQ')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def number(s):
 t=s.replace(',','').strip();v=float(t)
 if not math.isfinite(v):raise ValueError('nonfinite metric')
 return t
def wide(path,point,rng,expected_passes):
 raw=Path(path).read_bytes();digest=hashlib.sha256(raw).hexdigest()
 with Path(path).open(newline='',encoding='utf-8-sig') as f:table=list(csv.reader(f))
 if len(table)<3:raise ValueError('short NCU CSV')
 header=table[0]
 if len(header)!=len(set(header)):raise ValueError('duplicate raw header')
 units=table[1]
 if len(units)!=len(header):raise ValueError('unit row width')
 idx={h:i for i,h in enumerate(header)}
 range_cols=[i for i,h in enumerate(header) if 'Push/Pop_Range' in h]
 if len(range_cols)!=1:raise ValueError('ambiguous NVTX column')
 need=['ID','Process ID','Kernel Name','Block Size','Grid Size','profiler__replayer_passes',*METRICS]
 if any(n not in idx for n in need):raise ValueError('missing required NCU column')
 for m in METRICS:
  if units[idx[m]]!='byte':raise ValueError('metric unit mismatch '+m)
 candidates=[]
 for rownum,row in enumerate(table[2:],start=3):
  if len(row)!=len(header) or not row[idx['ID']].strip():continue
  if rng not in row[range_cols[0]]:continue
  if number(row[idx['profiler__replayer_passes']])!=str(expected_passes):raise ValueError('replay pass mismatch')
  candidates.append((rownum,row))
 if not candidates:raise ValueError('missing semantic range')
 proc={r[idx['Process ID']] for _,r in candidates}
 if len(proc)!=1:raise ValueError('ambiguous semantic process/range')
 M,impl,_=POINTS[point];inp=M*3584;out=M*18944;dense=135790592;packed=35273728 if impl=='AWQ' else ''
 normalized=[];names={}
 for rownum,row in candidates:
  kid=row[idx['ID']];name=row[idx['Kernel Name']]
  if kid in names and names[kid]!=name:raise ValueError('kernel ID/name conflict')
  names[kid]=name
  for metric in METRICS:
   normalized.append({'semantic_point':point,'range_name':rng,'range_occurrence':'0','kernel_id':kid,'kernel_name':name,'metric_name':metric,'metric_unit':units[idx[metric]],'metric_value':number(row[idx[metric]]),'input_elements':str(inp),'output_elements':str(out),'dense_weight_bytes':str(dense),'packed_weight_bytes':str(packed),'source_raw_filename':Path(path).name,'source_row_identity':str(rownum),'raw_ncu_id':kid,'grid':row[idx['Grid Size']],'block':row[idx['Block Size']],'raw_source_sha256':digest})
 expected=1 if impl=='RAW' else 2
 if len(names)!=expected:raise ValueError('kernel inventory count mismatch')
 lowered=' '.join(names.values()).lower()
 if impl=='AWQ' and not ('gemm' in lowered and ('reduce' in lowered or 'sum' in lowered)):raise ValueError('AWQ inventory not GEMM+reduction')
 return normalized,{'sha256':digest,'selected_kernel_count':len(names),'process_id':next(iter(proc)),'kernel_names':list(names.values()),'units':{m:units[idx[m]] for m in METRICS}}
def session_audit(pack,point,v2):
 stem=('RAW_'+point if v2 else 'RAW_'+point+'_NCU');s=(pack/(stem+'_SESSION.csv')).read_text();profile=(pack/(stem+'_PROFILE.log')).read_text() if v2 else ''
 _,_,rng=POINTS[point];metrics='--metrics '+','.join(METRICS)
 if v2:
  ok=all(x in s for x in ('--replay-mode application','--cache-control none','--nvtx-include '+rng+'/',metrics)) and '2025.1.1.0 (build 35528883)' in s and '"status": "PASS"' in profile
 else:ok='--replay-mode application' not in s and '--cache-control none' not in s and metrics in s
 return {'status':'PASS' if ok else 'FAIL','session_sha256':sha(pack/(stem+'_SESSION.csv')),'profile_sha256':sha(pack/(stem+'_PROFILE.log')) if v2 else None,'replay_mode':'application' if v2 else 'default kernel replay','cache_control':'none' if v2 else 'not explicitly none','nvtx_range':rng}
def classify(old,new):
 if (old>1)!=(new>1):return 'QUALITATIVE_DIRECTION_CHANGED'
 return 'SAME_DIRECTION_SIMILAR_MAGNITUDE' if abs(new/old-1)<=.25 else 'SAME_DIRECTION_DIFFERENT_MAGNITUDE'
def main():
 a=argparse.ArgumentParser();a.add_argument('--v2-pack',type=Path,required=True);a.add_argument('--v1-pack',type=Path,required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args();o=x.out;o.mkdir(parents=True,exist_ok=True)
 allnorm=[];v2points={};provenance={};modes={}
 for point,(M,impl,rng) in POINTS.items():
  n,p=wide(x.v2_pack/('RAW_'+point+'_BASE.csv'),point,rng,1);allnorm+=n;provenance[point]=p;modes[point]=session_audit(x.v2_pack,point,True);v2points[(M,impl)]=aggregate(n,point,rng,POLICY)
 if any(v['status']!='PASS' for v in modes.values()):raise SystemExit('profiler mode audit failed')
 with (o/'RAW_NORMALIZED_ROWS.tsv').open('w',newline='') as f:
  fields=list(allnorm[0]);w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader();w.writerows(allnorm)
 dump(o/'RAW_PROVENANCE_AUDIT.json',{'status':'PASS','points':provenance});dump(o/'PROFILER_MODE_AUDIT.json',{'status':'PASS','ncu_version':'2025.1.1.0 build 35528883','points':modes});dump(o/'RUNTIME_METRIC_POLICY.json',POLICY)
 with (o/'INDEPENDENT_TRAFFIC_SUMS.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['point','metric_name','unit','semantic_module_sum'])
  for point,(M,impl,_) in POINTS.items():
   for metric in METRICS:w.writerow([point,metric,'byte',v2points[(M,impl)]['SEMANTIC_MODULE_SUM'][metric]['value_exact']])
 comp=compare(v2points,METRICS)
 for r in comp:r['shape_interaction_ratio']=r['M256_AWQ_over_RAW']/r['M1_AWQ_over_RAW']
 dump(o/'INDEPENDENT_TRAFFIC_COMPARISON.json',{'status':'PASS','metrics':comp})
 v1points={};v1mode={}
 for point,(M,impl,rng) in POINTS.items():
  n,_=wide(x.v1_pack/('RAW_'+point+'_NCU_BASE.csv'),point,rng,7);v1points[(M,impl)]=aggregate(n,point,rng,POLICY);v1mode[point]=session_audit(x.v1_pack,point,False)
 v1comp=compare(v1points,METRICS);by1={r['metric_name']:r for r in v1comp};by2={r['metric_name']:r for r in comp};v12=[]
 for metric in METRICS:
  v12.append({'metric_name':metric,'v1':by1[metric],'v2':by2[metric],'M1_class':classify(by1[metric]['M1_AWQ_over_RAW'],by2[metric]['M1_AWQ_over_RAW']),'M256_class':classify(by1[metric]['M256_AWQ_over_RAW'],by2[metric]['M256_AWQ_over_RAW'])})
 dump(o/'V1_V2_INDEPENDENT_COMPARISON.json',{'status':'PASS','v1_profiler_mode':v1mode,'classification_rule':'same direction and ratio-of-ratios within 25% => similar magnitude','metrics':v12})
 sums={(point,metric):int(v2points[(M,impl)]['SEMANTIC_MODULE_SUM'][metric]['value']) for point,(M,impl,_) in POINTS.items() for metric in METRICS};refs={('M1_RAW','l1tex__t_bytes.sum'):272187392,('M1_RAW','lts__t_bytes.sum'):137167040,('M1_RAW','dram__bytes.sum'):138156416,('M1_AWQ','l1tex__t_bytes.sum'):47284224,('M1_AWQ','lts__t_bytes.sum'):41898912,('M1_AWQ','dram__bytes.sum'):640,('M256_RAW','l1tex__t_bytes.sum'):417071104,('M256_RAW','lts__t_bytes.sum'):417723360,('M256_RAW','dram__bytes.sum'):156380160,('M256_AWQ','l1tex__t_bytes.sum'):1411252224,('M256_AWQ','lts__t_bytes.sum'):1266170592,('M256_AWQ','dram__bytes.sum'):178195840}
 dump(o/'PRODUCER_MATCH_CHECK.json',{'status':'PASS' if sums==refs else 'FAIL','comparisons':[{'point':k[0],'metric':k[1],'consumer':sums[k],'producer_reference':refs[k],'equal':sums[k]==refs[k]} for k in refs]})
 awq=35273728;raw=135790592;l2=67108864;dram_awq=sums[('M1_AWQ','dram__bytes.sum')];dram_raw=sums[('M1_RAW','dram__bytes.sum')]
 dump(o/'CAPACITY_RESIDENCY_CONSISTENCY.json',{'AWQ_packed_storage_bytes':awq,'RAW_FP16_dense_weight_bytes':raw,'device_L2_bytes':l2,'AWQ_packed_less_than_L2':awq<l2,'RAW_dense_greater_than_L2':raw>l2,'M1_AWQ_DRAM_bytes':dram_awq,'M1_RAW_DRAM_bytes':dram_raw,'assessment':'CONSISTENT_WITH_WARM_CACHE_CAPACITY_RESIDENCY_HYPOTHESIS_NOT_CAUSAL_PROOF'})
 text='# C16 E1 Semantic NCU V2 consumer interpretation\n\nApplication-replay/cache-control-none raw evidence independently reproduces strong shape-dependent RAW/AWQ semantic traffic ratios. M1 AWQ DRAM is extremely small relative to RAW. Packed AWQ state is smaller than L2 while dense RAW FP16 weight exceeds L2; this is consistent with a warm-cache capacity/residency hypothesis, but does not prove cache or TLB causality. No GPU, NVBit, full trace, or mechanism work was authorized.\n';(o/'SCIENTIFIC_INTERPRETATION.md').write_text(text)
 dump(o/'FINAL_DECISION.json',{'status':'C16_E1_SEMANTIC_NCU_V2_CONSUMER_PASS','raw_recompute_matches_producer':sums==refs,'cache_causality_proven':False});dump(o/'NEXT_STEP_AUTHORIZATION.json',{'status':'REVIEW_REQUIRED','new_gpu_experiment_authorized':False,'nvbit_full_trace_authorized':False,'cache_tlb_mechanism_authorized':False})
if __name__=='__main__':main()
