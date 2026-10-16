"""Lock-free evidence closeout; never resumes CUDA or changes original A61 assets."""
import json
from pathlib import Path
import subprocess
import sys
from paths import OLD, R, W, ROOT, CLEANUP, save, sha, allocated
from preflight import snapshot


def main():
    before = json.loads((R / 'old_A61_metadata_before.json').read_text())
    assert snapshot(OLD) == before, 'OLD_A61_METADATA_CHANGED'
    bindings = json.loads((OLD / 'readonly_runtime_bindings.json').read_text())
    site = Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/venv/lib/python3.10/site-packages')
    count = 0
    for distribution in bindings['distributions']:
        for row in distribution['verified_installed_files']:
            p = site / row['path']
            st = p.stat()
            assert st.st_size == row['bytes'] and st.st_mtime_ns == row['mtime_ns'] and sha(p) == row['sha256'], str(p)
            count += 1
    for row in json.loads((R / 'CPU_preflight.json').read_text())['checked_graph_files']:
        assert sha(row['path']) == row['sha256']
    scripts = json.loads((R / 'pre_GPU_script_identity.json').read_text())
    assert all(sha(W / name) == value for name, value in scripts.items()), 'EXECUTED_SOURCE_MUTATED'
    subprocess.run([sys.executable, str(W / 'tools/aiarch_a65/library_audit.py'), '--post'], check=True)
    ledger = json.loads((R / 'gpu_ledger.json').read_text())
    assert ledger['cumulative_seconds'] <= 180
    assert all(x['all_owned_processes_ended'] for x in ledger['attempts'])
    save('post_readonly_audit.json', {'status': 'PASS', 'old_A61_metadata_entries_unchanged': len(before),
                                      'core_runtime_files_SHA_size_mtime_unchanged': count,
                                      'all_used_graph_and_feature_SHA_unchanged': True,
                                      'GPU_executed_source_unchanged': True,
                                      'new_allocated_including_cleanup_bytes': allocated(),
                                      'no_CUDA_no_GPU_lock_in_this_audit': True})
    print('PASS_POST_READONLY_AND_RESOURCE_AUDIT', count, flush=True)


if __name__ == '__main__':
    main()
