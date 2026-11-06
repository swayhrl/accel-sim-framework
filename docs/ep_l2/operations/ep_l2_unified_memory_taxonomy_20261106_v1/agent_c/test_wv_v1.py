#!/usr/bin/env python3
"""Bounded anti-misclassification checks; no model, subprocess, Trace, raw or authority access."""
import copy, importlib.util, json, pathlib, hashlib
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('wv',P/'extract_wv_v1.py')
wv=importlib.util.module_from_spec(spec);spec.loader.exec_module(wv)
checks=[]
def ok(name,pred):
    assert pred,name
    checks.append({'name':name,'status':'PASS'})
def rejected(name,a,b,allow):
    try:wv.guard_pair(a,b,allow)
    except ValueError:ok(name,True)
    else:raise AssertionError(name)
a={'accepted':True,'input_identity_sha256':'I','ordered_commands_canonical_sha256':'CMD','source5':{'core':'A','ELF':'B'},'effective_options':{'geometry':'32x8','DRAM':'850','queue':'128'}}
b=copy.deepcopy(a);b['effective_options']['geometry']='64x8'
ok('exact_identity_geometry_only_pair',set(wv.guard_pair(a,b,['geometry']))=={'geometry'})
for key,value in [('input_identity_sha256','Other'),('ordered_commands_canonical_sha256','Other'),('source5',{'core':'Other','ELF':'B'}),('source5',{'core':'A','ELF':'Other'}),('accepted',False)]:
    c=copy.deepcopy(b);c[key]=value;rejected('reject_pair_change_'+key+'_'+str(value),a,c,['geometry'])
for k in ['DRAM','queue']:
    c=copy.deepcopy(b);c['effective_options'][k]='changed';rejected('reject_hidden_hardware_change_'+k,a,c,['geometry'])
c=copy.deepcopy(b);c['ordered_commands_canonical_sha256']=None
rejected('reject_missing_command_identity',a,c,['geometry'])
ok('missing_V_is_unknown_not_zero',wv.classify({}, {},'F')['V']=='UNKNOWN')
ok('explicit_zero_V_is_zero',wv.classify({}, {'read_responses':0},'F')['V']=='VICTIM_RESPONSE_ZERO_OBSERVED')
ok('S_V_not_applicable',wv.classify({}, {'read_responses':0},'S')['V']=='NOT_APPLICABLE')
ok('unaccepted_zero_not_scientific_zero',wv.classify({}, {'read_responses':0},'F',False)['V']=='UNACCEPTED')
ok('positive_response_does_not_prove_program_histogram',wv.classify({}, {'read_responses':3},'F')['program_sector_temporal_reuse']=='UNKNOWN')
ok('positive_response_does_not_prove_avoided_DRAM',wv.classify({}, {'read_responses':3},'F')['avoidable_DRAM_requests']=='UNKNOWN')
ok('WB_volume_does_not_prove_capacity_pressure',wv.classify({'wb_created':999999999},{},'F')['WAD_capacity']=='UNKNOWN')
ok('explicit_WAD_refusal_is_pressure_evidence',wv.classify({'head_waits':{'WAD_FULL':{'blocked_observations_over_slices':1}}},{},'F')['WAD_capacity']=='WAD_CAPACITY_REFUSAL_OBSERVED')
rows={str(i):{k:0 for k in wv.V_KEYS} for i in range(64)}
rows['63']['read_responses']=7
m={'mechanism_metrics':{'full_mechanism_records':{'victim':rows}}}
ok('exact64_final_cumulative_projection',wv.get_metrics(m,'F')[1]['read_responses']==7)
bad=copy.deepcopy(m);del bad['mechanism_metrics']['full_mechanism_records']['victim']['63']
ok('63_slices_cannot_be_explicit_complete_zero',wv.get_metrics(bad,'F')[1]=={})
bad=copy.deepcopy(m);del bad['mechanism_metrics']['full_mechanism_records']['victim']['63']['read_responses']
ok('missing_one_counter_not_zero', 'read_responses' not in wv.get_metrics(bad,'F')[1])
bad=copy.deepcopy(m);bad['mechanism_metrics']['full_mechanism_records']['victim']['kernel_cumulative_duplicate']=copy.deepcopy(rows['63'])
ok('extra_cumulative_record_not_double_summed',wv.get_metrics(bad,'F')[1]=={})
d=json.load(open(P/'WV_REUSE_EVIDENCE_BY_INPUT.json'))
ok('103_original_rows_preserved',len(d['rows'])==103)
ok('35_population_preserved',sum(r['member_main35'] for r in d['rows'])==35)
ok('42_population_preserved',sum(r['member_main42'] for r in d['rows'])==42)
ok('96_content_population_preserved',sum(r['member_ordinary96'] for r in d['rows'])==96)
ok('unresolved7_not_fake_measurements',sum(not r['member_ordinary96'] for r in d['rows'])==7)
ok('286_accepted_5_unaccepted_preserved',d['counts']['accepted_endpoints']==286 and d['counts']['unaccepted_endpoints']==5)
ok('all103_global_sector_histograms_unknown',all(r['program_sector_temporal_reuse']=='UNKNOWN' for r in d['rows']))
ok('no_acceleration_classification_field',all('performance_is_validation_not_class_definition' in p for p in d['comparisons']))
e={e['cohort']:e for e in d['endpoints']}
ok('GEMM_same_input_positive_and_zero_separate_configs',e['EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1']['V']['read_responses']==609858 and e['EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1']['V']['read_responses']==0)
ok('FWT_cold_negative_preserved',next(p for p in d['comparisons'] if p['kind']=='NEW_SOURCE_MATCHED_COLD_FILTER_NEGATIVE_RESULT')['saved_cycles']==-1123)
ok('all_accepted_projection_has_original_sealed_validation_ref',all(e.get('source_refs',{}).get('validation_ref') for e in d['endpoints'] if e['accepted']))
out={'schema':'WV_TAXONOMY_BOUNDED_COUNTEREXAMPLE_QA_V1','status':'PASS','checks':checks,'count':len(checks),'model_starts':0,'budget_consumption':0,'raw_trace_reads':0,'extractor_sha256':hashlib.sha256((P/'extract_wv_v1.py').read_bytes()).hexdigest(),'machine_delivery_sha256':hashlib.sha256((P/'WV_REUSE_EVIDENCE_BY_INPUT.json').read_bytes()).hexdigest()}
(P/'WV_CLASSIFIER_QA.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks)}))
