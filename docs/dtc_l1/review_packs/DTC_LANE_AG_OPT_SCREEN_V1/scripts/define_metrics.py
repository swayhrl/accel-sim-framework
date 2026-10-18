#!/usr/bin/env python3
"""Freeze explicit typed metrics; absence is never converted into zero."""
from common import *

DEFINITIONS=[
 ('cycles','gpu_tot_sim_cycle','core cycles','1','Last natural full-input cumulative GPU core cycles; no host-wall substitution.'),
 ('ready_hit_events','DTC_L1_oo_valid_hits','accepted128B references','1','Physical ready at accepted logical lookup.'),
 ('pending_merge_events','DTC_L1_oo_pending_hits','accepted128B references','1','Attach to not-yet-ready mapped allocation, not unique load instructions.'),
 ('new_line_events','DTC_L1_oo_new_misses','accepted128B references','1','New whole-line lower request and allocation.'),
 ('PIB_integral','DTC_SERVICE_V1_pib_integral','entry core-cycles','1','Sum of active entries over all64SM samples.'),
 ('physical_integral','DTC_SERVICE_V1_physical_integral','line core-cycles','1','Sum of allocated128B identities over all64SM samples.'),
 ('mean_PIB_per_SM','DTC_SERVICE_V1_pib_integral','entries per SM sample','DTC_SERVICE_V1_samples','All64SM, including inactive SMs; samples=64*cycles.'),
 ('mean_physical_per_SM','DTC_SERVICE_V1_physical_integral','128B lines per SM sample','DTC_SERVICE_V1_samples','Allocated physical ownership, not just queryable mappings.'),
 ('collected_sectors','DTC_SERVICE_V1_collected_sectors','32B requested sectors','1','Sectors actually collected via unchanged finite collection port.'),
 ('fully_ready_to_complete_sum','DTC_SERVICE_V1_fully_ready_to_complete_sum','retired instruction core-cycles','1','Original ready origin to original retirement, cumulative completed population.'),
 ('ready_to_collect_sum','DTC_SERVICE_V1_ready_to_collect_sum','retired instruction core-cycles','1','Original observed ready to first collection.'),
 ('collection_cycles','DTC_SERVICE_V1_collection_cycles','retired instruction core-cycles','1','Inclusive collect_done-collect_start+1; not actual collection/WB overlap.'),
 ('WB_wait','DTC_SERVICE_V1_wb_wait','retired instruction core-cycles','1','Retirement cycle minus collect_done minus1.'),
 ('finite_retired_population','DTC_SERVICE_V1_retired','instructions','1','Population accepted by dtc_l1_service_retired, separate from sidecar observation retirement.'),
 ('waiter_notifications','DTC_L1_oo_wakeups','waiter notification events','1','Notification events, not unique consumers, own-dep0 population or early-ready timing.'),
 ('tag_evictions','DTC_L1_oo_tag_evictions','mapping replacements','1','Not Tag bank conflict count, not byte-level conflict.'),
 ('lower_create','DTC_L1_oo_lower_created','whole128B requests','1','Created whole-line cacheable lower ownership.'),
 ('lower_inject','DTC_L1_oo_lower_issued','whole128B requests','1','Actual injection of owned whole-line request, not DRAM atoms.'),
 ('lower_responses','DTC_L1_oo_lower_responses','whole128B response owners','1','Reassembled complete whole-line responses.'),
 ('credit_acquired','DTC_L1_lower_credit_acquired','lower credits','1','Actual credit ownership acquisition.'),
 ('credit_released','DTC_L1_lower_credit_released','lower credits','1','Actual credit release, terminal outstanding must0.'),
 ('collection_WB_actual_overlap','UNAVAILABLE','SM core-cycles','1','No joint same-cycle counter in fixed X2/AE normal export; interval sums cannot reconstruct overlap.'),
 ('per_consumer_notification_population','UNAVAILABLE','consumers by notification/readiness state','1','No original normal-export population histogram; aggregate wakeups insufficient.'),
 ('Tag_set_conflict_histogram','UNAVAILABLE','events by logical set','1','Fixed real-input normal printer lacks this histogram.'),
 ('Tag_bank_quota_conflicts','UNAVAILABLE','failed grants by bank','1','Production frontend has CPU-visible quota counters but original normal export does not print them.'),
 ('L2_accepted_read_sectors','traffic.L2_accepted_read_32B_sectors','32B accepted sectors','1','GLOBAL_ACC_R HIT+HIT_RESERVED+MISS+SECTOR_MISS, equals TOTAL_ACCESS. Not misses alone.'),
 ('L2_read_payload_bytes','traffic.L2_read_payload_bytes','bytes','1','32 times accepted read sectors; not link protocol overhead.'),
 ('DRAM_issued_read_atoms','traffic.DRAM_issued_read_atoms','32B issued read atoms','1','Sum mutually exclusive n_rd+n_rd_L2_A over20controllers.'),
 ('DRAM_issued_write_atoms','traffic.DRAM_issued_write_atoms','32B issued write atoms','1','Sum mutually exclusive n_write+n_wr_bk over20controllers.'),
 ('DRAM_read_payload_bytes','traffic.DRAM_read_payload_bytes','bytes','1','32 times issued read atoms; BL2*buswidth16*chips1 fixed.'),
 ('DRAM_write_payload_bytes','traffic.DRAM_write_payload_bytes','bytes','1','32 times issued write atoms; not DTC credit times128.'),
 ('K1_source_event_frames','UNAVAILABLE','source-defined events / mappings','1','K policy0 means original K1-only normal frame absent; never observed zero.'),
 ('IO_MODERN_active_structure','UNAVAILABLE','NOT_ACTIVE','1','OO only, do not compare inactive structure counters as observations.'),
 ('architectural_load_values','UNAVAILABLE','values','1','Timing SASS replay lacks an actual load payload oracle.'),
 ('AF_real_input_opportunities','UNAVAILABLE','opportunities','1','AF CPU witnesses do not establish real input opportunity; AF excluded.'),
]

