"""Read-only CPU qualification of prepared source and runtime pins."""
import copy
import json
from pathlib import Path
import unittest

import route_guard
from route_authority import Hold

ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
SPEC = ROOT / 'control/prepared_specs/C1/E2-DTCSHORT-C1-GESUMMV-OFF-V1.json'


class GuardCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_bytes())

    def test_frozen_runtime_binding(self):
        value = route_guard.verify_runtime(self.spec)
        self.assertEqual(value['status'], 'FROZEN_RUNTIME_AND_OPTIONS_PASS')
        self.assertEqual(value['options'], 271)

    def test_frozen_genuine164_input(self):
        value = route_guard.verify_input(self.spec)
        self.assertEqual(value['status'], 'FROZEN_FULL_BODY_SHA_BOUND_GENUINE164_INPUT')
        self.assertEqual(value['kernels'], 1)

    def test_bad_switch_and_bad_lib_rejected(self):
        bad = copy.deepcopy(self.spec)
        bad['expected_options']['-gpgpu_dtc_l1_short_collect_first'] = ['1']
        with self.assertRaisesRegex(Hold, 'CANDIDATE_SWITCH_DRIFT'):
            route_guard.verify_runtime(bad)
        bad = copy.deepcopy(self.spec)
        bad['libcudart_sha256'] = '0' * 64
        with self.assertRaisesRegex(Hold, 'FROZEN_BINARY_OR_LIB_DRIFT'):
            route_guard.verify_runtime(bad)

    def test_bad_input_identity_rejected(self):
        bad = copy.deepcopy(self.spec)
        bad['input_sha256'] = '0' * 64
        with self.assertRaisesRegex(Hold, 'INPUT_DIGEST_DRIFT'):
            route_guard.verify_input(bad)

    def test_lock_held_helper_is_pure_and_fail_closed(self):
        q = {'state': 'ARMED', 'remaining': 1, 'budget': 1,
             'consumed': {}, 'admitted_specs': {'cell': 'sha'}}
        self.assertTrue(route_guard.locked_admission({}, q, 'cell', 'sha'))
        with self.assertRaisesRegex(Hold, 'LOCKED_COHORT_SPEC'):
            route_guard.locked_admission({}, q, 'cell', 'bad')


if __name__ == '__main__':
    unittest.main(verbosity=2)
