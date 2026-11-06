"""Pure, closed-evidence Oracle analysis. No runtime/model/registry imports.

The input is S's DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1 plus its immutable
KERNEL_FACTS payloads. Acceptance is consumed, never granted by this module.
"""
import copy
import itertools
import math
import re
from collections import Counter

MODES = ('OFF_MATCHED', 'M_DATAREAD', 'L2_DATAREAD', 'L1_DATAREADY')
AUTHORITY = '18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
BUILD_KEYS = ('core_commit', 'framework_commit', 'binary_sha256', 'libcudart_sha256')
REF_KEYS = ('result_sha256', 'spec_sha256', 'execution_plan_sha256', 'native_strict_sha256', 'kernel_evidence_sha256')
BOUNDARIES = [
    'Runtime closer acceptance and final independent scientific review are distinct statuses.',
    'S uses actual same-input same-build accepted OFF, never historical DH-P0 or C1 structural results.',
    'Negative speedups and H are retained. Different mode denominators are explicit.',
    'No per-program best-Oracle GM, mathematical/monotone/additive bound, or feasible equal-gain claim.',
    'Kernel work/order validation does not assert identical cross-warp issue order.',
    'Kernel counters remain as printed; reset/cumulative/delta semantics are not inferred.',
    'Missing reported counters remain null; source-proven derived values retain a separate proof.',
    'Capture ELF, HtoD/initial-state and full-application numerical correctness limitations remain.',
]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def integer(value, positive=False):
    return type(value) is int and (value > 0 if positive else value >= 0)

def digest(value, length=64):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{%d}' % length, value) is not None

def matrix_index(matrix):
    points = matrix.get('rows', [])
    require(len(points) == 128, 'FIXED_MATRIX_MUST_HAVE_128_SLOTS')
    plans, programs = {}, {}
    for p in points:
        require(p['mode'] in MODES and digest(p['input_digest']), 'BAD_MATRIX_MODE_OR_FULL_INPUT_SHA')
        require(p.get('design') == 'DH', 'CH_OR_NON_DH_IS_OUTSIDE_AUTHORIZATION')
        require(p['plan_id'] not in plans, 'DUPLICATE_MATRIX_PLAN')
        plans[p['plan_id']] = p
        old = programs.setdefault(p['input_digest'], p)
        require(all(old[k] == p[k] for k in ('program', 'suite', 'initial_fixed8')), 'MATRIX_INPUT_METADATA_CONFLICT')
    require(len(programs) == 32, 'FIXED_POPULATION_MUST_HAVE_32_INPUTS')
    require(len({p['program'] for p in programs.values()}) == 32, 'ONE_FROZEN_INPUT_PER_PROGRAM_REQUIRED')
    require(sum(bool(p['initial_fixed8']) for p in programs.values()) == 8, 'INITIAL_SUBSET_MUST_HAVE_8_INPUTS')
    for key in programs:
        require(Counter(p['mode'] for p in points if p['input_digest'] == key) == Counter(MODES), 'MATRIX_FOUR_MODES_REQUIRED')
    return plans, programs

