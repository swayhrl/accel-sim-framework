"""Exact SC61 CPU-only preparation; no generic command or GPU interface."""
import re,os,sys,pathlib,json,hashlib,time,stat,resource,importlib.util,shutil
G=2**30
JOB='ORD_Rodinia_streamcluster_1be5fda1aa60_A001'
POST_SHA='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
DEADLINE=1793241315.9269235
NAME='streamcluster_remote_post_remaining_local_ssd_crosshost_prepare_20261028_v10'
NB=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')/NAME/'runtime'
RB=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates')/NAME/'runtime'
NS=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/inflight')/JOB
RS=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/inflight')/JOB
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def no_links(p):
 p=pathlib.Path(p)
 for q in [p,*p.parents]:need(not q.is_symlink(),'SYMLINK_PATH')
def readref(r):
 p=pathlib.Path(r['path']);no_links(p);need(0<r['bytes']<=8*2**20,'METADATA_BOUND')
 with p.open('rb') as f:
  b=os.fstat(f.fileno());need(stat.S_ISREG(b.st_mode)and b.st_size==r['bytes'],'REGULAR_SIZE');raw=f.read(8*2**20+1);e=os.fstat(f.fileno())
  key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(key(b)==key(e),'SAME_FD_METADATA_CHANGED')
 n=p.stat();need((b.st_size,b.st_mtime_ns,b.st_ctime_ns,b.st_dev)==(n.st_size,n.st_mtime_ns,n.st_ctime_ns,n.st_dev),'PATH_METADATA_CHANGED')
 need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'RAW_REF_SHA')
 return json.loads(raw)
def ref(p):p=pathlib.Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
def save(p,x):
 p=pathlib.Path(p);raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
 with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def pinned_module(path,h,name):
 b=pathlib.Path(path).read_bytes();need(hashlib.sha256(b).hexdigest()==h,'CODE_RAW_PIN')
 m=type(sys)(name);m.__file__=str(path);exec(compile(b,str(path),'exec'),m.__dict__);return m
def code_check(base,mfsha):
 base=pathlib.Path(base);need(digest(base/'CODE_MANIFEST.json')==mfsha,'CODE_MF_PIN')
 m=json.loads((base/'CODE_MANIFEST.json').read_bytes())
 for n,r in m['files'].items():
  need(pathlib.PurePosixPath(n).as_posix()==n and '..'not in pathlib.PurePosixPath(n).parts and not n.startswith('/'),'MF_PATH')
  p=base/n;no_links(p);need(p.stat().st_size==r['bytes']and digest(p)==r['sha256'],'MF_FILE')
 return m
