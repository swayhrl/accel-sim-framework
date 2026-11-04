from pathlib import Path as P
import json,shutil,hashlib,re
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');V=J/'research/performance_first_v3_20261104_v1';A=V/'agent_a_mid_tag';ACT=V/'activation_20261104_v1';F=ACT/'agent_a_formal';R=ACT/'runtimes/midtag';DATA=J/'execution_midtag_v3_20261104_v1/midtag'
F.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True);(F/'spec_candidates').mkdir(exist_ok=True);(F/'review_drafts').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(P(p).read_text())
def put(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
for p in (A/'runtime_candidate').rglob('*'):
 if p.is_file()and'__pycache__'not in p.parts:
  q=R/p.relative_to(A/'runtime_candidate');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
# Contract now requires independent explicit Main reviews, not producer labels.
p=R/'mode_contract.py';t=p.read_text()
t=t.replace("q['status']=='PASS_MIDTAG_CPU_ENGINEERING_NOT_APPLICATION'","q['status']=='MAIN_REVIEWED_MIDTAG_MODE_CPU_PASS_NOT_APPLICATION'and q.get('approved_by')=='EP-MAIN'")
t=t.replace("q['status']=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'","q['status']=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'and q.get('approved_by')=='EP-MAIN'")
p.write_text(t)
# Parser still preserves frozen numeric body/suffix; bind only new mode mapper.
p=R/'mode_aware_terminal.py';t=p.read_text();oldhash=sha(A/'runtime_candidate/mode_contract.py');t=t.replace(repr(oldhash),repr(sha(R/'mode_contract.py')));p.write_text(t)
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text().replace(repr(oldhash),repr(sha(R/'mode_contract.py'))).replace(repr(sha(A/'runtime_candidate/mode_aware_terminal.py')),repr(sha(R/'mode_aware_terminal.py')))
needle="    need(authorization['goal'] == GOAL and authorization['user_request_ref'] == ref(ROOT/'control/USER_REQUEST.txt'), 'user authorization binding')\n"
assert needle in t
t=t.replace(needle,needle+"    need(authorization.get('explicit_user_approval')is True and authorization.get('approved_launches')==8 and authorization.get('allowed_cohorts')==sorted(ALLOWED_COHORTS),'fresh exact eight user scope approval')\n    need(authorization.get('source_identity')==s['source_identity'],'authorization Source5 binding')\n")
old="    need(ref(NATIVE/'bin/native')==route['global_shared_native_ref'],'global Native changed; exact route review required')\n"
assert old in t
t=t.replace(old,"    guard=module(route['guard_module_ref'],'midtag_formal_native_route_guard')\n    guard.validate_current(str(ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json'))\n")
p.write_text(t)
# Preserve generic frontend location rules; no formal frontend installation or global router changes.
specs=[]
for p in sorted((A/'spec_candidates').glob('*.json')):
 s=read(p);case=s['cohort'];overlay=R/'configs'/case/'final_midtag.config';overlay.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s['ordered_configs'][-1]['path'],overlay)
 s['ordered_configs'][-1]=ref(overlay)
 s.update(status='FORMAL_EXACT_SCOPE_PREPARATION_PENDING_MAIN_REVIEW_AND_SEAL',old_application_acceptance_inherited=False,launch_budget_registered=0,scientific_launch_permission=False,approved_launches=1,Main_review_status='PRODUCER_PENDING_EP_MAIN',application_budget_semantics='FRESH_USER_APPROVED_EXACT_ONE_START_REQUIRES_MAIN_REGISTRATION')
 s['native_entry_ref']=dict(path=str(DATA.parent/'bin/native_midtag_v3'),sha256='PENDING_MAIN_NATIVE_INSTALLATION')
 for key,name in [('host_common_ref','ep_perf_common_v2.py'),('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py'),('postprocess_module_ref','ep_perf_postprocess.py'),('archive_module_ref','ep_perf_archive.py')]:s[key]=ref(R/name)
 s['host_qualification_ref']=dict(path=str(F/'review_drafts/MAIN_HOST_QUALIFICATION.json'),sha256='PENDING_MAIN_REVIEW')
 s['mode_cpu_qualification_ref']=dict(path=str(F/'review_drafts/MAIN_MODE_CPU_QUALIFICATION.json'),sha256='PENDING_MAIN_REVIEW')
 s['resource_module_ref']=dict(path=str(ACT/'agent_c_resources/resources_midtag.py'),sha256='PENDING_RESOURCE_QUALIFICATION')
 s['resource_policy_ref']=dict(path=str(ACT/'agent_c_resources/RESOURCE_POLICY_CAP2.json'),sha256='PENDING_RESOURCE_QUALIFICATION')
 pins={k:v for k,v in s['pinned_files'].items()if '/env/lib/'in k or'/common-lib/'in k}
 for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py']:pins[str(R/n)]=sha(R/n)
 s['pinned_files']=pins;specs.append(s);put(F/'spec_candidates'/(case+'.json'),s)
