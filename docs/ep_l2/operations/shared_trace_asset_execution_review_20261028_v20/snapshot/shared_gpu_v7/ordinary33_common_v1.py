"""Exact frozen33 capture-only contract; no import-time execution/query."""
import pathlib,os,sys,json,hashlib,time,stat,resource,shutil,re
G=2**30
NAME='remaining30_queue_positive_closure_prepare_20261028_v7'
NB=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')/NAME/'runtime'
RB=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates')/NAME/'runtime'
DEADLINE=1793241315.9269235
def need(x,m):
 if not x:raise RuntimeError(m)
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def no_links(p):
 for q in [pathlib.Path(p),*pathlib.Path(p).parents]:need(not q.is_symlink(),'NO_SYMLINK')
def readref(r):
 p=pathlib.Path(r['path']);no_links(p);need(0<r['bytes']<=8*2**20,'BOUNDED_METADATA')
 with p.open('rb')as f:
  a=os.fstat(f.fileno());raw=f.read(8*2**20+1);b=os.fstat(f.fileno())
  key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  need(stat.S_ISREG(a.st_mode)and key(a)==key(b),'SAMEFD_METADATA')
 need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'REF_BYTES_SHA')
 return json.loads(raw)
def ref(p):p=pathlib.Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def save(p,x):
 with pathlib.Path(p).open('xb')as f:f.write((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
def rawmodule(p,h,name):
 b=pathlib.Path(p).read_bytes();need(hashlib.sha256(b).hexdigest()==h,'PINNED_SOURCE_BYTES');m=type(sys)(name);m.__file__=str(p);exec(compile(b,str(p),'exec'),m.__dict__);return m
def code_check(D,h):
 need(sha(D/'CODE_MANIFEST.json')==h,'CODE_MANIFEST_PIN')
 x=json.loads((D/'CODE_MANIFEST.json').read_bytes())
 for n,r in x['files'].items():
  need(not n.startswith('/')and '..'not in pathlib.PurePosixPath(n).parts,'MF_PATH');p=D/n;no_links(p);need(p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'MF_MEMBER_PIN')
 return x
def dependencies(D,mf):
 for n in ['activity_proof_v3','inherited_leases_v5','owned_runtime_v1']:
  sys.modules[n]=rawmodule(D/(n+'.py'),mf['files'][n+'.py']['sha256'],n)
 return sys.modules['inherited_leases_v5'],sys.modules['owned_runtime_v1']
def validate_scope(a,allowlist,now=None):
 now=time.time()if now is None else now
 need(a['schema']=='ROOT_EXACT33_CAPTURE_ONLY_CAMPAIGN_V1'and a['status']=='ROOT_APPROVED_CAPTURE_ONLY','ROOT_SCOPE_NOT_APPROVED')
 need(re.fullmatch('[A-Za-z0-9_]{1,60}',a['campaign_id'])is not None,'CAMPAIGN_ID')
 need(a['original_absolute_deadline_unix']==DEADLINE and a['not_before_unix']<=now<DEADLINE,'NO_SILENT_DEADLINE_EXTENSION')
 need(a['Native_runtime_root']==str(NB)and a['remote_runtime_root']==str(RB),'EXACT_CODE_ROOT')
 ids=a['ordered_job_ids'];need(ids and len(ids)==len(set(ids))and set(ids)<=set(allowlist['jobs']),'EXACT33_ALLOWLIST')
 need(len(allowlist['jobs'])==33 and a['frozen33_attestation_sha256']==allowlist['frozen33_attestation_ref']['sha256'],'ALLOWLIST_BINDING')
 planpath=pathlib.Path(__file__).parent/'PRIOR_CAPTURE_EXCLUSION_V4.json';planraw=planpath.read_bytes();plan=json.loads(planraw)
 need(hashlib.sha256(planraw).hexdigest()==a['prior_capture_exclusion_sha256']and plan['schema']=='EXACT33_ACTUAL_CLOSED_CAPTURE_EXCLUSION_V4','EXACT_PRIOR_CLOSED_CAPTURE_PLAN')
 need(ids==plan['remaining_ordered_job_ids']and not(set(ids)&set(plan['closed_capture_job_ids'])),'NEVER_RECAPTURE_CLOSED_INPUTS')
 need(a.get('Root_known_comfy_nonperformance_policy_ref')is not None,'ROOT_SHARED_KNOWN_COMFY_POLICY_REQUIRED')
 need(1793128044.0<=a['Root_GPU_not_before_unix']<DEADLINE and a['SC_CPU_ONLY_active_GPU_allowed']is False,'HUMAN_GPU_HOLD_AND_SC_CPU_ONLY_BLOCK')
 need(1<=a['canonical_shared_wait_seconds']<=900 and 1<=a['inter_job_yield_seconds']<=10,'BOUNDED_FAIR_SHARED_WAIT')
 v=a.get('SC_positive_closure');need(type(v)is dict and all(type(v.get(k))is str and v[k]for k in ['remote_run_root','run_id','scope_sha256','code_manifest_sha256','scope_schema']),'ROOT_EXACT_SC_POSITIVE_CLOSURE_REQUIRED')
 need(a['stop_after_first_closed_job']is True,'ROOT_INITIAL_SINGLE_JOB_PILOT')
 z=a['Native_bridge_policy'];need(z['schema']=='ROOT_EXACT33_NATIVE_LIGHT_BRIDGE_POLICY_V1'and z['role']=='ORDINARY33_CAPTURE_ONLY_CONTROL_NAS'and z['actors']==3 and z['each_actor_AS_bytes']==512*2**20 and z['host_floor_bytes']>=67*G and z['cgroup_floor_bytes']>=51*G,'NATIVE_CAPTURE_CONTROL_ROLE')
 need(z['Native_POST_or_trace_payload_allowed']is False and z['foreign_current_SPEC_identity_and_cap_check_required']is True,'NO_NATIVE_HEAVY_POST_OR_FOREIGN_BYPASS')
 need(a['remote_foreign_future_cap_authority_complete']is False,'NO_INVENTED_FOREIGN_FUTURE_AUTHORITY')
 need(a['Native_control_RAM_bytes']==2*G and a['remote_headroom_bytes']==32*G and a['Root_SC_POST_reserved_RAM_bytes']==10*G,'EXPLICIT_TWO_HEAVY_PHASE_RESOURCES')
 need(a['Root_SC_capture_reservation_bytes']==8*G,'SC_MUST_RESERVE_CAPTURE8_NOT_OLD4')
 need(a['SC_success_is_capture_prerequisite']is False and a['POST_or_archive_in_GPU_service_allowed']is False,'CAPTURE_POST_SPLIT')
 need(set(a['job_limits'])==set(ids),'ALL_JOB_LIMITS')
 for jid in ids:
  v=a['job_limits'][jid];j=allowlist['jobs'][jid];need(v['memory_max_bytes']in[8*G,20*G],'CAPTURE8_OR20_HARD')
  need(0<v['capture_timeout_sec']<=j['maximum_capture_timeout_sec']and 0<v['capture_max_bytes']<=j['maximum_capture_bytes'],'FINITE_ORIGINAL_CAPS')
  need(v['memory_max_bytes']!=20*G or v['require_SC_POST_inactive']is True,'LARGE_CAPTURE_SERIAL_POLICY')
 need(all(x['Root_reviewed']is True for x in a['known_remote_residents']),'KNOWN_RESIDENTS_ROOT_REVIEW')
 return a
def validate_mutual(a,m):
 peer=a['SC_POST_peer_locator']
 need(peer is not None and m['schema']=='ROOT_SC_POST_ORDINARY33_MUTUAL_ADMISSION_V1'and m['status']=='ROOT_APPROVED','ROOT_STATIC_MUTUAL')
 need(m['campaign_id']==a['campaign_id']and m['capture_code_manifest_sha256']==a['code_manifest_sha256'],'EXACT_CAPTURE_CAMPAIGN_CODE')
 need(m['Native_runtime_root']==str(NB)and m['remote_runtime_root']==str(RB),'EXACT_CAPTURE_ROOTS')
 need(m['SC_run_id']==peer['run_id']and m['SC_code_manifest_sha256']==peer['code_manifest_sha256'],'EXACT_STATIC_SC_RUN_CODE')
 need(m['SC_cpu_ids']==list(range(8))and m['SC_max_CPU_percent']==800 and a['remote_cpu_ids']==[8,9],'EXACT_COACTIVITY_CPU_SETS')
 need(m['capture_memory_bytes']==8*G and m['SC_capture_reserved_bytes']==8*G and m['SC_service_memory_bytes']==10*G and m['headroom_bytes']==32*G,'EXACT_MUTUAL_MEMORY')
 need(m['max_concurrent_capture_services']==1 and m['twenty_GiB_with_active_SC_allowed']is False and m['original_absolute_deadline_unix']==DEADLINE,'FINITE_SERIAL_CAPTURE8_ONLY')
 return m

def physical_ram(available,own_remaining,SC_remaining):
 required=own_remaining+SC_remaining+32*G;need(available>=required,'CAPTURE_AND_POST_PHYSICAL_RAM')
 return dict(MemAvailable_bytes=available,own_remaining_bytes=own_remaining,SC_remaining_bytes=SC_remaining,headroom_bytes=32*G,required_bytes=required,status='PASS')
def job_parameters(a,allowlist,jid):
 need(jid in a['ordered_job_ids']and jid in allowlist['jobs'],'EXACT_JOB_ID');j=allowlist['jobs'][jid];v=a['job_limits'][jid]
 return j,v
def post_binding(a,jid,root,leaf):
 need(leaf['status']=='LEAF_CAPTURE_FINISHED_POST_UNVALIDATED'and leaf['job_id']==jid,'CAPTURE_POSITIVE_COMPLETION')
 need(leaf['full_record_validation_complete']is False and leaf['POST_complete']is False,'NO_FALSE_POST_QUALIFICATION')
 return dict(schema='EXACT33_CAPTURED_POST_PENDING_V1',status='CAPTURED_POST_PENDING',job_id=jid,campaign_id=a['campaign_id'],capture_root=str(root),leaf_receipt_ref=ref(root/'LEAF_CAPTURED.json'),raw_body_SHA_status='DEFERRED_TO_CPU_POST',full_record_validation_complete=False,POST_complete=False,consumer_qualification=False,scientific_qualification=False,source_KEEP=True)
