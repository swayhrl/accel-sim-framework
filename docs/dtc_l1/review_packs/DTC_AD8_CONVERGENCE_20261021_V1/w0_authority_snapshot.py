"""One W0 read-only current authority snapshot; no launch or lock authority."""
import hashlib
import json
import os
from pathlib import Path
import sys

PACK = Path(__file__).resolve().parent
E = Path('/workspace/dtc-ag8-ad-convergence-174-v1/evidence')
GATE = E/'w0_frozen_authority'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sys.argv == [str(PACK/'w0_authority_snapshot.py')]
    assert Path.cwd() == PACK.parents[3]
    proof=json.loads((E/'W0_SOURCE_BINDING.json').read_text())
    sources={r['path']:r['sha256'] for r in proof}
    sources[str(PACK/'w0_authority_snapshot.py')]=sha(PACK/'w0_authority_snapshot.py')
    for path,digest in sources.items():
        assert sha(path)==digest
    role=dict(name='AG8_W0_READONLY_AUTHORITY_ONLY_NO_DISPATCH',
        argvs=[[sys.executable,'-I','-B',str(PACK/'w0_authority_snapshot.py')]],
        cwd=str(Path.cwd()),executable=sys.executable,
        executable_sha256=sha(sys.executable),source_sha256=sources)
    sys.path[:0]=[str(GATE/'vendor'),str(GATE)]
    from cpu_admission_v2 import CPUAdmission
    # Only sample(), never admit(), run_guarded(), launch, lock or signals.
    snapshot=CPUAdmission(dict(admission=dict(disk_floor_exclusive_bytes=5*1024**3)),[role]).sample()
    with (E/'W0_CURRENT_AUTHORITY_RAW.json').open('x') as f:
        f.write(json.dumps(dict(snapshot=snapshot,role=role),indent=2)+'\n')
    a=snapshot['authority']
    summary=dict(status=a['status'],utc=snapshot['utc'],monotonic_ns=snapshot['monotonic_ns'],
        host=snapshot['host'],uid=snapshot['uid'],own_pid=os.getpid(),
        own_role_observed=any(r['role']==role['name'] and r['pid']==os.getpid()
                              for r in a.get('exact_external_CPU_controls',[])),
        checks=a['checks'],unknown_controls_count=len(a['unknown_controls']),
        active_own_AG_simulator_instances=a['own_AG_processes'],
        foreign_project_resources_counted=len(a['foreign_projects']),
        exact_current_role_is_readonly=True,fullsim_dispatch_permission=False,
        BA_dispatcher_identity_not_inferred_from_uid=True,
        role=role,raw_local_only=str(E/'W0_CURRENT_AUTHORITY_RAW.json'))
    (PACK/'W0_CURRENT_AUTHORITY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='role'}))


if __name__=='__main__':
    main()
