"""Finite174-new native qualification entry. Never SSH-executes a simulator.

Only exact frozen and explicitly approved cohorts are selectable. Missing approval, fresh
source/resource closure, pending prior cohort, or changed bytes fail before fork.
No daemon, retry, refund, deletion, or mutation of old scientific ledgers.
"""
import argparse,datetime,fcntl,hashlib,json,os,pathlib,resource,signal,socket,subprocess,sys,time,uuid
P=pathlib.Path
ROOT=P('/root/data/dtc_main_v100_sweep_20261025_v1')
sys.path.insert(0,str(ROOT/'tools'))
COHORTS={f'E2-AEV100-{r["input_digest"][:16]}-{c}':'DTC' for r in json.loads((ROOT/'control/INTAKE_CANDIDATES.json').read_bytes())['inputs'] for c in ['DM','DH','CM','CH']}
GIB=1024**3;MIB=1024**2
sys.dont_write_bytecode=True

def require(ok,why):
 if not ok:raise RuntimeError(why)

def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(MIB),b''):h.update(b)
 return h.hexdigest()

def read(p):return json.loads(P(p).read_bytes())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def exclusive(p,obj):
 b=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode();p=P(p)
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def allocated(p):return sum(x.lstat().st_blocks*512 for x in [P(p),*P(p).rglob('*')] if not x.is_symlink())

def identity():
 require(os.uname().nodename=='huangrulin-sshfs-174','wrong execution hostname')
 require(os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','wrong mount namespace')
 require(P('/proc/sys/kernel/random/boot_id').read_text().strip()=='59e1e1a4-84b6-431f-ac2d-03e340207019','boot changed; readmission required')
 require(ROOT.stat().st_dev==2128,'native backing device changed')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(ROOT)],text=True))['filesystems'][0]
 require(fs['fstype']=='ext4','native ext4 required')
 return {'hostname':os.uname().nodename,'mnt_namespace':os.readlink('/proc/self/ns/mnt'),'pid_namespace':os.readlink('/proc/self/ns/pid'),'native_device':ROOT.stat().st_dev,'filesystem':fs}

def spec_for(cohort):
 require(cohort in COHORTS,'unapproved cohort')
 p=ROOT/'control'/(cohort+'_SPEC.json');s=read(p)
 request=read(ROOT/'control'/('Q2_PRECISE_AMENDMENT_REQUEST.json' if cohort.endswith('Q2') else 'SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'))
 row=next(x for x in request['specs'] if x['cohort']==cohort)
 require(sha(p)==row['sha256'] and s['project']==COHORTS[cohort],'frozen spec changed')
 return s

def output_cap(s):
 limit=s['limits']['max_result_directory_bytes'];p=ROOT/'control'/('OPERATIONAL_OUTPUT_CAP_'+s['cohort']+'.json')
 if p.exists():
  plan=read(p);cap=plan['effective_result_cap_bytes'];require(plan['cohort']==s['cohort'] and type(cap) is int and 0<cap<=limit,'operational cap may only tighten frozen upper limit');return cap
 return limit

def resources(s,fresh_source=False):
 v=os.statvfs(ROOT);free=v.f_bavail*v.f_frsize
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cur=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip()
 # All native result+restore caps, including completed ones, remain conservatively
 # reserved here. This intentionally overcounts completed bytes until closeout.
 result_restore=0
 serial=ROOT/'control/EP_NATIVE_MIGRATION_Q2_AUTHORIZATION.json'
 stage_only=s.get('resource_profile')=='SERIAL_STAGE_ONLY_EP64_DTC512_V1'
 if s['project']=='DTC' and serial.exists():
  binding=read(serial);stage_only=binding.get('explicit_user_approval') is True and binding.get('resource_profile')=='SERIAL_STAGE_ONLY_EP64_DTC512_V1' and binding.get('approval_request_sha256')==sha(ROOT/'control/Q2_PRECISE_AMENDMENT_REQUEST.json')
 reservations=[(s['project'],output_cap(s))] if stage_only else [('EP',384*MIB),('DTC',512*MIB)]
 for project,cap in reservations:
  for kind in ['results','recovery']:
   folder=ROOT/project/'run'/kind
   # Existing earlier attempts/restores are already reflected in df; subtracting
   # them from a NEW attempt's reservation would undercount. Stage-only reserves
   # the full new writing cap; the old conservative Q1 profile remains preserved.
   used=0 if stage_only else sum(x.stat().st_size for x in folder.rglob('*') if x.is_file()) if folder.exists() else 0
   result_restore+=max(0,cap-used)
 pending_engineering=max(0,256*MIB-allocated(ROOT/'EP/src')-allocated(ROOT/'DTC/src')-allocated(ROOT/'common-lib')-allocated(ROOT/'EP/bin')-allocated(ROOT/'DTC/bin'))
 source=read(ROOT/'control/SOURCE_PREFLIGHT.json') if (ROOT/'control/SOURCE_PREFLIGHT.json').exists() else None
 other=None if source is None else source['other_outstanding_write_reservations_bytes']
 out={'utc':now(),'native_free_bytes':free,'free_inodes':v.f_favail,'host_MemAvailable_bytes':mem,'cgroup_memory_current':cur,'cgroup_memory_max':maximum,'combined_result_and_restore_reservation_bytes':result_restore,'remaining_engineering_reservation_bytes':pending_engineering,'other_outstanding_write_reservations_bytes':other,'disk_floor_bytes':5*GIB,'monitor_reserve_bytes':2*GIB,'required_free_bytes':None if other is None else 7*GIB+result_restore+pending_engineering+other}
 out['physical_RAM_pass']=mem>=64*GIB and (maximum=='max' or int(maximum)-cur>=s['limits']['max_process_tree_rss_bytes']+512*MIB)
 out['physical_disk_pass']=other is not None and free>=out['required_free_bytes'] and v.f_favail>=100000
 if fresh_source:
  require(source is not None and time.time()-source['observed_unix']<=30,'fresh exact source resource/owner preflight missing')
  require(source['EP_actual_starts']==57 and source['DTC_actual_starts']==2,'old science count changed')
  require(source['no_active_scientific_dispatch_or_unresolved_intent'] is True,'source active/unresolved closure missing')
  require(source['current_owner_bindings_verified'] is True,'owner exact spec review missing')
 return out

