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
ROOT = Path('/workspace/dtc-ag8-ad-convergence-174-v1')
E = ROOT/'evidence'
G = E/'w0_frozen_authority'
REG = PACK/'AD8_AUTHORITY_REGISTRATION.json'
MANIFEST = PACK/'AD8_TWO_POINT_MANIFEST.json'
INITIAL_READBACK = E/'W3_CONTROLLER_READBACK.json'
RELEASE_READBACK = E/'W3_RELEASE_READBACK.json'
GATE = E/'W3_REGISTRATION_GATE_PASS.json'
SESSION = E/'w3_controller_once'
LEDGER = E/'AD8_BUDGET_LEDGER.json'
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
        authority_owner='BA',goal_commit='1aa6aab1bf698ca5b5267318dbbceb2854a46131')


def qualification(registration):
    expected_statuses={'W1_PASS_PURE_CPU_ONLY','FRAMEWORK_ONLY_BUILD_PASS_NOT_EXECUTED',
        'W2_TARGETED_CPU_PROTOCOL_AND_GUARD_PASS','PASS_CLOCK_REPAIR_NINE_PROTOCOL_METHODS'}
    require({r['required_status'] for r in registration['requirements']} == expected_statuses and
        len({r['path'] for r in registration['requirements']})==len(registration['requirements']),
        'EXACT_W1_W2_BUILD_CLOCK_REPAIR_ACTUAL_RECEIPTS_REQUIRED')
    for row in registration['requirements']:
        require(sha(row['path']) == row['sha256'],'ACTUAL_QUALIFICATION_RECEIPT_CHANGED')
        value = json.loads(Path(row['path']).read_text())
        require(value['status'] == row['required_status'],'ACTUAL_QUALIFICATION_NOT_PASS')
        for key,expected in row.get('bindings',{}).items():
            require(value.get(key) == expected,'QUALIFICATION_REQUIRED_BINDING:'+key)
    comparator = registration['comparator']
    require(sha(comparator['path']) == comparator['sha256'],'AG7_BASE_DECISION_CHANGED')
    base = json.loads(Path(comparator['path']).read_text())
    require(base['BA_scoped_cross_cohort_comparator_acceptance'] is True and
        base['pre_fork_science_gate_pass'] is True and
        base['BA_decision']['canonical_task'] == '/root' and
        base['extra_BASE_starts_authorized'] == 0,'EXPLICIT_NEW_AG7_BASE_SCOPE_REQUIRED')
    pilot = registration['pilot_acceptance']
    require(pilot.get('BA_explicit_conservative_pilot_surrogate_accepted') is True and
        pilot.get('host_io_three_ge30s_preserved') is True and
        pilot.get('maximum_cgroup_high_episode_s') == 1800 and
        pilot.get('no_external_task_harm_claim') is True,
        'EXPLICIT_CONSERVATIVE_HOST_EPISODE_SURROGATE_ACCEPTANCE_REQUIRED')


