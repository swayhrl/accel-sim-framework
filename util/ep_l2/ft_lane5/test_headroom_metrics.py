import unittest
from headroom_metrics import parse_rows,SUM_FIELDS
class MetricsTests(unittest.TestCase):
    def rows(self):
        rows=[]
        for i in range(64):
            r={'scope':'application',**{n:10 for n in SUM_FIELDS}};r.update(samples=100,c7d_dram_issue_eligible=20,c7d_wad_lifetime_avg=50,c7d_wad_lifetime_max=70,wad_max=16,lowerq_max=128,slice=i,scope='application',completion_cycle=100);rows.append('EPL2B0V1|'+ '|'.join(k+'='+str(v) for k,v in r.items()))
        r={'scope':'window','dram_cycles':100,'scheduler_occ_max':30,'returnq_occ_max':2,'scheduler_full_cycles':5,'returnq_full_cycles':0,'successful_read_issues':10,'successful_write_issues':10};rows.append('EPL2DRAMV1|'+ '|'.join(k+'='+str(v) for k,v in r.items()));return rows
    def test_distinct_normalization_denominators(self):
        a=parse_rows(self.rows())['aggregate'];self.assertEqual(a['L2_to_DRAM_full_per_sampled_L2_slice_cycle'],.1);self.assertEqual(a['scheduler_full_per_actual_issue_attempt'],.5);self.assertEqual(a['scheduler_full_per_sampled_DRAM_channel_tick'],.05)
    def test_missing_field_never_becomes_zero(self):
        r=self.rows();r[0]=r[0].replace('c7d_dram_credit_block=10|','')
        with self.assertRaises(KeyError):parse_rows(r)
    def test_no_dram_windows_never_implies_nonbinding(self):
        with self.assertRaises(ValueError):parse_rows(self.rows()[:-1])
    def test_other_native_records_are_not_misparsed(self):
        r=self.rows();r.append('EPL2B0V1|QUIESCENT|slice=0|pass=1');self.assertEqual(parse_rows(r)['aggregate']['samples'],6400)
    def test_earlier_cumulative_application_clock_refuses(self):
        r=self.rows();r.append(r[0].replace('completion_cycle=100','completion_cycle=99'))
        with self.assertRaises(ValueError):parse_rows(r)
    def test_final_cumulative_kernel_record_selected(self):
        r=self.rows();r.append(r[0].replace('completion_cycle=100','completion_cycle=200').replace('samples=100','samples=200'));self.assertEqual(parse_rows(r)['aggregate']['samples'],6500)
if __name__=='__main__':unittest.main()
