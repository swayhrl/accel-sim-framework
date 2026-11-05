# DRAFT new R1 private resources; never imported by prior requests.
"""Performance-first V2 exact16 physical x PIB resource admission. Read-only authority/files; no dispatch or signals.
Runtime pressure pauses new admission. Hard native floor/inode/actual-own write
contract remain unsafe. Archive callers MUST use admission_disk_pass.
"""
import pathlib,json,hashlib,importlib.util,os,math,time
P=pathlib.Path;G=1024**3;M=1024**2
V1_REMAINING28=P('/root/data/dtc_perf_first_remaining28_20261104_v1');V1_REMAINING28_REQ='DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1'
OLD_NEGATIVE16=P('/root/data/dtc_perf_first_v2_codesign16_20261105_v1');OLD_NEGATIVE16_REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
R=P('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');REQ='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1'
FIRST4=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1');FIRST4_REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'
REMAINING48=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');REMAINING48_REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
FIRST16=P('/root/data/dtc_stage_iia_first16_20261104_v1');FIRST16_REQ='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'
ARCHIVE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1')
PROTECTED_CPUS=set([2,258])|set(range(32,64))|set(range(288,320))
STAGE1_REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';STAGE1=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
PEER=P('/root/data/dtc_failure_repair_20261025_v1/ops/revision20/resource_accounting_v1.py');PEER_SHA='e9c864c109ea4e87521713246e5a1602d95da5413861cc7f34be100180ee866e'
PURE=STAGE1/'tools/l2_resources.py';PURE_SHA='6ad97e35de88ff5876bc0af674324f979f35c211f31d182976d2f66abb9c4854'
SCHEMA='DTC_PERFV2_CODESIGN16_LAYOUT_R1_DYNAMIC_RESOURCE_POLICY_V1';_PURE=None;_PEER=None;_JOIN={};_LAST_SAMPLE=None;_PEAK_RSS={};_RECENT_INPUT_PEAKS={};_LAST_PRECLAIM_HOLDS=[]
DEFAULT_POLICY=dict(schema=SCHEMA,memory_utilization_fraction=.88,min_host_headroom_bytes=8*G,min_cgroup_headroom_bytes=8*G,native_safety_floor_bytes=5*G,metadata_reserve_bytes=256*M,min_free_inodes=100000,stage1_metadata_reserve_bytes=G)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def _load(name,path):
 m=__import__('types').ModuleType(name);m.__file__=str(path);exec(compile(P(path).read_bytes(),str(path),'exec'),m.__dict__);return m
def _pure():
 global _PURE
 assert sha(PURE)==PURE_SHA,'PURE_RESOURCE_SOURCE_DRIFT'
 if _PURE is None:
  _PURE=_load('perf16r1_private_pure_resource',PURE);_PURE.R=R;_PURE.REQ=REQ
  _PURE.DEFAULT_POLICY.update(DEFAULT_POLICY);_PURE.pressure_reasons=pressure_reasons;_PURE.forecast=forecast
 return _PURE
def _peer():
 global _PEER
 assert sha(PEER)==PEER_SHA,'PEER_RESOURCE_SOURCE_DRIFT'
 if _PEER is None:
  _PEER=_load('perf16r1_readonly_r20_peer',PEER);_PEER.authority=bounded_authority
 return _PEER
def policy(value=None):
 p=dict(_pure().DEFAULT_POLICY);p.update(DEFAULT_POLICY);p.update(value or {})
 assert p['schema']==SCHEMA and .85<=p['memory_utilization_fraction']<=.90
 assert p['native_safety_floor_bytes']>=5*G and p['metadata_reserve_bytes']>=0
 assert p['min_host_headroom_bytes']>=8*G and p['min_cgroup_headroom_bytes']>=8*G
 return p
def _base_sample_system():
 s=_pure().sample_system()
 for name in ['memory','cpu','io']:s['host_'+name+'_pressure']=_pure()._pressure('/proc/pressure/'+name)
 try:s['cgroup_swap_current_bytes']=int(P('/sys/fs/cgroup/memory.swap.current').read_text())
 except (OSError,ValueError):s['cgroup_swap_current_bytes']=None
 try:
  v=os.statvfs(ARCHIVE);s['archive_free_bytes']=v.f_bavail*v.f_frsize;mount=json.loads(__import__('subprocess').check_output(['findmnt','-J','-T',str(ARCHIVE)],text=True))['filesystems'][0];s['true164_mount_verified']=mount['fstype']=='fuse.sshfs'and mount['source']=='admin-wcx@10.208.130.164:/home/shared'
 except (OSError,ValueError,KeyError,__import__('subprocess').SubprocessError):s['archive_free_bytes']=0;s['true164_mount_verified']=False
 return s
