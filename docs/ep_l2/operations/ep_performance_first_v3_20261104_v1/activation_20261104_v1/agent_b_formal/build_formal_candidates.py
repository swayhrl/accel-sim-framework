"""Main-invoked deterministic Vector2 runtime/spec materialization.
No registry, Native route, model fork or Git writes. Existing frozen specs never replaced.
"""
from pathlib import Path
import argparse,json,hashlib,sys,importlib.util
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
V=J/'research/performance_first_v3_20261104_v1';A=Path(__file__).resolve().parent;H=A/'runtime'
E=V/'agent_b_vector_modes';F=J/'execution_vector1700_decomposition_v3_20261104_v1/vector1700'
Q=A/'qualification';D=Q/'REVIEW_DRAFTS'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(d,indent=2,sort_keys=True)+'\n').encode()
 if p.exists() and p.read_bytes()==b:return
 p.write_bytes(b)
def module(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--resource-module',required=True);ap.add_argument('--resource-policy',required=True)
 ap.add_argument('--native-entry',required=True);ap.add_argument('--require-reviewed',action='store_true');ap.add_argument('--install-specs',action='store_true')
 args=ap.parse_args()
 guard=V/'activation_20261104_v1/agent_d_execution/native_route_guard_v3.py';safe=guard.with_name('safe_native_core_v3.py')
 assert sha(guard)=='9df2bab0058b571466998f71bfa487a929b6718a0d7e56d347746e98d6208ca9'
 assert sha(safe)=='6f6e149210e3e6d2308bf4c28e2e77c414639965d3804f750cb03205cca3de5d'
 native=ref(args.native_entry);res=ref(args.resource_module);pol=ref(args.resource_policy)
 auth=ref(F/'control/USER_AUTHORIZATION.json');parent=ref(V/'activation_20261104_v1/control/USER_AUTHORIZATION.json')
 assert read(auth['path'])['parent_authorization_ref']==parent
 sid=read(E/'specs/W_ONLY.json')['source_identity'];geo=read(E/'specs/W_ONLY.json')['geometry']
 modules=[ref(p)for p in H.rglob('*')if p.is_file()and '__pycache__'not in p.parts]
 modules.extend([ref(guard),ref(safe),res,pol])
 resources_common=Path(args.resource_module).with_name('resources_v3.py')
 modules.append(ref(resources_common))
 other_policy=Path(args.resource_policy).with_name('RESOURCE_POLICY_CAP2.json')
 if other_policy.exists() and str(other_policy)!=str(Path(args.resource_policy)):modules.append(ref(other_policy))
 # Drafts cannot pass formal contract. Main signs real files outside REVIEW_DRAFTS.
 host=dict(schema='EP_MAIN_VECTOR1700_W_WV_HOST_QUALIFICATION_V1',status='DRAFT_REQUIRES_MAIN_REVIEW',proposed_PASS_status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',approved_by=None,source_identity=sid,geometry=geo,modes_qualified=sorted(['W_ONLY','WV_ZERO_RO']),cohorts_qualified=sorted(['EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1','EP_PERF_PFV3_VECTOR4M_WV_ZERO_RO_1700_V1']),modules=modules,evidence_refs={'actual_controls':ref(E/'HOST_PARSER_NATIVE_ENGINEERING_CONTROLS.json'),'final_recheck':ref(E/'FINAL_MAIN_REVIEW_RECHECK.json'),'formal_scope_controls':ref(A/'FORMAL_HOST_NEGATIVE_CONTROLS.json'),'resource_CPU':ref(Path(args.resource_module).with_name('CPU_RESOURCE_QUALIFICATION.json'))},application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN')
 put(D/'HOST_QUALIFICATION.json',host)
 reviews={}
 for n in ['MODE_CPU_REVIEW.json','HOST_QUALIFICATION.json','INPUT_ELIGIBILITY.json','S_F_REUSE_REVIEW.json']:
  reviews[n]=ref(Q/n) if (Q/n).exists()else ref(D/n)
 mc=module('formal_vector_contract',H/'mode_contract.py');output=[]
 for mode in ['W_ONLY','WV_ZERO_RO']:
  s=read(E/'specs'/(mode+'.json'))
  # Formal immutable references use the common path+SHA shape; optional engineering bytes are metadata only.
  s['mode_cpu_qualification_ref']=ref(s['mode_cpu_qualification_ref']['path'])
  s.update(status='USER_APPROVED_PENDING_MAIN_NATIVE_ACTIVATION',approved_launches=1,launch_permission=True,scientific_scope_activated=True)
  s['scientific_option_contract']=dict(complete_282=True,formal_mode=mode,exact_Source5=s['source_identity'],only_declared_five_mode_switches_from_repaired_S1700=True,physical_resource_contract='FORMAL_S_VS_UNIFIED_W_PACKAGE_ROLE_DIFFERENCES_DISCLOSED')
  s['configuration_template_spec_ref']=s['proposal_reference_spec_ref']
  s['configuration_template_usage']='ACCEPTED_SAME_SOURCE_S1700_CONFIG_REFERENCE_NOT_NEW_MODE_ACCEPTANCE'
  s['REF850_usage']='NOT_APPLICABLE_REUSE_ACCEPTED_SOURCE862_S_F1700'
  s['service_family_point_id']='PFV3_VECTOR4M_'+mode+'_1700'
  s['service_family_proposal_ref']=ref(V/'main/EXACT_SCIENTIFIC_SCOPE_REQUEST.json')
  for k,n in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('postprocess_module_ref','ep_perf_postprocess.py'),('archive_module_ref','ep_perf_archive.py')]:s[k]=ref(H/n)
  s.update(mode_cpu_review_ref=reviews['MODE_CPU_REVIEW.json'],host_qualification_ref=reviews['HOST_QUALIFICATION.json'],eligibility_ref=reviews['INPUT_ELIGIBILITY.json'],matched_controls_review_ref=reviews['S_F_REUSE_REVIEW.json'],native_entry_ref=native,native_route_guard_ref=ref(guard),resource_module_ref=res,resource_policy_ref=pol,Main_scientific_launch_authorization=auth,parent_scientific_authorization_ref=parent)
  s['pinned_files']={r['path']:r['sha256']for r in modules}
  s['host_cpu']=None
  # Existing measured profile ~0.53GB, retain exact prior hard guards. Actual admission is dynamic.
  s['mode_qualification_boundary']='CPU_AND_HOST_REVIEW_ONLY_NOT_NEW_MODE_APPLICATION_ACCEPTANCE'
  s['application_NI']='NOT_MEASURED';s['B0_M0a_application_NI']='NOT_PROVEN'
  s['qualification_todo']=[]
  if args.require_reviewed or args.install_specs:
   mc.validate_static(s)
   el=read(s['eligibility_ref']['path']);assert el['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE'and el['approved_by']=='EP-MAIN'
  p=A/'specs'/(mode+'.json');put(p,s)
  if args.install_specs:
   target=F/'cases'/s['cohort']/'control/FROZEN_SPEC.json';target.parent.mkdir(parents=True,exist_ok=True)
   b=p.read_bytes()
   if target.exists():assert target.read_bytes()==b,'refuse overwrite different frozen spec'
   else:
    with target.open('xb')as f:f.write(b)
  output.append(dict(cohort=s['cohort'],mode=mode,spec_ref=ref(p),formal_spec_path=str(F/'cases'/s['cohort']/'control/FROZEN_SPEC.json')))
 manifest=dict(schema='EP_MAIN_VECTOR1700_FORMAL_INSTALL_BINDING_V1',request_id=s['science_request_id'],data_root=str(F),runtime_root=str(H),authorization_ref=auth,parent_authorization_ref=parent,Source5=sid,scope_budget=2,points=output,module_refs=modules,native_entry_ref=native,route_guard_ref=ref(guard),resource_module_ref=res,resource_policy_ref=pol,Main_reviews_required=True,real_registry_writes=0,global_native_writes=0,model_starts=0,installed_specs=args.install_specs)
 put(A/'FORMAL_INSTALL_MANIFEST.json',manifest);print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
