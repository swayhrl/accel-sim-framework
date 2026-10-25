"""Authorized metadata-only supersession of two never-activated requests."""
import pathlib,json,hashlib,copy,datetime,subprocess,os
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R2=F/'validation_lava_memory_v2';L=F/'validation_late_failure_v1';R1=F/'validation';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');G=1024**3;M=1024**2;LAVA='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';parent=F/'ops/revision16/sweep_controller.py';PARENT='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,d,new=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x' if new else 'w') as f:json.dump(d,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def link(p,target):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() or p.is_symlink():assert p.resolve()==P(target).resolve()
 else:p.symlink_to(target)
assert sha(parent)==PARENT
registry=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
assert all(req not in registry['registered_future_requests'] for req in [LAVA,LATE])
assert all(not list((root/'control/qualification_ledger').glob('*.INTENT.json')) for root in [R2,L])
assert not (R2/'control/draft_preimages/UNACTIVATED_R15_BEFORE_R16/MANIFEST.json').exists()
source_before={str(p):sha(p) for root in [R2,L] for p in (root/'tools').glob('*.py')}
pre=R2/'control/draft_preimages/UNACTIVATED_R15_BEFORE_R16';pre.mkdir(parents=True)
saved=[]
for p in sorted((R2/'control').rglob('*.json')):
 if pre in p.parents or 'draft_preimages' in p.parts:continue
 rel=p.relative_to(R2/'control');dest=pre/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
 assert sha(dest)==sha(p);saved.append({'canonical_path':str(p),'preimage_path':str(dest),'sha256':sha(p)})
