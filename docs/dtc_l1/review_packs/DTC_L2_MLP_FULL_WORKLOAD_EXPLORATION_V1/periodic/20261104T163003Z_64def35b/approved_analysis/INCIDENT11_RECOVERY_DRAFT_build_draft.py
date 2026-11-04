"""One-to-one incident recovery identities. Own archive writes only; no grants."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,datetime,os
P=pathlib.Path;D=P(__file__).parent;A=D.parents[2];R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
INCIDENT='DTC_BPF_SCOPE_SELFLOCK_CADENCE_20261029_0031CST_V1'
ROLE='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('DRAFT_NO_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'DRAFT_WRITES_OWN_ROOT_ONLY'
sys.addaudithook(guard)
def raw(p):return P(p).read_bytes()
def read(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def pretty(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def compact(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):p=P(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def freeze(p,data):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert raw(p)==data,'EXISTING_DRAFT_IMMUTABLE '+str(p)
 else:p.write_bytes(data)
delta=A/'agents/A/results_independent_20261029_v2/DELTA.json';incident=A/'agents/B/bpf_install_cadence_incident_v1/READONLY_REVIEW.json';incident_manifest=incident.parent/'MANIFEST.json';mainplan=A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json'
live=[v for v in read(delta)['liveness_checks']if v['same_birth_live']is True];assert len(live)==11 and len({v['cohort']for v in live})==11
review=read(incident);evidence={v['cohort']:v for v in review['cohorts']};assert set(evidence)=={v['cohort']for v in live}
keys=read(mainplan)['science_keys'];q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];rows=[];members=[];sources=[pin(p)for p in [delta,incident,incident_manifest,mainplan,P(__file__)]]
for v in sorted(live,key=lambda x:x['cohort']):
 old=v['cohort'];new=old[:-3]+'-IR1-V1';assert old.endswith('-V1')and new not in q['admitted_specs']and new not in q['consumed']
 assert not(R/'control/qualification_ledger'/(new+'.INTENT.json')).exists()
 sp=R/'control/specs'/(old+'.json');rp=R/'analysis'/(old+'.RESULT.json');dp=R/'control/qualification_ledger'/(old+'.DONE.json');ip=dp.with_name(old+'.INTENT.json');s=read(sp);result=read(rp);done=read(dp);intent=read(ip);x=evidence[old]
 assert sha(sp)==q['admitted_specs'][old]and s['host_cpu']is None
 assert result['state']=='FAIL_L2MLP_ARCHIVED_NO_RETRY'and result['proof']['performance_accepted']is False and result['cycles']is None
 assert done==q['consumed'][old]['execution_receipt']and done['source_disposition']=='SOURCE_KEEP'and done['uuid']==result['uuid']==q['consumed'][old]['uuid']==x['uuid']
 assert done['stop_reason']=='DTC_ORIGINAL_RESOURCE_POLICY:INVALID_OR_MISSING_RESOURCE_SAMPLE_CADENCE'
 assert sha(rp)==x['RESULT']['sha256']and sha(dp)==x['DONE']['sha256']and(v['pid'],v['start_ticks'])==(x['pid'],x['start_ticks'])
 projection={k:s[k]for k in keys};science=compact(projection)
 lineage=dict(schema='DTC_INCIDENT_RECOVERY_TRIAL_LINEAGE_V1',incident_id=INCIDENT,incident_evidence_sha256=sha(incident),original_cohort=old,original_uuid=done['uuid'],original_pid=v['pid'],original_start_ticks=v['start_ticks'],original_canonical_spec_sha256=sha(sp),original_negative_RESULT_sha256=sha(rp),original_DONE_sha256=sha(dp),original_raw_sha256=done['raw_sha256'],original_raw_uncompressed_sha256=done['raw_uncompressed_sha256'],science_projection_sha256=science,new_grants=1,refunds=0,automatic_retry=False,reuse_old_UUID=False,primary_statistics_excluded=True,validated_union_authorized=False,original_performance_accepted=False,original_SOURCE_KEEP=True,trial_cycles=None,planned_grant_not_actual_authority=True)
 trial=dict(s,cohort=new,host_cpu=None,scientific_role=ROLE,incident_recovery_trial_lineage=lineage)
 assert compact({k:trial[k]for k in keys})==science and trial['expected_options']==s['expected_options']and trial['native_simulator_argv']==s['native_simulator_argv']
 allowed={'cohort','scientific_role','incident_recovery_trial_lineage'};changes={k for k in set(trial)|set(s)if trial.get(k)!=s.get(k)};assert changes<=allowed
 folder=D/'identities'/new;draft=folder/'DRAFT_SPEC.json';freeze(draft,pretty(trial))
 saved=[]
 for path,name in [(sp,'ORIGINAL_CANONICAL_SPEC.json'),(rp,'ORIGINAL_NEGATIVE_RESULT.json'),(dp,'ORIGINAL_DONE.json'),(ip,'ORIGINAL_INTENT.json')]:
  target=folder/name;freeze(target,raw(path));sources.append(pin(path));saved.append(pin(target));members.append(pin(target))
 members.append(pin(draft));rows.append(dict(original_cohort=old,new_cohort=new,program=s['program'],suite=s['suite'],cell=s['cell'],profile=s['profile'],input_digest=s['input_digest'],input_binding_sha256=s['input_binding_sha256'],Core=s['core_commit'],Framework=s['framework_commit'],binary_sha256=s['binary_sha256'],original_uuid=done['uuid'],original_pid=v['pid'],original_start_ticks=v['start_ticks'],original_negative_RESULT_sha256=sha(rp),original_DONE_sha256=sha(dp),original_raw_sha256=done['raw_sha256'],original_SOURCE_KEEP=True,original_performance_accepted=False,draft_spec=pin(draft),original_sources=saved,science_projection_sha256=science,full_expected_options_sha256=compact(s['expected_options']),expected_option_count=len(s['expected_options']),native_simulator_argv_sha256=compact(s['native_simulator_argv']),changed_fields=sorted(changes),all_nonallowed_fields_byte_semantically_equal=True,planned_new_grants=1,actual_new_grants=0,trial_cycles=None,primary_statistics_excluded=True,validated_union_authorized=False))
assert len(rows)==11 and len({r['new_cohort']for r in rows})==11
plan=dict(schema='DTC_INCIDENT11_INDEPENDENT_RECOVERY_TRIAL_DRAFT_V1',state='DRAFT_NOT_REGISTERED_NOT_STARTED_NOT_PRIMARY',incident_id=INCIDENT,selection_rule='Exactly DELTA.liveness_checks same_birth_live=True; deterministic old-cohort sort and one-to-one suffix IR1-V1; no selection by performance/cycles/PASS',mapping_count=11,scientific_role=ROLE,science_projection_keys=keys,science_projection_hash='SHA256 compact sorted JSON without newline',rows=rows,sources=sources,contract=dict(execution_authorization='Existing user Goal ordinary-engineering and explicit incident-recovery authorization',additional_per_trial_user_permission_required=False,official_independent_registration_and_full_resource_gates_required=True,all_original_negative_results_and_ledger_records_retained=True,canary4_engineering_first=True,union_into_effective35_GM_parent_or_adoption_requires_explicit_user_confirmation=True,primary_statistics_excluded=True,validated_union_authorized=False,default_observation_contract_unchanged=True,no_BPF_observation_adoption_in_this_draft=True,source_binary_input_270_options_and_native_simulator_argv_identical_to_each_original=True,future_resource_changes='Only later official forecast/limit amendment; science projection and complete lineage must stay fixed'),actual_new_grants=0,actual_model_starts=0,production_changes=0,registry_writes=0,original_350_matrix_writes=0,refunds=0,cycles_available=0)
freeze(D/'DRAFT_PLAN.json',pretty(plan));members.append(pin(D/'DRAFT_PLAN.json'));freeze(D/'SCIENCE_IDENTITY_PROOF.json',pretty(dict(schema='INCIDENT11_DRAFT_SCIENCE_PROOF_V1',status='PASS_READONLY_ONE_TO_ONE_IDENTITY_COPY_NOT_EXECUTION_QUALIFICATION',mapped11=True,all_11_science_projections_identical=True,all_11_full_options_and_native_argv_identical=True,all_11_canonical_host_cpu_None=True,changed_fields_allowlist=sorted(allowed),old_negatives_untouched=True,actual_models=0,actual_grants=0,per_cohort=[dict(new_cohort=r['new_cohort'],science_projection_sha256=r['science_projection_sha256'],expected_option_count=r['expected_option_count'],draft_spec_sha256=r['draft_spec']['sha256'])for r in rows])));members.append(pin(D/'SCIENCE_IDENTITY_PROOF.json'))
print(json.dumps(dict(plan=pin(D/'DRAFT_PLAN.json'),proof=pin(D/'SCIENCE_IDENTITY_PROOF.json'),members=members,count=11,source_script=pin(__file__))))
