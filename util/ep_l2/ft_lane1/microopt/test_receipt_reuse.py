"""Tool integrity cases only; do not count as simulator production tests."""
from pathlib import Path
import copy,hashlib,tempfile,unittest
from validate import verify_prior_command,REJECTION_PROOF

class PriorCommandIntegrity(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
 def record(self,name,code,text,expected=0):
  p=Path(self.temp.name)/(name+'.log');p.write_text(text)
  row=dict(log=str(p),log_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
      case_name=name,exit_code=code,expected_exit_code=expected,expected_failure=bool(expected))
  if expected:row['error']=repr(RuntimeError(f'{name} exited {expected}'))
  return row
 def test_real_positive_and_named_guard_rejection_are_reusable(self):
  verify_prior_command(self.record('native_OFF',0,'actual native PASS'))
  verify_prior_command(self.record('reject_P2',134,REJECTION_PROOF,134))
 def test_unexpected_failures_cannot_inherit_negative_scope(self):
  rows=[self.record('native_OFF',1,'unexpected failure'),
        self.record('native_ON',134,REJECTION_PROOF,134),
        self.record('reject_legacy',134,'different unrelated abort',134)]
  for row in rows:
   with self.subTest(case=row['case_name']),self.assertRaises(AssertionError):verify_prior_command(row)
 def test_changed_log_or_resource_stop_cannot_be_reused(self):
  row=self.record('reject_Ideal',134,REJECTION_PROOF,134)
  stopped=copy.deepcopy(row);stopped['resource_stop']={'disk_free_bytes':0}
  with self.assertRaises(AssertionError):verify_prior_command(stopped)
  timed_out=copy.deepcopy(row);timed_out['error']=repr(RuntimeError('owned build/test timeout'))
  with self.assertRaises(AssertionError):verify_prior_command(timed_out)
  Path(row['log']).write_text('modified after accepted receipt')
  with self.assertRaises(AssertionError):verify_prior_command(row)

if __name__=='__main__':unittest.main()
