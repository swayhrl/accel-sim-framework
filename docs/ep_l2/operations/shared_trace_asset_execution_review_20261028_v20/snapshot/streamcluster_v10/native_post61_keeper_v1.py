"""Root-only exact Native lease holder; no GPU or whole-queue lease."""
import pathlib,hashlib,sys
_C=pathlib.Path(__file__).with_name('sc_remote_common_v1.py');_B=_C.read_bytes()
if hashlib.sha256(_B).hexdigest()!='4472b0ff40f6448dd67f78d861c0e7394d23bce5f48607985df11c01d8063cd5':raise RuntimeError('COMMON_RAW_PIN')
exec(compile(_B,str(_C),'exec'),globals())
import argparse,fcntl,signal,subprocess,shlex,threading,socket
D=pathlib.Path(__file__).resolve().parent
def native_gate(a,root):
 # Native2GiB is ONLY this control tree. Heavy POST uses the independent109 10GiB+8GiB gate.
 r=a['native_resource_code_manifest_ref'];need(r['sha256']=='952f859b6818109d8fe4b83f4f3a8ffc3eddfe54f792b257c88010beb473b8ee','FROZEN_R4_MF');mf=readref(r);base=pathlib.Path(r['path']).parent
 for n,v in mf['files'].items():need((base/n).stat().st_size==v['bytes']and digest(base/n)==v['sha256'],'NATIVE_OBSERVER_MF_PIN')
 old=list(sys.path);sys.path.insert(0,str(base));previous_helpers={}
 helpers=['hash18_registered_spec_planning_v1','dtc_l2_mlp_registered_spec_planning_v1','dtc_recovery12_registered_r20_spec_planning_v1']
 for name in helpers:
  previous_helpers[name]=sys.modules.get(name);sys.modules[name]=pinned_module(base/(name+'.py'),mf['files'][name+'.py']['sha256'],name)
 try:
  o=pinned_module(base/'current_foreign_observer_v1.py',mf['files']['current_foreign_observer_v1.py']['sha256'],'SC61_foreign')
  def raw_existing(name,path):
   need(path==o.V/'resources.py','ONLY_PINNED_EXISTING_RESOURCE_MODULE');return pinned_module(path,'ce77a7748e8beb0ff4eb71571e4a24858e0e2c905d1bf15a0c642d07b18d84bd',name)
  o.load=raw_existing
  for name,h in [('PROFILE.json','a3d8362d8c06e563cb74d55f92762d2f58d18943f0061fa5a87256335df9f8ce'),('legacy_foreign_binding.json','e069be66ddd0e7d9e7000c2edc93d0dcc12436e830c6f685a08e8c0960ce2c34')]:need(digest(o.V/name)==h,'FIXED_R5_DATA')
  v=o.observe();need(v['unknown_active_cohort_count']==0,'NATIVE_UNKNOWN_FOREIGN')
  mr=a['memory_module_ref'];need(mr['sha256']=='ccde5eb672a38448b834b8339cbbaf1ceeab1b9e8d4ac101253965eab7dd1238','FIXED_MEMORY_MODULE');m=pinned_module(mr['path'],mr['sha256'],'SC61_memory');snap=m.collect();verdict=m.evaluate(snap,v['additional_active_RAM_commitments_bytes'],2*G,'native174')
 finally:
  sys.path[:]=old
  for name,value in previous_helpers.items():
   if value is None:sys.modules.pop(name,None)
   else:sys.modules[name]=value
 light=native_light_verdict(verdict,v,a['Native_bridge_policy'])
 need(shutil.disk_usage('/root/data').free>=5*G+64*2**20,'NATIVE_FLOOR')
 save(root/('NATIVE_RESOURCE_'+str(time.time_ns())+'.json'),dict(light_bridge_verdict=light,original_full_R4_aggregate_verdict=verdict,additional_foreign=v['additional_active_RAM_commitments_bytes'],own_control=2*G,heavy_POST_budget_checked_separately_109=True))
