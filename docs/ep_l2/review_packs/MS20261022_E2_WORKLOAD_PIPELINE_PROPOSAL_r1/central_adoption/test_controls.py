"""Bounded engineering controls using candidate actual APIs and temporary registry.
No simulator, native test, build, real process, live lease or central mutation.
"""
import contextlib,copy,hashlib,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
sys.path.insert(0,str(HERE/'candidate'))
import coordinator as c
import workload_policy as w
import limits_policy as lp
import policy_v2 as pv
LIVE=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())

class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='e2_scope_control_');self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);(self.root/c.FIELD).mkdir();self.output=self.root/'out';self.output.mkdir()
  self.data=copy.deepcopy(LIVE);self.item=self.data[c.FIELD]
  self.coord=c.Coordinator(self.root)
  self.enterContext(patch.object(c,'OUTPUT',self.output))
  self.live=dict(available_memory_bytes=220*c.GIB,disk_free_bytes=20*c.GIB,share_disk_free_bytes=44*c.GIB)
  self.usage=dict(new_bytes=6899258320,total_bytes=21208834704,old_bytes=14309576384)
  self.enterContext(patch.object(c,'local_resources',return_value=self.live))
  self.enterContext(patch.object(c,'output_usage',return_value=self.usage))
  self.old_digest=c.digest
  self.fakebin=self.root/'fake-main61';self.fakebin.write_bytes(b'not executable: synthetic control')
  def digest(path):return w.MAIN61 if Path(path).resolve()==self.fakebin.resolve() or Path(path).name=='accel-sim.out' else self.old_digest(path)
  self.enterContext(patch.object(c,'digest',side_effect=digest))
  self.save();self.coord.adopt_workload_pipeline(w.APPROVAL_PATH)
  self.specs=[]
  oldpack=ROOT/'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_FWT_FIRST_PAIR_CONTINUATION_r1'
  for profile in ('S','F'):
   spec=json.loads((oldpack/f'FWT_7_21_{profile}_SPEC.json').read_text())
   cid='V4_FWT_MAIN61_RESTORE_'+profile
   spec.update(condition_id=cid,budget_bucket=w.FWT_BATCH,binary=str(self.fakebin),timeout_seconds=None,
      retry_previous_attempt=w.CONDITIONS[cid][5],retry_reason='synthetic exact approved lifecycle restoration')
   spec['operational_limits_override']=w.operational_override(spec)
   spec['input_audit']={'identity':spec['identity']}
   self.coord.bind_workload_condition(spec);self.specs.append(spec)
 def save(self):(self.root/'RUN_REGISTRY.json').write_text(json.dumps(self.data))
 def read(self):return json.loads((self.root/'RUN_REGISTRY.json').read_text())
 def mutate(self,fn):
  data=self.read();fn(data[c.FIELD]);(self.root/'RUN_REGISTRY.json').write_text(json.dumps(data))
 def test_actual_approval_bytes_and_initial_adoption(self):
  x=self.coord.snapshot();self.assertTrue(w.active(x));self.assertEqual(x['actual_starts'],46)
  self.assertFalse(self.coord.adopt_workload_pipeline(w.APPROVAL_PATH)['changed'])
 def test_fwt_S_actual_reserve_api(self):
  row=self.coord.reserve_application(self.specs[0]);x=self.coord.snapshot()
  self.assertEqual(row['condition_id'],self.specs[0]['condition_id']);self.assertEqual(x['actual_starts'],46)
  self.assertEqual(x[w.FIELD]['batches'][w.FWT_BATCH]['attempt_ids'],[row['attempt_id']])
 def test_both_fwt_reservations_resource_only(self):
  rows=[self.coord.reserve_application(s) for s in self.specs]
  self.assertEqual(len(rows),2);self.assertEqual(len(self.coord.snapshot()['attempts']),48)
 def test_duplicate_same_condition_denied(self):
  self.coord.reserve_application(self.specs[0])
  with self.assertRaisesRegex(ValueError,'already attempted'):self.coord.reserve_application(self.specs[0])
 def test_wrong_binary_denied(self):
  s=copy.deepcopy(self.specs[0]);s['identity']['binary_sha256']='0'*64
  self.assertFalse(lp.has_start_capacity(self.coord.snapshot(),s))
 def test_wrong_trace_denied(self):
  s=copy.deepcopy(self.specs[0]);s['identity']['trace_content_sha256']='0'*64
  self.assertFalse(lp.scope_allowed(self.coord.snapshot(),s))
 def test_wrong_profile_denied(self):
  s=copy.deepcopy(self.specs[0]);s['profile']='F';self.assertFalse(w.scope_allowed(self.coord.snapshot(),s))
 def test_extra_condition_denied(self):
  s=copy.deepcopy(self.specs[0]);s['condition_id']='V4_EXTRA'
  with self.assertRaises(ValueError):self.coord.reserve_application(s)
 def test_wrong_bucket_denied(self):
  s=copy.deepcopy(self.specs[0]);s['budget_bucket']='contingency';self.assertFalse(w.scope_allowed(self.coord.snapshot(),s))
 def test_no_unbound_sgemm_inherits_fwt_qualification(self):
  s=copy.deepcopy(self.specs[0]);s.update(condition_id='V4_SGEMM_MAIN61_EXPLORATORY_S',budget_bucket=w.SGEMM_BATCH,
   selection_id='D_EXP_SGEMM_MEDIUM_20261022_r1',comparison_group='V4_EXP_SGEMM_MAIN61_SF',retry_previous_attempt=None,retry_reason=None)
  s['identity']['workload']='sgemm';s['identity']['trace_content_sha256']=w.TRACES['sgemm'];s['operational_limits_override']=w.operational_override(s)
  with self.assertRaisesRegex(ValueError,'wrong input/main61 Q'):self.coord.bind_workload_condition(s)
 def test_config_and_parser_change_denied(self):
  for field,value in [('configs',[]),('parser',{'path':'wrong'}),('qualification_id','wrong')]:
   s=copy.deepcopy(self.specs[0]);s[field]=value;self.assertFalse(w.scope_allowed(self.coord.snapshot(),s))
 def test_identity_timeout_remains_frozen_but_effective_null(self):
  s=self.specs[0];self.assertEqual(s['identity']['termination_contract']['timeout_seconds'],10800)
  self.assertIsNone(lp.effective_timeout(self.coord.snapshot(),s))
  s=copy.deepcopy(s);s['operational_limits_override']['effective_timeout_seconds']=10800
  with self.assertRaises(ValueError):lp.effective_timeout(self.coord.snapshot(),s)
 def test_inputaudit_only_reattachment_allowed(self):
  s=copy.deepcopy(self.specs[0]);s['input_audit']={'identity':s['identity'],'new_inspection':True}
  self.assertTrue(w.scope_allowed(self.coord.snapshot(),s))
 def test_old46_prefix_immutable(self):
  self.mutate(lambda x:x['attempts'][0].update(state='REFUNDED'))
  with self.assertRaisesRegex(ValueError,'old46|pre-amendment'):self.coord.snapshot()
 def test_old_reservations_immutable(self):
  self.mutate(lambda x:x['reservations'].update(contingency=9))
  with self.assertRaises(ValueError):self.coord.snapshot()
 def test_old_matrix_immutable(self):
  self.mutate(lambda x:x['full_system_matrix'].update(sha256='0'*64))
  with self.assertRaises(ValueError):self.coord.snapshot()
 def test_old_accepted_immutable(self):
  self.mutate(lambda x:x['accepted_pairs'].clear())
  with self.assertRaisesRegex(ValueError,'scientific record'):self.coord.snapshot()
 def test_no_spec_rebinding(self):
  s=copy.deepcopy(self.specs[0]);s['retry_reason']='different'
  with self.assertRaisesRegex(ValueError,'immutable spec'):self.coord.bind_workload_condition(s)
 def test_wrong_retry_id_denied(self):
  s=copy.deepcopy(self.specs[0]);s['retry_previous_attempt']='E001'
  self.assertFalse(w.scope_allowed(self.coord.snapshot(),s))
 def test_no_bypass_failure_refund(self):
  row=self.coord.reserve_application(self.specs[0])
  def finish(x):
   a=x['attempts'][-1];a.update(state='RESOURCE_LIMIT',actual_start=True)
  self.mutate(finish)
  x=self.read();x['runs'][row['run_key']]['status']='RESOURCE_LIMIT';(self.root/'RUN_REGISTRY.json').write_text(json.dumps(x))
  self.assertEqual(self.coord.snapshot()['actual_starts'],46) # snapshot is read-only; next transaction recounts
  with self.coord.locked() as (d,item):pass
  self.assertEqual(self.coord.snapshot()['actual_starts'],47)
  with self.assertRaisesRegex(ValueError,'already attempted'):self.coord.reserve_application(self.specs[0])
 def test_only_original_controller_may_start(self):
  row=self.coord.reserve_application(self.specs[0]);directory=Path(row['result_directory']);directory.mkdir();(directory/'accel-sim.out').write_bytes(b'fake')
  with self.assertRaisesRegex(ValueError,'singleton E controller'):
   self.coord.start_application(row['attempt_id'],[str(directory/'accel-sim.out')],directory,{},io.BytesIO(),lambda *a,**k:None)
 def test_single_original_lock(self):
  with self.coord.unique_controller():
   with self.assertRaisesRegex(ValueError,'already active'):
    with self.coord.unique_controller():pass
 def test_disk5plus2guard_retained(self):
  self.live['disk_free_bytes']=7*c.GIB
  with self.assertRaisesRegex(ValueError,'workspace'):self.coord.reserve_application(self.specs[0])
 def test_share_guard_retained(self):
  self.live['share_disk_free_bytes']=39*c.GIB
  with self.assertRaisesRegex(ValueError,'Share'):self.coord.reserve_application(self.specs[0])
 def test_memory_guard_retained(self):
  self.live['available_memory_bytes']=70*c.GIB
  with self.assertRaisesRegex(ValueError,'memory|RAM'):self.coord.reserve_application(self.specs[0])
 def test_new10gib_guard_retained(self):
  self.usage['new_bytes']=10*c.GIB
  with self.assertRaisesRegex(ValueError,'new-study'):self.coord.reserve_application(self.specs[0])
 def test_total24gib_guard_retained(self):
  self.usage['total_bytes']=24*c.GIB
  with self.assertRaisesRegex(ValueError,'old\+new'):self.coord.reserve_application(self.specs[0])
 def test_endpoint_cap_384mib(self):
  s=copy.deepcopy(self.specs[0]);s['maximum_result_bytes']=385*2**20
  self.assertFalse(w.scope_allowed(self.coord.snapshot(),s))
 def test_failed_spec_unchanged_old_prefix_buckets_results(self):
  old=copy.deepcopy(self.coord.snapshot());self.coord.reserve_application(self.specs[0]);new=self.coord.snapshot()
  for key in ('reservations','capacity_diagnostic_matrix','full_system_matrix','accepted_results','accepted_pairs','scientific_holds'):
   self.assertEqual(old.get(key),new.get(key))
  self.assertEqual(old['attempts'][:46],new['attempts'][:46]);self.assertEqual(old['t0_unix'],new['t0_unix'])

 def make_sgemm(self,profile):
  original=ROOT/'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_FWT_FIRST_PAIR_CONTINUATION_r1/FWT_7_21_QUALIFICATION.json'
  q=json.loads(original.read_text());q['input_selection_id']='D_EXP_SGEMM_MEDIUM_20261022_r1'
  qp=self.root/'sgemm-q.json';qp.write_text(json.dumps(q));qid=c.digest(qp)
  selection={'campaign_id':c.CAMPAIGN,'selected_by':'E','selection_id':q['input_selection_id'],
    'full_input_identity':{'trace_content_sha256':w.TRACES['sgemm'],'expected_full_instructions':1658916864,
     'comparison_groups':['V4_EXP_SGEMM_MAIN61_SF'],'runtime_independent_input_source':'SYNTHETIC_CONTROL_ONLY'}}
  sp=self.root/'sgemm-selection.json';sp.write_text(json.dumps(selection))
  data=self.read();x=data[c.FIELD];x['qualifications'][qid]={'path':str(qp),'sha256':qid,'qualification':q}
  x['input_selections'][q['input_selection_id']]={'path':str(sp),'sha256':c.digest(sp),'selection':selection}
  (self.root/'RUN_REGISTRY.json').write_text(json.dumps(data))
  s=copy.deepcopy(self.specs[int(profile=='F')]);s.update(condition_id='V4_SGEMM_MAIN61_EXPLORATORY_'+profile,
   budget_bucket=w.SGEMM_BATCH,selection_id=q['input_selection_id'],comparison_group='V4_EXP_SGEMM_MAIN61_SF',
   qualification_id=qid,retry_previous_attempt=None,retry_reason=None)
  s['identity']['workload']='sgemm';s['identity']['trace_content_sha256']=w.TRACES['sgemm']
  s['identity']['runtime_config_sha256']=('a' if profile=='S' else 'b')*64
  s['operational_limits_override']=w.operational_override(s);s['input_audit']={'identity':s['identity']}
  self.coord.bind_workload_condition(s);return s
 def test_four_exact_actual_interfaces_and_no_fifth(self):
  ss=self.specs+[self.make_sgemm('S'),self.make_sgemm('F')]
  for s in ss:self.coord.reserve_application(s)
  x=self.coord.snapshot();self.assertEqual(len(x['attempts']),50)
  self.assertEqual([len(z['attempt_ids']) for z in x[w.FIELD]['batches'].values()],[2,2])
  for s in ss:
   with self.assertRaises(ValueError):self.coord.reserve_application(s)
 def test_fifth_injected_row_rejected(self):
  for s in self.specs+[self.make_sgemm('S'),self.make_sgemm('F')]:self.coord.reserve_application(s)
  self.mutate(lambda x:x['attempts'].append(copy.deepcopy(x['attempts'][-1])))
  with self.assertRaisesRegex(ValueError,'at most four'):self.coord.snapshot()
 def test_real_start_api_fake_process_charge_and_failure_retained(self):
  from types import SimpleNamespace
  row=self.coord.reserve_application(self.specs[0]);directory=Path(row['result_directory']);directory.mkdir()
  (directory/'accel-sim.out').write_bytes(b'fake');(directory/'raw.log').write_bytes(b'fake terminal failure')
  real_identity=c.process_identity
  fake_identity={'pid':999999999,'start_ticks':42,'boot_id':'SYNTHETIC'}
  def identity(pid):return fake_identity if pid==999999999 else real_identity(pid)
  with self.coord.unique_controller():
   with patch.object(c,'process_identity',side_effect=identity):
    p=self.coord.start_application(row['attempt_id'],[str(directory/'accel-sim.out')],directory,{},io.BytesIO(),
      lambda *a,**k:SimpleNamespace(pid=999999999))
   self.assertEqual(self.coord.snapshot()['actual_starts'],47)
  receipt=dict(attempt_id=row['attempt_id'],run_key=row['run_key'],identity=row['identity'],status='RESOURCE_LIMIT',
    detail='synthetic failure charged',raw_log_sha256=c.digest(directory/'raw.log'))
  rp=directory/'RESULT.json';rp.write_text(json.dumps(receipt));self.coord.finish_application(row['attempt_id'],'RESOURCE_LIMIT',rp)
  self.assertEqual(self.coord.snapshot()['actual_starts'],47)
  with self.assertRaises(ValueError):self.coord.reserve_application(self.specs[0])
 def test_missing_approval_hash_refused(self):
  with patch.object(w,'APPROVAL_SHA256','0'*64):
   with self.assertRaisesRegex(ValueError,'approval changed'):w.authority()
 def test_cpu_guard_retained(self):
  data=self.read();data['resource_leases']['synthetic-cpu']={'status':'RUNNING','host':c.socket.gethostname(),
   'cpu_units':8,'memory_bytes':1,'kind':'test','result_directory':str(self.output),'disk_growth_bytes':1}
  (self.root/'RUN_REGISTRY.json').write_text(json.dumps(data))
  with self.assertRaisesRegex(ValueError,'CPU'):self.coord.reserve_application(self.specs[0])

 def test_old_bucket_recount_does_not_charge_new_batches(self):
  old=self.coord.snapshot();before={b:sum(pv.charged_bucket(a,old['reservations'])==b and a.get('actual_start') is True for a in old['attempts']) for b in old['reservations']}
  for spec in self.specs+[self.make_sgemm('S'),self.make_sgemm('F')]:self.coord.reserve_application(spec)
  def charge(x):
   for a in x['attempts'][46:]:a.update(actual_start=True,state='FAILED')
  self.mutate(charge)
  x=self.coord.snapshot();after={b:sum(pv.charged_bucket(a,x['reservations'])==b and a.get('actual_start') is True for a in x['attempts']) for b in x['reservations']}
  self.assertEqual(before,after)
  self.assertEqual(sum(pv.charged_bucket(a,x['reservations']) in (w.FWT_BATCH,w.SGEMM_BATCH) for a in x['attempts']),4)
 def test_exact_E_adoption_of_original_D_neutral_selection(self):
  p=ROOT/'docs/ep_l2/review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1/sgemm_qualification/D_SELECTION_ADOPTION.json'
  original=copy.deepcopy(self.coord.snapshot()['input_selections']);row=self.coord.adopt_workload_selection(p)
  x=self.coord.snapshot();self.assertEqual(row['selection']['selected_by'],'E')
  self.assertTrue(all(x['input_selections'][k]==v for k,v in original.items()))
  self.assertEqual(self.coord.adopt_workload_selection(p),row)
 def test_E_adoption_origin_hash_tamper_denied(self):
  p=ROOT/'docs/ep_l2/review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1/sgemm_qualification/D_SELECTION_ADOPTION.json'
  value=json.loads(p.read_text());value['original_D_preregistration']['sha256']='0'*64
  wrong=self.root/'wrong-selection.json';wrong.write_text(json.dumps(value))
  with self.assertRaisesRegex(ValueError,'preregistration bytes changed'):self.coord.adopt_workload_selection(wrong)

if __name__=='__main__':
 stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,
  'failures':len(result.failures),'errors':len(result.errors),'new_application_native_build_process_starts':0,
  'live_registry_mutations':0,'test_output':stream.getvalue()}
 (HERE/'CONTROL_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(stream.getvalue());sys.exit(not result.wasSuccessful())
