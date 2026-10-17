"""One shared12GiB cap, predicted growth and real filesystem refusal; no app starts."""
import unittest,socket
from unittest.mock import patch
from registry import admit_result_output,live_result_output
from test_lane5 import identity

class OutputBudget12G(unittest.TestCase):
 def setUp(self):
  self.host=socket.gethostname();self.data={'hosts':{self.host:{'max_result_bytes':12*2**30,'default_run_output_limit_bytes':2*2**30,'min_disk_free_bytes':48*2**30}},'runs':{}}
  self.state={'actual_bytes':8*2**30,'resources':{'disk_free_bytes':70*2**30,'share_disk_free_bytes':41*2**30},'roots':{},'workspace_root':'/workspace/ep_l2_potential20261017_lane5_results','workspace_st_dev':156}
 def admit(self):
  with patch('registry.live_result_output',return_value=self.state):return admit_result_output(self.data,self.host,identity(),'/unused')
 def test_single_global12_not_per_campaign(self):
  self.state['actual_bytes']=12*2**30
  with self.assertRaisesRegex(ValueError,'ceiling'):self.admit()
  self.state['actual_bytes']+=1
  with self.assertRaisesRegex(ValueError,'ceiling'):self.admit()
 def test_predicted_growth_refused_before_mutation(self):
  self.state['actual_bytes']=11*2**30
  with self.assertRaisesRegex(ValueError,'predicted growth'):self.admit()
  self.assertEqual(self.data['runs'],{})
 def test_concurrent_reservations_share_total(self):
  self.data['runs']['active']={'status':'RUNNING','result_directory':'/not-existing','output_budget':{'predicted_growth_bytes':2*2**30}}
  with self.assertRaisesRegex(ValueError,'predicted growth'):self.admit()
 def test_workspace_and_share_floors_preserved(self):
  for k,v in [('disk_free_bytes',49*2**30),('share_disk_free_bytes',39*2**30)]:
   with self.subTest(k=k):
    old=self.state['resources'][k];self.state['resources'][k]=v
    with self.assertRaises(ValueError):self.admit()
    self.state['resources'][k]=old
 def test_safe_unknown_forecast_keeps_old_raw_cap(self):
  a=self.admit();self.assertEqual(a['predicted_growth_bytes'],2*2**30+128*2**20);self.assertEqual(self.data['hosts'][self.host]['default_run_output_limit_bytes'],2*2**30)
 def test_share_output_path_rejected(self):
  with self.assertRaises(ValueError):live_result_output('/root/share/new_unapproved_run')
if __name__=='__main__':unittest.main()