def validate_scope(a):
 need(a['schema']=='ROOT_SC_CPU_ONLY_REMAINING_SCOPE_V10'and a['status']=='ROOT_APPROVED_CPU_ONLY','ROOT_APPROVAL_REQUIRED')
 need(a['job_id']==JOB and a['GPU_CUDA_or_simulator_allowed']is False and a['source_KEEP']is True,'EXACT_CPU_SCOPE')
 need(a['original_absolute_deadline_unix']==DEADLINE and a['not_before_unix']<=time.time()<DEADLINE,'ORIGINAL_DEADLINE')
 need(a['Native_runtime_root']==str(NB)and a['remote_runtime_root']==str(RB),'FIXED_CODE_ROOT')
 need(a['Native_source_root']==str(NS)and a['remote_source_root']==str(RS),'FIXED_SOURCE_ROOT')
 need(re.fullmatch('[A-Za-z0-9_]{1,80}',a['run_id']) is not None,'RUN_ID')
 need(hashlib.sha256((json.dumps(a['original61_selected'],sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()=='19080e8334aab89b44cbf861216a13de585b311b8eb54012540d1e00280b0f02','ACTUAL61_LIST_PIN')
 need(hashlib.sha256((json.dumps(a['original61_expected'],sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()=='2b9829cabe0f309bb096027d57670623f21fb5d08d36a557f7211779a2b1c56a','ACTUAL61_EXPECTED_PIN')
 need(a['workers']==8 and a['remote_cpu_ids']==list(range(8)),'ROOT_EXPLICIT_CPU8_SINGLE_HARD10G')
 need(a['remote_memory_max_bytes']==10*G and a['remote_swap_max_bytes']==0 and a['remote_physical_headroom_bytes']==8*G,'REMOTE_HEAVY_POST_BUDGET')
 need(a['Native_control_envelope_bytes']==2*G,'NATIVE_CONTROL_ONLY_BUDGET')
 z=a['Native_bridge_policy'];need(z['schema']=='ROOT_SC_EXACT61_NATIVE_LIGHT_BRIDGE_POLICY_V1'and z['role']=='SC_EXACT61_REMOTE_CPU_BRIDGE_ONLY_NAS','EXACT_LIGHT_CONTROL_ROLE')
 need(z['actors']==3 and z['each_actor_AS_bytes']==512*2**20 and z['host_floor_bytes']>=67*G and z['cgroup_floor_bytes']>=51*G,'LIGHT_PHYSICAL_FLOORS')
 need(z['Native_POST_or_trace_payload_allowed']is False and z['foreign_current_SPEC_identity_and_cap_check_required']is True,'NO_HEAVY_NATIVE_OR_FOREIGN_BYPASS')
 need(a['postprocessor_sha256']==POST_SHA,'FROZEN_5D_ADOPTION')
 need(1<=len(a['selected'])<=59 and len(set(a['selected']))==len(a['selected']),'EXACT_REMAINING_SCOPE')
 need(all(pathlib.Path(n).name==n and n.startswith('kernel-')and n.endswith('.trace.xz')for n in a['selected']),'NAMES')
 need(set(a['expected'])==set(a['selected']),'EXPECTED59')
 need(a['Root_extra2_acceptance_raw_sha256']=='d3f224eb983bd91e3fd6c427504b8bd044f95f3bfb3f37b7b0994c5d139b576f','EXTRA2_ACCEPTANCE_SCOPE_PIN')
 extra=extra2_acceptance();names=[r['name']for r in extra['rows']];need(names==a['original61_selected'][:2],'EXACT_ROOT_ACCEPTED_TWO')
 validate_v8_adopted_rows(a,accepted_v8(a));need(a['expected']=={n:a['original61_expected'][n]for n in a['selected']},'EXACT_REMAINING_EXPECTED')
 need(a['local_ssd_parent']=='/data/c16/sc_post_local_ssd_20261028_v9'and a['local_scratch_budget_bytes']==32*G and a['per_worker_scratch_budget_bytes']==4*G and a['local_ssd_free_floor_bytes']==10*G,'EXACT_LOCAL_SSD_BUDGET')
 need(a['Root_V9_failed_bootstrap_closure_accepted']is True,'ROOT_V9_SUPPLEMENTAL_SHUTDOWN_ACCEPTANCE_REQUIRED')
 need(a['output_cap_interval_seconds']==30 and a['cleanup_own_local_scratch_after_NAS_closed']is True,'EXACT_LOCAL_OUTPUT_POLICY')
 need(a['max_memory_pause_seconds']==900,'BOUNDED_900S_PAUSE')
 need(hashlib.sha256((json.dumps(a['old193_batch_refs'],sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()=='4aac204b338330ddd81c6f69f400193644cbfcf6c2aa23dcc377a02d7b08998b','OLD193_INDEX_PIN')
 need(a['old6_partial_ref']['sha256']=='4df6fa16a795b4b754b9a4b815b88f7edf5d1032e58e0d8a05aab3ac5863f1e5','OLD6_INDEX_PIN')
 need(a['Root_same_owner_other_POST_reserved_bytes']==0,'CPU_ONLY_NO_OTHER_GPU_RESERVATION')
 need(a['remote_process_metadata_role']=='BOUNDED_UNATTRIBUTED_TELEMETRY_ONLY'and a['remote_large_process_telemetry_limit']==20,'CPU_ONLY_PROCESS_TELEMETRY_POLICY')
 need(a['Root_concurrent_POST_schedule_verified']is True,'OTHER_POST_SCHEDULE_UNREVIEWED')
 need(a['execution_mode']=='CPU_ONLY_NO_GPU_COACTIVITY'and a['GPU_capture_coactivity_allowed']is False and a['peer_POST_reservations']==[],'EXACT_CPU_ONLY_NO_GPU_COACTIVITY')
 need(a['Root_user_cpu_only_authorization_ref']is not None and a['Root_cpu_only_resource_ref']is not None,'ROOT_EXACT_NEW_CPU_ONLY_SELECTION_REFS')
 need(all(a.get(k)is None for k in ['mutual_contract_ref','capture33_scope_sha256','capture33_code_manifest_sha256','capture33_identity']),'NO_CLAIM_OR_DEPENDENCY_ON_GPU_COEXISTENCE')
 need(a['remote_declared_future_cap_authority_complete']is False,'DO_NOT_INVENT_FOREIGN_COMPLETE')
 return a
def validate_v8_adopted_rows(a,z):
 need(z['schema']=='ROOT_SC_V8_CLOSED_PREFIX_ADOPTION_ACCEPTANCE_V1'and z['status']==a['Root_V8_adoption_required_status']and z['status'].startswith('ROOT_INDEPENDENT_CURRENT')and z['status'].endswith('_GROUPED_WHOLE_SHA_ACCEPTED'),'ROOT_V8_ADOPTION_REQUIRED')
 need(z['source_scope_ref']['sha256']=='5956010996924f6fdf9eae39ca9882754e00b099c513284655d74c9ef45b4aba'and z['source_code_manifest_sha256']=='ecc05e73fbdfb0a071368f2bcce9fbc47a68b30896d82b70ba6270c0c7fbda6a','EXACT_V8_SCOPE_CODE')
 need(z['current_grouped_body_wholeSHA_rechecked']is True and z['all_owned_closed_and_asset_locks_released']is True,'V8_ROOT_WHOLE_SHA_AND_CLOSURE')
 rows=z['rows'];names=[r['name']for r in rows];original=a['original61_selected'][2:]
 need(len(set(names))==len(names)and set(names)<=set(original),'V8_UNIQUE_ORIGINAL_SUBSET')
 for r in rows:
  q=a['original61_expected'][r['name']]
  need(r['source_sha256']==q['source_sha256']and[r[k]for k in ['records','ctas','warps']]==[q[k]for k in ['records','ctas','warps']],'V8_EXACT_SOURCE_COUNTS')
 need(z['closed_count']==len(rows)and z['closed_records']==sum(r['records']for r in rows),'V8_ADOPTED_TOTALS')
 need(a['selected']==[n for n in original if n not in names]and a['remaining_records']==sum(a['original61_expected'][n]['records']for n in a['selected']),'ORIGINAL59_MINUS_ALL_ROOT_ACCEPTED_V8_ONLY')
 need(a['closed_adoption_count']==1552+len(rows)and z['closed_records']+a['remaining_records']==201344544,'V8_PLUS_REMAINING_ALL59')
 need(z['remaining_names']==a['selected']and z['remaining_expected']==a['expected']and z['total_closed_count']==a['closed_adoption_count']and z['total_closed_records']==5317079280+z['closed_records'],'ROOT_V8_REMAINING_AND_TOTALS_BINDING')
 return z
def accepted_v8(a):
 primary=a['Root_V8_closed_adoption_ref'];p=pathlib.Path(__file__).resolve().parent/'ROOT_ACCEPTED_V8_ADOPTION_V1.json'
 return readref(dict(path=str(p),bytes=primary['bytes'],sha256=primary['sha256']))

class PhysicalRAMShortage(RuntimeError):
 def __init__(self,detail):self.detail=detail;super().__init__('REMOTE_PHYSICAL_RAM_HEADROOM')
def extra2_acceptance():
 p=pathlib.Path(__file__).resolve().parent/'ROOT_EXTRA2_ACCEPTANCE_V1.json';need(digest(p)=='d3f224eb983bd91e3fd6c427504b8bd044f95f3bfb3f37b7b0994c5d139b576f','ROOT_ACCEPTED_EXTRA2_RAW_PIN');z=json.loads(p.read_bytes());need(z['schema']=='ROOT_CURRENT_EXTRA2_GROUPED_WHOLE_SHA_ADOPTION_ACCEPTANCE_V1'and z['current_grouped_body_wholeSHA_rechecked']is True and z['total_closed_count']==1552 and z['remaining_records']==201344544,'EXTRA2_ROOT_ACCEPTANCE');return z
def memory_verdict(available,own_remaining,other_remaining,headroom):
 need(min(available,own_remaining,other_remaining,headroom)>=0,'RAM_NUMBERS')
 required=own_remaining+other_remaining+headroom
 if available<required:raise PhysicalRAMShortage(dict(available=available,required=required,own_remaining=own_remaining,other_remaining=other_remaining,headroom=headroom))
 return dict(available=available,required=required,own_remaining=own_remaining,other_remaining=other_remaining,headroom=headroom)
def normalize_result(n,r,a,remote_root):
 q=a['expected'][n];need(r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and r['closed_reopened_full_xz_crc']is True and r['source_keep']is True,'POST_CLOSURE')
 need(r['source']==str(RS/'traces'/n)and r['source_sha256']==q['source_sha256'],'SOURCE_IDENTITY')
 need([r[k]for k in ['records','ctas','warps']]==[q[k]for k in ['records','ctas','warps']],'COUNTS')
 p=pathlib.Path(r['grouped']);no_links(p);need(p.resolve().is_relative_to(pathlib.Path(remote_root).resolve()),'OUTPUT_ESCAPE')
 return dict(name=n,logical_source=str(NS/'traces'/n),remote_source=r['source'],source_sha256=r['source_sha256'],result=r,postprocessor_sha256=POST_SHA)

def native_light_verdict(old,v,policy):
 need(v['unknown_active_cohort_count']==0,'UNKNOWN_FOREIGN')
 need(old['host_MemAvailable']>=policy['host_floor_bytes'],'NATIVE_HOST67G_FLOOR')
 for r in old['rows']:
  need(r['effective_headroom'] is None or r['effective_headroom']>=policy['cgroup_floor_bytes'],'NATIVE_CGROUP51G_FLOOR')
  need(r['pressure_full_avg10']<=5 and r['pressure_some_avg10']<=20,'NATIVE_PSI')
  need(all(r['events_delta'].get(k,0)==0 for k in ['high','max','oom','oom_kill','oom_group_kill']),'NATIVE_OOM_EVENT')
 for r in v['current_RAM_planning_rows']:
  cap=(r.get('local_registered_SPEC_planning_proof')or{}).get('max_process_tree_rss_bytes')
  if cap is None:cap=r['registered_memory_fields'].get('max_process_tree_rss_bytes')
  if cap is None:cap=r['actual_RLIMIT_AS_bytes']
  need(type(cap)is int and cap>0 and r['actual_current_tree_Rss_bytes']<=cap,'REGISTERED_FOREIGN_CURRENT_TREE_OVER_CAP')
 return dict(schema='SC_EXACT61_NATIVE_LIGHT_BRIDGE_VERDICT_V1',status='PASS',role=policy['role'],own_control_bytes=2*G,host_MemAvailable=old['host_MemAvailable'],cgroup_min_headroom=min((r['effective_headroom']for r in old['rows']if r['effective_headroom']is not None),default=None),original_R4_full_aggregate_status=old['status'],original_R4_foreign_additional_bytes=v['additional_active_RAM_commitments_bytes'],foreign_forecasts_fully_disclosed_control_role_uses_physical_floor_policy=True,Native_CPU_POST_allowed=False,remote_heavy_POST_gate_bypassed=False,current_foreign_rows_checked=len(v['current_RAM_planning_rows']))

