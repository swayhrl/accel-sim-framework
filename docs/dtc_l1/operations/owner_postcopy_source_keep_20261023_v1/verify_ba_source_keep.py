#!/usr/bin/env python3
"""One bounded BA owner reconfirmation. Reads four sources; never mutates them.
Run manually only for a newly authorized owner snapshot, not as a periodic test.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys

T_COMMIT = 'aecccb6ad757a17c1c254940b01e11d56a6480a1'
OWNER_COMMIT = '75706e8a0e58309087c4eadb6280f7f3578bcb76'
T_BASE = 'docs/ep_l2/operations/result_offload_pilot_20261023_v1/'
OWNER_BASE = 'docs/dtc_l1/review_packs/DTC_AG8R1_FINITE_RESUME_20261021_V1/'
OLD_WORKTREE = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-ag8r1-finite-resume-174-v1')
TXID = '24b5cab04e21b55c269d15fce39746c03c4730159b24a2f5fd657ae687964a9c'
TARGET_SHA = 'db87833e52fd98c738a68e85591da3c70e2cb506f2c6fd7ffd495fe4bd27077d'
FIELDS = ('dev', 'inode', 'size', 'mtime_ns', 'ctime_ns', 'uid', 'gid', 'mode', 'nlink')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd)


def git_file(commit, path):
    raw = git('show', commit + ':' + path)
    return raw, {'commit': commit, 'path': path, 'bytes': len(raw),
                 'git_blob': git('rev-parse', commit + ':' + path).decode().strip(),
                 'sha256': sha(raw)}


def identity(s):
    return {'dev': s.st_dev, 'inode': s.st_ino, 'size': s.st_size,
            'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns,
            'uid': s.st_uid, 'gid': s.st_gid, 'mode': s.st_mode,
            'nlink': s.st_nlink, 'permissions_mode': stat.S_IMODE(s.st_mode),
            'allocated': s.st_blocks * 512}


def directory_snapshot(path):
    # O_NOATIME prevents this owner inventory from altering access metadata.
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NOATIME | os.O_CLOEXEC)
    try:
        before = identity(os.fstat(fd))
        entries = []
        for name in sorted(os.listdir(fd)):
            s = os.stat(name, dir_fd=fd, follow_symlinks=False)
            kind = 'directory' if stat.S_ISDIR(s.st_mode) else 'regular' if stat.S_ISREG(s.st_mode) else 'other'
            entries.append({'name': name, 'dev': s.st_dev, 'inode': s.st_ino, 'kind': kind})
        assert before == identity(os.fstat(fd)) == identity(os.lstat(path)), path
    finally:
        os.close(fd)
    return {'path': path, **before, 'entries': entries}


def main(evidence, output):
    assert socket.gethostname() == 'huangrulin-174'
    assert os.getuid() == 0
    assert git('rev-parse', 'HEAD', cwd=OLD_WORKTREE).decode().strip() == OWNER_COMMIT
    assert not git('status', '--porcelain', cwd=OLD_WORKTREE).strip()
    remote_inputs = json.loads((evidence / 'GITHUB_REMOTE_INPUTS.json').read_bytes())
    inputs = {}
    for key, rel in [('request', 'OWNER_POSTCOPY_HANDOFF_REQUEST.json'),
                     ('target_receipt', 'results/DTC_L1_AD_GEMM/ARCHIVE_AND_NATIVE_RESTORE_RECEIPT.json'),
                     ('T_source_proof', 'results/DTC_L1_AD_GEMM/SOURCE_POSTCOPY_READONLY_CHECK.json')]:
        raw, ref = git_file(T_COMMIT, T_BASE + rel)
        assert remote_inputs[key].encode('utf-8') == raw, key
        inputs[key] = (json.loads(raw), ref)
    request = inputs['request'][0]
    project = next(x for x in request['projects'] if x['owner'] == 'BA')
    wrapper = inputs['target_receipt'][0]
    target = wrapper['receipt']
    proof = inputs['T_source_proof'][0]
    assert project['txid'] == target['txid'] == proof['txid'] == TXID
    canonical_target = (json.dumps(target, sort_keys=True, separators=(',', ':')) + '\n').encode()
    assert sha(canonical_target) == wrapper['receipt_sha256'] == project['target_receipt_sha256'] == TARGET_SHA
    assert target['owner_publication'] == OWNER_COMMIT
    assert project['files'] == target['files'] == 4
    assert project['bytes'] == target['raw_bytes'] == 183244
    assert target['source_disposition'] == proof['source_action'] == request['source_action'] == 'SOURCE_KEEP'
    assert target['source_released_bytes'] == proof['source_released_bytes'] == request['source_released_bytes'] == 0
    references = []
    parsed = {}
    for name in ['COPY_READY_AD_GEMM.json', 'ACCEPTED_METRICS.json', 'PER_START_EVIDENCE.json',
                 'AG8R1_COHORT_TERMINAL.json', 'AG8R1_BUDGET_LEDGER.json']:
        path = OWNER_BASE + name
        raw, ref = git_file(OWNER_COMMIT, path)
        assert (OLD_WORKTREE / path).read_bytes() == raw
        assert Path(path).read_bytes() == raw
        references.append({**ref, 'old_owner_worktree_and_current_copy_equal_exact_git': True})
        parsed[name] = json.loads(raw)
    ready = parsed['COPY_READY_AD_GEMM.json']
    assert references[0]['sha256'] == target['owner_ready_sha256'] == proof['owner_ready_sha256']
    dir_before = [directory_snapshot(x['path']) for x in ready['directories']]
    for actual, expected in zip(dir_before, ready['directories']):
        assert all(actual[k] == expected[k] for k in FIELDS), actual['path']
        assert actual['entries'] == expected['entries'], actual['path']
    files = []
    for expected in ready['files']:
        path = expected['path']
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME | os.O_CLOEXEC)
        try:
            before = identity(os.fstat(fd))
            assert stat.S_ISREG(before['mode']) and before == identity(os.lstat(path))
            assert all(before[k] == expected[k] for k in FIELDS), path
            chunks = []
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            raw = b''.join(chunks)
            after = identity(os.fstat(fd))
            assert before == after == identity(os.lstat(path)), path
        finally:
            os.close(fd)
        digest = sha(raw)
        target_row = next(x for x in target['paths'] if x['source'] == path)
        proof_row = next(x for x in proof['files'] if x['relative_path'] == expected['name'])
        assert digest == expected['sha256'] == target_row['sha256'] == proof_row['sha256']
        assert len(raw) == before['size'] == target_row['size']
        for row in [target_row['source_identity'], proof_row['identity']]:
            assert all((before['permissions_mode'] if k == 'mode' else before[k]) == v for k, v in row.items())
        files.append({'path': path, 'name': expected['name'], 'sha256': digest,
                      'before': before, 'after': after, 'path_fd_identity_matched': True,
                      'equal_original_COPY_READY_target_receipt_and_T_postcopy_proof': True,
                      'noatime_read': True, 'owner_read_fd_closed': True})
    dir_after = [directory_snapshot(x['path']) for x in ready['directories']]
    assert dir_before == dir_after
    assert sum(x['before']['size'] for x in files) == 183244
    metrics = parsed['ACCEPTED_METRICS.json']
    assert metrics['accepted'] == 1 and metrics['rows'][0]['cycles'] == ready['accepted_state']['cycles'] == 1044499
    gemm = next(x for x in parsed['PER_START_EVIDENCE.json']['points'] if x['point'] == 'AD_GEMM')
    assert gemm['accepted'] and gemm['attempt_uuid'] == ready['attempt_uuid']
    assert gemm['references']['STRICT.json']['sha256'] == next(x for x in files if x['name'] == 'STRICT.json')['sha256']
    receipt = {
        'schema': 'DTC_L1_BA_OWNER_POSTCOPY_SOURCE_KEEP_RECEIPT_V1',
        'status': 'PASS_OWNER_RECONFIRMED_SOURCE_KEEP',
        'issued_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'owner': 'DTC-L1 BA', 'canonical_task': '/root', 'host': socket.gethostname(),
        'independently_issued_by_owner': True, 'not_issued_by_T': True,
        'project': 'DTC_L1_AD_GEMM', 'txid': TXID, 'target_receipt_sha256': TARGET_SHA,
        'target_receipt_sha256_definition': 'SHA256(UTF8(json.dumps(wrapper.receipt,sort_keys=True,separators=(comma,colon))+LF))',
        'published_T_inputs': {k: v[1] for k, v in inputs.items()},
        'target_receipt_source_proof_note': 'Target source_readonly_proof_sha256 binds its earlier transfer-stage proof; the separately published later T postcopy proof is bound above by its own exact Git file SHA256. These are distinct proofs.',
        'owner_COPY_READY_sha256': references[0]['sha256'], 'original_owner_publication': OWNER_COMMIT,
        'files_count': len(files), 'source_bytes_hashed_once': 183244, 'files': files,
        'directory_records_before': dir_before, 'directory_records_after': dir_after,
        'directory_identity_and_entries_unchanged': True,
        'accepted_references': references, 'original_accepted_references_unchanged': True,
        'accepted_state': ready['accepted_state'], 'science_acceptance_recomputed_or_promoted': False,
        'source_action': 'SOURCE_KEEP', 'source_released_bytes': 0,
        'source_paths_remain_authoritative': True, 'source_mutations': 0,
        'reader_disposition': {
            'this_owner_snapshot': 'ALL_READ_ONLY_NOATIME_FDS_CLOSED_BEFORE_RECEIPT_WRITE',
            'planned_owner_source_readers': 'NONE_SCHEDULED; coordinate any future BA source read with T',
            'original_owner_reader_disposition_reference': references[0],
            'other_owner_or_unregistered_readers': 'UNKNOWN_NOT_SCANNED; no global quiescence claim',
            'source_deletion_or_release': 'NOT_AUTHORIZED_NOT_SCHEDULED'},
        'scientific_goal_restarted_or_reset': False, 'science_starts': 0,
        'scientific_budgets_and_frozen_UUIDs': 'UNCHANGED',
        'target_archive_or_native_restore_reaudited_by_BA': False,
        'scope': 'One owner-only postcopy source verification; T retains target verification and final resource/workflow accounting.',
        'E2_owner_signature': 'NOT_ISSUED_BY_BA; E2 must independently reconfirm its own request transaction',
    }
    with output.open('x') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status': receipt['status'], 'files': len(files), 'bytes': 183244,
                      'receipt': str(output), 'txid': TXID, 'source_released_bytes': 0}))


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
