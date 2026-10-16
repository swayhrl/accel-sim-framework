"""Bounded read-only pilot-envelope observation. Never a disk waiter or admission."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import time

from registry import Registry, ACTIVE, local_resources, process_identity


def sample():
    mounts = []
    for name in ('/workspace', '/tmp', '/root/share'):
        p = Path(name)
        v, s = os.statvfs(p), p.stat()
        mounts.append({'path': name, 'device': s.st_dev, 'realpath': str(p.resolve()),
            'block_bytes': v.f_frsize, 'f_blocks': v.f_blocks, 'f_bfree': v.f_bfree,
            'f_bavail': v.f_bavail, 'available_bytes': v.f_bavail * v.f_frsize,
            'free_not_available_bytes': (v.f_bfree - v.f_bavail) * v.f_frsize})
    processes = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            exe, cwd = os.readlink(p/'exe'), os.readlink(p/'cwd')
            command = (p/'cmdline').read_bytes().decode(errors='replace').replace('\0', ' ')
            searchable = (exe + ' ' + cwd + ' ' + command).lower()
            tags = [k for k in ('dtc', 'c16', 'storage', 'archive', 'gate_wait', 'engineering_pilot') if k in searchable]
            if not tags and not any(k in Path(exe).name for k in ('accel-sim.out', 'vvp', 'cc1plus', 'cmake')):
                continue
            io = {k: int(v.strip()) for k,v in (line.split(':',1) for line in (p/'io').read_text().splitlines())}
            processes.append({'process': process_identity(int(p.name)), 'executable': exe,
                'cwd': cwd, 'tags': tags, 'io': io, 'fd_count': len(list((p/'fd').iterdir()))})
        except (OSError, ValueError, ProcessLookupError):
            continue
    small = {}
    for name in ('/proc/pressure/io', '/sys/fs/cgroup/io.stat', '/sys/fs/cgroup/memory.events'):
        try:
            small[name] = Path(name).read_text()
        except OSError:
            small[name] = None
    with Registry().locked() as live:
        active = {'runs': [r for r in live['runs'].values() if r['status'] in ACTIVE],
            'leases': [r for r in live.get('resource_leases', {}).values() if r['status'] in ACTIVE],
            'policy': live['hosts'][live['authority_host']]}
    return {'at': datetime.now(timezone.utc).isoformat(), 'monotonic_seconds': time.monotonic(),
        'resources': local_resources(), 'filesystems': mounts, 'observed_processes': processes,
        'pressure': small, 'central': active}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    points = []
    for n in range(4):
        if n:
            time.sleep(10)
        points.append(sample())
        print('READONLY_SAMPLE', n+1, points[-1]['resources'], flush=True)
    steps = []
    for a,b in zip(points,points[1:]):
        changes = []
        for fa,fb in zip(a['filesystems'],b['filesystems']):
            changes.append({'path': fa['path'], 'available_byte_decrease': fa['available_bytes']-fb['available_bytes'],
                'devices_unchanged': fa['device']==fb['device']})
        before = {(r['process']['pid'],r['process']['start_ticks']):r for r in a['observed_processes']}
        io = []
        for row in b['observed_processes']:
            old = before.get((row['process']['pid'],row['process']['start_ticks']))
            if old:
                io.append({'process': row['process'], 'tags': row['tags'],
                    'write_bytes_delta': row['io']['write_bytes']-old['io']['write_bytes'],
                    'wchar_delta': row['io']['wchar']-old['io']['wchar']})
        steps.append({'seconds': b['monotonic_seconds']-a['monotonic_seconds'], 'filesystems': changes, 'observed_process_io_deltas': io})
    report = {'kind': 'BOUNDED_READONLY_OBSERVATION_NOT_A_FUTURE_WRITE_BOUND',
        'host': socket.gethostname(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'mount_namespace': os.readlink('/proc/self/ns/mnt'),
        'source': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'samples': points, 'intervals': steps,
        'limits': '30-second sample cannot bound later external bursts, compiler/linker growth or monitor/kill overshoot. f_bfree-f_bavail is not usable capacity. No admission or source cleanup performed.'}
    (args.out/'RESOURCE_OBSERVATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('BOUNDED_OBSERVATION_FINISHED', flush=True)


if __name__ == '__main__':
    main()
