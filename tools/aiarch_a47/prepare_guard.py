import pathlib,os,json,time,signal,shutil
from budget_io import ROOT,check_disk
os.sched_setaffinity(0,[0,2,4,6]);started=json.loads((ROOT/'start.json').read_text())['epoch'];samples=[];maxrss=0;peakrunning=0
while time.time()-started<7200:
 roots=[x for x in json.loads((ROOT/'prepare_pids.json').read_text()).values() if isinstance(x,int)];roots.append(os.getpid())
 table={}
 for p in pathlib.Path('/proc').glob('[0-9]*'):
  try:
   a=p.joinpath('stat').read_text().split();table[int(p.name)]=(int(a[3]),a[2])
  except (OSError,ValueError):pass
 pids=set(roots)
 for _ in range(6):pids.update(k for k,v in table.items() if v[0] in pids)
 rss=0;running=0
 for pid in pids:
  try:
   s=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in s.splitlines() if x.startswith('VmRSS:')))*1024
   for t in pathlib.Path(f'/proc/{pid}/task').iterdir():
    try:running+=t.joinpath('stat').read_text().split()[2]=='R'
    except OSError:pass
  except (OSError,StopIteration):pass
 maxrss=max(maxrss,rss);peakrunning=max(peakrunning,running);size=check_disk()
 if rss>8*1024**3:
  for pid in pids-{os.getpid()}:
   try:os.kill(pid,signal.SIGTERM)
   except ProcessLookupError:pass
  (ROOT/'prepare_guard_failure.json').write_text(json.dumps({'reason':'RAM_BUDGET','rss':rss}));break
 samples.append({'epoch':time.time(),'rss':rss,'running':running,'disk':size});samples=samples[-1000:]
 (ROOT/'prepare_resource.json').write_text(json.dumps({'peak_tree_rss_bytes_sampled':maxrss,'peak_running_threads_sampled':peakrunning,'CPU_affinity_effective_logical_limit':[0,2,4,6],'samples':samples}))
 if all(pid not in table or table[pid][1]=='Z' for pid in roots if pid!=os.getpid()):break
 time.sleep(.5)
