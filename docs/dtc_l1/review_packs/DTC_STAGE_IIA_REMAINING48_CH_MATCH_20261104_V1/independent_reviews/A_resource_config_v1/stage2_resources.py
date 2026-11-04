"""Remaining48-only resource admission. Read-only authority/files; no dispatch or signals.
Runtime pressure pauses new admission. Hard native floor/inode/actual-own write
contract remain unsafe. Archive callers MUST use admission_disk_pass.
"""
import pathlib,json,hashlib,importlib.util,os,math,time
P=pathlib.Path;G=1024**3;M=1024**2
R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
FIRST16=P('/root/data/dtc_stage_iia_first16_20261104_v1');FIRST16_REQ='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'
ARCHIVE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
STAGE1_REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';STAGE1=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
PEER=P('/root/data/dtc_failure_repair_20261025_v1/ops/revision20/resource_accounting_v1.py');PEER_SHA='e9c864c109ea4e87521713246e5a1602d95da5413861cc7f34be100180ee866e'
PURE=STAGE1/'tools/l2_resources.py';PURE_SHA='6ad97e35de88ff5876bc0af674324f979f35c211f31d182976d2f66abb9c4854'
SCHEMA='DTC_STAGE_IIA_REMAINING48_DYNAMIC_RESOURCE_POLICY_V1';_PURE=None;_PEER=None;_JOIN={};_LAST_SAMPLE=None;_PEAK_RSS={};_RECENT_INPUT_PEAKS={};_LAST_PRECLAIM_HOLDS=[]
DEFAULT_POLICY=dict(schema=SCHEMA,memory_utilization_fraction=.88,min_host_headroom_bytes=8*G,min_cgroup_headroom_bytes=8*G,native_safety_floor_bytes=5*G,metadata_reserve_bytes=256*M,min_free_inodes=100000,stage1_metadata_reserve_bytes=G)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def _load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def _pure():
 global _PURE
 assert sha(PURE)==PURE_SHA,'PURE_RESOURCE_SOURCE_DRIFT'
 if _PURE is None:
  _PURE=_load('remaining48_private_pure_resource',PURE);_PURE.R=R;_PURE.REQ=REQ
  _PURE.DEFAULT_POLICY.update(DEFAULT_POLICY);_PURE.pressure_reasons=pressure_reasons;_PURE.forecast=forecast
 return _PURE
def _peer():
 global _PEER
 assert sha(PEER)==PEER_SHA,'PEER_RESOURCE_SOURCE_DRIFT'
 if _PEER is None:_PEER=_load('remaining48_readonly_r20_peer',PEER)
 return _PEER
def policy(value=None):
 p=dict(_pure().DEFAULT_POLICY);p.update(DEFAULT_POLICY);p.update(value or {})
 assert p['schema']==SCHEMA and .85<=p['memory_utilization_fraction']<=.90
 assert p['native_safety_floor_bytes']>=5*G and p['metadata_reserve_bytes']>=0
 assert p['min_host_headroom_bytes']>=8*G and p['min_cgroup_headroom_bytes']>=8*G
 return p
