"""Actual Main-created bundle, actual current summary, read-only journal guard.
Only independent E evidence files are written. No registration/install/models.
"""
import datetime,hashlib,importlib.util,json,pathlib,sys,time
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from typed_analysis_view import project,recommend_from_bundles
from owner_recommend_adapter import make_owner_recommend
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
C='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';U='19105d9d-7522-498e-bf1d-73fbf7aba766'
TX='1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f'
VERIFIER=A/'agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py'
PIN='08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
path=R/'analysis/AUTO_SUMMARY.json'
rawbytes=path.read_bytes();raw=json.loads(rawbytes);scope=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json')
raw_identity=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()
p=next(p for p in scope['points']if p['cohort']==C);d=p['input_digest']
binding=dict(cohort=C,uuid=U,input_digest=d,cell='DH',profile='M16',bundle_path=str(A/'engineering_negative_evidence_v1'/C/TX),
 certificate_sha256='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7')
view,proof=project(raw,[binding],VERIFIER,PIN)
J=R/'control/operational_amendments/registry_journal_v1'
jmodule=load('actual_readonly_journal',J/'l2_registry_journal.py')
manifest=read(J/'DELIVERY_MANIFEST.json')['activation_manifest']
journal=jmodule.RegistryJournal(load('actual_readonly_registry',R/'tools/l2_registry.py'),load('actual_readonly_engine',R/'tools/l2_native.py'),manifest)
paths=dict(base=str(R/'tools/l2_adaptive.py'),supplement=str(A/'agents/E/boundary_validation_v2/l2_boundary_validation.py'))
pins={k:sha(p)for k,p in paths.items()}
base=load('actual_readonly_base_adaptive',paths['base']);v2=load('actual_readonly_supplement',paths['supplement'])
def prior_guarded_recommend(summary,matrix,search):
 return journal.guard_decision(v2.augment(base.recommend(summary,matrix,search),summary,matrix,search))
owner_wrapper=make_owner_recommend(prior_guarded_recommend,journal,paths,pins,[binding],VERIFIER,PIN)
result=owner_wrapper(raw,scope,history)
assert owner_wrapper.last_issue is None and owner_wrapper.existing_journal is journal
row=view['table'][d]['M16']['DH'];assert row['state']=='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'and not row['accepted']and row['cycles']is None
assert raw['table'][d]['M16']['DH']['state']!='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'
assert hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()==raw_identity
assert not result['scientific_stage_complete']and result['requires_engineering_review']
evidence=dict(status='PASS_REAL_BUNDLE_READONLY_INTEGRATION',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 verifier_path=str(VERIFIER),verifier_sha256=PIN,binding=binding,
 original_summary_path=str(path),original_summary_snapshot_sha256=hashlib.sha256(rawbytes).hexdigest(),original_summary_utc=raw.get('utc'),
 original_scan_row=raw['table'][d]['M16']['DH'],typed_scan_row=row,
 original_state_counts=raw.get('state_counts'),typed_analysis_view=view['typed_engineering_analysis_view'],
 adaptive_state=result['state'],proposals=result['proposals'],adoption_ready=result['adoption_ready'],scientific_stage_complete=result['scientific_stage_complete'],
 requires_engineering_review=result['requires_engineering_review'],registry_journal_status=result['registry_journal_status'],
 real_owner_factory_path_qualified=True,readonly_reinstantiated_journal_not_production_owner_object=True,
 source_pins=pins,verified_negative_proof=proof,source_sha256={n:sha(HERE/n)for n in ('typed_analysis_view.py','terminal_gate.py','owner_recommend_adapter.py')},
 production_installed=False,production_mutations=0,model_starts=0,signals_sent=0,registry_grants=0)
out=HERE/'REAL_BUNDLE_READONLY_INTEGRATION.json';out.write_text(json.dumps(evidence,indent=2)+'\n')
print(json.dumps({k:evidence[k]for k in ('status','utc','adaptive_state','adoption_ready','scientific_stage_complete','requires_engineering_review','registry_journal_status','source_sha256')}))
