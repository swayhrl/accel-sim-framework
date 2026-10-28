"""Focused CPU2 scope/lineage/approval-only qualification. No models or grants."""
import ast,copy,hashlib,pathlib,json,types,os,time,difflib
import cpu_fixture_v2 as F
D=F.D;f=F.fixture();m=f.lib;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except(RuntimeError,AssertionError,KeyError,ValueError,OSError):checks.append(n);return
 raise AssertionError(n+' not rejected')
oldpath=D.parent/'cpu_spare_memory_v1/cpu_memory.py';oldsrc=oldpath.read_text();newsrc=(D/'cpu_memory.py').read_text();needold='5b081e91077d84856f077d3f2fcbbf9f2aee97af6a6ed3297942cae44a304b54';ck('old_CPU1_frozen_source_exact',F.sha(oldpath)==needold)
def functions(src):return {x.name:ast.get_source_segment(src,x)for x in ast.parse(src).body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
a=functions(oldsrc);b=functions(newsrc);unchanged=['read','sha','js','objsha','need','load','atomic','effective_policy','budget','_kv','_ranges','_cgroups','_snapshot','sample_cpu_evidence','verify_cpu_evidence','_raw','project','_invocation','_native_forecast'];ck('all_sampling_quota_topology_ticks_and_RAM_math_helpers_byte_identical',all(a[n]==b[n]for n in unchanged))
def policy(src):return ast.get_source_segment(src,next(x for x in ast.parse(src).body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='POLICY'for t in x.targets)))
ck('POLICY_numeric_and_unknown_ancestor_rules_byte_identical',policy(oldsrc)==policy(newsrc))
m.validate(f.cfg,f.q);ck('proper_CPU1_object_and_old39_extracted_not_ACTIVE_as_old95',f.cfg['fallback_v2_config']==f.previous['fallback_v2_config']and f.cfg['previous_cpu_v1_config']==f.previous and f.old['overlay_id']=='FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1')
before=copy.deepcopy({k:v for k,v in f.q['additional_operational_overlays'].items()if k!=m.ID});c=f.points[0]
ck('two_distinct_allowed_unspent_primary_cohorts_eligible',all(m.eligible_cohort(f.cfg,f.q,x,'OWNER_CHOOSE')for x in f.points))
claims={c:dict(CPU_fixture_claim=True)};ck('OWNER_CHOOSE_rejects_existingclaim_FRAME_and_NATIVE_keep_ownclaim',not m.eligible_cohort(f.cfg,f.q,c,'OWNER_CHOOSE',claims)and m.eligible_cohort(f.cfg,f.q,c,'OWNER_FRAME',claims)and m.eligible_cohort(f.cfg,f.q,c,'NATIVE',claims))
ck('no_global_q_wildcard_or_unknown_cohort',not m.eligible_cohort(f.cfg,f.q,'NOT_ALLOWED','NATIVE'))
f.q['consumed'][c]=dict(uuid='CPU_FIXTURE_SPENT');ck('spent_dynamically_excluded_without_invalidating_whole_cfg',not m.eligible_cohort(f.cfg,f.q,c,'NATIVE'));m.validate(f.cfg,f.q);f.q['consumed'].pop(c)
f.q['sealed']=[c];ck('sealed_dynamically_excluded',not m.eligible_cohort(f.cfg,f.q,c,'NATIVE'));f.q['sealed']=[]
reject('unknown_stage_rejected',lambda:m.eligible_cohort(f.cfg,f.q,c,'UNRECOGNIZED'))
production=copy.deepcopy(f.q);production.pop('qualification_only');reject('CPU_standin_canary_cannot_authorize_real_Main_q',lambda:m.validate(f.cfg,production))
body=f.gate.read_bytes();f.gate.unlink();reject('missing_actual_natural_receipt_failclosed',lambda:m.validate(f.cfg,f.q));f.gate.write_bytes(body)
bad=copy.deepcopy(f.cfg);bad['canary_qualification_sha256']='0'*64;reject('wrong_canary_receipt_SHA_rejected',lambda:m.validate(bad,f.q))
r=copy.deepcopy(f.receipt);r['production_release_eligible']=False;F.put(f.gate,r);f.cfg['canary_qualification_sha256']=F.sha(f.gate);f.q['additional_operational_overlays'][m.ID]=dict(m.record(f.cfg),status='ACTIVE');reject('nonrelease_natural_receipt_rejected',lambda:m.validate(f.cfg,f.q));f.gate.write_bytes(body);f.cfg['canary_qualification_sha256']=F.sha(f.gate);f.q['additional_operational_overlays'][m.ID]=dict(m.record(f.cfg),status='ACTIVE')
row=copy.deepcopy(f.q['consumed'][f.canary]);f.q['consumed'][f.canary]['execution_receipt']['stop_reason']='CPU_FIXTURE_NOT_NATURAL';reject('actual_q_nonnatural_or_missing_DONE_not_authorized',lambda:m.validate(f.cfg,f.q));f.q['consumed'][f.canary]=row
bad=copy.deepcopy(f.cfg);bad['previous_cpu_v1_config_sha256']='0'*64;reject('previous_CPU1_config_preimage_hash_mismatch',lambda:m.validate(bad,f.q))
p=m.project_for_candidate(f.base,f.cfg,c,selected_cpu=2,evidence=f.evidence(2),context=dict(kind='OWNER_CHOOSE'))['additional_cpu_spare_memory_admission_proof'];ck('new_V2_scope_and_per_cohort_mode_not_fake_singleton',p['schema']==m.ID and p['mode']=='CPU_SPARE_PER_COHORT'and m.verify_memory_proof(p)['mode']=='CPU_SPARE_PER_COHORT')
q=copy.deepcopy(p);q['mode']='CPU_SPARE_SINGLETON';reject('old_singleton_mode_not_relabelled_as_new_V2',lambda:m.verify_memory_proof(q))
receipt_path=f.gate;f.gate.unlink();ck('offline_verifier_uses_snapshotted_qualification_not_current_Main_path',m.verify_memory_proof(p)['mode']=='CPU_SPARE_PER_COHORT');f.gate.write_bytes(body)
future='CPU2_FUTURE_EXTENSION';f.q['admitted_specs'][future]='CPU_FIXTURE_FUTURE_SPEC';ck('admitted_not_allowed_is_not_stolen_before_SCOPE_ACK',not m.eligible_cohort(f.cfg,f.q,future,'NATIVE'));f.cfg['allowed_cohorts'].append(future);f.q['additional_operational_overlays'][m.ID]=dict(m.record(f.cfg),status='ACTIVE');m.validate(f.cfg,f.q);ck('one_list_append_enables_future_registered_primary_without_duplicate_CPU_list',m.eligible_cohort(f.cfg,f.q,future,'NATIVE')and'allowed_cohorts'not in f.cfg['cpu_exception_scope'])
ck('old95_and_CPU1_records_not_mutated',before=={k:v for k,v in f.q['additional_operational_overlays'].items()if k!=m.ID})
canary_spec=F.read(F.R/'control/specs'/(f.canary+'.json'));resource=F.load('cpu2_actual_forecast_source',F.R/'tools/l2_resources.py');forecast=resource.forecast(canary_spec,F.read(F.R/'control/HISTORICAL_RSS.json'),F.read(F.R/'control/RESOURCE_POLICY.json'));canary_spec['estimated_peak_model_RAM_bytes']=max(canary_spec['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes'])
saved_sampler=m.sample_cpu_evidence;m.sample_cpu_evidence=lambda selected_cpu=None,**kw:f.evidence(selected_cpu)
def native(c):
 spec=copy.deepcopy(canary_spec);spec.update(cohort=c,host_cpu=2);base=copy.deepcopy(f.base);cost=spec['estimated_peak_model_RAM_bytes'];base['own_ram_forecasts']=[dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=cost)];base['total_projected_additional_RAM_bytes']=3*F.G+cost;base['admission_decision']['additional_reserved_RAM_bytes']=base['total_projected_additional_RAM_bytes']
 return types.SimpleNamespace(__file__=str(F.R/'tools/l2_native.py'),registered=lambda:(None,None,f.q,None),spec_for=lambda c:copy.deepcopy(spec),assert_parent_lease=lambda:dict(pid=99999001,start_ticks=1,fd=17,CPU_fixture_only=True),resources=lambda s,fresh_source=False:copy.deepcopy(base),engine=lambda:types.SimpleNamespace(exclusive=lambda p,x:F.put(p,x)))
