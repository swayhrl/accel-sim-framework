"""Exact frozen33 capture-only contract; no import-time execution/query."""
import pathlib,os,sys,json,hashlib,time,stat,resource,shutil,re
G=2**30
NAME='repeat_only4_queue_prepare_20261029_v3'
NB=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates')/NAME/'runtime'
RB=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2/private_candidates')/NAME/'runtime'
DEADLINE=0.0
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
 p=pathlib.Path(p);raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();need(len(raw)<=8*2**20,'BOUNDED_JSON_PUBLICATION')
 tmp=p.with_name(p.name+'.tmp_publish_'+str(os.getpid())+'_'+str(time.monotonic_ns()))
 fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  # Same-filesystem hardlink publishes the complete closed inode once; EEXIST never overwrites.
  os.link(tmp,p,follow_symlinks=False)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
class HandshakeJSONReadError(RuntimeError):
 def __init__(self,path,observations):
  super().__init__('HANDSHAKE_JSON_NOT_COMPLETE_WITHIN_ORIGINAL_DEADLINE:'+str(path));self.raw_observations=observations
def read_handshake_json(p,deadline):
 p=pathlib.Path(p);until=min(float(deadline),time.monotonic()+2);observations=[]
 while True:
  if time.monotonic()>until:raise HandshakeJSONReadError(p,observations)
  try:
   no_links(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
   try:
    a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<=a.st_size<=8*2**20,'HANDSHAKE_BOUNDED_REGULAR');parts=[];total=0
    while True:
     b=os.read(fd,min(65536,8*2**20+1-total))
     if not b:break
     total+=len(b);need(total<=8*2**20,'HANDSHAKE_READ_CAP');parts.append(b)
    raw=b''.join(parts);z=os.fstat(fd);key=lambda q:(q.st_dev,q.st_ino,q.st_size,q.st_mtime_ns,q.st_ctime_ns)
    need(key(a)==key(z)and len(raw)==a.st_size,'HANDSHAKE_SAMEFD_METADATA')
   finally:os.close(fd)
   observations.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),unix=time.time()));observations=observations[-8:]
   parsed=json.loads(raw);need(time.monotonic()<=until,'HANDSHAKE_READ_DEADLINE');return parsed,observations
  except(FileNotFoundError,json.JSONDecodeError)as e:
   if isinstance(e,FileNotFoundError):observations.append(dict(path=str(p),error='ENOENT',unix=time.time()));observations=observations[-8:]
   if time.monotonic()>=until:raise HandshakeJSONReadError(p,observations)from e
   time.sleep(min(.02,max(0,until-time.monotonic())))
def rawmodule(p,h,name):
 b=pathlib.Path(p).read_bytes();need(hashlib.sha256(b).hexdigest()==h,'PINNED_SOURCE_BYTES');m=type(sys)(name);m.__file__=str(p);m.__source_sha256__=h;exec(compile(b,str(p),'exec'),m.__dict__);return m
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
def cpu_coactivity_policy(a):
 r=a['Root_109_CPU_coactivity_policy_ref'];need(r['sha256']=='c2a82cb5c89d4e6cdbc9fabf0106eed45a4acf3eb5602e01748ca763da17d49e','ROOT_EXACT_CPU_COACTIVITY_POLICY')
 key='remote_path'if str(__file__).startswith('/data/c16/')else'native_path'
 p=readref(dict(path=r[key],bytes=r['bytes'],sha256=r['sha256']))
 need(p['schema']=='ROOT_109_BOUNDED_EP_CPU_COACTIVITY_POLICY_V1'and p['status']=='ROOT_APPROVED_FOR_NEW_FROZEN_CAPTURE_CONTROL_ONLY'and p['scientific_qualification_or_budget_or_history_changed']is False,'CPU_COACTIVITY_POLICY_SCOPE')
 return p

