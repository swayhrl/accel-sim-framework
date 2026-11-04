"""Prepare fresh V4 private immutable proposal specs; no authority/route writes or starts."""
from pathlib import Path
import json,hashlib,os,sys,copy,importlib.util
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';O=Path(__file__).resolve().parent;R=O/'private_runtime'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
sys.path.insert(0,str(R));import runtime_monitor_schema_v4_strict as schema
closure=read(R/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json');extra=read(R/'TRACE_CHILD_HOST_DEPENDENCIES.json')
goal='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104';cohorts=['EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1','EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1']
put(O/'proposal/SCIENTIFIC_PERMISSION_REQUIRED.json',dict(schema='EP_MAIN_PFV4_SCOPED_USER_AUTHORIZATION_V1',goal=goal,explicit_user_approval=False,registered=False,approved_launches=0,proposed_new_independent_budget=2,old_budgets_reusable=False,old_failure_refund_or_retry=False,Source5=closure['Source5'],allowed_cohorts=sorted(cohorts),source_keep=True))
mods=[ref(p)for p in R.rglob('*')if p.is_file()and '__pycache__'not in p.parts]
host=read(V/'agent_b_formal/qualification/HOST_QUALIFICATION.json');host.update(status='PRIVATE_ENGINEERING_DELTA_INTEGRATED_NOT_SCIENTIFIC_AUTHORIZATION',approved_by=None,cohorts_qualified=sorted(cohorts),modules=mods,prior_review_ref=ref(V/'agent_b_formal/qualification/HOST_QUALIFICATION.json'),prior_124_checks_reused_not_rerun=True,install_binding_required_by_Main=True)
put(O/'proposal/HOST_INTEGRATION_BINDING_CANDIDATE.json',host)
results=[];oldrefs=[]
for mode,cohort in zip(['W_ONLY','WV_ZERO_RO'],cohorts):
 old=P/('execution_vector1700_decomposition_v3_20261104_v1/vector1700/cases/EP_PERF_PFV3_VECTOR4M_'+mode+'_1700_V1/control/FROZEN_SPEC.json');s=read(old);oldrefs.append(ref(old))
 s.update(cohort=cohort,science_request_id=goal,goal='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1',status='PRIVATE_FRESH_V4_PROPOSAL_UNAUTHORIZED_UNREGISTERED',launch_permission=False,scientific_scope_activated=False,approved_launches=1,application_budget=1,automatic_retry=False,source_keep=True,host_cpu=None,native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt'),same_background_peer_cohort=cohorts[1]if mode=='W_ONLY'else cohorts[0],Main_scientific_launch_authorization=ref(O/'proposal/SCIENTIFIC_PERMISSION_REQUIRED.json'),host_qualification_ref=ref(O/'proposal/HOST_INTEGRATION_BINDING_CANDIDATE.json'),native_entry_ref=ref(R/'native_vector1700_v4'),native_route_guard_ref=ref(R/'native_route_guard_v3.py'),resource_module_ref=ref(R/'resources_vector1700_v4.py'))
 for k,n in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('postprocess_module_ref','ep_perf_postprocess.py'),('archive_module_ref','ep_perf_archive.py')]:s[k]=ref(R/n)
 # Keep all original pins; append exact 22 native pins plus current dependencies and private code.
 s['pinned_files']={**s['pinned_files'],**closure['pinned_files'],**{x['path']:x['sha256']for x in extra['dependencies']},**{x['path']:x['sha256']for x in mods}}
 s['preconsume_schema_ref']=ref(R/'runtime_monitor_schema_v4_strict.py');s['runtime_contract_ref']=ref(R/'RUNTIME_FULL_43_CONTRACT_V4.json');s['native_runtime_closure_ref']=ref(R/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json');s['extra_Host_dependency_ref']=ref(R/'TRACE_CHILD_HOST_DEPENDENCIES.json')
 s['stage_release']='FIRST_W_ONLY_ACCEPTED_FULL_DRAIN_TRUE164_FULL_SHA_TWO_INDEPENDENT_RESTORES_THEN_WV'if mode=='WV_ZERO_RO'else'PILOT_FIRST'
 s['application_NI']='NOT_MEASURED';s['B0_M0a_application_NI']='NOT_PROVEN';s['prior_failure_reused_as_budget']=False
 # Full schema is consumed now before any native consume; this grants no permission.
 proof=schema.validate_spec_contract(s,ref(R/'RUNTIME_FULL_43_CONTRACT_V4.json'),ref(R/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json'),check_current_domain=True,check_current_dependencies=True,extra_dependencies_ref=ref(R/'TRACE_CHILD_HOST_DEPENDENCIES.json'))
 # Exact original source/background/five switches and282 options remain source-specific check.
 sp=importlib.util.spec_from_file_location('private_mode_contract_'+mode,R/'mode_contract.py');mc=importlib.util.module_from_spec(sp);sp.loader.exec_module(mc);mc.check_background(s)
 target=O/'proposal/specs'/(mode+'.json');put(target,s);results.append(dict(mode=mode,cohort=cohort,spec_ref=ref(target),schema=proof,effective_options_282_preserved=True))
put(O/'proposal/PREPARATION_SCHEMA_RECEIPT.json',dict(status='PASS',points=results,scientific_permission=False,registered=False,model_starts=0,authority_writes=0,route_writes=0))
reuse=read(V/'agent_b_formal/qualification/S_F_REUSE_REVIEW.json')
request=dict(schema='EP_MAIN_PFV4_FRESH_VECTOR1700_TWO_POINT_REQUEST_V1',status='UNAUTHORIZED_NOT_REGISTERED_NOT_LAUNCHABLE',request_id=goal,new_budget=2,old_Vector_budget_reusable=False,old_Vector2_consumed_closed_unaccepted_preserved=True,automatic_retry=False,source_keep=True,Source5=closure['Source5'],points=results,accepted_sameSource_controls={m:reuse['controls'][m]for m in ['S','F']},accepted_cycles={'S':45974,'F':55925},staged_release={'first':cohorts[0],'second':cohorts[1],'requirements':['W_ONLY CLOSED_ACCEPTED','full declared commandlist and hardware drained','true164 archive full SHA','FIRST and INDEPENDENT native target complete SHA restores matching archive SHA']},engineering_gap='Main controlled installation binding of this already tested private runtime and new exact specs; no new engineering rerun required after unchanged pins pass',scientific_gap='Explicit fresh user authorization budget2 and Main registry/native route admission; current proposal grants none',no_model_ELF_launch=True)
put(O/'proposal/FRESH_TWO_POINT_REQUEST.json',request)
put(O/'SOURCEKEEP_PREIMAGES.json',dict(reviewed_commit='9c4a1a958f726be1250608b0a3b82c79438d0926',untouched_refs=oldrefs+[ref(V/'agent_b_incident_20261104_v1/DELIVERY_MANIFEST.json'),ref(V/'agent_b_incident_20261104_v1/actual_process_fixture_v2/DELIVERY_MANIFEST.json'),ref(V/'agent_b_incident_20261104_v1/closure_addendum_v1/DELIVERY_MANIFEST.json')],source_keep=True))
print(json.dumps(dict(status='PRIVATE_PROPOSALS_FULL_SCHEMA_PASS',points=results)))
