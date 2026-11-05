"""Engineering-only closeout for an exact failed broad observation UUID.
No install, registry update, model launch, source rewrite, or performance acceptance.
Root must supply existing original full archive callback and current authority.
"""
import gzip,hashlib,json,pathlib
P=pathlib.Path
PRODUCTION_ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
FIELD='additional_strace_bpf_observation_binding'
ID='DTC_STRACE_BROAD_SHARED_CPU_V1'
FAIL='FAIL_L2MLP_ARCHIVED_NO_RETRY'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def require(v,m):
 if not v:raise RuntimeError('NEGATIVE_CLOSEOUT_HOLD:'+m)
def negative_history(c,root,authority,qualification_only=False):
 root=P(root);require(root==PRODUCTION_ROOT or qualification_only,'nonproduction root needs fixture flag')
 row=authority['consumed'][c];ip=root/'control/qualification_ledger'/(c+'.INTENT.json')
 i=read(ip);d=read(ip.with_name(c+'.DONE.json'));out=P(i['output'])
 require(out==root/'DTC/run/results'/row['uuid'],'exact source namespace')
 require(row['intent_sha256']==sha(ip),'INTENT source hash')
 require(d==row.get('execution_receipt')==read(out/'NATIVE_EXIT.json'),'exact DONE/registry/EXIT equality')
 require(i['uuid']==d['uuid']==row['uuid'] and d['cohort']==c,'same identity')
 require(bool(d.get('stop_reason') or d['launcher_wait_returncode']),'normal completion cannot use negative closeout')
 require(d.get('automatic_retry')is False and d.get('source_disposition')=='SOURCE_KEEP','no retry/source release')
 require(sha(out/'raw.log.gz')==d['raw_sha256'],'compressed original raw hash')
 digest=hashlib.sha256();size=0
 with gzip.open(out/'raw.log.gz','rb')as f:
  for data in iter(lambda:f.read(1024*1024),b''):digest.update(data);size+=len(data)
 require(digest.hexdigest()==d['raw_uncompressed_sha256'] and size==d['raw_uncompressed_bytes'],'uncompressed original raw hash')
 binding=i[FIELD];snapshot=out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json'
 require(binding['schema']==ID and sha(snapshot)==binding['snapshot_sha256'],'historical observation binding')
 snap=read(snapshot);require(snap['schema']==ID,'historical observation generation')
 require(snap['config']['qualified_sources']==binding['qualified_sources'],'captured source identity')
 for role,source in snap['config']['source_paths'].items():
  if role in binding['qualified_sources']:require(sha(source)==binding['qualified_sources'][role],'captured source changed '+role)
 rule=snap['scope_policy'];require(rule['validated_union_authorized']is False,'negative union cannot be authorized')
 require(type(rule['primary_statistics_excluded'])is bool,'historical exclusion')
 if rule['primary_statistics_excluded']:require(rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL','unknown excluded role')
 return i,d,out,snap
def verify_negative_archive(c,root,out,archive):
 receipt=archive['receipt'];bundle=P(receipt['target_mount_path']);restore=P(receipt['native_restore'])
 require(receipt['cohort']==c and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['source_disposition']=='SOURCE_KEEP','original complete archive status')
 manifest=read(bundle/'SOURCE_MANIFEST.json');canonical=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 require(hashlib.sha256(canonical).hexdigest()==receipt['manifest_sha256'] and manifest['cohort']==c and manifest['source_root']==str(out),'manifest identity')
 entries={x['path']:x for x in manifest['entries']}
 require(len(entries)==len(manifest['entries'])==archive['independently_verified_entries'],'full original archive verification count')
 require(restore.resolve().is_relative_to(P(root)/'DTC/run/recovery'),'native restore namespace')
 if P(root)==PRODUCTION_ROOT:
  require(restore.stat().st_dev==P(root).stat().st_dev==2128,'native device2128')
  require(bundle.resolve().is_relative_to(P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/results')),'true164 archive namespace')
 required=['STRACE_BPF_OBSERVATION_SNAPSHOT.json','STRACE_BPF_ACTIVATION.json','STRACE_BPF_FORK_PLAN.json','NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_EXIT.json','raw.log.gz','CPU_SHARED_TIMESLICE_SNAPSHOT.json','SHARED_JSON_IO_SNAPSHOT.json']
 proof=[]
 for name in required:
  e=entries.get(name);require(e is not None and e['type']=='file','missing negative archive evidence '+name)
  require(not(out/name).is_symlink() and not(restore/name).is_symlink(),'unexpected evidence symlink')
  require(sha(out/name)==e['sha256']==sha(restore/name) and(out/name).stat().st_size==e['size']==(restore/name).stat().st_size,'negative archive/restore bytes '+name)
  proof.append(dict(path=name,sha256=e['sha256'],bytes=e['size']))
 return dict(schema='BROAD_SHARED_NEGATIVE_ARCHIVE_CLOSURE_V1',status='NEGATIVE_EVIDENCE_ARCHIVED_AND_NATIVE_RESTORED',cohort=c,required_files=proof,manifest_sha256=receipt['manifest_sha256'],native_restore=str(restore),performance_accepted=False)
def close_negative(c,root,authority_provider,original_archive,put,qualification_only=False):
 root=P(root);i,d,out,snap=negative_history(c,root,authority_provider(),qualification_only)
 rp=root/'analysis'/(c+'.RESULT.json');mirror=root/'analysis/incident_recovery_results'/(c+'.RESULT.json')
 if rp.exists():
  previous=read(rp);require(previous['state']==FAIL and previous['uuid']==d['uuid'] and previous.get('cycles')is None and previous['proof'].get('performance_accepted')is False,'existing RESULT cannot change')
  archive=original_archive(c);check=verify_negative_archive(c,root,out,archive)
  require(previous['archive']==dict(archive,additional_strace_bpf_negative_archive_verification=check),'existing negative archive changed')
  if snap['scope_policy']['primary_statistics_excluded']:require(read(mirror)==previous,'negative IR mirror differs')
  return previous
 archive=original_archive(c);check=verify_negative_archive(c,root,out,archive)
 # Re-read authority and raw identity after potentially long archive copying.
 i2,d2,out2,snap2=negative_history(c,root,authority_provider(),qualification_only)
 require((i,d,out,snap)==(i2,d2,out2,snap2),'identity changed during archive')
 rule=snap['scope_policy']
 proof=dict(status='L2_MLP_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],accepted_cycles=None,raw_sha256=d['raw_sha256'],raw_uncompressed_sha256=d['raw_uncompressed_sha256'],performance_accepted=False)
 value=dict(state=FAIL,cohort=c,uuid=d['uuid'],cycles=None,proof=proof,archive=dict(archive,additional_strace_bpf_negative_archive_verification=check),new_contract_only=True,original_or_repair_results_replaced=False,scientific_role=rule['scientific_role'],primary_statistics_excluded=rule['primary_statistics_excluded'],validated_union_authorized=False,observation_generation=ID,model_retries=0)
 if rule['primary_statistics_excluded']:
  if mirror.exists():require(read(mirror)==value,'negative IR mirror conflict')
  else:put(mirror,value,True)
 put(rp,value,True)
 return value
def make_safe_finish(current_safe,selected,root,authority_provider,original_archive,put,qualification_only=False):
 """Optional owner wrapper: positive and historical routes delegate unchanged."""
 def safe(c):
  try:
   if not selected(c):return current_safe(c)
   row=authority_provider()['consumed'].get(c,{})
   d=row.get('execution_receipt')
   if not d or not(d.get('stop_reason')or d.get('launcher_wait_returncode')):return current_safe(c)
   return close_negative(c,root,authority_provider,original_archive,put,qualification_only)
  except Exception as e:return dict(state='NEGATIVE_CLOSEOUT_ENGINEERING_HOLD_PRESERVE',cohort=c,error=repr(e),accepted_cycles=None,model_retries=0,validated_union_authorized=False)
 return safe