def pressure_reasons(s,previous=None,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));out=[]
 if s['host_MemAvailable_bytes']<p['min_host_headroom_bytes']:out.append('HOST_HEADROOM_LT_FLOOR')
 cg=s.get('cgroup_effective_headroom_bytes')
 if cg is not None and cg<p['min_cgroup_headroom_bytes']:out.append('CGROUP_HEADROOM_LT_FLOOR')
 # Original pure pressure implementation copied privately, never source rewritten.
 for field,kind,key in [('cpu_pressure','full','cpu_pressure_full_avg10_pause'),('memory_pressure','some','memory_psi_some_avg10_pause'),('memory_pressure','full','memory_psi_full_avg10_pause'),('io_pressure','full','io_psi_full_avg10_pause')]:
  default={'cpu_pressure_full_avg10_pause':10.,'memory_psi_some_avg10_pause':2.,'memory_psi_full_avg10_pause':.5,'io_psi_full_avg10_pause':30.}[key]
  if s.get(field,{}).get(kind,{}).get('avg10',0)>p.get(key,default):out.append(field+'_'+kind)
 for field,kind,key,default in [('host_memory_pressure','some','host_memory_psi_some_avg10_pause',2.),('host_memory_pressure','full','host_memory_psi_full_avg10_pause',.5),('host_cpu_pressure','full','host_cpu_psi_full_avg10_pause',10.),('host_io_pressure','full','host_io_psi_full_avg10_pause',30.)]:
  if s.get(field,{}).get(kind,{}).get('avg10',0)>p.get(key,default):out.append(field+'_'+kind)
 if previous:
  seconds=s['monotonic']-previous.get('monotonic',s['monotonic'])
  if seconds>0 and max(0,s.get('host_pswpout_pages',0)-previous.get('host_pswpout_pages',0))*s.get('page_size',4096)/seconds>p.get('swap_out_bytes_per_second_pause',64*M):out.append('ACTIVE_SWAP_OUT')
  if s.get('host_oom_kill_count',0)>previous.get('host_oom_kill_count',0):out.append('HOST_OOM_KILL_INCREASE')
  before_swap=previous.get('cgroup_swap_current_bytes');after_swap=s.get('cgroup_swap_current_bytes')
  if seconds>0 and isinstance(before_swap,int)and isinstance(after_swap,int)and max(0,after_swap-before_swap)/seconds>p.get('cgroup_swap_growth_bytes_per_second_pause',64*M):out.append('CGROUP_ACTIVE_SWAP_GROWTH')
  old=previous.get('cgroup_memory_events',{});now=s.get('cgroup_memory_events',{})
  if p.get('oom_event_increase_pause',True)and any(now.get(k,0)>old.get(k,0)for k in ['oom','oom_kill','max']):out.append('CGROUP_LIMIT_OR_OOM_INCREASE')
  a=previous.get('cgroup_cpu_stat',{});b=s.get('cgroup_cpu_stat',{});quota=s.get('cpu_quota_equivalent')
  if seconds>=.5 and a and b:
   used=max(0,b.get('usage_usec',0)-a.get('usage_usec',0))/(seconds*1e6)
   if quota and used>=quota*p.get('cpu_utilization_quota_pause_fraction',.9):out.append('CGROUP_CPU_USAGE_NEAR_QUOTA')
   periods=max(0,b.get('nr_periods',0)-a.get('nr_periods',0));n=max(0,b.get('nr_throttled',0)-a.get('nr_throttled',0));duration=max(0,b.get('throttled_usec',0)-a.get('throttled_usec',0))/(seconds*1e6)
   if n>=3 and periods and n/periods>=p.get('cpu_throttled_period_fraction_pause',.2)and duration>=p.get('cpu_throttled_walltime_fraction_pause',.1):out.append('CGROUP_CPU_THROTTLING')
 return out
def forecast(spec,history=None,policy=None):
 # Registered exact input prediction is authoritative; historical failures remain evidence.
 estimate=spec['estimated_peak_model_RAM_bytes'];assert type(estimate)is int and estimate>0
 hard=spec['limits']['max_process_tree_rss_bytes'];assert hard>=estimate
 rows=history.get('records',history)if isinstance(history,dict)else(history or []);key=spec.get('workload',spec.get('input_digest'));elapsed=spec.get('historical_elapsed_seconds')or max([x.get('elapsed',x.get('elapsed_seconds',0))or 0 for x in rows if x.get('workload',x.get('input_digest'))==key and x.get('success',x.get('accepted',False))]+[0])
 recent=_RECENT_INPUT_PEAKS.get(key,0);estimate=max(estimate,math.ceil(recent*1.20)+384*M if recent else 0);assert estimate<=hard,'REGISTERED_RSS_LIMIT_BELOW_DYNAMIC_FORECAST'
 return dict(workload=key,predicted_peak_RAM_bytes=estimate,proposed_process_tree_rss_cap_bytes=hard,historical_elapsed_seconds=elapsed,history_source='NEW_REGISTERED_PREDICTION_PLUS_OBSERVED_SAME_INPUT_PEAK' ,resource_class='MEDIUM'if estimate>=4*G else'SMALL')
def choose_dispatch(pending,sample,claims,history=None,previous=None,policy=None,dispatch_index=0):
 """Same owner calls before each serialized claim. Try other fitting IDs if disk-limited."""
 global _LAST_PRECLAIM_HOLDS
 p=globals()['policy'](policy);remaining=list(pending);_LAST_PRECLAIM_HOLDS=[]
 while remaining:
  d=_pure().choose_dispatch(remaining,sample,claims,history or [],previous,p,dispatch_index)
  if d is None:return None
  spec=next(s for s in remaining if s['cohort']==d['cohort']);v=resources(spec,True)
  if v['physical_RAM_pass']and v['admission_disk_pass']:
   return dict(d,preclaim_resource_gate=dict(required_free_bytes=v['required_free_bytes'],native_free_bytes=v['native_free_bytes'],admission_disk_pass=True,physical_RAM_pass=True))
  _LAST_PRECLAIM_HOLDS.append(dict(cohort=spec['cohort'],required_free_bytes=v['required_free_bytes'],native_free_bytes=v['native_free_bytes'],admission_disk_pass=v['admission_disk_pass'],physical_RAM_pass=v['physical_RAM_pass'],pressure_reasons=v['admission_decision']['pressure_reasons']))
  if v['admission_decision']['pressure_reasons']:return None
  remaining=[s for s in remaining if s['cohort']!=spec['cohort']]
 return None
def preclaim_diagnostics():return list(_LAST_PRECLAIM_HOLDS)
def _fingerprint(p):
 try:
  t=P(p).stat();return (t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns)
 except FileNotFoundError:return None
def _archived(peer,root,c,row):
 out=root/'DTC/run/results'/row['uuid'];paths=[root/'control'/(c+'_ARCHIVE_RECEIPT.json'),root/'control/qualification_ledger'/(c+'.INTENT.json'),root/'control/qualification_ledger'/(c+'.DONE.json'),out/'NATIVE_EXIT.json']
 key=(str(root),c,json.dumps(row,sort_keys=True),tuple(_fingerprint(p)for p in paths));old=_JOIN.get((str(root),c))
 if old and old[0]==key:return old[1]
 yes=peer.archived(root,c,row);_JOIN[(str(root),c)]=(key,yes);return yes

