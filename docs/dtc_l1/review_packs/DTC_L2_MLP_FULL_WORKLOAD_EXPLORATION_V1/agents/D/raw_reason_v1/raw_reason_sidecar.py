"""One-shot read-only L2 failure-reason extraction from closed accepted logs.

Only the last cumulative stats frame per stream is retained. No per-kernel sum,
no missing-to-zero conversion, no import of frozen production modules.
"""
import pathlib,json,re,gzip,hashlib,datetime,argparse,os
P=pathlib.Path
REASON=re.compile(r'^\s*L2_cache_stats_fail_breakdown\[([^\]]+)\]\[([^\]]+)\]\s*=\s*(\d+)\s*$')
UID=re.compile(r'^\s*kernel_launch_uid\s*=\s*(\d+)\s*$')
STREAM=re.compile(r'^\s*kernel_stream_id\s*=\s*(\d+)\s*$')
REJECT=re.compile(r'^\s*L2_total_cache_reservation_fails\s*=\s*(\d+)\s*$')

def parse_frames(lines):
 frames=[];current=None;unbound=[];unparsed=[]
 for n,line in enumerate(lines,1):
  u=UID.match(line)
  if u:
   current=dict(kernel_uid=int(u[1]),stream_id=None,uid_line=n,reason_fields={},reason_lines=[],reservation_fails=None);frames.append(current);continue
  s=STREAM.match(line)
  if s and current is not None:current['stream_id']=int(s[1]);current['stream_line']=n;continue
  r=REASON.match(line)
  if r:
   item=dict(line=n,text=line.rstrip(),access_type=r[1],reason=r[2],value=int(r[3]))
   if current is None or current['stream_id']is None:unbound.append(item)
   else:
    k=r[1]+':'+r[2];assert k not in current['reason_fields'],'Duplicate reason field in one stats frame'
    current['reason_fields'][k]=int(r[3]);current['reason_lines'].append(item)
  elif'L2_cache_stats_fail_breakdown'in line:unparsed.append(dict(line=n,text=line.rstrip()))
  f=REJECT.match(line)
  if f and current is not None:current['reservation_fails']=int(f[1])
 last={}
 for frame in frames:
  if frame['stream_id']is not None:last[str(frame['stream_id'])]=frame
 positive={}
 for frame in last.values():
  for key,v in frame['reason_fields'].items():positive[key]=positive.get(key,0)+v
 return dict(printed_stats_frame_count=len(frames),unique_kernel_uids=sorted({f['kernel_uid']for f in frames}),stream_ids=sorted({f['stream_id']for f in frames if f['stream_id']is not None}),last_cumulative_frame_by_stream=last,positive_reason_known_contributions=positive or None,sum_known_positive_reason_contributions=sum(positive.values())if positive else None,unbound_reason_lines=unbound,unparsed_reason_lines=unparsed,unprinted_reasons=None,rule='Use last cumulative frame per stream, never sum successive kernel prints. Missing reason fields remain absent/None; positive contributions do not imply unprinted reasons are zero.')

def read_json(p,sources):
 with P(p).open('rb')as h:
  before=os.fstat(h.fileno());b=h.read();after=os.fstat(h.fileno())
 assert(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)and len(b)==after.st_size
 digest=hashlib.sha256(b).hexdigest();sources[str(p)]=dict(path=str(p),sha256=digest,bytes=len(b));return json.loads(b)

def accepted(v):
 p=v.get('proof',{});c=v.get('cycles')
 if v.get('state')not in['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START']or p.get('performance_accepted')is not True or type(c)is not int or c<=0 or c!=p.get('cycles'):return False
 if v['state']=='REFERENCE_ACCEPTED_NO_NEW_START':return all(v.get('reuse_verification',{}).get(k)is True for k in['strict_verified','natural_done_verified','archive_native_restore_verified','complete_effective_options_equal','core_framework_binary_equal','input_scope_equal'])
 return bool(v.get('archive'))

