import os,pathlib,json,hashlib,time,urllib.request,urllib.error,shutil
os.sched_setaffinity(0,[0,2,4,6]);ROOT=pathlib.Path('/data/c16/aiarch_a59_graphsage_products_native_109_v1');WORK=pathlib.Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def receipt(x):
 with (ROOT/'raw/http_receipts.jsonl').open('a') as f:f.write(json.dumps({'epoch':time.time(),**x})+'\n')
def used(kind=None):
 p=ROOT/'raw/http_receipts.jsonl'
 return sum(x.get('bytes',0) for x in map(json.loads,p.read_text().splitlines()) if kind is None or x.get('kind')==kind) if p.exists() else 0
def check():
 size=sum(p.stat().st_blocks*512 for root in [ROOT,WORK] for p in root.rglob('*') if p.is_file() and not p.is_symlink());assert size<8*1024**3 and shutil.disk_usage(ROOT).free>=64*1024**3,'DISK_BUDGET';assert time.time()-json.loads((ROOT/'start.json').read_text())['epoch']<7200,'CPU_PREP_TIMEOUT';return size

def request(url,name=None,method='GET',kind='metadata',limit=2*1024**2,headers=None):
 check();total=used();kc=used(kind);cap=min(4*1024**3-total,(int(1.5*1024**3)-kc) if kind=='dependency' else (int(2.5*1024**3)-kc) if kind=='data' else limit);assert cap>0
 req=urllib.request.Request(url,headers={'User-Agent':'AIARCH-A59-bounded-research',**(headers or {})},method=method);t=time.monotonic();data=bytearray();p=ROOT/name if name else None;f=None;row={'url':url,'method':method,'kind':kind,'bytes':0}
 try:
  resp=urllib.request.urlopen(req,timeout=40);row.update(status=resp.status,final_url=resp.url,headers=dict(resp.headers));length=int(resp.headers.get('Content-Length',0));assert method=='HEAD' or length<=min(cap,limit),'KNOWN_ENTITY_EXCEEDS_AUTHORIZED_BUDGET'
  if p:p.parent.mkdir(exist_ok=True,parents=True);f=p.open('wb')
  while method!='HEAD':
   b=resp.read(min(1024**2,int(min(cap,limit)-row['bytes'])+1))
   if not b:break
   row['bytes']+=len(b);assert row['bytes']<=min(cap,limit),'DOWNLOAD_BOUND'
   if f:f.write(b)
   else:data.extend(b)
   check()
  resp.close()
 except urllib.error.HTTPError as e:
  data.extend(e.read(min(8192,int(cap))));row.update(status=e.code,error=repr(e),bytes=len(data))
 except Exception as e:row['error']=repr(e)
 finally:
  if f:f.close()
  row['seconds']=time.monotonic()-t
  if p and p.exists():row.update(path=str(p),sha256=sha(p))
  else:row['body_excerpt']=data[:500].decode(errors='replace')
  receipt(row)
 return row,bytes(data)
