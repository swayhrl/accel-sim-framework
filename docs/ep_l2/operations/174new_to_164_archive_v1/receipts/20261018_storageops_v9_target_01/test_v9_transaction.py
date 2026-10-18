"""Tiny destructive cases are strictly inside new marked synthetic fixtures."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import v9_transaction as v


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ops_v9_fixture_')
        self.root = Path(self.tmp.name)
        (self.root / 'SYNTHETIC_ONLY').write_bytes(b'OPS_V9_SYNTHETIC_ONLY\n')
        self.source = self.root / 'source'; self.source.mkdir()
        self.base = self.root / 'archive'; self.base.mkdir()
        self.file = self.source / 'tiny.bin'; self.file.write_bytes(b'fixture-v9\x00' * 37)
        os.chmod(self.file, 0o640)
        self.manifest = self.make_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def make_manifest(self):
        s = self.file.stat(); row = dict(relative_path='tiny.bin', type='regular', sha256=v.hash_file(self.file), **v.identity(s))
        d = self.source.stat()
        directories = [dict(relative_path='.', uid=d.st_uid, gid=d.st_gid,
                            mode=d.st_mode & 0o7777, mtime_ns=d.st_mtime_ns, ctime_ns=d.st_ctime_ns)]
        selected = dict(files=[row], directories=directories, symlink_policy='REFUSE', hardlink_policy='REFUSE')
        return dict(source_filesystem_identity=dict(dev=s.st_dev, namespace='SYNTHETIC'),
                    source_root=str(self.source), source_frozen_commit='a' * 40,
                    genuine164_destination_root=str(self.base), selector_sha256=v.digest(v.canonical(selected)),
                    current_readers=[], **selected)

    def transaction(self, manifest=None):
        return v.Transaction(self.base, manifest or self.manifest, fixture=True)

    def accept(self, tx, **kwargs):
        return tx.accept_chunk('tiny.bin', 0, self.file, self.manifest['files'][0]['sha256'], txid=tx.txid, **kwargs)

    def gates(self):
        return dict(txid=v.transaction_id(self.manifest), exact_user_permission=True,
                    target_restore_verified=True, target_proof='SYNTHETIC-RESTORE-PROOF',
                    workspace=60 * 1024**3, share=41 * 1024**3, memory=80 * 1024**3)

    def release(self, crash=None, **changes):
        gates = self.gates(); gates.update(changes)
        return v.fixture_release(self.file, v.identity(self.file.stat()), v.hash_file(self.file),
                                 self.root / 'release.jsonl', gates, crash=crash)

    def test_upload_crash_before_record_resume_duplicate_and_final_resume(self):
        tx = self.transaction()
        with self.assertRaises(v.Hold): self.accept(tx, crash='before_chunk_record')
        resumed = self.transaction()
        resumed.reconcile_partial_chunk('tiny.bin', 0, self.manifest['files'][0]['sha256'], self.file.stat().st_size)
        self.accept(resumed); self.accept(resumed)
        result = resumed.finalize()
        self.assertEqual(v.hash_file(result / 'tree/tiny.bin'), v.hash_file(self.file))
        self.assertEqual(self.transaction().finalize(), result)
        self.assertEqual(len(list(self.base.iterdir())), 1)

    def test_upload_crash_after_record_resume_and_no_extra_copy(self):
        tx = self.transaction()
        with self.assertRaises(v.Hold): self.accept(tx, crash='after_chunk_record')
        self.accept(self.transaction()); result = self.transaction().finalize()
        self.assertEqual(v.hash_file(result / 'tree/tiny.bin'), v.hash_file(self.file))

    def test_mismatched_txid(self):
        tx = self.transaction()
        with self.assertRaises(v.Hold): tx.accept_chunk('tiny.bin', 0, self.file, v.hash_file(self.file), txid='b'*64)

    def test_corrupt_chunk(self):
        tx = self.transaction(); self.accept(tx)
        p = next(p for p in (tx.work / 'chunks').iterdir() if p.suffix != '.json')
        p.write_bytes(b'corrupt')
        with self.assertRaises(v.Hold): self.accept(self.transaction())

    def test_corrupt_chunk_manifest(self):
        tx = self.transaction(); self.accept(tx)
        p = next((tx.work / 'chunks').glob('*.json')); r = json.loads(p.read_bytes()); r['offset'] = 1; p.write_bytes(v.canonical(r))
        with self.assertRaises(v.Hold): tx.finalize()

    def test_corrupt_transaction_manifest(self):
        tx = self.transaction(); (tx.work / 'manifest.json').write_bytes(b'{}')
        with self.assertRaises(v.Hold): self.transaction()

    def test_changed_selector_sha(self):
        m = copy.deepcopy(self.manifest); m['files'][0]['sha256'] = 'b'*64
        with self.assertRaises(v.Hold): self.transaction(m)

    def test_corrupt_commit_marker(self):
        tx=self.transaction();self.accept(tx);final=tx.finalize();(final/'COMMIT.json').write_bytes(b'{}')
        with self.assertRaises(v.Hold):self.transaction()

    def test_source_inode_drift(self):
        identity = v.identity(self.file.stat()); content = self.file.read_bytes(); self.file.rename(self.file.with_suffix('.old')); self.file.write_bytes(content)
        with self.assertRaises(v.Hold): v.hash_file(self.file, identity)

    def test_source_mtime_and_ctime_drift(self):
        old = v.identity(self.file.stat()); os.utime(self.file, ns=(old['mtime_ns']+1000000, old['mtime_ns']+1000000))
        with self.assertRaises(v.Hold): v.hash_file(self.file, old)
        old = v.identity(self.file.stat()); os.chmod(self.file, 0o600)
        with self.assertRaises(v.Hold): v.hash_file(self.file, old)

    def test_wrong_mount_and_projection(self):
        for fs in [dict(target='/root/share/mnt164', source='/dev/md127', fstype='ext4'),
                   dict(target='/root/share/mnt164', source='somebody@other:/home/shared', fstype='fuse.sshfs')]:
            with self.assertRaises(v.Hold): v.mount_identity(self.root, fs)

    def test_symlink_and_traversal(self):
        link = self.root / 'link'; link.symlink_to(self.file)
        with self.assertRaises(v.Hold): v.hash_file(link)
        for path in ['../tiny.bin', '/tiny.bin', 'a/../../b', './tiny.bin', 'a//b', 'a\\b']:
            with self.assertRaises(v.Hold): v.relpath(path)

    def test_hardlink_refusal(self):
        os.link(self.file, self.root/'linked')
        with self.assertRaises(v.Hold): v.hash_file(self.file)

    def test_no_replace_final(self):
        tx = self.transaction(); self.accept(tx); tx.final.mkdir(); (tx.final/'sentinel').write_bytes(b'KEEP')
        with self.assertRaises(v.Hold): tx.finalize()
        self.assertEqual((tx.final/'sentinel').read_bytes(), b'KEEP')

    def test_native_restore_metadata_and_refuse_populated(self):
        tx = self.transaction(); self.accept(tx); final = tx.finalize(); dest=self.root/'restore'
        r=v.native_restore(final/'tree',self.manifest,dest)
        self.assertTrue(r['numeric_metadata_verified']); self.assertEqual((dest/'tiny.bin').read_bytes(), self.file.read_bytes())
        with self.assertRaises(v.Hold): v.native_restore(final/'tree',self.manifest,dest)

    def test_rename_without_replacement_preserves_existing(self):
        a=self.root/'a';b=self.root/'b';a.write_bytes(b'A');b.write_bytes(b'B')
        with self.assertRaises(v.Hold): v.rename_noreplace(a,b)
        self.assertEqual(a.read_bytes(),b'A');self.assertEqual(b.read_bytes(),b'B')

    def test_immutable_state_chain_and_corrupt_previous_receipt(self):
        tx=self.transaction();tx.transition('DISCOVERED',{});tx.transition('SOURCE_FROZEN',{})
        p=tx.work/'receipts/01.json';r=json.loads(p.read_bytes());r['previous_receipt_sha256']='f'*64;p.write_bytes(v.canonical(r))
        with self.assertRaises(v.Hold):tx.transition('COPY_READY',{})

    def test_target_cannot_authorize_source_release(self):
        tx=self.transaction()
        with self.assertRaises(v.Hold):tx.transition('RELEASE_ELIGIBLE',{})

    def test_idempotent_prior_state_reference(self):
        tx=self.transaction();first=tx.transition('DISCOVERED',{});tx.transition('SOURCE_FROZEN',{})
        self.assertEqual(tx.transition('DISCOVERED',{}),first)

    def test_exclusive_create_fallback_and_resume(self):
        tx=self.transaction();self.accept(tx)
        original=v.rename_noreplace
        def unsupported_directory(source,target):
            if Path(source).is_dir():raise v.Hold('no-replace finalize: Invalid argument')
            return original(source,target)
        with patch.object(v,'rename_noreplace',side_effect=unsupported_directory):result=tx.finalize()
        self.assertTrue((result/'COMMIT.json').exists());self.assertTrue((result/'RESERVATION.json').exists())
        self.assertEqual(self.transaction().finalize(),result)

    def test_native_restore_refuses_sshfs_projection(self):
        with patch.object(v.subprocess,'check_output',return_value='fuse.sshfs\n'):
            with self.assertRaises(v.Hold):v.native_restore(self.source,self.manifest,self.root/'restore')

    def test_release_crash_after_intent(self):
        with self.assertRaises(v.Hold):self.release(crash='after_intent')
        self.assertEqual(v.fixture_reconcile(self.file,self.root/'release.jsonl')['status'],'HOLD_INTENT_PRESENT_NO_AUTO_UNLINK')
        with self.assertRaises(v.Hold):self.release()
        self.assertTrue(self.file.exists())

    def test_release_crash_after_unlink(self):
        with self.assertRaises(v.Hold):self.release(crash='after_unlink')
        result=v.fixture_reconcile(self.file,self.root/'release.jsonl')
        self.assertEqual(result['status'],'UNCERTAIN_MANUAL_READBACK_REQUIRED');self.assertFalse(result['unlink_performed_by_reconcile'])

    def test_release_crash_after_done(self):
        with self.assertRaises(v.Hold):self.release(crash='after_done')
        self.assertEqual(v.fixture_reconcile(self.file,self.root/'release.jsonl')['status'],'RELEASED_NO_RETRY')
        self.assertFalse(self.file.exists())

    def test_active_reader_fd(self):
        with self.file.open('rb'):
            with self.assertRaises(v.Hold):self.release()
        self.assertTrue(self.file.exists())

    def test_active_pid_registry_and_scheduled_reader(self):
        for key in ['reader_pid','registry','scheduled_reader']:
            with self.assertRaises(v.Hold):self.release(**{key:True})
        self.assertTrue(self.file.exists())

    def test_permission_and_restore_withheld(self):
        for key in ['exact_user_permission','target_restore_verified']:
            with self.assertRaises(v.Hold):self.release(**{key:False})

    def test_current_sha_differs(self):
        with self.assertRaises(v.Hold):v.fixture_release(self.file,v.identity(self.file.stat()),'b'*64,self.root/'release.jsonl',self.gates())

    def test_insufficient_floors_and_oversized_batch(self):
        for change in [dict(workspace=48*1024**3-1),dict(share=40*1024**3-1),dict(memory=64*1024**3-1),dict(staging=v.CAP+1)]:
            with self.assertRaises(v.Hold):self.release(**change)

    def test_large_sparse_bridge_refused(self):
        large=self.root/'large';large.write_bytes(b'')
        with large.open('r+b') as out:out.truncate(v.CAP+1)
        tx=self.transaction()
        with self.assertRaises(v.Hold):tx.accept_chunk('tiny.bin',0,large,'a'*64,txid=tx.txid)

    def test_production_paths_cannot_enter_fixture_release(self):
        with self.assertRaises(v.Hold):v.fixture_root(Path('/workspace/repos/research'))

    def test_concurrent_df_accounting(self):
        result=v.space_accounting(100,150,80,110)
        self.assertEqual(result['immediate_batch_gain_bytes'],50)
        self.assertEqual(result['long_window_endpoint_change_bytes'],30)

    def test_durable_hold_has_previous_sha_and_duplicate_reuses_record(self):
        from v9_hold_receipt import guard, record_hold
        tx=self.transaction();previous=tx.transition('DISCOVERED',{})
        for _ in range(2):
            with self.assertRaises(v.Hold):
                with guard(tx,'ARCHIVE_STAGED'):
                    tx.accept_chunk('tiny.bin',0,self.file,v.hash_file(self.file),txid='b'*64)
        paths=list((tx.work/'holds').glob('*.json'));self.assertEqual(len(paths),1)
        receipt=json.loads(paths[0].read_bytes());self.assertEqual(receipt['previous_receipt_sha256'],previous)
        self.assertEqual(receipt['status'],'HOLD');self.assertFalse(receipt['source_release_authorized'])


def run():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ProtocolTests)
    result=unittest.TestResult();suite.run(result)
    return dict(schema='STORAGE_OPS_V9_FAULT_INJECTION_TESTS',status='PASS' if result.wasSuccessful() else 'FAIL',
                tests_run=result.testsRun,failures=[dict(test=str(t),traceback=s) for t,s in result.failures],
                errors=[dict(test=str(t),traceback=s) for t,s in result.errors],production_source_files_touched=0,
                destructive_scope='ONLY marked tempfile ops_v9_fixture_* trees',test_names=unittest.defaultTestLoader.getTestCaseNames(ProtocolTests))


if __name__=='__main__':
    receipt=run();print(json.dumps(receipt));raise SystemExit(0 if receipt['status']=='PASS' else 1)
