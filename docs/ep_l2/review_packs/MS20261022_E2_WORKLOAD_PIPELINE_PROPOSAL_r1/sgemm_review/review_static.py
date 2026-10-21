"""Bounded SGEMM preparation review. Never imports/executes campaign runtime."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
A = '89c3f4e186e5a2514cda94163b37e3a813ec704e'
C = '93f6db1881bb7bbb59f5e7f53196b7441ef3268b'
D = '6e956ad5963f5ced177a3fca572cf6062d992846'
AP = 'docs/ep_l2/review_packs/MS20261021_A2_SGEMM_MAIN61_CONFIG_PROPOSAL_r1/'
CP = 'docs/ep_l2/review_packs/MS20261021_C_SGEMM_FALLBACK_BFS_HOST_r1/'
DP = 'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_DECISION_BUNDLE_r2/'
refs = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(commit, path, expected=None):
    size = int(subprocess.check_output(['git', 'cat-file', '-s', commit + ':' + path], cwd=ROOT))
    assert size <= 262144, (path, size)
    raw = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
    if expected:
        assert sha(raw) == expected, path
    refs.append({'commit': commit, 'path': path, 'bytes': len(raw), 'sha256': sha(raw)})
    return raw


def doc(commit, path, expected=None):
    return json.loads(blob(commit, path, expected))


def stat_only(path):
    s = os.stat(path)
    return {'path': str(path), 'resolved_path': str(Path(path).resolve()), 'device': s.st_dev,
            'inode': s.st_ino, 'nlink': s.st_nlink, 'bytes': s.st_size,
            'allocated_bytes': s.st_blocks * 512, 'mtime_ns': s.st_mtime_ns,
            'ctime_ns': s.st_ctime_ns, 'content_rehashed': False}


proposal = doc(A, AP + 'PROPOSAL.json')
coverage = doc(A, AP + 'QUALIFICATION_COVERAGE_MAP.json')
terminal = doc(A, AP + 'TERMINAL_BINDING_PROPOSAL.json')
merged = doc(D, DP + 'SGEMM_PREPARATION_MERGE.json')
manifest_raw = blob(C, CP + 'sgemm_empty_fallback/manifest.candidate.json',
                    'c0a758b2fc0552be62f827ecc31b7ce32c06353fe3dcab0a87cfbea4c7e5b104')
ranges_raw = blob(C, CP + 'sgemm_empty_fallback/certified_ranges.csv',
                  'ce98b276a772d17869de61ee6aa6cf6f7d856354eb4062b7c0c0c762d6e71944')
assert blob(A, AP + 'C_INPUT/manifest.candidate.json') == manifest_raw
assert blob(A, AP + 'C_INPUT/certified_ranges.csv') == ranges_raw
manifest = json.loads(manifest_raw)
assert manifest['status'] == 'SAFE_FALLBACK_NO_CERTIFIED_LINES'
assert manifest['scope'] == 'NO_READONLY_CERTIFICATION'
assert ranges_raw.decode().strip().splitlines() == ['first_line,last_line_inclusive']
assert manifest['framework_source_commit'] == '06cf7fd7d5dd7d0f0815345d4c692ee01bc3e025'
assert proposal['source_identity']['framework_source_commit'] == '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'


def options(names):
    effective = {}
    for name in names:
        tokens = shlex.split(blob(A, AP + 'CONFIGS/' + name).decode(), comments=True)
        assert len(tokens) % 2 == 0
        for key, value in zip(tokens[::2], tokens[1::2]):
            assert key.startswith('-') and key != '-config'
            effective[key] = value
    return effective


S = options(['base-0.config', 'base-1.config', 'base-2.config', 'S.config'])
F = options(['base-0.config', 'base-1.config', 'base-2.config', 'F.config'])
assert len(S) == 149 and len(F) == 154
changed = {key: {'S': S.get(key), 'F': F.get(key)} for key in sorted(S.keys() | F.keys())
           if S.get(key) != F.get(key)}
assert changed == merged['S_F_changed_options']
assert len(changed) == 10
assert not any('capacity_diag' in key or 'large_capacity' in key for key in F)
for key, value in {'-gpgpu_ep_l2_bank_ops': '1', '-gpgpu_ep_l2_payload_mode': '2',
                   '-gpgpu_ep_l2_wbuf_entries': '16', '-gpgpu_ep_l2_wad_entries': '128',
                   '-gpgpu_ep_l2_descriptor_pool_size': '512',
                   '-gpgpu_ep_l2_descriptor_per_line_cap': '32',
                   '-gpgpu_ep_l2_diag_copy_free': '0', '-gpgpu_ep_l2_diag_l2_data_free': '0',
                   '-gpgpu_ep_l2_tvd_fixed_entries': '0', '-gpgpu_ep_l2_static_s64': '0',
                   '-gpgpu_ep_l2_ideal_meta': '0', '-gpgpu_ep_l2_ideal_read_hit': '0',
                   '-gpgpu_ep_l2_ideal_wb': '0'}.items():
    assert S[key] == F[key] == value
assert [F[k] for k in ('-gpgpu_ep_l2_ft_mode', '-gpgpu_ep_l2_tvd_clean',
                      '-gpgpu_ep_l2_tvd_dirty', '-gpgpu_ep_l2_ro_tag_detach',
                      '-gpgpu_ep_l2_ro_line_mshr_bypass')] == ['2', '1', '1', '1', '1']
assert F['-gpgpu_ep_l2_ro_manifest_sha256'] == sha(manifest_raw)
assert F['-gpgpu_ep_l2_ro_ranges_sha256'] == sha(ranges_raw)
assert F['-gpgpu_ep_l2_ro_scope'] == manifest['scope']

input_stats = []
entry = Path(proposal['input']['entry'])
entry_raw = entry.read_bytes()
assert len(entry_raw) < 4096
assert sha(entry_raw) == manifest['commandlist_sha256']
assert entry_raw.decode() == proposal['input']['complete_commandlist']
for item in proposal['input']['trace_manifest']:
    observed = stat_only(entry.parent / item['name'])
    assert observed['bytes'] == item['bytes']
    observed['saved_expected_sha256'] = item['sha256']
    input_stats.append(observed)

old_proof_path = 'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/CANDIDATE_AUDIT.json'
proof = doc('6825d1cd0c87d8b0122e03a9dff5253c873b747b', old_proof_path,
            'be9074886c6a91a760d3df48e9fddf1b4b114728ea12cb1a1d44d573db906532')
sg = next(x for x in proof['results'] if x['workload'] == 'sgemm')
assert sg['first_rejected_record'] is None
assert sg['trace_content_sha256'] == proposal['input']['trace_content_sha256']
assert sg['trace_content_manifest'] == proposal['input']['trace_manifest']
assert sg['full_active_lane_instruction_records'] == 1658916864
assert sg['files'][0]['atomic_absence'] is True
assert sg['files'][0]['global_atomic_records'] == sg['files'][0]['shared_atomic_records'] == 0

gates = []
for row in coverage['existing_native_gates']:
    ref = row['evidence_ref']
    gate = doc(ref['commit'], ref['path'], ref['sha256'])
    assert gate['status'] == 'PASS' and gate['production_driven'] is True
    gates.append(row['gate'])
assert len(gates) == 18
parser_ref = terminal['parser_ref']
parser = blob(parser_ref['commit'], parser_ref['path'], parser_ref['sha256']).decode()
assert "r['scope']==resource['oracle']==opts['-gpgpu_ep_l2_ro_scope']" in parser
assert "r['manifest']==opts['-gpgpu_ep_l2_ro_manifest_sha256']" in parser
assert "'F':(2,0,0)" in parser
fallback = doc('0b608f2f9142d44e53d54a55679c1b00b504d6a6',
               'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/gates/mode_legality.json')
native_fallback = next(x for x in fallback['current_affected_native'] if x['case'] == 'new_combined_fallback')
assert native_fallback['actual_exit'] == 0 and native_fallback['expectation_verified'] is True

result = {
 'schema': 'E2_SGEMM_BOUNDED_PREPARATION_REVIEW_V1',
 'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status': 'STATIC_PREPARATION_PASS_NOT_INDEPENDENT_INPUT_QUALIFICATION_OR_LAUNCH_AUTHORITY',
 'source_identity': proposal['source_identity'], 'archive_identity': proposal['archive'],
 'registration_id': proposal['registration_id'],
 'registration_unchanged': 'REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE',
 'cohort': proposal['cohort'],
 'independently_reproduced_static_checks': {
  'effective_S_options': len(S), 'effective_F_options': len(F),
  'changed_options': changed, 'five_mechanisms_plus_five_input_bindings': True,
  'finite_payload': 1168, 'physical_bank_ops': 1, 'no_capacity_master_option_added': True,
  'empty_fallback_artifacts_equal_published_C': True,
  'actual_RO_opportunity': 'UNKNOWN_NOT_MEASURED_ZERO',
  'T_M': 'ON', 'command_count': 3, 'kernel_count': 1,
  'expected_full_instructions': 1658916864,
  'current_small_commandlist_SHA_matches': True,
  'current_large_input_stat_matches_saved_bytes': True,
  'current_large_input_SHA_proven_by_this_review': False,
  'saved_complete_grammar_opcode_nonatomic_proof_reused': True,
  'exact_main61_generic_native_gate_metadata_SHA_matches': len(gates),
  'gate_names': gates,
  'existing_exact_main61_empty_fallback_native_exit0_reusable': True,
  'parser_supports_F_and_actual_scope_manifest_binding_statically': True,
  'new_mechanism_build_or_bulk_native_needed_by_known_static_evidence': False,
  'C_framework_field_is_preparation_schema_lineage_not_runtime_identity': True},
 'input_stats': input_stats,
 'saved_trace_content_sha256': proposal['input']['trace_content_sha256'],
 'binary_archive_stat_only': [stat_only(proposal['binary']['path']), stat_only(proposal['archive']['path'])],
 'minimal_pending_obligations': [
  {'owner': 'E2', 'gate': 'CURRENT_COMPLETE_INPUT_CONTENT_BINDING',
   'need': 'Original frozen-input content binding must close under original controller. Stat/bytes and inherited SHA alone do not prove current large-body equality; reuse valid exact saved proof and satisfy original fresh digest identity gate without another grammar scan.'},
  {'owner': 'E2', 'gate': 'INDEPENDENT_SGEMM_COMBINATION_INPUT_Q_AND_PARSER_SEAL',
   'need': 'Write exact independent SGEMM S/F qualification with own input semantics, scope admission, finite profile, C empty-candidate adoption and main61 parser/config/source/native-evidence seal; do not copy FWT Q or mislabel candidate metadata as qualified.'},
  {'owner': 'user_then_E2', 'gate': 'NEW_SEPARATE_TWO_START_EXPLORATORY_BATCH_AUTHORITY',
   'need': 'Approve exact new SGEMM S/F independent exploratory batch of two actual starts. Original32 and contingency8 buckets stay unchanged/full; removal of overall numerical cap does not grant this condition or expand those buckets.'},
  {'owner': 'E2_at_each_start', 'gate': 'ORIGINAL_CENTRAL_RESOURCE_AND_IDENTITY_ADMISSION',
   'need': 'Verify current actual source/main/archive/config/spec/input/oracle/parser/lease, cumulative output allowance, collector/metadata reserves, workspace5GiB floor plus2GiB monitor, CPU/RAM/Share. No registry changes made here.'},
  {'owner': 'E2_after_actual_run', 'gate': 'INDEPENDENT_TERMINAL_ACCEPTANCE',
   'need': 'Native OS wait exit0, all1658916864 instructions and one kernel, commandlist3 complete, exact64slice FT/B0/MS/TVD/RO frames, epoch closure/final snapshot, exact-once identities and resource drain; actual RO scope/hash/config equal, no fatal/cap/timeout. These are future observations, never preparation PASS.'}],
 'proposal_cost': {'actual_starts_now': 0, 'future_starts_if_separately_approved': 2,
  'endpoint_cap_each_bytes': 402653184, 'pair_endpoint_caps_bytes': 805306368,
  'separate_collector_qualification_metadata_reserve': 'Root combined proposal must quantify; not included in768MiB endpoint cap',
  'walltime': 'UNKNOWN', 'offline_scan837_48_seconds_is_not_runtime': True,
  'no_automatic_retry_or_refund': True},
 'claim_limits': ['Existing frozen trace model only; original source revision/capture command and numeric payload identity remain UNKNOWN.',
                  'No Btree replacement or original-main-set promotion; independently labeled SGEMM exploratory set.',
                  'No measured zero-RO claim, no certified positive RO opportunity, no inference of detach mechanism activation.',
                  'No all-new-capacity93a9 qualification transferred to finite main61 or conversely.'],
 'new_application_native_build_goal_or_controller_actions': 0,
 'central_registry_lease_client_changes': 0,
 'large_trace_body_bytes_read': 0,
 'source_refs': refs,
}
(OUT / 'STATIC_REVIEW.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': result['status'], 'gates': len(gates), 'refs': len(refs),
                  'large_trace_bytes_read': 0, 'output': str(OUT / 'STATIC_REVIEW.json')}))
