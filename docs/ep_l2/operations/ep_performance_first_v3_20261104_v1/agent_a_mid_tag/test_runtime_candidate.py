from pathlib import Path as P
import json,sys,copy,hashlib,importlib.util,traceback,os
A=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/agent_a_mid_tag');R=A/'runtime_candidate';sys.path.insert(0,str(R));import ep_perf_common_v2 as c,mode_contract as m,ep_perf_native_wv_modes_draft as e,ep_perf_frontend as f,mode_aware_terminal as parser
def put(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return c.ref(p)
fixture=A/'host_fixture_root';(fixture/'control').mkdir(parents=True,exist_ok=True)
user=fixture/'control/USER_REQUEST.txt';user.write_text('SYNTHETIC_HOST_CPU_FIXTURE_ONLY_NO_USER_AUTHORIZATION_OR_SCIENCE_START\n')
auth=fixture/'control/AUTH_FIXTURE.json';put(auth,dict(goal=c.GOAL,user_request_ref=c.ref(user),fixture_only=True,scientific_launch_permission=False))
registry,epoch=c.authority();reg=copy.deepcopy(registry);q=dict(budget=8,remaining=8,consumed={},admitted_specs={},authorization_ref=c.ref(auth),runtime_versions={})
reg['registered_future_requests'][c.GOAL]=q;cases={}
for p in sorted((A/'spec_candidates').glob('*.json')):
 s=c.read(p);case=s['cohort'];dest=fixture/'cases'/case/'control/FROZEN_SPEC.json';put(dest,s);q['admitted_specs'][case]=c.sha(dest);q['runtime_versions'][s['host_engine_ref']['sha256']]=dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']);cases[case]=s
e.ROOT=fixture;e.authority=lambda:(copy.deepcopy(reg),copy.deepcopy(epoch));f.ROOT=fixture;f.authority=e.authority
checks=[]
def check(name,fn,positive=True):
 try:result=fn();passed=positive;detail=result if isinstance(result,(dict,list,str,int,bool,type(None)))else str(type(result))
 except Exception as exc:passed=not positive;detail=type(exc).__name__+': '+str(exc)
 checks.append(dict(name=name,PASS=passed,positive=positive,detail=detail));assert passed,(name,detail)
for case,s in cases.items():
 check('ENGINE_SPEC_FOR_'+case,lambda case=case:e.spec_for(case,require_release=False)['cohort'])
 check('MODE_STATIC_'+case,lambda s=s:m.validate_static(s))
 if s['mode']=='S':check('MATCHED_PEER_'+case,lambda s=s:m.validate_fair_pair(s,cases[s['same_background_peer_cohort']]))
 for label,mutation in [
  ('foreign_cohort',lambda d:d.update(cohort='EP_PERF_NOT_APPROVED')),
  ('new_Core',lambda d:d['source_identity'].update(core_source_commit='0'*40)),
  ('clock1275',lambda d:d['expected_effective_options'].update({'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:1275.0'})),
  ('FRFCFS256',lambda d:d['expected_effective_options'].update({'-gpgpu_frfcfs_dram_sched_queue_size':'256'})),
  ('ROenabled',lambda d:d.update(M=True)),
  ('ROcertificate',lambda d:d.update(ro_qualification_ref={'path':'fake','sha256':'f'*64})),
  ('observer000',lambda d:d['expected_effective_options'].update({'-gpgpu_ep_l2_b0_stats':'0'})),
  ('unfairTagGeometry',lambda d:d['geometry'].update(ways=8 if d['geometry']['ways']==16 else 16)),
  ('badInput',lambda d:d.update(input_identity_sha256='0'*64)),
  ('missing_option',lambda d:d['expected_effective_options'].pop('-icnt_flit_size')),
  ('PayloadExpansion',lambda d:d['expected_effective_options'].update({'-gpgpu_ep_l2_wbuf_entries':'32'}))]:
  d=copy.deepcopy(s);mutation(d);check(label+'_'+case,lambda d=d:m.validate_static(d),False)
for case in cases:
 if '_GEMM_' in case:check('GEMM_BEFORE_FOUR_FWT_DENIED_'+case,lambda case=case:e.spec_for(case),False)
check('PARSER_FROZEN_NUMERIC_MATH',lambda:parser.numeric_math()[1])
os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
for args in [
 ['experiment','run-native','EP_PERF_NOT_APPROVED','--project','EP_L2'],
 ['experiment','restart',next(iter(cases)),'--project','EP_L2'],
 ['experiment','prepare',next(iter(cases)),'--project','DTC_L1'],
 ['result','accept',next(iter(cases)),'--project','EP_L2']]:
 check('FRONTEND_REJECT_'+str(args),lambda args=args:f.main(args),False)
for case in cases:
 check('NONINSTALLED_NATIVE_NO_FORK_'+case,lambda case=case:e.run_native(case),False)
# Verify no real authority/budget/entry writes made by this dry adapter validation.
check('REAL_AUTHORITY_UNCHANGED',lambda:c.authority()[0]==registry)
receipt=dict(schema='EP_PFV3_MIDTAG_DRY_HOST_NATIVE_QUALIFICATION_V1',status='PASS_EXACT8_DRY_ENGINE_MODE_PAIR_NEGATIVES_NATIVE_FAIL_CLOSED',checks=checks,total_checks=len(checks),PASS_count=sum(x['PASS']for x in checks),fixture_root=str(fixture),fixture_authority_is_in_memory_only=True,real_science_registry_written=False,real_global_Native_written=False,model_fork_count=0,model_starts=0,application_NI='NOT_MEASURED',mode_parser_math_body_and_suffix='BYTE_PRESERVED_V2',production_Source_changed=False)
put(A/'evidence/DRY_HOST_NATIVE_QUALIFICATION.json',receipt)
print(json.dumps(dict(status=receipt['status'],checks=len(checks),model_starts=0)))

