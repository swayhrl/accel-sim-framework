"""Canonical BA/root two-phase AG7 controller. NO automatic restart or canary.

Actual execution is authorized only through the exact remotely frozen authority
registration SHA in argv. All simulator starts go through the unchanged owned
ptrace guard, the paid four-point AG7 ledger and real strict closure. This entry
never creates UUIDs. The canonical root publishes them only after the gate receipt.
"""
from fractions import Fraction
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time

PACK = Path(__file__).resolve().parent
REPO = PACK.parents[3]
ROOT = Path('/workspace/dtc-ag8r1-finite-resume-174-v1')
E = ROOT/'evidence/io_warning_route_repair'
G = ROOT/'evidence/w0_frozen_authority'
REG = PACK/'IO_WARNING_AUTHORITY_REGISTRATION.json'
MANIFEST = PACK/'IO_WARNING_RESERVATION_PROPOSAL.json'
INITIAL_READBACK = E/'IO_WARNING_RELEASE_READBACK.json'
RELEASE_READBACK = E/'UNUSED_NO_SECOND_SOURCE_RELEASE.json'
GATE = E/'W3_REGISTRATION_GATE_PASS.json'
SESSION = E/'c2_c3_once'
LEDGER = E/'AG8R1_BUDGET_LEDGER.json'
ORDER = ('AD_GEMM','AD_Gaussian')
O = 'K0/OO128/Tag64x8/AE0/AD0'
GIB = 1024**3
ACTIVE_READBACK = INITIAL_READBACK
PIN = None
INTERRUPTED = []


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True)+'\n')


def git(*args):
    return subprocess.check_output(['/usr/bin/git','-C',str(REPO),*args],
        env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},text=True,timeout=30).strip()


def publication(path=None):
    """Authenticate root tool's exact independent GitHub readback against Git."""
    require(not INTERRUPTED,'EXPLICIT_CONTROLLER_ABORT_NO_FORK_OR_ACCEPTANCE')
    path = ACTIVE_READBACK if path is None else path
    receipt = json.loads(Path(path).read_text())
    head, tree = receipt['head'], receipt['tree']
    require(head == receipt['fetched_head'] == git('rev-parse','HEAD') and
        tree == receipt['fetched_tree'] == git('rev-parse','HEAD^{tree}') and
        not git('status','--porcelain'), 'EXACT_CLEAN_GITHUB_READBACK_REQUIRED')
    require(receipt['registration_sha256'] == PIN == sha(REG),
        'EXACT_PINNED_CONTROLLER_REGISTRATION_REQUIRED')
    for relative, binding in receipt['files'].items():
        target = (REPO/relative).resolve()
        require(target.is_relative_to(REPO) and sha(target) == binding['sha256'] and
            git('rev-parse',head+':'+relative) == binding['blob'],
            'REMOTE_READBACK_BLOB_OR_SOURCE_CHANGED:'+relative)
    require(str(REG.relative_to(REPO)) in receipt['files'],
        'AUTHORITY_REGISTRATION_NOT_IN_READBACK')
    registration = json.loads(REG.read_text())
    for source,digest in registration['role']['source_sha256'].items():
        require(sha(source) == digest,'SOURCE_CLOSURE_CHANGED:'+source)
    return receipt


def verify_ba_release(registration_path, registration_sha256):
    require(Path(registration_path) == REG and registration_sha256 == PIN,
        'BA_RELEASE_REQUEST_NOT_EXACT_CONTROLLER_REGISTRATION')
    receipt = publication()
    return dict(verified=True, remote_head=receipt['head'],fetched_head=receipt['fetched_head'],
        remote_tree=receipt['tree'],fetched_tree=receipt['fetched_tree'],
        registration_blob=receipt['files'][str(REG.relative_to(REPO))]['blob'],
        registration_sha256=PIN,clean_worktree=True,canonical_task='/root',
        authority_owner='BA',goal_commit='ae2e9c6f1ce7a0bb3e043c7a251f3f9dd1f86304')


