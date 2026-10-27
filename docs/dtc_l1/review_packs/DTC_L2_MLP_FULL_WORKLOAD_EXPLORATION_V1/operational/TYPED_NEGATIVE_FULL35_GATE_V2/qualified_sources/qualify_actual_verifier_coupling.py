"""Actual frozen verifier return-schema coupling, owned native CPU transaction.
No production bundle, original scan result, authority, or model is changed.
"""
import contextlib,copy,hashlib,importlib.util,json,pathlib,sys,types
from unittest.mock import patch
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import typed_analysis_view as view
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
E=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E')
SCAN=E.parent/'scan_m16_diagnosis_v1/terminal_impl_v1'
SOURCE=SCAN/'scan_m16_engineering_negative_v1.py'
DRIVER=SCAN/'qualify_scan_m16_engineering_negative_v1.py'
PIN='08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
assert sha(SOURCE)==PIN
assert sha(DRIVER)=='b658c3d42c6e1fd2e42817134fa568342e44dff3b81aef00bfe33862b6b5ed07'
qual=load('actual_scan_qualification_fixture',DRIVER)
f=qual.Qualification('test_full_transaction_and_pinned_verifier_idempotence');f.setUp();checks=[]
try:
 with contextlib.ExitStack()as stack:
  pin,_=f.transaction_fixture(stack);m=f.m
  scope=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json')
  point=next(p for p in scope['points']if p['cohort']==m.C);digest=point['input_digest']
  s=read(R/'control/specs'/(m.C+'.json'))
  identity=dict(input_digest=digest,cell='DH',target_profile='M16',trace_entry=s['native_simulator_argv'][2],
   core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],configs=s['configs'],expected_options_sha256='SYNTHETIC_CONTEXT_ONLY')
  stack.enter_context(patch.object(m,'scientific_identity',return_value=identity))
  actual=m.run_execute(pin)
  assert type(actual['certificate'])is str
  consumer=load('actual_view_coupling_consumer',R/'tools/l2_results.py');records={}
  for p in scope['points']:
   records[p['cohort']]=dict(state=consumer.PASS,cycles=10**9,uuid='SYNTHETIC_CPU_ONLY',proof=dict(performance_accepted=True,cycles=10**9),archive={'SYNTHETIC_CPU_ONLY':True})
  records[m.C]=dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cycles=None,uuid=m.U)
  raw=consumer.summarize(scope,records);before=copy.deepcopy(raw)
  binding=dict(cohort=m.C,uuid=m.U,input_digest=digest,cell='DH',profile='M16',bundle_path=str(P(actual['certificate']).parent),certificate_sha256=actual['certificate_sha256'])
  # Reuse the SAME actual verifier instance with its owned CPU context fixtures.
  # verify_bundle body, real archive validation, and real native restore remain.
  with patch.object(view,'private_module',return_value=m):
   projected,proofs=view.project(raw,[binding],SOURCE,pin)
   row=projected['table'][digest]['M16']['DH']
   assert row['state']==view.TYPED and row['cycles']is None and not row['accepted']
   assert raw==before and row['typed_engineering_original_row']==raw['table'][digest]['M16']['DH']
   checks.append('actual_frozen_verify_bundle_PATH_return_full_archive_restore_consumed_correctly')
   paths=dict(base=str(R/'tools/l2_adaptive.py'),supplement=str(E/'boundary_validation_v2/l2_boundary_validation.py'))
   pins={k:sha(p)for k,p in paths.items()};guard_calls=[]
   def existing_final_guard(result):
    guard_calls.append(result['typed_engineering_terminal_policy']['schema'])
    result.update(registry_journal_status=dict(safe_for_scientific_completion=False,requires_engineering_review=True),
     scientific_stage_complete=False,adoption_ready=False,FINAL_GUARD_SENTINEL=True)
    return result
   result=view.recommend_from_bundles(raw,scope,history,paths,pins,[binding],SOURCE,pin,existing_final_guard)
   assert len(guard_calls)==1 and result['FINAL_GUARD_SENTINEL']and not result['scientific_stage_complete']
   assert result['verified_typed_engineering_negatives'][0]['cohort']==m.C and raw==before
   checks.append('actual_schema_project_recommend_preserves_existing_finalguard_last_and_raw_summary')
  # Deliberately forged post-verifier paths/pins rejected by independent reader.
  for forged in (dict(actual,certificate=str(P(actual['certificate']).with_name('WRONG.json'))),dict(actual,certificate_sha256='WRONG')):
   try:view.load_verified_certificate(forged,binding,m)
   except AssertionError:pass
   else:raise AssertionError('forged certificate path/pin accepted')
  checks.append('certificate_exact_basename_parent_and_SHA_independently_checked')
  cert=P(actual['certificate']);alias=cert.parent/'CPU_ONLY_SYMLINK.json';alias.symlink_to(cert)
  try:view.load_verified_certificate(dict(actual,certificate=str(alias)),dict(binding,bundle_path=str(alias.parent)),m)
  except AssertionError:pass
  else:raise AssertionError('symlink certificate accepted')
  alias.unlink();checks.append('symlink_or_nonexact_certificate_path_rejected')
finally:f.tearDown()
output=dict(status='PASS',count=len(checks),checks=checks,verifier_path=str(SOURCE),verifier_sha256=PIN,
 verifier_fixture_driver_sha256=sha(DRIVER),view_source_sha256=sha(HERE/'typed_analysis_view.py'),driver_sha256=sha(__file__),
 qualification_scope='actual frozen verifier full execute->archive->native restore->verify CPU transaction; owned mock context and proc only',
 actual_production_scan_bundle_verified=False,production_mutations=0,models_started=0,signals_sent=0,registry_grants=0)
(HERE/'ACTUAL_VERIFIER_COUPLING_CPU_QUALIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
