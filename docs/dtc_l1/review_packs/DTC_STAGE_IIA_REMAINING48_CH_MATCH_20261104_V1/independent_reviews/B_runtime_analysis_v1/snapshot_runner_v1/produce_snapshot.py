"""One-shot readonly analysis publisher-provider. Root may schedule it; never a model dispatcher."""
from __future__ import annotations
import argparse,datetime,fcntl,gzip,hashlib,importlib.util,json,os,pathlib,sys,time
sys.dont_write_bytecode=True
P=pathlib.Path;HERE=P(__file__).resolve().parent;ADAPTER=HERE.parent/'runtime_adapter_v1/actual_remaining48_readonly_adapter.py';ADAPTER_SHA='0383daa67804db3b92779f2520cbbc0978c195c759e27357938319c942442e1c';AM=ADAPTER.parent/'MANIFEST.json';AM_SHA='ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea';REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,v):
 p=P(p);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.writing');tmp.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');tmp.replace(p)
def load_adapter():
 require(sha(ADAPTER)==ADAPTER_SHA and sha(AM)==AM_SHA,'FIXED_READONLY_ADAPTER_OR_QUALIFICATION_CHANGED');sp=importlib.util.spec_from_file_location('qualified_new48_readonly_adapter',ADAPTER);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def verify_frozen_reference_results():
 fixedp=ADAPTER.parent/'FIXED_RUNTIME_INPUTS.json';fixed=json.loads(fixedp.read_bytes());rc=fixed['reference_contract'];require(sha(rc['path'])==rc['sha256'],'REFERENCE_CONTRACT_DRIFT');reference=json.loads(P(rc['path']).read_bytes());n=0
 for r in reference['original128_references']+reference['first16_CH_references']:
  require(sha(r['source_RESULT_path'])==r['source_RESULT_sha256'],'FROZEN_REFERENCE_RESULT_SHA_DRIFT:'+r['source_RESULT_path']);n+=1
  alias=r.get('legal_prior_P0_alias')
  if alias:require(sha(alias['underlying_RESULT_path'])==alias['underlying_RESULT_sha256'],'LEGAL_INHERITED_P0_SOURCE_SHA_DRIFT')
 require(n==144,'WRONG_FROZEN_REFERENCE_COUNT');return reference

