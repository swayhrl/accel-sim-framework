"""Small admission/receipt regressions; never invoke CMake or the simulator."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('lane1_builder', Path(__file__).with_name('build_r0_1.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
GIB = 1024**3
POLICY = {'min_disk_free_bytes': 48 * GIB, 'min_available_memory_bytes': 64 * GIB}
ENOUGH = {'disk_free_bytes': 50 * GIB, 'available_memory_bytes': 72 * GIB}


class AdmissionTests(unittest.TestCase):
    def test_exact_admission_boundary(self):
        self.assertIsNone(builder.admission_hold(POLICY, ENOUGH, {}))

    def test_growth_is_additional_to_floor(self):
        self.assertIn('DISK', builder.admission_hold(POLICY,
            dict(ENOUGH, disk_free_bytes=50 * GIB - 1), {}))

    def test_lowered_shared_policy_cannot_lower_frozen_floor(self):
        self.assertIn('DISK', builder.admission_hold(dict(POLICY, min_disk_free_bytes=1),
            dict(ENOUGH, disk_free_bytes=49 * GIB), {}))

    def test_stricter_policy_is_respected(self):
        self.assertIn('DISK', builder.admission_hold(dict(POLICY, min_disk_free_bytes=51 * GIB), ENOUGH, {}))

    def test_memory_reservation_preserves_floor(self):
        self.assertIn('MEMORY', builder.admission_hold(POLICY,
            dict(ENOUGH, available_memory_bytes=72 * GIB - 1), {}))

    def test_existing_build_refuses_duplicate(self):
        self.assertIn('DUPLICATE', builder.admission_hold(POLICY, ENOUGH, {'other': {}}))

    def test_exact_matrix(self):
        rows = builder.repair_commands(Path('/build'), Path('/core'))
        self.assertEqual(21, len(rows))
        self.assertEqual(21, len({name for name, _ in rows}))
        for mode in (1, 2):
            for capacity in (8, 16):
                names = {f'host_prefill_{mode}_{capacity}', f'partition_{mode}_{capacity}',
                    f'physical_clock_{mode}_{capacity}_0', f'physical_clock_{mode}_{capacity}_4096',
                    f'warm_clock_{mode}_{capacity}'}
                self.assertTrue(names <= {name for name, _ in rows})
        self.assertEqual('ft_directed', rows[-1][0])

    def test_full_entry_hold_never_invokes_compiler_or_lease(self):
        # Inject a fake registry/resource view. The live registry is never locked
        # or mutated; the main() path must return before any subprocess launch.
        class FakeRegistry:
            def __init__(self, root):
                pass

            @contextlib.contextmanager
            def locked(self):
                yield {'authority_host': 'fixture', 'hosts': {'fixture': POLICY}, 'resource_leases': {}}

            def build_lease(self, *args, **kwargs):
                raise AssertionError('resource hold must not claim a lease')

        registry = types.ModuleType('registry')
        registry.Registry = FakeRegistry
        registry.ACTIVE = {'RESERVED', 'RUNNING'}
        registry.local_resources = lambda: dict(ENOUGH, disk_free_bytes=48 * GIB)
        registry.process_identity = lambda pid: {'pid': pid}
        fw = Path(builder.__file__).resolve().parents[3]
        core = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r0-1')
        def fake_head(path):
            if path == core:
                return builder.CORE_CANDIDATE
            return 'fixture-fw' if path == fw else builder.PYBIND11_COMMIT
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'hold'
            with patch.dict(sys.modules, registry=registry), \
                 patch.object(builder, 'FRAMEWORK_ROOT', fw), \
                 patch.object(builder, 'head', side_effect=fake_head), \
                 patch.object(builder.subprocess, 'check_output', return_value=b''), \
                 patch.object(builder.subprocess, 'Popen', side_effect=AssertionError('compiler must not start')), \
                 patch.object(sys, 'argv', ['builder', '--core', str(core), '--out', str(out), '--execute']):
                builder.main()
            receipt = json.loads((out / 'BUILD_AND_TEST_RECEIPT.json').read_text())
            self.assertIn('RESOURCE_HOLD', receipt['status'])
            self.assertFalse(receipt['compiler_started'])
            self.assertIsNone(receipt['binary_sha256'])
            self.assertEqual([], receipt['tests'])


class ReceiptTests(unittest.TestCase):
    def run_child(self, body, resources=ENOUGH, timeout=5, error=False, expected_code=None):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            report = {'disk_floor_bytes': 48 * GIB, 'memory_floor_bytes': 64 * GIB}
            def save():
                (out / 'receipt.json').write_text(json.dumps(report))
            arguments = ([sys.executable, '-u', '-c', body], 'child', out, dict(os.environ),
                report, save, lambda: resources, lambda pid: {'pid': pid}, timeout)
            if error:
                with self.assertRaises(RuntimeError):
                    builder.run_owned(*arguments)
            else:
                builder.run_owned(*arguments)
            record = json.loads((out / 'receipt.json').read_text())['commands'][0]
            self.assertEqual(builder.digest(out / 'child.log'), record['log_sha256'])
            self.assertIn('exit_code', record)
            if expected_code is not None:
                self.assertEqual(expected_code, record['exit_code'])
            if error:
                self.assertIn('error', record)
            return record

    def test_success_retains_hash(self):
        self.run_child("print('fixture success')", expected_code=0)

    def test_nonzero_exit_retains_hash(self):
        self.run_child("print('fixture failure'); raise SystemExit(23)", error=True, expected_code=23)

    def test_timeout_retains_hash_and_stops_only_owned_child(self):
        self.run_child('import time; time.sleep(5)', timeout=0.01, error=True)

    def test_disk_stop_retains_hash(self):
        record = self.run_child('import time; time.sleep(5)',
            resources=dict(ENOUGH, disk_free_bytes=48 * GIB - 1), error=True)
        self.assertIn('resource_stop', record)

    def test_memory_stop_retains_hash(self):
        record = self.run_child('import time; time.sleep(5)',
            resources=dict(ENOUGH, available_memory_bytes=64 * GIB - 1), error=True)
        self.assertIn('resource_stop', record)


if __name__ == '__main__':
    unittest.main()