def _dynamic(peer,root,q,claims,metadata,spec=None,fresh=False):
 """Same exact-DONE/archive join as pinned R20. Unknown consumed stays bounded."""
 writes=metadata;actual=metadata;ram=[];wr=[];verified=0;pending=set(claims)-set(q['consumed'])
 if fresh and spec and spec['cohort']not in q['consumed']:pending.add(spec['cohort'])
 for c,row in q['consumed'].items():
  used,live=peer.rss(root,row)
  if _archived(peer,root,c,row)and not live:verified+=1;continue
  sp=read(root/'control/specs'/(c+'.json'));assert sha(root/'control/specs'/(c+'.json'))==q['admitted_specs'][c],'SPEC_RESOURCE_PIN_DRIFT'
  size=peer.size(root/'DTC/run/results'/row['uuid']);actual+=size;done=bool(row.get('execution_receipt'))
  need=size+16*M if done and not live else max(0,2*sp['limits']['max_result_directory_bytes']-size)
  writes+=need;wr.append(dict(cohort=c,uuid=row['uuid'],observed_result_bytes=size,additional_write_restore_bytes=need,execution_receipt=done,observed_model_live=live,archive_join=_archived(peer,root,c,row)))
  if live or not done:
   hard=sp['limits']['max_process_tree_rss_bytes'];estimate=sp['estimated_peak_model_RAM_bytes'];peak=used
   if root==R:
    ident=(c,row['uuid']);_PEAK_RSS[ident]=max(_PEAK_RSS.get(ident,0),used);peak=_PEAK_RSS[ident];key=sp.get('workload',sp['input_digest']);_RECENT_INPUT_PEAKS[key]=max(_RECENT_INPUT_PEAKS.get(key,0),peak)
   envelope=min(hard,max(estimate,math.ceil(peak*1.20)+384*M));ram.append(dict(cohort=c,RSS_bytes=used,additional_reserved_bytes=max(0,envelope-used),kind='LIVE_MODEL'if live else'SPENT_UNRESOLVED_GENERATION_RETAINED'))
 for c in sorted(pending):
  sp=read(root/'control/specs'/(c+'.json'));assert sha(root/'control/specs'/(c+'.json'))==q['admitted_specs'][c],'CANDIDATE_SPEC_DRIFT'
  if c in claims:assert claims[c]['result_cap_bytes']==sp['limits']['max_result_directory_bytes'],'CLAIM_OUTPUT_CAP_DRIFT'
  writes+=2*sp['limits']['max_result_directory_bytes'];ram.append(dict(cohort=c,RSS_bytes=0,additional_reserved_bytes=forecast(sp)['predicted_peak_RAM_bytes']if root==R else sp['estimated_peak_model_RAM_bytes'],kind='CLAIM_OR_CANDIDATE'))
  wr.append(dict(cohort=c,additional_write_restore_bytes=2*sp['limits']['max_result_directory_bytes'],claimed_or_candidate=True))
 return dict(projected_write_bytes=writes,actual_unarchived_output_bytes=actual,additional_RAM_bytes=sum(x['additional_reserved_bytes']for x in ram),ram=ram,writes=wr,exact_archived_nonlive_count=verified,registered_write_bytes=q['reserved_write_bytes'],projection_within_registered_ceiling=writes<=q['reserved_write_bytes'])


def _closed_first16(peer,reg):
 q=reg['registered_future_requests'][FIRST16_REQ];claims=peer.claims(FIRST16);d=_dynamic(peer,FIRST16,q,claims,256*M)
 exact=(q['budget']==len(q['consumed'])==16 and q['remaining']==0 and set(claims)<=set(q['consumed'])and d['exact_archived_nonlive_count']==16 and not d['writes'])
 if exact:
  d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_first16_zero_future_metadata=True,closed_join_basis='16exactDONE_EXIT_INTENT_registry_archive_joins_and_nonlive_generation;existing_files_remain_in_df')
 return d

