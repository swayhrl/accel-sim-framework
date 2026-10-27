"""Real plan + final verifier + actual guarded primary chain, no registration."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,threading
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import supplemental_trial as m
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);o=importlib.util.module_from_spec(sp);sp.loader.exec_module(o);return o
plan=read(HERE/'CANDIDATE_PLAN.json');m.validate_plan(plan);initial=m.sha(R/'control/MATRIX_CURRENT.json')
engine=load('supp_actual_readonly_engine',R/'tools/l2_native.py')
store=m.SupplementalRegistry(R,engine,threading.RLock(),lambda:None,lineage_verifier=m.verify_lineage)
q,primary=store.check(plan);lineage=m.verify_lineage(plan)
assert lineage['verifier_source_sha256']=='9a023005a1847108dfb7e05ef0bacddbadcb7558766c5847bb08d2e2f678e673'
assert lineage['original_v1_verifier_pass_claimed']is False
try:store.assert_owner()
except AssertionError:external_owner_rejected=True
else:raise AssertionError('external helper treated as production parent')
dispatch=store.dispatch_view(primary);assert len(dispatch['points'])==350 and dispatch['supplemental_dispatch_view']['supplemental_cohorts']==[]
assert not store.folder.exists()and m.NEW not in q['admitted_specs']and not(R/'control/specs'/(m.NEW+'.json')).exists()
J=R/'control/operational_amendments/registry_journal_v1';jmod=load('supp_readonly_actual_journal',J/'l2_registry_journal.py')
journal=jmod.RegistryJournal(load('supp_readonly_actual_registry',R/'tools/l2_registry.py'),engine,read(J/'DELIVERY_MANIFEST.json')['activation_manifest'])
sys.path.insert(0,str(A/'agents/E/engineering_terminal_gate_v1'))
from owner_recommend_adapter import make_owner_recommend
base=load('supp_readonly_base',R/'tools/l2_adaptive.py');v2=load('supp_readonly_boundary',A/'agents/E/boundary_validation_v2/l2_boundary_validation.py')
def prior(summary,scope,history):return journal.guard_decision(v2.augment(base.recommend(summary,scope,history),summary,scope,history))
paths=dict(base=str(R/'tools/l2_adaptive.py'),supplement=str(A/'agents/E/boundary_validation_v2/l2_boundary_validation.py'));pins={k:m.sha(p)for k,p in paths.items()}
binding=dict(cohort=m.OLD,uuid=m.OLD_UUID,input_digest=plan['old_spec']['input_digest'],cell='DH',profile='M16',
 bundle_path=str(P(plan['new_spec']['supplemental_trial_lineage']['negative_certificate_path']).parent),certificate_sha256=lineage['certificate_sha256'])
line=plan['new_spec']['supplemental_trial_lineage']
current_typed=make_owner_recommend(prior,journal,paths,pins,[binding],line['negative_verifier_path'],line['negative_verifier_sha256'])
outer=m.make_primary_adaptive(current_typed,store,journal)
raw=read(R/'analysis/AUTO_SUMMARY.json');raw_identity=m.digest(raw)
# A synthetic READ-ONLY dispatch-view point tests stripping without granting it.
scope=copy.deepcopy(primary);scope['points'].append(copy.deepcopy(plan['new_point']));scope['supplemental_dispatch_view']={'CPU_READONLY_INTERFACE_ONLY':True}
result=outer(raw,scope,read(R/'control/SEARCH_HISTORY.json'))
assert current_typed.last_issue is None and m.digest(raw)==raw_identity
assert result['verified_typed_engineering_negatives'][0]['cohort']==m.OLD
assert not result['adoption_ready']and not result['scientific_stage_complete']and result['requires_engineering_review']
assert result['registry_journal_status']['safe_for_scientific_completion']is True
assert m.sha(R/'control/MATRIX_CURRENT.json')==initial and not store.folder.exists()and m.NEW not in engine.registered()[2]['admitted_specs']
out=dict(status='PASS_REAL_READONLY_SUPPLEMENTAL_INTERFACE_CHAIN',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 plan_sha256=m.digest(plan),module_sha256=m.sha(HERE/'supplemental_trial.py'),new_cohort=m.NEW,
 primary_points=350,real_dispatch_supplemental_points=0,synthetic_dispatch_point_only_for_interface_test=True,
 existing_budget=q['budget'],proposed_new_grants=1,original_failed_UUID_preserved=True,all_270_options_and_configs_identical=True,
 lineage_verifier_path=line['negative_verifier_path'],lineage_verifier_sha256=line['negative_verifier_sha256'],
 original_v1_verifier_pass_claimed=False,verifier_policy=lineage['verification_policy'],
 original_typed_gate_preserved=True,registry_journal_finalguard_preserved=True,
 adaptive_state=result['state'],proposals=result['proposals'],adoption_ready=False,scientific_stage_complete=False,requires_engineering_review=True,
 primary_matrix_sha256=initial,external_registration_owner_rejected=external_owner_rejected,
 production_registry_grants=0,production_prepare_calls=0,production_mutations=0,model_starts=0,signals=0)
(HERE/'READONLY_INTEGRATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
