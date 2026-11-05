import unittest,tempfile,csv
from pathlib import Path
from v11_dispatch import audit_csv
class V11Tests(unittest.TestCase):
 def fake(self,passes,log=True,badtime=False):
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);p=Path(d.name)/'x'
  h=['ID','Kernel Name','Grid Size','Block Size','dram__bytes_read.sum','gpu__time_duration.sum','profiler__replayer_passes']
  with p.open('w') as f:
   w=csv.writer(f);w.writerow(h);w.writerow(['','','','','byte','ns','pass'])
   for i,n in enumerate(passes):w.writerow([i,'gemv','(1,1,1)','(1,1,1)',100,'nan' if badtime and i==1 else 10,n])
  return p
 def test_all_three_rows_audited(self):
  a=audit_csv(self.fake([1,1,1]),'100% - 1 pass\n'*3);self.assertTrue(a['safe_single_pass']);self.assertEqual(len(a['nodes']),3)
 def test_later_bad_pass_not_hidden(self):self.assertFalse(audit_csv(self.fake([1,2,1]),'100% - 1 pass\n'*3)['safe_single_pass'])
 def test_missing_backup_not_zero(self):self.assertIsNone(audit_csv(self.fake([1]),'100% - 1 pass')['nodes'][0]['backup_bytes'])
 def test_insufficient_log_evidence_rejects(self):self.assertFalse(audit_csv(self.fake([1,1]),'100% - 1 pass')['safe_single_pass'])
 def test_nonfinite_later_row_rejected(self):
  with self.assertRaises(ValueError):audit_csv(self.fake([1,1],badtime=True),'100% - 1 pass\n'*2)
 def test_filter_not_cutlass_type_substring(self):
  s=(Path(__file__).parent/'v9_runtime.py').read_text();self.assertNotIn('regex:.*(gemv|gemm|cutlass).*',s);self.assertIn("'--rename-kernels','off'",s)
 def test_no_curve_QKV_or_numerical_rerun(self):
  s=(Path(__file__).parent/'v11_dispatch.py').read_text();self.assertNotIn("'CURVE'",s);self.assertNotIn("'NUMERIC'",s);self.assertIn("'NCU_B1_L17'",s)
 def test_local_graph_input_lifetime_and_measurement(self):
  s=(Path(__file__).parent/'controlled_worker.py').read_text();self.assertIn('actual_DRAM_state_requires_NCU=True',s);self.assertIn("evict.add_(1)",s);self.assertIn('output_identical=True',s)