def _closed_metadata_scope(peer,request,root,q,claims,write_bytes,write_entries):
 """Only a complete fresh read-only closed join releases the old 1GiB forecast.
 Existing files remain in df. No old registry/source/accounting is rewritten.
 """
 proof=dict(request=request,root=str(root),released_future_metadata_bytes=0,points={},reasons=[],q_canonical_sha256=hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),claims_canonical_sha256=hashlib.sha256(json.dumps(claims,sort_keys=True,separators=(',',':')).encode()).hexdigest(),registered_write_bytes_unchanged=q.get('reserved_write_bytes'))
 try:
  assert request in peer.ROOTS and peer.ROOTS[request]==root,'UNKNOWN_SCOPE'
  assert write_bytes==G and write_entries==[],'NOT_METADATA_ONLY_EXACT_1G'
  assert q['state']=='CLOSED' and q['remaining']==0 and type(q['budget'])is int and q['budget']>0 and len(q['consumed'])==q['budget'],'NOT_FULLY_CLOSED'
  assert set(claims)<=set(q['consumed']),'UNCONSUMED_CLAIM'
  for c,row in q['consumed'].items():
   paths=[root/'control/qualification_ledger'/(c+'.INTENT.json'),root/'control/qualification_ledger'/(c+'.DONE.json'),root/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json',root/'control'/(c+'_ARCHIVE_RECEIPT.json'),root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json']
   pins=[dict(path=str(x),sha256=sha(x))for x in paths]
   assert _archived(peer,root,c,row),'ARCHIVE_DONE_EXIT_INTENT_REGISTRY_JOIN_MISSING'
   pidmap=read(paths[-1]);assert type(pidmap['pid'])is int and type(pidmap['start_ticks'])is int,'PID_GENERATION_MISSING'
   used,live=peer.rss(root,row);assert not live,'LIVE_GENERATION'
   proof['points'][c]=dict(uuid=row['uuid'],intent_sha256=row['intent_sha256'],execution_receipt_sha256=hashlib.sha256(json.dumps(row['execution_receipt'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),pins=pins,observed_pid=pidmap['pid'],observed_start_ticks=pidmap['start_ticks'],observed_live=False,archive_join=True)
  proof['released_future_metadata_bytes']=G
 except(AssertionError,OSError,ValueError,KeyError,TypeError)as e:proof['reasons'].append(str(e))
 proof['existing_df_bytes_removed']=0;proof['old_registry_or_source_modified']=False
 return proof

def _closed_known_metadata(peer,reg,b):
 proofs={}
 for request,root in peer.ROOTS.items():
  # An unknown/missing/changed budget remains conservative in pinned base R20.
  if b['known_remaining_writes_by_request'].get(request)!=G:continue
  q=reg['registered_future_requests'].get(request,{})
  proofs[request]=_closed_metadata_scope(peer,request,root,q,peer.claims(root),b['known_remaining_writes_by_request'].get(request),b['write_entries_by_request'].get(request))
 return dict(schema='REMAINING48_PRIVATE_CLOSED_METADATA_FORWARD_PROJECTION_V1',peer_source_sha256=PEER_SHA,proofs=proofs,released_future_metadata_bytes=sum(x['released_future_metadata_bytes']for x in proofs.values()),existing_df_bytes_removed=0,old_registry_or_source_modified=False)

def _evaluate(spec,fresh,s,prev,b,peers,own,q,p):
 replaced={request:sum(x['reserved_write_bytes']for x in b['peer_reservations']if x['request']==request)for request in [STAGE1_REQ,FIRST16_REQ,REMAINING48_REQ,FIRST4_REQ,V1_REMAINING28_REQ,OLD_NEGATIVE16_REQ,REQ]}
 closed=b.get('remaining48_closed_metadata_forward_projection',{});released=closed.get('released_future_metadata_bytes',0)
 required=b['required_free_bytes']-sum(replaced.values())-released+own['projected_write_bytes']+sum(x['projected_write_bytes']for x in peers.values())
 total=b['reserved_additional_live_and_candidate_RAM_bytes']+own['additional_RAM_bytes']+sum(x['additional_RAM_bytes']for x in peers.values());decision=_pure().memory_admission(s,total,prev,p)
 release=s.get('direction_release',dict(pass_=False,reasons=['DIRECTION_RELEASE_MISSING']))
 if not release.get('pass'):decision=dict(decision,pass_admission=False,pressure_pause_new=True,pressure_reasons=decision['pressure_reasons']+['V2_EXPLICIT_DIRECTION_RELEASE_HOLD'])
 bound=own['projection_within_registered_ceiling']and all(x['projection_within_registered_ceiling']for x in peers.values())and all(b['per_scope_write_ceiling_pass'].values())
 archive_ok=s['true164_mount_verified']and s['archive_free_bytes']>p.get('true164_free_floor_bytes',G)+own['projected_write_bytes']
 admission_disk=bound and archive_ok and s['native_free_bytes']>required and s['free_inodes']>=p['min_free_inodes']
 runtime_safe=s['native_free_bytes']>p['native_safety_floor_bytes']and s['free_inodes']>=p['min_free_inodes']and own['actual_unarchived_output_bytes']<=q['reserved_write_bytes']
 return dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_DYNAMIC_RESOURCES_V1',utc=s.get('utc'),source_module_sha256=sha(__file__),peer_source_sha256=PEER_SHA,pure_source_sha256=PURE_SHA,host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_memory_max=s.get('cgroup_memory_max'),cgroup_memory_current=s.get('cgroup_memory_current'),cgroup_effective_headroom_bytes=s.get('cgroup_effective_headroom_bytes'),native_free_bytes=s['native_free_bytes'],free_inodes=s['free_inodes'],archive_free_bytes=s['archive_free_bytes'],true164_mount_verified=s['true164_mount_verified'],required_free_bytes=required,local_safety_floor_bytes=p['native_safety_floor_bytes'],host_floor_bytes=p['min_host_headroom_bytes'],cgroup_floor_bytes=p['min_cgroup_headroom_bytes'],admission_decision=decision,admission_pressure_pass=decision['pass_admission'],admission_disk_pass=admission_disk,archive_disk_pass=admission_disk,pressure_pause_new=not decision['pass_admission']or not admission_disk,physical_RAM_pass=decision['pass_admission']if fresh else True,physical_disk_pass=admission_disk if fresh else runtime_safe,actual_native_runtime_safe=runtime_safe,own_remaining_write_and_restore_bytes=own['projected_write_bytes'],own_actual_unarchived_output_bytes=own['actual_unarchived_output_bytes'],own_write_ceiling_pass=own['projection_within_registered_ceiling'],total_projected_additional_RAM_bytes=total,reserved_additional_live_and_candidate_RAM_bytes=total,own_ram_forecasts=own['ram'],own_write_entries=own['writes'],dynamic_known_peers=peers,static_reservations_replaced_by_evidence_bytes=replaced,closed_metadata_forward_projection=closed,pinned_R20_known_writes=b['known_remaining_writes_by_request'],other_peer_reservations=[x for x in b['peer_reservations']if x['request']not in replaced],per_scope_write_ceiling_pass=b['per_scope_write_ceiling_pass'],runtime_pressure_does_not_terminate_healthy_model=True,direction_release=release,protected_cpu_policy=s.get('protected_cpu_policy'),archive_must_require_admission_disk_pass=True,source_tier='NATIVE_DEVICE2128_BOUNDED_GZIP_SPOOL',archive_tier='GENUINE164_SOURCE_KEEP_FULL_NATIVE_RESTORE',policy_scope='ADMISSION'if fresh else'RUNTIME_ACTUAL_UNSAFE_ONLY')

def _full_resources(spec,fresh_source=False):
 global _LAST_SAMPLE
 p=policy(read(R/'control/RESOURCE_POLICY.json'));peer=_peer();b=peer.resources({'request':peer.ORIG,'cohort':'PERFV2_CODESIGN16_LAYOUT_R1_READONLY_PEER_ACCOUNTING'},False);reg,ep=peer.authority();assert ep['epoch']==2
 b['remaining48_closed_metadata_forward_projection']=_closed_known_metadata(peer,reg,b)
 q=reg['registered_future_requests'][REQ];assert q['request']==REQ and q['budget']==len(q['admitted_specs'])==16 and q['remaining']==q['budget']-len(q['consumed'])
 assert set(q['admitted_specs'])==set(EXPECTED16_COHORTS),'EXACT_AUTHORIZED16_SCOPE'
 assert spec.get('request',REQ)==REQ and spec['cohort']in q['admitted_specs']and sha(R/'control/specs'/(spec['cohort']+'.json'))==q['admitted_specs'][spec['cohort']]
 assert spec['profile']==spec['structure_variant']and spec['profile']in VARIANT_TOKENS and spec['cell']=='DH'and spec['downstream_profile']=='P0'
 assert spec['cohort']=='E2-DTCPFV2R1-'+spec['input_digest'][:16]+'-DH-'+VARIANT_TOKENS[spec['profile']]+'-V1'
 assert spec['program']in FROZEN_PROGRAMS and spec['input_digest']==FROZEN_PROGRAMS[spec['program']]
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert set(claims)<=set(q['admitted_specs'])
 peers={STAGE1_REQ:_dynamic(peer,STAGE1,reg['registered_future_requests'][STAGE1_REQ],peer.claims(STAGE1),p['stage1_metadata_reserve_bytes']),FIRST16_REQ:_closed_first16(peer,reg),REMAINING48_REQ:_closed_remaining48(peer,reg),FIRST4_REQ:_closed_first4(peer,reg),V1_REMAINING28_REQ:_closed_v1_remaining28(peer,reg),OLD_NEGATIVE16_REQ:_closed_old_negative16(peer,reg)}
 own=_dynamic(peer,R,q,claims,p['metadata_reserve_bytes'],spec,fresh_source);s=sample_system();s['direction_release']=direction_release_gate(p);prev=_LAST_SAMPLE;observer=R/'control/RESOURCE_OBSERVER.json'
 if observer.exists():
  try:
   v=read(observer)
   if v.get('boot_id')==s['boot_id']and 0<=s['monotonic']-v.get('monotonic',float('-inf'))<=120:prev=v.get('previous_sample')or v
  except(OSError,ValueError):pass
 result=_evaluate(spec,fresh_source,s,prev,b,peers,own,q,p);light={k:v for k,v in s.items()if k not in ['cpu_topology','cpu_ticks','observed_models','observed_affinity_claims']};light.update(result);result=light;result['policy_sha256']=sha(R/'control/RESOURCE_POLICY.json');_LAST_SAMPLE=s;return result


def _closed_remaining48(peer,reg):
 q=reg['registered_future_requests'][REMAINING48_REQ];claims=peer.claims(REMAINING48)
 d=_dynamic(peer,REMAINING48,q,claims,256*M)
 exact=(q['budget']==len(q['consumed'])==48 and q['remaining']==0 and set(claims)<=set(q['consumed']) and d['exact_archived_nonlive_count']==48 and not d['writes'])
 if exact:
  d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_remaining48_zero_future_metadata=True,closed_join_basis='48exactDONE_EXIT_INTENT_registry_archive_joins_and_nonlive_generation;existing_files_remain_in_df')
 d['all_execution_receipts_present']=(q['budget']==len(q['consumed'])==48 and q['remaining']==0 and all(bool(row.get('execution_receipt'))for row in q['consumed'].values()))
 return d





def _siblings(c):
 try:
  out=set()
  for part in (P('/sys/devices/system/cpu')/('cpu'+str(c))/'topology/thread_siblings_list').read_text().strip().split(','):
   if '-'in part:a,b=map(int,part.split('-'));out.update(range(a,b+1))
   else:out.add(int(part))
  return out
 except(OSError,ValueError):return {c}

def sample_system():
 s=_base_sample_system();excluded=set(PROTECTED_CPUS)
 for row in s.get('observed_models',[]):
  for c in row.get('cpus',[]):excluded.update(_siblings(c))
 s['cpu_allowed']=[c for c in s['cpu_allowed']if c not in excluded]
 s['protected_cpu_policy']=dict(always_excluded=sorted(PROTECTED_CPUS),actual_model_and_SMT_excluded=sorted(excluded-PROTECTED_CPUS),remaining_allowed_n=len(s['cpu_allowed']),signals_or_affinity_changes=0)
 return s

VARIANT_TOKENS={'PHYS768_OOPIB192_TAG64x8':'PHYS768-OOPIB192','PHYS1024_OOPIB192_TAG64x8':'PHYS1024-OOPIB192'}
FROZEN_PROGRAMS={'2DCONV': 'd984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0', 'GEMM': 'fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318', 'convolutionSeparable': '4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449', 'scan': '6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39', 'ATAX': 'eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950', 'MVT': 'f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079', 'BICG': 'ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef', 'vectorAdd': 'e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'}
FIRST4_COHORTS=['E2-DTCPF4-d984ea5475a581ad-DH-PHYS768-V1', 'E2-DTCPF4-fc0705ae3721e999-DH-PHYS768-V1', 'E2-DTCPF4-f437190767aaed49-DH-PHYS768-V1', 'E2-DTCPF4-ae34174fbbdf83b2-DH-PHYS768-V1']

def _closed_first4(peer,reg):
 q=reg['registered_future_requests'][FIRST4_REQ];claims=peer.claims(FIRST4)
 d=_dynamic(peer,FIRST4,q,claims,256*M)
 exact=(q['budget']==len(q['consumed'])==4 and q['remaining']==0 and set(q['admitted_specs'])==set(FIRST4_COHORTS) and set(claims)<=set(q['consumed']) and d['exact_archived_nonlive_count']==4 and not d['writes'])
 if exact:d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_first4_zero_future_metadata=True)
 return d




