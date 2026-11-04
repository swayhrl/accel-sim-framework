from pathlib import Path
import json,hashlib,copy,ast,sys,importlib.util
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('new48_readonly_adapter',D/'actual_remaining48_readonly_adapter.py');ad=importlib.util.module_from_spec(sp);sp.loader.exec_module(ad);checks=[]
def check(n,v):
 assert v,n;checks.append({'check':n,'pass':True})
def raises(n,fn,kind=ValueError):
 try:fn()
 except kind:checks.append({'check':n,'pass':True});return
 raise AssertionError(n)
m,fixed,base=ad.frozen_inputs();ff,candidate,plan,ctx=ad.static_runtime_context();check('all122actual_source_pins_and_plan_candidate_SHA_pass',len(plan['source_pins'])==122);check('48members24inputs_match_fixed_PROPOSAL',len(fixed['expected_CH'])==48 and len({e['input_digest']for e in fixed['expected_CH']})==24);check('candidate_is_not_grant_flag',ctx['registration_granted']is False);check('new48union_scope_only',plan['core32_reporting_authorized']is True and plan['first16_reexecution_authorized']is False and plan['supplement_deferred_UNRESOLVED_combinations_authorized']is False)
# Simulate an authority pair with no new48 grant, without altering any registry bytes.
orig_get=ad.get;regpath=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');eppath=regpath.parents[1]/'CURRENT_SCIENCE_EPOCH.json'
def missing_grant_get(p):
 p=Path(p)
 if p==regpath:return {'registered_future_requests':{}},{'path':'CPU_ONLY_NO_GRANT_REGISTRY','sha256':'0'*64}
 if p==eppath:return {'native_registry_sha256':'0'*64},{'path':'CPU_ONLY_MATCHED_EPOCH','sha256':'1'*64}
 return orig_get(p)
ad.get=missing_grant_get;raises('candidate_alone_rejected_as_actual_grant',ad.registry_context,PermissionError);index,cache=ad.collect();check('no_grant_collect_all48_pending_no_accepted',index['source_qualified']is False and len(index['observations'])==48 and all(not r['accepted']and r['cycles']is None and r['status']=='AWAIT_ACTUAL_REGISTRY_GRANT'for r in index['observations'])and cache=={});ad.get=orig_get
# Exact result-role boundary. No filesystem result is created by these CPU fixtures.
e=fixed['expected_CH'][0];fixture={'cohort':e['cohort'],'scientific_role':'STAGEII_REMAINING48_AUTHORIZED_CH','input_digest':e['input_digest'],'cell':'CH','profile':e['profile'],'state':ad.PASS,'validated_union_authorized':True,'union_scope':'CORE32_FIRST16_PLUS_REMAINING48_FIXED_SHA','new_contract_only':True,'original_or_repair_results_replaced':False};ad.validate_result_scope(fixture,e);check('new_role_union_fixture_valid_scope_only',True)
for key,value in [('scientific_role','STAGEII_AUTHORIZED_CH'),('validated_union_authorized',False),('union_scope','ORIGINAL350'),('state','HOLD'),('profile','P0')]:
 bad=dict(fixture);bad[key]=value;raises('reject_wrong_scope_'+key,lambda bad=bad:ad.validate_result_scope(bad,e))
