"""Freeze new memory-validation metadata only after final profile/R15 approval.

Does not register, replace the native entry, modify old ledgers or run models.
"""
import pathlib,json,hashlib,copy,subprocess
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_lava_memory_v2';R1=F/'validation';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_AE_LAVAMEM_REPAIR_20261026_V2';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,sort_keys=True,indent=2);f.write('\n')
def link(target,actual):
 target=P(target);actual=P(actual);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() or target.is_symlink():assert target.resolve()==actual.resolve()
 else:target.symlink_to(actual)
def main():
 profile_path=R/'control/LAVAMEM_BUILD_PROFILE_V2.json';p=read(profile_path);assert p['freeze_authorized'] is True,'wait for final R15 source review and final measured capacity profile'
 hard=p['max_process_tree_rss_bytes'];estimate=p['estimated_peak_model_RAM_bytes'];assert type(hard) is int and type(estimate) is int and hard>=estimate>=4*G and p['initial_working_set_floor_bytes']==4*G
 assert p['maximum_new_model_slots']==2 and p['allowed_model_CPUs'] and set(p['allowed_model_CPUs'])<=set(range(224,256))
 assert p['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70' and p['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'
 for key in ['binary_path','core_library_path','parent_controller_path','original_frontend_path','memory_evidence_path']:assert sha(p[key])==p[key.replace('_path','_sha256')]
 assert p['original_frontend_path']==str(R1/'tools/repair_frontend_v1.py')
 for kind in ['core','framework']:
  repo=P(p[kind+'_worktree']);assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==p[kind+'_commit'] and not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
 scope_path=R/'control/LAVAMEM_SCOPE_CANDIDATE_V2.json';scope=read(scope_path);assert scope['finite_budget']==2 and len(scope['points'])==2
 specs=[];aliases=[]
 for point in scope['points']:
  assert sha(point['prior_frozen_spec_path'])==point['prior_frozen_spec_sha256'];old=read(point['prior_frozen_spec_path']);s=copy.deepcopy(old);s.update(schema='DTC_LAVAMEM_CAPACITY_VALIDATION_EXACT_SPEC_V2',cohort=point['cohort'],request=REQ,prior_original_point=point,operational_runtime_profile='LAVAMEM_PROFILE_DRIVEN_CAPACITY_V2',build_profile_sha256=sha(profile_path),validation_kind='LAVAMEM_CAPACITY_CORRECTNESS_NOT_FORMAL',correctness_validation_only=True,memory_capacity_evidence_sha256=p['memory_evidence_sha256']);s['host_cpu']=p['allowed_model_CPUs'][0];s['limits']['max_process_tree_rss_bytes']=hard;s['estimated_peak_model_RAM_bytes']=estimate
  assert s['native_simulator_argv']==old['native_simulator_argv'] and s['expected_options']==old['expected_options'] and len(s['expected_options'])==270 and s['configs']==old['configs'] and s['expected']==old['expected']
  assert s['expected_options']['-trace']==[s['native_simulator_argv'][s['native_simulator_argv'].index('-trace')+1]]
  assert s['binary_sha256']==p['binary_sha256'] and str(P(s['native_simulator_argv'][0]).resolve())==str(P(p['binary_path']).resolve())
  for item in s['runtime_files']:
   assert sha(item['actual_realpath'])==item['sha256']
   if item['target'].startswith('DTC/env/lib/'):link(R/item['target'],item['actual_realpath'])
  cap=256*1024**2;cap_path=R/'control'/('OPERATIONAL_OUTPUT_CAP_'+s['cohort']+'.json');put(cap_path,{'schema':'LAVAMEM_RESULT_CAP256MiB_V2','cohort':s['cohort'],'effective_result_cap_bytes':cap,'frozen_upper_result_cap_bytes':s['limits']['max_result_directory_bytes'],'evidence_audit_path':p['output_cap_evidence_path'],'evidence_audit_sha256':sha(p['output_cap_evidence_path']),'hard_AS_and_RSS_bytes':hard,'input_and_270_options_unchanged':True,'scope':'new two-attempt capacity correctness only;no old cap or ledger change'});s['operational_output_cap_sha256']=sha(cap_path)
  sp=R/'control/specs'/(s['cohort']+'.json');put(sp,s);alias=R/'control'/(s['cohort']+'_SPEC.json');alias.write_bytes(sp.read_bytes());assert sha(alias)==sha(sp);specs.append({'cohort':s['cohort'],'path':str(sp),'sha256':sha(sp)});aliases.append({'path':str(alias),'sha256':sha(alias)})
 # Exact native loop support aliases, all versioned root paths; never write R1.
 link(R/'common-lib',T/'common-lib');link(R/'tools/lib',T/'tools/lib');link(R/'tools/bin/strace',T/'tools/bin/strace')
 pinpath=R/'control/RESULT_ENGINE_PIN.json';pinpath.write_bytes((R1/'control/RESULT_ENGINE_PIN.json').read_bytes())
 names=['lavamem_native_v2.py','lavamem_strict_v2.py','lavamem_outbox_v2.py','lavamem_frontend_v2.py','lavamem_ops_v2.py','lavamem_prepare_specs_v2.py','lavamem_prepare_scope_v2.py'];pins=[{'path':str(R/'tools'/name),'sha256':sha(R/'tools'/name)} for name in names]+p['additional_source_pins']+aliases+[{'path':p['memory_evidence_path'],'sha256':p['memory_evidence_sha256']},{'path':p['observer_overlay']['path'],'sha256':p['observer_overlay']['sha256']}]
 execution=dict(p,schema='DTC_LAVAMEM_TWO_POINT_EXECUTION_PLAN_V2',scope_path=str(scope_path),scope_sha256=sha(scope_path),build_profile_sha256=sha(profile_path),source_pins=pins,maximum_new_model_slots=2,maximum_validation_concurrency=2,maximum_original_concurrency=40,prior_repair_scope='FROZEN23_ALREADY_STARTED_NO_RELAUNCH',RAM_admission='NEW min(hard,max(4GiB,estimated_peak,RSS));ORIGINAL/R1 min(hard,max(4GiB,RSS));runtime actual64GiB host48GiB effective cgroup',known_writes='Three owned scopes deduplicated;other unrelated reservations only',statistics_scope='NEW_CAPACITY_CORRECTNESS_ONLY_NEVER_ORIGINAL288');ep=R/'control/EXECUTION_PLAN_V2.json';put(ep,execution)
 request={'schema':'DTC_LAVAMEM_NEW_EXACT_FINITE_REQUEST_V2','request':REQ,'specs':specs,'budget':2,'admitted_inputs':sorted({x['input_digest'] for x in scope['points']}),'input_digests':sorted({x['input_digest'] for x in scope['points']}),'execution_plan_sha256':sha(ep),'scope_sha256':sha(scope_path),'engine_sha256':sha(R/'tools/lavamem_native_v2.py'),'strict_sha256':sha(R/'tools/lavamem_strict_v2.py'),'outbox_sha256':sha(T/'tools/sweep_outbox.py'),'repair_outbox_overlay_sha256':sha(R/'tools/lavamem_outbox_v2.py'),'correctness_validation_only':True,'model_automatic_retries':0,'original_or_prior_qualification_budget_changed':False};rp=R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';put(rp,request)
 authorization={'approval_request_sha256':sha(rp),'explicit_user_approval':True,'owner_bindings_ratified':True,'target_resource_policy_ratified':True,'budgets':{x['cohort']:1 for x in specs},'scope':'Two new separate capacity-validation identities under current explicit repair testing authorization;old16GiB attempts remain failed and charged','not_activated_by_this_builder':True};put(R/'control/SCIENCE_AUTHORIZATION_CANDIDATE.json',authorization)
 candidate={'schema':'NATIVE_EPOCH2_REGISTERED_FUTURE_REQUEST_V2','request':REQ,'budget':2,'remaining':2,'consumed':{},'sealed':[],'sealed_unused':0,'state':'ARMED','admitted_specs':{x['cohort']:x['sha256'] for x in specs},'admitted_inputs':{key:{'scope':'LAVAMEM_CAPACITY_CORRECTNESS_ONLY','specs':[s['cohort'] for s in specs if key[:16] in s['cohort']]} for key in request['admitted_inputs']},'reserved_write_bytes':2*G,'execution_plan_sha256':sha(ep),'spec_request_sha256':sha(rp),'engine_sha256':request['engine_sha256'],'strict_sha256':request['strict_sha256'],'outbox_sha256':request['repair_outbox_overlay_sha256'],'orchestrator_sha256':p['parent_controller_sha256'],'authorized_parent_request':'DTC_AE_V100_FULL_SWEEP_20261025_V1','correctness_validation_only':True,'model_automatic_retries':0,'max_process_tree_rss_bytes':hard,'estimated_peak_model_RAM_bytes':estimate,'old_failed_attempts_preserved':True};put(R/'control/REGISTRY_REQUEST_CANDIDATE_V2.json',candidate);(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json').write_bytes((R/'control/REGISTRY_REQUEST_CANDIDATE_V2.json').read_bytes());put(R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 print(json.dumps({'prepared_specs':2,'profile_sha256':sha(profile_path),'plan_sha256':sha(ep),'request_sha256':sha(rp),'candidate_sha256':sha(R/'control/REGISTRY_REQUEST_CANDIDATE_V2.json'),'authority_registered':False,'entry_changed':False,'models_started':0}))
if __name__=='__main__':main()
