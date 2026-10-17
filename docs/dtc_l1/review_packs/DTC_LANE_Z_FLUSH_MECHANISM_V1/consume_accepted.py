#!/usr/bin/env python3
"""CPU-only immutable Git small-evidence consumer. No simulator/raw/process APIs.

Run from this worktree: python3 <this script> [--check]
Writes only inside this review pack; --check compares deterministic outputs.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

PACK = Path(__file__).resolve().parent
REPO = PACK.parents[3]
CHECK = sys.argv[1:] == ['--check']
assert sys.argv[1:] in ([], ['--check'])
REFS = {
    'A': 'f5c37d6edcce832a72cb0830021bffa78df6cc13',
    'M': 'd723784a8b897566b63113f95972f7a8d12a01ce',
    'T': 'f520a445436b57c0a0f2494fb858a1636f04d2bc',
}
PREFIX = {
    'A': 'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/',
    'M': 'docs/dtc_l1/review_packs/DTC_MECHANISM_CPU_CONSUMER_V1/',
    'T': 'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/',
}
FILES = {
    'A': ['final_closure_v1/README.md', 'final_closure_v1/ORIGINAL12_COMPLETE_NUMERIC_TABLE.tsv',
          'final_closure_v1/FINAL_INTEGRITY_AUDIT_V1.json',
          'checkpoint_20261016T2133Z/RESIDENCE_AND_OCCUPANCY.tsv'],
    'M': ['FILES_SHA256.tsv', 'METRIC_DEFINITIONS.md', 'METRIC_DEFINITIONS.tsv',
          'MISSING_FIELDS.md', 'EXISTING_RUN_MECHANISM.tsv', 'COUNTER_EVIDENCE.json',
          'VALIDATION.json', 'SCOPE_AND_SAMPLING_AUDIT.json', 'DWT2D_READONLY_CHECK.json',
          'CONVENTIONAL_LOOKUP_CONTEXT.tsv', 'CONVENTIONAL_LOOKUP_DEFINITIONS.tsv',
          'SOURCE_SHA256.tsv', 'LATEST_REPORT.md'],
    'T': ['FILES_SHA256.tsv', 'FULL_MATRIX.tsv', 'TERMINAL_MECHANISM_COMPARISON.tsv',
          'TERMINAL_METRIC_DEFINITIONS.md', 'FINAL_IDENTITY_AUDIT.json',
          'ORDERED_KERNELS.json', 'PRE_REGISTRATION.tsv', 'LATEST_REPORT.md',
          'CONTENT_PUBLICATION_FETCH_BACK.json'],
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def tab(rows, fields):
    out = io.StringIO()
    w = csv.DictWriter(out, fields, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    return out.getvalue().encode()

def write(rel, data):
    target = PACK / rel
    if isinstance(data, str):
        data = data.encode()
    if CHECK:
        assert target.read_bytes() == data, f'nonreproducible: {rel}'
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

blobs = {}
source_rows = []
def fetch(lane, rel):
    assert lane in REFS and rel in FILES[lane], 'outside immutable allowlist'
    key = (lane, rel)
    if key not in blobs:
        path = PREFIX[lane] + rel
        data = subprocess.check_output(['git', '-C', str(REPO), 'show', REFS[lane] + ':' + path])
        assert len(data) < 1_000_000, 'small-evidence file bound'
        blobs[key] = data
        write('sources/' + lane + '/' + rel, data)
        source_rows.append(dict(lane=lane, commit=REFS[lane], source_path=path,
                                bytes=len(data), sha256=sha(data)))
    return blobs[key]

def js(lane, rel):
    return json.loads(fetch(lane, rel))

def tsv(lane, rel):
    return list(csv.DictReader(io.StringIO(fetch(lane, rel).decode()), delimiter='\t'))

for lane in FILES:
    for rel in FILES[lane]:
        fetch(lane, rel)

manifest_checks = []
for lane in ['M', 'T']:
    manifest = {r['path']: r for r in tsv(lane, 'FILES_SHA256.tsv')}
    for rel in FILES[lane]:
        if rel == 'FILES_SHA256.tsv':
            continue
        entry = manifest.get(PREFIX[lane] + rel) or manifest.get(rel)
        assert entry, (lane, rel, 'not in accepted manifest')
        assert entry['sha256'] == sha(fetch(lane, rel)), (lane, rel, 'accepted hash mismatch')
        assert int(entry['bytes']) == len(fetch(lane, rel))
        manifest_checks.append(lane + ':' + rel)

# Preserve M's exact typed contract, with explicit types and Z supplements.
definitions = tsv('M', 'METRIC_DEFINITIONS.tsv')
for d in definitions:
    f = d['field']
    d['value_type'] = ('string' if f in ['workload', 'arm', 'attempt_uuid'] else
                       'float64' if f.startswith('mean_') else 'uint64')

def supplement(field, unit, denominator, stage, scope, comparison, value_type='uint64'):
    definitions.append(dict(field=field, typed_unit=unit, numerator=field,
        denominator=denominator, logging_stage=stage, address_and_instruction_scope=scope,
        includes_retry='no', per_kernel_or_whole='terminal final only unless kernel ordinal explicit',
        comparability=comparison, source_location='METRIC_DEFINITIONS.md',
        source_SHA_binding='SOURCE_BLOBS_SHA256.tsv', explanation='Z V1 supplement; missing is never zero',
        source_SHA256='{}', value_type=value_type))

supplement('kernel_cycles', 'GPU core-cycle', '1', 'final gpu_sim_cycle for each original launch ordinal',
           'same original ordered kernel and stream', 'same ROI/config/observer; do not sort by kernel name')
supplement('accepted_reference_count', 'accepted logical128B references', '1', 'ready+pending+new',
           'finite cacheable load path', 'not conventional coalesced cache references')
supplement('lower_created', 'lower request creation events', '1', 'DTC lower-created / accepted new allocation',
           'cacheable finite load path', 'distinct from successful injection; no bytes inference')
for f in ['terminal_queryable_mappings', 'terminal_lost_resident_allocations', 'kernel_boundary_invalidated_mappings']:
    supplement(f, 'logical128B mapping/allocation events or terminal count', '1',
               'direct event/snapshot only; UNAVAILABLE in consumed old evidence',
               'line+generation and declared boundary', 'not physical integral / eviction / completed map-loss count')
for f in ['ready_fraction', 'pending_fraction', 'new_fraction']:
    supplement(f, 'fraction of accepted logical128B references', 'accepted_reference_count',
               'successful accepted outcome', 'finite cacheable load path', 'same reference scope only', 'float64')
byfield = {d['field']: d for d in definitions}
assert len(byfield) == len(definitions)
write('METRIC_DEFINITIONS.tsv', tab(definitions, list(definitions[0])))

evidence = []
identities = []
checks = []
def test(name, condition):
    assert condition, name
    checks.append(dict(check=name, pass_check=True))

def add(lane, rel, pointer, workload, arm, uuid, metric, value, *, ordinal='', kernel='',
        stream='', raw='', denominator='1', scope='WHOLE_RUN_FINAL_CUMULATIVE',
        status='', tag='UNAVAILABLE', qualification='ACCEPTED_SCOPE_ONLY'):
    assert metric in byfield, metric
    d = byfield[metric]
    status = status or ('UNAVAILABLE' if str(value).startswith('UNAVAILABLE') else 'AVAILABLE')
    if status == 'AVAILABLE':
        number = float(value)
        assert number >= 0, (metric, value)
        if d['value_type'] == 'uint64':
            assert int(value) == number
    evidence.append(dict(lane=lane, source_commit=REFS[lane], source_path=PREFIX[lane]+rel,
        source_blob_sha256=sha(fetch(lane, rel)), source_pointer=pointer,
        workload=workload, arm=arm, attempt_uuid=uuid, tag_sets_x_ways=tag,
        qualification=qualification, kernel_ordinal=ordinal, kernel_name=kernel, stream=stream,
        metric_id=metric, value=value, status=status, typed_unit=d['typed_unit'],
        denominator=denominator, scope=scope, raw_field=raw or metric,
        comparability=d['comparability']))

a_rel = 'final_closure_v1/ORIGINAL12_COMPLETE_NUMERIC_TABLE.tsv'
a_rows = tsv('A', a_rel)
test('A_all_original12_preserved', len(a_rows) == 12)
a_audit = js('A', 'final_closure_v1/FINAL_INTEGRITY_AUDIT_V1.json')
test('A_41_accepted_strict_scopes', len(a_audit['original41_full_strict_and_ordered_scope']) == 41)
a_accepted = {r['uuid']:r for r in a_audit['original41_full_strict_and_ordered_scope']}
for index, row in enumerate(a_rows, 1):
    for arm in ['B16-N', 'TC80-N', 'TRAD96', 'IO', 'OO']:
        value = row[arm+'_cycles'] or 'UNAVAILABLE_ADMISSION_HOLD'
        if row[arm+'_uuid'] in a_accepted:
            test('A_'+row[arm+'_uuid']+'_cycle_binding', int(value) == a_accepted[row[arm+'_uuid']]['cycles'])
        add('A', a_rel, f'row:{index}:{arm}_cycles', row['workload'], arm,
            row[arm+'_uuid'] or 'UNAVAILABLE', 'cycles', value,
            qualification=row['input_lineage'] + ';' + row['scientific_disposition'] + ';' + row[arm+'_status'])

m_rel = 'EXISTING_RUN_MECHANISM.tsv'
m_rows = tsv('M', m_rel)
m_counter = js('M', 'COUNTER_EVIDENCE.json')
test('M_accepted_counter_status', m_counter['status'] == 'PASS')
test('M_nine_fixed_runs', len(m_rows) == len(m_counter['runs']) == 9)
m_pairs = [(r, e, m_rel, f'row:{i}') for i, (r, e) in enumerate(zip(m_rows, m_counter['runs']), 1)]
dwt = js('M', 'DWT2D_READONLY_CHECK.json')
test('M_only_old_DWT2D', dwt['new_runs'] == 0 and dwt['new_candidate_performance_reads'] == 0)
for i, entry in enumerate(dwt['results']):
    m_pairs.append((entry['row'], entry['evidence'], 'DWT2D_READONLY_CHECK.json', f'results[{i}].row'))

def validate_metrics(r, prefix):
    def n(f): return int(r[f])
    test(prefix+'_L2_success_bucket_balance', n('L2_read_sectors') == sum(n(f) for f in
        ['L2_read_hits', 'L2_read_pending_hits', 'L2_read_misses', 'L2_read_sector_misses']))
    test(prefix+'_L2_sector32_payload', n('L2_read_requested_payload_bytes') == n('L2_read_sectors')*32)
    test(prefix+'_DRAM_atom32', n('DRAM_atom_bytes') == 32)
    test(prefix+'_DRAM_read_commands', n('DRAM_read_payload_bytes') == (n('DRAM_n_rd')+n('DRAM_n_rd_L2_A'))*32)
    test(prefix+'_DRAM_write_commands', n('DRAM_write_payload_bytes') == (n('DRAM_n_write')+n('DRAM_n_wr_bk'))*32)
    test(prefix+'_lower_final_balance', n('lower_credit_acquired') == n('lower_credit_released') == n('global_read_injected'))
    if str(r['service_samples']).startswith('UNAVAILABLE'):
        return
    test(prefix+'_all64SM_samples', n('service_samples') == 64*n('cycles'))
    test(prefix+'_post_ready_identity', n('service_fully_ready_to_complete_sum') ==
        n('service_ready_to_collect_sum')+n('service_collection_cycles')+n('service_wb_wait'))
    test(prefix+'_accepted_outcomes', sum(n(f) for f in ['ready_hit_events','pending_merge_events',
        'cacheable_new_line_requests']) > 0)
    for numerator, denominator, mean in [
        ('service_pib_integral','service_samples','mean_PIB_all64_SM_cycles'),
        ('service_physical_integral','service_samples','mean_physical_all64_SM_cycles'),
        ('service_ready_to_collect_sum','service_retired','mean_ready_to_collect'),
        ('service_collection_cycles','service_retired','mean_collect'),
        ('service_wb_wait','service_retired','mean_post_collect_WB'),
        ('service_fully_ready_to_complete_sum','service_retired','mean_ready_to_complete'),
        ('service_map_loss_to_free_sum','service_map_loss_to_free_count','mean_map_loss_to_free')]:
        test(prefix+'_'+mean, abs(float(r[mean])-n(numerator)/n(denominator)) < 1e-8)

for r, e, rel, pointer in m_pairs:
    ident = e['identity']
    uuid = r['attempt_uuid']
    test('M_'+uuid+'_UUID_binding', ident['uuid'] == uuid)
    scope = ident['ordered_scope']
    test('M_'+uuid+'_ordered_count', len(scope) == int(r['ordered_kernels']))
    test('M_'+uuid+'_kernel_cycle_total', sum(k['cycles'] for k in scope) == int(r['cycles']))
    test('M_'+uuid+'_instruction_total', sum(k['instructions'] for k in scope) == int(r['active_thread_instructions']))
    validate_metrics(r, 'M_'+uuid)
    for f in ['DRAM_n_rd','DRAM_n_rd_L2_A','DRAM_n_write','DRAM_n_wr_bk']:
        test('M_'+uuid+'_'+f+'_controller_sum', int(r[f]) ==
             sum(int(mc[f.removeprefix('DRAM_')]) for mc in e['dram_final_controller_counters'].values()))
    if rel == m_rel:
        test('M_'+uuid+'_four_L2_sectors_per_injected_read_observed',
             int(r['L2_read_sectors']) == 4*int(r['global_read_injected']))
    identities.append(dict(lane='M', workload=r['workload'], arm=r['arm'], uuid=uuid,
        core=ident['core'], binary_sha256=ident['binary_sha256'],
        stdout_sha256=ident['raw_stdout']['sha256'], strict_sha256=ident['strict']['sha256'],
        trace_list_sha256=ident['trace_list_sha256'],
        ordered_kernels=len(scope), lineage='ORIGINAL_FROZEN_INPUT;MATCHED_ARM_NOT_UUID_MERGED',
        source_pointer=pointer))
    denoms = {f: r['service_samples'] for f in ['mean_PIB_all64_SM_cycles','mean_physical_all64_SM_cycles']}
    denoms.update({f:r['service_retired'] for f in ['mean_ready_to_complete','mean_ready_to_collect','mean_collect','mean_post_collect_WB']})
    denoms['mean_map_loss_to_free'] = r['service_map_loss_to_free_count']
    for f, value in r.items():
        if f in ['workload','arm','attempt_uuid']:
            continue
        add('M', rel, pointer+':'+f, r['workload'], r['arm'], uuid, f, value,
            raw=e.get('selected_field_raw_names',{}).get(f,f), denominator=denoms.get(f,'1'))
    for i,k in enumerate(scope,1):
        add('M', 'COUNTER_EVIDENCE.json' if rel == m_rel else rel,
            'uuid:'+uuid+':identity.ordered_scope['+str(i-1)+']', r['workload'],r['arm'],uuid,
            'kernel_cycles',k['cycles'],ordinal=i,kernel=k['kernel'],stream=k.get('stream','UNAVAILABLE'),
            raw='gpu_sim_cycle',scope='PER_KERNEL_NONCUMULATIVE_ORIGINAL_ORDER')
    if not str(r['ready_hit_events']).startswith('UNAVAILABLE'):
        D=sum(int(r[f]) for f in ['ready_hit_events','pending_merge_events','cacheable_new_line_requests'])
        mode = 'io' if r['arm'].startswith('IO') else 'oo'
        scalars=e['raw_scalars']
        test('M_'+uuid+'_dependency_balance', D == scalars['DTC_L1_'+mode+'_completion_dependency_count'] ==
             scalars['DTC_L1_'+mode+'_completion_dependency_closed'])
        add('M',rel,pointer,r['workload'],r['arm'],uuid,'accepted_reference_count',D)
        lower_raw='DTC_L1_'+mode+'_lower_created'
        add('M','COUNTER_EVIDENCE.json' if rel == m_rel else rel,pointer,r['workload'],r['arm'],uuid,
            'lower_created',scalars[lower_raw],raw=lower_raw)
        for f, source in [('ready_fraction','ready_hit_events'),('pending_fraction','pending_merge_events'),('new_fraction','cacheable_new_line_requests')]:
            add('M',rel,pointer,r['workload'],r['arm'],uuid,f,int(r[source])/D,denominator=D,raw=source+'/D')

conventional = tsv('M','CONVENTIONAL_LOOKUP_CONTEXT.tsv')
test('conventional_context_preserved', len(conventional) == 9)

t_full = tsv('T','FULL_MATRIX.tsv')
t_mech = tsv('T','TERMINAL_MECHANISM_COMPARISON.tsv')
t_pre = {r['attempt_uuid']:r for r in tsv('T','PRE_REGISTRATION.tsv')}
t_order = js('T','ORDERED_KERNELS.json')
test('T_seven_published_natural_strict_runs', len(t_full) == 7 and js('T','FINAL_IDENTITY_AUDIT.json')['strict_pass'] == 7)
full_by_uuid = {r['attempt_uuid']:r for r in t_full}
for uuid in full_by_uuid:
    FILES['T'].extend(['strict/'+uuid+'.strict.json', 'run_receipts/'+uuid+'/RUN_TERMINAL.json'])
    fetch('T','strict/'+uuid+'.strict.json')
    fetch('T','run_receipts/'+uuid+'/RUN_TERMINAL.json')
    # These terminal proofs must also match the published T manifest.
    manifest = {r['path']:r for r in tsv('T','FILES_SHA256.tsv')}
    for rel in FILES['T'][-2:]:
        test('T_'+uuid+'_'+rel.split('/')[-1]+'_manifest', manifest[rel]['sha256'] == sha(fetch('T',rel)))

T_MAP = {
    'cycles':'cycles', 'active_instructions':'active_thread_instructions',
    'accepted_128b_reference_count':'accepted_reference_count',
    'ready_reference_outcomes':'ready_hit_events','pending_reference_outcomes':'pending_merge_events',
    'new_allocation_outcomes':'cacheable_new_line_requests', 'dtc_lower_created':'lower_created',
    'tag_evictions':'tag_evictions','fully_ready_cacheable_retired':'service_retired',
    'all64sm_cycle_mean_pib':'mean_PIB_all64_SM_cycles',
    'all64sm_cycle_mean_physical':'mean_physical_all64_SM_cycles',
    'ready_to_collect_per_cacheable_warp':'mean_ready_to_collect',
    'collection_per_cacheable_warp':'mean_collect', 'wb_wait_per_cacheable_warp':'mean_post_collect_WB',
    'fully_ready_to_complete_per_cacheable_warp':'mean_ready_to_complete',
    'mean_completed_map_loss_to_free':'mean_map_loss_to_free',
    'collected_sectors':'service_collected_sectors', 'ready_fraction':'ready_fraction',
    'pending_fraction':'pending_fraction','new_fraction':'new_fraction',
}
SERVICE = {f.replace('service_','DTC_SERVICE_V1_',1):f for f in byfield if f.startswith('service_')}
for i,r in enumerate(t_mech,1):
    uuid=r['uuid']; new=uuid in full_by_uuid
    shape = (t_pre[uuid]['logical_sets']+'x'+t_pre[uuid]['logical_ways']) if new else '32x4'
    qualifier = 'T_DISCOVERY_OR_MATCHED_CONTROL_NOT_NEW_K0_K1'
    retired=r['fully_ready_cacheable_retired']
    for source,f in T_MAP.items():
        denom = r['accepted_128b_reference_count'] if f.endswith('_fraction') else retired if f in ['mean_ready_to_collect','mean_collect','mean_post_collect_WB','mean_ready_to_complete'] else 'SEE_SOURCE_SUM_AND_COUNT' if f.startswith('mean_') else '1'
        add('T','TERMINAL_MECHANISM_COMPARISON.tsv',f'row:{i}:{source}',r['workload'],r['point'],uuid,
            f,r[source],raw=source,denominator=denom,tag=shape,qualification=qualifier)
    test('T_'+uuid+'_outcome_dependency_balance', sum(int(r[f]) for f in
        ['ready_reference_outcomes','pending_reference_outcomes','new_allocation_outcomes']) ==
        int(r['accepted_128b_reference_count']) == int(r['completion_dependency_count']))
    for fraction,outcome in [('ready_fraction','ready_reference_outcomes'),
                             ('pending_fraction','pending_reference_outcomes'),
                             ('new_fraction','new_allocation_outcomes')]:
        test('T_'+uuid+'_'+fraction, abs(float(r[fraction])-int(r[outcome])/int(r['accepted_128b_reference_count'])) < 1e-14)
    if new:
        strict_rel='strict/'+uuid+'.strict.json'
        strict=js('T',strict_rel); terminal=js('T','run_receipts/'+uuid+'/RUN_TERMINAL.json')
        test('T_'+uuid+'_strict_complete', all(strict['checks'].values()))
        test('T_'+uuid+'_natural_exit', terminal['exit_status']==0 and terminal['termination_reason']=='NATURAL_PROCESS_RETURN')
        test('T_'+uuid+'_hash_cycle_identity', strict['base']['stdout_sha256']==terminal['stdout_sha256']==r['source_stdout_sha256']==full_by_uuid[uuid]['stdout_sha256'] and int(strict['base']['cycles'])==int(r['cycles']))
        service=json.loads(strict['base']['service_metrics'])
        test('T_'+uuid+'_samples',service['DTC_SERVICE_V1_samples']==64*int(r['cycles']))
        test('T_'+uuid+'_post_ready',service['DTC_SERVICE_V1_fully_ready_to_complete_sum']==sum(service['DTC_SERVICE_V1_'+f] for f in ['ready_to_collect_sum','collection_cycles','wb_wait']))
        for source,numerator,denominator in [
            ('all64sm_cycle_mean_pib','pib_integral','samples'),
            ('all64sm_cycle_mean_physical','physical_integral','samples'),
            ('ready_to_collect_per_cacheable_warp','ready_to_collect_sum','retired'),
            ('collection_per_cacheable_warp','collection_cycles','retired'),
            ('wb_wait_per_cacheable_warp','wb_wait','retired'),
            ('fully_ready_to_complete_per_cacheable_warp','fully_ready_to_complete_sum','retired'),
            ('mean_completed_map_loss_to_free','map_loss_to_free_sum','map_loss_to_free_count')]:
            test('T_'+uuid+'_'+source+'_mean', abs(float(r[source])-
                 service['DTC_SERVICE_V1_'+numerator]/service['DTC_SERVICE_V1_'+denominator]) < 1e-8)
        for raw,f in SERVICE.items():
            add('T',strict_rel,'base.service_metrics:'+raw,r['workload'],r['point'],uuid,f,
                service[raw],raw=raw,tag=shape,qualification=qualifier)
        order=t_order[r['workload']]
        test('T_'+uuid+'_ordered_strict_checks',len(order)==len(strict['ordered_kernel_checks']) and
             all(k['ordinal']==n and k['pass'] for n,k in enumerate(strict['ordered_kernel_checks'],1)))
        for k in order:
            cycle=r['cycles'] if len(order)==1 else 'UNAVAILABLE_IN_ACCEPTED_SMALL_EVIDENCE'
            add('T',strict_rel,'ordered_kernel_checks:'+str(k['ordinal']),r['workload'],r['point'],uuid,
                'kernel_cycles',cycle,ordinal=k['ordinal'],kernel=k['kernel'],stream='UNAVAILABLE',
                raw='gpu_sim_cycle_NOT_STORED_IN_MULTIKERNEL_SMALL_PACK',scope='PER_KERNEL_ORIGINAL_ORDER',tag=shape,qualification=qualifier)
        pre=t_pre[uuid]
        identities.append(dict(lane='T',workload=r['workload'],arm=r['point'],uuid=uuid,core=pre['core'],
            binary_sha256=pre['binary_sha256'],stdout_sha256=terminal['stdout_sha256'],
            strict_sha256=sha(fetch('T',strict_rel)),trace_list_sha256=pre['trace_list_sha256'],
            ordered_kernels=len(order),lineage=qualifier,source_pointer='FULL_MATRIX.tsv:uuid:'+uuid))
        for f in ['global_read_injected','global_write_injected','L2_read_sectors','L2_read_reservation_retries',
                  'DRAM_n_rd','DRAM_n_rd_L2_A','DRAM_n_write','DRAM_n_wr_bk','DRAM_read_payload_bytes','DRAM_write_payload_bytes']:
            add('T','TERMINAL_MECHANISM_COMPARISON.tsv',f'row:{i}',r['workload'],r['point'],uuid,f,
                'UNAVAILABLE_IN_SELECTED_T_MECHANISM_TABLE',tag=shape,qualification=qualifier)
    for f in ['terminal_queryable_mappings','terminal_lost_resident_allocations','kernel_boundary_invalidated_mappings']:
        add('T','TERMINAL_MECHANISM_COMPARISON.tsv',f'row:{i}',r['workload'],r['point'],uuid,f,
            'UNAVAILABLE',tag=shape,qualification=qualifier)

# Preserve the scientifically material opposite-direction observations.
for workload in ['GEMM','Gaussian']:
    old=next(r for r in t_mech if r['point']=='accepted_'+workload+'_OO128')
    new=next(r for r in t_mech if r['point']=='T1-C' and r['workload']==workload)
    test('reverse_evidence_'+workload, int(new['cycles'])<int(old['cycles']) and
         float(new['fully_ready_to_complete_per_cacheable_warp'])>float(old['fully_ready_to_complete_per_cacheable_warp']))
test('BICG_A_M_IO_UUIDs_kept_distinct', next(r for r in a_rows if r['workload']=='BICG')['IO_uuid'] !=
     next(r for r in m_rows if r['workload']=='BICG' and r['arm']=='IO128')['attempt_uuid'])
# Synthetic CPU arithmetic protects the preregistered direction; no simulator.
from fractions import Fraction
a,b,c,d = map(Fraction,[100,80,120,120])
test('preregistered_ratio_direction_fixture', (c/a,b/a,d/c,d/b)==
     (Fraction(6,5),Fraction(4,5),Fraction(1),Fraction(3,2)))
test('preregistered_interaction_identity_fixture', (d/b)/(c/a)==(d/c)/(b/a)==Fraction(5,4))
test('preregistered_additive_interaction_fixture', (d-b)-(c-a)==20)

# Explicit missing mapping rows also for M runs, never inferred from occupancy.
for r,e,rel,pointer in m_pairs:
    for f in ['terminal_queryable_mappings','terminal_lost_resident_allocations','kernel_boundary_invalidated_mappings']:
        add('M',rel,pointer,r['workload'],r['arm'],r['attempt_uuid'],f,'UNAVAILABLE')
test('all_output_fields_typed', all(r['metric_id'] in byfield for r in evidence))
test('no_missing_zero_imputation',all(r['value']!='0' for r in evidence if r['status']=='UNAVAILABLE'))
write('OLD_ACCEPTED_EVIDENCE.tsv',tab(evidence,list(evidence[0])))
write('INPUT_IDENTITIES.tsv',tab(identities,list(identities[0])))
write('SOURCE_BLOBS_SHA256.tsv',tab(source_rows,list(source_rows[0])))

validation=dict(status='PASS_CPU_CONSUMER_ONLY_WITH_EXPLICIT_MISSING_FIELDS',
    goal='DTC_LANE_Z_FLUSH_MECHANISM_CONSUMER_174_V1',accepted_sources=REFS,
    immutable_blob_files=len(source_rows),immutable_blob_bytes=sum(r['bytes'] for r in source_rows),
    original_manifest_hash_checks=len(manifest_checks)+14,old_evidence_rows=len(evidence),
    typed_metric_fields=len(definitions),identity_rows=len(identities),checks=checks,
    old_raw_or_trace_payload_reads=0,simulations_launched=0,native_jobs_launched=0,
    U_progress_probes=0,U_partial_BICG_cycle_reads=0,U_new_result_consumption=0,
    Core_mutations=0,paper_v013_mutations=0,GM12_recomputation=False,
    kernel_cycle_policy='M ordered_scope preserved; T single kernel whole=kernel; T Gaussian ordinal/name preserved cycles UNAVAILABLE',
    observer_policy='X published contract not consumed; default/effective flags UNAVAILABLE; no pre/post cycle mixing',
    scope='Revalidates immutable accepted extracts and provenance; does not rerun original strict/raw validation',
    consumer_sha256=sha(Path(__file__).read_bytes()),
    frozen_document_sha256={f:sha((PACK/f).read_bytes()) for f in
        ['METRIC_DEFINITIONS.md','PREREGISTERED_INTERPRETATION.md','MISSING_FIELDS.md']})
write('CPU_CONSUMER_VALIDATION.json',json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
if CHECK:
    manifest = list(csv.DictReader((PACK/'FILES_SHA256.tsv').open(),delimiter='\t'))
    files = {str(p.relative_to(PACK)) for p in PACK.rglob('*') if p.is_file() and p.name != 'FILES_SHA256.tsv'}
    assert files == {r['path'] for r in manifest}, 'incomplete package manifest'
    for row in manifest:
        data=(PACK/row['path']).read_bytes()
        assert len(data)==int(row['bytes']) and sha(data)==row['sha256'], row['path']
print(json.dumps({k:validation[k] for k in ['status','old_evidence_rows','typed_metric_fields','immutable_blob_files','immutable_blob_bytes']}))
