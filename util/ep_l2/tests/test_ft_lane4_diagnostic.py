"""Fail-closed parser/adapter tests; fixtures are not performance evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_ft_lane4_diagnostic as subject


def terminal_fixture(wb=True):
    lines=['gpu_tot_sim_cycle = 100','gpu_tot_sim_insn = 200',
           'GPGPU-Sim: *** exit detected ***']
    for s in range(64):
        lines.append(f'EPL2B0V1|scope=application|slice={s}|c7d_line_mshr_full_block=0')
        d={k:0 for k in ['line_mshr_used','descriptor_used','wad_live','resident_pending','bypass_live','bank_pending','payload_double_owner']}
        d.update(slice=s,kernel_uid=2**64-1,terminal_clean=1,resident_tag_payload_consistent=1)
        lines.append('EPL2B0V1|INVARIANT|'+ '|'.join(f'{k}={v}' for k,v in d.items()))
        d={k:0 for k in ['ideal_meta','ideal_read_hit','wb_data_full','diagnostic_wb_extra_slots','reference_responses_live',
                          'reference_arrivals_live','reads_served','dependency_wait_attempts','bank_wait_attempts',
                          'response_wait_attempts','symbolic_bytes','known_bytes','line_mshr_full','descriptor_full','per_address_full']}
        d.update(scope='application',slice=s,ideal_wb=int(wb))
        lines.append('EPL2IDEALV1|'+ '|'.join(f'{k}={v}' for k,v in d.items()))
        d={k:0 for k in ['wb_live','wb_slots','reserved','read_refs','accepted','wbuf_full','copy_bytes','version_checks','descriptor_responses']}
        d.update(slice=s,mode=1,wbuf=16,physical_slots=1168,ownership_consistent=1,copy_lines=2,staging_reads=2,wb_lower_accept=2)
        lines.append('EPL2FTV1|SUMMARY|'+ '|'.join(f'{k}={v}' for k,v in d.items()))
        d=dict(slice=s,unique_requesters=10,responses=10,absorbed_writebacks=2,requester_live=0,requester_exact_once=1,hardware_drained=1,pending_lower_reads=0,pending_returns=0,pending_responses=0)
        lines.append('EPL2FTV1|TERMINAL|'+ '|'.join(f'{k}={v}' for k,v in d.items()))
    return '\n'.join(lines)+'\n'


class Closure(unittest.TestCase):
    def parse(self,text,vector=None):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'raw.log';p.write_text(text)
            return subject.parse_terminal(p,vector or {'wb':True,'meta':False,'read_hit':False},require_ft=True)
    def test_complete(self):
        self.assertEqual(self.parse(terminal_fixture())['nonbinding_wb_data'],'PASS')
    def test_missing_slice(self):
        text='\n'.join(l for l in terminal_fixture().splitlines() if '|slice=63|' not in l)
        with self.assertRaises(ValueError):self.parse(text)
    def test_live_wad(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('wad_live=0','wad_live=1',1))
    def test_capacity_not_nonbinding(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('wb_data_full=0','wb_data_full=1',1))
    def test_copy_read_mismatch(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('staging_reads=2','staging_reads=1',1))
    def test_reference_leak(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('reference_arrivals_live=0','reference_arrivals_live=1',1))
    def test_missing_normal_exit(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('*** exit detected ***','INCOMPLETE'))
    def test_wrong_model(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('|wbuf=16|','|wbuf=8|',1))
        # A metadata-only row must not quietly include WB relief, even if all
        # capacity-full counters are zero and the terminal resources close.
        text=terminal_fixture().replace('ideal_meta=0','ideal_meta=1')
        with self.assertRaises(ValueError):self.parse(text,{'wb':False,'meta':True,'read_hit':False})
    def test_requester_mismatch(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('responses=10','responses=9',1))
    def test_pending_return(self):
        with self.assertRaises(ValueError):self.parse(terminal_fixture().replace('pending_returns=0','pending_returns=1',1))
    def test_missing_requester_stream(self):
        text='\n'.join(l for l in terminal_fixture().splitlines() if not l.startswith('EPL2FTV1|TERMINAL|'))
        with self.assertRaises(ValueError):self.parse(text)
    def test_unknown_measurements_not_zero(self):
        self.assertIsNone(self.parse(terminal_fixture())['limiter_counts']['dram_successful_read_bytes'])


class Config(unittest.TestCase):
    def check(self,text,assets=()):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'config';p.write_text(text)
            subject.validate_config_whole_file({'configs':[{'path':str(p)}],
                'auxiliary_assets':[{'name':a} for a in assets]})
    def test_real_multiline_form(self):
        self.check('-gpgpu_dram_timing_opt "nbk=16:\n CL=12:WL=2"\n-icnt_config_file q.icnt\n',['q.icnt'])
    def test_nested_config(self):
        with self.assertRaises(ValueError):self.check('-config next.config',['next.config'])
    def test_missing_auxiliary(self):
        with self.assertRaises(ValueError):self.check('-icnt_config_file missing.icnt')
    def test_unclosed_quote(self):
        with self.assertRaises(ValueError):self.check('-gpgpu_dram_timing_opt "bad\n')


if __name__=='__main__':unittest.main()
