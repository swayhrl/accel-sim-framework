"""Main-only finite NI of closed Conv/Black MS0 references, then two new S64 specs.

Never launches or registers a model. All prior artifacts remain immutable.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import uuid

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0, str(J / 'tools'))
from ep_perf_common import *

PREFIXES = (b'EPL2FTV1|', b'EPL2STRUCTV1|', b'EPL2ROC1V1|', b'EPL2ROV1|', b'EPL2TVDV1|')
MIB = 1 << 20
GIB = 1 << 30


def actual(pid, ticks=None):
    try:
        p = Path('/proc') / str(pid)
        a = (p / 'stat').read_text().rsplit(')', 1)[1].split()
        if a[0] in ('Z', 'X') or (ticks is not None and int(a[19]) != ticks):
            return None
        rss = int(next(v.split()[1] for v in (p / 'status').read_text().splitlines() if v.startswith('VmRSS:'))) * 1024
        return dict(pid=pid, start_ticks=int(a[19]), RSS_bytes=rss)
    except (OSError, StopIteration):
        return None


def gate():
    wrapper = J / 'agent_c/cpu_consistent_resources_v2.py'
    need(sha(wrapper) == '07d0a21fb34419392c90f161dc49f0dfda9ba7eda99dd5d2e53b697ba9491237', 'CPU sample wrapper pin')
    sp = importlib.util.spec_from_file_location('Main_CPU_short', wrapper)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    snap = mod.snapshot()
    need(snap['cpu_engineering_read_consistency']['status'] == 'CONSISTENT_SHORT_LOCK_METADATA_SAMPLE', 'fresh consistent resource sample')
    own = 0
    model_rows = []
    for case, row in read(J / 'control/DISPATCH_CLAIMS.json')['claims'].items():
        if row['state'] not in ('CLAIMED', 'RUNNING'):
            continue
        a = actual(row.get('model_pid'), row.get('model_start_ticks'))
        growth = max(0, row['estimated_peak_RAM_bytes'] - (a['RSS_bytes'] if a else 0))
        own += growth
        model_rows.append(dict(case=case, actual=a, remaining_growth_bytes=growth))
    # These exact engineering workers are not also in model claims. Check command
    # identity, not stale predecessor PIDs: the finite parser batch replaces workers.
    parser_rows, ro_rows = [], []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except OSError:
            continue
        a = actual(int(p.name))
        if not a:
            continue
        if ('/agent_c/parser_expansion/ep9dd_component_v6_firsthand_cpu_only ' in cmd or
                int(p.name) == 1984618 and a['start_ticks'] == 987927872):
            parser_rows.append(a)
        if '/agent_a/ro_remaining_main5_20261028_v1/' in cmd and any(x in cmd for x in ('run_offline_engineering_', 'onepass_ro_remaining5_')):
            ro_rows.append(a)
    need(len(parser_rows) <= 3 and len(ro_rows) <= 2, 'unexpected CPU engineering population needs review')
    cpu = sum(max(0, 512 * MIB - r['RSS_bytes']) for r in parser_rows)
    if ro_rows:
        cpu += max(0, 512 * MIB - sum(r['RSS_bytes'] for r in ro_rows))
    # Agent B's simultaneously proposed pure CPU worker is conservatively included
    # as a complete128MiB cap; Main candidate includes only its remaining AS growth.
    cpu += 128 * MIB
    own_current = actual(os.getpid())
    cpu += max(0, 128 * MIB - own_current['RSS_bytes'])
    floor = max(8 * GIB, snap.get('confirmed_foreign_host_floor_bytes', 0))
    cg_floor = max(8 * GIB, snap.get('confirmed_foreign_cgroup_floor_bytes', 0))
    usable = max(0, snap['host_MemAvailable_bytes'] - floor)
    if snap.get('cgroup_effective_headroom_bytes') is not None:
        usable = min(usable, max(0, snap['cgroup_effective_headroom_bytes'] - cg_floor))
    required = snap['foreign_additional_RAM_bytes'] + own + cpu
    writes = snap['cpu_engineering_read_consistency']['own_advertised_remaining_writes']
    disk_required = snap['foreign_remaining_write_bytes'] + writes + max(5 * GIB, GIB) + 2 * MIB
    allowed = not snap['foreign_metadata_errors'] and usable >= required and snap['native_free_bytes'] >= disk_required
    value = dict(schema='EP_MAIN_BOUNDED_128M_CPU_ONLY_HARD_FUTURE_GROWTH_V1', utc=now(),
        snapshot=snap, own_model_growth_rows=model_rows, parser_CPU_rows=parser_rows,
        RO_combined512M_rows=ro_rows, conservative_other_B_pure_CPU_cap_bytes=128*MIB,
        Main_CPU_AS_cap_bytes=128*MIB, additional_CPU_growth_bytes=cpu,
        model_future_growth_bytes=own, usable_hard_RAM_bytes=usable,
        all_future_growth_required_bytes=required, margin_bytes=usable-required,
        disk_required_bytes=disk_required, pass_admission=allowed,
        scope='CPU/read-only accepted raw only; no model/native/R3 policy change',
        Source64_build_started=False, automatic_model_retry=False)
    path = J / 'control' / ('P_MS0_CONV_BLACK_NI_RESOURCE_' + str(uuid.uuid4()) + '.json')
    put(path, value, True)
    need(allowed, 'CPU_HARD_FUTURE_GROWTH_HOLD:' + str(path))
    resource.setrlimit(resource.RLIMIT_AS, (128*MIB, 128*MIB))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    os.nice(10)
    return ref(path)


def endpoint(q, case):
    row = q['consumed'][case]
    need(row['state'] == 'CLOSED_ACCEPTED', 'natural accepted+archived endpoint required')
    point = exact(row['accepted_point_ref'])
    ar = exact(row['archive_receipt_ref'])
    need(ar['status'] == 'TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and len(ar['native_restores']) == 2, 'true164 complete acceptance closure')
    need(all(x['status'] == 'INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' for x in ar['native_restores']), 'actual two restores')
    s = exact(point['spec_ref'])
    raw = point['raw_stream_receipt']
    path = Path(raw['path'])
    need(path.stat().st_size == raw['stored_bytes'] and sha(path) == raw['stored_sha256'], 'closed compressed raw integrity')
    whole, selected, count, total = hashlib.sha256(), hashlib.sha256(), 0, 0
    with gzip.open(path, 'rb') as f:
        for line in f:
            whole.update(line)
            total += len(line)
            if line.startswith(PREFIXES):
                selected.update(line)
                count += 1
    need(whole.hexdigest() == raw['raw_sha256'] and total == raw['raw_bytes'], 'complete decompressed raw identity')
    need(count >= 64, "whole application's protocol closure not observed")
    return s, point, dict(count=count, sha256=selected.hexdigest(), prefixes=[x.decode() for x in PREFIXES]), row


def main():
    gate_ref = gate()
    registry, unused = authority()
    q = registry['registered_future_requests'][GOAL]
    samples = read(J / 'control/SEARCH_PLAN_U_D_N_V1.json')['exploration_inputs'][1:]
    ni_rows = []
    for sample in samples:
        for mode in ('S', 'F'):
            old_case = sample['reference_cohorts'][mode]
            new_case = 'EP_PERF_' + sample['case_short'] + '_' + mode + '_REF_G32_W8_P1168_MS0_V1'
            old_s, old, p0, r0 = endpoint(q, old_case)
            new_s, new, p1, r1 = endpoint(q, new_case)
            delta = {k: [v, new_s['expected_effective_options'][k]] for k, v in old_s['expected_effective_options'].items() if new_s['expected_effective_options'][k] != v}
            need(len(old_s['expected_effective_options']) == len(new_s['expected_effective_options']) == 282 and delta == {'-gpgpu_ep_l2_ms_observer': ['1', '0']}, 'exact sole282 MS observer delta')
            need(old_s['observer_env'] == new_s['observer_env'] and old_s['source_identity'] == new_s['source_identity'], 'same environment/Source5')
            for k in ('input_identity_sha256', 'mode', 'cycles', 'instructions', 'CTA', 'kernel_count', 'hardware_drained'):
                need(old[k] == new[k], 'application NI mismatch:' + k)
            need(new['hardware_drained'] and p0 == p1, 'protocol population/order/state NI')
            ni_rows.append(dict(mode=mode, program=new_s['program'], original_MS1_point_ref=r0['accepted_point_ref'], matched_MS0_point_ref=r1['accepted_point_ref'],
                archive_refs=[r0['archive_receipt_ref'], r1['archive_receipt_ref']], all282_delta=delta,
                cycles=new['cycles'], instructions=new['instructions'], CTA=new['CTA'], kernels=new['kernel_count'], protocol_projection=p1))
    ni = dict(schema='EP_MAIN_P_MS0_FINITE_APPLICATION_NI_V1', goal=GOAL,
        status='FINITE_CONV_BLACK_BOTH_MODES_CYCLES_CENSUS_AND_PROTOCOL_NI_PASS', utc=now(),
        CPU_resource_gate_ref=gate_ref, tests=ni_rows, old_MS1_point_not_relabelled_MS0=True,
        scope='Only these exact two inputs/two modes. Statistical populations differ, not all workloads NI or host overhead proof.')
    ni_path = J / 'control/P_MS0_CONV_BLACK_APPLICATION_NI_RECEIPT.json'
    ni_ref = put(ni_path, ni, True)
    hqr = ref(J / 'control/HOST_QUALIFICATION_P_S64_MS0_V1.json')
    hq = exact(hqr)
    adapter = module(hq['qualified_parameter_validation_module_ref'], 'Main_finite_static64')
    refs, aliases = [], []
    for sample in samples:
        s_case = 'EP_PERF_' + sample['case_short'] + '_S_REF_G32_W8_P1168_MS0_V1'
        f_case = 'EP_PERF_' + sample['case_short'] + '_F_REF_G32_W8_P1168_MS0_V1'
        base_path = J / 'cases' / s_case / 'control/FROZEN_SPEC.json'
        base = read(base_path)
        need(q['consumed'][s_case]['state'] == q['consumed'][f_case]['state'] == 'CLOSED_ACCEPTED', 'real same observer references')
        case = 'EP_PERF_' + sample['case_short'] + '_S_G32_W8_STATIC64_MS0_V1'
        need(case not in q['admitted_specs'], 'new unconsumed static64 cohort')
        folder = J / 'cases' / case
        s = copy.deepcopy(base)
        s.update(cohort=case, profile='P_S64_VS_UNIFIED1168_MSOFF')
        s['expected_effective_options']['-gpgpu_ep_l2_static_s64'] = '1'
        configs = []
        for i, r in enumerate(base['ordered_configs']):
            text = Path(r['path']).read_text()
            if i == len(base['ordered_configs'])-1:
                text += '\n# Fixed total1168 physical slots; strong static role partition1024/80/64.\n-gpgpu_ep_l2_static_s64 1\n'
            path = folder / 'env' / ('config-' + str(i) + '.config')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x') as f:
                f.write(text)
            configs.append(ref(path))
        s['ordered_configs'] = configs
        fref = q['consumed'][f_case]['accepted_point_ref']
        s['scientific_option_contract'] = dict(mode='S', complete_282=True, observer_profile_id='MS0_B0M0A1_FOUR_OFF',
            application_NI_receipt_ref=ni_ref, only_new_layout_delta={'-gpgpu_ep_l2_static_s64': '1'},
            reused_F_endpoint_ref=fref, F_accepted_endpoint_keeps_original_identity=True, no_new_F_launch=True,
            reference_MS0_S_spec_ref=ref(base_path),
            profile_contract_ref=ref(J / 'agent_b/p_s64_math_v1/S64_MATCHED_PROFILE_CONTRACT.json'))
        s['limits']['wall_seconds'] = max(s['limits']['wall_seconds'], 24*3600)
        s['pinned_files'][ni_ref['path']] = ni_ref['sha256']
        adapter.qualify_history_spec(s)
        refs.append(put(folder / 'control/FROZEN_SPEC.json', s, True))
        aliases.append(dict(new_S_cohort=case, existing_matched_F_cohort=f_case, existing_matched_F_point_ref=fref, no_relabel=True))
    stage_name = 'STAGE_P_S64_CONV_BLACK_AFTER_MS0_NI'
    stage = dict(schema='EP_FULL_PERF_FINITE_STAGE_V1', goal=GOAL, status='MAIN_REVIEWED_EXACT_FINITE_STAGE', stage=stage_name,
        scientific_owner='Main', maximum_new_starts=2, automatic_retry=False, refund=False, source_keep=True,
        authorization_ref=ref(J/'control/USER_AUTHORIZATION.json'), engine_ref=ref(J/'tools/ep_perf_native.py'), common_ref=ref(J/'tools/ep_perf_common.py'),
        specs=refs, resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME', application_NI_receipt_ref=ni_ref,
        predeclared_plan_ref=ref(J/'control/SEARCH_PLAN_P_S64_MS0_V1.json'), reused_F_aliases=aliases)
    sr = put(J / 'control' / (stage_name + '.json'), stage, True)
    print(json.dumps(dict(status='NI_PASS_AND_TWO_EXACT_NEW_S64_S_SPECS_PREPARED_ZERO_STARTS', ni_ref=ni_ref, stage_ref=sr)))


if __name__ == '__main__':
    main()