def validate_scope(a,allowlist,now=None):
 now=time.time()if now is None else now
 need(a['schema']=='ROOT_REPEAT_ONLY4_QA_OR_CAPTURE_V1'and a['status']=='ROOT_APPROVED_CAPTURE_ONLY','ROOT_SCOPE_NOT_APPROVED')
 need(re.fullmatch('[A-Za-z0-9_]{1,60}',a['campaign_id'])is not None,'CAMPAIGN_ID')
 global DEADLINE
 need(a['queue_stage']in['NATIVE_QA','CAPTURE']and a['not_before_unix']<=now<a['queue_absolute_deadline_unix']<=a['not_before_unix']+28800,'EXACT_NEW_PILOT_STAGE_CLOCK');DEADLINE=a['queue_absolute_deadline_unix']
 pilot_conditions(a,allowlist)
 need(a['Native_runtime_root']==str(NB)and a['remote_runtime_root']==str(RB),'EXACT_CODE_ROOT')
 for jid in a['ordered_job_ids']:
  j=allowlist['jobs'][jid];job=readref(dict(path=str(pathlib.Path(__file__).parent/j['job_relative']),bytes=j['job_bytes'],sha256=j['job_sha256']));validate_job_declaration(job,j.get('family')or j.get('program'))
 ids=a['ordered_job_ids'];need(ids and len(ids)==len(set(ids))and set(ids)<=set(allowlist['jobs']),'EXACT33_ALLOWLIST')
 need(1<=len(allowlist['jobs'])<=4 and a['repeat4_attestation_sha256']==allowlist['repeat4_attestation_ref']['sha256'],'ALLOWLIST_BINDING')
 planpath=pathlib.Path(__file__).parent/'PRIOR_CAPTURE_EXCLUSION_V4.json';planraw=planpath.read_bytes();plan=json.loads(planraw)
 need(hashlib.sha256(planraw).hexdigest()==a['prior_capture_exclusion_sha256']and plan['schema']=='EXACT_REPEAT_ONLY4_NEW_INPUT_EXCLUSION_V1','EXACT_PRIOR_CLOSED_CAPTURE_PLAN')
 need(ids==[jid for jid in plan['remaining_ordered_job_ids']if jid in set(ids)]and set(ids)<=set(plan['remaining_ordered_job_ids'])and not(set(ids)&set(plan['closed_capture_job_ids'])),'ORDERED_NONEMPTY_SUBSET_NEVER_RECAPTURE_CLOSED_INPUTS')
 need(a.get('Root_known_comfy_nonperformance_policy_ref')is not None,'ROOT_SHARED_KNOWN_COMFY_POLICY_REQUIRED')
 need(1793128044.0<=a['Root_GPU_not_before_unix']<DEADLINE and a['SC_CPU_ONLY_active_GPU_allowed']is False,'HUMAN_GPU_HOLD_AND_SC_CPU_ONLY_BLOCK')
 need(1<=a['canonical_shared_wait_seconds']<=900 and 1<=a['inter_job_yield_seconds']<=10,'BOUNDED_FAIR_SHARED_WAIT')
 v=a.get('SC_positive_closure');need(type(v)is dict and all(type(v.get(k))is str and v[k]for k in ['remote_run_root','run_id','scope_sha256','code_manifest_sha256','scope_schema']),'ROOT_EXACT_SC_POSITIVE_CLOSURE_REQUIRED')
 need(type(a['stop_after_first_closed_job'])is bool,'ROOT_TYPED_STOP_AFTER_FIRST_CLOSED_JOB')
 z=a['Native_bridge_policy'];need(z['schema']=='ROOT_REMOTE_CAPTURE_CONTROL_PHYSICAL_ROLE_V4'and z['role']=='REMOTE_CAPTURE_CONTROL_NAS_BOUNDED2'and z['actors']==3 and z['each_actor_AS_bytes']==512*2**20 and z['total_control_envelope_bytes']==2*G and z['host_floor_bytes']==16*G and z['cgroup_floor_bytes']==8*G and z['Native_payload_POST_hash_parse_copy_model_allowed']is False,'NATIVE_ROLE4_CONTROL_ONLY')
 need(a['Native_control_role_decision_ref']['sha256']=='7669ce3ba6da5092e8df08cc485471ad35ed661851af7e530b3a3944c84363a0','EXACT_ROOT_ROLE4_DECISION')
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
 cpu_coactivity_policy(a)
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

def physical_ram(available,own_remaining,SC_remaining,headroom_bytes=32*G):
 need(headroom_bytes in [16*G,32*G],'EXACT_APPROVED_PHYSICAL_HEADROOM_PROFILE')
 required=own_remaining+SC_remaining+headroom_bytes;need(available>=required,'CAPTURE_AND_POST_PHYSICAL_RAM')
 return dict(MemAvailable_bytes=available,own_remaining_bytes=own_remaining,SC_remaining_bytes=SC_remaining,headroom_bytes=headroom_bytes,required_bytes=required,status='PASS')
def job_parameters(a,allowlist,jid):
 need(jid in a['ordered_job_ids']and jid in allowlist['jobs'],'EXACT_JOB_ID');j=allowlist['jobs'][jid];v=a['job_limits'][jid]
 return j,v
def post_binding(a,jid,root,leaf):
 need(leaf['status']=='LEAF_CAPTURE_FINISHED_POST_UNVALIDATED'and leaf['job_id']==jid,'CAPTURE_POSITIVE_COMPLETION')
 need(leaf['full_record_validation_complete']is False and leaf['POST_complete']is False,'NO_FALSE_POST_QUALIFICATION')
 return dict(schema='EXACT33_CAPTURED_POST_PENDING_V1',status='CAPTURED_POST_PENDING',job_id=jid,campaign_id=a['campaign_id'],capture_root=str(root),leaf_receipt_ref=ref(root/'LEAF_CAPTURED.json'),raw_body_SHA_status='DEFERRED_TO_CPU_POST',full_record_validation_complete=False,POST_complete=False,consumer_qualification=False,scientific_qualification=False,source_KEEP=True)

