#!/usr/bin/env python3
"""DRAFT: Root review required. No import-time scheduling. Never run during preparation."""
import pathlib,json,time,hashlib,fcntl,os,subprocess,threading,shlex,traceback,shutil
D=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
# Original v3 save/sha/publish/update_job functions are copied verbatim below.
def save(p,o):
 t=p.with_name(p.name+'.tmp')
 with t.open('w') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   t=time.monotonic();h.update(b);time.sleep(max(0,len(b)/(15*1048576)-(time.monotonic()-t)))
 return h.hexdigest()
def publish(sender):
 root=B/sender['inflight'];assert B in root.parents
 manifest=root/'SENDER_MANIFEST.json';assert sha(manifest)==sender['sender_manifest_sha256']
 m=json.loads(manifest.read_text())
 asset=m['asset']
 assert asset['kind']=='FULL_APPLICATION_TRACE' and asset['producer_semantic_qualification']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 assert asset['capture_gpu_uuid']=='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59' and asset['actual_cubin_arch']==89
 assert sha(root/asset.get('binary_member','bin/vectorAdd'))==asset['binary_sha256']
 assert sha(root/'tools/producer.so')==asset['producer_sha256']
 validation=json.loads((root/'FULL_RECORD_VALIDATION.json').read_text())
 assert validation['kernels']==asset['full_application']['kernel_launches'] and validation['all_declared_warps_terminate']
 raw={p.name for p in (root/'traces').glob('kernel*.trace.xz')}
 lists=list((root/'traces').glob('kernelslist_ctx_*'));assert len(lists)==1
 named={line.strip() for line in lists[0].read_text().splitlines() if line.strip().startswith('kernel')}
 assert raw==named and len(raw)==validation['kernels']
 assert len(list((root/'traces').glob('kernel*.traceg.xz')))==len(raw)
 for x in m['files']:
  p=root/x['path'];assert root in p.parents and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x
 for name in ['PARENT_ORDINARY_BULK_RELEASE.json','CHANNEL_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_V2_QUALIFICATION_RECEIPT.json','PUMP_V2_AB_RECEIVER_QUALIFICATION.json']:
  src=C/name;dst=root/('RECEIVER_'+name);assert not dst.exists();shutil.copyfile(src,dst)
 actual=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
 final={'asset_id':sender['asset_id'],'source_sender_manifest_sha256':sender['sender_manifest_sha256'],'files':actual,'file_count':len(actual),'logical_bytes':sum(x['bytes'] for x in actual)}
 save(root/'MANIFEST.json',final);digest=sha(root/'MANIFEST.json')
 commit={'schema':'RTX4080_SHARED_IMMUTABLE_COMMIT_V1','kind':'FULL_APPLICATION_TRACE','status':'COMMITTED_VERIFIED','asset_id':sender['asset_id'],'manifest_sha256':digest,'files':len(actual),'logical_bytes':final['logical_bytes'],'producer_semantic_status':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_per_profile_qualification':'NOT_AUTOMATICALLY_GRANTED','source_keep':True,'release_bytes':0,'ssd_payload_staging_bytes':0,'utc_unix':time.time(),'channel':'dedicated RTX4080 Native174 locks;109->privateSSHFS174new->true164'}
 save(root/'COMMIT.json',commit)
 dest=B/'objects'/sender['asset_id'];assert not dest.exists();root.rename(dest)
 assert sha(dest/'MANIFEST.json')==digest
 for x in actual:
  p=dest/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 commit['object_path']=str(dest);save(B/'receipts'/(sender['asset_id']+'_RECEIVER_READBACK.json'),commit)
 cat=B/'catalog/ASSETS.json';data=json.loads(cat.read_text()) if cat.exists() else {'schema':'RTX4080_ASSET_CATALOG_V1','objects':[]}
 assert all(x['asset_id']!=sender['asset_id'] for x in data['objects']);data['objects'].append(commit);save(cat,data)
 return commit
def update_job(job):
 f=open(C/'RTX4080_QUEUE.lock','a');fcntl.flock(f,fcntl.LOCK_EX)
 try:
  fresh=json.loads((C/'QUEUE.json').read_text());found=False
  for i,x in enumerate(fresh):
   if x['id']==job['id']:fresh[i]=job;found=True;break
  assert found,'job lost from queue'
  save(C/'QUEUE.json',fresh)
 finally:fcntl.flock(f,fcntl.LOCK_UN);f.close()

SNAPSHOT_SHA='8c0af4fa9cf7a6f2a742a2c003f658bc89750437dc96cfcb6f7c087c75da8259'
PILOT_IDS=('ORD_Parboil_spmv_2b5047e90504_A001','ORD_Parboil_spmv_30a625972ad8_A001','ORD_Parboil_spmv_ce342c25b419_A001')
IDENTITY_KEYS=('id','type','worker_script','worker_sha256','job_path')
def scope_jobs(queue,frozen,selected):
 byid={}
 for job in queue:
  if job['id'] in byid:raise RuntimeError('duplicate queue ID')
  byid[job['id']]=job
 out=[]
 for id in selected:
  if id not in frozen:raise RuntimeError('outside frozen50')
  live=byid.get(id)
  if live is None:raise RuntimeError('frozen job disappeared')
  if any(live.get(k)!=frozen[id].get(k) for k in IDENTITY_KEYS):raise RuntimeError('frozen identity changed')
  if live.get('status')=='PENDING':out.append(dict(live))
 return out
def run_remote(job,frozen,deadline,err):
 code=(D/'remote_watchdog_candidate.py').read_text()
 args=[job['worker_script'],job['worker_sha256'],job['job_path'],frozen['job_sha256'],str(deadline-120),str(20*3600)]
 command='exec python3 -B -c '+shlex.quote(code)+' '+' '.join(shlex.quote(x) for x in args)
 # stdin is a heartbeat channel: EOF, parent death, disconnect, or stall fail closed remotely.
 chunks=[];overflow=threading.Event();size=[0]
 p=subprocess.Popen(['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=12','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=3','gpu109',command],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True)
 def drain():
  while True:
   chunk=p.stdout.read(8192)
   if not chunk:break
   size[0]+=len(chunk)
   if size[0]<=1048576:chunks.append(chunk)
   else:overflow.set()
 reader=threading.Thread(target=drain,daemon=True);reader.start()
 stopped=threading.Event()
 def pulse():
  try:
   while not stopped.is_set():
    p.stdin.write('alive\n');p.stdin.flush()
    if stopped.wait(2):break
  except (BrokenPipeError,OSError,ValueError):pass
 t=threading.Thread(target=pulse,daemon=True);t.start()
 try:
  # Remote deadline has two minutes reserved for identity checked cleanup and transport.
  p.wait(timeout=min(20*3600+90,max(1,deadline-time.time()-30)))
  reader.join(timeout=3)
  assert not reader.is_alive() and not overflow.is_set(),'remote stdout bound exceeded'
  return p.returncode,''.join(chunks)
 except BaseException:
  # Close heartbeat; do not treat killing ssh alone as remote cleanup.
  stopped.set();t.join(timeout=3)
  try:p.stdin.close()
  except (OSError,ValueError):pass
  try:p.wait(timeout=45)
  except subprocess.TimeoutExpired:p.kill();p.wait()
  raise RuntimeError('transport interrupted; cleanup must be independently acknowledged; do not launch another job')
 finally:
  stopped.set();t.join(timeout=3)
  try:p.stdin.close()
  except (OSError,ValueError):pass
def main():
 snap_path=D/'FROZEN_PENDING_36_AFTER.json'
 assert hashlib.sha256(snap_path.read_bytes()).hexdigest()==SNAPSHOT_SHA,'snapshot changed'
 snap=json.loads(snap_path.read_text());frozen={j['id']:j for j in snap['jobs']}
 assert len(frozen)==36
 # Explicit invocation chooses pilot3 or all frozen50. No automatic extension.
 import sys
 assert len(sys.argv)==2 and sys.argv[1]=='--frozen36','choose exact --frozen36'
 selected=list(frozen)
 assert hashlib.sha256((D/'remote_watchdog_candidate.py').read_bytes()).hexdigest()=='06be838b97c255bbb299a9fb641556455e8f34267c73c1da94d60a2db0ddfde5'
 token=os.environ.pop('RTX_CPU2_GATE_TOKEN','');assert token,'controller launch token required'
 gate=D/'BATCH_LAUNCH_GATE.json';until=time.monotonic()+60
 while not gate.exists():
  assert time.monotonic()<until,'startup gate deadline'
  time.sleep(.1)
 g=json.loads(gate.read_text())
 own_ticks=pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19]
 assert g=={'token':token,'pid':os.getpid(),'start_ticks':own_ticks},'startup gate identity mismatch'
 run=D/('run_'+str(time.time_ns()));run.mkdir()
 deadline=time.time()+72*3600
 import signal
 def batch_timeout(sig,frame):raise TimeoutError('72h batch deadline reserve reached')
 signal.signal(signal.SIGALRM,batch_timeout);signal.setitimer(signal.ITIMER_REAL,72*3600-60)
 single=open(C/'RTX4080_DISPATCHER.lock','a');fcntl.flock(single,fcntl.LOCK_EX|fcntl.LOCK_NB)
 ident={'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'start_unix':time.time(),'deadline_unix':deadline,'selected_ids':selected}
 save(run/'IDENTITY.json',ident)
 save(D/'NEW_BATCH_STARTED.json',dict(ident,run_directory=str(run),launch_token=token))
 def state(status,**kw):save(run/'STATE.json',dict(ident,status=status,unix=time.time(),**kw))
 while True:
  if (C/'STOP_AFTER_CURRENT').exists():state('STOP_AFTER_CURRENT');return
  if time.time()>=deadline-120:state('BATCH_DEADLINE');return
  queue=json.loads((C/'QUEUE.json').read_text());jobs=scope_jobs(queue,frozen,selected)
  if not jobs:state('FROZEN_SCOPE_EXHAUSTED');return
  job=jobs[0];locks=[];claimed=False
  try:
   for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=open(C/name,'a')
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:f.close();raise
    locks.append(f)
   # Under channel leases recheck live queue scope/status and stop immediately before claim.
   if (C/'STOP_AFTER_CURRENT').exists():state('STOP_AFTER_CURRENT');return
   fresh=scope_jobs(json.loads((C/'QUEUE.json').read_text()),frozen,[job['id']])
   if not fresh:continue
   job=fresh[0]
   assert job['type']=='CAPTURE_ORDINARY'
   job.update(status='RUNNING',started=time.time());update_job(job);claimed=True;state('RUNNING',job=job)
   with (run/(job['id']+'.stderr.log')).open('x') as err:
    rc,output=run_remote(job,frozen[job['id']],deadline,err)
   (run/(job['id']+'.stdout.log')).write_text(output)
   assert rc==0,('worker/guard exit',rc)
   sender=json.loads(output)
   if sender.get('status')=='SENDER_COMPLETE':
    # v3 publisher remains original; publication is synchronous under the same leases.
    commit=publish(sender);job.update(status='COMMITTED_VERIFIED',commit=commit)
   else:job.update(status=sender.get('status','HOLD'),result=sender)
  except BlockingIOError:
   state('WAIT_RTX_CHANNEL_LOCK');time.sleep(min(5,max(0,deadline-time.time()-120)));continue
  except Exception as e:
   if claimed:
    job.update(status='FAILED_RETAINED',error=repr(e),traceback=traceback.format_exc());save(run/(job['id']+'_FAILURE.json'),job)
    job['end_unix']=time.time();update_job(job)
   state('FAILED_STOP',job_id=job['id'],error=repr(e));return
  finally:
   for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  job['end_unix']=time.time();update_job(job);state(job['status'],job_id=job['id'])
  print(json.dumps({'job_id':job['id'],'status':job['status']}),flush=True)
  if job['status']!='COMMITTED_VERIFIED':state('NONCOMMIT_STOP',job_id=job['id']);return
if __name__=='__main__':main()
