"""Read-only real input/negative/IO qualification audit; writes E candidate only."""
import argparse,copy,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from supplemental_trial import OLD,NEW,OLD_UUID,ROLE,digest,scientific,validate_plan
from route_qualification import current_route,MEM
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
V=A/'agents/scan_m16_diagnosis_v1/terminal_verifier_v2/scan_m16_terminal_verifier_v2.py'
VPIN='9a023005a1847108dfb7e05ef0bacddbadcb7558766c5847bb08d2e2f678e673'
args=argparse.ArgumentParser();args.add_argument('--verifier-path');args.add_argument('--verifier-sha');parsed=args.parse_args()
assert bool(parsed.verifier_path)==bool(parsed.verifier_sha)
if parsed.verifier_path:V=P(parsed.verifier_path);VPIN=parsed.verifier_sha
B=A/'engineering_negative_evidence_v1'/OLD/'1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert sha(V)==VPIN;verified=load('supplemental_readonly_negative',V).verify_bundle(B,VPIN)
cert_path=P(verified['certificate']);cert=read(cert_path)
assert verified['performance_accepted']is False and verified['accepted_cycles']is None and cert['original_spent_starts']==1
assert verified['cohort']==OLD and verified['uuid']==OLD_UUID
e=load('supplemental_readonly_native',R/'tools/l2_native.py');_,_,q,execution_plan=e.registered();old=e.canonical(OLD)
assert q['consumed'][OLD]['uuid']==OLD_UUID and not q['consumed'][OLD].get('execution_receipt')and NEW not in q['admitted_specs']
matrix=read(R/'control/MATRIX_CURRENT.json');point=next(p for p in matrix['points']if p['cohort']==OLD)
io_path=R/'control/operational_amendments/io_actual_canary_v1/ACTUAL_IO_ROLLOUT_QUALIFICATION.json';io=read(io_path)
assert io['status']=='PASS_CANARY_ROLLOUT_READONLY_REPLAY'and io['production_release_eligible']is True and io['Main_approved_broad_future_admission_after_actual_canary']is True
cfg_path=R/'control/operational_amendments/shared_json_io_v1/ACTIVE_IO.json';cfg=read(cfg_path)
front=load('supplemental_readonly_IO_frontend',cfg['frontend_path']);front.validate(cfg,q)
assert front.parse(['experiment','prepare',NEW,'--project','DTC_L1'])==(['experiment','prepare',NEW,'--project','DTC_L1'],False)
route=current_route();route_path=HERE/'ROUTE_CPU_QUALIFICATION.json';route_qa=read(route_path)
assert route_qa['status']=='PASS'and route_qa['current_route']==route
assert io['source_and_route_pins']['/root/data/ep_l2_dtc_l1_native_v2/bin/native']==route['original_IO_qualified_entry_sha256']
lineage=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_TRIAL_LINEAGE_V1',role=ROLE,original_failed_cohort=OLD,original_uuid=OLD_UUID,
 original_failed_spec_sha256=sha(R/'control/specs'/(OLD+'.json')),negative_certificate_path=str(cert_path),negative_certificate_sha256=sha(cert_path),
 negative_verifier_path=str(V),negative_verifier_sha256=VPIN,IO_actual_qualification_path=str(io_path),IO_actual_qualification_sha256=sha(io_path),
 negative_verification_policy=verified.get('verification_policy'),original_v1_verifier_pass_claimed=verified.get('original_v1_verifier_pass_claimed'),
 original_producer_source_path=verified.get('original_producer_source_path'),original_producer_source_sha256=verified.get('original_producer_source_sha256'),
 IO_frontend_path=cfg['frontend_path'],IO_frontend_sha256=cfg['frontend_sha256'],
 native_entry_evidence=dict(route,qualification_path=str(route_path),qualification_sha256=sha(route_path),
  registration_callback='route_qualification.route_lineage_verifier'),
 trial_reason='Independent same-config performance trial after typed engineering negative; no repair validation identity reused',
 new_grants=1,refunds=0,reuse_old_UUID=False,primary_statistics_excluded=True,validated_union_authorized=False)
new=copy.deepcopy(old);new.update(cohort=NEW,scientific_role=ROLE,supplemental_trial_lineage=lineage)
newpoint=dict(point,cohort=NEW,scientific_role=ROLE)
pinmap={x['path']:x['sha256']for x in execution_plan['source_pins']}
for path in [cert_path,V,io_path,cfg_path,R/'control/specs'/(OLD+'.json'),R/'control/BUILD_PROFILE.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',P('/root/data/ep_l2_dtc_l1_native_v2/bin/native'),HERE/'supplemental_trial.py',HERE/'qualify_supplemental.py',HERE/'CPU_QUALIFICATION.json',P(__file__),HERE/'route_qualification.py',route_path,MEM/'memory_frontend.py',MEM/'native.before.sh',MEM/'ROUTER_ACTIVATED.json',MEM/'CPU_QUALIFICATION.json',MEM/'PUBLICATION_READBACK.json']:
 digest_file=sha(path)
 if str(path)in pinmap:assert pinmap[str(path)]==digest_file
 pinmap[str(path)]=digest_file
if verified.get('original_producer_source_path'):
 path=verified['original_producer_source_path'];assert sha(path)==verified['original_producer_source_sha256'];pinmap[path]=sha(path)
plan=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_TRIAL_PLAN_V1',role=ROLE,old_cohort=OLD,new_cohort=NEW,old_uuid=OLD_UUID,
 old_spec=old,new_spec=new,old_spec_sha256=digest(old),new_spec_sha256=digest(new),scientific_identity_sha256=digest(scientific(old)),
 new_point=newpoint,source_and_evidence_pins=[dict(path=p,sha256=h)for p,h in sorted(pinmap.items())],
 primary_scope_sha256=sha(R/'control/SCOPE.json'),execution_plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),
 native_support=dict(prefix_only_no_suffix_constraint=True,canonical_prepare_strict_outbox_dynamic_admitted=True,
  nonpadding_original_worker_and_existing_broad_IO_route=True,new_input=False,primary_statistics='UNCHANGED',newtrial_destination='SUPPLEMENTAL_ONLY'))
plan['native_support'].update(current_memory_route_excluded_for_new=True,fresh_registration_callback='route_qualification.route_lineage_verifier')
validate_plan(plan);(HERE/'CANDIDATE_PLAN.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
audit=dict(status='PASS_READONLY_NATIVE_SUPPORT_AND_LINEAGE',candidate_plan_sha256=digest(plan),new_cohort=NEW,
 old_spec_sha256=plan['old_spec_sha256'],new_spec_sha256=plan['new_spec_sha256'],effective_option_count=len(new['expected_options']),
 all_effective_options_identical=old['expected_options']==new['expected_options'],all_configs_identical=old['configs']==new['configs'],
 scientific_identity_sha256=plan['scientific_identity_sha256'],negative_verified=verified,IO_canary_cohort=io['cohort'],IO_qualified=True,
 current_native_route_evidence=route,
 primary_matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),primary_matrix_points=len(matrix['points']),existing_budget=q['budget'],
 R_new_spec_created=(R/'control/specs'/(NEW+'.json')).exists(),production_registry_grants=0,model_starts=0,signals=0,production_mutations=0)
(HERE/'READONLY_SUPPORT_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:audit[k]for k in ('status','candidate_plan_sha256','new_spec_sha256','effective_option_count','all_effective_options_identical','all_configs_identical','existing_budget','R_new_spec_created','production_registry_grants')}))
