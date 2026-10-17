"""Controller safety checks; no simulator, lease, qualification or real registry writes."""
import copy
import json
from pathlib import Path
import signal
import socket
import tempfile
import unittest
from unittest.mock import patch

import continue_matrix as cm
from registry import PARALLEL, run_key
from review_r0_1_pair import p2_h0_candidates

SPEC_PATH = cm.H / 'parallel_unified_specs_execution_r2/S002_convolutionSeparable_S64.json'
SPEC = json.loads(SPEC_PATH.read_text())
KEY = run_key(SPEC['identity'])
CAMPAIGN = {'experiment_id': PARALLEL, 't0_unix': 1792236614.5007188,
            'deadline_unix': 1792323014.5007188, 'maximum_starts': 72}
POLICY = {'max_simulators': 4, 'max_cpu_units': 8, 'max_reserved_memory_bytes': 32*2**30,
          'max_result_bytes': 12*2**30, 'min_disk_free_bytes': 48*2**30,
          'min_available_memory_bytes': 64*2**30, 'default_run_output_limit_bytes': 2*2**30}


class Safety(unittest.TestCase):
    def test_never_relaunch_existing_states(self):
        for status in ['RUNNING', 'RESERVED', 'COMPLETE_VALID', 'FAILED', 'TIMEOUT', 'RESOURCE_LIMIT']:
            registry = {'runs': {KEY: {'identity': SPEC['identity'], 'status': status}}}
            self.assertEqual(cm.disposition(SPEC, registry, set()), status)

    def test_accepted_requires_valid_canonical_identity(self):
        registry = {'runs': {KEY: {'identity': SPEC['identity'], 'status': 'COMPLETE_VALID'}}}
        self.assertEqual(cm.disposition(SPEC, registry, {KEY}), 'ACCEPTED')
        registry['runs'][KEY]['status'] = 'FAILED'
        with self.assertRaises(ValueError):
            cm.disposition(SPEC, registry, {KEY})

    def test_identity_change_refused(self):
        identity = copy.deepcopy(SPEC['identity'])
        identity['binary_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            cm.disposition(SPEC, {'runs': {KEY: {'identity': identity, 'status': 'RUNNING'}}}, set())

    def test_cap_deadline_and_t0_no_reset(self):
        cm.validate_budget(CAMPAIGN, CAMPAIGN)
        for field in ['maximum_starts', 'deadline_unix', 't0_unix']:
            bad = dict(CAMPAIGN)
            bad[field] += 1
            with self.assertRaises(ValueError):
                cm.validate_budget(bad, CAMPAIGN)

    def test_legacy_default_memory_exactly_matches_registry(self):
        policy={'default_run_memory_bytes':8*2**30}
        self.assertEqual(cm.memory_reservation({},policy),8*2**30)
        self.assertEqual(cm.memory_reservation({'memory_reservation_bytes':None},policy),8*2**30)
        self.assertEqual(cm.memory_reservation({'memory_reservation_bytes':4*2**30},policy),4*2**30)
        with self.assertRaises(ValueError):
            cm.memory_reservation({'memory_reservation_bytes':0},policy)

    def test_p2_cannot_borrow_source_scope_or_withdrawn_baseline(self):
        spec = json.loads((cm.H / 'parallel_unified_specs_execution_r2/S007_convolutionSeparable_B16_BANKED.json').read_text())
        good = {'identity': spec['identity'], 'profile': 'B16_OFF', 'regime': 'H0', 'scientific_acceptance': 'CURRENT_ACCEPTED'}
        rows = [good]
        for field in ['core_source_commit', 'framework_source_commit', 'binary_sha256', 'trace_content_sha256', 'epoch_range', 'termination_contract']:
            bad = copy.deepcopy(good)
            bad['identity'][field] = 'OTHER'
            rows.append(bad)
        for field, value in [('profile', 'I_MEM_ALL_DATA'), ('regime', 'Q4'), ('scientific_acceptance', 'WITHDRAWN')]:
            bad = copy.deepcopy(good)
            bad[field] = value
            rows.append(bad)
        self.assertEqual(p2_h0_candidates(rows, spec, 'B16_BANKED'), [good])

    def controller_case(self, runs, accepted, expected, expired=False):
        registry = {'campaigns': {PARALLEL: CAMPAIGN}, 'runs': runs, 'resource_leases': {},
                    'hosts': {socket.gethostname(): POLICY}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue = {**CAMPAIGN, 'revision': 'TEST_FIXTURE', 'units': [{'id': 'fixture', 'kind': 'single',
                'specs': [{'path': str(SPEC_PATH), 'sha256': cm.digest(SPEC_PATH)}]}]}
            path = root / 'queue.json'
            path.write_text(json.dumps(queue))
            old_handler = signal.getsignal(signal.SIGTERM)
            try:
                with patch.object(cm, 'OUT', root), patch.object(cm, 'read_registry', return_value=registry), \
                     patch.object(cm, 'load_current_authority', return_value={'binding': {'test_fixture': True}}), \
                     patch.object(cm, 'deliver_checkpoint') as checkpoint, \
                     patch.object(cm, 'current_manifest', return_value={'rows': [{'run_key': k, 'scientific_acceptance': 'CURRENT_ACCEPTED', 'workload':SPEC['identity']['workload'],'binary_sha256':SPEC['identity']['binary_sha256'],'regime':'H0','profile':'S64'} for k in accepted]}), \
                     patch.object(cm.subprocess, 'check_output', return_value='test-fixture-source'), \
                     patch.object(cm.subprocess, 'Popen') as spawn, \
                     patch.object(cm.time, 'time', return_value=CAMPAIGN['deadline_unix'] + (1 if expired else -10)):
                    self.assertEqual(cm.main(path), 0)
                    spawn.assert_not_called()
                    checkpoint.assert_called_once()
                result = json.loads((root / 'TEST_FIXTURE_PROGRESS.json').read_text())
                self.assertEqual(result['status'], expected)
            finally:
                signal.signal(signal.SIGTERM, old_handler)

    def test_controller_skips_accepted_without_subprocess_or_lease(self):
        row = {'identity': SPEC['identity'], 'status': 'COMPLETE_VALID', 'experiment_id': PARALLEL}
        self.controller_case({KEY: row}, {KEY}, 'SELECTED_READY_MATRIX_CURRENT_ACCEPTED')

    def test_controller_real_attempt_history_reaches_cap_before_spawn(self):
        row = {'status': 'COMPLETE_VALID', 'experiment_id': PARALLEL, 'attempt_history': [{}]*71}
        self.controller_case({'another_key': row}, set(), 'START_CAP_BOUNDARY')

    def test_deadline_leaves_admitted_run_untouched(self):
        row = {'identity': SPEC['identity'], 'status': 'RUNNING', 'experiment_id': PARALLEL}
        self.controller_case({KEY: row}, set(), 'DEADLINE_NO_NEW_ACTION_EXISTING_RUNNERS_LEFT_NATURAL', expired=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
