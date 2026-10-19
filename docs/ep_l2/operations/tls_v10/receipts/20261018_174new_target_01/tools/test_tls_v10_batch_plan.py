"""Synthetic coverage/cap/identity tests; no source reads, staging or transfers."""
import copy
import unittest

import tls_v10_batch_plan as batch
import v9_transaction as v9


def manifest(sizes):
    rows = [dict(relative_path='file-%03d' % i, type='regular', nlink=1,
                 sha256=v9.digest(b'') if n == 0 else 'a' * 64,
                 size=n, allocated=4096, dev=156, inode=i + 1, uid=12345,
                 gid=23456, mode=0o640, mtime_ns=1, ctime_ns=2)
            for i, n in enumerate(sizes)]
    return dict(source_root='/SYNTHETIC_ONLY', source_filesystem_identity='SYNTHETIC_ONLY',
                source_frozen_commit='a' * 40, genuine164_destination_root='/SYNTHETIC_ONLY/archive',
                source_file_inventory_sha256='b' * 64,
                selector_sha256=v9.digest(v9.canonical(rows)), files=rows,
                directories=[dict(relative_path='.', uid=12345, gid=23456,
                                  mode=0o750, mtime_ns=1)])


class BatchPlanTests(unittest.TestCase):
    def plan(self, sizes, **kw):
        m = manifest(sizes)
        result = batch.plan_batches(m, v9.validate_manifest(m), **kw)
        rows = {r['relative_path']: r for r in m['files']}
        coverage = {p: 0 for p in rows}
        names = []
        for window in result['batches']:
            self.assertEqual(window['txid'], result['txid'])
            self.assertEqual(window['manifest_sha256'], result['manifest_sha256'])
            self.assertEqual(window['selector_sha256'], result['selector_sha256'])
            self.assertLessEqual(len(window['entries']), result['max_entries'])
            self.assertEqual(window['raw_bytes'], sum(e['length'] for e in window['entries']))
            self.assertLessEqual(window['raw_bytes'], result['window_cap'])
            for e in window['entries']:
                p = e['relative_path']; names.append(p)
                self.assertEqual(e['offset'], coverage[p])
                self.assertGreater(e['length'], 0)
                self.assertLessEqual(e['length'], result['raw_cap'])
                self.assertEqual(e['original_sha256'], rows[p]['sha256'])
                coverage[p] += e['length']
        self.assertEqual(coverage, {p: r['size'] for p, r in rows.items()})
        self.assertEqual(names, sorted(names))
        self.assertFalse(result['copy_ready'])
        self.assertFalse(result['receiving_authorized'])
        self.assertFalse(result['physical_allocation_proven'])
        self.assertFalse(result['source_release_authorized'])
        return result

    def test_small_files_share_window_without_combining_identity(self):
        p = self.plan([1] * 300)
        self.assertEqual([len(b['entries']) for b in p['batches']], [128, 128, 44])

    def test_large_original_exact_ordered_nonoverlapping_coverage(self):
        p = self.plan([batch.RAW_CAP * 2 + 17, 1])
        self.assertEqual([b['raw_bytes'] for b in p['batches']], [batch.RAW_CAP, batch.RAW_CAP, 18])

    def test_raw_and_batch_boundaries(self):
        self.plan([5, 5, 1, 23], raw_cap=8, window_cap=10, max_entries=2)

    def test_empty_files_have_no_zero_length_payload(self):
        p = self.plan([0, 0, 1, 0])
        self.assertEqual(len(p['empty_files']), 3)
        self.assertEqual(len(p['batches']), 1)

    def test_all_empty_and_no_files(self):
        self.assertEqual(self.plan([0, 0])['batches'], [])
        self.assertEqual(self.plan([])['batches'], [])

    def test_deterministic_reexecution_does_not_issue_new_window(self):
        self.assertEqual(self.plan([144, 6000, 0]), self.plan([144, 6000, 0]))

    def test_existing_144_byte_canary_remains_separate(self):
        p = self.plan([144, 1, 1], first_range_alone=True)
        self.assertEqual([b['raw_bytes'] for b in p['batches']], [144, 2])
        self.assertEqual(len(p['batches'][0]['entries']), 1)
        self.assertEqual(p['batches'][0]['entries'][0]['offset'], 0)

    def test_invalid_canary_option_refused(self):
        with self.assertRaises(v9.Hold):
            self.plan([144], first_range_alone='true')

    def test_wrong_txid_and_changed_selector_refused(self):
        m = manifest([144])
        with self.assertRaises(v9.Hold):
            batch.plan_batches(m, 'c' * 64)
        m['files'][0]['size'] += 1
        with self.assertRaises(v9.Hold):
            batch.plan_batches(m, v9.transaction_id(m))

    def test_invalid_caps_and_types_refused(self):
        for key in ('raw_cap', 'window_cap', 'max_entries'):
            for value in (0, -1, True, 1.5, batch.RAW_CAP + 1):
                with self.subTest(key=key, value=value):
                    with self.assertRaises(v9.Hold):
                        self.plan([144], **{key: value})

    def test_fractional_or_boolean_file_size_refused(self):
        for value in (1.5, True):
            m = manifest([value])
            with self.assertRaises(v9.Hold):
                batch.plan_batches(m, v9.transaction_id(m))

    def test_wrong_empty_hash_refused(self):
        m = manifest([0]); m['files'][0]['sha256'] = 'c' * 64
        m['selector_sha256'] = v9.digest(v9.canonical(m['files']))
        with self.assertRaises(v9.Hold):
            batch.plan_batches(m, v9.transaction_id(m))

    def test_distinct_group_txids_cannot_be_merged(self):
        m = manifest([144]); other = copy.deepcopy(m)
        other['source_root'] = '/OTHER_SYNTHETIC_ONLY'
        with self.assertRaises(v9.Hold):
            batch.plan_batches(other, v9.transaction_id(m))


if __name__ == '__main__':
    unittest.main()
