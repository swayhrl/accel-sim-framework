"""Source-prepared canonical BA/root AG7 authority and isolated own-lock adapter.

No CLI, import work, launch, process adoption, signal, budget or UUID API. Only
explicit exclusive_self_lock() may CREATE/FLOCK the new AG7 lock. A pinned,
independently verified canonical BA/root release is mandatory; uid is merely an
environment predicate. Frozen legacy source/code and all unknown-lock checks are
retained. This adapter alone never grants a simulation capability.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import types

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
WORKTREE = PACK.parents[3]
ROOT = Path('/workspace/dtc-ag8r1-finite-resume-174-v1')
LOCK = ROOT / 'AG_execution_io_warning.lock'
FROZEN = ROOT / 'evidence/w0_frozen_authority'
SOURCE_INDEX = ROOT / 'evidence/W0_SOURCE_BINDING.json'
GOAL = 'AG8R1_FINITE_RESOURCE_CONTINUATION'
GOAL_COMMIT = 'ae2e9c6f1ce7a0bb3e043c7a251f3f9dd1f86304'
ROLE = 'AG8R1_SOLE_CANONICAL_BA_ROOT_DISPATCH_CONTROLLER'
PASS = 'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _clone_raw_only(function):
    """Fresh function globals: original code and old users remain unchanged."""
    scope = dict(function.__globals__)
    scope['RAW'] = ROOT
    return types.FunctionType(function.__code__, scope, function.__name__,
                              function.__defaults__, function.__closure__)


class ExplicitAG7Authority:
    """Own process only; release_verifier is the reviewed BA publication join.

    release_verifier(registration_path, pinned_sha) must independently validate
    the exact remotely fetched registration/blob/clean source and its explicit
    BA canonical /root authorization, returning the receipt shape checked below.
    A caller-supplied claim, uid/root pathname, CPU role or old AG6 release is not
    sufficient. The callback itself is in this controller's frozen source closure.
    """
    def __init__(self, registration_path, pinned_registration_sha256,
                 release_verifier):
        self.path = Path(registration_path)
        self.digest = pinned_registration_sha256
        self.release_verifier = release_verifier
        self.fd = None
        self.lock_record = None
        self.owner = None
        self._validate_registration()
        # These imports must resolve to the W0 frozen copies, never a current tip.
        import shared_authority
        import legacy_authority_runtime
        import ownership
        self.shared = shared_authority
        self.legacy = legacy_authority_runtime
        self.identity = ownership.identity
        for module, path in ((shared_authority, FROZEN/'shared_authority.py'),
                             (legacy_authority_runtime, FROZEN/'legacy_authority_runtime.py'),
                             (ownership, FROZEN/'vendor/ownership.py')):
            require(Path(module.__file__).resolve() == path,
                    'AG7_AUTHORITY_IMPORT_NOT_FROZEN:' + module.__name__)
        self.owner = self.identity(os.getpid())
        self._verify_self()

    def _validate_registration(self):
        require(self.path.is_absolute() and self.path.resolve() == self.path and
                self.path.is_relative_to(PACK), 'AG7_AUTHORITY_REGISTRATION_PATH')
        require(sha(self.path) == self.digest, 'AG7_AUTHORITY_REGISTRATION_CHANGED')
        registration = json.loads(self.path.read_text())
        require(registration['schema'] == 'DTC_AG8R1_BA_ROOT_AUTHORITY_V1' and
                registration['goal'] == GOAL and
                registration['goal_commit'] == GOAL_COMMIT and
                registration['canonical_task'] == '/root' and
                registration['authority_owner'] == 'BA' and
                registration['sole_dispatcher'] is True and
                registration['root'] == str(ROOT) and
                registration['own_lock'] == str(LOCK),
                'EXPLICIT_CANONICAL_BA_ROOT_AG7_RELEASE_REQUIRED')
        receipt = self.release_verifier(self.path, self.digest)
        require(isinstance(receipt, dict) and receipt.get('verified') is True and
                receipt.get('remote_head') == receipt.get('fetched_head') and
                receipt.get('remote_tree') == receipt.get('fetched_tree') and
                receipt.get('clean_worktree') is True and
                receipt.get('registration_sha256') == self.digest and
                receipt.get('canonical_task') == '/root' and
                receipt.get('authority_owner') == 'BA' and
                receipt.get('goal_commit') == GOAL_COMMIT,
                'AG7_CANONICAL_BA_RELEASE_NOT_INDEPENDENTLY_VERIFIED')
        for key in ('remote_head', 'remote_tree', 'registration_blob'):
            value = receipt.get(key)
            require(isinstance(value, str) and len(value) == 40 and
                    all(c in '0123456789abcdef' for c in value),
                    'AG7_RELEASE_OBJECT_ID_REQUIRED:' + key)
        role = registration['role']
        entry = Path(registration['controller_entry'])
        require(entry.is_absolute() and entry.resolve() == entry and
                entry.is_relative_to(PACK) and entry.suffix == '.py',
                'AG7_EXACT_CONTROLLER_ENTRY_REQUIRED')
        require(role['name'] == ROLE and role['cwd'] == str(WORKTREE) and
                role['executable'] == '/usr/bin/python3.10' and
                role['argvs'] == [['/usr/bin/python3.10', '-I', '-B', str(entry), '@REG_SHA@']] and
                str(entry) in role['source_sha256'] and
                str(HERE/'authority_dispatch.py') in role['source_sha256'] and
                str(SOURCE_INDEX) in role['source_sha256'],
                'AG7_DISPATCH_ROLE_IS_NOT_EXACT_SOURCE_BOUND')
        # The callback's module file is frozen too; no arbitrary lambda releases.
        callback_path = Path(self.release_verifier.__code__.co_filename).resolve()
        require(str(callback_path) in role['source_sha256'],
                'BA_RELEASE_VERIFIER_NOT_IN_CONTROLLER_SOURCE_CLOSURE')
        for path, digest in role['source_sha256'].items():
            require(Path(path).is_absolute() and sha(path) == digest,
                    'AG7_DISPATCH_SOURCE_CHANGED:' + path)
        require(sha(role['executable']) == role['executable_sha256'],
                'AG7_DISPATCH_INTERPRETER_CHANGED')
        index = json.loads(SOURCE_INDEX.read_text())
        frozen = {row['path']: row['sha256'] for row in index}
        require(registration['frozen_authority_sha256'] == frozen,
                'AG7_FROZEN_AUTHORITY_INDEX_NOT_EXACT_W0')
        for path, digest in frozen.items():
            require(sha(path) == digest, 'AG7_FROZEN_AUTHORITY_CHANGED:' + path)
        # Registration stores one literal placeholder to break the hash cycle.
        # Only after its SHA is authenticated, resolve ONE exact actual argv;
        # runtime matching never accepts a wildcard or another registration SHA.
        runtime_role = dict(role, argvs=[['/usr/bin/python3.10', '-I', '-B',
                                        str(entry), self.digest]])
        self.registration, self.role, self.publication = registration, runtime_role, receipt

    def _verify_self(self):
        # UID/hostname are environmental exclusions, never the authorization proof.
        require(socket.gethostname() == 'huangrulin-174' and os.getuid() == 0,
                'AG7_ORIGINAL174_ENVIRONMENT_REQUIRED')
        require(ROOT.resolve() == ROOT and WORKTREE.resolve() == WORKTREE,
                'AG7_ROOT_OR_WORKTREE_SYMLINK')
        live = self.shared.fresh_process(os.getpid(), self.identity)
        if self.owner is not None:
            require(live['start_ticks'] == self.owner['start_ticks'],
                    'AG7_CANONICAL_CONTROLLER_INSTANCE_CHANGED')
        require(live['tracer_pid'] == 0 and live['state'] != 'Z',
                'AG7_CONTROLLER_ALREADY_TRACED_OR_TERMINAL')
        require(live['argv'] == self.role['argvs'][0] and
                live['cwd'] == self.role['cwd'] and
                live['exe'] == self.role['executable'],
                'AG7_CURRENT_CONTROLLER_EXEC_ARGV_CWD_MISMATCH')
        return live

    @contextlib.contextmanager
    def exclusive_self_lock(self):
        """Create this NEW path once; approved finite waits may unlock/reacquire only its own descriptor. Never open an old/foreign lock."""
        self._validate_registration()
        self._verify_self()
        require(self.fd is None and self.lock_record is None,
                'AG7_LOCK_ALREADY_USED_NO_RESTART')
        fd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            owner = self.identity(os.getpid())
            require(owner['start_ticks'] == self.owner['start_ticks'],
                    'AG7_OWN_LOCK_INSTANCE_CHANGED')
            stat = os.fstat(fd)
            record = dict(schema='DTC_AG7_OWN_LOCK_V1', goal=GOAL,
                canonical_task='/root', authority_owner='BA',
                pid=owner['pid'], start_ticks=owner['start_ticks'],
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                registration_sha256=self.digest, lock_path=str(LOCK),
                lock_device=stat.st_dev, lock_inode=stat.st_ino,
                acquired_monotonic_ns=time.monotonic_ns())
            raw = (json.dumps(record, sort_keys=True) + '\n').encode()
            require(len(raw) <= 4096 and os.write(fd, raw) == len(raw),
                    'AG7_OWN_LOCK_RECORD_NOT_COMPLETE')
            os.fsync(fd)
            self.fd, self.lock_record = fd, record
            self.verify_lock()
            yield dict(record)
        finally:
            self.fd = None
            os.close(fd)  # release only own descriptor; retain immutable record.

    def verify_lock(self):
        require(self.fd is not None and self.lock_record is not None,
                'AG7_EXCLUSIVE_OWN_LOCK_REQUIRED')
        live = self._verify_self()
        fdstat, pathstat = os.fstat(self.fd), os.stat(LOCK, follow_symlinks=False)
        require((fdstat.st_dev, fdstat.st_ino) ==
                (pathstat.st_dev, pathstat.st_ino) ==
                (self.lock_record['lock_device'], self.lock_record['lock_inode']),
                'AG7_OWN_LOCK_PATH_OR_INODE_REPLACED')
        require(json.loads(LOCK.read_text()) == self.lock_record and
                live['pid'] == self.lock_record['pid'] and
                live['start_ticks'] == self.lock_record['start_ticks'],
                'AG7_OWN_LOCK_RECORD_OR_HOLDER_CHANGED')
        kernel = Path('/proc/self/fdinfo', str(self.fd)).read_text()
        require('FLOCK' in kernel and 'WRITE' in kernel and
                os.readlink('/proc/self/fd/' + str(self.fd)) == str(LOCK),
                'AG7_OWN_EXCLUSIVE_KERNEL_FLOCK_NOT_HELD')
        return dict(self.lock_record)

    def release_for_finite_wait(self):
        """Unlock only this controller's own descriptor; retain immutable record."""
        self.verify_lock()
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        kernel=Path('/proc/self/fdinfo',str(self.fd)).read_text()
        require('FLOCK' not in kernel,'PRODUCTION_FLOCK_NOT_RELEASED_FOR_WAIT')
        self.finite_wait_unlocked=True
        return dict(pid=self.owner['pid'],start_ticks=self.owner['start_ticks'],
            monotonic_ns=time.monotonic_ns(),kernel_fdinfo=kernel,production_flock_held=False)

    def reacquire_after_finite_wait(self):
        require(getattr(self,'finite_wait_unlocked',False) is True and self.fd is not None,
            'NOT_OWN_APPROVED_FINITE_WAIT')
        self._validate_registration();self._verify_self()
        fdstat,pathstat=os.fstat(self.fd),os.stat(LOCK,follow_symlinks=False)
        require((fdstat.st_dev,fdstat.st_ino)==(pathstat.st_dev,pathstat.st_ino)==
            (self.lock_record['lock_device'],self.lock_record['lock_inode']) and
            json.loads(LOCK.read_text())==self.lock_record and
            os.readlink('/proc/self/fd/'+str(self.fd))==str(LOCK),'OWN_WAIT_LOCK_INSTANCE_CHANGED')
        fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self.finite_wait_unlocked=False
        return self.verify_lock()

    def bind_review(self, local_ownership, peer_provider=lambda: [],
                    external_launch_view_provider=None):
        """Unchanged full-scope scan/history/unknowns plus exact own role/lock.

        Caller still supplies the existing event-confirmed Ownership instance;
        this adapter never discovers/adopts a simulator or grants a signal right.
        """
        proc, frozen_snapshot, frozen_review = self.legacy.bind_frozen_procedures()
        snapshot = _clone_raw_only(frozen_snapshot)
        legacy_review = _clone_raw_only(frozen_review)
        shared = self.shared.SharedOwnership(local_ownership, self.identity)
        contracts = json.loads((FROZEN/'EXACT_EXTERNAL_ROLE_CONTRACTS.json').read_text())
        legacy_sources = self.legacy.exact_legacy_output_sources()

        def review_now(own_owner=None):
            self._validate_registration()
            self.verify_lock()
            require(own_owner is None or
                    (own_owner['pid'], own_owner['start_ticks']) ==
                    (self.owner['pid'], self.owner['start_ticks']),
                    'AG7_REVIEW_CANNOT_LEND_OTHER_OWNER_IDENTITY')
            shared.update_peers(peer_provider())
            current = snapshot()
            result = self.shared.review_with_exact_roles(
                current, legacy_review, self.owner, shared,
                contracts['roles'] + [self.role], self.identity, self.legacy.DATA,
                legacy_sources,
                external_launch_view=(external_launch_view_provider()
                    if external_launch_view_provider else None),
                require_external_launch_binding=True,
                callback_sample_id=str(time.monotonic_ns()))
            own_locks = [r for r in current['FLOCKs'] if r['path'] == str(LOCK)]
            require(len(own_locks) == 1 and
                    own_locks[0]['pid'] == self.owner['pid'] and
                    own_locks[0]['start_ticks'] == self.owner['start_ticks'] and
                    own_locks[0]['fd'] == str(self.fd),
                    'AG7_EXACT_SELF_FLOCK_NOT_UNIQUE_IN_ALL_SCOPE_SNAPSHOT')
            return current, dict(result, explicit_canonical_BA_root_registration=self.digest,
                own_AG7_lock_verified=True, old_locks_modified=False,
                unknown_controls_or_locks_exempted=False,
                all_project_resource_population_unchanged=True,
                adapter_alone_grants_simulation_permission=False)
        return review_now
