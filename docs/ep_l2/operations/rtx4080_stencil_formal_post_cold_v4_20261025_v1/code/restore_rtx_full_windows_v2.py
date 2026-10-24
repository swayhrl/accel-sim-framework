"""Full immutable RTX object cold read through bounded Native ext4 windows.

No payload is omitted because of its size. The full-file digest consumes every
closed, reopened Native window. This is not simultaneous full-tree materialization.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import time

C = pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
N = C.parent
B = pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def atomic_new(p, obj):
    assert not p.exists()
    temp = p.with_name(p.name + '.tmp')
    with temp.open('x') as out:
        json.dump(obj, out, indent=2)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())
    os.replace(temp, p)


def rel_path(s):
    p = pathlib.PurePosixPath(s)
    assert s and not p.is_absolute() and '..' not in p.parts and str(p) == s
    return pathlib.Path(*p.parts)


def full_member_set(root):
    result = set()
    for current, dirs, files in os.walk(root, followlinks=False):
        current = pathlib.Path(current)
        for name in dirs + files:
            assert not (current / name).is_symlink(), 'No source symlink traversal'
        for name in files:
            p = current / name
            assert p.is_file()
            result.add(p.relative_to(root).as_posix())
    return result


def restore_file(source, expected_bytes, expected_sha, work, window_bytes,
                 check, rate_bytes, pace=None, opener=None):
    before = source.stat()
    assert before.st_size == expected_bytes
    digest = hashlib.sha256()
    offset = windows = largest = 0
    start = time.monotonic()
    window = work / 'current.window'
    assert not window.exists()
    with (opener(source) if opener else source.open('rb')) as inp:
        while offset < expected_bytes or windows == 0:
            check()
            target = min(window_bytes, expected_bytes - offset)
            part = hashlib.sha256()
            written = 0
            with window.open('xb') as out:
                while written < target:
                    check()
                    b = inp.read(min(2**20, target - written))
                    assert b, 'Source truncated before declared EOF'
                    out.write(b)
                    if pace:pace(len(b))
                    part.update(b)
                    written += len(b)
                    time.sleep(max(0, (offset + written) / rate_bytes -
                                   (time.monotonic() - start)))
                out.flush()
                os.fsync(out.fileno())
            reopened = hashlib.sha256()
            with window.open('rb') as cold:
                for b in iter(lambda: cold.read(2**20), b''):
                    check()
                    reopened.update(b)
                    digest.update(b)
            assert reopened.hexdigest() == part.hexdigest()
            assert window.stat().st_size == target
            offset += target
            windows += 1
            largest = max(largest, target)
            # Release only this owned, closed, SHA-verified temporary window.
            assert window.parent == work and not window.is_symlink()
            window.unlink()
        assert inp.read(1) == b'', 'Source has extra bytes beyond manifest size'
    assert offset == expected_bytes and digest.hexdigest() == expected_sha
    after = source.stat()
    assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)
    return {'bytes': offset, 'sha256': digest.hexdigest(), 'windows': windows,
            'max_window_bytes': largest, 'closed_reopened_Native_all_bytes': True}


def run(root, work, output, limit, rate, guard, expected_commit, pace=None, opener=None):
    assert not work.exists() and not output.exists()
    work.mkdir()
    commit_bytes = (root / 'COMMIT.json').read_bytes()
    assert sha_bytes(commit_bytes) == expected_commit
    commit = json.loads(commit_bytes)
    assert commit['status'] == 'COMMITTED_VERIFIED'
    manifest_bytes = (root / 'MANIFEST.json').read_bytes()
    assert sha_bytes(manifest_bytes) == commit['manifest_sha256']
    manifest = json.loads(manifest_bytes)
    rows = manifest['files']
    names = [r['path'] for r in rows]
    assert len(names) == len(set(names)) == manifest['file_count']
    assert sum(r['bytes'] for r in rows) == manifest['logical_bytes']
    assert commit['files'] == len(rows) and commit['logical_bytes'] == manifest['logical_bytes']
    for row in rows:
        rel_path(row['path'])
        assert isinstance(row['bytes'], int) and row['bytes'] >= 0
    expected_set = set(names) | {'COMMIT.json', 'MANIFEST.json'}
    assert full_member_set(root) == expected_set
    all_rows = rows + [
        {'path': 'MANIFEST.json', 'bytes': len(manifest_bytes), 'sha256': sha_bytes(manifest_bytes)},
        {'path': 'COMMIT.json', 'bytes': len(commit_bytes), 'sha256': expected_commit},
    ]
    results = []
    ledger = work / 'MEMBERS_CLOSED.jsonl'
    for row in all_rows:
        guard()
        result = restore_file(root / rel_path(row['path']), row['bytes'], row['sha256'],
                              work, limit, guard, rate, pace, opener)
        result['path'] = row['path']
        results.append(result)
        with ledger.open('a') as f:
            f.write(json.dumps(result) + '\n')
            f.flush()
            os.fsync(f.fileno())
    guard()
    assert full_member_set(root) == expected_set
    assert (root / 'COMMIT.json').read_bytes() == commit_bytes
    assert (root / 'MANIFEST.json').read_bytes() == manifest_bytes
    assert not (work / 'current.window').exists()
    receipt = {
        'status': 'ALL_MANIFEST_MEMBERS_BOUNDED_NATIVE_COLD_RESTORE_PASS',
        'asset_id': commit['asset_id'], 'COMMIT_sha256_before_and_after': expected_commit,
        'MANIFEST_sha256_before_and_after': commit['manifest_sha256'],
        'manifest_payload_files': len(rows), 'manifest_payload_bytes': manifest['logical_bytes'],
        'including_manifest_and_commit_files': len(results),
        'including_manifest_and_commit_bytes': sum(r['bytes'] for r in results),
        'all_member_exact_set': True, 'member_results': results,
        'maximum_live_window_bytes': max(r['max_window_bytes'] for r in results),
        'window_limit_bytes': limit, 'rate_limit_NAS_bytes_per_second': rate,
        'scope': 'Every manifest member and both immutable metadata files restored serially through closed/reopened Native windows; all failed history in manifest included; no simultaneous full-tree materialization',
        'original_source_KEEP': True, 'source_release_bytes': 0,
        'GPU_SIM_109_or_full_record_validation_runs': 0,
    }
    atomic_new(output, receipt)
    return receipt


def main():
    import resource,fcntl,stat
    jobpath=pathlib.Path(__import__('sys').argv[1]);job=json.loads(jobpath.read_text())
    assert job['status']=='APPROVED_EXACT_STENCIL_ALL_MEMBER_COLD_V2'
    assert sha_bytes(pathlib.Path(__file__).read_bytes())==job['worker_sha256']
    assert job['asset_id']=='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2'
    work=pathlib.Path(job['work']);output=pathlib.Path(job['candidate'])
    assert work.parent==N and work.name==job['asset_id']+'_bounded_cold_v2'
    assert output==work/'FINAL_CANDIDATE.json'
    assert work.parent.stat().st_dev==2128 and C.stat().st_dev==2128
    for row in job['dependencies']:
        p=pathlib.Path(row['path']);assert p.stat().st_size==row['bytes'] and sha_bytes(p.read_bytes())==row['sha256']
    def load(name,path):
        q=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
    assert sha_bytes((C/'resource_library_copy_v10_pinned.py').read_bytes())=='7e5b290e330cbc1fcc845b6a9c7ce3487d181677d117a8d77a31c60d12a42521'
    assert sha_bytes((C/'read_native_foreign_reserve_v1.py').read_bytes())=='441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba'
    policy=load('resource10',C/'resource_library_copy_v10_pinned.py');auth=load('authority',C/'read_native_foreign_reserve_v1.py')
    normal=policy.Resources();deadline=time.monotonic()+job['deadline_seconds'];last=None;last_at=0
    prefix=job['asset_id']+'_COLD_V2_';cap=128*2**20
    resource.setrlimit(resource.RLIMIT_FSIZE,(cap,cap))
    def usage():
        total=0
        for p in list(work.glob('*'))+list(C.glob(prefix+'*')):
            try:s=p.stat()
            except OSError as e:
                if e.errno==2:continue
                raise
            assert stat.S_ISREG(s.st_mode),'cold native scratch only flat regular files'
            total+=s.st_size
        return total
    def guard(admission=False):
        nonlocal last,last_at
        assert time.monotonic()<deadline
        if last is None or time.monotonic()-last_at>=10:
            until=time.monotonic()+10
            while True:
                n=normal(True);a=auth.snapshot()
                if n['registered_foreign_write_reservations_bytes']==a['sum_all_records_reserved_write_bytes']:break
                assert time.monotonic()<until
            last={'normal':n,'authority':a};last_at=time.monotonic()
        used=usage();assert used<=cap
        floor=5*2**30+last['authority']['sum_all_records_reserved_write_bytes']+2**30+64*2**20
        assert shutil.disk_usage(N).free>=floor+max(0,cap-used)+(128*2**20 if admission else 0)
    guard(True)
    lock=(N/(job['asset_id']+'_validation_hot_epoch2/AGGREGATE_NAS_READ.lock')).open('a')
    # Every payload read itself is serialized and adaptively paced by this
    # wrapper, so no other participating NAS reader bypasses its aggregate lock.
    class LimitedReader:
        def __init__(self,stream):self.stream=stream
        def __enter__(self):return self
        def __exit__(self,*args):return self.stream.__exit__(*args)
        def read(self,count=-1):
            assert 0<=count<=2**20
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:
                b=self.stream.read(count)
                if b:policy.adaptive_io_pace(len(b),15*2**20)
                return b
            finally:fcntl.flock(lock,fcntl.LOCK_UN)
    root=B/'objects'/job['asset_id']
    def opener(p):
        assert root in p.parents
        return LimitedReader(p.open('rb'))
    try:
        result=run(root,work,output,64*2**20,15*2**20,guard,job['commit_sha256'],opener=opener)
        guard()
    finally:lock.close()
    print(json.dumps({k:v for k,v in result.items()if k!='member_results'}))

if __name__=='__main__':main()
