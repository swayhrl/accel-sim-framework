"""Lock-free A65 admission: metadata, full accepted asset SHA, isolated package view."""
import ast
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import time
from paths import OLD, R, ROOT, W, CLEANUP, sha, save, allocated


def snapshot(root):
    result = {}
    for p in sorted(root.rglob('*')):
        st = p.lstat()
        result[str(p.relative_to(root))] = [st.st_mode, st.st_size, st.st_mtime_ns,
                                           os.readlink(p) if p.is_symlink() else None]
    return result


def main():
    assert not R.exists(), 'resume directory must be new'
    R.mkdir()
    for sub in ['raw', 'cache/home', 'cache/inductor', 'cache/triton', 'cache/driver',
                'cache/torch', 'cache/extensions', 'tmp']:
        (R / sub).mkdir(parents=True)
    started = time.monotonic()
    save('old_A61_metadata_before.json', snapshot(OLD))
    public = W / 'docs/ai_workload_research/runs/AI_ARCH_A61_IGB_SMALL_GNN_NATIVE_109_V1'
    accepted = json.loads((public / 'GRAPH_AND_TRAIN_IDENTITY.json').read_text())
    checked = []
    for path, record in accepted['graph']['files'].items():
        p = Path(path.replace('<A61_OUTPUT>', str(OLD)))
        assert p.stat().st_size == record['bytes'] and sha(p) == record['sha256'], str(p)
        checked.append({'path': str(p), **record})
    archive = OLD / 'downloads/igb_homogeneous_small.tar.gz'
    # Determine the retained archive basename without changing its accepted identity.
    if not archive.exists():
        choices = [p for p in (OLD / 'downloads').iterdir() if p.stat().st_size == 3865024231]
        assert len(choices) == 1
        archive = choices[0]
    assert sha(archive) == 'fa237780a84b7d1956c180564a9d080d61b43b32b2bf2810b3960f1ab028a919'
    for name, info in accepted['split_and_node_orders']['splits'].items():
        assert sha(OLD / (name + '_ids.npy')) == info['sha256']
    for seed, info in accepted['split_and_node_orders']['orders'].items():
        assert sha(OLD / ('order_' + seed + '.npy')) == info['sha256']
    print('PASS_FULL_DATA_CSC_SPLIT_ORDER_SHA', flush=True)
    bindings = json.loads((OLD / 'readonly_runtime_bindings.json').read_text())
    base = Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/venv/lib/python3.10/site-packages')
    count = 0
    for distribution in bindings['distributions']:
        for rec in distribution['verified_installed_files']:
            p = base / rec['path']
            st = p.stat()
            assert st.st_size == rec['bytes'] and st.st_mtime_ns == rec['mtime_ns']
            assert sha(p) == rec['sha256'], str(p)
            count += 1
    assert count == 10686
    site = OLD / 'venv/lib/python3.10/site-packages'
    local_files = 0
    for p in site.rglob('*'):
        if p.is_file() and not p.is_symlink():
            sha(p)
            local_files += 1
    print('PASS_CORE_10686_AND_A61_SITE_READONLY', local_files, flush=True)
    env = os.environ.copy()
    env.update(LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib',
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    subprocess.run(['/data/c16/env/cpython-3.10.12/bin/python3.10', '-m', 'venv',
                    '--without-pip', '--symlinks', str(R / 'runtime')], check=True, env=env)
    dest = R / 'runtime/lib/python3.10/site-packages'
    links = []
    for p in site.iterdir():
        if p.name in ['sitecustomize.py', '__pycache__']:
            continue
        if p.suffix == '.pth':
            assert p.name == 'distutils-precedence.pth'
            assert '_distutils_hack' in p.read_text() and 'torch' not in p.read_text()
        q = dest / p.name
        assert not q.exists()
        q.symlink_to(p.resolve(), target_is_directory=p.is_dir())
        links.append({'path': str(q), 'readonly_target': str(p.resolve())})
    # Own write guard: old sitecustomize is not imported and no old file is edited.
    guard = '''import sys,os,pathlib
_R=pathlib.Path(%r).resolve();_W=pathlib.Path(%r).resolve()
def _allowed(p):
 if not isinstance(p,(str,bytes,os.PathLike)):return True
 q=pathlib.Path(os.fsdecode(p)).resolve()
 return q==pathlib.Path('/dev/null') or q.is_relative_to(_R) or q.is_relative_to(_W)
def _audit(event,args):
 if event=='open' and len(args)>2 and isinstance(args[2],int) and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
  if not _allowed(args[0]):raise PermissionError('A65_OUTSIDE_WRITE_BLOCKED '+str(args[0]))
 if event in ['os.remove','os.rmdir','os.mkdir','os.chmod'] and not _allowed(args[0]):raise PermissionError('A65_OUTSIDE_WRITE_BLOCKED')
 if event in ['os.rename','os.replace'] and (not _allowed(args[0]) or not _allowed(args[1])):raise PermissionError('A65_OUTSIDE_MOVE_BLOCKED')
sys.addaudithook(_audit)
''' % (str(R), str(W))
    (dest / 'sitecustomize.py').write_text(guard)
    versions = {d.metadata['Name'].lower().replace('_', '-'): d.version
                for d in importlib.metadata.distributions(path=[str(dest)])}
    for name, version in {'torch': '2.2.0+cu121', 'dgl': '2.4.0+cu121',
                          'torch-geometric': '2.6.1', 'numpy': '1.26.4',
                          'triton': '2.2.0'}.items():
        assert versions[name] == version
    save('runtime_view.json', {'status': 'PASS_UNCHANGED_PACKAGES_READONLY_VIEW',
                              'links': links, 'versions': versions,
                              'dependency_installs': 0, 'downloads': 0,
                              'old_sitecustomize_imported': False})
    source = (W / 'tools/aiarch_a61/native_utils.py').read_text()
    names = ['GraphSAGE', 'train_step', 'DataContext', 'validate_mb']
    body = '\n\n'.join(ast.get_source_segment(source, node) for node in ast.parse(source).body
                         if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names)
    header = '''"""Read-only audited A61 algorithm copies; Apache-2.0 DGL example attribution retained."""
import os,hashlib
assert os.environ.get('A65_GPU_LOCK_HELD')=='1'
from paths import OLD,R,save,event
import numpy as np
import torch
import torch.nn.functional as F
import dgl
import dgl.graphbolt as gb
from torch_geometric.nn import SAGEConv
N=1000000;D=1024;B=1024;C=19
FEAT=np.load(OLD/'data/small/processed/paper/node_feat.npy',mmap_mode='r')
LABEL=np.load(OLD/'data/small/processed/paper/node_label_19.npy',mmap_mode='r').reshape(-1)
IP=np.load(OLD/'graph/indptr.npy',mmap_mode='r')
IX=np.load(OLD/'graph/indices.npy',mmap_mode='r')
KEYS=np.load(OLD/'graph/edge_keys_sorted.npy',mmap_mode='r')
def sync():torch.cuda.synchronize()
def digest_array(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
'''
    (W / 'tools/aiarch_a65/math_copy.py').write_text(header + '\n' + body + '\n')
    original = {x.name: ast.dump(x, include_attributes=False) for x in ast.parse(source).body
                if isinstance(x, (ast.ClassDef, ast.FunctionDef)) and x.name in names}
    copied = {x.name: ast.dump(x, include_attributes=False) for x in ast.parse(body).body}
    assert original == copied
    save('algorithm_ast_identity.json', {'status': 'PASS_EXACT_AST', 'definitions': names,
                                        'A61_native_utils_SHA256': sha(W / 'tools/aiarch_a61/native_utils.py'),
                                        'A65_math_copy_SHA256': sha(W / 'tools/aiarch_a65/math_copy.py')})
    log = subprocess.check_output([str(R / 'runtime/bin/python'),
                                  str(W / 'tools/aiarch_a65/test_compare.py')], env=env, text=True)
    assert log.strip() == 'PASS_12_DIRECTED_COMPARATOR_CASES_NO_TORCH'
    save('comparator_cpu_tests.json', {'status': 'PASS', 'stdout': log,
                                      'Torch_imports': 0, 'CUDA_initializations': 0})
    save('preregistration.json', {
        'input': 'one new natural official ItemSampler B1024, seed20261015, original train split',
        'sampling': 'PINNED_CACHE_ON; exact A61 DataContext API/maths; clone one returned minibatch',
        'models': '3 independent GraphSAGE+Adam, unique seed20261015 CPU state loaded bitwise',
        'entry': 'original train_step; compiledC=torch.compile(train_step,dynamic=True)',
        'updates': 'A/B/C once each; total3; no formaltraining or numerical-failure retry',
        'loss_gate': {'atol': 1e-5, 'rtol': 1e-4, 'relative_denominator': 'eagerA loss'},
        'updated_parameter_gate': {'atol': 1e-6, 'rtol': 1e-4,
                                   'direction': 'torch.allclose(eagerA, candidate), candidate relative denominator'},
        'gradient_comparison': 'fullbatch paired descriptive statistics; legacy1e-5/1e-3 numbers diagnostic only because original gate used 16seed FP64 oracle',
        'FP32': True, 'TF32': False, 'highest_matmul_precision': True,
        'allocator_fraction': .70, 'cache_size_limit': 32,
        'diagnostic_policy': 'allthree prescribed qualification observations only; input/initialstate/nonfinite/resource violations stop immediately; pair stats classify triplet without an early perparameter assert',
        'compiled_cache': 'fresh A65 private namespace; no old cache writes',
        'qualification_metadata_not_performance': True,
        'new_disk_hard_limit_bytes': 128 * 1024**2,
        'estimated_new_cache_bound_bytes': 32 * 1024**2,
        'estimated_compressed_raw_bound_bytes': 24 * 1024**2,
        'cleanup_must_finish_before_GPU': True})
    assert allocated() + 32 * 1024**2 + 24 * 1024**2 < 128 * 1024**2
    assert snapshot(OLD) == json.loads((R / 'old_A61_metadata_before.json').read_text())
    save('CPU_preflight.json', {'status': 'PASS', 'checked_graph_files': checked,
                                'accepted_archive_SHA256': sha(archive),
                                'old_core_files_SHA_size_mtime_verified': count,
                                'A61_site_regular_files_read': local_files,
                                'new_disk_allocated_before_GPU_bytes': allocated(),
                                'elapsed_seconds': time.monotonic() - started,
                                'no_Torch_import_no_CUDA_no_GPU_lock': True})
    print('A65_CPU_PREFLIGHT_PASS', flush=True)


if __name__ == '__main__':
    main()
