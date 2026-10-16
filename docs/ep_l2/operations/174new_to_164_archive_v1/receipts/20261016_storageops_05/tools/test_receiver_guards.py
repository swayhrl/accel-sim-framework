"""Metadata-only adversarial validation checks; no rsync or source operations."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest

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

if __name__ == '__main__':
    unittest.main()
