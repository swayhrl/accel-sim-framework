import os,resource,pathlib,json,hashlib,time,urllib.request,urllib.error,shutil
os.sched_setaffinity(0,[0]);resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0));R=pathlib.Path('/data/c16/aiarch_a59_license_authority_cpu_109_v1');W=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 s=json.loads((R/'start.json').read_text());assert time.time()<s['deadline_epoch'],'TIME_LIMIT';size=sum(p.stat().st_blocks*512 for root in [R,W] for p in root.rglob('*') if p.is_file() and not p.is_symlink());assert size<32*1024**2 and shutil.disk_usage(R).free>=64*1024**3,'DISK_LIMIT';return size

def fetch(url,name,limit=1024**2,headers=None):
 check();ledger=R/'raw/requests.jsonl';used=sum(x.get('bytes',0) for x in map(json.loads,ledger.read_text().splitlines())) if ledger.exists() else 0;assert used+limit<=16*1024**2;row={'url':url,'start_epoch':time.time(),'method':'GET','max_bytes':limit};b=b''
 try:
  q=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AIARCH-A59-license-audit',**(headers or {})}),timeout=25);row.update(status=q.status,final_url=q.url,headers=dict(q.headers));assert not (headers or {}).get('Range') or q.status==206,'RANGE_NOT_HONORED_NO_BODY_READ';
  while len(b)<=limit:
   chunk=q.read(min(65536,limit+1-len(b)))
   if not chunk:break
   b+=chunk
  q.close();assert len(b)<=limit
 except urllib.error.HTTPError as e:row.update(status=e.code,error=repr(e),headers=dict(e.headers));b=e.read(min(limit,16384))
 except Exception as e:row['error']=repr(e)
 p=R/'sources'/name;p.write_bytes(b);row.update(bytes=len(b),path=str(p),sha256=sha(p),finish_epoch=time.time());
 with ledger.open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps({k:v for k,v in row.items() if k not in ['headers']}),flush=True);check();return row,b