def qualification(registration):
    expected_statuses={'W1_PASS_PURE_CPU_ONLY','FRAMEWORK_ONLY_BUILD_PASS_NOT_EXECUTED',
        'W2_TARGETED_CPU_PROTOCOL_AND_GUARD_PASS','PASS_CLOCK_REPAIR_NINE_PROTOCOL_METHODS','PASS_AG8R1_C1_CPU_WALL_CONTRACT'}
    require({r['required_status'] for r in registration['requirements']} == expected_statuses and
        len({r['path'] for r in registration['requirements']})==len(registration['requirements']),
        'EXACT_REUSED_W1_W2_AND_NEW_C1_RECEIPTS_REQUIRED')
    for row in registration['requirements']:
        require(sha(row['path']) == row['sha256'],'ACTUAL_QUALIFICATION_RECEIPT_CHANGED')
        value = json.loads(Path(row['path']).read_text())
        require(value['status'] == row['required_status'],'ACTUAL_QUALIFICATION_NOT_PASS')
        for key,expected in row.get('bindings',{}).items():
            require(value.get(key) == expected,'QUALIFICATION_REQUIRED_BINDING:'+key)
    c1 = json.loads(Path(registration['C1_receipt']['path']).read_text())
    require(sha(registration['C1_receipt']['path'])==registration['C1_receipt']['sha256'] and c1['status']=='PASS_AG8R1_C1_CPU_WALL_CONTRACT' and c1['tests_completed'] is True and c1['simulator_starts']==0 and c1['C1_exception_transferred_to_heavy_or_runtime'] is False,'REAL_C1_PASS_REQUIRED')
    require(all(sha(path)==digest for path,digest in c1['actual_wall_result']['source_sha256'].items()),'QUALIFIED_WALL_SUBJECT_SOURCE_CHANGED')
    comparator = registration['comparator']
    require(sha(comparator['path']) == comparator['sha256'],'AG7_BASE_DECISION_CHANGED')
    base = json.loads(Path(comparator['path']).read_text())
    require(base['BA_scoped_cross_cohort_comparator_acceptance'] is True and
        base['pre_fork_science_gate_pass'] is True and
        base['BA_decision']['canonical_task'] == '/root' and
        base['extra_BASE_starts_authorized'] == 0,'EXPLICIT_NEW_AG7_BASE_SCOPE_REQUIRED')
    bridge=registration['IO_amendment_qualification']
    require(sha(bridge['path'])==bridge['sha256'],'IO_AMENDMENT_TEST_RECEIPT_CHANGED')
    proof=json.loads(Path(bridge['path']).read_text())
    require(proof['status']=='PASS_USER_IO_WARNING_TARGETED_TESTS' and all(sha(p)==v for p,v in proof['source_sha256'].items()),'CURRENT_IO_WARNING_SOURCE_QUALIFICATION_REQUIRED')
    pilot = registration['pilot_acceptance']
    require(pilot.get('BA_explicit_conservative_pilot_surrogate_accepted') is True and
        pilot.get('user_IO_PSI_warning_only') is True and
        pilot.get('maximum_cgroup_high_episode_s') is None and
        pilot.get('no_external_task_harm_claim') is True,
        'EXPLICIT_CONSERVATIVE_HOST_EPISODE_SURROGATE_ACCEPTANCE_REQUIRED')


