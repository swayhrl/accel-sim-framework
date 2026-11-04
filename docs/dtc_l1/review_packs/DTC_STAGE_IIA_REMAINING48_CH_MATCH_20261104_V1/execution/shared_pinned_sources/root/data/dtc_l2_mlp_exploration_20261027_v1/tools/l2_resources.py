"""Resource admission helpers. No launch, registry mutation, process signalling or controller.
Only the coordinating owner serializes claims and assigns a CPU before registration.
Memory pressure pauses new admission; it does not terminate a healthy consumed model.
"""
import os,json,pathlib,hashlib,datetime,importlib.util,math,time
_TOPOLOGY_CACHE={}
P=pathlib.Path;G=1024**3;M=1024**2
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
PEER=P('/root/data/dtc_failure_repair_20261025_v1/ops/revision20/resource_accounting_v1.py')
PEER_SHA='e9c864c109ea4e87521713246e5a1602d95da5413861cc7f34be100180ee866e'
DEFAULT_POLICY=dict(schema='L2_MLP_DYNAMIC_ADMISSION_POLICY_V1',memory_utilization_fraction=.88,
 min_host_headroom_bytes=8*G,min_cgroup_headroom_bytes=8*G,minimum_prediction_bytes=768*M,
 history_multiplier=1.20,history_additive_bytes=256*M,hard_limit_multiplier=1.5,hard_limit_additive_bytes=G,
 candidate_l2_metadata_margin_bytes=128*M,memory_psi_some_avg10_pause=2.,memory_psi_full_avg10_pause=.5,
 io_psi_full_avg10_pause=30.,swap_out_bytes_per_second_pause=64*M,oom_event_increase_pause=True,
 native_safety_floor_bytes=5*G,min_free_inodes=100000,metadata_reserve_bytes=G,
 minimum_unobserved_bytes=768*M,owner_cpu_margin=4,long_job_interval=3,resource_sample_max_age_seconds=5,admission_resource_sample_max_age_seconds=2,cpu_utilization_quota_pause_fraction=.90,cpu_pressure_full_avg10_pause=10.,cpu_throttled_period_fraction_pause=.20,cpu_throttled_walltime_fraction_pause=.10)

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def _kv(p):
 try:return {a:int(b)for a,b in(x.split()for x in P(p).read_text().splitlines())}
 except(OSError,ValueError):return {}

def _pressure(p):
 out={}
 try:
  for row in P(p).read_text().splitlines():
   words=row.split();out[words[0]]={k:float(v)for k,v in(w.split('=')for w in words[1:])}
 except(OSError,ValueError):pass
 return out

