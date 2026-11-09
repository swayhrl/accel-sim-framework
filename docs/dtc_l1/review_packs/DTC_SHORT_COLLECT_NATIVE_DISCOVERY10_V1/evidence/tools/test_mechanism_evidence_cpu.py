"""R0 CPU-only synthetic closure and corruption tests; never invokes a model."""
import gzip
import hashlib
import io
import json
import os
import fcntl
import tarfile
import tempfile
import unittest
from pathlib import Path

import mechanism_outbox as outbox
import mechanism_strict as strict


def write_json(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True) + '\n')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


class EvidenceCPU(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='short_collect_r0_',
            dir='/root/data/dtc_short_collect_native_discovery10_v1_20261109/fixtures')
        self.root = Path(self.tmp.name)
        self.uuid = 'synthetic-uuid-never-register'
        self.output = self.root / 'DTC/run/results' / self.uuid
        self.output.mkdir(parents=True)
        self.binary = self.root / 'simulator.bin'
        self.binary.write_bytes(b'synthetic-binary')
        self.loader = self.root / 'loader.bin'
        self.loader.write_bytes(b'synthetic-loader')
        self.cudart = self.root / 'libcudart.so'
        self.cudart.write_bytes(b'synthetic-libcudart')
        self.strace = self.root / 'strace.bin'
        self.strace.write_bytes(b'synthetic-strace')
        runtime = {'runtime_files': [dict(role=role, realpath=str(path), sha256=strict.sha(path))
                    for role, path in [('binary', self.binary), ('libcudart', self.cudart),
                                       ('loader', self.loader), ('strace', self.strace)]]}
        self.runtime = self.root / 'runtime.json'
        write_json(self.runtime, runtime)
        self.spec = dict(request='R0_SYNTHETIC', cohort='SHORT-COLLECT-SYNTHETIC-ON',
                         mode='ON', program='synthetic', binary_path=str(self.binary),
                         binary_sha256=strict.sha(self.binary), runtime_binding_path=str(self.runtime),
                         runtime_sha256=strict.sha(self.runtime),
                         native_simulator_argv=[str(self.binary), '--synthetic'],
                         execution_mnt_namespace='mnt:[synthetic]',
                         expected={'kernels':1,'CTA':1,'instructions':10},
                         expected_options={f'-synthetic-{i}':['0'] for i in range(270)},
                         core_commit='9a0de9b9f97144f481b3e3637e329ebab01acb74',
                         framework_commit='02775fd795cde5aae1480d81cee6eb481d0a08f4',
                         original_environment={'DTC_AG7_INPUT_SHA':'input','DTC_AG7_ROI_SHA':'roi'})
        self.domain={'input_digest':'synthetic-input-digest','rows':[]}
        self.binding=self.root/'input_binding.json'
        write_json(self.binding,{'input_digest':'synthetic-input-digest','qualification':self.domain})
        self.spec.update(input_binding_path=str(self.binding),
                         input_binding_sha256=strict.sha(self.binding),
                         input_digest='synthetic-input-digest')
        self.spec['expected_options'][strict.SWITCH] = ['1']
        self.intent = dict(request='R0_SYNTHETIC', cohort=self.spec['cohort'], uuid=self.uuid,
                           output=str(self.output), automatic_retry=False,
                           consumed_before_launcher_fork=1)
        raw = (f"kernel_name = synthetic\nDTC_SHORT_COLLECT_V1 enabled=1 "
               f"choice_decision_different=2 eligible_choice_different=1\n"
               f"{self.spec['core_commit'][:7]} {self.spec['framework_commit']}\n").encode()
        self.raw = raw
        (self.output / 'raw.log.gz').write_bytes(gzip.compress(raw))
        self.done = dict(request='R0_SYNTHETIC', cohort=self.spec['cohort'], uuid=self.uuid,
                         stop_reason=None, launcher_wait_returncode=0,
                         native_simulator_observed=True, new_attempt_consumed=1,
                         automatic_retry=False, raw_sha256=strict.sha(self.output / 'raw.log.gz'),
                         raw_uncompressed_sha256=sha_bytes(raw), raw_uncompressed_bytes=len(raw))
        write_json(self.output / 'NATIVE_EXIT.json', self.done)
        write_json(self.output / 'NATIVE_LAUNCH.json',
                   dict(scientific_qualification_uuid=self.uuid, argv=self.spec['native_simulator_argv']))
        write_json(self.output / 'NATIVE_SIMULATOR_PID_AND_MAPS.json',
                   dict(uuid=self.uuid, pid=99999999, start_ticks=1, mnt_namespace='mnt:[synthetic]',
                        maps=' '.join(map(str, [self.binary,self.cudart,self.loader]))))
        progress = dict(seq=1,pid=99999999,start_ticks=1,generation=self.uuid,
                        input='input',roi='roi',mono_ns=1,completed=10,end='NATURAL')
        (self.output / 'progress.jsonl.gz').write_bytes(gzip.compress((json.dumps(progress)+'\n').encode()))

    def tearDown(self):
        if getattr(self,'preserve',False):
            self.tmp._finalizer.detach()
        else:
            self.tmp.cleanup()

    def test_closed_positive_and_negative(self):
        proof = strict.closed(self.spec,self.intent,self.done,self.output,self.domain,full_population=False)
        self.assertEqual(proof['eligible_choice_different'],1)
        self.assertEqual(proof['status'],'CPU_SYNTHETIC_ONLY')
        bad = dict(self.done,stop_reason='TIMEOUT')
        with self.assertRaisesRegex(ValueError,'NATIVE_EXIT_JOIN|NATURAL_NATIVE_EXIT'):
            strict.closed(self.spec,self.intent,bad,self.output,self.domain,full_population=False)
        self.spec['mode']='OFF'
        self.spec['expected_options'][strict.SWITCH]=['0']
        with self.assertRaisesRegex(ValueError,'MECHANISM_MODE_ECHO'):
            strict.closed(self.spec,self.intent,self.done,self.output,self.domain,full_population=False)
        self.spec['mode']='ON'
        self.spec['expected_options'][strict.SWITCH]=['1']
        with self.assertRaisesRegex(ValueError,'INPUT_DOMAIN_EXACT_JOIN'):
            strict.closed(self.spec,self.intent,self.done,self.output,
                          dict(self.domain,rows=[{'path':'unbound'}]),full_population=False)
        (self.output/'raw.log.gz').write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'CLOSED_GZIP_SHA'):
            strict.closed(self.spec,self.intent,self.done,self.output,self.domain,full_population=False)

    def test_source_keep_manifest_and_typed_restore(self):
        proof = strict.closed(self.spec,self.intent,self.done,self.output,self.domain,full_population=False)
        write_json(self.output/'MECHANISM_STRICT.json',proof)
        with self.assertRaisesRegex(RuntimeError,'NATURAL_POSITIVE_REQUIRES_STRICT'):
            outbox.source_manifest(self.intent,self.done,root=self.root,
                                   nas=self.root/'synthetic164')
        # Test only the archive mechanics with a synthetic accepted-shaped proof.
        # Production root recomputes full strict and cannot use this fixture.
        mock = dict(proof,status='NATURAL_STRICT_ACCEPTED')
        write_json(self.output/'MECHANISM_STRICT.json',mock)
        true164 = os.environ.get('DTC_R0_TRUE164') == '1'
        nas = outbox.NAS if true164 else self.root/'synthetic164'
        if true164:
            outbox.gate(2*1024*1024)
            self.preserve=True
        manifest = outbox.source_manifest(self.intent,self.done,root=self.root,nas=nas)
        self.assertEqual(manifest['source_disposition'],'SOURCE_KEEP')
        self.assertEqual(manifest['scientific_status'],'NATURAL_STRICT_ACCEPTED')
        f,v = outbox.libraries()
        bundle = nas/manifest['cohort']/manifest['txid'] if true164 else nas/'bundle'
        receiver_lock = None
        if true164:
            receiver_lock = Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb')
            fcntl.flock(receiver_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        (bundle/'chunks').mkdir(parents=True)
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload,mode='w',format=tarfile.PAX_FORMAT) as tar:
            for row in manifest['entries']:
                p = self.output/row['path']
                info=tarfile.TarInfo(row['path'])
                info.uid,info.gid,info.mode=row['uid'],row['gid'],row['mode']
                info.mtime=row['mtime_ns']//10**9
                info.pax_headers={'mtime':f"{row['mtime_ns']//10**9}.{row['mtime_ns']%10**9:09d}"}
                if row['type']=='directory':
                    info.type=tarfile.DIRTYPE
                    tar.addfile(info)
                else:
                    data=p.read_bytes()
                    info.size=len(data)
                    tar.addfile(info,io.BytesIO(data))
        data=payload.getvalue()
        chunk=bundle/'chunks'/'00000000000000000000.part'
        with chunk.open('xb') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        index=dict(archive_bytes=len(data),archive_sha256=sha_bytes(data),chunks=[
            dict(txid=manifest['txid'],name=chunk.name,offset=0,size=len(data),sha256=sha_bytes(data))])
        with (bundle/'SOURCE_MANIFEST.json').open('xb') as stream:
            stream.write(outbox.canon(manifest));stream.flush();os.fsync(stream.fileno())
        with (bundle/'ARCHIVE_INDEX.json').open('xb') as stream:
            stream.write(outbox.canon(index));stream.flush();os.fsync(stream.fileno())
        seal=dict(txid=manifest['txid'],manifest_sha256=sha_bytes(outbox.canon(manifest)),
                  archive_index_sha256=sha_bytes(outbox.canon(index)),
                  policy='EXCLUSIVE_CREATE_COMMIT_MARKER_LAST')
        with (bundle/'COMMIT.json').open('xb') as stream:
            stream.write(outbox.canon(seal));stream.flush();os.fsync(stream.fileno())
        f.verify_archive(bundle,manifest)
        restored=(outbox.ROOT/'fixtures/r0_true164_restores'/manifest['txid']) if true164 else self.root/'restored'
        restored.parent.mkdir(parents=True,exist_ok=True)
        f.restore(bundle,manifest,restored,v)
        self.assertEqual(len(f.check_native(restored,manifest)),len(manifest['entries']))
        self.assertTrue((self.output/'raw.log.gz').exists())
        if true164:
            # Preserve the successful 164 archive. Corrupt an isolated local copy.
            corrupt=self.root/'corrupt164'
            (corrupt/'chunks').mkdir(parents=True)
            for name in ['SOURCE_MANIFEST.json','ARCHIVE_INDEX.json','COMMIT.json']:
                (corrupt/name).write_bytes((bundle/name).read_bytes())
            bad=corrupt/'chunks'/chunk.name
            bad.write_bytes(chunk.read_bytes())
            with bad.open('r+b') as stream:
                stream.seek(20);stream.write(b'X')
            with self.assertRaisesRegex(RuntimeError,'SHA|sha|mismatch'):
                f.verify_archive(corrupt,manifest)
            receipt=dict(schema='DTC_R0_TRUE164_SYNTHETIC_ONLY_V1',science_starts=0,
                         request_registration=0,source=str(self.output),
                         archive=str(bundle),restore=str(restored),txid=manifest['txid'],
                         archive_sha256=index['archive_sha256'],entries=len(manifest['entries']),
                         positive_archive_readback='PASS',typed_native_restore='PASS',
                         corrupted_local_copy_rejected='PASS',SOURCE_KEEP=True)
            write_json(outbox.ROOT/'evidence/R0_TRUE164_SYNTHETIC_RECEIPT.json',receipt)
            receiver_lock.close()
        else:
            with chunk.open('r+b') as stream:
                stream.seek(20);stream.write(b'X')
            with self.assertRaisesRegex(RuntimeError,'SHA|sha|mismatch'):
                f.verify_archive(bundle,manifest)

    def test_before_pid_negative_is_not_performance(self):
        (self.output/'NATIVE_SIMULATOR_PID_AND_MAPS.json').unlink()
        self.done.update(native_simulator_observed=False,stop_reason='LAUNCHER_FAILED',
                         launcher_wait_returncode=1)
        write_json(self.output/'NATIVE_EXIT.json',self.done)
        negative=strict.classify_closed_failure(self.intent,self.done,self.output)
        self.assertEqual(negative['failure_class'],'BEFORE_NATIVE_PID')
        self.assertIsNone(negative['accepted_cycles'])
        self.assertFalse(negative['performance_accepted'])

    def test_archive_rejects_wrong_source_root(self):
        wrong=dict(self.intent,output=str(self.root/'results'/self.uuid))
        with self.assertRaisesRegex(RuntimeError,'EXACT_NEW_SOURCE_ROOT'):
            outbox.source_manifest(wrong,self.done,root=self.root,nas=self.root/'synthetic164')

    def test_registered_exact_bytes_join(self):
        specs=self.root/'control/specs'
        ledger=self.root/'control/qualification_ledger'
        specs.mkdir(parents=True)
        ledger.mkdir(parents=True)
        spec_path=specs/(self.spec['cohort']+'.json')
        intent_path=ledger/(self.spec['cohort']+'.INTENT.json')
        done_path=ledger/(self.spec['cohort']+'.DONE.json')
        write_json(spec_path,self.spec)
        self.intent['spec_sha256']=strict.sha(spec_path)
        write_json(intent_path,self.intent)
        write_json(done_path,self.done)
        registry=self.root/'registry.json'
        epoch=self.root/'epoch.json'
        row=dict(uuid=self.uuid,intent_sha256=strict.sha(intent_path),
                 execution_receipt=dict(path=str(done_path),sha256=strict.sha(done_path)))
        reg=dict(registered_future_requests={'R0_SYNTHETIC':dict(
            admitted_specs={self.spec['cohort']:strict.sha(spec_path)},
            consumed={self.spec['cohort']:row})})
        write_json(registry,reg)
        write_json(epoch,dict(native_registry_sha256=strict.sha(registry)))
        proof=strict.registered_join(self.spec,self.intent,self.done,
                    registry=registry,epoch=epoch,root=self.root)
        self.assertEqual(proof['done_sha256'],strict.sha(done_path))
        row['execution_receipt']['sha256']='0'*64
        write_json(registry,reg)
        write_json(epoch,dict(native_registry_sha256=strict.sha(registry)))
        with self.assertRaisesRegex(ValueError,'REGISTRY_LEDGER_CLOSED_JOIN'):
            strict.registered_join(self.spec,self.intent,self.done,
                    registry=registry,epoch=epoch,root=self.root)


if __name__=='__main__':
    unittest.main()
