import pathlib,json,hashlib,importlib.util,copy,os,tempfile,subprocess,time,signal,fcntl,datetime,ast,types
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
adapter=load('host_QA_adapter','sweep_host_execution_v1.py');native=load('host_QA_original_engine','sweep_native_cap1m.py');checks=[]
base={'cgroup_memory_max':str(256*G),'cgroup_memory_current':200*G,'host_MemAvailable_bytes':300*G,'reserved_additional_live_and_candidate_RAM_bytes':128*G,'physical_RAM_pass':False,'physical_disk_pass':True}
stat={'file':180*G,'inactive_file':160*G,'shmem':2*G,'file_mapped':G,'file_dirty':G,'file_writeback':G}
r=adapter.adjusted(base,stat);assert r['physical_RAM_pass'] and r['physical_disk_pass'] and r['cgroup_reclaimable_clean_inactive_file_credit_bytes']==152*G;checks.append('clean_inactive_cache_credit_keeps48GiB_plus_all_hard_cap_reservations')
for name,bs,st in [('no_cache',base,{}),('dirty_cache',base,dict(stat,file_dirty=180*G)),('mapped_cache',base,dict(stat,file_mapped=180*G)),('low_host_MemAvailable',dict(base,host_MemAvailable_bytes=100*G),stat),('anon_exhaustion',dict(base,cgroup_memory_current=255*G),{})]:
 assert not adapter.adjusted(bs,st)['physical_RAM_pass'];checks.append(name+'_rejected')
assert adapter.adjusted(dict(base,physical_disk_pass=False),stat)['physical_disk_pass'] is False;checks.append('disk_guard_not_relaxed')
assert adapter.memory_credit({'file':100*G,'inactive_file':300*G,'shmem':90*G})==2*G;checks.append('credit_bounded_by_clean_file_excluding_shared_pages')
with tempfile.TemporaryDirectory(prefix='dtc_host_binding_fixture_') as tmp:
 a=load('isolated_host_binding_fixture','sweep_host_execution_v1.py');a.T=P(tmp);root=P(tmp);(root/'control/qualification_ledger').mkdir(parents=True);(root/'tools').mkdir();(root/'tools/sweep_native_cap1m.py').write_text('CPU_FIXTURE_ONLY')
 cell='FIXTURE_NEW';old='FIXTURE_OLD';uuid='CPU_FIXTURE_UUID';out=root/uuid;out.mkdir();orig={'cohort':cell,'host_cpu':4,'scientific_options':['UNCHANGED']};(root/'control'/(cell+'_SPEC.json')).write_text(json.dumps(orig));claims={'claims':{cell:{'host_cpu':64}}};cp=root/'control/POOL_DISPATCH_RESERVATIONS.json';cp.write_text(json.dumps(claims));fq={'consumed':{cell:{'uuid':uuid}}};profile={'preserved_prefix_cells':[old],'allowed_CPUs':[4,64],'control_CPUs':sorted(os.sched_getaffinity(0)),'plan_sha256':'CPU_FIXTURE'}
 def save(p,r):
  with P(p).open('x') as f:json.dump(r,f)
 fake=types.SimpleNamespace(spec_for=lambda c:copy.deepcopy(dict(orig,cohort=c)),resources=lambda s,f=False:dict(base),exclusive=save,child_info=lambda pid:{'pid':pid},read_current_authority=lambda:( {'registered_future_requests':{'FIXTURE':fq}},{}),REQUEST='FIXTURE')
 a.plan=lambda n:(fq,profile);fake=a.install(fake);assert fake.spec_for(cell)['host_cpu']==64 and orig['host_cpu']==4 and fake.spec_for(old)['host_cpu']==4;checks.append('only_future_host_CPU_override_original_scientific_fields_and_prefix_CPU_preserved')
 claims['claims'][cell]['host_cpu']=999;cp.write_text(json.dumps(claims))
 try:fake.spec_for(cell);raise RuntimeError('outside_CPU_not_rejected')
 except AssertionError:pass
 claims['claims'][cell]['host_cpu']=64;cp.write_text(json.dumps(claims));checks.append('unregistered_CPU_assignment_rejected')
 fake.exclusive(root/'control/qualification_ledger'/(cell+'.INTENT.json'),{'cohort':cell,'uuid':uuid});intent=read(root/'control/qualification_ledger'/(cell+'.INTENT.json'));assert intent['host_execution_binding']['actual_host_cpu']==64
 fake.exclusive(out/'NATIVE_LAUNCH.json',{'scientific_qualification_uuid':uuid});assert read(out/'NATIVE_LAUNCH.json')['host_execution_binding']==intent['host_execution_binding'];checks.append('explicit_adapter_identity_and_CPU_join_in_INTENT_and_actual_launch')
 child=subprocess.Popen(['/usr/bin/python3','-c','import time;time.sleep(3)'],preexec_fn=lambda:os.sched_setaffinity(0,{64}))
 try:
  observed=fake.child_info(child.pid);assert observed['host_cpu_affinity_actual']==[64];fake.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',observed);checks.append('real_CPU_only_child_actual_kernel_affinity_bound_in_PID_receipt')
  try:fake.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(observed,host_cpu_affinity_actual=[65]));raise RuntimeError('wrong_actual_affinity_not_rejected')
  except AssertionError:pass
  checks.append('actual_PID_CPU_mismatch_rejected_before_receipt_write')
 finally:child.wait(timeout=5)
