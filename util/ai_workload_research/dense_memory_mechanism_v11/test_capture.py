import unittest,tempfile,json
from pathlib import Path
from types import SimpleNamespace as S
from capture import capture_batch
class FullBatchPersistence(unittest.TestCase):
 def test_first_numeric_failure_preserves_second_and_graph(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);raw={'samples':[]};private={'samples':[]};sample={'point':'P3','role':'DIAGNOSTIC','round':0}
   def response(i):return S(request_id=str(i),prompt_token_ids=[i],outputs=[S(token_ids=[i+3],logprobs=[{i+3:S(logprob=-1.0,rank=1)}])])
   capture_batch([response(0),response(1)],['A00','A01'],[[0],[1]],sample,raw,private,d/'raw.json',d/'private.json',{'active_compiled_Qwen2Model':[{'compiled':True}],'graph_replays':[]})
   with self.assertRaises(AssertionError):
    assert False,'first completion numeric gate failed'
   saved=json.loads((d/'private.json').read_text())
   self.assertEqual([x['source'] for x in saved['samples'][0]['outputs']],['A00','A01'])
   self.assertEqual(saved['samples'][0]['outputs'][1]['tokens'],[4])
   self.assertTrue(json.loads((d/'raw.json').read_text())['samples'][0]['capture_complete_before_numeric_gate'])
   self.assertTrue(json.loads((d/'raw.json').read_text())['samples'][0]['active_compiled_Qwen2Model'])
 def test_all_completion_alternatives_preserved_before_rejection(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);raw={'samples':[]};private={'samples':[]}
   out=S(token_ids=[3],logprobs=[{3:S(logprob=-1,rank=1)}])
   response=S(request_id='r',prompt_token_ids=[1],outputs=[out,out])
   capture_batch([response],['A'],[[1]],dict(point='P',role='D',round=0),raw,private,d/'r',d/'p',{})
   self.assertEqual(len(json.loads((d/'p').read_text())['samples'][0]['outputs'][0]['completions']),2)
if __name__=='__main__':unittest.main()
