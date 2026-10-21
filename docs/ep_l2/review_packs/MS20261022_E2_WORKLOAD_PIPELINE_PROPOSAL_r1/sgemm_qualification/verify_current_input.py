"""One approved, identity-only streaming SHA pass; no grammar or trace output."""
import pathlib, hashlib, json, time, datetime, os
out=pathlib.Path(__file__).resolve().parent
review=json.loads((out.parent/'sgemm_review/STATIC_REVIEW.json').read_text())
rows=[]
for source in review['input_stats']:
 p=pathlib.Path(source['path']); fd=os.open(p,os.O_RDONLY); pre=os.fstat(fd); before=p.stat(); h=hashlib.sha256(); read=0; start=time.monotonic()
 with os.fdopen(fd,'rb') as f:
  while True:
   block=f.read(8*1024*1024)
   if not block: break
   h.update(block); read+=len(block)
  post=os.fstat(f.fileno())
 after=p.stat()
 def fp(s): return {'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'bytes':s.st_size,'allocated_bytes':s.st_blocks*512,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
 unchanged=fp(pre)==fp(post)==fp(before)==fp(after)
 row={'path':str(p),'before':fp(pre),'after':fp(post),'path_stat_after':fp(after),'streamed_bytes':read,'sha256':h.hexdigest(),'expected_sha256':source['saved_expected_sha256'],'before_after_unchanged':unchanged,'wall_seconds':time.monotonic()-start}
 row['PASS']=unchanged and read==pre.st_size and row['sha256']==row['expected_sha256']; rows.append(row)
 report={'schema':'E2_SGEMM_CURRENT_COMPLETE_INPUT_IDENTITY_V1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if all(x['PASS'] for x in rows) else 'FAIL','scope':'One current content identity pass; existing complete D grammar and non-atomic evidence reused by exact SHA. No grammar scan, application or native execution.','files':rows,'trace_content_sha256':review['saved_trace_content_sha256'],'composite_definition':'Named files canonical JSON list, inherited original coordinator input digest; independently recomputed during runner inspection','application_starts':0,'native_starts':0}
 (out/'CURRENT_INPUT_IDENTITY.json').write_text(json.dumps(report,indent=2)+'\n')
 assert report['status']=='PASS',report
print(json.dumps({'status':report['status'],'files':len(rows),'bytes_read':sum(x['streamed_bytes'] for x in rows),'wall_seconds':sum(x['wall_seconds'] for x in rows)}))
