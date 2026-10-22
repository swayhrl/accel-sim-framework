"""SYNTHETIC engineering arithmetic only. No real admission or application."""
import copy,hashlib,importlib.util,json,sys,tempfile,types,unittest
from pathlib import Path
sys.dont_write_bytecode=True
G=2**30;M=2**20;CIDS=tuple('V8_TAGPRESSURE_'+w+'_F' for w in ('cfd_097k','dwt2d','vectorAdd_4M','convolutionSeparable'))
r=types.ModuleType('tagpressure_successor');r.CONDITIONS=CIDS;r.CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1';r.FIELD='tagpressure_observer_successor_batch';r.ACTIVE={'RESERVED','RUNNING','START_INTENT_UNRECONCILED'};r.BEFORE={'RESERVED','START_INTENT_UNRECONCILED','FAILED_SPAWN','CANCELLED_BEFORE_START'};r.AFTER={'RUNNING','COMPLETE_VALID','FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE'}
def req(x,m):
 if not x:raise ValueError(m)
r.require=req
m={'conditions':{cid:{'metadata_forecast_bytes':160*M,'resources':{'maximum_result_bytes':384*M}} for cid in CIDS},'collector_metadata_forecast_bytes':640*M,'source_identity':{'source':'SYNTHETIC'}}
r.scope=lambda:types.SimpleNamespace(manifest=lambda:m)
def read(ref):
 b=Path(ref['path']).read_bytes();req(hashlib.sha256(b).hexdigest()==ref['sha256'],'fixture metadata changed');return json.loads(b)