FAMILIES={'scan','alignedTypes','transpose','convolutionSeparable'}
def pilot_conditions(a,allowlist):
 ids=a['ordered_job_ids'];need(1<=len(ids)<=4 and set(ids)<=set(allowlist['jobs']),'EXACT1_TO4_FROZEN_REPEAT_INPUTS')
 families=[allowlist['jobs'][jid].get('family')or allowlist['jobs'][jid].get('program')for jid in ids]
 need(len(set(families))==len(families)and set(families)<=FAMILIES,'EXACT_FAMILY_NO_DUPLICATE')
 need('scan'not in families or families[0]=='scan','SCAN_FIRST_WHEN_INCLUDED')
 need(a['complete_capture_required']is True and a['CPUpost_fullF9_separate_required']is True and a['partial_capture_as_complete_allowed']is False,'COMPLETE_INPUT_NO_POST_BYPASS')
 for jid,v in a['job_limits'].items():
  cap=600 if a['queue_stage']=='NATIVE_QA' else 7200
  bound=128*2**20 if a['queue_stage']=='NATIVE_QA' else 2*G
  need(v['require_SC_POST_inactive']is True and 0<v['capture_timeout_sec']<=cap and 0<v['capture_max_bytes']<=bound,'FINITE_ROOT_REVIEWED_QA600_CAPTURE2H_2G_POLL_NOT_QUOTA')
 if a['queue_stage']=='CAPTURE':native_qa_accepted(a)
 if str(__file__).startswith('/data/c16/'):
  m=rawmodule(pathlib.Path(__file__).parent/'existing_st_alias_guard_reused_v1.py','268fe67e14d8709987efb971593ed6d6f5d83a117f9c3d20a7be6e728b61d7fc','repeat_existingST')
  H=rawmodule(pathlib.Path(__file__).parent/'tools/reviewed_mvt_committer.py','1dd52a5789936d0ae19ce0388d39c09b29615e49218fed11a7a0b0cf3f74521f','repeat_ST_H')
  m.exact_existing_ST_alias(a,H)
def validate_job_declaration(job,family):
 t=job['task'];p=t['profile'];c=t['repeat_only_source_contract']
 need(t['program']==family and c['family']==family and family in FAMILIES,'EXACT_FAMILY_JOB_CONTRACT')
 need(c['schema']=='FROZEN_REPEAT_ONLY_PROGRAM_SOURCE_STDOUT_CONTRACT_V1'and c['profile']==p and c['argv']==t['argv']and c['binary_sha256']==t['binary_sha256'],'FROZEN_SOURCE_CONTRACT')
 need(re.fullmatch('[0-9a-f]{64}',t['binary_sha256'])is not None and re.fullmatch('[0-9a-f]{64}',c['Root_source_acceptance_ref']['sha256'])is not None,'REAL_SOURCE_BINARY_ACCEPTANCE_NOT_UNKNOWN')
 need(c['only_repeat_literal_source_delta']is True and c['spatial_N_shape_type_grid_block_unchanged']is True and c['original_warmup_preserved']is True,'REPEAT_ONLY_METHOD_BOUND')
 need(type(p['expected_kernels'])is int and 0<p['expected_kernels']<=100000 and len(c['stdout_constraints'])in range(1,33),'DECLARED_COMPLETE_KERNEL_AND_QA_BOUND')
 re.compile(t['correctness']['stdout_regex'])
 for row in c['stdout_constraints']:
  need(0<=row['min_count']<=row['max_count']<=100000 and len(row['pattern'])<=512,'BOUNDED_STDOUT_CONSTRAINT');re.compile(row['pattern'])
 input_libc_identity(t)
 return True
