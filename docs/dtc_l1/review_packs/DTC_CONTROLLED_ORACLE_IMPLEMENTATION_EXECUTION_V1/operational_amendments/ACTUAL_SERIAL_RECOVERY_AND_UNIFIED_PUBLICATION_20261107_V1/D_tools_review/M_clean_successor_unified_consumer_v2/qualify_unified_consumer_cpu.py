"""CPU-only mutation qualification. Never imports an operational module."""
import copy,hashlib,importlib.util,json,tempfile
from pathlib import Path
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/D_independent_review_v1/unified_consumer_publication_source_review_v1/M_clean_successor_unified_consumer_v2')
spec=importlib.util.spec_from_file_location('adapter',O/'oracle_unified_roots_consumer.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cfg=m.read(O/'UNIFIED_BINDINGS.fixed.json'); settings=m.read(cfg['science_settings']['path'])
matrix=m.read(cfg['fixed_matrix']['path']); expected={p['plan_id']:p for p in matrix['rows']if not p['initial_fixed8']}
tests=[]
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def ref(p):return {'path':str(p),'sha256':m.sha(p)}
with tempfile.TemporaryDirectory(prefix='cpu_metadata_',dir=O) as td:
 r=Path(td);control=r/'control';tools=r/'tools';control.mkdir();tools.mkdir()
 for n in ('main.py','guard.py','oracle_successor_engine.py'):
  (tools/n).write_text("raise AssertionError('CPU fixture operational module must never execute')\n")
 candidate=control/'candidate.json';put(candidate,{'CPU_ONLY':True})
 build=control/'BUILD_PROFILE.json';put(build,settings['expected_build_identity'])
 points=[dict(p,cohort='CPU_COHORT_'+str(i),request=m.REQUEST)for i,p in enumerate(expected.values())]
 mp=control/'MATRIX.fixed.json';put(mp,{'points':points})
 ep=control/'RESULT_ENGINE_PIN.json';put(ep,{'scientific_bundle':'CPU_ONLY_METADATA_NOT_ACCEPTED'})
 lease=control/'CLEAN_OWNER_PRIVATE_LEASE.json'
 L={'schema':'DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1','request':m.REQUEST,'budget':96,'old32_new_starts':0,
    'pid':99999991,'start_ticks':111,'authority_commit':m.AUTH,'guard_sha256':m.sha(tools/'guard.py'),
    'controller':ref(tools/'main.py'),'locks':[{'role':v}for v in ('governance','owner','qualification','shared')]}
 put(lease,L)
 P={'preparation_phase':'SCIENCE_FINAL_FROZEN','actual_execution_authorized':True,'authority_commit':m.AUTH,
    'request':m.REQUEST,'stage':'remaining24','expected_new_starts':96,'exact_input_count':24,'CH_budget':0,
    'execution_root':str(r),'parent_pid':L['pid'],'parent_start_ticks':111,'clean_owner_guard':ref(tools/'guard.py'),
    'clean_owner_lease':ref(lease),'parent_controller_path':str(tools/'main.py'),'parent_controller_sha256':m.sha(tools/'main.py'),
    'clean_operational_generation':{'kind':'SERIAL_LEGAL_DTC_MAIN_SUCCESSOR','old32_new_starts':0,'same_PID_exec_or_legacy_frame_required':False},
    'RESULT_ENGINE_PIN':ref(ep),'result_engine_pin':ref(ep),'build_profile_sha256':m.sha(build),
    'source_pins':[ref(tools/n)for n in ('main.py','guard.py','oracle_successor_engine.py')],
    'authorized_cohorts':[p['cohort']for p in points]}
 pp=control/'EXECUTION_PLAN.json';put(pp,P)
 R={'status':'PASS_NEW_PRIVATE_CPU_LAYOUT_SOURCE_RESOURCE_QUALIFICATION','root':str(r),'parent_pid':L['pid'],
    'parent_start_ticks':111,'source_scientific_projection_equal':True,'plan':ref(pp),'candidate':ref(candidate),
    'scientific_models_started':0,'science_registrations':0}
 rp=control/'CLEAN_PARENT_FINAL_BIND_CPU_QUALIFICATION.fixed.json';put(rp,R)
 C={'matrix_fixed_sha256':m.sha(mp),'expected_build_identity':settings['expected_build_identity'],
    'expected_plan_rows':expected,'final_bind_receipt_name':rp.name,'private_operational_engine_name':'oracle_successor_engine.py'}
 def pure(p=P,rr=R,l=L,b=None):return m.metadata_new_binding(r,p,rr,l,{'scientific_bundle':'CPU_ONLY'},settings['expected_build_identity'],b or settings['expected_build_identity'])
 good=pure();assert good['scientific_registration_permission_granted']is False and good['live_owner_or_lock_reverification_performed']is False
 tests.append({'name':'valid_new_serial_metadata_no_live_owner_or_acceptance_claim','pass':True})
 def bad(name,target,key,value):
  p,rr,l,b=copy.deepcopy(P),copy.deepcopy(R),copy.deepcopy(L),copy.deepcopy(settings['expected_build_identity'])
  obj={'plan':p,'receipt':rr,'lease':l,'build':b}[target];obj[key]=value
  try:pure(p,rr,l,b)
  except (ValueError,KeyError,TypeError):tests.append({'name':name,'pass':True});return
  raise AssertionError('not rejected '+name)
 mutations=[('draft','plan','preparation_phase','CPU_DRAFT'),('not_authorized','plan','actual_execution_authorized',False),
 ('wrong_authority','plan','authority_commit','x'),('wrong_request','plan','request','old'),('wrong_stage','plan','stage','initial8'),
 ('wrong_budget','plan','expected_new_starts',97),('wrong_inputs','plan','exact_input_count',25),('CH_forbidden','plan','CH_budget',1),
 ('foreign_root','plan','execution_root','/tmp/foreign'),('old_owner_not_successor','plan','parent_pid',1498278),
 ('old_helper_not_successor','plan','parent_pid',438646),('missing_start','plan','parent_start_ticks',None),
 ('receipt_not_pass','receipt','status','CPU_PREPARED'),('receipt_parent','receipt','parent_pid',8888),
 ('receipt_root','receipt','root','/tmp/other'),('projection_not_proven','receipt','source_scientific_projection_equal',False),
 ('lease_schema','lease','schema','old'),('lease_request','lease','request','old'),('lease_budget','lease','budget',95),
 ('old32_never_restart','lease','old32_new_starts',1),('lease_pid','lease','pid',77),('lease_start','lease','start_ticks',222),
 ('lease_guard','lease','guard_sha256','0'*64),('lease_controller','lease','controller',{'path':'wrong','sha256':'0'*64}),
 ('lease_roles','lease','locks',[{'role':'owner'}]),('generation_old_frame','plan','clean_operational_generation',{'kind':'SERIAL_LEGAL_DTC_MAIN_SUCCESSOR','old32_new_starts':0,'same_PID_exec_or_legacy_frame_required':True}),
 ('ambiguous_engine','plan','result_engine_pin',{'path':'x','sha256':'x'})]
 for x in mutations:bad(*x)
 for k in settings['expected_build_identity']:bad('fixed_build_'+k,'build',k,'changed')
 assert m.inspect_new_root(r,C)['ready']is True
 tests.append({'name':'full_filesystem_new_private_binding_without_operational_import','pass':True})
 def file_bad(name,path,value):
  before=path.read_bytes();receipt_before=rp.read_bytes();put(path,value)
  if path==pp:put(rp,dict(R,plan=ref(pp)))
  try:
   q=m.inspect_new_root(r,C);assert not q.get('ready'),name
   tests.append({'name':name,'pass':True,'observed':q.get('reason')})
  finally:path.write_bytes(before);rp.write_bytes(receipt_before)
 file_bad('receipt_plan_sha_mismatch',rp,dict(R,plan={'path':str(pp),'sha256':'0'*64}))
 file_bad('receipt_candidate_outside_root',rp,dict(R,candidate={'path':'/etc/hosts','sha256':m.sha('/etc/hosts')}))
 file_bad('plan_cohort_scope_change',pp,dict(P,authorized_cohorts=['bad']))
 file_bad('missing_source_engine_pin',pp,dict(P,source_pins=P['source_pins'][:2]))
 file_bad('mutable_guard_bytes',tools/'guard.py',{'changed':True})
 file_bad('matrix_changed',mp,{'points':points[:-1]})
 file_bad('build_changed',build,{'changed':True})
 file_bad('CPU_manifest_not_scientific_authority',pp,dict(P,preparation_phase='CPU_DRAFT',actual_execution_authorized=False))
 before=rp.read_bytes();rp.unlink()
 assert not m.inspect_new_root(r,C).get('ready');rp.write_bytes(before)
 tests.append({'name':'missing_final_receipt_HOLD','pass':True})
 # A final engineering receipt plus a fabricated PASS does not supply strict,
 # native lifecycle, archive/restore or legal identity evidence.
 analysis=r/'analysis';analysis.mkdir()
 for index,state in enumerate((m.PASS,'NEGATIVE_CPU_ONLY','HOLD_CPU_ONLY')):
  p=points[index];put(analysis/(p['cohort']+'.RESULT.json'),{
   'state':state,'uuid':'CPU_NOT_A_SCIENTIFIC_UUID_'+str(index),'cycles':123,
   'program':p['program'],'input_digest':p['input_digest'],'plan_id':p['plan_id'],
   'oracle_mode':p['mode'],'proof':settings['expected_build_identity']})
 fakecfg=copy.deepcopy(cfg);fakecfg['remaining24_private']['root']=str(r)
 fakecfg['remaining24_private']['matrix_fixed_sha256']=m.sha(mp)
 bp=r/'CPU_BINDINGS.json';put(bp,fakecfg)
 fake=m.snapshot_once(bp,O/'synthetic_CPU_receipt_not_acceptance_projection',analyze=False)
 fake_rows={x['plan_id']:x for x in fake['rows']}
 assert fake_rows[points[0]['plan_id']]['classification']=='HOLD'
 assert fake_rows[points[0]['plan_id']]['cycles']is None
 tests.append({'name':'fabricated_PASS_plus_CPU_receipt_never_accepted_without_real_strict_archive_identity','pass':True,
 'observed':fake_rows[points[0]['plan_id']]['validation_error']})
 for p in points[1:3]:
  row=fake_rows[p['plan_id']];assert row['classification']=='negative_or_hold'and row['cycles']is None and row['observed_cycles_not_accepted']==123
 tests.append({'name':'negative_HOLD_observed_cycles_retained_but_excluded_from_accepted','pass':True})
 assert sum(x['classification']=='accepted'for x in fake['rows'])==32 and len(fake['rows'])==128
 tests.append({'name':'synthetic_engineering_receipt_cannot_expand_32_accepted_to_new96','pass':True})
 # Guard all ordinary Path reads of process/raw state during a real frozen-data refresh.
 original_open=Path.open;prohibited=[]
 def guarded_open(path,*args,**kwargs):
  s=str(path)
  if s.startswith('/proc/')or 'raw.log' in s or 'stdout.log' in s:
   prohibited.append(s);raise AssertionError('forbidden process/raw read '+s)
  return original_open(path,*args,**kwargs)
 Path.open=guarded_open
 try:
  actual=m.snapshot_once(O/'UNIFIED_BINDINGS.fixed.json',O/'qualified_actual_projection_v2')
 finally:Path.open=original_open
 old=m.read(cfg['initial8_data_only']['snapshot']['path'])
 newaccepted={r['plan_id']:(r['uuid'],r['result_sha256'],r['cycles'])for r in actual['rows']if r.get('classification')=='accepted'}
 oldaccepted={r['plan_id']:(r['uuid'],r['result_sha256'],r['cycles'])for r in old['rows']if r.get('classification')=='accepted'}
 assert all(newaccepted.get(k)==v for k,v in oldaccepted.items())and not prohibited
 assert len(actual['rows'])==128 and len(oldaccepted)==32
 tests.append({'name':'actual_frozen32_UUID_resultSHA_cycles_retained_no_process_or_old_raw_reads','pass':True})
 report={'schema':'DTC_UNIFIED_READONLY_CPU_QUALIFICATION_V1','status':'PASS','cases':len(tests),'tests':tests,
 'operational_modules_imported':0,'models_started':0,'registrations':0,'owner_or_tracer_actions':0,
 'archive_or_restore_writes':0,'actual_projection_statuses':actual['status_counts'],
 'actual_new_root_binding':actual['explicit_stage_bindings']['remaining24'],
 'CPU_fixture_not_scientific_acceptance':True}
 put(O/'CPU_QUALIFICATION.fixed.json',report)
 print(json.dumps({'status':'PASS','cases':len(tests),'actual_statuses':actual['status_counts']}))
