"""Small real-file range/resume tests in isolated /tmp; no production data."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import polybench_range_receiver as r

class RangeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='storageops-range-test-')
        root=Path(self.tmp.name).resolve();self.archive=root/'archive';self.bridge=root/'bridge'
        self.archive.mkdir();self.bridge.mkdir();(self.bridge/'.TARGET_RECEIVER.lock').write_bytes(b'')
        self.raw=b'abcdefghijk'
        spec=dict(r.SPEC,size=len(self.raw),payload=4,sha256=hashlib.sha256(self.raw).hexdigest())
        self.patches=[mock.patch.object(r,'ARCHIVE',self.archive),mock.patch.object(r,'BRIDGE',self.bridge),
            mock.patch.object(r,'SPEC',spec),mock.patch.object(r,'check_resources',return_value=dict(
                share_available_bytes=100*1024**3,archive_available_bytes=100*1024**3))]
        for p in self.patches:p.start()
        self.scope=dict(source_archive_path=spec['source'],source_archive_size_bytes=spec['size'],
            source_archive_sha256=spec['sha256'],source_action='SOURCE_KEEP',source_release_authorized=False,
            owner='root:root; fixture',owner_authorization='COPY_OK_ONLY',no_active_readers_or_writers=True,
            original_archive_retained=True,both_closeout_stage_roots_retained=True,
            source_archive_identity=dict(device=156,inode=8,nlink=1,size_bytes=spec['size'],mtime_ns=1,ctime_ns=1))
        self.proof=dict(commit='a'*40,github_readback_verified=True,receipt_sha256=hashlib.sha256(json.dumps(self.scope).encode()).hexdigest())

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()

    def staged(self,index,payload=None):
        batch='PB_CHUNK_'+str(index).zfill(3);part=self.raw[index*4:index*4+4] if payload is None else payload
        path=self.bridge/batch/'files/payload.bin';path.parent.mkdir(parents=True);path.write_bytes(part)
        h=hashlib.sha256(part).hexdigest()
        data=dict(schema='STORAGE_OPS_V7_ARCHIVE_RANGE_READY',batch_id=batch,project='Decoupled-L2',
            source_receipt_commit=self.proof['commit'],source_scope_sha256=self.proof['receipt_sha256'],
            source_archive_path=r.SPEC['source'],source_archive_size_bytes=r.SPEC['size'],source_archive_sha256=r.SPEC['sha256'],
            source_archive_identity=self.scope['source_archive_identity'],source_archive_identity_rechecked_before_after_stage=True,
            source_action='SOURCE_KEEP',source_release_authorized=False,chunk_index=index,chunk_count=3,
            offset_bytes=index*4,length_bytes=len(part),bridge_root=str(self.bridge),destination_archive_root=str(self.archive),
            final_destination_relative_path=r.SPEC['final'],bridge_path=str(path),source_range_sha256=h,bridge_sha256=h,
            bridge_reopened_sha256_verified=True)
        encoded=(json.dumps(data,indent=2)+'\n').encode();(self.bridge/(batch+'_READY.json')).write_bytes(encoded)
        return data,hashlib.sha256(encoded).hexdigest()

    def clear_stage(self,data):
        p=Path(data['bridge_path']);p.unlink();p.parent.rmdir();p.parent.parent.rmdir()

    def receive(self,data,digest,**kw):
        return r.receive(data,digest,self.scope,self.proof,rate=0,**kw)

    def test_rejects_wrong_archive_ranges_scope_and_release(self):
        data,digest=self.staged(0)
        for key,value in [('offset_bytes',1),('chunk_count',4),('length_bytes',5),
                          ('source_release_authorized',True),('final_destination_relative_path','../escape'),
                          ('source_archive_sha256','b'*64),('bridge_path','/outside/payload.bin')]:
            bad=dict(data);bad[key]=value
            with self.assertRaises(ValueError):r.validate(bad,self.scope,self.proof)
        bad_scope=dict(self.scope,no_active_readers_or_writers=False)
        with self.assertRaises(ValueError):r.validate(data,bad_scope,self.proof)
        identity=dict(self.scope['source_archive_identity'],mtime_ns='UNKNOWN')
        with self.assertRaises(ValueError):r.validate(dict(data,source_archive_identity=identity),dict(self.scope,source_archive_identity=identity),self.proof)

    def test_unowned_existing_archive_is_never_overwritten(self):
        data,digest=self.staged(0);final=self.archive/r.SPEC['final'];final.parent.mkdir(parents=True);final.write_bytes(b'KEEP')
        with self.assertRaises(ValueError):self.receive(data,digest)
        self.assertEqual(final.read_bytes(),b'KEEP')

    def test_frozen_plan_rejects_rounded_identity_and_substituted_range_hash(self):
        data,digest=self.staged(0)
        plan=dict(source_path=r.SPEC['source'],source_size_bytes=11,source_sha256=r.SPEC['sha256'],
            source_dev=156,source_inode=8,source_nlink=1,source_mtime_ns=1,source_ctime_ns=1,chunk_count=3,
            chunks=[dict(index=i,offset_bytes=i*4,size_bytes=len(self.raw[i*4:i*4+4]),sha256=hashlib.sha256(self.raw[i*4:i*4+4]).hexdigest()) for i in range(3)])
        r.validate_plan(data,self.scope,plan)
        with self.assertRaises(ValueError):r.validate_plan(data,self.scope,dict(plan,source_mtime_ns=99))
        bad=copy.deepcopy(plan);bad['chunks'][0]['sha256']='b'*64
        with self.assertRaises(ValueError):r.validate_plan(data,self.scope,bad)

    def test_predecessor_and_single_bridge_window_required(self):
        data,digest=self.staged(1)
        with self.assertRaises(ValueError):self.receive(data,digest)
        self.clear_stage(data);data,digest=self.staged(0)
        (self.bridge/'another/files').mkdir(parents=True)
        with self.assertRaises(ValueError):self.receive(data,digest)

    def test_owned_partial_resume_preserves_verified_prefix(self):
        data,digest=self.staged(0);out=self.receive(data,digest);self.clear_stage(data)
        part=Path(out['partial_archive_path']);part.write_bytes(part.read_bytes()+b'bad')
        data,digest=self.staged(1)
        with self.assertRaises(ValueError):self.receive(data,digest)
        self.receive(data,digest,resume=True)
        self.assertEqual(part.read_bytes(),b'abcdefgh')

    def test_completed_component_revalidation_needs_no_bridge_payload(self):
        data,digest=self.staged(0);self.receive(data,digest);self.clear_stage(data)
        out=self.receive(data,digest)
        self.assertEqual(out['new_received_range_bytes'],0)
        self.assertTrue(out['idempotent_existing_range_verified'])

    def test_receipt_failure_after_journal_commit_recovers_without_copy(self):
        data,digest=self.staged(0)
        with mock.patch.object(r,'atomic_json',side_effect=OSError('simulated receipt outage')):
            with self.assertRaises(OSError):self.receive(data,digest)
        out=self.receive(data,digest)
        self.assertEqual(out['new_received_range_bytes'],0)
        self.assertTrue(out['recovered_owned_journal_without_data_transfer'])

    def test_whole_requires_gap_free_complete_coverage_and_sha(self):
        for i in range(3):
            data,digest=self.staged(i);self.receive(data,digest);self.clear_stage(data)
            if i<2:
                with self.assertRaises(ValueError):r.finalize(self.scope,self.proof)
        result=r.finalize(self.scope,self.proof)
        self.assertEqual(Path(result['destination_path']).read_bytes(),self.raw)
        self.assertEqual(result['destination_sha256'],hashlib.sha256(self.raw).hexdigest())
        again=r.finalize(self.scope,self.proof)
        self.assertEqual(again['new_primary_archived_bytes'],0)

    def test_valid_component_hashes_cannot_hide_wrong_whole_file(self):
        for i in range(3):
            data,digest=self.staged(i,b'XXX' if i==2 else None);self.receive(data,digest);self.clear_stage(data)
        with self.assertRaises(ValueError):r.finalize(self.scope,self.proof)
        self.assertFalse((self.archive/r.SPEC['final']).exists())

if __name__=='__main__':unittest.main()
