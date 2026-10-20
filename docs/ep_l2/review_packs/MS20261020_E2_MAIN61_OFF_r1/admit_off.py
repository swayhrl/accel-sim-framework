"""Bind the published E source-specific control in the original registry, no launch."""
from pathlib import Path
import sys,json,time,subprocess,importlib.util,copy
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));import coordinator as c
coord=c.Coordinator();cp=P/'CHECKPOINT.json';s=json.loads(cp.read_text());source=s['source_identity'];binary=source['binary_sha256'];publication=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
for f in ['native_off_control.py','CHECKPOINT.json']:
 assert subprocess.check_output(['git','show',publication+':'+(P/f).relative_to(ROOT).as_posix()],cwd=ROOT)==(P/f).read_bytes()
with coord.locked() as (data,item):
 assert item['controller']['state']=='STOPPED' and item['actual_starts']==7
 assert not any(r['status'] in c.ACTIVE for k in ['runs','resource_leases'] for r in data[k].values())
 assert binary not in item['native_off_controls_by_binary']
 item.setdefault('producer_identity_history',[]).append(dict(at_unix=time.time(),final_source_identity=item['final_source_identity'],official_producer_current=item['official_producer_current'],independent_native_current=item['independent_native_current'],reason='E2 accepts formal A2 release; old main773 stays held'))
 r=json.loads((P/'PRODUCER_IDENTITY_REVIEW.json').read_text());item['final_source_identity']=source
 item['official_producer_current']=dict(**r['producer_release'],publication=r['producer_publication'],source_identity=source,E_independent_qualification=False,current_scientific_status='FORMAL_PRODUCER_ACCEPTED_SOURCE_SPECIFIC_OFF_AND_GATES_PENDING')
 item['independent_native_current']=dict(**s['independent_native_receipt'],actual_native_cases=17,terminal_expectations=26,source_identity=source,scope='E17 retained exact new archive; unaffected prior tests retained by explicit delta review',scientific_acceptance='OFF_AND_ORIGINAL11_PLUS7_REVIEW_PENDING')
 item['native_off_controls_by_binary'][binary]=dict(binding=dict(path=str(cp),sha256=c.digest(cp)),publication=publication,reason='A2 formal release accepted by E2; one necessary exact new-source OFF, original contingency3 includes this and Conv S/F; no refunds or budget expansion')
clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=json.loads(clientpath.read_text());c.write_json(P/'CLIENT_BEFORE.json',client)
client.setdefault('producer_history',[]).append({k:copy.deepcopy(client.get(k)) for k in ['formal_official_binary_sha256','producer_release_status','current_qualifications','current_partial_main_binary_sha256']})
client.update(formal_official_binary_sha256=binary,current_partial_main_binary_sha256=binary,A_source_candidate_received=source['core_source_commit'],A2_formal_release_publication=r['producer_publication'],producer_release_status='MAIN61_FORMAL_A2_RELEASE_E2_ACCEPTED_NEW_SOURCE_OFF_PENDING',current_qualifications=[])
client['native_off_qualification_controls_by_binary'][binary]=dict(checkpoint_path=str(cp),checkpoint_sha256=c.digest(cp),entry=str(P/'native_off_control.py'),entry_sha256=c.digest(P/'native_off_control.py'),git_path=(P/'native_off_control.py').relative_to(ROOT).as_posix(),publication_commit=publication,purpose='ONE_NEW_BINARY_ORIGINAL_OFF_GATE_ORIGINAL40_CONTINGENCY_NOT_PERFORMANCE',control_tests=5)
c.write_json(clientpath,client);c.write_json(P/'CLIENT_BOUND.json',client)
module=importlib.util.spec_from_file_location('off',P/'native_off_control.py');m=importlib.util.module_from_spec(module);module.loader.exec_module(m);m.preflight(s)
c.write_json(P/'ADMISSION.json',dict(status='PUBLISHED_SOURCE_AND_CLIENT_BOUND_PREFLIGHT_PASS_NO_START_YET',at_unix=time.time(),publication=publication,source_identity=source,checkpoint_sha256=c.digest(cp),CLIENT_sha256=c.digest(clientpath),actual_starts=coord.snapshot()['actual_starts']))
print('EXACT_OFF_PREFLIGHT_PASS_ORIGINAL7_STARTS')