def scan_raw(raw,proof):
 sh=hashlib.sha256()
 with raw.open('rb')as h:
  for b in iter(lambda:h.read(1024*1024),b''):sh.update(b)
 assert sh.hexdigest()==proof['raw_gzip_sha256'],'Closed compressed raw SHA mismatch'
 uh=hashlib.sha256();nbytes=0
 def lines():
  nonlocal nbytes
  with gzip.open(raw,'rb')as h:
   for b in h:uh.update(b);nbytes+=len(b);yield b.decode()
 v=parse_frames(lines());assert uh.hexdigest()==proof['raw_uncompressed_sha256'],'Closed raw body SHA mismatch'
 return dict(v,raw_gzip_path=str(raw),raw_gzip_sha256=sh.hexdigest(),raw_uncompressed_sha256=uh.hexdigest(),raw_uncompressed_bytes=nbytes)

def closed_source(root,reference_root,point,result,sources):
 """Verify primary terminal evidence before opening a possibly large raw log."""
 proof=result['proof'];isref=result['state']=='REFERENCE_ACCEPTED_NO_NEW_START'
 source_root=reference_root if isref else root
 source_cohort=proof['cohort']if isref else point['cohort']
 source_result_path=source_root/'analysis'/(source_cohort+'.RESULT.json')
 original=read_json(source_result_path,sources)
 assert original['uuid']==result['uuid']and original['cycles']==result['cycles']and original['proof']==proof
 assert original['state']in['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE']
 ip=source_root/'control/qualification_ledger'/(source_cohort+'.INTENT.json');dp=ip.with_name(source_cohort+'.DONE.json')
 intent=read_json(ip,sources);done=read_json(dp,sources)
 out=source_root/'DTC/run/results'/result['uuid']
 assert intent['cohort']==source_cohort and intent['uuid']==done['uuid']==result['uuid']and P(intent['output'])==out
 exitproof=read_json(out/'NATIVE_EXIT.json',sources)
 assert done==exitproof and done['stop_reason']is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed']
 assert done['raw_sha256']==proof['raw_gzip_sha256']and done['raw_uncompressed_sha256']==proof['raw_uncompressed_sha256']
 strict_path=out/('DOWNSTREAM_STRICT.json'if isref else'L2_STRICT.json')
 assert read_json(strict_path,sources)==proof
 qualification=read_json(source_root/'DTC/control'/('SCIENCE_QUALIFICATION_'+source_cohort+'.json'),sources)
 assert qualification['strict_sha256']==sources[str(strict_path)]['sha256']and qualification['uuid']==result['uuid']
 receipt_path=source_root/'control'/(source_cohort+'_ARCHIVE_RECEIPT.json');receipt=read_json(receipt_path,sources)
 assert receipt==original['archive']['receipt']and original['archive']['independently_verified_entries']>0
 assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and receipt['source_disposition']=='SOURCE_KEEP'
 assert proof['input_digest']==point['input_digest']and proof['cell']==point['cell']
 return out/'raw.log.gz',dict(source_root=str(source_root),source_cohort=source_cohort,source_result_path=str(source_result_path),source_result_sha256=sources[str(source_result_path)]['sha256'],intent_path=str(ip),intent_sha256=sources[str(ip)]['sha256'],done_path=str(dp),done_sha256=sources[str(dp)]['sha256'],native_exit_path=str(out/'NATIVE_EXIT.json'),strict_path=str(strict_path),strict_sha256=sources[str(strict_path)]['sha256'],archive_receipt_path=str(receipt_path),archive_receipt_sha256=sources[str(receipt_path)]['sha256'],archive_target=receipt['target_mount_path'],archive_sha256=receipt['archive_sha256'],native_restore=receipt['native_restore'],source_verified_natural_closed_before_raw_open=True,legal_reference=isref)

