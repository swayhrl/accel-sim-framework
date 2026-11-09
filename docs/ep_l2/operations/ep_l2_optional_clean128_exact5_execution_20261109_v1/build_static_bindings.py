"""Build current Source5 Host/Native dependency documents; no registry writes."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
SOURCE = ROOT / 'documents/SOURCE_CPU_QUALIFICATION.json'
CASES = sorted(ROOT.glob('cases/*/control/DRAFT_SPEC.json'))
HOST_PATHS = ('/bin/sh', '/usr/bin/cat', '/lib64/ld-linux-x86-64.so.2',
              '/lib/x86_64-linux-gnu/libc.so.6',
              str(NATIVE / 'common-lib/libc.so.6'))


def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def put(path, obj):
    data = (json.dumps(obj, sort_keys=True, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(data)


def main():
    need(len(CASES) == 5, 'five draft Specs required')
    specs = [json.loads(path.read_bytes()) for path in CASES]
    source = json.loads(SOURCE.read_bytes())['source_identity']
    need(all(spec['source_identity'] == source for spec in specs), 'Source5 mismatch')
    native_prefix = str(NATIVE) + '/'
    native_paths = {p for p in specs[0]['pinned_files'] if p.startswith(native_prefix)}
    need(len(native_paths) == 22, 'Native22 path count changed')
    pins = {path: sha(path) for path in sorted(native_paths)}
    for spec in specs:
        need(all(spec['pinned_files'].get(path) == digest for path, digest in pins.items()),
             'Native22 differs from draft pin')
    closure = {'schema': 'EP_L2_EXACT5_SOURCE5_NATIVE22_CLOSURE_V1',
               'Source5': source, 'pinned_files': pins,
               'source_qualification_ref': {'path': str(SOURCE), 'sha256': sha(SOURCE)},
               'application_acceptance_granted': False}
    host = []
    for path in HOST_PATHS:
        item = pathlib.Path(path)
        resolved = item.resolve(strict=True)
        host.append({'path': path, 'resolved_path': str(resolved),
                     'sha256': sha(item), 'bytes': item.stat().st_size,
                     'current_identity_only': True})
    dependencies = {'schema': 'EP_L2_EXACT5_CURRENT_HOST_TRACE_CHILD_DEPENDENCIES_V1',
                    'Source5': source, 'dependencies': host,
                    'historical_accepted_identity': 'UNKNOWN_NO_HISTORICAL_PIN',
                    'application_acceptance_granted': False}
    contract = json.loads((ROOT / 'documents/RUNTIME_FULL43_CONTRACT.source.json').read_bytes())
    need(len(contract['required_keys']) == len(set(contract['required_keys'])) == 43,
         'strict Host43 contract changed')
    need(all(set(contract['required_keys']) <= set(spec) for spec in specs),
         'draft Spec lacks Host43 fields')
    need(all(len(spec['expected_effective_options']) == 283 for spec in specs),
         '283 options changed')
    output = ROOT / 'documents'
    put(output / 'SOURCE5_NATIVE22_CLOSURE.json', closure)
    put(output / 'SOURCE5_HOST_TRACE_CHILD_DEPENDENCIES.json', dependencies)
    put(output / 'RUNTIME_FULL43_CONTRACT.json', contract)
    print(json.dumps({'status': 'SOURCE5_STATIC_BINDING_DOCUMENTS_PASS_NO_LAUNCH',
                      'native_pins': len(pins), 'host_child_pins': len(host),
                      'host_contract_fields': 43, 'draft_specs_checked': 5,
                      'models_started': False}, sort_keys=True))


if __name__ == '__main__':
    main()
