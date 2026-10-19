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
            20: dict(pid=20, start_ticks=200, state='t', tracer_pid=10),
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
            self.roles, lambda p: self.rows[p], DATA, self.output_sources)

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
                result = exact_cpu_role(row, [role], lambda p: self.rows[p])
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
        self.assertIsNone(exact_cpu_role(row, [role], lambda p: self.rows[p]))
        self.assertEqual(self.verdict([row])['status'], 'STOP_AUTHORITY_NOT_CLOSED')

    def test_changed_source_expected_hash_rejected(self):
        role = copy.deepcopy(self.roles[0])
        role['source_sha256'][next(iter(role['source_sha256']))] = '0'*64
        row = dict(self.process(30), is_simulator=False, argv=role['argvs'][0],
                   exe=role['executable'], cwd=role['cwd'])
        with self.assertRaisesRegex(AuthorityReject, 'SOURCE_CHANGED'):
            exact_cpu_role(row, [role], lambda p: self.rows[p])

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SharedAuthorityCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'cases': result.testsRun, 'successful': result.wasSuccessful(),
                      'scope': 'ACTUAL_FROZEN_REVIEW_AND_ADAPTER_DECLARED_SYNTHETIC_PROCESS_ROWS',
                      'real_role_observation': False, 'global_authority_qualified': False,
                      'processes_created': 0, 'signals': 0, 'simulation_starts': 0}))
    sys.exit(0 if result.wasSuccessful() else 1)
