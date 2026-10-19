"""Tiny native synthetic grouping/replay/fault fixtures; never source science."""
import copy
import os
from pathlib import Path
import tempfile
import unittest

import tls_v10_grouped_ranges as group
import v9_transaction as v9


class GroupedRangesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ops_v9_fixture_tls_group_')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'SYNTHETIC_ONLY').write_bytes(b'OPS_V9_SYNTHETIC_ONLY\n')
        self.base = self.root / 'archive'; self.base.mkdir()
        self.bodies = [b'first tiny original\n', bytes(range(64))]
        rows = []
        for i, raw in enumerate(self.bodies):
            original = self.root / ('original%d' % i); original.write_bytes(raw)
            row = dict(relative_path='out%d' % i, type='regular', sha256=v9.digest(raw), **v9.identity(original.lstat()))
            row.update(uid=12345, gid=23456, mode=0o640, mtime_ns=1770000000123456789)
            rows.append(row)
        m = dict(source_filesystem_identity='SYNTHETIC_ONLY', source_root=str(self.root), source_frozen_commit='a'*40,
                 genuine164_destination_root=str(self.base), source_file_inventory_sha256='b'*64,
                 files=rows, directories=[dict(relative_path='.', uid=12345, gid=23456, mode=0o750,
                                               mtime_ns=1770000000123456789)], selector_sha256=v9.digest(v9.canonical(rows)))
        self.tx = v9.Transaction(self.base, m, fixture=True)
        ranges, entries = [], []
        for i, start, end in [(0, 0, len(self.bodies[0])), (1, 0, 23), (1, 23, 64)]:
            r = dict(relative_path='out%d' % i, offset=start, length=end-start,
                     original_sha256=rows[i]['sha256'], original_size=rows[i]['size'])
            ranges.append(r)
            p = self.root / ('bridge%d' % len(entries)); raw = self.bodies[i][start:end]; p.write_bytes(raw)
            r['bridge_path'] = str(p)
            entries.append(dict(relative_path=r['relative_path'], offset=start, length=len(raw),
                                source_identity={k: rows[i][k] for k in group.ID_KEYS},
                                source_full_sha256=rows[i]['sha256'], chunk_sha256=v9.digest(raw),
                                bridge_path=str(p), bridge_identity=v9.identity(p.lstat())))
        self.window = dict(txid=self.tx.txid, selector_sha256=m['selector_sha256'],
                           canonical_manifest_sha256=v9.digest(v9.canonical(m)), ranges=ranges)
        self.entries = entries
        self.native = self.root / 'native'

    def run_group(self, **kw):
        r = group.accept_group(self.tx, self.window, self.entries, native_parent=self.native, fixture=True, **kw)
        self.assertEqual([Path(e['bridge_path']).read_bytes() for e in self.entries],
                         [self.bodies[0], self.bodies[1][:23], self.bodies[1][23:]])
        self.assertEqual(r['source_files_deleted'], 0)
        self.assertFalse(r['complete_group_archived'])
        self.assertFalse(r['complete_group_native_restored'])
        return r

    def test_grouped_raw_ranges_reassemble_original_full_files_and_native_metadata(self):
        r = self.run_group(); self.assertEqual(r['range_count'], 3)
        tree = self.tx.finalize() / 'tree'
        restored = self.root / 'full-native'
        proof = v9.native_restore(tree, self.tx.manifest, restored)
        self.assertTrue(proof['numeric_metadata_verified'])
        for i, body in enumerate(self.bodies): self.assertEqual((restored / ('out%d' % i)).read_bytes(), body)

    def test_exact_replay_reuses_every_chunk_and_native_payload(self):
        self.run_group(); r = self.run_group()
        self.assertTrue(all(e['reused_archive_chunk'] and e['native_proof']['reused_existing_native_proof'] for e in r['entries']))

    def test_interruption_resumes_verified_prefix_without_copy_or_overwrite(self):
        with self.assertRaises(v9.Hold): self.run_group(crash_after=1)
        r = self.run_group()
        self.assertTrue(r['entries'][0]['reused_archive_chunk'])
        self.assertTrue(r['entries'][0]['native_proof']['reused_existing_native_proof'])
        self.assertFalse(r['entries'][1]['reused_archive_chunk'])

    def test_corrupt_verified_prefix_holds_instead_of_overwriting(self):
        r = self.run_group(); p = Path(r['entries'][0]['archive_chunk']); p.write_bytes(b'x'*p.stat().st_size)
        with self.assertRaises(v9.Hold): self.run_group()
        self.assertEqual(p.read_bytes(), b'x'*p.stat().st_size)

    def test_conflicting_identity_selector_or_manifest_rejected(self):
        for key in ['txid','selector_sha256','canonical_manifest_sha256']:
            saved=self.window[key]; self.window[key]='c'*64
            with self.assertRaises(v9.Hold): self.run_group()
            self.window[key]=saved

    def test_wrong_source_original_metadata_and_sha_rejected(self):
        self.entries[0]['source_identity']['inode']+=1
        with self.assertRaises(v9.Hold): self.run_group()
        self.entries[0]['source_identity']['inode']-=1
        self.entries[0]['source_full_sha256']='c'*64
        with self.assertRaises(v9.Hold): self.run_group()

    def test_noninteger_identity_or_unbound_bridge_path_rejected(self):
        self.entries[0]['source_identity']['nlink']=True
        with self.assertRaises(v9.Hold): self.run_group()
        self.entries[0]['source_identity']['nlink']=1
        self.entries[0]['bridge_path']=str(self.root/'original0')
        with self.assertRaises(v9.Hold): self.run_group()

    def test_wrong_range_order_missing_or_duplicate_entry_rejected(self):
        self.entries.reverse()
        with self.assertRaises(v9.Hold): self.run_group()
        self.entries.reverse(); self.entries.pop()
        with self.assertRaises(v9.Hold): self.run_group()

    def test_duplicate_ranges_rejected_before_any_archive_write(self):
        self.window['ranges'][2]=copy.deepcopy(self.window['ranges'][1])
        self.entries[2]=copy.deepcopy(self.entries[1])
        with self.assertRaises(v9.Hold): self.run_group()
        self.assertEqual(list((self.tx.work/'chunks').iterdir()), [])

    def test_zero_negative_boolean_over_cap_range_rejected(self):
        for n in [0,-1,True,group.RAW_CAP+1]:
            self.window['ranges'][0]['length']=n
            with self.assertRaises(v9.Hold): self.run_group()

    def test_bridge_inode_or_hash_drift_rejected(self):
        self.entries[0]['bridge_identity']['inode']+=1
        with self.assertRaises(v9.Hold): self.run_group()
        self.entries[0]['bridge_identity']['inode']-=1
        self.entries[0]['chunk_sha256']='c'*64
        with self.assertRaises(v9.Hold): self.run_group()

    def test_overlap_rejected(self):
        self.window['ranges'][2]['offset']=22;self.entries[2]['offset']=22
        with self.assertRaises(v9.Hold): self.run_group()

    def test_unmanifested_path_rejected(self):
        self.window['ranges'][0]['relative_path']='outside';self.entries[0]['relative_path']='outside'
        with self.assertRaises(v9.Hold): self.run_group()

    def test_symlink_and_hardlink_bridge_rejected(self):
        p=Path(self.entries[0]['bridge_path']);p.unlink();p.symlink_to(self.root/'original0')
        with self.assertRaises(v9.Hold): self.run_group()
        p.unlink();os.link(self.root/'original0',p)
        with self.assertRaises(v9.Hold): self.run_group()


if __name__=='__main__': unittest.main()
