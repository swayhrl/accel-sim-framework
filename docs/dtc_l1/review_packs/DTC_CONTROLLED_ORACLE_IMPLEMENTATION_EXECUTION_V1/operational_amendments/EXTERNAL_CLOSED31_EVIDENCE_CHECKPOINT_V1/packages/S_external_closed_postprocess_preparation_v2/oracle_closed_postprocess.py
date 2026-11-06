"""CPU-reviewed closeout component; import has no scientific side effects.

No CLI executes this component. Main must separately release a pinned admission
verifier and use the context manager. No scheduler, model, registration or hook
installer is used. CPU tests replace the backend with explicitly fake objects.
"""
from pathlib import Path
import copy
import fcntl
import hashlib
import json
import os
import threading
import time
import types

ROOT = Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
REQUEST = 'DTC_ORACLE_INITIAL8_20261106_V1'
MUTEX = ROOT.parent/'control/OWNER_RECOVERY_AND_CLOSEOUT.lock'
PLAN_SHA = '6bb3876db0fe5dc7ef4544e7a0a03f822a53da73129daed9bce5bc9d822c53b0'
RESULTS_SHA = 'e9ed50a7534904c5a6a434282b1d760ff494da21c665eb9b1df3eeda7a1cb3ee'
ALIAS_SHA = '5525945a40de4b28a9c28382bdb5829747d277413518f7250c74606c78c8c3f3'
SPARSE_SHA = 'dc00fb7a0435c85dd0b377ead470df58ce9127d6bc1ef32b7ec69ad5a5885c6d'
SCHEMA = 'DTC_ORACLE_CLOSED_POSTPROCESS_SESSION_V1'

class Hold(RuntimeError):
    pass

def require(value, message):
    if not value:
        raise Hold(message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_bytes())

def put_exclusive(path,value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())

def pinned(ref):
    require(set(ref) >= {'path','sha256'}, 'PIN_REFERENCE_REQUIRED')
    require(sha(ref['path']) == ref['sha256'], 'SOURCE_OR_EVIDENCE_PIN_DRIFT:'+str(ref['path']))
    return Path(ref['path'])

def load(path, name):
    path = Path(path)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module

def proc_start(pid):
    return int(Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19])

def snapshot_identity(root, cohort, consumed):
    """Read-only prerequisite; original strict/outbox still recheck everything."""
    require(isinstance(cohort,str) and '/' not in cohort and '..' not in cohort,
            'EXACT_COHORT_REQUIRED')
    require(cohort in consumed, 'EXISTING_CONSUMED_UUID_REQUIRED')
    row = consumed[cohort]
    ledger = root/'control/qualification_ledger'
    ip = ledger/(cohort+'.INTENT.json')
    dp = ledger/(cohort+'.DONE.json')
    i, d = read(ip), read(dp)
    out = root/'DTC/run/results'/row['uuid']
    require(Path(i['output']) == out and i['uuid']==d['uuid']==row['uuid'], 'OUTPUT_UUID_BINDING')
    require(i['cohort']==d['cohort']==cohort, 'COHORT_BINDING')
    require(sha(ip)==row['intent_sha256'], 'ORIGINAL_INTENT_PIN')
    require(d==row['execution_receipt']==read(out/'NATIVE_EXIT.json'), 'ORIGINAL_DONE_EXIT_RECEIPT')
    require(d['new_attempt_consumed']==1 and d['automatic_retry'] is False, 'ORIGINAL_ONCE_ONLY_UUID')
    require(d['stop_reason'] is None and d['launcher_wait_returncode']==0
            and d['native_simulator_observed'] is True, 'NATURAL_OBSERVED_CLOSED_ONLY')
    pid = read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
    try:
        live = proc_start(pid['pid'])==pid['start_ticks']
    except FileNotFoundError:
        live = False
    require(not live, 'SIMULATOR_STILL_LIVE')
    require(sha(out/'raw.log.gz')==d['raw_sha256'], 'ORIGINAL_RAW_PIN')
    return dict(cohort=cohort,uuid=d['uuid'],output=str(out),
                intent_sha256=sha(ip),done_sha256=sha(dp),raw_sha256=d['raw_sha256'])

