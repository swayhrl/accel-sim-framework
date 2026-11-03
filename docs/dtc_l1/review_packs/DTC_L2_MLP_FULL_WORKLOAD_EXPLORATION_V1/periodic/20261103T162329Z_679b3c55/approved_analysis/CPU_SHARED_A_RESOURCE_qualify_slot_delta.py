"""Two offline slot boundaries; not scope extension or authority qualification."""
import pathlib,json,copy,importlib.util,hashlib
P=pathlib.Path;D=P(__file__).parent
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
fx=load('shared_slot_private_unit',D/'cpu_fixture.py');f=fx.fixture();lib=f.lib;cfg=copy.deepcopy(f.cfg);cfg['allowed_cohorts'].append('CPU_OFFLINE_FUTURE_SLOT_ONLY');other=cfg['allowed_cohorts'][-1];e=f.inputs()['slot_evidence'];e['allowed_cohorts']=sorted(cfg['allowed_cohorts']);claims=json.loads(e['claims_utf8']);claims['claims'][other]={'host_cpu':1,'cpu_shared_timeslice_overlay_id':lib.ID};e['claims_utf8']=lib.js(claims).decode();e['claims_sha256']=hashlib.sha256(e['claims_utf8'].encode()).hexdigest();e['other_shared_reservations']=[dict(cohort=other,kind='SHARED_UNSPENT_OR_MODEL_CLAIM')];e['prospective_shared_count']=2
def rejects(e):
 try:lib.verify_slot_evidence(e,cfg,f.c,0)
 except Exception as x:return str(x)
 raise AssertionError('slot must refuse')
cap=rejects(e);bad=copy.deepcopy(e);bad['other_shared_reservations']=[];bad['prospective_shared_count']=1;omission=rejects(bad)
e=f.inputs()['slot_evidence'];e['allowed_cohorts']=sorted(cfg['allowed_cohorts']);e['consumed_inspections'].append(dict(cohort=other,row={'uuid':'CPU_ALREADY_CONSUMED_NO_DONE'},INTENT_utf8=lib.js(dict(cohort=other,uuid='CPU_ALREADY_CONSUMED_NO_DONE',output='CPU_MISSING_PID',**{lib.FIELD:{'schema':lib.ID}})).decode(),DONE_utf8=None));e['other_shared_reservations']=[dict(cohort=other,kind='SHARED_CONSUMED_AWAITING_JOINED_DONE',generation_observation={'missing':True})];e['prospective_shared_count']=2;gone=rejects(e)
proof=dict(schema='CPU_SHARED_SLOT_BOUNDARY_DELTA_V1',status='PASS',source_sha256=sha(lib.__file__),driver_sha256=sha(__file__),base20_path=str(D/'CPU_RESOURCE_QUALIFICATION.json'),base20_sha256=sha(D/'CPU_RESOURCE_QUALIFICATION.json'),checks=[dict(name='second_shared_claim_cap2_and_omission_rejected',status='PASS',cap_rejection=cap,omitted_rejection=omission),dict(name='known_shared_consumed_missingDONE_gonePID_not_refunded',status='PASS',rejection=gone)],fixture_note='Pure slot arithmetic uses a two-cohort shape; full cfg validator intentionally not invoked. This does NOT authorize broad initial scope, real registration or another identity.',models_started=0,new_grants=0,production_mutations=0)
(D/'CPU_SLOT_BOUNDARY_DELTA.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(source_sha256=sha(lib.__file__),delta_sha256=sha(D/'CPU_SLOT_BOUNDARY_DELTA.json'),checks=2)))