EXPECTED16_COHORTS=['E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS1024-OOPIB192-V1']

def _closed_v1_remaining28(peer,reg):
 q=reg['registered_future_requests'][V1_REMAINING28_REQ];claims=peer.claims(V1_REMAINING28);d=_dynamic(peer,V1_REMAINING28,q,claims,256*M)
 exact=(q['budget']==len(q['consumed'])==28 and q['remaining']==0 and set(claims)<=set(q['consumed'])and d['exact_archived_nonlive_count']==28 and not d['writes'])
 if exact:d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_v1_remaining28_zero_future_metadata=True)
 return d

def verify_direction_release(container,q=None):
 ref=container['project_authority'];assert P(ref['path']).resolve()==PROJECT_AUTHORITY_PATH.resolve()and ref['sha256']==PROJECT_AUTHORITY_SHA
 assert sha(ref['path'])==PROJECT_AUTHORITY_SHA;v=read(ref['path'])
 assert v['new_request']==REQ and v['authority_commit']==AUTHORITY_COMMIT and v['budget']==16 and v['remaining15_require_actual_simulator_PID_maps_matching_ROI_progress']is True
 assert v['frozen_proposed_matrix_sha256']==PROPOSAL_SHA and sha(v['user_authorization_path'])==v['user_authorization_sha256']==USER_AUTH_SHA
 proposal=read(PROPOSAL_PATH);assert sha(PROPOSAL_PATH)==PROPOSAL_SHA and set(x['proposed_new_cohort']for x in proposal['rows'])==set(EXPECTED16_COHORTS)
 direction=container['direction_release'];assert P(direction['path']).resolve()==DIRECTION_RELEASE_PATH.resolve()and direction['sha256']==DIRECTION_RELEASE_SHA and sha(direction['path'])==DIRECTION_RELEASE_SHA
 d=read(direction['path']);assert d['approved']is True and d['request']==REQ and d['authority_commit']==AUTHORITY_COMMIT and d['exact_candidate_count']==16 and set(d['candidate_cohorts'])==set(EXPECTED16_COHORTS)
 for pin in d['source_references']:assert sha(pin['path'])==pin['sha256']
 evidence=dict(project_authority_path=str(PROJECT_AUTHORITY_PATH),project_authority_sha256=PROJECT_AUTHORITY_SHA,user_authorization_path=v['user_authorization_path'],user_authorization_sha256=USER_AUTH_SHA,direction_release_path=str(DIRECTION_RELEASE_PATH),direction_release_sha256=DIRECTION_RELEASE_SHA,authority_commit=AUTHORITY_COMMIT,frozen_proposed_matrix_sha256=PROPOSAL_SHA,exact_candidate_count=16)
 if q is not None:assert q['request']==REQ and q['runtime_release_evidence']==evidence
 return evidence

