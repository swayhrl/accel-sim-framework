import importlib.util,pathlib,json,copy,time,os,tempfile,fcntl,subprocess
P=pathlib.Path;D=P(__file__).parent;sp=importlib.util.spec_from_file_location('resource_test',D/'resources_v3.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
G=1<<30;M=1<<20;checks=[]
def check(name,value):
 checks.append(dict(name=name,passed=bool(value)));assert value,name
s=r.snapshot(r.REQUESTS['midtag']);check('actual_no_foreign_metadata_errors',not s['foreign_metadata_errors']);check('actual_true164_verified',s['true164_mount_verified']);check('actual_loader_DTC48_all_claim_models_mapped',all(x['kind']=='MODEL'for x in s['actual_loader_aware_models']))
cpu=next(x for x in s['cpu_allowed']if x not in s['occupied_model_or_claim_cpus']);p=dict(requested_host_cpu=cpu,max_global_EP_models=10)
def decision(z=None,pol=None):
 z=copy.deepcopy(s if z is None else z);z['monotonic']=time.monotonic();return r.admit(z,G,256*M,policy=dict(p,**(pol or{})))
check('actual_fresh_numeric_admission_PASS_no_science',decision()['pass_admission'])
for n,cap,ok in [(9,10,True),(10,10,False),(1,2,True),(2,2,False)]:
 z=copy.deepcopy(s);z['global_EP_consumed_active_count']=n;check('globalEP_preconsume_'+str(n)+'_cap'+str(cap),decision(z,dict(max_global_EP_models=cap))['pass_admission']==ok)
check('stage_hold_preserved',not decision(pol=dict(stage_ready=False))['pass_admission'])
for name,field,value in [('RAM','host_MemAvailable_bytes',0),('cgroup','cgroup_effective_headroom_bytes',0),('SSD','native_free_bytes',0),('true164','true164_mount_verified',False),('inodes','free_inodes',0)]:
 z=copy.deepcopy(s);z[field]=value;check(name+'_HOLD',not decision(z)['pass_admission'])
z=copy.deepcopy(s);z['foreign_metadata_errors'].append('UNKNOWN_FOREIGN_OWNER');check('unknownforeign_HOLD',not decision(z)['pass_admission'])
check('growth_subtracts_actualRSS_once',r.remaining_growth(4*G,8*G,3*G)==G)
check('RSS_at_estimate_no_double_add',r.remaining_growth(4*G,8*G,4*G)==0)
check('existing_allocations_not_added_to_admission',decision()['required_additional_RAM_bytes']==s['foreign_additional_RAM_bytes']+G)
check('no_legacy_35GiB_extra_pool',decision()['required_free_bytes']<s['foreign_remaining_write_bytes']+256*M+6*G)
check('DTC48_lifetime_ceiling_not_added',s['DTC48_accounting']['derived_remaining_write_bytes']<=s['DTC48_accounting']['published_lifetime_ceiling_bytes'])
for argv,expected in [(['/bin/accel-sim.out','-trace','x'],'MODEL'),(['/lib64/ld-linux-x86-64.so.2','/bin/accel-sim.out'],'MODEL'),(['/bin/strace','/lib64/ld-linux-x86-64.so.2','/bin/accel-sim.out'],'WRAPPER_NOT_MODEL'),(['/bin/unreviewed','/bin/accel-sim.out'],'UNKNOWN_MODEL_WRAPPER')]:check('argv_'+expected,r.classify(argv)==expected)
if s['occupied_model_or_claim_cpus']:check('actual_foreign_CPU_conflict_HOLD',not decision(pol=dict(requested_host_cpu=s['occupied_model_or_claim_cpus'][0]))['pass_admission'])
check('outside_allowed_CPU_HOLD',not decision(pol=dict(requested_host_cpu=max(s['cpu_allowed'])+1))['pass_admission'])
z=copy.deepcopy(s);z['cpu_quota_equivalent']=len(z['actual_loader_aware_models']);check('cgroup_CPUquota_HOLD',not decision(z)['pass_admission'])
z=copy.deepcopy(s);z['EP_CPU_claims'].append(dict(request=z['current_request'],cohort='EXACT_OWN',state='CLAIMED',cpu=cpu));selfp=dict(requested_request_id=z['current_request'],requested_cohort='EXACT_OWN');check('exact_own_CLAIMED_CPU_exemption',decision(z,selfp)['pass_admission']);check('different_cohort_not_exempt',not decision(z,dict(selfp,requested_cohort='OTHER'))['pass_admission']);z['EP_CPU_claims'][-1]['state']='RUNNING';check('RUNNING_never_own_CLAIMED_exempt',not decision(z,selfp)['pass_admission'])
z=copy.deepcopy(s);z.update(current_own_restore_window_bytes=256*M,foreign_write_entries=[dict(request=r.REQUESTS['vector1700'],kind='ONE_SHARED_RESTORE_WINDOW_AND_2M_METADATA',bytes=256*M+2*M)],foreign_remaining_write_bytes=256*M+2*M);dedup,ow,rec=r.dedup_restore(z,300*M);check('shared_restore_window_not_doublecounted',dedup['foreign_remaining_write_bytes']==2*M and ow==300*M and rec['global_window_max_bytes']==256*M)
q={'registered_future_requests':{'EP_UNKNOWN_RAM_OWNER':dict(state='RUNNING',consumed={'X':dict(state='RUNNING')},reserved_write_bytes=1)}};b=r.runtime().qualified_math().base();check('real_mapper_unknown_owner_failclosed',any('unmapped active foreign RAM owner' in x for x in b.foreign_commitments(q)['foreign_metadata_errors']))
# Read-only exact lock binding in both archivers; no global lock acquisition or mutation.
a=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1')
for root in [a/'runtimes/midtag',a/'agent_b_formal/runtime']:
 check('archive_shared_lock_'+root.name,'with locked(GLOBAL_MAIN_RESTORE_WINDOW_LOCK)'in(root/'ep_perf_archive.py').read_text());check('common_global_lock_'+root.name,str(r.LOCKS/'ARCHIVE_SHARED_WINDOW.lock')in(root/'ep_perf_common_v2.py').read_text())
# Same flock primitive tested on private fixture only.
with tempfile.TemporaryDirectory(dir=D,prefix='CPU_PRIVATE_LOCK_')as t:
 lock=P(t)/'lock';lock.touch()
 with lock.open('rb')as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  code='import fcntl,sys;f=open(sys.argv[1],'+chr(34)+'rb'+chr(34)+');'+chr(10)+'try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'+chr(10)+'except BlockingIOError: sys.exit(7)'
  run=subprocess.run(['python3','-c',code,str(lock)],capture_output=True)
  check('private_same_path_restore_mutex_blocks_second_actor',run.returncode==7)
(D/'CPU_RESOURCE_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS',qualified_global_EP_caps=[2,10],total=len(checks),passed=len(checks),checks=checks,new_scientific_starts=0,no_shared_ledger_native_writes=True,actual_snapshot=s),indent=2)+chr(10));print(json.dumps(dict(status='PASS',checks=len(checks),caps=[2,10])))
