"""Reject false clock/config/canary identities without dispatching a simulator."""
import copy,hashlib,json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import registry as rg
import independent_microopt as m
import test_lane5 as fixtures

class Intake(unittest.TestCase):
 def test_native_identical_registration_is_allowed_but_conflicts_rejected(self):
  self.assertEqual(m.native_options('NATIVE_EFFECTIVE_OPTIONS_BEGIN\n-x 1\n-x 1\nNATIVE_EFFECTIVE_OPTIONS_END'),{'-x':'1'})
  with self.assertRaises(ValueError):m.native_options('NATIVE_EFFECTIVE_OPTIONS_BEGIN\n-x 1\n-x 2\nNATIVE_EFFECTIVE_OPTIONS_END')
 def test_warm_offset_4096_and_corrupt_clock(self):
  command=['fixture','base','overlay','1','8','4096','warm_hit'];text='FT real partition lower-full/WBUF/WAD/set_done mode=1 C=8 peak=8 PASS\nCLOCK_AUDIT|offset=4096|violations=0|max_grants_per_physical_bank_cycle=1\n'
  m.validate_case('warm_clock_1_8',command,text)
  with self.assertRaises(ValueError):m.validate_case('warm_clock_1_8',command,text.replace('violations=0','violations=1'))
 def test_s64_actual_capacity_and_clock_are_both_required(self):
  cmd=['fixture','base','overlay','1','16','4096'];text='CLOCK_CAPACITY|static_s64=1|configured_C=16|actual_fixed_capacity=64|peak=64|wad=66\nFT real partition lower-full/WBUF/WAD/set_done mode=1 C=16 peak=64 PASS\nCLOCK_AUDIT|offset=4096|violations=0|max_grants_per_physical_bank_cycle=1\n'
  m.validate_case('MQ2_S64_ft_memcpy_clock_4096',cmd,text)
  for old,new in [('actual_fixed_capacity=64','actual_fixed_capacity=16'),('violations=0','violations=1')]:
   with self.assertRaises(ValueError):m.validate_case('MQ2_S64_ft_memcpy_clock_4096',cmd,text.replace(old,new))
 def test_only_exact_published_all_off_canary_and_no_counter_reset(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);reg=rg.Registry(root);i=fixtures.identity();i.update(m.IDENTITY);i['feature_vector']['finite_wbuf']=False;i['ideal_vector']={k:False for k in i['ideal_vector']};d={'campaigns':{rg.PARALLEL:{'deadline_unix':2e12,'extra_cells':[],'t0_unix':123,'maximum_starts':72}},'runs':{'old':{'status':'FAILED','attempt_history':[{}]}},'resource_leases':{}}
   d['authority_host']=socket.gethostname();rg.write_json(root/'RUN_REGISTRY.json',d);p=root/'proof.json'
   def checkpoint(identity):
    rg.write_json(p,{'identity':identity,'official_release':m.PUB,'status':'PREDECLARED_NECESSARY_SERVICE_RUNTIME_NATIVE_OFF_CANARY'});return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
   wrong=copy.deepcopy(i);wrong['binary_sha256']='b'*64
   with self.assertRaises(ValueError):reg.register_native_off_control(wrong,checkpoint(wrong),'E_NATIVE_OFF_SERVICE_F0AF_R1')
   row=reg.register_native_off_control(i,checkpoint(i),'E_NATIVE_OFF_SERVICE_F0AF_R1');self.assertEqual(row['expected_run_key'],rg.run_key(i));after=reg.snapshot();self.assertEqual(after['runs'],d['runs']);self.assertEqual(after['campaigns'][rg.PARALLEL]['t0_unix'],123);self.assertEqual(after['campaigns'][rg.PARALLEL]['maximum_starts'],72)

if __name__=='__main__':unittest.main()