def collect(root,reference_root,scope_path):
 root=P(root);reference_root=P(reference_root);sources={};matrix=read_json(root/'control/MATRIX_CURRENT.json',sources);scope=read_json(scope_path,sources)
 stream_scope={r['input_digest']:r for r in scope['rows']};rows=[];skipped=[]
 for point in matrix['points']:
  c=point['cohort'];rp=root/'analysis'/(c+'.RESULT.json')
  if not rp.exists():continue
  result=read_json(rp,sources)
  if not accepted(result):skipped.append(dict(cohort=c,state=result.get('state'),reason='NOT_ACCEPTED_CLOSED_RESULT'));continue
  proof=result['proof']
  identity=dict(cohort=c,input_digest=point['input_digest'],program=point['program'],suite=point['suite'],cell=point['cell'],profile=point['profile'],uuid=result['uuid'],state=result['state'],cycles=result['cycles'],result_path=str(rp),result_sha256=sources[str(rp)]['sha256'])
  try:
   raw,closure=closed_source(root,reference_root,point,result,sources)
   scan=scan_raw(raw,proof);declared=stream_scope.get(point['input_digest'],{});expected=point['expected']['kernels']
   complete=(len(scan['unique_kernel_uids'])==expected and scan['stream_ids']==declared.get('stream_ids')and declared.get('complete_header_coverage')is True and not scan['unbound_reason_lines']and not scan['unparsed_reason_lines'])
   frames=scan['last_cumulative_frame_by_stream'];values=[f['reservation_fails']for f in frames.values()]
   observed_total=sum(values)if values and all(v is not None for v in values)else None
   matched=scan['sum_known_positive_reason_contributions']==observed_total if observed_total is not None and scan['sum_known_positive_reason_contributions']is not None else None
   rows.append(dict(identity,status='SIDECAR_EXTRACTED_CLOSED_ACCEPTED',source_closure=closure,closed_raw=scan,complete_declared_stream_stats_coverage=complete,observed_last_frame_reservation_fail_total=observed_total,known_reason_sum_matches_observed_reservation_fail_total=matched,scope='VERIFIED_SINGLE_STREAM_DECLARED_TRACE'if complete and len(scan['stream_ids'])==1 else'PER_STREAM_LAST_FRAME_EVIDENCE_ONLY'))
  except (OSError,ValueError,KeyError,AssertionError)as e:rows.append(dict(identity,status='SIDECAR_EVIDENCE_ERROR_NO_RECLASSIFICATION',error=repr(e)))
 return dict(schema='DTC_L2_MLP_CLOSED_RAW_REASON_SIDECAR_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(root),matrix_revision=matrix.get('revision'),rows=rows,skipped=skipped,sources=list(sources.values()),model_starts=0,original_strict_results_modified=False,no_missing_zero_fill=True,no_per_kernel_cumulative_double_count=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='/root/data/dtc_l2_mlp_exploration_20261027_v1');ap.add_argument('--reference-root',default='/root/data/dtc_hash_downstream18_20261027_v1');ap.add_argument('--stream-scope',default=str(P(__file__).resolve().parents[1]/'report_v1/input_stream_scope.json'));ap.add_argument('--output',required=True);a=ap.parse_args()
 out=P(a.output).resolve();root=P(a.root).resolve();assert not out.is_relative_to(root),'Derived sidecar must be outside experiment root';assert not out.exists(),'Use a new output filename; do not overwrite prior sidecars'
 v=collect(root,a.reference_root,a.stream_scope);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x')as h:json.dump(v,h,indent=2);h.write('\n')
 print(json.dumps(dict(status='READ_ONLY_SIDECAR_GENERATED',output=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),closed_accepted_rows=len(v['rows']),errors=sum(r['status']!='SIDECAR_EXTRACTED_CLOSED_ACCEPTED'for r in v['rows']),model_starts=0),indent=2))
if __name__=='__main__':main()