for c in f.points:
 n=native(c);m.install_future_native(n,f.cfg,False,invocation_cohort=c);out=f.root/c;out.mkdir();ex=n.engine();ex.exclusive(out/'CPU_ONLY.INTENT.json',dict(cohort=c,output=str(out)));snapshot=F.read(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json');binding=F.read(out/'CPU_ONLY.INTENT.json')['additional_cpu_spare_memory_admission_binding'];ck('new_native_per_cohort_mode_and_snapshot_gate_'+c,binding['schema']==m.ID and binding['mode']=='CPU_SPARE_PER_COHORT'and snapshot['canary_qualification_utf8']==f.gate.read_text()and all(m.verify_memory_proof(p,require_native=True)['mode']=='CPU_SPARE_PER_COHORT'for p in snapshot['fresh_preflights']))
m.sample_cpu_evidence=saved_sampler
sample=m.sample_cpu_evidence(sample_seconds=.5);F.put(f.root/'READONLY_REAL_CPU_SAMPLE.json',sample);ck('same_real_sampler_runs_CPU2_schema_truthfully',sample['schema']==m.ID+'_CPU_DOUBLE_SAMPLE'and sample['second']['monotonic']-sample['first']['monotonic']>=.5)
diff=dict(previous_source_sha256=F.sha(oldpath),new_source_sha256=F.sha(D/'cpu_memory.py'),unchanged_function_names=unchanged,unchanged_function_SHA256={n:hashlib.sha256(a[n].encode()).hexdigest()for n in unchanged},POLICY_byte_identical=True,unified_diff=''.join(difflib.unified_diff(oldsrc.splitlines(True),newsrc.splitlines(True),fromfile='CPU1_5b/cpu_memory.py',tofile='CPU2/cpu_memory.py')))
F.put(D/'CPU1_TO_CPU2_EXACT_SOURCE_DIFF.json',diff)
report=dict(schema='CPU2_SCOPE_LINEAGE_AND_GATE_CPU_QUALIFICATION_V1',status='PASS',library_source_sha256=F.sha(D/'cpu_memory.py'),driver_sha256=F.sha(__file__),builder_sha256=F.sha(D/'cpu_fixture_v2.py'),checks=checks,count=len(checks),fixture=str(f.root),actual_cpu_sample_eligible=sample['eligible'],actual_CPU_sample_path=str(f.root/'READONLY_REAL_CPU_SAMPLE.json'),actual_CPU_sample_sha256=F.sha(f.root/'READONLY_REAL_CPU_SAMPLE.json'),cpu_pid=os.getpid(),qualification_standin_gate_is_not_production_authority=True,real_canary_receipt_not_yet_supplied=True,old_source_5b_unchanged=True,production_mutations=0,models_started=0,science_grants_added=0)
F.put(D/'CPU_SCOPE_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),source_sha256=report['library_source_sha256'],cpu_pid=os.getpid(),report=str(D/'CPU_SCOPE_QUALIFICATION.json'))))
