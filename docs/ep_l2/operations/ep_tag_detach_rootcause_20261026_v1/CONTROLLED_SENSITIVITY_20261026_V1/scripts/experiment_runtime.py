#!/usr/bin/env python3
"""Finite native EP controls. Exact new requests, private run lease, short shared writer lock."""
import sys
sys.dont_write_bytecode=True
import copy, datetime, fcntl, hashlib, importlib.util, json, os, pathlib, resource, shutil, signal, socket, subprocess, time, uuid
P=pathlib.Path
ROOT=P('/root/data/ep_memory_path_sensitivity_20261026_v1')
BASE=P('/root/data/ep_l2_main_vector_r5_20261023_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
E1='EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1'
E2='EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1'
GIB=2**30;MIB=2**20
LED=N/'control/qualification_ledger';REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
def bind(case):
 global B,C
 need(case in [E1,E2],'unapproved exact case')
 C=case;B=ROOT/'cases'/case
def need(ok,why):
 if not ok:raise RuntimeError(why)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def enc(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):
 p=P(p)
 with p.open('xb') as f:f.write(enc(v));f.flush();os.fsync(f.fileno())
def replace(p,v):
 p=P(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');put(tmp,v);os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def writer():
 # DTC's NATIVE_QUALIFICATION.lock is its long-lived batch lease. Never acquire it.
 f=(REG.parent/'REGISTRY_UPDATE.lock').open('rb');fcntl.flock(f,fcntl.LOCK_EX);return f
def case_lease():
 f=(B/'control/CASE_RUN.lock').open('a+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);return f
def identity():
 sys.path.insert(0,str(N/'tools'));import native_v2
 return native_v2.identity()
def spec():return read(B/'control/FROZEN_SPEC.json')
def pins():
 s=spec();binding=read(B/'control/SPEC_AUTHORIZATION_BINDING.json')
 need(sha(B/'control/FROZEN_SPEC.json')==binding['spec_sha256'],'spec drift')
 need(sha(B/'control/USER_AUTHORIZATION.json')==binding['authorization_sha256'],'authorization drift')
 need(s['cohort']==C and s['application_budget']==1 and s['automatic_retry'] is False,'finite scope mismatch')
 for p,h in s['pinned_files'].items():need(sha(p)==h,'pinned file changed '+p)
 for p,h in s['env_hashes'].items():need(sha(p)==h,'env changed '+p)
 return s
def resources(runtime=False):
 import resource_accounting
 s=spec();last=None
 for unused in range(4):
  last=resource_accounting.snapshot(ROOT,C,s['reserved_write_bytes'],s['memory_cap_bytes'],runtime=runtime)
  if last['consistent_snapshot']:break
  time.sleep(.1)
 last['physical_disk_pass']=last['disk_pass'];last['physical_RAM_pass']=last['RAM_pass']
 return last
def current_assets():
 proof=read(ROOT/'control/FRESH_INPUT_ASSET_BINDING.json')
 need(proof['status']=='FRESH_GENUINE164_INPUT_CLOSED_REOPEN_FULL_SHA_PASS','fresh input proof missing')
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T',proof['native_mirror_mount_path']],text=True))['filesystems'][0]
 need(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','genuine164 mapping changed')
 need(P(proof['source_root']).resolve()==P(proof['native_mirror_mount_path']).resolve(),'input alias changed')
 for row in proof['members']:
  p=P(row['path']);t=p.stat()
  need([t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns]==row['identity'] and os.access(p,os.R_OK),'fresh input stat drift; bounded revalidation required')
 return {'EP_VECTORADD_S':proof}
def prepare():
 s=pins();host=identity()
 sys.path.insert(0,str(N/'tools'));import native_v2
 assets=current_assets()
 need(sha(s['binary_path'])==s['source_identity']['binary_sha256'],'binary identity')
 for i in range(4):need((B/'env'/('config-'+str(i)+'.config')).read_bytes()==(BASE/'env'/('config-'+str(i)+'.config')).read_bytes(),'baseline configuration drift')
 expected='-gpgpu_clock_domains 1132.0:1132.0:1132.0:935.0\n' if C==E1 else '-gpgpu_cache:dl1 S:4:128:128,L:T:m:L:L,A:512:8,32:0,32\n'
 need((B/'env/config-4.config').read_text()==expected,'extra or wrong option')
 need(s['host_cpu'] in os.sched_getaffinity(0),'CPU unavailable')
 r=resources();need(r['consistent_snapshot'] and r['physical_disk_pass'] and r['physical_RAM_pass'],'RESOURCE_HOLD:'+json.dumps({k:r.get(k) for k in ['free_bytes','required_free_bytes','disk_pass','RAM_pass','errors']}))
 return {'status':'PREPARED_NO_APPLICATION_START','cohort':C,'identity':host,'assets':assets,'resources':r,'spec_sha256':sha(B/'control/FROZEN_SPEC.json')}
def qualify():
 need(os.environ.get('EP_MEMORY_NATIVE_ENTRY')=='1','sole entry required')
 lease=case_lease();need(not (B/'control/NATIVE_HELP_INTENT.json').exists(),'help already consumed')
 p=prepare();s=spec();loader=N/'common-lib/ld-linux-x86-64.so.2'
 args=[str(loader),'--inhibit-cache','--library-path',str(N/'EP/env/lib'),s['binary_path'],'-h']
 put(B/'control/NATIVE_HELP_INTENT.json',{'utc':now(),'argv':args,'max_invocations':1,'full_application':False})
 log=B/'run/log/ELF_HELP.log'
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','TMPDIR':str(B/'run/tmp'),'XDG_CACHE_HOME':str(B/'run/cache')}
 with log.open('xb') as f:cp=subprocess.run(args,cwd=B/'run/tmp',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=20)
 text=log.read_text(errors='replace')
 need(cp.returncode in [0,1] and ('usage' in text.lower() or 'option' in text.lower()) and 'gpu_tot_sim_insn' not in text and 'kernel_name =' not in text,'native help invalid')
 q={'status':'NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','qualified_by':'EP-MAIN','cohort':C,'source_identity':s['source_identity'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'native_identity':p['identity'],'resources':p['resources'],'assets':p['assets'],'expected_effective_options':s['expected_effective_options'],'actual_native_loading':{'argv':args,'returncode':cp.returncode,'output_sha256':sha(log),'simulator_help_invocations':1,'full_trace_or_kernel_executed':False},'semantic_scope':'Same exact binary/input/protocol; one declared service or queue parameter; fresh native process/terminal required; no inherited app acceptance'}
 put(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',q);return q
def mutate(reg,epoch,tag):
 need(sha(REG)==epoch['native_registry_sha256'],'authority pair mismatch')
 oldreg=sha(REG);olde=sha(EPOCH);hist=REG.parent/'request_history'
 for p,h in [(REG,oldreg),(EPOCH,olde)]:
  target=hist/(p.stem+'.'+h+'.json')
  if not target.exists():target.write_bytes(p.read_bytes())
 replace(REG,reg)
 epoch=copy.deepcopy(epoch);epoch.update(native_registry_sha256=sha(REG),new_budget_remaining=reg['new_scientific_budget_remaining'],request_revision={'request_id':C,'operation':tag,'utc':now(),'prior_registry_sha256':oldreg,'prior_current_epoch_sha256':olde})
 replace(EPOCH,epoch)
 put(hist/(C+'.'+tag+'.'+uuid.uuid4().hex+'.json'),{'operation':tag,'prior_registry_sha256':oldreg,'new_registry_sha256':sha(REG),'new_epoch_sha256':sha(EPOCH),'authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json')})
def require_e2_enabled():
 if C!=E2:return None
 import l1_plan
 decision=read(ROOT/'control/E2_DECISION.json')
 e1done=read(LED/(E1+'.DONE.json'));out=P(e1done['output'])
 point=read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 need(e1done['launcher_wait_returncode']==0 and e1done['stop_reason'] is None and e1done['native_simulator_observed'],'E1 not naturally complete')
 need(point['status']=='EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED' and point['cohort']==E1 and point['hardware_drained'] is True,'E1 not accepted')
 need(point['raw_sha256']==e1done['raw_sha256']==sha(out/'raw.log')==decision['E1_raw_sha256'],'E1 raw binding')
 need(point['source_identity']==read(ROOT/'cases'/E1/'control/FROZEN_SPEC.json')['source_identity']==spec()['source_identity'],'E1/E2 source mismatch')
 need(point['native_spec_sha256']==sha(ROOT/'cases'/E1/'control/FROZEN_SPEC.json')==decision['E1_spec_sha256'],'E1 spec binding')
 need(decision['E1_accepted_point_sha256']==sha(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json'),'decision accepted point binding')
 import comparison
 need(sha(out/'SENSITIVITY_COMPARISON.json')==decision['E1_comparison_sha256'],'decision comparison binding')
 extracted=comparison.raw_extract(out/'raw.log')
 records=[r for r in extracted['l1_last_records'].values() if r.get('scope')=='application']
 need(len(records)==1,'exact E1 L1 application scope missing')
 metrics=records[0]
 recommendation=l1_plan.recommend_e2(True,metrics['accesses'],metrics['miss_queue_full'])
 need(decision['recommendation']==recommendation['recommendation']=='E2_INFORMATION_WORTHWHILE_PENDING_NATIVE_ADMISSION','E2 information gate not passed')
 return recommendation
def register():
 need(os.environ.get('EP_MEMORY_NATIVE_ENTRY')=='1','sole entry required')
 lease=case_lease();p=prepare();q=read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')
 need(q['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q['spec_sha256']==sha(B/'control/FROZEN_SPEC.json'),'qualification mismatch')
 require_e2_enabled()
 with writer() as lock:
  reg=read(REG);epoch=read(EPOCH)
  need(epoch['epoch']==2 and epoch['holder']==socket.gethostname() and sha(REG)==epoch['native_registry_sha256'],'native authority mismatch')
  need(C not in reg['registered_future_requests'],'already registered')
  prior=copy.deepcopy(reg['registered_future_requests'])
  row={'project':'EP_L2','owner':'EP-MAIN','state':'AUTHORIZED_UNUSED','budget':1,'consumed':0,'automatic_retry':False,'reserved_write_bytes':spec()['advertised_peer_reservation_bytes'],'actual_write_restore_envelope_bytes':spec()['reserved_write_bytes'],'shared_floor_compatibility_margin_bytes':spec()['shared_floor_compatibility_margin_bytes'],'spec_path':str(B/'control/FROZEN_SPEC.json'),'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'authorization_path':str(B/'control/USER_AUTHORIZATION.json'),'authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json'),'native_qualification_sha256':sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')}
  reg['registered_future_requests'][C]=row;reg['new_scientific_budget_remaining']+=1
  need(all(reg['registered_future_requests'][k]==v for k,v in prior.items()),'peer mutated')
  mutate(reg,epoch,'REGISTER')
 return {'status':'NEW_EXACT_EP_REQUEST_REGISTERED','request':row}
def info(pid):
 p=P('/proc')/str(pid);parts=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start_ticks':int(parts[19]),'mnt_namespace':os.readlink(p/'ns/mnt'),'exe':os.readlink(p/'exe'),'cmdline':(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),'maps':(p/'maps').read_text()}
def run():
 need(os.environ.get('EP_MEMORY_NATIVE_ENTRY')=='1','sole entry required')
 lease=case_lease();prepared=prepare();s=spec();require_e2_enabled()
 uid=str(uuid.uuid4());out=B/'run/results'/uid
 with writer() as lock:
  reg=read(REG);epoch=read(EPOCH);need(sha(REG)==epoch['native_registry_sha256'],'authority mismatch')
  row=reg['registered_future_requests'][C]
  need(row['state']=='AUTHORIZED_UNUSED' and row['consumed']==0 and row['budget']==1 and reg['new_scientific_budget_remaining']>0,'no exact unused budget')
  need(row['spec_sha256']==sha(B/'control/FROZEN_SPEC.json') and row['authorization_sha256']==sha(B/'control/USER_AUTHORIZATION.json') and row['native_qualification_sha256']==sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),'registered identities drift')
  need(not (LED/(C+'.INTENT.json')).exists(),'already consumed; no retry')
  out.mkdir()
  for p in (B/'env').iterdir():shutil.copy2(p,out/p.name)
  put(LED/(C+'.INTENT.json'),{'cohort':C,'uuid':uid,'utc':now(),'output':str(out),'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json'),'consumed_before_launcher_fork':1,'new_attempt_consumed':1,'automatic_retry':False})
  row.update(state='CONSUMED_RUNNING_OR_UNRESOLVED',consumed=1,uuid=uid,output=str(out));reg['new_scientific_budget_remaining']-=1;mutate(reg,epoch,'CONSUME')
 loader=str(N/'common-lib/ld-linux-x86-64.so.2')
 args=[loader,'--library-path',str(N/'tools/lib')+':'+str(N/'common-lib'),str(N/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(out/'actual_file_process_network.log'),'--',loader,'--inhibit-cache','--library-path',str(N/'EP/env/lib'),s['binary_path'],'-trace',s['trace_entry']]
 for i in range(5):args+=['-config',str(out/('config-'+str(i)+'.config'))]
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','TMPDIR':str(B/'run/tmp'),'XDG_CACHE_HOME':str(B/'run/cache')}
 def limits():
  os.setsid();os.sched_setaffinity(0,{s['host_cpu']});os.nice(10);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(s['memory_cap_bytes'],s['memory_cap_bytes']))
 start=time.monotonic();p=None;reason=None;rc=None;observed=None;peak=0;peakrss=0;last=-10;last_consistent=0
 try:
  with (out/'raw.log').open('xb') as raw,(out/'RESOURCE_SAMPLES.jsonl').open('xb') as samples:
   p=subprocess.Popen(args,cwd=out,env=env,stdout=raw,stderr=subprocess.STDOUT,preexec_fn=limits)
   put(out/'NATIVE_LAUNCH.json',{'utc':now(),'launcher_pid':p.pid,'argv':args,'environment':env,'identity':identity(),'prepared':prepared,'source_identity':s['source_identity'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'entry_sha256':sha(__file__),'old174_ssh_scientific_execution':False,'independent_EP_case_lease':True,'DTC_parent_lease_borrowed':False})
   while p.poll() is None:
    childfile=P('/proc')/str(p.pid)/'task'/str(p.pid)/'children'
    for child in childfile.read_text().split() if childfile.exists() else []:
     try:
      v=info(int(child))
      if s['binary_path'] in v['maps'] and observed is None:
       need(v['mnt_namespace']=='mnt:[4026535153]','wrong native namespace');observed=v;put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',v)
     except (FileNotFoundError,ProcessLookupError):pass
    size=sum(f.stat().st_size for f in out.rglob('*') if f.is_file());peak=max(peak,size)
    temp_bytes=sum(f.stat().st_size for folder in [B/'run/tmp',B/'run/cache'] for f in folder.rglob('*') if f.is_file())
    hot_bytes=size+temp_bytes
    if temp_bytes>s['temporary_cap_bytes']:reason='TEMP_DIRECTORY_CAP'
    if hot_bytes>s['result_cap_bytes']+s['temporary_cap_bytes']:reason='HOT_DIRECTORY_CAP'
    if time.monotonic()-start-last>=5:
     last=time.monotonic()-start;r=resources(runtime=True);rss=0
     for pid in [p.pid,*([observed['pid']] if observed else [])]:
      try:rss+=int(next(x.split()[1] for x in (P('/proc')/str(pid)/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
      except (FileNotFoundError,ProcessLookupError,StopIteration):pass
     peakrss=max(peakrss,rss);r.update(elapsed_seconds=last,observed_rss_bytes=rss,result_bytes=size);samples.write(enc(r).replace(b'\n',b' ')+b'\n');samples.flush()
     if r['consistent_snapshot']:
      last_consistent=last
      if not r['physical_disk_pass']:reason='RESOURCE_DISK_HOLD'
      if not r['physical_RAM_pass']:reason='RESOURCE_RAM_HOLD'
     elif last-last_consistent>30:reason='RESOURCE_SNAPSHOT_UNSTABLE_30S'
     if os.statvfs(B).f_bavail*os.statvfs(B).f_frsize < 7*GIB+s['reserved_write_bytes']:reason='HARD_DISK_FLOOR'
     if rss>s['memory_cap_bytes']:reason='PROCESS_RSS_CAP'
    if size>s['result_cap_bytes']:reason='RESULT_CAP'
    if time.monotonic()-start>s['wall_timeout_seconds']:reason='WALL_CAP'
    if (B/'control/ABORT').exists():reason='EXPLICIT_ABORT'
    if reason:os.killpg(p.pid,signal.SIGTERM);break
    time.sleep(.2)
   try:rc=p.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
   raw.flush();os.fsync(raw.fileno());samples.flush();os.fsync(samples.fileno())
 except BaseException as error:
  reason=reason or 'LAUNCH_OR_GUARD_EXCEPTION:'+type(error).__name__+':'+str(error)
 finally:
  if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
 receipt={'schema':'NATIVE_QUALIFICATION_EXECUTION_RECEIPT_V1','cohort':C,'uuid':uid,'output':str(out),'launcher_wait_returncode':rc,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'native_simulator_observed':observed is not None,'peak_observed_rss_bytes':peakrss,'peak_result_logical_bytes':peak,'new_attempt_consumed':1,'automatic_retry':False,'source_disposition':'SOURCE_KEEP','raw_sha256':sha(out/'raw.log') if (out/'raw.log').exists() else None,'scientific_acceptance':'PENDING_INDEPENDENT_NATIVE_EP_TERMINAL'}
 put(out/'NATIVE_EXIT.json',receipt);put(LED/(C+'.DONE.json'),receipt)
 with writer() as lock:
  reg=read(REG);epoch=read(EPOCH);reg['registered_future_requests'][C]['state']='NATURAL_COMPLETE_PENDING_ACCEPTANCE_ARCHIVE' if rc==0 and reason is None else 'STOP_UNACCEPTED_PENDING_ARCHIVE';mutate(reg,epoch,'CLOSE')
 return receipt
def status():
 reg=read(REG);row=reg['registered_future_requests'].get(C)
 return {'cohort':C,'registered':row,'resources':resources()}
def main(args):
 op=args[0]
 if op=='prepare':return prepare()
 if op=='qualify':return qualify()
 if op=='register':return register()
 if op=='run-native':return run()
 if op in ['inspect','status']:return status()
 if op=='accept':
  import acceptance
  return acceptance.acceptance(C)
 raise RuntimeError('unsupported exact operation')
bind(E1)
