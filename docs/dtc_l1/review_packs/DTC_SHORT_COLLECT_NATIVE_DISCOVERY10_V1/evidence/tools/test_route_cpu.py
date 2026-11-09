"""CPU-only synthetic qualification. No production registry or model is touched."""
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid

import route_authority as a
import route_lease as lease


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(a.encoded(value))


class RouteCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dtc_short_collect_R0_')
        self.root = Path(self.temp.name)
        self.control = self.root / 'control'
        (self.control / 'specs').mkdir(parents=True)
        (self.control / 'qualification_ledger').mkdir()
        (self.root / 'results').mkdir()
        self.engine = self.root / 'tools' / 'engine.py'
        self.engine.parent.mkdir()
        self.engine.write_text('# CPU fixture engine\n')
        cells, specs = [], {}
        for program in a.STAGES['C1']:
            for mode in ('OFF', 'ON'):
                cohort = f'E2-DTCSHORT-C1-{program}-{mode}'
                path = self.control / 'specs' / (cohort + '.json')
                spec = {
                    'request': 'DTC_SHORT_COLLECT_C1_FIXTURE_V1',
                    'cohort': cohort, 'program': program, 'mode': mode,
                    'input_sha256': a.INPUTS[program], 'core_commit': a.CORE,
                    'framework_commit': a.FRAMEWORK, 'binary_sha256': a.BINARY,
                    'libcudart_sha256': a.LIB,
                }
                put(path, spec)
                specs[cohort] = a.sha(path)
                cells.append({'cohort': cohort, 'program': program, 'mode': mode,
                              'input_sha256': a.INPUTS[program],
                              'spec_path': str(path.relative_to(self.root)),
                              'spec_sha256': a.sha(path)})
        self.request = self.control / 'REQUEST_C1.json'
        pins = self.control / 'SOURCE_PINS.json'
        runtime = self.control / 'RUNTIME_BINDINGS.json'
        plan = self.control / 'plans' / 'C1_PLAN.json'
        put(pins, {'fixture': 'source'})
        put(runtime, {'fixture': 'runtime'})
        request = {
            'contract_commit': a.CONTRACT, 'candidate_core': a.CORE,
            'framework_commit': a.FRAMEWORK, 'binary_sha256': a.BINARY,
            'libcudart_sha256': a.LIB, 'stage': 'C1', 'budget': 4,
            'request_id': 'DTC_SHORT_COLLECT_C1_FIXTURE_V1',
            'cells': cells, 'admitted_specs': specs,
            'plan_path': str(plan.relative_to(self.root)),
            'reserved_write_bytes': 1024 * 1024,
            'runtime_sha256': a.sha(runtime), 'source_pins_sha256': a.sha(pins),
        }
        planned = {key: request[key] for key in ('contract_commit', 'candidate_core',
            'framework_commit', 'binary_sha256', 'libcudart_sha256', 'stage',
            'budget', 'request_id', 'reserved_write_bytes', 'runtime_sha256',
            'source_pins_sha256')}
        planned.update(cells=cells, limits_per_cell=None,
                       source_pins_path=str(pins.relative_to(self.root)),
                       runtime_binding_path=str(runtime.relative_to(self.root)))
        put(plan, planned)
        request['plan_sha256'] = a.sha(plan)
        put(self.request, request)
        self.registry = self.control / 'NATIVE_SCIENCE_REGISTRY.json'
        self.epoch = self.control / 'CURRENT_SCIENCE_EPOCH.json'
        self.lock = self.control / 'REGISTRY_UPDATE.lock'
        self.lock.touch()
        self.peer = {
            'request': 'HISTORICAL_PEER', 'state': 'RUNNING', 'budget': 7,
            'remaining': 3, 'consumed': {'old': {'uuid': str(uuid.uuid4())}},
            'admitted_specs': {'old': 'oldsha'}, 'reserved_write_bytes': 42,
        }
        put(self.registry, {'schema': 'CPU_FIXTURE', 'epoch': 2,
                            'registered_future_requests': {'HISTORICAL_PEER': self.peer},
                            'new_scientific_budget_remaining': 3,
                            'old_source_history': {'do_not_touch': True}})
        put(self.epoch, {'epoch': 2, 'state': 'NATIVE_SCIENCE_ACTIVE',
                         'native_registry_sha256': a.sha(self.registry),
                         'new_budget_remaining': 3})
        self.store = a.RegistryStore(self.registry, self.epoch, self.lock)

    def tearDown(self):
        self.temp.cleanup()

    def register(self):
        return self.store.register(self.request, self.root, self.engine)

    def consume(self, cohort=None, **extra):
        if cohort is None:
            cohort = a.read(self.request)['cells'][0]['cohort']
        return self.store.consume(self.request, self.root, cohort,
                                  self.control / 'qualification_ledger', self.root / 'results',
                                  lease_check=lambda: True,
                                  preflight_check=lambda: True,
                                  locked_admission_check=lambda registry, q: True,
                                  **extra)

    def test_append_only_registration_and_one_use_intent(self):
        self.register()
        registered, epoch = self.store.snapshot()
        self.assertEqual(registered['registered_future_requests']['HISTORICAL_PEER'], self.peer)
        self.assertEqual(epoch['native_registry_sha256'], a.sha(self.registry))
        cohort = a.read(self.request)['cells'][0]['cohort']
        intent = self.consume(cohort)
        self.assertEqual(intent['consumed_before_launcher_fork'], 1)
        self.assertEqual(intent['automatic_retry'], False)
        q = self.store.snapshot()[0]['registered_future_requests'][intent['request']]
        self.assertEqual(q['remaining'], 3)
        self.assertEqual(q['consumed'][cohort]['intent_sha256'],
                         a.sha(self.control / 'qualification_ledger' / (cohort + '.INTENT.json')))
        self.assertEqual(self.store.snapshot()[0]['registered_future_requests']['HISTORICAL_PEER'], self.peer)
        with self.assertRaisesRegex(a.Hold, 'CELL_CONSUMED_OR_SEALED|INTENT_ALREADY_EXISTS'):
            self.consume(cohort)
        self.assertEqual(self.store.snapshot()[0]['registered_future_requests'][intent['request']]['remaining'], 3)

    def test_bad_matrix_and_old_prefix_fail_before_registry(self):
        request = a.read(self.request)
        request['cells'][0]['input_sha256'] = 'bad'
        put(self.request, request)
        with self.assertRaisesRegex(a.Hold, 'INPUT_SHA_DRIFT'):
            self.register()

    def test_plan_bytes_and_exact_cell_join_rejected(self):
        request = a.read(self.request)
        plan = self.root / request['plan_path']
        plan.write_bytes(plan.read_bytes() + b' ')
        with self.assertRaisesRegex(a.Hold, 'EXACT_PLAN_FILE_SHA_REQUIRED'):
            self.register()
        plan.write_bytes(plan.read_bytes()[:-1])
        altered = a.read(plan)
        altered['cells'][0]['mode'] = 'ON'
        put(plan, altered)
        request['plan_sha256'] = a.sha(plan)
        put(self.request, request)
        with self.assertRaisesRegex(a.Hold, 'PLAN_CELL_REQUEST_DRIFT:mode'):
            self.register()
        self.assertNotIn('DTC_SHORT_COLLECT_C1_FIXTURE_V1',
                         self.store.snapshot()[0]['registered_future_requests'])

    def test_true_same_pid_different_fd_exclusion(self):
        with self.lock.open('r+b') as first, self.lock.open('r+b') as second:
            fcntl.flock(first, fcntl.LOCK_EX | fcntl.LOCK_NB)
            actual = lease.actual_flock(self.lock, os.getpid(), first.fileno())
            self.assertEqual(actual['fd'], first.fileno())
            with self.assertRaises(BlockingIOError):
                fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(a.Hold, 'REGISTRY_LOCK_BUSY'):
                self.store.snapshot()

    def test_ex_mutator_does_not_recurse_to_shared_reader(self):
        self.register()
        cohort = a.read(self.request)['cells'][0]['cohort']
        with self.assertRaisesRegex(a.Hold, 'REGISTRY_LOCK_BUSY'):
            self.store.consume(self.request, self.root, cohort,
                               self.control / 'qualification_ledger', self.root / 'results',
                               lease_check=lambda: True, preflight_check=lambda: True,
                               locked_admission_check=lambda registry, q: self.store.snapshot())
        self.assertFalse((self.control / 'qualification_ledger' / (cohort + '.INTENT.json')).exists())

    def test_before_registry_failure_keeps_durable_intent_no_retry(self):
        self.register()
        cohort = a.read(self.request)['cells'][0]['cohort']
        self.store._write_locked = lambda *args: (_ for _ in ()).throw(RuntimeError('injected IO failure'))
        with self.assertRaisesRegex(RuntimeError, 'injected IO failure'):
            self.consume(cohort)
        intent_path = self.control / 'qualification_ledger' / (cohort + '.INTENT.json')
        self.assertTrue(intent_path.exists())
        self.assertEqual(self.store.snapshot()[0]['registered_future_requests'][a.read(self.request)['request_id']]['remaining'], 4)
        with self.assertRaisesRegex(a.Hold, 'INTENT_ALREADY_EXISTS'):
            self.consume(cohort)

    def test_live_release_required_and_independent_identity(self):
        live = a.RegistryStore(self.registry, self.epoch, self.lock, fixture_only=False)
        with self.assertRaisesRegex(a.Hold, 'LIVE_R0_RELEASE_REQUIRED'):
            live.register(self.request, self.root, self.engine)


if __name__ == '__main__':
    unittest.main(verbosity=2)