def prepare(cohort):
 s=spec_for(cohort);host=identity();checks=[]
 for r in s['runtime_files']:
  p=ROOT/r['target'];require(p.is_file() and sha(p)==r['sha256'],'runtime SHA drift: '+str(p));checks.append(str(p))
 for kind,commit in [('framework',s['framework_commit']),('core',s['core_commit'])]:
  repo=ROOT/s['project']/'src'/kind
  require(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==commit,'source commit drift')
  require(not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip(),'tracked checkout dirty')
 rec=read(ROOT/'control'/s['trace_receipt_file']);mirror=P(rec['native_mirror_mount_path']);mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(mirror)],text=True))['filesystems'][0]
 require(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','genuine164 identity changed')
 require(P(rec['source_root']).resolve()==mirror.resolve(),'trace compatibility changed')
 for row in read(ROOT/'control/TRACE_CURRENT_STAT_BINDINGS.json')[s['project']]:
  p=P(row['path']);t=p.stat();require([t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns]==row['identity'],'frozen archived trace object identity drift')
  with p.open('rb') as f:require(bool(f.read(1)),'trace unreadable')
 return {'status':'ENGINEERING_PREPARE_PASS_SCIENCE_APPROVAL_SEPARATE','cohort':cohort,'identity':host,'runtime_files_SHA_checked':checks,'trace_mount':mount,'resources':resources(s),'scientific_starts':0}

def child_info(pid):
 p=P('/proc')/str(pid);st=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start_ticks':int(st[19]),'mnt_namespace':os.readlink(p/'ns/mnt'),'pid_namespace':os.readlink(p/'ns/pid'),'exe':os.readlink(p/'exe'),'cmdline':(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),'maps':(p/'maps').read_text()}

def current_status(project=None):
 rows=[];legacy=[]
 for p in sorted((ROOT/'control/qualification_ledger').glob('*.INTENT.json')):
  x=read(p);which=COHORTS.get(x['cohort'])
  if x['cohort']=='DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1':
   if project in [None,'DTC']:
    done=p.with_name(p.name.replace('.INTENT.json','.DONE.json'));legacy.append({'cohort':x['cohort'],'uuid':x['uuid'],'charged':1,'native_receipt':read(done) if done.exists() else None,'current_AD_qualification':False})
   continue
  if project and which!=project:continue
  done=p.with_name(p.name.replace('.INTENT.json','.DONE.json'));state=read(done) if done.exists() else None
  rows.append({'cohort':x['cohort'],'project':which,'uuid':x['uuid'],'charged':1,'state':'STOP_UNACCEPTED' if state and (state['stop_reason'] or state['launcher_wait_returncode']) else 'NATURAL_COMPLETE' if state else 'RUNNING_OR_UNRESOLVED','native_receipt':state,'output':x['output']})
 epoch=ROOT/'control/CURRENT_SCIENCE_EPOCH.json'
 qualifications={}
 for name in [project] if project else ['EP','DTC']:
  q=ROOT/name/'control/SCIENCE_QUALIFICATION.json';qualifications[name]=read(q) if q.exists() else {'status':'PENDING_INDEPENDENT_COMPLETE_NATIVE_QUALIFICATION'}
 return {'identity':identity(),'historical_Source_counters_frozen':{'EP':57,'DTC':2,'EP_T0':1792414193},'native_migration_charged_starts':len(rows),'native_migration_attempts':rows,'separate_legacy_replay_charged_starts':len(legacy),'separate_legacy_replays':legacy,'independent_scientific_qualifications':qualifications,'current_science_epoch':read(epoch) if epoch.exists() else None,'production_science':'QUALIFICATION_PHASE_NO_PRODUCTION_EPOCH' if not epoch.exists() else 'NATIVE_ONLY; EVERY_NEW_REQUEST_REQUIRES_EXACT_OWNER_SPEC_AND_EXPLICIT_UNUSED_BUDGET','old174_SSH_scientific_execution':'FORBIDDEN','model_processes_started_by_this_status_query':0}

def current_assets(names):
 out={};bindings=read(ROOT/'control/TRACE_CURRENT_STAT_BINDINGS.json')
 for name in names:
  project='EP' if name=='EP_VECTORADD_S' else 'DTC';rec=read(ROOT/'control'/(name+'_TRACE_RECEIPT.json'));checks=[]
  for x in bindings[project]:
   p=P(x['path']);t=p.stat();require([t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns]==x['identity'],'archived asset identity changed; bounded revalidation required');checks.append({'path':str(p),'bytes':t.st_size,'readable':os.access(p,os.R_OK)})
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',rec['native_mirror_mount_path']],text=True))['filesystems'][0];require(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','genuine164 mount changed')
  out[name]={'state':'AVAILABLE_FROZEN_TWO_MEMBER_INPUT_TRUE164','source_root':rec['source_root'],'native_compatibility_realpath':str(P(rec['source_root']).resolve()),'target_mount_root':rec['native_mirror_mount_path'],'current_metadata_checks':checks,'prior_closed_full_SHA_proof':str(ROOT/'control'/(name+'_TRACE_RECEIPT.json')),'fresh_large_body_rehash':False,'new_payload_bytes':0,'old_originals':'SOURCE_KEEP','scope':'Only these two named input member sets; other unimported cold assets remain REMOTE_SOURCE_KEEP_NOT_DIRECTLY_AVAILABLE'}
 return out

