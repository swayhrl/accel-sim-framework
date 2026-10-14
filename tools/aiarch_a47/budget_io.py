"""Bounded official-source transfers with persistent cumulative accounting."""
import fcntl,hashlib,json,os,pathlib,shutil,time,urllib.request
ROOT=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1')
def charge(n,kind,url):
 p=ROOT/'download_budget.json'
 with p.open('r+') as f:
  fcntl.flock(f,fcntl.LOCK_EX);d=json.load(f)
  assert d['total_bytes']+n<=6*1024**3,'TOTAL_DOWNLOAD_BUDGET'
  if kind=='data':assert d['data_bytes']+n<=int(.6*1024**3),'DATA_DOWNLOAD_BUDGET'
  d['total_bytes']+=n;d['data_bytes']+=n if kind=='data' else 0;f.seek(0);json.dump(d,f);f.truncate();f.flush()
def check_disk():
 work=pathlib.Path(json.loads((ROOT/'start.json').read_text())['work'])
 size=sum(p.stat().st_blocks*512 for r in [ROOT,work] for p in r.rglob('*') if p.is_file())
 assert size<=12*1024**3 and shutil.disk_usage(ROOT).free>=64*1024**3,'DISK_BUDGET'
 return size
def get_small(url,name,limit=16*1024**2):
 p=ROOT/'metadata'/name
 if p.exists():return p.read_bytes()
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as f:
  raw=f.read(limit+1);charge(len(raw),'metadata',url);assert len(raw)<=limit
 p.write_bytes(raw);return raw
def download(url,path,size,sha=None,kind='wheel',headers=None):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0',**(headers or {})});t=time.monotonic();n=0;h=hashlib.sha256()
 with urllib.request.urlopen(req,timeout=45) as f,open(path,'wb') as out:
  assert int(f.headers.get('Content-Length',size))==size
  response={'status':f.status,'final_url':f.geturl(),'etag':f.headers.get('ETag'),'content_range':f.headers.get('Content-Range')}
  while True:
   b=f.read(min(1024**2,size-n+1))
   if not b:break
   charge(len(b),kind,url);n+=len(b);assert n<=size;out.write(b);h.update(b)
   if n%(16*1024**2)<1024**2:check_disk()
 assert n==size,(n,size)
 if sha:assert h.hexdigest()==sha,'ENTITY_SHA_MISMATCH'
 receipt={'url':url,'bytes':n,'sha256':h.hexdigest(),'seconds':time.monotonic()-t,**response}
 return receipt
