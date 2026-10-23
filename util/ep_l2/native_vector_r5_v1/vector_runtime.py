#!/usr/bin/env python3
"""One user-authorized native epoch2 Vector r5 cohort. No legacy controller."""
import argparse,copy,datetime,fcntl,hashlib,importlib.util,json,os,pathlib,resource,shutil,signal,subprocess,sys,time,uuid
P=pathlib.Path;B=P('/root/data/ep_l2_main_vector_r5_20261023_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
C='EP_NATIVE_TAGPRESSURE_VECTOR_HOLDOUT_V1';GIB=2**30;MIB=2**20
LED=N/'control/qualification_ledger';REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
def need(v,s):
 if not v:raise RuntimeError(s)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def enc(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def put(p,x):
 p=P(p);data=enc(x)
 with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def replace(p,x):
 p=P(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');put(tmp,x);os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def lock():
 f=(LED/'NATIVE_QUALIFICATION.lock').open('rb');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);return f
def identity():
 sys.path.insert(0,str(N/'tools'));import native_v2
 return native_v2.identity()
def spec():return read(B/'control/FROZEN_SPEC.json')
def pins():
 s=spec();need(sha(B/'control/FROZEN_SPEC.json')==read(B/'control/SPEC_AUTHORIZATION_BINDING.json')['spec_sha256'],'spec changed')
 need(s['cohort']==C and s['application_budget']==1 and s['automatic_retry'] is False,'wrong finite scope')
 for path,h in s['pinned_files'].items():need(sha(path)==h,'pinned file changed '+path)
 return s
def resources():
 identity();s=spec();reg=read(REG)
 other=GIB
 observed=[]
 for key,r in reg.get('registered_future_requests',{}).items():
  if key==C:continue
  if r.get('state') not in ['COMPLETE','CLOSED','STOP_UNACCEPTED']:
   extra=r.get('reserved_write_bytes')
   need(type(extra) is int and extra>=0,'foreign request reservation unknown')
   other+=extra;observed.append({'request':key,'bytes':extra})
 v=os.statvfs(B);free=v.f_bavail*v.f_frsize
 mem=int(next(t.split()[1] for t in P('/proc/meminfo').read_text().splitlines() if t.startswith('MemAvailable:')))*1024
 cur=int(P('/sys/fs/cgroup/memory.current').read_text());mx=P('/sys/fs/cgroup/memory.max').read_text().strip()
 reserved=s['reserved_write_bytes'];required=7*GIB+other+reserved
 return {'utc':now(),'free_bytes':free,'required_free_bytes':required,'own_reserved_write_bytes':reserved,'other_registered_reservations':observed,'additional_unregistered_project_headroom_bytes':GIB,'host_MemAvailable_bytes':mem,'cgroup_current_bytes':cur,'cgroup_max':mx,'physical_disk_pass':free>=required and v.f_favail>=100000,'physical_RAM_pass':mem>=64*GIB and (mx=='max' or int(mx)-cur>=s['memory_cap_bytes']+512*MIB),'Share_new_bytes':0}
def prepare():
 s=pins();host=identity()
 sys.path.insert(0,str(N/'tools'));import native_v2
 assets=native_v2.current_assets(['EP_VECTORADD_S'])
 need(s['source_identity']['binary_sha256']==sha(B/'bin/accel-sim.out'),'wrong r5 binary')
 need(sha(N/'tools/native_v2.py')==s['frozen_old_entry_sha256'],'old native code changed')
 need(all((LED/p.name.replace('.INTENT.json','.DONE.json')).exists() for p in LED.glob('*.INTENT.json')),'prior native intent unresolved')
 r=resources();need(r['physical_disk_pass'] and r['physical_RAM_pass'],'RESOURCE_HOLD')
 return {'status':'PREPARED_NO_APPLICATION_START','identity':host,'assets':assets,'resources':r,'spec_sha256':sha(B/'control/FROZEN_SPEC.json')}
def qualify():
 need(not (B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json').exists(),'qualification already performed')
 need(not (B/'control/NATIVE_HELP_INTENT.json').exists(),'native help already consumed')
 p=prepare();s=spec();loader=N/'common-lib/ld-linux-x86-64.so.2'
 argv=[str(loader),'--inhibit-cache','--library-path',str(N/'EP/env/lib'),str(B/'bin/accel-sim.out'),'-h']
 log=B/'run/log/ELF_HELP.log'
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','TMPDIR':str(B/'run/tmp'),'XDG_CACHE_HOME':str(B/'run/cache')}
 put(B/'control/NATIVE_HELP_INTENT.json',{'utc':now(),'argv':argv,'maximum_invocations':1,'full_application':False})
 with log.open('xb') as stream:
  cp=subprocess.run(argv,cwd=B/'run/tmp',env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=20)
 text=log.read_text(errors='replace');need('gpu_tot_sim_insn' not in text and 'kernel_name =' not in text,'help unexpectedly simulated')
 need(cp.returncode in [0,1] and ('option' in text.lower() or 'usage' in text.lower()),'native ELF help qualification failed')
 q={'status':'NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','qualified_by':'EP-MAIN','cohort':C,'source_identity':s['source_identity'],'native_identity':p['identity'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'historical_semantic_evidence':{'qualification':sha(B/'sources/historical/vector_qualification.json'),'native_release':sha(B/'sources/historical/native_release.json'),'source_review':sha(B/'sources/historical/source_review.json'),'reuse_scope':'Unchanged exact binary/input/profile bytes; historical source semantic gates only, no inherited native process/application acceptance'},'actual_native_loading':{'argv':argv,'returncode':cp.returncode,'output_sha256':sha(log),'full_trace_or_kernel_executed':False,'simulator_help_invocations':1},'assets':p['assets'],'resources':p['resources'],'new_full_applications':0}
 put(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',q);return q
def registry_change(reg,e,tag):
 oldreg=sha(REG);olde=sha(EPOCH);folder=N/'control/science_authority'/'request_history';folder.mkdir(exist_ok=True)
 for p,h in [(REG,oldreg),(EPOCH,olde)]:
  target=folder/(p.stem+'.'+h+'.json')
  if not target.exists():target.write_bytes(p.read_bytes())
 replace(REG,reg);e=copy.deepcopy(e);e.update(native_registry_sha256=sha(REG),new_budget_remaining=reg['new_scientific_budget_remaining'],request_revision={'request_id':C,'operation':tag,'utc':now(),'prior_registry_sha256':oldreg,'prior_current_epoch_sha256':olde})
 replace(EPOCH,e)
 put(folder/(C+'.'+tag+'.'+uuid.uuid4().hex+'.json'),{'operation':tag,'prior_registry_sha256':oldreg,'new_registry_sha256':sha(REG),'new_epoch_pointer_sha256':sha(EPOCH),'user_authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json')})
def register():
 held=lock();prepare();q=read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json');need(q['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','qualification absent')
 reg=read(REG);e=read(EPOCH);need(sha(REG)==e['native_registry_sha256'] and e['epoch']==2 and e['holder']==os.uname().nodename,'epoch/registry mismatch')
 need(C not in reg['registered_future_requests'],'request already registered')
 row={'project':'EP_L2','owner':'EP-MAIN','state':'AUTHORIZED_UNUSED','budget':1,'consumed':0,'automatic_retry':False,'reserved_write_bytes':spec()['reserved_write_bytes'],'spec_path':str(B/'control/FROZEN_SPEC.json'),'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'authorization_path':str(B/'control/USER_AUTHORIZATION.json'),'authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json'),'native_qualification_sha256':sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')}
 reg['registered_future_requests'][C]=row;reg['new_scientific_budget_remaining']+=1;registry_change(reg,e,'REGISTER')
 return {'status':'NEW_EXACT_COHORT_REGISTERED','request':row,'epoch':read(EPOCH)}
def info(pid):
 p=P('/proc')/str(pid);parts=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start_ticks':int(parts[19]),'mnt_namespace':os.readlink(p/'ns/mnt'),'exe':os.readlink(p/'exe'),'cmdline':(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),'maps':(p/'maps').read_text()}
def run():
 held=lock();prepared=prepare();s=spec();reg=read(REG);e=read(EPOCH);need(sha(REG)==e['native_registry_sha256'],'epoch CAS mismatch')
 row=reg['registered_future_requests'][C];need(row['spec_sha256']==sha(B/'control/FROZEN_SPEC.json') and row['authorization_sha256']==sha(B/'control/USER_AUTHORIZATION.json') and row['native_qualification_sha256']==sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),'registered spec/auth/native Q drift');need(row['state']=='AUTHORIZED_UNUSED' and row['consumed']==0 and row['budget']==1 and reg['new_scientific_budget_remaining']>0,'no unused exact budget')
 need(not (LED/(C+'.INTENT.json')).exists(),'already consumed; no restart')
 uid=str(uuid.uuid4());out=B/'run/results'/uid;out.mkdir()
 for p in (B/'env').iterdir():shutil.copy2(p,out/p.name)
 intent={'cohort':C,'uuid':uid,'utc':now(),'output':str(out),'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'authorization_sha256':sha(B/'control/USER_AUTHORIZATION.json'),'new_attempt_consumed':1,'consumed_before_launcher_fork':1,'automatic_retry':False}
 put(LED/(C+'.INTENT.json'),intent)
 row.update(state='CONSUMED_RUNNING_OR_UNRESOLVED',consumed=1,uuid=uid,output=str(out));reg['new_scientific_budget_remaining']-=1;registry_change(reg,e,'CONSUME')
 loader=str(N/'common-lib/ld-linux-x86-64.so.2')
 argv=[loader,'--library-path',str(N/'tools/lib')+':'+str(N/'common-lib'),str(N/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(out/'actual_file_process_network.log'),'--',loader,'--inhibit-cache','--library-path',str(N/'EP/env/lib'),str(B/'bin/accel-sim.out'),'-trace',s['trace_entry']]
 for i in range(4):argv+=['-config',str(out/('config-'+str(i)+'.config'))]
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','TMPDIR':str(B/'run/tmp'),'XDG_CACHE_HOME':str(B/'run/cache')}
 def limits():
  os.setsid();os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(s['memory_cap_bytes'],s['memory_cap_bytes']))
 start=time.monotonic();p=None;reason=None;rc=None;observed=None;peak=0;peak_rss=0;last=-10
 try:
  with (out/'raw.log').open('xb') as raw,(out/'RESOURCE_SAMPLES.jsonl').open('xb') as samples:
   p=subprocess.Popen(argv,cwd=out,env=env,stdout=raw,stderr=subprocess.STDOUT,preexec_fn=limits)
   put(out/'NATIVE_LAUNCH.json',{'utc':now(),'launcher_pid':p.pid,'argv':argv,'environment':env,'identity':identity(),'prepared':prepared,'source_identity':s['source_identity'],'spec_sha256':sha(B/'control/FROZEN_SPEC.json'),'entry_sha256':sha(__file__),'old174_ssh_scientific_execution':False})
   while p.poll() is None:
    children=P('/proc')/str(p.pid)/'task'/str(p.pid)/'children'
    for child in children.read_text().split() if children.exists() else []:
     try:
      v=info(int(child))
      if str(B/'bin/accel-sim.out') in v['maps'] and observed is None:
       need(v['mnt_namespace']=='mnt:[4026535153]','wrong simulator namespace');observed=v;put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',v)
     except (FileNotFoundError,ProcessLookupError):pass
    size=sum(f.stat().st_size for f in out.rglob('*') if f.is_file());peak=max(peak,size)
    if time.monotonic()-start-last>=5:
     last=time.monotonic()-start;r=resources();rss=0
     for pid in [p.pid,*([observed['pid']] if observed else [])]:
      try:rss+=int(next(t.split()[1] for t in (P('/proc')/str(pid)/'status').read_text().splitlines() if t.startswith('VmRSS:')))*1024
      except (FileNotFoundError,ProcessLookupError,StopIteration):pass
     peak_rss=max(peak_rss,rss);r.update(elapsed_seconds=last,observed_rss_bytes=rss,result_bytes=size);samples.write(enc(r).replace(b'\n',b' ')+b'\n');samples.flush()
     if not r['physical_disk_pass']:reason='RESOURCE_DISK_HOLD'
     if not r['physical_RAM_pass']:reason='RESOURCE_RAM_HOLD'
     if rss>s['memory_cap_bytes']:reason='PROCESS_RSS_CAP'
     need(sha(REG)==read(EPOCH)['native_registry_sha256'],'runtime epoch/registry drift')
    if size>s['result_cap_bytes']:reason='RESULT_CAP'
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
 receipt={'schema':'NATIVE_QUALIFICATION_EXECUTION_RECEIPT_V1','cohort':C,'uuid':uid,'output':str(out),'launcher_wait_returncode':rc,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'native_simulator_observed':observed is not None,'peak_observed_rss_bytes':peak_rss,'peak_result_logical_bytes':peak,'new_attempt_consumed':1,'automatic_retry':False,'old_EP_starts':57,'old_DTC_starts':2,'source_disposition':'SOURCE_KEEP','raw_sha256':sha(out/'raw.log') if (out/'raw.log').exists() else None,'scientific_acceptance':'PENDING_INDEPENDENT_NATIVE_EP_MAIN_TERMINAL_JOIN'}
 put(out/'NATIVE_EXIT.json',receipt);put(LED/(C+'.DONE.json'),receipt)
 reg=read(REG);e=read(EPOCH);reg['registered_future_requests'][C]['state']='COMPLETE' if rc==0 and reason is None else 'STOP_UNACCEPTED';registry_change(reg,e,'CLOSE')
 return receipt
def status():
 s={'cohort':C,'epoch':read(EPOCH),'registered':read(REG)['registered_future_requests'].get(C),'resources':resources()}
 for kind in ['INTENT','DONE']:
  p=LED/(C+'.'+kind+'.json')
  if p.exists():s[kind]=read(p)
 return s
def main(args):
 op=args[0]
 if op=='prepare':return prepare()
 if op=='qualify':return qualify()
 if op=='register':return register()
 if op=='run-native':return run()
 if op in ['inspect','status']:return status()
 raise RuntimeError('unsupported exact operation')
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'HOLD','reason':str(e),'automatic_retry':False},ensure_ascii=False),file=sys.stderr);sys.exit(2)
