import unittest,tempfile,json,ast
from pathlib import Path
from types import SimpleNamespace as N
from unittest.mock import patch
from numeric_observation import compare,validate
from capture import capture_batch
from supervisor import Supervisor
from test_supervision import config,services,FakeChild
class NumericRoleTests(unittest.TestCase):
 def row(self,tokens=[1],values=[-.91]):
  probs=[{str(t):p} for t,p in zip(tokens,values)]
  return dict(tokens=tokens,logprobs=probs,returned_prompt_token_ids=[7],completions=[dict(tokens=tokens,logprobs=probs)])
 def test_old_numeric_fail_observation_does_not_throw(self):
  result=compare(self.row(values=[-.91057825]),self.row(values=[-1.01327586]))
  self.assertFalse(result['old_logprob_all_pass']);self.assertTrue(result['tokens_exact'])
 def test_token_divergence_remains_fixed_length_descriptive(self):
  result=compare(self.row([1,2],[1.,2.]),self.row([1,3],[1.,3.]))
  self.assertEqual(result['common_prefix_tokens'],1);self.assertEqual(result['first_divergence'],1);self.assertFalse(result['tokens_exact'])
 def test_invalid_input_still_stops(self):
  with self.assertRaises(AssertionError):validate(self.row(),[8],1,20)
 def test_nonfinite_still_stops(self):
  with self.assertRaises(AssertionError):validate(self.row(values=[float('nan')]),[7],1,20)
 def test_None_logprob_path_not_fake_PASS(self):
  row=self.row();row['completions'][0]['logprobs']=[];row['logprobs']=[]
  validate(row,[7],1,None);self.assertIsNone(compare(row,row,False)['old_logprob_all_pass'])
 def test_sampled_prob_and_cache_receipt_persist_before_gate(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);raw={'samples':[]};private={'samples':[]}
   out=N(token_ids=[1],logprobs=[{1:N(logprob=-1.2,rank=1)}])
   response=N(request_id='r',prompt_token_ids=[7],outputs=[out],num_cached_tokens=496)
   capture_batch([response],['A'],[[7]],dict(point='P',role='FORMAL',round=0),raw,private,d/'r',d/'p',{})
   saved=json.loads((d/'p').read_text());self.assertEqual(saved['samples'][0]['outputs'][0]['num_cached_tokens'],496)
   self.assertEqual(saved['samples'][0]['outputs'][0]['completions'][0]['sampled_token_logprobs'],[-1.2])
class DispatcherTests(unittest.TestCase):
 def build(self,name,failed=False):
  cfg=config(name);cfg.update(v8_dispatch=True,worker_tasks=['BASE','PREFIX'],held_seconds_max=1800)
  s=services();state={'current':None,'spawned':0,'active':0};children=[]
  def spawn():
   self.assertEqual(state['active'],0)
   state['spawned']+=1;state['active']=1;c=FakeChild(2 if failed and state['spawned']==1 else 0);children.append(c);state['current']=state['spawned'];return c
  def result():
   state['active']=0
   names=['MAIN','LP20_CONTROL','LP_NONE'] if state['current']==1 else ['APC_COLD','APC_WARM']
   return dict(status='ERROR' if failed and state['current']==1 else 'V8_WORKER_COMPLETE',model_initializations=1,config_completion={n:{'P'+str(i):5 for i in range(1,7)} for n in names})
  s.spawn=spawn;s.worker_result=result
  return cfg,s,state
 def test_serial_two_contexts_one_lock_and_cleanup(self):
  cfg,s,state=self.build('v8serial');r=Supervisor(cfg,s).run()
  self.assertEqual(r['status'],'V8_STUDY_COMPLETE');self.assertEqual(r['worker_launches'],2);self.assertEqual(r['lock_attempt_count'],1);self.assertTrue(r['lock_released']);self.assertEqual(r['GPU_model_initializations'],2)
 def test_runtime_error_prevents_next_GPU_owner(self):
  cfg,s,state=self.build('v8failure',True);r=Supervisor(cfg,s).run()
  self.assertEqual(r['status'],'NUMERIC_OR_RUNTIME_NO_GO');self.assertEqual(state['spawned'],1);self.assertTrue(r['lock_released'])
 def test_missing_matrix_cannot_be_complete(self):
  cfg,s,state=self.build('v8missing');s.worker_result=lambda:dict(status='V8_WORKER_COMPLETE',model_initializations=1,config_completion={})
  r=Supervisor(cfg,s).run();self.assertEqual(r['status'],'NUMERIC_OR_RUNTIME_NO_GO');self.assertEqual(r['worker_launches'],1)
class FrozenV8PlanTests(unittest.TestCase):
 def test_observer_after_formal_only_and_restored(self):
  text=(Path(__file__).parent/'worker.py').read_text()
  self.assertLess(text.index("series(['LP20_CONTROL','LP_NONE'])"),text.index('observer.install()'))
  self.assertIn('observer.restore()',text);self.assertIn("role in ['OBSERVER','CACHE_PRIME']",text)
 def test_original_double_diagnostic_not_repeated(self):
  text=(Path(__file__).parent/'worker.py').read_text();self.assertNotIn("for ri in range(c['V6_diagnostic_phase']",text)
 def test_cold_warm_reset_outside_timing(self):
  text=(Path(__file__).parent/'worker.py').read_text();self.assertIn('llm.reset_prefix_cache()',text);self.assertIn("override_count=1",text)
if __name__=='__main__':unittest.main()