oldprofile=read(R2/'control/LAVAMEM_BUILD_PROFILE_V2.json');oldplan=read(R2/'control/EXECUTION_PLAN_V2.json');oldrequest=read(R2/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');oldq=read(R2/'control/REGISTRY_REQUEST_CANDIDATE_V2.json');oldauth=read(R2/'control/SCIENCE_AUTHORIZATION.json')
assert oldq['consumed']=={} and oldq['remaining']==2 and oldq['reserved_write_bytes']==2*G
put(pre/'MANIFEST.json',{'schema':'UNACTIVATED_R15_CANONICAL_METADATA_PREIMAGES_BEFORE_R16_V1','status':'EXACT_BYTES_PRESERVED_NO_SCIENTIFIC_ATTEMPT','original_R15_parent_sha256':oldprofile['parent_controller_sha256'],'saved':saved,'source_SHA_unchanged':source_before,'R2_never_registered':True,'R2_INTENT_count':0,'budget_refunded':False,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},True)
profile=copy.deepcopy(oldprofile);profile.update(parent_controller_path=str(parent),parent_controller_sha256=PARENT,scope_path=str(R2/'control/LAVAMEM_SCOPE_CANDIDATE_V2.json'),supersedes_never_activated_parent='R15',supersession_preimage_manifest_path=str(pre/'MANIFEST.json'),supersession_preimage_manifest_sha256=sha(pre/'MANIFEST.json'),reserved_write_bytes=G+512*M,writer_gate='1GiB metadata + one live/write-restore allowance512MiB; second point waits exact archive receipt;finite budget stays2')
put(R2/'control/LAVAMEM_BUILD_PROFILE_V2.json',profile)
specrows=[];aliaspins=[]
for cell in oldq['admitted_specs']:
 sp=R2/'control/specs'/(cell+'.json');s=read(sp);before=copy.deepcopy(s);s['build_profile_sha256']=sha(R2/'control/LAVAMEM_BUILD_PROFILE_V2.json');put(sp,s);alias=R2/'control'/(cell+'_SPEC.json');alias.write_bytes(sp.read_bytes());aliaspins.append({'path':str(alias),'sha256':sha(alias)});specrows.append({'cohort':cell,'path':str(sp),'sha256':sha(sp)})
 assert all(s[k]==before[k] for k in s if k!='build_profile_sha256')
plan=copy.deepcopy(oldplan);plan.update(profile);plan.update(build_profile_sha256=sha(R2/'control/LAVAMEM_BUILD_PROFILE_V2.json'),scope_path=str(R2/'control/LAVAMEM_SCOPE_CANDIDATE_V2.json'),scope_sha256=sha(R2/'control/LAVAMEM_SCOPE_CANDIDATE_V2.json'))
aliaspaths={x['path'] for x in aliaspins};plan['source_pins']=[x for x in oldplan['source_pins'] if x['path'] not in aliaspaths]+aliaspins
put(R2/'control/EXECUTION_PLAN_V2.json',plan)
request=copy.deepcopy(oldrequest);request.update(specs=specrows,execution_plan_sha256=sha(R2/'control/EXECUTION_PLAN_V2.json'),supersedes_unactivated_R15_metadata=True,supersession_preimage_manifest_sha256=sha(pre/'MANIFEST.json'));put(R2/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',request)
q=copy.deepcopy(oldq);q.update(admitted_specs={x['cohort']:x['sha256'] for x in specrows},execution_plan_sha256=sha(R2/'control/EXECUTION_PLAN_V2.json'),spec_request_sha256=sha(R2/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),orchestrator_sha256=PARENT,reserved_write_bytes=G+512*M,supersedes_unactivated_R15_metadata=True);put(R2/'control/REGISTRY_REQUEST_CANDIDATE_V2.json',q);(R2/'control/REGISTRY_REQUEST_CANDIDATE_V1.json').write_bytes((R2/'control/REGISTRY_REQUEST_CANDIDATE_V2.json').read_bytes())
auth=copy.deepcopy(oldauth);auth.update(approval_request_sha256=sha(R2/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),parent_metadata_supersession='R15_NEVER_ACTIVATED_TO_R16_WITH_PREIMAGES',registered_reserved_write_bytes=G+512*M,finite_budget_unchanged=2,all_prior_authorization_fields_and_user_text_preserved=True);put(R2/'control/SCIENCE_AUTHORIZATION.json',auth)
ac=read(R2/'control/SCIENCE_AUTHORIZATION_CANDIDATE.json');ac.update(approval_request_sha256=auth['approval_request_sha256']);put(R2/'control/SCIENCE_AUTHORIZATION_CANDIDATE.json',ac)
# New late4 scope/specs are independently charged identities, never original288.
scope=read(L/'control/LATE_SCOPE_CANDIDATE_V1.json');scope.update(status='FINAL_PREPARED_NOT_REGISTERED_NOT_ACTIVATED',diagnosis_pack_path=str(F/'analysis/new_original_failures_20261026_v1'),models_started=0);put(L/'control/LATE_SCOPE_CANDIDATE_V1.json',scope)
topo=json.loads(subprocess.check_output(['lscpu','-J','-e=CPU,CORE,SOCKET,ONLINE'],text=True))['cpus'];physical={int(x['cpu']):(int(x['core']),int(x['socket'])) for x in topo};cpus=list(range(144,160));other=set(range(64,144))|set(range(160,256));assert not {physical[x] for x in cpus}&{physical[x] for x in other};assert set(cpus)<=os.sched_getaffinity(0)
lp=copy.deepcopy(read(L/'control/LATE_BUILD_PROFILE_DRAFT_V1.json'));lp.update(schema='DTC_LATE_FOUR_POINT_BUILD_PROFILE_V1',freeze_authorized=True,status='FINAL_PREPARED_NOT_REGISTERED_NOT_ACTIVATED',parent_controller_path=str(parent),parent_controller_sha256=PARENT,initial_working_set_floor_bytes=4*G,scope_path=str(L/'control/LATE_SCOPE_CANDIDATE_V1.json'),reserved_write_bytes=3*G,additional_source_pins=copy.deepcopy(profile['additional_source_pins']),CPU_topology_evidence=[x for x in topo if int(x['cpu']) in cpus],CPU_pool_physically_disjoint_from_all_three_other_scopes=True,diagnosis_pack_path=str(F/'analysis/new_original_failures_20261026_v1'),original_frontend_path=str(R2/'tools/lavamem_frontend_v2.py'),original_frontend_sha256=sha(R2/'tools/lavamem_frontend_v2.py'))
pp=L/'control/LATE_BUILD_PROFILE_V1.json';put(pp,lp,True)
rows=[];aliases=[]
for i,point in enumerate(scope['points']):
 cell=point['cohort'];s=read(L/'control/spec_candidates'/(cell+'.json'));old=read(s['prior_original_point']['prior_frozen_spec_path']);s.update(schema='DTC_LATE_FAILURE_NEW_IDENTITY_EXACT_SPEC_V1',candidate_not_registered=False,build_profile_sha256=sha(pp),operational_runtime_profile='LATE_FAILURE_4G_INITIAL_16G_HARD_V1',host_cpu=cpus[i],estimated_peak_model_RAM_bytes=4*G)
 assert s['expected_options']==old['expected_options'] and len(s['expected_options'])==270 and s['native_simulator_argv'][1:]==old['native_simulator_argv'][1:] and s['configs']==old['configs'] and s['expected']==old['expected']
 assert s['expected_options']['-trace']==[s['native_simulator_argv'][s['native_simulator_argv'].index('-trace')+1]]
 assert s['core_commit']==lp['core_commit'] and s['framework_commit']==lp['framework_commit'] and s['binary_sha256']==lp['binary_sha256']
 capfile=L/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json');put(capfile,{'schema':'LATE_FAILURE_RESULT_CAP256MiB_V1','cohort':cell,'effective_result_cap_bytes':256*M,'frozen_upper_result_cap_bytes':s['limits']['max_result_directory_bytes'],'evidence_audit_path':lp['output_cap_evidence_path'],'evidence_audit_sha256':sha(lp['output_cap_evidence_path']),'hard_AS_and_RSS_bytes':16*G,'input_and_270_options_unchanged':True,'scope':'New late4 correctness attempt; originals remain charged failed; operational upper unchanged'},True);s['operational_output_cap_sha256']=sha(capfile)
 sp=L/'control/specs'/(cell+'.json');put(sp,s,True);alias=L/'control'/(cell+'_SPEC.json');alias.write_bytes(sp.read_bytes());rows.append({'cohort':cell,'path':str(sp),'sha256':sha(sp)});aliases.append({'path':str(alias),'sha256':sha(alias)})
 for item in s['runtime_files']:
  if item['target'].startswith('DTC/env/lib/'):link(L/item['target'],item['actual_realpath'])
link(L/'common-lib',T/'common-lib');link(L/'tools/lib',T/'tools/lib');link(L/'tools/bin/strace',T/'tools/bin/strace')
(L/'control/RESULT_ENGINE_PIN.json').write_bytes((R1/'control/RESULT_ENGINE_PIN.json').read_bytes())
names=['late_native_v1.py','late_strict_v1.py','late_outbox_v1.py','late_frontend_v1.py','late_ops_v1.py'];pins=[{'path':str(L/'tools'/x),'sha256':sha(L/'tools'/x)} for x in names]+lp['additional_source_pins']+aliases+[{'path':lp['original_frontend_path'],'sha256':lp['original_frontend_sha256']}]
le=dict(lp,schema='DTC_LATE_FOUR_POINT_EXECUTION_PLAN_V1',scope_path=str(L/'control/LATE_SCOPE_CANDIDATE_V1.json'),scope_sha256=sha(L/'control/LATE_SCOPE_CANDIDATE_V1.json'),build_profile_sha256=sha(pp),source_pins=pins,maximum_original_concurrency=40,RAM_admission='ORIGINAL/R1/NEW4 floor4GiB, LAVA floor96GiB, min(hard,max(floor,RSS));actualruntime64GiBhost48GiBcgroup',known_writes='four owned scopes exact known writes; only unrelated foreign ceilings');ep=L/'control/EXECUTION_PLAN_V1.json';put(ep,le,True)
lr={'schema':'DTC_LATE_FAILURE_FOUR_NEW_EXACT_FINITE_REQUEST_V1','request':LATE,'specs':rows,'budget':4,'admitted_inputs':sorted({x['input_digest'] for x in scope['points']}),'input_digests':sorted({x['input_digest'] for x in scope['points']}),'execution_plan_sha256':sha(ep),'scope_sha256':sha(L/'control/LATE_SCOPE_CANDIDATE_V1.json'),'engine_sha256':sha(L/'tools/late_native_v1.py'),'strict_sha256':sha(L/'tools/late_strict_v1.py'),'outbox_sha256':sha(T/'tools/sweep_outbox.py'),'repair_outbox_overlay_sha256':sha(L/'tools/late_outbox_v1.py'),'correctness_validation_only':True,'model_automatic_retries':0,'original_or_prior_qualification_budget_changed':False};rp=L/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';put(rp,lr,True)
lq={'schema':'NATIVE_EPOCH2_REGISTERED_FUTURE_REQUEST_V2','request':LATE,'budget':4,'remaining':4,'consumed':{},'sealed':[],'sealed_unused':0,'state':'ARMED','admitted_specs':{x['cohort']:x['sha256'] for x in rows},'admitted_inputs':{key:{'scope':'LATE_FAILURE_CORRECTNESS_ONLY','specs':[x['cohort'] for x in rows if key[:16] in x['cohort']]} for key in lr['admitted_inputs']},'reserved_write_bytes':3*G,'execution_plan_sha256':sha(ep),'spec_request_sha256':sha(rp),'engine_sha256':lr['engine_sha256'],'strict_sha256':lr['strict_sha256'],'outbox_sha256':lr['repair_outbox_overlay_sha256'],'orchestrator_sha256':PARENT,'authorized_parent_request':'DTC_AE_V100_FULL_SWEEP_20261025_V1','correctness_validation_only':True,'model_automatic_retries':0,'max_process_tree_rss_bytes':16*G,'estimated_peak_model_RAM_bytes':4*G,'old_failed_attempts_preserved':True};put(L/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',lq,True);put(L/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}},True)
la=copy.deepcopy(auth);la.update(approval_request_sha256=sha(rp),budgets={x['cohort']:1 for x in rows},scope='Four NEW full-input late failure correctness attempts with fixed9eed/027 repair source; old failures remain charged and unchanged',registered_reserved_write_bytes=3*G,finite_budget_unchanged=None,finite_new_budget=4,parent_metadata_supersession='NEW_REQUEST_R16_NOT_PREVIOUSLY_REGISTERED',prior_authorization_path=str(R1/'control/SCIENCE_AUTHORIZATION.json'),prior_authorization_sha256=sha(R1/'control/SCIENCE_AUTHORIZATION.json'));put(L/'control/SCIENCE_AUTHORIZATION.json',la,True)
assert all(sha(p)==h for p,h in source_before.items())
final={}
for root,prof,planname,cand in [(R2,'LAVAMEM_BUILD_PROFILE_V2.json','EXECUTION_PLAN_V2.json','REGISTRY_REQUEST_CANDIDATE_V2.json'),(L,'LATE_BUILD_PROFILE_V1.json','EXECUTION_PLAN_V1.json','REGISTRY_REQUEST_CANDIDATE_V1.json')]:
 final[str(root)]={key:{'path':str(root/'control'/name),'sha256':sha(root/'control'/name)} for key,name in [('profile',prof),('plan',planname),('request','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),('candidate',cand),('authorization','SCIENCE_AUTHORIZATION.json')]}
receipt={'schema':'R16_TWO_UNACTIVATED_SCOPES_METADATA_FREEZE_AND_SUPERSESSION_V1','status':'FINAL_METADATA_FROZEN_NO_ACTIVATION','parent_controller_sha256':PARENT,'preimage_manifest_path':str(pre/'MANIFEST.json'),'preimage_manifest_sha256':sha(pre/'MANIFEST.json'),'saved_preimages':len(saved),'final':final,'unchanged_source_pins':[{'path':p,'sha256':h} for p,h in sorted(source_before.items())],'old_R1_modified':False,'real_registrations':0,'entry_changes':0,'actual_models_started':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};out=F/'ops/revision16/R16_TWO_SCOPE_METADATA_FREEZE_RECEIPT_V1.json';put(out,receipt,True)
print(json.dumps({'status':receipt['status'],'final':final,'receipt':str(out),'receipt_sha256':sha(out),'saved_preimages':len(saved)},indent=2))
