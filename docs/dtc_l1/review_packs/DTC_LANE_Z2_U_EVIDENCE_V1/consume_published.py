#!/usr/bin/env python3
"""Read fixed published Git evidence only. No raw/PID/process/simulator access.
Usage: python3 <this file> [--check]. Writes only this Z2 pack; never V1.
"""
import csv
from decimal import Decimal, getcontext
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent
R = P.parents[3]
V1 = R/'docs/dtc_l1/review_packs/DTC_LANE_Z_FLUSH_MECHANISM_V1'
BASE = 'ccf208c723f44387160c0edfe9e4d56855dfbafd'
CHECK = sys.argv[1:] == ['--check']
assert sys.argv[1:] in ([], ['--check'])
getcontext().prec = 40
REF = {'U':'16e56912cfd02f2311a1603a29415dee829fd495',
       'T':'f520a445436b57c0a0f2494fb858a1636f04d2bc',
       'V':'26abd496417d9392245052e54fbd9ba27c6ffd96'}
ROOT = {'U':'docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1/',
        'T':'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/',
        'V':'docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/'}
ALLOW = {
 'U':['LATEST_REPORT.md','FULL_MATRIX.tsv','STRICT_AUDIT.json','FINAL_CONTRACT_AUDIT.json',
      'TERMINAL_MECHANISM_COMPARISON.tsv','TERMINAL_METRIC_DEFINITIONS.md',
      'METRIC_COMPARABILITY_EVIDENCE.json','FILES_SHA256.tsv','PRE_REGISTRATION.tsv',
      'PUBLICATION_CONTRACT.md','CONTENT_PUBLICATION_FETCH_BACK.json',
      'strict/0a035532-7456-4041-b04c-76c440f5a051.strict.json',
      'strict/92557e3d-0d57-4166-b2bc-5c610a93c523.strict.json',
      'run_receipts/0a035532-7456-4041-b04c-76c440f5a051/RUN_TERMINAL.json',
      'run_receipts/92557e3d-0d57-4166-b2bc-5c610a93c523/RUN_TERMINAL.json'],
 'T':['LATEST_REPORT.md','FULL_MATRIX.tsv','TERMINAL_MECHANISM_COMPARISON.tsv',
      'TERMINAL_METRIC_DEFINITIONS.md','FILES_SHA256.tsv','FINAL_IDENTITY_AUDIT.json',
      'PRE_REGISTRATION.tsv','strict/4c8355b5-1c17-4c0e-8b99-bbad03b56652.strict.json',
      'strict/63f15c5a-a731-4c07-a3ce-c65312142a50.strict.json'],
 'V':['K1_SEMANTIC_CONTRACT.md','SOURCE_EVENT_MAP.md','SOURCE_SHA256.tsv','OPEN_QUESTIONS.md','CPU_CHECKS.json'],
}
def sha(b): return hashlib.sha256(b).hexdigest()
def git(*args): return subprocess.check_output(['git','-C',str(R),*args])
def put(name, data):
    if isinstance(data,str): data=data.encode()
    dest=P/name
    if CHECK: assert dest.read_bytes()==data, 'changed generated output: '+name
    else:
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
def table(rows):
    s=io.StringIO();w=csv.DictWriter(s,list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows);return s.getvalue()
cache={};sources=[];checks=[]
def test(name, ok):
    assert ok,name
    checks.append({'check':name,'pass':True})
def fetch(lane,name):
    assert name in ALLOW[lane], 'outside published-file allowlist'
    key=(lane,name)
    if key not in cache:
        b=git('show',REF[lane]+':'+ROOT[lane]+name)
        assert len(b)<1_000_000, 'small-evidence bound'
        cache[key]=b;put('sources/'+lane+'/'+name,b)
        sources.append({'lane':lane,'commit':REF[lane],'path':ROOT[lane]+name,'bytes':len(b),'sha256':sha(b)})
    return cache[key]
def obj(lane,name): return json.loads(fetch(lane,name))
def rows(lane,name): return list(csv.DictReader(io.StringIO(fetch(lane,name).decode()),delimiter='\t'))

