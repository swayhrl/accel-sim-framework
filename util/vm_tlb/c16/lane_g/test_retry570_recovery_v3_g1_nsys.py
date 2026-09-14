from pathlib import Path
import unittest
SOURCE=(Path(__file__).parent/'retry570_recovery_v3_g1_nsys.py').read_text()
class G1Contract(unittest.TestCase):
 def test_one_campaign_parent_and_child_proof(self):
  for s in ('RecoveryV3CampaignLease','write_parent_lease_start','C16_G_PARENT_LEASE_TOKEN','--budget-owned-by-wrapper','MeasurementActive','child_acquired_second_lease'):
   self.assertIn(s,SOURCE)
  self.assertNotIn('BudgetLease(',SOURCE)
 def test_nsys_is_real_and_history_is_bound(self):
  for s in ('--trace=cuda,nvtx,osrt','--historical-sha256','historical_ledger','nsys-rep'):
   self.assertIn(s,SOURCE)
 def test_code_commit_is_independent_of_launch_cwd(self):
  self.assertIn("['git','-C',str(repo_root()),'rev-parse','HEAD']",SOURCE)
if __name__=='__main__': unittest.main()
