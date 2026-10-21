"""Pure parser-revision equivalence checks; no recovery function or native run."""
from pathlib import Path
import importlib.util,unittest,copy,json,hashlib
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('recovery_draft',P/'recover_completed_parser_only.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Boundaries(unittest.TestCase):
 def setUp(self):
  self.q={'terminal_parser':{'path':'old.py','sha256':'a'},'parser_seal':{'sha256':'a'},'qualified_unix':1,'scope_note':'old',
   'source_identity':{'binary_sha256':'93'},'archive':{'sha256':'bed'},'gates':{'data':{'status':'PASS'}},
   'supported_profiles':{'S':{'W':0}},'capacity_diagnostic':{'validation_scope':{'expected_full_instructions':143129372},'parser_seal':{'sha256':'a'}}}
 def test_exact_parser_metadata_only_revision(self):
  q=copy.deepcopy(self.q);q.update(terminal_parser={'path':'new.py','sha256':'b'},parser_seal={'sha256':'b'},qualified_unix=2,scope_note='decoder order repair',parser_only_revision={'previous':'a'})
  q['capacity_diagnostic']['parser_seal']={'sha256':'b'}
  self.assertEqual(m.stable_q(q),m.stable_q(self.q))
 def test_binary_change_is_not_parser_repair(self):
  q=copy.deepcopy(self.q);q['source_identity']['binary_sha256']='other';self.assertNotEqual(m.stable_q(q),m.stable_q(self.q))
 def test_native_gate_change_is_not_parser_repair(self):
  q=copy.deepcopy(self.q);q['gates']['data']['status']='UNKNOWN';self.assertNotEqual(m.stable_q(q),m.stable_q(self.q))
 def test_input_instruction_scope_change_is_not_parser_repair(self):
  q=copy.deepcopy(self.q);q['capacity_diagnostic']['validation_scope']['expected_full_instructions']+=1;self.assertNotEqual(m.stable_q(q),m.stable_q(self.q))
 def test_profile_change_is_not_parser_repair(self):
  q=copy.deepcopy(self.q);q['supported_profiles']['S']['W']=1;self.assertNotEqual(m.stable_q(q),m.stable_q(self.q))
 def test_audit_allows_only_q_and_parser_hashes(self):
  a={'qualification_sha256':'a','parser':{'sha256':'a'},'identity':{'trace':'fixed'},'expected_full_instructions':100}
  b=copy.deepcopy(a);b.update(qualification_sha256='b',parser={'sha256':'b'});self.assertEqual(m.stable_audit(a),m.stable_audit(b))
  b['expected_full_instructions']=101;self.assertNotEqual(m.stable_audit(a),m.stable_audit(b))
 def test_spec_preserves_all_scientific_and_resource_conditions(self):
  a={'qualification_id':'a','parser':{},'input_audit':{},'labels':{'diagnostic':True},'maximum_result_bytes':384*2**20,'identity':{'binary':'fixed'}}
  b=copy.deepcopy(a);b.update(qualification_id='b',parser={'new':True},input_audit={'new':True});self.assertEqual(m.stable_spec(a),m.stable_spec(b))
  b['maximum_result_bytes']+=1;self.assertNotEqual(m.stable_spec(a),m.stable_spec(b))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Boundaries))
 (P/'RECOVERY_BOUNDARY_CONTROL_RESULT.json').write_text(json.dumps(dict(status='PASS' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,actual_recoveries=0,parser_invocations=0,native_applications=0,registry_writes=0,script_sha256=hashlib.sha256((P/'recover_completed_parser_only.py').read_bytes()).hexdigest()),indent=2)+'\n')
 raise SystemExit(not r.wasSuccessful())