def verify_request_monotonic(before,after,root):
    """Allow only real receipt additions by already-running independent frontends.

    A long archive must not mistake a healthy peer's natural close for a new
    scientific launch. All old fields/receipts, consumed identities and every
    top-level registry field remain exact. No receipt is copied or written here.
    """
    require({k:v for k,v in before.items()if k!='consumed'}==
            {k:v for k,v in after.items()if k!='consumed'}, 'REGISTERED_REQUEST_IMMUTABLE_FIELDS_CHANGED')
    require(set(before['consumed'])==set(after['consumed']), 'CONSUMED_IDENTITY_SET_CHANGED')
    additions=[]
    for c,old in before['consumed'].items():
        new=after['consumed'][c]
        if old==new:continue
        require('execution_receipt' not in old and 'execution_receipt' in new,
                'EXISTING_RECEIPT_OR_IDENTITY_REWRITTEN')
        require(old=={k:v for k,v in new.items()if k!='execution_receipt'},
                'CONSUMED_UUID_INTENT_OR_OTHER_FIELDS_CHANGED')
        ledger=Path(root)/'control/qualification_ledger'
        ip=ledger/(c+'.INTENT.json');i=read(ip);d=read(ledger/(c+'.DONE.json'))
        out=Path(root)/'DTC/run/results'/old['uuid']
        require(sha(ip)==old['intent_sha256'] and i['uuid']==d['uuid']==old['uuid']
                and i['cohort']==d['cohort']==c and Path(i['output'])==out,
                'APPENDED_RECEIPT_ORIGINAL_INTENT_BINDING')
        require(d==new['execution_receipt']==read(out/'NATIVE_EXIT.json'),
                'APPENDED_RECEIPT_DONE_EXIT_BINDING')
        require(d['new_attempt_consumed']==1 and d['automatic_retry'] is False
                and type(d['launcher_wait_returncode']) is int
                and type(d['native_simulator_observed']) is bool,
                'APPENDED_RECEIPT_ORIGINAL_ONCE_ONLY_LIFECYCLE')
        require(sha(out/'raw.log.gz')==d['raw_sha256'], 'APPENDED_RECEIPT_ORIGINAL_RAW_PIN')
        additions.append(dict(cohort=c,uuid=old['uuid'],done_sha256=sha(ledger/(c+'.DONE.json'))))
    return additions

def _load_consumer(config):
    root = Path(config['stage_root'])
    require(sha(root/'tools/oracle_results.py')==RESULTS_SHA, 'ORIGINAL_RESULTS_PIN')
    alias_path, sparse_path = pinned(config['alias_hook']), pinned(config['sparse_hook'])
    require(config['alias_hook']['sha256']==ALIAS_SHA and config['sparse_hook']['sha256']==SPARSE_SHA,
            'ONLY_QUALIFIED_PRIVATE_HOOKS')
    consumer = load(root/'tools/oracle_results.py', 'closed_only_frozen_consumer')
    # wrap_consumer is module-private; install() is deliberately never called.
    consumer = load(alias_path, 'closed_only_exact_alias').wrap_consumer(consumer,root)
    consumer = load(sparse_path, 'closed_only_proven_sparse').wrap_consumer(consumer,root)
    return consumer

