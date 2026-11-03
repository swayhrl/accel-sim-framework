from pathlib import Path
import json,hashlib

def typed_domains(r):
 c=r['cell'];o=r['effective_options'];t=r['totals'];m=r['strict_metrics'];mode=int(o['-gpgpu_dtc_l1_mode'][0]);generic=int(o['-gpgpu_dtc_l1_pib_entries'][0]);oo=int(o['-gpgpu_dtc_l1_oo_pib_entries'][0]);assert (c,mode,generic,oo)in[('CH',1,256,128),('DH',3,8,128)]
 common={k:t.get(k)for k in ['L2_GLOBAL_read_accepted_sectors','L2_GLOBAL_read_miss_sectors','DRAM_issued_read_atoms32B','DRAM_issued_write_atoms32B','L2_total_cache_reservation_fails','gpu_stall_dramfull']}
 ch=None;dh=None;service=None
 if c=='CH':
  ch={'active_mode':'PAPER_BASE','active_common_PIB_capacity':256,'capacity_parameter':'-gpgpu_dtc_l1_pib_entries','common_PIB_full_events':m.get('DTC_L1_pib_full_events'),'common_tag_bank_conflict_attempts':m.get('DTC_L1_tag_conflicts'),'common_tag_request_attempts':m.get('DTC_L1_tag_requests'),'common_terminal_PIB_occupancy':m.get('DTC_L1_pib_occupancy'),'common_running_PIB_peak_per_SM':m.get('DTC_L1_pib_peak_per_sm'),'ordinary_L1_MSHR_entries':m.get('DTC_L1_baseline_mshr_entries'),'ordinary_L1_MSHR_entry_full_events':m.get('DTC_L1_baseline_mshr_entry_full_events'),'ordinary_L1_MSHR_merge_full_events':m.get('DTC_L1_baseline_mshr_merge_full_events')}
 else:
  dh={'active_mode':'PAPER_OO','active_OO_PIB_capacity':128,'capacity_parameter':'-gpgpu_dtc_l1_oo_pib_entries','generic_pib_parameter_value':8,'generic_pib_parameter_active_for_OO_admission':False,'OO_valid_line_hits':m.get('DTC_L1_oo_valid_hits'),'OO_pending_line_hits':m.get('DTC_L1_oo_pending_hits'),'OO_new_line_misses':m.get('DTC_L1_oo_new_misses'),'OO_tag_mapping_evictions':m.get('DTC_L1_oo_tag_evictions'),'OO_lower_requests_created':m.get('DTC_L1_oo_lower_created'),'OO_terminal_PIB_occupancy':m.get('DTC_L1_oo_pib_occupancy'),'OO_PIB_full_events':None,'OO_tag_bank_conflict_attempts':None,'missing_reason':'These OO full/conflict event fields are not printed in this active mode; CH common counters are never assigned here'}
  div=lambda x,y:t.get(x)/t[y]if t.get(x)is not None and t.get(y)not in[None,0]else None
  service={'domain':'DTC finite-service entries and all64SM samples; not CH ordinary-cache service','raw_cumulative':{k:v for k,v in t.items()if k.startswith('DTC_SERVICE_V1_')},'mean_PIB_entries_across_all64SMs':div('DTC_SERVICE_V1_pib_integral','DTC_SERVICE_V1_samples'),'mean_physical_lines_across_all64SMs':div('DTC_SERVICE_V1_physical_integral','DTC_SERVICE_V1_samples'),'fully_ready_to_retire_cycles_per_retired_entry':div('DTC_SERVICE_V1_fully_ready_to_complete_sum','DTC_SERVICE_V1_retired'),'map_loss_to_free_cycles_per_recorded_event':div('DTC_SERVICE_V1_map_loss_to_free_sum','DTC_SERVICE_V1_map_loss_to_free_count')}
 return {'cell':c,'profile':r['profile'],'RESULT_path':r['RESULT_path'],'RESULT_sha256':r['RESULT_sha256'],'common_downstream_counters':common,'CH_common_frontend':ch,'DH_PAPER_OO_frontend':dh,'DH_finite_service':service,'cross_mode_proxies_not_assumed_equivalent':True}

def active_path_sources():
 C=Path('/root/data/dtc_failure_repair_20261025_v1/core');out=[]
 for rel,ranges in [('src/gpgpu-sim/shader.cc',[(3378,3394),(4448,4475)]),('src/gpgpu-sim/dtc-l1-common.h',[(518,550),(1979,2004)])]:
  p=C/rel;b=p.read_bytes();ls=b.decode().splitlines();out.append({'commit':'9eedb3131937748f0492fa83aad37d3691118d70','path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'excerpts':[{'start':a,'end':z,'text':'\n'.join(f'{i+1}: {ls[i]}'for i in range(a-1,z))}for a,z in ranges]})
 return out
