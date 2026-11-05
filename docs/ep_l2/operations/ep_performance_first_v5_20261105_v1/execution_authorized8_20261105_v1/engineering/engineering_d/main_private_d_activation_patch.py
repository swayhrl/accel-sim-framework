"""Main-only D private-graph metadata patch. Default DRYRUN; no science actors."""
from pathlib import Path
import json,hashlib,os,shutil,argparse,time,fcntl,sys
O=Path(__file__).resolve().parent
V=O.parent.parent
D=V/'track_d_workloads/three_mm'
E=D/'execution';H=D/'runtime'
BASE=O/'BASELINE_PRIVATE_GRAPH_PINS.json';BASE_SHA='cde3ef7149517057c75aac40100f1da668e9ce677a2907239f67d5885d540586'
OVERLAY=V/'main/resource_binding_v1/D/MAIN_EXACT_RESOURCE_OVERLAY.json'
MAINREF=V/'activation_20261105_v1/control/D_MAIN_HOST_DELTA_APPROVAL_REF.json'
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
REQUEST='EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=sha(p))
def exact(r):
 need(type(r)is dict and sha(r['path'])==r['sha256'],'immutable ref drift '+str(r));return read(r['path'])
def only_private(p):
 p=Path(p);need(p.is_absolute() and p.is_relative_to(D) and p.resolve()==p,'outside exact D private graph');return p
def unchanged_source_inputs(a,b):
 keys=['source_identity','binary_path','static_library_path','input_identity_sha256','input_binding_ref','eligibility_ref','expected_effective_options','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','geometry','observer_env','ordered_configs','mode','T','M','ro_qualification_ref']
 for k in keys:need(a.get(k)==b.get(k),'forbidden physics/input change '+k)
 need(len(b['expected_effective_options'])==282,'Source78 exact282')
 for k in ['RSS_bytes','AS_bytes','result_bytes']:need(a['limits'][k]==b['limits'][k],'non-wall limit change '+k)
 need(b['limits']['wall_seconds']==259200,'D hard72h')
