"""CPU mocks only: no real tail consumer/strict/archive/model is called."""
from pathlib import Path
import copy,hashlib,importlib.util,json,tempfile,types,unittest
from unittest.mock import patch
P=Path(__file__).with_name('oracle_scan_off_tail1.py');s=importlib.util.spec_from_file_location('MOCK_TAIL1',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')

class Tests(unittest.TestCase):
 def predecessor(self):
  rows=[];completed=[];hashes={}
  for i in range(31):
   c='MOCK_NOT_SCIENCE_'+str(i);u='MOCK_UUID_'+str(i);sh='MOCK_SHA_'+str(i)
   rows.append(dict(cohort=c,uuid=u,existing_result_sha256=sh if i<8 else None))
   completed.append(dict(cohort=c,uuid=u,original_state=m.PASS,result_sha256=sh,preserved_existing_result=i<8));hashes[c]=sh
  return dict(rows=rows),dict(state='ALL_FIXED31_CLOSED_VERIFIED_PASS_COMPLETE_NO_SCIENCE_RELEASE',caller_pid=450154,errors=[],completed=completed),hashes

 def test_prior31_and_original8_must_be_complete_unchanged(self):
  snap,final,hashes=self.predecessor();self.assertTrue(m.predecessor_terminal_projection(final,snap,hashes)['previous8_preserved'])
  for target in ['incomplete','SHA','old8','tail']:
   s,f,h=copy.deepcopy(snap),copy.deepcopy(final),copy.deepcopy(hashes)
   if target=='incomplete':f['completed'].pop()
   elif target=='SHA':h[s['rows'][30]['cohort']]='WRONG'
   elif target=='old8':s['rows'][0]['existing_result_sha256']='WRONG'
   else:s['rows'][0]['cohort']=m.COHORT
   with self.assertRaises(m.Hold):m.predecessor_terminal_projection(f,s,h)

 def test_active_previous_closer_or_nonzero_exit_hold(self):
  f=['0']*50;f[0]='R';f[19]='1073442087'
  with self.assertRaises(m.Hold):m.predecessor_process_exited(f,1073442087)
  f[0]='Z';f[49]='256'
  with self.assertRaises(m.Hold):m.predecessor_process_exited(f,1073442087)
  f[49]='0';self.assertTrue(m.predecessor_process_exited(f,1073442087));self.assertTrue(m.predecessor_process_exited(None,1073442087))

 def fixture(self,root,negative=True,bad_value=None,add_fake_strict=False):
  spec=dict(input_digest=m.INPUT,program='scan',oracle_mode='OFF_MATCHED')
  sp=root/'control/specs'/(m.COHORT+'.json');put(sp,spec)
  out=root/'DTC/run/results'/m.UUID;out.mkdir(parents=True)
  (out/'raw.log.gz').write_bytes(b'MOCK_NOT_SCIENCE_RAW_NOT_GZIP')
  i=dict(uuid=m.UUID,cohort=m.COHORT,output=str(out));ip=root/'control/qualification_ledger'/(m.COHORT+'.INTENT.json');put(ip,i)
  d=dict(uuid=m.UUID,cohort=m.COHORT,new_attempt_consumed=1,automatic_retry=False,
       stop_reason='MOCK_ORIGINAL_STOP'if negative else None,launcher_wait_returncode=1 if negative else 0,
       native_simulator_observed=True,raw_sha256=m.sha(out/'raw.log.gz'),raw_uncompressed_sha256='MOCK_ORIGINAL_RAW_SHA')
  put(ip.with_name(m.COHORT+'.DONE.json'),d);put(out/'NATIVE_EXIT.json',d)
  put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=999999999,start_ticks=1))
  q=dict(request=m.REQUEST,budget=32,remaining=0,consumed={m.COHORT:dict(uuid=m.UUID,intent_sha256=m.sha(ip),execution_receipt=d)})
  engine=types.SimpleNamespace(registered=lambda:(None,None,copy.deepcopy(q),None),spec_for=lambda c:spec)
  calls=[]
  archive=dict(MOCK_NOT_SCIENCE=True,registered_outbox_binding=dict(negative_performance_accepted=False,failure_classification='MOCK_ORIGINAL_FAILURE'))
  outbox=types.SimpleNamespace(classification=lambda d:'MOCK_ORIGINAL_FAILURE',verify=lambda c:archive)
  def finish_evidence(c):
   calls.append('original_negative_consumer');rp=root/'analysis'/(c+'.RESULT.json')
   if rp.exists():return json.loads(rp.read_bytes())
   proof=dict(status='CONTROLLED_ORACLE_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],
       native_simulator_observed=d['native_simulator_observed'],failure_classification='MOCK_ORIGINAL_FAILURE',accepted_cycles=None,
       raw_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],performance_accepted=False)
   value=dict(uuid=m.UUID,cohort=c,state=m.NEG,cycles=None,proof=proof,archive=archive)
   if bad_value:bad_value(value)
   if add_fake_strict:put(out/'L2_STRICT.json',dict(MOCK_FORGED_PASS=True))
   put(rp,value);return value
  consumer=types.SimpleNamespace(load=lambda n,f:engine if f=='oracle_native.py'else outbox,finish_evidence=finish_evidence)
  class Session:
   def __init__(self):self.consumer=consumer
   def _assert_thread(self):calls.append('thread_check')
   def _admission(self):calls.append('actual_gate_mocked_no_science')
   def finish(self,c):calls.append('qualified_S17_positive_path');return dict(uuid=m.UUID,cohort=c,state=m.PASS,cycles=123)
  base=types.SimpleNamespace(verify_request_monotonic=lambda before,after,root:self.assertEqual(before,after))
  return Session(),base,engine,calls,sp,out

 def test_positive_uses_unmodified_S17_positive_finish(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_POS_')as tmp:
   root=Path(tmp);session,base,engine,calls,sp,out=self.fixture(root,negative=False)
   with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)):
    self.assertEqual(m.finish_one(session,base)['state'],m.PASS)
   self.assertIn('qualified_S17_positive_path',calls);self.assertNotIn('original_negative_consumer',calls)

 def test_negative_keeps_original_proof_null_cycles_and_no_strict(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_NEG_')as tmp:
   root=Path(tmp);session,base,engine,calls,sp,out=self.fixture(root)
   with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)):
    v=m.finish_one(session,base);self.assertEqual(v['state'],m.NEG);self.assertIsNone(v['cycles']);self.assertFalse(v['proof']['performance_accepted'])
    before=m.sha(root/'analysis'/(m.COHORT+'.RESULT.json'));m.finish_one(session,base)
    self.assertEqual(before,m.sha(root/'analysis'/(m.COHORT+'.RESULT.json')))
   self.assertFalse((out/'L2_STRICT.json').exists());self.assertNotIn('qualified_S17_positive_path',calls)

 def test_negative_cannot_promote_cycles_failure_or_fake_strict(self):
  mutations=[lambda v:v.update(cycles=0),lambda v:v.update(state=m.PASS),lambda v:v['proof'].update(stop_reason='CHANGED'),lambda v:v['proof'].update(performance_accepted=True)]
  for mutate in mutations:
   with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_BAD_')as tmp:
    root=Path(tmp);session,base,engine,calls,sp,out=self.fixture(root,bad_value=mutate)
    with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)),self.assertRaises(m.Hold):m.finish_one(session,base)
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_STRICT_')as tmp:
   root=Path(tmp);session,base,engine,calls,sp,out=self.fixture(root,add_fake_strict=True)
   with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)),self.assertRaises(m.Hold):m.finish_one(session,base)

 def test_missing_done_or_live_tail_is_hold_not_a_retry(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_WAIT_')as tmp:
   root=Path(tmp);session,base,engine,calls,sp,out=self.fixture(root)
   with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)),patch.object(m,'start',return_value=1),self.assertRaises(m.Hold):m.closed_tail(engine)
   (root/'control/qualification_ledger'/(m.COHORT+'.DONE.json')).unlink()
   with patch.object(m,'ROOT',root),patch.object(m,'SPEC_SHA',m.sha(sp)),self.assertRaises(m.Hold):m.closed_tail(engine)

 def test_default_unarmed_cannot_load_consumer(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_TAIL_DRAFT_')as tmp:
   p=Path(tmp)/'draft.json';put(p,dict(actual_execution_authorized=False))
   with self.assertRaises(m.Hold):m.run(p,m.sha(p))

if __name__=='__main__':unittest.main(verbosity=2)
