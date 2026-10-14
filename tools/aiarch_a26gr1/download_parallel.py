"""Four controlled official Range processes; preserve verified sequential prefix."""
import concurrent.futures,datetime,hashlib,json,os,pathlib,signal,time,urllib.request
from control import ROOT,check,state,save
URL='https://storage.cmusatyalab.org/mega-nerf-data/rubble-pixsfm.tgz';SIZE=9773995561;ETAG='"f9702b00013597490519bdea8f922a68-1865"';CHUNK=32*1024**2
TMP=ROOT/'range_chunks';TMP.mkdir(exist_ok=True)
def fetch(start,end):
 rec={'start':start,'end':end,'received_body_bytes':0,'status':'ERROR'};p=TMP/str(start);t=time.monotonic()
 def alarm(a,b):raise RuntimeError('RANGE_HTTP_TOTAL_DEADLINE')
 signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,90)
 try:
  req=urllib.request.Request(URL,headers={'Range':'bytes='+str(start)+'-'+str(end),'If-Range':ETAG,'User-Agent':'AIARCH-A26GR1/1.0'})
  with urllib.request.urlopen(req,timeout=15) as h:
   rec['http_status']=h.status;rec['content_range']=h.headers.get('Content-Range');rec['etag']=h.headers.get('ETag')
   assert h.status==206 and rec['content_range']=='bytes '+str(start)+'-'+str(end)+'/'+str(SIZE)
   assert rec['etag']==ETAG,'SCIENTIFIC_HTTP_IDENTITY_CHANGED'
   sha=hashlib.sha256()
   with p.open('xb') as f:
    while rec['received_body_bytes']<end-start+1:
     b=h.read(min(1024**2,end-start+1-rec['received_body_bytes']))
     if not b:break
     f.write(b);sha.update(b);rec['received_body_bytes']+=len(b)
     if rec['received_body_bytes']%(8*1024**2)==0:check()
   assert rec['received_body_bytes']==end-start+1
   rec.update(status='PASS',sha256=sha.hexdigest())
 except Exception as e:rec.update(error_type=type(e).__name__,error=str(e))
 finally:signal.setitimer(signal.ITIMER_REAL,0)
 rec['wall_seconds']=time.monotonic()-t
 return rec
if __name__=='__main__':
 path=ROOT/'downloads/rubble-pixsfm.tgz.part';receipt=ROOT/'rubble-pixsfm.tgz.download.json';records=json.loads(receipt.read_text())['chunks'];position=sum(x['bytes'] for x in records)
 assert path.stat().st_size==position
 with path.open('rb') as f:
  for x in records:assert hashlib.sha256(f.read(x['bytes'])).hexdigest()==x['sha256']
 jobs=[(i,min(i+CHUNK,SIZE)-1) for i in range(position,SIZE,CHUNK)];started=time.monotonic();attempts=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
  for batch in range(0,len(jobs),4):
   group=jobs[batch:batch+4];reserved=sum(e-s+1 for s,e in group);check(extra=reserved*2)
   s=state();assert s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+reserved<=25*1024**3
   s['http_new_body_bytes']+=reserved;save(s)
   results=[f.result() for f in [pool.submit(fetch,a,b) for a,b in group]]
   actual=sum(x['received_body_bytes'] for x in results);s=state();s['http_new_body_bytes']-=reserved-actual;save(s)
   for res in results:
    with (ROOT/'parallel_range_receipts.jsonl').open('a') as f:f.write(json.dumps(res)+'\n')
    if res['status']!='PASS':
     attempts+=1
     if attempts>2:raise RuntimeError('NETWORK_BOUNDED_RETRIES_EXHAUSTED '+str(res))
     p=TMP/str(res['start']);assert p.resolve().is_relative_to(ROOT.resolve())
     if p.exists():p.unlink()
     n=res['end']-res['start']+1;s=state();assert s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+n<=25*1024**3;s['http_new_body_bytes']+=n;save(s)
     res=pool.submit(fetch,res['start'],res['end']).result();s=state();s['http_new_body_bytes']-=n-res['received_body_bytes'];save(s)
     with (ROOT/'parallel_range_receipts.jsonl').open('a') as f:f.write(json.dumps(res)+'\n')
     assert res['status']=='PASS',res
    assert res['start']==position
    p=TMP/str(position);sha=hashlib.sha256()
    with p.open('rb') as src,path.open('ab') as dst:
     while b:=src.read(4*1024**2):sha.update(b);dst.write(b)
    assert sha.hexdigest()==res['sha256'];position=res['end']+1
    records.append({'start':res['start'],'end':res['end'],'bytes':res['received_body_bytes'],'sha256':res['sha256'],'http_status':206})
    p.unlink();receipt.write_text(json.dumps({'url':URL,'expected_size':SIZE,'etag':ETAG,'status':'PARTIAL','chunks':records,'completed_bytes':position},indent=2)+'\n')
   if batch%12==0:print('PARALLEL_PROGRESS',position,SIZE,'elapsed_seconds',round(time.monotonic()-started,1),flush=True)
 sha=hashlib.sha256()
 with path.open('rb') as f:
  assert hashlib.sha256(f.read(65536)).hexdigest()=='176a6f8fe9b559d23140e4972265259dac31527b0ccacf60a8da414f70d16125';f.seek(0)
  while b:=f.read(4*1024**2):sha.update(b)
 path.rename(ROOT/'downloads/rubble-pixsfm.tgz');receipt.write_text(json.dumps({'url':URL,'expected_size':SIZE,'etag':ETAG,'status':'COMPLETE','chunks':records,'completed_bytes':position,'sha256':sha.hexdigest(),'parallel_workers':4,'parallel_wall_seconds':time.monotonic()-started,'budget':check()},indent=2)+'\n')
 print('FULL_ARCHIVE_SHA256',sha.hexdigest(),'BYTES',position,flush=True)