q=native.read_current_authority()[0]['registered_future_requests'][native.REQUEST];assert len(q['consumed'])==129 and q['state']=='RUNNING' and q['budget']==356
original_rows=copy.deepcopy(q['consumed']);original_histories=native.read_current_authority()[0]
profile=read(T/'control/CAP1M_RUNTIME_PROFILE_CANDIDATE.json')
for row in profile['source_pins']+q['shared_tool_pins']:assert sha(row['path'])==row['sha256']
checks.append('all_original_source_pins_and_spent129_still_preserved')
failure=load('host_QA_memory_failure','sweep_failure_review_host_v1.py').classify('E2-AEV100-e7bb67e63e3c3847-DH');assert failure['scientific_acceptance'] is False and failure['accepted_cycles'] is None and failure['model_retries']==0
checks.append('actual_MEMORY_HEADROOM_failure_full_raw_SHA_and_guard_samples_classified_no_cycle')
# Exact stdlib/Linux parent-only retirement fixture. CPU-only sleeping child,
# separate native-like session, no signal to that child and no scientific code.
with tempfile.TemporaryDirectory(prefix='dtc_host_parent_transport_') as tmp:
 root=P(tmp);lockfile=root/'lease';marker=root/'closed';lockfile.touch()
 childcode='import time,pathlib;time.sleep(2);pathlib.Path('+repr(str(marker))+').write_text("NATURAL_CPU_FIXTURE_CLOSED")'
 parentcode='import subprocess,fcntl,sys,json,time;f=open('+repr(str(lockfile))+',"rb");fcntl.flock(f,fcntl.LOCK_EX);p=subprocess.Popen([sys.executable,"-c",'+repr(childcode)+'],start_new_session=True,close_fds=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);print(json.dumps({"pid":p.pid}),flush=True);p.wait()'
 parent=subprocess.Popen(['/usr/bin/python3','-c',parentcode],stdout=subprocess.PIPE,text=True,start_new_session=True);childpid=json.loads(parent.stdout.readline())['pid'];before=(P('/proc')/str(childpid)/'stat').read_text().rsplit(')',1)[1].split();ticks=int(before[19]);os.kill(parent.pid,signal.SIGTERM);parent.wait(timeout=3)
 after=(P('/proc')/str(childpid)/'stat').read_text().rsplit(')',1)[1].split();assert int(after[19])==ticks and after[0] not in ['Z','X']
 with lockfile.open('rb') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 deadline=time.monotonic()+5
 while not marker.exists() and time.monotonic()<deadline:time.sleep(.1)
 assert marker.read_text()=='NATURAL_CPU_FIXTURE_CLOSED';checks.append('parent_only_SIGTERM_releases_lease_child_survives_and_naturally_closes')
