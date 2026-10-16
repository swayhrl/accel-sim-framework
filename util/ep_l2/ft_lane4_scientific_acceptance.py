"""Lane4 launch/intake veto from the latest published Lane5 scientific authority.

Execution terminals stay immutable. No old qualification snapshot can override
review_r3 withdrawal or a newer explicit suspension. This module never qualifies
a release and never modifies Lane5 files, registry rows or preserved runs.
"""
import hashlib
import json
from pathlib import Path
import subprocess

REVIEW='a41bfb55934303a4d4a342762f74a16d137d0316'
PREFIX='docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/'
REF='origin/hrl/ep-l2-ft20261016-lane5-v1'
# Fixed source/binary identities cannot acquire a source repair retroactively.
WITHDRAWN_CORES={
 '126394be46b15f55b9756d43eb9ca9a9baae1c84',
 'be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de',
 'b8b3d55b392fcff793d0aec684bddb73ba3065a9'}
WITHDRAWN_BINARIES={
 '0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698',
 '2d2fb08217723bf920a486dcdce3412ca03c4a14028c9d67b401fd9b8a6d4664',
 '63f26de29e2b1932062934044cb3131fa5e2d36fa9821094939188bceb66a8ea'}
REPAIR_GATES={'physical_bank_clock','memcpy_payload_identity'}
IDENTITY_FIELDS=('core_source_commit','framework_source_commit','binary_sha256',
                 'runtime_config_sha256','trace_content_sha256','workload')


def check(ok,detail):
    if not ok:raise ValueError(detail)


def sha(data):return hashlib.sha256(data).hexdigest()


def load_authority(root, client, qualified_release=None):
    """One bounded read-only fetch per prepare/launch/final check; no polling."""
    root=Path(root)
    subprocess.run(['git','-C',str(root),'fetch','origin','hrl/ep-l2-ft20261016-lane5-v1'],
                   check=True,capture_output=True,timeout=45)
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse',REF],text=True).strip()
    def blob(rel):
        return subprocess.check_output(['git','-C',str(root),'show',commit+':'+rel])
    records={};hashes={}
    for name in ['APPLICATION_ACCEPTANCE.json','SCIENTIFIC_HOLD.json']:
        raw=blob(PREFIX+name);records[name]=json.loads(raw);hashes[name]=sha(raw)
    # R1.1's actual normalized envelope must itself be published by Lane5,
    # not merely an old certificate copied to an arbitrary local path.
    release_bytes=None;release_relative=None
    if qualified_release is not None:
        # Resolve the repository via Git rather than assuming directory depth.
        lane5_root=Path(subprocess.check_output(['git','-C',client['qualification_directory'],
                                               'rev-parse','--show-toplevel'],text=True).strip())
        path=Path(qualified_release).resolve()
        check(path.is_relative_to(lane5_root),'qualified release is not a published Lane5 path')
        release_relative=str(path.relative_to(lane5_root));release_bytes=blob(release_relative)
        check(sha(path.read_bytes())==sha(release_bytes),'local qualification differs from latest Lane5 publication')
    return dict(publication_commit=commit,records=records,sha256=hashes,
                qualified_release_relative=release_relative,qualified_release_bytes=release_bytes)


def check_not_withdrawn(identity,authority):
    check(identity['core_source_commit'] not in WITHDRAWN_CORES and
          identity['binary_sha256'] not in WITHDRAWN_BINARIES,
          'review_r3: old R0/R1/candidate application qualification is withdrawn')
    for row in authority['records']['APPLICATION_ACCEPTANCE.json'].get('rows',[]):
        state=row.get('scientific_acceptance','')
        if state.startswith(('SUSPENDED','RETRACTED','WITHDRAWN')) and (
           row.get('core_source_commit')==identity['core_source_commit'] or
           row.get('binary_sha256')==identity['binary_sha256']):
            check(False,'latest Lane5 authority suspends this source/binary')


def check_release_current(spec,authority,digest):
    identity=spec['identity'];check_not_withdrawn(identity,authority)
    raw=authority.get('qualified_release_bytes')
    check(raw is not None,'missing published R1.1 qualification bytes')
    release=json.loads(raw)
    check(release.get('status')=='INDEPENDENTLY_QUALIFIED' and
          release.get('qualified_by')=='lane5' and release.get('evidence_kind')=='PRODUCTION_DRIVEN',
          'latest Lane5 R1.1 release is not independently qualified')
    for key in IDENTITY_FIELDS[:3]:check(release.get(key)==identity[key],'published repaired release identity mismatch: '+key)
    check(sha(raw)==digest(spec['qualified_release']),'published qualification hash mismatch')
    for name in REPAIR_GATES:
        gate=release.get('gates',{}).get(name,{})
        check(gate.get('status')=='PASS' and gate.get('production_driven') is True,
              'missing production repair gate: '+name)
        check(digest(gate['evidence_path'])==gate['evidence_sha256'],'repair evidence changed: '+name)
    return dict(publication_commit=authority['publication_commit'],authority_sha256=authority['sha256'],
                qualified_release_sha256=sha(raw),published_qualified_release=authority['qualified_release_relative'],
                current_release_eligibility='PASS_NOT_A_RUN_ACCEPTANCE',review_commit=REVIEW)


def check_result_current(result,authority,run_key):
    """For an already executed row; absent/current-mismatched acceptance rejects."""
    identity=result['identity'];check(result['run_key']==run_key(identity),'run-key/identity mismatch')
    check_not_withdrawn(identity,authority)
    check(result.get('status')=='COMPLETE_VALID','execution was not complete')
    rows=[r for r in authority['records']['APPLICATION_ACCEPTANCE.json'].get('rows',[])
          if r.get('run_key')==result['run_key']]
    check(len(rows)==1,'missing/ambiguous latest run acceptance')
    row=rows[0];check(row.get('scientific_acceptance')=='CURRENT_ACCEPTED','run scientific acceptance is suspended/not current')
    for name in IDENTITY_FIELDS:check(row.get(name)==identity[name],'acceptance identity mismatch: '+name)
    raw=result.get('raw_log_sha256')
    check(isinstance(raw,str) and len(raw)==64 and all(c in '0123456789abcdef' for c in raw), 'missing valid raw log hash')
    check(row.get('raw_log_sha256')==raw,'acceptance raw hash mismatch')
    return dict(status='CURRENT_ACCEPTED',publication_commit=authority['publication_commit'],
                application_acceptance_sha256=authority['sha256']['APPLICATION_ACCEPTANCE.json'])