def kernel_validation(row, point, facts):
    errors = []
    if not isinstance(facts, dict):
        return ['MISSING_KERNEL_FACTS'], []
    for k in ('program', 'input_digest', 'mode', 'uuid'):
        if facts.get(k) != row.get(k):
            errors.append('KERNEL_FACTS_IDENTITY_' + k)
    records = facts.get('records')
    if not isinstance(records, list) or not records:
        return errors + ['EMPTY_KERNEL_RECORDS'], []
    expected = point['capture_identity']['expected']
    if len(records) != expected['kernels']:
        errors.append('KERNEL_COUNT_DIFFERENT_FROM_FROZEN_ROI')
    previous_cta = previous_cycles = 0
    total_instructions = total_cycles = 0
    for ordinal, k in enumerate(records, 1):
        if k.get('ordinal') != ordinal or not isinstance(k.get('kernel'), str):
            errors.append('KERNEL_ORDINAL_OR_NAME_INVALID')
        if not integer(k.get('cycles'), True):
            errors.append('INVALID_EXPLICIT_KERNEL_CYCLES')
        else:
            total_cycles += k['cycles']
        if not integer(k.get('active_instructions')):
            errors.append('UNKNOWN_KERNEL_ACTIVE_INSTRUCTIONS')
        else:
            total_instructions += k['active_instructions']
        if not integer(k.get('cumulative_CTA')) or k['cumulative_CTA'] < previous_cta:
            errors.append('UNKNOWN_OR_NONMONOTONIC_CUMULATIVE_CTA')
        else:
            delta = k['cumulative_CTA'] - previous_cta
            if k.get('CTA_delta') != delta:
                errors.append('CTA_DELTA_NOT_DEFINED_CUMULATIVE_DIFFERENCE')
            previous_cta = k['cumulative_CTA']
        if not integer(k.get('total_cycles'), True) or k['total_cycles'] < previous_cycles:
            errors.append('UNKNOWN_OR_NONMONOTONIC_TOTAL_CYCLES')
        else:
            if integer(k.get('cycles'), True) and k['total_cycles'] - previous_cycles != k['cycles']:
                errors.append('EXPLICIT_KERNEL_CYCLES_NOT_TOTAL_DIFFERENCE')
            previous_cycles = k['total_cycles']
        for field in ('result_sha256', 'strict_sha256'):
            target = row.get('result_sha256') if field == 'result_sha256' else row.get('native_strict_sha256')
            if k.get(field) != target:
                errors.append('KERNEL_EVIDENCE_SOURCE_BINDING_' + field)
        if not digest(k.get('raw_gzip_sha256')) or not digest(k.get('raw_uncompressed_sha256')):
            errors.append('KERNEL_RAW_SHA_UNAVAILABLE')
    if total_instructions != expected['instructions'] or previous_cta != expected['CTA']:
        errors.append('KERNEL_WORK_DIFFERENT_FROM_FROZEN_INPUT_ROI')
    if total_cycles != row.get('cycles') or previous_cycles != row.get('cycles'):
        errors.append('KERNEL_CYCLES_DO_NOT_CLOSE_WHOLE_INPUT')
    return sorted(set(errors)), records

def service_summary(metrics, cycles):
    fields = ('samples', 'pib_integral', 'physical_integral', 'collected_sectors', 'retired',
              'fully_ready_to_complete_sum', 'ready_to_collect_sum', 'collection_cycles',
              'wb_wait', 'map_loss_to_free_sum', 'map_loss_to_free_count')
    raw = {k: metrics.get('DTC_SERVICE_V1_' + k) for k in fields}
    samples = raw['samples']
    valid_samples = integer(cycles, True) and integer(samples, True) and samples == 64 * cycles
    result = {'as_printed': raw, 'sample_scope': 'MATCHES_64_SM_WHOLE_INPUT_CYCLES' if valid_samples else 'UNCONFIRMED_NO_DERIVED_OCCUPANCY',
              'PIB_average_per_SM': None, 'allocated_physical_average_per_SM': None,
              'note': 'Allocated lines include retained Ref-free cache state; averages are not saturation events or critical-path cycles.'}
    if valid_samples:
        for source, target in [('pib_integral', 'PIB_average_per_SM'), ('physical_integral', 'allocated_physical_average_per_SM')]:
            if integer(raw[source]):
                result[target] = raw[source] / samples
    retired = raw['retired']
    result['per_retired_load_intervals'] = {k: raw[k] / retired if integer(retired, True) and integer(raw[k]) else None
        for k in ('fully_ready_to_complete_sum', 'ready_to_collect_sum', 'collection_cycles', 'wb_wait')}
    return result

def evidence_summary(row):
    metrics = copy.deepcopy(row.get('terminal_metrics_as_printed') or {})
    traffic = copy.deepcopy(row.get('traffic_as_printed'))
    raw_read = (traffic or {}).get('L2_reported_GLOBAL_ACC_R_TOTAL_ACCESS', (traffic or {}).get('L2_accepted_read_32B_sectors'))
    derived = (traffic or {}).get('L2_derived_accepted_read_32B_sectors')
    request_keys = ('DTC_L1_oo_new_misses', 'DTC_L1_oo_lower_created', 'DTC_L1_oo_lower_issued',
        'DTC_L1_oo_lower_responses', 'DTC_L1_lower_credit_acquired', 'DTC_L1_lower_credit_released',
        'DTC_L1_lower_outstanding', 'DTC_L1_lower_cap_full_events', 'DTC_L1_oo_completion_dependency_count',
        'DTC_L1_oo_completion_dependency_closed', 'DTC_L1_oo_active_refs', 'DTC_L1_oo_physical_allocated',
        'DTC_L1_oo_pib_occupancy', 'DTC_L1_oo_valid_hits', 'DTC_L1_oo_pending_hits', 'DTC_L1_oo_tag_evictions')
    return {
        'mechanism_exposure_as_reported': row.get('actual_mechanism_exposure'),
        'request_Tag_Physical_PIB_Ref_as_printed': {k: metrics.get(k) for k in request_keys},
        'finite_service': service_summary(metrics, row['cycles']),
        'terminal_metrics_as_printed': metrics,
        'traffic_as_printed_and_proof': traffic,
        'L2_read_reported': raw_read,
        'L2_read_source_derived': derived,
        'derived_zero_is_not_a_reported_raw_zero': raw_read is None and derived == 0,
        'derived_proof_retained': copy.deepcopy((traffic or {}).get('sparse_partition_proof')),
        'latency_counters_as_printed': copy.deepcopy(row.get('latency_counters_as_printed')),
        'not_inferred_pressure_or_causality': ['Tag-bank conflicts when absent', 'PIB-full fraction when absent',
            'physical-full events when absent', 'active Ref integral when absent', 'per-eligible-read latency when absent'],
    }

