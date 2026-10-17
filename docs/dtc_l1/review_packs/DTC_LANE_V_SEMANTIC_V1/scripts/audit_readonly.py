#!/usr/bin/env python3
"""Read immutable git blobs; compile small header tests in a temporary directory.
Writes only this Lane V pack. Never invokes a simulator, launcher or Lane owner.
"""
import csv
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import tempfile

PACK = Path(__file__).resolve().parents[1]
FW = PACK.parents[3]
CORE_REPO = Path('/workspace/repos/gpgpu-sim_distribution')
CORE_WT = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
CORE = '6fba0136f8465b59fe5858a950fa39efb265f654'
BUILD = '18a68dcccd795f1b6cda75504e9450d00c9cee02'
A = 'f5c37d6edcce832a72cb0830021bffa78df6cc13'
T = 'f520a445436b57c0a0f2494fb858a1636f04d2bc'
U = '16e56912cfd02f2311a1603a29415dee829fd495'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def blob(repo, commit, path):
    return git(repo, 'show', f'{commit}:{path}')

def sha(data):
    return hashlib.sha256(data).hexdigest()

tests = ['dtc_l1_m1_common_test.cc', 'dtc_l1_finite_service_test.cc',
         'dtc_l1_completion_accounting_test.cc', 'dtc_l1_bad_generation_test.cc']
core_paths = [f'src/gpgpu-sim/{n}' for n in [
    'gpu-sim.cc', 'gpu-sim.h', 'shader.cc', 'shader.h', 'gpu-cache.cc',
    'gpu-cache.h', 'dtc-l1-common.h']]
core_paths += ['docs/dtc_l1/DTC_L1_SPEC.md', 'docs/dtc_l1/README.md', 'AGENTS.md']
core_paths += [f'tests/{n}' for n in tests]
fw_paths = ['gpu-simulator/trace-driven/trace_driven.cc',
            'gpu-simulator/trace-driven/trace_driven.h',
            'gpu-simulator/trace-parser/trace_parser.cc',
            'gpu-simulator/CMakeLists.txt', 'AGENTS.md']
inputs = [(CORE_REPO, CORE, p, 'frozen_core') for p in core_paths]
inputs += [(FW, BUILD, p, 'frozen_framework_build') for p in fw_paths]
ap = 'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/'
tp = 'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/'
up = 'docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1/'
inputs += [(FW, A, ap + p, 'published_A') for p in [
    'final_closure_v1/README.md', 'final_closure_v1/FINAL_INTEGRITY_AUDIT_V1.json',
    'final_closure_v1/OPEN_SCIENTIFIC_REVIEW_ITEMS.md',
    'final_closure_v1/SOURCE_POLICY_ORDERING_AND_PRESERVATION_V2.json']]
inputs += [(FW, T, tp + p, 'published_T') for p in [
    'LATEST_REPORT.md', 'CONTENT_PUBLICATION_FETCH_BACK.json', 'SCIENTIFIC_SCOPE.md']]
inputs += [(FW, U, up + p, 'published_U') for p in [
    'LATEST_REPORT.md', 'BACKGROUND_ADMISSION_RECEIPT.json', 'FINAL_CONTRACT_AUDIT.json',
    'CONTENT_PUBLICATION_FETCH_BACK.json', 'PUBLICATION_CONTRACT.md',
    'PUBLICATION_METADATA_CORRECTION.json', 'SOURCE_IDENTITY.json',
    'config/FAST64_OO.config', 'config/FINITE_PRIMARY_COMMON.config', 'config/T1-C.config']]
rows = []
for repo, commit, path, role in inputs:
    data = blob(repo, commit, path)
    live = CORE_WT / path if role == 'frozen_core' else FW / path
    match = 'NOT_READ_OTHER_LANE_WORKTREE'
    if role in ('frozen_core', 'frozen_framework_build'):
        assert live.read_bytes() == data, (role, path)
        match = 'EXACT'
    rows.append([role, commit, path, git(repo, 'rev-parse', f'{commit}:{path}').decode().strip(),
                 sha(data), len(data), match])
assert git(CORE_WT, 'rev-parse', 'HEAD').decode().strip() == CORE
assert not git(CORE_WT, 'status', '--porcelain'), 'Core must remain clean'

