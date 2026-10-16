"""A65 lock-free, standard-library-only admission audit; never launches CUDA."""
import ast
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time

W = Path(__file__).resolve().parents[2]
R = Path('/data/c16/aiarch_a65_igb_small_compiled_numeric_109_v1')
OLD = Path('/data/c16/aiarch_a61_igb_small_gnn_native_109_v1')
START = 'afe42345c4b0c45b3e09f3cb32ce4e3e0de09989'
PARENT = '37120f98186b83a946f4812755523f5d73245491'
REVIEW = '326dcac6227d1c1af6b38e4f76d21566525f35aa'
GOAL = 'docs/ai_workload_research/goals/AI_ARCH_A65_IGB_SMALL_SAME_BATCH_COMPILED_UPDATE_NUMERIC_109_V1.md'
REVIEW_PATH = 'docs/ai_workload_research/reviews/AI_ARCH_A64_A61_GNN_NUMERIC_STOP_INDEPENDENT_REVIEW_2026-10-16_V1.md'
RUN = 'docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1/'
os.sched_setaffinity(0, [0, 2, 4, 6])


def git(*args):
    return subprocess.check_output(['git', *args], cwd=W)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def save(name, value):
    (R / name).write_text(json.dumps(value, indent=2) + '\n')


def snapshot(root):
    # Metadata inventory includes old cache/raw/source; no Python imports there.
    out = {}
    for path in sorted(root.rglob('*')):
        st = path.lstat()
        out[str(path.relative_to(root))] = [st.st_mode, st.st_size, st.st_mtime_ns,
                                           os.readlink(path) if path.is_symlink() else None]
    return out


def allocated(root):
    return sum(p.lstat().st_blocks * 512 for p in root.rglob('*'))


