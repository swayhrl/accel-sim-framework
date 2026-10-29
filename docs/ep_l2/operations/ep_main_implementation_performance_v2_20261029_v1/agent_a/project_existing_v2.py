#!/usr/bin/env python3
from pathlib import Path
import json,csv,hashlib,datetime
R=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/observation_guided_20261029_v1')
N=R.parent/'implementation_performance_v2_20261029_v1/agent_a';N.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,x):(N/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def table(n,rows):
 with (N/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def ref(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def ints(rows,k):return [int(v[k]) for v in rows if k in v]
def sums(rows,ks):return {k:sum(ints(rows,k)) if len(ints(rows,k))==len(rows) else None for k in ks}
def maxs(rows,ks):return {k:max(ints(rows,k)) if len(ints(rows,k))==len(rows) else None for k in ks}
def ranges(rows,ks):return {k:[min(ints(rows,k)),max(ints(rows,k))] if len(ints(rows,k))==len(rows) else None for k in ks}
old=json.loads((R/'round2/agent_a/ACCEPTED_ENDPOINT_PROVENANCE.json').read_text())
features=json.loads((R/'agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json').read_text())
compare=list(csv.DictReader((R/'round2/agent_a/POSITIVE_NEGATIVE_RESOURCE_COMPARISON.csv').open()))
rows=[];reads=[];checks=[]
# Named accepted refs only. One full read per endpoint, <1MiB each; no raw or Trace.
for ep in old['references']:
 p=Path(ep['validation_ref']['path']);assert p.stat().st_size<1048576
 b=p.read_bytes();assert sha(b)==ep['validation_ref']['sha256'];a=json.loads(b)
 assert a['source_identity']==ep['source_identity']
 feat=next(x for x in features['rows'] if any(z['cohort']==ep['cohort'] for z in x['reference_endpoints']))
 assert a['input_identity_sha256']==feat['input_identity_sha256']
 assert a['cycles']==next(z['cycles'] for z in feat['reference_endpoints'] if z['cohort']==ep['cohort'])
 assert a['hardware_drained']
 scopes=a['application']['application_scopes'];B=list(scopes['EPL2B0V1'].values());D=list(scopes['EPL2DRAMV1'].values());L=list(scopes['EPL2L1V1'].values());M=list(scopes['EPL2M0AV1'].values())
 assert len(B)==len(M)==64 and len(D)==32
 assert all(x['scope']=='application' and x['interval']=='application_cumulative' and int(x['completion_cycle'])==a['cycles'] for x in B+M)
 assert len(a['application']['actual_options'])==282
 o={'program':feat['program'],'input_sha':a['input_identity_sha256'],'cohort':ep['cohort'],'mode':ep['mode'],'cycles':a['cycles'],'instructions':a['instructions'],'CTA':a['CTA'],'kernels':a['kernel_count'],'source_identity':a['source_identity'],'bundle_ref':ref(p),'accepted_outer_join_evidence':ep['point_ref'],'config282_sha256':sha(json.dumps(a['application']['actual_options'],sort_keys=True,separators=(',',':')).encode()),'ordered_kernel_catalog_sha256':sha(json.dumps(a['application']['ordered_kernel_catalog'],sort_keys=True,separators=(',',':')).encode()),'B0_slice_records':64,'DRAM_channel_records':32,'L1_records':len(L)}
 o['B0_sum_counters']=sums(B,['samples','bank_logical_ops','bank_wait_cycles','c7d_bank_fill_write','c7d_bank_resident_hit_read','c7d_bank_resident_write','c7d_bank_wb_readout','c7d_bank_bypass_fill','c7d_bank_bypass_read','c7d_dram_issue_eligible','c7d_dram_credit_block','c7d_dram_scheduler_full_block','c7d_dram_returnq_block','c7d_dram_to_l2_full_block','c7d_l2_to_dram_full_block','c7d_missq_full_block','c7d_line_mshr_full_block','c7d_per_address_cap_block','c7d_per_address_cap_eligible','c7d_payload_capacity_allocation_denial','c7d_payload_service_port_denial','c7e_dram_issue_attempt','c7e_dram_scheduler_causal_block','c7e_dram_scheduler_full_observed','c7e_dram_to_l2_return_path_block','c7e_dram_successful_read_bytes','c7e_dram_successful_write_bytes','c7e_dram_successful_read_issues','c7e_dram_successful_write_issues','c7e_tag_way_alloc_need','c7e_tag_way_alloc_block'])
 o['B0_max_over_slices']=maxs(B,['lowerq_max','missq_max','line_mshr_max','descriptor_max','wad_max','c7d_reserved_max','c7d_reserved_set_max','c7d_dram_scheduler_occ_max'])
 o['B0_integer_average_ranges_not_weighted_mean']=ranges(B,['lowerq_avg','missq_avg','line_mshr_avg','descriptor_avg','c7d_dram_scheduler_occ_avg'])
 o['M0_sum_counters']=sums(M,['m0_frontend_head_observed_cycles','m0_frontend_head_any_blocked_cycles','m0_frontend_head_blocked_cycles_lowerq','m0_frontend_head_blocked_cycles_missq','m0_frontend_head_blocked_cycles_responseq','m0_frontend_head_blocked_cycles_tag_way','m0_frontend_head_blocked_cycles_line_mshr','m0_frontend_head_blocked_cycles_per_address','m0_frontend_head_blocked_cycles_wad_hazard','m0_useful_frontend_admit','m0_useful_response_enqueue'])
 o['DRAM_sum_counters']=sums(D,['dram_cycles','scheduler_full_cycles','returnq_full_cycles','successful_read_bytes','successful_write_bytes','successful_read_issues','successful_write_issues','bandwidth_util_numerator_bytes','bandwidth_util_denominator_bytes'])
 o['DRAM_max_over_channels']=maxs(D,['scheduler_occ_max','returnq_occ_max'])
 o['DRAM_integer_average_ranges_not_weighted_mean']=ranges(D,['scheduler_occ_avg','returnq_occ_avg'])
 dd=o['DRAM_sum_counters'];o['DRAM_reported_transfer_utilization']=dd['bandwidth_util_numerator_bytes']/dd['bandwidth_util_denominator_bytes']
 o['L1_sum_reported_counters']=sums(L,['accesses','misses','miss_queue_full','mshr_entry_fail','mshr_merge_fail','mshr_rw_pending','line_alloc_fail','bank_latency_queue_conflict'])
 o['local_service']=a['model']['mechanism_metrics']['local_service']
 o['closure']={k:a['model'][k] for k in ['hardware_drained','live_descriptors','live_line_mshrs','live_wad','pending_lower_reads','pending_responses','pending_returns','transient_payloads']}
 checks.append({'cohort':ep['cohort'],'B0_vs_DRAM_successful_read_bytes_equal':o['B0_sum_counters']['c7e_dram_successful_read_bytes']==dd['successful_read_bytes'],'B0_vs_DRAM_successful_write_bytes_equal':o['B0_sum_counters']['c7e_dram_successful_write_bytes']==dd['successful_write_bytes'],'B0_samples_64_times_cycles':o['B0_sum_counters']['samples']==64*a['cycles']})
 reads.append(ref(p));rows.append(o)
dump('EXISTING_MEMORY_PATH_PROJECTION_V2.json',{'schema':'A_V2_BOUNDED_ACCEPTED_PROJECTION','rows':rows,'read_receipts':reads,'scope':'application cumulative final 64 slice B0/M0,32 channel DRAM,L1 reported scopes. Nonexclusive blocks not critical-path cycles. Integer averages are ranges, not precise means.'})
# New normalized descriptors use same-population byte totals or exact independent counters only.
comparisons=[]
for c in compare:
 S=next(x for x in rows if x['input_sha']==c['input_sha'] and x['mode']=='S');F=next(x for x in rows if x['input_sha']==c['input_sha'] and x['mode']==c['treatment_mode'])
 sd=S['DRAM_sum_counters'];fd=F['DRAM_sum_counters'];sb=S['B0_sum_counters'];fb=F['B0_sum_counters']
 q={'program':c['program'],'input_sha':c['input_sha'],'S_mode':'S','treatment_mode':c['treatment_mode'],'S_cycles':S['cycles'],'treatment_cycles':F['cycles'],'speedup':S['cycles']/F['cycles'],'S_DRAM_read_bytes':sd['successful_read_bytes'],'treatment_DRAM_read_bytes':fd['successful_read_bytes'],'DRAM_read_bytes_change_pct':100*(fd['successful_read_bytes']/sd['successful_read_bytes']-1) if sd['successful_read_bytes'] else None,'S_DRAM_write_bytes':sd['successful_write_bytes'],'treatment_DRAM_write_bytes':fd['successful_write_bytes'],'DRAM_write_bytes_change_pct':100*(fd['successful_write_bytes']/sd['successful_write_bytes']-1) if sd['successful_write_bytes'] else None,'S_DRAM_transfer_util':S['DRAM_reported_transfer_utilization'],'treatment_DRAM_transfer_util':F['DRAM_reported_transfer_utilization'],'S_credit_block':sb['c7d_dram_credit_block'],'treatment_credit_block':fb['c7d_dram_credit_block'],'S_scheduler_causal_block':sb['c7e_dram_scheduler_causal_block'],'treatment_scheduler_causal_block':fb['c7e_dram_scheduler_causal_block'],'S_scheduler_full_channel_cycles':sd['scheduler_full_cycles'],'treatment_scheduler_full_channel_cycles':fd['scheduler_full_cycles'],'S_L2_lowerFIFO_full':sb['c7d_l2_to_dram_full_block'],'treatment_L2_lowerFIFO_full':fb['c7d_l2_to_dram_full_block'],'S_L2_MissQ_full':sb['c7d_missq_full_block'],'treatment_L2_MissQ_full':fb['c7d_missq_full_block'],'S_ReturnQ_full_channel_cycles':sd['returnq_full_cycles'],'treatment_ReturnQ_full_channel_cycles':fd['returnq_full_cycles'],'S_lowerq_peak':S['B0_max_over_slices']['lowerq_max'],'treatment_lowerq_peak':F['B0_max_over_slices']['lowerq_max'],'S_missq_peak':S['B0_max_over_slices']['missq_max'],'treatment_missq_peak':F['B0_max_over_slices']['missq_max'],'S_tag_full_allocation_blocks':sb['c7e_tag_way_alloc_block'],'treatment_tag_full_allocation_blocks':fb['c7e_tag_way_alloc_block'],'S_tag_set_reserved_peak':S['B0_max_over_slices']['c7d_reserved_set_max'],'treatment_tag_set_reserved_peak':F['B0_max_over_slices']['c7d_reserved_set_max'],'S_L1_missQ_full':S['L1_sum_reported_counters']['miss_queue_full'],'treatment_L1_missQ_full':F['L1_sum_reported_counters']['miss_queue_full'],'S_L1_MSHR_entry_fail':S['L1_sum_reported_counters']['mshr_entry_fail'],'treatment_L1_MSHR_entry_fail':F['L1_sum_reported_counters']['mshr_entry_fail'],'actual_V_sector_bytes':int(c['actual_V_read_responses'])*32,'V_service_sectors_over_retention_slot_ticks':int(c['actual_V_read_responses'])/int(c['V_retention_slot_ticks']) if int(c['V_retention_slot_ticks']) else None,'logical_copy_ops_avoided':int(c['S_logical_copy_ops'])-int(c['treatment_logical_copy_ops']),'interpretation':'V intensity is service count/retention slot-ticks, not hit rate, byte capacity, independent benefit, unique-entry reuse, or model throughput'}
 comparisons.append(q)
table('POSITIVE_NEGATIVE_MEMORY_PATH_V2.csv',comparisons);dump('POSITIVE_NEGATIVE_MEMORY_PATH_V2.json',comparisons)
qa={'checks':checks,'metadata_checks_total':len(checks)*3,'all_checks_pass':all(all(v for k,v in x.items() if k!='cohort') for x in checks),'endpoint_count':len(rows),'input_count':len(comparisons),'bounded_bundle_bytes_read':sum(x['bytes'] for x in reads),'new_CPU_protocol_tests':0,'new_application_starts':0,'new_Trace_or_raw_reads':0,'test_kind':'SHA, Source5,input,282 configuration count, snapshot scopes and arithmetic population consistency, not protocol/NI/performance experiment'}
dump('OFFLINE_QA_V2.json',qa);print(json.dumps({'comparison':comparisons,'qa':qa},indent=2))
