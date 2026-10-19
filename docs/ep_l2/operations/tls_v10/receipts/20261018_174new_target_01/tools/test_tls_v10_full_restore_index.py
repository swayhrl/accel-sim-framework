"""Actual tiny Linux synthetic archives/restores; no scientific or source operations."""
import json
import os
from pathlib import Path
import tempfile
import unittest

import tls_v10_full_restore_index as index
import v9_transaction as v9


class FullRestoreIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ops_v9_fixture_tls_full_')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'SYNTHETIC_ONLY').write_bytes(b'OPS_V9_SYNTHETIC_ONLY\n')
        self.base = self.root / 'archive'; self.base.mkdir()
        rows = []
        for i, (name, raw) in enumerate([('first', b'hello\n'), ('docs/empty', b''), ('tree/two/out', bytes(range(64)))]):
            p = self.root / ('original%d' % i); p.write_bytes(raw)
            row = dict(relative_path=name, type='regular', sha256=v9.digest(raw), **v9.identity(p.lstat()))
            row.update(uid=12345, gid=23456, mode=0o640, mtime_ns=1770000000123456789)
            rows.append(row)
        dirs = [dict(relative_path=p, uid=12345, gid=23456, mode=0o750,
                     mtime_ns=1770000000123456789) for p in ['.', 'docs', 'tree', 'tree/two']]
        self.manifest = dict(source_filesystem_identity='SYNTHETIC_ONLY', source_root=str(self.root),
                             source_frozen_commit='a' * 40, genuine164_destination_root=str(self.base),
                             selector_sha256=v9.digest(v9.canonical(rows)), source_file_inventory_sha256='b' * 64,
                             files=rows, directories=dirs)
        self.txid = v9.validate_manifest(self.manifest)
        self.tx = v9.Transaction(self.base, self.manifest, fixture=True)
        for i, row in enumerate(rows):
            if row['size']:
                self.tx.accept_chunk(row['relative_path'], 0, self.root / ('original%d' % i), row['sha256'], txid=self.txid)
        self.archive = self.tx.finalize() / 'tree'
        self.native_parent = self.root / 'native'; self.native_parent.mkdir()
        self.native = self.native_parent / 'tree'
        self.reservation = dict(schema='TLS_V10_FULL_NATIVE_RESTORE_RESERVATION_V1', txid=self.txid,
                                manifest_sha256=v9.digest(v9.canonical(self.manifest)), native_tree=str(self.native),
                                destination_absent_before_restore=True, source_originals='SOURCE_KEEP')
        v9.exclusive_json(self.native_parent / 'RESTORE_RESERVATION.json', self.reservation)
        v9.native_restore(self.archive, self.manifest, self.native)

    def audit(self):
        return index.audit_full_restore(self.manifest, self.txid, self.archive, self.native, fixture=True)

    def test_all_files_empty_file_all_four_directories_full_numeric_metadata(self):
        r = self.audit()
        self.assertEqual((r['file_count'], r['directory_count'], r['original_logical_bytes']), (3, 4, 70))
        self.assertTrue(r['full_file_SHA_and_numeric_metadata_verified'])
        self.assertTrue(r['current_source_identity_and_readers_not_certified_by_target'])
        self.assertFalse(r['target_has_source_unlink_authority'])
        self.assertFalse(r['source_release_performed'])

    def test_read_only_reexecution_keeps_exact_index_and_tree_identity(self):
        before = v9.identity((self.native / 'first').lstat())
        self.assertEqual(self.audit(), self.audit())
        self.assertEqual(before, v9.identity((self.native / 'first').lstat()))

    def test_missing_even_zero_byte_original_refuses_full_group(self):
        (self.native / 'docs/empty').unlink()  # Owned synthetic only.
        with self.assertRaises(v9.Hold): self.audit()

    def test_extra_native_file_not_silently_excluded(self):
        (self.native / 'unexpected').write_bytes(b'fixture')
        with self.assertRaises(v9.Hold): self.audit()

    def test_missing_empty_directory_is_not_full_metadata_proof(self):
        extra = self.native / 'tree/two/out'; extra.unlink()
        extra.parent.rmdir()
        with self.assertRaises(v9.Hold): self.audit()

    def test_same_length_native_content_corruption_refused(self):
        p = self.native / 'first'; p.write_bytes(b'wrong\n')
        os.utime(p, ns=(1770000000123456789, 1770000000123456789))
        with self.assertRaises(v9.Hold): self.audit()

    def test_archive_corruption_refused(self):
        (self.archive / 'first').write_bytes(b'wrong\n')
        with self.assertRaises(v9.Hold): self.audit()

    def test_file_numeric_mode_or_directory_mtime_drift_refused(self):
        os.chmod(self.native / 'first', 0o600)
        with self.assertRaises(v9.Hold): self.audit()
        os.chmod(self.native / 'first', 0o640)
        os.utime(self.native, ns=(1, 1))
        with self.assertRaises(v9.Hold): self.audit()

    def test_symlink_and_hardlink_refused(self):
        p = self.native / 'first'; p.unlink(); p.symlink_to(self.root / 'original0')
        with self.assertRaises(v9.Hold): self.audit()
        p.unlink(); os.link(self.root / 'original0', p)
        with self.assertRaises(v9.Hold): self.audit()

    def test_no_commit_chunk_only_never_full_group(self):
        (self.archive.parent / 'COMMIT.json').write_bytes(b'{}\n')
        with self.assertRaises(v9.Hold): self.audit()

    def test_changed_manifest_or_wrong_txid_refused(self):
        with self.assertRaises(v9.Hold):
            index.audit_full_restore(self.manifest, 'c' * 64, self.archive, self.native, fixture=True)
        self.manifest['directories'][0]['mode'] = 0o700
        with self.assertRaises(v9.Hold): self.audit()

    def test_unowned_or_not_absent_before_restore_refused(self):
        self.reservation['destination_absent_before_restore'] = False
        (self.native_parent / 'RESTORE_RESERVATION.json').write_bytes(v9.canonical(self.reservation))
        with self.assertRaises(v9.Hold): self.audit()

    def test_existing_native_destination_is_not_overwritten(self):
        before = (self.native / 'first').read_bytes()
        with self.assertRaises(v9.Hold):
            v9.native_restore(self.archive, self.manifest, self.native)
        self.assertEqual((self.native / 'first').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
