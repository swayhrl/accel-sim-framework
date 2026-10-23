#!/usr/bin/env python3
"""Create the separately authorized full-tree owner manifest, without source writes.
No simulator, sidecar, external-reference traversal, or source release is performed.
This is an operational snapshot tool, not a scientific test or periodic job.
"""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import posixpath
import socket
import stat
import subprocess
import sys
import time

SOURCE = Path('/workspace/dtc-ag8r1-finite-resume-174-v1/attempts/AD_GEMM_940981e5-61c4-4772-83a3-50593fd1ba3a')
UUID = '940981e5-61c4-4772-83a3-50593fd1ba3a'
OWNER_HEAD = '75706e8a0e58309087c4eadb6280f7f3578bcb76'
OWNER_BASE = 'docs/dtc_l1/review_packs/DTC_AG8R1_FINITE_RESUME_20261021_V1/'
OLD_WORKTREE = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-ag8r1-finite-resume-174-v1')
NOATIME = os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME | os.O_CLOEXEC
SMALL_JSON = {'RUN_START.json', 'RUN_TERMINAL.json', 'ENGINE/TERMINAL.json',
              'ACTUAL_PRODUCER_BINDING.json', 'STRICT.json', 'INPUT_RUNTIME_IDENTITY.json',
              'MAPPING_CLOSURE.json'}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd)


def metadata(s):
    return {'dev': s.st_dev, 'device_major': os.major(s.st_dev), 'device_minor': os.minor(s.st_dev),
            'inode': s.st_ino, 'size': s.st_size, 'uid': s.st_uid, 'gid': s.st_gid,
            'mode': s.st_mode, 'mode_octal': oct(s.st_mode),
            'permissions_mode': stat.S_IMODE(s.st_mode), 'permissions_octal': oct(stat.S_IMODE(s.st_mode)),
            'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns, 'atime_ns': s.st_atime_ns,
            'nlink': s.st_nlink, 'blocks_512': s.st_blocks, 'allocated_bytes': s.st_blocks * 512,
            'blksize': s.st_blksize, 'rdev': s.st_rdev}


def invariant(s):
    # Access time is observational, not a scientific or copy-identity invariant.
    return {k: v for k, v in s.items() if k != 'atime_ns'}


def kind(s):
    m = s.st_mode
    return 'directory' if stat.S_ISDIR(m) else 'regular' if stat.S_ISREG(m) else 'symlink' if stat.S_ISLNK(m) else 'special'


def inventory():
    rows = {}

    def walk(path, rel):
        fd = os.open(path, NOATIME | os.O_DIRECTORY)
        try:
            before = metadata(os.fstat(fd))
            assert invariant(before) == invariant(metadata(os.lstat(path))), str(path)
            row = {'relative_path': rel, 'kind': 'directory', 'stat': before, 'entries': sorted(os.listdir(fd))}
            rows[rel] = row
            for name in row['entries']:
                sub = name if rel == '.' else rel + '/' + name
                s = os.stat(name, dir_fd=fd, follow_symlinks=False)
                k = kind(s)
                assert k != 'special', ('unsupported_special_node', sub)
                if k == 'directory':
                    walk(path / name, sub)
                    assert invariant(rows[sub]['stat']) == invariant(metadata(s))
                else:
                    item = {'relative_path': sub, 'kind': k, 'stat': metadata(s)}
                    if k == 'symlink':
                        raw = os.readlink(os.fsencode(name), dir_fd=fd)
                        after = metadata(os.stat(name, dir_fd=fd, follow_symlinks=False))
                        assert invariant(after) == invariant(item['stat']), sub
                        item.update({'target': os.fsdecode(raw), 'target_bytes_hex': raw.hex(),
                                     'link_text_sha256': sha(raw),
                                     'atime_ns_after_readlink': after['atime_ns']})
                    rows[sub] = item
            assert invariant(before) == invariant(metadata(os.fstat(fd))), rel
        finally:
            os.close(fd)
    walk(SOURCE, '.')
    return rows


def stable_inventory(a, b):
    assert set(a) == set(b), 'source tree membership changed'
    for rel in a:
        x, y = a[rel], b[rel]
        assert x['kind'] == y['kind'] and invariant(x['stat']) == invariant(y['stat']), rel
        if x['kind'] == 'directory':
            assert x['entries'] == y['entries'], rel
        if x['kind'] == 'symlink':
            assert x['target_bytes_hex'] == y['target_bytes_hex'], rel