def sample_system():
 import time
 c=P('/sys/fs/cgroup');mem={x.split(':')[0]:int(x.split()[1])*1024 for x in P('/proc/meminfo').read_text().splitlines()if ':'in x and x.split()[1].isdigit()};maximum=(c/'memory.max').read_text().strip();current=int((c/'memory.current').read_text());stat=_kv(c/'memory.stat');clean=max(0,stat.get('file',0)-sum(stat.get(k,0)for k in ['shmem','file_mapped','file_dirty','file_writeback']));credit=max(0,min(stat.get('inactive_file',0),clean)-2*G);eff=None if maximum=='max'else max(0,int(maximum)-current+credit);quota=(c/'cpu.max').read_text().split();v=os.statvfs(R if R.exists()else'/root/data')
 boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip();allowed=tuple(sorted(os.sched_getaffinity(0)));topology_key=(boot_id,allowed)
 if topology_key not in _TOPOLOGY_CACHE:
  topology=[]
  for cpu in allowed:
   base=P('/sys/devices/system/cpu')/('cpu'+str(cpu));nodes=list(base.glob('node[0-9]*'))
   topology.append(dict(cpu=cpu,node=int(nodes[0].name[4:])if nodes else 0,core=int((base/'topology/core_id').read_text()),socket=int((base/'topology/physical_package_id').read_text())))
  _TOPOLOGY_CACHE.clear();_TOPOLOGY_CACHE[topology_key]=topology
 topology=_TOPOLOGY_CACHE[topology_key]
 busy=[];foreign=[]
 for d in P('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   cmd=(d/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');aff=sorted(os.sched_getaffinity(int(d.name)))
   if len(aff)==1:foreign.append(dict(pid=int(d.name),cpus=aff,cmdline=cmd))
   if 'accel-sim.out'in cmd and'-trace'in cmd and'/tools/bin/strace'not in cmd:
    st=(d/'stat').read_text().rsplit(')',1)[1].split();pid=int(d.name);aff=sorted(os.sched_getaffinity(pid))
    # Strace command lines also name the executable; only the actual pinned model is a CPU claimant.
    if len(aff)==1:busy.append(dict(pid=pid,start_ticks=int(st[19]),cpus=aff,RSS_bytes=int(st[21])*os.sysconf('SC_PAGE_SIZE'),cmdline=cmd))
  except(OSError,ValueError,ProcessLookupError):pass
 vm=_kv('/proc/vmstat');events=_kv(c/'memory.events');ticks={}
 for row in P('/proc/stat').read_text().splitlines():
  words=row.split()
  if words and words[0].startswith('cpu')and words[0]!='cpu':ticks[int(words[0][3:])]=[int(x)for x in words[1:]]
 return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=time.monotonic(),boot_id=boot_id,host_MemAvailable_bytes=mem['MemAvailable'],host_MemTotal_bytes=mem['MemTotal'],host_swap_used_bytes=mem.get('SwapTotal',0)-mem.get('SwapFree',0),host_pswpout_pages=vm.get('pswpout',0),host_oom_kill_count=vm.get('oom_kill',0),cgroup_memory_max=maximum,cgroup_memory_current=current,cgroup_reclaimable_clean_inactive_file_credit_bytes=credit,cgroup_effective_headroom_bytes=eff,cgroup_memory_events=events,cgroup_cpu_stat=_kv(c/'cpu.stat'),cpu_pressure=_pressure(c/'cpu.pressure'),memory_pressure=_pressure(c/'memory.pressure'),io_pressure=_pressure(c/'io.pressure'),cpu_quota_equivalent=None if quota[0]=='max'else int(quota[0])/int(quota[1]),cpu_allowed=sorted(os.sched_getaffinity(0)),cpu_topology=topology,cpu_ticks=ticks,observed_models=busy,observed_affinity_claims=foreign,native_free_bytes=v.f_bavail*v.f_frsize,free_inodes=v.f_favail,page_size=os.sysconf('SC_PAGE_SIZE'))

def forecast(spec,history,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));rows=history.get('records',history)if isinstance(history,dict)else history;key=spec.get('workload');all_rows=[x for x in rows if x.get('workload')==key and isinstance(x.get('rss'),int)and x['rss']>0];same_success=[x for x in all_rows if spec.get('core_commit')and x.get('core_commit')==spec['core_commit']and x.get('success')];rows=same_success or all_rows;peak=max([x['rss']for x in rows]+[0]);valid=[x for x in rows if x.get('success')];elapsed=max([x.get('elapsed',0)or 0 for x in valid]+[0]);incomplete=bool(rows)and not valid
 if not rows:peak=spec.get('estimated_peak_model_RAM_bytes',p['minimum_unobserved_bytes'])
 predicted=max(p['minimum_prediction_bytes'],math.ceil(peak*p['history_multiplier'])+p['history_additive_bytes'])+p['candidate_l2_metadata_margin_bytes']
 # Failed/truncated history supplies a lower bound, never a reason to exclude the input.
 if incomplete:predicted=math.ceil(predicted*1.25)
 hard=math.ceil(predicted*p['hard_limit_multiplier'])+p['hard_limit_additive_bytes']
 return dict(workload=key,predicted_peak_RAM_bytes=predicted,proposed_process_tree_rss_cap_bytes=hard,history_records=len(rows),all_history_records=len(all_rows),history_selection='SAME_CORE_SUCCESSFUL_RECEIPTS'if same_success else'CONSERVATIVE_ALL_HISTORY_FALLBACK',all_history_peak_bytes=max([x['rss']for x in all_rows]+[0]),omitted_failed_or_other_core_records=len(all_rows)-len(rows),historical_peak_bytes=peak,historical_elapsed_seconds=elapsed,failed_only_lower_bound=incomplete,history_source='actual receipt peaks; successes and negatives preserved',resource_class='LARGE'if predicted>=16*G else'MEDIUM'if predicted>=4*G else'SMALL')