r.read=read;sys.modules[r.__name__]=r
sp=importlib.util.spec_from_file_location('split_metadata',Path(__file__).with_name('tagpressure_metadata.py'));md=importlib.util.module_from_spec(sp);sp.loader.exec_module(md)
class Tests(unittest.TestCase):
 def setUp(self):self.i={'attempts':[{} for _ in range(55)],r.FIELD:{'metadata_closures':{}},'accepted_results':{}};self.temp=tempfile.TemporaryDirectory();self.d=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def add(self,cid,state='RUNNING'):
  a={'condition_id':cid,'state':state,'actual_start':state not in r.BEFORE,'attempt_id':'NEW'+str(len(self.i['attempts']))};self.i['attempts'].append(a);return a
 def call(self,**kw):
  a=dict(item=self.i,resources={'disk_free_bytes':20*G},usage={'new_bytes':0,'total_bytes':0},physical_pending_bytes=0,other_result_pending_bytes=0,proposed_growth_bytes=384*M,proposed_monitor_bytes=2*G,endpoint_retained_bytes={},submitted_condition_ids=[],proposed_condition_ids=[CIDS[0]]);a.update(kw);return md.preflight(**a)
 def closure(self,cid):
  a=self.add(cid,'COMPLETE_VALID')
  def save(n,d):p=self.d/n;p.write_text(json.dumps(d));return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  rr=save('result.json',{'status':'COMPLETE_VALID'});self.i['accepted_results'][a['attempt_id']]=rr
  rb=save('readback.json',{'remote_commit':'a'*40,'verified':True})
  cr=save('closure.json',{'schema':'E2_R5_ENDPOINT_METADATA_PUBLICATION_CLOSED_V1','status':'E_ROOT_INDEPENDENT_POINT_AND_METADATA_CLOSED','campaign_id':r.CAMPAIGN,'condition_id':cid,'source_identity':m['source_identity'],'attempt_id':a['attempt_id'],'accepted_result_ref':rr,'actual_metadata_allocated_bytes':120*M,'actual_generation_retained_in_accounting':True,'retired_remaining_forecast_bytes':160*M,'released_forecast_is_not_generated_result_refund':True,'immutable_publication_commit':'a'*40,'publication_remote_readback_ref':rb});self.i[r.FIELD]['metadata_closures'][cid]=cr
 def test_initial_batch_generation_exact2125GiB(self):
  x=self.call();self.assertEqual(x['metadata_generation_reserve_bytes'],640*M);self.assertEqual(x['batch_endpoint_remaining_generation_bytes'],1536*M);self.assertEqual(x['full_batch_initial_forecast_bytes'],2281701376)
 def test_initial_physical_one160(self):self.assertEqual(self.call()['physical_metadata_forecast_bytes'],160*M)
 def test_physical_boundary_and_no_added640_rule(self):
  boundary=5*G+2*G+384*M+160*M;x=self.call(resources={'disk_free_bytes':boundary});self.assertEqual(x['physical_metadata_condition_ids'],[CIDS[0]]);self.assertLess(boundary-384*M-2*G-640*M,5*G)
 def test_physical_onebyte_short_rejected(self):
  with self.assertRaises(ValueError):self.call(resources={'disk_free_bytes':5*G+2*G+384*M+160*M-1})
 def test_monitor2GiB_not_borrowed(self):
  with self.assertRaises(ValueError):self.call(resources={'disk_free_bytes':5*G+384*M+160*M})
 def test_submitted_plus_proposed_dedup(self):
  self.add(CIDS[0]);x=self.call(endpoint_retained_bytes={CIDS[0]:1},submitted_condition_ids=[CIDS[0],CIDS[1]],proposed_condition_ids=[CIDS[1]]);self.assertEqual(x['physical_metadata_forecast_bytes'],320*M)
 def test_two_submitted_and_new_proposed(self):self.assertEqual(self.call(submitted_condition_ids=[CIDS[0],CIDS[1]],proposed_condition_ids=[CIDS[2]])['physical_metadata_forecast_bytes'],480*M)
 def test_terminal_unclosed_keeps_physical160(self):
  self.add(CIDS[0],'RESOURCE_LIMIT');self.assertEqual(self.call(proposed_condition_ids=[CIDS[1]])['physical_metadata_forecast_bytes'],320*M)
 def test_unstarted_not_physically_reserved(self):self.assertNotIn(CIDS[3],self.call()['physical_metadata_condition_ids'])
 def test_generation_cannot_only_reserve_active(self):
  with self.assertRaises(ValueError):self.call(usage={'new_bytes':8*G,'total_bytes':10*G})
 def test_total24_boundary_reject(self):
  with self.assertRaises(ValueError):self.call(usage={'new_bytes':0,'total_bytes':24*G-2281701376+1})
 def test_otherpending_generation_retained(self):
  with self.assertRaises(ValueError):self.call(usage={'new_bytes':10*G-2281701376,'total_bytes':0},other_result_pending_bytes=1)
 def test_active_actualbytes_reduce_only_endpoint_future(self):
  self.add(CIDS[0]);x=self.call(endpoint_retained_bytes={CIDS[0]:256*M},proposed_growth_bytes=0,proposed_monitor_bytes=0);self.assertEqual(x['batch_endpoint_remaining_generation_bytes'],1280*M);self.assertEqual(x['metadata_generation_reserve_bytes'],640*M)
 def test_cannot_pretend_unstarted_retained(self):
  with self.assertRaises(ValueError):self.call(endpoint_retained_bytes={CIDS[3]:384*M})
 def test_cannot_skip_actual_active_stat(self):
  self.add(CIDS[0])
  with self.assertRaises(ValueError):self.call()
 def test_zero_physical_growth_only_for_held(self):
  with self.assertRaises(ValueError):self.call(proposed_growth_bytes=0,proposed_monitor_bytes=0)
 def test_unknown_condition_rejected(self):
  with self.assertRaises(ValueError):self.call(submitted_condition_ids=['OTHER'])
 def test_duplicate_submitted_rejected(self):
  with self.assertRaises(ValueError):self.call(submitted_condition_ids=[CIDS[0],CIDS[0]])
 def test_wrong_endpoint_cap_rejected(self):
  old=m['conditions'][CIDS[0]]['resources']['maximum_result_bytes'];m['conditions'][CIDS[0]]['resources']['maximum_result_bytes']=385*M
  try:
   with self.assertRaises(ValueError):self.call()
  finally:m['conditions'][CIDS[0]]['resources']['maximum_result_bytes']=old
 def test_true_closure_retires_future_no_usage_reset(self):
  self.closure(CIDS[0]);usage={'new_bytes':200*M,'total_bytes':300*M};before=copy.deepcopy(usage);x=self.call(usage=usage,proposed_condition_ids=[CIDS[1]]);self.assertEqual(x['metadata_generation_reserve_bytes'],480*M);self.assertEqual(x['physical_metadata_forecast_bytes'],160*M);self.assertEqual(x['batch_endpoint_remaining_generation_bytes'],1152*M);self.assertEqual(usage,before)
 def test_closed_cannot_be_proposed(self):
  self.closure(CIDS[0])
  with self.assertRaises(ValueError):self.call()
 def test_unvalidated_closure_cannot_reduce_forecast(self):
  self.i[r.FIELD]['metadata_closures'][CIDS[0]]={'path':str(self.d/'missing'),'sha256':'0'*64}
  with self.assertRaises((ValueError,FileNotFoundError)):self.call(proposed_condition_ids=[CIDS[1]])
if __name__=='__main__':unittest.main(verbosity=2)