# Real closed first16 vectorAdd archive verifies byte-for-byte same SOURCE_KEEP/restore shape under explicit tiers.
OldR=Path('/root/data/dtc_stage_iia_first16_20261104_v1');OldA=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');co='E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1';rp=OldR/'analysis'/(co+'.RESULT.json');r=json.loads(rp.read_bytes());out=OldR/'DTC/run/results'/r['uuid'];done=json.loads((out/'NATIVE_EXIT.json').read_bytes());oldR,oldNAS,oldstatus=ad.R,ad.NAS,ad.STRICT_STATUS;ad.R=OldR;ad.NAS=OldA/'results';ad.STRICT_STATUS='STAGEII_FIRST16_NATIVE_TRACE_PERFORMANCE_QUALIFIED';oldctx={'outbox_sha256':sha(OldR/'tools/stage2_outbox.py')};refs,av=ad.verify_archive(co,r,out,done,True,oldctx);check('closed_actual_oldSOURCE2128_archive39_restore2128_stream_SHA_and_rows',av['native_restored_entries_verified']>0)
real_old_e=dict(e,cohort=co,input_digest=r['input_digest'],profile='F128');raises('old_first16_result_cannot_become_new48_role',lambda:ad.validate_result_scope(r,real_old_e))
wrongrole=ad.RESTORE_DEV;ad.RESTORE_DEV=39;raises('reject_164_as_native_restore_device',lambda:ad.verify_archive(co,r,out,done,True,oldctx));ad.RESTORE_DEV=wrongrole
wrongrole=ad.ARCHIVE_DEV;ad.ARCHIVE_DEV=2128;raises('reject_native_as_genuine164_archive_device',lambda:ad.verify_archive(co,r,out,done,True,oldctx));ad.ARCHIVE_DEV=wrongrole
raises('positive_archive_not_negative_scientific_status',lambda:ad.verify_archive(co,r,out,done,False,oldctx));ad.R,ad.NAS,ad.STRICT_STATUS=oldR,oldNAS,oldstatus
raises('unsafe_manifest_parent_escape',lambda:ad.exact_safe(Path('/tmp/safe'),'../escape'));raises('unsafe_manifest_absolute_path',lambda:ad.exact_safe(Path('/tmp/safe'),'/escape'))
# New source-tier contract checks nearest existing directories only, no mkdir on native model namespaces.
tiers=[]
for role,pin in fixed['source_tiers'].items():
 p=Path(pin['root']);nearest=p
 while not nearest.exists():nearest=nearest.parent
 check('new_'+role+'_nearest_existing_parent_device',nearest.stat().st_dev==pin['device']);tiers.append({'role':role,'declared_root':str(p),'nearest_existing':str(nearest),'actual_device':nearest.stat().st_dev,'expected_device':pin['device']})
# Source pins and prequalification remain exact; no dispatcher/native writer imported.
for pin in plan['source_pins']:check('source_pin_'+Path(pin['path']).name+'_'+pin['sha256'][:8],sha(pin['path'])==pin['sha256'])
pre=json.loads(Path(fixed['prequalification_manifest']['path']).read_bytes());check('prequal9members_unchanged',len(pre['files'])==9 and all(sha(Path(fixed['prequalification_manifest']['path']).parent/x['path'])==x['sha256']for x in pre['files']))
src=(D/'actual_remaining48_readonly_adapter.py').read_text();check('no_native_execution_or_mutation_import',not any(x in src for x in ['run_native(','.prepare(','.reset(',"load('l2_finish_engine'",'register_future_request(']));check('only_readonly_findmnt_subprocess',src.count('subprocess.check_output')==1 and "['findmnt'"in src)
report={'schema':'DTC_REMAINING48_ACTUAL_ADAPTER_CPU_QUALIFICATION_V1','checks':checks,'count':len(checks),'all_pass':True,'actual_new48_results_consumed':0,'actual_closed_old_archive_compatibility_witness':{'RESULT':{'path':str(rp),'sha256':sha(rp)},'archive_verification':av,'native_exit':{'path':str(out/'NATIVE_EXIT.json'),'sha256':sha(out/'NATIVE_EXIT.json')},'interpretation':'Real old closed archive validates generic shape/tier verification only; it was never a new48 observation or accepted source.'},'qualified_new_tiers':tiers,'synthetic_fixture_boundary':'Only in-memory role/no-grant dictionaries; no native identity/result/registry files written.','service_started':False,'new_models_or_runtime_actions':0}
(D/'CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print('CHECKS',len(checks),'PASS','OLD_RESTORED_MEMBERS',av['native_restored_entries_verified'])
