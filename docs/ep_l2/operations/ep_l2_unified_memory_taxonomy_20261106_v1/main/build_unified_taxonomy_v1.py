from pathlib import Path
import json,hashlib,csv,copy,datetime,collections
P=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=True)+'\n')
def main():
 a=read(P/'agent_a/UPDATED_EVIDENCE_ROWS.json')
 b=read(P/'agent_b/MEMORY_RESOURCE_CLASSIFICATION.json')
 c=read(P/'agent_c/WV_REUSE_EVIDENCE_BY_INPUT.json')
 idx=read(P/'agent_a/CURRENT_ENDPOINT_INDEX.json')
 assert len(a['rows'])==len(b['rows'])==len(c['rows'])==103
 bmap={(x.get('input_identity_sha256'),x.get('program_id'),x['program']):x for x in b['rows']}
 cmap={(x.get('input_identity_sha256'),x.get('program_id'),x['program']):x for x in c['rows']}
 cp={e['cohort']:e for e in c['endpoints']}
 rows=[];flat=[]
 for i,r in enumerate(a['rows']):
  key=(r.get('input_identity_sha256'),r.get('program_id'),r['program'])
  br=b['rows'][i];cr=c['rows'][i]
  assert br.get('input_identity_sha256')==cr.get('input_identity_sha256')==r.get('input_identity_sha256')
  assert br['program_id']==cr['program_id']==r['program_id']
  q=copy.deepcopy(r)
  # Names only disambiguate unresolved rows after exact population position; endpoint links use SHA, never names.
  assert br['original_row_index']==i
  dims={'memory_service_sensitivity':br['memory_service_sensitivity'],
        'Cache_Victim_retention_opportunity':{k:cr[k] for k in ['program_reuse_opportunity','program_sector_temporal_reuse','post_eviction_reuse_distance_distribution','historical_reuse_identity','actual_EP_utilization','victim_service_contexts','victim_zero_contexts']},
        'W_V_M_T_resource_pressure_and_applicability':{'endpoint_scoped_memory_and_RO':br['endpoints'],'endpoint_scoped_WV':[], 'separate_small_geometry_detach_evidence':br['separate_small_geometry_detach_evidence'],'Core812_RO_policy_activation':br['RO_policy_activation']}}
  for e in q['current_result_endpoints']:
   ce=cp[e['cohort']]
   assert ce['input_identity_sha256']==q['input_identity_sha256'] and ce['uuid']==e['uuid']
   dims['W_V_M_T_resource_pressure_and_applicability']['endpoint_scoped_WV'].append({k:ce.get(k) for k in ['cohort','uuid','source5','mode','geometry','clock_domains','effective_options_sha256','W','V','V_measurement_status','labels','measurement_confidence','generalization_confidence','source_refs','payload_end_state','lower_service','lower_service_semantics','wait_semantics']})
  if 'source812_accepted_layers' in br:
   dims['W_V_M_T_resource_pressure_and_applicability']['source812_accepted_layers']=br['source812_accepted_layers']
   dims['W_V_M_T_resource_pressure_and_applicability']['source812_interpretation']=br['source812_interpretation']
  q['classification_dimensions']=dims
  q['classification_scope']='Endpoint/context-specific observations; no universal binary friendly label and no cross-Source performance pairing.'
  q['classification_confidence']={'observed_metrics':'EXACT_MEASURED_ONLY_WITH_EXPLICIT_ENDPOINT_REF','program_opportunity_distribution':'UNKNOWN','cross_Source_prediction':'CANDIDATE_INFERENCE_ONLY'}
  q['classification_gaps']=list(dict.fromkeys(q['current_measurement_gaps']+br['gaps']+cr['gaps']))
  q['classification_evidence_refs']={'identity':ref(P/'agent_a/UPDATED_EVIDENCE_ROWS.json'),'memory_RO':ref(P/'agent_b/MEMORY_RESOURCE_CLASSIFICATION.json'),'W_V':ref(P/'agent_c/WV_REUSE_EVIDENCE_BY_INPUT.json')}
  q['features_define_labels_without_EP_speedup']=True
  rows.append(q)
  line=sorted({e['labels']['ordinary_line_MSHR_pressure'] for e in br['endpoints']})
  desc=sorted({e['labels']['descriptor_pressure'] for e in br['endpoints']})
  memories=br['memory_service_sensitivity']
  flat.append({'row_id':q['row_id'],'program':q['program'],'suite':q['suite'],'program_id':q['program_id'],'input_identity_sha256':q.get('input_identity_sha256'),'member_ordinary96':q['member_ordinary96'],'member_main35':q['member_main35'],'member_main42':q['member_main42'],'frozen_coverage_status':q['coverage_status'],'current_measurement_state':q['current_measurement_state'],'accepted_endpoint_count':q['current_accepted_endpoint_count'],'unaccepted_endpoint_count':q['current_unaccepted_endpoint_count'],'memory_service_sensitivity':memories.get('status','MEASURED_MATCHED_CLOCK_RESPONSE' if memories.get('comparisons') else 'UNKNOWN'),'program_sector_temporal_reuse_distribution':cr['program_sector_temporal_reuse'],'program_retained_sector_revisit_lower_bound':cr['program_reuse_opportunity'],'V_service_context_count':len(cr['victim_service_contexts']),'V_zero_context_count':len(cr['victim_zero_contexts']),'line_MSHR_pressure_labels_by_measured_strata':json.dumps(line or ['UNKNOWN']),'descriptor_pressure_labels_by_measured_strata':json.dumps(desc or ['UNKNOWN']),'Core812_pressure_activation':br['RO_policy_activation'],'endpoint_cohorts':json.dumps(cr['endpoint_cohorts']),'feature_generalization':'UNKNOWN_OUTSIDE_EXACT_SCOPES','confidence':'SEE_PER_ENDPOINT_JSON','classification_gaps':json.dumps(q['classification_gaps']),'structured_record_ref':'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.json#'+q['row_id']})
 counts=copy.deepcopy(a['counts'])
 counts.update({'traceable_classified_rows':103,'rows_with_original_reference_M_W_RO_measurement':b['coverage']['rows_with_reference_endpoints'],'rows_with_measured_clock_service_response':b['coverage']['rows_with_matched_clock_sensitivity'],'rows_with_realized_V_service':c['counts']['rows_with_positive_V_service_context'],'rows_with_V_zero_context':c['counts']['rows_with_explicit_zero_V_service_context'],'positive_and_zero_V_rows_nonexclusive':True,'V_measured_accepted_endpoints':c['counts']['accepted_endpoints_with_V_counts'],'program_sector_temporal_distribution_measured_rows':sum(r['classification_dimensions']['Cache_Victim_retention_opportunity']['program_sector_temporal_reuse']!='UNKNOWN' for r in rows)})
 document={'schema':'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scientific_authority':'1c63b67beace667ea8a8028d77fbf9e5f2a9afc7','counts':counts,'population_definition':{'frozen_rows':103,'content_groups':96,'unresolved_slots':7,'representative_inputs':35,'target_programs_or_slots':42,'current_accepted_scope':idx['scope'],'frozen_20261029_accepted_count_not_latest':222},'row_label_semantics':'EXISTENTIAL_SCOPED_OBSERVATIONS_NOT_UNIVERSAL_WORKLOAD_PROPERTIES; zero contexts and positive contexts may coexist','identity_join':a['join_policy'],'historical_feature_analysis_separate':read(P.parent/'observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json')['historical_reuse'],'performance_comparisons_for_validation_only':c['comparisons'],'endpoint_index_ref':ref(P/'agent_a/CURRENT_ENDPOINT_INDEX.json'),'rows':rows,'new_scientific_starts':0,'budget_consumption':0,'source_keep':True,'released_bytes':0,'old_acceptance_records_modified':False}
 write(P/'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.json',document)
 with (P/'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 write(P/'main/CLASSIFICATION_COVERAGE_SUMMARY.json',{'counts':counts,'classification_coverage_is_not_effective_measurement_coverage':True})
 print(json.dumps(counts))
if __name__=='__main__':main()