# Validate preservation without executing V1's consumer or rewriting any V1 file.
v1_rel=str(V1.relative_to(R))
v1_files=git('ls-tree','-r','--name-only',BASE,'--',v1_rel).decode().splitlines()
for f in v1_files: test('V1_preserve:'+f,git('show',BASE+':'+f)==(R/f).read_bytes())
defs=list(csv.DictReader((V1/'METRIC_DEFINITIONS.tsv').open(),delimiter='\t'))
old=list(csv.DictReader((V1/'OLD_ACCEPTED_EVIDENCE.tsv').open(),delimiter='\t'))
v1_validation=json.loads((V1/'CPU_CONSUMER_VALIDATION.json').read_text())
test('V1_78_fields_2790_rows_413_checks',len(defs)==78 and len(old)==2790 and len(v1_validation['checks'])==413)
definition={d['field']:d for d in defs}

# Read the complete published report/matrix/audits before any mechanism data.
fetch('U','LATEST_REPORT.md');u_full=rows('U','FULL_MATRIX.tsv')
u_strict=obj('U','STRICT_AUDIT.json');u_contract=obj('U','FINAL_CONTRACT_AUDIT.json')
test('U_fixed_two_strict_pass',u_strict['registered']==u_strict['actual_new_starts']==u_strict['strict_pass']==2)
test('U_terminal_contract_published',u_contract['status']=='PASS_TERMINAL_CONTRACT_AND_IDENTITY_AUDIT' and
     len(u_contract['points'])==2 and all(x['status']=='PASS_STRICT_HOLDOUT_SCOPE' and x['terminal_utc'] for x in u_contract['points']))
for lane,names in ALLOW.items():
    for name in names: fetch(lane,name)
for lane in ['U','T']:
    manifest={r['path']:r for r in rows(lane,'FILES_SHA256.tsv')}
    for name in ALLOW[lane]:
        if name=='FILES_SHA256.tsv': continue
        m=manifest[name]
        test(lane+'_published_manifest:'+name,m['sha256']==sha(fetch(lane,name)) and int(m['bytes'])==len(fetch(lane,name)))

u_mech=rows('U','TERMINAL_MECHANISM_COMPARISON.tsv')
u_raw=obj('U','METRIC_COMPARABILITY_EVIDENCE.json')
t_mech=rows('T','TERMINAL_MECHANISM_COMPARISON.tsv')
t_full=rows('T','FULL_MATRIX.tsv');t_pre={r['attempt_uuid']:r for r in rows('T','PRE_REGISTRATION.tsv')}
test('U_six_complete_arms',len(u_full)==len(u_mech)==6)
test('T_original_fixed_candidate_no_reselection',len(t_full)==7 and obj('T','FINAL_IDENTITY_AUDIT.json')['strict_pass']==7)

MAP={
 'cycles':'cycles','active_instructions':'active_thread_instructions',
 'accepted_128b_reference_count':'accepted_reference_count',
 'ready_reference_outcomes':'ready_hit_events','pending_reference_outcomes':'pending_merge_events',
 'new_allocation_outcomes':'cacheable_new_line_requests','dtc_lower_created':'lower_created',
 'ready_fraction':'ready_fraction','pending_fraction':'pending_fraction','new_fraction':'new_fraction',
 'tag_evictions':'tag_evictions','fully_ready_cacheable_retired':'service_retired',
 'all64sm_cycle_mean_pib':'mean_PIB_all64_SM_cycles','all64sm_cycle_mean_physical':'mean_physical_all64_SM_cycles',
 'ready_to_collect_per_cacheable_warp':'mean_ready_to_collect','collection_per_cacheable_warp':'mean_collect',
 'wb_wait_per_cacheable_warp':'mean_post_collect_WB','fully_ready_to_complete_per_cacheable_warp':'mean_ready_to_complete',
 'mean_completed_map_loss_to_free':'mean_map_loss_to_free','collected_sectors':'service_collected_sectors',
}
for f in ['L2_read_sectors','L2_read_hits','L2_read_pending_hits','L2_read_misses','L2_read_sector_misses',
          'L2_read_reservation_retries','L2_read_requested_payload_bytes','DRAM_n_rd','DRAM_n_rd_L2_A',
          'DRAM_n_write','DRAM_n_wr_bk','DRAM_atom_bytes','DRAM_read_payload_bytes','DRAM_write_payload_bytes']:
    MAP[f]=f