def direction_release_gate(container):
 try:return dict(pass_=True,**verify_direction_release(container),reasons=[],**{'pass':True})
 except(OSError,ValueError,KeyError,TypeError,AssertionError)as e:return dict(pass_=False,**{'pass':False},reasons=[type(e).__name__+':'+str(e)])

AUTHORITY_COMMIT='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe'
DIRECTION_RELEASE_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1/control/V1_DIRECTION_RELEASE.fixed.json')

def admission_hold(q,spec):
 """Pure/read-only typed Root safety decision. Consumed healthy models are unaffected.
 Keys may be a profile, or an exact cohort with matching profile. Malformed relevant
 entries raise, causing pause-new; they are never silently treated as no hold.
 """
 assert q['request']==REQ and spec['profile']==spec['structure_variant']and spec['profile']in VARIANT_TOKENS
 if spec['cohort']in q['consumed']:return None
 matches=[]
 for key in [spec['profile'],spec['cohort']]:
  if key not in q.get('admission_holds',{}):continue
  value=q['admission_holds'][key]
  assert isinstance(value,dict)and value,'MALFORMED_RELEVANT_ADMISSION_HOLD'
  assert value['classification']=='CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD'and value['decided_by']=='DTC_MAIN'
  assert value['profile']==spec['profile']and value['reason']and value['created_utc']
  assert value.get('request',REQ)==REQ
  if key==spec['cohort']:assert value.get('cohort',key)==key
  assert sha(value['evidence_path'])==value['evidence_sha256'],'PROFILE_HOLD_EVIDENCE_DRIFT'
  if 'decision_path'in value:assert sha(value['decision_path'])==value['decision_sha256'],'PROFILE_HOLD_DECISION_DRIFT'
  matches.append(dict(value,matched_key=key))
 return matches[0]if matches else None

PROJECT_AUTHORITY_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1/control/PROJECT_AUTHORITY.fixed.json')
PROJECT_AUTHORITY_SHA='5814765fb0b8301d68c0af1ce61a62a3db68a0d8d21f69f79b48816e41c8c48f'
USER_AUTH_SHA='aae1859a57f8b578a0b294fa595f972c8a2fcca89ebee0a4a2e2677a44011133'
PROPOSAL_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/B_results_v1/engineering_negative_v1/PENDING_RETRY16_PLAN.json')
PROPOSAL_SHA='006c0bf259dcbcb9e0fe49a58cc32830371399b85c64d77c6e35bd1b1c0d19bd'
DIRECTION_RELEASE_SHA='933cfe7baab9b1adfb7f7cfe071c5bb91bacaa6bbcf53d3a16065df0d2936538'

def bounded_authority(timeout_seconds=.20,root=None):
 import fcntl
 root=P(root)if root is not None else P('/root/data/ep_l2_dtc_l1_native_v2');deadline=time.monotonic()+timeout_seconds
 with(root/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as lock:
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB);break
   except BlockingIOError:
    if time.monotonic()>=deadline:raise RuntimeError('REGISTRY_READ_CONTENTION_PAUSE_NEW_NO_BLOCKING_MODEL_SAMPLE')
    time.sleep(.005)
  path=root/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';data=path.read_bytes();epoch=read(root/'control/CURRENT_SCIENCE_EPOCH.json');assert epoch['native_registry_sha256']==hashlib.sha256(data).hexdigest();return json.loads(data),epoch

