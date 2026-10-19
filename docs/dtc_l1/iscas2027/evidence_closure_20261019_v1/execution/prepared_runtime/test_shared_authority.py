"""PREPARED_NOT_TESTED. Actual adapter/frozen review, declared synthetic rows.
No fork, ptrace, signal, full snapshot, performance model or real PID reuse.
File and executable hashes are actual; argv, PID and parent-event rows are
synthetic fixtures. These tests cannot establish live external-role coverage.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from shared_authority import (AuthorityReject, SharedOwnership, exact_cpu_role,
                              review_with_exact_roles)
from legacy_authority_runtime import (DATA, bind_frozen_procedures,
                                      exact_legacy_output_sources)

class LocalFixture:
    tracer = 900001
    confirmed = {}
    pending = {}
    def classify(self, row):
        return 'CONFIRMED' if row['pid'] in self.confirmed else 'UNKNOWN'

class SharedAuthorityCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy = staticmethod(bind_frozen_procedures()[2])
        cls.roles = json.loads((HERE / 'EXACT_EXTERNAL_ROLE_CONTRACTS.json').read_text())['roles']
        cls.output_sources = exact_legacy_output_sources()

    def setUp(self):
        self.clock = [10.0]
        self.rows = {
            20: dict(pid=20, start_ticks=200, state='t', tracer_pid=10, tgid=20),
            10: dict(pid=10, start_ticks=100, state='S', tracer_pid=0),
            30: dict(pid=30, start_ticks=300, state='R', tracer_pid=0)}
        self.view = SharedOwnership(LocalFixture(), lambda p: self.rows[p], lambda: self.clock[0])
        self.peer = dict(guard=self.rows[10], age_seconds=.1,
                         registered_source_and_launch_verified=True,
                         ownership={'confirmed': [self.rows[20]], 'pending': []})
        self.view.update_peers([self.peer])

    def process(self, pid=20):
        return dict(self.rows[pid], is_simulator=True, argv=['/synthetic/accel-sim.out'],
                    exe='/synthetic/accel-sim.out', cwd='/synthetic', comm='accel-sim.out')

    def verdict(self, processes, owner=None):
        snapshot = {'processes': processes, 'FLOCKs': [], 'known_identity_checks': []}
        return review_with_exact_roles(snapshot, self.legacy, owner, self.view,
            self.roles, lambda p: self.rows[p], DATA, self.output_sources,
            process_reader=lambda pid: next(r for r in processes if r['pid'] == pid))

    def test_confirmed_peer_uses_frozen_review(self):
        self.assertEqual(self.verdict([self.process()])['status'],
                         'PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY')

    def test_unconfirmed_stopped_peer_never_passes(self):
        self.peer['ownership']['confirmed'] = []
        self.assertEqual(self.verdict([self.process()])['status'],
                         'PENDING_QUARANTINED_NO_AUTHORITY_PASS')

    def test_unconfirmed_peer_finite_deadline(self):
        self.peer['ownership']['confirmed'] = []
        self.view.classify(self.process())
        self.clock[0] += 2.01
        with self.assertRaisesRegex(AuthorityReject, 'CONFIRMATION_TIMEOUT'):
            self.view.classify(self.process())

    def test_peer_pending_prevents_pass_without_candidate_row(self):
        self.peer['ownership']['pending'] = [{'identity': self.rows[20]}]
        self.assertEqual(self.verdict([])['status'], 'PENDING_QUARANTINED_NO_AUTHORITY_PASS')

    def test_stale_peer_rejected(self):
        self.peer['age_seconds'] = 2.01
        with self.assertRaisesRegex(AuthorityReject, 'SNAPSHOT_STALE'):
            self.verdict([self.process()])

    def test_changed_peer_guard_instance_rejected(self):
        self.peer['guard'] = dict(self.rows[10], start_ticks=99)
        with self.assertRaisesRegex(AuthorityReject, 'GUARD_PID_REUSED'):
            self.verdict([self.process()])

    def test_changed_confirmed_child_instance_rejected(self):
        self.peer['ownership']['confirmed'] = [dict(self.rows[20], start_ticks=199)]
        with self.assertRaisesRegex(AuthorityReject, 'CONFIRMED_PID_REUSED'):
            self.verdict([self.process()])

    def test_unregistered_simulator_or_helper_is_unknown(self):
        self.assertEqual(self.verdict([self.process(30)])['status'], 'STOP_AUTHORITY_NOT_CLOSED')

    def test_historic_child_fallback_cannot_promote_unknown(self):
        owner = {'pid': 900001, 'start_ticks': 1, 'child_pid': 30, 'child_start_ticks': 300}
        self.assertEqual(self.verdict([self.process(30)], owner)['status'], 'STOP_AUTHORITY_NOT_CLOSED')

    def test_each_exact_external_source_contract(self):
        for role in self.roles:
            for argv in role['argvs']:
                row = dict(self.process(30), is_simulator=False, argv=argv,
                           exe=role['executable'], cwd=role['cwd'])
                result = exact_cpu_role(row, [role], lambda p: self.rows[p], lambda pid: row)
                self.assertEqual(result, role['name'])
                verdict = self.verdict([row])
                self.assertEqual(len(verdict['exact_external_CPU_controls']), 1)
                self.assertEqual(verdict['original_process_count'], 1)
                self.assertEqual(verdict['classification_process_count'], 0)
                self.assertFalse(verdict['simulation_permission_from_CPU_roles'])

    def test_extra_argument_is_not_role_permission(self):
        role = self.roles[0]
        row = dict(self.process(30), is_simulator=False, argv=role['argvs'][0]+['--start-simulation'],
                   exe=role['executable'], cwd=role['cwd'])
        self.assertIsNone(exact_cpu_role(row, [role], lambda p: self.rows[p], lambda pid: row))
        self.assertEqual(self.verdict([row])['status'], 'STOP_AUTHORITY_NOT_CLOSED')

    def test_changed_source_expected_hash_rejected(self):
        role = copy.deepcopy(self.roles[0])
        role['source_sha256'][next(iter(role['source_sha256']))] = '0'*64
        row = dict(self.process(30), is_simulator=False, argv=role['argvs'][0],
                   exe=role['executable'], cwd=role['cwd'])
        with self.assertRaisesRegex(AuthorityReject, 'SOURCE_CHANGED'):
            exact_cpu_role(row, [role], lambda p: self.rows[p], lambda pid: row)

    def test_current_role_attributes_cannot_use_stale_snapshot(self):
        role = self.roles[0]
        row = dict(self.process(30), is_simulator=False, argv=role['argvs'][0],
                   exe=role['executable'], cwd=role['cwd'])
        for changed in [dict(row, argv=row['argv']+['--unexpected']),
                        dict(row, cwd='/changed'), dict(row, exe='/changed')]:
            with self.assertRaisesRegex(AuthorityReject, 'CURRENT_ATTRIBUTES_CHANGED'):
                exact_cpu_role(row, [role], lambda p: self.rows[p], lambda pid: changed)

    def test_peer_thread_group_and_retired_generation_rejected(self):
        for changed, reason in [({'tgid': 999}, 'THREAD_GROUP_CHANGED'),
                                ({'tracer_pid': 999}, 'TRACER_CHANGED')]:
            self.peer['ownership']['confirmed'] = [dict(self.rows[20], **changed)]
            with self.assertRaisesRegex(AuthorityReject, reason):
                self.verdict([self.process()])
        self.peer['ownership']['confirmed'] = [dict(self.rows[20])]
        self.peer['ownership']['retired'] = [dict(self.rows[20])]
        with self.assertRaisesRegex(AuthorityReject, 'RETIRED_INSTANCE'):
            self.verdict([self.process()])

if __name__ == '__main__':
    import hashlib
    import io
    sys.path.insert(0,str(HERE/'vendor'))
    from cpu_admission_v2 import CPUAdmission, execution_binding
    registration_path=HERE.parent/'CPU_SHARED_AUTHORITY_REGISTRATION_V2.json'
    registration=json.loads(registration_path.read_text())
    if registration['status']!='REGISTERED_FOR_SHARED_OBSERVER_CPU_QUALIFICATION_ONLY':
        raise ValueError('EXACT_NEGATIVE_CPU_RELEASE_REQUIRED')
    for rel,digest in registration['prepared_source_sha256'].items():
        if hashlib.sha256((HERE/rel).read_bytes()).hexdigest()!=digest:
            raise ValueError('NEGATIVE_SOURCE_CHANGED:'+rel)
    for path,digest in registration['runtime_sha256'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:
            raise ValueError('NEGATIVE_RUNTIME_CHANGED:'+path)
    if not CPUAdmission(registration,registration['negative_gate_roles']).admit(Path(registration['negative_admission_output'])):
        print('WAIT_RESOURCE_OR_AUTHORITY_NO_TESTS_STARTED',flush=True)
        sys.exit(3)
    output=Path(registration['negative_receipt_path']).parent/'negative'
    output.mkdir(parents=True,exist_ok=False)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SharedAuthorityCases)
    stderr=io.StringIO()
    result=unittest.TextTestRunner(stream=stderr,verbosity=2).run(suite)
    summary={'cases':result.testsRun,'successful':result.wasSuccessful(),
             'scope':'ACTUAL_FROZEN_REVIEW_AND_ADAPTER_DECLARED_SYNTHETIC_PROCESS_ROWS',
             'real_role_observation':False,'global_authority_qualified':False,
             'processes_created':0,'signals':0,'simulation_starts':0}
    stdout=json.dumps(summary)+'\n'
    (output/'stdout').write_text(stdout);(output/'stderr').write_text(stderr.getvalue())
    receipt=dict(summary,returncode=0 if result.wasSuccessful() else 1,
                 **execution_binding(registration_path,registration),
                 test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 stdout_sha256=hashlib.sha256((output/'stdout').read_bytes()).hexdigest(),
                 stderr_sha256=hashlib.sha256((output/'stderr').read_bytes()).hexdigest(),output=str(output))
    target=Path(registration['negative_receipt_path'])
    with target.open('x') as stream:stream.write(json.dumps(receipt,indent=2)+'\n')
    sys.stdout.write(stdout);sys.stderr.write(stderr.getvalue())
    sys.exit(receipt['returncode'])
