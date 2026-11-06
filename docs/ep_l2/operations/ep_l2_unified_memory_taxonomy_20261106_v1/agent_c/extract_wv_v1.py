#!/usr/bin/env python3
"""Extract W/V evidence from accepted, already sealed small JSON only.
No subprocess, no model/trace/raw reads, and no shared authority writes.
"""
import collections, csv, hashlib, json, pathlib
ROOT=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
BASE=ROOT/'research/unified_memory_taxonomy_20261106_v1'
OUT=BASE/'agent_c'
OLD=ROOT/'research/observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json'
INDEX=BASE/'agent_a/CURRENT_ENDPOINT_INDEX.json'
READS={}
READ_BYTES=0
MAX_TOTAL=256*1024*1024
def canonical(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p,expected=None,cap=24*1024*1024):
    global READ_BYTES
    p=pathlib.Path(p)
    if p.name.endswith(('.gz','.traceg','.trace')) or 'raw' in p.name.lower():
        raise ValueError('forbidden raw/trace path')
    st=p.stat()
    if st.st_size>cap: raise ValueError('metadata size cap')
    b=p.read_bytes()
    if len(b)>cap:raise ValueError('metadata grew past cap')
    h=hashlib.sha256(b).hexdigest()
    if expected and h!=expected:raise ValueError('SHA mismatch '+str(p))
    READ_BYTES+=len(b)
    if READ_BYTES>MAX_TOTAL:raise ValueError('bounded metadata total exceeded')
    READS[str(p)]={'path':str(p),'bytes':len(b),'sha256':h}
    return json.loads(b)
def refread(r,cap=2*1024*1024):
    return read(r['path'],r.get('sha256'),cap)
def write(name,obj):
    p=OUT/name
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def valtag(x, positive, zero, unknown='UNKNOWN'):
    if x is None:return unknown
    return positive if x>0 else zero
def classify(w,v,mode,accepted=True):
    if not accepted:return {'W':'UNACCEPTED','V':'UNACCEPTED','program_sector_temporal_reuse':'UNKNOWN'}
    wc=w.get('wb_created'); q=v.get('directory_queries'); rr=v.get('read_responses')
    cp=[w.get('logical_copy_reads'),w.get('logical_copy_writes')]
    return {
      'W':valtag(wc,'WB_WORK_OBSERVED','WB_ZERO_OBSERVED'),
      'W_copy': 'COPY_WORK_OBSERVED' if any(x is not None and x>0 for x in cp) else ('COPY_ZERO_OBSERVED' if all(x==0 for x in cp) else 'UNKNOWN'),
      'V': 'NOT_APPLICABLE' if mode in ('S','W_ONLY') else valtag(rr,'RETAINED_SECTOR_SERVICE_OBSERVED','VICTIM_RESPONSE_ZERO_OBSERVED'),
      'WAD_capacity':valtag(w.get('head_waits',{}).get('WAD_FULL',{}).get('blocked_observations_over_slices'),'WAD_CAPACITY_REFUSAL_OBSERVED','WAD_REFUSAL_ZERO_OBSERVED'),
      'V_bank_wait':valtag(v.get('bank_wait_cycles'),'V_BANK_SERVICE_WAIT_OBSERVED','V_BANK_SERVICE_WAIT_ZERO_OBSERVED'),
      'V_query': 'NOT_APPLICABLE' if mode in ('S','W_ONLY') else valtag(q,'DIRECTORY_QUERY_COST_OBSERVED','DIRECTORY_QUERY_ZERO_OBSERVED'),
      'V_clean_retention':valtag(v.get('clean_retention_slot_cycles'),'CLEAN_RETENTION_OBSERVED','CLEAN_RETENTION_ZERO_OBSERVED'),
      'V_dirty_forward':valtag(v.get('dirty_forward_responses'),'MANDATORY_WB_FORWARD_OBSERVED','MANDATORY_WB_FORWARD_ZERO_OBSERVED'),
      'program_sector_temporal_reuse':'UNKNOWN',
      'post_eviction_reuse_distance_distribution':'UNKNOWN',
      'line_spatial_continuation_distribution':'UNKNOWN',
      'avoidable_DRAM_requests':'UNKNOWN',
      'application_critical_path_wait_cycles':'UNKNOWN'
    }