source=specs[0]['source_identity']
mode=read(A/'evidence/MODE_CPU_CANDIDATE_QUALIFICATION.json');mode.update(schema='EP_MAIN_MIDTAG_FORMAL_MODE_CPU_QUALIFICATION_V1',status='PRODUCER_PASS_PENDING_MAIN_REVIEW',required_final_status='MAIN_REVIEWED_MIDTAG_MODE_CPU_PASS_NOT_APPLICATION',approved_by='PRODUCER_PENDING_EP_MAIN',profiles_qualified=['PFV3_MIDTAG_G32W16','PFV3_MIDTAG_G64W8'],modes_qualified=['S','WV_ZERO_RO'],producer_evidence_ref=ref(A/'BUNDLE_MANIFEST.json'),application_permission=False)
put(F/'review_drafts/MAIN_MODE_CPU_QUALIFICATION_DRAFT.json',mode)
host=dict(schema='EP_MAIN_MIDTAG_FAMILY_HOST_QUALIFICATION_V1',status='PRODUCER_PASS_PENDING_MAIN_REVIEW',required_final_status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',approved_by='PRODUCER_PENDING_EP_MAIN',source_identity=source,modules=[ref(R/n)for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py']],modes_qualified=['S','WV_ZERO_RO'],profiles_qualified=['PFV3_MIDTAG_G32W16','PFV3_MIDTAG_G64W8'],reused_engineering_evidence_ref=ref(A/'evidence/DRY_HOST_NATIVE_QUALIFICATION.json'),fresh_formal_Host_evidence_ref=dict(path=str(F/'FORMAL_DRY_HOST_RECEIPT.json'),sha256='PENDING_LOCAL_QUALIFICATION'),new_application_acceptance=False)
put(F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json',host)
put(F/'review_drafts/MAIN_SOURCE_INPUT_REUSE_REVIEW_DRAFT.json',dict(status='PRODUCER_PASS_PENDING_MAIN_REVIEW',approved_by='PRODUCER_PENDING_EP_MAIN',source_identity=source,prior_Source_readback_ref=ref(A/'evidence/SOURCE78_READBACK.json'),accepted_REF_reuse_ref=ref(A/'evidence/REF_AND_G64X16_REUSE_QUALIFICATION.json'),accepted_Source_qualification_refs=sorted({json.dumps(s['source_qualification_ref'],sort_keys=True)for s in specs}),input_eligibility_refs=[s['eligibility_ref']for s in specs],new_Core_or_ELF=False))
native=F/'native_midtag_v3';native.write_text("#!/usr/bin/env python3\nimport os,sys\nos.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'\nos.execv('/usr/bin/python3',['/usr/bin/python3',"+repr(str(R/'ep_perf_frontend.py'))+"]+sys.argv[1:])\n");native.chmod(0o755)
put(F/'PREPARATION_STATE.json',dict(status='FORMAL_RUNTIME_READY_PENDING_D_C_REFS_AND_MAIN_REVIEW',canonical_request_id='EP_L2_MID_TAG_850MHZ_V1_20261104',intended_data_root=str(DATA),runtime_root=str(R),scope_entry_candidate_ref=ref(native),target_scope_entry=str(DATA.parent/'bin/native_midtag_v3'),exact_cohorts=sorted(s['cohort']for s in specs),new_model_starts=0,real_registry_writes=0,global_native_writes=0))
print('formal runtime/specs copied; oldA immutable preserved')

