"""Explicit unspent R13->R14 metadata supersession; no registry/entry writes."""
import pathlib,json,hashlib,datetime,os,copy,importlib.util,ast
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation';N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';NEW=F/'ops/revision14/sweep_controller.py';NEW_SHA='e33951d0d53677681e422a4e28005327e0b33c4492a1eb7fc02121daa492e413'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def atomic(path,obj):
 path=P(path);data=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
 if path.exists() and path.read_bytes()==data:return
 temp=path.with_name(path.name+'.R14_METADATA_SUPERSESSION')
 with temp.open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
 temp.replace(path)
def main():
 assert sha(NEW)==NEW_SHA;proof=read(R/'control/REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json');assert proof['status']=='PASS' and proof['positive_count']==23 and proof['real_model_or_component_processes_forked']==0;current=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQ];assert not current['consumed'] and current['remaining']==23 and not list((R/'control/qualification_ledger').glob('*.INTENT.json'));entry_sha=sha(N/'bin/native')
 backup=R/'control/draft_preimages/R13_REGISTERED_ZERO_START_BEFORE_R14';backup.mkdir(parents=True,exist_ok=False);paths=[R/'control/REPAIR_BUILD_PROFILE_V1.json',R/'control/EXECUTION_PLAN_V1.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',R/'control/SCIENCE_AUTHORIZATION_CANDIDATE.json',R/'control/SCIENCE_AUTHORIZATION.json',*sorted((R/'control/specs').glob('*.json')),*sorted((R/'control').glob('OPERATIONAL_OUTPUT_CAP_E2-AEREPAIR-*.json'))];assert len(paths)==52;old=[]
 for source in paths:
  dest=backup/source.relative_to(R/'control');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes());old.append({'path':str(source),'old_sha256':sha(source),'preimage':str(dest)})
 prior_auth=read(R/'control/SCIENCE_AUTHORIZATION.json');p=read(R/'control/REPAIR_BUILD_PROFILE_V1.json');p['parent_controller_path']=str(NEW);p['parent_controller_sha256']=NEW_SHA;existing={r['path'] for r in p['additional_source_pins']}
 for path in [R/'tools/qualify_repair_native_pre_popen_v1.py',R/'control/COMPAT_SPEC_LAYOUT_FIX_ZERO_START_V1.json',R/'control/REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json',P(__file__)]:
  if str(path) not in existing:p['additional_source_pins'].append({'path':str(path),'sha256':sha(path)})
 assert not any(row['path'].endswith('_SPEC.json') for row in p['additional_source_pins']),'alias/spec pins cannot enter profile hash cycle';atomic(R/'control/REPAIR_BUILD_PROFILE_V1.json',p)
 spec=importlib.util.spec_from_file_location('unspent_R14_metadata_only_original_builder',R/'tools/repair_prepare_specs_v1.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
 def put(path,value):
  if P(path)==R/'control/EXECUTION_PLAN_V1.json':
   value=copy.deepcopy(value);aliases=[]
   for canonical in sorted((R/'control/specs').glob('*.json')):
    alias=R/'control'/(canonical.stem+'_SPEC.json');assert alias.is_symlink() and alias.read_bytes()==canonical.read_bytes();aliases.append({'path':str(alias),'sha256':sha(alias)})
   assert len(aliases)==23;value['source_pins']+=aliases;value['compatibility_spec_alias_pins']=aliases;value['inherited_native_hardcoded_spec_layout_explicitly_bound']=True
  atomic(path,value)
 builder.put=put;builder.main();request_sha=sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');new_auth=dict(prior_auth,approval_request_sha256=request_sha);assert new_auth['budgets']==prior_auth['budgets'] and set(new_auth['budgets'].values())=={1};atomic(R/'control/SCIENCE_AUTHORIZATION.json',new_auth)
 assert all(new_auth[k]==v for k,v in prior_auth.items() if k!='approval_request_sha256');source=Tsource=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');tree=ast.parse(source.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_native');segment=ast.get_source_segment(source.read_text(),fn);assert "sha(ROOT/'control'/(cohort+'_SPEC.json'))" in segment
 aliases=[];q=read(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');plan=read(R/'control/EXECUTION_PLAN_V1.json')
 for cell,digest in sorted(q['admitted_specs'].items()):
  alias=R/'control'/(cell+'_SPEC.json');canonical=R/'control/specs'/(cell+'.json');assert sha(alias)==sha(canonical)==digest and {'path':str(alias),'sha256':digest} in plan['source_pins'];aliases.append({'cohort':cell,'alias':str(alias),'canonical':str(canonical),'sha256':digest})
 for row in old:assert sha(row['preimage'])==row['old_sha256'];row['new_sha256']=sha(row['path'])
 assert sha(N/'bin/native')==entry_sha and not read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQ]['consumed'];receipt={'schema':'DTC_REGISTERED_BUT_ZERO_START_REPAIR_METADATA_R14_SUPERSESSION_V1','status':'R14_CANDIDATE_READY_AUTH_TEXT_PRESERVED_NO_LEDGER_OR_ENTRY_CHANGE','preserved_preimages':old,'new_parent_path':str(NEW),'new_parent_sha256':NEW_SHA,'new_profile_sha256':sha(R/'control/REPAIR_BUILD_PROFILE_V1.json'),'new_plan_sha256':sha(R/'control/EXECUTION_PLAN_V1.json'),'new_request_sha256':request_sha,'new_registry_candidate_sha256':sha(R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json'),'new_authorization_sha256':sha(R/'control/SCIENCE_AUTHORIZATION.json'),'authorization_only_approval_request_sha256_changed':True,'aliases':aliases,'aliases_pinned_only_in_plan_after_spec_creation':True,'inherited_native_source_sha256':sha(source),'inherited_native_run_native_function_AST_sha256':hashlib.sha256(ast.dump(fn,include_attributes=False).encode()).hexdigest(),'native_compatibility_path_expression':"sha(ROOT/'control'/(cohort+'_SPEC.json'))",'real_registry_changed':False,'entry_changed':False,'new_models_started':0,'original_scientific_assets_changed':False,'existing_engineering_RESULTS_not_moved_by_this_tool':True,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};path=R/'control/R14_METADATA_SUPERSESSION_AND_ALIAS_BINDING_V1.json';assert not path.exists();path.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['status','new_profile_sha256','new_plan_sha256','new_request_sha256','new_registry_candidate_sha256','new_authorization_sha256','new_models_started','real_registry_changed']},indent=2))
if __name__=='__main__':main()