def pressure_reasons(s,previous=None,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));out=[]
 for field,kind,limit in [('cpu_pressure','full',p['cpu_pressure_full_avg10_pause']),('memory_pressure','some',p['memory_psi_some_avg10_pause']),('memory_pressure','full',p['memory_psi_full_avg10_pause']),('io_pressure','full',p['io_psi_full_avg10_pause'])]:
  if s.get(field,{}).get(kind,{}).get('avg10',0)>limit:out.append(field+'_'+kind)
 if previous:
  seconds=s['monotonic']-previous.get('monotonic',s['monotonic'])
  if seconds>0 and max(0,s.get('host_pswpout_pages',0)-previous.get('host_pswpout_pages',0))*s.get('page_size',4096)/seconds>p['swap_out_bytes_per_second_pause']:out.append('ACTIVE_SWAP_OUT')
  oldcpu=previous.get('cgroup_cpu_stat',{});newcpu=s.get('cgroup_cpu_stat',{});quota=s.get('cpu_quota_equivalent')
  if seconds>=.5 and oldcpu and newcpu:
   used=max(0,newcpu.get('usage_usec',0)-oldcpu.get('usage_usec',0))/(seconds*1e6)
   if quota and used>=quota*p['cpu_utilization_quota_pause_fraction']:out.append('CGROUP_CPU_USAGE_NEAR_QUOTA')
   periods=max(0,newcpu.get('nr_periods',0)-oldcpu.get('nr_periods',0));throttled=max(0,newcpu.get('nr_throttled',0)-oldcpu.get('nr_throttled',0));duration=max(0,newcpu.get('throttled_usec',0)-oldcpu.get('throttled_usec',0))/(seconds*1e6)
   if throttled>=3 and periods>0 and throttled/periods>=p['cpu_throttled_period_fraction_pause']and duration>=p['cpu_throttled_walltime_fraction_pause']:out.append('CGROUP_CPU_THROTTLING')
  old=previous.get('cgroup_memory_events',{});now=s.get('cgroup_memory_events',{})
  if p['oom_event_increase_pause']and any(now.get(k,0)>old.get(k,0)for k in ['oom','oom_kill','max']):out.append('CGROUP_LIMIT_OR_OOM_INCREASE')
 return out

def memory_admission(sample,additional_bytes,previous=None,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));host=max(0,sample['host_MemAvailable_bytes']-p['min_host_headroom_bytes']);cg=sample.get('cgroup_effective_headroom_bytes');cg=max(0,cg-p['min_cgroup_headroom_bytes'])if cg is not None else host;usable=min(host,cg);budget=int(usable*p['memory_utilization_fraction']);reasons=pressure_reasons(sample,previous,p)
 return dict(pass_admission=not reasons and additional_bytes<=budget,additional_reserved_RAM_bytes=additional_bytes,admission_RAM_budget_bytes=budget,pressure_reasons=reasons,pressure_pause_new=bool(reasons),memory_utilization_fraction=p['memory_utilization_fraction'],effective_usable_bytes=usable)

def cpu_candidates(sample,claims=None,previous=None):
 occupied={c for row in sample.get('observed_affinity_claims',sample.get('observed_models',[]))for c in row['cpus']};occupied|={v['host_cpu']for v in(claims or {}).values()};top={x['cpu']:x for x in sample['cpu_topology']};cores={(top[c]['socket'],top[c]['core'])for c in occupied if c in top};busy={}
 if previous:
  for c,now in sample.get('cpu_ticks',{}).items():
   old=previous.get('cpu_ticks',{}).get(c,previous.get('cpu_ticks',{}).get(str(c)))
   if old:
    delta=[a-b for a,b in zip(now,old)];total=sum(delta);busy[c]=(total-delta[3]-(delta[4]if len(delta)>4 else 0))/total if total>0 else 0
 counts={}
 for c in occupied:
  if c in top:counts[top[c]['node']]=counts.get(top[c]['node'],0)+1
 choices=[]
 for c in sample['cpu_allowed']:
  if c in occupied:continue
  t=top[c];choices.append((int((t['socket'],t['core'])in cores),busy.get(c,0),counts.get(t['node'],0),c))
 return [x[-1]for x in sorted(choices)]

