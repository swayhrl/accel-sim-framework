"""One explicitly authorized complete historical NN replay auxiliary lease.

Shares the existing native entry/qualification ledger. No scheduler/service,
old-Source execution, automatic retry, AD qualification substitution or deletion.
The existing long guard reads this short lease's published write reservation.
"""
import pathlib,json,os,hashlib,time,fcntl,subprocess,signal,resource,uuid,sys,re
P=pathlib.Path;ROOT=P('/root/data/ep_l2_dtc_l1_native_v2');COHORT='DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1';MIB=1024**2;GIB=1024**3
sys.dont_write_bytecode=True
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(x,why):
 if not x:raise RuntimeError(why)
def exclusive(p,x):
 raw=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
 with P(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def auth_and_prepare():
 c=ROOT/'control';request=c/'SHORT_NN_PARALLEL_APPROVAL_REQUEST.json';s=read(c/'SHORT_NN_PARALLEL_EXACT_SPEC.json');q=read(request);a=read(c/'SHORT_NN_PARALLEL_AUTHORIZATION.json')
 need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]' and ROOT.stat().st_dev==2128,'Target identity')
 need(sha(c/'SHORT_NN_PARALLEL_EXACT_SPEC.json')==q['spec_sha256'] and a['approval_request_sha256']==sha(request) and a['explicit_user_approval'] and a['max_starts']==1 and a['one_bounded_parallel_exception'],'precise one-start/concurrency permission missing')
 r=ROOT/'DTC_LEGACY';receipt=read(c/'LEGACY_NN_PREPARATION_RECEIPT.json')
 need(receipt['runtime_and_trace_SHA_verified'] and receipt['source_frozen_case']==COHORT,'prepared source identity missing')
 for row in receipt['runtime_files']:need(sha(row['native_target'])==row['sha256'],'legacy runtime SHA drift')
 binary=r/'bin/accel-sim.out';need(sha(binary)==s['binary']['sha256'],'wrong old accepted binary')
 trace=read(c/'LEGACY_NN_TRUE164_INPUT_RECEIPT.json');need(trace['status']=='TRACE_MEMBERS_ARCHIVE_AND_CLOSED_REOPEN_SHA_VERIFIED','genuine164 input proof missing')
 import native_v2
 native_v2.identity();baseline=read(c/'SOURCE_PREFLIGHT.json');other=baseline['other_outstanding_write_reservations_bytes'];free=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
 need(free-other-256*MIB-16*MIB>=7*GIB,'combined floor/reservations HOLD');need(2 in os.sched_getaffinity(0),'approved short CPU unavailable')
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;maximum=P('/sys/fs/cgroup/memory.max').read_text().strip();current=int(P('/sys/fs/cgroup/memory.current').read_text());need(mem>=64*GIB and (maximum=='max' or int(maximum)-current>=2*GIB+512*MIB),'RAM HOLD')
 ld=ROOT/'common-lib/ld-linux-x86-64.so.2';libs=r/'env/lib';p=subprocess.run([str(ld),'--library-path',str(libs),'--list',str(binary)],capture_output=True,text=True);need(p.returncode==0 and 'not found' not in p.stdout,'isolated legacy ELF closure missing')
 return s,a,trace