def profile_stdout(job,text):
 t=job['task'];p=t['profile'];c=t['repeat_only_source_contract']
 need(c['schema']=='FROZEN_REPEAT_ONLY_PROGRAM_SOURCE_STDOUT_CONTRACT_V1'and c['family']in FAMILIES and c['family']==t['program'],'FROZEN_PROGRAM_PROFILE_CONTRACT')
 need(c['binary_sha256']==t['binary_sha256']and c['argv']==t['argv']and c['profile']==p,'SOURCE_CONTRACT_BINARY_ARGV_PROFILE')
 need(re.fullmatch('[0-9a-f]{64}',c['Root_source_acceptance_ref']['sha256'])is not None and c['only_repeat_literal_source_delta']is True,'ROOT_SOURCE_DELTA_ACCEPTANCE_REQUIRED')
 need(c['spatial_N_shape_type_grid_block_unchanged']is True and c['original_warmup_preserved']is True,'NO_SPATIAL_OR_WARMUP_REDUCTION_IN_REPEAT_PROFILE')
 qa=t['correctness']['stdout_regex'];need(type(qa)is str and 0<len(qa)<=512 and re.search(qa,text)is not None,'ORIGINAL_NUMERIC_QA_STDOUT_REQUIRED')
 checks=c['stdout_constraints'];need(type(checks)is list and 1<=len(checks)<=32,'FROZEN_ORIGINAL_STDOUT_CONSTRAINTS')
 observed=[]
 for item in checks:
  pattern=item['pattern'];need(type(pattern)is str and 0<len(pattern)<=512,'BOUNDED_ROOT_STDOUT_PATTERN')
  matches=list(re.finditer(pattern,text));need(item['min_count']<=len(matches)<=item['max_count'],'ORIGINAL_STDOUT_PARAMETER_OR_CASE_COUNT')
  groups=[list(m.groups())for m in matches]
  if 'expected_groups'in item:need(groups==item['expected_groups'],'ORIGINAL_STDOUT_PARAMETER_GROUPS')
  observed.append(dict(pattern=pattern,count=len(matches),groups=groups))
 return dict(profile=p,original_QA_pattern=qa,observed_original_stdout_constraints=observed,input_identity_basis=t['input_reconstruction'],input_byte_SHA_observed=False,no_new_program_markers_required=True,numerical_equivalence=c['numerical_equivalence_scope'])
def native_qa_accepted(a):
 r=a.get('Root_native_QA_owned_acceptance_ref');need(type(r)is dict,'REAL_NATIVE_QA4_ACCEPTANCE_REQUIRED')
 path=r['remote_path']if str(__file__).startswith('/data/c16/')else r['native_path']
 q=readref(dict(path=path,bytes=r['bytes'],sha256=r['sha256']))
 need(q['schema']=='ROOT_REPEAT_ONLY4_ACTUAL_QA_AND_OWNED_ACCEPTANCE_V1'and q['owned_closed']is True and q['Native4_independently_free']is True,'ACTUAL_QA2_OWNED_REQUIRED')
 need(set(q['rows'])==set(a['ordered_job_ids']),'EXACT_SELECTED_QA_ROW_SET')
 for jid,z in q['rows'].items():need(z['job_id']==jid and z['exit_code']==0 and z['original_gold_QA_PASS']is True and z['no_tracer_injection']is True,'REAL_NATIVE_QA_NOT_PRODUCER')
 return q

def pilot_metadata_path(p):
 p=pathlib.Path(p)
 native=NB.parents[2];remote=RB.parents[2]
 for base in[native,remote]:
  if p.is_relative_to(base):
   rel=p.relative_to(base);need('..'not in rel.parts,'PILOT_METADATA_CANONICAL')
   return (remote if str(__file__).startswith('/data/c16/')else native)/rel
 raise RuntimeError('PILOT_METADATA_DOMAIN')
def input_libc_identity(task,verify=False):
 r=task['input_reconstruction'];kind=r['kind']
 need(kind in ['SOURCE_SEEDED_LIBC_RAND','DETERMINISTIC_INDEX_PATTERN'],'EXPLICIT_INPUT_RECONSTRUCTION_KIND')
 if kind=='SOURCE_SEEDED_LIBC_RAND':
  c=r['libc'];need(c['sha256']and c['bytes']>0 and r['seed']is not None,'SEEDED_LIBC_DECLARATION')
  if verify:need(sha(pathlib.Path(c['path']))==c['sha256'],'ACTUAL_LIBC_INPUT_GENERATOR_PIN')
  return c['sha256']
 need(r['libc_input_dependency']=='NOT_APPLICABLE'and r['formula'],'NO_RNG_FORMULA_REQUIRED')
 return 'NOT_APPLICABLE_TO_GENERATOR'
def qa_row(a,job):
 q=native_qa_accepted(a);z=q['rows'][job['id']];r=z['qa_result_ref'];actual=readref(dict(path=str(pilot_metadata_path(r['path'])),bytes=r['bytes'],sha256=r['sha256']))
 need(actual['status']=='NATIVE_QA_PASS_NOT_CAPTURED'and actual['job_id']==job['id']and actual['exit_code']==0 and actual['no_tracer_injection']is True,'ACTUAL_NATIVE_QA_RESULT')
 need(actual['argv']==job['task']['argv']and actual['binary_sha256']==job['task']['binary_sha256']and actual['libc_sha256']==input_libc_identity(job['task'])and actual['parsed_profile']['profile']==job['task']['profile'],'ACTUAL_NATIVE_QA_INPUT_JOIN')
 return actual
