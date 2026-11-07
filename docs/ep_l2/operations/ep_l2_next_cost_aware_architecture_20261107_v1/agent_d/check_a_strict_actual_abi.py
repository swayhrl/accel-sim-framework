import json,copy,importlib.util
from pathlib import Path
O=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('a_shell',O/'a_segment_record_shell.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
r=json.loads((O/'A_ACTUAL_PRODUCER_RECORD_REPLAY.json').read_text());c=json.loads((O/'A_FINAL_SOURCE_RECORD_ABI_CONTRACT.json').read_text());tests=[]
def test(name,fn,reject=False):
 try:fn()
 except Exception as e:
  if not reject:raise
  tests.append(dict(name=name,status='PASS_REJECT',reason=str(e)));return
 if reject:raise AssertionError('accepted negative '+name)
 tests.append(dict(name=name,status='PASS'))
def line(typ,row):return '|'.join([typ]+[k+'='+str(v)for k,v in row.items()])
def frame(mode):
 actual=r['rows'][mode]['parsed_records']
 pairs=[('EPL2TVDV2|SUMMARY','base_raw_summary'),('EPL2TVDV3|METADATA_COST','base_raw_cost')]+([('EPL2TVDX1|SEGMENT','extension_raw_segment'),('EPL2TVDX1|CONTROL','extension_raw_control')]if mode else[])
 out=[]
 for sid in range(64):
  for typ,key in pairs:
   row=copy.deepcopy(actual[key]);row['slice']=sid;out.append(line(typ,row))
 return out
for row in r['rows']:
 mode=row['mode'];v=row['parsed_records'];test('real_final_single_slice_mode'+str(mode),lambda v=v,mode=mode:m.validate_slice(v['base_raw_summary'],v['base_raw_cost'],v['extension_raw_segment'],v['extension_raw_control'],mode))
for mode in range(3):test('synthetic64_from_real_record_ABI_mode'+str(mode),lambda mode=mode:m.validate_final_frame(frame(mode),mode,c))
xs=frame(2)
test('unknown_hidden_port',lambda:m.validate_final_frame([xs[0]+'|extra_read_ports=1']+xs[1:],2,c),True)
test('unknown_zero_counter',lambda:m.validate_final_frame([xs[0]+'|unreviewed=0']+xs[1:],2,c),True)
test('missing_field',lambda:m.validate_final_frame([xs[0].replace('|mandatory=0','')]+xs[1:],2,c),True)
test('negative_count',lambda:m.validate_final_frame([xs[0].replace('|live=128','|live=-1')]+xs[1:],2,c),True)
test('duplicate_field',lambda:m.validate_final_frame([xs[0]+'|slice=0']+xs[1:],2,c),True)
test('wrongmode',lambda:m.validate_final_frame(frame(2),1,c),True)
test('missing_slice',lambda:m.validate_final_frame(xs[:-4],2,c),True)
test('duplicate_slice',lambda:m.validate_final_frame(xs+xs[:4],2,c),True)
test('unreviewed_record',lambda:m.validate_final_frame(['EPL2TVDX9|CONTROL|slice=0']+xs,2,c),True)
cc=copy.deepcopy(c);cc['record_field_sets']['EPL2TVDX1|CONTROL'].append('hidden_port');test('contract_schema_drift',lambda:m.validate_final_frame(xs,2,cc),True)
out=dict(status='PASS_ACTUAL_SOURCE_STRICT_ABI_AND_SYNTHETIC_POPULATION_CHECKS',count=len(tests),tests=tests,real_population_per_mode=1,synthetic64_is_not_actual_app=True,full_application_runs=0)
(O/'A_STRICT_ACTUAL_ABI_CHECKS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=out['status'],count=len(tests))))