def run():
 s,a,trace=auth_and_prepare();c=ROOT/'control';ledger=c/'qualification_ledger';lock=(ledger/'NATIVE_SHORT_NN_AUXILIARY.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);intent=ledger/(COHORT+'.INTENT.json');need(not intent.exists(),'short budget already consumed/unresolved; no retry')
 parent=read(ledger/'DTC_NATIVE_MIGRATION_Q1.INTENT.json');need(parent['uuid']=='35c3cc78-b7c0-4572-9ec5-91c0f1227500','unexpected primary attempt');primary=read(P(parent['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(primary['pid']);need(proc.exists() and int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==primary['start_ticks'],'primary not currently the approved long instance')
 r=ROOT/'DTC_LEGACY';uid=str(uuid.uuid4());out=r/'run/results'/uid;out.mkdir(parents=True)
 # Publish extra actual concurrent output+restore reservation atomically. The
 # Source registry and running primary's argv/environment/budget are untouched.
 pf=c/'SOURCE_PREFLIGHT.json';old=pf.read_bytes();baseline=json.loads(old);new=dict(baseline);new['other_outstanding_write_reservations_bytes']=baseline['other_outstanding_write_reservations_bytes']+16*MIB;new['temporary_native_auxiliary_reservation']={'cohort':COHORT,'uuid':uid,'bytes':16*MIB};newraw=(json.dumps(new,indent=2)+'\n').encode();temporary=c/('.SOURCE_PREFLIGHT_NN_'+uid);temporary.write_bytes(newraw);os.replace(temporary,pf)
 exclusive(intent,{'cohort':COHORT,'project':'DTC_LEGACY','uuid':uid,'output':str(out),'consumed_before_scientific_launcher_fork':1,'approval_request_sha256':a['approval_request_sha256'],'spec_sha256':sha(c/'SHORT_NN_PARALLEL_EXACT_SPEC.json'),'parent_long_uuid':parent['uuid'],'temporary_concurrency':2,'automatic_retry':False,'refund':False})
 import native_v2
 ld=str(ROOT/'common-lib/ld-linux-x86-64.so.2');libs=str(r/'env/lib');binary=r/'bin/accel-sim.out';argv=[ld,'--library-path',str(ROOT/'tools/lib')+':'+str(ROOT/'common-lib'),str(ROOT/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(out/'actual_file_process_network.log'),'--',ld,'--inhibit-cache','--library-path',libs,str(binary),'-trace',trace['native_mirror_mount_path']+'/kernelslist.g','-config',str(r/'env/FAST64_OO.config'),'-config',str(r/'env/trace.config')];env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CUDA_VISIBLE_DEVICES':'','LD_LIBRARY_PATH':libs,'TMPDIR':str(r/'run/tmp'),'XDG_CACHE_HOME':str(r/'run/cache')}
 def limits():os.setsid();os.sched_setaffinity(0,{2});resource.setrlimit(resource.RLIMIT_AS,(2*GIB,2*GIB));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 p=None;reason=None;proof=None;start=time.monotonic();raw=(out/'raw.log').open('xb');rc=None;peak_rss=0;resource_samples=[]
 try:
  p=subprocess.Popen(argv,cwd=out,env=env,stdout=raw,stderr=subprocess.STDOUT,preexec_fn=limits);exclusive(out/'NATIVE_LAUNCH.json',{'cohort':COHORT,'uuid':uid,'launcher_pid':p.pid,'argv':argv,'environment':env,'source_case':s,'native_loader_is_proc_exe':'mapped simulator ELF independently proved','single_existing_native_control_entry':True,'shared_native_ledger':str(ledger),'primary_long_unchanged':primary['pid'],'short_CPU':2,'launcher_sha256':sha(__file__)})
  while p.poll() is None:
   childfile=P('/proc')/str(p.pid)/'task'/str(p.pid)/'children'
   for child in childfile.read_text().split() if childfile.exists() else []:
    try:
     n=native_v2.child_info(int(child))
     if str(binary) in n['maps'] and proof is None:proof=n;exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',n)
    except FileNotFoundError:pass
   size=sum(x.stat().st_size for x in out.rglob('*') if x.is_file());free=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize;rss=0
   for pid in [p.pid,*([proof['pid']] if proof else [])]:
    try:rss+=int(next(x.split()[1] for x in (P('/proc')/str(pid)/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
    except (FileNotFoundError,StopIteration):pass
   peak_rss=max(peak_rss,rss);mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;current=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip();other=read(pf)['other_outstanding_write_reservations_bytes'];disk_pass=free-other-256*MIB>=7*GIB;ram_pass=mem>=64*GIB and (maximum=='max' or int(maximum)-current>=512*MIB)
   if not resource_samples or time.monotonic()-resource_samples[-1]['monotonic']>=1:resource_samples.append({'monotonic':time.monotonic(),'SSD_free':free,'other_reservations':other,'main_result_restore_reserved':256*MIB,'disk_pass':disk_pass,'MemAvailable':mem,'RAM_pass':ram_pass,'process_tree_RSS':rss})
   if not disk_pass:reason='COMBINED_DISK_RESERVATIONS'
   if not ram_pass:reason='RAM_HEADROOM'
   if rss>2*GIB:reason='SHORT_PROCESS_TREE_RSS'
   if size>8*MIB:reason='SHORT_OUTPUT_CAP'
   if free<7*GIB:reason='SHARED_FLOOR_PLUS_MONITOR'
   if time.monotonic()-start>120:reason='SHORT120S_WALL'
   if reason:os.killpg(p.pid,signal.SIGTERM);break
   time.sleep(0.05)
  try:rc=p.wait(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
 finally:
  if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGKILL);p.wait()
  raw.flush();os.fsync(raw.fileno());raw.close()
  # Remove only this transient reservation, preserving any unrelated concurrent
  # accounting change. Old Source data/ledgers are never touched.
  now=read(pf)
  if now.get('temporary_native_auxiliary_reservation',{}).get('uuid')==uid:
   now['other_outstanding_write_reservations_bytes']-=16*MIB;now.pop('temporary_native_auxiliary_reservation');tmp=c/('.SOURCE_PREFLIGHT_NN_DONE_'+uid);tmp.write_text(json.dumps(now,indent=2)+'\n');os.replace(tmp,pf)
 exclusive(out/'RESOURCE_SAMPLES.json',resource_samples)
 receipt={'schema':'NATIVE_LEGACY_SHORT_COMPLETE_EXECUTION_RECEIPT_V1','cohort':COHORT,'uuid':uid,'native_simulator_observed':proof is not None,'native_PID':proof['pid'] if proof else None,'native_mnt_namespace':proof['mnt_namespace'] if proof else None,'launcher_wait_returncode':rc,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'peak_observed_process_tree_RSS_bytes':peak_rss,'raw_sha256':sha(out/'raw.log'),'output':str(out),'new_attempt_consumed':1,'automatic_retry':False,'scientific_acceptance':'PENDING_EXACT_LEGACY_COMPLETE_TERMINAL_COMPARE','source_disposition':'SOURCE_KEEP','primary_long_uuid':parent['uuid'],'old_Source_EP57_DTC2_unchanged':True};exclusive(out/'NATIVE_EXIT.json',receipt);exclusive(ledger/(COHORT+'.DONE.json'),receipt);return receipt
if __name__=='__main__':
 try:print(json.dumps(run() if sys.argv[1:]==['--run'] else {'status':'NO_SCIENCE_PREPARE_ONLY','spec':auth_and_prepare()[0]},indent=2))
 except (RuntimeError,OSError,ValueError,KeyError) as e:print(json.dumps({'status':'HOLD_NO_RETRY','reason':str(e)}),file=sys.stderr);sys.exit(2)
