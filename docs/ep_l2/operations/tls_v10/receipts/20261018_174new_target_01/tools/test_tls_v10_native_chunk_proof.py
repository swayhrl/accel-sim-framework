"""Small native fault fixtures only; requires Linux/root for numeric metadata."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

import tls_v10_native_chunk_proof as proof
import v9_transaction as v9


class NativeChunkProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ops_v9_fixture_tls_native_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'SYNTHETIC_ONLY').write_bytes(b'OPS_V9_SYNTHETIC_ONLY\n')
        self.original = self.root / 'ORIGINAL_SYNTHETIC.bin'
        self.raw = bytes(range(251)) * 3  # 753 bytes, never a scientific asset.
        self.original.write_bytes(self.raw)
        original_stat = self.original.lstat()
        self.base = self.root / 'archive'
        self.base.mkdir()
        row = dict(relative_path='scientific-output.log', type='regular',
                   sha256=v9.digest(self.raw), **v9.identity(original_stat))
        row.update(uid=12345, gid=23456, mode=0o640, mtime_ns=1770000000123456789)
        dirs = [dict(relative_path='.', uid=12345, gid=23456, mode=0o750, mtime_ns=1770000000123456789)]
        self.manifest = dict(source_filesystem_identity='SYNTHETIC_ONLY', source_root=str(self.root),
                             selector_sha256=v9.digest(v9.canonical([row])), source_frozen_commit='a' * 40,
                             genuine164_destination_root=str(self.base), source_file_inventory_sha256='b' * 64,
                             files=[row], directories=dirs)
        self.txid = v9.validate_manifest(self.manifest)
        self.length = len(self.raw) - 23
        self.chunk_raw = self.raw[:self.length]
        key = v9.digest(row['relative_path'].encode()) + '.%016d' % 0
        self.chunk = self.base / (self.txid + '.partial') / 'chunks' / key
        self.chunk.parent.mkdir(parents=True)
        self.chunk.write_bytes(self.chunk_raw)
        self.dest = self.root / 'proof' / self.txid / key

    def run_proof(self, **overrides):
        args = dict(manifest=self.manifest, txid=self.txid, relative_path='scientific-output.log',
                    offset=0, length=self.length, chunk_sha256=v9.digest(self.chunk_raw),
                    archive_chunk=self.chunk, destination=self.dest, fixture=True)
        args.update(overrides)
        result = proof.prove_chunk(**args)
        self.assertEqual(self.original.read_bytes(), self.raw)
        return result

    def test_native_full_chunk_metadata_and_reopen_sha_scope(self):
        result = self.run_proof()
        receipt = result['receipt']
        self.assertEqual(receipt['proof_scope'], 'CHUNK_RANGE_ONLY')
        self.assertFalse(receipt['original_full_file_restored'])
        self.assertFalse(receipt['complete_group_restored'])
        self.assertFalse(receipt['source_release_authorized'])
        self.assertEqual(receipt['source_action'], 'SOURCE_KEEP')
        self.assertEqual((self.dest / 'payload').read_bytes(), self.chunk_raw)
        self.assertEqual(v9.hash_file(self.dest / 'payload'), receipt['chunk_sha256'])

    def test_duplicate_reuses_existing_exact_proof(self):
        first = self.run_proof()
        ident = v9.identity((self.dest / 'payload').lstat())
        second = self.run_proof()
        self.assertTrue(second['reused_existing_native_proof'])
        self.assertEqual(first['receipt'], second['receipt'])
        self.assertEqual(ident, v9.identity((self.dest / 'payload').lstat()))

    def test_after_copy_complete_orphan_adopted_no_overwrite(self):
        with self.assertRaises(v9.Hold):
            self.run_proof(crash='after_copy')
        orphan = self.dest / 'payload.partial'
        inode = orphan.stat().st_ino
        self.assertEqual(orphan.read_bytes(), self.chunk_raw)
        result = self.run_proof()
        self.assertEqual((self.dest / 'payload').stat().st_ino, inode)
        self.assertFalse(result['reused_existing_native_proof'])

    def test_after_finalize_reconciles_without_recopy(self):
        with self.assertRaises(v9.Hold):
            self.run_proof(crash='after_finalize')
        ident = v9.identity((self.dest / 'payload').lstat())
        self.assertFalse((self.dest / 'RESTORE_RECEIPT.json').exists())
        result = self.run_proof()
        self.assertTrue(result['reused_existing_native_proof'])
        self.assertEqual(ident, v9.identity((self.dest / 'payload').lstat()))

    def test_incomplete_orphan_holds_without_overwrite_or_delete(self):
        with self.assertRaises(v9.Hold):
            self.run_proof(crash='during_copy')
        partial = self.dest / 'payload.partial'
        before = partial.read_bytes()
        self.assertLess(len(before), self.length)
        with self.assertRaises(v9.Hold):
            self.run_proof()
        self.assertEqual(before, partial.read_bytes())
        self.assertFalse((self.dest / 'payload').exists())

    def test_corrupt_proof_and_metadata_drift_hold(self):
        self.run_proof()
        payload = self.dest / 'payload'
        before = payload.read_bytes()
        os.chmod(payload, 0o600)
        with self.assertRaises(v9.Hold):
            self.run_proof()
        self.assertEqual(payload.read_bytes(), before)
        os.chmod(payload, 0o640)
        payload.write_bytes(b'x' * self.length)
        os.utime(payload, ns=(1770000000123456789, 1770000000123456789))
        with self.assertRaises(v9.Hold):
            self.run_proof()
        self.assertEqual(payload.read_bytes(), b'x' * self.length)

    def test_txid_path_cap_hash_and_range_disagreement_hold(self):
        cases = [dict(txid='c' * 64), dict(relative_path='../outside'),
                 dict(offset=-1), dict(length=proof.RAW_CAP + 1),
                 dict(length=len(self.raw) + 1), dict(length=True),
                 dict(chunk_sha256='0' * 64), dict(chunk_sha256='x' * 64),
                 dict(archive_chunk=self.original)]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(v9.Hold):
                    self.run_proof(**args)
        self.assertFalse(self.dest.exists())

    def test_unowned_existing_destination_and_symlink_hold(self):
        self.dest.mkdir(parents=True)
        with self.assertRaises(v9.Hold):
            self.run_proof()
        self.assertEqual(list(self.dest.iterdir()), [])
        self.dest.rmdir()  # Exact empty synthetic fixture only.
        self.run_proof()
        payload = self.dest / 'payload'
        payload.unlink()  # Exact created synthetic fixture only.
        payload.symlink_to(self.original)
        with self.assertRaises(v9.Hold):
            self.run_proof()
        self.assertEqual(self.original.read_bytes(), self.raw)

    def test_reservation_manifest_metadata_conflict_hold(self):
        self.run_proof()
        manifest = copy.deepcopy(self.manifest)
        manifest['directories'][0]['mode'] = 0o700
        self.assertEqual(v9.validate_manifest(manifest), self.txid)
        with self.assertRaises(v9.Hold):
            self.run_proof(manifest=manifest)


if __name__ == '__main__':
    unittest.main()
