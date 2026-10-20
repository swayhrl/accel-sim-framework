"""Offline decoder regressions on retained real raw; no simulation or native tests."""
import importlib.util,json,re,tempfile,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
s=importlib.util.spec_from_file_location('compat',P/'parse_main_terminal.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
D=Path('/workspace/ep_l2_ms20261019_e_results');RAW=(D/'E009_76e25c1e/raw.log').read_text();SPEC=json.loads((D/'E009_76e25c1e/input_spec.json').read_text());Q=json.loads((ROOT/'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/convolutionSeparable_QUALIFICATION.json').read_text())
class CompatTests(unittest.TestCase):
 def check_bad(self,raw,reason):
  with tempfile.TemporaryDirectory(prefix='e2_decoder_control_') as temp:
   f=Path(temp)/'mutated-control.log';f.write_text(raw)
   with self.assertRaisesRegex(ValueError,reason):m.parse(f,SPEC,Q)
 def test_actual_final_same_clock_snapshot_is_valid(self):
  result=m.parse(D/'E009_76e25c1e/raw.log',SPEC,Q);self.assertEqual(result['cycles'],291469);self.assertEqual(result['instructions'],714547200);self.assertTrue(result['hardware_drained'])
 def test_S_is_unchanged(self):
  d=D/'E010_1108e4d2';self.assertEqual(m.parse(d/'raw.log',json.loads((d/'input_spec.json').read_text()),Q),json.loads((d/'terminal_summary.json').read_text()))
 def test_missing_BEGIN_rejected(self):self.check_bad(RAW.replace('EPL2ROV1|COMMANDLIST_BEGIN|commands=4\n',''),'commandlist END')
 def test_missing_END_rejected(self):self.check_bad(RAW.replace('EPL2ROV1|COMMANDLIST_END|complete=1|commands=4\n',''),'missing complete commandlist')
 def test_wrong_command_count_rejected(self):self.check_bad(RAW.replace('COMMANDLIST_BEGIN|commands=4','COMMANDLIST_BEGIN|commands=3'),'input count mismatch')
 def test_duplicate_BEGIN_rejected(self):self.check_bad(RAW.replace('EPL2ROV1|COMMANDLIST_BEGIN|commands=4\n','EPL2ROV1|COMMANDLIST_BEGIN|commands=4\n'*2),'invalid/duplicate')
 def test_no_post_END_snapshot_rejected(self):
  at=RAW.index('EPL2ROV1|COMMANDLIST_END|');self.check_bad(RAW[:at]+'EPL2ROV1|COMMANDLIST_END|complete=1|commands=4\nGPGPU-Sim: *** exit detected ***\n','post-END terminal snapshot')
 def test_final_snapshot_must_have_all64(self):
  at=RAW.index('EPL2ROV1|COMMANDLIST_END|');suffix=re.sub(r'^EPL2ROC1\|CLOSURE\|slice=63\|[^\n]*\n','',RAW[at:],flags=re.M);self.check_bad(RAW[:at]+suffix,'exact64slice')
 def test_clock_regression_rejected(self):self.check_bad(RAW.replace('gpu_tot_sim_cycle = 291469','gpu_tot_sim_cycle = 160983',1),'clock regressed')
 def test_unclosed_epoch_rejected(self):self.check_bad(RAW.replace('epoch_closed=1','epoch_closed=0'),'whole-epoch not drained')
 def test_preclock_slice_snapshot_still_rejected(self):self.check_bad('EPL2ROV1|SUMMARY|slice=0\n'+RAW,'snapshot lacks native clock')
if __name__=='__main__':unittest.main()
