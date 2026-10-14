"""Controlled one-file official Range download with cumulative caps and resumes."""
import argparse,hashlib,json,pathlib,time
from control import ROOT,http,state,save,check
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--name',required=True);p.add_argument('--size',type=int,required=True);p.add_argument('--sha256');p.add_argument('--etag');a=p.parse_args()
assert pathlib.Path(a.name).name==a.name and '/' not in a.name and '\\' not in a.name
folder=ROOT/'downloads';folder.mkdir(exist_ok=True);dst=folder/a.name;part=folder/(a.name+'.part');receipt=ROOT/(a.name+'.download.json')
check(extra=a.size-(part.stat().st_size if part.exists() else 0))
r,b=http(a.url,'HEAD');assert r.get('status')==200,r
headers={k.lower():v for k,v in r['headers'].items()};assert int(headers['content-length'])==a.size
etag=headers.get('etag');assert not a.etag or etag==a.etag,'SCIENTIFIC_HTTP_IDENTITY_CHANGED'
if dst.exists():
 assert dst.stat().st_size==a.size
 raise SystemExit('COMPLETE_ASSET_ALREADY_EXISTS_VERIFY_ONLY')
records=json.loads(receipt.read_text())['chunks'] if receipt.exists() else []
position=part.stat().st_size if part.exists() else 0
assert sum(x['bytes'] for x in records)==position
if position:
 with part.open('rb') as f:
  for x in records:assert hashlib.sha256(f.read(x['bytes'])).hexdigest()==x['sha256']
t0=time.monotonic();chunk=32*1024**2
while position<a.size:
 n=min(chunk,a.size-position);end=position+n-1;check(extra=n)
 s=state();assert s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']+n<=25*1024**3,'DOWNLOAD_BUDGET_WOULD_BE_EXCEEDED'
 for attempt in range(3):
  rec,data=http(a.url,limit=n,headers={'Range':'bytes='+str(position)+'-'+str(end),'If-Range':etag} if etag else {'Range':'bytes='+str(position)+'-'+str(end)},deadline=90)
  h={k.lower():v for k,v in rec.get('headers',{}).items()}
  good=rec.get('status')==206 and h.get('content-range')=='bytes '+str(position)+'-'+str(end)+'/'+str(a.size) and len(data)==n
  if position==0 and n==a.size:good|=rec.get('status')==200 and len(data)==a.size
  if etag and h.get('etag') and h['etag']!=etag:raise RuntimeError('HTTP_IDENTITY_CHANGED_NO_SPLICE')
  if good:break
  if attempt==2:raise RuntimeError('NETWORK_DOWNLOAD_BOUNDED_RETRIES_EXHAUSTED '+str(rec))
 with part.open('ab') as f:f.write(data);f.flush()
 records.append({'start':position,'end':end,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'http_status':rec['status']});position+=len(data)
 receipt.write_text(json.dumps({'url':a.url,'expected_size':a.size,'etag':etag,'status':'PARTIAL','chunks':records,'completed_bytes':position},indent=2)+'\n')
 if len(records)%8==0:print('DOWNLOAD_PROGRESS',a.name,position,a.size,'elapsed_seconds',round(time.monotonic()-t0,1),flush=True)
sha=hashlib.sha256()
with part.open('rb') as f:
 while b:=f.read(4*1024**2):sha.update(b)
assert not a.sha256 or sha.hexdigest()==a.sha256,'FULL_SHA_MISMATCH'
if a.name=='rubble-pixsfm.tgz':
 with part.open('rb') as f:
  assert hashlib.sha256(f.read(65536)).hexdigest()=='176a6f8fe9b559d23140e4972265259dac31527b0ccacf60a8da414f70d16125','A26G_PREFIX_CHANGED'
  f.seek(-32,2);assert hashlib.sha256(f.read()).hexdigest()=='261708c427a3399b1c35e941bb5d4442c670f4e84388709d0e8a0baf2b525e6e','A26G_FOOTER_CHANGED'
part.rename(dst);receipt.write_text(json.dumps({'url':a.url,'expected_size':a.size,'etag':etag,'status':'COMPLETE','chunks':records,'completed_bytes':position,'sha256':sha.hexdigest(),'wall_seconds':time.monotonic()-t0,'budget':check()},indent=2)+'\n')
print('DOWNLOAD_COMPLETE',a.name,position,sha.hexdigest(),flush=True)