shader = blob(CORE_REPO, CORE, 'src/gpgpu-sim/shader.cc').decode()
common = blob(CORE_REPO, CORE, 'src/gpgpu-sim/dtc-l1-common.h').decode()
cache = blob(CORE_REPO, CORE, 'src/gpgpu-sim/gpu-cache.cc').decode()
def body(text, signature):
    start = text.index('{', text.index(signature))
    depth = 1
    i = start + 1
    while depth:
        depth += (text[i] == '{') - (text[i] == '}')
        i += 1
    return text[start + 1:i - 1]

static = {}
for name in ('invalidate', 'flush'):
    b = body(shader, f'void ldst_unit::{name}()')
    assert f'm_L1D->{name}();' in b and 'm_dtc' not in b
    static[f'ldst_{name}_ordinary_only'] = True
assert 'void invalidate(' not in common and 'void flush(' not in common
static['no_dtc_frontend_invalidate_or_flush_api'] = True
b = body(shader, 'bool ldst_unit::dtc_l1_m4_observe_admit(')
assert 'add_external_dependency' in b and '->access(' not in b
static['sidecar_has_external_dependency_without_tag_access'] = True
b = body(shader, 'bool ldst_unit::dtc_l1_oo_select_ready(')
assert 'older_same_warp_fence' in b and 'warp_id()' in b and 'PROXY_FENCE' in b
static['oo_select_filters_younger_same_warp_behind_proxy'] = True
for name in ('io', 'oo'):
    b = body(shader, f'bool ldst_unit::dtc_l1_{name}_consume_response(')
    assert 'record.physical' in b and 'find_tag' not in b
    static[f'{name}_response_uses_saved_physical'] = True
assert 'conventional_miss_lifecycle_active()' in body(cache, 'void baseline_cache::retire_pending_invalidate()')
static['ordinary_invalidate_deferred_for_ordinary_misses'] = True

def no_core_dump():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

results = []
compiler = subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]
with tempfile.TemporaryDirectory(prefix='dtc-lane-v-cpu-') as scratch:
    scratch = Path(scratch)
    (scratch / 'dtc-l1-common.h').write_bytes(blob(CORE_REPO, CORE, 'src/gpgpu-sim/dtc-l1-common.h'))
    sources = [(n, blob(CORE_REPO, CORE, f'tests/{n}')) for n in tests]
    sources += [('visibility_witness.cc', (PACK / 'scripts/visibility_witness.cc').read_bytes())]
    for name, data in sources:
        source = scratch / name
        source.write_bytes(data)
        binary = scratch / source.stem
        command = ['g++', '-std=c++14', '-O0', '-g0', '-I', str(scratch), str(source), '-o', str(binary)]
        built = subprocess.run(command, capture_output=True, text=True, timeout=60)
        assert built.returncode == 0, built.stderr
        run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20,
                             preexec_fn=no_core_dump)
        assert run.returncode == 0, (name, run.stderr)
        # O13 and C03 deliberately abort only a child. Preserve the assertion.
        results.append({'test': name, 'sha256': sha(data), 'exit_code': run.returncode,
                        'stdout': run.stdout,
                        'stderr': run.stderr.replace(str(scratch), '<temporary-header-tests>'),
                        'expected_child_abort': name in (
                            'dtc_l1_bad_generation_test.cc', 'dtc_l1_completion_accounting_test.cc')})

with (PACK / 'SOURCE_SHA256.tsv').open('w') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['role', 'commit', 'path', 'git_blob', 'sha256', 'bytes', 'worktree_match'])
    w.writerows(rows)
receipt = {'status': 'PASS_BOUNDED_SOURCE_AND_HEADER_CHECKS', 'core': CORE, 'framework_build': BUILD,
           'evidence_commits': {'A': A, 'T': T, 'U': U}, 'compiler': compiler,
           'compile_flags': ['-std=c++14', '-O0', '-g0', 'assertions enabled'],
           'static_checks': static, 'header_tests': results,
           'full_simulator_runs': 0, 'architectural_value_tests': 0,
           'source_manifest_rows': len(rows), 'core_clean': True,
           'scope': 'No K1 implementation exists here. PASS is not data coherence or all-ISA correctness.'}
(PACK / 'CPU_CHECKS.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'tests': len(results), 'source_rows': len(rows)}))
