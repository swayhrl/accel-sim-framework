"""Single-writer read-only analysis service for the already registered first16.

No model/native-engine/result-producer/archive-writer imports or actions. No Git.
"""
from __future__ import annotations
import argparse,copy,datetime,fcntl,gzip,hashlib,importlib.util,json,os,pathlib,sys,time
sys.dont_write_bytecode=True
P=pathlib.Path;HERE=P(__file__).resolve().parent
ADAPTER=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/B_runtime_adapter_v1/actual_readonly_adapter.py')
ADAPTER_SHA='c3310df8a4c8fb2d94ba57742339c3220367822c62128270810060d3967107a7'
REQ='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'
PASS='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE';FAIL='FAIL_STAGEII_CH_ARCHIVED_NO_RETRY'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def require(v,msg):
 if not v:raise ValueError(msg)
def atomic(p,v):
 p=P(p);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.writing');b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 with tmp.open('wb') as h:h.write(b);h.flush();os.fsync(h.fileno())
 tmp.replace(p)
def load_adapter():
 require(sha(ADAPTER)==ADAPTER_SHA,'FIXED_ACTUAL_ADAPTER_SOURCE_CHANGED')
 spec=importlib.util.spec_from_file_location('fixed_readonly_adapter',ADAPTER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def result_signature(adapter,contract):
 rows=[]
 for e in contract['expected_CH']:
  c=e['cohort'];refs={}
  for role,p in [('RESULT',adapter.R/'analysis'/(c+'.RESULT.json')),('INTENT',adapter.R/'control/qualification_ledger'/(c+'.INTENT.json')),('DONE',adapter.R/'control/qualification_ledger'/(c+'.DONE.json')),('ARCHIVE_RECEIPT',adapter.R/'control'/(c+'_ARCHIVE_RECEIPT.json'))]:
   refs[role]={'path':str(p),'sha256':sha(p)} if p.exists() else None
  rows.append({'cohort':c,'refs':refs})
 return hashlib.sha256(canon(rows)).hexdigest(),rows

def cache_metadata_ok(row):
 """Recheck all source JSON witnesses before reusing immutable full-archive validation."""
 refs=list(row.get('sources',{}).values())
 refs+=list(row.get('archive_verification',{}).get(k) for k in ['archive_receipt','source_manifest','archive_index','commit','native_restore'])
 refs+=[row.get(k) for k in ['native_exit','intent','done','dispatch_binding','root_science_qualification']]
 try:
  return bool(refs) and all(isinstance(r,dict) and sha(r['path'])==r['sha256'] for r in refs if r is not None)
 except (OSError,KeyError,ValueError):return False

def base_pending(e,reason):return {'program':e['program'],'suite':e['suite'],'input_digest':e['input_digest'],'design':'CH','profile':e['profile'],'cohort':e['cohort'],'source_role':'STAGEII_AUTHORIZED_CH','request':REQ,'accepted':False,'cycles':None,'status':'HOLD_READONLY_VERIFICATION','reason':reason}

def consume(adapter,contract,base,cache,force_full):
 q,plan,context=adapter.registry_context();require(plan['remaining48_not_authorized'] is True and plan['no_extensions'] is True,'LATER48_MUST_REMAIN_LOCKED')
 expected={x['cohort'] for x in contract['expected_CH']};require(set(q['admitted_specs'])==expected,'REGISTERED_MEMBERSHIP_DIFFERS_FROM_FIXED16')
 by={(x['input_digest'],x['design'],x['profile']):x for x in base['references']};newcache={};rows=[];full=[];reused=[]
 for e in contract['expected_CH']:
  c=e['cohort'];rp=adapter.R/'analysis'/(c+'.RESULT.json');old=cache.get(c)
  try:
   result_sha=sha(rp) if rp.exists() else None
   if not force_full and old and old['result_sha256']==result_sha and old['row']['status'] in [PASS,FAIL] and cache_metadata_ok(old['row']):
    row=copy.deepcopy(old['row']);row['analysis_validation_mode']='RECHECKED_CRITICAL_JSON_SHA_WITH_CACHED_IMMUTABLE_FULL_ARCHIVE_AUDIT';row['full_archive_audit_utc']=old['full_archive_audit_utc'];row['critical_json_rechecked_utc']=now();reused.append(c);newcache[c]=old
   else:
    row=adapter.observation(e,by[e['input_digest'],'CH','P0'],context,q)
    if row['status'] in [PASS,FAIL]:
     stamp=now();row['analysis_validation_mode']='FULL_CURRENT_ARCHIVE_STREAM_NATIVE_RESTORE_AND_CRITICAL_SOURCE_AUDIT';row['full_archive_audit_utc']=stamp;row['critical_json_rechecked_utc']=stamp;newcache[c]={'result_sha256':result_sha,'row':copy.deepcopy(row),'full_archive_audit_utc':stamp};full.append(c)
  except (AssertionError,KeyError,ValueError,OSError,json.JSONDecodeError) as exc:row=base_pending(e,str(exc))
  rows.append(row)
 index={'schema':'DTC_STAGEIIA_FIRST16_ANALYSIS_OBSERVATIONS_V1','request':REQ,'authority':'READONLY_ACTUAL_REGISTERED_STRICT_ARCHIVE_WITNESS_VERIFIED','observations':rows,'runtime_source_pins':context,'new_model_starts':0,'native_scientific_writes':0,'remaining48_locked':True,'registered_consumed':len(q['consumed']),'registered_remaining':q['remaining'],'verification':{'full_current_audit':full,'critical_json_sha_rechecked_cached_archive':reused,'full_archive_force':force_full}}
 return index,newcache

def write_snapshot(adapter,consumer,contract,base,index,signature):
 tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+signature[:8];out=HERE/'snapshots'/tag;out.mkdir(parents=True,exist_ok=False)
 index['observed_utc']=now();p=out/'OBSERVATIONS.json';p.write_text(json.dumps(index,indent=2)+'\n');observed=consumer.load_root_index(p,sha(p));report=consumer.evaluate(contract,base,observed);report['analysis_observation_index']={'path':str(p),'sha256':sha(p)};report['remaining48_locked']=True;report['observed_utc']=index['observed_utc'];report['full_archive_audit_vs_cached_metadata']=index['verification'];(out/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');(out/'RESULTS.md').write_text(consumer.markdown(report))
 accepted=sum(r['accepted'] for r in index['observations']);negative=sum(r['status']==FAIL for r in index['observations']);hold=sum(r['status']=='HOLD_READONLY_VERIFICATION' for r in index['observations']);complete=accepted+negative==16 and hold==0
 summary={'schema':'DTC_STAGEIIA_FIRST16_ANALYSIS_SUMMARY_V1','request':REQ,'observed_utc':index['observed_utc'],'expected_CH':16,'accepted_CH':accepted,'archived_negative_CH':negative,'verification_hold':hold,'await_result':16-accepted-negative-hold,'registered_consumed':index['registered_consumed'],'registered_remaining':index['registered_remaining'],'all_registered16_terminal_verified':complete,'scientific_population':'FIRST8_PREDECLARED_SUBSET_NOT_35_OR_CORE32','common_both_F_n':len(report['common_F128_F256_population']),'per_profile_available_paired':report['per_profile_available_paired'],'common_F128_F256_metrics':report['common_F128_F256_metrics'],'direct_F_comparison':report['direct_F_comparison'],'remaining48_locked':True,'no_git_or_native_scientific_writes':True,'new_model_starts':0};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 for name in ['OBSERVATIONS.json','RESULTS.json','SUMMARY.json']:
  data=(out/name).read_bytes();(out/(name+'.gz')).write_bytes(gzip.compress(data,mtime=0))
 members=[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(out.iterdir())];manifest={'schema':'DTC_STAGEIIA_FIRST16_ANALYSIS_SNAPSHOT_MANIFEST_V1','source_signature':signature,'files':members,'source_service_sha256':sha(__file__),'fixed_adapter_sha256':ADAPTER_SHA,'remaining48_locked':True};mp=out/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
 ready={'schema':'DTC_STAGEIIA_FIRST16_ANALYSIS_PUBLICATION_PROVIDER_V1','sole_publisher':'ROOT_ONLY','observed_utc':index['observed_utc'],'manifest':{'path':str(mp),'sha256':sha(mp)},'snapshot':str(out),'all_registered16_terminal_verified':complete,'files':[{'name':f'STAGEIIA_FIRST16_{n}','path':str(out/n),'sha256':sha(out/n)} for n in ['RESULTS.md','RESULTS.json.gz','SUMMARY.json.gz','OBSERVATIONS.json.gz']],'summary':{k:summary[k] for k in ['accepted_CH','archived_negative_CH','await_result','verification_hold','common_both_F_n','registered_consumed','registered_remaining','remaining48_locked']}}
 atomic(HERE/'PUBLICATION_PROVIDER.json',ready);atomic(HERE/'LATEST.json',{'schema':'DTC_STAGEIIA_FIRST16_ANALYSIS_LATEST_V1','observed_utc':index['observed_utc'],'snapshot':str(out),'manifest_sha256':sha(mp),'summary':ready['summary'],'complete':complete});return ready

def main():
 ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group(required=True);group.add_argument('--once',action='store_true');group.add_argument('--watch',action='store_true');group.add_argument('--status',action='store_true');ap.add_argument('--interval-seconds',type=int,default=120);ap.add_argument('--full-audit-seconds',type=int,default=1800);a=ap.parse_args();require(a.interval_seconds>=30 and a.full_audit_seconds>=a.interval_seconds,'POLLING_INTERVAL_TOO_SMALL')
 if a.status:
  for n in ['HEALTH.json','LATEST.json']:
   p=HERE/n
   if p.exists():print(n,p.read_text())
  return
 with (HERE/'ANALYSIS_OWNER.lock').open('a+b') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print(json.dumps({'status':'EXISTING_READONLY_ANALYSIS_OWNER_RUNNING','new_models_started':0}));return
  adapter=load_adapter();consumer,contract,base=adapter.frozen_inputs();cache={};last_signature=None;last_full=0.0;retry_on_hold=False
  pid=os.getpid();start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);owner={'pid':pid,'start_ticks':start_ticks,'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),'role':'READONLY_ANALYSIS_ONLY_NOT_MODEL_CONTROLLER','source_sha256':sha(__file__),'interval_seconds':a.interval_seconds,'full_audit_seconds':a.full_audit_seconds}
  atomic(HERE/'OWNER.json',owner)
  while True:
   if (HERE/'STOP_ANALYSIS_REQUESTED').exists():atomic(HERE/'HEALTH.json',dict(owner,status='STOPPED_READONLY_ANALYSIS_BY_OWN_STOP_FILE',utc=now()));break
   try:
    require(sha(ADAPTER)==ADAPTER_SHA,'FIXED_ADAPTER_SOURCE_DRIFT');signature,sources=result_signature(adapter,contract);full=time.monotonic()-last_full>=a.full_audit_seconds
    if signature!=last_signature or full or retry_on_hold:
     consumer.verify_original_sources(base);index,newcache=consume(adapter,contract,base,cache,full);ready=write_snapshot(adapter,consumer,contract,base,index,signature);cache=newcache;last_signature=signature;retry_on_hold=any(r['status']=='HOLD_READONLY_VERIFICATION' for r in index['observations'])
     if full:last_full=time.monotonic()
     status=dict(owner,status='RESULT_TABLE_UPDATED',utc=now(),summary=ready['summary'],publication_provider_sha256=sha(HERE/'PUBLICATION_PROVIDER.json'));atomic(HERE/'HEALTH.json',status);print(json.dumps(status),flush=True)
     if ready['all_registered16_terminal_verified']:atomic(HERE/'HEALTH.json',dict(status,status='ALL_REGISTERED16_TERMINAL_ANALYSIS_COMPLETE_ROOT_PUBLICATION_PENDING_OR_EXTERNAL'));break
    else:atomic(HERE/'HEALTH.json',dict(owner,status='WAITING_SOURCE_CHANGE',utc=now(),signature=signature))
   except BaseException as exc:
    atomic(HERE/'HEALTH.json',dict(owner,status='HOLD_READONLY_ANALYSIS_RETRY_LATER',utc=now(),error=repr(exc)));print(json.dumps({'utc':now(),'status':'HOLD_READONLY_ANALYSIS_RETRY_LATER','error':repr(exc)}),flush=True)
   if a.once:break
   time.sleep(a.interval_seconds)
if __name__=='__main__':main()
