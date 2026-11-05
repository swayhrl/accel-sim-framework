import unittest,json,tempfile,hashlib,os
from pathlib import Path
from types import SimpleNamespace as N
from unittest.mock import patch
from worker import append
from v9_runtime import bind_actual,execute_tasks
from supervisor import Supervisor
from resource_monitor import MonitorStop
from test_supervision import config,services,FakeChild
class V9PlanTests(unittest.TestCase):
 def test_curve_design_complete_balanced(self):
  out=Path(__file__).resolve().parents[3]/'docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9'
  c=json.loads((out/'SCIENCE_CONTRACT.json').read_text());expected={p['point'] for p in c['points']}
  self.assertEqual(len(expected),18);self.assertEqual(c['output_lengths'],[1,2,4,8,16,32])
  for order in c['warmup_rounds']+c['formal_rounds']:self.assertEqual(set(order),expected);self.assertEqual(len(order),18)
  self.assertIsNone(c['sampling']['logprobs'])
 def test_journal_nonfinite_failure_evidence_not_lost(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'r';h=append(p,dict(t=float('nan'),all_completions=[1,2]))
   value=json.loads(p.read_text());self.assertIn('nonfinite_float',value['t']);self.assertEqual(value['all_completions'],[1,2]);self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)
 def test_profiles_clock_cache_and_scope_explicit(self):
  text=(Path(__file__).parent/'v9_runtime.py').read_text()
  for term in ["'--clock-control','none'","'--cache-control','none'","'--graph-profiling','node'","'--launch-count','1'","'--profile-from-start','no'"]:self.assertIn(term,text)
  self.assertNotIn('--set full',text)
 def test_all_returned_before_validity_gates(self):
  text=(Path(__file__).parent/'worker.py').read_text();self.assertLess(text.index("private_hash=append(private_journal,secret)"),text.index("assert len(responses)==len(prompts)"))
 def test_numeric_altered_not_native(self):
  text=(Path(__file__).parent/'worker.py').read_text();self.assertIn("altered=task=='NUMERIC'",text);self.assertIn('enforce_eager=altered',text)
 def test_only_first_decode_graph_profiled_NCU(self):
  text=(Path(__file__).parent/'worker.py').read_text();self.assertIn("task.startswith('NCU') and not ncu_capture[0]",text);self.assertIn('torch.cuda.profiler.start()',text);self.assertIn('torch.cuda.profiler.stop()',text)
class BindingTests(unittest.TestCase):
 def build(self,root):
  tool=Path(__file__).parent;expected=dict(pid=20,uid=1004,start_ticks='1',boot_id='b',executable='/usr/bin/python3.12')
  v=dict(task='NSYS',nonce='n',supervisor_pid=10,identity=expected,worker_sha256=hashlib.sha256((tool/'worker.py').read_bytes()).hexdigest())
  (root/'WORKER_IDENTITY.json').write_text(json.dumps(v))
  state=dict(task='NSYS',nonce='n',context=root,actual_pid=None)
  ps=N(Process=lambda pid:N(children=lambda recursive=True:[N(pid=20)],is_running=lambda:True,status=lambda:'running',create_time=lambda:1.0))
  s=N(pid=10,ps=ps,v9state=state);x=N(s=s,cfg={'tool':str(tool)},owned={10},lifecycle=N(bind_worker=lambda pid:None),r={'children':[{}]})
  return x,expected,v
 def test_actual_model_can_differ_from_wrapper(self):
  with tempfile.TemporaryDirectory() as d:
   x,expected,v=self.build(Path(d))
   with patch('v9_runtime.identity',return_value=expected):self.assertTrue(bind_actual(x))
   self.assertEqual(x.s.v9state['actual_pid'],20);self.assertIn(20,x.owned)
 def test_nonce_mismatch_not_whitelisted(self):
  with tempfile.TemporaryDirectory() as d:
   x,expected,v=self.build(Path(d));x.s.v9state['nonce']='changed'
   with self.assertRaises(MonitorStop):bind_actual(x)
 def test_PID_birth_mismatch_stops(self):
  with tempfile.TemporaryDirectory() as d:
   x,expected,v=self.build(Path(d))
   with patch('v9_runtime.identity',return_value={**expected,'start_ticks':'2'}):
    with self.assertRaises(MonitorStop):bind_actual(x)
 def test_foreign_tree_cannot_be_bound(self):
  with tempfile.TemporaryDirectory() as d:
   x,expected,v=self.build(Path(d));x.s.ps.Process=lambda pid:N(children=lambda recursive=True:[],is_running=lambda:True,status=lambda:'running')
   with patch('v9_runtime.identity',return_value=expected):
    with self.assertRaises(MonitorStop):bind_actual(x)
class OptionalDispatchTests(unittest.TestCase):
 def build(self):
  cfg=config('v9_dispatch');cfg.update(worker_tasks=['CURVE','NSYS','NUMERIC'],held_seconds_max=1800)
  s=services();state={};s.v9state=state
  def spawn():state['task']=state['next_task'];state['launch']={};return FakeChild(0)
  s.spawn=spawn
  def result():
   task=state['task']
   return dict(status='V9_OPTIONAL_UNAVAILABLE' if task=='NSYS' else 'V9_WORKER_COMPLETE',model_initializations=1,point_completion={str(i):5 for i in range(18)})
  s.worker_result=result;x=Supervisor(cfg,s);x.held=0;x.lifecycle=N(bind_worker=lambda pid:None);x.snapshot=lambda phase:{'own_NVML_bytes':0}
  return x
 def test_optional_profiler_failure_continues_other_task(self):
  x=self.build();execute_tasks(x);self.assertEqual(x.r['status'],'V9_STUDY_COMPLETE');self.assertEqual([v['task'] for v in x.r['children']],['CURVE','NSYS','NUMERIC']);self.assertEqual(len(x.r['optional_failures']),1)
 def test_fundamental_validity_stops(self):
  x=self.build();original=x.s.worker_result
  x.s.worker_result=lambda:dict(original(),validity_stop=x.s.v9state['task']=='NSYS')
  with self.assertRaises(MonitorStop):execute_tasks(x)
  self.assertEqual(len(x.r['children']),2)
if __name__=='__main__':unittest.main()
