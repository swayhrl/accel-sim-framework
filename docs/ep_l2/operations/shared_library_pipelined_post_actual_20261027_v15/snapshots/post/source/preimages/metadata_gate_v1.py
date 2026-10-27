#!/usr/bin/python3
"""Fixed streamcluster CPU adoption boundary/phase compiler. PREPARE ONLY: never launches work."""
from pathlib import Path
import os,json,hashlib,argparse,time,re
JOB='ORD_Rodinia_streamcluster_1be5fda1aa60_A001'
PROFILE='STREAMCLUSTER_CLOSED_F9_CPU_ADOPTION_PREPARE_V1'
POST='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
SCHED='9308c508d85c84db7e9b8d49e465ffaffc426fef638a92d05eec4c6dc7cae423'
FIXED_ROOT='/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/inflight/'+JOB
OBJECT_ROOT=FIXED_ROOT.replace('/inflight/','/objects/')
KNOWN_HANDLES={'worker':(795210,'360511682'),'post':(1008828,'367078090')}
def need(x,m):
 if not x:raise RuntimeError('HOLD_'+m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def read_json(path,expected=None,limit=8*2**20):
 p=Path(path);need(p.suffix=='.json'and not p.is_symlink(),'METADATA_JSON_ONLY')
 before=p.lstat();need(0<before.st_size<=limit,'FINITE_METADATA_BYTES')
 with p.open('rb')as f:
  need((os.fstat(f.fileno()).st_dev,os.fstat(f.fileno()).st_ino)==(before.st_dev,before.st_ino),'OPEN_IDENTITY');raw=f.read(limit+1);after=os.fstat(f.fileno())
 need(len(raw)<=limit and(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)==(p.stat().st_dev,p.stat().st_ino,p.stat().st_size,p.stat().st_mtime_ns,p.stat().st_ctime_ns),'METADATA_STABLE')
 if expected:need(digest(raw)==expected,'ORIGINAL_METADATA_SHA')
 return json.loads(raw)
def boundary(e,s):
 need(e['schema']=='STREAMCLUSTER_CLOSED_CPU_EVIDENCE_V1'and e['job_id']==s['job_id']==JOB,'EXACT_JOB')
 need(e['snapshot_sha256']==s['snapshot_sha256'],'FROZEN_SNAPSHOT')
 t=e['terminal'];need(t['whole_job_terminal']is True and t['owned_inventory_complete']is True and t['source_writers_closed']is True,'WHOLE_JOB_OWNED_TERMINAL')
 need(t['audit_age_seconds']>=0 and t['audit_age_seconds']<=300,'FRESH_TERMINAL_AUDIT')
 need(t['root_terminal_receipt_raw_sha256']and re.fullmatch('[0-9a-f]{64}',t['root_terminal_receipt_raw_sha256']),'ROOT_TERMINAL_REF_REQUIRED')
 handles={x['role']:x for x in t['handles']};need(set(KNOWN_HANDLES)<=set(handles),'ORIGINAL_HANDLES_REQUIRED')
 for role,(pid,ticks)in KNOWN_HANDLES.items():
  h=handles[role];need(h['pid']==pid and h['start_ticks']==ticks and h['state']=='EXITED_REAPED'and h['identity_known']is True,'ORIGINAL_'+role.upper()+'_TERMINAL')
 need(all(x['identity_known']is True and x['state']=='EXITED_REAPED'for x in t['handles']),'UNKNOWN_OR_LIVE_DESCENDANT')
 leases=t['leases'];need(set(leases)=={'gpu_campaign_109','LOCAL_IO_109','RTX_SOURCE_174','RTX_TARGET_174'}and all(x=='FREE_OBSERVED'for x in leases.values()),'ALL_ORIGINAL_LEASES_FREE')
 need(e['metadata']==s['metadata'],'ORIGINAL_EXECUTION_MAP_F9_PINS')
 need(e['identity']==s['identity'],'BINARY_ARGV_PROFILE_PRODUCER_INPUT_SOURCE_IDENTITY')
 need(e['root_source']in[FIXED_ROOT,OBJECT_ROOT],'EXACT_SOURCE_ROOT')
 if e['root_source']==OBJECT_ROOT:need(e.get('archive',{}).get('receiver_COMMIT_closed')is True,'IMMUTABLE_OBJECT_ONLY_AFTER_RECEIVER_COMMIT')
 return True
def compile_plan(e,s):
 need(s['snapshot_sha256']==digest(canon({k:v for k,v in s.items()if k!='snapshot_sha256'})),'SNAPSHOT_SELF_HASH')
 boundary(e,s);names=s['declared_order'];by=s['per_kernel'];raw=e['raw_inventory'];need(len(raw)==len(names),'RAW_EXACT_CARDINALITY')
 idx={}
 for x in raw:
  name=x['name'];need(name not in idx and name in by and x['regular_no_symlink']is True,'RAW_NAME_OR_TYPE')
  need(x['path']==e['root_source']+'/traces/'+name and x['known_f9_sha256']==s['known_raw_sha256'][name],'KNOWN_RAW_SHA_AND_EXACT_PATH')
  idx[name]=x
 need(set(idx)==set(names),'RAW_EXACT_SET')
 reused={};partial=[];missing=[];posts=e['post_inventory']
 for x in posts:
  name=x['name'];need(name in by and name not in reused and name not in partial,'POST_NAME_DUPLICATE_OR_EXTRA')
  if x['state']=='PARTIAL_RETAINED':
   partial.append(name);continue
  need(x['state']=='PER_KERNEL_CLOSED_RECEIPT','UNKNOWN_POST_STATE')
  r=x['receipt'];base=by[name]
  need(x['origin_scheduler_sha256']==SCHED and x['postprocessor_sha256']==POST,'POST_CODE_PINS')
  need(r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and r['source_sha256']==s['known_raw_sha256'][name],'POST_SOURCE_CLOSED')
  need([r['records'],r['ctas'],r['warps']]==[base['records'],base['ctas'],base['warps']],'POST_F9_COUNTS')
  need(re.fullmatch('[0-9a-f]{64}',r['grouped_sha256'])and x['receipt_raw_sha256']and x['receipt_owned_closed_provenance']is True,'POST_RECEIPT_PROVENANCE')
  need(x['grouped_path']in[FIXED_ROOT+'/post_parallel2/'+name.replace('.trace.xz','.traceg.xz'),FIXED_ROOT+'/traces/'+name.replace('.trace.xz','.traceg.xz'),OBJECT_ROOT+'/traces/'+name.replace('.trace.xz','.traceg.xz')],'POST_EXACT_OLD_PATH')
  reused[name]=dict(name=name,known_raw_sha256=r['source_sha256'],grouped_sha256=r['grouped_sha256'],grouped_path=x['grouped_path'],receipt_raw_sha256=x['receipt_raw_sha256'],current_grouped_body_reopen_required_at_archive=True)
 for name in names:
  if name not in reused:missing.append(name)
 jobs=[dict(schema='EXACT_COMPLETE_KERNEL_CPU_POST_REQUEST_V1',job_id=JOB,name=n,source_path=idx[n]['path'],expected_known_raw_sha256=s['known_raw_sha256'][n],f9_validation_raw_sha256=s['metadata']['validation_sha256'],records=by[n]['records'],ctas=by[n]['ctas'],warps=by[n]['warps'],postprocessor_sha256=POST,CPU_only=True,source_KEEP=True,destination_policy='NEW_PRIVATE_ATTEMPT_ONLY_NEVER_OVERWRITE_OLD',partial_old_files='KEEP_NOT_QUALIFIED_OR_DELETED')for n in missing]
 need(e['root_source']!=OBJECT_ROOT or not missing,'NEVER_POST_IN_IMMUTABLE_OBJECT')
 arch=e.get('archive',{});closed=arch.get('receiver_COMMIT_closed')is True and arch.get('all_payload_raw_and_grouped_SHA_reconciled')is True and arch.get('current_version_and_pointer_closed')is True
 if closed:
  need(not missing and arch.get('kernel_count')==len(names)and arch.get('records')==s['records']and arch.get('source_KEEP')is True,'ARCHIVE_COMPLETE_EXACT')
  stage='NO_RECOVERY_PENDING_INDEPENDENT_ARCHIVE_REOPEN'
 elif missing:stage='CPU_POST_MISSING_COMPLETE_KERNELS_THEN_FULL_ARCHIVE'
 else:stage='ARCHIVED_OBJECT_CURRENT_CLOSURE_REQUIRED'if e['root_source']==OBJECT_ROOT else'ALL_POST_CANDIDATES_PRESENT_FULL_ARCHIVE_RECEIVER_CURRENT_REQUIRED'
 return dict(schema='STREAMCLUSTER_CPU_ADOPTION_REVIEW_PLAN_V1',profile=PROFILE,stage=stage,job_id=JOB,declared_order=names,reuse_existing_f9=True,reexecute_record_validator=False,capture_or_GPU_allowed=False,known_raw_hashes_are_original_evidence_not_fresh_current_body_proof=True,reused_POST_candidates=[reused[n]for n in names if n in reused],preserved_partial_names=partial,missing_complete_kernel_POST_requests=jobs,qualified_POST_cpu_concurrency_ceiling=2,shared_IO='Existing5d is not bandwidth-throttled; future exact shared IO/owned writer lease/resource profile required. No15MiB/s guarantee.',archive_required=dict(all_original_RAW_SHA_must_match_f9_during_actual_full_body_archive_or_reconciliation=True,all_grouped_files_full_body_SHA_and_complete_original_whole_application_set=True,sender_manifest_full_tree=True,true164_receiver_reopen_MANIFEST_COMMIT=True,ordinary_ASSETS_version_and_CURRENT_CAS_close=True,metadata_is_not_body_proof=True),future_fixed_post_argv=['/usr/bin/nice','-n','15','/usr/bin/prlimit','--as=1610612736','--','python3','-B','ROOT_PINNED_5D_POST','EXACT_RAW','NEW_GROUPED','NEW_PRIVATE_WORK','--scratch-budget','ROOT_EXACT_APPROVED_BYTES'],execution_state='PREPARE_ONLY_NO_ACTIONS_DISPATCHED',remaining_admission_gaps=['Root fresh independently verified terminal/owned/lease receipts','Root exact finite CPU-only resource/IO scope and new private work paths','Root-admitted selected-only resume scheduler; old9308 rejects existing dest and prescans all RAW','Whole-body sender/archive/receiver source reconciliation; no metadata shortcut','Ordinary CURRENT updater adapter: ff7 publisher writes ASSETS but not CURRENT; derived updater is design reference only'],source_KEEP=True,consumer_or_science_or_numeric_qualification=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--snapshot',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 s=read_json(a.snapshot);e=read_json(a.evidence)
 try:result=compile_plan(e,s)
 except(RuntimeError,KeyError,TypeError,ValueError)as ex:result=dict(status='HOLD',reason=str(ex),job_id=JOB,source_KEEP=True,execution_started=False)
 out=Path(a.output);need(not out.exists(),'NEW_OUTPUT_ONLY');out.write_bytes(canon(result));print(json.dumps(dict(status=result.get('stage',result.get('status')),execution_started=False)))
if __name__=='__main__':main()
