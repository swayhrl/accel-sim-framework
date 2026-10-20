"""E parser grammar controls; retained logs remain read-only, never accepted here."""
import json
from pathlib import Path
import tempfile
import unittest
import runner

class RuntimeMetricsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'raw.log'
        self.options={'-gpgpu_ep_l2_ft_mode':'1','-gpgpu_ep_l2_ro_certificate_file':'/w/a # b#c',
                      '-gpgpu_cache:dl2':'S:64:128:16,L:B:m:N:L,A:128:4,16:0,32',
                      '-gpgpu_cache:dl2_texture_only':'0'}
        self.dump=''.join(f'{k:<30} {v:>20} # native description\n' for k,v in self.options.items())
        self.end='gpu_tot_sim_cycle = 10\ngpu_tot_sim_insn = 20\nGPGPU-Sim: *** exit detected ***\n'
    def parse(self,text):
        self.path.write_text(text);return runner.runtime_metrics(self.path,self.options)
    def test_commented_colon_keys_and_literal_hash_path(self):
        self.assertEqual(self.parse(self.dump+self.end),{'cycle':10,'insn':20})
    def test_plain_existing_dump_supported(self):
        # Plain dumps are supported where the value contains no comment delimiter.
        self.options['-gpgpu_ep_l2_ro_certificate_file']='/w/a#b'
        self.assertEqual(self.parse(''.join(f'{k} {v}\n' for k,v in self.options.items())+self.end),{'cycle':10,'insn':20})
    def test_wrong_or_missing_required_options(self):
        for key,value in self.options.items():
            for replacement in ('',f'{key} WRONG # description\n'):
                with self.subTest(key=key,replacement=replacement):
                    lines=self.dump.splitlines(keepends=True)
                    text=''.join(replacement if line.startswith(key+' ') else line for line in lines)
                    with self.assertRaisesRegex(ValueError,'options mismatch/missing'):self.parse(text+self.end)
    def test_conflicting_duplicate_before_and_after(self):
        for duplicate in ('-gpgpu_ep_l2_ft_mode 2 # bad\n','-gpgpu_cache:dl2 WRONG # bad\n'):
            for text in (duplicate+self.dump+self.end,self.dump+duplicate+self.end):
                with self.subTest(duplicate=duplicate,text=text):
                    with self.assertRaisesRegex(ValueError,'conflicting native option'):self.parse(text)
    def test_identical_duplicate_allowed(self):
        self.assertEqual(self.parse(self.dump+self.dump+self.end),{'cycle':10,'insn':20})
    def test_missing_exit_or_counter_remains_rejected(self):
        for text in (self.end.replace('GPGPU-Sim: *** exit detected ***\n',''),
                     self.end.replace('gpu_tot_sim_cycle = 10\n',''),
                     self.end.replace('gpu_tot_sim_insn = 20\n',''),
                     self.end.replace('gpu_tot_sim_cycle = 10','gpu_tot_sim_cycle = malformed')):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError,'native exit/counters'):self.parse(self.dump+text)
    def test_latest_cumulative_counters(self):
        self.assertEqual(self.parse(self.dump+'gpu_tot_sim_cycle = 1\ngpu_tot_sim_insn = 2\n'+self.end),{'cycle':10,'insn':20})
    def test_actual_retained_S_is_control_only_status_immutable(self):
        root=Path('/workspace/ep_l2_ms20261019_e_results/E002_09c7145e')
        before=(root/'run_status.json').read_bytes()
        audit=json.loads((root/'input_audit.json').read_text())
        self.assertEqual(runner.runtime_metrics(root/'raw.log',audit['effective_options']),{'cycle':292932,'insn':714547200})
        self.assertEqual((root/'run_status.json').read_bytes(),before)
        self.assertEqual(json.loads(before)['status'],'FAILED')
    def test_actual_retained_crashed_F_still_rejected(self):
        root=Path('/workspace/ep_l2_ms20261019_e_results/E003_af8fc7e6')
        before=(root/'run_status.json').read_bytes()
        audit=json.loads((root/'input_audit.json').read_text())
        with self.assertRaisesRegex(ValueError,'native exit/counters'):runner.runtime_metrics(root/'raw.log',audit['effective_options'])
        self.assertEqual((root/'run_status.json').read_bytes(),before)
        self.assertEqual(json.loads(before)['exit_code'],-11)

if __name__=='__main__':unittest.main()
