import copy
import hashlib
import json
import math
from pathlib import Path
import oracle_opportunity_analyzer as oa

def h(x): return hashlib.sha256(x.encode()).hexdigest()
BUILD={'core_commit':'1'*40,'framework_commit':'2'*40,'binary_sha256':'3'*64,'libcudart_sha256':'4'*64}
CONFIGS={m:[h('base'+str(i)) for i in range(4)]+[h(m)] for m in oa.MODES}
MATRIX_SHA=h('fixed_matrix_fixture')

def fixture():
    matrix={'rows':[]}; snapshot={'schema':'DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1','matrix_sha256':MATRIX_SHA,'rows':[],
        'authority_commit':oa.AUTHORITY,'CH_budget':0,
        'generated_utc':'CPU_FIXTURE','closed_fingerprint_sha256':h('closed'),'validation_errors':[],'closed_result_count':8}
    for index in range(32):
        inp=h('input'+str(index))
        for mode in oa.MODES:
            p={'plan_id':f'PLAN-{index}-{mode}','program':f'P{index:02}','suite':'A' if index<16 else 'B',
                'input_digest':inp,'mode':mode,'initial_fixed8':index<8,'stage':'initial8' if index<8 else 'remaining24',
                'capture_identity':{'expected':{'instructions':30,'CTA':3,'kernels':2},'source_scope':'CPU_FIXTURE'},'design':'DH'}
            matrix['rows'].append(p)
            snapshot['rows'].append({k:p[k] for k in ('plan_id','program','suite','input_digest','mode','initial_fixed8','stage')})
            snapshot['rows'][-1].update(status='CPU_DRAFT_UNREGISTERED' if index>=8 else 'RUNNING_OR_POSTPROCESS_PENDING',
                classification='missing',cycles=None,independent_review_status='NOT_YET_FINAL_INDEPENDENT_REVIEW',historical_DH0_context_cycles=999999)
    facts={}
    def accept(index,mode,cycles):
        r=next(r for r in snapshot['rows'] if r['program']==f'P{index:02}' and r['mode']==mode)
        r.update(status='ACCEPTED_RUNTIME_CLOSER',classification='accepted',cycles=cycles,uuid=r['plan_id'],**BUILD,
            result_sha256=h(r['plan_id']+'result'),spec_sha256=h(r['plan_id']+'spec'),execution_plan_sha256=h('plan'),
            native_strict_sha256=h(r['plan_id']+'strict'),kernel_evidence_sha256=h(r['plan_id']+'facts'),
            non_oracle_options_sha256=h(r['input_digest']+'options'),configuration_file_pins=[{'sha256':x} for x in CONFIGS[mode]],
            terminal_metrics_as_printed={'DTC_SERVICE_V1_samples':cycles*64,'DTC_SERVICE_V1_pib_integral':cycles*64*5,
                'DTC_SERVICE_V1_physical_integral':cycles*64*400},actual_mechanism_exposure=0,
            traffic_as_printed={'L2_reported_GLOBAL_ACC_R_TOTAL_ACCESS':None,'L2_derived_accepted_read_32B_sectors':0,
                'sparse_partition_proof':{'proof':'SOURCE_PROVEN_NOT_ZERO_FILL'}},latency_counters_as_printed={})
        half=cycles//2
        records=[]
        for ordinal,(c,total,inst,cta,delta) in enumerate([(half,half,10,1,1),(cycles-half,cycles,20,3,2)],1):
            records.append({'ordinal':ordinal,'kernel':'SAME_REPEATED_KERNEL_NAME','cycles':c,'total_cycles':total,
                'active_instructions':inst,'cumulative_CTA':cta,'CTA_delta':delta,'result_sha256':r['result_sha256'],
                'strict_sha256':r['native_strict_sha256'],'raw_gzip_sha256':h('raw'+r['plan_id']),
                'raw_uncompressed_sha256':h('plain'+r['plan_id']),'as_printed_counters':{'missing_counter':None,'ambiguous_cumulative':7},
                'oracle':{'exposure':0},'scope':'AS_PRINTED_NO_RESET_INFERRED'})
        facts[r['plan_id']]={k:r[k] for k in ('program','input_digest','mode','uuid')}
        facts[r['plan_id']]['records']=records
    for m,c in zip(oa.MODES,[100,50,125,100]): accept(0,m,c)
    accept(1,'OFF_MATCHED',200);accept(1,'M_DATAREAD',50)
    accept(2,'M_DATAREAD',75);accept(3,'OFF_MATCHED',100)
    hold=next(r for r in snapshot['rows']if r['program']=='P03'and r['mode']=='L1_DATAREADY')
    hold.update(status='NEGATIVE_OR_HOLD_RETAINED',classification='negative_or_hold',raw_status='FAILED_LIFECYCLE',
        observed_cycles_not_accepted=12,raw_failure_proof={'preserve':'FAILED_NOT_PERFORMANCE'})
    c1={h('input2'):{'input_digest':h('input2'),'status':'OLD_REAL_STRUCTURAL_EVIDENCE','DH0_cycles':100,'not_an_OFF_substitute':True}}
    return snapshot,matrix,facts,c1

