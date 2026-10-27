"""CPU-only chooser integration against real resource arithmetic; no production."""
import pathlib,importlib.util,json,hashlib,copy,sys
P=pathlib.Path;B=P(__file__).parent
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('original_resource',B/'l2_resources.py');a=load('consistent_admission',B/'l2_consistent_admission_amendment_v1.py');G=m.G;checks=[]
def ck(n,v):assert v,n;checks.append(n)
sample=dict(monotonic=10,host_MemAvailable_bytes=100*G,cgroup_effective_headroom_bytes=100*G,cpu_allowed=list(range(32)),cpu_quota_equivalent=32,cpu_topology=[dict(cpu=x,socket=0,node=x//16,core=x)for x in range(32)],observed_models=[],memory_pressure={},io_pressure={},cgroup_memory_events={})
history={'records':[dict(workload='small',rss=G,elapsed=1,success=True),dict(workload='large',rss=8*G,elapsed=1000,success=True)]}
points=[dict(cohort='large',workload='large',limits={'max_result_directory_bytes':64*m.M}),dict(cohort='small',workload='small',limits={'max_result_directory_bytes':64*m.M})]
base=dict(sample,physical_RAM_pass=True,physical_disk_pass=True,admission_decision={'pressure_reasons':[]},total_projected_additional_RAM_bytes=0,required_free_bytes=5*G,native_free_bytes=100*G,own_remaining_write_and_restore_bytes=G,own_reserved_write_ceiling_bytes=24*G)
count={'n':0}
def baseline():count['n']+=1;return copy.deepcopy(base)
def choose(claims=None,points_=None):return a.choose_consistent(m.choose_dispatch,m,points_ or points,sample,claims or {},history,None,{},0,baseline,4)
d=choose();ck('eligible_long_still_chosen',d['cohort']=='large');ck('provider_baseline_called_once',count['n']==1)
ck('global_model_cap_not_four',d['consistent_admission']['global_model_capacity_unchanged'])
claims={str(i):dict(host_cpu=i,predicted_peak_RAM_bytes=G,observed_model=False)for i in range(4)};ck('four_unobserved_claims_pauses_preexec_only',choose(claims)is None)
old=copy.deepcopy(sample);sample['observed_models']=[dict(cpus=[i],RSS_bytes=G)for i in range(4)];ck('observed_models_do_not_consume_launch_window',choose(claims)is not None);sample=old
base['total_projected_additional_RAM_bytes']=75*G;count['n']=0;d=choose();ck('nonfit_large_falls_back_smaller',d['cohort']=='small');ck('fallback_does_not_rescan_provider_per_candidate',count['n']==1)
ck('peer_and_live_margin_preserved',d['consistent_admission']['additional_reserved_RAM_bytes']>75*G)
base['total_projected_additional_RAM_bytes']=90*G;ck('no_memory_fit_deferred',choose()is None)
base['total_projected_additional_RAM_bytes']=0;base['physical_RAM_pass']=False;ck('baseline_ram_hold_stops_new_only',choose()is None);base['physical_RAM_pass']=True
base['native_free_bytes']=5*G;ck('disk_reservation_stays_strict',choose()is None);base['native_free_bytes']=100*G
base['admission_decision']['pressure_reasons']=['CGROUP_CPU_THROTTLING'];ck('pressure_stays_strict',choose()is None);base['admission_decision']['pressure_reasons']=[]
ck('original_function_unmodified',m.choose_dispatch.__name__=='choose_dispatch')
ck('pending_and_claims_unmodified',points[0]['cohort']=='large'and len(claims)==4)
large_canonical=dict(points[1],estimated_peak_model_RAM_bytes=200*G)
ck('old_binding_large_estimate_not_undercounted',choose(points_=[large_canonical])is None)
try:a.choose_consistent(m.choose_dispatch,m,points,sample,{},history,None,{},0,baseline,0)
except AssertionError:checks.append('nonpositive_inflight_window_rejected')
else:raise AssertionError('zero window accepted')
# Isolated live-thread frame installation and restoration. No parent attachment.
import threading,types,concurrent.futures
ready=threading.Event();stop=threading.Event();box={}
fake_res=types.SimpleNamespace(choose_dispatch=m.choose_dispatch,resources=lambda spec,fresh:copy.deepcopy(base),memory_admission=m.memory_admission)
fake_engine=types.SimpleNamespace(registered=lambda:(None,None,{'consumed':{'reference':{}},'reserved_write_bytes':24*G},None),canonical=lambda c:dict(cohort=c),__file__='fixture')
a.R=B/'CPU_CONSISTENT_OWNER_FIXTURE';(a.R/'tools').mkdir(parents=True,exist_ok=True);(a.R/'tools/l2_resources.py').write_bytes((B/'l2_resources.py').read_bytes());fake_res.__file__=str(a.R/'tools/l2_resources.py')
ns=dict(threading=threading,concurrent=concurrent,ready=ready,stop=stop,box=box,fake_res=fake_res,fake_engine=fake_engine)
code='def run_scheduler():\n res=fake_res;engine=fake_engine;max_workers=384;claims={};running={};pool=concurrent.futures.ThreadPoolExecutor(max_workers=384,thread_name_prefix="L2MLP");box["pool"]=pool;box["claims"]=claims;ready.set();stop.wait(5);pool.shutdown()\n'
exec(compile(code,str(a.R/'tools/l2_ops.py'),'exec'),ns)
t=threading.Thread(target=ns['run_scheduler'],name='DTC_L2_MLP_ONE_OWNER');t.start();assert ready.wait(5);sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD=t
try:
 original=fake_res.choose_dispatch
 try:a.install_on_existing_thread(t,4,'bad-resource-pin')
 except AssertionError:checks.append('resource_source_identity_mismatch_rejected')
 else:raise AssertionError('bad resource SHA accepted')
 proof=a.install_on_existing_thread(t,4,hashlib.sha256(P(fake_res.__file__).read_bytes()).hexdigest());ck('isolated_owner_wrapper_installed',fake_res.choose_dispatch is not original)
 ck('existing_executor_capacity_384_unchanged',proof['global_model_capacity']==384 and box['pool']._max_workers==384)
 ck('claims_semantics_not_mutated',box['claims']=={})
 r=a.restore_in_owner();ck('original_chooser_restored_without_restart',fake_res.choose_dispatch is original and r['claims_running_and_models_untouched'])
finally:stop.set();t.join(5)
result=dict(status='PASS',checks=checks,passed=len(checks),production_owner_attached=False,simulator_starts=0,source_sha256=hashlib.sha256((B/'l2_consistent_admission_amendment_v1.py').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),original_resource_sha256=hashlib.sha256((B/'l2_resources.py').read_bytes()).hexdigest())
(B/'CONSISTENT_ADMISSION_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
