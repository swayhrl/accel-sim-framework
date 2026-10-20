"""Targeted new E17 intake failures; no native process and no resource lease."""
import importlib.util,json,copy,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('main61off',P/'native_off_control.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CP=json.loads((P/'CHECKPOINT.json').read_text());E=json.loads(Path(CP['independent_native_receipt']['path']).read_text())
class EvidenceTests(unittest.TestCase):
 def test_actual_seventeen_retained(self):m.validate_native17(E,CP['source_identity'])
 def test_wrong_source_rejected(self):
  with self.assertRaisesRegex(ValueError,'source and scope'):m.validate_native17(E,dict(CP['source_identity'],binary_sha256='0'*64))
 def test_missing_case_rejected(self):
  bad=copy.deepcopy(E);bad['tests'].pop()
  with self.assertRaisesRegex(ValueError,'source and scope'):m.validate_native17(bad,CP['source_identity'])
 def test_failed_case_rejected(self):
  bad=copy.deepcopy(E);bad['tests'][0]['actual_exit']=1
  with self.assertRaisesRegex(ValueError,'changed/failed'):m.validate_native17(bad,CP['source_identity'])
 def test_missing_expected_assertion_rejected(self):
  bad=copy.deepcopy(E);key=next(iter(bad['tests'][0]['terminal_checks']));bad['tests'][0]['terminal_checks'][key]=False
  with self.assertRaisesRegex(ValueError,'assertion missing'):m.validate_native17(bad,CP['source_identity'])
if __name__=='__main__':unittest.main()
