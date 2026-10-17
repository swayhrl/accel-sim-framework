"""Classify a source-identified unrelated project without weakening resource limits."""
from common import resource_snapshot as original_snapshot, sha
from pathlib import Path

_audited = {}
EP_ROOT = '/workspace/results/ep_l2_ft20261016/'
EP_BINARY = '23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee'


def unrelated_ep_l2(item):
    argv=item['argv']
    if not argv or not argv[0].startswith(EP_ROOT) or not argv[0].endswith('/accel-sim.out'):
        return False
    binary=Path(argv[0])
    identity=(str(binary),binary.stat().st_ino,binary.stat().st_mtime_ns)
    if identity not in _audited:
        configs=list(binary.parent.glob('config-*.config'))
        text='\n'.join(p.read_text() for p in configs)
        _audited[identity]=(sha(binary)==EP_BINARY and '-gpgpu_ep_l2_ft_mode ' in text
                            and not any(line.startswith('-gpgpu_dtc') for line in text.splitlines()))
    return _audited[identity]


def resource_snapshot():
    snapshot=original_snapshot()
    unrelated=[p for p in snapshot['processes'] if unrelated_ep_l2(p)]
    snapshot['unrelated_project_processes']=unrelated
    snapshot['processes']=[p for p in snapshot['processes'] if not unrelated_ep_l2(p)]
    snapshot['authority_scope']='DTC or unknown simulators/authorities; fingerprinted EP_L2_FT is separate'
    snapshot['resource_scope']='ALL projects still contribute to unchanged host/cgroup memory, swap, disk and pressure limits'
    return snapshot
