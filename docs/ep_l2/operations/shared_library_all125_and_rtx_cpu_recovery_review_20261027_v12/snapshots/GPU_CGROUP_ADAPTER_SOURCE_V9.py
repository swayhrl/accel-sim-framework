"""Fixed typed budget-to-kernel gate adapter. Authority sums are not replaced by host-free."""
import pathlib,os,time,sys
from runtime_memory_gate_v9 import collect,evaluate,need
def validate_authority(a,x):
 need(x['schema']=='ROOT_COMPLETE_TWO_HOST_RESOURCE_AUTHORITY_V9'and x['root_scope_id']==a['root_scope_id'],'exact independent resource schema/scope')
 need(x['all_foreign_Native_and_RAM_reservations_complete']is True,'independent full foreign authority missing')
 for key in ('native_registry_refs','remote_registry_refs'):
  need(type(x[key])is list and len(x[key])>0,'nonempty raw registry closure refs mandatory')
  for r in x[key]:need(type(r)is dict and type(r.get('path'))is str and len(r.get('sha256',''))==64,'typed raw registry ref')
 for prefix in ('Native174','Native109'):
  for suffix in ('all_reserved_bytes','own_control_bytes','all_RAM_reserved_bytes','own_RAM_bytes'):
   need(type(x[prefix+'_'+suffix])is int and x[prefix+'_'+suffix]>=0,'typed nonnegative complete foreign/own disk/RAM bytes')
  need(type(x[prefix+'_expected_cgroup_namespace'])is str and x[prefix+'_expected_cgroup_namespace'].startswith('cgroup:['),'explicit qualified cgroup namespace')
 need(x['Native109_own_RAM_bytes']>=20*1024**3,'full own20GiB RAM budget remains mandatory')
 return True
def check(a,x,role,root,owned=None):
 from cross_host_v9 import write,sha
 native=role=='native174';prefix='Native174'if native else'Native109'
 foreign=x[prefix+'_all_RAM_reserved_bytes'];own=x[prefix+'_own_RAM_bytes']
 # This exact namespace value must come from separately approved budget authority, not a self-asserted completeness bool.
 expected=x[prefix+'_expected_cgroup_namespace']
 need(type(expected)is str and expected.startswith('cgroup:['),'explicit expected cgroup namespace binding')
 snap=collect();gate=evaluate(snap,foreign,own,role,a['run_id'],owned)
 if snap['host']['namespaces']['cgroup']!=expected:
  gate['status']='HOLD';gate['failures'].append(dict(reason='actual cgroup namespace differs from independent authority'))
 path=pathlib.Path(root)/(prefix+'_CGROUP_RUNTIME_'+str(time.time_ns())+'.json')
 write(path,dict(schema='FULL_RESERVATIONS_PLUS_ACTUAL_CGROUP_GATE_V9',root_scope_id=a['root_scope_id'],resource_authority_sha256=a['resource_authority_ref']['sha256'],kernel_snapshot=snap,gate=gate,authority_budget_separate_from_kernel=True))
 need(gate['status']=='PASS','actual cgroup memory runtime HOLD; receipt '+str(path))
 return dict(path=str(path),sha256=sha(path),status='PASS')
