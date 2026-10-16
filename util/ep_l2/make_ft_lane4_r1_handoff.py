#!/usr/bin/env python3
"""Replay the frozen minimal patch in a private index; preserve R0 and prior evidence."""
import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
REVIEW='aec01450d3c527524ee09ee59242f582fafe5354'
R0='126394be46b15f55b9756d43eb9ca9a9baae1c84'
CANDIDATE='b8b3d55b392fcff793d0aec684bddb73ba3065a9'
R0_BINARY=Path('/workspace/results/ep_l2_ft20261016/lane1/binaries/release-126394be.out')
R0_SHA='0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698'
PRIOR=ROOT/'docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2'
OFF=ROOT/'docs/ep_l2/review_packs/FT20261016_LANE4_OFF_EQUIVALENCE_r1'


def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def git(root,*args,env=None):
    return subprocess.check_output(['git','-C',str(root),*args],text=True,env=env).strip()


def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def stat(p):
    s=p.stat();return dict(inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,mode=s.st_mode)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--test-log',type=Path,required=True);a=p.parse_args()
    assert git(a.core,'rev-parse','HEAD')==CANDIDATE
    assert not git(a.core,'status','--porcelain')
    assert not git(ROOT,'status','--porcelain','--untracked-files=no','--','util/ep_l2')
    a.out.mkdir(parents=True,exist_ok=False)
    producer=git(ROOT,'rev-parse','HEAD');before=stat(R0_BINARY)
    assert digest(R0_BINARY)==R0_SHA
    source_patch=PRIOR/'CORE_MINIMAL.patch';patch=a.out/'CORE_MINIMAL.patch'
    shutil.copyfile(source_patch,patch)
    # Git's common source tree and ordinary index/worktree are not modified.
    with tempfile.TemporaryDirectory(prefix='ep-l2-lane4-r1-index-') as tmp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        git(a.core,'read-tree',R0,env=env)
        git(a.core,'apply','--cached','--check',str(patch.resolve()),env=env)
        git(a.core,'apply','--cached',str(patch.resolve()),env=env)
        replay=git(a.core,'write-tree',env=env)
    expected=git(a.core,'rev-parse',CANDIDATE+'^{tree}');assert replay==expected
    assert not git(a.core,'status','--porcelain')
    write(a.out/'PATCH_REPLAY.json',dict(status='PASS',parent_core=R0,candidate_core=CANDIDATE,
        patch_sha256=digest(patch),unchanged_from_r2=digest(patch)==digest(source_patch),
        replay_tree=replay,candidate_tree=expected,complete_tree_equal=True,
        method='git read-tree R0; git apply --cached --check; git apply --cached; git write-tree in a private temporary index',
        producing_tool_commit=producer,core_worktree_unchanged=True))
    dependencies=[]
    for lane in (1,5):
        ref=f'origin/hrl/ep-l2-ft20261016-lane{lane}-v1';head=git(ROOT,'rev-parse',ref)
        rel=f'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane{lane}/RECEIPT.json'
        raw=subprocess.check_output(['git','-C',str(ROOT),'show',head+':'+rel])
        dest=a.out/f'LANE{lane}_RECEIPT_SNAPSHOT.json';dest.write_bytes(raw)
        dependencies.append(dict(lane_id=lane,publication_commit=head,receipt_path=rel,receipt_sha256=digest(dest)))
    write(a.out/'DEPENDENCIES.json',dependencies)
    for old in [PRIOR,OFF]:
        subprocess.run(['sha256sum','-c','--quiet','SHA256SUMS'],cwd=old,check=True)
    counts=json.loads((PRIOR/'VALIDATION_COUNTS.json').read_text())
    assert len(counts['cpp_invocations'])==12
    write(a.out/'REUSED_EVIDENCE.json',dict(publication='96fbcb612773900fd75268ffe4e00ed9f13d3d42',
        packs=[dict(path=str(x.relative_to(ROOT)),checksums_sha256=digest(x/'SHA256SUMS')) for x in [PRIOR,OFF]],
        prior_cpp_invocations=12,prior_illegal_cli_rejections=6,prior_parser_tests=16,
        prior_full_application_runs=3,reexecuted_old_application_runs=0))
    candidate=json.loads((PRIOR/'BUILD_MANIFEST.json').read_text())
    assert digest(candidate['binary'])==candidate['binary_sha256']
    write(a.out/'R1_INTEGRATION_CONTRACT.json',dict(continuation_commit=REVIEW,
        original_scientific_contract='6c136e2a56a008695f8c8b815723bf8f1a760db9',
        status='PATCH_REPLAY_VERIFIED_R1_COMMON_RELEASE_PENDING',integration_owner='lane1',qualification_owner='lane5',
        r0=dict(core_source_commit=R0,framework_source_commit='37dec04d223ae65167c5584e56887c74f6540d27',
                binary_sha256=R0_SHA,role='R0_B16_U_WB16_MAIN_EXPERIMENT_PROCEEDS_INDEPENDENTLY'),
        candidate=candidate,patch_sha256=digest(patch),patch_parent=R0,
        actual_lane1_R1_release=None,actual_R1_qualified_release=None,
        common_R1_matched_baseline_specs=None,
        qualification_scope='R1 normal gates plus each requested ideal mode; no dependency on other ideal modes',
        ideal_gates_contract=dict(location='Lane5 normalized R1 qualified release: ideal_gates[mode]',
            fields=['status=PASS','production_driven=true','ideal_vector','evidence_path','evidence_sha256'],
            mode_keys=['I_WB','I_META','I_READ_HIT','I_WB_META'],R0_requires_ideal_gates=False),
        R1_variant_invariants=['same Core/Framework/binary/trace/workload/epoch/features/environment and baseline configs',
            'only one appended three-ideal-bit overlay','qualification envelope SHA frozen at prepare',
            'per-mode independent production evidence hash checked','matched baseline run key retained',
            'derived runtime config hash recomputed before execution'],
        no_R0_binary_rebuild=True,no_R0_result_used_as_matched_R1_numerator=True))
    fields=['family','workload','mode','owner','status','cycles','instructions','core_source_commit',
            'framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','run_key','matched_baseline_key']
    with (a.out/'R1_CEILING_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for workload in ['convolutionSeparable','FWT_7_21','vectorAdd_4M','sad']:
            for mode in ['B16_BANKED','I_WB','I_META','I_READ_HIT']+(['I_WB_META'] if workload in ['convolutionSeparable','FWT_7_21'] else []):
                w.writerow(dict(family='R1_B16_MATCHED_DIAGNOSTIC',workload=workload,mode=mode,
                    owner='lane5' if mode=='B16_BANKED' else 'lane4',status='NOT_RUN_R1_RELEASE_QUALIFICATION_AND_MATCHED_SPEC_PENDING'))
    assert 'Ran 19 tests' in a.test_log.read_text() and a.test_log.read_text().rstrip().endswith('OK')
    shutil.copyfile(a.test_log,a.out/'R1_BINDING_TESTS.log')
    client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    assert digest(client['registry_client'])==client['registry_client_sha256']
    sys.path.insert(0,str(Path(client['registry_client']).parent))
    from registry import Registry
    snapshot=Registry(client['canonical_root']).snapshot()
    active=[dict(r,run_key=k) for k,r in snapshot['runs'].items() if r['status'] in ['RUNNING','RESERVED']]
    own=[r for r in active if r['owner']=='lane4'];assert not own
    history=[dict(run_key=k,status=r['status'],identity=r['identity']) for k,r in snapshot['runs'].items() if r['owner']=='lane4']
    assert len(history)==3 and all(r['status']=='COMPLETE_VALID' for r in history)
    write(a.out/'REGISTRY_CHECK.json',dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        registry_updated_at=snapshot['updated_at'],client=client,active_runs_all_lanes=active,active_lane4_runs=own,
        retained_lane4_history=history,new_simulations_launched=0,new_build_leases=0,
        active_resource_leases=[r for r in snapshot['resource_leases'].values() if r['status']!='RELEASED']))
    assert before==stat(R0_BINARY) and digest(R0_BINARY)==R0_SHA
    write(a.out/'R0_PROTECTION.json',dict(status='PASS',binary=str(R0_BINARY),binary_sha256=R0_SHA,
        stat_before=before,stat_after=stat(R0_BINARY),content_and_file_identity_unchanged=True,
        writes_to_R0_binary=0,builds=0,simulations=0,R0_requires_Lane4=False))
    (a.out/'README.md').write_text('''# Lane 4 review_r2 continuation: R1 integration delivery

R0 production qualification and B16/U_WB16 main experiments belong to Lane5
and proceed without ideals, TVD or RO. Nothing in this pack requires a new
R0 binary. The immutable R0 content and file identity are verified unchanged.

CORE_MINIMAL.patch is the previously reviewed r2 patch against exact Core
126394be. PATCH_REPLAY.json proves a fresh private-index replay produces the
entire b8b3d55b candidate tree. No normal index or worktree was altered. Lane1
can apply this exact patch to a separate R1 integration worktree, freeze its
actual new source/binary identity, and send R1 to Lane5 for independent gates.
The existing candidate binary is offered as evidence, not a Lane1 R1 release.

R1_INTEGRATION_CONTRACT.json specifies the runner interface. Lane5 owns its
qualified release and B16 baseline specs. The per-mode ideal_gates entry is
R1-only metadata recording the already required independent mode validation;
only the requested mode needs qualification. R0 normal qualification needs no
ideal flags/gates. The adapter binds the qualification bytes, recomputes the
derived config hash, rejects mixed R0/R1 source/binary/trace/epoch, and records
the exact matched baseline key. The 19 new tests use synthetic non-executable
files and establish validation behavior only, never qualification/performance.

Prior audit, 12 production C++ invocations, six illegal configurations,
16 parser tests, and three complete legacy applications are reused, not rerun.
R1_CEILING_RESULTS.csv has 18 explicitly unrun cells with blank metrics and
identities. No old 1.721x result is inserted. Actual Lane1 common R1 release,
Lane5 independent mode qualification and same-binary B16 specs are pending.
Future per-cell results will be published as they complete, preserving the
first-wave four workloads and convolution/FWT-only I_WB_META combinations.
''')
    (a.out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(a.out)}\n' for p in sorted(a.out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
    print(json.dumps(dict(pack=str(a.out),patch_replay='PASS',tree=replay,
        R0_unchanged=True,new_binding_tests_pass=19,new_simulations=0,active_lane4_runs=0)))


if __name__=='__main__':main()
