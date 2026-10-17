#!/usr/bin/env python3
"""Pinned Git objects + small CPU-only synthetic/header probes. No simulator.
Writes only V2 pack; does not import or execute another Lane's scripts.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACK = Path(__file__).resolve().parents[1]
FW = PACK.parents[3]
CORE_REPO = Path('/workspace/repos/gpgpu-sim_distribution')
FROZEN = '6fba0136f8465b59fe5858a950fa39efb265f654'
BUILD = '18a68dcccd795f1b6cda75504e9450d00c9cee02'
V = '26abd496417d9392245052e54fbd9ba27c6ffd96'
Y = 'b673d046b38f61159b5db67a477d58d1afa4662f'
XFW = '49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4'
XFW_HISTORICAL = '0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc'
XCORE = 'c0a5e2c31e407c57e3a4af3ce529c921e8059a05'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def blob(repo, commit, path):
    return git(repo, 'show', f'{commit}:{path}')

inputs = []
for name in ['gpu-sim.cc', 'gpu-sim.h', 'shader.cc', 'shader.h',
             'gpu-cache.cc', 'gpu-cache.h', 'dtc-l1-common.h']:
    inputs.append((CORE_REPO, FROZEN, 'src/gpgpu-sim/' + name, 'FROZEN_CORE'))
inputs.append((CORE_REPO, FROZEN, 'src/abstract_hardware_model.cc', 'FROZEN_COALESCER'))
for name in ['trace-driven/trace_driven.cc', 'trace-driven/trace_driven.h',
             'trace-parser/trace_parser.cc', 'trace-parser/trace_parser.h',
             'ISA_Def/ampere_opcode.h']:
    inputs.append((FW, BUILD, 'gpu-simulator/' + name, 'FRAMEWORK_BUILD'))
for name in ['dtc-l1-common.h', 'dtc-l1-invalidation.h', 'shader.cc', 'shader.h', 'gpu-sim.cc']:
    inputs.append((CORE_REPO, XCORE, 'src/gpgpu-sim/' + name, 'PUBLISHED_X_CORE'))
for commit, directory, names, role in [
    (V, 'DTC_LANE_V_SEMANTIC_V1', ['LATEST_REPORT.md', 'SOURCE_EVENT_MAP.md', 'K1_SEMANTIC_CONTRACT.md'], 'V1_UNCHANGED'),
    (Y, 'DTC_LANE_Y_INVALIDATION_V1', ['LATEST_REPORT.md', 'VALIDATION_GATE.json', 'OPEN_VALUE_SEMANTICS.md', 'CONTRACT_BINDING.json'], 'Y_V1'),
    (XFW, 'DTC_LANE_X_OPTIN_INVALIDATION_V1', ['LATEST_REPORT.md', 'GIT_DELIVERY.json', 'SOURCE_AND_BINARY_IDENTITY.json'], 'X_FRAMEWORK_SNAPSHOT')]:
    for name in names:
        inputs.append((FW, commit, f'docs/dtc_l1/review_packs/{directory}/{name}', role))
for name in ['LATEST_REPORT.md', 'GIT_DELIVERY.json']:
    inputs.append((FW, XFW_HISTORICAL,
                   'docs/dtc_l1/review_packs/DTC_LANE_X_OPTIN_INVALIDATION_V1/' + name,
                   'X_HISTORICAL_READBACK'))

# Distinguish X's new trace-binary build commit from the frozen build commit.
# These selected routing files are byte-identical across the three Framework
# identities. This is a source claim, not a binary/runtime equivalence claim.
framework_route_match = {}
for _, _, path, role in inputs:
    if role == 'FRAMEWORK_BUILD':
        assert blob(FW, BUILD, path) == blob(FW, XFW_HISTORICAL, path) == blob(FW, XFW, path)
        framework_route_match[path] = 'EXACT_BLOB_BYTES'

rows = []
for repo, commit, path, role in inputs:
    data = blob(repo, commit, path)
    rows.append([role, commit, path,
                 git(repo, 'rev-parse', f'{commit}:{path}').decode().strip(),
                 hashlib.sha256(data).hexdigest(), len(data)])
with (PACK / 'SOURCE_SHA256.tsv').open('w') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(['role', 'commit', 'path', 'git_blob', 'sha256', 'bytes'])
    writer.writerows(rows)

cases = json.loads((PACK / 'inputs/value_cases.json').read_text())['cases']
outcomes = []
for case in cases:
    command = [sys.executable, '-E', str(PACK / 'scripts/value_oracle.py'),
               '--case', case['id'], '--expect-status', case['expected_status']]
    run = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert run.returncode == 0, (case['id'], run.stderr, run.stdout)
    observed = json.loads(run.stdout)
    wrong = 'REJECT_SYNTHETIC_CONTRACT' if case['expected_status'] == 'PASS_SYNTHETIC_CONDITIONAL' else 'PASS_SYNTHETIC_CONDITIONAL'
    negative = subprocess.run(command[:-1] + [wrong], capture_output=True, text=True, timeout=15)
    assert negative.returncode == 1, case['id']
    outcomes.append({'id': case['id'], 'expected_status': case['expected_status'],
                     'observed': observed, 'harness_exit': run.returncode,
                     'wrong_expectation_control': {'requested_status': wrong, 'exit': negative.returncode}})

header_results = []
with tempfile.TemporaryDirectory(prefix='dtc-v2-value-header-') as scratch:
    scratch = Path(scratch)
    for label, commit, has_k1 in [('frozen', FROZEN, False), ('published_X', XCORE, True)]:
        target = scratch / label
        target.mkdir()
        (target / 'dtc-l1-common.h').write_bytes(blob(CORE_REPO, commit, 'src/gpgpu-sim/dtc-l1-common.h'))
        binary = target / 'header_value_bridge'
        command = ['g++', '-std=c++14', '-O0', '-g0', '-I', str(target)]
        if has_k1:
            command += ['-DHAS_PUBLISHED_K1']
        command += [str(PACK / 'scripts/header_value_bridge.cc'), '-o', str(binary)]
        build = subprocess.run(command, capture_output=True, text=True, timeout=60)
        assert build.returncode == 0, build.stderr
        run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
        assert run.returncode == 0, run.stderr
        header_results.append({'source': label, 'commit': commit, 'exit': run.returncode,
                               'compile_flags': ['-std=c++14', '-O0', '-g0', 'assertions enabled'],
                               'observations': [json.loads(x) for x in run.stdout.splitlines()],
                               'scope': 'metadata + external synthetic byte overlays only'})

receipt = {'status': 'PASS_CPU_SCOPE_WITH_EXPECTED_VALUE_REJECTIONS',
           'input_commits': {'frozen_core': FROZEN, 'framework_build': BUILD,
                            'V1': V, 'Y_V1': Y, 'X_framework_snapshot': XFW, 'X_core_snapshot': XCORE,
                            'X_historical_stop_and_trace_build': XFW_HISTORICAL},
           'selected_framework_route_files_match': framework_route_match,
           'compiler': subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
           'synthetic_case_count': len(outcomes),
           'wrong_expectation_controls': len(outcomes),
           'semantic_status_counts': {s: sum(x['observed']['status'] == s for x in outcomes)
                                      for s in sorted(set(x['observed']['status'] for x in outcomes))},
           'source_hash_rows': len(rows), 'synthetic_results': outcomes, 'header_results': header_results,
           'production_value_tests': 0, 'full_simulator_runs': 0, 'performance_runs': 0,
           'actual_trace_body_reads': 0, 'production_source_modifications': 0,
           'k2_implemented': False, 'k1_independent_acceptance': 'NOT_GRANTED_BY_V2',
           'scientific_gate': 'VALUE_CORRECTNESS_UNPROVEN; K2_FUTURE_ONLY_REQUIRES_SEPARATE_AUTHORIZATION'}
(PACK / 'CPU_VALUE_WITNESSES.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'synthetic_case_count',
      'wrong_expectation_controls', 'semantic_status_counts', 'source_hash_rows']}))
