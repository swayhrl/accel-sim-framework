"""Actual copied Coordinator/temp registry/flock; fake native processes only."""
import copy,io,json,os,sys,unittest,builtins,hashlib
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
sys.path[:0]=[str(HERE),str(E/'util/ep_l2/mechanism_e')]
import synthetic_fixture_factory as f
import detach_scope_core as core
import detach_diagnostic_policy as dp
import detach_validation as dv
import coordinator as c
import limits_policy as lp
import policy_v2 as pv
import runner
import controller

WRITE_TARGETS=[]
EXTERNAL_REGISTRY_CHANGE_OBSERVED=[]

class APIControls(unittest.TestCase):
 def setUp(self):
  old_builtin_open=builtins.open;old_io_open=io.open;old_os_open=os.open
  def check_target(file):
   if isinstance(file,int):
    path=Path(os.readlink('/proc/self/fd/'+str(file))).resolve()
   else:path=Path(file).resolve()
   if not path.is_relative_to(HERE):raise AssertionError('write outside isolated candidate forbidden: '+str(path))
   WRITE_TARGETS.append(str(path))
  def builtin_open(file,mode='r',*args,**kwargs):
   if any(x in mode for x in 'wax+'):check_target(file)
   return old_builtin_open(file,mode,*args,**kwargs)
  def io_open(file,mode='r',*args,**kwargs):
   if any(x in mode for x in 'wax+'):check_target(file)
   return old_io_open(file,mode,*args,**kwargs)
  def os_open(file,flags,*args,**kwargs):
   if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):check_target(file)
   return old_os_open(file,flags,*args,**kwargs)
  self.enterContext(patch.object(builtins,'open',side_effect=builtin_open))
  self.enterContext(patch.object(io,'open',side_effect=io_open))
  self.enterContext(patch.object(os,'open',side_effect=os_open))
  self.fixture=f.ScopeControls('test_01_baseline_no_adoption');self.fixture.setUp()
  self.addCleanup(self.fixture.doCleanups)
  self.fx=self.fixture;self.root=self.fx.root/'central';self.root.mkdir()
  (self.root/c.FIELD).mkdir();self.out=self.fx.root/'results';self.out.mkdir()
  self.data=json.loads(f.LIVE_BYTES);self.data[c.FIELD]=copy.deepcopy(self.fx.item)
  self.item=self.data[c.FIELD]
  self.binary=self.fx.root/'SYNTHETIC_NOT_EXECUTABLE';self.binary.write_text('SYNTHETIC_FIXTURE NOT AN ELF\n')
  source=copy.deepcopy(self.fx.manifest['scientific_binding']['source_identity'])
  source['binary_sha256']=core.file_sha(self.binary)
  base=json.loads((E/'docs/ep_l2/review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1/sgemm_qualification/SGEMM_F_SPEC.json').read_text())
  identity=copy.deepcopy(base['identity'])
  for k in ('core_source_commit','framework_source_commit','binary_sha256'):identity[k]=source[k]
  profile=copy.deepcopy(base['profile_semantics']);profile['labels']['diagnostic']=True
  self.spec=copy.deepcopy(self.fx.spec)
  self.spec.update(identity=identity,binary=str(self.binary),vendor_pybind11_commit=source['vendor_pybind11_commit'],
   campaign_id=c.CAMPAIGN,launch_owner='E',comparison_group='SYNTHETIC_DIAGNOSTIC_POINT',
   profile_semantics=profile,labels=profile['labels'],timeout_seconds=None)
  self.spec['input_audit']={'identity':identity}
  q=dict(synthetic_fixture=True,status='INDEPENDENTLY_QUALIFIED',source_identity=source,
         scientific_scope=core.SCI_SCOPE,profile_semantics=profile,supported_profiles={'F':profile},
         detach_observer_diagnostic={'synthetic_fixture':True},input_selection_id=self.spec['selection_id'])
  qref=f.write(self.fx.root/'qualification.json',q);self.spec['qualification_id']=qref['sha256']
  producer=f.write(self.fx.root/'producer.json',{'synthetic_fixture':True,'source_identity':source})
  b=self.fx.manifest['scientific_binding'];b.update(source_identity=source,identity=identity,qualification=qref,
   producer=producer,spec_sha256=core.spec_sha(self.spec))
  self.fx.approval['manifest_scientific_binding_sha256']=core.sha(b);self.fx.refresh_authority()
  self.auth=self.fx.auth;self.qref=qref;self.q=q
  self.enterContext(patch.object(dp,'_AUTHORITY',self.auth))
  self.enterContext(patch.object(c,'OUTPUT',self.out))
  self.enterContext(patch.object(c,'retained_tree_bytes',return_value=0))
  self.enterContext(patch.object(c,'local_resources',return_value={
   'available_memory_bytes':220*c.GIB,'disk_free_bytes':24*c.GIB,'share_disk_free_bytes':44*c.GIB}))
  self.enterContext(patch.object(c,'output_usage',return_value={
   'old_bytes':14309576384,'new_bytes':8*c.GIB,'total_bytes':22*c.GIB}))
  self.coord=c.Coordinator(self.root)
  self.save()
  self.old_process=c.process_identity;self.fake_alive=True
  self.fake_pid=987654321
  self.fake_identity={'pid':self.fake_pid,'start_ticks':123456789,'boot_id':'SYNTHETIC_BOOT_ID'}
  def proc(pid):
   if pid==self.fake_pid:
    if not self.fake_alive:raise FileNotFoundError('synthetic retired')
    return copy.deepcopy(self.fake_identity)
   return self.old_process(pid)
  self.enterContext(patch.object(c,'process_identity',side_effect=proc))
 def save(self):f.write(self.root/'RUN_REGISTRY.json',self.data)
 def read(self):return json.loads((self.root/'RUN_REGISTRY.json').read_text())
 def ready(self):
  self.coord.adopt_detach_observer_batch()
  d=self.read();d[c.FIELD]['qualifications'][self.qref['sha256']]={**self.qref,'qualification':self.q}
  f.write(self.root/'RUN_REGISTRY.json',d)
  self.coord.bind_detach_observer_condition(self.spec)
 def reserve(self):
  self.ready();return self.coord.reserve_application(self.spec)
 def start(self):
  a=self.reserve();directory=Path(a['result_directory']);directory.mkdir()
  (directory/'accel-sim.out').write_bytes(self.binary.read_bytes())
  class Fake:
   pid=987654321
   guardian_identity={'pid':987654322,'start_ticks':987,'boot_id':'SYNTHETIC_BOOT_ID'}
   def release(self):pass
  with self.coord.unique_controller():
   result=self.coord.start_application(a['attempt_id'],[str(directory/'accel-sim.out')],directory,{},io.BytesIO(),lambda *args,**kwargs:Fake())
   self.assertEqual(result.pid,self.fake_pid)
  return a,directory
 def test_01_unconfigured_default_refuses_adoption(self):
  with patch.object(dp,'_AUTHORITY',None):
   with self.assertRaisesRegex(ValueError,'UNAVAILABLE'):self.coord.adopt_detach_observer_batch()
  self.assertEqual(self.coord.snapshot()['actual_starts'],50)
 def test_02_actual_adoption_and_binding(self):
  self.ready();s=self.coord.snapshot();self.assertTrue(dp.active(s))
  self.assertFalse(self.coord.adopt_detach_observer_batch()['changed'])
  self.assertEqual(s['actual_starts'],50)
 def test_03_actual_reservation_and_duplicate_rejection(self):
  a=self.reserve();s=self.coord.snapshot()
  self.assertEqual(len(s['attempts']),51);self.assertEqual(s['actual_starts'],50)
  self.assertEqual(a['scientific_scope'],core.SCI_SCOPE)
  with self.assertRaises(ValueError):self.coord.reserve_application(self.spec)
 def test_04_original_real_flock_excludes_second_controller(self):
  with self.coord.unique_controller():
   with self.assertRaisesRegex(ValueError,'already active'):
    with self.coord.unique_controller():pass
  self.assertEqual(self.coord.snapshot()['controller']['state'],'STOPPED')
 def test_05_actual_start_fakePopen_and_witness(self):
  self.start();s=self.coord.snapshot();self.assertEqual(s['actual_starts'],51)
  self.assertTrue(s[core.FIELD]['start_witness'])
  self.assertEqual(s['attempts'][-1]['process'],self.fake_identity)
 def test_06_coordinated_refund_rejected_by_actual_snapshot(self):
  self.start();d=self.read();a=d[c.FIELD]['attempts'][-1]
  a.update(state='CANCELLED_BEFORE_START',actual_start=False);d[c.FIELD]['actual_starts']=50
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaisesRegex(ValueError,'witness|refund'):self.coord.snapshot()
 def test_07_actual_spawn_failure_consumes_scope(self):
  a=self.reserve();directory=Path(a['result_directory']);directory.mkdir()
  (directory/'accel-sim.out').write_bytes(self.binary.read_bytes())
  def fail(*args,**kwargs):raise OSError('SYNTHETIC failed spawn')
  with self.coord.unique_controller():
   self.assertIsNone(self.coord.start_application(a['attempt_id'],[str(directory/'accel-sim.out')],directory,{},io.BytesIO(),fail))
  s=self.coord.snapshot();self.assertEqual(s['actual_starts'],50)
  self.assertEqual(s['attempts'][-1]['state'],'FAILED_SPAWN')
  self.assertIsNone(s[core.FIELD]['start_witness'])
  with self.assertRaises(ValueError):self.coord.reserve_application(self.spec)
 def test_08_C_A_leases_not_scope_conflict(self):
  for role in ('C','A'):
   d=self.read();d['resource_leases']['SYNTHETIC_'+role]={'experiment_id':c.CAMPAIGN,
     'owner':'mechanism_'+role,'role':role,'status':'RUNNING'}
   f.write(self.root/'RUN_REGISTRY.json',d)
  self.assertTrue(self.coord.adopt_detach_observer_batch()['changed'])
 def test_09_E_lease_and_own_run_block_adoption(self):
  d=self.read();d['resource_leases']['SYNTHETIC_E']={'experiment_id':c.CAMPAIGN,
   'owner':'mechanism_E','role':'E','status':'RUNNING'}
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaisesRegex(ValueError,'active'):self.coord.adopt_detach_observer_batch()
 def test_10_real_resource_gate_rejects_5plus2_space(self):
  self.ready()
  with patch.object(c,'local_resources',return_value={'available_memory_bytes':220*c.GIB,
      'disk_free_bytes':6*c.GIB,'share_disk_free_bytes':44*c.GIB}):
   with self.assertRaises(ValueError):self.coord.reserve_application(self.spec)
  self.assertEqual(len(self.coord.snapshot()['attempts']),50)
 def test_11_legacy_batches_and_sources_preserved(self):
  self.start();s=self.coord.snapshot()
  self.assertEqual(core.sha(s['attempts'][:50]),self.fx.seal['old50'])
  self.assertEqual(core.sha(s['workload_pipeline_batches']),self.fx.seal['old_workload'])
  self.assertEqual(s['final_source_identity'],self.fx.item['final_source_identity'])
  self.assertEqual(s['capacity_diagnostic_runtime'],self.fx.item['capacity_diagnostic_runtime'])
  self.assertEqual(pv.charged_bucket(s['attempts'][-1],s['reservations']),self.spec['budget_bucket'])
 def test_12_actual_runner_stub_rejects_observer_acceptance(self):
  with self.assertRaisesRegex(ValueError,'NOT_INDEPENDENTLY_ADAPTED'):
   runner.validate_terminal_summary({},self.spec,{'qualification':self.q},{})
 def test_13_queue_pairs_and_union_refused(self):
  self.ready();p=self.fx.root/'spec.json';ref=f.write(p,self.spec)
  dp.queue_guard(self.coord.snapshot(),{'specs':[ref],'pairs':[]},c.digest)
  for q in ({'specs':[ref,ref],'pairs':[]},{'specs':[ref],'pairs':[{}]}):
   with self.assertRaises(ValueError):dp.queue_guard(self.coord.snapshot(),q,c.digest)
 def test_14_actual_runkey_extra_binary_or_input_denied(self):
  self.ready()
  for field in ('binary_sha256','trace_content_sha256'):
   s=copy.deepcopy(self.spec);s['identity'][field]='0'*64;s['input_audit']['identity']=s['identity']
   with self.assertRaises(ValueError):self.coord.reserve_application(s)
 def test_15_old50_mutation_and_52_tail_denied(self):
  self.reserve();d=self.read();d[c.FIELD]['attempts'].append(copy.deepcopy(d[c.FIELD]['attempts'][-1]))
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaises(ValueError):self.coord.snapshot()
 def test_16_actual_native_terminal_receipt_boundary_fake_only(self):
  a,directory=self.start();(directory/'raw.log').write_text('SYNTHETIC_NOT_NATIVE_OUTPUT\n')
  self.fake_alive=False
  receipt={'attempt_id':a['attempt_id'],'run_key':a['run_key'],'identity':a['identity'],
    'status':'COMPLETE_VALID','raw_log_sha256':c.digest(directory/'raw.log'),'independent_acceptance':'PASS',
    'complete_input_verified':True,'validation':{'status':'PASS','synthetic_fixture':True},
    'detail':'SYNTHETIC coordinator boundary fixture; parser not run','scientific_scope':core.SCI_SCOPE,
    'qualification_id':self.spec['qualification_id'],'profile':'F','synthetic_fixture':True}
  native={'synthetic_fixture':True,'native_process':self.fake_identity,
    'guardian_process':{'pid':987654322,'start_ticks':987,'boot_id':'SYNTHETIC_BOOT_ID'},
    'exit_code':0,'wait_status':0,'stop_reason':None,'released_to_native':True,
    'binding':{'attempt_id':a['attempt_id'],'run_key':a['run_key'],'identity':a['identity']}}
  native_ref=f.write(directory/'NATIVE_EXIT.json',native)
  receipt.update(native_exit_evidence=native,native_exit_receipt_sha256=native_ref['sha256'])
  ref=f.write(directory/'run_status.json',receipt)
  self.coord.finish_application(a['attempt_id'],'COMPLETE_VALID',ref['path'])
  s=self.coord.snapshot();self.assertEqual(s['accepted_results'][a['attempt_id']]['scientific_scope'],core.SCI_SCOPE)
  self.assertEqual(s['accepted_pairs'],self.fx.item['accepted_pairs'])
  with self.assertRaisesRegex(ValueError,'cannot be S/F pair'):
   runner.accept_pair(self.coord,a['attempt_id'],a['attempt_id'],'SYNTHETIC_FORBIDDEN')
 def test_18_actual_finish_refuses_missing_durable_collector_evidence(self):
  a,directory=self.start();(directory/'raw.log').write_text('SYNTHETIC_NOT_NATIVE_OUTPUT\n')
  self.fake_alive=False
  receipt={'attempt_id':a['attempt_id'],'run_key':a['run_key'],'identity':a['identity'],
    'status':'COMPLETE_VALID','raw_log_sha256':c.digest(directory/'raw.log'),
    'independent_acceptance':'PASS','complete_input_verified':True,'validation':{'status':'PASS'},
    'detail':'SYNTHETIC intentionally missing durable collector evidence'}
  ref=f.write(directory/'run_status.json',receipt)
  with self.assertRaisesRegex(ValueError,'durable native exit receipt missing'):
   self.coord.finish_application(a['attempt_id'],'COMPLETE_VALID',ref['path'])
  self.assertNotIn(a['attempt_id'],self.coord.snapshot()['accepted_results'])

 def test_19_tail_deleted_but_canonical_run_retained_rejected(self):
  self.start();d=self.read();item=d[c.FIELD]
  item['attempts']=item['attempts'][:50]
  item['actual_starts']=50
  item[core.FIELD]['attempt_ids']=[]
  item[core.FIELD]['start_witness']=None
  self.assertTrue(dp.active(item)) # Pure item-level check cannot see retained canonical run.
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaisesRegex(ValueError,'canonical run/tail'):
   self.coord.snapshot()

 def test_20_refund_but_canonical_start_retained_rejected(self):
  self.start();d=self.read();item=d[c.FIELD];a=item['attempts'][-1]
  a.update(state='CANCELLED_BEFORE_START',actual_start=False)
  for key in ('process','started_unix','started_identity','immutable_started_marker'):a.pop(key,None)
  item[core.FIELD]['start_witness']=None;item['actual_starts']=50
  self.assertTrue(dp.active(item)) # All local witnesses removed, canonical run still proves start.
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaisesRegex(ValueError,'canonical started run'):
   self.coord.snapshot()

 def test_21_canonical_run_missing_but_tail_retained_rejected(self):
  a=self.reserve();d=self.read();d['runs'].pop(a['run_key'])
  f.write(self.root/'RUN_REGISTRY.json',d)
  with self.assertRaisesRegex(ValueError,'canonical run/tail'):
   self.coord.snapshot()

 def test_17_no_actual_central_or_source_mutation(self):
  self.start()
  current_live=f.LIVE.read_bytes()
  EXTERNAL_REGISTRY_CHANGE_OBSERVED.append(current_live!=f.LIVE_BYTES)
  actual_item=json.loads(current_live)[c.FIELD]
  self.assertEqual(core.sha(actual_item['attempts'][:50]),self.fx.seal['old50'])
  self.assertTrue(all(Path(x).is_relative_to(HERE) for x in WRITE_TARGETS))
  before=json.loads((HERE/'SOURCE_BASELINE.json').read_text())['original_files']
  for n,digest in before.items():self.assertEqual(core.file_sha(E/'util/ep_l2/mechanism_e'/n),digest)
  self.assertFalse(os.access(self.binary,os.X_OK))

if __name__=='__main__':
 result=unittest.main(verbosity=2,exit=False)
 report={'all_intercepted_writes_under_candidate':all(Path(x).is_relative_to(HERE) for x in WRITE_TARGETS),
  'intercepted_write_open_count':len(WRITE_TARGETS),'unique_write_targets':len(set(WRITE_TARGETS)),
  'external_peer_registry_update_observed':any(EXTERNAL_REGISTRY_CHANGE_OBSERVED),
  'actual_registry_mutations_by_candidate':0,'initial_registry_sha256':hashlib.sha256(f.LIVE_BYTES).hexdigest(),
  'final_registry_sha256':hashlib.sha256(f.LIVE.read_bytes()).hexdigest(),
  'limitations':'Write guard covers builtin/io/os writable opens; no native/subprocess executed. It is test isolation, not a systemwide security monitor.'}
 (HERE/'WRITE_GUARD_OBSERVATIONS.json').write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.result.wasSuccessful() else 1)

