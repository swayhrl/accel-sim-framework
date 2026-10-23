"""Finite174-new native qualification entry. Never SSH-executes a simulator.

Only two frozen migration cohorts are selectable. Missing exact approval, fresh
source/resource closure, pending prior cohort, or changed bytes fail before fork.
No daemon, retry, refund, deletion, or mutation of old scientific ledgers.
"""
import argparse,datetime,fcntl,hashlib,json,os,pathlib,resource,signal,socket,subprocess,sys,time,uuid
P=pathlib.Path
ROOT=P('/root/data/ep_l2_dtc_l1_native_v2')
COHORTS={'EP_NATIVE_MIGRATION_Q1':'EP','DTC_NATIVE_MIGRATION_Q1':'DTC','EP_NATIVE_MIGRATION_Q2':'EP'}
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
 rows=[]
 for p in sorted((ROOT/'control/qualification_ledger').glob('*.INTENT.json')):
  x=read(p);which=COHORTS.get(x['cohort'])
  if project and which!=project:continue
  done=p.with_name(p.name.replace('.INTENT.json','.DONE.json'));state=read(done) if done.exists() else None
  rows.append({'cohort':x['cohort'],'project':which,'uuid':x['uuid'],'charged':1,'state':'STOP_UNACCEPTED' if state and (state['stop_reason'] or state['launcher_wait_returncode']) else 'NATURAL_COMPLETE' if state else 'RUNNING_OR_UNRESOLVED','native_receipt':state,'output':x['output']})
 epoch=ROOT/'control/CURRENT_SCIENCE_EPOCH.json'
 return {'identity':identity(),'historical_Source_counters_frozen':{'EP':57,'DTC':2,'EP_T0':1792414193},'native_migration_charged_starts':len(rows),'native_migration_attempts':rows,'current_science_epoch':read(epoch) if epoch.exists() else None,'production_science':'QUALIFICATION_PHASE_NO_PRODUCTION_EPOCH' if not epoch.exists() else 'NATIVE_ONLY; EVERY_NEW_REQUEST_REQUIRES_EXACT_OWNER_SPEC_AND_EXPLICIT_UNUSED_BUDGET','old174_SSH_scientific_execution':'FORBIDDEN','model_processes_started_by_this_status_query':0}

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
 s=spec_for(cohort);prepared=prepare(cohort)
 auth=ROOT/'control'/('EP_NATIVE_MIGRATION_Q2_AUTHORIZATION.json' if cohort.endswith('Q2') else 'SCIENCE_AUTHORIZATION.json');require(auth.is_file(),'SCIENCE_QUALIFICATION_PENDING_APPROVAL; no simulator fork')
 a=read(auth);req=ROOT/'control'/('Q2_PRECISE_AMENDMENT_REQUEST.json' if cohort.endswith('Q2') else 'SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 require(a['approval_request_sha256']==sha(req) and a['explicit_user_approval'] is True and a['owner_bindings_ratified'] is True and a['target_resource_policy_ratified'] is True,'exact scientific authorization missing')
 require(a['budgets'].get(cohort)==1,'exact one-start budget missing')
 if cohort.startswith('DTC'):
  p=ROOT/'EP/control/SCIENCE_QUALIFICATION.json';require(p.exists() and read(p)['status']=='EP_SCIENCE_QUALIFIED','EP must qualify before DTC')
  require((ROOT/'control/DTC_NATIVE_GUARD_CONTROL_TESTS.json').exists() and read(ROOT/'control/DTC_NATIVE_GUARD_CONTROL_TESTS.json')['status']=='PASS','native exact BA guard/telemetry controls missing')
 budget_dir=ROOT/'control/qualification_ledger';budget_dir.mkdir(exist_ok=True)
 lock=(budget_dir/'NATIVE_QUALIFICATION.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 intent=budget_dir/(cohort+'.INTENT.json');require(not intent.exists(),'attempt already consumed or unresolved; never retry/refund')
 res=resources(s,fresh_source=True);require(res['physical_disk_pass'] and res['physical_RAM_pass'],'RESOURCE_HOLD')
 admission=None
 if s['project']=='DTC':
  from native_dtc_guard import native_admission
  admission=native_admission(ROOT/'DTC/run');require(admission['status']=='PASS','DTC original memory/paired/native-device admission HOLD')
  res=resources(s,fresh_source=True);require(res['physical_disk_pass'] and res['physical_RAM_pass'],'RESOURCE_HOLD_AFTER_DTC_PAIR')
 ident=str(uuid.uuid4());out=ROOT/s['project']/'run/results'/ident;out.mkdir()
 exclusive(intent,{'cohort':cohort,'uuid':ident,'utc':now(),'spec_sha256':sha(ROOT/'control'/(cohort+'_SPEC.json')),'authorization_sha256':sha(auth),'consumed_before_launcher_fork':1,'automatic_retry':False,'old_ledger_mutations':0,'output':str(out)})
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','LD_LIBRARY_PATH':str(ROOT/s['project']/'env/lib'),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','TMPDIR':str(ROOT/s['project']/'run/tmp'),'XDG_CACHE_HOME':str(ROOT/s['project']/'run/cache')}
 progress=(out/'progress.jsonl').open('xb');passed=();channel=None;sender=None;dtc_guard=None;began_ns=time.monotonic_ns()
 if s['project']=='DTC':
  channel,sender=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);channel.setblocking(False);sender.setblocking(False);channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
  for key in ['DTC_AG7_POLICY_B_PROGRESS','DTC_AG7_INPUT_SHA','DTC_AG7_ROI_SHA']:env[key]=s['original_environment'][key]
  env['DTC_AG7_GENERATION']=ident;env['DTC_AG7_PROGRESS_FD']=str(sender.fileno());passed=(sender.fileno(),)
 loader=str(ROOT/'common-lib/ld-linux-x86-64.so.2');argv=[loader,'--library-path',str(ROOT/'tools/lib')+':'+str(ROOT/'common-lib'),str(ROOT/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(out/'actual_file_process_network.log'),'--',loader,'--inhibit-cache','--library-path',str(ROOT/s['project']/'env/lib'),*s['native_simulator_argv']]
 def limits():
  os.setsid();os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(s['limits']['max_process_tree_rss_bytes'],s['limits']['max_process_tree_rss_bytes']))
 raw=(out/'raw.log').open('xb');samples=(out/'RESOURCE_SAMPLES.jsonl').open('xb');start=time.monotonic();p=None;reason=None;observations=[];peak=0;last_full=start-10;peak_rss=0
 try:
  p=subprocess.Popen(argv,cwd=out,env=env,stdout=raw,stderr=subprocess.STDOUT,pass_fds=passed,preexec_fn=limits)
  exclusive(out/'NATIVE_LAUNCH.json',{'utc':now(),'launcher_pid':p.pid,'argv':argv,'environment':env,'host':identity(),'prepared':prepared,'resources':res,'effective_result_cap_bytes':output_cap(s),'frozen_upper_result_cap_bytes':s['limits']['max_result_directory_bytes'],'native_DTC_original_rebound_admission':admission,'scientific_qualification_uuid':ident,'old174_SSH_invocation':False,'finite_native_launcher_sha256':sha(__file__)})
  while p.poll() is None:
   childfile=P('/proc')/str(p.pid)/'task'/str(p.pid)/'children'
   for child in childfile.read_text().split() if childfile.exists() else []:
    try:
     n=child_info(int(child))
     if str(ROOT/s['project']/'bin/accel-sim.out') in n['maps'] and not observations:
      require(n['mnt_namespace']=='mnt:[4026535153]','simulator namespace mismatch');observations.append(n);exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',n)
      if s['project']=='DTC':
       from native_dtc_guard import NativeDTCGuard
       dtc_guard=NativeDTCGuard(channel,{'proven_actual_root':True,'pid':n['pid'],'start_ticks':n['start_ticks'],'generation':ident,'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']},out,began_ns)
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
     native=child_info(observations[0]['pid']);same=native['start_ticks']==observations[0]['start_ticks'] and native['mnt_namespace']==s['execution_mnt_namespace'];mapped=str(ROOT/s['project']/'bin/accel-sim.out') in native['maps'] and all(line.rsplit(None,1)[-1].startswith(str(ROOT)+'/') for line in native['maps'].splitlines() if '/' in line)
     safety={'authority':sha(auth)==read(intent)['authorization_sha256'],'identity':same,'mapper':mapped,'output_limits':size<=output_cap(s),'output_device':out.stat().st_dev==ROOT.stat().st_dev,'expected_growth':r['physical_disk_pass'],'explicit_abort_clear':not (ROOT/'control/ABORT_NATIVE_QUALIFICATION').exists(),'ownership':read(intent)['uuid']==ident}
     # Shared host/device measurements are deliberately conservative; none of
     # these counters is labeled exclusively owned by this simulation.
     io_scope={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True,'basis':'Explicit user-ratified Target resource profile and original BA shared-scope IO warning policy; all non-IO safety decisions retained'}
     faults=int((P('/proc')/str(native['pid'])/'stat').read_text().rsplit(')',1)[1].split()[9]);decision=dtc_guard.sample(out,safety,io_scope,faults);samples.write((json.dumps({'DTC_exact_original_policy':decision})+'\n').encode());samples.flush()
     if decision['decision']['decision']=='STOP':reason='DTC_ORIGINAL_RESOURCE_POLICY:'+','.join(decision['decision']['stop_reasons'])
   if size>output_cap(s):reason='RESULT_CAP'
   if free<7*GIB:reason='NATIVE_DISK_FLOOR_PLUS_MONITOR'
   if time.monotonic()-start>s['limits']['timeout_seconds']:reason='EXACT_WALL_TIMEOUT'
   if reason:os.killpg(p.pid,signal.SIGTERM);break
   time.sleep(0.2)
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
  raw.flush();os.fsync(raw.fileno());raw.close();progress.flush();os.fsync(progress.fileno());progress.close();samples.flush();os.fsync(samples.fileno());samples.close()
  if channel is not None:channel.close();sender.close()
 receipt={'schema':'NATIVE_QUALIFICATION_EXECUTION_RECEIPT_V1','cohort':cohort,'uuid':ident,'native_simulator_observed':bool(observations),'launcher_wait_returncode':rc,'launcher_is_strace_parent_of_native_simulator':True,'actual_simulator_wait_and_file_evidence':'actual_file_process_network.log','stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'peak_result_logical_bytes':peak,'peak_observed_rss_bytes':peak_rss,'raw_sha256':sha(out/'raw.log'),'output':str(out),'scientific_acceptance':'PENDING_EXACT_INDEPENDENT_TERMINAL_AND_BASELINE_COMPARISON','source_disposition':'SOURCE_KEEP','old_EP_starts':57,'old_DTC_starts':2,'new_attempt_consumed':1,'automatic_retry':False}
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

if __name__=='__main__':
 try:print(json.dumps(main(),indent=2))
 except (RuntimeError,OSError,KeyError,ValueError,StopIteration) as e:print(json.dumps({'status':'HOLD','reason':str(e),'science_retry':False}),file=sys.stderr);sys.exit(2)
