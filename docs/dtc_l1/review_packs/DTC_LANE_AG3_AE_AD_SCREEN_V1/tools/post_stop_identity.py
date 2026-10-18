"""Read-only frozen-file check after STOP; never accepts a failed run."""
from common import *
import sys
sys.path.insert(0,str(PACK/'tools/ag2_requal'))
from mapping_roles import verify_file
from strict_screen import input_identity


def main():
    if json.loads((RAW/'COHORT_TERMINAL.json').read_text())['status']!='STOP':raise ValueError('NOT_STOPPED')
    manifest=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
    pub=json.loads((RAW/'PREREG_PUBLICATION_READBACK.json').read_text())
    assert sha(PACK/'EXECUTABLE_PREREGISTRATION.json')==pub['manifest_sha256']
    operative=[dict(path=path,expected_sha256=h,current_sha256=sha(PACK/path)) for path,h in manifest['files'].items()]
    assert all(r['expected_sha256']==r['current_sha256'] for r in operative)
    runtime={}
    for m in json.loads((PACK/'RUNTIME_MAPPING_MANIFESTS.json').read_text()).values():
        for entry in m['files']:
            actual=verify_file(entry)
            runtime[entry['path']]=dict(path=entry['path'],role=entry['role'],sha256=actual['sha256'],identity=actual['identity'],matches_frozen=True)
    inputs=[]
    for name in manifest['ordered_specs'][:2]:
        spec=json.loads((PACK/name).read_text());inputs.append(dict(workload=spec['workload'],identity=input_identity(spec)))
    assert git(CORE,'rev-parse','HEAD')==manifest['core_commit'] and not git(CORE,'status','--porcelain')
    write(PACK/'POST_STOP_IDENTITY.json',dict(utc=now(),status='PASS_FILES_STILL_FROZEN_NOT_RETROSPECTIVE_GAUSSIAN_PASS',operative_files=operative,runtime_files=list(runtime.values()),inputs=inputs,core=manifest['core_commit'],core_clean=True,manifest_sha256=pub['manifest_sha256'],Gaussian_actual_lifecycle_identity='FAILED_UNCHANGED',Gaussian_performance_accepted=False,simulator_starts_by_check=0))
    print(json.dumps(dict(status='PASS_POST_STOP_FILES_UNCHANGED',operative_files=len(operative),unique_runtime_files=len(runtime),inputs=len(inputs),Gaussian_acceptance_changed=False)))


if __name__=='__main__':main()