SERVICES={f:f.replace('service_','DTC_SERVICE_V1_',1) for f in definition if f.startswith('service_')}
FIELDS=list(dict.fromkeys(list(MAP.values())+list(SERVICES)+['global_read_injected','global_write_injected',
    'terminal_queryable_mappings','terminal_lost_resident_allocations','kernel_boundary_invalidated_mappings']))
def missing(v): return str(v).startswith('UNAVAILABLE')
evidence=[]; runs=[];crosswalk=[]
for source,f in MAP.items():
    d=definition[f]
    crosswalk.append({'source_field':source,'Z_V1_metric_id':f,'V1_type':d['value_type'],'unit':d['typed_unit'],
        'denominator_contract':d['denominator'],'OO_same_path':'COMPARABLE_WITH_SAME_IDENTITY_SCOPE',
        'cross_CPLUS':'COMPARABLE_WHOLE_RUN' if f in ['cycles','active_thread_instructions'] else
            'COMPARABLE_U_L2_DRAM_TYPED_PATH' if f.startswith(('L2_','DRAM_')) else 'UNCOMPARABLE_DTC_VS_CONVENTIONAL',
        'source_contract':'V1 dictionary + published U/T terminal definitions; no alias changes to V1'})
for f,raw in SERVICES.items():
    crosswalk.append({'source_field':raw,'Z_V1_metric_id':f,'V1_type':definition[f]['value_type'],
        'unit':definition[f]['typed_unit'],'denominator_contract':definition[f]['denominator'],
        'OO_same_path':'COMPARABLE_FINAL_SNAPSHOT','cross_CPLUS':'UNAVAILABLE_DTC_SERVICE_PATH',
        'source_contract':'U published comparator raw_scalars / T published strict base.service_metrics'})
for f,raw in [('global_read_injected','gpgpu_n_mem_read_global'),('global_write_injected','gpgpu_n_mem_write_global')]:
    crosswalk.append({'source_field':raw,'Z_V1_metric_id':f,'V1_type':definition[f]['value_type'],
        'unit':definition[f]['typed_unit'],'denominator_contract':'1 packet count; if normalized use same-run active-thread instructions',
        'OO_same_path':'SUCCESSFUL_ICNT_INJECTION','cross_CPLUS':'COMMON_SUCCESSFUL_INJECTION_BOUNDARY_U_PROOF',
        'source_contract':'Published U raw_scalars; not lower-created, not retry, not DRAM bytes'})
put('METRIC_CROSSWALK.tsv',table(crosswalk))

