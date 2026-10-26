"""Version the never-activated remaining4 resource binding and all dependent metadata."""
import pathlib,json,hashlib,copy,sys,re,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_remaining_failure_v1';N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,d,new=False):
 with P(p).open('x' if new else 'w') as f:json.dump(d,f,sort_keys=True,indent=2);f.write('\n')
def main(expected,parent_expected=None):
 assert re.fullmatch('[a-f0-9]{64}',expected);module=F/'ops/revision19/resource_accounting_v1.py';assert sha(module)==expected;reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');assert REQ not in reg['registered_future_requests'] and not list((R/'control/qualification_ledger').glob('*.INTENT.json'))
 pp=R/'control/REMAINING_BUILD_PROFILE_V1.json';ep=R/'control/EXECUTION_PLAN_V1.json';rp=R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';qp=R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json';ap=R/'control/SCIENCE_AUTHORIZATION.json';scope=R/'control/REMAINING_SCOPE_CANDIDATE_V1.json';old=read(pp);oldsha=old['resource_accounting_overlay']['sha256'];q=read(qp);assert oldsha!=expected and q['budget']==q['remaining']==4 and q['consumed']=={}
 if parent_expected is not None:assert re.fullmatch('[a-f0-9]{64}',parent_expected) and sha(old['parent_controller_path'])==parent_expected
 else:parent_expected=old['parent_controller_sha256'];assert sha(old['parent_controller_path'])==parent_expected
 pre=R/'control/draft_preimages'/('UNACTIVATED_RESOURCE_'+oldsha[:12]+'_BEFORE_'+expected[:12]);pre.mkdir(parents=True);saved=[]
 for path in sorted([*list((R/'control').glob('*.json')),*list((R/'control/specs').glob('*.json'))]):
  rel=path.relative_to(R/'control');dest=pre/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(path.read_bytes())
  assert sha(dest)==sha(path);saved.append({'canonical_path':str(path),'preimage_path':str(dest),'sha256':sha(path)})
 oldsrc=F/'ops/revision19/resource_accounting_e195_PRE_RACE_FIX_PREIMAGE.py';assert sha(oldsrc)==oldsha
 put(pre/'MANIFEST.json',{'schema':'UNACTIVATED_REMAINING4_RESOURCE_SUPERSESSION_PREIMAGES_V1','saved':saved,'old_resource_sha256':oldsha,'new_resource_sha256':expected,'old_parent_sha256':old['parent_controller_sha256'],'new_parent_sha256':parent_expected,'old_resource_source_preimage_path':str(oldsrc),'old_resource_source_preimage_sha256':sha(oldsrc),'budget':4,'actual_consumed':0,'registered':False,'model_starts':0},True)
 p=copy.deepcopy(old);p.update(resource_accounting_overlay={'path':str(module),'sha256':expected},parent_controller_sha256=parent_expected,continuation_fallback_frontend_sha256=sha(old['continuation_fallback_frontend_path']),status='R19_REVISED_PARENT_AND_RESOURCE_SOURCE_BOUND_CANDIDATE_NOT_REGISTERED_AT_FREEZE',unactivated_resource_preimage_manifest_path=str(pre/'MANIFEST.json'),unactivated_resource_preimage_manifest_sha256=sha(pre/'MANIFEST.json'))
 resource_paths={str(module),str(F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json'),str(F/'control/R19_CLOSED_SCOPE_CERTIFICATE_V1.json'),str(F/'ops/revision19/RESOURCE_ACCOUNTING_CPU_QUALIFICATION_V1.json')}
 for pin in p['additional_source_pins']:
  if pin['path'] in resource_paths:pin['sha256']=sha(pin['path'])
 put(pp,p);d=read(scope);d['parent_controller_sha256']=parent_expected;put(scope,d);specs=[];aliases={}
 for cell in q['admitted_specs']:
  sp=R/'control/specs'/(cell+'.json');s=read(sp);s['build_profile_sha256']=sha(pp);put(sp,s);alias=R/'control'/(cell+'_SPEC.json');alias.write_bytes(sp.read_bytes());specs.append({'cohort':cell,'path':str(sp),'sha256':sha(sp)});aliases[str(alias)]=sha(alias)
 plan=read(ep);plan.update(p);plan['build_profile_sha256']=sha(pp);plan['scope_sha256']=sha(scope)
 for pin in plan['source_pins']:
  if pin['path'] in resource_paths:pin['sha256']=sha(pin['path'])
  if pin['path'] in aliases:pin['sha256']=aliases[pin['path']]
  if pin['path']==p['continuation_fallback_frontend_path']:pin['sha256']=p['continuation_fallback_frontend_sha256']
 put(ep,plan);request=read(rp);request.update(specs=specs,execution_plan_sha256=sha(ep),scope_sha256=sha(scope));put(rp,request);auth=read(ap);auth['approval_request_sha256']=sha(rp);put(ap,auth);q.update(admitted_specs={r['cohort']:r['sha256'] for r in specs},execution_plan_sha256=sha(ep),spec_request_sha256=sha(rp),orchestrator_sha256=parent_expected);put(qp,q)
 # Preserve the qualified old-version CPU receipt as an explicit preimage.
 # The new proof uses exclusive-create and must actually run again.
 priorcpu=R/'control/REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json'
 if priorcpu.exists():assert sha(priorcpu)==next(x['sha256'] for x in saved if x['canonical_path']==str(priorcpu));priorcpu.unlink()
 receipt={'schema':'REMAINING4_UNACTIVATED_RESOURCE_METADATA_SUPERSESSION_RECEIPT_V1','status':'SUPERSEDED_UNACTIVATED_CANDIDATE_REQUIRES_NEW_CPU','old_resource_sha256':oldsha,'new_resource_sha256':expected,'parent_controller_sha256':p['parent_controller_sha256'],'preimage_manifest_path':str(pre/'MANIFEST.json'),'preimage_manifest_sha256':sha(pre/'MANIFEST.json'),'saved_count':len(saved),'profile_sha256':sha(pp),'plan_sha256':sha(ep),'request_sha256':sha(rp),'candidate_sha256':sha(qp),'authorization_sha256':sha(ap),'old_scopes_modified':False,'model_starts':0,'registry_or_entry_changes':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};dest=R/'control'/('UNACTIVATED_RESOURCE_SUPERSESSION_'+expected[:12]+'_V1.json');put(dest,receipt,True);print(json.dumps(dict(receipt,receipt_path=str(dest),receipt_sha256=sha(dest)),indent=2))
if __name__=='__main__':assert len(sys.argv) in [2,3];main(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None)