def _closed_old_negative16(peer,reg):
 q=reg['registered_future_requests'][OLD_NEGATIVE16_REQ];claims=peer.claims(OLD_NEGATIVE16);d=_dynamic(peer,OLD_NEGATIVE16,q,claims,256*M)
 if q['budget']==len(q['consumed'])==16 and q['remaining']==0 and set(claims)<=set(q['consumed'])and d['exact_archived_nonlive_count']==16 and not d['writes']:
  d=dict(d,projected_write_bytes=0,actual_unarchived_output_bytes=0,additional_RAM_bytes=0,projection_within_registered_ceiling=True,closed_negative16_zero_future_metadata=True)
 return d

def runtime_resources(spec):
 """Local-only actual safety sample. No registry, peer, archive/164 or proc sweep.
 Full admission/restore forecasts must NEVER be inferred from this receipt.
 """
 start=time.monotonic();sv=os.statvfs(R);free=sv.f_bavail*sv.f_frsize;mem={x.split(':')[0]:int(x.split()[1])*1024 for x in P('/proc/meminfo').read_text().splitlines()if':'in x and x.split()[1].isdigit()};cg=P('/sys/fs/cgroup');mx=(cg/'memory.max').read_text().strip();current=int((cg/'memory.current').read_text());head=None if mx=='max'else max(0,int(mx)-current)
 safe=R.stat().st_dev==2128 and free>5*G and sv.f_favail>=100000
 return dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_LOCAL_RUNTIME_SAMPLE_V1',utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),monotonic=time.monotonic(),sample_wall_seconds=time.monotonic()-start,host_MemAvailable_bytes=mem['MemAvailable'],cgroup_memory_max=mx,cgroup_memory_current=current,cgroup_effective_headroom_bytes=head,native_free_bytes=free,free_inodes=sv.f_favail,local_safety_floor_bytes=5*G,physical_RAM_pass=True,physical_disk_pass=safe,admission_disk_pass=False,archive_disk_pass=False,admission_pressure_pass=False,full_restore_budget_not_evaluated=True,scope='RUNTIME_ACTUAL_NATIVE_LOCAL_SAFETY_ONLY',registry_or_peer_reads=0,true164_reads=0,pressure_only_controls_new_admission=True,source_module_sha256=_SOURCE_SHA_AT_IMPORT)

def resources(spec,fresh_source=False):
 return _full_resources(spec,True)if fresh_source else runtime_resources(spec)

def archive_resources(spec):
 """Explicit full restore budget, independent of pressure/release pause-new."""
 return _full_resources(spec,False)

FIRST_COHORT='E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS768-OOPIB192-V1'
INITIAL_GATE_PATH=R/'control/INITIAL_RUNTIME_RELEASE.json'
INITIAL_GATE_SCHEMA='DTC_PERFV2_CODESIGN16_LAYOUT_R1_INITIAL_RUNTIME_RELEASE_V1'

class WaitInitialRuntimeGate(RuntimeError):pass

def _assert_native_small(path,limit):
 path=P(path);assert path.resolve().is_relative_to(R.resolve())and path.stat().st_dev==2128,'INITIAL_GATE_NATIVE_SMALL_METADATA_ONLY'
 assert path.stat().st_size<=limit,'INITIAL_GATE_METADATA_OVERSIZE'

def _bounded_native_json(path,limit=1024*1024):
 _assert_native_small(path,limit);return read(path)

def _closed_progress_rows(path):
 import zlib
 path=P(path);_assert_native_small(path,2*M)
 obj=zlib.decompressobj(31);data=obj.decompress(path.read_bytes(),4*M);assert not obj.unconsumed_tail and len(data)<4*M,'INITIAL_GATE_STREAM_PREFIX_OVERSIZE'
 # Streaming gzip with unfinished footer is valid while waiting, complete lines only.
 return [json.loads(line)for line in data.decode().splitlines()if line.strip().endswith('}')]

