#!/usr/bin/env python3
"""Build the reviewed finite-service DTC candidate without running a model."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/root/data/dtc_finite_service_completion_v1_20261109')
CORE = ROOT / 'core'
BUILD = ROOT / 'build' / 'frozen_candidate_9a0de9b9'
CORE_BUILD = BUILD / 'core'
FRAMEWORK_BUILD = BUILD / 'framework'
LOGS = BUILD / 'logs'
OLD = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
FRAMEWORK = OLD / 'source' / 'framework-build'
SOURCE_CORE = OLD / 'source' / 'integration-core'
OLD_BUILD_CORE = OLD / 'build' / 'core'
OLD_BUILD_FRAMEWORK = OLD / 'build' / 'framework'
EXPECTED_CORE = '9a0de9b9f97144f481b3e3637e329ebab01acb74'
EXPECTED_FRAMEWORK = '02775fd795cde5aae1480d81cee6eb481d0a08f4'

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def check_source():
    assert git('-C', str(CORE), 'rev-parse', 'HEAD') == EXPECTED_CORE
    assert not git('-C', str(CORE), 'status', '--porcelain')
    safe = ['-c', f'safe.directory={FRAMEWORK}', '-C', str(FRAMEWORK)]
    assert git(*safe, 'rev-parse', 'HEAD') == EXPECTED_FRAMEWORK
    assert not git(*safe, 'status', '--porcelain')

def step(label, argv):
    log = LOGS / (label + '.log')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(log, 'wb') as f:
        proc = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT)
    result = {'label': label, 'argv': argv, 'started_utc': started,
              'returncode': proc.returncode, 'log': str(log), 'log_SHA256': sha(log)}
    receipt['steps'].append(result)
    save()
    if proc.returncode:
        print(f'{label} failed: {log}', file=sys.stderr)
        sys.exit(proc.returncode)
    print(f'{label}: PASS', flush=True)

def save():
    (BUILD / 'BUILD_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')

def artifact(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'SHA256': sha(path)}

check_source()
for directory in (CORE_BUILD, FRAMEWORK_BUILD, LOGS):
    directory.mkdir(parents=True, exist_ok=True)
receipt = {'schema': 'DTC_FINITE_SERVICE_COMPLETION_CPU_BUILD_V1',
           'core_commit': EXPECTED_CORE, 'framework_commit': EXPECTED_FRAMEWORK,
           'core_source': str(CORE), 'framework_source': str(FRAMEWORK),
           'build_root': str(BUILD), 'steps': [], 'simulator_calls': 0, 'GPU_calls': 0}
version_header_source = OLD_BUILD_FRAMEWORK / 'accelsim_version.h'
version_header = FRAMEWORK_BUILD / 'accelsim_version.h'
shutil.copyfile(version_header_source, version_header)
receipt['framework_generated_version_header'] = {
    'source': str(version_header_source), 'artifact': artifact(version_header)}
save()
step('compiler_version', ['/usr/bin/g++', '--version'])
step('cmake_version', ['cmake', '--version'])
step('core_configure', ['cmake', '-S', str(CORE), '-B', str(CORE_BUILD),
                        '-DCMAKE_BUILD_TYPE=Release',
                        '-DCUDAToolkit_ROOT=/root/data/dtc_main_20261023_v1/ae_fair_v1/toolchain',
                        '-DGPGPUSIM_BUILD_DTC_L1_TESTS=ON',
                        '-DGPGPUSIM_BUILD_AEFAIR_TESTS=ON',
                        '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'])
step('core_build', ['cmake', '--build', str(CORE_BUILD), '-j', '8'])
old_receipt = json.loads((OLD / 'build' / 'FRAMEWORK_BUILD_RECEIPT.json').read_text())
for index, old_step in enumerate(old_receipt['compile_steps']):
    argv = old_step['argv']
    replacements = ((str(SOURCE_CORE), str(CORE)),
                    (str(OLD_BUILD_CORE), str(CORE_BUILD)),
                    (str(OLD_BUILD_FRAMEWORK), str(FRAMEWORK_BUILD)))
    for old_path, new_path in replacements:
        argv = [argument.replace(old_path, new_path) for argument in argv]
    if old_step.get('label') == 'link':
        step('framework_link', argv)
    else:
        step(f'framework_compile_{index}', argv)
binary = FRAMEWORK_BUILD / 'accel-sim.out'
lib = CORE_BUILD / 'libcudart.so'
receipt['binary'] = artifact(binary)
receipt['libcudart'] = artifact(lib)
step('binary_linkage', ['ldd', str(binary)])
step('binary_linkage_with_local_lib',
     ['env', f'LD_LIBRARY_PATH={CORE_BUILD}', 'ldd', str(binary)])
step('libcudart_linkage', ['ldd', str(lib)])
save()
print(json.dumps({'binary': receipt['binary'], 'libcudart': receipt['libcudart']}, indent=2))
