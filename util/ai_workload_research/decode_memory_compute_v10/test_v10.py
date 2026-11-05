import unittest,tempfile,csv
from pathlib import Path
from v10_dispatch import audit_csv,PAIR
class V10Tests(unittest.TestCase):
 def csv(self,passes,backup,missing=False):
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);p=Path(d.name)/'x.csv'
  names=['Kernel Name','Grid Size','Block Size','profiler__replayer_passes','profiler__replayer_bytes_mem_backed_up.sum']
  if missing:names=names[:-1]
  with p.open('w') as f:
   w=csv.writer(f);w.writerow(names);w.writerow(['']*len(names));w.writerow(['gemv','1','1',str(passes),str(backup)][:len(names)])
  return p
 def test_singlepass_no_backup(self):self.assertTrue(audit_csv(self.csv(1,0))['safe_single_pass'])
 def test_multipass_rejected(self):self.assertFalse(audit_csv(self.csv(2,1000))['safe_single_pass'])
 def test_backup_not_assumed_zero(self):
  with self.assertRaises((ValueError,KeyError)):audit_csv(self.csv(1,0,True))
 def test_singlepass_backup_still_rejected(self):self.assertFalse(audit_csv(self.csv(1,1000))['safe_single_pass'])
 def test_sparse_metrics(self):self.assertEqual(PAIR,['dram__bytes_read.sum','gpu__time_duration.sum'])
 def test_no_whole_curve_dispatch(self):
  s=(Path(__file__).parent/'v10_dispatch.py').read_text();self.assertNotIn("'CURVE'",s)
 def test_preemptive_guard_not_cap_relaxation(self):
  s=(Path(__file__).parent/'v10_dispatch.py').read_text();self.assertIn('10*1024**3',s);self.assertIn('contract_limit_unchanged=16*1024**3',s)
 def test_proxy_not_native(self):
  s=(Path(__file__).parent/'micro_worker.py').read_text();self.assertIn('not_model_performance=True',s);self.assertIn('distinct_weights=1',s)