def stat(pairs, population, label):
    values = [p['S'] for p in pairs]
    return {'population_label': label, 'fixed_population_denominator': population,
        'accepted_matched_pairs': len(pairs), 'missing_or_unpaired': population - len(pairs),
        'coverage': len(pairs) / population if population else None,
        'GM_S_over_accepted_matched_subset': math.exp(math.fsum(math.log(x) for x in values) / len(values)) if values else None,
        'faster': sum(p['cycles'] < p['OFF_cycles'] for p in pairs),
        'equal': sum(p['cycles'] == p['OFF_cycles'] for p in pairs),
        'slower': sum(p['cycles'] > p['OFF_cycles'] for p in pairs),
        'S_sorted': sorted(values), 'H_sorted': sorted(p['H'] for p in pairs),
        'input_digests': [p['input_digest'] for p in pairs],
        'scope': 'COMPLETE_FIXED_POPULATION' if population and len(pairs) == population else 'ACCEPTED_SUBSET_NOT_FULL_POPULATION'}

def analyze(snapshot, matrix, kernel_facts, *, matrix_sha256, expected_build_identity,
            expected_configs_by_mode, snapshot_sha256=None, c1_context=None):
    """Return deterministic derived data; caller supplies SHA-verified closed artifacts.

    kernel_facts is indexed by plan_id and contains S's complete immutable flat
    KERNEL_FACTS objects. This function performs no filesystem or process access.
    """
    require(snapshot.get('schema') == 'DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1', 'UNSUPPORTED_CONSUMER_CONTRACT')
    require(snapshot.get('authority_commit') == AUTHORITY and snapshot.get('CH_budget') == 0, 'WRONG_AUTHORITY_OR_CH_SCOPE')
    require(snapshot.get('matrix_sha256') == matrix_sha256 and digest(matrix_sha256), 'FROZEN_MATRIX_SHA_MISMATCH')
    plans, population = matrix_index(matrix)
    supplied = {}
    for r in snapshot.get('rows', []):
        pid = r.get('plan_id')
        require(pid in plans and pid not in supplied, 'UNFROZEN_OR_DUPLICATE_SNAPSHOT_PLAN')
        require(all(r.get(k) == plans[pid][k] for k in ('program', 'suite', 'input_digest', 'mode', 'initial_fixed8')), 'SNAPSHOT_PLAN_IDENTITY_CHANGED')
        supplied[pid] = r
    require(len(supplied) == 128, 'SNAPSHOT_MUST_RETAIN_ALL_128_STATUSES')
    cells, pair_rows, kernels_by_id = {}, [], {}
    for pid, point in plans.items():
        r = supplied[pid]
        accepted = r.get('classification') == 'accepted' and r.get('status') == 'ACCEPTED_RUNTIME_CLOSER'
        cell = {k: copy.deepcopy(r.get(k)) for k in ('plan_id', 'program', 'suite', 'input_digest', 'mode', 'stage',
            'status', 'classification', 'raw_status', 'uuid', 'cycles', 'independent_review_status', 'result_path',
            'result_sha256', 'spec_path', 'spec_sha256', 'execution_plan_path', 'execution_plan_sha256',
            'native_strict_path', 'native_strict_sha256', 'kernel_evidence_path', 'kernel_evidence_sha256',
            'core_commit', 'framework_commit', 'binary_sha256', 'libcudart_sha256', 'non_oracle_options_sha256',
            'configuration_file_pins', 'archive_receipt', 'engineering_events', 'observed_cycles_not_accepted',
            'raw_failure_proof', 'validation_error', 'read_note')}
        cell.update(runtime_closer_accepted=accepted, analysis_identity_and_work_supported=False,
                    validation_errors=[], S=None, H=None, pair_status='NOT_ACCEPTED',
                    historical_DH0_context_cycles=r.get('historical_DH0_context_cycles'),
                    historical_context_never_used_for_pair=True)
        if accepted:
            errors = []
            if not integer(r.get('cycles'), True): errors.append('INVALID_WHOLE_INPUT_CYCLES')
            for k in BUILD_KEYS:
                if r.get(k) != expected_build_identity.get(k): errors.append('UNFROZEN_BUILD_' + k)
            for k in REF_KEYS:
                if not digest(r.get(k)): errors.append('MISSING_PIN_' + k)
            if not digest(r.get('non_oracle_options_sha256')): errors.append('MISSING_NON_ORACLE270_VECTOR_PIN')
            expected_configs = expected_configs_by_mode.get(r['mode'], [])
            if [p.get('sha256') for p in (r.get('configuration_file_pins') or [])] != expected_configs:
                errors.append('UNFROZEN_ORDERED_CONFIGURATION_PINS')
            ke, records = kernel_validation(r, point, kernel_facts.get(pid))
            errors += ke
            cell['validation_errors'] = sorted(set(errors))
            cell['analysis_identity_and_work_supported'] = not errors
            cell['pair_status'] = 'WAITING_MATCHED_OFF' if not errors else 'HOLD_IDENTITY_OR_KERNEL_WORK'
            cell['evidence'] = evidence_summary(r)
            cell['kernel_records_as_printed'] = copy.deepcopy(records)
            kernels_by_id[pid] = records
        cells[(point['input_digest'], point['mode'])] = cell
    kernel_pairs = []
    for (inp, mode), cell in cells.items():
        if mode == MODES[0]:
            cell['pair_status'] = 'MATCHED_OFF_CONTROL' if cell['analysis_identity_and_work_supported'] else cell['pair_status']
            continue
        if not cell['analysis_identity_and_work_supported']: continue
        off = cells[(inp, MODES[0])]
        if not off['analysis_identity_and_work_supported']:
            cell['pair_status'] = 'MISSING_OR_UNQUALIFIED_MATCHED_OFF'
            continue
        if cell['non_oracle_options_sha256'] != off['non_oracle_options_sha256']:
            cell['pair_status'] = 'HOLD_NON_ORACLE270_MISMATCH'
            continue
        ks, os = kernels_by_id[cell['plan_id']], kernels_by_id[off['plan_id']]
        shape = lambda records: [(k['ordinal'], k['kernel'], k['active_instructions'], k['CTA_delta']) for k in records]
        if shape(ks) != shape(os):
            cell['pair_status'] = 'HOLD_KERNEL_SEQUENCE_OR_WORK_MISMATCH'
            continue
        s, h = off['cycles'] / cell['cycles'], 1 - cell['cycles'] / off['cycles']
        cell.update(S=s, H=h, S_exact_ratio=[off['cycles'], cell['cycles']],
                    H_exact_ratio=[off['cycles']-cell['cycles'], off['cycles']], pair_status='MATCHED_RUNTIME_ACCEPTED_PRELIMINARY')
        cell['observed_matched_response'] = ('FASTER_UNDER_CONTROLLED_SCENARIO' if cell['cycles'] < off['cycles'] else
            'SLOWER_UNDER_CONTROLLED_SCENARIO' if cell['cycles'] > off['cycles'] else 'EXACT_ZERO_RESPONSE')
        p = {k: cell[k] for k in ('program', 'suite', 'input_digest', 'mode', 'cycles', 'S', 'H', 'uuid', 'result_sha256')}
        p.update(OFF_cycles=off['cycles'], OFF_uuid=off['uuid'], initial_fixed8=population[inp]['initial_fixed8'],
                 independent_final_review_status=cell['independent_review_status'])
        pair_rows.append(p)
        for x,y in zip(ks, os):
            kernel_pairs.append({'program':cell['program'],'input_digest':inp,'mode':mode,'ordinal':x['ordinal'],
                'kernel':x['kernel'],'OFF_kernel_cycles':y['cycles'],'Oracle_kernel_cycles':x['cycles'],
                'S':y['cycles']/x['cycles'],'H':1-x['cycles']/y['cycles'],
                'active_instructions':x['active_instructions'],'CTA_delta':x['CTA_delta'],
                'OFF_record_as_printed':copy.deepcopy(y),'Oracle_record_as_printed':copy.deepcopy(x),
                'counter_delta_or_reset_inferred':False})
    statistics = {}
    for mode in MODES[1:]:
        pairs = [p for p in pair_rows if p['mode'] == mode]
        statistics[mode] = {'CORE32':stat(pairs,32,'FIXED_CORE32'),
            'fixed8':stat([p for p in pairs if p['initial_fixed8']],8,'INITIAL_FIXED8_NOT_CORE32'),
            'suites':{suite:stat([p for p in pairs if p['suite']==suite],sum(p['suite']==suite for p in population.values()),suite)
                for suite in sorted({p['suite'] for p in population.values()})}}
    intersections = {}
    for names in list(itertools.combinations(MODES[1:],2)) + [MODES[1:]]:
        common = [i for i in population if all(cells[(i,m)].get('S') is not None for m in names)]
        label = '__'.join(names)
        item={'common_input_digests':common,'accepted_common_inputs':len(common),'fixed_denominator':32,
              'coverage':len(common)/32,'same_set_GM_by_mode':{m:stat([p for p in pair_rows if p['mode']==m and p['input_digest'] in common],32,'SAME_ACCEPTED_INTERSECTION') for m in names}}
        if len(names)==2:
            ratios=[cells[(i,names[0])]['cycles']/cells[(i,names[1])]['cycles'] for i in common]
            item['GM_cycles_first_mode_over_second']=math.exp(math.fsum(math.log(x) for x in ratios)/len(ratios)) if ratios else None
        intersections[label]=item
    per_program=[]
    for inp,p in population.items():
        c1=copy.deepcopy((c1_context or {}).get(inp))
        if c1 is not None: require(c1.get('input_digest')==inp,'C1_CONTEXT_FULL_INPUT_MISMATCH')
        per_program.append({'program':p['program'],'suite':p['suite'],'input_digest':inp,'initial_fixed8':p['initial_fixed8'],
            'frozen_input_and_ROI':copy.deepcopy(p['capture_identity']),
            'C1_real_structure_evidence_separate':c1 or {'status':'NOT_INGESTED_UNKNOWN','not_an_OFF_substitute':True},
            'C2_controlled_Oracle_cells':{mode:cells[(inp,mode)] for mode in MODES},
            'causal_or_feasible_headroom_claim':'NOT_ESTABLISHED_BY_ORACLE_SPEEDUP'})
    return {'schema':'DTC_CORE32_CONTROLLED_ORACLE_OPPORTUNITY_ANALYSIS_V1','matrix_sha256':matrix_sha256,
        'source_snapshot_sha256':snapshot_sha256,'source_snapshot_generated_utc':snapshot.get('generated_utc'),
        'closed_fingerprint_sha256':snapshot.get('closed_fingerprint_sha256'),'fixed_population':32,'initial_population':8,
        'runtime_closer_accepted_cells':sum(c['runtime_closer_accepted'] for c in cells.values()),
        'analysis_identity_work_supported_cells':sum(c['analysis_identity_and_work_supported'] for c in cells.values()),
        'cell_population':128,'cell_status_counts':dict(Counter(c['status'] for c in cells.values())),
        'classification_counts':dict(Counter(c['classification'] for c in cells.values())),
        'source_consumer_validation_errors':copy.deepcopy(snapshot.get('validation_errors')),
        'source_consumer_closed_result_count':snapshot.get('closed_result_count'),
        'independent_review_status_counts':dict(Counter(str(c.get('independent_review_status')) for c in cells.values())),
        'mode_statistics':statistics,'mode_common_intersections':intersections,
        'four_cell_common_accepted':intersections['__'.join(MODES[1:])],
        'matched_program_pairs':pair_rows,'matched_kernel_pairs':kernel_pairs,'program_records':per_program,
        'boundaries':BOUNDARIES,'scientific_starts_by_analyzer':0,'best_oracle_stitched_GM':'FORBIDDEN_NOT_COMPUTED',
        'ROI_validation_scope':'Consumes frozen input/spec/strict references and checks complete kernel sequence/work; does not independently reread original traces.'}
