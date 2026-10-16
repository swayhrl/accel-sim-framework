"""Metadata-only adversarial validation checks; no rsync or source operations."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import os
import tempfile
import hashlib
import subprocess
from unittest import mock

spec = importlib.util.spec_from_file_location('receiver_under_test', sys.argv[1])
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)
READY = json.loads(Path(sys.argv[2]).read_text())
INVENTORY = list(csv.DictReader(Path(sys.argv[3]).read_text().splitlines()))
sys.argv = [sys.argv[0]]

class GuardChecks(unittest.TestCase):
    def reject(self, mutate):
        data = copy.deepcopy(READY)
        mutate(data)
        with self.assertRaises(ValueError):
            receiver.validate(data, INVENTORY)

    def test_exact_frozen_source_ready_accepted(self):
        self.assertEqual(len(receiver.validate(copy.deepcopy(READY), INVENTORY)), 52)

    def test_destination_traversal(self):
        self.reject(lambda d: d['files'][0].update(destination_relative_path='EP-L2/../../outside'))

    def test_outside_archive_root(self):
        self.reject(lambda d: d.update(destination_archive_root='/root/share/mnt164/huangrulin/c16_ai_workload'))

    def test_wrong_bridge_namespace(self):
        self.reject(lambda d: d.update(bridge_root='/root/share/container-workspaces/hrl-174-new/staging'))

    def test_frozen_source_hash_changed(self):
        self.reject(lambda d: d['files'][0].update(source_sha256='0'*64, bridge_sha256='0'*64))

    def test_duplicate_file(self):
        def mutate(d):
            d['files'][1] = copy.deepcopy(d['files'][0])
        self.reject(mutate)

    def test_unstable_source_not_admitted(self):
        self.reject(lambda d: d.update(source_identity_nlink_and_hash_rechecked_before_and_after_stage=False))

    def test_oversized_batch_not_admitted(self):
        self.reject(lambda d: d.update(total_size_bytes=receiver.LIMIT+1))

    def test_generic_project_name_does_not_authorize(self):
        self.reject(lambda d: d.update(batch_id='DTC-COLD-001', project='DTC-L1'))

    def test_explicitly_scoped_generic_project_plan(self):
        data = copy.deepcopy(READY)
        data.update(batch_id='DTC-COLD-TEST-001', project='DTC-L1',
            owner='unit-test-owner', owner_authorization='COLD_COPY_OK', retention='SOURCE_KEEP',
            asset_state='COLD', contains_unique_original_inputs=False,
            source_status='STAGED_READY', source_mount='overlay:0:156',
            source_commit='1'*40, source_config='unit-test-only', producer='synthetic_fixture',
            run_key='unit-test', rehydration_recipe='unit-test-only, no actual data transfer')
        f = data['files'][0]
        f.update(bridge_path=str(receiver.BRIDGE / data['batch_id'] / 'files' / f['relative_path']),
            destination_relative_path='DTC-L1/fixture/' + f['relative_path'],
            source_mtime_ns=1, source_ctime_ns=1, source_uid=0, source_gid=0,
            source_mode=0o644, readers_and_inflight_references=[])
        data.update(files=[f], file_count=1, total_size_bytes=f['size_bytes'])
        self.assertEqual(len(receiver.validate(data)), 1)

    @unittest.skipUnless(os.name == 'posix', 'live receiver uses Linux flock')
    def test_second_receiver_descriptor_is_rejected(self):
        import fcntl
        first = os.open(receiver.BRIDGE / '.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
        second = os.open(receiver.BRIDGE / '.TARGET_RECEIVER.lock', os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(first, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(second)
            os.close(first)

    def test_v7_scientific_copy_requires_explicit_keep_and_owner_scope(self):
        d = copy.deepcopy(READY)
        d.update(schema='STORAGE_OPS_V7_COLD_PROJECT_BATCH_READY', batch_id='R1-B001',
            project='EP-L2', owner='source-ops-reviewed-owner', owner_authorization='COLD_COPY_OK',
            retention='SOURCE_KEEP', asset_state='COLD', source_status='STAGED_READY',
            contains_unique_original_inputs=True, source_action='COPY_OK_ONLY',
            release_requires_user_approval=True, project_manifest_sha256='1'*64,
            owner_scope_receipt_sha256='2'*64, dependencies_complete=True, no_active_consumers=True,
            source_mount='overlay:0:156', source_commit='1'*40, source_config='preserved-with-project',
            producer='historical-project', run_key='historical', rehydration_recipe='manifest restore only')
        f = d['files'][0]
        f.update(bridge_path=str(receiver.BRIDGE / d['batch_id'] / 'files' / f['relative_path']),
            source_mtime_ns=1, source_ctime_ns=1, source_uid=0, source_gid=0,
            source_mode=0o644, readers_and_inflight_references=[])
        d.update(files=[f], file_count=1, total_size_bytes=f['size_bytes'])
        self.assertEqual(len(receiver.validate(d)), 1)
        d['release_requires_user_approval'] = False
        with self.assertRaises(ValueError):
            receiver.validate(d)

    def test_full_project_scope_rejects_hash_substitution(self):
        f = copy.deepcopy(READY['files'][0])
        row = dict(source_path=f['source_path'], size_bytes=f['size_bytes'],
            sha256='0'*64, device=f['source_dev'], inode=f['source_inode'], nlink=1)
        with self.assertRaises(ValueError):
            receiver.validate_project_membership({'project_manifest_sha256':'1'*64}, [f], [row], '1'*64)

class ResumeChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='storage-ops-receiver-unit-')
        self.root = Path(self.temp.name)
        self.archive = self.root / 'archive'; self.archive.mkdir()
        self.bridge = self.root / 'bridge'; self.bridge.mkdir()
        self.batch = 'UNIT-COPY-001'
        self.rows = []
        for name, payload in [('a.bin', b'fixture-one'), ('b.bin', b'fixture-two')]:
            p = self.bridge / self.batch / 'files' / name
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            self.rows.append(dict(source_path='/virtual-source/' + name, bridge_path=str(p),
                relative_path=name, destination_relative_path='UNIT/project/' + name,
                size_bytes=len(payload), source_sha256=digest, bridge_sha256=digest))
        self.data = dict(batch_id=self.batch, project='UNIT', files=self.rows, file_count=2,
            total_size_bytes=sum(f['size_bytes'] for f in self.rows), source_receipt_commit='1'*40)
        self.manifest = self.bridge / (self.batch + '_READY.json')
        self.manifest.write_text(json.dumps(self.data))
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.patches = [mock.patch.object(receiver, 'ARCHIVE', self.archive),
            mock.patch.object(receiver, 'BRIDGE', self.bridge),
            mock.patch.object(receiver, 'check_resources', return_value={'archive_available_bytes':10**9,'share_available_bytes':10**12})]
        for p in self.patches:p.start()
        self.copies = []
        self.fail_copy = False

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()

    def fake_rsync(self, args, input=None, **kwargs):
        if '--dry-run' in args:
            return subprocess.CompletedProcess(args, 0, b'', b'')
        names = [x.decode() for x in input.split(b'\0') if x]
        self.copies.append(names)
        for index, name in enumerate(names):
            dest = Path(args[-1]) / name; dest.parent.mkdir(parents=True, exist_ok=True)
            raw = (Path(args[-2]) / name).read_bytes()
            dest.write_bytes(raw[:2] if self.fail_copy and index == len(names)-1 else raw)
        return subprocess.CompletedProcess(args, 23 if self.fail_copy else 0, b'', b'simulated interrupted copy' if self.fail_copy else b'')

    def execute(self, resume=False):
        with mock.patch.object(receiver.subprocess, 'run', side_effect=self.fake_rsync):
            return receiver.receive(self.data, self.digest, self.rows, self.manifest, resume=resume)

    def test_unowned_existing_archive_is_not_overwritten(self):
        dest = self.archive / self.rows[0]['destination_relative_path']
        dest.parent.mkdir(parents=True); dest.write_bytes(b'keep-existing')
        with self.assertRaises(ValueError):self.execute()
        self.assertEqual(dest.read_bytes(), b'keep-existing')
        self.assertEqual(self.copies, [])

    def test_owned_partial_resume_skips_already_complete_file(self):
        self.fail_copy = True
        with self.assertRaises(ValueError):self.execute()
        with self.assertRaises(ValueError):self.execute()
        self.fail_copy = False
        out = self.execute(resume=True)
        self.assertEqual(out['status'], 'DEST_VERIFIED')
        self.assertEqual(self.copies[-1], ['b.bin'])
        self.assertTrue(out['resumed_from_owned_journal'])

    def test_completed_batch_idempotence_does_not_need_stage_or_transfer(self):
        self.execute()
        for f in self.rows:Path(f['bridge_path']).unlink()
        before = len(self.copies)
        out = self.execute()
        self.assertEqual(len(self.copies), before)
        self.assertEqual(out['new_archived_bytes'], 0)
        self.assertTrue(out['idempotent_existing_archive_verified'])

if __name__ == '__main__':
    unittest.main()
