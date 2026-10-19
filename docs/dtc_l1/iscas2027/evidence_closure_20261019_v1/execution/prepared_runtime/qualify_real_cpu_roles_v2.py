"""One source-bound foreground CPU role cohort. No simulator entry or retry."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent
FW=HERE.parents[5]
CPU_OUTPUT=Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator/cpu-qualification')
ENV={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['/usr/bin/git','-C',str(FW),*args],env=ENV,text=True).strip()
def write(path,value):
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')
def main():
    if list(sys.argv)!=[str(HERE/'qualify_real_cpu_roles_v2.py')] or dict(os.environ)!=ENV:
        raise ValueError('EXACT_SOURCE_BOUND_CPU_MANAGER_ENTRY_AND_ENV_REQUIRED')
    registration_path=HERE.parent/'CPU_ROLE_MANAGER_REGISTRATION_V2.json'
    registration=json.loads(registration_path.read_text())
    raw=Path(registration['manager_output']).resolve().parent
    if (raw.parent!=CPU_OUTPUT or not raw.name.startswith('real-external-roles-v2') or
            Path(registration['manager_output']).resolve()!=raw/'manager'):
        raise ValueError('FIXED_ISOLATED_CPU_ROLE_COHORT_REQUIRED')
    publication_path=raw.parent/(raw.name+'-prereg')/'PUBLICATION_READBACK.json'
    publication=json.loads(publication_path.read_text())
    head=publication['head']
    if publication['fetched_head']!=head or git('rev-parse','refs/dtc-closure-readback/cpu-role-manager-v2')!=head:
        raise ValueError('EXACT_REMOTE_READBACK_REQUIRED')
    if git('status','--porcelain') or git('rev-parse','HEAD')!=head:
        raise ValueError('PREREGISTERED_CLEAN_MANAGER_SOURCE_REQUIRED')
    for rel,binding in publication['files'].items():
        if sha(FW/rel)!=binding['sha256'] or git('rev-parse',head+':'+rel)!=binding['blob']:
            raise ValueError('PUBLISHED_MANAGER_SOURCE_OR_ARTIFACT_CHANGED:'+rel)
    role_path=HERE.parent/'CPU_ROLE_MANAGER_ROLE_V2.json'
    release_path=HERE.parent/'CPU_ROLE_MANAGER_RELEASE_V2.json'
    policy_path=HERE.parent/'CPU_ROLE_MANAGER_POLICY_V2.json'
    contract_path=HERE/'EXACT_EXTERNAL_ROLE_CONTRACTS.json'
    def published_sha(path):
        return publication['files'][str(path.relative_to(FW))]['sha256']
    role=json.loads(role_path.read_text())
    role_sha=hashlib.sha256(json.dumps(role,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    trust=dict(release_sha256=published_sha(release_path),
               role_contract_sha256=published_sha(contract_path),
               admission_policy_sha256=published_sha(policy_path),manager_role_sha256=role_sha)
    raw.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(HERE/'vendor'));sys.path.insert(0,str(HERE))
    from ownership import identity
    from external_cpu_role_manager import run_exact_cpu_roles
    own=dict(identity(os.getpid()),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
    write(raw/'ENTRY_START.json',dict(utc=datetime.now(timezone.utc).isoformat(),entry=own,publication_head=head,registration_sha256=published_sha(registration_path),simulator_starts=0))
    report=None;error=None
    try:
        report=run_exact_cpu_roles(registration_path,published_sha(registration_path),trusted_hashes=trust,manager_role=role)
    except BaseException as failure:
        error=repr(failure)
    finally:
        write(raw/'ENTRY_TERMINAL.json',dict(utc=datetime.now(timezone.utc).isoformat(),error=error,report=report,simulator_starts=0,no_background_retry=True))
    print(json.dumps(dict(error=error,status=report['status'] if report else 'STOP_CPU_MANAGER_ENTRY',output=str(raw))),flush=True)
    return 0 if error is None and report and report['status']=='PASS_PER_ROLE_CPU_OBSERVATIONS_ONLY' else 3
if __name__=='__main__':sys.exit(main())
