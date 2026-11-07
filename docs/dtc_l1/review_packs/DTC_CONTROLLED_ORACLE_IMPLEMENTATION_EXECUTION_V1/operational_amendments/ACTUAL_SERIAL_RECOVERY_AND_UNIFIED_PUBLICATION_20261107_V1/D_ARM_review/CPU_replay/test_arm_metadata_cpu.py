from pathlib import Path
import copy,importlib.util,unittest,ast,json
p=Path(__file__).with_name('arm_registered_request_metadata.py');s=importlib.util.spec_from_file_location('CPU_METADATA',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.q=dict(state=m.FROM,budget=96,remaining=96,consumed={},owner_pid=m.OWNER,owner_start_ticks=m.START,ready_for_registration=True,admitted_specs={'MOCK':1},uuid_history='UNCHANGED')
  self.old={'budget':32,'remaining':0,'uuid':'MOCK_IMMUTABLE'};self.reg=dict(registered_future_requests={m.REQUEST:copy.deepcopy(self.q),m.OLD:copy.deepcopy(self.old)},history={'UNCHANGED':1})
 def test_only_own_state_changes(self):
  before=copy.deepcopy(self.reg);m.cas_arm(self.reg,self.q,self.old);self.assertEqual(self.reg['registered_future_requests'][m.REQUEST]['state'],'ARMED');self.reg['registered_future_requests'][m.REQUEST]['state']=m.FROM;self.assertEqual(self.reg,before)
 def test_stale_own_CAS_refused(self):
  self.reg['registered_future_requests'][m.REQUEST]['remaining']=95
  with self.assertRaises(RuntimeError):m.cas_arm(self.reg,self.q,self.old)
 def test_foreign_owner_refused(self):
  self.q['owner_pid']=1;self.reg['registered_future_requests'][m.REQUEST]=copy.deepcopy(self.q)
  with self.assertRaises(RuntimeError):m.cas_arm(self.reg,self.q,self.old)
 def test_any_consumed_identity_refused(self):
  self.q['consumed']={'MOCK_UUID':{}};self.reg['registered_future_requests'][m.REQUEST]=copy.deepcopy(self.q)
  with self.assertRaises(RuntimeError):m.cas_arm(self.reg,self.q,self.old)
 def test_old32_change_refused(self):
  self.reg['registered_future_requests'][m.OLD]['budget']=33
  with self.assertRaises(RuntimeError):m.cas_arm(self.reg,self.q,self.old)
 def test_default_inert(self):self.assertEqual(m.main([])['registry_writes'],0)
 def test_actual_prepare_state_assertion_before_mock_parent_guard(self):
  # Extract the real source's exact state assertion; no native module load,
  # prepare call, parent imitation, resource probe or scientific run.
  native=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24/tools/oracle_native.py').read_text();tree=ast.parse(native)
  prepare=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='prepare');gate=next(x for x in prepare.body if isinstance(x,ast.Assert)and "q['state']"in ast.unparse(x))
  code=compile(ast.fix_missing_locations(ast.Module(body=[gate],type_ignores=[])),'ACTUAL_PREPARE_STATE_ASSERTION','exec')
  with self.assertRaises(AssertionError):exec(code,{'q':self.q,'c':'MOCK'})
  q=copy.deepcopy(self.q);q['state']='ARMED';exec(code,{'q':q,'c':'MOCK'})
if __name__=='__main__':unittest.main()