def run_native(cohort):
 epoch=ROOT/'control/CURRENT_SCIENCE_EPOCH.json'
 if epoch.exists():
  registry=ROOT/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';_,e=read_current_authority()
  require(e['state']=='NATIVE_SCIENCE_ACTIVE' and e['epoch']==2 and e['holder']==os.uname().nodename and authority_consistent(),'current native epoch/registry authority mismatch')
  # Migration approvals never become production credit. A future precisely
  # authorized request must first be registered in this one current ledger.
  require(read_current_authority()[0]['registered_future_requests'][REQUEST]['remaining']>0,'current request has no unused scientific credit')
 s=spec_for(cohort);prepared=prepare(cohort)
 auth=ROOT/'control'/('EP_NATIVE_MIGRATION_Q2_AUTHORIZATION.json' if cohort.endswith('Q2') else 'SCIENCE_AUTHORIZATION.json');require(auth.is_file(),'SCIENCE_QUALIFICATION_PENDING_APPROVAL; no simulator fork')
 a=read(auth);req=ROOT/'control'/('Q2_PRECISE_AMENDMENT_REQUEST.json' if cohort.endswith('Q2') else 'SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 require(a['approval_request_sha256']==sha(req) and a['explicit_user_approval'] is True and a['owner_bindings_ratified'] is True and a['target_resource_policy_ratified'] is True,'exact scientific authorization missing')
 require(a['budgets'].get(cohort)==1,'exact one-start budget missing')
 if cohort.startswith('DTC'):
  p=NATIVE/'EP/control/SCIENCE_QUALIFICATION.json';require(p.exists() and read(p)['status']=='EP_SCIENCE_QUALIFIED','EP must qualify before DTC')
  require((ROOT/'control/DTC_NATIVE_GUARD_CONTROL_TESTS.json').exists() and read(ROOT/'control/DTC_NATIVE_GUARD_CONTROL_TESTS.json')['status']=='PASS','native exact BA guard/telemetry controls missing')
 budget_dir=ROOT/'control/qualification_ledger';budget_dir.mkdir(exist_ok=True)
 assert_batch_lease()
 lock=(budget_dir/(cohort+'.ATTEMPT.lock')).open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 intent=budget_dir/(cohort+'.INTENT.json');require(not intent.exists(),'attempt already consumed or unresolved; never retry/refund')
 res=resources(s,fresh_source=True);require(res['physical_disk_pass'] and res['physical_RAM_pass'],'RESOURCE_HOLD')
 admission=None
 if s['project']=='DTC':
  from sweep_storage_guard import native_admission
  admission=native_admission(ROOT/'DTC/run');require(admission['status']=='PASS','DTC original memory/paired/native-device admission HOLD')
  res=resources(s,fresh_source=True);require(res['physical_disk_pass'] and res['physical_RAM_pass'],'RESOURCE_HOLD_AFTER_DTC_PAIR')
 ident=str(uuid.uuid4());out=ROOT/s['project']/'run/results'/ident;out.mkdir();(out/'tmp').mkdir();(out/'cache').mkdir()
 exclusive(intent,{'cohort':cohort,'uuid':ident,'utc':now(),'spec_sha256':sha(ROOT/'control'/(cohort+'_SPEC.json')),'authorization_sha256':sha(auth),'consumed_before_launcher_fork':1,'automatic_retry':False,'old_ledger_mutations':0,'output':str(out)})
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','LD_LIBRARY_PATH':str(ROOT/s['project']/'env/lib'),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','TMPDIR':str(out/'tmp'),'XDG_CACHE_HOME':str(out/'cache')}
 progress=compressed_stream(out/'progress.jsonl.gz');passed=();channel=None;sender=None;dtc_guard=None;began_ns=time.monotonic_ns()
 if s['project']=='DTC':
  channel,sender=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);channel.setblocking(False);sender.setblocking(False);channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
  for key in ['DTC_AG7_POLICY_B_PROGRESS','DTC_AG7_INPUT_SHA','DTC_AG7_ROI_SHA']:env[key]=s['original_environment'][key]
  env['DTC_AG7_GENERATION']=ident;env['DTC_AG7_PROGRESS_FD']=str(sender.fileno());passed=(sender.fileno(),)
 loader=str(ROOT/'common-lib/ld-linux-x86-64.so.2');argv=[loader,'--library-path',str(ROOT/'tools/lib')+':'+str(ROOT/'common-lib'),str(ROOT/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(out/'actual_file_process_network.log'),'--',loader,'--inhibit-cache','--library-path',str(ROOT/s['project']/'env/lib'),*s['native_simulator_argv']]
 def limits():
  os.setsid();os.sched_setaffinity(0,{s['host_cpu']});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(s['limits']['max_process_tree_rss_bytes'],s['limits']['max_process_tree_rss_bytes']))
 from sweep_read_cache import Adviser
 read_cache_adviser=Adviser()
 from sweep_io import RawCapture
 raw=RawCapture(out/'raw.log.gz');samples=compressed_stream(out/'RESOURCE_SAMPLES.jsonl.gz');start=time.monotonic();p=None;reason=None;observations=[];peak=0;last_full=start-10;peak_rss=0
 try:
  p=subprocess.Popen(argv,cwd=out,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,pass_fds=passed,preexec_fn=limits);raw.start(p.stdout)
  exclusive(out/'NATIVE_LAUNCH.json',{'utc':now(),'launcher_pid':p.pid,'argv':argv,'environment':env,'host':identity(),'prepared':prepared,'resources':res,'effective_result_cap_bytes':output_cap(s),'frozen_upper_result_cap_bytes':s['limits']['max_result_directory_bytes'],'native_DTC_original_rebound_admission':admission,'scientific_qualification_uuid':ident,'old174_SSH_invocation':False,'finite_native_launcher_sha256':sha(__file__)})
  while p.poll() is None:
   childfile=P('/proc')/str(p.pid)/'task'/str(p.pid)/'children'
   for child in childfile.read_text().split() if childfile.exists() else []:
    try:
     n=child_info(int(child))
     if str(ROOT/s['project']/'bin/accel-sim.out') in n['maps'] and not observations:
      require(n['mnt_namespace']=='mnt:[4026535153]','simulator namespace mismatch');observations.append(n);exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',n)
      if s['project']=='DTC':
       from sweep_storage_guard import NativeDTCGuard
       dtc_guard=NativeDTCGuard(channel,{'proven_actual_root':True,'pid':n['pid'],'start_ticks':n['start_ticks'],'generation':ident,'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']},out,began_ns);last_full=start-10
    except FileNotFoundError:pass
   size=sum(x.stat().st_size for x in out.rglob('*') if x.is_file());peak=max(peak,size)
   free=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
   if dtc_guard is not None:
    try:
     value=dtc_guard.drain()
     for row in value['records']:progress.write((json.dumps(row)+'\n').encode());progress.flush()
     why=dtc_guard.quick_stop()
     if why:reason=why
    except (ValueError,OSError) as error:reason='DTC_TELEMETRY:'+str(error)
   elif s['project']=='DTC' and time.monotonic_ns()-began_ns>30*10**9:reason='DTC_ROOT_OR_PRODUCER_NOT_BOUND_WITHIN30S'
   if time.monotonic()-last_full>=10:
    r=resources(s);last_full=time.monotonic();r['elapsed_seconds']=last_full-start
    rss=0
    for pid in [p.pid,*[x['pid'] for x in observations]]:
     status=P('/proc')/str(pid)/'status'
     try:rss+=int(next(x.split()[1] for x in status.read_text().splitlines() if x.startswith('VmRSS:')))*1024
     except (FileNotFoundError,StopIteration):pass
    peak_rss=max(peak_rss,rss);r['process_tree_observed_rss_bytes']=rss;samples.write((json.dumps(r)+'\n').encode());samples.flush()
    if not r['physical_RAM_pass']:reason='MEMORY_HEADROOM'
    if not r['physical_disk_pass']:reason='CONCURRENT_WRITE_RESERVATIONS'
    if rss>s['limits']['max_process_tree_rss_bytes']:reason='PROCESS_RSS_CAP'
    if dtc_guard is not None:
     read_cache_adviser.process(observations[0]['pid'],observations[0]['start_ticks'])
     native=child_info(observations[0]['pid']);same=native['start_ticks']==observations[0]['start_ticks'] and native['mnt_namespace']==s['execution_mnt_namespace'];mapped=str(ROOT/s['project']/'bin/accel-sim.out') in native['maps'] and all(line.rsplit(None,1)[-1] in {r['actual_realpath'] for r in s['runtime_files']} for line in native['maps'].splitlines() if '/' in line)
     safety={'authority':sha(auth)==read(intent)['authorization_sha256'],'identity':same,'mapper':mapped,'output_limits':size<=output_cap(s),'output_device':out.stat().st_dev==ROOT.stat().st_dev,'expected_growth':r['physical_disk_pass'],'explicit_abort_clear':not (ROOT/'control/ABORT').exists(),'ownership':read(intent)['uuid']==ident}
     # Shared host/device measurements are deliberately conservative; none of
     # these counters is labeled exclusively owned by this simulation.
     io_scope={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True,'basis':'Explicit user-ratified Target resource profile and original BA shared-scope IO warning policy; all non-IO safety decisions retained'}
     faults=int((P('/proc')/str(native['pid'])/'stat').read_text().rsplit(')',1)[1].split()[9]);decision=dtc_guard.sample(out,safety,io_scope,faults);samples.write((json.dumps({'DTC_exact_original_policy':decision})+'\n').encode());samples.flush()
     if decision['decision']['decision']=='STOP':reason='DTC_ORIGINAL_RESOURCE_POLICY:'+','.join(decision['decision']['stop_reasons'])
   if raw.error:reason='LOSSLESS_RAW_CAPTURE_IO_ERROR:'+raw.error
   if size>output_cap(s):reason='RESULT_CAP'
   if free<=5*GIB:reason='USER_LOCAL_OUTPUT_AT_OR_BELOW_5GiB'
   if time.monotonic()-start>s['limits']['timeout_seconds']:reason='EXACT_WALL_TIMEOUT'
   if reason:os.killpg(p.pid,signal.SIGTERM);break
   time.sleep(0.01)
  try:rc=p.wait(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
  if dtc_guard is not None:
   try:
    value=dtc_guard.drain()
    for row in value['records']:progress.write((json.dumps(row)+'\n').encode())
    if value['terminal']!='NATURAL' and reason is None:reason='DTC_NATURAL_TELEMETRY_CLOSURE_MISSING'
   except (ValueError,OSError) as error:
    if reason is None:reason='DTC_FINAL_TELEMETRY:'+str(error)
 finally:
  if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGKILL);p.wait()
  raw.flush();os.fsync(raw.fileno());raw.close();close_compressed(progress);close_compressed(samples)
  if channel is not None:channel.close();sender.close()
 receipt={'schema':'NATIVE_QUALIFICATION_EXECUTION_RECEIPT_V1','cohort':cohort,'uuid':ident,'native_simulator_observed':bool(observations),'launcher_wait_returncode':rc,'launcher_is_strace_parent_of_native_simulator':True,'actual_simulator_wait_and_file_evidence':'actual_file_process_network.log','stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'peak_result_logical_bytes':peak,'peak_observed_rss_bytes':peak_rss,'raw_sha256':sha(out/'raw.log.gz'),'raw_storage':'GZIP_LOSSLESS_1','raw_uncompressed_sha256':raw.hash.hexdigest(),'raw_uncompressed_bytes':raw.bytes,'output':str(out),'scientific_acceptance':'PENDING_EXACT_INDEPENDENT_TERMINAL_AND_BASELINE_COMPARISON','source_disposition':'SOURCE_KEEP','old_EP_starts':57,'old_DTC_starts':2,'new_attempt_consumed':1,'automatic_retry':False}
 exclusive(out/'NATIVE_EXIT.json',receipt);exclusive(budget_dir/(cohort+'.DONE.json'),receipt);return receipt

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('area',choices=['project','asset','experiment','result']);p.add_argument('operation');p.add_argument('item',nargs='?');p.add_argument('--destination');p.add_argument('--project',choices=['EP_L2','DTC_L1']);a=p.parse_args(argv);project={'EP_L2':'EP','DTC_L1':'DTC'}.get(a.project)
 if a.area=='experiment' and a.item=='DTC_LEGACY_FAST64_NN_NATIVE_SHORT_Q1':
  require(project in [None,'DTC'],'project/cohort mismatch');import legacy_nn_short
  if a.operation in ['inspect','prepare']:return {'status':'PREPARED_NO_SCIENCE_START','frozen_spec':legacy_nn_short.auth_and_prepare()[0]}
  if a.operation=='run-native':return legacy_nn_short.run()
  raise RuntimeError('unsupported exact legacy operation')
 if a.area=='project' and a.operation=='status':return current_status(project)
 if (a.area=='project' and a.operation=='assets') or (a.area=='asset' and a.operation=='ensure'):
  names=[a.item] if a.item else ['EP_VECTORADD_S'] if project=='EP' else ['DTC_AD_GEMM'] if project=='DTC' else ['EP_VECTORADD_S','DTC_AD_GEMM'];require(all(x in ['EP_VECTORADD_S','DTC_AD_GEMM'] for x in names),'asset not owner-approved for automatic ensure');return current_assets(names)
 if a.area=='experiment' and a.operation=='inspect':
  s=spec_for(a.item);require(project is None or s['project']==project,'project/cohort mismatch');return {'frozen_spec':s,'status':current_status(s['project'])}
 if a.area=='experiment' and a.operation in ['prepare','run-native'] and project:require(spec_for(a.item)['project']==project,'project/cohort mismatch')
 if a.area=='experiment' and a.operation=='prepare':return prepare(a.item)
 if a.area=='experiment' and a.operation=='run-native':return run_native(a.item)
 if a.area=='result' and a.operation in ['archive','restore']:
  import native_result
  return native_result.archive(a.item) if a.operation=='archive' else native_result.restore(a.item,a.destination)
 raise RuntimeError('unsupported operation; no remote scientific fallback')


# New exact science request adapter. Migration source is preserved unchanged;
# this derived module reuses its observed launcher/telemetry loop, with a new
# exact-source/runtime/asset contract and the SAME central native registry/lock.
NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2')
REQUEST='DTC_AE_V100_FULL_SWEEP_20261025_V1'
sys.path.insert(0,str(NATIVE/'tools'))
import native_v2 as original_native

def update_authority(mutator):
 registry_lock=(NATIVE/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b')
 fcntl.flock(registry_lock,fcntl.LOCK_EX)
 registry=NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
 epoch=NATIVE/'control/CURRENT_SCIENCE_EPOCH.json'
 r=read(registry);e=read(epoch)
 require(authority_consistent(),'native registry/epoch hash mismatch')
 history=NATIVE/'control/science_authority/request_history';history.mkdir(exist_ok=True)
 for p in [registry,epoch]:
  backup=history/(p.stem+'.'+sha(p)+'.json')
  if not backup.exists():backup.write_bytes(p.read_bytes())
 prior_registry_sha=sha(registry);prior_epoch_sha=sha(epoch)
 mutator(r)
 r['new_scientific_budget_remaining']=sum(x.get('remaining',max(0,x.get('budget',0)-(x.get('consumed',0) if isinstance(x.get('consumed',0),int) else len(x.get('consumed',{}))))) for x in r['registered_future_requests'].values())
 tmp=registry.with_name('.AEFAIR_REGISTRY.writing')
 with tmp.open('w') as f:f.write(json.dumps(r,sort_keys=True,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,registry)
 e['native_registry_sha256']=sha(registry);e['new_budget_remaining']=r['new_scientific_budget_remaining']
 e['request_revision']={'request_id':REQUEST,'operation':'AEFAIR_SHORT3_EXACT_UPDATE','utc':now(),'prior_registry_sha256':prior_registry_sha,'prior_current_epoch_sha256':prior_epoch_sha}
 tmp=epoch.with_name('.AEFAIR_EPOCH.writing')
 with tmp.open('w') as f:f.write(json.dumps(e,sort_keys=True,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,epoch)
 for folder in [registry.parent,epoch.parent]:
  fd=os.open(folder,os.O_RDONLY);os.fsync(fd);os.close(fd)

_original_exclusive=exclusive
def exclusive(p,obj):
 _original_exclusive(p,obj)
 if P(p).name.endswith('.INTENT.json') and obj.get('cohort') in COHORTS:
  def consume(r):
   q=r['registered_future_requests'][REQUEST]
   require(q['remaining']>0 and obj['cohort'] not in q['consumed'],'new exact cell already consumed')
   q['consumed'][obj['cohort']]={'uuid':obj['uuid'],'intent':str(P(p).resolve()),'intent_sha256':sha(p),'charged':1}
   q['remaining']-=1;q['state']='RUNNING'
  update_authority(consume)

def spec_for(cohort):
 require(cohort in COHORTS,'unknown AE fairness cell')
 p=ROOT/'control'/(cohort+'_SPEC.json');s=read(p)
 request=read(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 row=next(x for x in request['specs'] if x['cohort']==cohort)
 require(sha(p)==row['sha256'] and s['request']==REQUEST and s['project']=='DTC','new exact spec changed')
 return s

def resources(s,fresh_source=False):
 v=os.statvfs(ROOT);free=v.f_bavail*v.f_frsize
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cur=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip()
 # Shared physical pool: no double count of overlay/ext4. Fresh measured bytes
 # plus current registered peers and1GiB unregistered headroom, all12 tightened caps and
 # bounded256MiB outbox spool. Historical Source snapshot is never freshened.
 peer_reservations=[]
 for key,row in read(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'].items():
  if key!=REQUEST and row.get('state') not in ['COMPLETE','CLOSED','STOP_UNACCEPTED']:
   extra=row.get('reserved_write_bytes');require(type(extra) is int and extra>=0,'unknown active peer reservation')
   peer_reservations.append({'request':key,'reserved_write_bytes':extra})
 peer_bytes=sum(x['reserved_write_bytes'] for x in peer_reservations)
 required=5*GIB+peer_bytes+24*32*MIB+256*MIB
 return {'utc':now(),'native_free_bytes':free,'free_inodes':v.f_favail,'host_MemAvailable_bytes':mem,'cgroup_memory_current':cur,'cgroup_memory_max':maximum,'required_free_bytes':required,'other_outstanding_write_reservations_bytes':peer_bytes,'peer_reservations':peer_reservations,'reservation_basis':'User5GiB local safety floor includes monitor/unknown headroom; add exact bounded own writes and registered foreign writes only;164 and174-new are capacity tiers in one asset pool','physical_RAM_pass':mem>=64*GIB and (maximum=='max' or int(maximum)-cur>=32*GIB),'physical_disk_pass':free>required and v.f_favail>=100000,'fresh_local_resource_sample':True}

def prepare(cohort):
 s=spec_for(cohort);host=identity()
 registry=NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
 epoch=read(NATIVE/'control/CURRENT_SCIENCE_EPOCH.json')
 require(sha(registry)==epoch['native_registry_sha256'],'native registry hash mismatch')
 q=read(registry)['registered_future_requests'][REQUEST]
 require(q['spec_request_sha256']==sha(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'request not current-authority registered')
 require(q['controller_sha256']==sha(__file__),'unreviewed changed controller')
 require(q['state'] in ['ARMED','RUNNING'] and cohort not in q['consumed'],'cell consumed or cohort sealed')
 existing={p.name.removesuffix('.INTENT.json') for p in (ROOT/'control/qualification_ledger').glob('E2-AEF3-*.INTENT.json')}
 require(set(q['consumed'])==existing,'unresolved central intent/registry accounting mismatch')
 for row in s['runtime_files']:
  p=ROOT/row['target'];require(p.is_file() and str(p.resolve())==row['actual_realpath'] and sha(p)==row['sha256'],'runtime/config file drift:'+str(p))
 for kind,commit in [('framework',s['framework_commit']),('core',s['core_commit'])]:
  repo=ROOT/kind
  require(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==commit,'qualified source HEAD changed')
  require(not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip(),'qualified source worktree dirty')
 asset=check_input(s)
 for row in q['shared_tool_pins']:
  require(sha(row['path'])==row['sha256'],'shared frozen guard/entry dependency changed')
 r=resources(s,True);require(r['physical_RAM_pass'] and r['physical_disk_pass'],'new native physical resource HOLD')
 return {'status':'AEFAIR_EXACT_REGISTERED_PREPARE_PASS_NO_START','cohort':cohort,'identity':host,'resources':r,'asset':asset,'request':REQUEST,'source_and_runtime_checked':True,'scientific_starts':0}

def finish_cell(cohort):
 receipt=run_native(cohort)
 def done(r):
  q=r['registered_future_requests'][REQUEST]
  q['consumed'][cohort]['execution_receipt']=receipt
  if receipt['stop_reason'] or receipt['launcher_wait_returncode']:
   q['state']='STOP_UNACCEPTED';q['sealed_unused']=q['remaining'];q['remaining']=0
  else:q['state']='RUNNING' if q['remaining'] else 'ALL_STARTS_CLOSED_PENDING_SCIENCE_ACCEPTANCE'
 update_authority(done)
 return receipt

if __name__=='__main__':
 try:print(json.dumps(main(),indent=2))
 except (RuntimeError,OSError,KeyError,ValueError,StopIteration) as e:print(json.dumps({'status':'HOLD','reason':str(e),'science_retry':False}),file=sys.stderr);sys.exit(2)

def check_input(s):
 p=ROOT/'control/INPUT_IDENTITIES.json'
 require(sha(p)==read(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_identities_sha256'],'input manifest changed')
 d=read(p)[s['workload']];a=d['asset']
 require(P(a['source_root']).resolve()==P(a['mount_tree']).resolve(),'trace compatibility path drift')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',a['mount_tree']],text=True))['filesystems'][0]
 require(fs['source']=='admin-wcx@10.208.130.164:/home/shared' and fs['fstype']=='fuse.sshfs','genuine164 input mount changed')
 for r in d['members']:
  p=P(r['path']);st=p.stat();require([st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns]==r['identity'],'full-SHA-qualified input object changed')
  with p.open('rb') as f:require(bool(f.read(1)),'input unreadable')
 return {'status':'FULL_SHA_PREFLIGHT_BOUND_CURRENT_STAT_IDENTITY_PASS','asset_id':a['asset_id'],'members':len(d['members']),'input_manifest_sha256':sha(ROOT/'control/INPUT_IDENTITIES.json'),'full_SHA_repeated_during_prepare':False,'scientific_qualification':'PER_WORKLOAD_WHOLE_INPUT_STRICT_REQUIRED'}

# These definitions deliberately supersede only admission/authority plumbing in
# the pinned native launcher. The simulator, argv, exact BA runtime class and
# one-start journal remain unchanged.
import gzip
REQUEST='DTC_AE_V100_FULL_SWEEP_20261025_V1'
TERMINAL_PEER_STATES={'COMPLETE','CLOSED','STOP_UNACCEPTED','COMPAT_PARTIAL_COMPLETE'}
def compressed_stream(path):
 disk=P(path).open('xb');stream=gzip.GzipFile(fileobj=disk,mode='wb',mtime=0);stream._native_disk=disk;return stream
def close_compressed(stream):
 disk=stream._native_disk;stream.close();disk.flush();os.fsync(disk.fileno());disk.close()
def read_current_authority():
 with (NATIVE/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as held:
  fcntl.flock(held,fcntl.LOCK_SH)
  reg=NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';r=read(reg);e=read(NATIVE/'control/CURRENT_SCIENCE_EPOCH.json')
  require(sha(reg)==e['native_registry_sha256'],'registry/epoch hash mismatch')
  return r,e
def authority_consistent():read_current_authority();return True
def assert_batch_lease():
 lease=read(ROOT/'control/BATCH_LEASE.json');p=P('/proc')/str(lease['pid'])
 require(p.exists() and int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==lease['start_ticks'],'batch lease generation gone')
 require(lease['request']==REQUEST and 'sweep_controller.py' in (p/'cmdline').read_bytes().replace(b'\0',b' ').decode(),'batch lease owner mismatch')
 require(os.readlink(p/'fd'/str(lease['fd']))==str(NATIVE/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'),'global qualification lease FD mismatch')
 require('FLOCK' in (p/'fdinfo'/str(lease['fd'])).read_text(),'global qualification lease not held')
 pid=os.getpid();ancestors=[]
 for _ in range(20):
  if pid<=1:break
  ancestors.append(pid)
  if pid==lease['pid']:break
  pid=int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[1])
 require(lease['pid'] in ancestors,'model operation not descended from the one finite native batch controller')
 return lease
def spec_for(cohort):
 require(cohort in COHORTS,'cohort outside frozen complete-input matrix')
 p=ROOT/'control'/(cohort+'_SPEC.json');s=read(p)
 r,e=read_current_authority();q=r['registered_future_requests'][REQUEST]
 require(q['admitted_specs'].get(cohort)==sha(p) and s['request']==REQUEST and s['project']=='DTC','spec not exact-current-qualified and admitted')
 require(s['input_digest'] in read(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['input_digests'],'input outside finite request')
 return s
def check_input(s):
 p=ROOT/'control/input_bindings'/(s['input_digest']+'.json');require(sha(p)==s['input_binding_sha256'],'whole-input qualification binding drift')
 b=read(p);d=b['qualification'];require(d['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS' and not d['issues'],'unresolved input-domain HOLD')
 entry=P(d['trace_entry']);require(sha(entry)==b['asset']['commandlist_sha256'],'commandlist SHA drift')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(entry)],text=True))['filesystems'][0]
 require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 input mount mismatch')
 for row in d['rows']:
  p=P(row['path']);st=p.stat();require([st.st_size,st.st_mtime_ns]==row['full_SHA_current_size_mtime'],'post-fullSHA input size/mtime drift')
  with p.open('rb') as f:require(bool(f.read(1)),'unreadable full-SHA member')
 return {'status':'CURRENT_FULL_BODY_SHA_BOUND_GENUINE164_INPUT','input_digest':s['input_digest'],'kernels':len(d['rows']),'binding_sha256':sha(ROOT/'control/input_bindings'/(s['input_digest']+'.json')),'FUSE_inode':'Informational only; current whole contentSHA and immutable object member identities are the evidence, old inode validators untouched','native_values':'UNPROVEN'}
def resources(s,fresh_source=False):
 v=os.statvfs(ROOT);free=v.f_bavail*v.f_frsize
 mem=int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 cur=int(P('/sys/fs/cgroup/memory.current').read_text());maximum=P('/sys/fs/cgroup/memory.max').read_text().strip()
 r,e=read_current_authority();q=r['registered_future_requests'][REQUEST];peers=[]
 for key,row in r['registered_future_requests'].items():
  if key==REQUEST or row.get('state') in TERMINAL_PEER_STATES:continue
  extra=row.get('reserved_write_bytes');require(type(extra) is int and extra>=0,'unknown foreign write reservation');peers.append({'request':key,'reserved_write_bytes':extra})
 # Reserve remaining live result growth plus full future native restore. Completed
 # bytes are already in df; queued/unstarted inputs may wait and are not double counted.
 own=GIB;live=[];remaining_RAM=0
 for cell,row in q['consumed'].items():
  out=ROOT/'DTC/run/results'/row['uuid'];done=row.get('execution_receipt')
  if (ROOT/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists():continue
  size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) if out.exists() else 0
  if done:reserve=size+16*MIB
  else:
   active_spec=read(ROOT/'control'/(cell+'_SPEC.json'));cap=active_spec['limits']['max_result_directory_bytes'];reserve=max(0,2*cap-size)
   rss=0;pidfile=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if pidfile.exists():
    bound=read(pidfile);proc=P('/proc')/str(bound['pid'])
    try:
     if int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==bound['start_ticks']:rss=int(next(l.split()[1] for l in (proc/'status').read_text().splitlines() if l.startswith('VmRSS:')))*1024
    except (FileNotFoundError,StopIteration):pass
   remaining_RAM+=max(0,active_spec['limits']['max_process_tree_rss_bytes']-rss)
  own+=reserve;live.append({'cohort':cell,'remaining_write_and_restore_bytes':reserve})
 claims=read(ROOT/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'] if (ROOT/'control/POOL_DISPATCH_RESERVATIONS.json').exists() else {}
 for cell,claim in claims.items():
  if cell in q['consumed']:continue
  reserve=2*claim['result_cap_bytes'];own+=reserve;remaining_RAM+=claim['RAM_cap_bytes'];live.append({'cohort':cell,'claimed_before_INTENT_write_and_restore_bytes':reserve})
 if fresh_source and s['cohort'] not in q['consumed'] and s['cohort'] not in claims:
  remaining_RAM+=s['limits']['max_process_tree_rss_bytes']
  reserve=2*s['limits']['max_result_directory_bytes'];own+=reserve;live.append({'cohort':s['cohort'],'new_candidate_reservation_bytes':reserve})
 peer=sum(x['reserved_write_bytes'] for x in peers);required=5*GIB+own+peer
 return {'utc':now(),'native_free_bytes':free,'free_inodes':v.f_favail,'host_MemAvailable_bytes':mem,'cgroup_memory_current':cur,'cgroup_memory_max':maximum,'required_free_bytes':required,'local_safety_floor_bytes':5*GIB,'bounded_own_remaining_write_and_restore_bytes':own,'own_reservations':live,'peer_reservations':peers,'other_outstanding_write_reservations_bytes':peer,'reserved_additional_live_and_candidate_RAM_bytes':remaining_RAM,'physical_RAM_pass':mem>=64*GIB+remaining_RAM and (maximum=='max' or int(maximum)-cur>=48*GIB+remaining_RAM),'physical_disk_pass':free>required and v.f_favail>=100000 and own<=q['reserved_write_bytes'],'fresh_local_resource_sample':True,'storage_basis':'5GiB fast-tier margin plus known pending writes only;genuine164 bulk inputs/cold assets not duplicated;each new job admitted separately'}
def prepare(cohort):
 s=spec_for(cohort);host=identity();r,e=read_current_authority();q=r['registered_future_requests'][REQUEST]
 require(q['spec_request_sha256']==sha(ROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and q['controller_sha256']==sha(__file__),'request or qualified launcher drift')
 require(q['state'] in ['ARMED','RUNNING'] and cohort not in q['consumed'] and cohort not in q['sealed'],'consumed/sealed cell cannot run')
 require(accounting_matches(),'central intent accounting mismatch')
 for row in s['runtime_files']:
  p=ROOT/row['target'];require(str(p.resolve())==row['actual_realpath'] and sha(p)==row['sha256'],'runtime/config file drift')
 for kind,commit in [('core',s['core_commit']),('framework',s['framework_commit'])]:
  require(subprocess.check_output(['git','-C',str(ROOT/kind),'rev-parse','HEAD'],text=True).strip()==commit,'source HEAD drift')
  require(not subprocess.check_output(['git','-C',str(ROOT/kind),'status','--porcelain'],text=True).strip(),'source worktree dirty')
 for row in q['shared_tool_pins']:require(sha(row['path'])==row['sha256'],'pinned guard/parser dependency drift')
 asset=check_input(s);res=resources(s,True);require(res['physical_RAM_pass'] and res['physical_disk_pass'],'RESOURCE_HOLD_NO_START')
 return {'status':'SWEEP_EXACT_REGISTERED_PREPARE_PASS_NO_START','cohort':cohort,'identity':host,'resources':res,'asset':asset,'request':REQUEST,'scientific_starts':0}
def exclusive(p,obj):
 if P(p).name.endswith('.INTENT.json') and obj.get('cohort') in COHORTS:
  lease=assert_batch_lease();require(obj['cohort'] in read(ROOT/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'],'cohort has no serialized pre-fork resource reservation');obj=dict(obj,batch_lease_pid=lease['pid'],batch_lease_start_ticks=lease['start_ticks'])
  def consume(r):
   q=r['registered_future_requests'][REQUEST];cohort=obj['cohort']
   require(q['remaining']>0 and cohort not in q['consumed'] and cohort not in q['sealed'],'cell not unused')
   _original_exclusive(p,obj)
   q['consumed'][cohort]={'uuid':obj['uuid'],'intent':str(P(p).resolve()),'intent_sha256':sha(p),'charged':1};q['remaining']-=1;q['state']='RUNNING'
  update_authority(consume)
 else:_original_exclusive(p,obj)
def finish_cell(cohort):
 receipt=run_native(cohort)
 def closed(r):
  q=r['registered_future_requests'][REQUEST];q['consumed'][cohort]['execution_receipt']=receipt
  q['state']='RUNNING' # A failed independent cell never refunds credit or erases peers.
 update_authority(closed);return receipt

def accounting_matches():
 with (NATIVE/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as held:
  fcntl.flock(held,fcntl.LOCK_SH)
  q=read(NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQUEST]
  return set(q['consumed'])=={p.name.removesuffix('.INTENT.json') for p in (ROOT/'control/qualification_ledger').glob('E2-AEV100-*.INTENT.json')}