class CloseoutSession:
    """Single worker, whole-session mutual exclusion, no scientific admission.

    The same lock MUST be acquired before any old-owner recovery or image
    transition. A lock alone cannot freeze an uncooperative old archive worker;
    an independently reviewed live verifier must prove retirement/exclusion.
    """
    def __init__(self, config):
        self.config = copy.deepcopy(config)
        self.root = Path(config['stage_root'])
        self.thread = threading.get_ident()
        self.lock = None
        self.consumer = None
        self.verifier = None
        self.events = []

    def _assert_thread(self):
        require(threading.get_ident()==self.thread, 'ONE_CLOSEOUT_THREAD_ONLY')
        require(self.lock is not None, 'GOVERNANCE_LOCK_NOT_HELD')

    def _admission(self):
        self._assert_thread()
        context = dict(schema=SCHEMA,stage_root=str(self.root),request=REQUEST,
                       governance_lock=str(MUTEX),caller_pid=os.getpid(),
                       caller_start_ticks=proc_start(os.getpid()),
                       execution_mode=self.config['execution_mode'],new_scientific_starts=0)
        context['governance_lock_fd']=self.lock.fileno()
        stat=os.fstat(self.lock.fileno())
        context['governance_lock_device_inode']=[stat.st_dev,stat.st_ino]
        pinned(self.config['alias_hook']);pinned(self.config['sparse_hook'])
        if hasattr(self,'runner_release_sha'):
            require(sha(__file__)==self.runner_release_sha,'RUNNER_RELEASE_SOURCE_DRIFT')
        require(sha(self.config['admission_verifier']['path'])==self.config['admission_verifier']['sha256'],
                'ADMISSION_VERIFIER_DRIFT')
        proof = self.verifier.verify_closeout_admission(context,copy.deepcopy(self.config))
        require(proof.get('status')=='PASS', 'LIVE_CLOSEOUT_ADMISSION_HOLD:'+str(proof))
        for key in ['request','governance_lock','caller_pid','caller_start_ticks','execution_mode']:
            require(proof.get(key)==context[key], 'LIVE_ADMISSION_BINDING:'+key)
        require(proof.get('original_closer_threads_excluded') is True
                and proof.get('owner_recovery_excluded') is True
                and proof.get('new_scientific_starts_permitted') is False,
                'REAL_FULL_FLOW_EXCLUSION_REQUIRED')
        require(proof.get('independent_quiescence_or_retirement_review')=='PASS', 'INDEPENDENT_OLD_IMAGE_PROOF_REQUIRED')
        require(proof.get('observed_monotonic_ns',0)<=time.monotonic_ns()
                <=proof.get('valid_until_monotonic_ns',0), 'LIVE_ADMISSION_PROOF_EXPIRED')
        require(proof['valid_until_monotonic_ns']-proof['observed_monotonic_ns']<=60*10**9,
                'FRESH_ADMISSION_PROOF_REQUIRED')
        return proof

    def __enter__(self):
        require(self.root==ROOT and self.config['request']==REQUEST, 'INITIAL32_ONLY_NO_R24')
        require(self.config['execution_mode'] in {'OWNER_IMAGE_CLOSEOUT','EXTERNAL_POSTPROCESS_ONLY'},
                'EXPLICIT_CLOSEOUT_ROLE')
        require(self.config.get('actual_execution_authorized') is True, 'PREPARATION_ONLY_NOT_AUTHORIZED')
        require(self.config.get('new_scientific_starts',None)==0, 'ZERO_SCIENCE_STARTS_REQUIRED')
        require(self.config.get('governance_lock')==str(MUTEX), 'ONE_MAIN_RECOVERY_CLOSEOUT_LOCK')
        require(sha(self.root/'control/EXECUTION_PLAN.json')==PLAN_SHA, 'REGISTERED_PLAN_UNCHANGED')
        auth = read(pinned(self.config['authorization']))
        require(auth.get('status')=='AUTHORIZED_CLOSED_ONLY' and auth.get('request')==REQUEST,
                'MAIN_ACTUAL_CLOSED_ONLY_RELEASE_REQUIRED')
        require(auth.get('runner_sha256')==sha(__file__)
                and auth.get('admission_verifier')==self.config['admission_verifier']
                and auth.get('execution_mode')==self.config['execution_mode']
                and auth.get('governance_lock')==str(MUTEX), 'ACTUAL_RELEASE_SOURCE_ROLE_MUTEX_BINDING')
        self.allowed = auth['authorized_closed_cohorts']
        self.runner_release_sha=auth['runner_sha256']
        require(isinstance(self.allowed,list) and len(set(self.allowed))==len(self.allowed)<=32,
                'EXACT_CLOSED_COHORT_RELEASE_REQUIRED')
        # A newly created file is just a governance rendezvous, not evidence that
        # the old image is stopped; the independent verifier remains mandatory.
        MUTEX.parent.mkdir(parents=True,exist_ok=True)
        self.lock = MUTEX.open('a+b')
        try:
            fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.verifier = load(pinned(self.config['admission_verifier']), 'closed_only_live_admission')
            self._admission()
            self.consumer = _load_consumer(self.config)
            return self
        except BaseException:
            self.lock.close(); self.lock=None
            raise

    def finish(self, cohort):
        """Finish one existing naturally closed UUID, or verify/adopt its RESULT.

        No automatic retry. Original archive_resources/CLOSED_COPY/receiver locks
        and SOURCE_KEEP are retained. On an engineering exception the caller may
        preserve this event and later explicitly retry same-UUID postprocessing;
        this function never resubmits a model or modifies consumed identities.
        """
        self._assert_thread()
        require(cohort in self.allowed, 'COHORT_NOT_RELEASED_FOR_CLOSEOUT')
        gate = self._admission()
        engine = self.consumer.load('closed_only_read_engine','oracle_native.py')
        before = copy.deepcopy(engine.registered()[2])
        require(before['request']==REQUEST and before['budget']==32, 'ONLY_ORIGINAL_INITIAL32')
        original = snapshot_identity(self.root,cohort,before['consumed'])
        rp = self.root/'analysis'/(cohort+'.RESULT.json')
        old_sha = sha(rp) if rp.exists() else None
        event = dict(schema=SCHEMA,role=self.config['execution_mode'],caller_pid=os.getpid(),
                     caller_start_ticks=proc_start(os.getpid()),original_identity=original,
                     admission=gate,original_result_sha256=old_sha,source_keep=True,
                     model_starts=0,new_UUIDs=0,registry_writes=0,
                     runner_sha256=sha(__file__),alias_hook=self.config['alias_hook'],
                     sparse_hook=self.config['sparse_hook'],started_monotonic_ns=time.monotonic_ns())
        audit_root = ROOT.parent/'control/CLOSED_POSTPROCESS_AUDIT'
        stem = str(time.time_ns())+'.'+str(os.getpid())+'.'+cohort
        # This sidecar records the actual closer role before the first write to
        # strict/archive/RESULT. It is NOT part of original simulator provenance.
        put_exclusive(audit_root/(stem+'.BEGIN.json'),event)
        try:
            value = self.consumer.finish_evidence(cohort)
            require(value['uuid']==original['uuid'] and value['cohort']==cohort, 'FINISHED_UUID_MATCH')
            if old_sha is not None:
                require(sha(rp)==old_sha, 'EXISTING_RESULT_MUST_NOT_CHANGE')
            # Original finish returns existing RESULT early. Independently verify
            # its archive/restored typed tree with the SAME qualified outbox.
            outbox = self.consumer.load('closed_only_verify_outbox','oracle_outbox.py')
            archive_proof = outbox.verify(cohort)
            require(value.get('archive')==archive_proof, 'RESULT_ARCHIVE_PROOF_MATCH')
            strict=read(Path(original['output'])/'L2_STRICT.json')
            require(value.get('proof')==strict and value.get('cycles')==strict.get('cycles')
                    and strict.get('performance_accepted') is True, 'ORIGINAL_STRICT_RESULT_MATCH')
            require(read(rp)==value, 'RESULT_EXACT_ON_DISK')
            event.update(status='CLOSED_RESULT_VERIFIED',result_path=str(rp),
                         result_sha256=sha(rp),original_state=value.get('state'),
                         archive_verification=archive_proof,adopted_existing_result=old_sha is not None)
            return value
        except BaseException as error:
            event.update(status='CLOSEOUT_ENGINEERING_HOLD_NO_RETRY',error=repr(error))
            raise
        finally:
            # No writes to registry/epoch are ever used for reconciliation.
            try:
                event['concurrent_existing_frontend_receipts']=verify_request_monotonic(
                    before,engine.registered()[2],self.root)
                require(snapshot_identity(self.root,cohort,before['consumed'])==original,
                        'ORIGINAL_SCIENTIFIC_ARTIFACTS_CHANGED')
            except BaseException as error:
                event.update(status='CLOSEOUT_INTEGRITY_HOLD',integrity_error=repr(error))
                self.events.append(event)
                put_exclusive(audit_root/(stem+'.END.json'),event)
                raise
            event['finished_monotonic_ns']=time.monotonic_ns()
            self.events.append(event)
            put_exclusive(audit_root/(stem+'.END.json'),event)

    def __exit__(self, typ, value, tb):
        # Export self.events to a separate immutable engineering sidecar, never
        # insert fabricated provenance into original raw/strict/RESULT fields.
        if self.lock is not None:
            self.lock.close(); self.lock=None
        return False

if __name__=='__main__':
    print(json.dumps(dict(status='PREPARATION_ONLY',actual_consume_archive_restore=False,
                          message='No execute CLI; Main pinned release + live exclusion verifier required.')))