allowed=os.sched_getaffinity(0);cpus=[];cores=set()
for cpu in range(64,128):
 if cpu not in allowed:continue
 p=P('/sys/devices/system/cpu')/('cpu'+str(cpu))/'topology';key=((p/'physical_package_id').read_text(),(p/'core_id').read_text())
 if key not in cores:cores.add(key);cpus.append(cpu)
 if len(cpus)==32:break
assert len(cpus)>=12 and set(range(32,48))<=allowed;checks.append('distinct_physical_model_cores_and_separate_frontend_CPU_pool')
pins=[]
for file in ['sweep_host_execution_v1.py','sweep_frontend_host_v1.py','sweep_failure_review_host_v1.py','revision7/sweep_controller.py']:
 p=T/'tools'/file;compile(p.read_text(),str(p),'exec');pins.append({'path':str(p),'sha256':sha(p)})
pins.extend(profile['source_pins']);pins={r['path']:r for r in pins};pins=list(pins.values())
plan={'schema':'DTC_HOST_EXECUTION_ADAPTER_PLAN_V1','profile_id':'HOST_CPU_CACHE_AWARE_V1','adapter_sha256':sha(T/'tools/sweep_host_execution_v1.py'),'preserved_prefix_cells':sorted(q['consumed']),'preserved_prefix_count':129,'maximum_jobs':12,'model_CPUs':cpus,'control_CPUs':list(range(32,48)),'allowed_CPUs':sorted(set(cpus)|set(range(4,9))),'per_model_address_space_and_RSS_cap_unchanged_bytes':16*G,'source_pins':pins,'prior_entry_sha256':sha(P('/root/data/ep_l2_dtc_l1_native_v2/bin/native')),'memory_basis':'HostMemAvailable>=64GiB+all remaining16GiB hard caps; cgroup rawfree+clean inactive cache credit>=48GiB+same caps; exclude shared/mapped/dirty/writeback plus8GiB cache margin. While an original frontend is live additionally preserve its original raw-current predicate plus32GiB extra raw headroom. No global cache drop.','user_authorized_high_parallelism':True,'model_retries':0,'scientific_cache_config_input_options_changed':False,'source_spec_and_spent_history_changed':False,'future_unused_only':True,'local_floor_bytes':5*G}
if (T/'control/HOST_EXECUTION_PLAN_V1.json').exists():assert read(T/'control/HOST_EXECUTION_PLAN_V1.json')==plan
else:exclusive(T/'control/HOST_EXECUTION_PLAN_V1.json',plan)
assert native.read_current_authority()[0]['registered_future_requests'][native.REQUEST]['consumed']==original_rows
qualification={'status':'PASS','controller_sha256':sha(T/'tools/revision7/sweep_controller.py'),'plan_sha256':sha(T/'control/HOST_EXECUTION_PLAN_V1.json'),'qualification_source_sha256':sha(T/'tools/host_execution_qualification_v1.py'),'checks':checks,'check_count':len(checks),'scientific_model_starts':0,'model_signals':0,'CPU_fixture_parent_signals':1,'source_pins':pins,'actual_negative_failure_sha256':sha(T/'analysis/E2-AEV100-e7bb67e63e3c3847-DH.FAILURE_CLASSIFICATION_R5.json'),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
oldqual=T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json'
if oldqual.exists():oldqual.rename(T/'control/draft_preimages/CONTINUATION_R7_QUAL_BEFORE_ACTUAL_CPU_BINDING_CASES.json')
exclusive(T/'control/CONTINUATION_R7_ZERO_MODEL_QUALIFICATION.json',qualification)
print(json.dumps({'status':'PASS','checks':len(checks),'maximum_jobs':12,'model_CPUs':cpus,'memory_STOP_sample':{k:failure['negative_outer_RAM_samples'][-1].get(k) for k in ['cgroup_memory_current','cgroup_memory_max','reserved_additional_live_and_candidate_RAM_bytes','host_MemAvailable_bytes','physical_RAM_pass']},'new_scientific_starts':0}))
