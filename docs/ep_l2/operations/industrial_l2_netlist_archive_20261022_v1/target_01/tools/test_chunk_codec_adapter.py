
import unittest,tempfile,pathlib,os,json,hashlib,stat
import v9_transaction as v
import chunk_codec_adapter as a
class CodecTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='ops_v9_fixture_');self.root=pathlib.Path(self.temp.name);(self.root/'SYNTHETIC_ONLY').write_bytes(b'OPS_V9_SYNTHETIC_ONLY\n');src=self.root/'source';src.mkdir();self.data={}
  for i in range(9):
   name=a.PREFIXES[i//3]+'synthetic_%d.json'%i;p=src/name;p.parent.mkdir(parents=True,exist_ok=True);raw=(b'{"opaque":"'+bytes([65+i])*317+b'"}\n \n');p.write_bytes(raw);os.chmod(p,0o640);os.utime(p,ns=(1700000000123456789+i,1700000000123456789+i));self.data[name]=raw
  files=[dict(relative_path=n,type='regular',sha256=v.digest(raw),**v.identity((src/n).stat())) for n,raw in self.data.items()]
  ds={'.'}
  for n in self.data:ds.update(p.as_posix() for p in pathlib.PurePosixPath(n).parents)
  dirs=[dict(relative_path=n,type='directory',**v.identity((src/n).stat())) for n in sorted(ds)]
  self.man=dict(source_root='/workspace/repos/gpu-l2-cache-verilog/build',source_filesystem_identity='SYNTHETIC_ONLY',source_frozen_commit='a'*40,files=files,directories=dirs,selector_sha256=v.digest(v.canonical(files)),source_file_inventory_sha256=v.digest(v.canonical(files)),source_directory_inventory_sha256=v.digest(v.canonical(dirs)),genuine164_destination_root=str(self.root/'archive'),destination_path_on_174new=str(self.root/'archive'),source_originals_action='SOURCE_KEEP_NO_RELEASE_AUTHORITY')
  self.arc=a.Archive(self.root/'archive',self.man,fixture=True);self.name=next(iter(self.data));self.bridge=self.root/'bridge';self.bridge.write_bytes(self.data[self.name])
 def tearDown(self):
  v.fixture_root(self.root);self.temp.cleanup()
 def put(self,**kw):return self.arc.put(self.name,0,self.bridge,v.digest(self.data[self.name]),self.arc.txid,**kw)
 def fill(self):
  for name,raw in self.data.items():
   for off,end in [(0,100),(100,len(raw))]:
    b=raw[off:end];self.bridge.write_bytes(b);self.arc.put(name,off,self.bridge,v.digest(b),self.arc.txid)
 def test_roundtrip_all9_full_byte_SHA_native_fixture_metadata(self):
  self.fill();seal=self.arc.seal();self.assertEqual(len(seal['files']),9);receipt=self.arc.native_restore(self.root/'restored',fixture=True);self.assertEqual(receipt['status'],'SYNTHETIC_NATIVE_FIXTURE_PASS');self.assertTrue(receipt['fixture_only'])
  for n,b in self.data.items():self.assertEqual((self.root/'restored'/n).read_bytes(),b)
 def test_duplicate_reuses_verified_chunk(self):
  first=self.put();self.assertTrue(self.put()['reused']);self.assertEqual(first['compressed_sha256'],self.put()['compressed_sha256'])
 def test_crash_complete_partial_resumes_without_overwrite(self):
  with self.assertRaises(v.Hold):self.put(crash='partial')
  self.put();self.assertTrue(self.put()['reused'])
 def test_crash_final_without_receipt_adopts_after_validation(self):
  with self.assertRaises(v.Hold):self.put(crash='final_before_record')
  self.put();self.assertTrue(self.put()['reused'])
 def test_crash_after_receipt_reuses(self):
  with self.assertRaises(v.Hold):self.put(crash='record')
  self.assertTrue(self.put()['reused'])
 def test_wrong_txid_rejected_before_write(self):
  with self.assertRaises(v.Hold):self.arc.put(self.name,0,self.bridge,v.digest(self.data[self.name]),'b'*64)
  self.assertFalse(list((self.arc.root/'chunks').iterdir()))
 def test_corrupt_existing_chunk_refuses_overwrite(self):
  r=self.put();p=self.arc.root/'chunks'/r['chunk_file'];p.write_bytes(b'corrupt')
  with self.assertRaises(v.Hold):self.put()
  self.assertEqual(p.read_bytes(),b'corrupt')
 def test_truncated_partial_hold_no_blind_reset(self):
  key=self.arc.key(self.name,0);p=self.arc.root/'chunks'/(key+'.gz.partial');p.write_bytes(b'bad')
  with self.assertRaises(v.Hold):self.put()
  self.assertEqual(p.read_bytes(),b'bad')
 def test_missing_chunk_cannot_commit(self):
  self.put()
  with self.assertRaises(v.Hold):self.arc.seal()
  self.assertFalse((self.arc.root/'COMMIT.json').exists())
 def test_unowned_destination_refused(self):
  p=self.root/'foreign';p.mkdir();m=dict(self.man,genuine164_destination_root=str(p))
  with self.assertRaises(v.Hold):a.Archive(p,m,fixture=True)
 def test_restore_nonabsent_refuses_overwrite(self):
  self.fill();p=self.root/'restored';p.mkdir();(p/'keep').write_bytes(b'keep')
  with self.assertRaises(v.Hold):self.arc.native_restore(p,fixture=True)
  self.assertEqual((p/'keep').read_bytes(),b'keep')
 def test_fixture_cannot_claim_NATIVE164(self):
  self.fill()
  with self.assertRaises(v.Hold):self.arc.native_restore(self.root/'forbidden_native')
  self.assertFalse((self.root/'forbidden_native').exists())
 def test_path_or_frozen_count_change_refused(self):
  m=dict(self.man,files=self.man['files'][:-1]);m['selector_sha256']=v.digest(v.canonical(m['files']))
  with self.assertRaises(v.Hold):a.Archive(self.root/'another',m,fixture=True)
 def test_chunk_codec_or_selector_collision_refused(self):
  self.put();p=next((self.arc.root/'chunks').glob('*.json'));r=json.loads(p.read_bytes());r['raw_sha256']='0'*64;p.write_bytes(v.canonical(r))
  with self.assertRaises(v.Hold):self.put()

 def test_original_industrial_source_txid_retained(self):
  b=dict(source_fs_id=dict(dev=123,fsid=456,namespace='SYNTHETIC'),canonical_root=self.man['source_root'],exact_frozen_selector_sha256='d'*64,source_commit='a'*40,native164_destination=self.man['genuine164_destination_root'])
  raw=json.dumps(b,sort_keys=True,separators=(',',':')).encode();m=dict(self.man,original_source_binding=b,source_transaction_id=v.digest(raw),source_selector_sha256='d'*64)
  self.assertEqual(a.scope(m,fixture=True),v.digest(raw))
  m['source_transaction_id']='f'*64
  with self.assertRaises(v.Hold):a.scope(m,fixture=True)
 def test_industrial_binding_target_change_refused(self):
  b=dict(source_fs_id={},canonical_root=self.man['source_root'],exact_frozen_selector_sha256='d'*64,source_commit='a'*40,native164_destination='/different')
  m=dict(self.man,original_source_binding=b,source_transaction_id=v.digest(json.dumps(b,sort_keys=True,separators=(',',':')).encode()),source_selector_sha256='d'*64)
  with self.assertRaises(v.Hold):a.scope(m,fixture=True)
if __name__=='__main__':unittest.main(verbosity=2)