class Budget:
    def __init__(self, manifest, manifest_sha):
        self.manifest=manifest;self.manifest_sha=manifest_sha
        self.value=dict(schema='DTC_AG8R1_BUDGET_V1',goal='AG8R1_FINITE_RESOURCE_CONTINUATION',
            authority_registration_sha256=PIN,manifest_sha256=manifest_sha,
            maximum_new_starts=2,maximum_simultaneous_simulators=1,
            consumed_start_slots=0,actual_forks=0,unresolved_fork_slots=0,accepted=0,entries=[],
            old_AG6_consumed=1,old_AG6_three_UUIDs_sealed=True,old_AG7_consumed=3,old_AG7_accepted=2,old_AG7_unstarted_UUID_sealed=True,old_AG8_consumed=0,old_AG8_UUIDs_created=0,BA_original_consumed=0,
            automatic_retry=False,replacement_starts=0,F=None,provisional_O=O)
        write(LEDGER,self.value)
    def persist(self):
        temp=LEDGER.with_name('.AG7_LEDGER_'+str(os.getpid())+'_'+str(time.monotonic_ns()))
        write(temp,self.value)
        os.replace(temp,LEDGER)
    def verify(self):
        require(json.loads(LEDGER.read_text())==self.value,'AG7_LEDGER_CHANGED_OUTSIDE_CANONICAL_OWNER')
        return True
    def consume(self,point,start):
        self.verify();entries=self.value['entries'];index=len(entries)
        require(index<2 and point['point']==ORDER[index] and point['order']==index and
            all(row['accepted'] for row in entries),'FIXED_PREFIX_OR_FOUR_START_LIMIT')
        require(self.manifest['points'][index]['attempt_uuid']==point['attempt_uuid'] and
            not any(row['attempt_uuid']==point['attempt_uuid'] for row in entries),
            'FIXED_NEW_UUID_ONCE_ONLY')
        row=dict(point=point['point'],order=index,attempt_uuid=point['attempt_uuid'],
            destination=point['destination'],consumed=True,actual_fork=None,accepted=False,
            start_sha256=hashlib.sha256(json.dumps(start,sort_keys=True).encode()).hexdigest())
        entries.append(row);self.value['consumed_start_slots']=len(entries)
        self.value['unresolved_fork_slots']=sum(r['actual_fork'] is None for r in entries)
        self.persist()
        return dict(row)
    def verify_consumed(self,point,receipt):
        self.verify()
        require(receipt in self.value['entries'] and receipt['consumed'] is True and
            receipt['attempt_uuid']==point['attempt_uuid'] and
            self.value['entries'][-1]['attempt_uuid']==point['attempt_uuid'],
            'CONSUMED_SLOT_NOT_CURRENT_REGISTERED_POINT')
        return True
    def close_point(self,point,accepted):
        self.verify();row=self.value['entries'][-1]
        require(row['attempt_uuid']==point['attempt_uuid'],'CLOSING_FOREIGN_BUDGET_SLOT')
        child=Path(point['destination'])/'ENGINE/FORK_CHILD.json'
        if child.exists():
            proof=json.loads(child.read_text())
            require(type(proof['pid']) is int and proof['pid']>0,'ACTUAL_FORK_RECEIPT_INVALID')
            row['actual_fork']=True
        else:
            engine_terminal=Path(point['destination'])/'ENGINE/TERMINAL.json'
            explicit_no_fork=False
            if engine_terminal.exists():
                evidence=json.loads(engine_terminal.read_text())
                explicit_no_fork=evidence.get('actual_fork_children')==0 and evidence.get('root_pid') is None
            row['actual_fork']=False if explicit_no_fork else None
        require(accepted is not True or row['actual_fork'] is True,
            'ACCEPTANCE_REQUIRES_POSITIVE_ACTUAL_FORK_PROOF')
        row['accepted']=accepted is True
        self.value['actual_forks']=sum(r['actual_fork'] is True for r in self.value['entries'])
        self.value['unresolved_fork_slots']=sum(r['actual_fork'] is None for r in self.value['entries'])
        self.value['accepted']=sum(r['accepted'] for r in self.value['entries'])
        self.persist()
    def seal(self,reason):
        self.verify();self.value.update(terminal_reason=reason,
            sealed_unstarted=[dict(point=p['point'],attempt_uuid=p['attempt_uuid'])
                for p in self.manifest['points'][len(self.value['entries']):]])
        self.persist()


