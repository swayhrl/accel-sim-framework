"""Bounded private CPU scope tests. No native operation or model process is invoked."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,sys,tempfile,time
C=Path(__file__).resolve().parent; R=C/'runtime';J=C.parents[2];E=J/'execution_v2_20261103_v1';N=J/'research/implementation_performance_v2_20261029_v1'
sys.path.insert(0,str(R))
import ep_perf_native_wv_modes_draft as eng
import mode_contract as mc
import ep_perf_frontend as front
sp=importlib.util.spec_from_file_location('binder',C/'bind_stencil_specs.py');binder=importlib.util.module_from_spec(sp);sp.loader.exec_module(binder)
def ref(p):p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x));return ref(p)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
rows=[]
def check(label,func,reject=False):
 try:
  out=func()
  if reject:raise AssertionError('invalid candidate accepted')
  rows.append({'label':label,'status':'PASS'})
 except (RuntimeError,ValueError,AssertionError) as ex:
  if not reject:raise
  if str(ex)=='invalid candidate accepted':raise
  rows.append({'label':label,'status':'PASS','rejection':str(ex)})
old_hashes={str(p):ref(p)['sha256']for p in (E/'runtime_w').rglob('*')if p.is_file()}
start=time.monotonic()
with tempfile.TemporaryDirectory(prefix='CPU_PRIVATE_',dir=C)as td:
 T=Path(td);eng.ROOT=T;eng.authority=lambda:(reg,{})
 user=T/'control/USER_REQUEST.txt';user.parent.mkdir();user.write_text('TEST_ONLY NOT USER AUTHORIZATION')
 auth=save(T/'auth.json',{'goal':eng.GOAL,'user_request_ref':ref(user),'TEST_ONLY':True,'application_permission':False})
 reg=json.loads((eng.NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text())
 q={'budget':2,'remaining':2,'consumed':{},'admitted_specs':{},'runtime_versions':{},'authorization_ref':auth}
 reg['registered_future_requests'][eng.GOAL]=q
 hostq=json.loads((N/'main/MAIN_SOURCE78_W_ONLY_HOST_QUALIFICATION_V2.json').read_text());hostq['modules']=[ref(p)for p in R.rglob('*')if p.is_file()];hostq['TEST_ONLY']=True;hostq['approved_by']='TEST_ONLY_NOT_MAIN';hostqref=save(T/'test_hostq.json',hostq)
 binder.MODULES=R
 originals=[json.loads((N/'main/wv_engineering_bound_specs'/n).read_text())for n in ['stencil_W_ONLY.json','stencil_WV_ZERO_RO.json']]
 specs=[]
 for original in originals:
  identity_before=digest(original)
  eligibility=save(T/(original['mode']+'_test_eligibility.json'),dict(status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',source_identity=original['source_identity'],input_identity_sha256=original['input_identity_sha256'],modes_qualified=['W_ONLY','WV_ZERO_RO'],ordered_kernel_identity=json.loads(Path(original['input_binding_ref']['path']).read_text())['ordered_kernel_identity'],TEST_ONLY=True,application_permission=False))
  bs=dict(host_qualification_ref=hostqref,source_qualification_ref=ref(E/'control/W_SOURCE_QUALIFICATION.json'),eligibility_ref=eligibility,resource_module_ref=ref(E/'tools/resources_wv.py'),resource_policy_ref=ref(E/'control/RESOURCE_POLICY.json'),authorization_ref=auth,native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt'))
  s=binder.bind(original,bs);specs.append(s)
  check(s['mode']+'_binder_original_immutable',lambda:eng.need(identity_before==digest(original),'binder mutated input'))
  check(s['mode']+'_all_scientific_fields_unchanged',lambda:eng.need(all(s[k]==original[k]for k in ['source_identity','expected_effective_options','input_binding_ref','ordered_configs','observer_env','geometry','limits','trace_entry','mode','T','M','mode_cpu_qualification_ref','matched_S_anchor_qualification_ref']),'scientific field changed'))
  p=T/'cases'/s['cohort']/'control/FROZEN_SPEC.json';save(p,s);q['admitted_specs'][s['cohort']]=ref(p)['sha256'];q['runtime_versions'][s['host_engine_ref']['sha256']]=dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref'])
  check(s['mode']+'_formal_static_real_Source78_anchor_CPU',lambda s=s:eng.formal_mode_contract(s))
  check(s['mode']+'_cross_cohort_mode_rejected',lambda s=s:eng.authorized_scope_mode(dict(s,mode='WV_ZERO_RO'if s['mode']=='W_ONLY'else'W_ONLY')),True)
  for key in ['T','M']:
   check(s['mode']+'_'+key+'_true_rejected',lambda s=s,key=key:eng.authorized_scope_mode(dict(s,**{key:True})),True)
 for s in specs:check(s['mode']+'_full_spec_for_private_registry',lambda s=s:eng.spec_for(s['cohort']))
 for case in ['EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','EP_PERF_V2_PROPOSED_FASTWALSHTRANSFORM_FC3A9062_W_ONLY','EP_PERF_V2_PROPOSED_SCAN_00_W_ONLY','EP_PERF_T3_CONV16X8_A_F_MINUS_T_OFF_V1']:
  check(case+'_scope_rejected',lambda case=case:eng.spec_path(case),True)
 # Native sole-entry remains mandatory; no frontend action reaches model machinery.
 oldenv=os.environ.pop('EP_FULL_PERF_NATIVE_ENTRY',None)
 check('frontend_without_native_guard_rejected',lambda:front.main(['experiment','prepare',specs[0]['cohort'],'--project','EP_L2']),True)
 os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
 check('frontend_foreign_cohort_rejected_before_authority',lambda:front.main(['experiment','prepare','EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY','--project','EP_L2']),True)
 check('frontend_unknown_operation_rejected',lambda:front.main(['experiment','arbitrary',specs[0]['cohort'],'--project','EP_L2']),True)
 if oldenv is None:os.environ.pop('EP_FULL_PERF_NATIVE_ENTRY',None)
 else:os.environ['EP_FULL_PERF_NATIVE_ENTRY']=oldenv
 def function_text(text,name):
  part=text.split('def '+name+'(',1)[1];return part.split('\ndef ',1)[0]
 old=(E/'runtime_w/ep_perf_native_wv_modes_draft.py').read_text();new=(R/'ep_perf_native_wv_modes_draft.py').read_text()
 for name in ['prepare','run','resource_gate']:
  if 'def '+name+'('in old:check(name+'_scoped_native_and_resource_logic_byte_preserved',lambda name=name:eng.need(function_text(old,name)==function_text(new,name),'function drift'))
 for p in (E/'runtime_w').rglob('*'):
  if p.is_file()and p.name not in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','ep_perf_frontend.py','ep_perf_archive.py']:
   check(str(p.relative_to(E/'runtime_w'))+'_frozen_byte_preservation',lambda p=p:eng.need(p.read_bytes()==(R/p.relative_to(E/'runtime_w')).read_bytes(),'frozen dependency drift'))
 assert old_hashes=={str(p):ref(p)['sha256']for p in(E/'runtime_w').rglob('*')if p.is_file()}
receipt={'schema':'EP_STENCIL_WV_INCREMENTAL_PRIVATE_CPU_SCOPE_CONTROLS_V1','status':'PASS_PRIVATE_CPU_ONLY_NOT_APPLICATION_QUALIFICATION','controls':rows,'elapsed_seconds':time.monotonic()-start,'model_starts':0,'native_operations':0,'real_authority_writes':0,'old_runtime_files_unchanged':True,'TEST_ONLY_approvals_never_adopt_as_Main':True,'CPU_mode_and_S_anchor_evidence':'Actual existing Main CPU and accepted closed Stencil S references read; new relocated HostQ and private registry are TEST_ONLY fixtures, Main must issue real relocated HostQ'}
(C/'CPU_INCREMENTAL_CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'controls':len(rows),'elapsed_seconds':receipt['elapsed_seconds']}))
