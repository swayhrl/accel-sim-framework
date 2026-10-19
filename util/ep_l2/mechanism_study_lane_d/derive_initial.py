"""Bounded offline D analysis. No simulator, compiler, body rehash or raw mutation."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
L5 = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1')
OLD = Path('/workspace/ep_l2_mechanism_lane3_v1/derived_r2')
TARGET = Path('/workspace/worktrees/accel-sim-ep-l2/docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1')
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
AUTHORITY = 'd9263fa2431592b33e900d9b48c6f20029d8b544'
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
UNKNOWN = 'UNKNOWN'
SOURCES = {}

def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def source(path):
    path = Path(path)
    data = path.read_bytes()
    SOURCES[str(path)] = {'sha256': sha_bytes(data), 'bytes': len(data)}
    return data
def read_json(path): return json.loads(source(path))
def read_csv(path): return list(csv.DictReader(source(path).decode().splitlines()))
def write_json(name, obj): (OUT / name).write_text(json.dumps(obj, indent=2) + '\n')
def write_csv(name, rows):
    if not rows: return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / name).open('w', newline='') as stream:
        w = csv.DictWriter(stream, fieldnames=fields, restval=UNKNOWN); w.writeheader(); w.writerows(rows)
def presence(value):
    return UNKNOWN if value in [None, '', UNKNOWN] else 'YES' if int(value) else 'NO'

def tail_records(path):
    """At most 2 MiB per immutable raw; last cumulative row per slice, never sum kernels."""
    path = Path(path)
    with path.open('rb') as stream:
        start = max(0, path.stat().st_size - 2**21)
        stream.seek(start); data = stream.read()
    SOURCES[str(path)] = {'read_scope': 'last_2MiB_only_not_full_rehash',
                          'tail_sha256': sha_bytes(data), 'bytes': path.stat().st_size,
                          'tail_offset': start}
    app, ft, mq, rg = {}, {}, {}, {}
    for line in data.decode(errors='replace').splitlines():
        parts = line.split('|')
        fields = dict(p.split('=', 1) for p in parts[1:] if '=' in p)
        if 'slice' not in fields: continue
        sl = int(fields['slice'])
        if line.startswith('EPL2B0V1|scope=application|interval=application_cumulative|'):
            app[sl] = fields
        elif line.startswith('EPL2FTV1|SUMMARY|'): ft[sl] = fields
        elif line.startswith('EPL2SERVICEV1|MQ2|'): mq[sl] = fields
        elif line.startswith('EPL2SERVICEV1|RG1_BANK|'): rg[(sl, int(fields['bank']))] = fields
    return app, ft, mq, rg

def total(records, field, expected=64):
    if len(records) != expected or any(field not in row for row in records.values()): return UNKNOWN
    return sum(int(row[field]) for row in records.values())

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    accepted_file = L5 / 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/APPLICATION_ACCEPTANCE.json'
    acceptance = read_json(accepted_file)
    accepted = {r['run_key']: r for r in acceptance['rows'] if r['scientific_acceptance'] == 'CURRENT_ACCEPTED'}
    pressure = read_csv(OLD / 'pressure_and_banks.csv')
    h0 = [r for r in pressure if r['condition'] == 'H0' and r['binary'].startswith('23094a9d')]
    assert len(h0) == 10
    opportunities, excerpts = [], {}
    for row in h0:
        a = accepted[row['run_key']]
        assert a['raw_log_sha256'] == row['raw_sha256'] and a['observed_cycles'] == int(row['cycles'])
        app, ft, _, _ = tail_records(row['raw_log'])
        assert set(app) == set(ft) == set(range(64))
        assert all(int(r['completion_cycle']) == int(row['cycles']) for r in app.values())
        assert total(app, 'c7d_line_mshr_full_block') == int(row['c7d_line_mshr_full_block'])
        assert total(ft, 'wbuf_full') == int(row['wbuf_full'])
        tag = total(app, 'c7d_tag_set_all_reserved_block')
        excerpts[row['run_key']] = {
            'raw': row['raw_log'], 'prior_accepted_full_raw_sha256': row['raw_sha256'],
            'current_scope': 'terminal64slice_fields_recovered_from_bounded_tail_not_full_rehash',
            'slice_fields': [{k: r.get(k, UNKNOWN) for k in ['slice', 'completion_cycle', 'samples',
                             'c7d_tag_set_all_reserved_block', 'c7d_line_mshr_full_block',
                             'c7d_descriptor_pool_full_block']} for r in app.values()]}
        r = {k: row[k] for k in ['workload', 'cycles', 'instructions', 'run_key', 'core', 'framework',
                                 'binary', 'trace', 'raw_log', 'raw_sha256']}
        r.update(evidence_group='HISTORICAL_H0_SOURCE2309_CURRENT_ACCEPTED', baseline_profile=row['mode'],
                 W_WB_space_refusal=presence(row['wbuf_full']), W_refusal_retry_events=row['wbuf_full'],
                 W_distinct_blocked_requests=UNKNOWN, W_wait_distribution=UNKNOWN,
                 W_copy_lines=row['copy_lines'], W_WB_record_peak=row['staged_record_peak'],
                 W_WAD_control_refusal=presence(row['c7d_wad_full_events']),
                 W_WAD_control_retry_events=row['c7d_wad_full_events'],
                 W_physical_WB_role_mean=row['physical_WB_role_mean'], V_post_eviction_reuse=UNKNOWN,
                 R_tag_all_pending=presence(tag), R_tag_retry_events=tag,
                 R_line_MSHR_refusal=presence(row['c7d_line_mshr_full_block']),
                 R_line_MSHR_retry_events=row['c7d_line_mshr_full_block'],
                 R_descriptor_refusal=presence(total(app, 'c7d_descriptor_pool_full_block')),
                 R_distinct_blocked_requests=UNKNOWN,
                 DRAM_scheduler_pressure=presence(row['c7d_dram_scheduler_full_block']),
                 DRAM_scheduler_refusal_events=row['c7d_dram_scheduler_full_block'],
                 DRAM_issue_attempts=row['c7e_dram_issue_attempt'], bank_logical_ops=row['bank_logical_ops'],
                 limitations='Retries != distinct UIDs or disjoint GPU cycles; WB roles != WB records; NO means zero observed in this full source/input/mode only; V lacks actual L2-order shadow')
        opportunities.append(r)
    write_csv('OPPORTUNITY_TABLE.csv', opportunities)
    write_json('TERMINAL_FIELD_EVIDENCE.json', excerpts)

    # Older B0 measurements are input-selection context, not current FT performance anchors.
    candidate_names = ['btree', 'dwt2d', 'spmv', 'scan', 'sgemm']
    blocks = {r['workload']: r for r in read_csv(TARGET / 'target_blocking_matrix.csv') if r['variant'] == 'B0-Legacy'}
    comp = {r['workload']: r for r in read_csv(TARGET / 'target_baseline_comparison.csv')}
    runs = {r['workload']: r for r in read_csv(TARGET / 'ACCEPTED_FORMAL_RUNS.csv') if r['variant'] == 'B0-Legacy'}
    manifest_path = REPO / 'docs/l2_char_v1/ROUND1_WAVE1_TRACE_MANIFEST.json'
    manifest = read_json(manifest_path)
    roster = {r['workload']: r for r in manifest['trace_body_sha256']}
    candidates = []
    for name in candidate_names:
        m = roster[name]; entry = Path(m['kernelslist']); commands = source(entry).decode()
        listed = [l.strip() for l in commands.splitlines() if l.strip() and not l.startswith('Memcpy')]
        assert listed == [Path(x['path']).name for x in m['trace_files']]
        assert sha_bytes(commands.encode()) == m['kernelslist_sha256']
        bodies = []
        for x in m['trace_files']:
            path = Path(x['path']); exists = path.is_file()
            bodies.append(dict(x, exists=exists, actual_bytes=path.stat().st_size if exists else None,
                               current_full_body_hash='NOT_REPEATED_BY_D_REBIND_BY_E',
                               size_matches_committed=exists and path.stat().st_size == x['bytes']))
        script = entry.parent.parent / 'run.sh'
        capture = source(script).decode() if script.is_file() else UNKNOWN
        old = runs[name]; c = comp[name]; b = blocks[name]
        # The two selected candidates must match the old complete command list provenance.
        assert old['trace_sha256'] == m['kernelslist_sha256']
        candidate = {'workload': name, 'selected_new_input': name in ['btree', 'dwt2d'],
                     'input': m['input'], 'entry': str(entry), 'commandlist_literal': commands,
                     'commandlist_sha256': m['kernelslist_sha256'], 'bodies': bodies,
                     'body_count': len(bodies), 'body_bytes': sum(x['bytes'] for x in bodies),
                     'complete_declared_body_coverage': all(x['size_matches_committed'] for x in bodies),
                     'published_trace_tree_sha256': m['trace_tree_sha256'],
                     'published_tree_hash_definition': 'ROUND1_WAVE1_TRACE_MANIFEST tree hash; not Lane5 input_spec trace_content hash',
                     'capture_script': str(script) if script.exists() else None,
                     'capture_script_literal': capture, 'directory_version_label': '9.1' if '/9.1/' in str(entry) else '11.0',
                     'toolchain_version': 'capture CUDA_VERSION=9.1 declaration, not directory inference' if script.exists() else UNKNOWN,
                     'application_source_revision': UNKNOWN,
                     'runtime_input': 'trace replay; capture run.sh/data arguments retained as provenance, never executed by D',
                     'historical_full_instructions': int(old['terminal_instructions']),
                     'expected_full_application_instructions': int(old['terminal_instructions']),
                     'historical_baseline_cycles': int(old['terminal_cycles']),
                     'expected_exit': 'normal full declared command list, exact instructions, hardware drain; cycles unrestricted',
                     'baseline_pressure': {k: b[k] for k in ['tag_set_block', 'line_mshr_full_block', 'descriptor_pool_full_block',
                                            'per_address_cap_block', 'wad_full', 'scheduler_causal_block']},
                     'historical_runtime_core': old['runtime_core_sha'],
                     'historical_runtime_framework': old['runtime_framework_sha'],
                     'historical_config': old['runtime_config_composite_sha256'],
                     'historical_raw_log': old['raw_log_path'], 'historical_raw_sha256': old['raw_log_uncompressed_sha256'],
                     'current_readonly_epoch_certificate': 'UNKNOWN_NOT_GRANTED_BY_D',
                     'current_new_binary_qualification': 'PENDING_A_E',
                     'scope_limit': 'old B01152/256 context differs from new1168/512 FT; no current source qualification or post-eviction-hit inference'}
        reasons = {
            'btree': 'Contract-priority complete2-kernel query input; old per-address cap674, no measured tag/MSHR-full. A read-heavy negative-pressure control; no promised RO/victim hit.',
            'dwt2d': 'Contract-priority full1024x1024 ten-kernel input; old WAD74044/scheduler281249 retry evidence contrasts btree. No victim reuse proof.',
            'spmv': 'Predeclared first fallback only if a selected input fails real completeness/eligibility or budget; small34.5MB complete input, old descriptor pressure361635. Not auto-added.',
            'scan': 'Not selected:5.329GB/33kernels and much larger historical cycles; real old tag/descriptor pressure noted, but greater input/runtime cost. Not a zero-pressure claim.',
            'sgemm': 'Not selected:2.216GB,1.659B instructions; old per-address-cap1409 but no measured tag/MSHR-full; literal capture script absent. Can rebuild wrapper from provenance if needed, no blanket halt.'}
        candidate['selection_reason'] = reasons[name]; candidates.append(candidate)
        opportunities.append({
            'workload': name, 'baseline_profile': 'B0-Legacy',
            'evidence_group': 'HISTORICAL_C7E_CANDIDATE_CONTEXT_NOT_CURRENT_FT',
            'cycles': old['terminal_cycles'], 'instructions': old['terminal_instructions'],
            'core': old['runtime_core_sha'], 'framework': old['runtime_framework_sha'],
            'binary': UNKNOWN, 'trace': m['trace_tree_sha256'],
            'trace_hash_scope': 'published ROUND1 tree hash, not Lane5 composite content hash',
            'raw_log': old['raw_log_path'], 'raw_sha256': old['raw_log_uncompressed_sha256'],
            'W_WB_space_refusal': UNKNOWN, 'W_refusal_retry_events': UNKNOWN,
            'W_distinct_blocked_requests': UNKNOWN, 'W_wait_distribution': UNKNOWN,
            'W_copy_lines': UNKNOWN, 'W_WB_record_peak': UNKNOWN, 'W_physical_WB_role_mean': UNKNOWN,
            'W_WAD_control_refusal': presence(b['wad_full']), 'W_WAD_control_retry_events': b['wad_full'],
            'V_post_eviction_reuse': UNKNOWN, 'R_tag_all_pending': presence(b['tag_set_block']),
            'R_tag_retry_events': b['tag_set_block'], 'R_line_MSHR_refusal': presence(b['line_mshr_full_block']),
            'R_line_MSHR_retry_events': b['line_mshr_full_block'],
            'R_descriptor_refusal': presence(b['descriptor_pool_full_block']),
            'R_distinct_blocked_requests': UNKNOWN,
            'DRAM_scheduler_pressure': presence(b['scheduler_causal_block']),
            'DRAM_scheduler_refusal_events': b['scheduler_causal_block'],
            'limitations': 'old B0 context/budget only; no WBUF16 counter or current runtime qualification. tag/MSHR/descriptor/per-address-cap are distinct. V and RO eligibility unknown.'})
    write_csv('OPPORTUNITY_TABLE.csv', opportunities)
    # Never redate the preregistration on rerun.
    selection_path = OUT / 'INPUT_SELECTION.json'
    prior = json.loads(selection_path.read_text()) if selection_path.exists() else {}
    selected_at = prior.get('selected_at_utc', dt.datetime.now(dt.timezone.utc).isoformat())
    scope = read_json(OLD / 'INPUT_SCOPE.json')
    core_inputs = []
    for name in ['convolutionSeparable', 'FWT_7_21']:
        s = next(r for r in scope if r['workload'] == name)
        assert Path(s['entry']).read_text() == s['commandlist_literal']
        core_inputs.append(dict(s, expected_full_application_instructions=s['runtime_instruction_count'],
                                selected_conditions=['S', 'U', 'S_COPY_FREE', 'S_L2_DATA_FREE', 'U_L2_DATA_FREE'],
                                reason='contract default plus traditional WB/copy pressure; Conv also line-MSHR refusal; no new mechanism performance selection'))
    selection = {'campaign_id': CAMPAIGN, 'authority': AUTHORITY, 'selected_at_utc': selected_at,
                 'selection_policy': 'contract priority, complete existing input, traditional structural pressure and cost; no new mechanism speedup',
                 'core_diagnostic_inputs': core_inputs, 'new_inputs': ['btree', 'dwt2d'], 'candidates': candidates,
                 'default_full_starts_reserved': {'core_diagnostics': 10, 'new_input_pairs': 4, 'victim': 3, 'RO': 4, 'contingency': 3},
                 'V_target': 'UNKNOWN until actual L2-order opportunity; do not infer from SM trace order',
                 'R_target': 'convolutionSeparable is first pressure-backed candidate ONLY if C full-epoch subset oracle and A/E qualification succeed; do not shrink capacities to manufacture opportunity',
                 'ro_scope': 'UNKNOWN for every candidate until C full-epoch reads/stores/atomics/aliases/host writes proof; btree has host updates between kernels',
                 'screen_requested_by_D': 0, 'screens_if_needed': 'E only, original6x120s/2M cap; no automatic new starts',
                 'no_trace_copy_or_body_rehash': True, 'E_rebinding_required': 'fresh run input_spec/whole-body identity and source-bound qualification; committed hashes+current size checks alone are not new scientific qualification'}
    write_json('INPUT_SELECTION.json', selection)

    historical = []
    for r in read_csv(OLD / 'finite_pairs.csv'):
        assert r['B_key'] in accepted and r['U_key'] in accepted
        a, b = accepted[r['B_key']], accepted[r['U_key']]
        assert a['binary_sha256'] == b['binary_sha256'] == r['binary']
        assert a['trace_content_sha256'] == b['trace_content_sha256'] == r['trace']
        assert a['observed_cycles'] == int(r['B_cycles']) and b['observed_cycles'] == int(r['U_cycles'])
        historical.append(dict(r, scope='HISTORICAL_CURRENT_ACCEPTED_NOT_NEW_STUDY', interpretation='counter/placement/capacity interaction; not pure-copy or disjoint GPU-cycle attribution'))
    write_csv('HISTORICAL_H0_R19_PAIRS.csv', historical)
    r19 = read_json(L5 / 'docs/ep_l2/review_packs/FT20261018_LANE5_R19_GOAL_COMPLETION_AUDIT_r1/10_PAIR_PUBLICATION_AUDIT.json')
    r19_rows = []
    for record in r19:
        assert record['both_current_accepted']
        comp = record['comparison']
        r19_rows.append({'workload': record['workload'], 'regime': record['regime'],
                         'B_cycles': comp['C_B_h'], 'U_cycles': comp['C_U_h'],
                         'B_over_U': comp['S_h'], 'interaction_vs_own_H0': comp['J_h'],
                         'both_current_accepted': True, 'same_binary': comp['same_binary'],
                         'publication': record['publication_commit'], 'pair_pack': record['pair_pack'],
                         'scope': 'HISTORICAL_R19_CLOSED_10_PAIRS; overlaps some old18 reference rows; never count twice or restart unused3'})
    assert len(r19_rows) == 10
    write_csv('HISTORICAL_R19_COMPLETE_10_PAIRS.csv', r19_rows)
    service_path = L5 / 'docs/ep_l2/review_packs/FT20261018_LANE5_FINAL_INTAKE_COMPLETION_AUDIT_r1/FINAL_MICROOPT_MATRIX_18.csv'
    grid = read_csv(service_path)
    with (SHARED / 'REGISTRY.lock').open() as lock:
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_SH); registry = read_json(SHARED / 'RUN_REGISTRY.json')
    for r in grid:
        r['scope'] = 'HISTORICAL_MICROOPT_SOURCE_F0_NOT_NEW_STUDY'
        if r['scientific_acceptance'] != 'CURRENT_ACCEPTED':
            assert not r['cycles']; r.update(mq2_bypasses=UNKNOWN, rg1_recovered_grants=UNKNOWN,
                                            same_binary_OFF_ratio=UNKNOWN); continue
        assert accepted[r['run_key']]['observed_cycles'] == int(r['cycles'])
        anchor = next(x for x in grid if x['workload'] == r['workload'] and x['profile'] == r['profile'] and x['regime'] == 'SERVICE_OFF')
        assert anchor['binary_sha256'] == r['binary_sha256'] and anchor['trace_content_sha256'] == r['trace_content_sha256']
        r['same_binary_OFF_ratio'] = int(anchor['cycles']) / int(r['cycles'])
        raw = Path(registry['runs'][r['run_key']]['result_directory']) / 'raw.log'
        _, _, mq, rg = tail_records(raw)
        r.update(mq2_bypasses=total(mq, 'bypasses'), rg1_recovered_grants=total(rg, 'recovered_grants', 256), raw_log=str(raw))
    write_csv('HISTORICAL_MICROOPT_MATRIX_18.csv', grid)
    four = []
    for r in accepted.values():
        if not r['binary_sha256'].startswith('fb67') or r['workload'] not in ['convolutionSeparable', 'FWT_7_21']: continue
        if any(r['identity']['ideal_vector'].values()): continue
        f = r['identity']['feature_vector']
        profile = 'S64' if f['static_s64'] else 'U_CAP16' if f['wb_local_cap'] == 16 else 'U' if f['unified_wb'] else 'B16'
        four.append({'workload': r['workload'], 'profile': profile, 'cycles': r['observed_cycles'],
                     'instructions': r['instructions'], 'run_key': r['run_key'], 'binary_sha256': r['binary_sha256'],
                     'core': r['core_source_commit'], 'framework': r['framework_source_commit'],
                     'config': r['runtime_config_sha256'], 'trace': r['trace_content_sha256'],
                     'scope': 'HISTORICAL_FOUR_MODE_SAME_FB_BINARY_NOT_PURE_COPY_ABLATION'})
    assert len(four) == 8
    write_csv('HISTORICAL_FOUR_MODE.csv', four)
    refs = {}
    frozen = [('f3d89e77de0fbac16a05df42bd84f02f54dbc890', 'docs/ep_l2/mechanism_analysis/EPL2_MECHANISM_ANALYSIS_AND_MINIMAL_VALIDATION_V1/r1/CASE_ANALYSIS.md')]
    frozen += [(AUTHORITY, 'docs/ep_l2/chatgpt_handoff/mechanism_study_2026_10_19_v1/' + name)
               for name in ['MASTER_PLAN.md', 'EXPERIMENTS.md', 'CAMPAIGN.json', 'FIVE_LANE_GOALS.md']]
    for commit, path in frozen:
        raw = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=REPO)
        refs[path] = {'commit': commit, 'sha256': sha_bytes(raw)}
    write_json('SOURCE_MANIFEST.json', {'authority': AUTHORITY, 'old_Lane5_frozen_HEAD': '94fd48b69b37adb692e6152301b317f5f2e6a1e9',
                                      'old_Lane5_acceptance_generation': acceptance['generation'], 'sources': SOURCES,
                                      'immutable_references_read': refs,
                                      'analysis_source_sha256': sha_bytes(Path(__file__).read_bytes()),
                                      'large_input_body_hashing': 'NOT_REPEATED', 'application_starts_by_D': 0})
    print(json.dumps({'H0_rows': len(h0), 'candidate_context_rows': len(candidates), 'same_binary_historical_pairs': len(historical),
                      'historical_microopt_rows': len(grid), 'four_mode_rows': len(four), 'new_study_applications_started': 0}))

if __name__ == '__main__': main()