def _admit_once(pipeline, label, expected_bytes):
    """One finite strict pair, no W1 exception, retry, poll or threshold change."""
    dest=SESSION/'admissions'/label
    dest.mkdir(parents=True,exist_ok=False)
    samples=[];checks={}
    for index in range(2):
        require(not INTERRUPTED,'EXPLICIT_ABORT_DURING_ADMISSION')
        if index:time.sleep(10.1)
        require(not INTERRUPTED,'EXPLICIT_ABORT_DURING_ADMISSION')
        current,authority=pipeline.sampler.sample(pipeline.empty)
        write(dest/('FIRST.json' if index==0 else 'SECOND.json'),
            dict(snapshot=current,authority=authority))
        values=pipeline.resources.checks(current)
        require(authority['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY' and
            values['original174'],'TRUE_AUTHORITY_OR_ENVIRONMENT_FAILURE_IMMEDIATE_STOP')
        require(current['ag7_io_scope']['known_scope'] is True,
            'TRUE_IO_SCOPE_SAFETY_FAILURE_IMMEDIATE_STOP')
        require(current['disk_free_bytes']>5*GIB,'TRUE_STORAGE_DANGER_IMMEDIATE_STOP')
        values.update(authority=authority['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY',
            known_io_scope=current['ag7_io_scope']['known_scope'] is True,
            projected_writes_gt5GiB=current['disk_free_bytes']-expected_bytes>5*GIB)
        checks.update({str(index+1)+'_'+k:v for k,v in values.items()})
        samples.append(current)
        if not all(values.values()):
            write(dest/'ADMISSION.json',dict(status='RESOURCE_HOLD',checks=checks,simulator_starts=0))
            return None
    checks.update(pipeline.resources.paired(*samples))
    write(dest/'ADMISSION.json',dict(status='PASS_STRICT_FULLSIM_R2' if all(checks.values())
        else 'RESOURCE_HOLD',checks=checks))
    return samples[-1] if all(checks.values()) else None


def admit(pipeline, label, expected_bytes):
    # AG8: first primary rejection is HOLD; no automatic resource retry.
    return _admit_once(pipeline,label+'_once',expected_bytes)


class Budget:
    def __init__(self, manifest, manifest_sha):
        self.manifest=manifest;self.manifest_sha=manifest_sha
        self.value=dict(schema='DTC_AD8_BUDGET_V1',goal='AG8_AD_CONVERGENCE_V1',
            authority_registration_sha256=PIN,manifest_sha256=manifest_sha,
            maximum_new_starts=2,maximum_simultaneous_simulators=1,
            consumed_start_slots=0,actual_forks=0,unresolved_fork_slots=0,accepted=0,entries=[],
            old_AG6_consumed=1,old_AG6_three_UUIDs_sealed=True,old_AG7_consumed=3,old_AG7_accepted=2,old_AG7_unstarted_UUID_sealed=True,BA_original_consumed=0,
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


def select(results, manifest):
    from cross_cohort_selection import select_cross_cohort
    return select_cross_cohort(results, manifest, json.loads(REG.read_text()))


def main():
    global PIN,ACTIVE_READBACK
    require(len(sys.argv)==2 and len(sys.argv[1])==64 and
        all(c in '0123456789abcdef' for c in sys.argv[1]),'EXACT_REGISTRATION_SHA_ARGV_REQUIRED')
    PIN=sys.argv[1]
    require(sys.argv[0]==str(PACK/'ad8_controller_entry.py'),'EXACT_CANONICAL_ENTRY_REQUIRED')
    publication()
    registration=json.loads(REG.read_text());qualification(registration)
    sys.path[:0]=[str(PACK/'prepared_ad8'),str(PACK/'prepared_ad8/vendor'),str(G/'vendor'),str(G)]
    from authority_dispatch import ExplicitAG7Authority
    from controller_pipeline import Pipeline
    from ag7_dispatch import run_one
    from ag7_runner import current_guard_checks
    authority=ExplicitAG7Authority(REG,PIN,verify_ba_release)
    SESSION.mkdir(exist_ok=False)
    results=[];budget=None;failure=None
    previous_handlers={number:signal.signal(number,lambda n,frame:INTERRUPTED.append(n))
        for number in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP)}
    try:
        with authority.exclusive_self_lock():
            pipeline=Pipeline(registration,authority,publication)
            initial_identity=pipeline.initial_gate()
            initial=admit(pipeline,'initial_pre_UUID_gate',4*GIB)
            require(initial is not None,'RESOURCE_HOLD_INITIAL_NO_UUID_NO_START')
            qualification(registration);source=publication()
            from wall_contract_qualification import qualify_wall_contract
            wall_qualification = qualify_wall_contract(E)
            require(wall_qualification['status']=='PASS_AD8_NARROW_WALL_CONTRACT', 'NEW_WALL_CONTRACT_NOT_QUALIFIED')
            require(not MANIFEST.exists(),'UUID_MANIFEST_MUST_NOT_PRECEDE_ALL_PRELAUNCH_GATES')
            write(GATE,dict(status='W3_REGISTRATION_GATE_PASS',authority_registration_sha256=PIN,
                canonical_task='/root',controller_owner=authority.owner,lock=authority.verify_lock(),
                publication_head=source['head'],identity=initial_identity,
                initial_R2_second_ns=initial['monotonic_ns'],simulator_starts=0,
                wall_contract_qualification_sha256=sha(E/'D1_WALL_CONTRACT_QUALIFICATION.json'),
                UUID_creation_authorized_only_after_this_gate=True))
            deadline=time.monotonic()+300
            while not RELEASE_READBACK.exists():
                require(not INTERRUPTED,'EXPLICIT_ABORT_DURING_RELEASE_WAIT')
                require(time.monotonic()<deadline,'BOUNDED_W3_RELEASE_WAIT_EXPIRED_NO_START')
                time.sleep(0.5)
            ACTIVE_READBACK=RELEASE_READBACK
            released=publication()
            require(released['registration_gate_sha256']==sha(GATE) and
                released['manifest_path']==str(MANIFEST) and
                released['manifest_sha256']==sha(MANIFEST) and
                str(MANIFEST.relative_to(REPO)) in released['files'],
                'EXACT_POST_GATE_MANIFEST_RELEASE_READBACK_REQUIRED')
            raw=MANIFEST.read_bytes();manifest=json.loads(raw);manifest_sha=sha(MANIFEST)
            require(tuple(p['point'] for p in manifest['points'])==ORDER and
                [p['order'] for p in manifest['points']]==list(range(2)) and
                len({p['attempt_uuid'] for p in manifest['points']})==2 and
                manifest['maximum_new_starts']==2 and manifest['maximum_simultaneous_simulators']==1 and
                manifest['registration_gate_sha256']==sha(GATE),
                'FOUR_NEW_ONCE_ONLY_POST_GATE_AG7_MANIFEST_REQUIRED')
            budget=Budget(manifest,manifest_sha)
            for spec in manifest['points']:
                qualification(registration);publication();budget.verify()
                point,mappings=pipeline.prepare_point(spec,raw,manifest_sha,released['head'])
                baseline=admit(pipeline,point['point'],point['expected_attempt_output_bytes'])
                require(baseline is not None,'RESOURCE_HOLD_POINT_'+point['point'])
                def pre_fork(p,environment,b):
                    publication();qualification(registration);authority.verify_lock();budget.verify()
                    require(p==point and b==baseline and p['publication_head']==released['head'] and
                        sha(MANIFEST)==manifest_sha,'EXACT_RELEASE_POINT_OR_BASELINE_CHANGED')
                    expected=dict(point['runtime_environment'])
                    expected['DTC_AG7_PROGRESS_FD']=environment['DTC_AG7_PROGRESS_FD']
                    require(environment==expected,'DYNAMIC_TELEMETRY_FD_ONLY_ENV_DELTA')
                    return pipeline.current_frozen_check(point) is True
                def checks(p,owned,pid,current):
                    current_authority=pipeline.last_authority
                    return current_guard_checks(p,owned,pid,current,current_authority,
                        mapping_manifests=mappings,identity_reader=pipeline.identity,
                        expected_output_device=baseline['output_filesystem_device'],
                        expected_remaining_write_bytes=point['expected_attempt_output_bytes'],
                        interrupted=bool(INTERRUPTED),ledger_is_current=budget.verify())
                def sample(owned):
                    current,verdict=pipeline.sampler.sample(owned)
                    pipeline.last_authority=verdict
                    return current,verdict
                hooks=dict(pre_fork=pre_fork,consume_start=budget.consume,
                    verify_consumed=budget.verify_consumed,sample=sample,guard_checks=checks,
                    io_impact=pipeline.sampler.io_impact,validate_root_image=pipeline.validate_root_image,
                    finalize=pipeline.finalize,abort_requested=lambda:bool(INTERRUPTED))
                try:
                    result=run_one(point,baseline=baseline,mapping_manifests=mappings,
                        deps=pipeline.deps,hooks=hooks)
                    strict=result.get('finalized',{})
                    accepted=strict.get('performance_accepted') is True and strict.get('scientific_strict_pass') is True
                    budget.close_point(point,accepted)
                    results.append(strict)
                    require(accepted,'FIRST_ACTUAL_AG7_SCIENCE_SAFETY_OR_CLOSURE_FAILURE')
                except BaseException:
                    if budget.value['entries'] and budget.value['entries'][-1]['attempt_uuid']==point['attempt_uuid']:
                        budget.close_point(point,False)
                    raise
            selection=select(results,manifest)
            write(ROOT/'AD8_CROSS_COHORT_SELECTION_V1.json',selection)
            budget.value['F']=selection['F'];budget.persist();budget.seal('COMPLETE_FOUR_ACCEPTED_ARMS_STOP')
    except BaseException as error:
        failure=repr(error)
        if budget is not None:
            try:budget.seal(failure)
            except BaseException as ledger_error:
                failure+='; LEDGER_SEAL_FAIL_CLOSED:'+repr(ledger_error)
    finally:
        for number,handler in previous_handlers.items():signal.signal(number,handler)
    terminal=dict(status='COMPLETE_AD8_STOP' if failure is None else 'AD8_HOLD_OR_STOP',
        reason=failure,canonical_task='/root',authority_registration_sha256=PIN,
        actual_starts=0 if budget is None else (None if budget.value['unresolved_fork_slots'] else budget.value['actual_forks']),
        confirmed_actual_starts_minimum=0 if budget is None else budget.value['actual_forks'],
        unresolved_fork_slots=0 if budget is None else budget.value['unresolved_fork_slots'],
        accepted=0 if budget is None else budget.value['accepted'],
        F=None if budget is None else budget.value['F'],provisional_O=O,
        old_AG6_consumed=1,old_AG6_three_UUIDs_sealed=True,old_AG7_consumed=3,old_AG7_accepted=2,old_AG7_unstarted_UUID_sealed=True,BA_original_consumed=0,
        old_goal_restart=False,automatic_retry=False,background_workflow=False,results=results)
    write(SESSION/'CONTROLLER_TERMINAL.json',terminal)
    print(json.dumps({k:v for k,v in terminal.items() if k!='results'},sort_keys=True),flush=True)
    return 0 if failure is None else 2


if __name__=='__main__':
    raise SystemExit(main())