def register(lane,r,role,cohort,primary='TERMINAL_MECHANISM_COMPARISON.tsv'):
    uuid=r['uuid'];values={f:'UNAVAILABLE_NOT_PUBLISHED_IN_SELECTED_TYPED_EVIDENCE' for f in FIELDS}
    origin={}
    for src,f in MAP.items():
        if src in r: values[f]=r[src];origin[f]=(primary,'uuid:'+uuid+':'+src,src)
    if primary=='PRE_REGISTRATION.tsv':
        for f,raw in [('cycles','original_cplus_cycles'),('active_thread_instructions','instructions')]:
            origin[f]=('FULL_MATRIX.tsv','attempt_uuid:'+r['_fixed_uuid']+':'+raw,raw)
    if lane=='U':
        e=u_raw[uuid];raw=e['raw_scalars'];raw_file='METRIC_COMPARABILITY_EVIDENCE.json'
        test('U_'+uuid+'_stdout_binding',e['identity']['raw_stdout']['sha256']==r['source_stdout_sha256'])
        scope=e['identity']['ordered_scope']
        test('U_'+uuid+'_kernel_order_whole',sum(k['cycles'] for k in scope)==int(r['cycles']) and
             sum(k['instructions'] for k in scope)==int(r['active_instructions']))
    elif role=='T1C':
        raw_file='strict/'+uuid+'.strict.json';s=obj('T',raw_file)
        raw=json.loads(s['base']['service_metrics'])
        test('T_'+uuid+'_strict_hash',s['base']['stdout_sha256']==r['source_stdout_sha256'])
    else: raw={};raw_file=primary
    for f,src in SERVICES.items():
        if src in raw: values[f]=raw[src];origin[f]=(raw_file,'uuid:'+uuid+':'+src,src)
    for f,src in [('global_read_injected','gpgpu_n_mem_read_global'),('global_write_injected','gpgpu_n_mem_write_global')]:
        if src in raw: values[f]=raw[src];origin[f]=(raw_file,'uuid:'+uuid+':raw_scalars.'+src,src)
    if role!='CPLUS':
        D=sum(int(values[f]) for f in ['ready_hit_events','pending_merge_events','cacheable_new_line_requests'])
        test(lane+'_'+uuid+'_reference_balance',D==int(values['accepted_reference_count'])==int(r['completion_dependency_count']))
        for f,num in [('ready_fraction','ready_hit_events'),('pending_fraction','pending_merge_events'),('new_fraction','cacheable_new_line_requests')]:
            test(lane+'_'+uuid+'_'+f,abs(float(values[f])-int(values[num])/D)<1e-14)
    if not missing(values['service_samples']):
        test(lane+'_'+uuid+'_all64SM_samples',int(values['service_samples'])==64*int(values['cycles']))
        test(lane+'_'+uuid+'_post_ready_sum',int(values['service_fully_ready_to_complete_sum'])==sum(int(values[f]) for f in
             ['service_ready_to_collect_sum','service_collection_cycles','service_wb_wait']))
        for mean,numerator,denominator in [
            ('mean_PIB_all64_SM_cycles','service_pib_integral','service_samples'),
            ('mean_physical_all64_SM_cycles','service_physical_integral','service_samples'),
            ('mean_ready_to_collect','service_ready_to_collect_sum','service_retired'),
            ('mean_collect','service_collection_cycles','service_retired'),
            ('mean_post_collect_WB','service_wb_wait','service_retired'),
            ('mean_ready_to_complete','service_fully_ready_to_complete_sum','service_retired'),
            ('mean_map_loss_to_free','service_map_loss_to_free_sum','service_map_loss_to_free_count')]:
            test(lane+'_'+uuid+'_'+mean+'_denominator',abs(float(values[mean])-
                 int(values[numerator])/int(values[denominator]))<1e-8)
    if lane=='U':
        test('U_'+uuid+'_typed_L2_DRAM_path',r['L2_DRAM_comparability']=='PASS_SAME_PATH_TYPED_DEFINITIONS')
        test('U_'+uuid+'_L2_sector32',int(values['L2_read_requested_payload_bytes'])==32*int(values['L2_read_sectors']))
        test('U_'+uuid+'_L2_four_buckets',int(values['L2_read_sectors'])==sum(int(values[f]) for f in
             ['L2_read_hits','L2_read_pending_hits','L2_read_misses','L2_read_sector_misses']))
        for f in ['DRAM_n_rd','DRAM_n_rd_L2_A','DRAM_n_write','DRAM_n_wr_bk']:
            test('U_'+uuid+'_'+f+'_controllers',int(values[f])==sum(x[f.removeprefix('DRAM_')] for x in e['dram_final_controller_counters'].values()))
        test('U_'+uuid+'_DRAM_read_bytes',int(values['DRAM_read_payload_bytes'])==32*(int(values['DRAM_n_rd'])+int(values['DRAM_n_rd_L2_A'])))
        test('U_'+uuid+'_DRAM_write_bytes',int(values['DRAM_write_payload_bytes'])==32*(int(values['DRAM_n_write'])+int(values['DRAM_n_wr_bk'])))
        test('U_'+uuid+'_atom32',int(values['DRAM_atom_bytes'])==32)
    for f in FIELDS:
        value=values[f];srcfile,pointer,rawfield=origin.get(f,(primary,'uuid:'+uuid+':not-published',f))
        denom='1'
        if f.endswith('_fraction'): denom=values['accepted_reference_count']
        if f in ['mean_PIB_all64_SM_cycles','mean_physical_all64_SM_cycles']:
            denom=values['service_samples'] if not missing(values['service_samples']) else '64SM * '+str(values['cycles'])+' core-cycles (published normalization contract)'
        if f in ['mean_ready_to_collect','mean_collect','mean_post_collect_WB','mean_ready_to_complete']: denom=values['service_retired']
        if f=='mean_map_loss_to_free': denom=values['service_map_loss_to_free_count']
        comparable=('WHOLE_RUN_SAME_INPUT' if f in ['cycles','active_thread_instructions'] else
            'U_TYPED_L2_DRAM_CPLUS_COMPARABLE' if lane=='U' and f.startswith(('L2_','DRAM_')) else
            'U_COMMON_SUCCESSFUL_INJECTION_CPLUS_COMPARABLE' if lane=='U' and f in ['global_read_injected','global_write_injected'] else
            'DTC_SAME_PATH_ONLY_CPLUS_UNCOMPARABLE')
        status='UNAVAILABLE' if missing(value) else 'AVAILABLE'
        if role=='CPLUS' and comparable=='DTC_SAME_PATH_ONLY_CPLUS_UNCOMPARABLE':
            status='UNAVAILABLE_DTC_FIELD_CROSS_PATH_UNCOMPARABLE'
        evidence.append({'cohort':cohort,'workload':r['workload'],'role':role,'uuid':uuid,'source_lane':lane,
            'source_commit':REF[lane],'source_path':ROOT[lane]+srcfile,'source_blob_sha256':sha(fetch(lane,srcfile)),
            'source_pointer':pointer,'stdout_sha256':r['source_stdout_sha256'],'metric_id':f,'value':value,
            'value_type':definition[f]['value_type'],'unit':definition[f]['typed_unit'],'denominator':denom,
            'scope':'WHOLE_RUN_FINAL_CUMULATIVE_NOT_SUM_OF_KERNEL_SNAPSHOTS','status':status,
            'comparison_domain':comparable,'raw_field':rawfield})
    runs.append({'lane':lane,'row':r,'role':role,'cohort':cohort,'values':values})

