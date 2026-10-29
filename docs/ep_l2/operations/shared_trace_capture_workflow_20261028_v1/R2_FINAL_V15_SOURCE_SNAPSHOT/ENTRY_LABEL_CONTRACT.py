"""Entry-only selected completeCTA evidence contract. Does not execute or grant a model."""
import math
ENTRY='ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ONLY'
ALIGNED='CUDA118_ALIGNEDTYPES_MEM49999872_GRID64X256_TYPES12_REPEAT2_OBJECTLINK_V2'
def need(v,m):
 if not v:raise ValueError(m)
def entry_witness(result,sample,feature,qid):
 need(qid in ['SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1', 'TRANSPOSE_CUDA118_REPEAT2_ORIGINAL1024_OBJECTLINK_V2', 'CUDA118_CONVOLUTION_SEPARABLE_ORIGINAL_3072_REPEAT2_V1'],'EXACT_REMAINING3_ROW')
 need(result['status']=='PASS_'+ENTRY and result['qualification_label']==sample['qualification_label']==ENTRY,'EXACT_ENTRY_NOT_FULL_FEATURE')
 need(result['rc']==0 and result['budget_reason']is None and result['stop_reason']is None and set(result['checks'])=={'normal_exit', 'all_CTAs', 'record_diagnostics_disabled', 'total_nonzero_source_plus_aux_retirement', 'mapped_private_core', 'exact_kernel_uid_order', 'no_active_unknown_input', 'per_kernel_source_plus_aux_retirement', 'under_cycle_cap', 'rc0', 'no_wall_or_log_cap'} and all(x is True for x in result['checks'].values()),'REAL_ENTRY_PASS_NO_BUDGET')
 need(result['whole_input_functional']is False and result['numeric_science_performance_generic_ISA_qualification']is False and result['generic_CALL_RET_dynamic_support_claim']is False,'NO_WHOLEINPUT_OR_SCIENCE')
 need(result['all_features_model_exercised']is sample['all_features_model_exercised']is False,'NO_FULL_FEATURE_GRANT')
 need(result['process_terminal']['joined']is True and result['process_terminal']['present_after_join']is False and result['process_terminal']['rc']==0,'OWN_MODEL_JOINED')
 need(result['expected']==sample['expected_selected_CTA_retirement'],'EXACT_EXPECTED_MATCH')
 e=result['expected'];need(e['CTAs_cumulative']==[1]and len(e['kernel_uids'])==len(e['per_kernel_retired_active_lane_uops'])==1,'EXACT_ONE_CTA_ONE_KERNEL');need(e['active_unknown_records']==0 and e['total_retired_active_lane_uops']>0,'NO_UNKNOWN_POSITIVE_RETIRE')
 need(result['kernel_uids']==e['kernel_uids']and result['completed_CTAs_cumulative']==e['CTAs_cumulative']and result['retired_lane_uops_per_kernel']==e['per_kernel_retired_active_lane_uops']and result['retired_lane_uops_total']==e['total_retired_active_lane_uops'],'ACTUAL_RETIREMENT_MATCH')
 need(sample['status']=='STRUCTURAL_COMPLETE_CTA_BYTE_PRESERVATION_ONLY_NOT_CONSUMER_PASS'and sample['parent_fields_not_reinterpreted_or_dropped']is True,'COMPLETE_CTA_PRESERVATION')
 selected=sample['selection'];rr=sample['results'];need(len(rr)==len(selected)==1 and rr[0]['selected_CTAs']==1,'ONE_COMPLETE_CTA')
 need(rr[0]['selected_records']==selected[0]['records']>0 and rr[0]['output_full_CRC']is True,'COMPLETE_SAMPLE_CRC')
 need(rr[0]['kernel']==selected[0]['kernel']and rr[0]['expected_retired_active_lane_uops']==rr[0]['source_active_lane_uops']+rr[0]['aux_active_lane_uops']==e['total_retired_active_lane_uops'],'LANE_COUNT_UNITS_JOIN')
 allkeys=set(feature['features']);covered=sample['covered_feature_witness_subset'];remaining=sample['remaining_unexercised_features']
 need(len(covered)==len(set(covered))and len(remaining)==len(set(remaining))and set(covered).isdisjoint(remaining)and set(covered)|set(remaining)==allkeys,'EXACT_PARTIAL_FEATURE_PARTITION')
 need(len(remaining)>0,'PARTIAL_NOT_ALL_EMPTY_FIRST_WITNESS_SUBSET_ALLOWED')
 for key in covered:
  w=feature['features'][key];need(w['observed_active']is True and w['kernel']==selected[0]['kernel']and w['cta']==selected[0]['origin'],'FIRST_WITNESS_SOURCE_CTA')
 h=feature['kernel_headers'][selected[0]['kernel']];need(len(selected[0]['origin'])==len(h['grid'])==3,'EXACT_3D_CTA');need(all(0<=x<n for x,n in zip(selected[0]['origin'],h['grid'])),'SOURCE_CTA_BOUNDS')
 return dict(consumer_status='ENTRY_COMPLETE_CTA_ONLY',qualification_label=ENTRY,feature_coverage_partial=True,all_source_features_model_exercised=False,first_witness_subset_covered=covered,remaining_unexercised_first_witness_features=remaining,feature_coverage_interpretation='First-witness evidence partition only; not an opcode absence assertion for other executed records',selected_complete_source_CTAs=[dict(kernel=x['kernel'],origin=x['origin'],derived=x['derived'],parent_body_sha256=x['parent_body_sha256'],source_records=x['records'])for x in selected],selected_source_records=rr[0]['selected_records'],selected_source_active_lane_uops=rr[0]['source_active_lane_uops'],selected_aux_active_lane_uops=rr[0]['aux_active_lane_uops'],actual_retired_active_lane_uops=result['retired_lane_uops_total'],full_input_functional=False,full_input_numeric=False,performance_qualification=False,science_qualification=False,generic_CALL_RET_dynamic_support=False,actual_derived_model_executed=False)