def main():
    t0 = time.monotonic()
    assert git('rev-parse', 'HEAD').decode().strip() == START
    assert git('rev-parse', PARENT + '^{tree}').decode().strip() == 'd13b446ca4824cb3ad7ffae25b5ce91c023b75a1'
    assert not R.exists(), 'A65 output must be new'
    # Admission is checked before costly asset hashing or any GPU environment work.
    free = shutil.disk_usage(OLD).free
    assert free < 64 * 1024**3, 'Reassess admission; this receipt only handles observed failure'
    R.mkdir()
    before = snapshot(OLD)
    save('old_asset_metadata_before.json', before)
    authorities = {}
    for commit, path in [(START, GOAL), (REVIEW, REVIEW_PATH),
                         (PARENT, RUN + 'FINAL_REPORT.md'),
                         (PARENT, RUN + 'COMPILED_QUALIFICATION_FAILURE.json'),
                         (PARENT, RUN + 'raw/native_attempt0_compile.log'),
                         (PARENT, 'tools/aiarch_a61/native.py'),
                         (PARENT, 'tools/aiarch_a61/native_utils.py'),
                         (PARENT, 'tools/aiarch_a61/common.py'),
                         (PARENT, 'tools/aiarch_a61/gpu_supervisor.py')]:
        body = git('show', commit + ':' + path)
        authorities[commit + ':' + path] = {
            'git_blob': git('rev-parse', commit + ':' + path).decode().strip(),
            'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
        if path.startswith('tools/'):
            assert body == (W / path).read_bytes(), 'A61 source changed'
    save('authority_identity.json', authorities)
    (R / 'A64_REVIEW_READONLY.md').write_bytes(git('show', REVIEW + ':' + REVIEW_PATH))
    source = (W / 'tools/aiarch_a61/native.py').read_text()
    utils = (W / 'tools/aiarch_a61/native_utils.py').read_text()
    ast.parse(source)
    ast.parse(utils)
    save('static_review.json', {
        'compiled_entry': 'torch.compile(train_step,dynamic=True); original model objects',
        'old_joint_predicate': 'n==n2 AND torch.allclose(p,z,atol=1e-6,rtol=1e-4)',
        'separate_old_name_gate_result': 'UNKNOWN_NOT_CAPTURED',
        'old_initial_parameter_SHA': 'UNKNOWN_NOT_CAPTURED',
        'old_compiled_gradient_and_update_deltas': 'UNKNOWN_NOT_CAPTURED',
        'risks': ['zip does not separately assert length/order/names/shape/dtype',
                  'initial weights and empty optimizer states not independently hashed',
                  'cache correctness replays precede compiled reuse of original mb',
                  'exact original mb feature lifetime and before/after hashes not captured'],
        'old_common_and_supervisor': 'hardcoded A61 output; neither executed nor imported',
        'old_sitecustomize': 'hardcoded A61 write allowance; must not reuse as A65 guard',
        'sitecustomize_SHA256': sha(OLD / 'venv/lib/python3.10/site-packages/sitecustomize.py'),
        'future_runner_requirement': 'new output/cache namespace and read-only packages; exact same math, seed, gates, versions',
        'comparator_GPU_runner_and_full_asset_rehash': 'NOT_RUN: resource admission already failed',
        'A61_STOP_preserved': True,
        'compiler_bug': 'NOT_ESTABLISHED'})
    payloads = json.loads((OLD / 'graph_cpu_identity.json').read_text())['files']
    files = {}
    for path, accepted in payloads.items():
        p = Path(path)
        st = p.stat()
        assert st.st_size == accepted['bytes']
        files[path] = {'exists': True, 'bytes': st.st_size,
                       'accepted_A61_SHA256': accepted['sha256'],
                       'fresh_full_SHA256': 'NOT_RUN_AFTER_RESOURCE_STOP'}
    save('asset_presence_only.json', {
        'status': 'PRESENT_SIZE_MATCH_ONLY_NOT_FRESH_SHA_QUALIFIED',
        'files': files,
        'train_split_present': (OLD / 'train_ids.npy').is_file(),
        'natural_order_present': (OLD / 'order_20261015.npy').is_file(),
        'frozen_environment_present': (OLD / 'venv/pyvenv.cfg').is_file(),
        'full_library_and_payload_hash_gate': 'NOT_RUN_AFTER_RESOURCE_STOP'})
    after = snapshot(OLD)
    assert before == after, 'Old assets metadata mutated during audit'
    save('readonly_check.json', {
        'status': 'PASS_METADATA_UNCHANGED', 'entries': len(before),
        'comparison': 'lstat mode/size/mtime_ns/symlink target; before == after',
        'full_content_rehash': False,
        'old_source_git_bytes_match': True,
        'old_environment_imports': 0, 'old_asset_writes_by_task': 0})
    save('resource_stop.json', {
        'status': 'BUDGET_STOP', 'reason': 'FREE_FS_BELOW_64_GIB_AT_CPU_ADMISSION',
        'filesystem_path': str(OLD), 'available_bytes': free,
        'available_GiB': free / 1024**3, 'required_bytes': 64 * 1024**3,
        'shortfall_bytes': 64 * 1024**3 - free,
        'new_worktree_allocated_bytes_at_audit': allocated(W),
        'old_cache_allocated_bytes_readonly_estimate': allocated(OLD / 'cache'),
        'GPU_lock_attempts': 0, 'GPU_lock_seconds': 0,
        'CUDA_initializations': 0, 'GPU_processes_launched': 0,
        'minibatches_sampled': 0, 'qualification_updates': 0,
        'formal_updates': 0, 'download_data_dependency_bytes': 0, 'installs': 0,
        'environment_created': False, 'compile_cache_created': False,
        'RAM_peak_audit_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        'CPU_affinity': sorted(os.sched_getaffinity(0)),
        'CPU_audit_wall_seconds': time.monotonic() - t0,
        'policy': 'no cleanup of old assets, no polling for resources, no threshold relaxation',
        'eagerA': 'NOT_RUN', 'eagerB': 'NOT_RUN', 'compiledC': 'NOT_RUN',
        'numerical_qualification': 'NOT_RUN', 'no_future_GPU_goal': True})
    print(json.dumps(json.loads((R / 'resource_stop.json').read_text()), indent=2))


if __name__ == '__main__':
    main()