for r in u_mech:
    role={'ORIGINAL_OO128':'OLD_OO','FIXED_T1C':'T1C','ORIGINAL_CPLUS':'CPLUS'}[r['point']]
    match=next(x for x in u_full if x['attempt_uuid']==r['uuid'])
    test('U_'+r['uuid']+'_matrix_identity',match['stdout_sha256']==r['source_stdout_sha256'] and match['cycles']==r['cycles'])
    if role=='T1C':
        s=obj('U','strict/'+r['uuid']+'.strict.json');term=obj('U','run_receipts/'+r['uuid']+'/RUN_TERMINAL.json')
        test('U_'+r['uuid']+'_natural_exit',term['exit_status']==0 and term['termination_reason']=='NATURAL_PROCESS_RETURN')
        test('U_'+r['uuid']+'_strict_pass',all(s['checks'].values()) and sha(fetch('U','strict/'+r['uuid']+'.strict.json'))==match['strict_sha256'])
    register('U',r,role,'FIXED_HOLDOUT')
for workload in ['GEMM','Gaussian']:
    for role in ['OLD_OO','T1C']:
        r=next(x for x in t_mech if x['workload']==workload and x['point']==('T1-C' if role=='T1C' else 'accepted_'+workload+'_OO128'))
        register('T',r,role,'DISCOVERY')
    fixed=next(x for x in t_full if x['workload']==workload and x['candidate']=='T1-C')
    pre=t_pre[fixed['attempt_uuid']]
    r={'workload':workload,'uuid':pre['original_cplus_uuid'],'cycles':fixed['original_cplus_cycles'],
       'active_instructions':fixed['instructions'],'source_stdout_sha256':pre['original_cplus_stdout_sha256'],
       '_fixed_uuid':fixed['attempt_uuid']}
    register('T',r,'CPLUS','DISCOVERY',primary='PRE_REGISTRATION.tsv')

def pct(new,old):
    if missing(new) or missing(old): return 'UNAVAILABLE'
    if Decimal(str(old))==0: return 'UNDEFINED_ZERO_DENOMINATOR'
    return str((Decimal(str(new))/Decimal(str(old))-1)*100)
comparisons=[]
COMPARE=['cycles','lower_created','global_read_injected','ready_fraction','pending_fraction',
         'mean_PIB_all64_SM_cycles','mean_physical_all64_SM_cycles','mean_ready_to_collect',
         'mean_collect','mean_ready_to_complete','mean_map_loss_to_free','L2_read_sectors',
         'L2_read_reservation_retries','DRAM_read_payload_bytes','DRAM_write_payload_bytes']
