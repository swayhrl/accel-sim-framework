"""Conditional native science epoch2 publication, not a dispatcher/launcher.

Called once only after BOTH actual scientific qualifications and true164/native
restores. Old Source ledgers are never edited. A shared management retirement
marker is administrative fencing; privileged raw-root bypass is not prevented.
"""
import pathlib,json,hashlib,os,time,fcntl,subprocess,sys
P=pathlib.Path;ROOT=P('/root/data/ep_l2_dtc_l1_native_v2');MANAGEMENT=P('/root/data/ep_l2_dtc_l1_management_20261023_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,s):
 if not v:raise RuntimeError(s)
def exclusive(p,x):
 raw=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode();p=P(p)
 if p.exists():need(p.read_bytes()==raw,'immutable epoch record collision')
 else:
  with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def prepare():
 need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','Target native identity')
 ep=read(ROOT/'EP/control/SCIENCE_QUALIFICATION.json');dt=ROOT/'DTC/control/SCIENCE_QUALIFICATION.json';need(ep['status']=='EP_SCIENCE_QUALIFIED' and dt.exists() and read(dt)['status']=='DTC_SCIENCE_QUALIFIED','BOTH_NATIVE_SCIENTIFIC_QUALIFICATIONS_REQUIRED')
 proofs={};archives={}
 for project,cohort in [('EP','EP_NATIVE_MIGRATION_Q2'),('DTC','DTC_NATIVE_MIGRATION_Q1')]:
  p=ROOT/project/'control'/('SCIENCE_QUALIFICATION_'+cohort+'.json');q=read(p);a=ROOT/'control'/(cohort+'_ARCHIVE_RECEIPT.json');r=read(a);need(r['scientific_status']==project+'_SCIENCE_QUALIFIED' and r['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','qualified actual164 archive/restore missing');proofs[project]={'path':str(p),'sha256':sha(p),'uuid':q['uuid'],'PID':q['native_PID'],'qualification':q};archives[project]={'path':str(a),'sha256':sha(a),'receipt':r}
 source=read(ROOT/'control/SOURCE_PREFLIGHT.json');need(time.time()-source['observed_unix']<=300,'fresh final source owner/active/budget review missing');need(source['EP_actual_starts']==57 and source['DTC_actual_starts']==2 and source['current_owner_bindings_verified'] and source['no_active_scientific_dispatch_or_unresolved_intent'],'source history/owner/active state changed')
 first=read(MANAGEMENT/'source_authority/EPOCH_0001_COMMITTED.json');need(first['epoch']==1,'existing management epoch1 mismatch')
 approvals={}
 for name in ['SCIENCE_AUTHORIZATION.json','EP_NATIVE_MIGRATION_Q2_AUTHORIZATION.json']:
  p=ROOT/'control'/name;x=read(p);need(x['explicit_user_approval'] and x['owner_bindings_ratified'] and x['target_resource_policy_ratified'],'exact authorization absent');approvals[name]={'path':str(p),'sha256':sha(p),'approval_request_sha256':x['approval_request_sha256']}
 history=[]
 for cohort in ['EP_NATIVE_MIGRATION_Q1','EP_NATIVE_MIGRATION_Q2','DTC_NATIVE_MIGRATION_Q1']:
  p=ROOT/'control/qualification_ledger'/(cohort+'.DONE.json');need(p.exists(),'native cohort unresolved');q=read(p);history.append({'cohort':cohort,'uuid':q['uuid'],'path':str(p),'sha256':sha(p),'charged_starts':1,'outcome':'STOP_UNACCEPTED' if q['stop_reason'] or q['launcher_wait_returncode'] else 'NATURAL_COMPLETE_INDEPENDENTLY_QUALIFIED'})
 short='DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1';short_intent=ROOT/'control/qualification_ledger'/(short+'.INTENT.json')
 if short_intent.exists():
  p=short_intent.with_name(short+'.DONE.json');need(p.exists(),'separate authorized legacy replay unresolved');q=read(p);history.append({'cohort':short,'uuid':q['uuid'],'path':str(p),'sha256':sha(p),'charged_starts':1,'outcome':'SEPARATE_LEGACY_REPLAY_NOT_CURRENT_AD_QUALIFICATION','counts_as_current_AD_qualification':False})
 return {'schema':'NATIVE_SCIENCE_EPOCH2_PREPARED_V1','epoch':2,'prior_management_epoch':1,'holder':'huangrulin-sshfs-174','scientific_entry':str(ROOT/'bin/native'),'projects':proofs,'archives':archives,'approvals':approvals,'source_historical_canonical_sha256':source['canonical_reference_sha256'],'source_historical_preimages_root':str(ROOT/'control/source_historical_preimages'),'old_source_EP_starts':57,'old_source_DTC_starts':2,'native_migration_EP_consumed':2,'native_migration_DTC_consumed':1,'native_attempt_history':history,'unused_migration_budgets':0,'future_science_requires':'New unique request-id, exact owner spec/input/config/binary/native lineage, separately explicit user budget, fresh current-stage plus all-other-project resource admission; no old cohort retry','old_source_dispatch':'Administratively retired, original files and ledgers untouched; root bypass outside protocol','original_assets_and_new_results':'SOURCE_KEEP','current_scientific_lock':str(ROOT/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'),'model_invocation_via_old174_SSH':'FORBIDDEN'}
def commit():
 lock=(ROOT/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 plan=prepare();d=ROOT/'control/science_authority';d.mkdir(exist_ok=True)
 existing=d/'EPOCH_0002_COMMITTED.json'
 if existing.exists():
  x=read(existing);need(x['prepared_sha256']==sha(d/'EPOCH_0002_PREPARED.json'),'existing epoch content drift');return x
 exclusive(d/'EPOCH_0002_PREPARED.json',plan)
 intent={'state':'INTENT_NATIVE_SCIENCE_EPOCH2','prepared_sha256':sha(d/'EPOCH_0002_PREPARED.json'),'epoch':2,'prior_epoch':1};exclusive(d/'EPOCH_0002_INTENT.json',intent)
 # This new marker is inside the already authorized shared management root;
 # neither the Source RUN_REGISTRY nor its old scientific budget is modified.
 retirement={'schema':'SOURCE_OFFICIAL_SCIENTIFIC_DISPATCH_ADMIN_RETIREMENT_V2','retired_official_Source_projects':['EP_L2','DTC_L1'],'new_epoch':2,'new_holder':'huangrulin-sshfs-174','native_entry':str(ROOT/'bin/native'),'prepared_sha256':intent['prepared_sha256'],'old_management_epoch1_retained':True,'old_source_scientific_ledgers_mutated':False,'old_original_simulator_commands_not_to_be_invoked':True,'already_running_tasks_interrupted':False,'root_raw_bypass':'Outside administrative protocol; no kernel security claim'};exclusive(MANAGEMENT/'source_authority/NATIVE_SCIENCE_EPOCH2_RETIREMENT.json',retirement)
 registry={'schema':'SINGLE_CURRENT_NATIVE_SCIENCE_REGISTRY_V2','epoch':2,'authority':'174-new native only','prepared_sha256':intent['prepared_sha256'],'old_source_history':plan['source_historical_canonical_sha256'],'qualification_history':plan['native_attempt_history'],'new_scientific_budget_remaining':0,'registered_future_requests':{},'all_prior_failures_preserved':True,'T0_old_EP':1792414193,'source_release_bytes':0};exclusive(d/'NATIVE_SCIENCE_REGISTRY.json',registry)
 done={'state':'NATIVE_SCIENCE_ACTIVE','epoch':2,'holder':'huangrulin-sshfs-174','prepared_sha256':intent['prepared_sha256'],'native_registry_sha256':sha(d/'NATIVE_SCIENCE_REGISTRY.json'),'retirement_sha256':sha(MANAGEMENT/'source_authority/NATIVE_SCIENCE_EPOCH2_RETIREMENT.json'),'scientific_qualification':{'EP':'PASS','DTC':'PASS'},'new_budget_remaining':0,'future_starts_not_implicitly_authorized':True};exclusive(existing,done)
 exclusive(ROOT/'control/CURRENT_SCIENCE_EPOCH.json',done);return done
if __name__=='__main__':
 try:print(json.dumps(commit() if sys.argv[1:] == ['--commit'] else prepare(),indent=2))
 except (RuntimeError,OSError,KeyError,ValueError) as e:print(json.dumps({'status':'HOLD_NO_SCIENCE_SWITCH','reason':str(e)}),file=sys.stderr);sys.exit(2)
