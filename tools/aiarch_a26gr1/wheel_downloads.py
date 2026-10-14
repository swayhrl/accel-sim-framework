"""Pipelined official wheel acquisition, hash locks and shared budget accounting."""
import concurrent.futures,hashlib,json,os,pathlib,signal,time,urllib.request
from control import ROOT,http,state,save,check
FOLDER=ROOT/'wheels';FOLDER.mkdir(exist_ok=True)
def fetch(x):
 target=FOLDER/x['filename'];part=target.with_suffix(target.suffix+'.part');n=0;t=time.monotonic();r={'name':x['name'],'filename':x['filename'],'expected_sha256':x['sha256'],'received_body_bytes':0,'status':'FAIL'}
 def expire(a,b):raise RuntimeError('SOFTWARE_DOWNLOAD_DEADLINE')
 s=state();left=14400-s['cpu_prepare_active_before_resume_seconds']-(time.time()-s['cpu_prepare_resume_epoch'])
 signal.signal(signal.SIGALRM,expire);signal.setitimer(signal.ITIMER_REAL,max(1,min(600,left-2)))
 try:
  req=urllib.request.Request(x['url'],headers={'User-Agent':'AIARCH-A26GR1/1.0'})
  with urllib.request.urlopen(req,timeout=30) as h:
   assert h.status==200 and int(h.headers.get('Content-Length',-1))==x['bytes']
   sha=hashlib.sha256()
   with part.open('xb') as f:
    while n<x['bytes']:
     b=h.read(min(1024**2,x['bytes']-n))
     if not b:break
     f.write(b);sha.update(b);n+=len(b)
     if n%(32*1024**2)==0:check()
   assert n==x['bytes'] and sha.hexdigest()==x['sha256'],'SOFTWARE_SHA_OR_SIZE_MISMATCH'
   part.rename(target);r.update(status='PASS',sha256=sha.hexdigest())
 except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
 finally:signal.setitimer(signal.ITIMER_REAL,0)
 r.update(received_body_bytes=n,wall_seconds=time.monotonic()-t);return r
if __name__=='__main__':
 assert json.loads((ROOT/'colmap_identity.json').read_text())['status']=='REAL_SCENE_BYTE_CORRESPONDENCE_PASS'
 lock=json.loads((ROOT/'distribution_closure.json').read_text());jobs=[]
 for x in lock['official_registry_wheels']:
  p=FOLDER/x['filename']
  if p.exists():assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
  else:jobs.append(x)
 # CPU image decoding packages are fetched first so preprocessing can start while the rest download.
 order=['numpy','pillow','imageio','scipy','packaging','setuptools','wheel'];jobs.sort(key=lambda x:(order.index(x['name']) if x['name'] in order else 100,x['bytes']))
 receipts=[];retry_count=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
  for i in range(0,len(jobs),4):
   group=jobs[i:i+4];reserve=sum(x['bytes'] for x in group);check(extra=reserve)
   s=state();assert s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+reserve<=25*1024**3;s['http_new_body_bytes']+=reserve;save(s)
   results=[f.result() for f in [pool.submit(fetch,x) for x in group]]
   s=state();s['http_new_body_bytes']-=reserve-sum(r['received_body_bytes'] for r in results);save(s)
   for x,r in zip(group,results):
    receipts.append(r)
    if r['status']!='PASS':
     retry_count+=1
     if retry_count>2:raise RuntimeError('OFFICIAL_WHEEL_DOWNLOAD_BOUNDED_RETRIES_EXHAUSTED '+str(r))
     p=(FOLDER/x['filename']).with_suffix('.whl.part');assert p.resolve().is_relative_to(ROOT.resolve())
     if p.exists():p.unlink()
     s=state();assert s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+x['bytes']<=25*1024**3;s['http_new_body_bytes']+=x['bytes'];save(s)
     r=pool.submit(fetch,x).result();s=state();s['http_new_body_bytes']-=x['bytes']-r['received_body_bytes'];save(s);receipts.append(r);assert r['status']=='PASS',r
   (ROOT/'wheel_download_receipts.json').write_text(json.dumps({'status':'PARTIAL','files':receipts},indent=2)+'\n')
   print('OFFICIAL_WHEEL_BATCH_READY',min(i+4,len(jobs)),len(jobs),flush=True)
 (ROOT/'wheel_download_receipts.json').write_text(json.dumps({'status':'PASS','files':receipts,'package_count':len(lock['official_registry_wheels']),'budget':check()},indent=2)+'\n');print('ALL_LOCKED_WHEELS_PASS',len(lock['official_registry_wheels']),flush=True)
