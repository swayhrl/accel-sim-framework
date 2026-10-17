"""Reject parser recovery outside exact native-success failure; no simulator."""
from copy import deepcopy
import hashlib,json,unittest
from registry import canonical,write_json
from test_parallel_registry import ParallelRegistry
from test_lane5 import identity

class PostprocessingRecovery(unittest.TestCase):
 def setUp(self):
  self.f=ParallelRegistry();self.f.setUp();self.addCleanup(self.f.tearDown);self.r=self.f.registry
  _,row=self.r.claim(identity(),'lane5','/original',resources=self.f.resources,experiment=self.f.exp)
  self.key=row['run_key'];self.lease=row['lease_id'];self.r.update(self.key,self.lease,'FAILED',exit_code=0,detail='InvalidEvidence: production terminal parser failed',raw_log_sha256='a'*64)
  self.old=self.r.snapshot()['runs'][self.key];self.path=self.f.root/'parser_recovery.json';self.recovery={'status':'COMPLETE_VALID','new_simulator_starts':0,'identity':self.old['identity'],'run_key':self.key,'old_terminal_sha256':hashlib.sha256(canonical(self.old)).hexdigest(),'raw_log_sha256':'a'*64,'new_result_directory':'/unapproved'}
 def proof(self):
  write_json(self.path,self.recovery);return {'path':str(self.path),'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()}
 def test_raw_identity_and_start_mutations_refused(self):
  for k,v in [('raw_log_sha256','b'*64),('run_key','c'*64),('identity',{}),('new_simulator_starts',1),('old_terminal_sha256','0'*64)]:
   with self.subTest(k=k):
    old=deepcopy(self.recovery);self.recovery[k]=v
    with self.assertRaises(ValueError):self.r.revalidate_postprocessing(self.key,self.lease,self.proof())
    self.recovery=old;self.assertEqual(self.r.snapshot()['runs'][self.key],self.old)
 def test_nonzero_exit_live_and_success_refused(self):
  for fields in [{'exit_code':1},{'status':'RUNNING'},{'status':'COMPLETE_VALID'},{'detail':'native runtime abort'}]:
   with self.subTest(fields=fields):
    with self.r.locked() as d:d['runs'][self.key]={**self.old,**fields}
    self.recovery['old_terminal_sha256']=hashlib.sha256(canonical({**self.old,**fields})).hexdigest()
    with self.assertRaises(ValueError):self.r.revalidate_postprocessing(self.key,self.lease,self.proof())
 def test_changed_proof_and_stale_lease_refused(self):
  proof=self.proof();self.path.write_text('{}')
  with self.assertRaises(ValueError):self.r.revalidate_postprocessing(self.key,self.lease,proof)
  with self.assertRaises(ValueError):self.r.revalidate_postprocessing(self.key,'stale',self.proof())
if __name__=='__main__':unittest.main()
