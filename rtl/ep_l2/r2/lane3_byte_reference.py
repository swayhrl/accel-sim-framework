#!/usr/bin/env python3
"""Independent byte-address value/snapshot oracle for an external RTL adapter.

No import from simulator, payload store, stimulus generator, or RTL. Observed
protocol assertions are deliberately NOT simulated/proven by this reference.
"""
import argparse,hashlib,json
from pathlib import Path
class ByteReference:
 def __init__(self,base,data):self.memory={base+i:v for i,v in enumerate(data)};self.snapshots={}
 def store(self,addr,data):
  for i,value in enumerate(data):self.memory[addr+i]=value
 def load(self,key,addr,size):
  assert key not in self.snapshots;value=bytes(self.memory[addr+i] for i in range(size));self.snapshots[key]=value;return value

def verify(stimulus):
 rows=[]
 for case in stimulus['cases']:
  initial=bytes.fromhex(case['initial_line_hex']);base=case['line_address'];ref=ByteReference(base,initial);stores=reads=assertions=0
  for event in case['events']:
   if event['op']=='store':
    payload=bytes.fromhex(event['data_hex']);assert len(payload)==event['size'];before=dict(ref.memory);offset=event['address']-base
    assert int(event['byte_mask_128_hex'],16)==sum(1<<(offset+i) for i in range(len(payload)))
    ref.store(event['address'],payload);stores+=1
    assert all(ref.memory[a]==value for a,value in before.items() if not event['address']<=a<event['address']+len(payload))
   elif event['op']=='read':assert ref.load(event['snapshot_id'],event['address'],event['size']).hex()==event['expected_hex'];reads+=1
   elif event['op']=='expect_snapshot':assert ref.snapshots[event['snapshot_id']].hex()==event['expected_hex'];reads+=1
   elif event['op']=='observe':assertions+=1  # Passed to RTL adapter; not "checked" here.
   else:raise ValueError(event['op'])
  assert bytes(ref.memory[base+i] for i in range(128)).hex()==case['final_line_hex']
  rows.append({'case_id':case['case_id'],'status':'BYTE_REFERENCE_SELF_CHECK_PASS_ONLY','stores':stores,'read_snapshot_comparisons':reads,'protocol_assertions_NOT_executed':assertions,'production_numeric_equivalence':False})
 return rows
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stimulus',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();data=a.stimulus.read_bytes();v={'schema':'INDEPENDENT_BYTE_REFERENCE_SELF_CHECK_V1','stimulus_sha256':hashlib.sha256(data).hexdigest(),'reference_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':verify(json.loads(data)),'scope':'Only independent reference and expected vectors; no RTL output or simulator numerical byte output consumed.'};a.output.write_text(json.dumps(v,indent=2)+'\n');print('10 reference cases PASS; no production byte-merge qualification')
