from pathlib import Path
import json,hashlib,datetime
V=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');A=V/'activation_20261104_v1';C=A/'control'
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def exact(r):assert ref(r['path'])['sha256']==r['sha256'],r['path'];return read(r['path'])
def put(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 assert not p.exists(),'signed immutable review already exists; inspect not overwrite'
 p.write_text(json.dumps(x,indent=2)+'\n');return ref(p)
def base_review(p):
 x=read(p);source=x['source_identity'];auth=read(C/'USER_AUTHORIZATION.json');assert any(f['Source5']==source for f in auth['families'])
 for k in ['protocol_ref','actual282_ref','producer_evidence_ref','cpu_evidence_ref','fresh_formal_Host_evidence_ref','reused_engineering_evidence_ref']:
  if x.get(k):exact(x[k])
 for r in x.get('evidence_refs',{}).values():
  if isinstance(r,dict)and'path'in r:exact(r)
 for r in x.get('modules',[]):assert ref(r['path'])['sha256']==r['sha256'],r['path']
 x['status']=x.get('required_final_status',x.get('proposed_PASS_status'));assert x['status']
 x['approved_by']='EP-MAIN';x['Main_review_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();x['Main_user_authorization_ref']=ref(C/'USER_AUTHORIZATION.json');x['Main_reviewed_producer_draft_ref']=ref(p);x['new_application_acceptance']=False;x['application_NI']='NOT_MEASURED';x['scientific_acceptance_granted']=False
 return x
# Newgeometry Source78 mode proof: four actualproduction MS011/111 pairs and actual282.
ap=A/'agent_a_formal/review_drafts';am=base_review(ap/'MAIN_MODE_CPU_QUALIFICATION_DRAFT.json');ni=exact(am['protocol_ref']);echo=exact(am['actual282_ref']);assert len(ni['pairs'])==4 and all(p['PASS']for p in ni['pairs']);assert len(echo['runs'])==8 and all(r['exact282_PASS']for r in echo['runs'])
mode_a=put(C/'main_qualification/MIDTAG_MODE_CPU_QUALIFICATION.json',am)
# Source862 newW/WV strict receipt population is enforced by the frozen modecontract.
bp=A/'agent_b_formal/qualification/REVIEW_DRAFTS';bq=A/'agent_b_formal/qualification';bm=base_review(bp/'MODE_CPU_REVIEW.json');cpu=exact(bm['cpu_evidence_ref']);assert cpu['status']=='PASS'and cpu['models_started']==0 and len(cpu['pairs'])==6 and all(p['PASS']for p in cpu['pairs'])
mode_b=put(bq/'MODE_CPU_REVIEW.json',bm)
bi=base_review(bp/'INPUT_ELIGIBILITY.json');assert set(bi['modes_qualified'])=={'W_ONLY','WV_ZERO_RO'};old=bi['new_modeCPU_ref'];bi['prior_S_F_modeCPU_ref']=old;bi['new_modeCPU_ref']=mode_b;bi['RO_runtime_enabled_for_requested_modes']=False;bi['RO_certificate_authority_for_requested_modes']=False;bi['Main_review_scope']='Complete declared input/ordered kernels on exact Source862 W/WV, no original full hardware capture or numeric-output claim'
exact(bi['input_binding_ref']);exact(bi['new_sourceCPU_ref']);put(bq/'INPUT_ELIGIBILITY.json',bi)
br=base_review(bp/'S_F_REUSE_REVIEW.json');assert set(br['controls'])=={'S','F'}
for mode,row in br['controls'].items():
 pt=exact(row['accepted_point_ref']);s=exact(row['spec_ref']);ar=exact(row['archive_receipt_ref']);assert pt['cycles']==(45974 if mode=='S'else 55925) and pt['hardware_drained']
 assert pt['source_identity']==s['source_identity']==bm['source_identity'];assert s['expected_effective_options']['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:1700.0'
 assert ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and len(ar['native_restores'])==2
 assert all(r['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'for r in ar['native_restores'])
put(bq/'S_F_REUSE_REVIEW.json',br)
# Hostsourcegraph checks against the final immutable runtime files and qualified resource adapter.
resource=exact(ref(A/'agent_c_resources/CPU_RESOURCE_QUALIFICATION.json'));assert resource['status']=='PASS'and set(resource['qualified_global_EP_caps'])=={2,10}
for producer,destination in [(ap/'MAIN_HOST_QUALIFICATION_DRAFT.json',C/'main_qualification/MIDTAG_HOST_QUALIFICATION.json'),(bp/'HOST_QUALIFICATION.json',bq/'HOST_QUALIFICATION.json')]:
 x=base_review(producer);paths={r['path']for r in x['modules']};assert str(A/'agent_c_resources/resources_v3.py')in paths
 assert any(p.endswith('native_route_guard_v3.py')for p in paths)
 x['resource_qualification_ref']=ref(A/'agent_c_resources/CPU_RESOURCE_QUALIFICATION.json');x['Main_review_scope']='Exact new Source/mode runtime/parser/dependencygraph and dynamiccap2/cap10 adapter, not application acceptance or NI'
 put(destination,x)
print('Main signed A mode+Host, B mode+input+SFreuse+Host; no authority or models changed')
