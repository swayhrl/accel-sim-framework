"""Frozen-input runner. Requires a qualified release, central quota, and explicit closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time

from registry import Registry, canonical, run_key, write_json, process_identity, local_resources
from validate import validate_summary, require
from feature_schema import ro_bits
from acceptance import load_current_authority, current_manifest, reject_withdrawn, authorize_launch

GATES = {'old_all_off_equivalence', 'finite_wbuf', 'requester_exact_once',
         'sector_reference_data', 'stale_fill', 'resource_closure',
         'wb_lifecycle', 'bank_service', 'physical_bank_clock',
         'memcpy_payload_identity', 'mode_legality'}
FEATURES = {'finite_wbuf', 'unified_wb', 'tvd', 'ro', 'adaptive_policy',
            'wbuf_entries', 'payload_capacity_per_slice', 'bank_count', 'ops_per_bank_cycle'}
IDEALS = {'wb', 'meta', 'read_hit'}
RESULT_ROOT = Path('/workspace/results/ep_l2_ft20261016')
WORKSPACE_RESULT_ROOT = Path('/workspace/ep_l2_potential20261017_lane5_results')
RESULT_DISK_FLOOR = 40 * 1024**3  # Preserve the existing Share protection.


def result_disk_free_bytes():
    stat = os.statvfs(RESULT_ROOT)
    return stat.f_bavail * stat.f_frsize


def output_root(spec):
    root = Path(spec.get('result_root', str(RESULT_ROOT))).resolve(strict=True)
    require(root in {RESULT_ROOT.resolve(strict=True), WORKSPACE_RESULT_ROOT}, 'Unapproved result filesystem/root')
    if root == WORKSPACE_RESULT_ROOT:
        require(root.stat().st_dev == Path('/workspace').stat().st_dev and
                root.stat().st_dev != Path('/root/share').stat().st_dev,
                'New output must use the verified workspace physical filesystem')
    return root


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def asset_manifest(assets, ordered=False):
    names = set()
    result = []
    for item in assets:
        name = Path(item['name'])
        require(not name.is_absolute() and '..' not in name.parts and str(name) not in names,
                'unsafe or duplicate asset name')
        names.add(str(name))
        path = Path(item['path']).resolve(strict=True)
        require(path.is_file(), 'asset is not a regular file')
        result.append({'name': str(name), 'sha256': digest(path), 'bytes': path.stat().st_size})
    require(bool(result), 'empty input content manifest')
    return result if ordered else sorted(result, key=lambda item: item['name'])


def content_hash(manifest):
    return hashlib.sha256(canonical(manifest)).hexdigest()


def validate_trace_closure(spec):
    declared = {item['name']: Path(item['path']).resolve(strict=True) for item in spec['trace_files']}
    entry = declared[spec['entry_trace_name']]
    references = set()
    for raw in entry.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith(('MemcpyHtoD,', 'MemcpyDtoH,', 'MemcpyDtoD,')):
            continue
        require(bool(re.fullmatch(r'kernel-[^/\s]+\.traceg(?:\.gz)?', line)),
                'unsupported kernelslist command; explicit adapter required: ' + line)
        require(line in declared and declared[line] == (entry.parent / line).resolve(strict=True),
                'referenced kernel content absent or mapped to a different file')
        references.add(line)
    require(bool(references), 'trace list has no kernels')
    require(set(declared) == references | {spec['entry_trace_name']}, 'trace content closure mismatch')


def validate_config_closure(spec):
    assets = {item['name'] for item in spec['auxiliary_assets']}
    for config in spec['configs']:
        # GPGPU-Sim accepts a quoted DRAM timing value spanning several lines.
        # Lex the complete file so its unchanged native syntax remains valid.
        tokens = shlex.split(Path(config['path']).read_text(), comments=True)
        require('-config' not in tokens, 'nested config must be flattened into ordered frozen inputs')
        for token in tokens:
            if token.endswith(('.xml', '.icnt', '.config')):
                require(token in assets, 'unaccounted configuration file dependency: ' + token)



def validate_atomic_input_scope(spec, release, traces):
    if release.get('application_input_scope') != 'FULL_NATIVE_NONATOMIC_ONLY':
        return None
    proof = spec.get('atomic_input_scope')
    require(isinstance(proof, dict), 'complete non-atomic input proof required')
    require(digest(proof['path']) == proof['sha256'], 'atomic input proof changed')
    audit = json.loads(Path(proof['path']).read_text())
    require(audit['status'] == 'COMPLETE_NATIVE_OPCODE_AUDIT' and
            audit['input_scope'] == 'COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS',
            'input atomic scope not independently cleared')
    require(audit['tool_sha256'] == release['atomic_input_auditor_sha256'] and
            audit['producer_publication'] == release['producer_publication_commit'],
            'input scope tool/producer differs from qualified release')
    for name in ('core_source_commit', 'framework_source_commit', 'binary_sha256', 'trace_content_sha256'):
        require(audit['identity'][name] == spec['identity'][name], 'input scope identity mismatch: ' + name)
    require(audit['trace_content_manifest'] == traces and
            audit['global_atomic_records_with_repeats'] == 0 and
            audit['shared_atomic_records_with_repeats'] == 0,
            'complete trace proof missing or atomic opcode present')
    return {'sha256': proof['sha256'], 'scope': 'FULL_NATIVE_NONATOMIC_ONLY'}



def validate_native_legacy_semantic_proof(spec, release, traces, binding=None):
    if not release.get('input_adapter_revision'):
        return
    if binding is None:
        client = json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
        binding = client.get('native_legacy_semantic_proof')
    proof = spec.get('native_legacy_semantic_proof')
    require(isinstance(binding, dict) and isinstance(proof, dict), 'r17 native legacy semantic proof required')
    require(proof['sha256'] == binding['report_sha256'] == digest(proof['path']), 'r17 semantic proof bytes changed')
    report = json.loads(Path(proof['path']).read_text())
    require(report['status'] == 'PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF' and
            report['tool_sha256'] == binding['tool_sha256'] and
            report['tooling_source_commit'] == binding['source_commit'], 'r17 proof incomplete or different source')
    for name in ('core_source_commit', 'framework_source_commit', 'binary_sha256'):
        require(report['source_identity'][name] == spec['identity'][name], 'r17 semantic source/binary mismatch')
    matches = [r for r in report['workloads'] if r['workload'] == spec['identity']['workload']]
    require(len(matches) == 1 and matches[0]['status'] == 'FULL_ORIGINAL_BYTES_AND_NATIVE_ZERO_MASK_SEMANTICS_PROVEN', 'r17 workload scope unsupported')
    bodies = [{k: f[k] for k in ('name', 'sha256', 'bytes')} for f in matches[0]['files']]
    require(sorted(bodies, key=lambda r:r['name']) ==
            [r for r in traces if r['name'] != spec['entry_trace_name']], 'r17 complete body-byte closure differs')


def inspect(spec):
    identity = spec['identity']
    key = run_key(identity)
    authority = load_current_authority()
    reject_withdrawn(identity, current_manifest(authority))
    require(set(identity['ideal_vector']) == IDEALS, 'ideal vector must include every V1 ideal mode')
    feature = identity['feature_vector']
    detach, bypass = ro_bits(feature)
    for flag in ('finite_wbuf', 'unified_wb', 'tvd', 'adaptive_policy'):
        require(type(feature[flag]) is bool, 'feature flag must be boolean')
    for field in ('wbuf_entries', 'payload_capacity_per_slice', 'bank_count', 'ops_per_bank_cycle'):
        require(type(feature[field]) is int, 'resource capacity/service field must be an integer')
    require(all(type(v) is bool for v in identity['ideal_vector'].values()), 'ideal flags must be boolean')
    require(feature['finite_wbuf'] is True and feature['wbuf_entries'] in (8, 16), 'finite WBUF capacity required')
    require(feature['payload_capacity_per_slice'] == 1152 + feature['wbuf_entries'], 'unmatched data budget')
    require(feature['bank_count'] == 4 and feature['ops_per_bank_cycle'] == 1, 'bank service mismatch')
    require(not feature['adaptive_policy'], 'adaptive policy is not a qualified V1 mode')
    require(feature['unified_wb'] or not (feature['tvd'] or detach or bypass), 'TVD/RO require integrated unified substrate')
    require(not any(identity['ideal_vector'].values()), 'ideal runs use Lane 4 diagnostic runner and separate tables')
    require(identity['epoch_range'].get('scope') == 'full_application', 'diagnostic fragments cannot enter implementation results')
    require(digest(spec['binary']) == identity['binary_sha256'], 'binary content mismatch')
    configs = asset_manifest(spec['configs'], ordered=True)
    assets = asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
    traces = asset_manifest(spec['trace_files'])
    require(content_hash({'ordered_configs': configs, 'auxiliary_assets': assets,
                          'environment': spec.get('environment', {})}) == identity['runtime_config_sha256'],
            'runtime config/auxiliary content mismatch')
    require(content_hash(traces) == identity['trace_content_sha256'], 'trace content mismatch')
    validate_config_closure(spec)
    require(spec['entry_trace_name'] in {r['name'] for r in traces}, 'entry trace is not content-pinned')
    validate_trace_closure(spec)
    # The release envelope is normalized by Lane 5 from published Lane 1 receipts.
    release = json.loads(Path(spec['qualified_release']).read_text())
    require(release['status'] == 'INDEPENDENTLY_QUALIFIED', 'release is not independently qualified')
    require(release['qualified_by'] == 'lane5' and release['evidence_kind'] == 'PRODUCTION_DRIVEN',
            'harness-only or self-declared producer evidence cannot qualify production')
    for name in ('core_source_commit', 'framework_source_commit', 'binary_sha256'):
        require(release[name] == identity[name], 'release/source/binary mismatch: ' + name)
    require(identity['feature_vector'] in release['qualified_feature_vectors'], 'feature combination not independently qualified')
    require(release['gates'].keys() >= GATES, 'missing independent qualification gate')
    evidence = []
    for name in GATES:
        gate = release['gates'][name]
        require(gate['status'] == 'PASS' and gate['production_driven'] is True,
                'unpassed/nonproduction qualification: ' + name)
        require(digest(gate['evidence_path']) == gate['evidence_sha256'], 'qualification artifact changed')
        evidence.append({'gate': name, 'sha256': gate['evidence_sha256']})
    from headroom_config import validate as validate_headroom_config
    condition = validate_headroom_config(spec, release, configs, assets)
    atomic_scope = validate_atomic_input_scope(spec, release, traces)
    validate_native_legacy_semantic_proof(spec, release, traces)
    parser = spec['parser']
    require(digest(parser['path']) == parser['sha256'], 'parser source content mismatch')
    require(type(spec['timeout_seconds']) is int and spec['timeout_seconds'] > 0, 'explicit positive timeout required')
    require(type(spec.get('environment', {})) is dict and
            all(isinstance(k, str) and isinstance(v, str) for k, v in spec.get('environment', {}).items()),
            'explicit string environment required')
    launch_authorization = authorize_launch(identity, digest(spec['qualified_release']), authority)
    audit = {'run_key': key, 'configs': configs, 'auxiliary_assets': assets,
            'traces': traces, 'qualification_evidence': evidence,
            'qualified_release_sha256': digest(spec['qualified_release']),
            'scientific_launch_authorization': launch_authorization, 'atomic_input_scope': atomic_scope}
    if condition is not None:
        audit['downstream_config_qualification'] = condition
    return audit


def tree_bytes(root):
    return sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink()) if root.exists() else 0


def process_tree_rss(pid):
    total, queue = 0, [pid]
    seen = set()
    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)
        try:
            total += int(Path(f'/proc/{current}/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
            queue.extend(map(int, Path(f'/proc/{current}/task/{current}/children').read_text().split()))
        except (FileNotFoundError, ProcessLookupError):
            pass
    return total


def terminate_owned(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def run(spec, registry):
    require(result_disk_free_bytes() >= RESULT_DISK_FLOOR,
            'result filesystem below existing Share40GiB protection; no claim')
    audit = inspect(spec)
    key = audit['run_key']
    root = output_root(spec)
    directory = root / key
    require(result_disk_free_bytes() >= RESULT_DISK_FLOOR,
            'result filesystem changed during input audit; no claim')
    experiment = None
    if spec.get('experiment_id') == 'EPL2_DOWNSTREAM_HEADROOM_R19':
        deadline = 1792220956 + 36000  # This explicitly authorized r19 CONTINUE T0 +10h.
        require(time.time() + spec['timeout_seconds'] < deadline, 'Insufficient bounded window for original timeout')
        experiment = {'experiment_id':spec['experiment_id'],'regime':spec['regime'],'deadline_unix':deadline}
    elif spec.get('experiment_id') == 'EPL2_PARALLEL_POTENTIAL_20261017_V1':
        from registry import PARALLEL
        campaign = registry.snapshot().get('campaigns', {}).get(PARALLEL)
        require(campaign is not None, 'New campaign must be centrally registered')
        experiment = {k:spec[k] for k in ('experiment_id','regime','cell_id','profile')}
        experiment['deadline_unix'] = campaign['deadline_unix']
    elif spec.get('experiment_id'):
        raise ValueError('Unknown experiment; no unaccounted launch')
    fresh, allocation = registry.claim(spec['identity'], spec['owner'], directory, **({'experiment':experiment} if experiment else {}))
    if not fresh:
        return {'status': 'DUPLICATE_NOT_LAUNCHED', 'existing': allocation}
    lease = allocation['lease_id']
    process = None
    created_directory = False
    status, detail = 'INCOMPLETE', 'runner interrupted before terminal validation'
    result = {'run_key': key, 'identity': spec['identity'], 'allocation': allocation,
              'audit': audit, 'status': status,
              'output_filesystem': {'realpath': str(root), 'st_dev':root.stat().st_dev}}
    started = time.monotonic()
    try:
        directory.mkdir(parents=True, exist_ok=False)
        created_directory = True
        write_json(directory / 'input_spec.json', spec)
        write_json(directory / 'input_audit.json', audit)
        binary = directory / 'accel-sim.out'
        shutil.copy2(spec['binary'], binary)
        require(digest(binary) == spec['identity']['binary_sha256'], 'binary changed during snapshot')
        configs = []
        for index, item in enumerate(spec['configs']):
            target = directory / f'config-{index}.config'
            shutil.copyfile(item['path'], target)
            require(digest(target) == audit['configs'][index]['sha256'], 'config changed during snapshot')
            configs.append(target)
        for item in spec['auxiliary_assets']:
            target = directory / item['name']
            require(not target.exists() and target.resolve().is_relative_to(directory), 'asset collides with frozen inputs')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item['path'], target)
            expected = next(r['sha256'] for r in audit['auxiliary_assets'] if r['name'] == item['name'])
            require(digest(target) == expected, 'auxiliary asset changed during snapshot')
        trace = next(item['path'] for item in spec['trace_files'] if item['name'] == spec['entry_trace_name'])
        command = [str(binary)]
        for config in configs:
            command.extend(['-config', str(config)])
        command.extend(['-trace', str(Path(trace).resolve())])
        environment = os.environ.copy()
        environment.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        environment.update(spec.get('environment', {}))
        require(all(environment[k] == '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')),
                'single CPU reservation cannot launch threaded child')
        policy = registry.snapshot()['hosts'][allocation['host']]
        require(sum(tree_bytes(p) for p in {RESULT_ROOT.resolve(), root}) < policy['max_result_bytes'], 'shared EP-L2 output ceiling')
        with (directory / 'raw.log').open('xb') as log:
            process = subprocess.Popen(command, cwd=directory, stdout=log, stderr=subprocess.STDOUT,
                                       env=environment, start_new_session=True)
            registry.update(key, lease, 'RUNNING', process=process_identity(process.pid))
            peak_rss = 0
            while process.poll() is None:
                peak_rss = max(peak_rss, process_tree_rss(process.pid))
                live = local_resources()
                if (time.monotonic() - started > spec['timeout_seconds'] or
                    experiment is not None and experiment['experiment_id'] == 'EPL2_DOWNSTREAM_HEADROOM_R19' and time.time() >= experiment['deadline_unix']):
                    status, detail = 'TIMEOUT', 'explicit runtime deadline'
                    terminate_owned(process)
                    break
                if (peak_rss > allocation['memory_bytes'] or
                    (directory / 'raw.log').stat().st_size > policy['default_run_output_limit_bytes'] or
                    sum(tree_bytes(p) for p in {RESULT_ROOT.resolve(), root}) > policy['max_result_bytes'] or
                    result_disk_free_bytes() < RESULT_DISK_FLOOR or
                    (root == WORKSPACE_RESULT_ROOT and (os.statvfs(root).f_bavail * os.statvfs(root).f_frsize < policy['min_disk_free_bytes'])) or
                    live['disk_free_bytes'] < policy['min_disk_free_bytes'] or
                    live['available_memory_bytes'] < policy['min_available_memory_bytes']):
                    status, detail = 'RESOURCE_LIMIT', 'own run exceeded shared resource safety policy'
                    terminate_owned(process)
                    break
                time.sleep(1)
        result.update(exit_code=process.returncode, peak_process_tree_rss_bytes=peak_rss,
                      wall_seconds=time.monotonic() - started)
        if status not in {'TIMEOUT', 'RESOURCE_LIMIT'}:
            require(process.returncode == 0, 'nonzero simulator process exit')
            normal = False
            cycles = instructions = None
            with (directory / 'raw.log').open(errors='replace') as stream:
                for line in stream:
                    normal |= 'GPGPU-Sim: *** exit detected ***' in line
                    match = re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*', line)
                    if match:
                        if match[1] == 'cycle': cycles = int(match[2])
                        else: instructions = int(match[2])
            require(normal and cycles is not None and instructions is not None, 'missing native terminal execution evidence')
            if experiment is not None:
                from headroom_config import validate_runtime_dump
                result['downstream_effective_config'] = validate_runtime_dump(directory / 'raw.log', spec)
            # Parser adapter must produce terminal_summary.json with explicit, source-mapped fields.
            parser = spec['parser']
            with (directory / 'parser.log').open('xb') as output:
                completed = subprocess.run([sys.executable, parser['path'], '--raw', str(directory / 'raw.log'),
                    '--out', str(directory / 'terminal_summary.json')], cwd=directory,
                    stdout=output, stderr=subprocess.STDOUT, timeout=120)
            require(completed.returncode == 0, 'production terminal parser failed')
            summary = json.loads((directory / 'terminal_summary.json').read_text())
            require(summary['cycles'] == cycles and summary['instructions'] == instructions, 'native/parser metric mismatch')
            result['validation'] = validate_summary(summary, spec['identity'])
            result['summary'] = summary
            status, detail = 'COMPLETE_VALID', 'qualified binary, exact inputs, legal hardware terminal and closure'
        # Rehash all sources, including complete trace contents, after execution.
        require(inspect(spec) == audit, 'source/input evidence changed during execution')
    except (Exception, KeyboardInterrupt) as error:
        if process is not None:
            terminate_owned(process)
        status, detail = 'FAILED', f'{type(error).__name__}: {error}'
    finally:
        result.update(status=status, detail=detail, wall_seconds=time.monotonic() - started)
        if created_directory:
            if (directory / 'raw.log').exists():
                result['raw_log_sha256'] = digest(directory / 'raw.log')
            write_json(directory / 'run_status.json', result)
        registry.update(key, lease, status, exit_code=process.returncode if process else None,
                        detail=detail, raw_log_sha256=result.get('raw_log_sha256'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--registry-root', type=Path, default=Path('/workspace/ep_l2_ft20261016_shared'))
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    def interrupted(signum, frame):
        raise KeyboardInterrupt('runner received signal ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    result = inspect(spec) if args.check_only else run(spec, Registry(args.registry_root))
    print(json.dumps(result, indent=2))
    if not args.check_only and result['status'] not in {'COMPLETE_VALID', 'DUPLICATE_NOT_LAUNCHED'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