def prepare():
 need(sha(BASE)==BASE_SHA,'patch baseline pin drift')
 baseline=read(BASE)
 for r in baseline['files']:need(sha(r['path'])==r['sha256'],'D private preimage drift '+r['path'])
 reg=read(REG);need(REQUEST not in reg['registered_future_requests'],'D already registered; immutable Specs cannot be patched')
 cp=E/'control/DISPATCH_CLAIMS.json';need(not cp.exists() or not read(cp)['claims'],'D claims already exist')
 for p in (E/'cases').glob('*/run/*'):raise ValueError('D run generation exists; patch forbidden')
 ov=read(OVERLAY);need(ov['request']==REQUEST and ov['source_identity']==read(ov['points'][0]['reviewed_base_ref']['path'])['source_identity'],'exact overlay request/Source')
 apref=read(MAINREF);approval=exact(apref);need(approval['schema']=='EP_MAIN_PFV5_HOST_RELEASE_DELTA_APPROVAL_V1' and approval['approved_by']=='EP-MAIN' and approval['explicit_user_approval']is True,'Main delta approval absent')
 need(approval['request_id']==REQUEST and approval['approved_launches']==3 and approval['independent_release']is True and approval['hard_wall_seconds']==259200,'D exact Main limits/scope')
 auth=exact(approval['fresh_user_authorization_ref']);parent=exact(approval['parent_authorization_ref'])
 need(auth['goal']==auth['request_id']==REQUEST and auth['Source5']==approval['Source5']==ov['source_identity'] and auth['explicit_user_approval']is True and auth['approved_launches']==3,'Main family authorization exact Source')
 cohorts=sorted(p['cohort']for p in ov['points'])
 need(auth['allowed_cohorts']==approval['allowed_cohorts']==cohorts and auth['per_cohort_budget']=={c:1 for c in cohorts},'exact independent D3')
 need(parent['approved_total_launches']==8 and parent['global_EP_model_cap']==10 and parent['all_eight_independently_released']is True and parent['WV_REF_completion_is_launch_gate']is False and parent['baseline_completion_is_launch_gate']is False,'parent exact8 independent scope')
 need(auth['independent_release']is True and auth['no_launch_completion_predecessor']is True and auth['automatic_retry']is False and auth['refund']is False and auth['source_keep']is True,'family no retry/KEEP/independent')
 need(auth['hard_wall_seconds']==259200 and auth['soft_wall_reference_seconds']=={'S':43200,'WV_ZERO_RO':50400},'hard/soft values')
 need(auth['user_request_ref']==ref(E/'control/USER_REQUEST.txt'),'Main own user request bytes')
 payload={}
 def add(path,value):payload[str(only_private(path))]=raw(value)
 request=read(E/'control/EXACT_REQUEST.json')
 request.update(status='MAIN_AUTHORIZED_EXACT_REQUEST3_PENDING_FORMAL_REGISTRATION',approved_starts=3,registered_starts=0,consumed_starts=0,independent_release=True,WV_REF_completion_is_launch_gate=False,hard_wall_seconds=259200,soft_wall_reference_seconds=auth['soft_wall_reference_seconds'],Main_scope_authorization_ref=approval['fresh_user_authorization_ref'])
 for p in request['exact_points']:
  rp=p['resource_proposal'];rp['soft_wall_reference_seconds']=rp['proposed_hard_wall_seconds'];rp['proposed_hard_wall_seconds']=259200
  rp['wall_contract']='Main-approved72h hard; prior12/14h are soft reference only. RAM/AS/RSS/output unchanged.'
 add(E/'control/EXACT_REQUEST.json',request)
 reqref=dict(path=str(E/'control/EXACT_REQUEST.json'),sha256=hashlib.sha256(payload[str(E/'control/EXACT_REQUEST.json')]).hexdigest())
 derived=dict(auth,request_ref=reqref,authoritative_family_authorization_ref=approval['fresh_user_authorization_ref'],Main_host_delta_approval_ref=apref,derived_by='MAIN_EXECUTION_OF_REVIEWED_PRIVATE_METADATA_PATCH',scientific_registration_here=False)
 add(E/'control/USER_AUTHORIZATION.json',derived)
 authref=dict(path=str(E/'control/USER_AUTHORIZATION.json'),sha256=hashlib.sha256(payload[str(E/'control/USER_AUTHORIZATION.json')]).hexdigest())
 host=exact(ov['host_ref']);modules={r['path']:dict(r)for r in host['modules']}
 for r in ov['native_owned_pin_additions']:need(sha(r['path'])==r['sha256'],'Main resource pin drift');modules[r['path']]=dict(r)
 for r in [apref,approval['fresh_user_authorization_ref'],approval['parent_authorization_ref'],authref,reqref]:modules[r['path']]=dict(r)
 host.update(modules=sorted(modules.values(),key=lambda z:z['path']),new_scientific_approval_required=False,Main_fresh_family_authorization_ref=authref,Main_host_delta_approval_ref=apref,hard_wall_seconds=259200,soft_wall_reference_seconds=auth['soft_wall_reference_seconds'],independent_release=True,scientific_registration_here=False)
 hp=E/'control/HOST_QUALIFICATION_MAIN_72H_RESOURCE_V5.json';add(hp,host);href=dict(path=str(hp),sha256=hashlib.sha256(payload[str(hp)]).hexdigest())
 specrows=[]
 for p in ov['points']:
  old=exact(p['reviewed_base_ref']);s=exact(p['selected_prospective_ref'])
  s['Main_scientific_launch_authorization']=authref;s['host_qualification_ref']=href
  s['limits']['wall_seconds']=259200;s['soft_wall_reference_seconds']=auth['soft_wall_reference_seconds'][s['mode']]
  s['Main_host_delta_approval_ref']=apref;s['independent_scientific_release']=True;s['WV_REF_completion_is_launch_gate']=False
  s['pinned_files'].update({r['path']:r['sha256']for r in host['modules']});s['pinned_files'][str(hp)]=href['sha256']
  unchanged_source_inputs(old,s)
  target=only_private(p['intended_future_formal_path']);add(target,s)
  specrows.append(dict(cohort=s['cohort'],target=str(target),preimage_ref=p['reviewed_base_ref'],prospective_sha256=hashlib.sha256(payload[str(target)]).hexdigest(),hard_wall=259200,soft_wall_reference=s['soft_wall_reference_seconds'],old_other_resources_unchanged=True))
 route=read(E/'control/NATIVE_ENTRY_ROUTE_V4.json');owned={r['path']:dict(r)for r in route['owned_runtime_pins']}
 for r in host['modules']+[href]:owned[r['path']]=dict(r)
 route.update(owned_runtime_pins=sorted(owned.values(),key=lambda z:z['path']),Main_resource_binding_overlay_ref=ref(OVERLAY),Main_host_delta_approval_ref=apref,independent_release=True)
 need(route['status']=='DRAFT_NOT_INSTALLED' and route['scientific_scope_activated']is False,'route already installed')
 add(E/'control/NATIVE_ENTRY_ROUTE_V4.json',route)
 # No production execution code changes are necessary: monitor reads Spec wall,
 # WV anchor returns UNKNOWN and no new-cell predecessor is required.
 mode=(H/'mode_contract.py').read_text();engine=(H/'ep_perf_native_wv_modes_draft.py').read_text()
 need("if mode=='WV_ZERO_RO':return dict(status='UNKNOWN_NO_ACCEPTED_3MM_WV_REF_NEW_ANCHOR_REQUESTED_NOT_YET_RUN',cycles=None" in mode,'WV missing-reference semantics drift')
 need("if elapsed > s['limits']['wall_seconds']:"in engine,'original hard-wall monitor not Spec-driven')
 key=hashlib.sha256(raw(dict(base=BASE_SHA,overlay=sha(OVERLAY),approval=apref,payload={p:hashlib.sha256(b).hexdigest()for p,b in payload.items()}))).hexdigest()[:20]
 plan=O/'plans'/key;plan.mkdir(parents=True,exist_ok=True)
 mapping=[]
 for target,data in payload.items():
  p=plan/'payload'/Path(target).relative_to(D);p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():need(p.read_bytes()==data,'immutable plan drift')
  else:p.write_bytes(data)
  mapping.append(dict(target=target,source=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),preimage_ref=ref(target)if Path(target).exists()else None))
 report=dict(schema='EP_MAIN_V5_D_PRIVATE_ACTIVATION_PATCH_PLAN_V1',status='DRYRUN_ONLY_PRIVATE_GRAPH_NOT_MODIFIED',plan_key=key,Main_delta_approval_ref=apref,resource_overlay_ref=ref(OVERLAY),exact_D3=specrows,files=mapping,no_production_code_change=True,original_monitor_AST_preserved=True,WV_REF_predecessor_removed_count=0,WV_REF_predecessor_explanation='No such predecessor exists in the frozen D producer/consumer; UNKNOWN reference remains legal. All8 dispatcher stage gates will be independently released.',scientific_registration_consumption_or_models=0,shared_Native_or_registry_modified=False)
 (plan/'PLAN.json').write_bytes(raw(report));return report,plan
