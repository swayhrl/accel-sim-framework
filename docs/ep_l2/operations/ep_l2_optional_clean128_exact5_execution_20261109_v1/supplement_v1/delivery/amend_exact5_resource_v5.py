#!/usr/bin/env python3
"""Correct peer claim mapping without duplicating a shared V3 scope."""
import copy, hashlib, importlib.util, json
from pathlib import Path

ROOT=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FAMILIES={'gemm':('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
                   ['EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1','EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1','EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1']),
          'stencil':('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
                     ['EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1','EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'])}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 common=load(ROOT/'runtime/host_gemm_bound_v2/ep_perf_common_v2.py','exact5_v4_common')
 with common.locked(common.GLOBAL_MAIN_ADMISSION_LOCK):
  reg,unused=common.authority()
  assert common.read(ROOT/'control/DISPATCH_CLAIMS.json')=={'claims':{}}
  for family,(request,cases) in FAMILIES.items():
   host=ROOT/'runtime'/('host_'+family+'_bound_v2')
   original=host/'resources_exact5_v2.py';candidate=host/'resources_exact5_v2.py.candidate_v5'
   assert candidate.exists() and not (host/'resources_exact5_v2.py.version4').exists()
   (host/'resources_exact5_v2.py.version4').write_bytes(original.read_bytes())
   original.write_bytes(candidate.read_bytes())
   assert sha(original)==sha(candidate)
   qual_old=ROOT/'documents'/('HOST_QUALIFICATION_EXACT5_'+family.upper()+'_V4.json')
   qual_new=qual_old.with_name('HOST_QUALIFICATION_EXACT5_'+family.upper()+'_V5.json')
   qual=copy.deepcopy(common.read(qual_old))
   for item in qual['modules']:
    if item['path']==str(original):item['sha256']=sha(original)
   qual['supplement_revision']='V5_SHARED_CLAIM_OWNER_MAPPING'
   common.put(qual_new,qual,True)
   old={case:common.ref(ROOT/'cases'/case/'control/FROZEN_SPEC.json') for case in cases}
   new={}
   for case in cases:
    path=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
    prior=path.with_name('FROZEN_SPEC.version4.json')
    prior.write_bytes(path.read_bytes())
    value=common.read(path)
    value['resource_module_ref']=common.ref(original)
    value['host_qualification_ref']=common.ref(qual_new)
    new[case]=value
   local=load(host/'ep_perf_common_v2.py','exact5_v4_'+family)
   def amend(registry):
    row=registry['registered_future_requests'][request]
    assert not row['consumed'] and row['admitted_specs']=={case:old[case]['sha256'] for case in cases}
    for case in cases:
     path=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
     local.put(path,new[case]);row['admitted_specs'][case]=sha(path)
    return row['admitted_specs']
   new_pins=local.transaction('EXACT5_V5_SHARED_CLAIM_OWNER_MAPPING_KEEP_BUDGET',amend)
   local.put(ROOT/'control'/('RESOURCE_BINDING_AMENDMENT_'+family.upper()+'_V5.json'),
             dict(request=request,old_specs=old,new_spec_sha256=new_pins,
                  adapter_ref=local.ref(original),consumed_at_amendment=0,
                  other_owner_rows_unchanged=True),True)
   reg,unused=local.authority()
   print(json.dumps(dict(family=family,new_spec_sha256=new_pins)))

if __name__=='__main__':main()