def main():
 p=argparse.ArgumentParser();p.add_argument('--scope',required=True);p.add_argument('--scope-sha',required=True);p.add_argument('--code-sha',required=True);x=p.parse_args()
 code_check(D,x.code_sha);need(D==NB,'ROOT_INSTALLED_NATIVE_CODE')
 ap=pathlib.Path(x.scope);need(ap.parent==pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control'),'ROOT_NATIVE_CONTROL_SCOPE')
 st=ap.stat();need(st.st_uid==0 and st.st_mode&0o022==0,'ROOT_AUTHORITY_ATTRIBUTES')
 a=validate_scope(readref(dict(path=str(ap),bytes=st.st_size,sha256=x.scope_sha)));readref(a['Root_user_cpu_only_authorization_ref']);readref(a['Root_cpu_only_resource_ref']);need(a['code_manifest_sha256']==x.code_sha,'SCOPE_CODE_PIN')
 need(a['Native_host']==socket.gethostname()and a['Native_boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'NATIVE_BOOT')
 need(set(a['Native_cpu_ids'])<=os.sched_getaffinity(0),'NATIVE_CPUS');os.sched_setaffinity(0,set(a['Native_cpu_ids']));os.nice(15)
 resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.umask(0o077)
 root=NB/'runs'/a['run_id'];root.mkdir(parents=True,exist_ok=False)
 with(root/'ROOT_SCOPE.raw.json').open('xb')as f:f.write(ap.read_bytes());f.flush();os.fsync(f.fileno())
 frozen=readref(a['frozen_source_proof_ref']);need(frozen['schema']=='ROOT_FROZEN_READ_ONLY_POST_ASSET_V1'and frozen['source_mode']=='FrozenReadOnly'and frozen['source_KEEP']is True and frozen['job_id']==JOB and frozen['source_root']==str(NS)and frozen['snapshot_ref']['sha256']==a['frozen_snapshot_raw_sha256']=='25882c6056ba64866713b1dd0836c8aa0c0424ddb360f66d769e3f498165e24e','ORIGINAL_FROZEN_READONLY_F9_SOURCE')
 native_gate(a,root);mf=json.loads((D/'CODE_MANIFEST.json').read_bytes());O=pinned_module(D/'owned_runtime_v1.py',mf['files']['owned_runtime_v1.py']['sha256'],'SC61_owned');O.set_subreaper();me=O.ident(os.getpid())
 retire=a['Root_old_SC_owner_closed_and_stale_auth_retired_ref'];need(retire['sha256']=='d723c79225dba461493efd7d485c6550362cc2d9476ecbcca55ec7536a86da3c','EXACT_OLD_TERMINAL_RETIREMENT')
 z=readref(retire);zc=readref(z['actual_failed_owned_closed']);old_owner=z['owner'];now=O.ident(old_owner[0]);need(z['actual_pid_absent']is True and zc['status']=='ALL_OWNED_CLOSED_BEFORE_LAST_FD_CLOSE'and(now is None or now[1]!=old_owner[1]),'OLD_OWNED_NOT_CLOSED')
 need(not pathlib.Path(z['original_AUTH_ref']['path']).exists()and not pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/ROOT_STREAMCLUSTER_CPU_RESUME_EXEC_APPROVAL_V2.json').exists(),'OLD_AUTH_STILL_PRESENT')
 extra=extra2_acceptance();old_release=readref(extra['source_Native_release_ref']);old_native_owner=old_release['owner'];now=O.ident(old_native_owner[0]);need(old_release['scope_sha256']=='d1877f2a07943b3204ff7403e0f1a40aeb2a3699ef4e15cd3b32317c9142616e'and old_release['status']=='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED'and(now is None or now[1]!=old_native_owner[1]),'V1_OLD_NATIVE_CLOSED_RELEASED_NO_DUPLICATE')
 prior=readref(a['predecessor_V4_release_ref']);prior_scope=a['predecessor_V4_scope_ref'];readref(prior_scope);oldowner=prior['owner'];now=O.ident(oldowner[0]);need(prior['scope_sha256']==prior_scope['sha256']and prior['status']=='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED'and(now is None or now[1]!=oldowner[1]),'V4_PREDECESSOR_RELEASED_NO_RESTART_DUPLICATE')
 latest=readref(a['predecessor_V7_release_ref']);latest_scope=a['predecessor_V7_scope_ref'];readref(latest_scope);owner=latest['owner'];now=O.ident(owner[0]);need(latest['scope_sha256']==latest_scope['sha256']and latest['status']=='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED'and(now is None or now[1]!=owner[1]),'V7_PREDECESSOR_RELEASED_NO_DUPLICATE')
 accepted=accepted_v8(a);v8release=readref(accepted['source_Native_release_ref']);v8scope=accepted['source_scope_ref'];readref(v8scope);owner=v8release['owner'];now=O.ident(owner[0]);need(v8release['scope_sha256']==v8scope['sha256']and v8release['status']=='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED'and(now is None or now[1]!=owner[1]),'V8_MIGRATION_PREDECESSOR_CLOSED')
 failed=readref(a['Root_V9_failed_bootstrap_closure_ref']);need(failed['scope_sha256']=='40dbfe8c72e32b4e51442a5c06ee510f30033894eb11da932dd751a6011c6afe'and failed['Native_owner']==[2001093,'988396571']and failed['Native_exact_owner_absent']is True and failed['Native_asset4_kernel_held_rows']==[]and failed['remote']['exact_scope_processes']==[]and failed['remote']['exact_service_cgroup_exists']is False and failed['POST_workers_started']==0,'EXACT_V9_FAILED_BOOTSTRAP_SUPPLEMENTAL_CLOSURE')
 now=O.ident(2001093);need(now is None or now[1]!='988396571','V9_NATIVE_OLD_EXACT_OWNER_STILL_PRESENT')
 paths=[pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/asset_operations')/JOB/n for n in ['CAPTURE.lock','INPUT.lock','OUTPUT.lock','RUNTIME.lock']]
 fds=[];proc=None;launched=False;closed=False;stop=threading.Event();finished=threading.Event();seq=[0];send_lock=threading.Lock()
 def frame(kind):
  with send_lock:
   seq[0]+=1;proc.stdin.write((json.dumps(dict(kind=kind,scope_sha256=x.scope_sha,seq=seq[0]))+'\n').encode());proc.stdin.flush()
 def heartbeat():
  while not finished.is_set():
   try:frame('STOP'if stop.is_set()or time.time()>=DEADLINE else'BEAT')
   except(BrokenPipeError,OSError,ValueError):pass
   time.sleep(.2)
 for sig in [signal.SIGTERM,signal.SIGHUP,signal.SIGINT]:signal.signal(sig,lambda s,f:stop.set())
 try:
  for lp in paths:
   no_links(lp);fd=os.open(lp,os.O_RDWR|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);fds.append(fd)
  save(root/'NATIVE_KEEPER.json',dict(owner=me,scope_sha256=x.scope_sha,locks=[dict(path=str(p),fd=fd,dev=os.fstat(fd).st_dev,inode=os.fstat(fd).st_ino)for p,fd in zip(paths,fds)],no_GPU_or_queue_lock=True))
  argv=['systemd-run','--user','--quiet','--wait','--collect','--pipe','--unit=sc-post59-'+a['run_id'],'--property=MemoryMax='+str(10*G),'--property=MemorySwapMax=0','--property=OOMPolicy=kill','--property=CPUQuota=800%','--property=AllowedCPUs='+','.join(map(str,a['remote_cpu_ids'])),'--property=KillMode=control-group','--property=TimeoutStopSec=30','--','/usr/bin/python3','-I','-S','-B',str(RB/'remote_post61_v1.py'),'--run',a['run_id'],'--scope-sha',x.scope_sha,'--code-sha',x.code_sha]
  def bound_ssh():resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20))
  sshbase=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ControlMaster=no','-o','ControlPath=none','-o','ControlPersist=no','gpu109']
  with(root/'REMOTE.stdout.log').open('xb')as out,(root/'REMOTE.stderr.log').open('xb')as err:
   launched=True;proc=subprocess.Popen(sshbase+[shlex.join(argv)],stdin=subprocess.PIPE,stdout=out,stderr=err,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
  heartbeat_thread=threading.Thread(target=heartbeat,daemon=True);heartbeat_thread.start();last_resource=time.monotonic()
  while not(root/'REMOTE_CLOSED_PROPOSAL.json').exists():
   need(proc.poll()is None,'SSH_EXIT_WITHOUT_REMOTE_CLOSURE')
   if time.time()>=DEADLINE:stop.set()
   if time.monotonic()-last_resource>30:
    try:native_gate(a,root)
    except BaseException:stop.set()
    last_resource=time.monotonic()
   time.sleep(.2)
  observer=['/usr/bin/python3','-I','-S','-B',str(RB/'remote_post61_v1.py'),'--run',a['run_id'],'--scope-sha',x.scope_sha,'--code-sha',x.code_sha,'--observe']
  cp=subprocess.run(sshbase+[shlex.join(observer)],capture_output=True,timeout=30,preexec_fn=bound_ssh,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
  need(cp.returncode==0,'INDEPENDENT109_CLOSURE_OBSERVER');v=json.loads(cp.stdout);need(v['scope_sha256']==x.scope_sha and v['owned_closed']is True and v['proposal_sha256']==digest(root/'REMOTE_CLOSED_PROPOSAL.json'),'EXACT_CLOSURE_WITNESS')
  save(root/'REMOTE_CLOSURE_OBSERVATION.json',v);save(root/'NATIVE_CLEANUP_ACK.json',dict(scope_sha256=x.scope_sha,proposal_sha256=v['proposal_sha256'],owner=me,observation_sha256=digest(root/'REMOTE_CLOSURE_OBSERVATION.json')))
  end=time.monotonic()+30
  while not(root/'REMOTE_ACK_CONSUMED.json').exists():need(time.monotonic()<end,'REMOTE_ACK_MISSING');time.sleep(.1)
  ack=json.loads((root/'REMOTE_ACK_CONSUMED.json').read_bytes());need(ack['scope_sha256']==x.scope_sha and ack['ACK_sha256']==digest(root/'NATIVE_CLEANUP_ACK.json'),'ACK_PIN')
  finished.set();heartbeat_thread.join(timeout=10);need(not heartbeat_thread.is_alive(),'NATIVE_HEARTBEAT_NOT_CLOSED_BEFORE_STDIN_CLOSE');proc.stdin.close();proc.wait(timeout=30);O.reap();need(not O.children(me),'LOCAL_OWNED_CLOSED')
  for fd in fds:os.close(fd)
  fds=[];closed=True;save(root/'NATIVE_RELEASED.json',dict(scope_sha256=x.scope_sha,owner=me,status='REMOTE_OWNED_CLOSED_ACKED_ASSET_LOCKS_RELEASED',remote_returncode=proc.returncode,source_KEEP=True))
 except BaseException as e:
  stop.set()
  if launched and not closed:
   if proc is not None and proc.stdin and not proc.stdin.closed:
    try:proc.stdin.close()
    except BrokenPipeError:pass
   O.hold(root/'HOLD_UNKNOWN.json',e,fds)
  else:
   for fd in fds:os.close(fd)
   raise
if __name__=='__main__':main()
