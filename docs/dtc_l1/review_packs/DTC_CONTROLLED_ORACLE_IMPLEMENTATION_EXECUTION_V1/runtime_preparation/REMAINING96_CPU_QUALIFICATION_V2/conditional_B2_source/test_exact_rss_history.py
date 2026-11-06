"""No model/registry write: real forecast/resources functions with CPU IO mocks."""
from pathlib import Path
import copy,hashlib,importlib.util,json,tempfile,types,unittest
P=Path(__file__).with_name('oracle_exact_rss_history.py');s=importlib.util.spec_from_file_location('CPU_EXACT_RSS',P);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
I='1'*64;J='2'*64;U='00000000-0000-0000-0000-000000000001'
class Tests(unittest.TestCase):
 def values(self):
  request='MOCK_NOT_SCIENCE_REQUEST';c='MOCK_NOT_SCIENCE_C';spec=dict(cohort=c,request=request,input_digest=I,_history_expected_spec_sha='MOCK_SPEC')
  intent=dict(uuid=U,cohort=c);done=dict(uuid=U,cohort=c,new_attempt_consumed=1,automatic_retry=False,peak_observed_rss_bytes=300,stop_reason='MOCK_NEGATIVE_ALLOWED')
  row=dict(uuid=U,intent_sha256='MOCK_INTENT',execution_receipt=done)
  return request,c,row,spec,'MOCK_SPEC',intent,'MOCK_INTENT',done,copy.deepcopy(done),{I}

 def test_exact_closed_negative_RSS_mapping_without_performance_filter(self):
  value,reject=h.validate_closed_sample(*self.values());self.assertIsNone(reject)
  self.assertEqual(value['peak_RSS_bytes'],300);self.assertTrue(value['performance_acceptance_not_consulted'])

 def test_missing_zero_bool_RSS_omitted_not_zero_history(self):
  for peak in [None,0,-1,True,'300']:
   args=list(self.values());args[7]['peak_observed_rss_bytes']=peak;args[2]['execution_receipt']=args[7];args[8]=copy.deepcopy(args[7])
   value,reject=h.validate_closed_sample(*args);self.assertIsNone(value);self.assertIn('NOT_ZERO',reject['reason'])

 def test_foreign_sha_broken_receipt_uuid_or_spec_refused(self):
  for kind in ['SHA','receipt','uuid','spec']:
   args=list(self.values())
   if kind=='SHA':args[3]['input_digest']=J
   elif kind=='receipt':args[8]['peak_observed_rss_bytes']=9
   elif kind=='uuid':args[2]['uuid']='foreign'
   else:args[4]='wrong'
   with self.assertRaises(h.HistoryHold):h.validate_closed_sample(*args)

 def test_capture_real_temporary_closed_files_outside_EX(self):
  with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_RSS_')as tmp:
   root=Path(tmp);c='MOCK_C';request='MOCK_REQ';out=root/'DTC/run/results'/U
   spec=dict(request=request,cohort=c,input_digest=I);sp=root/'control/specs'/(c+'.json');put(sp,spec)
   intent=dict(uuid=U,cohort=c,output=str(out));ip=root/'control/qualification_ledger'/(c+'.INTENT.json');put(ip,intent)
   done=dict(uuid=U,cohort=c,new_attempt_consumed=1,automatic_retry=False,peak_observed_rss_bytes=444)
   dp=ip.with_name(c+'.DONE.json');put(dp,done);put(out/'NATIVE_EXIT.json',done)
   q=dict(request=request,admitted_specs={c:h.sha(sp)},consumed={c:dict(uuid=U,intent_sha256=h.sha(ip),execution_receipt=done)})
   inEX=[False];calls=[]
   def registered():
    if inEX[0]:raise AssertionError('NO_REGISTRY_REENTRY_IN_EX')
    calls.append('OUTSIDE_EX');return None,None,q,None
   ctx=dict(root=root,request=request,e=types.SimpleNamespace(registered=registered))
   snapshot=h.capture([ctx],{I});self.assertEqual(snapshot['rows'][0]['peak_RSS_bytes'],444);self.assertEqual(calls,['OUTSIDE_EX'])
   before=dict(snapshot);inEX[0]=True
   for _ in range(3):self.assertEqual(h.verify_snapshot(snapshot),before)
   self.assertEqual(calls,['OUTSIDE_EX']) # snapshot consumption never falls back to capture

 def resource(self):
  p=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8/tools/oracle_resources.py')
  r=types.ModuleType('MOCK_RES_REAL_FUNCTIONS');r.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),r.__dict__)
  predictions=[]
  helper=types.SimpleNamespace(admit_resource=lambda sample,predicted,*args,**kwargs:(predictions.append(predicted)or dict(admit=True,reasons=[],required_native_bytes=5*1024**3)))
  peer=types.SimpleNamespace(check=lambda spec,container:dict(status='PASS',fresh_local_native_peer_reservations=True,native_device=2128,bounded_runtime_seconds=1,own_future_write_bytes=0,native_restore_bytes=0,peer_future_write_bytes=0))
  r.load=lambda name,path:peer if name=='oracle_qualified_peer_disk_adapter'else helper
  r.sha=lambda path:'MOCK_PIN'
  r.plan=lambda:dict(peer_disk_adapter=dict(path='MOCK_PEER',sha256='MOCK_PIN',function='check'),archive_target_root='/root/share/mnt164/MOCK_ONLY')
  r.sample_system=lambda:dict(cpu_allowed=[1],observed_affinity_claims=[],native_free_bytes=99*1024**3)
  class MockSubprocess:
   class TimeoutExpired(Exception):pass
   @staticmethod
   def check_output(argv,**kwargs):
    return json.dumps(dict(filesystems=[dict(fstype='fuse.sshfs',source='admin-wcx@10.208.130.164:/home/shared')]))if argv[0]=='findmnt'else json.dumps(dict(free_bytes=100*1024**3))
  r.subprocess=MockSubprocess
  return r,predictions

 def snapshot(self,rows):
  body=dict(schema='MOCK_NOT_SCIENCE_SNAPSHOT',rows=rows);body['snapshot_sha256']=h.digest(body);return body

 def test_actual_picker_fresh_and_postclaim_use_same_snapshot_NO_EX_IO(self):
  r,pred=self.resource();snap=self.snapshot([dict(input_digest=I,peak_RSS_bytes=300)]);h.bind_forecast(r,lambda:snap)
  spec=dict(cohort='MOCK_C',input_digest=I,estimated_peak_model_RAM_bytes=100,expected=dict(instructions=10))
  decision=h.choose(r,snap,[spec],r.sample_system(),{},policy={});self.assertEqual(decision['predicted_peak_RAM_bytes'],360)
  first=r.resources(spec,True);second=r.resources(spec,True)
  self.assertEqual(pred[-2:],[360,360]);self.assertEqual(decision['RSS_history_snapshot_sha256'],snap['snapshot_sha256'])
  self.assertTrue(first['physical_RAM_pass']and second['physical_disk_pass'])
  self.assertEqual(r.forecast(dict(spec,input_digest=J)),100) # foreign input sample cannot lower/raise this input

 def test_no_history_or_smaller_history_preserves_frozen_prediction(self):
  for rows in [[],[dict(input_digest=I,peak_RSS_bytes=10)]]:
   r,pred=self.resource();snap=self.snapshot(rows);h.bind_forecast(r,lambda:snap)
   self.assertEqual(r.forecast(dict(input_digest=I,estimated_peak_model_RAM_bytes=100)),100)

 def test_changed_snapshot_or_other_snapshot_object_refused(self):
  r,pred=self.resource();snap=self.snapshot([dict(input_digest=I,peak_RSS_bytes=300)]);h.bind_forecast(r,lambda:snap)
  spec=dict(input_digest=I,estimated_peak_model_RAM_bytes=100)
  with self.assertRaises(h.HistoryHold):r.forecast(spec,copy.deepcopy(snap['rows']))
  snap['rows'][0]['peak_RSS_bytes']=5
  with self.assertRaises(h.HistoryHold):r.forecast(spec)

if __name__=='__main__':unittest.main(verbosity=2)