V_KEYS=['read_responses','dirty_forward_responses','served_sectors','served_sector_bytes','clean_installs','dirty_installs','promotions','directory_queries','lookup_wait_cycles','bank_wait_cycles','wb_wait_cycles','icnt_wait_cycles','clean_retention_slot_cycles','retention_slot_cycles','total_retention_slot_cycles']
WAIT_KEYS=['WAD_FULL','WB_DATA_SPACE','COPY_PIPELINE','DATA_SERVICE','BANK_COMPATIBLE_LANDING','SAME_ADDRESS_WB','PINNED_PAYLOAD','VICTIM_LOOKUP','RESPONSE_QUEUE_FULL']
def get_metrics(model,mode):
    mm=model.get('mechanism_metrics',{})
    tr=mm.get('trigger',{})
    w={k:model[k] for k in ('wb_created','wb_completed','wb_lower_accepted') if k in model}
    for k in ('logical_copy_reads','logical_copy_writes'):
        if k in tr:w[k]=tr[k]
    w['diagnostic_flags']=tr.get('diagnostic_flags',{})
    w['exempt_services']=tr.get('exempt_services',{})
    bn=mm.get('bottleneck',{})
    w['head_waits']={k:{kk:vv for kk,vv in val.items() if kk!='hist_log2'} for k,val in (bn.items() if isinstance(bn,dict) else []) if k in WAIT_KEYS and isinstance(val,dict)}
    rows=mm.get('full_mechanism_records',{}).get('victim',{})
    v={}
    if isinstance(rows,dict) and len(rows)==64 and {str(i) for i in range(64)}==set(rows):
        for k in V_KEYS:
            if all(k in row and isinstance(row[k],int) for row in rows.values()):
                v[k]=sum(row[k] for row in rows.values())
    status='OBSERVED_FINAL_64_SLICE_CUMULATIVE' if v else ('NOT_APPLICABLE' if mode in ('S','W_ONLY') else 'NOT_COLLECTED_OR_NOT_EMITTED')
    return w,v,status,mm.get('local_service',{})
def match_basis(e):
    return {'input_identity_sha256':e['input_identity_sha256'],'ordered_commands_canonical_sha256':e.get('ordered_commands_canonical_sha256'),'literal_commandlist_sha256':e.get('literal_commandlist_sha256'),'source5':e['source5'],'geometry':e.get('geometry'),'clock_domains':e.get('clock_domains'),'mode':e['mode'],'effective_options_sha256':e.get('effective_options_sha256'),'mode_feature_contract':e.get('mode_feature_contract'),'spec_ref':e['spec_ref']}