def main():
 rows=[]
 for name,key,unit,denom,definition in DEFINITIONS:
  rows.append(dict(field=name,source_key=key,unit=unit,denominator=denom,
      population='FINAL_COMPLETE_INPUT_CUMULATIVE_SNAPSHOT_NO_SUM_OF_KERNEL_CUMULATIVES',
      availability='NOT_EXPORTED_OR_NOT_ACTIVE_UNAVAILABLE' if key=='UNAVAILABLE' else 'ONLY_AFTER_NEW_FULL_STRICT_PASS',
      availability_K0='UNAVAILABLE_NOT_EXPORTED' if key=='UNAVAILABLE' else 'MEASURED_ONLY_AFTER_NEW_K0_FULL_STRICT_PASS',
      availability_K1='UNAVAILABLE_K1_NOT_RUN',
      comparability='PUBLIC_SAME_DEFINITION_ONLY' if key!='UNAVAILABLE' else 'NO_DIRECT_COMPARISON',
      definition=definition,missing_policy='UNAVAILABLE_NOT_ZERO; UNDEFINED_ZERO_DENOMINATOR'))
 table(PACK/'METRIC_DICTIONARY.tsv',rows)
 write(PACK/'COMPARISON_FORMULAS.json',dict(integer_cycles='last gpu_tot_sim_cycle after whole-input natural exit0 and strict',
     cycle_ratio='arm_cycles / this_cohort_same_input_BASE_cycles',
     speedup_ratio='this_cohort_same_input_BASE_cycles / arm_cycles',
     exact_rational=True,old_T_AA5_denominators=False,aggregate_across_inputs=False,GM12=False,
     averaging='PIB or physical integral / (64 * final core cycles); all64SM',
     zero_denominator='UNDEFINED_ZERO_DENOMINATOR',missing='UNAVAILABLE',
     ON_specific='NONCOMPARATIVE_DIAGNOSTIC_OFF_NOT_PRINTED_UNAVAILABLE'))
 print('Typed metric dictionary and per-input common BASE formulas frozen locally; no simulation.')

if __name__=='__main__':main()