checks=[]
def check(name,condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
def analyze(s,m,k,c1=None):
    return oa.analyze(s,m,k,matrix_sha256=MATRIX_SHA,expected_build_identity=BUILD,expected_configs_by_mode=CONFIGS,c1_context=c1)
def cell(result,index,mode): return result['program_records'][index]['C2_controlled_Oracle_cells'][mode]

s,m,k,c1=fixture(); before=json.dumps([s,m,k,c1],sort_keys=True); result=analyze(s,m,k,c1)
check('pure_function_does_not_mutate_inputs',before==json.dumps([s,m,k,c1],sort_keys=True))
check('fixed32_and128_retained',result['fixed_population']==32 and result['cell_population']==128 and len(result['program_records'])==32)
check('slow_oracle_negative_H_not_clipped',cell(result,0,'L2_DATAREAD')['S']==.8 and cell(result,0,'L2_DATAREAD')['H']==-.25)
check('zero_response_kept',cell(result,0,'L1_DATAREADY')['S']==1 and cell(result,0,'L1_DATAREADY')['H']==0)
check('missing_OFF_never_uses_historical_or_C1',cell(result,2,'M_DATAREAD')['S'] is None and cell(result,2,'M_DATAREAD')['pair_status']=='MISSING_OR_UNQUALIFIED_MATCHED_OFF')
check('C1_is_separate',result['program_records'][2]['C1_real_structure_evidence_separate']['DH0_cycles']==100)
st=result['mode_statistics']['M_DATAREAD']['CORE32']
check('mode_GM_uses_own_accepted_subset',st['accepted_matched_pairs']==2 and math.isclose(st['GM_S_over_accepted_matched_subset'],math.sqrt(8)))
check('constant32_denominator_with_missing',st['fixed_population_denominator']==32 and st['missing_or_unpaired']==30 and st['coverage']==2/32)
check('fixed8_not_promoted_to32',result['mode_statistics']['M_DATAREAD']['fixed8']['fixed_population_denominator']==8)
four=result['four_cell_common_accepted']
check('four_cell_intersection_separate_GM',four['accepted_common_inputs']==1 and four['same_set_GM_by_mode']['M_DATAREAD']['GM_S_over_accepted_matched_subset']==2)
check('common_GM_not_different_denominator_mode_GM',four['same_set_GM_by_mode']['M_DATAREAD']['GM_S_over_accepted_matched_subset']!=st['GM_S_over_accepted_matched_subset'])
check('slower_counts_kept',result['mode_statistics']['L2_DATAREAD']['CORE32']['slower']==1)
check('HOLD_and_observed_failed_cycles_preserved',cell(result,3,'L1_DATAREADY')['observed_cycles_not_accepted']==12 and cell(result,3,'L1_DATAREADY')['S'] is None)
check('no_final_review_promotion',cell(result,0,'M_DATAREAD')['independent_review_status']=='NOT_YET_FINAL_INDEPENDENT_REVIEW')
ev=cell(result,0,'M_DATAREAD')['evidence']
check('reported_null_and_derived_zero_distinct',ev['L2_read_reported'] is None and ev['L2_read_source_derived']==0 and ev['derived_proof_retained']['proof']=='SOURCE_PROVEN_NOT_ZERO_FILL')
check('missing_pressure_not_zero',ev['request_Tag_Physical_PIB_Ref_as_printed']['DTC_L1_oo_active_refs'] is None)
check('defined_occupancy_mean',ev['finite_service']['PIB_average_per_SM']==5)
kp=result['matched_kernel_pairs']
check('repeated_names_keep_ordinal',len([x for x in kp if x['program']=='P00'and x['mode']=='M_DATAREAD'])==2)
check('kernel_cycles_not_cumulative',next(x for x in kp if x['program']=='P00'and x['mode']=='M_DATAREAD'and x['ordinal']==2)['Oracle_kernel_cycles']==25)
check('as_printed_counters_not_differenced',all(x['counter_delta_or_reset_inferred'] is False and x['Oracle_record_as_printed']['as_printed_counters']['ambiguous_cumulative']==7 for x in kp))
check('no_best_oracle_GM',result['best_oracle_stitched_GM']=='FORBIDDEN_NOT_COMPUTED')

def mutate(name,fn,expected_part):
    ss,mm,kk,cc=fixture(); rr=next(r for r in ss['rows']if r['program']=='P00'and r['mode']=='M_DATAREAD')
    fn(rr,kk[rr['plan_id']]);out=analyze(ss,mm,kk,cc);c=cell(out,0,'M_DATAREAD')
    check(name,c['S'] is None and (expected_part in c['pair_status'] or any(expected_part in e for e in c['validation_errors'])))
for field in oa.BUILD_KEYS:
    mutate('reject_mismatched_'+field,lambda r,k,f=field:r.__setitem__(f,'f'*len(r[f])),'UNFROZEN_BUILD_')
mutate('reject_270_vector_mismatch',lambda r,k:r.__setitem__('non_oracle_options_sha256','f'*64),'HOLD_NON_ORACLE270')
mutate('reject_changed_config_pins',lambda r,k:r['configuration_file_pins'][0].__setitem__('sha256','f'*64),'UNFROZEN_ORDERED')
mutate('reject_missing_strict_pin',lambda r,k:r.__setitem__('native_strict_sha256',None),'MISSING_PIN_')
mutate('reject_actual_kernel_work_change',lambda r,k:k['records'][1].__setitem__('active_instructions',21),'KERNEL_WORK_DIFFERENT')
mutate('reject_reordered_kernel_work_even_same_totals',lambda r,k:(k['records'][0].__setitem__('active_instructions',20),k['records'][1].__setitem__('active_instructions',10)),'KERNEL_SEQUENCE_OR_WORK')
mutate('reject_CTA_delta_corruption',lambda r,k:k['records'][1].__setitem__('CTA_delta',1),'CTA_DELTA_NOT_DEFINED')
mutate('reject_kernel_cycles_relabelled_total',lambda r,k:k['records'][1].__setitem__('cycles',50),'EXPLICIT_KERNEL_CYCLES_NOT_TOTAL')
mutate('reject_missing_kernel_facts_identity',lambda r,k:k.__setitem__('input_digest','f'*64),'KERNEL_FACTS_IDENTITY_')
mutate('reject_invalid_null_cycles_without_crash',lambda r,k:r.__setitem__('cycles',None),'INVALID_WHOLE_INPUT')
mutate('unknown_sample_scope_has_null_mean',lambda r,k:r['terminal_metrics_as_printed'].__setitem__('DTC_SERVICE_V1_samples',None),'__NO_HOLD_EXPECTED__') if False else None
ss,mm,kk,cc=fixture();rr=next(r for r in ss['rows']if r['program']=='P00'and r['mode']=='M_DATAREAD');rr['terminal_metrics_as_printed']['DTC_SERVICE_V1_samples']=None
check('unconfirmed_service_scope_no_mean',cell(analyze(ss,mm,kk,cc),0,'M_DATAREAD')['evidence']['finite_service']['PIB_average_per_SM'] is None)
for name,fn in [('duplicate_row',lambda s,m:s['rows'].append(copy.deepcopy(s['rows'][0]))),
    ('unfrozen_row',lambda s,m:s['rows'][0].__setitem__('plan_id','FOREIGN')),
    ('changed_full_input_identity',lambda s,m:s['rows'][0].__setitem__('input_digest','f'*64)),
    ('missing_fixed_slot',lambda s,m:s['rows'].pop()),
    ('bad_population_matrix',lambda s,m:m['rows'].pop()),
    ('foreign_authority',lambda s,m:s.__setitem__('authority_commit','f'*40)),
    ('CH_budget',lambda s,m:s.__setitem__('CH_budget',1)),
    ('CH_matrix_design',lambda s,m:m['rows'][0].__setitem__('design','CH'))]:
    ss,mm,kk,cc=fixture();fn(ss,mm)
    try:analyze(ss,mm,kk,cc);raise AssertionError('accepted '+name)
    except ValueError:checks.append('fail_closed_'+name)
report={'schema':'DTC_CORE32_OPPORTUNITY_ANALYZER_CPU_FIXTURE_V1','pass':True,'checks':len(checks),'names':checks,
    'scientific_starts':0,'raw_logs_read':0,'management_operations':0,'synthetic_only':True}
Path(__file__).with_name('CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
