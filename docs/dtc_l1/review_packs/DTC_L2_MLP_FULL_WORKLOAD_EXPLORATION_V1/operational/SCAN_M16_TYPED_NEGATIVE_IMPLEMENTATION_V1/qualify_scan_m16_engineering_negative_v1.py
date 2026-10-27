"""Native CPU-only fixtures. All writes confined to owned tempfile directories."""
import pathlib,importlib.util,tempfile,os,gzip,json,hashlib,unittest,copy,sys,contextlib
from unittest.mock import patch
sys.dont_write_bytecode=True
P=pathlib.Path
SOURCE=P(__file__).with_name('scan_m16_engineering_negative_v1.py')
def module():
 s=importlib.util.spec_from_file_location('cpu_engineering_negative',SOURCE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Qualification(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='DTC_NEGATIVE_CPU_',dir='/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis');self.root=P(self.tmp.name);self.m=module();self.m.OUT=self.root/'original';self.m.OUT.mkdir();self.m.PROC=self.root/'proc';self.m.PROC.mkdir();self.m.identity=lambda:dict(CPU_FIXTURE_ONLY=True)
  for name,data in [('raw.log.gz',b'CPU fixture only\n'),('progress.jsonl.gz',(json.dumps(dict(generation=self.m.U,seq=1,end='NONE',completed=42))+'\n').encode()),('RESOURCE_SAMPLES.jsonl.gz',b'{"CPU_FIXTURE_ONLY":true}\n')]:
   (self.m.OUT/name).write_bytes(gzip.compress(data,mtime=0))
  (self.m.OUT/'empty').mkdir();(self.m.OUT/'perf_counter_2026-10-28_00-00-00.csv.gz').write_bytes(gzip.compress(b'counter\n',mtime=0));os.symlink('perf_counter_2026-10-28_00-00-00.csv.gz',self.m.OUT/'perf_counter.csv.gz')
 def tearDown(self):self.tmp.cleanup()
 def make_proc(self,pid=999,env=b'',flags=None):
  d=self.m.PROC/str(pid);d.mkdir();(d/'fd').mkdir();(d/'fdinfo').mkdir();(d/'stat').write_text(str(pid)+' (CPU_FIXTURE) '+' '.join(['S']+['0']*18+['123']));(d/'environ').write_bytes(env)
  if flags is not None:
   os.symlink(self.m.OUT/'raw.log.gz',d/'fd/3');(d/'fdinfo/3').write_text('flags:\t'+oct(flags)[2:]+'\n')
  return d
 def test_inventory_and_crc_complete(self):
  rows=self.m.inventory_tree(self.m.OUT);self.assertEqual(len(rows),7);self.assertEqual(self.m.gzip_evidence(self.m.OUT)['progress.jsonl.gz']['natural_terminal_count'],0)
 def test_inventory_rejects_symlink_and_fifo(self):
  os.symlink('/etc/passwd',self.m.OUT/'bad')
  with self.assertRaises(RuntimeError):self.m.inventory_tree(self.m.OUT)
  (self.m.OUT/'bad').unlink();os.mkfifo(self.m.OUT/'bad')
  with self.assertRaises(RuntimeError):self.m.inventory_tree(self.m.OUT)
 def test_crc_and_natural_or_sequence_rejected(self):
  path=self.m.OUT/'raw.log.gz';b=path.read_bytes();path.write_bytes(b[:-1])
  with self.assertRaises((EOFError,OSError)):self.m.gzip_evidence(self.m.OUT)
  path.write_bytes(b)
  for change in [dict(seq=2,end='NONE'),dict(seq=1,end='NATURAL')]:
   (self.m.OUT/'progress.jsonl.gz').write_bytes(gzip.compress((json.dumps(dict(generation=self.m.U,completed=42,**change))+'\n').encode()))
   with self.assertRaises(RuntimeError):self.m.gzip_evidence(self.m.OUT)
 def test_atomic_immutable_no_overwrite(self):
  p=self.root/'immutable.json';self.m.atomic_immutable(p,b'FIRST');self.m.atomic_immutable(p,b'FIRST')
  with self.assertRaises(RuntimeError):self.m.atomic_immutable(p,b'SECOND')
  self.assertEqual(p.read_bytes(),b'FIRST')
  os.symlink(p,self.root/'alias')
  with self.assertRaises(RuntimeError):self.m.atomic_immutable(self.root/'alias',b'FIRST')
 def test_true164_atomic_metadata_publication_fixture(self):
  with tempfile.TemporaryDirectory(prefix='CPU_NAS_ATOMIC_ONLY_',dir=SOURCE.parent)as name:
   p=P(name)/'CPU_ONLY.json';self.m.atomic_immutable(p,b'{"CPU_FIXTURE_ONLY":true}\n');self.m.atomic_immutable(p,b'{"CPU_FIXTURE_ONLY":true}\n')
   self.assertEqual(p.read_bytes(),b'{"CPU_FIXTURE_ONLY":true}\n')
 def test_departure_scans_all_env_and_fd(self):
  rows=self.m.inventory_tree(self.m.OUT);self.make_proc();v=self.m.departure_scan(rows,[]);self.assertEqual(v['permission_or_other_holes'],0)
  with self.assertRaises(RuntimeError):self.m.departure_scan(rows,[999])
  (self.m.PROC/'999/environ').write_bytes(b'DTC_AG7_GENERATION='+self.m.U.encode()+b'\0')
  with self.assertRaises(RuntimeError):self.m.departure_scan(rows,[])
 def test_writer_fds_rejected_but_readers_allowed(self):
  rows=self.m.inventory_tree(self.m.OUT);d=self.make_proc(flags=os.O_RDONLY);self.m.departure_scan(rows,[])
  (d/'fdinfo/3').write_text('flags:\t02\n')
  with self.assertRaises(RuntimeError):self.m.departure_scan(rows,[])
 def test_unreadable_environment_is_not_zero(self):
  rows=self.m.inventory_tree(self.m.OUT);self.make_proc()
  with patch.object(P,'read_bytes',side_effect=PermissionError('CPU unreadable')):
   with self.assertRaises(PermissionError):self.m.departure_scan(rows,[])
 def test_full_original_context_archive_restore_and_resume(self):
  m=self.m;b,f,v=m.libraries();context=self.root/'context';context.mkdir();(context/'CPU_ONLY.json').write_text('{"CPU_FIXTURE_ONLY":true}\n')
  rows=m.inventory_tree(m.OUT)
  ctx=dict(pins={'CPU_FIXTURE_ONLY':True})
  with patch.object(m,'scientific_identity',return_value=dict(CPU_FIXTURE_ONLY=True)):
   manifest=m.build_manifest(ctx,rows,context,'CPU_TX')
  bundle=self.root/'archive';bundle.mkdir();(bundle/'chunks').mkdir();m.immutable_json(bundle/'SOURCE_MANIFEST.json',manifest)
  original=m.inventory_tree(m.OUT)
  def check(mm,cc):self.assertEqual(m.inventory_tree(m.OUT),original);return True
  with patch.object(m,'resource_gate',return_value={'CPU_FIXTURE_ONLY':True}),patch.object(m,'source_check',side_effect=check):
   idx=m.archive_stream(b,f,v,bundle,manifest,ctx);again=m.archive_stream(b,f,v,bundle,manifest,ctx);self.assertEqual(idx,again)
  dst=self.root/'restored';proof=f.restore(bundle,manifest,dst,v,gate=lambda:None);self.assertEqual(len(proof),len(manifest['entries']));self.assertEqual(f.check_native(dst,manifest),proof)
  self.assertEqual(m.gzip_evidence(dst),m.gzip_evidence(m.OUT));self.assertEqual(m.inventory_tree(m.OUT),original)
  self.assertEqual((dst/m.PREFIX/'CPU_ONLY.json').read_bytes(),(context/'CPU_ONLY.json').read_bytes())
  # All bytes, original numeric metadata and the internal symlink were checked by frozen restore.
  chunk=bundle/'chunks'/idx['chunks'][0]['name'];data=chunk.read_bytes();chunk.write_bytes(data[:-1]+bytes([data[-1]^1]))
  with self.assertRaises(RuntimeError):f.verify_archive(bundle,manifest)
 def test_manifest_collision_no_source_mutation(self):
  (self.m.OUT/self.m.PREFIX).mkdir()
  with self.assertRaises(RuntimeError):self.m.inventory_tree(self.m.OUT)
 def test_partial_chunk_resume_and_conflict(self):
  m=self.m;b,f,v=m.libraries();bundle=self.root/'archive';bundle.mkdir();(bundle/'chunks').mkdir();man=dict(txid='CPU_TX')
  b.gate=lambda:None;data=b'CPU_FIXTURE_ONLY_DATA'*1000;partial=bundle/'chunks'/'00000000000000000000.part.writing';partial.write_bytes(data[:101]);w=b.RangeWriter(bundle,man,v,f);w.write(data);idx=w.finish();self.assertEqual((bundle/'chunks'/idx['chunks'][0]['name']).read_bytes(),data)
  other=self.root/'conflict';other.mkdir();(other/'chunks').mkdir();(other/'chunks'/'00000000000000000000.part.writing').write_bytes(b'WRONG')
  w=b.RangeWriter(other,man,v,f);w.write(data)
  with self.assertRaises(RuntimeError):w.finish()
 def test_execute_requires_exact_self_pin_before_any_mutation(self):
  with self.assertRaises(RuntimeError):self.m.run_execute('WRONG')
  self.assertFalse((self.root/'production').exists())
 def transaction_fixture(self,stack):
  m=self.m;libs=m.libraries();stack.enter_context(patch.object(m,'libraries',return_value=libs));m.R=self.root/'contract';m.R.mkdir();m.PROD=self.root/'NAS_CPU_ONLY'/m.C;m.RESTORE=self.root/'restore_parent/restores';m.RESTORE.parent.mkdir();m.RECEIVER=self.root/'receiver.lock';m.RECEIVER.write_bytes(b'')
  (m.OUT/'actual_file_process_network.log').write_text('1775705 CPU_FIXTURE_ONLY\n')
  key=str(m.R/'control/specs'/(m.C+'.json'));ctx=dict(pins={key:dict(sha256='CPU_ONLY_SPEC',bytes=0)},row=dict(intent_sha256='CPU_ONLY_INTENT'),spec={})
  original=m.inventory_tree(m.OUT)
  def check(mm,cc):self.assertEqual(m.inventory_tree(m.OUT),original);return True
  stack.enter_context(patch.object(m,'context',return_value=ctx));stack.enter_context(patch.object(m,'scientific_identity',return_value=dict(CPU_FIXTURE_ONLY=True)))
  stack.enter_context(patch.object(m,'context_payloads',return_value={'CPU_ONLY.json':b'{"CPU_FIXTURE_ONLY":true}\n'}));stack.enter_context(patch.object(m,'resource_gate',return_value=dict(CPU_FIXTURE_ONLY=True)));stack.enter_context(patch.object(m,'source_check',side_effect=check))
  # Actual process departure implementation remains active against an empty owned mock /proc.
  return m.sha(SOURCE),original
 def test_full_transaction_and_pinned_verifier_idempotence(self):
  with contextlib.ExitStack()as stack:
   pin,original=self.transaction_fixture(stack);a=self.m.run_execute(pin);self.assertEqual(a['status'],'VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED');self.assertIsNone(a['accepted_cycles']);self.assertFalse(a['performance_accepted'])
   b=self.m.run_execute(pin);self.assertEqual(a['certificate_sha256'],b['certificate_sha256']);self.assertEqual(self.m.inventory_tree(self.m.OUT),original)
   cert=P(a['certificate']);v=json.loads(cert.read_bytes());self.assertIsNone(v['launcher_wait_returncode']);self.assertFalse(v['original_done_present']);self.assertFalse(v['original_exit_present']);self.assertFalse(v['original_registry_execution_receipt_present'])
   self.assertEqual(self.m.verify_certificate(cert,pin)['certificate_sha256'],a['certificate_sha256'])
   # Archive source entries may not be dropped even if an attacker rehashes outer metadata.
   mp=cert.parent/'SOURCE_MANIFEST.json';manifest=json.loads(mp.read_bytes());manifest['entries']=manifest['entries'][1:];mp.write_bytes(self.m.canon(manifest))
   with self.assertRaises(RuntimeError):self.m.verify_certificate(cert,pin)
 def test_interrupted_restore_requires_explicit_new_owned_attempt(self):
  with contextlib.ExitStack()as stack:
   pin,original=self.transaction_fixture(stack);b,f,v=self.m.libraries();restore=f.restore
   with patch.object(self.m,'libraries',return_value=(b,f,v)):
    def fail_after_mkdir(bundle,m,dst,v,gate=None):dst.mkdir();(dst/'PARTIAL_CPU_ONLY').write_text('partial');raise RuntimeError('CPU injected interruption')
    with patch.object(f,'restore',side_effect=fail_after_mkdir):
     with self.assertRaises(RuntimeError):self.m.run_execute(pin)
    partials=list(self.m.RESTORE.glob('*'));self.assertEqual(len(partials),1)
    with self.assertRaises(RuntimeError):self.m.run_execute(pin)
    result=self.m.run_execute(pin,new_restore_attempt=True);self.assertEqual(result['status'],'VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED');self.assertTrue((partials[0]/'PARTIAL_CPU_ONLY').exists());self.assertEqual(self.m.inventory_tree(self.m.OUT),original)
 def test_certificate_rejects_unknown_to_fabricated(self):
  m=self.m;manifest=dict(scientific_identity={'CPU_FIXTURE_ONLY':True},source_identity={'CPU_FIXTURE_ONLY':True});idx=dict(archive_sha256='a');receipt=dict(schema='ENGINEERING_NEGATIVE_EVIDENCE_COPY_RECEIPT_V1',scientific_acceptance=False)
  dep=[dict(monotonic_ns=t,boot_id=m.BOOT,mnt_namespace=m.NS,proc_scan_complete=True,permission_or_other_holes=0,exact_generation_pids=[],known_related_pids_present=[],source_writer_fds=[])for t in [1,10**9+1]]
  cert=dict(schema=m.CERT,state='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY',cohort=m.C,uuid=m.U,request=m.REQ,accepted_cycles=None,launcher_wait_returncode=None,performance_accepted=False,scientific_acceptance=False,actual_signal_delivery='NOT_DIRECTLY_OBSERVED',observed_frontend_returncode=2,original_done_present=False,original_exit_present=False,original_registry_execution_receipt_present=False,scientific_identity=manifest['scientific_identity'],source_identity=manifest['source_identity'],original_spent_starts=1,refunded_starts=0,automatic_retry=False,source_disposition='SOURCE_KEEP',manifest_sha256=m.digest(m.canon(manifest)),archive_sha256='a',archive_receipt_sha256=m.digest(m.canon(receipt)),departure_proof_sha256=m.digest(m.canon(dep)))
  m.validate_certificate(cert,manifest,idx,receipt,dep)
  for key,value in [('accepted_cycles',1),('launcher_wait_returncode',-9),('performance_accepted',True),('scientific_acceptance',True),('original_done_present',True),('original_exit_present',True),('original_registry_execution_receipt_present',True),('refunded_starts',1),('automatic_retry',True),('uuid','wrong')]:
   cc=copy.deepcopy(cert);cc[key]=value
   with self.subTest(key=key),self.assertRaises(RuntimeError):m.validate_certificate(cc,manifest,idx,receipt,dep)
if __name__=='__main__':unittest.main(verbosity=2)
