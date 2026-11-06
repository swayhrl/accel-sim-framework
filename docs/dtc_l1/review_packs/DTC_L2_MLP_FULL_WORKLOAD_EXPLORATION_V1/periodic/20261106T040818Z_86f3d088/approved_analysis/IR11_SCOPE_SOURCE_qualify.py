"""Seven pure-scope CPU cases; actual frozen scopes + private new authority."""
import pathlib,json,hashlib,copy,importlib.util
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/incident11_scope_bridge_v1';B=A/'agents/B/incident11_recovery_trials_plan_v1';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(n,v):(D/n).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
m=load('incident_scope_candidate',D/'scope_bridge.py');oldpath=A/'coordinator/bpf_canary_orchestration_v2/scope_bridge.py';old=load('unchanged_canary2a82',oldpath);cp=A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json';canary=old.CanaryScope(read(cp));plan=read(B/'DRAFT_PLAN.json');assert sha(B/'DRAFT_PLAN.json')=='72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5'
assert sha(B/'MANIFEST.json').startswith('5914');q=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];matrix=read(R/'control/MATRIX_CURRENT.json');primary=read(R/'control/SCOPE.json');r2='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2';legacy=set(canary.rows)|{r2};obj=m.IncidentScope(plan,legacy)
specs={row['new_cohort']:read(row['draft_spec']['path'])for row in plan['rows']};hashes={row['new_cohort']:sha(row['draft_spec']['path'])for row in plan['rows']}
fakeq=copy.deepcopy(q);fakeq['admitted_specs'].update(hashes);fakeq['authorized_incident_recovery_trials']=[obj.authorization_record(c)for c in obj.rows];canonical=lambda c:(specs[c],hashes[c])
previous=copy.deepcopy(matrix);r2spec=read(R/'control/specs'/(r2+'.json'));previous['points'].append({k:r2spec[k]for k in ['cohort','input_digest','program','suite','profile','cell']})
oldcanonical=lambda c:(read(R/'control/specs'/(c+'.json')),sha(R/'control/specs'/(c+'.json')));previous=canary.dispatch_view(previous,matrix,primary,q,oldcanonical)
baseline=m.digest(previous);matrixhash=m.digest(matrix);qhash=m.digest(q);spechash=m.digest(specs);checks=[]
def check(name,condition):assert condition,name;checks.append(dict(name=name,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return True
 return False
view=obj.dispatch_view(previous,matrix,primary,fakeq,canonical);stripped=obj.primary_view(view,matrix,primary,fakeq,canonical);r2view=canary.primary_view(stripped,matrix,primary,q,oldcanonical)
check('actual_primary_dynamicN_plus_existing5_plus_IR11_composes_and_strips_exactly',len(view['points'])==len(matrix['points'])+5+11 and m.digest(stripped)==baseline and len(r2view['points'])==len(matrix['points'])+1)
c=next(iter(specs));amended=copy.deepcopy(specs[c]);amended['estimated_peak_model_RAM_bytes']+=12345;amended['limits']['max_process_tree_rss_bytes']+=98765;newh=m.digest(amended);aq=copy.deepcopy(fakeq);aq['admitted_specs'][c]=newh
check('official_resource_refresh_uses_current_grant_SHA_not_DRAFT_fullSHA',obj.validate(c,amended,newh,aq)['canonical_sha256']==newh and newh!=hashes[c])
physics=copy.deepcopy(specs[c]);physics['expected_options']['-gpgpu_dram_return_queue_size']='999';bound=copy.deepcopy(specs[c]);bound['host_cpu']=1
check('science_option_drift_and_bound_canonical_CPU_rejected',reject(lambda:obj.validate(c,physics,hashes[c],fakeq))and reject(lambda:obj.validate(c,bound,hashes[c],fakeq)))
bad=copy.deepcopy(fakeq);bad['authorized_incident_recovery_trials'][0]['original_negative_RESULT_sha256']='0'*64;short=copy.deepcopy(fakeq);short['authorized_incident_recovery_trials'].pop();wrong=copy.deepcopy(specs[c]);wrong['incident_recovery_trial_lineage']['original_uuid']='WRONG_UUID'
check('exact11_authority_and_oldnegative_UUID_mapping_required',reject(lambda:obj.validate(c,specs[c],hashes[c],bad))and reject(lambda:obj.validate(c,specs[c],hashes[c],short))and reject(lambda:obj.validate(c,wrong,hashes[c],fakeq)))
optional=obj.optional_dispatch_view(previous,matrix,primary,q,canonical);unknown=copy.deepcopy(previous);unknown['points'].append(dict(cohort='UNKNOWN_TRIAL',scientific_role='UNKNOWN_NEW_ROLE'));unsafe=obj.optional_dispatch_view(unknown,matrix,primary,fakeq,canonical)
check('optional_missing_evidence_keeps_exact_legacy_queue_unknown_role_failclosed',optional['legacy_queue_usable']and m.digest(optional['view'])==baseline and optional['scientific_final']is False and unsafe['view']is None and unsafe['legacy_queue_usable']is False)
summary={'table':{'x':{'F256':{'DH':dict(cohort=c,scientific_role=m.ROLE)}}}};contaminated=copy.deepcopy(matrix);contaminated['points'].append(dict(cohort=c,scientific_role=m.ROLE))
check('primary_summary_and_matrix_contamination_nonfinal_HOLD',reject(lambda:obj.assert_primary_summary(summary,matrix,primary))and reject(lambda:obj.dispatch_view(previous,contaminated,primary,fakeq,canonical)))
tampered=copy.deepcopy(view);tampered['points'][0]['program']='TAMPERED_PRIOR';check('no_inputs_oldq_science_or_prior_view_mutated_and_strip_tamper_rejected',m.digest(previous)==baseline and m.digest(matrix)==matrixhash and m.digest(q)==qhash and m.digest(specs)==spechash and reject(lambda:obj.primary_view(tampered,matrix,primary,fakeq,canonical)))
proof=dict(schema='INCIDENT11_PURE_SCOPE_CPU_QUALIFICATION_V1',status='PASS',qualification_only=True,checks=checks,source_sha256=sha(m.__file__),driver_sha256=sha(__file__),source_pins={str(p):sha(p)for p in[B/'DRAFT_PLAN.json',B/'MANIFEST.json',oldpath,cp,R/'control/SCOPE.json',R/'control/MATRIX_CURRENT.json']},legacy_nonprimary_cohorts=sorted(legacy),current_runtime_sizes_fixture=dict(real_primary=len(matrix['points']),existing_nonprimary=len(legacy),with_IR11=len(view['points'])),fixture_scope='Real current primary+Canary2a82 source; synthetic previous R2 view row + private newq/IR11 grants, not actual owner or registration',production_mutations=0,models_started=0,new_grants=0)
put('CPU_QUALIFICATION.json',proof);put('AUTHORIZATION_RECORDS.template.json',dict(schema='INCIDENT11_EXACT_AUTHORIZATION_ROWS_TEMPLATE_V1',status='NOT_REGISTERED',authorized_incident_recovery_trials=[obj.authorization_record(c)for c in obj.rows]))
print(json.dumps(dict(path=str(D),source_sha256=sha(m.__file__),QA_sha256=sha(D/'CPU_QUALIFICATION.json'),checks=len(checks))))
