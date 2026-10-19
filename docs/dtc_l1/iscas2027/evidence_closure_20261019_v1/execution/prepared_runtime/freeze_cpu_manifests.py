"""Registered static ELF closure only; never execute the target ELF or loader."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')

def main():
    sys.path.insert(0, str(HERE / 'vendor'))
    from freeze_static import freeze_executable
    output = RAW / 'cpu-qualification/real-lifecycle-v1-prereg'
    output.mkdir(parents=True, exist_ok=False)
    build = RAW / 'build'
    for name, value in [('helper-data', b'AG4_HELPER_OK\n'),
                        ('unknown-data', b'x' * 4096)]:
        with (build / name).open('xb') as stream:
            stream.write(value)
    manifests, objects = {}, {}
    for target in [build / 'closure-cpu-authority',
                   Path('/usr/bin/dash'), Path('/usr/bin/cat')]:
        manifest, dependencies = freeze_executable(target, build)
        manifests[manifest['target']] = manifest
        objects[manifest['target']] = dependencies
    for name, value in [('MANIFESTS.json', manifests), ('STATIC_ELF_OBJECTS.json', objects)]:
        with (output / name).open('x') as stream:
            stream.write(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'status': 'STATIC_CPU_RUNTIME_FROZEN_NOT_EXECUTED',
                      'output': str(output), 'target_count': len(manifests),
                      'manifests_sha256': hashlib.sha256((output / 'MANIFESTS.json').read_bytes()).hexdigest(),
                      'target_executions': 0, 'simulation_starts': 0}))

if __name__ == '__main__':
    main()
