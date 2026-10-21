"""Bounded engineering-only checks. No native/app/registry writes or subprocess."""
import ast,copy,importlib.util,inspect,json,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;R=P.parents[4];C=P/'candidate'
sys.path.insert(0,str(R/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(C))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=load('none_durable',C/'durable_exit.py');v=load('none_validator',C/'capacity_validation.py');l=load('none_limits',C/'limits_policy.py')
RT=ast.parse((C/'runner.py').read_text())
inspectfn=next(x for x in RT.body if isinstance(x,ast.FunctionDef) and x.name=='inspect')
start=next(i for i,x in enumerate(inspectfn.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='timeout' for t in x.targets))
end=next(i for i,x in enumerate(inspectfn.body[start:],start) if isinstance(x,ast.If))
block=compile(ast.fix_missing_locations(ast.Module(body=inspectfn.body[start:end+1],type_ignores=[])),'actual_inspect_timeout_block','exec')
execute=next(x for x in RT.body if isinstance(x,ast.FunctionDef) and x.name=='execute')
condition=next(x.test for x in ast.walk(execute) if isinstance(x,ast.If) and 'time.monotonic() - started' in ast.unparse(x.test))
condition=compile(ast.Expression(condition),'actual_runner_monitor_condition','eval')
def require(ok,msg):
 if not ok:raise ValueError(msg)
class Controls(unittest.TestCase):
 def setUp(self):
  self.spec=json.loads((P.parent/'input_preparation/materialized_parser_r2/convolutionSeparable/S_ON_SPEC.json').read_text())
 def nullspec(self):
  s=copy.deepcopy(self.spec);s['timeout_seconds']=None;s['operational_limits_override']=l.operational_override(s);return s
 def helper(self,spec,active=True,scope=True):
  with patch.object(l,'active',return_value=active),patch.object(l,'scope_allowed',return_value=scope):return l.effective_timeout({},spec)
 def inspectblock(self,spec,intake=None,active=True,scope=True):
  env=dict(spec=spec,item={},require=require,time=types.SimpleNamespace(time=lambda:100),limits_policy=l,
   capacity_policy=types.SimpleNamespace(effective_limits=lambda i:dict(intake_deadline_unix=intake)),launch_check=True)
  with patch.object(l,'active',return_value=active),patch.object(l,'scope_allowed',return_value=scope):exec(block,env)
  return env
 def test_null_no_time_stop(self):self.assertFalse(d.time_limit_reached(dict(timeout_seconds=None,intake_deadline_unix=None),10**12,10**12))
 def test_old_timeout_still_stops(self):self.assertTrue(d.time_limit_reached(dict(timeout_seconds=10800,intake_deadline_unix=None),10800,100))
 def test_old_intake_still_stops(self):self.assertTrue(d.time_limit_reached(dict(timeout_seconds=None,intake_deadline_unix=100),1,100))
 def test_before_both_bounds_open(self):self.assertFalse(d.time_limit_reached(dict(timeout_seconds=10800,intake_deadline_unix=200),20,100))
 def test_missing_timeout_not_silently_unbounded(self):
  with self.assertRaises(KeyError):d.time_limit_reached(dict(intake_deadline_unix=None),1,100)
 def test_missing_intake_not_silently_unbounded(self):
  with self.assertRaises(KeyError):d.time_limit_reached(dict(timeout_seconds=None),1,100)
 def test_exact_none_effective(self):self.assertIsNone(self.helper(self.nullspec()))
 def test_old_spec_10800_retained(self):self.assertEqual(self.helper(self.spec),10800)
 def test_none_no_approval_rejected(self):
  with self.assertRaises(ValueError):self.helper(self.nullspec(),active=False)
 def test_none_outside_scope_rejected(self):
  with self.assertRaises(ValueError):self.helper(self.nullspec(),scope=False)
 def test_none_no_override_rejected(self):
  s=self.nullspec();s.pop('operational_limits_override')
  with self.assertRaises(ValueError):self.helper(s)
 def test_none_changed_approval_rejected(self):
  s=self.nullspec();s['operational_limits_override']['approval']['sha256']='0'*64
  with self.assertRaises(ValueError):self.helper(s)
 def test_none_extra_waiver_rejected(self):
  s=self.nullspec();s['operational_limits_override']['ignore_resource_gate']=True
  with self.assertRaises(ValueError):self.helper(s)
 def test_actual_inspect_null_open(self):self.assertIsNone(self.inspectblock(self.nullspec())['timeout'])
 def test_actual_inspect_null_finite_intake_rejected(self):
  with self.assertRaises(ValueError):self.inspectblock(self.nullspec(),intake=999999)
 def test_actual_inspect_old_bound_open(self):self.assertEqual(self.inspectblock(self.spec,intake=11000)['timeout'],10800)
 def test_actual_inspect_old_bound_exceeds_intake(self):
  with self.assertRaises(ValueError):self.inspectblock(self.spec,intake=10899)
 def test_actual_inspect_legacy_huge_timeout_rejected(self):
  s=copy.deepcopy(self.spec);s['timeout_seconds']=10**12
  with self.assertRaises(ValueError):self.inspectblock(s)
 def test_monitor_null_open(self):
  self.assertFalse(eval(condition,dict(timeout=None,time=types.SimpleNamespace(monotonic=lambda:10**12),started=0,limits=dict(intake_deadline_unix=None),limits_policy=l)))
 def test_monitor_finite_old_timeout(self):
  self.assertTrue(eval(condition,dict(timeout=10800,time=types.SimpleNamespace(monotonic=lambda:10801),started=0,limits=dict(intake_deadline_unix=None),limits_policy=l)))
 def test_scientific_contract_original_accepted(self):
  t=self.spec['identity']['termination_contract'];v.validate_termination_contract(copy.deepcopy(t),copy.deepcopy(t),t)
 def test_scientific_contract_cannot_be_rewritten_none(self):
  t=self.spec['identity']['termination_contract'];s=copy.deepcopy(t);s['timeout_seconds']=None
  with self.assertRaises(ValueError):v.validate_termination_contract(s,t,t)
 def test_scientific_contract_all_none_rejected(self):
  with self.assertRaises(ValueError):v.validate_termination_contract(None,None,None)
 def test_no_effect_on_frozen_spec_identity(self):
  original=copy.deepcopy(self.spec);self.helper(self.nullspec());self.assertEqual(self.spec,original)
 def test_deadline_none_open_and_finite_closed(self):
  self.assertTrue(l.deadline_open(None,10**12));self.assertFalse(l.deadline_open(100,100));self.assertTrue(l.deadline_open(101,100))
 def captured_factory(self,spec):
  attempt=dict(policy_id='SYNTHETIC',disk_floor_bytes=5*2**30,monitor_reserve_bytes=2*2**30,maximum_result_bytes=384*2**20,monitor_interval_seconds=2,termination_grace_seconds=5,attempt_id='MOCK',run_key='MOCK')
  coord=types.SimpleNamespace(Coordinator=lambda:types.SimpleNamespace(snapshot=lambda:{}))
  policy=types.SimpleNamespace(effective_limits=lambda i:dict(intake_deadline_unix=None,additional_results_max_bytes=10*2**30,old_plus_new_results_max_bytes=24*2**30))
  with patch.dict(sys.modules,dict(coordinator=coord,capacity_policy=policy,limits_policy=l)),patch.object(l,'active',return_value=True),patch.object(l,'scope_allowed',return_value=True):
   spawn=d.popen_factory(spec,attempt,dict(comparison_invariants_sha256='MOCK'))
  return inspect.getclosurevars(spawn).nonlocals
 def test_factory_persists_null_and_approval_binding_without_spawn(self):
  spec=self.nullspec();captured=self.captured_factory(spec)
  self.assertIsNone(captured['bounds']['timeout_seconds']);self.assertIsNone(captured['bounds']['intake_deadline_unix'])
  self.assertEqual(captured['bounds']['frozen_identity_timeout_seconds'],10800)
  self.assertEqual(captured['binding']['operational_limits_override'],spec['operational_limits_override'])
 def test_factory_old_timeout_preserved_without_override(self):
  captured=self.captured_factory(self.spec);self.assertEqual(captured['bounds']['timeout_seconds'],10800)
  self.assertNotIn('operational_limits_override',captured['bounds']);self.assertNotIn('operational_limits_override',captured['binding'])
 def test_unique_top_level_defs_and_syntax_four_sources(self):
  for name in ('runner','controller','durable_exit','capacity_validation'):
   with self.subTest(name=name):
    tree=ast.parse((C/(name+'.py')).read_text());defs=[x.name for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))];self.assertEqual(len(defs),len(set(defs)));compile(tree,str(C/(name+'.py')),'exec')
 def test_bounded_handshake_parser_and_resource_guards_retained(self):
  durable=(C/'durable_exit.py').read_text();runner=(C/'runner.py').read_text()
  for text in ('time.monotonic()+10','time.monotonic()-started > 15','self.collector.wait(timeout=5)',"request['bounds']['termination_grace_seconds']"):
   self.assertIn(text,durable)
  self.assertIn('timeout=120',runner)
  for text in ('additional_results_max_bytes','old_plus_new_results_max_bytes','disk_policy.stop_detail','available_memory_bytes','share_disk_free_bytes','memory_bytes','maximum_result_bytes'):
   self.assertIn(text,durable)
if __name__=='__main__':unittest.main()
