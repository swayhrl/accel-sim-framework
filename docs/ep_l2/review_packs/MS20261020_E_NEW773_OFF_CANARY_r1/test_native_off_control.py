import importlib.util,json,sys,copy,time
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'util/ep_l2/mechanism_e'))
import test_coordinator as fixtures
import unittest
import coordinator as c
s=importlib.util.spec_from_file_location('off_control',Path.cwd()/'docs/ep_l2/review_packs/MS20261020_E_NEW773_OFF_CANARY_r1/native_off_control.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class OffControlTests(unittest.TestCase):
 save=fixtures.ControlTests.save
 read=fixtures.ControlTests.read
 def setUp(self):
  fixtures.ControlTests.setUp(self);self.ledger.update(authority_commit=c.AUTHORITY,maximum_actual_starts=40,reservations=copy.deepcopy(c.policy_v2.RESERVATIONS));self.ledger['final_source_identity']={k:self.identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')};self.identity['feature_vector']['finite_wbuf']=False;self.identity['workload']='vectorAdd_4M'
  self.cp=self.root/'control.json';self.cp.write_text('immutable fixture checkpoint not scientific')
  self.ledger['input_selections']['D_V2_vectorAdd_4M']=self.ledger['input_selections']['fixture'];self.ledger['native_off_control_binding']=dict(path='HISTORICAL_OLD_SOURCE_CONTROL',sha256='0'*64);self.ledger['native_off_control_attempt']='E001_HISTORICAL';self.ledger['native_off_controls_by_binary']={self.identity['binary_sha256']:dict(binding=dict(path=str(self.cp.resolve()),sha256=c.digest(self.cp)))};self.save()
  self.s=dict(campaign_id=c.CAMPAIGN,prepared_by='E',source_identity=self.ledger['final_source_identity'],identity=self.identity,run_key=c.run_key(self.identity),scientific_performance_endpoint=False,actual_start_bucket='contingency',expected_metrics=dict(cycle=73873,insn=56000000),maximum_result_bytes=384*2**20,memory_bytes=4*c.GIB)
 def test_canary_reserves_original_contingency_without_faking_qualification(self):
  a=m.reserve(self.coord,self.s,self.cp);d=self.read();i=d[c.FIELD];self.assertEqual(a['budget_bucket'],'contingency');self.assertEqual(i['actual_starts'],0);self.assertEqual(i['remaining_start_capacity'],39);self.assertNotIn(a['qualification_id'],i['qualifications']);self.assertFalse(i['accepted_results']);self.assertEqual(d['campaigns'],self.data['campaigns'])
 def test_canary_replay_is_rejected(self):
  m.reserve(self.coord,self.s,self.cp)
  with self.assertRaisesRegex(ValueError,'already reserved'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_changed_source_rejected(self):
  self.s['source_identity']=dict(self.s['source_identity'],binary_sha256='f'*64)
  with self.assertRaisesRegex(ValueError,'wrong control source'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_changed_checkpoint_rejected(self):
  self.cp.write_text('changed')
  with self.assertRaisesRegex(ValueError,'binding changed'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_cannot_be_performance_endpoint(self):
  self.s['scientific_performance_endpoint']=True
  with self.assertRaisesRegex(ValueError,'never a performance'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_uses_actual_resource_gate(self):
  self.live['share_disk_free_bytes']=40*c.GIB-1
  with self.assertRaisesRegex(ValueError,'Share'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_rejects_exhausted40(self):
  self.ledger['attempts']=[dict(actual_start=True,state='FAILED',budget_bucket='seven_workload_common_S_F') for _ in range(40)];self.save()
  with self.assertRaisesRegex(ValueError,'original40'):m.reserve(self.coord,self.s,self.cp)
 def test_canary_rejects_exhausted8(self):
  self.ledger['attempts']=[dict(actual_start=True,state='FAILED',budget_bucket='contingency') for _ in range(8)];self.save()
  with self.assertRaisesRegex(ValueError,'contingency8'):m.reserve(self.coord,self.s,self.cp)
 def test_old_source_attempt_and_binding_preserved(self):
  old=self.read()[c.FIELD];m.reserve(self.coord,self.s,self.cp);new=self.coord.snapshot()
  self.assertEqual(new['native_off_control_attempt'],old['native_off_control_attempt'])
  self.assertEqual(new['native_off_control_binding'],old['native_off_control_binding'])
  self.assertIn('attempt',new['native_off_controls_by_binary'][self.identity['binary_sha256']])
 def test_mismatched_run_key_rejected(self):
  self.s['run_key']='f'*64
  with self.assertRaisesRegex(ValueError,'wrong control key'):m.reserve(self.coord,self.s,self.cp)
if __name__=='__main__':
 import unittest
 unittest.main()
