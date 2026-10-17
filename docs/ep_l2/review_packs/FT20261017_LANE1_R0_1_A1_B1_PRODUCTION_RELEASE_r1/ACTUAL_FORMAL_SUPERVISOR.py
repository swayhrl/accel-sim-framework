import datetime,fcntl,hashlib,json,os,pathlib,signal,subprocess,time
out=pathlib.Path(__file__).resolve().parent
shared=pathlib.Path('/workspace/ep_l2_ft20261016_shared')
fw=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ft20261017-lane1-a1-fixed-r1');core=pathlib.Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-fixed-r1');build=pathlib.Path('/workspace/build/ep-l2-ft20261017-lane1-a1-fixed-r1')
assert json.loads((out.parent/'a1_red_r4/RECEIPT.json').read_text())['status']=='FOUR_REAL_A1_REPRODUCTIONS_CONFIRMED'
first=json.loads((out/'FIRST_RESOURCE_CONFIRMATION.json').read_text());deadline=datetime.datetime.fromisoformat('2026-10-17T13:25:31+00:00').timestamp()
def write(name,d):
 p=out/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def resources():
 with (shared/'REGISTRY.lock').open() as f:
  fcntl.flock(f,fcntl.LOCK_SH);d=json.loads((shared/'RUN_REGISTRY.json').read_text())
 return {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workspace_available_bytes':os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize,'share_available_bytes':os.statvfs('/root/share').f_bavail*os.statvfs('/root/share').f_frsize,'active':{k:{i:v for i,v in d[k].items() if v['status'] in ['RESERVED','RUNNING']} for k in ['runs','resource_leases']}}
def allocated_bytes(root):
 total=0
 if root.exists():
  for base,dirs,files in os.walk(root):
   for name in files:
    try:total+=(pathlib.Path(base)/name).lstat().st_blocks*512
    except FileNotFoundError:pass
 return total

def memory_available():
 for line in pathlib.Path('/proc/meminfo').read_text().splitlines():
  if line.startswith('MemAvailable:'): return int(line.split()[1])*1024
 raise RuntimeError('MemAvailable missing')

def owned_rss(pid):
 total=0;todo=[pid];seen=set()
 while todo:
  n=todo.pop()
  if n in seen:continue
  seen.add(n);p=pathlib.Path('/proc')/str(n)
  try:
   stat=(p/'stat').read_text().rsplit(')',1)[1].split();total+=int(stat[21])*os.sysconf('SC_PAGE_SIZE');todo.extend(map(int,(p/'task'/str(n)/'children').read_text().split()))
  except (FileNotFoundError,ProcessLookupError):pass
 return total
wait_until=datetime.datetime.fromisoformat(first['at']).timestamp()+61
while time.time()<wait_until:time.sleep(min(1,wait_until-time.time()))
with (shared/'LANE1_BUILD_EXECUTION.lock').open('a+') as mutex:
 fcntl.flock(mutex,fcntl.LOCK_EX|fcntl.LOCK_NB)
 second=resources();assert second['workspace_available_bytes']>=50*2**30 and not second['active']['resource_leases'];write('SECOND_RESOURCE_CONFIRMATION.json',second)
 assert not build.exists()
 for tree,expected in [(fw,'9bd17f9db3e8cbbc3fdad7283d1e292918546fd5'),(core,'7b8e6ac70b8fe0f1bd37efca11acb5284938825d')]:
  assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=tree,text=True).strip()==expected;assert subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=tree)==b''
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_TERMINAL_PROMPT='0',GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf',GIT_CONFIG_VALUE_0='git@github.com:',GIT_CONFIG_KEY_1='credential.helper',GIT_CONFIG_VALUE_1='!gh auth git-credential')
 command=['python3',str(fw/'util/ep_l2/ft_lane1/build_r0_1.py'),'--core',str(core),'--out',str(out/'producer'),'--execute']
 report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'first_confirmation':first,'second_confirmation':second,'mode':'FORMAL_R16_A1_B1_FRESH_SOURCE_31_DIRECTED_ORIGINAL_RESOURCE_GUARDS','maximum_build_jobs':2,'goal_deadline_utc':'2026-10-17T13:25:31+00:00','prior_failed_build_preserved':'/workspace/build/ep-l2-ft20261016-lane1-r0-1','minimum_workspace_available_bytes':second['workspace_available_bytes'],'minimum_share_available_bytes':second['share_available_bytes'],'sampled_peak_owned_tree_rss_bytes':0,'sampling_interval_seconds':2,'peak_scope':'sampled owner descendant aggregate RSS, not an unobserved continuous maximum','signal_scope':'Only this exact new producer PID receives INT; producer finally terminates its own child group and releases its lease'}
 start=time.monotonic();stopped=False
 with (out/'PRODUCER_CONSOLE.log').open('x') as log:
  p=subprocess.Popen(command,cwd=fw,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);stat=(pathlib.Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split();report['producer_identity']={'pid':p.pid,'start_ticks':int(stat[19]),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()};write('SUPERVISOR.json',report)
  while p.poll() is None:
   for name,key in [('/workspace','minimum_workspace_available_bytes'),('/root/share','minimum_share_available_bytes')]:
    f=os.statvfs(name);report[key]=min(report[key],f.f_bavail*f.f_frsize)
   report['sampled_peak_owned_build_allocated_bytes']=max(report.get('sampled_peak_owned_build_allocated_bytes',0),allocated_bytes(build));report['sampled_peak_owned_output_allocated_bytes']=max(report.get('sampled_peak_owned_output_allocated_bytes',0),allocated_bytes(out));report['minimum_available_memory_bytes']=min(report.get('minimum_available_memory_bytes',2**63),memory_available());report['sampled_peak_owned_tree_rss_bytes']=max(report['sampled_peak_owned_tree_rss_bytes'],owned_rss(p.pid))
   if (time.time()>=deadline or os.statvfs('/root/share').f_bavail*os.statvfs('/root/share').f_frsize<40*2**30) and not stopped:p.send_signal(signal.SIGINT);stopped=True;report['stop_reason']='BOUNDED_CONTINUE_DEADLINE' if time.time()>=deadline else 'SHARE_40GIB_FLOOR'
   report['last_observed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write('SUPERVISOR.json',report);time.sleep(2)
 report.update(exit_code=p.returncode,wall_seconds=time.monotonic()-start,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),final_resources=resources());write('SUPERVISOR.json',report);print(json.dumps(report))