def guard_pair(a,b,allow):
    if not(a['accepted'] and b['accepted']):raise ValueError('unaccepted pair')
    for k in ('input_identity_sha256','ordered_commands_canonical_sha256','source5'):
        if a.get(k)!=b.get(k) or a.get(k) is None:raise ValueError('pair identity mismatch '+k)
    ao,bo=a['effective_options'],b['effective_options']
    diff={k:[ao.get(k),bo.get(k)] for k in sorted(set(ao)|set(bo)) if ao.get(k)!=bo.get(k)}
    if not set(diff)<=set(allow):raise ValueError('unreviewed option delta '+str(diff))
    return diff
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    old=read(OLD); index=read(INDEX)
    oldep={e['cohort']:e for r in old['rows'] for e in r.get('reference_endpoints',[])}
    endpoints=[]; rawindex={e['cohort']:e for e in index['endpoints']}
    for e in index['endpoints']:
        x={k:e.get(k) for k in ['cohort','program','uuid','accepted','registry_state','request_id','cycles','host_elapsed_seconds','estimated_wall_seconds','limits']}
        x.update(match_basis(e))
        x['identity_status']=e['identity_status'];x['source_refs']=e.get('source_refs',{})
        if not e['accepted']:
            x.update({'W':{},'V':{},'V_measurement_status':'UNACCEPTED','labels':classify({}, {},e['mode'],False),'measurement_confidence':'UNACCEPTED_NOT_SCIENCE'})
            endpoints.append(x);continue
        vr=e.get('source_refs',{}).get('validation_ref')
        if not vr:raise ValueError('accepted endpoint lacks sealed small validation')
        vd=refread(vr); model=vd.get('model',{})
        if model.get('cycles')!=e['cycles']:raise ValueError('cycles mismatch')
        if vd.get('input_identity_sha256')!=e['input_identity_sha256']:raise ValueError('input mismatch')
        w,v,status,local=get_metrics(model,e['mode'])
        oe=oldep.get(e['cohort'])
        if oe:
            if 'input_identity_sha256' in oe and oe['input_identity_sha256']!=e['input_identity_sha256']:
                raise ValueError('old join input mismatch')
            if canonical(oe['source_identity'])!=canonical(e['source_identity_original']):raise ValueError('source join mismatch')
            if oe['validation_ref']['sha256']!=vr['sha256']:raise ValueError('validation join mismatch')
            oldv=oe.get('V',{}).get('metrics',{})
            for k,z in oldv.items():
                if k in v and z!=v[k]:raise ValueError('old/new counter disagreement '+k)
            # Supplement historical non-aggregable WAD/occupancy fields by exact same immutable endpoint.
            for k in ['wad_max','c7d_wad_full_events','c7d_wad_hazard_events','WBUF_time_mean_over_slice_ticks','WBUF_peak_max_over_slices','WBUF_occupancy_denominator_slice_ticks','bank_logical_ops','bank_wait_cycles']:
                if k in oe.get('W',{}):w[k]=oe['W'][k]
        x.update({'W':w,'V':v,'V_measurement_status':status,
                  'lower_service':local,'payload_end_state':{k:model.get(k) for k in ['payload_capacity','payload_free','payload_roles']},
                  'labels':classify(w,v,e['mode']),
                  'measurement_confidence':'EXACT_ACCEPTED_INPUT_SOURCE_OPTIONS_SMALL_BUNDLE_PROJECTION',
                  'generalization_confidence':'UNKNOWN_OUTSIDE_THIS_INPUT_SOURCE_CONFIG',
                  'victim_semantics':'Successful real payload service and response enqueue for retained valid sectors; not avoided-DRAM count or all-program temporal-reuse histogram',
                  'wait_semantics':'Overlapping per-request/slice wait observations; no summation as application critical-path cycles',
                  'lower_service_semantics':'Lower enqueue/admission payload bytes; not completed DRAM bandwidth'})
        endpoints.append(x)
    endpointmap={x['cohort']:x for x in endpoints}
    # Exact same Source/input/ordered-command pair proofs. No performance-derived classification.
    comparisons=[]
    def pair(a,b,kind,allow):
        aa,bb=rawindex[a],rawindex[b];diff=guard_pair(aa,bb,allow)
        comparisons.append({'kind':kind,'baseline':a,'candidate':b,'baseline_cycles':aa['cycles'],'candidate_cycles':bb['cycles'],'saved_cycles':aa['cycles']-bb['cycles'],'cycle_reduction_percent':100*(aa['cycles']-bb['cycles'])/aa['cycles'],'option_delta':diff,'exact_input_sha':aa['input_identity_sha256'],'ordered_commands_canonical_sha256':aa['ordered_commands_canonical_sha256'],'source5':aa['source5'],'baseline_ref':aa['spec_ref'],'candidate_ref':bb['spec_ref'],'performance_is_validation_not_class_definition':True})
    geometry=['-gpgpu_cache:dl2']
    mode=['-gpgpu_ep_l2_payload_mode','-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty']
    # These exact configurations differ only in actual declared geometry or finite W/V mode.
    for a,b in [
      ('EP_PERF_STENCIL_BD0309DF_S_REF_V1','EP_PERF_PFV4_A1_STENCIL_S_G64W8_V1'),
      ('EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO','EP_PERF_PFV4_A1_STENCIL_WV_ZERO_RO_G64W8_V1'),
      ('EP_PERF_3MM_F9F80028_S_REF_V1','EP_PERF_PFV4_A2_3MM_S_G64W8_V1'),
      ('EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1'),
      ('EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1','EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1'),
      ('EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1','EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1'),
      ('EP_PERF_GEMM_140F6ED3_S_REF_V1','EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1'),
      ('EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1','EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1')]:
        pair(a,b,'GEOMETRY_CAPACITY_SUBSTITUTION',geometry)
    for a,b in [
      ('EP_PERF_STENCIL_BD0309DF_S_REF_V1','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO'),
      ('EP_PERF_PFV4_A1_STENCIL_S_G64W8_V1','EP_PERF_PFV4_A1_STENCIL_WV_ZERO_RO_G64W8_V1'),
      ('EP_PERF_3MM_F9F80028_S_REF_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1'),
      ('EP_PERF_PFV4_A2_3MM_S_G64W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1'),
      ('EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1','EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1'),
      ('EP_PERF_GEMM_140F6ED3_S_REF_V1','EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1'),
      ('EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1','EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1')]:
        pair(a,b,'S_VS_WV_W_PLUS_V_NOT_V_ISOLATED',mode)
    for a,b in [
      ('EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_W_ONLY','EP_PERF_V2_PROPOSED_STENCIL_BD0309DF_WV_ZERO_RO'),
      ('EP_PERF_V2_PROPOSED_FASTWALSHTRANSFORM_FC3A9062_W_ONLY','EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1'),
      ('EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1')]:
        pair(a,b,'CONTROLLED_V_ENABLE_OVER_W_ONLY',['-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty'])
    # Explicit new-Source FWT candidate switch comparison; never compare newSource to oldSource for candidate effect.
    off='EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1';on='EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1'
    coldkeys={k for k in set(rawindex[off]['effective_options'])|set(rawindex[on]['effective_options']) if rawindex[off]['effective_options'].get(k)!=rawindex[on]['effective_options'].get(k)}
    if len(coldkeys)!=1 or not any('cold' in k for k in coldkeys):raise ValueError('unexpected cold switch')
    pair(off,on,'NEW_SOURCE_MATCHED_COLD_FILTER_NEGATIVE_RESULT',coldkeys)
    rows=[]
    for r in old['rows']:
        es=[e for e in endpoints if e['input_identity_sha256'] and e['input_identity_sha256']==r.get('input_identity_sha256')]
        accepted=[e for e in es if e['accepted']]
        positive=[e for e in accepted if e['labels']['V']=='RETAINED_SECTOR_SERVICE_OBSERVED']
        zeros=[e for e in accepted if e['labels']['V']=='VICTIM_RESPONSE_ZERO_OBSERVED']
        rows.append({'program':r['program'],'program_id':r['program_id'],'input_identity_sha256':r.get('input_identity_sha256'),'member_ordinary96':r['member_ordinary96'],'member_main35':r['member_main35'],'member_main42':r['member_main42'],'accepted_endpoint_count':len(accepted),'unaccepted_endpoint_count':len(es)-len(accepted),'endpoint_cohorts':[e['cohort'] for e in es],'victim_service_contexts':[e['cohort'] for e in positive],'victim_zero_contexts':[e['cohort'] for e in zeros],'evidence_summary':'SCOPED_V_SERVICE_AND_ZERO_CONTEXTS' if positive and zeros else ('SCOPED_V_SERVICE_OBSERVED' if positive else ('SCOPED_V_ZERO_OBSERVED' if zeros else 'UNKNOWN')),'program_sector_temporal_reuse':'UNKNOWN','post_eviction_reuse_distance_distribution':'UNKNOWN','program_reuse_opportunity':'RETAINED_SECTOR_REVISIT_LOWER_BOUND_OBSERVED' if positive else 'UNKNOWN_NOT_PROVEN_ABSENT','actual_EP_utilization':'CONTEXT_SPECIFIC_REFER_TO_ENDPOINTS' if accepted else 'UNKNOWN','historical_reuse_identity':r['historical_reuse_mapping'],'gaps':['Full-population sector temporal/spatial separation and post-eviction recency not measured for this exact Source78 identity','Victim response is not a counterfactual avoided-DRAM count','Any unmeasured Source/config remains UNKNOWN']})
    out={'schema':'UNIFIED_MEMORY_TAXONOMY_AGENT_C_WV_EVIDENCE_V1','row_count':len(rows),'original_population_definition':{'rows':103,'content_groups':96,'main35':35,'main42':42,'unresolved_slots':7},'model_starts':0,'budget_consumption':0,'raw_or_trace_body_reads':0,'rows':rows,'endpoints':endpoints,'comparisons':comparisons,'thresholds':{'RETAINED_SECTOR_SERVICE_OBSERVED':'accepted complete endpoint; read_responses > 0 after real retained-payload service and enqueue','VICTIM_RESPONSE_ZERO_OBSERVED':'accepted complete V-enabled endpoint; 64 final slice counters explicitly sum to read_responses = 0','WB_WORK_OBSERVED':'accepted complete endpoint; wb_created > 0','WB_CAPACITY_REFUSAL':'head_waits.WAD_FULL distinct/observations > 0 only; never infer pressure from WB count alone','UNKNOWN':'missing/not-emitted/disabled/unaccepted/outside exact identity; missing is never zero'},'global_limitations':['No acceleration used to define favorable reuse','No historical Motivation/Streaming identity-unresolved feature merged into Source78','No occupancy peaks summed across slices','No query/response/installation denominators treated as interchangeable','No sum of overlapping waits treated as GPU critical path','No completed DRAM bandwidth inferred from lower admission bytes']}
    out['counts']={'accepted_endpoints':sum(e['accepted'] for e in endpoints),'unaccepted_endpoints':sum(not e['accepted'] for e in endpoints),'rows_with_accepted_results':sum(r['accepted_endpoint_count']>0 for r in rows),'rows_with_positive_V_service_context':sum(bool(r['victim_service_contexts']) for r in rows),'rows_with_explicit_zero_V_service_context':sum(bool(r['victim_zero_contexts']) for r in rows),'accepted_endpoints_with_V_counts':sum(e.get('V_measurement_status')=='OBSERVED_FINAL_64_SLICE_CUMULATIVE' for e in endpoints),'exact_pair_comparisons':len(comparisons)}
    write('WV_REUSE_EVIDENCE_BY_INPUT.json',out)
    write('SOURCE_READ_MANIFEST.json',{'schema':'BOUNDED_SEALED_METADATA_READS_V1','total_bytes_read':READ_BYTES,'files':list(READS.values()),'raw_trace_reads':0})
    with (OUT/'WV_REUSE_COMPACT.csv').open('w',newline='') as f:
        fields=['program','program_id','input_identity_sha256','accepted_endpoint_count','unaccepted_endpoint_count','evidence_summary','program_reuse_opportunity','program_sector_temporal_reuse','actual_EP_utilization']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:r[k] for k in fields})
    print(json.dumps(out['counts']))
if __name__=='__main__':main()