def known_instances(instances):
    rows = []
    for pid, expected in sorted(set(instances)):
        try:
            text = Path('/proc', str(pid), 'stat').read_text()
            fields = text[text.rfind(')') + 2:].split()
            actual, state = int(fields[19]), fields[0]
            same = actual == expected
            live = same and state not in ('Z', 'X', 'x')
            row = {'pid': pid, 'expected_start_ticks': expected, 'observed_start_ticks': actual,
                   'state': state, 'live_owned_writer': live,
                   'disposition': 'OWN_INSTANCE_RETIRED' if same and not live else 'PID_REUSED_NOT_ADOPTED' if not same else 'LIVE_OWN_INSTANCE'}
        except FileNotFoundError:
            row = {'pid': pid, 'expected_start_ticks': expected, 'live_owned_writer': False,
                   'disposition': 'ABSENT_OWN_INSTANCE'}
        assert not row['live_owned_writer'], row
        rows.append(row)
    return {'utc': utc(), 'scope': 'Only exact previously registered AD_GEMM/controller instances; no global process/fd scan, adoption, or signals', 'instances': rows}


def write_new(path, raw):
    with path.open('xb') as f:
        f.write(raw)
    return {'path': path.name, 'bytes': len(raw), 'sha256': sha(raw)}


def main(out, evidence):
    started = utc()
    mono = time.monotonic()
    assert socket.gethostname() == 'huangrulin-174' and os.getuid() == 0
    assert git('rev-parse', 'HEAD', cwd=OLD_WORKTREE).decode().strip() == OWNER_HEAD
    assert not git('status', '--porcelain', cwd=OLD_WORKTREE).strip()
    refs, original = [], {}
    for name in ['COPY_READY_AD_GEMM.json', 'ACCEPTED_METRICS.json', 'PER_START_EVIDENCE.json',
                 'FINAL_OWNED_JOBS.json', 'AG8R1_COHORT_TERMINAL.json', 'AG8R1_BUDGET_LEDGER.json']:
        path = OWNER_BASE + name
        raw = git('show', OWNER_HEAD + ':' + path)
        assert (OLD_WORKTREE / path).read_bytes() == raw == Path(path).read_bytes()
        original[name] = json.loads(raw)
        refs.append({'commit': OWNER_HEAD, 'path': path, 'sha256': sha(raw), 'bytes': len(raw),
                     'git_blob': git('rev-parse', OWNER_HEAD + ':' + path).decode().strip(),
                     'original_owner_worktree_bytes_unchanged': True})
    prior = original['COPY_READY_AD_GEMM.json']
    jobs = original['FINAL_OWNED_JOBS.json']
    assert jobs['status'] == 'NO_OWN_ACTIVE_CONTROLLER_OR_SIMULATOR'
    # The original controller and the three closed AD_GEMM producer instances.
    wanted_pids = {2586113, 2586836, 2586891, 2586892}
    instances = [(x['pid'], x['start_ticks']) for x in jobs['instances'] if x['pid'] in wanted_pids]
    assert {p for p, _ in instances} == wanted_pids
    before_writers = known_instances(instances)
    parents = [{'path': str(p), 'stat': metadata(os.lstat(p))} for p in [SOURCE.parent.parent, SOURCE.parent]]
    before = inventory()
    rows = {}
    small = {}
    read_bytes = 0
    for rel in sorted(before):
        entry = before[rel]
        if entry['kind'] != 'regular':
            continue
        path = SOURCE / rel
        fd = os.open(path, NOATIME)
        digest = hashlib.sha256()
        count = 0
        payload = []
        try:
            first = metadata(os.fstat(fd))
            assert stat.S_ISREG(first['mode'])
            assert invariant(first) == invariant(entry['stat']) == invariant(metadata(os.lstat(path))), rel
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                count += len(chunk)
                if rel in SMALL_JSON:
                    assert count <= 4 * 1024 * 1024, rel
                    payload.append(chunk)
            last = metadata(os.fstat(fd))
            assert invariant(first) == invariant(last) == invariant(metadata(os.lstat(path))), rel
            assert count == first['size']
        finally:
            os.close(fd)
        read_bytes += count
        rows[rel] = {'relative_path': rel, 'kind': 'regular', 'sha256': digest.hexdigest(),
                     'stat': first, 'path_fd_identity_matched': True, 'metadata_stable_during_hash': True,
                     'read_flags': ['O_RDONLY', 'O_NOFOLLOW', 'O_NOATIME', 'O_CLOEXEC'],
                     'owner_hash_fd_closed': True}
        if rel in SMALL_JSON:
            small[rel] = json.loads(b''.join(payload))
    after = inventory()
    stable_inventory(before, after)
    after_writers = known_instances(instances)
    for p in parents:
        assert invariant(p['stat']) == invariant(metadata(os.lstat(p['path'])))
    gemm = next(x for x in original['PER_START_EVIDENCE.json']['points'] if x['point'] == 'AD_GEMM')
    assert gemm['accepted'] and gemm['attempt_uuid'] == UUID and gemm['cycles'] == 1044499
    joins = []
    for rel, ref in gemm['references'].items():
        assert rows[rel]['sha256'] == ref['sha256'] and rows[rel]['stat']['size'] == ref['bytes'], rel
        joins.append({'path': rel, 'sha256': ref['sha256'], 'bytes': ref['bytes'], 'equal_original_accepted_reference': True})
    for section, rel in [('progress', 'PROGRESS.jsonl'), ('resource', 'RESOURCE_MONITOR.jsonl')]:
        ref = gemm[section]['source_reference']
        assert rows[rel]['sha256'] == ref['sha256'] and rows[rel]['stat']['size'] == ref['bytes'], rel
        joins.append({'path': rel, 'sha256': ref['sha256'], 'bytes': ref['bytes'], 'equal_original_accepted_reference': True})
    for f in prior['files']:
        assert rows[f['name']]['sha256'] == f['sha256']
        assert all(rows[f['name']]['stat'][k] == f[k] for k in ['dev', 'inode', 'size', 'mtime_ns', 'ctime_ns', 'uid', 'gid', 'mode', 'nlink'])
    mapping = small['MAPPING_CLOSURE.json']
    index = mapping['map_payload_index']
    maps = {k: v for k, v in rows.items() if k.startswith('ENGINE/maps/')}
    assert len(maps) == len(index) == mapping['map_payloads'] == 8380
    for name, ref in index.items():
        row = maps['ENGINE/maps/' + name]
        assert row['sha256'] == ref['sha256'] and row['stat']['size'] == ref['bytes'], name
    assert sum(x['stat']['size'] for x in maps.values()) == mapping['map_payload_bytes']
    strict, run, terminal = small['STRICT.json'], small['RUN_START.json'], small['RUN_TERMINAL.json']
    assert strict['scientific_strict_pass'] and strict['performance_accepted'] and strict['cycles'] == 1044499
    assert strict['attempt_uuid'] == run['attempt_uuid'] == UUID
    assert terminal['returncode'] == 0 and terminal['identity_pass'] and terminal['engine']['owned_children_live'] == 0
    groups = collections.defaultdict(list)
    for rel, row in rows.items():
        groups[(row['stat']['dev'], row['stat']['inode'])].append(rel)
    hardlinks = []
    for (dev, ino), members in sorted(groups.items()):
        nlink = rows[members[0]]['stat']['nlink']
        assert nlink >= len(members)
        if nlink > 1:
            hardlinks.append({'dev': dev, 'inode': ino, 'paths': members, 'st_nlink': nlink,
                              'links_outside_tree': nlink - len(members)})
    links = []
    for rel, entry in sorted(before.items()):
        if entry['kind'] != 'symlink':
            continue
        target = entry['target']
        normalized = posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))
        internal = not target.startswith('/') and normalized != '..' and not normalized.startswith('../')
        link = {**entry, 'preserve_as_symlink': True, 'dereferenced_for_copy_or_hash': False,
                'sha256_definition': 'SHA256 of literal readlink bytes, not referent contents',
                'resolved_lexical_relative_path': normalized if internal else None,
                'reference_class': 'INTERNAL_RELATIVE' if internal else 'EXTERNAL_NO_TRAVERSAL',
                'referent_in_manifest': internal and normalized in before}
        if internal and normalized in rows:
            link['referent_sha256'] = rows[normalized]['sha256']
            link['referent_stat'] = rows[normalized]['stat']
        links.append(link)
    directory_rows = [before[k] for k in sorted(before) if before[k]['kind'] == 'directory']
    parts = []
    ordered = [rows[k] for k in sorted(rows)]
    for i in range(0, len(ordered), 512):
        raw = b''.join(canon(x) for x in ordered[i:i + 512])
        parts.append({**write_new(out / ('FILES_%03d.jsonl' % (i // 512)), raw),
                      'records': len(ordered[i:i + 512]),
                      'first_relative_path': ordered[i]['relative_path'],
                      'last_relative_path': ordered[min(i + 511, len(ordered) - 1)]['relative_path']})
    directories_ref = write_new(out / 'DIRECTORIES.jsonl', b''.join(canon(x) for x in directory_rows))
    links_ref = write_new(out / 'LINKS.json', json.dumps({'symlinks': links, 'regular_hardlink_groups': hardlinks,
        'all_regular_files_st_nlink_one': all(x['stat']['nlink'] == 1 for x in ordered),
        'directory_nlink_semantics': 'POSIX dot/parent/subdirectory topology; not duplicate regular-file payloads',
        'hardlink_policy': 'Preserve each recorded in-tree inode equivalence class. Do not traverse or release external aliases.',
        'symlink_policy': 'Copy literal link text as a symlink, preserve topology; never dereference implicitly.'}, indent=2, sort_keys=True).encode() + b'\n')
    writer_ref = write_new(out / 'WRITER_CLOSURE.json', json.dumps({
        'before': before_writers, 'after': after_writers,
        'terminal_reference': next(x for x in joins if x['path'] == 'RUN_TERMINAL.json'),
        'engine_terminal_reference': next(x for x in joins if x['path'] == 'ENGINE/TERMINAL.json'),
        'known_owner_writer_closed': True, 'tree_membership_and_non_atime_stat_stable_before_after_whole_hash_pass': True,
        'original_owner_final_jobs_reference': next(x for x in refs if x['path'].endswith('FINAL_OWNED_JOBS.json')),
        'global_writer_absence_claimed': False}, indent=2, sort_keys=True).encode() + b'\n')
    identity_doc = small['INPUT_RUNTIME_IDENTITY.json']
    refsem = {
        'tree_scope': 'Exactly every entry lexically below source_root, plus root itself; no exclusions, all hidden/empty/nested entries included.',
        'nested_maps': {'directory': 'ENGINE/maps', 'payload_files': len(maps), 'payload_bytes': mapping['map_payload_bytes'],
                        'all_hashes_and_sizes_equal_original_MAPPING_CLOSURE_index': True},
        'historical_snapshot_semantics': 'ENGINE/maps snapshots and engine event records retain historical producer identities and mapped-image references. They are evidence, not live processes or instructions to copy referenced binaries.',
        'absolute_path_semantics': 'Keep all original bytes and paths. Archived copies do not replace original authoritative paths. No JSON/log/path rewriting or automatic traversal of referenced input, config, code, shared libraries or other attempts.',
        'external_dependencies_copied': False, 'external_dependencies_current_bytes_reaudited': False,
        'external_dependency_retention': 'Retain original dependencies and published scientific provenance. This full attempt tree is not a self-contained runnable source/input archive.',
        'execution_reference': {'publication_head': run['publication_head'], 'source_core': run['source_core'],
                                'argv': run['argv'], 'config_copies': run['config_copies'],
                                'producer_binding': small['ACTUAL_PRODUCER_BINDING.json']},
        'recorded_accepted_input_runtime_identity': {k: identity_doc[k] for k in ['core_commit', 'options_sha256', 'trace_list', 'trace_list_sha256', 'runtime_path', 'runtime_sha256', 'runtime_library_path', 'runtime_library_sha256', 'original_framework']},
        'scientific_reference_stage_semantics': 'Intermediate DISPATCH_JOIN_PENDING and embedded pre-acceptance flags remain historical stage records. Final acceptance is bound to the unchanged external owner ACCEPTED_METRICS/PER_START_EVIDENCE and final STRICT; no intermediate artifact is relabeled.',
        'original_accepted_reference_joins': joins, 'original_owner_publications': refs,
        'source_parent_identity_records': parents}
    refs_ref = write_new(out / 'REFERENCE_SEMANTICS.json', json.dumps(refsem, indent=2, sort_keys=True).encode() + b'\n')
    manifest = {
        'schema': 'DTC_L1_BA_FULL_RESULT_TREE_COPY_READY_SOURCE_KEEP_V1', 'status': 'COPY_READY',
        'owner': 'DTC-L1 BA', 'canonical_task': '/root', 'host': socket.gethostname(),
        'independently_issued_by_owner': True, 'not_issued_by_T': True, 'E2_owner_signature': 'NOT_ISSUED_BY_BA',
        'project': 'DTC_L1_AD_GEMM_FULL_RESULT_TREE', 'point': 'AD_GEMM', 'attempt_uuid': UUID,
        'source_root': str(SOURCE), 'started_at_utc': started, 'issued_at_utc': utc(),
        'elapsed_seconds_nonperformance': time.monotonic() - mono,
        'ordinary_files': len(ordered), 'directories_including_root': len(directory_rows), 'symlinks': len(links),
        'special_nodes': 0, 'hardlinked_regular_inode_groups': len(hardlinks),
        'ordinary_file_logical_bytes': read_bytes,
        'ordinary_file_allocated_bytes': sum(x['stat']['allocated_bytes'] for x in ordered),
        'total_tree_allocated_bytes_including_directories': sum(x['stat']['allocated_bytes'] for x in before.values()),
        'symlink_literal_bytes': sum(x['stat']['size'] for x in links),
        'full_file_records': parts, 'directory_records': directories_ref, 'link_records': links_ref,
        'writer_closure': writer_ref, 'reference_semantics': refs_ref,
        'all_regular_files_whole_content_sha256': True, 'each_regular_payload_hashed_once_this_snapshot': True,
        'all_directory_members_recorded': True, 'all_known_owner_writers_closed': True,
        'whole_tree_membership_identity_and_non_atime_metadata_stable_before_after': True,
        'stat_schema': {'mode': 'Full POSIX st_mode including file type', 'permissions_mode': 'stat.S_IMODE(st_mode)',
                        'timestamps': 'Integer nanoseconds, not floating-point seconds',
                        'allocated_bytes': 'st_blocks multiplied by 512; distinct from logical size',
                        'atime': 'Recorded observationally; excluded from identity preservation checks because reads/readlink may update it. No utime restoration is performed.',
                        'birthtime': 'Unavailable from this Linux Python stat interface; not invented'},
        'accepted_state': prior['accepted_state'], 'original_owner_publication': OWNER_HEAD,
        'original_accepted_references_unchanged': True,
        'source_keep': {'required': True, 'source_paths_retained': True, 'source_remains_authoritative': True,
                        'source_released_bytes': 0, 'no_unlink': True, 'no_rename': True, 'no_rewrite': True,
                        'no_truncate': True, 'no_chmod_chown': True, 'no_utime': True, 'no_cleanup_scheduled': True},
        'reader_disposition': {
            'owner_manifest_hash_reader': 'ONE_READ_ONLY_NOATIME_STREAM; ALL_SOURCE_FILE_AND_DIRECTORY_FDS_CLOSED_BEFORE_PUBLICATION',
            'current_owner_scientific_readers': 'TERMINAL; exact registered controller/producer instances absent or retired or PID reused without adoption',
            'planned_owner_source_readers': 'NONE_SCHEDULED; coordinate any later BA raw-tree readers with T before starting',
            'future_T_copy_reader': 'NEW_FULL_TREE_TRANSACTION; single data stream; fresh source verification and target/resource admission by T; SOURCE_KEEP throughout',
            'other_owner_or_unregistered_readers': 'UNKNOWN_NOT_SCANNED; no global quiescence claim',
            'mutating_or_deleting_owner_reader': 'NONE_AUTHORIZED_OR_SCHEDULED'},
        'authorization_scope': 'Manifest publication only. No sidecar start or target allocation/transfer/restore by BA, no source release, no Goal restart/reset, no new simulations or tests.',
        'science_starts': 0, 'scientific_budgets_and_frozen_UUIDs': 'UNCHANGED',
        'old_nine_sidecar_manifests_sufficient_for_this_tree': False,
        'not_an_archive_target_receipt': True, 'transaction_identity': 'To be assigned by T to a fresh full-tree transaction bound to this exact manifest publication; do not reuse prior sidecar txid.'}
    ready_ref = write_new(out / 'COPY_READY_AD_GEMM_FULL_TREE.json', json.dumps(manifest, indent=2, sort_keys=True).encode() + b'\n')
    write_new(evidence / 'SNAPSHOT_RESULT.json', json.dumps({'status': 'PASS_COMPLETE_OWNER_MANIFEST',
        'manifest': ready_ref, 'ordinary_files': len(ordered), 'directories_including_root': len(directory_rows),
        'symlinks': len(links), 'ordinary_file_logical_bytes': read_bytes, 'source_released_bytes': 0}, indent=2).encode() + b'\n')
    print(json.dumps({'status': 'COPY_READY', 'files': len(ordered), 'directories': len(directory_rows),
                      'symlinks': len(links), 'logical_bytes': read_bytes, 'manifest_sha256': ready_ref['sha256']}))


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
