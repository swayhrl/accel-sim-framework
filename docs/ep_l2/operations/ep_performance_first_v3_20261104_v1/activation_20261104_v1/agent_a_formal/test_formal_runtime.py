from pathlib import Path as P
import sys,json,hashlib,copy,os
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');F=V/'activation_20261104_v1/agent_a_formal';R=V/'activation_20261104_v1/runtimes/midtag';A=V/'agent_a_mid_tag';DATA=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag')
sys.path.insert(0,str(R));import ep_perf_common_v2 as c,mode_contract as m,ep_perf_native_wv_modes_draft as e,ep_perf_frontend as front,mode_aware_terminal as parser
def put(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return c.ref(p)
fixture=F/'host_fixture_root';(fixture/'control').mkdir(parents=True,exist_ok=True)
user=fixture/'control/USER_REQUEST.txt';user.write_bytes((DATA/'control/USER_REQUEST.txt').read_bytes())
auth=c.read(DATA/'control/USER_AUTHORIZATION.json');auth['user_request_ref']=c.ref(user);auth['fixture_only']=True;authref=put(fixture/'control/AUTH_FIXTURE.json',auth)
# These are explicitly owned synthetic Main-review fixtures, never submitted as Main reviews.
mode=c.read(F/'review_drafts/MAIN_MODE_CPU_QUALIFICATION_DRAFT.json');mode.update(status=mode['required_final_status'],approved_by='EP-MAIN',fixture_only=True)
mode_ref=put(fixture/'control/MODE_CPU_REVIEW_FIXTURE.json',mode)
host=c.read(F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json');host.update(status=host['required_final_status'],approved_by='EP-MAIN',fixture_only=True)
host_ref=put(fixture/'control/HOST_REVIEW_FIXTURE.json',host)
registry,epoch=c.authority();reg=copy.deepcopy(registry);q=dict(budget=8,remaining=8,consumed={},admitted_specs={},authorization_ref=authref,runtime_versions={});reg['registered_future_requests'][c.GOAL]=q
cases={}
for p in sorted((F/'spec_candidates').glob('*.json')):
 s=c.read(p);old=c.read(A/'spec_candidates'/p.name);assert s['expected_effective_options']==old['expected_effective_options'] and s['source_identity']==old['source_identity'] and s['observer_env']==old['observer_env']and s['input_identity_sha256']==old['input_identity_sha256']
 assert s['ordered_configs'][:-1]==old['ordered_configs'][:-1];assert c.sha(s['ordered_configs'][-1]['path'])==c.sha(old['ordered_configs'][-1]['path'])
 s.update(host_qualification_ref=host_ref,mode_cpu_qualification_ref=mode_ref,Main_scientific_launch_authorization=authref)
 path=fixture/'cases'/s['cohort']/'control/FROZEN_SPEC.json';put(path,s);q['admitted_specs'][s['cohort']]=c.sha(path);q['runtime_versions'][s['host_engine_ref']['sha256']]=dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']);cases[s['cohort']]=s
e.ROOT=fixture;e.authority=lambda:(copy.deepcopy(reg),copy.deepcopy(epoch));front.ROOT=fixture;front.authority=e.authority
checks=[]
def check(name,fn,positive=True):
 try:r=fn();passed=positive;detail=r if isinstance(r,(dict,list,str,bool,int,type(None)))else str(type(r))
 except Exception as err:passed=not positive;detail=type(err).__name__+': '+str(err)
 checks.append(dict(name=name,PASS=passed,positive=positive,detail=detail));assert passed,(name,detail)
for case,s in cases.items():
 check('FORMAL_SPEC_VALIDATED_'+case,lambda case=case:e.spec_for(case,require_release=False)['cohort'])
 check('STATIC_MODE_'+case,lambda s=s:m.validate_static(s))
 if s['mode']=='S':check('MATCHED_S_WV_'+case,lambda s=s:m.validate_fair_pair(s,cases[s['same_background_peer_cohort']]))
 if '_GEMM_'in case:check('GEMM_HELD_UNTIL_FWT_FOUR_ARCHIVED_'+case,lambda case=case:e.spec_for(case),False)
 for label,mutate in [
 ('foreign_cohort',lambda d:d.update(cohort='EP_PERF_FOREIGN')),
 ('Source',lambda d:d['source_identity'].update(binary_sha256='0'*64)),
 ('clock',lambda d:d['expected_effective_options'].update({'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:1275.0'})),
 ('FRFCFS',lambda d:d['expected_effective_options'].update({'-gpgpu_frfcfs_dram_sched_queue_size':'256'})),
 ('Tag',lambda d:d['expected_effective_options'].update({'-gpgpu_cache:dl2':'S:64:128:16,L:B:m:L:P,A:128:1,128:0,32'})),
 ('RO',lambda d:d.update(M=True)),
 ('ROcertificate',lambda d:d.update(ro_qualification_ref={'path':'fake','sha256':'f'*64})),
 ('observer',lambda d:d['expected_effective_options'].update({'-gpgpu_ep_l2_b0_stats':'0'})),
 ('Payload',lambda d:d['expected_effective_options'].update({'-gpgpu_ep_l2_wbuf_entries':'32'})),
 ('input',lambda d:d.update(input_identity_sha256='0'*64)),
 ('missing282',lambda d:d['expected_effective_options'].pop('-icnt_flit_size'))]:
  bad=copy.deepcopy(s);mutate(bad);check('DENY_'+label+'_'+case,lambda bad=bad:m.validate_static(bad),False)
 bad=copy.deepcopy(s);bad['host_qualification_ref']=c.ref(F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json');check('PRODUCER_HOST_REVIEW_NOT_MAIN_'+case,lambda bad=bad:m.validate_static(bad),False)
 bad=copy.deepcopy(s);bad['mode_cpu_qualification_ref']=c.ref(F/'review_drafts/MAIN_MODE_CPU_QUALIFICATION_DRAFT.json');check('PRODUCER_CPU_REVIEW_NOT_MAIN_'+case,lambda bad=bad:m.validate_static(bad),False)
check('FROZEN_NUMERIC_BODY_AND_SUFFIX',lambda:parser.numeric_math()[1])
os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
for case in cases:check('NO_INSTALLED_ROUTE_NO_CONSUME_'+case,lambda case=case:e.run_native(case),False)
for args in [['experiment','run-native','EP_PERF_FOREIGN','--project','EP_L2'],['experiment','retry',next(iter(cases)),'--project','EP_L2'],['experiment','prepare',next(iter(cases)),'--project','DTC_L1']]:check('NATIVE_FRONTEND_NEGATIVE_'+str(args),lambda args=args:front.main(args),False)
# Authorization negative checks mutate in-memory q only; no real authority changes.
oldauth=q['authorization_ref']
auth_bad=copy.deepcopy(auth);auth_bad['approved_launches']=9;q['authorization_ref']=put(fixture/'control/BAD_AUTH9.json',auth_bad)
check('BAD_NINE_START_AUTH_DENIED',lambda:e.spec_for(next(iter(cases)),False),False);q['authorization_ref']=oldauth
old=next(iter(cases));saved=q['admitted_specs'][old];q['admitted_specs'][old]='0'*64;check('REGISTERED_SPEC_SHA_DRIFT_DENIED',lambda:e.spec_for(old,False),False);q['admitted_specs'][old]=saved
check('REAL_REGISTRY_UNCHANGED',lambda:c.authority()[0]==registry)
receipt=dict(schema='EP_PFV3_MIDTAG_FORMAL_DRY_HOST_QUALIFICATION_V1',status='PRODUCER_FORMAL_HOST_PASS_PENDING_MAIN_REVIEW',checks=checks,total_checks=len(checks),PASS_count=sum(x['PASS']for x in checks),request_id=c.GOAL,actual_approved_auth_ref=c.ref(DATA/'control/USER_AUTHORIZATION.json'),immutable_base_bundle_ref=c.ref(A/'BUNDLE_MANIFEST.json'),scientific282_Source_input_ELF_unchanged=True,CPU_reexecuted=False,app_models_started=0,models_forked=0,real_registry_writes=0,global_native_writes=0,synthetic_Main_review_fixture_only=True,review_drafts_are_rejected=True,guard_module_ref=e.NATIVE_ROUTE_GUARD_REF,application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON')
put(F/'FORMAL_DRY_HOST_RECEIPT.json',receipt);print(json.dumps(dict(status=receipt['status'],checks=len(checks),new_models=0)))

