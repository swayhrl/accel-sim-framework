"""Same-key failed attempt recovery preserves every prior lease/evidence and budget."""
from copy import deepcopy
import json,hashlib,unittest
from registry import write_json,run_key,attempt_count,PARALLEL
from test_parallel_registry import ParallelRegistry

class AuditedRetryTests(unittest.TestCase):
 def setUp(self):
  self.fixture=ParallelRegistry();self.fixture.setUp();self.addCleanup(self.fixture.tearDown);self.r=self.fixture.registry;self.identity=__import__('test_lane5').identity();self.exp=self.fixture.exp
  _,self.old=self.r.claim(self.identity,'lane5','/failed/immutable_r1',resources=self.fixture.resources,experiment=self.exp);self.r.update(self.old['run_key'],self.old['lease_id'],'FAILED',detail='copy executable mode missing');self.terminal=deepcopy(self.r.snapshot()['runs'][self.old['run_key']]);self.file=self.fixture.root/'recovery.json';self.decision={'run_key':self.old['run_key'],'previous_lease_id':self.old['lease_id'],'new_result_directory':'/new/immutable_r2','engineering_reason':'copy-mode fix, exact identity unchanged'};write_json(self.file,self.decision);self.proof={'path':str(self.file),'sha256':hashlib.sha256(self.file.read_bytes()).hexdigest()}
 def retry(self):return self.r.claim(self.identity,'lane5','/new/immutable_r2',resources=self.fixture.resources,experiment=self.exp,retry_checkpoint=self.proof)
 def test_same_key_keeps_old_record_and_counts_failed_attempt(self):
  fresh,row=self.retry();self.assertTrue(fresh);self.assertEqual(row['attempt_history'],[self.terminal]);self.assertEqual(attempt_count(row),2);self.assertEqual(row['run_key'],self.old['run_key']);self.assertNotEqual(row['lease_id'],self.old['lease_id'])
  with self.assertRaises(ValueError):self.r.update(row['run_key'],self.old['lease_id'],'FAILED')
 def test_replay_and_live_retry_refused(self):
  self.retry()
  with self.assertRaises(ValueError):self.retry()
 def test_altered_decision_or_identity_refused(self):
  self.file.write_text('{}')
  with self.assertRaises(ValueError):self.retry()
 def test_terminal_success_never_retried(self):
  with self.r.locked() as d:d['runs'][self.old['run_key']]['status']='COMPLETE_VALID'
  with self.assertRaises(ValueError):self.retry()

if __name__=='__main__':unittest.main()
