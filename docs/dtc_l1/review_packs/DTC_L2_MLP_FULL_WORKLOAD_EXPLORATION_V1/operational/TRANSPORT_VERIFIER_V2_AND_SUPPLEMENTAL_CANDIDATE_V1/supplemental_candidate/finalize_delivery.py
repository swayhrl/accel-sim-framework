import datetime,hashlib,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
cpu=read(HERE/'CPU_QUALIFICATION.json');support=read(HERE/'READONLY_SUPPORT_AUDIT.json');integration=read(HERE/'READONLY_INTEGRATION.json');plan=read(HERE/'CANDIDATE_PLAN.json')
assert cpu['status']=='PASS'and cpu['count']==26 and cpu['source_sha256']==sha(HERE/'supplemental_trial.py')
assert support['status']=='PASS_READONLY_NATIVE_SUPPORT_AND_LINEAGE'and integration['status']=='PASS_REAL_READONLY_SUPPLEMENTAL_INTERFACE_CHAIN'
assert integration['module_sha256']==sha(HERE/'supplemental_trial.py')and support['candidate_plan_sha256']==sha(HERE/'CANDIDATE_PLAN.json')==integration['plan_sha256']
assert support['R_new_spec_created']is False and support['existing_budget']==344
for pin in plan['source_and_evidence_pins']:assert sha(pin['path'])==pin['sha256']
files={p.name:dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in HERE.iterdir()if p.is_file()and p.name!='DELIVERY_MANIFEST.json'}
out=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_SCAN_M16_V1_DELIVERY',status='CPU26_AND_REAL_READONLY_QUALIFIED_NOT_REGISTERED_NOT_INSTALLED',
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,plan_sha256=sha(HERE/'CANDIDATE_PLAN.json'),
 proposed_cohort=plan['new_cohort'],role=plan['role'],proposed_new_grants=1,existing_grants=344,primary_cells=350,
 inference_contract='NO_PRIMARY_REPLACEMENT_NO_UNION_OR_PRIMARY_GM',
 known_limitation='Internal original-native global registry/epoch dual-write crash window remains HOLD requiring separate Main recovery; only before/after COMPLETE authority-update gap qualified',
 production_registry_grants=0,production_prepare_calls=0,production_installed=False,model_starts=0,signals=0,production_mutations=0)
(HERE/'DELIVERY_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],source_sha256=cpu['source_sha256'],plan_sha256=out['plan_sha256'],manifest_sha256=sha(HERE/'DELIVERY_MANIFEST.json'),cpu_checks=26)))
