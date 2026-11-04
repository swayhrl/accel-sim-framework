#!/usr/bin/env python3
"""Fixed48 actual host-resource consumer; closed resource streams only, never raw.log."""
import argparse,collections,datetime,gzip,hashlib,json,os,pathlib,statistics,sys,traceback
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');BASE=P(__file__).resolve().parent
FIXED=A/'agents/B_runtime_analysis_v1/runtime_adapter_v1/FIXED_RUNTIME_INPUTS.json';FIXED_SHA='eb9eaab821a81984c4559bb95844cbd90114664fa6b6d9d329e0f8d3e3049b15';QUAL_SHA='ff7555aff68156598df69ef83a1d48750b29884383ba8362f91f04c6ab5a16ea';PLAN_SHA='9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3';REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1';PASS='PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE';NEG='FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY'
METRICS=['elapsed_receipt_seconds','receipt_peak_observed_rss_bytes','resource_stream_sampled_rss_max_bytes','receipt_sampled_output_logical_max_bytes','raw_log_gzip_stored_bytes','raw_log_uncompressed_bytes_receipt','resource_log_gzip_stored_bytes','archive_stream_container_bytes','source_regular_file_logical_bytes','native_source_allocated_bytes_observed','native_restore_allocated_bytes_observed']
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def checked(p,want):assert sha(p)==want,('SHA_MISMATCH',str(p));return rd(p)
def put(p,v):P(p).write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def pin(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def positive_or_zero(v):return type(v)is int and v>=0
def pid_live(j):
 try:s=P('/proc',str(j['pid']),'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==j['start_ticks']and s[0]not in ['Z','X']
 except(FileNotFoundError,ProcessLookupError):return False

def resource_records(path):
 with gzip.open(path,'rt')as f:
  for line in f:
   if line.strip():yield json.loads(line)
def fold_resource_records(records):
 n=0;rss=[];times=[];pause=0;reasons=collections.Counter();guard=collections.Counter();unknown=0
 for v in records:
  n+=1
  if not isinstance(v,dict):raise ValueError('RESOURCE_RECORD_NOT_DICT')
  if 'process_tree_observed_rss_bytes'in v:
   x=v['process_tree_observed_rss_bytes'];assert positive_or_zero(x);rss.append(x)
   if isinstance(v.get('elapsed_seconds'),(int,float)):times.append(v['elapsed_seconds'])
   pause+=int(v.get('pressure_pause_new')is True);reasons.update(v.get('admission_decision',{}).get('pressure_reasons',[]))
  elif 'DTC_exact_original_policy'in v:
   d=v['DTC_exact_original_policy'].get('decision',{});guard.update([d.get('decision','UNKNOWN')]);reasons.update('GUARD:'+str(x)for x in d.get('stop_reasons',[]))
  else:unknown+=1
 gaps=[b-a for a,b in zip(times,times[1:])];assert all(x>=0 for x in gaps),'NONMONOTONE_RESOURCE_ELAPSED'
 return dict(JSON_records=n,RSS_observations=len(rss),sampled_launcher_plus_simulator_RSS_max_bytes=max(rss)if rss else None,first_sample_elapsed_seconds=times[0]if times else None,last_sample_elapsed_seconds=times[-1]if times else None,observed_sampling_gap_max_seconds=max(gaps)if gaps else None,nominal_sampling_gap_seconds_from_source=10,admission_pressure_pause_observations=pause,pressure_reason_observation_counts=dict(reasons),guard_decision_observation_counts=dict(guard),unclassified_record_count=unknown,per_job_CPU_time_seconds=None,per_job_CPU_utilization=None,CPU_measurement_status='UNKNOWN_NOT_RECORDED;global_cgroup_CPU_not_attributed',absolute_true_RSS_peak_bytes=None,RSS_scope='VmRSS sum of launcher plus observed simulator PIDs in base native source, sampled roughly10s; not every possible descendant, shared pages may be counted twice, not an absolute peak')

def rss_consistency(receipt_max,summary):
 x=summary['sampled_launcher_plus_simulator_RSS_max_bytes'];n=summary['RSS_observations']
 if n==0:return dict(status='NO_SAMPLES_RECEIPT_ZERO_INITIALIZER'if receipt_max==0 else'MISSING_SAMPLES_WITH_NONZERO_RECEIPT',equal=None)
 return dict(status='MATCH'if receipt_max==x else'MISMATCH',equal=receipt_max==x)

def tree_metadata_bytes(root,entries):
 root=P(root);assert ({'.'}|{str(p.relative_to(root))for p in root.rglob('*')})=={e['path']for e in entries},'UNLISTED_OR_MISSING_TREE_ENTRY'
 seen=set();allocated=0;logical=0;files=0
 for e in entries:
  rel=P(e['path']);assert not rel.is_absolute()and'..'not in rel.parts;f=root/rel;st=f.lstat()
  if e['type']=='file':assert f.is_file()and not f.is_symlink()and st.st_size==e['size'];logical+=st.st_size;files+=1
  elif e['type']=='directory':assert f.is_dir()and not f.is_symlink()
  elif e['type']=='symlink':assert f.is_symlink()and os.readlink(f)==e['target']
  else:raise ValueError('UNKNOWN_MANIFEST_TYPE')
  if(st.st_dev,st.st_ino)not in seen:allocated+=st.st_blocks*512;seen.add((st.st_dev,st.st_ino))
 return dict(regular_file_logical_bytes=logical,allocated_st_blocks_bytes=allocated,regular_files=files,listed_entries=len(entries),allocated_scope='lstat st_blocks×512 of listed files/dirs/symlinks; hardlinks deduplicated within this tree; symlink targets not followed; not global df or cross-tree shared-extent accounting',file_content_SHA_reverified_here=False)

def engineering_metadata(cohort):
 rows=[]
 for pattern in [cohort+'.PREPARE.*.json',cohort+'.NATIVE_COMMAND.*.json']:
  for p in sorted((R/'logs').glob(pattern)):
   j=rd(p);obj=None
   try:obj=json.loads(j.get('stdout',''))
   except(ValueError,TypeError):pass
   rows.append(dict(file=pin(p),kind='PREPARE'if'.PREPARE.'in p.name else'NATIVE_COMMAND',command_returncode=j.get('returncode'),reported_status=obj.get('status',obj.get('schema'))if isinstance(obj,dict)else None,reported_reason=obj.get('reason')if isinstance(obj,dict)else None,stderr_nonempty=bool(j.get('stderr'))))
 return dict(logged_command_records=rows,logged_command_count=len(rows),nonzero_command_returncode_count=sum(x['command_returncode']not in [0,None]for x in rows),scope='metadata invocation/admission records; count is not a simulator-start/retry count; absent logs do not prove absence of all engineering events')

def validate_intent(e,o,it):
 assert it['cohort']==e['cohort']and it['spec_sha256']==e['canonical_spec_sha256']and it['consumed_before_launcher_fork']==1 and it['automatic_retry']is False,'INTENT_FIXED_IDENTITY_MISMATCH'
 b=it['l2_mlp_execution_binding'];assert b['request']==REQ and b['approved_contract_commit']=='5f67b4d6b94568a9f1acc80c3e56736bd81e4753'and b['plan_sha256']==PLAN_SHA,'INTENT_REQUEST_PLAN_MISMATCH'
 assert isinstance(it['uuid'],str)and it['uuid'];assert o.get('uuid')is None or it['uuid']==o['uuid'],'INTENT_OBSERVATION_UUID_MISMATCH'
 return it['uuid']

def empty_row(e):return dict(program=e['program'],suite=e['suite'],input_digest=e['input_digest'],profile=e['profile'],cohort=e['cohort'],uuid=None,resource_status='PENDING_NO_LIVE_RESOURCE_OR_RAW_READ',upstream_performance_status=None,metrics={k:None for k in METRICS},CPU=dict(requested_host_cpu=None,initial_observed_affinity=None,affinity_match=None,per_job_CPU_time_seconds=None,per_job_CPU_utilization=None,status='PENDING_OR_UNKNOWN'),resource_samples=None,receipt_sample_max_consistency=None,storage_metadata=None,engineering=None,sources=[],unknowns=[],upstream_outcome_not_changed=True)

def closed_resource_row(e,ob,row):
 c=e['cohort'];resultp=R/'analysis'/(c+'.RESULT.json');result=checked(resultp,ob['sources']['RESULT']['sha256']);assert result['state']in[PASS,NEG]and result['state']==ob['status']and result['uuid']==row['uuid'];assert result['input_digest']==e['input_digest']and result['profile']==e['profile']
 out=R/'DTC/run/results'/row['uuid'];donep=R/'control/qualification_ledger'/(c+'.DONE.json');exitp=out/'NATIVE_EXIT.json';done=rd(donep);assert done==rd(exitp)and done['cohort']==c and done['uuid']==row['uuid']and done['new_attempt_consumed']==1 and done['automatic_retry']is False
 pidp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';pid=rd(pidp)if pidp.exists()else None;assert not pid or not pid_live(pid),'NEVER_READ_LIVE_RESOURCE_STREAM'
 row['sources']+=[pin(x)for x in[resultp,donep,exitp]];row['upstream_performance_status']=result['state'];row['metrics'].update(elapsed_receipt_seconds=done['elapsed_seconds'],receipt_peak_observed_rss_bytes=done['peak_observed_rss_bytes'],receipt_sampled_output_logical_max_bytes=done['peak_result_logical_bytes'],raw_log_uncompressed_bytes_receipt=done['raw_uncompressed_bytes'])
 rc=result['archive']['receipt'];ar=P(rc['target_mount_path']);assert ar.resolve().is_relative_to((A/'results').resolve());receiptp=ar/'RECEIPT.json';assert rd(receiptp)==rc and rc['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and rc['source_disposition']=='SOURCE_KEEP';mfpath=ar/'SOURCE_MANIFEST.json';mf=checked(mfpath,rc['manifest_sha256']);ixp=ar/'ARCHIVE_INDEX.json';ix=rd(ixp);commitp=ar/'COMMIT.json';com=rd(commitp);assert sha(ixp)==com['archive_index_sha256']and com['manifest_sha256']==rc['manifest_sha256'];assert ix['archive_bytes']==rc['archive_bytes']==sum(x['size']for x in ix['chunks']);assert ix['archive_sha256']==rc['archive_sha256'];entries=mf['entries'];em={x['path']:x for x in entries};row['sources']+=[pin(x)for x in[receiptp,mfpath,ixp,commitp]]
 restore=P(rc['native_restore']);assert restore.resolve().is_relative_to((R/'DTC/run/recovery').resolve());sourcebytes=tree_metadata_bytes(out,entries);restorebytes=tree_metadata_bytes(restore,entries);assert out.stat().st_dev==restore.stat().st_dev==2128;assert sourcebytes['regular_file_logical_bytes']==restorebytes['regular_file_logical_bytes']==rc['original_bytes']
 row['storage_metadata']=dict(source=sourcebytes,native_restore=restorebytes,archive_stream_container_bytes=rc['archive_bytes'],archive_container_scope='receipt/index tar-stream container bytes; contains already-compressed log members; not asserted extra compression or SSHFS allocated bytes',no_sum_as_realtime_df_or_hardware_area=True)
 row['metrics'].update(archive_stream_container_bytes=rc['archive_bytes'],source_regular_file_logical_bytes=sourcebytes['regular_file_logical_bytes'],native_source_allocated_bytes_observed=sourcebytes['allocated_st_blocks_bytes'],native_restore_allocated_bytes_observed=restorebytes['allocated_st_blocks_bytes'])
 for name,key in [('raw.log.gz','raw_log_gzip_stored_bytes'),('RESOURCE_SAMPLES.jsonl.gz','resource_log_gzip_stored_bytes')]:
  assert name in em and(out/name).stat().st_size==em[name]['size'];row['metrics'][key]=em[name]['size']
 assert em['raw.log.gz']['sha256']==done['raw_sha256'] # raw content is not opened by this consumer.
 rsp=out/'RESOURCE_SAMPLES.jsonl.gz';assert sha(rsp)==em['RESOURCE_SAMPLES.jsonl.gz']['sha256'];row['sources'].append(pin(rsp));ss=fold_resource_records(resource_records(rsp));row['resource_samples']=ss;row['metrics']['resource_stream_sampled_rss_max_bytes']=ss['sampled_launcher_plus_simulator_RSS_max_bytes'];cons=rss_consistency(done['peak_observed_rss_bytes'],ss);row['receipt_sample_max_consistency']=cons;assert cons['status']in['MATCH','NO_SAMPLES_RECEIPT_ZERO_INITIALIZER'],'RSS_RECEIPT_AND_STREAM_DISAGREE'
 if ss['last_sample_elapsed_seconds']is not None:assert ss['last_sample_elapsed_seconds']<=done['elapsed_seconds']+1,'RESOURCE_ELAPSED_EXCEEDS_DONE'
 dbp=R/'control/dispatch_bindings'/(c+'.json');db=rd(dbp);assert db['cohort']==c and db['canonical_spec_sha256']==e['canonical_spec_sha256'];row['sources'].append(pin(dbp));observed=pid.get('host_cpu_affinity_actual')if pid else None;row['CPU']=dict(requested_host_cpu=db['host_cpu'],initial_observed_affinity=observed,affinity_match=observed==[db['host_cpu']]if observed is not None else None,per_job_CPU_time_seconds=None,per_job_CPU_utilization=None,status='INITIAL_AFFINITY_OBSERVED_NOT_WHOLE_RUN_CPU_UTILIZATION',simulator_pid=pid and pid['pid'],simulator_start_ticks=pid and pid['start_ticks'])
 if pid:row['sources'].append(pin(pidp))
 row['engineering']=dict(**engineering_metadata(c),native_launcher_wait_returncode=done['launcher_wait_returncode'],native_stop_reason=done['stop_reason'],new_attempt_consumed=1,automatic_retry=False,native_simulator_observed=done['native_simulator_observed'])
 row['unknowns']=['Absolute true RSS peak; tracked-pid sampled max only','Per-job CPU time/utilization and whole-run affinity history','Global concurrent RAM peak; point maxima are not additive','Archive SSHFS physical allocation and globally shared native extents'];row['resource_status']='CLOSED_ACCEPTED_RESOURCE_SUMMARY'if result['state']==PASS else'CLOSED_NEGATIVE_RESOURCE_SUMMARY';return row

def load_provider(path):
 raw=P(path).read_bytes();p=json.loads(raw);assert p['schema']=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1'and p['request']==REQ and p['source_qualified']is True;assert p['qualification_manifest']['sha256']==QUAL_SHA;assert sha(p['qualification_manifest']['path'])==QUAL_SHA;mf=checked(p['manifest']['path'],p['manifest']['sha256']);assert mf['source_qualified']and mf['runtime_plan']['sha256']==PLAN_SHA;mp={x['path']:x['sha256']for x in mf['files']};payload={}
 for leaf in['SUMMARY.json.gz','OBSERVATIONS.json.gz']:
  f=next(x for x in p['files']if P(x['path']).name==leaf);assert mp[f['path']]==f['sha256'];assert sha(f['path'])==f['sha256'];payload[leaf]=json.loads(gzip.decompress(P(f['path']).read_bytes()))
 s=payload['SUMMARY.json.gz'];assert s==p['summary']and s['expected_CH']==48 and s['registered_consumed']+s['registered_remaining']==48;fixed=checked(FIXED,FIXED_SHA);points=fixed['expected_CH'];obs=payload['OBSERVATIONS.json.gz']['observations'];assert len(points)==len(obs)==48 and{x['cohort']for x in points}=={x['cohort']for x in obs};return raw,p,points,{x['cohort']:x for x in obs}

def distribution(vals):
 vals=[v for v in vals if v is not None];v=sorted(vals)
 return dict(observed_n=len(v),missing_n=48-len(v),minimum=min(v)if v else None,median=statistics.median(v)if v else None,p95_order_statistic=v[max(0,(95*len(v)+99)//100-1)]if v else None,maximum=max(v)if v else None)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--provider',type=P,required=True);ap.add_argument('--output-dir',type=P,required=True);ap.add_argument('--mode',choices=['current','final'],required=True);args=ap.parse_args();raw,p,points,obs=load_provider(args.provider);s=p['summary']
 if args.mode=='final':assert p['all_registered48_terminal_verified']is True and s['all_registered48_terminal_verified']is True and s['registered_consumed']==48 and s['registered_remaining']==s['verification_hold']==s['await_result']==0 and s['accepted_CH']+s['archived_negative_CH']==48,'AWAIT_ALL48_NATURAL_TERMINAL_NO_FINAL_RESOURCE_RUN'
 out=args.output_dir.resolve();assert out.is_relative_to((BASE/'updates').resolve())and not out.exists();out.mkdir(parents=True);(out/'PROVIDER.fixed.json').write_bytes(raw);rows=[]
 for e in points:
  row=empty_row(e);o=obs[e['cohort']];row['upstream_performance_status']=o['status'];ip=R/'control/qualification_ledger'/(e['cohort']+'.INTENT.json')
  if ip.exists():it=rd(ip);row['uuid']=validate_intent(e,o,it);row['uuid_source']='SMALL_ONE_START_INTENT_METADATA_NOT_TERMINAL_PROMOTION';row['sources'].append(pin(ip))
  if o['status']in[PASS,NEG]:
   try:
    assert row['uuid']==o['uuid'];row=closed_resource_row(e,o,row)
   except Exception as ex:row['resource_status']='CLOSED_RESOURCE_EVIDENCE_HOLD';row['unknowns'].append(repr(ex))
  rows.append(row)
 uuids=[r['uuid']for r in rows if r['uuid']is not None];assert len(uuids)==len(set(uuids)),'DUPLICATE_ACTUAL_INTENT_UUID'
 complete=[r for r in rows if r['resource_status']in['CLOSED_ACCEPTED_RESOURCE_SUMMARY','CLOSED_NEGATIVE_RESOURCE_SUMMARY']];holds=[r for r in rows if r['resource_status']=='CLOSED_RESOURCE_EVIDENCE_HOLD'];summary=dict(schema='DTC_REMAINING48_ACTUAL_RESOURCE_SUMMARY_V1',mode=args.mode,provider_observed_utc=p['observed_utc'],analysis_observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixed_identities48=True,upstream_accepted=s['accepted_CH'],upstream_archived_negative=s['archived_negative_CH'],closed_resource_complete=len(complete),closed_resource_evidence_HOLD=len(holds),pending_or_unverified=len(rows)-len(complete)-len(holds),RSS_receipt_stream_consistency_counts=dict(collections.Counter(r['receipt_sample_max_consistency']['status']for r in complete)),per_point_distributions={k:distribution([r['metrics'][k]for r in complete if k!='receipt_peak_observed_rss_bytes'or r['resource_samples']['RSS_observations']>0])for k in METRICS},separate_stored_byte_totals_closed_only=dict(raw_log_gzip_stored_bytes=sum(r['metrics']['raw_log_gzip_stored_bytes']for r in complete),resource_log_gzip_stored_bytes=sum(r['metrics']['resource_log_gzip_stored_bytes']for r in complete),archive_stream_container_bytes=sum(r['metrics']['archive_stream_container_bytes']for r in complete)),receipt_peak_distribution_excludes_no_sample_zero_initializer=True,receipt_peak_zero_initializer_rows=sum(r['resource_samples']['RSS_observations']==0 for r in complete),no_sum_of_RSS_peaks_reported=True,no_elapsed_sum_as_walltime=True,whole_round_wall_seconds=None,absolute_concurrent_peak_RSS_bytes=None,bytes_not_combined_as_realtime_space_or_hardware_cost=True,raw_log_contents_read=False,live_resource_streams_read=False,new_models_or_services=0,waiter_or_owner_changed=False)
 put(out/'POINT_RESOURCES.json',dict(schema='DTC_REMAINING48_CLOSED_HOST_RESOURCES_WITH_PENDING_V1',rows=rows,units=dict(bytes='bytes',elapsed='monotonic execution-wrapper stopwatch seconds, not CPU time or simulated cycles',RSS='sampled VmRSS sum of tracked launcher+simulator PIDs, not absolute peak',allocated='lstat st_blocks×512 at analysis observation, not logical bytes or global df')));put(out/'SUMMARY.json',summary)
 lines=['# Actual host resources: fixed Remaining48','',f"Mode {args.mode}; closed resource coverage {len(complete)}/48; resource-evidence HOLD {len(holds)}; pending/unverified {48-len(complete)-len(holds)}. Upstream statuses remain unchanged.",'','| Program | F | Status | Elapsed s (receipt) | RSS sampled max MiB | Raw gzip MiB | Archive stream MiB | Source logical MiB | Native restore allocated MiB |','|---|---|---|---:|---:|---:|---:|---:|---:|']
 def fmt(v,bytes=False):return '—'if v is None else format(v/1024**2 if bytes else v,'.2f')
 for r in rows:
  m=r['metrics'];lines.append('| '+r['program']+' | '+r['profile']+' | '+r['resource_status']+' | '+fmt(m['elapsed_receipt_seconds'])+' | '+fmt(m['resource_stream_sampled_rss_max_bytes'],True)+' | '+fmt(m['raw_log_gzip_stored_bytes'],True)+' | '+fmt(m['archive_stream_container_bytes'],True)+' | '+fmt(m['source_regular_file_logical_bytes'],True)+' | '+fmt(m['native_restore_allocated_bytes_observed'],True)+' |')
 lines+=['','The table reports host execution resources, not simulated hardware cost. Receipt RSS and explicit resource-stream maxima are checked for equality;10-second samples do not establish absolute peak, and the base collector sums launcher+observed simulator VmRSS, not necessarily all descendants or unique physical pages. CPU time/utilization remains UNKNOWN; global cgroup CPU is never attributed to a point. Initial affinity is a point-in-time observation only.','', 'Receipt elapsed includes wrapper start/wait/log closure; point elapsed sums would be job-seconds, not round walltime. Point RSS maxima are not added into concurrent peak. Source regular-file logical bytes, compressed log storage, archive container bytes and native restored allocation are separate scopes, never summed into realtime free-space or area. Archive container compression beyond its existing gzip members is not assumed. File-content verification for large raw logs/archive chunks is reused from the qualified B lifecycle; this consumer does not reopen raw.log contents or replace C full lifecycle review. Pending identities keep all resource values null and only small INTENT identity metadata is read.']
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');members=[dict(path=x.name,sha256=sha(x),bytes=x.stat().st_size)for x in sorted(out.iterdir())if x.is_file()];put(out/'MANIFEST.json',dict(schema='DTC_ACTUAL_RESOURCE_REPORT_MANIFEST_V1',files=members,consumer_source_sha256=sha(__file__),provider_input_sha256=hashlib.sha256(raw).hexdigest(),raw_read=False,model_or_service_actions=0));print(json.dumps(dict(output=str(out),closed=len(complete),HOLD=len(holds),pending=48-len(complete)-len(holds),manifest_sha256=sha(out/'MANIFEST.json'))));return 2 if holds else 0
if __name__=='__main__':raise SystemExit(main())
