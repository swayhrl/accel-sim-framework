"""Synthetic metadata-only tests of Adapter.check; no binding/build/native PASS.
Construct an uninitialized check-only object explicitly to avoid executing a
producer/native release import: no configure_binding/parse/acceptance is called.
"""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
import tagpressure_validation as v
from test_controls import BIND

class SourceMetadataControls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='r5_metadata_only_',dir='/tmp/e2_r5_parser_candidate');p=Path(self.tmp.name);m=p/'SYNTHETIC_METADATA_ONLY.json';m.write_text('{"SYNTHETIC_FIXTURE":true}\n');ref={'path':str(m),'sha256':hashlib.sha256(m.read_bytes()).hexdigest()}
  self.a=v.Adapter.__new__(v.Adapter);self.a.source={**BIND,'framework_source_commit':'4'*40,'vendor_pybind11_commit':'5'*40};self.a.binding={k:copy.deepcopy(ref) for k in v.REF_KEYS}
  feat={'payload_capacity_per_slice':1168,'bank_count':4,'ops_per_bank_cycle':1,'wbuf_entries':16,'unified_wb':True,'tvd':True,'ro_tag_detach':True,'ro_line_mshr_bypass':True};prof={'research_switches':dict.fromkeys(('W','V','T','M'),1),'feature_vector':feat,'ideal_vector':{'copy_free':False}}
  contract={'validation_scope':self.a.binding,'trace_content_sha256':'6'*64,'runtime_config_sha256':'7'*64,'input_selection_id':'SYNTHETIC_SELECTION','termination_contract':{'kind':'FULL_APPLICATION_MECHANISM_V2'},'expected_full_instructions':123,'expected_kernel_uids':[1]}
  self.q={'status':'INDEPENDENTLY_QUALIFIED','qualified_by':'E','scientific_scope':v.SCI_SCOPE,'synthetic_fixture':False,'source_identity':self.a.source,'detach_observer_diagnostic':contract,'supported_profiles':{'F':prof},'terminal_parser':ref};self.qpath=p/'Q_SYNTHETIC_NOT_REGISTERED.json'
  self.spec={'qualification_id':'','scientific_scope':v.SCI_SCOPE,'profile':'F','pairs':[],'vendor_pybind11_commit':self.a.source['vendor_pybind11_commit'],'identity':{'core_source_commit':BIND['core_source_commit'],'framework_source_commit':'4'*40,'binary_sha256':BIND['binary_sha256'],'feature_vector':feat,'ideal_vector':prof['ideal_vector'],'trace_content_sha256':'6'*64,'runtime_config_sha256':'7'*64,'termination_contract':contract['termination_contract']},'profile_semantics':prof,'environment':{'EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1'},'selection_id':'SYNTHETIC_SELECTION','parser':ref};self.audit={};self.seal()
 def tearDown(self):self.tmp.cleanup()
 def seal(self):
  self.qpath.write_text(json.dumps(self.q));d=hashlib.sha256(self.qpath.read_bytes()).hexdigest();self.row={'path':str(self.qpath),'sha256':d,'qualification':self.q};self.spec['qualification_id']=d;self.audit={'qualification_sha256':d,'expected_full_instructions':123}
 def good(self):self.assertEqual(self.a.check(self.spec,self.row,self.audit)['expected_full_instructions'],123)
 def bad(self):
  with self.assertRaises((ValueError,KeyError)):self.a.check(self.spec,self.row,self.audit)
 def test_check_only_exact_metadata(self):self.good();self.assertIsNone(v._ADAPTER);self.assertFalse(v.INDEPENDENT_SCHEMA_VALIDATION_READY)
 def test_old_scope_rejected(self):self.spec['scientific_scope']='DETACH_OBSERVER_DIAGNOSTIC_POINT_V1';self.bad()
 def test_source_mismatch(self):self.spec['identity']['core_source_commit']='a'*40;self.bad()
 def test_binary_mismatch(self):self.spec['identity']['binary_sha256']='a'*64;self.bad()
 def test_missing_new_observer_env(self):del self.spec['environment']['EPL2_TAGPRESSURE_DIAG'];self.bad()
 def test_input_mismatch(self):self.spec['identity']['trace_content_sha256']='a'*64;self.bad()
 def test_config_mismatch(self):self.spec['identity']['runtime_config_sha256']='a'*64;self.bad()
 def test_pair_claim(self):self.spec['pair_id']='FAKEPAIR';self.bad()
 def test_qualification_file_changed(self):self.qpath.write_text('{}');self.bad()
 def test_q_source_mismatch(self):self.q['source_identity']=copy.deepcopy(self.a.source);self.q['source_identity']['binary_sha256']='a'*64;self.seal();self.bad()
 def test_wrong_scope_binding(self):self.q['detach_observer_diagnostic']['validation_scope']={};self.seal();self.bad()
 def test_bool_kernel_uid(self):self.q['detach_observer_diagnostic']['expected_kernel_uids']=[True];self.seal();self.bad()
 def test_duplicate_kernel_uid(self):self.q['detach_observer_diagnostic']['expected_kernel_uids']=[1,1];self.seal();self.bad()
 def test_full_instruction_audit_mismatch(self):self.audit['expected_full_instructions']=122;self.bad()
 def test_no_default_binding_public_validator(self):
  with self.assertRaises(ValueError):v.validate_summary({},self.spec,self.row,self.audit)

if __name__=='__main__':unittest.main(verbosity=2)