def refs_signature(ad,cache):
 refs=[]
 for c in sorted(json.loads((ADAPTER.parent/'FIXED_RUNTIME_INPUTS.json').read_bytes())['expected_CH'],key=lambda x:x['cohort']):
  co=c['cohort']
  for p in[ad.R/'analysis'/(co+'.RESULT.json'),ad.R/'control/qualification_ledger'/(co+'.INTENT.json'),ad.R/'control/qualification_ledger'/(co+'.DONE.json'),ad.R/'control'/(co+'_ARCHIVE_RECEIPT.json')]:refs.append({'path':str(p),'sha256':sha(p)if p.exists()else None})
 for x in cache.values():
  row=x['row'];r=list(row.get('sources',{}).values())+list(row.get('archive_verification',{}).get(k)for k in['archive_receipt','source_manifest','archive_index','commit','native_restore'])+[row.get(k)for k in['native_exit','intent','done','dispatch_binding','root_science_qualification']]
  for v in r:
   if isinstance(v,dict):
    p=P(v['path']);refs.append({'path':str(p),'sha256':sha(p)if p.exists()else None})
 # The current authority pair is a source identity witness; a candidate file is never a substitute.
 for p in[P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),P('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json'),ad.R/'control/EXECUTION_PLAN.json']:
  refs.append({'path':str(p),'sha256':sha(p)if p.exists()else None})
 return hashlib.sha256(json.dumps(refs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def summary_for(report,index):
 c=report['coverage'];qualified=index.get('source_qualified')is True and index.get('registration_granted')is True
 terminal=qualified and c['remaining48_terminal_verified']and index.get('registered_consumed')==48 and index.get('registered_remaining')==0 and c['remaining48_accepted']+c['remaining48_archived_negative']==48 and c['remaining48_verification_HOLD']==0 and c['remaining48_pending']==0
 return {'schema':'DTC_REMAINING48_ANALYSIS_SUMMARY_V1','request':REQ,'source_qualified':qualified,'observed_utc':index['observed_utc'],'expected_CH':48,'accepted_CH':c['remaining48_accepted'],'archived_negative_CH':c['remaining48_archived_negative'],'verification_hold':c['remaining48_verification_HOLD'],'await_result':c['remaining48_pending'],'registered_consumed':index.get('registered_consumed'),'registered_remaining':index.get('registered_remaining'),'core32_fixed_input_n':32,'core32_common_both_F_n':c['common_both_F_n'],'accepted_six_source_slots':c['accepted_source_slots'],'expected_six_source_slots':192,'all_registered48_terminal_verified':terminal,'full_CORE32_complete_sixcell_accepted':c['common_both_F_n']==32,'original128_and_first16_separate_source_roles':True,'new_model_starts':0,'native_scientific_writes':0}
def markdown(report,summary):
 def val(v):return'MISSING'if v is None else f'{v:.6f}'if isinstance(v,float)else str(v)
 def tab(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(val(x)for x in r)+' |'for r in rows])
 lines=['# Remaining48 CH matching / fixed CORE32 readonly results','',f"As of {summary['observed_utc']}; source_qualified={summary['source_qualified']}. New48 accepted {summary['accepted_CH']}/48, archived negative {summary['archived_negative_CH']}, verification HOLD {summary['verification_hold']}, pending {summary['await_result']}. Complete both-F population {summary['core32_common_both_F_n']}/32. Source slots accepted {summary['accepted_six_source_slots']}/192.",'','All32 fixed inputs remain listed. Interim available-subset GM is descriptive, not the full32suite result. Direct F comparison uses the same accepted six-cell intersection; negatives/HOLD/pending never become cycles. Original128, first16newCH and remaining48newCH keep distinct source roles; source_profile is actual configuration, not a comparison-context alias.','',tab(['Suite','Common n','Profile','GM S_CH','GM S_DH','GM CH/DH','GM I'],[[s,g['common_both_F']['n'],pf,*[g['common_both_F']['profiles'][pf][k]['GM']for k in['S_CH','S_DH','R','I']]]for s,g in [('ALL_CORE32',report['all_core32'])]+list(report['by_suite'].items())for pf in['F128','F256']]),'',tab(['Program','Full input SHA','CH0','CH128','CH256','DH0','DH128','DH256','I128','I256','Common bothF'],[[r['program'],r['input_digest'],*[r['six_source_cells'][c+'_'+p]['cycles']for c in['CH','DH']for p in['P0','F128','F256']],r['metrics_by_profile']['F128']['I']if r['metrics_by_profile']['F128']else None,r['metrics_by_profile']['F256']['I']if r['metrics_by_profile']['F256']else None,r['common_both_F_accepted']]for r in report['all_programs']]),'','JSON retains all source path/SHA/role/UUID/alias/status, sign distributions, suites, missing reasons and same-set F comparisons. I>1 is relative improvement, not proof DTC exceeds CH. No per-program bestF GM or equal-area claim. FR queue/shared credits coupled; fixed850MHz DRAM/10MiB L2/frontend mechanisms preserved. No new model, registry/controller action, extra48/combination or v0.23 edit by this readonly consumer.','']
 return '\n'.join(lines)
def run_once(force_full_archive=False):
 HERE.mkdir(parents=True,exist_ok=True)
 with(HERE/'ANALYSIS_WRITER.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);ad=load_adapter()
  try:verify_frozen_reference_results()
  except(Exception)as e:
   hold={'status':'FROZEN_REFERENCE_SOURCE_HOLD','utc':now(),'source_qualified':False,'error':repr(e),'historical_snapshots_not_changed':True,'new_model_starts':0};atomic(HERE/'HEALTH.json',hold);atomic(HERE/'SOURCE_QUALIFICATION_HOLD.json',hold)
   prior=json.loads((HERE/'PUBLICATION_PROVIDER.json').read_bytes())if(HERE/'PUBLICATION_PROVIDER.json').exists()else{'schema':'DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1','request':REQ,'files':[],'sole_publisher':'ROOT_ONLY'};prior.update(source_qualified=False,source_qualification_hold=hold,all_registered48_terminal_verified=False,historical_snapshot_retained=True);atomic(HERE/'PUBLICATION_PROVIDER.json',prior);return hold
  state=json.loads((HERE/'STATE.json').read_bytes())if(HERE/'STATE.json').exists()else{};cache=json.loads((HERE/'CACHE.json').read_bytes())if(HERE/'CACHE.json').exists()else{};signature=refs_signature(ad,cache);due=force_full_archive or time.time()-state.get('last_full_archive_audit_unix',0)>=1800
  # static context checks122pins even when no result changes; no model/authority mutation.
  try:ad.static_runtime_context();static_error=None
  except(Exception)as e:static_error=repr(e)
  if signature==state.get('signature')and not due and static_error is None:
   health={'status':'UNCHANGED_CRITICAL_SOURCE_SHA_RECHECKED','utc':now(),'signature':signature,'source_qualified':state.get('source_qualified'),'next_full_archive_audit_seconds':max(0,1800-(time.time()-state.get('last_full_archive_audit_unix',0))),'no_new_models':True};atomic(HERE/'HEALTH.json',health);return health
  try:index,newcache=ad.collect(previous_cache=cache,force_full_archive=due);_,fixed,_=ad.frozen_inputs()
  except(Exception)as e:
   # Immutable analysis inputs still define fixed membership; drift never becomes acceptance.
   fp=ADAPTER.parent/'FIXED_RUNTIME_INPUTS.json';require(sha(fp)==ad.FIXED_SHA,'FIXED_MEMBERSHIP_UNTRUSTWORTHY');fixed=json.loads(fp.read_bytes());index={'schema':'DTC_REMAINING48_ANALYSIS_OBSERVATIONS_V1','request':REQ,'observed_utc':now(),'source_qualified':False,'registration_granted':False,'observations':[ad.pending(x,'HOLD_READONLY_VERIFICATION',repr(e))for x in fixed['expected_CH']],'new_model_starts':0,'native_scientific_writes':0};newcache={}
  st=fixed['pure_stats'];require(sha(st['path'])==st['sha256'],'PURE_STATS_SOURCE_DRIFT');sp=importlib.util.spec_from_file_location('pinned_CORE32_stats',st['path']);stats=importlib.util.module_from_spec(sp);sp.loader.exec_module(stats);rc=fixed['reference_contract'];require(sha(rc['path'])==rc['sha256'],'REFERENCE_CONTRACT_DRIFT');reference=json.loads(P(rc['path']).read_bytes());report=stats.evaluate(reference,index['observations']);summary=summary_for(report,index);summary['frozen_reference_RESULT_SHA_rechecked']=144
  tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+signature[:8];out=HERE/'snapshots'/tag;out.mkdir(parents=True,exist_ok=False);files=[]
  for name,obj in[('OBSERVATIONS.json.gz',index),('CORE32_RESULTS.json.gz',report),('SUMMARY.json.gz',summary)]:
   data=(json.dumps(obj,indent=2,sort_keys=True)+'\n').encode();p=out/name;p.write_bytes(gzip.compress(data,compresslevel=6,mtime=0));files.append({'name':'STAGEIIA_REMAINING48_'+name,'path':str(p),'sha256':sha(p)})
  p=out/'CORE32_RESULTS.md';p.write_text(markdown(report,summary));files.append({'name':'STAGEIIA_REMAINING48_CORE32_RESULTS.md','path':str(p),'sha256':sha(p)})
  snapmanifest={'schema':'DTC_REMAINING48_READONLY_ANALYSIS_SNAPSHOT_V1','created_utc':index['observed_utc'],'files':files,'adapter':{'path':str(ADAPTER),'sha256':ADAPTER_SHA},'qualification_manifest':{'path':str(AM),'sha256':AM_SHA},'runtime_plan':fixed['execution_plan'],'reference_contract':rc,'pure_stats':st,'source_qualified':summary['source_qualified'],'new_model_starts':0,'native_scientific_writes':0};mp=out/'MANIFEST.json';mp.write_text(json.dumps(snapmanifest,indent=2,sort_keys=True)+'\n')
  provider={'schema':'DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1','request':REQ,'observed_utc':index['observed_utc'],'source_qualified':summary['source_qualified'],'qualification_manifest':{'path':str(AM),'sha256':AM_SHA},'snapshot':str(out),'manifest':{'path':str(mp),'sha256':sha(mp)},'files':files,'summary':summary,'core32_fixed_input_n':32,'all_registered48_terminal_verified':summary['all_registered48_terminal_verified'],'sole_publisher':'ROOT_ONLY','new_model_starts':0,'native_scientific_writes':0};atomic(HERE/'PUBLICATION_PROVIDER.json',provider);atomic(HERE/'CACHE.json',newcache);atomic(HERE/'STATE.json',{'signature':signature,'source_qualified':summary['source_qualified'],'snapshot':str(out),'last_full_archive_audit_unix':time.time()if due else state.get('last_full_archive_audit_unix',0)});atomic(HERE/'LATEST.json',summary);atomic(HERE/'HEALTH.json',{'status':'SNAPSHOT_WRITTEN','utc':now(),'source_qualified':summary['source_qualified'],'new_model_starts':0});return provider
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--force-full-archive',action='store_true');a=p.parse_args();v=run_once(a.force_full_archive);print(json.dumps({'status':v.get('status','SNAPSHOT_READY'),'source_qualified':v.get('source_qualified'),'snapshot':v.get('snapshot'),'summary':v.get('summary')}))
