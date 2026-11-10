"""CPU-only regression for the uncreated true164 namespace admission check."""
import unittest

import mechanism_outbox
import route_guard
from route_authority import Hold


class ArchiveCapacityR0(unittest.TestCase):
    def test_uncreated_namespace_reads_existing_true164_parent(self):
        value = route_guard.archive_capacity(mechanism_outbox.NAS, 2 * 1024 * 1024)
        self.assertEqual(value['status'], 'TRUE164_CAPACITY_PASS')
        self.assertFalse(value['target_namespace_exists'])
        self.assertEqual(value['mount'], route_guard.TRUE164)
        self.assertGreater(value['free_bytes'], value['required_bytes'])

    def test_outside_namespace_rejected(self):
        with self.assertRaisesRegex(Hold, 'ARCHIVE_OUTSIDE_TRUE164_MOUNT'):
            route_guard.archive_capacity('/tmp/dtc-short-collect-escape', 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
