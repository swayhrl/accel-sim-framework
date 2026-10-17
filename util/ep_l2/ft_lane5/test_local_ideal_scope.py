"""Synthetic terminal scope/diagnostic-budget checks, never scientific evidence."""
import copy,json,re,tempfile,unittest
from pathlib import Path
from local_ideal_scope import IDENTITY,features,PROFILE_BITS
from parse_local_ideal_terminal import parse,digest
from validate import validate_summary

class LocalScopeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.repo=Path(__file__).resolve().parents[3];cls.spec=json.loads((cls.repo/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/parallel_specs_execution_r5/ROP40_H0/convolutionSeparable_B16_BANKED.json').read_text())
  import registry
  rows=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())['runs'].values();row=next(r for r in rows if r.get('regime')=='D4' and r['identity']['workload']=='convolutionSeparable' and r['identity']['feature_vector']['unified_wb'] is False)
  raw=Path(row['result_directory'])/'raw.log'
  with raw.open() as stream:cls.raw=''.join(x for x in stream if x.startswith(('EPL2FTV1|','EPL2B0V1|INVARIANT|','gpu_tot_sim_')))
 def make(self,profile):
  s=copy.deepcopy(self.spec);s.update(scientific_scope='LOCAL_IDEAL_NATIVE_V1',profile=profile,scope_tool={'path':str(self.repo/'util/ep_l2/ft_lane5/local_ideal_scope.py'),'sha256':digest(self.repo/'util/ep_l2/ft_lane5/local_ideal_scope.py')})
  s['identity'].update(IDENTITY);wb,meta,read=PROFILE_BITS[profile];s['identity']['ideal_vector']={'wb':wb,'meta':meta,'read_hit':read};f=s['identity']['feature_vector'];f.update(unified_wb=profile=='U_OFF',payload_capacity_per_slice=None if wb else 1168,ideal_wb=wb,ideal_meta=meta,ideal_read_hit=read,nominal_payload_capacity_per_slice=1168,diagnostic_extra_payload_backing=wb,wb_data_capacity_non_binding=wb)
  return s
 def text(self,s,extra=0):
  enabled=any(s['identity']['ideal_vector'].values());out=[]
  for line in self.raw.splitlines(True):
   if line.startswith('EPL2FTV1|SUMMARY|'):
    if enabled:line=re.sub(r'\|wbuf_full=\d+',r'|wbuf_full=0',line)
    if '|slice=0|' in line and extra:
     line=re.sub(r'\|physical_slots=(\d+)',lambda m:'|physical_slots='+str(int(m[1])+extra),line);line=re.sub(r'\|role_free=(\d+)',lambda m:'|role_free='+str(int(m[1])+extra),line)
   out.append(line)
  if enabled:
   for i in range(64):
    d={'scope':'application','slice':i,'ideal_meta':int(s['identity']['ideal_vector']['meta']),'ideal_wb':int(s['identity']['ideal_vector']['wb']),'ideal_read_hit':int(s['identity']['ideal_vector']['read_hit']),'wb_data_full':0,'diagnostic_wb_extra_slots':extra if i==0 else 0,'reference':'BYTE_VERSION_SYMBOLS_WITH_OPTIONAL_KNOWN_VALUES','reference_responses_live':0,'reference_arrivals_live':0,'line_mshr_full':0,'descriptor_full':0,'per_address_full':0}
    out.append('EPL2IDEALV1|'+'|'.join(f'{k}={v}' for k,v in d.items())+'\n')
  return ''.join(out)
 def parsed(self,s,text):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'raw';p.write_text(text);return parse(p,s)
 def test_explicit_finite_and_all4_local_profiles(self):
  for profile in ['B16_OFF','I_WB','I_META','I_WB_META','I_READ_HIT']:
   with self.subTest(profile=profile):
    s=self.make(profile);features(s['identity'],profile);summary=self.parsed(s,self.text(s,3 if s['identity']['ideal_vector']['wb'] else 0));self.assertEqual(validate_summary(summary,s['identity'])['status'],'PASS')
 def test_dynamic_storage_is_counted_and_cannot_be_hidden(self):
  s=self.make('I_WB');summary=self.parsed(s,self.text(s,7));self.assertEqual(summary['payload_capacity'],1168*64+7);self.assertEqual(summary['diagnostic_payload_extra_slots'],7)
  summary['diagnostic_payload_extra_slots']=0
  with self.assertRaises(ValueError):validate_summary(summary,s['identity'])
 def test_missing_slice_and_live_reference_refuse(self):
  s=self.make('I_READ_HIT');text=self.text(s)
  for bad in ['\n'.join(x for x in text.splitlines() if not x.startswith('EPL2IDEALV1|scope=application|slice=63|')),text.replace('reference_responses_live=0','reference_responses_live=1',1)]:
   with self.assertRaises(ValueError):self.parsed(s,bad)
 def test_wrong_flag_and_unqualified_combination_refuse(self):
  s=self.make('I_META')
  with self.assertRaises(ValueError):self.parsed(s,self.text(s).replace('ideal_meta=1','ideal_meta=0',1))
  s['identity']['feature_vector']['tvd']=True
  with self.assertRaises(ValueError):features(s['identity'],'I_META')

if __name__=='__main__':unittest.main()
