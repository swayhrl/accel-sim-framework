#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_authority import form_b_gate

def h(v,sparse,base=True,target=True):return {'metadata':{'model_version':str(v),'sparse':str(sparse)},'has_base_hash':base,'has_target_hash':target}
class Tests(unittest.TestCase):
 def test_valid_form_b(self):self.assertEqual(form_b_gate([h(1,False),h(2,True),h(3,True),h(4,True)],True),(True,[]))
 def test_missing_hashes_rejected(self):
  ok,r=form_b_gate([h(1,False),h(2,True,False,False),h(3,True,False,False),h(4,True,False,False)],False);self.assertFalse(ok);self.assertIn('PATCH_BASE_HASH_MISSING',r);self.assertIn('RECONSTRUCTED_TARGET_HASH_MISSING',r);self.assertIn('PUBLIC_CONSUMER_WRONG_BASE_REJECTION_MISSING',r)
 def test_nonconsecutive_rejected(self):self.assertIn('VERSIONS_NOT_CONSECUTIVE',form_b_gate([h(1,False),h(2,True),h(4,True),h(5,True)],True)[1])
 def test_first_must_be_anchor(self):self.assertIn('FIRST_VERSION_NOT_FULL_ANCHOR',form_b_gate([h(1,True),h(2,True),h(3,True),h(4,True)],True)[1])
if __name__=='__main__':unittest.main()