def sample_system():
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
 estimate=spec.get('estimated_peak_model_RAM_bytes',4*G);assert type(estimate)is int and estimate>0
 hard=spec['limits']['max_process_tree_rss_bytes'];assert hard>=estimate
 rows=history.get('records',history)if isinstance(history,dict)else(history or []);key=spec.get('workload',spec.get('input_digest'));elapsed=spec.get('historical_elapsed_seconds')or max([x.get('elapsed',x.get('elapsed_seconds',0))or 0 for x in rows if x.get('workload',x.get('input_digest'))==key and x.get('success',x.get('accepted',False))]+[0])
 recent=_RECENT_INPUT_PEAKS.get(key,0);estimate=max(estimate,math.ceil(recent*1.20)+128*M if recent else 0);assert estimate<=hard,'REGISTERED_RSS_LIMIT_BELOW_DYNAMIC_FORECAST'
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
   envelope=min(hard,max(estimate,math.ceil(peak*1.20)+128*M));ram.append(dict(cohort=c,RSS_bytes=used,additional_reserved_bytes=max(0,envelope-used),kind='LIVE_MODEL'if live else'SPENT_UNRESOLVED_GENERATION_RETAINED'))
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
 replaced={request:sum(x['reserved_write_bytes']for x in b['peer_reservations']if x['request']==request)for request in [STAGE1_REQ,FIRST16_REQ,REQ]}
 closed=b.get('remaining48_closed_metadata_forward_projection',{});released=closed.get('released_future_metadata_bytes',0)
 required=b['required_free_bytes']-sum(replaced.values())-released+own['projected_write_bytes']
 for request,detail in peers.items():
  if replaced.get(request,0):required+=detail['projected_write_bytes']
 total=b['reserved_additional_live_and_candidate_RAM_bytes']+own['additional_RAM_bytes']+sum(x['additional_RAM_bytes']for x in peers.values());decision=_pure().memory_admission(s,total,prev,p)
 bound=own['projection_within_registered_ceiling']and all(x['projection_within_registered_ceiling']for x in peers.values())and all(b['per_scope_write_ceiling_pass'].values())
 archive_ok=s['true164_mount_verified']and s['archive_free_bytes']>p.get('true164_free_floor_bytes',G)+own['projected_write_bytes']
 admission_disk=bound and archive_ok and s['native_free_bytes']>required and s['free_inodes']>=p['min_free_inodes']
 runtime_safe=s['native_free_bytes']>p['native_safety_floor_bytes']and s['free_inodes']>=p['min_free_inodes']and own['actual_unarchived_output_bytes']<=q['reserved_write_bytes']
 return dict(schema='DTC_STAGE_IIA_REMAINING48_DYNAMIC_RESOURCES_V1',utc=s.get('utc'),source_module_sha256=sha(__file__),peer_source_sha256=PEER_SHA,pure_source_sha256=PURE_SHA,host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_memory_max=s.get('cgroup_memory_max'),cgroup_memory_current=s.get('cgroup_memory_current'),cgroup_effective_headroom_bytes=s.get('cgroup_effective_headroom_bytes'),native_free_bytes=s['native_free_bytes'],free_inodes=s['free_inodes'],archive_free_bytes=s['archive_free_bytes'],true164_mount_verified=s['true164_mount_verified'],required_free_bytes=required,local_safety_floor_bytes=p['native_safety_floor_bytes'],host_floor_bytes=p['min_host_headroom_bytes'],cgroup_floor_bytes=p['min_cgroup_headroom_bytes'],admission_decision=decision,admission_disk_pass=admission_disk,pressure_pause_new=not decision['pass_admission']or not admission_disk,physical_RAM_pass=decision['pass_admission']if fresh else True,physical_disk_pass=admission_disk if fresh else runtime_safe,actual_native_runtime_safe=runtime_safe,own_remaining_write_and_restore_bytes=own['projected_write_bytes'],own_actual_unarchived_output_bytes=own['actual_unarchived_output_bytes'],own_write_ceiling_pass=own['projection_within_registered_ceiling'],total_projected_additional_RAM_bytes=total,reserved_additional_live_and_candidate_RAM_bytes=total,own_ram_forecasts=own['ram'],own_write_entries=own['writes'],dynamic_known_peers=peers,static_reservations_replaced_by_evidence_bytes=replaced,closed_metadata_forward_projection=closed,pinned_R20_known_writes=b['known_remaining_writes_by_request'],other_peer_reservations=[x for x in b['peer_reservations']if x['request']not in replaced],per_scope_write_ceiling_pass=b['per_scope_write_ceiling_pass'],runtime_pressure_does_not_terminate_healthy_model=True,archive_must_require_admission_disk_pass=True,source_tier='NATIVE_DEVICE2128_BOUNDED_GZIP_SPOOL',archive_tier='GENUINE164_SOURCE_KEEP_FULL_NATIVE_RESTORE',policy_scope='ADMISSION'if fresh else'RUNTIME_ACTUAL_UNSAFE_ONLY')

def resources(spec,fresh_source=False):
 global _LAST_SAMPLE
 p=policy(read(R/'control/RESOURCE_POLICY.json'));peer=_peer();b=peer.resources({'request':peer.ORIG,'cohort':'REMAINING48_READONLY_PEER_ACCOUNTING'},False);reg,ep=peer.authority();assert ep['epoch']==2
 b['remaining48_closed_metadata_forward_projection']=_closed_known_metadata(peer,reg,b)
 q=reg['registered_future_requests'][REQ];assert q['request']==REQ and q['budget']==len(q['admitted_specs'])==48 and q['remaining']==q['budget']-len(q['consumed'])
 assert spec.get('request',REQ)==REQ and spec['cohort']in q['admitted_specs']and spec['cohort'].startswith('E2-DTC2A48-')
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert set(claims)<=set(q['admitted_specs'])
 oldq=reg['registered_future_requests'][STAGE1_REQ];peers={STAGE1_REQ:_dynamic(peer,STAGE1,oldq,peer.claims(STAGE1),p['stage1_metadata_reserve_bytes']),FIRST16_REQ:_closed_first16(peer,reg)}
 own=_dynamic(peer,R,q,claims,p['metadata_reserve_bytes'],spec,fresh_source);s=sample_system();prev=_LAST_SAMPLE;observer=R/'control/RESOURCE_OBSERVER.json'
 if observer.exists():
  try:
   v=read(observer)
   if v.get('boot_id')==s['boot_id']and 0<=s['monotonic']-v.get('monotonic',float('-inf'))<=120:prev=v.get('previous_sample')or v
  except (OSError,ValueError):pass
 result=_evaluate(spec,fresh_source,s,prev,b,peers,own,q,p);light={k:v for k,v in s.items()if k not in ['cpu_topology','cpu_ticks','observed_models','observed_affinity_claims']};light.update(result);result=light;result['policy_sha256']=sha(R/'control/RESOURCE_POLICY.json');_LAST_SAMPLE=s;return result