def inspect_first_closed(plan,q):
 """Native-only bounded evidence. No registered/authority/peer/full archive call.
 Release waits for the first point's natural strict/archive closure; no /proc
 disappearance ambiguity, and no extra canary identity is introduced.
 """
 assert q['request']==REQ and q['budget']==16 and q['admitted_specs'].get(FIRST_COHORT)
 if FIRST_COHORT not in q['consumed']:raise WaitInitialRuntimeGate('WAIT_INITIAL_RUNTIME_GATE_FIRST_UNUSED')
 row=q['consumed'][FIRST_COHORT];uid=row['uuid'];out=R/'DTC/run/results'/uid;donep=R/'control/qualification_ledger'/(FIRST_COHORT+'.DONE.json')
 if not donep.exists():raise WaitInitialRuntimeGate('WAIT_INITIAL_RUNTIME_GATE_FIRST_EXECUTING')
 done=_bounded_native_json(donep);assert done==row['execution_receipt']==_bounded_native_json(out/'NATIVE_EXIT.json')
 if done['launcher_wait_returncode']!=0 or done['stop_reason']is not None or done['native_simulator_observed']is not True:raise RuntimeError('FIRST_LEGAL_POINT_EXECUTION_FAILED_PAUSE_ALL_NEW_ADMISSION')
 resultp=R/'analysis'/(FIRST_COHORT+'.RESULT.json')
 if not resultp.exists():raise WaitInitialRuntimeGate('WAIT_INITIAL_RUNTIME_GATE_NATURAL_FIRST_ARCHIVE_PENDING')
 result=_bounded_native_json(resultp)
 if result['state']!='PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE':raise RuntimeError('FIRST_LEGAL_POINT_STRICT_OR_ARCHIVE_FAILED_PAUSE_ALL_NEW_ADMISSION')
 assert result['proof']['performance_accepted']is True and result['uuid']==uid and result['cohort']==FIRST_COHORT
 specp=R/'control/specs'/(FIRST_COHORT+'.json');spec=_bounded_native_json(specp);assert sha(specp)==q['admitted_specs'][FIRST_COHORT]
 assert spec['program']=='vectorAdd'and spec['profile']==spec['structure_variant']=='PHYS768_OOPIB192_TAG64x8'
 ip=R/'control/qualification_ledger'/(FIRST_COHORT+'.INTENT.json');intent=_bounded_native_json(ip);assert intent['uuid']==uid and sha(ip)==row['intent_sha256']
 pm=_bounded_native_json(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=_bounded_native_json(out/'NATIVE_LAUNCH.json');assert launch['scientific_qualification_uuid']==uid
 assert launch['argv'][-len(spec['native_simulator_argv']):]==spec['native_simulator_argv']
 binding=intent['l2_mlp_execution_binding'];assert launch['l2_mlp_execution_binding']==pm['l2_mlp_execution_binding']==binding
 assert binding['request']==REQ and binding['engine_sha256']==q['engine_sha256']and binding['plan_sha256']==q['execution_plan_sha256']and binding['runtime_release_evidence']==q['runtime_release_evidence']
 assert binding['runtime_guard_sha256']==plan['runtime_guard']['sha256']and binding['runtime_guard_policy_sha256']==plan['runtime_guard']['policy_sha256']
 assert pm['mnt_namespace']==spec['execution_mnt_namespace']
 assert spec['native_simulator_argv'][0]in pm['maps']and '/root/data/dtc_failure_repair_20261025_v1/core-build/libcudart.so'in pm['maps']
 expected_loader=(R/'common-lib/ld-linux-x86-64.so.2').resolve();assert P(pm['exe']).resolve()==expected_loader and sha(pm['exe'])=='9eb34cb2da3ae2a9398cc09b3cd2d069563ec40d9858cb711af15cd23fa80abf'
 dispatchp=R/'control/dispatch_bindings'/(FIRST_COHORT+'.json');db=_bounded_native_json(dispatchp);assert pm['host_cpu_affinity_actual']==[db['host_cpu']]and pm['dispatch_binding_sha256']==sha(dispatchp)
 progressp=out/'progress.jsonl.gz';progress=_closed_progress_rows(progressp);assert progress,'NO_AUTHENTICATED_FIRST_PROGRESS'
 lastseq=0;lastmono=0;positive=[]
 for packet in progress:
  assert packet['v']==1 and packet['pid']==pm['pid']and packet['start_ticks']==pm['start_ticks']and packet['generation']==uid
  assert packet['input']==spec['original_environment']['DTC_AG7_INPUT_SHA']==spec['input_digest']and packet['roi']==spec['original_environment']['DTC_AG7_ROI_SHA']
  assert packet['seq']>lastseq and packet['mono_ns']>=lastmono and packet['end']not in ['LIMIT','ERROR']
  lastseq=packet['seq'];lastmono=packet['mono_ns']
  if packet['completed']>0:positive.append(packet)
 assert positive,'NO_NONZERO_MATCHING_ROI_PROGRESS'
 rp=out/'RESOURCE_SAMPLES.jsonl.gz';samples=_closed_progress_rows(rp);guards=[x['DTC_exact_original_policy']for x in samples if'DTC_exact_original_policy'in x];assert guards,'NO_AUTHENTICATED_GUARD_POLICY_SAMPLE'
 for guard in guards:
  b=guard['runtime_policy_binding'];assert b['schema']=='DTC_PERFV2_CODESIGN16_LAYOUT_R1_ADMISSION_PRESSURE_ONLY_RUNTIME_V1'and b['guard_sha256']==plan['runtime_guard']['sha256']and b['policy_sha256']==plan['runtime_guard']['policy_sha256']and b['telemetry_receiver_sha256']=='f523975b9780b498b988e2b3145ba5b4aebdef4d0e9b0146392d3a31a99a4ec1'
  assert guard['decision']['decision']!='STOP'
 paths=[ip,donep,out/'NATIVE_EXIT.json',resultp,specp,dispatchp,out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',out/'NATIVE_LAUNCH.json',progressp,rp]
 return dict(schema=INITIAL_GATE_SCHEMA,request=REQ,first_cohort=FIRST_COHORT,uuid=uid,input_digest=spec['input_digest'],roi=spec['original_environment']['DTC_AG7_ROI_SHA'],observed_pid=pm['pid'],observed_start_ticks=pm['start_ticks'],actual_loader_exe=pm['exe'],release_mode='NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE_FIRST_POINT_WITH_AUTHENTICATED_NONZERO_PROGRESS',closed_first_accepted=True,guard_STOP_observed=False,positive_progress_sample=positive[0],source_refs=[dict(path=str(x),sha256=sha(x))for x in paths],source_resource_sha256=sha(__file__),release15=True,scientific_performance_promoted_by_gate=False)

def verify_initial_runtime_gate(plan,cohort,q=None):
 assert cohort in EXPECTED16_COHORTS
 if cohort==FIRST_COHORT:return None
 if q is None:q=bounded_authority()[0]['registered_future_requests'][REQ]
 if not INITIAL_GATE_PATH.exists():raise WaitInitialRuntimeGate('WAIT_INITIAL_RUNTIME_GATE')
 witness=_bounded_native_json(INITIAL_GATE_PATH);fresh=inspect_first_closed(plan,q)
 assert witness==fresh,'INITIAL_GATE_CLOSED_EVIDENCE_DRIFT'
 return dict(path=str(INITIAL_GATE_PATH),sha256=sha(INITIAL_GATE_PATH),schema=INITIAL_GATE_SCHEMA,first_cohort=FIRST_COHORT,uuid=witness['uuid'],release15=True)

_SOURCE_SHA_AT_IMPORT=sha(__file__)
