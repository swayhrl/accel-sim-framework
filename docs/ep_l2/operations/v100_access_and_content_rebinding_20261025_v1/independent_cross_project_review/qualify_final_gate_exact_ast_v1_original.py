import pathlib,ast,json,copy,hashlib,datetime
R=pathlib.Path('/root/data/shared_sm70_trace_library_20261024_v1');O=pathlib.Path('/root/data/sm70_cross_project_independent_review_20261025_v1');O.mkdir(exist_ok=False)
old=R/'tools/finish_report_cross_v2_a_frozen.py';new=R/'tools/finish_report.py';assert hashlib.sha256(old.read_bytes()).hexdigest()=='55b44ca201cada368cb0c99dbdbc742659438c821f1da6838e766626ab838805';assert hashlib.sha256(new.read_bytes()).hexdigest()=='dbd2213423e12097a429a82458d63763adffe1cb11084c4f8e5cfc0666a8bd8a'
def gates(p):
 tree=ast.parse(p.read_text());body=tree.body;start=next(i for i,n in enumerate(body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='cross'for t in n.targets))+1;end=next(i for i,n in enumerate(body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='restore'for t in n.targets));block=body[start:end];assert all(isinstance(x,(ast.Assign,ast.Assert))for x in block);return compile(ast.Module(body=block,type_ignores=[]),str(p),'exec')
oldgate=gates(old);newgate=gates(new);dirs=['/root/data/ep_l2_main_20261023_v1/worktree','/root/data/dtc_main_20261023_v1','/root/workspace/offline-sim-v1'];assets=[{'bundle_id':'synthetic_bundle_A','members':[{},{}]},{'bundle_id':'synthetic_bundle_B','members':[{}]}];catalog={'catalog_id':'synthetic_current_catalog','assets':assets};base={'status':'PASS_CROSS_PROJECT_ALL_ASSET_ACCESS','catalog_id':catalog['catalog_id'],'assets':2,'projects_tested':3,'project_activation_required':False,'scientific_starts':0,'verification_revision':'V2_EACH_CWD_ALL_DECLARED_MEMBERS','all_member_read_projects':3,'reports':[{'cwd':d,'operation':'all_bundles_all_declared_members_open_seek_reopen','results':[{'bundle_id':'synthetic_bundle_A','members':2,'status':'PASS_SEALED_IDENTITY_OPEN_REOPEN'},{'bundle_id':'synthetic_bundle_B','members':1,'status':'PASS_SEALED_IDENTITY_OPEN_REOPEN'}]}for d in dirs]}
cases=[]
def add(name,mutator,want):
 x=copy.deepcopy(base);mutator(x)
 try:exec(newgate,{'cross':x,'catalog':catalog,'assets':assets});accepted=True;error=None
 except(AssertionError,KeyError)as e:accepted=False;error=repr(e)
 assert accepted==want,(name,accepted,error);cases.append({'case':name,'accepted':accepted,'expected':want,'error':error})
add('valid_current_three_project_all_member_metadata',lambda x:None,True)
def oldsingle(x):x.pop('verification_revision');x.pop('all_member_read_projects');x['reports']=x['reports'][:1]
add('old_single_round_report_rejected',oldsingle,False)
add('one_project_disguised_as_three_rejected',lambda x:x.update(reports=x['reports'][:1]),False)
add('same_bundle_member_counts_different_catalog_rejected',lambda x:x.update(catalog_id='synthetic_previous_catalog'),False)
add('wrong_assets_count_rejected',lambda x:x.update(assets=1),False)
add('wrong_projects_tested_rejected',lambda x:x.update(projects_tested=2),False)
add('activation_required_rejected',lambda x:x.update(project_activation_required=True),False)
add('scientific_start_claim_rejected',lambda x:x.update(scientific_starts=1),False)
add('missing_bundle_result_rejected',lambda x:x['reports'][1].update(results=x['reports'][1]['results'][:1]),False)
add('wrong_member_count_rejected',lambda x:x['reports'][2]['results'][0].update(members=1),False)
add('wrong_cwd_rejected',lambda x:x['reports'][2].update(cwd='/synthetic_wrong_project'),False)
add('wrong_open_reopen_status_rejected',lambda x:x['reports'][0]['results'][0].update(status='PASS_FULL_SHA'),False)
add('duplicate_bundle_result_rejected',lambda x:x['reports'][1].update(results=[x['reports'][1]['results'][0],x['reports'][1]['results'][0]]),False)
stale=copy.deepcopy(base);stale['catalog_id']='synthetic_previous_catalog';exec(oldgate,{'cross':stale,'catalog':catalog,'assets':assets})
q={'schema':'SM70_FINAL_GATE_SYNTHETIC_CPU_ONLY','status':'ONE_POSITIVE_TWELVE_NEGATIVES_PASS','actual_data_validation_executed':False,'old55_gate_accepts_same_counts_stale_catalog_reproduced':True,'new_dbd_gate_rejects_same_counts_stale_catalog':True,'source_scope':'Only AST-extracted Assign/Assert block after metadata read and before restore read. Original finish_report module never imported or executed; no publication/sender/trace reads.','new_finish_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'old_finish_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'cases':cases,'sender_signals':0,'scientific_starts':0,'GPU_starts':0,'109_accesses':0};p=O/'SYNTHETIC_FINAL_GATE_QUALIFICATION.json';p.write_text(json.dumps(q,indent=2)+'\n')
for path in [R/'tools/cross_project_validate.py',new,old,R/'tools/trace_assets_public.py',R/'control/CROSS_PROJECT_VALIDATION_REQUIREMENT_REPAIR_V2.json',R/'control/FINISH_REPORT_CROSS_PROJECT_SCOPE_GATE_V2.json',R/'control/CROSS_PROJECT_FINAL_CATALOG_BINDING_V3.json']:(O/path.name).write_bytes(path.read_bytes())
print(json.dumps({'report':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cases':len(cases),'status':q['status']}))
