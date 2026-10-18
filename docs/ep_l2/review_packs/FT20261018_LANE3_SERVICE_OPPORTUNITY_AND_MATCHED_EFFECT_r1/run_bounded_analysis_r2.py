import pathlib,json,hashlib,subprocess,sys,importlib.util,resource,os,datetime,fcntl
root=pathlib.Path('/workspace/ep_l2_ft20261016_shared');out=pathlib.Path(__file__).parent
client=json.loads((root/'CLIENT_CONTRACT.json').read_text());module=pathlib.Path(client['registry_client']);blob=module.read_bytes();expected=client['registry_client_sha256']
if hashlib.sha256(blob).hexdigest()!=expected:
 blob=subprocess.check_output(['git','show',client['registry_source_commit']+':util/ep_l2/ft_lane5/registry.py'],cwd='/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1');assert hashlib.sha256(blob).hexdigest()==expected
 module=out/'published_registry.py';module.write_bytes(blob)
spec=importlib.util.spec_from_file_location('registry',module);regmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(regmod);registry=regmod.Registry()
pre=registry.snapshot();active=lambda rows:{k:v for k,v in rows.items() if v['status'] in ('RUNNING','RESERVED')}
processes=[]
for proc in pathlib.Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');exe=os.readlink(proc/'exe')
  if any(k in exe for k in ('accel-sim','yosys','vvp')) or ('ep_l2' in cmd and 'guard_unique.py' in cmd):
   stat=(proc/'stat').read_text().split(') ',1)[1].split();processes.append(dict(pid=int(proc.name),cmdline=cmd,exe=exe,start_ticks=int(stat[19]),cwd=os.readlink(proc/'cwd')))
 except (OSError,IndexError):pass
state=dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),scientific_acceptance=client['scientific_acceptance'],active_runs=active(pre['runs']),active_leases=active(pre['resource_leases']),campaign_summary={k: {z:v.get(z) for z in ('t0_unix','deadline_unix','maximum_starts')} for k,v in pre.get('campaigns',{}).items()},resources=regmod.local_resources(),actual_processes=processes,registry_client_sha256=expected,registry_client_source=client['registry_source_commit'])
(out/'PREFLIGHT_r2.json').write_text(json.dumps(state,indent=2)+'\n')
lease=registry.build_lease('lane3',cpu=1,memory=2*2**30)
record=dict(lease=lease,owner='lane3',cpu=1,memory_bytes=2*2**30,kind='read_only_analysis_not_build',maximum_seconds=180,maximum_output_bytes=32*2**20)
(out/'ANALYSIS_LEASE_r2.json').write_text(json.dumps(record,indent=2)+'\n')
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
try:
 with (out/'derive_r2.stdout.log').open('w') as stdout,(out/'derive_r2.stderr.log').open('w') as stderr:
  result=subprocess.run([sys.executable,'util/ep_l2/service_opportunity_v1/derive.py','--out',str(out/'derived_r2')],cwd='/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane3-v1',stdout=stdout,stderr=stderr,timeout=180,preexec_fn=limits,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
 record['exit_code']=result.returncode
finally:
 registry.release_build(lease,'lane3');record['released']=True;record['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'ANALYSIS_LEASE_r2.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));print((out/'derive_r2.stdout.log').read_text());print((out/'derive_r2.stderr.log').read_text());assert result.returncode==0
