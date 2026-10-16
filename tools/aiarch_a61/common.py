import os,pathlib,json,hashlib,time,urllib.request,urllib.error,shutil,fcntl
os.sched_setaffinity(0,[0,2,4,6]);R=pathlib.Path('/data/c16/aiarch_a61_igb_small_gnn_native_109_v1');W=pathlib.Path(__file__).resolve().parents[2]
def sha(p,algo='sha256'):
 h=hashlib.new(algo)
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2)+'\n')
def check():
 size=sum(p.stat().st_blocks*512 for root in [R,W] for p in root.rglob('*') if p.is_file() and not p.is_symlink());assert size<14*1024**3,'NEW_DISK_LIMIT';assert shutil.disk_usage(R).free>=64*1024**3,'FREE_FS_LIMIT';return size

def rows():
 p=R/'raw/http.jsonl';return list(map(json.loads,p.read_text().splitlines())) if p.exists() else []
def receipt(d):
 with (R/'raw/http.jsonl').open('a') as f:f.write(json.dumps(d)+'\n')
def request(url,name=None,method='GET',kind='metadata',limit=2*1024**2,headers=None):
 check();prior=rows();used=sum(x.get('bytes',0) for x in prior);kused=sum(x.get('bytes',0) for x in prior if x.get('kind')==kind);cap=min(6*1024**3-used,(int(4.5*1024**3)-kused) if kind=='data' else(int(1.5*1024**3)-kused) if kind=='dependency' else limit);assert cap>0
 row={'url':url,'kind':kind,'method':method,'start_epoch':time.time(),'bytes':0};p=R/name if name else None;f=None;b=bytearray();h=hashlib.sha256()
 try:
  q=urllib.request.urlopen(urllib.request.Request(url,method=method,headers={'User-Agent':'AIARCH-A61-approved-research',**(headers or {})}),timeout=30);row.update(status=q.status,final_url=q.url,headers=dict(q.headers));length=int(q.headers.get('Content-Length',0));assert method=='HEAD' or length<=min(limit,cap),'KNOWN_LENGTH_BUDGET';assert not (headers or {}).get('Range') or q.status==206,'RANGE_NOT_HONORED'
  if p:p.parent.mkdir(parents=True,exist_ok=True);f=p.open('wb')
  if method!='HEAD':
   while True:
    chunk=q.read(min(1024**2,int(min(limit,cap)-row['bytes'])))
    if not chunk:break
    row['bytes']+=len(chunk);h.update(chunk)
    if f:f.write(chunk)
    else:b.extend(chunk)
    if row['bytes']>=min(limit,cap):assert length==row['bytes'],'ENTITY_REACHED_BUDGET_WITHOUT_KNOWN_COMPLETION';break
    if row['bytes']%(64*1024**2)<1024**2:check()
  q.close()
 except urllib.error.HTTPError as e:
  row.update(status=e.code,error=repr(e),headers=dict(e.headers));b.extend(e.read(8192));row['bytes']+=len(b);h.update(b)
 except Exception as e:row['error']=repr(e)
 finally:
  if f:f.close()
  if p and not f and b:p.write_bytes(b)
  row.update(finish_epoch=time.time(),sha256=h.hexdigest())
  if p:row['path']=str(p)
  receipt(row)
 return row,bytes(b)
