import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('ft_terminal',Path(__file__).with_name('parse_ft_terminal.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class TerminalContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.raw=Path(self.tmp.name)/'raw.log'
        self.spec={'identity':{'feature_vector':{'payload_capacity_per_slice':1168,'wbuf_entries':16,'unified_wb':True},'termination_contract':{'hardware_drained':True}}}
        self.rows=[]
        for sid in range(64):
            self.rows.extend([
                f'EPL2FTV1|SUMMARY|slice={sid}|physical_slots=1168|wbuf=16|mode=2|role_free=1167|role_resident=1|role_bypass=0|wb_slots=0|ownership_consistent=1|reserved=0|read_refs=0|wb_live=0|wb_created=3|wb_lower_accept=3|wb_completed=3',
                f'EPL2FTV1|TERMINAL|slice={sid}|unique_requesters=9|responses=9|requester_live=0|requester_exact_once=1|hardware_drained=1|pending_lower_reads=0|pending_returns=0|pending_responses=0',
                f'EPL2B0V1|INVARIANT|slice={sid}|kernel_uid=18446744073709551615|descriptor_used=0|line_mshr_used=0|wad_live=0|resident_pending=0|bypass_live=0'])
        self.rows.extend(['gpu_tot_sim_cycle = 100','gpu_tot_sim_insn = 200'])
    def tearDown(self):self.tmp.cleanup()
    def parse(self):
        self.raw.write_text('\n'.join(self.rows)+'\n');return module.parse(self.raw,self.spec)
    def reject(self,before,after):
        self.rows[0]=self.rows[0].replace(before,after)
        with self.assertRaises(ValueError):self.parse()
    def test_source_scope_and_no_invented_data_pass(self):
        value=self.parse();self.assertEqual(value['cycles'],100)
        self.assertEqual(value['payload_capacity'],1168*64)
        self.assertEqual(value['unique_requesters'],9*64)
        self.assertFalse(value['data_correctness_qualification'])
    def test_missing_slice(self):
        self.rows=self.rows[3:]
        with self.assertRaises(ValueError):self.parse()
    def test_mode_mismatch(self):self.reject('mode=2','mode=1')
    def test_budget_mismatch(self):self.reject('physical_slots=1168','physical_slots=1160')
    def test_wb_milestone(self):self.reject('wb_completed=3','wb_completed=2')
    def test_live_refs(self):self.reject('read_refs=0','read_refs=1')
    def test_conservation(self):self.reject('role_free=1167','role_free=1168')
    def test_exact_once_gate(self):
        self.rows[1]=self.rows[1].replace('requester_exact_once=1','requester_exact_once=0')
        with self.assertRaises(ValueError):self.parse()

if __name__=='__main__':unittest.main()
