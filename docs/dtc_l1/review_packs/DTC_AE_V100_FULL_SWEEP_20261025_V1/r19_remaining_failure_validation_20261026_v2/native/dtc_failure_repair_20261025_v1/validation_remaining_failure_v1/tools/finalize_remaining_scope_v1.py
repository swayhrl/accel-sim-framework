"""Freeze remaining4 candidates only after actual R19/source qualification.

Never registers a request, replaces the entry, consumes a model budget or edits
older scope data. Every output is exclusive-create in this new scope.
"""
import pathlib,json,hashlib,copy,subprocess
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_remaining_failure_v1';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1';G=1024**3;M=1024**2
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,d):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(d,f,sort_keys=True,indent=2);f.write('\n')
def link(p,target):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() or p.is_symlink():assert p.resolve()==P(target).resolve()
 else:p.symlink_to(target)
def main():
 pp=R/'control/REMAINING_BUILD_PROFILE_V1.json';p=read(pp);assert p['freeze_authorized'] is True and p['request']==REQ
 assert p['parent_controller_path']==str(F/'ops/revision19/sweep_controller.py') and sha(p['parent_controller_path'])==p['parent_controller_sha256']
 assert p['continuation_fallback_frontend_path']==str(F/'ops/revision19/frontend_v1.py') and sha(p['continuation_fallback_frontend_path'])==p['continuation_fallback_frontend_sha256']
 assert p['maximum_new_model_slots']==4 and p['reserved_write_bytes']==3*G and set(p['allowed_model_CPUs'])==set(range(192,208))
 assert p['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70' and p['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'
 for key in ['binary_path','core_library_path']:assert sha(p[key])==p[key.replace('_path','_sha256')]
 overlay=p['resource_accounting_overlay'];assert overlay['path']==str(F/'ops/revision19/resource_accounting_v1.py') and sha(overlay['path'])==overlay['sha256']
 scopepath=R/'control/REMAINING_SCOPE_CANDIDATE_V1.json';scope=read(scopepath);assert scope['finite_budget']==len(scope['points'])==4 and set(scope['per_cohort_memory'])==set(p['per_cohort_memory'])
 assert sha(p['closed_R1_cpu_reuse_evidence']['path'])==p['closed_R1_cpu_reuse_evidence']['sha256']
 source=__import__('importlib.util',fromlist=['spec_from_file_location']);spec=source.spec_from_file_location('remaining_cpu_fresh_final',R/'tools/remaining_native_v1.py');engine=source.module_from_spec(spec);spec.loader.exec_module(engine);engine.check_reclaimed_cpu_pool(p)
 for kind in ['core','framework']:
  repo=P(p[kind+'_worktree']);assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==p[kind+'_commit'] and not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
 # Preflight every point before the first final output, so a missing negative
 # archive or mismatched original cannot strand a partially built request.
 for point in scope['points']:
  cell=point['cohort'];draft=read(R/'control/spec_candidates'/(cell+'.json'));old=read(point['prior_frozen_spec_path']);archive=P(point['prior_archive_receipt_path'])
  assert archive.exists() and read(archive)['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','old negative archive pending'
  assert sha(point['prior_frozen_spec_path'])==point['prior_frozen_spec_sha256'] and sha(point['prior_INTENT_path'])==point['prior_INTENT_sha256'] and sha(point['prior_DONE_path'])==point['prior_DONE_sha256']
  assert draft['expected_options']==old['expected_options'] and len(draft['expected_options'])==270 and draft['native_simulator_argv'][1:]==old['native_simulator_argv'][1:] and draft['expected']==old['expected']
  for target in [R/'control/specs'/(cell+'.json'),R/'control'/(cell+'_SPEC.json'),R/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json')]:assert not target.exists(),'unactivated prior candidate requires explicit supersession, never overwrite'
  point['prior_archive_receipt_sha256']=sha(archive)
 preimage=R/'control/draft_preimages/REMAIN4_SCOPE_AT_FINAL_FREEZE';preimage.mkdir(parents=True)
 with (preimage/scopepath.name).open('xb') as stream:stream.write(scopepath.read_bytes())
 scope['status']='R19_SOURCE_BOUND_CANDIDATE_PREPARED_NOT_REGISTERED_AT_FREEZE';scope['parent_controller_sha256']=p['parent_controller_sha256']
 scopepath.write_text(json.dumps(scope,sort_keys=True,indent=2)+'\n')
 rows=[];aliases=[];unique_runtime={}
 for point in scope['points']:
  cell=point['cohort'];cp=R/'control/spec_candidates'/(cell+'.json');s=read(cp);old=read(point['prior_frozen_spec_path']);resource=p['per_cohort_memory'][cell]
  assert sha(point['prior_frozen_spec_path'])==point['prior_frozen_spec_sha256'] and sha(point['prior_INTENT_path'])==point['prior_INTENT_sha256'] and sha(point['prior_DONE_path'])==point['prior_DONE_sha256']
  archive=P(point['prior_archive_receipt_path']);assert archive.exists(),'prior negative archive must be independently closed before final validation request';oldarchive=read(archive);assert oldarchive['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  s.update(schema='REMAINING_FAILURE_NEW_FINITE4_EXACT_SPEC_V1',candidate_not_activated=False,build_profile_sha256=sha(pp),operational_runtime_profile='REMAINING4_PER_COHORT_CAPACITY_9EED_027_V1')
  s['prior_original_point']['archive_receipt_sha256']=sha(archive)
  assert s['limits']['max_process_tree_rss_bytes']==resource['max_process_tree_rss_bytes'] and s['estimated_peak_model_RAM_bytes']==resource['estimated_peak_model_RAM_bytes'] and resource['initial_working_set_floor_bytes']==4*G
  assert len(s['expected_options'])==270 and s['expected_options']==old['expected_options'] and s['configs']==old['configs'] and s['native_simulator_argv'][1:]==old['native_simulator_argv'][1:] and s['expected']==old['expected'] and s['original_environment']==old['original_environment']
  assert s['binary_sha256']==p['binary_sha256'] and sha(s['native_simulator_argv'][0])==s['binary_sha256']
  binding=P(s.get('input_binding_path',str(T/'control/input_bindings'/(s['input_digest']+'.json'))));assert sha(binding)==s['input_binding_sha256'];domain=read(binding)['qualification'];assert domain['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS' and not domain['issues']
  cap=R/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json');put(cap,{'schema':'REMAINING4_RESULT_CAP256MiB_V1','cohort':cell,'effective_result_cap_bytes':256*M,'frozen_upper_result_cap_bytes':s['limits']['max_result_directory_bytes'],'evidence_audit_path':p['output_cap_evidence_path'],'evidence_audit_sha256':sha(p['output_cap_evidence_path']),'input_and_270_options_unchanged':True,'scope':'Only this new finite4 correctness request; old negative rows not refunded or altered'});s['operational_output_cap_sha256']=sha(cap)
  sp=R/'control/specs'/(cell+'.json');put(sp,s);alias=R/'control'/(cell+'_SPEC.json');alias.write_bytes(sp.read_bytes());aliases.append({'path':str(alias),'sha256':sha(alias)});rows.append({'cohort':cell,'path':str(sp),'sha256':sha(sp)})
  for item in s['runtime_files']:
   unique_runtime[item['actual_realpath']]=item['sha256']
   if item['target'].startswith('DTC/env/lib/'):link(R/item['target'],item['actual_realpath'])
 for path,h in unique_runtime.items():assert sha(path)==h
 link(R/'common-lib',T/'common-lib');link(R/'tools/lib',T/'tools/lib');link(R/'tools/bin/strace',T/'tools/bin/strace')
 (R/'control/RESULT_ENGINE_PIN.json').write_bytes((F/'validation/control/RESULT_ENGINE_PIN.json').read_bytes())
 names=['remaining_native_v1.py','remaining_strict_v1.py','remaining_outbox_v1.py','remaining_ops_v1.py','remaining_frontend_v1.py','finalize_remaining_scope_v1.py'];pins=[{'path':str(R/'tools'/n),'sha256':sha(R/'tools'/n)} for n in names]+p['additional_source_pins']+[{'path':overlay['path'],'sha256':overlay['sha256']},{'path':p['closed_R1_cpu_reuse_evidence']['path'],'sha256':p['closed_R1_cpu_reuse_evidence']['sha256']},{'path':p['continuation_fallback_frontend_path'],'sha256':p['continuation_fallback_frontend_sha256']}]+aliases
 ep=R/'control/EXECUTION_PLAN_V1.json';plan=dict(p,schema='REMAINING_FAILURE_FINITE4_EXECUTION_PLAN_V1',scope_path=str(scopepath),scope_sha256=sha(scopepath),build_profile_sha256=sha(pp),source_pins=pins,maximum_original_concurrency=40,maximum_new_model_slots=4,statistics_scope='CORRECTNESS_ONLY_NOT_ORIGINAL_PERFORMANCE');put(ep,plan)
 rp=R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';request={'schema':'REMAINING_FAILURE_NEW_FINITE4_SCIENTIFIC_APPROVAL_REQUEST_V1','request':REQ,'specs':rows,'budget':4,'admitted_inputs':sorted({pt['input_digest'] for pt in scope['points']}),'input_digests':sorted({pt['input_digest'] for pt in scope['points']}),'execution_plan_sha256':sha(ep),'scope_sha256':sha(scopepath),'engine_sha256':sha(R/'tools/remaining_native_v1.py'),'strict_sha256':sha(R/'tools/remaining_strict_v1.py'),'outbox_sha256':sha(T/'tools/sweep_outbox.py'),'repair_outbox_overlay_sha256':sha(R/'tools/remaining_outbox_v1.py'),'correctness_validation_only':True,'model_automatic_retries':0,'older_request_budgets_or_consumed_rows_changed':False};put(rp,request)
 auth=read(R/'control/SCIENCE_AUTHORIZATION_DRAFT_V1.json');auth.update(status='FINAL_NEW_FINITE4_REQUEST_APPROVAL_BINDING_NO_ACTIVATION',approval_request_sha256=sha(rp));put(R/'control/SCIENCE_AUTHORIZATION.json',auth)
 candidate={'schema':'NATIVE_EPOCH2_REGISTERED_FUTURE_REQUEST_V2','request':REQ,'budget':4,'remaining':4,'consumed':{},'sealed':[],'sealed_unused':0,'state':'ARMED','admitted_specs':{r['cohort']:r['sha256'] for r in rows},'admitted_inputs':{k:{'scope':'NEW_REMAIN4_CORRECTNESS_ONLY','specs':[r['cohort'] for r in rows if k[:16] in r['cohort']]} for k in request['admitted_inputs']},'reserved_write_bytes':3*G,'execution_plan_sha256':sha(ep),'spec_request_sha256':sha(rp),'engine_sha256':request['engine_sha256'],'strict_sha256':request['strict_sha256'],'outbox_sha256':request['repair_outbox_overlay_sha256'],'orchestrator_sha256':p['parent_controller_sha256'],'authorized_parent_request':'DTC_AE_V100_FULL_SWEEP_20261025_V1','correctness_validation_only':True,'model_automatic_retries':0,'per_cohort_memory':p['per_cohort_memory'],'old_failed_attempts_preserved':True};put(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',candidate);put(R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 print(json.dumps({'status':'FINAL_REMAIN4_PREPARED_NOT_REGISTERED_NOT_ACTIVATED','budget':4,'profile_sha256':sha(pp),'plan_sha256':sha(ep),'request_sha256':sha(rp),'candidate_sha256':sha(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json'),'authorization_sha256':sha(R/'control/SCIENCE_AUTHORIZATION.json'),'spec_count':len(rows),'old_requests_modified':False,'model_starts':0},indent=2))
if __name__=='__main__':main()