def choose_dispatch(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
 """Select one fit candidate. Re-sample and serialize a claim before choosing another."""
 p=dict(DEFAULT_POLICY,**(policy or {}));cpus=cpu_candidates(sample,claims,previous);quota=sample.get('cpu_quota_equivalent')or len(sample['cpu_allowed']);n=len(sample.get('observed_models',[]))+sum(1 for x in claims.values()if not x.get('observed_model'))
 if not cpus or n>=max(1,int(quota)-p['owner_cpu_margin']):return None
 rows=[]
 for spec in pending:
  f=forecast(spec,history,p);cost=f['predicted_peak_RAM_bytes'];extra=sum(x.get('additional_reserved_bytes',max(0,x.get('predicted_peak_RAM_bytes',0)-next((v['RSS_bytes']for v in sample.get('observed_models',[])if x['host_cpu']in v['cpus']),0)))for x in claims.values())+cost;decision=memory_admission(sample,extra,previous,p)
  if decision['pass_admission']:rows.append((spec,f,decision))
 if not rows:return None
 # One long/large job every three admissions; other slots favor short jobs. All remain eligible.
 long_turn=dispatch_index%p['long_job_interval']==0
 active_counts={}
 for value in claims.values():
  key=value.get('workload');active_counts[key]=active_counts.get(key,0)+1
 rows.sort(key=lambda x:(active_counts.get(x[0].get('workload'),0),-x[1]['historical_elapsed_seconds']if long_turn else x[1]['historical_elapsed_seconds'],x[1]['predicted_peak_RAM_bytes'],x[0]['cohort']))
 spec,f,decision=rows[0];return dict(cohort=spec['cohort'],host_cpu=cpus[0],forecast=f,admission=decision)

def validated_observer_sample(observer,boot_id,now,max_age_seconds):
 if not isinstance(observer,dict)or observer.get('boot_id')!=boot_id:return None
 age=now-observer.get('monotonic',float('-inf'))
 if not 0<=age<=max_age_seconds:return None
 required=['host_MemAvailable_bytes','cgroup_effective_headroom_bytes','native_free_bytes','free_inodes','observed_models','cpu_topology','cpu_allowed','cgroup_cpu_stat','cpu_pressure']
 if any(k not in observer for k in required):return None
 return dict(observer,resource_observer_cache_used=True,resource_observer_sample_age_seconds=age)

def resource_sample(fresh_source=False,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip();path=R/'control/RESOURCE_OBSERVER.json';observer=None;observer_sha=None
 try:
  raw=path.read_bytes();observer=json.loads(raw);observer_sha=hashlib.sha256(raw).hexdigest()
 except(OSError,ValueError):pass
 limit=p['admission_resource_sample_max_age_seconds']if fresh_source else p['resource_sample_max_age_seconds'];cached=validated_observer_sample(observer,boot_id,time.monotonic(),limit)
 if cached is not None:return dict(cached,resource_observer_sha256=observer_sha)
 return dict(sample_system(),resource_observer_cache_used=False,resource_observer_sample_age_seconds=0,resource_observer_sha256=observer_sha)

HEAVY_SAMPLE_FIELDS={'cpu_topology','cpu_ticks','observed_models','observed_affinity_claims','previous_sample','cpu_allowed'}
HEAVY_PEER_FIELDS={'RAM_reservation_entries','write_entries_by_request','claim_snapshots','certified_departed_generation_entries','uncertain_ghosts_retained'}
def lightweight_resource_receipt(peer,sample,ram,writes,cohort,fresh_source=False):
 light={k:v for k,v in sample.items()if k not in HEAVY_SAMPLE_FIELDS};light.update(cpu_allowed_count=len(sample.get('cpu_allowed',[])),observed_model_count=len(sample.get('observed_models',[])),observed_affinity_claim_count=len(sample.get('observed_affinity_claims',[])))
 selected_ram=ram if fresh_source else[x for x in ram if x.get('cohort')==cohort];selected_writes=writes if fresh_source else[x for x in writes if x.get('cohort')==cohort]
 base=dict(peer)if fresh_source else{k:v for k,v in peer.items()if k not in HEAVY_PEER_FIELDS}
 return dict(base,**light,own_ram_forecasts=selected_ram,own_write_entries=selected_writes,own_ram_forecast_count=len(ram),own_write_entry_count=len(writes),own_forecast_additional_RAM_bytes=sum(x.get('additional_reserved_bytes',0)for x in ram),own_write_entry_total_bytes=sum(x.get('additional_write_restore_bytes',0)for x in writes),resource_receipt_lists_scope='ALL_ON_PREPARE'if fresh_source else'CURRENT_COHORT_ONLY')

def resources(spec,fresh_source=False):
 """Compatible original-native resource fields with independent new admission policy."""
 policy=read(R/'control/RESOURCE_POLICY.json');p=dict(DEFAULT_POLICY,**policy);assert p['schema']=='L2_MLP_DYNAMIC_ADMISSION_POLICY_V1';assert sha(PEER)==PEER_SHA
 old=load('l2_readonly_peers',PEER);b=old.resources({'request':old.ORIG,'cohort':'L2_MLP_RESOURCE_METADATA'},False);reg,_=old.authority();q=reg['registered_future_requests'][REQ];claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];s=resource_sample(fresh_source,p);prevpath=R/'control/RESOURCE_OBSERVER.json';previous=s.get('previous_sample')or(read(prevpath)if prevpath.exists()else None);ram=[];writes=[];own=p['metadata_reserve_bytes']
 for c,row in q['consumed'].items():
  if (R/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists():continue
  sp=read(R/'control/specs'/(c+'.json'));assert sha(R/'control/specs'/(c+'.json'))==q['admitted_specs'][c];out=R/'DTC/run/results'/row['uuid'];size=old.size(out);closed=bool(row.get('execution_receipt'));need=size+16*M if closed else max(0,2*sp['limits']['max_result_directory_bytes']-size);own+=need;writes.append(dict(cohort=c,additional_write_restore_bytes=need))
  if not closed:
   rss,live=old.rss(R,row);estimate=sp['estimated_peak_model_RAM_bytes'];envelope=min(sp['limits']['max_process_tree_rss_bytes'],max(estimate,math.ceil(rss*1.10)));ram.append(dict(cohort=c,RSS_bytes=rss,additional_reserved_bytes=max(0,envelope-rss),kind='LIVE_MODEL'if live else'SPENT_UNRESOLVED_GENERATION'))
 candidates=set(claims)-set(q['consumed'])
 if fresh_source and spec['cohort']not in q['consumed']:candidates.add(spec['cohort'])
 for c in candidates:
  sp=read(R/'control/specs'/(c+'.json'));assert sha(R/'control/specs'/(c+'.json'))==q['admitted_specs'][c];own+=2*sp['limits']['max_result_directory_bytes'];ram.append(dict(cohort=c,RSS_bytes=0,additional_reserved_bytes=sp['estimated_peak_model_RAM_bytes'],kind='CLAIM_OR_CANDIDATE'))
 total=b['reserved_additional_live_and_candidate_RAM_bytes']+sum(x['additional_reserved_bytes']for x in ram);decision=memory_admission(s,total,previous,p);mine=sum(x['reserved_write_bytes']for x in b['peer_reservations']if x['request']==REQ);required=b['required_free_bytes']-mine+own;bound=own<=q['reserved_write_bytes'];runtime_not_kill=not fresh_source
 return dict(lightweight_resource_receipt(b,s,ram,writes,spec['cohort'],fresh_source),schema='L2_MLP_DYNAMIC_WORKINGSET_RESOURCE_V1',source_module_sha256=sha(__file__),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),own_remaining_write_and_restore_bytes=own,own_write_ceiling_pass=bound,total_projected_additional_RAM_bytes=total,reserved_additional_live_and_candidate_RAM_bytes=total,required_free_bytes=required,admission_decision=decision,pressure_pause_new=decision['pressure_pause_new'],physical_RAM_pass=runtime_not_kill or decision['pass_admission'],host_floor_bytes=p['min_host_headroom_bytes'],cgroup_floor_bytes=p['min_cgroup_headroom_bytes'],physical_disk_pass=all(b['per_scope_write_ceiling_pass'].values())and bound and s['native_free_bytes']>required and s['free_inodes']>=p['min_free_inodes'],runtime_pressure_does_not_terminate_healthy_model=True)
