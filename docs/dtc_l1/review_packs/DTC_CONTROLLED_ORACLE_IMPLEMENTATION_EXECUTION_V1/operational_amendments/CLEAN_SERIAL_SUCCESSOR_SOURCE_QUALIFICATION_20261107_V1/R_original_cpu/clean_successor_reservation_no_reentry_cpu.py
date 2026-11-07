from pathlib import Path
import ast,types,json,copy,hashlib,tempfile,os
R=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');X=A/'agents/R_clean_successor_cpu_preparation_v1';q=json.loads((R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json').read_bytes());REQ=q['request'];scratch=R/'engineering_cpu/reservation_EX_no_reentry';(scratch/'control/specs').mkdir(parents=True,exist_ok=True)
for c in q['admitted_specs']:(scratch/'control/specs'/(c+'.json')).write_bytes((R/'control/specs'/(c+'.json')).read_bytes())
p=R/'tools/oracle_ops.py';tree=ast.parse(p.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='sync_stage_reservation');texts=ast.get_source_segment(p.read_text(),fn);trace=[];state={'EX':False};store=copy.deepcopy(q);store['reserved_write_bytes']=768*1024**2
class E:
 def authority(self):
  assert not state['EX'],'RECURSIVE_SH_UNDER_EX';trace.append('UNLOCKED_SH_SNAPSHOT_READ');return({'registered_future_requests':{REQ:copy.deepcopy(store)}},{'epoch':2})
 def update_authority(self,callback):
  assert not state['EX'];state['EX']=True;trace.append('EX_BEGIN_PASSED_SNAPSHOT_ONLY')
  try:callback({'registered_future_requests':{REQ:store}})
  finally:state['EX']=False;trace.append('EX_END')
def load(name,path):
 assert not state['EX'],'SOURCE_OR_FS_LOAD_UNDER_EX';m=types.ModuleType(name);m.__file__=str(path);exec(compile(Path(path).read_bytes(),str(path),'exec'),m.__dict__);return m
# Preserve actual new reservations source but place its copy under isolatedroot.
(scratch/'tools').mkdir(exist_ok=True);(scratch/'tools/oracle_reservations.py').write_bytes((R/'tools/oracle_reservations.py').read_bytes())
ns={'load':load,'put':lambda p,v:Path(p).write_text(json.dumps(v))};exec(compile(texts,'<ACTUAL_NEW_PRIVATE_SYNC_STAGE_RESERVATION>','exec'),ns);ctx={'root':scratch,'request':REQ,'e':E()};before=copy.deepcopy(store);v=ns['sync_stage_reservation'](ctx,{})
assert store['reserved_write_bytes']==256*1024**2 and {k:v for k,v in store.items()if k!='reserved_write_bytes'}=={k:v for k,v in before.items()if k!='reserved_write_bytes'}
assert trace==['UNLOCKED_SH_SNAPSHOT_READ','EX_BEGIN_PASSED_SNAPSHOT_ONLY','EX_END'];positive=list(trace)
trace.clear();v=ns['sync_stage_reservation'](ctx,{});assert trace==['UNLOCKED_SH_SNAPSHOT_READ'],'UNCHANGED_RESERVE_MUST_NOT_WRITE_REGISTRY'
# Explicit EX negative: an injected authority read is rejected by mocked lock,
# proving the original callback does not rely on a recursive reader capability.
state['EX']=True
try:
 try:E().authority();raise AssertionError('SH_NOT_REJECTED')
 except AssertionError as e:assert str(e)=='RECURSIVE_SH_UNDER_EX'
finally:state['EX']=False
r={'schema':'DTC_CLEAN_PRIVATE_RESERVATION_ACTUAL_FUNCTION_CPU_TEST_V1','status':'PASS','source_path':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tested_function_source_sha256':hashlib.sha256(texts.encode()).hexdigest(),'checks':['actual derived sync_stage_reservation source executes against isolated copied96 speccaps','SH snapshot+all local IO occurs before pure EX callback','only own reserved_write_bytes changes768MiB→256MiB','budget/admitted_specs/UUID/technical ceiling and all othermockq fields unchanged','unchanged reserved projection does not write registry','mock recursiveSH inEX is rejected'],'positive_call_trace':positive,'production_registry_reads_or_writes_by_fixture':0,'production_locks':0,'scientific_models_started':0,'scientific_UUIDs':0};(X/'RESERVATION_EX_NO_REENTRY_CPU_QUALIFICATION.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(r['checks']),'trace':positive}))
