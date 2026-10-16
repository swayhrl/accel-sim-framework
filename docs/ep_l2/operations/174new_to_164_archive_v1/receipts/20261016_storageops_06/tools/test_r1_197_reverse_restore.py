import copy
import json
from pathlib import Path
import unittest

import r1_197_reverse_restore_stage as reverse


class ExactReverseGuards(unittest.TestCase):
    def setUp(self):
        here = Path(__file__).resolve().parent
        base = here if (here/'SOURCE_R1_197_REVERSE_BATCH_PLAN_R10.json').exists() else here.parent
        self.plan_raw = (base/'SOURCE_R1_197_REVERSE_BATCH_PLAN_R10.json').read_bytes()
        self.manifest_raw = (base/'SOURCE_R1_197_EXACT_MANIFEST_R10.tsv').read_bytes()
        self.plan, self.rows = reverse.load_scope(self.plan_raw, self.manifest_raw)
        self.ack = dict(source_action='SOURCE_KEEP', source_release_authorized=False,
            source_released_bytes=0, target_window_decision_sha256=reverse.DECISION_SHA,
            reverse_plan_sha256=reverse.PLAN_SHA, exact_scope_manifest_sha256=reverse.MANIFEST_SHA,
            canonical_four_column_manifest_sha256=reverse.CANONICAL_SHA,
            native_staging_root=reverse.NATIVE)

    def test_real_frozen_scope_is_exact_197_ten_batches(self):
        self.assertEqual(len(self.rows), 197)
        self.assertEqual(sum(b['logical_bytes'] for b in self.plan['batches']), 4464202341)
        self.assertEqual(self.plan['batches'][0]['logical_bytes'], 470083881)

    def test_changed_plan_bytes_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'plan SHA'):
            reverse.load_scope(self.plan_raw+b'\n', self.manifest_raw)

    def test_changed_manifest_bytes_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'manifest SHA'):
            reverse.load_scope(self.plan_raw, self.manifest_raw+b'\n')

    def test_duplicate_across_batches_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['batches'][1]['files'][0] = copy.deepcopy(plan['batches'][0]['files'][0])
        with self.assertRaisesRegex(RuntimeError, 'duplicate'):
            reverse.validate_membership(plan, self.rows)

    def test_numeric_uid_substitution_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['batches'][0]['files'][0]['uid'] += 1
        with self.assertRaisesRegex(RuntimeError, 'metadata substitution'):
            reverse.validate_membership(plan, self.rows)

    def test_parent_traversal_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['batches'][0]['files'][0]['relative_path'] = '../unlisted.vvp'
        with self.assertRaisesRegex(RuntimeError, 'unsafe'):
            reverse.validate_membership(plan, self.rows)

    def test_batch_order_substitution_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['batches'][0]['index'] = 1
        with self.assertRaisesRegex(RuntimeError, 'ordinal'):
            reverse.validate_membership(plan, self.rows)

    def test_oversized_batch_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['batches'][0]['logical_bytes'] = 512*1024**2 + 1
        with self.assertRaisesRegex(RuntimeError, 'size mismatch'):
            reverse.validate_membership(plan, self.rows)

    def test_exact_source_ack_is_valid(self):
        reverse.validate_acceptance(self.ack, reverse.DECISION_SHA)

    def test_source_release_authority_is_rejected(self):
        self.ack['source_release_authorized'] = True
        with self.assertRaisesRegex(RuntimeError, 'cannot authorize'):
            reverse.validate_acceptance(self.ack, reverse.DECISION_SHA)

    def test_native_path_substitution_rejected(self):
        self.ack['native_staging_root'] = reverse.SOURCE
        with self.assertRaisesRegex(RuntimeError, 'native root mismatch'):
            reverse.validate_acceptance(self.ack, reverse.DECISION_SHA)

    def test_wrong_target_decision_rejected(self):
        self.ack['target_window_decision_sha256'] = '0'*64
        with self.assertRaisesRegex(RuntimeError, 'exact target decision'):
            reverse.validate_acceptance(self.ack, reverse.DECISION_SHA)


if __name__ == '__main__':
    unittest.main()
