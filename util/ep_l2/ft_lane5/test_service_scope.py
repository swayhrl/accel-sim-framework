"""Service identity and cumulative-counter counterexamples; no runtime qualification."""
import copy,tempfile,unittest
from pathlib import Path
from service_scope import IDENTITY,expected,features,terminal_services

class Scope(unittest.TestCase):
 def spec(self):
  f,i=expected('S64_mq2_1');return {'producer_profile':'S64_mq2_1','identity':{**IDENTITY,'feature_vector':f,'ideal_vector':i}}
 def test_same_new_binary_fixed_geometry_and_single_factor(self):
  s=self.spec();features(s['identity'],s['producer_profile']);self.assertEqual(s['identity']['feature_vector']['static_wb_capacity'],64)
  for field,value in [('mq2',False),('rg1',True),('ops_per_bank_cycle',2),('bank_count',8),('payload_capacity_per_slice',1216),('static_wb_capacity',16),('wb_local_cap',16),('ideal_meta',True)]:
   i=copy.deepcopy(s['identity']);i['feature_vector'][field]=value
   with self.assertRaises(ValueError):features(i,s['producer_profile'])
  i=copy.deepcopy(s['identity']);i['binary_sha256']='fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7'
  with self.assertRaises(ValueError):features(i,s['producer_profile'])
  for p in ['Unified_rg1_1','I_WB','P2_B16','S64_mq2_rg1_1']:
   with self.assertRaises(ValueError):expected(p)
 def frames(self):
  lines=['gpu_tot_sim_cycle = 100\n']
  for s in range(64):
   lines.append(f'EPL2SERVICEV1|MQ2|slice={s}|enabled=1|wb_bank_waits=2|bypasses=1|window=2|lower_enqueues_per_cycle=1\n')
   for b in range(4):lines.append(f'EPL2SERVICEV1|RG1_BANK|slice={s}|bank={b}|enabled=0|held_not_ready_cycles=0|another_ready_cycles=0|recovered_grants=0|physical_services=1\n')
   for c in range(7):lines.append(f'EPL2SERVICEV1|RG1_CLIENT|slice={s}|client={c}|max_attempt_to_first_ready=0|max_attempt_to_consume=0|max_first_ready_to_consume=0|consumed=0|cancellations=0\n')
  return ''.join(lines)
 def parse(self,text):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'raw.log';p.write_text(text);return terminal_services(p,self.spec())
 def test_exact64_final_clock_over_prior_cumulative_frames(self):
  text=self.frames();result=self.parse(text.replace('cycle = 100','cycle = 20')+text);self.assertEqual(len(result['MQ2']),64);self.assertEqual(sum(r['bypasses'] for r in result['MQ2'].values()),64)
 def test_missing_slice_unqualified_activity_and_conflicting_frame_rejected(self):
  text=self.frames()
  for broken in [''.join(l for l in text.splitlines(True) if '|slice=63|' not in l),text.replace('recovered_grants=0','recovered_grants=1'),text.replace('bypasses=1','bypasses=3'),text+text.splitlines(True)[1].replace('bypasses=1','bypasses=0')]:
   with self.assertRaises(ValueError):self.parse(broken)

if __name__=='__main__':unittest.main()
