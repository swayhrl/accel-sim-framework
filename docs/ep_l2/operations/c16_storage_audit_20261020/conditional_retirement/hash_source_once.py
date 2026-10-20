#!/usr/bin/env python3
"""One foreground C16 source-hash attempt; never waits for admission or deletes data."""
import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import tempfile
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REGISTRY = Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
RATE = 64 * 1024**2


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, item):
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    with os.fdopen(fd, 'w') as stream:
        json.dump(item, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(name, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def identity(s):
    return dict(dev=s.st_dev, inode=s.st_ino, size=s.st_size, nlink=s.st_nlink,
                mode=stat.S_IMODE(s.st_mode), uid=s.st_uid, gid=s.st_gid,
                mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)


def expected(r):
    return dict(dev=int(r['source_dev']), inode=int(r['source_inode']),
                size=int(r['size_bytes']), nlink=1, mode=int(r['mode_octal'], 8),
                uid=int(r['uid']), gid=int(r['gid']), mtime_ns=int(r['mtime_ns']),
                ctime_ns=int(r['ctime_ns_provenance_only']))


def gate():
    raw = REGISTRY.read_bytes()
    data = json.loads(raw)
    # Exact ACTIVE set in existing ft_lane5/registry.py; no imported controller code.
    active = {'RESERVED', 'RUNNING'}
    runs = [k for k, v in data['runs'].items() if v.get('status') in active]
    leases = [k for k, v in data['resource_leases'].items() if v.get('status') in active]
    controller = data['mechanism_study_20261019_v1']['controller']['state']
    pressure = Path('/proc/pressure/io').read_text()
    avg = {l.split()[0]: float(next(t.split('=')[1] for t in l.split() if t.startswith('avg10=')))
           for l in pressure.splitlines()}
    mem = next(int(l.split()[1]) * 1024 for l in Path('/proc/meminfo').read_text().splitlines()
               if l.startswith('MemAvailable:'))
    v = os.statvfs('/root/share')
    share = v.f_bavail * v.f_frsize
    reasons = []
    override_path = HERE / 'USER_IO_OVERRIDE.json'
    override = json.loads(override_path.read_text()) if override_path.exists() else {}
    allow_competing_io = (override.get('IO10_stop_condition_removed') is True and
                          override.get('active_E2_is_not_a_source_read_veto') is True)
    if leases:
        reasons.append('ACTIVE_PHYSICAL_RESOURCE_LEASE_HOLD')
    if (runs or controller != 'STOPPED') and not allow_competing_io:
        reasons.append('ACTIVE_EP_L2_RUN_LEASE_OR_CONTROLLER_NO_C16_READ_ADMISSION')
    if max(avg['some'], avg['full']) >= 10 and not allow_competing_io:
        reasons.append('CURRENT_HOST_IO10_HOLD')
    if mem < 64 * 1024**3 + 1024**2:
        reasons.append('MEMORY64G_HOLD')
    if share < 40 * 1024**3:
        reasons.append('SHARE40G_HOLD')
    return dict(utc=now(), admitted=not reasons, reasons=reasons,
                io_avg10=avg, original_io_guard=10, active_runs=runs,
                active_resource_leases=leases, controller_state=controller,
                registry_sha256=hashlib.sha256(raw).hexdigest(),
                explicit_user_IO_override=allow_competing_io,
                override_sha256=hashlib.sha256(override_path.read_bytes()).hexdigest() if allow_competing_io else None,
                MemAvailable=mem, Share_available=share, registry_writes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, choices=['P3', 'P2'])
    args = parser.parse_args()
    if socket.gethostname() != 'huangrulin-174' or os.readlink('/proc/self/ns/mnt') != 'mnt:[4026534768]':
        raise SystemExit('Wrong original174 host/mount namespace')
    os.nice(19)  # Caller also uses ionice -c3; no change to another process.
    rows = [r for r in csv.DictReader((BASE / 'RESTORE_MAPPING.tsv').open(), delimiter='\t')
            if r['package'] == args.package]
    assert len(rows) == (2 if args.package == 'P3' else 4)
    output = HERE / (args.package + '_CURRENT_SOURCE_SHA.json')
    receipt = dict(schema='C16_GATED_FOREGROUND_SOURCE_HASH_V1', package=args.package,
                   started_utc=now(), gate_samples=[], files=[], bytes_read=0,
                   rate_cap_Bps=RATE, payload_writer_or_watcher_started=False, source_deletions=0)
    for r in rows:
        receipt['files'].append(dict(path=r['original174_path'], expected_sha256=r['sha256_expected'],
                                     size=int(r['size_bytes']), status='NOT_READ', actual_sha256=None))
    try:
        for r, item in zip(rows, receipt['files']):
            g = gate()
            receipt['gate_samples'].append(g)
            if not g['admitted']:
                receipt['status'] = 'HOLD_BEFORE_PAYLOAD_OPEN'
                receipt['hold_reasons'] = g['reasons']
                break
            path = Path(r['original174_path'])
            assert path.parent.resolve(strict=True) == path.parent, 'Redirected source parent'
            assert stat.S_ISREG(path.lstat().st_mode) and identity(path.lstat()) == expected(r)
            digest, count, start, last_gate = hashlib.sha256(), 0, time.monotonic(), time.monotonic()
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, 'rb') as stream:
                before = os.fstat(stream.fileno())
                assert identity(before) == expected(r)
                item['stat_before'] = identity(before)
                while count < int(r['size_bytes']):
                    if time.monotonic() - last_gate >= 1:
                        g = gate()
                        receipt['gate_samples'].append(g)
                        if not g['admitted']:
                            item['status'] = 'PARTIAL_UNVERIFIED_NO_RESUMABLE_SHA_STATE'
                            raise RuntimeError(','.join(g['reasons']))
                        last_gate = time.monotonic()
                    block = stream.read(min(1024**2, int(r['size_bytes']) - count))
                    assert block, 'Unexpected short source'
                    digest.update(block)
                    count += len(block)
                    receipt['bytes_read'] += len(block)
                    item['bytes_read_so_far'] = count
                    time.sleep(max(0, count / RATE - (time.monotonic() - start)))
                after = os.fstat(stream.fileno())
            item['stat_after'] = identity(after)
            assert identity(before) == identity(after) == identity(path.lstat()) == expected(r)
            assert digest.hexdigest() == r['sha256_expected'], 'Source SHA mismatch'
            item.update(status='CURRENT_FULL_SHA_PASS', actual_sha256=digest.hexdigest(),
                        bytes_hashed=count, completed_utc=now())
            receipt['status'] = 'PARTIAL_PACKAGE_PROGRESS'
            save(output, receipt)
        else:
            receipt['status'] = 'COMPLETE_PACKAGE_SOURCE_SHA_PASS'
    except (AssertionError, OSError, RuntimeError, KeyboardInterrupt) as error:
        receipt['status'] = 'HOLD'
        receipt['hold_reason'] = str(error)
    receipt['completed_utc'] = now()
    save(output, receipt)
    print(json.dumps(dict(package=args.package, status=receipt['status'],
                          bytes_read=receipt['bytes_read'], hold_reasons=receipt.get('hold_reasons', []))))


if __name__ == '__main__':
    main()
