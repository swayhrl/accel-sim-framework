#!/usr/bin/env python3
"""Tiny lifecycle tests: native CPU fixture only; no dispatcher main, GPU, or NAS payload."""
import pathlib,os,json,hashlib,subprocess,time,signal,sys,ast
D=pathlib.Path(__file__).resolve().parent
F=D/'cpu_fixture';F.mkdir(exist_ok=True)
W=D/'remote_watchdog_candidate.py'
worker=F/'worker.py'
worker.write_text("""import pathlib,sys,json,subprocess,signal,time,os
j=json.loads(pathlib.Path(sys.argv[1]).read_text());d=pathlib.Path(j['fixture'])
def track(pid):
 with (d/'pids').open('a') as f:f.write(str(pid)+'\\n')
track(os.getpid())
if j['mode']=='normal':
 print('x'*262144);sys.exit(0)
if j['mode']=='leaf':
 child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)'],start_new_session=True);track(child.pid)
 def term(sig,frame):
  c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True);track(c.pid);sys.exit(0)
 signal.signal(signal.SIGTERM,term)
while True:time.sleep(.05)
""")
launcher="""import sys,pathlib
ns={'__name__':'cpu_fixture_import'};p=pathlib.Path(sys.argv[1]);exec(compile(p.read_text(),str(p),'exec'),ns)
ns['HEARTBEAT_GRACE']=0.8;ns['MIN_REMAINING']=0;ns['ATTEMPT_ROOT']=pathlib.Path(sys.argv[2])
sys.argv=sys.argv[2:];sys.argv[0]='fixture_watchdog';sys.exit(ns['main']())
"""
results=[]
for case in ['normal','deadline','eof','expiry','sigterm','sighup']:
 case_dir=F/case;case_dir.mkdir(exist_ok=True)
 marker=case_dir/'pids';marker.unlink(missing_ok=True)
 job=case_dir/'job.json';job.write_text(json.dumps({'id':'CPU_ONLY','mode':'normal' if case=='normal' else 'leaf','fixture':str(case_dir)}))
 limit=1.0 if case=='deadline' else 10
 args=[sys.executable,'-B','-c',launcher,str(W),str(F),str(worker),hashlib.sha256(worker.read_bytes()).hexdigest(),str(job),hashlib.sha256(job.read_bytes()).hexdigest(),str(time.time()+60),str(limit)]
 p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 p.stdin.write('alive\n');p.stdin.flush()
 if case!='normal':
  until=time.monotonic()+3
  while not marker.exists() and p.poll() is None and time.monotonic()<until:time.sleep(.02)
  time.sleep(.15)
 if case=='eof':p.stdin.close();p.stdin=None
 elif case=='sigterm':os.kill(p.pid,signal.SIGTERM)
 elif case=='sighup':os.kill(p.pid,signal.SIGHUP)
 elif case=='deadline':
  # Heartbeats continue long enough that deadline, rather than expiry, wins.
  for _ in range(5):
   if p.poll() is None:
    try:p.stdin.write('alive\n');p.stdin.flush()
    except BrokenPipeError:break
   time.sleep(.15)
 if case in ['normal','expiry','sigterm','sighup','deadline']:
  # communicate would close stdin and test EOF instead; wait while draining normal output.
  if case=='normal':
   out=p.stdout.read();err=p.stderr.read();p.wait(timeout=8)
   p.stdin.close();p.stdin=None
  else:
   p.wait(timeout=8);out=p.stdout.read();err=p.stderr.read()
 else:out,err=p.communicate(timeout=8)
 pids=[int(x) for x in marker.read_text().split()] if marker.exists() else []
 surviving=[]
 for pid in pids:
  stat=pathlib.Path('/proc',str(pid),'stat')
  if stat.exists():surviving.append(pid)
 expected=0 if case=='normal' else 74
 assert p.returncode==expected,(case,p.returncode,out[-2000:],err[-2000:])
 assert not surviving,(case,'surviving fixtures',surviving)
 if case!='normal':
  reason=json.loads(out)['error']
  expect={'deadline':'guard deadline','eof':'parent channel EOF','expiry':'heartbeat expired','sigterm':'signal 15','sighup':'signal 1'}[case]
  assert reason==expect,(case,reason)
 results.append({'case':case,'returncode':p.returncode,'fixture_pids':pids,'surviving':surviving,'stdout_bytes':len(out),'stderr':err[-2000:]})
# External sibling must survive wrong-ticks and process-tree scope tests.
ns={'__name__':'cpu_fixture_import'};exec(compile(W.read_text(),str(W),'exec'),ns)
external=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
try:
 ident=ns['ident'](external.pid)
 assert ns['send']((ident[0],str(int(ident[1])+1),ident[2]),signal.SIGTERM)==False
 assert external.poll() is None
 assert external.pid not in [x[0] for x in ns['children'](ns['ident'](os.getpid())) if x[0]!=external.pid]
 results.append({'case':'pidfd_wrong_ticks_external_alive','pid':external.pid,'passed':external.poll() is None})
finally:external.terminate();external.wait(timeout=3)

(D/'WATCHDOG_CPU_FIXTURE_RESULT_V1.json').write_text(json.dumps({'status':'EXACT_WATCHDOG_CPU_LIFECYCLE_PASS','watchdog_sha256':hashlib.sha256(W.read_bytes()).hexdigest(),'results':results,'GPU_started':False,'source_KEEP':True},sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':'EXACT_WATCHDOG_CPU_LIFECYCLE_PASS','cases':len(results)}))
