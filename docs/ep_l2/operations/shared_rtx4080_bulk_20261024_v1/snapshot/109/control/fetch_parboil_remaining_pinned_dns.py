#!/usr/bin/env python3
import pathlib,json,hashlib,urllib.request,concurrent.futures,time,socket
_old_getaddrinfo=socket.getaddrinfo
def _pinned_raw(host,port,*a,**kw):
 return _old_getaddrinfo('185.199.108.133' if host=='raw.githubusercontent.com' else host,port,*a,**kw)
socket.getaddrinfo=_pinned_raw
r=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');root=r/'assets/parboil_source_verified';tree={x['path']:x for x in json.loads((r/'control/parboil_tree.json').read_text())};recovery=json.loads((r/'control/PARBOIL_PARTIAL_ARCHIVE_MEMBER_RECOVERY.json').read_text())
out=r/'assets/parboil_download_attempts';out.mkdir(exist_ok=True)
def fetch(path):
 x=tree[path];p=root/path
 if p.exists():return {'path':path,'status':'ALREADY_VERIFIED'}
 url='https://raw.githubusercontent.com/palmer-dabbelt/parboil/4e0fc54866546efa44fe93af57c9cef62f6c8eb9/'+path
 errs=[]
 for attempt in [3,4]:
  part=out/(x['sha']+'.attempt%03d'%attempt);part.parent.mkdir(parents=True,exist_ok=True)
  try:
   with urllib.request.urlopen(url,timeout=60) as src,part.open('xb') as f:
    while True:
     b=src.read(1048576)
     if not b:break
     f.write(b)
   b=part.read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   assert len(b)==x['size'] and sha==x['sha'],path
   p.parent.mkdir(parents=True,exist_ok=True)
   if x['mode']=='120000':p.symlink_to(b.decode())
   else:p.write_bytes(b);p.chmod(0o755 if x['mode']=='100755' else 0o644)
   return {'path':path,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':sha,'attempt':attempt,'status':'VERIFIED','prior_errors':errs}
  except Exception as e:errs.append(repr(e))
 return {'path':path,'url':url,'status':'DOWNLOAD_GAP_RETAINED','errors':errs}
receipts=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for f in concurrent.futures.as_completed([pool.submit(fetch,p) for p in recovery['remaining']]):
  rec=f.result();receipts.append(rec)
  (r/'control/PARBOIL_REMAINDER_DOWNLOAD_REPAIRED_DNS_RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')
  if len(receipts)%20==0:print('remaining_verified',sum(x['status']=='VERIFIED' for x in receipts),'done',len(receipts),flush=True)
print('COMPLETE',len(receipts),'gaps',sum(x['status']=='DOWNLOAD_GAP_RETAINED' for x in receipts),flush=True)