def apply(report,plan):
 marker=O/'MAIN_PRIVATE_PATCH_APPLIED.json';need(not marker.exists(),'one-shot patch already applied')
 pre=O/'preimages'/report['plan_key'];pre.mkdir(parents=True,exist_ok=False)
 reg=read(REG);need(REQUEST not in reg['registered_future_requests'],'registered scope cannot be patched')
 for r in report['files']:
  p=only_private(r['target']);old=r['preimage_ref']
  need((p.exists() and old and sha(p)==old['sha256'])or(not p.exists() and old is None),'preimage transitioned')
 for r in report['files']:
  if r['preimage_ref']:
   p=Path(r['target']);save=pre/p.relative_to(D);save.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,save);need(sha(save)==r['preimage_ref']['sha256'],'preimage SHA copy')
 (pre/'PREIMAGES.json').write_bytes(raw(dict(plan_ref=ref(plan/'PLAN.json'),files=report['files'],no_original_bytes_discarded=True)))
 for r in report['files']:
  p=Path(r['target']);data=Path(r['source']).read_bytes();need(hashlib.sha256(data).hexdigest()==r['sha256'],'staged payload drift');p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.Main-private-patch')
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p);need(sha(p)==r['sha256'],'applied graph readback')
 out=dict(status='MAIN_EXECUTED_PRIVATE_D_GRAPH_PATCH_APPLIED_NO_NATIVE_INSTALL_REGISTRATION_OR_MODEL',plan_ref=ref(plan/'PLAN.json'),preimages=str(pre),installed=[dict(path=r['target'],sha256=r['sha256'])for r in report['files']],new_science_consumed=0,shared_Native_or_registry_modified=False)
 marker.write_bytes(raw(out));return out
def main():
 a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');v=a.parse_args()
 if (O/'MAIN_PRIVATE_PATCH_APPLIED.json').exists():
  need(not v.apply,'one-shot already applied');print(json.dumps(read(O/'MAIN_PRIVATE_PATCH_APPLIED.json')));return
 report,plan=prepare()
 if v.apply:
  with (O/'PRIVATE_D_PATCH.lock').open('a+b')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);out=apply(report,plan)
 else:out=dict(status=report['status'],plan_ref=ref(plan/'PLAN.json'),exact_D3=report['exact_D3'],production_code_changes=0,new_science_registered_consumed_models=0)
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
