import json,re,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,"util/vm_tlb/c16/data_plane")
from pipeline import *
def m(r,a=[]):return {"schema_version":1,"run_id":r,"created_at_utc":"2026-09-15T00:00:00Z","scientific_status":"DIAGNOSTIC","producer":{"hostname":"109","gpu_name":"synthetic","gpu_uuid":"none","driver":"none","cuda":"none"},"git":{"repository":"x","commit":"0"*40,"dirty":False},"model":{"model_id":"synthetic","revision":"r","asset_receipt_sha256":"0"*64},"input":{"binding_id":"b","authority_status":"SYNTHETIC","receipt_sha256":"1"*64,"token_ids_sha256_or_semantic_hash":"2"*64},"scenario":{"batch":1,"prefill_tokens":1,"decode_tokens":1,"input_class":"SYNTHETIC","phase":"TEST"},"runtime":{"python":"3","torch":"none","transformers":"none","dtype":"none","attention_backend":"none"},"capture":{"instrument":"none","tool_version":"none","tool_identity_sha256_if_applicable":None,"target":"none","exact_argv":[]},"artifacts":a}
class T(unittest.TestCase):
 def setup(self):
  q=tempfile.TemporaryDirectory();self.addCleanup(q.cleanup);x=Path(q.name);(x/'ready').mkdir();(x/'transferred').mkdir();rid=run_id('m','s','p','i','t');s=x/rid;s.mkdir();(s/'a').write_text('x');mfile=x/'m.json';mfile.write_text(json.dumps(m(rid)));return x,rid,s,mfile
 def test_T1_valid_finalize(self):x,r,s,mf=self.setup();self.assertTrue(finalize(s,x/'ready',mf,r)[0].is_dir())
 def test_T2_missing_artifact(self):x,r,s,mf=self.setup();(s/'a').unlink();self.assertRaises(ValueError,finalize,s,x/'ready',mf,r)
 def test_T3_mutated_declared_hash(self):x,r,s,mf=self.setup();mf.write_text(json.dumps(m(r,[{'relative_path':'a','size_bytes':1,'sha256':'0'*64}])));self.assertRaises(ValueError,finalize,s,x/'ready',mf,r)
 def test_T4_symlink(self):x,r,s,mf=self.setup();(s/'l').symlink_to(s/'a');self.assertRaises(ValueError,finalize,s,x/'ready',mf,r)
 def test_T5_collision(self):x,r,s,mf=self.setup();(x/'ready'/r).mkdir();self.assertRaises(FileExistsError,finalize,s,x/'ready',mf,r)
 def test_T6_schema_status(self):x,r,s,mf=self.setup();z=m(r);z['scientific_status']='BAD';self.assertRaises(ValueError,validate_manifest,z);z=m(r);del z['model'];self.assertRaises(ValueError,validate_manifest,z)
 def test_T7_deterministic(self):x,r,s,mf=self.setup();(s/'b').write_text('y');self.assertEqual(inventory(s),inventory(s))
 def test_T8_publish_dry(self):a=publish_argv('hrl174new','/dest',run_id('m','s','p','i','t'),'/src');self.assertIn('--append-verify',a);self.assertNotIn('--delete',a);self.assertIn('.partial/',a[-1])
 def test_T9_malformed_ack(self):self.assertRaises(ValueError,validate_ack,{},'r','0'*64,'raw/r',1,1)
 def test_T10_wrong_ack_binding(self):a={'schema_version':1,'run_id':'wrong','source_manifest_sha256':'0'*64,'destination_manifest_or_verification_sha256':'1'*64,'file_count':1,'total_bytes':1,'destination_raw_path':'raw/r','verified_at_utc':'x','verification_status':'PASS','catalog_entry_sha256':'2'*64};self.assertRaises(ValueError,validate_ack,a,'r','0'*64,'raw/r',1,1)
 def test_T11_valid_ack_transition(self):x,r,s,mf=self.setup();d,c=finalize(s,x/'ready',mf,r);a={'schema_version':1,'run_id':r,'source_manifest_sha256':c['manifest_sha256'],'destination_manifest_or_verification_sha256':'1'*64,'file_count':c['file_count'],'total_bytes':c['total_bytes'],'destination_raw_path':'raw/'+r,'verified_at_utc':'x','verification_status':'PASS','catalog_entry_sha256':'2'*64};validate_ack(a,r,c['manifest_sha256'],'raw/'+r,c['file_count'],c['total_bytes']);self.assertTrue(transition(x/'ready',x/'transferred',r).is_dir())
 def test_T12_cleanup_no_delete(self):x,r,s,mf=self.setup();self.assertFalse(cleanup(s)['deleted']);self.assertTrue((s/'a').exists())
 def test_T13_10k_unique_safe(self):a={run_id('m','s','p','i','t') for _ in range(10000)};self.assertEqual(len(a),10000);self.assertTrue(all(re.fullmatch(r'C16R_[A-Za-z0-9_.-]+',x) for x in a))
if __name__=='__main__':unittest.main()
