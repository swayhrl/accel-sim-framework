"""CPU budget and audited HTTP helpers; no framework imports or GPU operations."""
import datetime,hashlib,json,os,pathlib,resource,shutil,signal,time,urllib.request,urllib.error
ROOT=pathlib.Path(os.environ['A26R_ROOT']);WORK=pathlib.Path(os.environ['A26R_WORK'])
def state():return json.loads((ROOT/'budget_state.json').read_text())
def save(s):(ROOT/'budget_state.json').write_text(json.dumps(s,indent=2)+'\n')
def allocated(root):return sum(p.stat().st_blocks*512 for p in root.rglob('*') if p.is_file() and not p.is_symlink())
def check(extra=0):
 s=state();elapsed=time.time()-s['r1_goal_started_epoch']
 if s.get('cpu_prepare_resume_epoch'):elapsed=s['cpu_prepare_active_before_resume_seconds']-s['prior_cpu_prepare_seconds']+time.time()-s['cpu_prepare_resume_epoch']
 if s.get('cpu_prepare_complete_epoch'):elapsed=s['cpu_prepare_cumulative_at_qualification']-s['prior_cpu_prepare_seconds']
 if elapsed+s['prior_cpu_prepare_seconds']>=14400:raise RuntimeError('CPU_PREPARE_BUDGET_STOP')
 if s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes']>25*1024**3:raise RuntimeError('DOWNLOAD_BUDGET_STOP')
 free=shutil.disk_usage(ROOT).free
 if free-extra<64*1024**3:raise RuntimeError('FILESYSTEM_RESERVE_STOP')
 used=s['prior_disk_conservative_bytes']+allocated(ROOT)+allocated(WORK)+s.get('controller_new_disk_bytes',0)
 if used+extra>=60*1024**3:raise RuntimeError('NEW_DISK_CAP_STOP')
 return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_bytes':free,'task_allocated_bytes_conservative':used,'cpu_wall_cumulative_seconds':elapsed+s['prior_cpu_prepare_seconds'],'http_cumulative_bytes':s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes'],'collector_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
def http(url,method='GET',limit=2*1024**2,headers=None,deadline=30):
 rec={'url':url,'method':method,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};data=bytearray();t=time.monotonic()
 def expire(a,b):raise RuntimeError('HTTP_TOTAL_DEADLINE')
 old=signal.signal(signal.SIGALRM,expire);signal.setitimer(signal.ITIMER_REAL,deadline)
 try:
  req=urllib.request.Request(url,method=method,headers={'User-Agent':'AIARCH-A26GR1/1.0',**(headers or {})})
  with urllib.request.urlopen(req,timeout=15) as h:
   rec.update(status=h.status,headers={k:v for k,v in h.headers.items() if k.lower() in ['content-length','content-range','etag','last-modified','content-type','accept-ranges']})
   if method!='HEAD':
    while len(data)<limit:
     b=h.read(min(65536,limit-len(data)))
     if not b:break
     data.extend(b)
 except urllib.error.HTTPError as e:rec.update(status=e.code,error='HTTPError');data=e.read(min(limit,65536))
 except Exception as e:rec.update(error_type=type(e).__name__,error=str(e))
 finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
 data=bytes(data)
 s=state();s['http_new_body_bytes']+=len(data);save(s)
 rec.update(received_body_bytes=len(data),body_sha256=hashlib.sha256(data).hexdigest(),wall_seconds=time.monotonic()-t)
 with (ROOT/'http_receipts.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 check();return rec,data
