"""No real registry or simulator is touched: exact one-replay/budget controls."""
import importlib.util,json,sys,copy
from pathlib import Path
import unittest
sys.path.insert(0,str(Path.cwd()/'util/ep_l2/mechanism_e'))
import coordinator as c
import test_coordinator as f
spec=importlib.util.spec_from_file_location('forensic_control',Path(__file__).with_name('diagnostic_replay.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ForensicControlTests(unittest.TestCase):
 save=f.ControlTests.save
 read=f.ControlTests.read
 def setUp(self):
  f.ControlTests.setUp(self);self.identity['binary_sha256']='773271ac70f009dddcd4c522f66dcd37967e4f57ce1e5082d3fc5aea61f2f9f5'
  source={k:self.identity[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']}
  self.ledger.update(authority_commit=c.AUTHORITY,maximum_actual_starts=40,reservations=copy.deepcopy(c.policy_v2.RESERVATIONS),final_source_identity=source)
  self.original=copy.deepcopy(self.identity);self.identity['termination_contract']={'kind':'FORENSIC_ONLY'}
  self.cp=self.root/'cp.json';self.cp.write_text('immutable control fixture only')
  self.ledger['forensic_controls']={m.CONTROL_ID:dict(checkpoint_path=str(self.cp.resolve()),checkpoint_sha256=c.digest(self.cp))}
  self.ledger['attempts']=[dict(attempt_id='E006_original',identity=self.original,profile='F',actual_start=True,state='FAILED',budget_bucket='contingency')]
  self.s=dict(campaign_id=c.CAMPAIGN,prepared_by='E',source_identity=source,identity=self.identity,original_identity=self.original,original_attempt_id='E006_original',run_key=c.run_key(self.identity),scientific_performance_endpoint=False,purpose='READ_ONLY_ABORT_STATE_NO_ACCEPTANCE',maximum_result_bytes=384*2**20,memory_bytes=8*c.GIB,CPU=2)
  self.save()
 def test_reserve_is_not_actual_start_or_fake_qualification(self):
  a=m.reserve(self.coord,self.s,self.cp);i=self.coord.snapshot();self.assertEqual(i['actual_starts'],1);self.assertEqual(i['remaining_start_capacity'],38);self.assertEqual(a['budget_bucket'],'contingency');self.assertNotIn(a['qualification_id'],i['qualifications']);self.assertFalse(i['accepted_results'])
 def test_original_failed_attempt_is_immutable(self):
  m.reserve(self.coord,self.s,self.cp);self.assertEqual(self.coord.snapshot()['attempts'][0],self.ledger['attempts'][0]);self.assertEqual(self.read()['campaigns'],self.data['campaigns'])
 def test_replay_cannot_be_launched_twice(self):
  m.reserve(self.coord,self.s,self.cp)
  with self.assertRaisesRegex(ValueError,'alreadyreserved'):m.reserve(self.coord,self.s,self.cp)
 def test_wrong_source_rejected(self):
  self.s['source_identity']=dict(self.s['source_identity'],core_source_commit='f'*40)
  with self.assertRaisesRegex(ValueError,'wrongsource'):m.reserve(self.coord,self.s,self.cp)
 def test_different_original_identity_rejected(self):
  self.s['original_identity']=dict(self.s['original_identity'],workload='OTHER')
  with self.assertRaisesRegex(ValueError,'originalfailedF'):m.reserve(self.coord,self.s,self.cp)
 def test_modified_checkpoint_rejected(self):
  self.cp.write_text('changed')
  with self.assertRaisesRegex(ValueError,'binding changed'):m.reserve(self.coord,self.s,self.cp)
 def test_no_performance_promotion(self):
  self.s['scientific_performance_endpoint']=True
  with self.assertRaisesRegex(ValueError,'forensic-only'):m.reserve(self.coord,self.s,self.cp)
 def test_real_share_protection_applies(self):
  self.live['share_disk_free_bytes']=40*c.GIB-1
  with self.assertRaisesRegex(ValueError,'Share'):m.reserve(self.coord,self.s,self.cp)
 def test_no_refund_exhausted40(self):
  self.ledger['attempts'] += [dict(actual_start=True,state='FAILED',budget_bucket='seven_workload_common_S_F') for _ in range(39)];self.save()
  with self.assertRaisesRegex(ValueError,'original40'):m.reserve(self.coord,self.s,self.cp)
 def test_contingency8_exhaustion_applies(self):
  self.ledger['attempts'] += [dict(actual_start=True,state='FAILED',budget_bucket='contingency') for _ in range(7)];self.save()
  with self.assertRaisesRegex(ValueError,'contingency8'):m.reserve(self.coord,self.s,self.cp)
if __name__=='__main__':unittest.main()