for workload in ['GEMM','Gaussian','DWT2D','BICG']:
    selected={x['role']:x for x in runs if x['row']['workload']==workload}
    a,b,c=(selected[k] for k in ['OLD_OO','T1C','CPLUS'])
    out={'workload':workload,'cohort':b['cohort'],'comparison':'OLD_OO32x4_TO_FIXED_T1C64x8',
         'old_OO_uuid':a['row']['uuid'],'T1C_uuid':b['row']['uuid'],'CPLUS_uuid':c['row']['uuid'],
         'source_commit':REF[b['lane']],'old_over_new_cycle_speed_ratio':str(Decimal(a['row']['cycles'])/Decimal(b['row']['cycles'])),
         'CPLUS_cycles':c['row']['cycles'],'T1C_cycles_vs_CPLUS_pct':pct(b['row']['cycles'],c['row']['cycles']),
         'CPLUS_metric_boundary':'Cycles comparable same full input; DTC ready/service fields UNCOMPARABLE; U L2/DRAM separately typed',
         'causality':'DESCRIPTIVE_COVARIATION_NOT_ADDITIVE_GPU_CYCLE_ATTRIBUTION'}
    for f in COMPARE:
        oldv=a['values'][f];newv=b['values'][f]
        out[f+'_old']=oldv;out[f+'_new']=newv;out[f+'_change_pct']=pct(newv,oldv)
    test(workload+'_post_ready_opposite_direction_preserved',int(b['row']['cycles'])<int(a['row']['cycles']) and
         float(b['values']['mean_ready_to_complete'])>float(a['values']['mean_ready_to_complete']))
    comparisons.append(out)
test('exactly_four_individual_comparisons',len(comparisons)==4)
bicg=next(x for x in comparisons if x['workload']=='BICG')
test('BICG_negative_CPLUS_preserved',abs(Decimal(bicg['T1C_cycles_vs_CPLUS_pct'])-Decimal('62.334259491238456'))<Decimal('1e-12'))
test('BICG_lower_small_DRAM_cycle_large',abs(Decimal(bicg['lower_created_change_pct']))<Decimal('0.2') and
     Decimal(bicg['DRAM_read_payload_bytes_change_pct'])<Decimal('-18') and Decimal(bicg['cycles_change_pct'])<Decimal('-13'))
put('U_T_TYPED_EVIDENCE.tsv',table(evidence));put('FOUR_INPUT_DESCRIPTIVE_COMPARISON.tsv',table(comparisons))
put('SOURCE_BLOBS_SHA256.tsv',table(sources))
validation={'status':'PASS_PUBLISHED_U_T_TYPED_CONSUMER_V1_PRESERVED',
    'fixed_commits':REF,'V1_commit':BASE,'V1_preserved_files':len(v1_files),'V1_fields':78,'V1_rows':2790,'V1_checks_preserved':413,
    'Z2_checks':checks,'typed_evidence_rows':len(evidence),'point_runs_including_CPLUS':len(runs),'individual_comparisons':4,
    'source_blobs':len(sources),'old_raw_reads':0,'background_PID_or_progress_probes':0,'partial_performance_reads':0,
    'new_factorial_performance_reads':0,'simulations':0,'Core_edits':0,'paper_edits':0,'new_overall_GM':False,
    'scope':'Revalidates completed published Git extracts, not fresh raw/strict execution.',
    'consumer_sha256':sha(Path(__file__).read_bytes()),
    'K1_V2_document_sha256':sha((P/'K1_INTERPRETATION_V2.md').read_bytes())}
put('CPU_CONSUMER_VALIDATION.json',json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
if CHECK:
    manifest=list(csv.DictReader((P/'FILES_SHA256.tsv').open(),delimiter='\t'))
    actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f!=P/'FILES_SHA256.tsv'}
    assert actual=={x['path'] for x in manifest}
    for x in manifest:
        b=(P/x['path']).read_bytes();assert len(b)==int(x['bytes']) and sha(b)==x['sha256'],x['path']
print(json.dumps({k:validation[k] for k in ['status','typed_evidence_rows','individual_comparisons','source_blobs']}))
