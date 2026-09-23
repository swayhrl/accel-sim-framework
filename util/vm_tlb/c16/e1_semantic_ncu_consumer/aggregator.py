#!/usr/bin/env python3
"""Fail-closed semantic-range NCU CSV parser and module aggregator."""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
class AggregationError(ValueError):pass
FIELDS={'semantic_point','range_name','range_occurrence','kernel_id','kernel_name','metric_name','metric_unit','metric_value','input_elements','output_elements','dense_weight_bytes','packed_weight_bytes'}
def read_csv(path):
 with Path(path).open(newline='',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f);missing=FIELDS-set(reader.fieldnames or ())
  if missing:raise AggregationError('missing columns: '+','.join(sorted(missing)))
  return list(reader)
def aggregate(rows,point,target_range,policy):
 candidates=[r for r in rows if r['semantic_point']==point and r['range_name']==target_range]
 if not candidates:raise AggregationError('missing target range')
 occurrences={r['range_occurrence'] for r in candidates}
 if len(occurrences)!=1:raise AggregationError('ambiguous target range occurrence')
 if '' in occurrences:raise AggregationError('missing range occurrence')
 allowed=set(policy['additive_metrics'])|set(policy['non_additive_metrics'])
 kernels=defaultdict(lambda:{'kernel_name':None,'metrics':{}});units={}
 for r in candidates:
  metric=r['metric_name'];unit=r['metric_unit']
  if metric not in allowed:raise AggregationError('unclassified metric '+metric)
  expected=policy['additive_metrics'].get(metric,policy['non_additive_metrics'].get(metric))
  if unit!=expected:raise AggregationError('unit mismatch '+metric+': '+unit+' != '+expected)
  if metric in units and units[metric]!=unit:raise AggregationError('inconsistent unit '+metric)
  units[metric]=unit;key=(r['kernel_id'],r['kernel_name']);k=kernels[key];k['kernel_name']=r['kernel_name']
  if metric in k['metrics']:raise AggregationError('duplicate kernel metric row')
  try:value=float(r['metric_value'])
  except ValueError as exc:raise AggregationError('invalid metric value') from exc
  k['metrics'][metric]={'value':value,'unit':unit}
 dims={name:{int(r[name]) for r in candidates if r[name]!=''} for name in ('input_elements','output_elements','dense_weight_bytes','packed_weight_bytes')}
 if any(len(v)>1 for v in dims.values()):raise AggregationError('inconsistent normalization denominator')
 denom={k:(next(iter(v)) if v else None) for k,v in dims.items()}
 sums={}
 for metric,unit in policy['additive_metrics'].items():
  values=[k['metrics'][metric]['value'] for k in kernels.values() if metric in k['metrics']]
  if len(values)!=len(kernels):raise AggregationError('missing additive metric on kernel '+metric)
  total=sum(values);norm={'per_input_element':total/denom['input_elements'] if denom['input_elements'] else None,'per_output_element':total/denom['output_elements'] if denom['output_elements'] else None,'per_dense_weight_byte':total/denom['dense_weight_bytes'] if denom['dense_weight_bytes'] else None,'per_packed_weight_byte':total/denom['packed_weight_bytes'] if denom['packed_weight_bytes'] else None};sums[metric]={'value':total,'unit':unit,'normalization':norm}
 nonadd={metric:[{'kernel_id':kid,'kernel_name':name,'value':k['metrics'][metric]['value'],'unit':k['metrics'][metric]['unit']} for (kid,name),k in kernels.items() if metric in k['metrics']] for metric in policy['non_additive_metrics']}
 return {'status':'PASS','semantic_point':point,'range_name':target_range,'range_occurrence':next(iter(occurrences)),'kernel_count':len(kernels),'kernels':[{'kernel_id':kid,'kernel_name':name,'metrics':k['metrics']} for (kid,name),k in kernels.items()],'SEMANTIC_MODULE_SUM':sums,'non_additive_per_kernel':nonadd,'denominators':denom}
def compare(points,metrics):
 out=[]
 for metric in metrics:
  value=lambda m,impl:points[(m,impl)]['SEMANTIC_MODULE_SUM'][metric]['value']
  out.append({'metric_name':metric,'M1_AWQ_over_RAW':value(1,'AWQ')/value(1,'RAW'),'M256_AWQ_over_RAW':value(256,'AWQ')/value(256,'RAW'),'RAW_M256_over_M1':value(256,'RAW')/value(1,'RAW'),'AWQ_M256_over_M1':value(256,'AWQ')/value(1,'AWQ')})
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--csv',type=Path,required=True);p.add_argument('--policy',type=Path,required=True);p.add_argument('--point',required=True);p.add_argument('--range',dest='target',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=aggregate(read_csv(a.csv),a.point,a.target,json.loads(a.policy.read_text()));a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','kernels':result['kernel_count']}))
if __name__=='__main__':main()
