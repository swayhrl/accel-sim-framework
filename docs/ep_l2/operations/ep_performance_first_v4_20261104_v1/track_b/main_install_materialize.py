"""Main-only concrete materializer. Default --check is read-only; never writes shared Native/authority or starts models."""
from pathlib import Path
import argparse,json,hashlib,sys,os,copy
O=Path(__file__).resolve().parent;R=O/'private_runtime';ROOT=O/'private_execution/vector1700';N=Path('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';GOAL='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def need(v,m):
 if not v:raise ValueError(m)
def put(p,d):
 p=Path(p);b=(json.dumps(d,indent=2,sort_keys=True)+'\n').encode();p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():need(p.read_bytes()==b,'refuse different immutable destination '+str(p))
 else:
  with p.open('xb')as f:f.write(b)
def exact(r):need(sha(r['path'])==r['sha256'],'reference drift '+r['path']);return read(r['path'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--materialize',action='store_true');ap.add_argument('--main-install-binding');ap.add_argument('--scientific-authorization');ap.add_argument('--user-request');ap.add_argument('--registry-preimage-sha256');ap.add_argument('--shared-native-preimage-sha256');a=ap.parse_args()
 manifest=read(O/'IMMUTABLE_RUNTIME_PACKAGE.json')
 for r in manifest['files']:need(sha(r['path'])==r['sha256'],'runtime package drift '+r['path'])
 for r in read(O/'CURRENT_EXACT_DEPENDENCY_REOPEN.json')['rows']:need(sha(r['path'])==r['expected_sha256'],'current dependency drift '+r['path'])
 for r in read(O/'SOURCEKEEP_PREIMAGES.json')['untouched_refs']:need(sha(r['path'])==r['sha256'],'SOURCEKEEP preimage changed '+r['path'])
 prior=read(REG)['registered_future_requests']['EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104'];need(prior['remaining']==0 and len(prior['consumed'])==2 and prior['state']=='CLOSED_WITH_TECHNICAL_FAILURES','old failure closure changed')
 sys.path.insert(0,str(R));import runtime_monitor_schema_v4_strict as schema
 from ep_perf_native_wv_modes_draft import _SCHEMA_REFS
 specs=[read(O/'proposal/specs'/n)for n in ['W_ONLY.json','WV_ZERO_RO.json']]
 for s in specs:schema.validate_spec_contract(s,**_SCHEMA_REFS,check_current_domain=True,check_current_dependencies=True)
 if not a.materialize:print(json.dumps(dict(status='MAIN_INSTALL_PREIMAGE_CHECK_PASS_NO_WRITES',package_ref=ref(O/'IMMUTABLE_RUNTIME_PACKAGE.json'),fresh_request_registered=GOAL in read(REG)['registered_future_requests'],current_registry_sha256=sha(REG),current_shared_native_sha256=sha(N/'bin/native'),scientific_authorization=False,model_starts=0)));return
 need(all([a.main_install_binding,a.scientific_authorization,a.user_request,a.registry_preimage_sha256,a.shared_native_preimage_sha256]),'materialize requires concrete Main binding, fresh science approval/user request and exact current preimages')
 need(sha(REG)==a.registry_preimage_sha256 and sha(N/'bin/native')==a.shared_native_preimage_sha256,'authority/shared Native preimage drift; refresh Main preimage review')
 need(GOAL not in read(REG)['registered_future_requests'],'fresh request already exists')
 bind=read(a.main_install_binding);auth=read(a.scientific_authorization);cohorts=sorted(s['cohort']for s in specs)
 need(bind.get('approved_by')=='EP-MAIN'and bind.get('status')=='MAIN_INSTALL_BINDING_ACCEPTED'and bind.get('runtime_package_ref')==ref(O/'IMMUTABLE_RUNTIME_PACKAGE.json')and bind.get('delta_receipt_ref')==ref(O/'delta_fixture_v4/DELTA_INTEGRATION_RECEIPT.json')and bind.get('final_engine_equivalence_ref')==ref(O/'FINAL_ENGINE_FIXTURE_EQUIVALENCE.json'),'Main exact installation binding absent')
 need(bind.get('shared_native_candidate_ref')==ref(O/'SHARED_NATIVE_ADDITIVE_CANDIDATE.sh'),'Main exact additive Native candidate review absent')
 need(auth.get('schema')=='EP_MAIN_PFV4_SCOPED_USER_AUTHORIZATION_V1'and auth.get('explicit_user_approval')is True and auth.get('goal')==GOAL and auth.get('approved_launches')==2 and auth.get('allowed_cohorts')==cohorts and auth.get('Source5')==specs[0]['source_identity'],'fresh exact scientific approval absent')
 parent=exact(auth['parent_authorization_ref']);need(parent.get('explicit_user_approval')is True and parent.get('old_budgets_reusable')is False and parent.get('additional_NI')==0,'new parent scope/no old budget permission absent')
 usertarget=ROOT/'control/USER_REQUEST.txt';need(auth.get('user_request_ref')==dict(path=str(usertarget),sha256=sha(a.user_request)),'user transcript/final native-root binding')
 need(sha(N/'bin/native')==read(O/'SHARED_NATIVE_PREIMAGE.json')['sha256'],'Native candidate based on different preimage; rematerialize additive candidate for Main review')
 usertarget.parent.mkdir(parents=True,exist_ok=True)
 if usertarget.exists():need(usertarget.read_bytes()==Path(a.user_request).read_bytes(),'user transcript immutable destination drift')
 else:
  with usertarget.open('xb')as f:f.write(Path(a.user_request).read_bytes())
 authpath=ROOT/'control/USER_AUTHORIZATION.json';put(authpath,auth)
 host=read(O/'proposal/HOST_INTEGRATION_BINDING_CANDIDATE.json');host.update(status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',approved_by='EP-MAIN',Main_install_binding_ref=ref(a.main_install_binding));host['evidence_refs'].update(delta=ref(O/'delta_fixture_v4/DELTA_INTEGRATION_RECEIPT.json'),routing=ref(O/'routing_stage_delta/ROUTING_DELTA_RECEIPT.json'),current_dependencies=ref(O/'CURRENT_EXACT_DEPENDENCY_REOPEN.json'),final_engine_equivalence=ref(O/'FINAL_ENGINE_FIXTURE_EQUIVALENCE.json'),staged_release=ref(O/'routing_stage_delta/STAGED_RELEASE_DELTA_RECEIPT.json'))
 hostpath=ROOT/'control/HOST_QUALIFICATION.json';put(hostpath,host)
 from mode_contract import validate_static
 admitted={}
 for s in specs:
  s=copy.deepcopy(s);s.update(status='USER_APPROVED_MAIN_BOUND_FRESH_V4',launch_permission=True,scientific_scope_activated=True,Main_scientific_launch_authorization=ref(authpath),parent_scientific_authorization_ref=auth['parent_authorization_ref'],host_qualification_ref=ref(hostpath))
  schema.validate_spec_contract(s,**_SCHEMA_REFS,check_current_domain=True,check_current_dependencies=True);validate_static(s)
  p=ROOT/'cases'/s['cohort']/'control/FROZEN_SPEC.json';put(p,s);admitted[s['cohort']]=sha(p)
 # New route baseline is the complete exact additive candidate, preserving every existing Native byte.
 contractpath=ROOT/'control/SHARED_ROUTE_CONTRACT_V4.json';put(contractpath,dict(schema='EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1',installed_baseline_ref=ref(O/'SHARED_NATIVE_ADDITIVE_CANDIDATE.sh'),reviewed_foreign_insertions=[],Main_install_binding_ref=ref(a.main_install_binding),previous_shared_native_ref=read(O/'SHARED_NATIVE_PREIMAGE.json')))
 route=read(O/'routing_stage_delta/SYNTHETIC_PRIVATE_ROUTE_NO_SCIENCE_AUTHORITY.json');route.pop('TEST_ONLY',None);route.pop('scope',None);route.update(goal=GOAL,Main_user_authorization_ref=ref(authpath),shared_route_contract_ref=ref(contractpath),global_shared_native_ref=dict(path=str(N/'bin/native'),sha256=sha(O/'SHARED_NATIVE_ADDITIVE_CANDIDATE.sh')),formal_Native_CPU_Host_qualification_ref=ref(O/'delta_fixture_v4/DELTA_INTEGRATION_RECEIPT.json'))
 routepath=ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json';put(routepath,route)
 row=dict(request=GOAL,owner='EP-MAIN',project='EP_L2',budget=2,remaining=2,consumed={},admitted_specs=admitted,runtime_versions={specs[0]['host_engine_ref']['sha256']:dict(engine_ref=specs[0]['host_engine_ref'],common_ref=specs[0]['host_common_ref'])},authorization_ref=ref(authpath),parent_authorization_ref=auth['parent_authorization_ref'],source_identity=specs[0]['source_identity'],allowed_cohorts=cohorts,native_entry_ref=ref(R/'native_vector1700_v4'),native_qualification_ref=ref(routepath),state='REGISTERED_NOT_LAUNCHED',resource_group_id=GOAL,reserved_write_bytes=0,source_keep=True,automatic_retry=False,refund=False,global_model_concurrency_authorized=10,global_model_concurrency_qualified=10)
 put(ROOT/'control/MAIN_ATOMIC_ACTIVATION_PAYLOAD.json',dict(new_registry_row_only=row,registry_preimage_sha256=a.registry_preimage_sha256,shared_native_preimage_sha256=a.shared_native_preimage_sha256,shared_native_candidate_ref=ref(O/'SHARED_NATIVE_ADDITIVE_CANDIDATE.sh'),requirements=['Main sole atomic registry+epoch accounting addition under REGISTRY_UPDATE.lock; preserve all foreign rows and original consumed2','Main reviews compatibility of any active existing Native route guards before byte-exact additive install','Main sole dispatcher resource admission; no second dispatcher','prepare both; release W_ONLY first; WV only after accepted/archive/two independent restores'],model_starts=0))
 print(json.dumps(dict(status='MAIN_PRIVATE_INSTALL_MATERIALIZED_NO_AUTHORITY_ROUTE_WRITE_NO_START',payload_ref=ref(ROOT/'control/MAIN_ATOMIC_ACTIVATION_PAYLOAD.json'))))
if __name__=='__main__':main()
