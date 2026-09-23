#!/usr/bin/env python3
"""Independent exact-byte census from tensor metadata; no geometry inference."""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
class CapacityError(ValueError):pass
ROLES=('q_proj','down_proj','up_proj')
def tensor_bytes(t):
 name=str(t.get('name','')).strip();shape=t.get('shape');size=t.get('element_size')
 if not name:raise CapacityError('empty tensor name')
 if not isinstance(shape,list) or not shape or any(not isinstance(x,int) or x<=0 for x in shape):raise CapacityError('invalid shape '+name)
 if not isinstance(size,int) or size<=0:raise CapacityError('invalid element_size '+name)
 return math.prod(shape)*size
def group(ts,label):
 if not isinstance(ts,list) or not ts:raise CapacityError('missing '+label)
 names=[str(x.get('name','')).strip() for x in ts]
 if len(names)!=len(set(names)):raise CapacityError('duplicate tensor '+label)
 return {x['name']:tensor_bytes(x) for x in ts}
def census(doc):
 if not isinstance(doc,dict) or not isinstance(doc.get('device_l2_bytes'),int) or doc['device_l2_bytes']<=0:raise CapacityError('invalid device_l2_bytes')
 if set(doc.get('roles',{}))!=set(ROLES):raise CapacityError('roles must be q/down/up exactly')
 rows=[]
 for role in ROLES:
  r=doc['roles'][role];raw=group(r.get('raw_fp16'),'raw_fp16');awq=group(r.get('awq_state_dict'),'awq_state_dict')
  if 'weight' not in raw:raise CapacityError('RAW weight missing '+role)
  if not {'qweight','qzeros','scales'}<=set(awq):raise CapacityError('AWQ required state missing '+role)
  if any(str(x.get('dtype'))!='torch.float16' for x in r['raw_fp16']):raise CapacityError('RAW dtype mismatch '+role)
  raw_weight=raw['weight'];raw_bias=sum(v for k,v in raw.items() if k!='weight');raw_total=sum(raw.values());awq_total=sum(awq.values());l2=doc['device_l2_bytes']
  rows.append({'role':role,'raw_weight_bytes':raw_weight,'raw_bias_bytes':raw_bias,'raw_total_bytes':raw_total,'awq_state_dict_bytes':awq_total,'device_l2_bytes':l2,'raw_vs_l2':'LT' if raw_total<l2 else 'EQ' if raw_total==l2 else 'GT','awq_vs_l2':'LT' if awq_total<l2 else 'EQ' if awq_total==l2 else 'GT','awq_components':awq})
 return rows
def main():
 p=argparse.ArgumentParser();p.add_argument('--metadata',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=census(json.loads(a.metadata.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True)
 fields=['role','raw_weight_bytes','raw_bias_bytes','raw_total_bytes','awq_state_dict_bytes','device_l2_bytes','raw_vs_l2','awq_vs_l2','awq_components']
 with a.output.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows({**r,'awq_components':json.dumps(r['awq_components'],sort_keys=True)} for r in rows)
if __name__=='__main__':main()
