#!/usr/bin/env python3
"""Bounded exact C16 package unlink, with pinned readiness and durable INTENT/DONE.

Reuses the fd-relative/no-symlink identity and fsynced journal method of existing
storageops release_polybench_closeout_r13.py. Default is metadata preflight only.
"""
import argparse
import csv
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import time

HERE = Path(__file__).resolve().parent
BRIDGE = Path('/root/share/c16_storage_audit_restore_20261020_v1')
JOURNAL = BRIDGE / 'SOURCE_RELEASE_JOURNAL.jsonl'
REPO_PATH = 'docs/ep_l2/operations/c16_storage_audit_20261020/conditional_retirement/PRE_RELEASE_ELIGIBILITY.json'


def require(ok, text):
    if not ok:
        raise RuntimeError(text)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def capacity():
    v = os.statvfs('/workspace')
    return dict(available_bytes=v.f_bavail * v.f_frsize,
                df_B1=subprocess.check_output(['df', '-B1', '-P', '/workspace'], text=True))


def append(event):
    event = dict(utc=now(), **event)
    fd = os.open(JOURNAL, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        payload = (json.dumps(event, sort_keys=True) + '\n').encode()
        require(os.write(fd, payload) == len(payload), 'Short durable journal write')
        os.fsync(fd)
    finally:
        os.close(fd)
    fd = os.open(BRIDGE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def open_parent(path):
    p = Path(path)
    require(p.is_absolute() and str(p).startswith('/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_') and '..' not in p.parts, 'Out of exact outbound scope')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in p.parent.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def check_file(fd, row):
    s = os.stat(Path(row['path']).name, dir_fd=fd, follow_symlinks=False)
    wanted = row['identity']
    actual = dict(dev=s.st_dev, inode=s.st_ino, size=s.st_size, nlink=s.st_nlink,
                  uid=s.st_uid, gid=s.st_gid, mode=stat.S_IMODE(s.st_mode),
                  mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns,
                  allocated_bytes=s.st_blocks * 512)
    require(stat.S_ISREG(s.st_mode) and actual == wanted, 'Exact identity changed: ' + row['path'])


def current_refs(rows):
    names = {r['path'] for r in rows}
    identities = {(r['identity']['dev'], r['identity']['inode']) for r in rows}
    hits = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            command = (p / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if any(n in command for n in names):
                hits.append(dict(pid=p.name, reason='exact path argv'))
            for f in (p / 'fd').iterdir():
                try:
                    s = f.stat()
                    if (s.st_dev, s.st_ino) in identities:
                        hits.append(dict(pid=p.name, fd=f.name, reason='exact file fd'))
                except (FileNotFoundError, ProcessLookupError):
                    pass
        except (FileNotFoundError, ProcessLookupError):
            pass
    require(not hits, 'Live exact-path reader: ' + json.dumps(hits))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', choices=['P3', 'P2'], required=True)
    ap.add_argument('--proof-commit', required=True)
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    require(socket.gethostname() == 'huangrulin-174' and os.readlink('/proc/self/ns/mnt') == 'mnt:[4026534768]', 'Wrong source namespace')
    require(len(args.proof_commit) == 40 and all(x in '0123456789abcdef' for x in args.proof_commit), 'Invalid pinned proof commit')
    local = (HERE / 'PRE_RELEASE_ELIGIBILITY.json').read_bytes()
    remote = subprocess.check_output(['gh', 'api', 'repos/swayhrl/accel-sim-framework/contents/' + REPO_PATH + '?ref=' + args.proof_commit,
                                      '-H', 'Accept: application/vnd.github.raw+json'])
    require(remote == local, 'GitHub readiness proof differs')
    proof = json.loads(local)
    require(proof['user_conditional_authority'] is True and proof['historical_A_G_signature_claimed'] is False, 'Authority scope mismatch')
    require(proof['restore_route_verified'] is True and proof['future_duties_taken_over'] is True, 'Recovery or duty gate incomplete')
    require(proof['target_current_full_SHA_count'] == 6 and proof['source_current_full_SHA_count'] == 6, 'Six-file identity proof incomplete')
    package = proof['packages'][args.package]
    require(package['ready'] is True, 'Package HOLD')
    rows = package['files']
    require(len(rows) == (2 if args.package == 'P3' else 4) and len({r['path'] for r in rows}) == len(rows), 'Wrong package selector')
    mapping_bytes = (HERE.parent / 'RESTORE_MAPPING.tsv').read_bytes()
    require(hashlib.sha256(mapping_bytes).hexdigest() == '0a5dd6177837b18e0928327110c3eaaac60fa994690c3c3d40e382c6ba251234', 'Frozen six-file mapping changed')
    frozen = {r['original174_path']: r for r in csv.DictReader(mapping_bytes.decode().splitlines(), delimiter='\t') if r['package'] == args.package}
    require(set(frozen) == {r['path'] for r in rows}, 'Selector differs from the frozen exact package')
    for r in rows:
        require(r['source_sha256'] == r['target_sha256'] == r['frozen_sha256'] == frozen[r['path']]['sha256_expected'], 'Source/target/frozen SHA mismatch')
    require(hashlib.sha256((HERE.parent / 'RESTORE.sh').read_bytes()).hexdigest() == proof['restore_script_sha256'], 'Restore program changed')
    require(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == proof['release_script_sha256'], 'Release program changed')
    current_refs(rows)
    # Full metadata pass before the first unlink; preserve every nonselector file.
    for row in rows:
        fd = open_parent(row['path'])
        try:
            check_file(fd, row)
        finally:
            os.close(fd)
    require(len(proof['controls_126']) == 126, 'Protected control inventory incomplete')
    for control in proof['controls_126']:
        require(hashlib.sha256(Path(control['path']).read_bytes()).hexdigest() == control['sha256'], 'Protected control changed')
    if not args.execute:
        print(json.dumps(dict(status='EXACT_PACKAGE_METADATA_PREFLIGHT_PASS', package=args.package, files=len(rows))))
        return
    lock = os.open(BRIDGE / 'SOURCE_RELEASE.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        prior = [json.loads(l) for l in JOURNAL.read_text().splitlines()] if JOURNAL.exists() else []
        require(not any(e.get('event') == 'PACKAGE_DONE' and e.get('package') == args.package for e in prior), 'Package already done')
        if args.package == 'P2':
            require(any(e.get('event') == 'PACKAGE_DONE' and e.get('package') == 'P3' for e in prior), 'P3 must sign off before P2')
        before = capacity()
        append(dict(event='PACKAGE_INTENT', package=args.package, proof_commit=args.proof_commit,
                    target_commit=proof['target_commit'], files=[r['path'] for r in rows], capacity_before=before))
        started = time.monotonic()
        for row in rows:
            require(time.monotonic() - started < 30, 'Bounded package source-operation time exceeded; stop with registered INTENT')
            current_refs(rows)
            fd = open_parent(row['path'])
            try:
                check_file(fd, row)
                append(dict(event='INTENT', package=args.package, file=row, proof_commit=args.proof_commit))
                check_file(fd, row)
                os.unlink(Path(row['path']).name, dir_fd=fd)
                os.fsync(fd)
                append(dict(event='DONE', package=args.package, path=row['path'],
                            source_sha256=row['source_sha256'], identity=row['identity']))
            finally:
                os.close(fd)
        after = capacity()
        result = dict(event='PACKAGE_DONE', package=args.package, paths=[r['path'] for r in rows],
                      files=len(rows), logical_bytes=sum(r['identity']['size'] for r in rows),
                      allocated_bytes=sum(r['identity']['allocated_bytes'] for r in rows),
                      capacity_before=before, capacity_after=after,
                      observed_df_net_growth_bytes=after['available_bytes'] - before['available_bytes'],
                      concurrent_other_work=True)
        append(result)
        print(json.dumps(result))
    finally:
        os.close(lock)


if __name__ == '__main__':
    main()
