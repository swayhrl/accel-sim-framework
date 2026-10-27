import pathlib,json,hashlib,copy,unittest,tempfile,importlib.util,os
from unittest.mock import patch
P=pathlib.Path;S=P(__file__).with_name('scan_m16_terminal_verifier_v2.py')
def mod():
 s=importlib.util.spec_from_file_location('v2_cpu',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def manifests(m):
 row=dict(path='native.raw',type='file',dev=2128,inode=123,nlink=1,allocated=4096,uid=0,gid=0,mode=420,size=4,mtime_ns=1,ctime_ns=2,sha256='a'*64)
 entries=[row]
 for name in ['']+sorted(m.CONTEXT_FILES):entries.append(dict(row,path=m.CONTEXT if not name else m.CONTEXT+'/'+name,type='directory'if not name else'file',inode=100+len(entries),dev=39))
 old=dict(schema='CPU_ONLY',entries=entries,original_entries=[copy.deepcopy(row)],selector_sha256=hashlib.sha256(canon(entries)).hexdigest(),source_root='CPU_NATIVE')
 return old,copy.deepcopy(old)
def reseal(v):v['selector_sha256']=hashlib.sha256(canon(v['entries'])).hexdigest()
class Qualify(unittest.TestCase):
 def test_context_only_inode_drift_legal_and_preserved(self):
  m=mod();a,b=manifests(m)
  for x in b['entries'][1:]:x['inode']+=10000
  reseal(b);saved=copy.deepcopy(a);v=m.compare_context_transport(a,b,canon);self.assertEqual(v['changed_count'],8);self.assertEqual(a,saved)
 def test_native_original_inode_and_all_metadata_drift_rejected(self):
  m=mod();a,b=manifests(m)
  for field in ['inode','dev','ctime_ns','mtime_ns','nlink','allocated','uid','gid','mode','size']:
   c=copy.deepcopy(b);c['entries'][0][field]+=1;reseal(c)
   with self.subTest(field=field),self.assertRaises(RuntimeError):m.compare_context_transport(a,c,canon)
 def test_context_non_inode_fields_strict(self):
  m=mod();a,b=manifests(m)
  for field in ['dev','ctime_ns','mtime_ns','nlink','allocated','uid','gid','mode','size']:
   c=copy.deepcopy(b);c['entries'][2][field]+=1;reseal(c)
   with self.subTest(field=field),self.assertRaises(RuntimeError):m.compare_context_transport(a,c,canon)
  for field,value in [('sha256','b'*64),('type','symlink'),('path',m.CONTEXT+'/EVIL.json')]:
   c=copy.deepcopy(b);c['entries'][2][field]=value;reseal(c)
   with self.subTest(field=field),self.assertRaises(RuntimeError):m.compare_context_transport(a,c,canon)
 def test_context_member_holes_or_extra_paths_rejected(self):
  m=mod();a,b=manifests(m)
  for change in ['missing','extra','order']:
   c=copy.deepcopy(b)
   if change=='missing':c['entries'].pop()
   if change=='extra':c['entries'].append(dict(c['entries'][-1],path=m.CONTEXT+'/EXTRA'))
   if change=='order':c['entries'].reverse()
   reseal(c)
   with self.subTest(change=change),self.assertRaises(RuntimeError):m.compare_context_transport(a,c,canon)
 def test_old_or_current_selector_fabrication_rejected(self):
  m=mod();a,b=manifests(m)
  for which in ['old','current']:
   aa,bb=copy.deepcopy(a),copy.deepcopy(b);target=aa if which=='old'else bb;target['selector_sha256']='fake'
   with self.assertRaises(RuntimeError):m.compare_context_transport(aa,bb,canon)
 def test_old_source_and_new_self_drift_failclosed(self):
  m=mod()
  with self.assertRaises(RuntimeError):m.verify_bundle(m.EXPECTED_BUNDLE,'wrong-self')
  with tempfile.TemporaryDirectory(prefix='DTC_NEGATIVE_V2_CPU_',dir='/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis')as d:
   p=P(d)/'old.py';p.write_text('CPU_ONLY')
   with patch.object(m,'OLD_SOURCE',p):
    with self.assertRaises(RuntimeError):m.old_module()
 def test_original_manifest_certificate_archive_seals_reject_tamper(self):
  m=mod()
  with tempfile.TemporaryDirectory(prefix='DTC_NEGATIVE_V2_CPU_',dir='/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis')as d:
   p=P(d)/'SEALED';p.write_bytes(b'CPU_ORIGINAL');pin=m.sha(p)
   with patch.object(m,'SEALED',{'SEALED':pin}):
    m.verified_original_seals(P(d));p.write_bytes(b'CPU_TAMPERED')
    with self.assertRaises(RuntimeError):m.verified_original_seals(P(d))
    p.unlink();os.symlink('/etc/hostname',p)
    with self.assertRaises(RuntimeError):m.verified_original_seals(P(d))
 def test_native_restore_content_and_mode_tamper_rejected(self):
  m=mod();o=m.old_module();b,f,v=o.libraries()
  with tempfile.TemporaryDirectory(prefix='DTC_NEGATIVE_V2_CPU_',dir='/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis')as d:
   root=P(d);p=root/'raw';p.write_bytes(b'CPU_ORIGINAL');manifest={'entries':o.inventory_tree(root)};f.check_native(root,manifest)
   p.write_bytes(b'CPU_TAMPERED')
   with self.assertRaises(RuntimeError):f.check_native(root,manifest)
   p.write_bytes(b'CPU_ORIGINAL');os.chmod(p,0o400)
   with self.assertRaises(RuntimeError):f.check_native(root,manifest)
 def test_manifest_nontransport_source_pins_cannot_drift(self):
  m=mod();a,b=manifests(m);b['source_root']='OTHER_NATIVE'
  with self.assertRaises(RuntimeError):m.compare_context_transport(a,b,canon)
 def test_frozen_archive_full_chunk_sha_tamper_rejected(self):
  m=mod();o=m.old_module();b,f,v=o.libraries();b.gate=lambda:None
  with tempfile.TemporaryDirectory(prefix='DTC_NEGATIVE_V2_CPU_',dir='/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis')as d:
   root=P(d);(root/'chunks').mkdir();manifest=dict(txid='CPU_ONLY',entries=[],reused_objects={});(root/'SOURCE_MANIFEST.json').write_bytes(o.canon(manifest));w=b.RangeWriter(root,manifest,v,f);w.write(b'CPU_ONLY_ARCHIVE_BYTES'*1000);idx=w.finish()
   (root/'ARCHIVE_INDEX.json').write_bytes(o.canon(idx));(root/'COMMIT.json').write_bytes(o.canon(dict(txid=manifest['txid'],manifest_sha256=o.digest(o.canon(manifest)),archive_index_sha256=o.digest(o.canon(idx)),policy='EXCLUSIVE_CREATE_COMMIT_MARKER_LAST')));f.verify_archive(root,manifest)
   chunk=root/'chunks'/idx['chunks'][0]['name'];data=chunk.read_bytes();chunk.write_bytes(data[:-1]+bytes([data[-1]^1]))
   with self.assertRaises(RuntimeError):f.verify_archive(root,manifest)
if __name__=='__main__':unittest.main(verbosity=2)
