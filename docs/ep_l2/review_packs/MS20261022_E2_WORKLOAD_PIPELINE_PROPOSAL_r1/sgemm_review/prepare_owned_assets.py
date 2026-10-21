"""Copy bounded published candidates into E ownership; no adoption or execution."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
ASSETS = OUT / 'prepared_assets'
A = '89c3f4e186e5a2514cda94163b37e3a813ec704e'
C = '93f6db1881bb7bbb59f5e7f53196b7441ef3268b'
AP = 'docs/ep_l2/review_packs/MS20261021_A2_SGEMM_MAIN61_CONFIG_PROPOSAL_r1/'
CP = 'docs/ep_l2/review_packs/MS20261021_C_SGEMM_FALLBACK_BFS_HOST_r1/'
COPIES = []
RAW = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(commit, path):
    size = int(subprocess.check_output(['git', 'cat-file', '-s', commit + ':' + path], cwd=ROOT))
    assert size <= 65536
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)


def copy(commit, path, relative):
    raw = blob(commit, path)
    dest = ASSETS / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    assert dest.read_bytes() == raw
    COPIES.append({'source_commit': commit, 'source_path': path,
                   'source_sha256': sha(raw), 'source_bytes': len(raw),
                   'prepared_path': str(dest), 'relative_prepared_path': relative,
                   'prepared_sha256_before_path_rebind': sha(raw)})
    RAW[relative] = raw
    return dest


for name in ['base-0.config', 'base-1.config', 'base-2.config', 'S.config', 'F.config']:
    copy(A, AP + 'CONFIGS/' + name, 'CONFIGS/' + name)
for name in ['manifest.candidate.json', 'certified_ranges.csv']:
    raw = blob(C, CP + 'sgemm_empty_fallback/' + name)
    assert blob(A, AP + 'C_INPUT/' + name) == raw
    copy(C, CP + 'sgemm_empty_fallback/' + name, 'C_INPUT/' + name)
copy(C, CP + 'SGEMM_COMMANDLIST.txt', 'C_INPUT/SGEMM_COMMANDLIST.txt')
assert blob(A, AP + 'C_INPUT/SGEMM_COMMANDLIST.txt') == RAW['C_INPUT/SGEMM_COMMANDLIST.txt']


def opts(raws):
    result = {}
    for raw in raws:
        tokens = shlex.split(raw.decode(), comments=True)
        assert len(tokens) % 2 == 0
        for key, value in zip(tokens[::2], tokens[1::2]):
            assert key.startswith('-') and key != '-config'
            result[key] = value
    return result


rebindings = []
for profile in ['S', 'F']:
    relative = 'CONFIGS/' + profile + '.config'
    original = RAW[relative]
    effective = opts([original])
    updated = original
    for option, target_name in [('-gpgpu_ep_l2_ro_ranges', 'certified_ranges.csv'),
                                 ('-gpgpu_ep_l2_ro_manifest', 'manifest.candidate.json')]:
        if option not in effective:
            continue
        before = effective[option]
        after = str((ASSETS / 'C_INPUT' / target_name).resolve())
        # The exact published path appears once; all other bytes must survive.
        assert updated.count(before.encode()) == 1
        updated = updated.replace(before.encode(), after.encode(), 1)
        rebindings.append({'profile': profile, 'option': option, 'before': before, 'after': after})
    old_options, new_options = opts([original]), opts([updated])
    assert old_options.keys() == new_options.keys()
    differences = {key for key in old_options if old_options[key] != new_options[key]}
    assert differences <= {'-gpgpu_ep_l2_ro_ranges', '-gpgpu_ep_l2_ro_manifest'}
    (ASSETS / relative).write_bytes(updated)
assert len(rebindings) == 2 and all(x['profile'] == 'F' for x in rebindings)

base_names = ['CONFIGS/base-0.config', 'CONFIGS/base-1.config', 'CONFIGS/base-2.config']
old = {p: opts([RAW[n] for n in base_names + ['CONFIGS/' + p + '.config']]) for p in ['S', 'F']}
new = {p: opts([(ASSETS / n).read_bytes() for n in base_names + ['CONFIGS/' + p + '.config']]) for p in ['S', 'F']}
assert len(new['S']) == 149 and len(new['F']) == 154
assert old['S'] == new['S']
assert {key for key in old['F'] if old['F'][key] != new['F'][key]} == {
    '-gpgpu_ep_l2_ro_ranges', '-gpgpu_ep_l2_ro_manifest'}
pair_diff = {k: {'S': new['S'].get(k), 'F': new['F'].get(k)}
             for k in sorted(new['S'].keys() | new['F'].keys())
             if new['S'].get(k) != new['F'].get(k)}
assert len(pair_diff) == 10
assert new['F']['-gpgpu_ep_l2_ro_ranges_sha256'] == sha(RAW['C_INPUT/certified_ranges.csv'])
assert new['F']['-gpgpu_ep_l2_ro_manifest_sha256'] == sha(RAW['C_INPUT/manifest.candidate.json'])
assert new['F']['-gpgpu_ep_l2_ro_scope'] == 'NO_READONLY_CERTIFICATION'
for k in new['S'].keys() | new['F'].keys():
    assert 'capacity_diag' not in k and 'large_capacity' not in k
for k, val in {'-gpgpu_ep_l2_bank_ops': '1', '-gpgpu_ep_l2_wbuf_entries': '16',
                '-gpgpu_ep_l2_payload_mode': '2', '-gpgpu_ep_l2_descriptor_pool_size': '512',
                '-gpgpu_ep_l2_descriptor_per_line_cap': '32', '-gpgpu_ep_l2_wad_entries': '128',
                '-gpgpu_ep_l2_static_s64': '0', '-gpgpu_ep_l2_tvd_fixed_entries': '0',
                '-gpgpu_ep_l2_diag_copy_free': '0', '-gpgpu_ep_l2_diag_l2_data_free': '0',
                '-gpgpu_ep_l2_ideal_meta': '0', '-gpgpu_ep_l2_ideal_read_hit': '0',
                '-gpgpu_ep_l2_ideal_wb': '0'}.items():
    assert new['S'][k] == new['F'][k] == val
assert [new['F'][k] for k in ['-gpgpu_ep_l2_ft_mode', '-gpgpu_ep_l2_tvd_clean',
    '-gpgpu_ep_l2_tvd_dirty', '-gpgpu_ep_l2_ro_tag_detach', '-gpgpu_ep_l2_ro_line_mshr_bypass']] == ['2','1','1','1','1']
manifest = json.loads(RAW['C_INPUT/manifest.candidate.json'])
assert manifest['commandlist_sha256'] == sha(RAW['C_INPUT/SGEMM_COMMANDLIST.txt'])
assert manifest['commandlist'].startswith('/workspace/worktrees/accel-sim-decoupled-l2/')
for row in COPIES:
    current = Path(row['prepared_path']).read_bytes()
    row.update(prepared_sha256=sha(current), prepared_bytes=len(current),
               byte_identical_to_published=current == RAW[row['relative_prepared_path']])
report = {
    'schema': 'E2_OWNED_SGEMM_STATIC_ASSET_PREPARATION_V1',
    'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PREPARED_NOT_E_SEALED_NOT_QUALIFIED_NOT_ADOPTED_NOT_LAUNCHABLE',
    'asset_owner': 'E2', 'source_refs_and_current_asset_identity': COPIES,
    'allowed_nonsemantic_rebindings': rebindings,
    'only_two_F_path_values_changed': True,
    'S_config_byte_identical_to_A2': True,
    'other_F_option_values_unchanged': True,
    'C_candidate_manifest_ranges_commandlist_byte_identical': True,
    'actual_full_trace_entry_unchanged': manifest['commandlist'],
    'metadata_commandlist_copy_is_not_runtime_trace_entry': True,
    'effective_options': new,
    'effective_option_counts': {'S': len(new['S']), 'F': len(new['F'])},
    'S_F_option_differences': pair_diff,
    'finite_policy': {'payload_slots': 1168, 'resident_tags': 1024, 'line_mshrs': 128,
                      'descriptors': 512, 'shared_wad_tvd': 128, 'per_address_cap': 32,
                      'banks': 4, 'bank_ops_per_physical_cycle': 1,
                      'F_WVTM': [1,1,1,1], 'diagnostic_and_ideal_flags': 'OFF',
                      'capacity_master_option': 'ABSENT_OLD_MAIN61_DO_NOT_APPEND'},
    'source_identity': {'core_source_commit': 'd010911e3174a3764791183cd108fe4664ba8731',
                        'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
                        'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
                        'binary_sha256': '61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'},
    'source_identity_inherited_candidate_binding_not_fresh_binary_verification': True,
    'actual_RO_opportunity': 'UNKNOWN_NOT_MEASURED_ZERO',
    'scientific_scope_registry_parser_qualification_changes': 0,
    'new_native_app_build_goal_controller_actions': 0,
    'large_trace_body_bytes_read': 0,
}
(OUT / 'PREPARED_ASSET_BINDING.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'asset_count': len(COPIES),
                  'only_two_F_paths_changed': True, 'S': len(new['S']), 'F': len(new['F']),
                  'binding_sha256': sha((OUT / 'PREPARED_ASSET_BINDING.json').read_bytes())}))
