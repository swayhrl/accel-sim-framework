from taxonomy_rules import *
def run():
 checks=[]
 def check(name,ok):
  if not ok: raise AssertionError(name)
  checks.append(name)
 check('missing_stays_UNKNOWN',all(v=='UNKNOWN' for v in classify_endpoint({}).values()))
 check('unknown_block_not_zero',pressure(None,0,128)=='UNKNOWN')
 check('zero_scope_not_universal',pressure(0,110,128)=='NO_BLOCK_OBSERVED_IN_MEASURED_SCOPE')
 check('positive_hardware_boundary',pressure(1,128,128)=='OBSERVED_RESOURCE_BLOCKING')
 check('peak_without_block_no_false_block',pressure(0,128,128)=='BOUNDARY_REACHED_NO_BLOCK_OBSERVED')
 check('negative_rejected',pressure(-1,0,128)=='UNKNOWN')
 check('bool_not_counter',activity(False)=='UNKNOWN')
 check('NaN_not_counter',activity(float('nan'))=='UNKNOWN')
 check('no_service_pair_no_class',service_sensitivity(10,5,False,True)['label']=='UNKNOWN')
 check('mechanism_change_not_service',service_sensitivity(10,5,True,False)['label']=='UNKNOWN')
 check('service_nonzero_not_threshold',service_sensitivity(100,99,True,True)['cycle_change_fraction']==0.01)
 check('zero_cycles_invalid',service_sensitivity(0,1,True,True)['label']=='UNKNOWN')
 check('missing_source_not_equal',not match_identity({},{}))
 m={'line_full_events':3,'ro_merges':999,'victim_served_sectors':1}
 check('speedup_not_classifier',classify_endpoint(dict(m,EP_speedup=0.1))==classify_endpoint(dict(m,EP_speedup=99)))
 check('merge_does_not_imply_activation',classify_endpoint(m)['RO_pressure_policy_activation']=='UNKNOWN')
 check('victim_service_not_full_reuse_census',classify_endpoint(m)['program_sector_temporal_reuse']=='UNKNOWN')
 a={str(i):'0' for i in range(282)};a['-gpgpu_ep_l2_ro_pressure_epoch']='0';b=dict(a);b['-gpgpu_ep_l2_ro_pressure_epoch']='1'
 check('283_single_diff',allowed_policy_pair(a,b))
 b['0']='1';check('hidden_hardware_diff_rejected',not allowed_policy_pair(a,b))
 return checks
if __name__=='__main__':
 import json
 print(json.dumps({'status':'PASS','checks':run(),'count':len(run())},sort_keys=True))
