"""Bounded, read-only Lane5 scratch audit; never delete frozen assets."""
import argparse
import os
from pathlib import Path
import subprocess

from registry import Registry, local_resources, now, write_json
from run import digest


def filesystem(path):
    p = Path(path)
    s, v = p.stat(), os.statvfs(p)
    return {'path': str(p), 'realpath': str(p.resolve()), 'device': s.st_dev,
            'inode': s.st_ino, 'free_bytes': v.f_bavail * v.f_frsize}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    out = parser.parse_args().out
    out.mkdir(exist_ok=False)
    reg = Registry()
    with reg.locked() as live:
        before = local_resources()
        policy = live['hosts'][live['authority_host']]
        active = [v for v in live['runs'].values() if v['status'] in ('RUNNING', 'RESERVED')]
        leases = [v for v in live.get('resource_leases', {}).values()
                  if v['status'] in ('RUNNING', 'RESERVED')]
        filesystems = [filesystem(p) for p in
                      ('/workspace', '/workspace/build', '/workspace/results',
                       '/workspace/worktrees', '/tmp', '/root/data', '/root/share', '/dev/shm')]
    workspace_device = filesystems[0]['device']
    candidates = []
    # This list is intentionally limited to own named roots, never all builds.
    roots = list(Path('/workspace/build').glob('*lane5*'))
    roots += list(Path('/tmp').glob('*lane5*'))
    roots += list(Path('/workspace/results/ep_l2_ft20261016').glob('lane5*'))
    for root in sorted(roots):
        if not root.is_dir():
            continue
        for p in sorted(root.rglob('*')):
            if not p.is_file() or p.is_symlink() or p.suffix not in ('.o', '.gcda', '.gcno'):
                continue
            st = p.stat()
            candidates.append({'path': str(p), 'realpath': str(p.resolve()),
                'device': st.st_dev, 'inode': st.st_ino, 'nlink': st.st_nlink,
                'bytes': st.st_size, 'allocated_bytes': st.st_blocks * 512,
                'sha256': digest(p), 'workspace_device': st.st_dev == workspace_device,
                'action': 'PRESERVE_NO_RECOVERY_OF_WORKSPACE_FLOOR',
                'rebuild_source': 'Pinned clock-probe compile commands and source in correction pack; audit references preserved'})
    # Read-only reference, not permission to clean another lane's build.
    reference_builds = []
    for name in ('ep-l2-ft20261016-lane1-v1', 'ep-l2-ft20261016-lane1-r1'):
        p = Path('/workspace/build') / name
        if p.is_dir():
            allocated = int(subprocess.check_output(['du', '-sx', '--block-size=1', str(p)],
                                                    text=True).split()[0])
            reference_builds.append({'path': str(p), 'owner': 'lane1',
                'existing_allocated_bytes': allocated, 'action': 'READ_ONLY_REFERENCE_NO_CLEANUP',
                'scope': 'current full-build footprint, not a measured transient compile peak'})
    with reg.locked():
        after = local_resources()
        report = {'schema_version': 'EPL2_LANE5_RESOURCE_RECOVERY_AUDIT_V1', 'at': now(),
            'authority_commit': 'a41bfb55934303a4d4a342762f74a16d137d0316',
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'resources_before': before, 'resources_after': after, 'policy': policy,
            'filesystems': filesystems, 'active_runs': active, 'active_leases': leases,
            'own_scratch_candidates': candidates, 'reference_builds': reference_builds,
            'own_recoverable_workspace_allocated_bytes': sum(p['allocated_bytes'] for p in candidates if p['workspace_device']),
            'workspace_deficit_bytes': max(0, policy['min_disk_free_bytes'] - after['disk_free_bytes']),
            'physical_bytes_released_by_this_audit': 0, 'mutated_or_deleted_files': [],
            'safe_alternate_filesystem_found': False,
            'status': 'RESOURCE_HOLD_NO_SUFFICIENT_OWN_WORKSPACE_SCRATCH',
            'reason': 'Own probe objects reside on results /root/share filesystem. Removing them cannot restore the different workspace/build filesystem floor. No own large build/tmp root found. Both actual disk filesystems are below 48GiB; shm is only64MiB. Frozen results, unique binaries, audits, traces and other owners remain untouched.',
            'next': 'Recover actual workspace headroom plus measured build increment through owner-authorized nonfrozen scratch elsewhere; retain unchanged48GiB floor. Lane1 alone performs official R0.1 build; no duplicate full compilation.'}
        write_json(out / 'RESOURCE_RECOVERY.json', report)
        write_json(reg.root / 'RESOURCE_RECOVERY_R3.json', report)
    print(report['status'], 'workspace deficit bytes', report['workspace_deficit_bytes'], flush=True)


if __name__ == '__main__':
    main()
