"""Exact common native plan preparation only; no compiler, lease, or applications."""
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(spec, handoff, core, build, out, suite):
    for rel, expected in spec['control_files_SHA256'].items():
        assert sha(handoff / rel) == expected, 'changed frozen input: ' + rel
    for rel, expected in spec['core_inputs_SHA256'].items():
        assert sha(core / rel) == expected, 'changed Core input: ' + rel
    if spec.get('release_kind') == 'L2_LARGE_CAPACITY_DIAGNOSTIC':
        inputs=out/'inputs';inputs.mkdir()
        common=(core/'tests/ep_l2/ft_wbuf.config').read_text()+"\n-gpgpu_simple_dram_model 0\n-gpgpu_ep_l2_ms_observer 1\n"
        generated={
          'DEFAULT.config':common,
          'OFF.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 0\n',
          'ON.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 1\n',
          'ON64.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 1\n-gpgpu_n_mem 32\n-gpgpu_n_sub_partition_per_mchannel 2\n',
          'REJECT_COPY.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 1\n-gpgpu_ep_l2_diag_copy_free 1\n',
          'REJECT_RO.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 1\n-gpgpu_ep_l2_ro_tag_detach 1\n',
          'REJECT_FORCE_HIT.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 1\n-l2_ideal 1\n',
          'REJECT_VALUE.config':common+'-gpgpu_ep_l2_diag_l2_large_capacity 2\n',
        }
        for name,text in generated.items():(inputs/name).write_text(text)
        replacements={'{CORE}':str(core),'{BUILD}':str(build),'{OUT}':str(out),'{INPUTS}':str(inputs)}
        cases=[]
        for row in spec['cases']:
            assert re.fullmatch(r'ep_l2_[A-Za-z0-9_]+',row['target'])
            assert row['expected_exit'] in (0,21) and 0<row['timeout_seconds']<=120
            args=[]
            for arg in row['args']:
                for token,value in replacements.items():arg=arg.replace(token,value)
                args.append(arg)
            cases.append(dict(row,native_command=[str(build/'gpgpu-sim'/row['target']),*args]))
        return cases,{str(f):sha(f) for f in inputs.iterdir()}
    inputs = out / 'inputs'
    inputs.mkdir()
    original = handoff / 'full_system_v2/C_FROZEN_INPUT_r1/native_inputs'
    copied = inputs / 'C_NATIVE'
    copied.mkdir()
    # Copy only the explicit tiny frozen inputs, never traces/old results.
    for src in sorted(original.rglob('*')):
        if src.is_file():
            rel = src.relative_to(original)
            assert (src.relative_to(handoff)).as_posix() in spec['control_files_SHA256']
            dst = copied / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    old_prefix = '/workspace/worktrees/accel-sim-ep-l2-ms20261019-c-ro-v1/docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/c/full_system_v2_r1/native_inputs'
    for dst in sorted(copied.glob('*.config')):
        dst.write_text(dst.read_text().replace(old_prefix, str(copied)))
    full = (copied / 'T1M1.config').read_text()
    generated = {
        'R_ONLY.config': full + '\n-gpgpu_ep_l2_tvd_clean 0\n-gpgpu_ep_l2_tvd_dirty 0\n',
        'GPU64.config': full + '\n-gpgpu_n_mem 32\n-gpgpu_n_sub_partition_per_mchannel 2\n-gpgpu_cache:dl2 S:64:128:16,L:B:m:L:L,A:128:32,256:0,32\n',
        'F_OBSERVER1.config': full + '\n-gpgpu_ep_l2_ms_observer 1\n',
        'F_DATA_FREE.config': full + '\n-gpgpu_ep_l2_diag_l2_data_free 1\n-gpgpu_ep_l2_ms_observer 1\n',
    }
    for name, text in generated.items():
        (copied / name).write_text(text)
    profiles = inputs / 'PROFILES'
    profiles.mkdir()
    fixture = (core / 'tests/ep_l2/ft_wbuf.config').read_text()
    for rel in spec['control_files_SHA256']:
        if rel.startswith('profiles/'):
            dst = profiles / Path(rel).name
            dst.write_text(fixture + (handoff / rel).read_text())
    for name in ['S_COPY_FREE', 'S_L2_DATA_FREE']:
        text = (profiles / (name + '_observer0.config')).read_text()
        (profiles / (name + '_ROP7.config')).write_text(text + '\n-gpgpu_l2_rop_latency 7\n')
    replacements = {'{CORE}': str(core), '{BUILD}': str(build), '{OUT}': str(out), '{INPUTS}': str(inputs)}
    cases = []
    for row in spec['cases']:
        if (row['suite'] == 'diagnostics' and suite == 'main') or (row['suite'] == 'main' and suite == 'diagnostics'):
            continue
        assert re.fullmatch(r'ep_l2_[A-Za-z0-9_]+', row['target'])
        assert re.fullmatch(r'[A-Za-z0-9_-]+', row['id'])
        assert row['expected_exit'] in (0, 21) and 0 < row['timeout_seconds'] <= 120
        args = []
        for arg in row['args']:
            for token, value in replacements.items():
                arg = arg.replace(token, value)
            assert not re.search(r'\{(?:CORE|BUILD|OUT|INPUTS)\}', arg)
            # An existing named fixture input must be the exact pinned source
            # or own snapshot. Native target paths need not exist before build.
            if arg.startswith('/') and Path(arg).suffix in ('.config', '.g', '.csv', '.json'):
                p = Path(arg)
                assert p.is_file() and (p.is_relative_to(core) or p.is_relative_to(inputs))
            args.append(arg)
        cases.append(dict(row, native_command=[str(build / 'gpgpu-sim' / row['target']), *args]))
    assert len(cases) == sum(spec['counts'][g] for g in (['main', 'diagnostics'] if suite == 'all' else [suite]))
    config_hashes = {str(p): sha(p) for p in sorted(inputs.rglob('*')) if p.is_file()}
    # Check the actual copied certificate/command bytes and rewritten config
    # bindings now. This is input preparation, never runtime certification.
    for dirname in ['certified', 'fallback']:
        manifest = json.loads((copied / dirname / 'manifest.json').read_text())
        assert manifest['commandlist_sha256'] == sha(copied / 'kernelslist.g')
        assert manifest['artifacts']['certified_ranges.csv'] == sha(copied / dirname / 'certified_ranges.csv')
    for config in copied.glob('*.config'):
        opts = {}
        for line in config.read_text().splitlines():
            parts = line.split('#', 1)[0].split(None, 1)
            if len(parts) == 2:
                opts[parts[0]] = parts[1]
        for field in ['ranges', 'manifest']:
            assert sha(opts['-gpgpu_ep_l2_ro_' + field]) == opts['-gpgpu_ep_l2_ro_' + field + '_sha256']
    return cases, config_hashes