def sample_opportunity(pipeline,label,expected_bytes):
    """Unchanged strict paired R2; first failed sample ends this opportunity."""
    dest=SESSION/'admissions'/label;dest.mkdir(parents=True,exist_ok=False)
    checks={};samples=[];began=time.monotonic_ns()
    result=dict(label=label,began_ns=began,checks=checks,sample_count=0,
        source_registration_sha256=PIN,canonical_task='/root',IO_PSI_warning_only_user_amendment=True,CPU_exception_applied=False)
    for index in range(2):
        require(not INTERRUPTED,'EXPLICIT_ABORT_DURING_R2')
        if index:time.sleep(10.1)
        current,authority=pipeline.sampler.sample(pipeline.empty)
        write(dest/('FIRST.json' if index==0 else 'SECOND.json'),dict(snapshot=current,authority=authority))
        values=pipeline.resources.checks(current)
        for k in ('host_io_full_avg10','cgroup_io_full_avg10'):
            if values[k] is not True:result.setdefault('IO_PSI_warnings',[]).append(dict(sample=index+1,check=k))
            values.pop(k)
        values.update(authority=authority['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',
            known_io_scope=current['ag7_io_scope']['known_scope'] is True,
            projected_writes_gt5GiB=current['disk_free_bytes']-expected_bytes>5*GIB)
        checks.update({str(index+1)+'_'+k:v for k,v in values.items()})
        samples.append(current);result['sample_count']=len(samples)
        failed=[k for k,v in values.items() if v is not True]
        if failed:
            result.update(status='RESOURCE_HOLD',failed_checks=failed,
                sole_host_IO_failure=failed==['host_io_full_avg10'],ended_ns=time.monotonic_ns(),
                observed_host_IO_full_avg10=float(current['pressure']['io']['full']['avg10']),
                observed_cgroup_IO_full_avg10=float(current['cgroup_pressure_parsed']['io']['full']['avg10']),
                actual_output_free_bytes=current['disk_free_bytes'],snapshot_utc=current.get('utc'))
            write(dest/'ADMISSION.json',result)
            return None,result
    paired=pipeline.resources.paired(*samples)
    checks.update({k:v for k,v in paired.items() if not k.endswith(('host_io_full_avg10','cgroup_io_full_avg10'))})
    failed=[k for k,v in checks.items() if v is not True]
    result.update(status='PASS_STRICT_FULLSIM_R2' if not failed else 'HARD_SAFETY_STOP',failed_checks=failed,
        sole_host_IO_failure=False,ended_ns=time.monotonic_ns(),second_sample_ns=samples[-1]['monotonic_ns'],
        observed_host_IO_full_avg10=float(samples[-1]['pressure']['io']['full']['avg10']),
        observed_cgroup_IO_full_avg10=float(samples[-1]['cgroup_pressure_parsed']['io']['full']['avg10']),
        actual_output_free_bytes=samples[-1]['disk_free_bytes'],snapshot_utc=samples[-1].get('utc'))
    write(dest/'ADMISSION.json',result)
    return (samples[-1] if not failed else None),result


def persist_windows(value):
    path=E/'C2_ADMISSION_WINDOWS.json';temporary=E/('.C2_WINDOWS_'+str(time.monotonic_ns()))
    write(temporary,value);os.replace(temporary,path)


def first_point_windows(pipeline,authority,expected_bytes):
    qualification(json.loads(REG.read_text()));publication();pipeline.loaded_image_check()
    baseline,result=sample_opportunity(pipeline,'AD_GEMM_user_IO_warning_R2',expected_bytes)
    persist_windows(dict(schema='USER_IO_WARNING_SINGLE_FRESH_R2',opportunities=[result],waits=[],busy_resource_polling=False,source_registration_sha256=PIN))
    require(baseline is not None,'NON_IO_HARD_ADMISSION_FAILURE')
    return baseline,result


def main():
    global PIN
    require(len(sys.argv)==2 and len(sys.argv[1])==64,'EXACT_CANONICAL_REGISTRATION_SHA_ARGV')
    PIN=sys.argv[1]
    require(sys.argv[0]==str(PACK/'ag8r1_io_warning_entry.py'),'EXACT_AG8R1_CONTROLLER_ENTRY')
    publication();registration=json.loads(REG.read_text());qualification(registration)
    sys.path[:0]=[str(PACK/'prepared_ag8r1'),str(PACK/'prepared_ag8r1/vendor'),str(G/'vendor'),str(G)]
    from authority_dispatch import ExplicitAG7Authority
    from controller_pipeline import Pipeline
    from ag7_dispatch import run_one
    from ag7_runner import current_guard_checks
    authority=ExplicitAG7Authority(REG,PIN,verify_ba_release)
    SESSION.mkdir(exist_ok=False);(E/'execution_releases').mkdir(exist_ok=False)
    results=[];budget=None;failure=None
    previous={n:signal.signal(n,lambda number,frame:INTERRUPTED.append(number))
        for n in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP)}
    try:
        with authority.exclusive_self_lock():
            pipeline=Pipeline(registration,authority,publication)
            initial_identity=pipeline.initial_gate()
            write(E/'C0_CURRENT_IDENTITY.json',initial_identity)
            raw=MANIFEST.read_bytes();manifest=json.loads(raw);manifest_sha=sha(MANIFEST);released=publication()
            require(manifest['reservation_only'] is True and manifest['CPU_PASS_sha256']==sha(registration['C1_receipt']['path']) and
                tuple(p['point'] for p in manifest['points'])==ORDER and
                [p['order'] for p in manifest['points']]==[0,1] and
                len({p['attempt_uuid'] for p in manifest['points']})==2 and
                manifest['maximum_new_starts']==2 and manifest['maximum_simultaneous_simulators']==1 and
                str(MANIFEST.relative_to(REPO)) in released['files'],'TWO_ONLY_REMOTE_BOUND_INACTIVE_RESERVATIONS')
            budget=Budget(manifest,manifest_sha)
            for spec in manifest['points']:
                qualification(registration);publication();budget.verify()
                point,mappings=pipeline.prepare_point(spec,raw,manifest_sha,released['head'])
                if spec['order']==0:baseline,admission=first_point_windows(pipeline,authority,point['expected_attempt_output_bytes'])
                else:
                    baseline,admission=sample_opportunity(pipeline,'AD_Gaussian_single_mandatory_R2',point['expected_attempt_output_bytes'])
                    write(E/'C2_SECOND_POINT_ADMISSION.json',admission)
                    require(baseline is not None,'RESOURCE_HOLD_AD_GAUSSIAN_SINGLE_R2_NO_RECOVERY')
                # This executable release manifest does not exist before the
                # actual full heavy R2. The public proposal alone is powerless.
                activation=dict(schema='AG8R1_POST_R2_EXECUTABLE_RELEASE_V1',status='EXECUTABLE_ONLY_THIS_CURRENT_INSTANCE_AND_R2',
                    canonical_task='/root',owner=authority.owner,point=point['point'],attempt_uuid=point['attempt_uuid'],
                    source_registration_sha256=PIN,proposal_sha256=manifest_sha,publication_head=released['head'],
                    baseline_sha256=hashlib.sha256(json.dumps(baseline,sort_keys=True).encode()).hexdigest(),
                    full_strict_admission=admission,CPU_PASS_sha256=sha(registration['C1_receipt']['path']))
                activation_path=E/'execution_releases'/(point['point']+'.json');write(activation_path,activation)
                activation_sha=sha(activation_path)
                def pre_fork(p,environment,b):
                    publication();qualification(registration);authority.verify_lock();budget.verify()
                    require(sha(activation_path)==activation_sha and json.loads(activation_path.read_text())==activation and
                        p==point and b==baseline and sha(MANIFEST)==manifest_sha and
                        activation['baseline_sha256']==hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest(),
                        'CURRENT_POST_R2_RELEASE_SOURCE_INSTANCE_OR_BASELINE_CHANGED')
                    expected=dict(point['runtime_environment']);expected['DTC_AG7_PROGRESS_FD']=environment['DTC_AG7_PROGRESS_FD']
                    require(environment==expected,'EXACT_OBSERVATIONAL_DYNAMIC_FD_ONLY')
                    return pipeline.current_frozen_check(point) is True
                def checks(p,owned,pid,current):
                    return current_guard_checks(p,owned,pid,current,pipeline.last_authority,
                        mapping_manifests=mappings,identity_reader=pipeline.identity,
                        expected_output_device=baseline['output_filesystem_device'],
                        expected_remaining_write_bytes=point['expected_attempt_output_bytes'],
                        interrupted=bool(INTERRUPTED),ledger_is_current=budget.verify())
                def sample(owned):
                    current,verdict=pipeline.sampler.sample(owned);pipeline.last_authority=verdict;return current,verdict
                hooks=dict(pre_fork=pre_fork,consume_start=budget.consume,verify_consumed=budget.verify_consumed,
                    sample=sample,guard_checks=checks,io_impact=pipeline.sampler.io_impact,
                    validate_root_image=pipeline.validate_root_image,finalize=pipeline.finalize,
                    abort_requested=lambda:bool(INTERRUPTED))
                try:
                    result=run_one(point,baseline=baseline,mapping_manifests=mappings,deps=pipeline.deps,hooks=hooks)
                    strict=result.get('finalized',{});accepted=strict.get('performance_accepted') is True and strict.get('scientific_strict_pass') is True
                    budget.close_point(point,accepted);results.append(strict)
                    require(accepted,'FIRST_ACTUAL_AG8R1_SCIENCE_SAFETY_OR_STRICT_FAILURE')
                except BaseException:
                    if budget.value['entries'] and budget.value['entries'][-1]['attempt_uuid']==point['attempt_uuid']:budget.close_point(point,False)
                    raise
            from cross_cohort_selection import select_cross_cohort
            selection=select_cross_cohort(results,manifest,registration)
            write(ROOT/'AG8R1_CROSS_COHORT_SELECTION.json',selection)
            budget.value['F']=selection['F'];budget.persist();budget.seal('COMPLETE_FOUR_POINT_CROSS_COHORT_SELECTION_STOP')
    except BaseException as error:
        failure=repr(error)
        if budget is not None:budget.seal(failure)
    finally:
        for n,handler in previous.items():signal.signal(n,handler)
    terminal=dict(status='COMPLETE_AG8R1_STOP' if failure is None else 'AG8R1_HOLD_OR_STOP',reason=failure,
        canonical_task='/root',source_registration_sha256=PIN,
        actual_starts=0 if budget is None else (None if budget.value['unresolved_fork_slots'] else budget.value['actual_forks']),
        confirmed_actual_starts_minimum=0 if budget is None else budget.value['actual_forks'],
        unresolved_fork_slots=0 if budget is None else budget.value['unresolved_fork_slots'],
        accepted=0 if budget is None else budget.value['accepted'],F=None if budget is None else budget.value['F'],
        old_AG6_consumed=1,old_AG7_consumed=3,old_AG7_accepted=2,old_AG8_consumed=0,BA_original_consumed=0,
        old_goal_restart=False,automatic_retry=False,background_workflow=False,results=results)
    write(SESSION/'CONTROLLER_TERMINAL.json',terminal)
    print(json.dumps({k:v for k,v in terminal.items() if k!='results'},sort_keys=True),flush=True)
    return 0 if failure is None else 2

if __name__=='__main__':raise SystemExit(main())
