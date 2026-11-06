"""Bounded read-only Oracle admission/archive native-space forecasting.

Not used by the high-frequency runtime guard. No registry mutations or model
invocations. Historical files already included in statvfs are never subtracted.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,types
P=Path;G=1024**3;M=1024**2
R1=P('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1/tools/perf16r1_resources.py')
R1_SHA='e5ac53287a70bc58dd63c25a3434ea3a5578220c2bced5d2e8f72506957580c1'
N=P('/root/data/ep_l2_dtc_l1_native_v2')
def sha(path):return hashlib.sha256(P(path).read_bytes()).hexdigest()
def read(path):return json.loads(P(path).read_bytes())
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def require(x,msg):
 if not x:raise RuntimeError(msg)
def load(name,path):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(P(path).read_bytes(),str(path),'exec'),m.__dict__);return m
def _native(path):
 p=P(path);require(p.is_absolute()and p.stat().st_dev==2128,'NOT_NATIVE_DEVICE_2128:'+str(p));return p
def _size(path):
 p=P(path)
 if not p.exists():return 0
 _native(p);n=0;count=0
 for base,dirs,files in os.walk(p,followlinks=False):
  for name in files:
   z=P(base)/name
   if z.is_symlink():continue
   s=z.stat();require(s.st_dev==2128,'RESULT_NON_NATIVE_FILE');n+=s.st_size;count+=1
   require(count<=10000,'RESULT_METADATA_ENTRY_BOUND')
 return n
def _closed_projection(r1,peer,root,q,metadata):
 claims=peer.claims(root);d=r1._dynamic(peer,root,q,claims,metadata)
 exact=(q.get('remaining')==0 and type(q.get('budget'))is int and q['budget']==len(q['consumed'])and set(claims)<=set(q['consumed'])and d['exact_archived_nonlive_count']==q['budget']and not d['writes'])
 # Release future metadata only after *all* consumed exact UUIDs have a fresh
 # registry/INTENT/DONE/NATIVE_EXIT + SOURCE_KEEP typed-restore receipt join and
 # no live process generation. No existing file bytes are removed from df.
 future=0 if exact else d['projected_write_bytes']
 return {'request':q['request'],'root':str(root),'registered_reserved_write_bytes':q['reserved_write_bytes'],'projected_future_write_restore_bytes':future,'fresh_exact_archived_nonlive_count':d['exact_archived_nonlive_count'],'consumed_n':len(q['consumed']),'budget':q['budget'],'remaining':q['remaining'],'all_exact_closed_nonlive':exact,'write_entries':d['writes'],'future_metadata_bytes':0 if exact else metadata,'existing_native_bytes_removed_from_df':0,'q_sha256':digest(q),'claims_sha256':digest(claims),'within_registered_ceiling':future<=q['reserved_write_bytes']}
def _own_projection(peer,root,q,spec=None,registered=True):
 root=_native(root);claims=peer.claims(root);consumed=q.get('consumed',{});require(isinstance(consumed,dict),'OWN_CONSUMED_SCHEMA');require(set(claims)<=set(q['admitted_specs']),'OWN_CLAIM_NOT_ADMITTED')
 metadata=256*M
 technical=q['maximum_source_plus_restore_lifetime_bytes'];require(type(technical)is int and technical>=metadata,'OWN_TECHNICAL_CEILING_MISSING_OR_INVALID')
 require(type(q['reserved_write_bytes'])is int and metadata<=q['reserved_write_bytes']<=technical,'OWN_DYNAMIC_RESERVATION_INVALID')
 specs={};maximum_cap=0
 for c,pin in q['admitted_specs'].items():
  spath=root/'control/specs'/(c+'.json');sp=read(spath);require(sha(spath)==pin,'OWN_ADMITTED_SPEC_SHA_DRIFT')
  cap=sp['limits']['max_result_directory_bytes'];require(type(cap)is int and cap>0,'OWN_CAP_UNBOUNDED');specs[c]=sp;maximum_cap=max(maximum_cap,cap)
 if spec is not None:require(spec['cohort']in specs,'OWN_CANDIDATE_NOT_ADMITTED')
 pending=set(claims)-set(consumed)
 active_source=0;active_restore=0;detail=[];archived_count=0
 for c,row in consumed.items():
  sp=specs[c];out=root/'DTC/run/results'/row['uuid'];observed=_size(out);rss,live=peer.rss(root,row);archived=peer.archived(root,c,row)
  if archived and not live:
   archived_count+=1;detail.append({'cohort':c,'uuid':row['uuid'],'exact_archived_nonlive':True,'future_write_bytes':0,'restore_window_demand_bytes':0});continue
  cap=sp['limits']['max_result_directory_bytes'];require(observed<=cap,'OWN_OUTPUT_CAP_EXCEEDED');done=bool(row.get('execution_receipt'))
  w=16*M if done and not live else max(0,cap-observed)
  active_source+=w;active_restore=max(active_restore,cap)
  detail.append({'cohort':c,'uuid':row['uuid'],'observed_result_bytes':observed,'observed_live':live,'observed_RSS_bytes':rss,'execution_receipt_present':done,'archive_join':archived,'future_write_bytes':w,'restore_window_demand_bytes':cap})
 for c in sorted(pending):
  cap=specs[c]['limits']['max_result_directory_bytes'];require(claims[c]['result_cap_bytes']==cap,'OWN_CLAIM_CAP_DRIFT')
  active_source+=cap;active_restore=max(active_restore,cap);detail.append({'cohort':c,'claimed_not_consumed':True,'future_write_bytes':cap,'restore_window_demand_bytes':cap})
 # One archive worker: a stage holds ONE restore window, not cap per model.
 # Authorized but unclaimed rows are not actual restore windows. An empty
 # stage retains metadata only, even if96 future rows remain authorized.
 idle_restore=0
 live_restore=max(active_restore,idle_restore)
 active_metadata=metadata
 if not registered and spec is None:
  require(not claims and not consumed,'INACTIVE_UNREGISTERED_STAGE_HAS_WORK')
  active_source=live_restore=active_metadata=idle_restore=0
 live_total=active_source+live_restore+active_metadata
 require(live_total<=q['reserved_write_bytes'],'OWN_LIVE_WINDOWS_EXCEED_DYNAMIC_RESERVATION_PAUSE_NEW')
 extra_source=extra_restore=0
 if spec is not None and spec['cohort']not in claims and spec['cohort']not in consumed:
  cap=specs[spec['cohort']]['limits']['max_result_directory_bytes'];extra_source=cap;extra_restore=max(0,cap-live_restore)
 prospective_source=active_source+extra_source;prospective_restore=live_restore+extra_restore
 prospective_total=prospective_source+prospective_restore+active_metadata
 require(prospective_total<=technical,'OWN_PROSPECTIVE_WINDOWS_EXCEED_TECHNICAL_CEILING')
 return {'own_future_write_bytes':prospective_source,'native_restore_bytes':prospective_restore,'entries':detail,'q_sha256':digest(q),'claims_sha256':digest(claims),'all_unclaimed_future_cells_charged':False,'existing_native_bytes_removed_from_df':0,'registered_stage':registered,'metadata_reserve_bytes':active_metadata,'idle_restore_floor_bytes':idle_restore,'single_restore_window':True,'archive_workers_required':1,'live_actual_source_write_bytes':active_source,'live_actual_native_restore_bytes':live_restore,'live_actual_projection_bytes':live_total,'dynamic_registered_reserved_write_bytes':q['reserved_write_bytes'],'prospective_candidate_extra_write_bytes':extra_source,'prospective_candidate_extra_restore_bytes':extra_restore,'prospective_candidate_extra_bytes':extra_source+extra_restore,'prospective_projection_bytes':prospective_total,'maximum_source_plus_restore_lifetime_bytes':technical,'exact_archived_nonlive_n':archived_count}

def _worker(spec,plan):
 start=time.monotonic();require(plan['archive_workers']==1,'SINGLE_RESTORE_WINDOW_REQUIRES_ONE_ARCHIVE_WORKER');require(sha(R1)==R1_SHA,'R1_PEER_REFERENCE_SOURCE_DRIFT');r1=load('oracle_readonly_reference_r1',R1);peer=r1._peer()
 reg,ep=r1.bounded_authority(timeout_seconds=.20);require(ep['epoch']==2,'NOT_EPOCH2');regsha=digest(reg)
 # All legacy/private helpers see the same already unlocked read-only snapshot;
 # no recursive flock, no registry lock held while reading native/FUSE files.
 peer.authority=lambda:(reg,ep)
 b=peer.resources({'request':peer.ORIG,'cohort':'CONTROLLED_ORACLE_READONLY_PEER_ACCOUNTING'},False)
 require(all(b['per_scope_write_ceiling_pass'].values()),'LEGACY_SCOPE_WRITE_CEILING_HOLD')
 closed=r1._closed_known_metadata(peer,reg,b)
 # Preserve the actual old356/sealed72/R20 departure projection. Release only
 # exact1GiB metadata scopes independently proven by the existing reference.
 legacy=sum(b['known_remaining_writes_by_request'].values())-closed['released_future_metadata_bytes'];require(legacy>=0,'NEGATIVE_LEGACY_FORECAST')
 roots={r1.STAGE1_REQ:(r1.STAGE1,G),r1.FIRST16_REQ:(r1.FIRST16,256*M),r1.REMAINING48_REQ:(r1.REMAINING48,256*M),r1.FIRST4_REQ:(r1.FIRST4,256*M),r1.V1_REMAINING28_REQ:(r1.V1_REMAINING28,256*M),r1.OLD_NEGATIVE16_REQ:(r1.OLD_NEGATIVE16,256*M),r1.REQ:(r1.R,256*M)}
 projections={}
 for request,(root,metadata)in roots.items():
  q=reg['registered_future_requests'][request];_native(root);projections[request]=_closed_projection(r1,peer,root,q,metadata);require(projections[request]['within_registered_ceiling'],'PEER_SCOPE_WRITE_CEILING_HOLD:'+request)
 ownrequest=spec.get('request',plan['request']);require(ownrequest==plan['request'],'OWN_REQUEST_MISMATCH')
 root=P(plan['execution_root']);_native(root)
 oracle_roots=dict(plan.get('oracle_request_roots',{}))
 if not oracle_roots:
  for z in plan['shared_pool_roots']:
   rp=_native(z);request=read(rp/'control/EXECUTION_PLAN.json')['request'];require(request not in oracle_roots,'DUPLICATE_ORACLE_STAGE_REQUEST');oracle_roots[request]=str(rp)
 require(oracle_roots.get(ownrequest)==str(root),'OWN_ROOT_NOT_SHARED_POOL_BOUND')
 require(len(oracle_roots)==len(set(oracle_roots.values()))==2,'EXACT_TWO_ORACLE_STAGE_ROOTS_REQUIRED')
 stage_q={};stage_claims={};stage_windows={}
 for request,z in oracle_roots.items():
  rp=_native(z)
  if request in reg['registered_future_requests']:q=reg['registered_future_requests'][request]
  else:q=read(rp/'control/REGISTRY_REQUEST_CANDIDATE.json')
  require(q['request']==request,'ORACLE_STAGE_REQUEST_MISMATCH')
  require(q['budget']==len(q['admitted_specs']),'ORACLE_STAGE_ADMITTED_COUNT_MISMATCH')
  require(q['remaining']==q['budget']-len(q['consumed']),'ORACLE_STAGE_BUDGET_CONSERVATION')
  require(read(rp/'control/EXECUTION_PLAN.json')['request']==request,'ORACLE_STAGE_PLAN_REQUEST_DRIFT')
  stage_q[request]=q;stage_claims[request]=peer.claims(rp)
  if request not in reg['registered_future_requests']:require(not stage_claims[request]and not q['consumed'],'UNREGISTERED_STAGE_HAS_SCIENTIFIC_CLAIM_OR_CONSUMPTION')
  stage_windows[request]=_own_projection(peer,rp,q,spec if request==ownrequest else None,registered=request in reg['registered_future_requests'])
 poolpath=P(plan['shared_pool_dispatch_reservations_path']);_native(poolpath.parent)
 if poolpath.exists():
  pool=read(poolpath);require(pool['schema']=='DTC_CONTROLLED_ORACLE_SHARED_POOL_CLAIMS_V1','SHARED_POOL_SCHEMA')
  registered_roots={request:z for request,z in oracle_roots.items()if request in reg['registered_future_requests']}
  require(pool['requests']==registered_roots,'SHARED_POOL_REGISTERED_REQUEST_ROOT_BINDING')
  expected={request+':'+c:(request,c,row)for request,claims in stage_claims.items()for c,row in claims.items()}
  require(set(pool['claims'])==set(expected),'SHARED_AND_STAGE_POOL_CLAIMS_DIFFER')
  for key,(request,c,row)in expected.items():
   pr=pool['claims'][key];require(pr['request']==request and pr['execution_root']==oracle_roots[request]and pr['cohort']==c,'SHARED_POOL_CLAIM_IDENTITY')
   require(row==pr,'SHARED_AND_STAGE_CLAIM_RECORD_DRIFT')
   qp=stage_q[request]['consumed'].get(c)
   if pr.get('uuid')is not None:require(qp and pr['uuid']==qp['uuid'],'SHARED_POOL_CLAIM_UUID_DRIFT')
  sharedproof={'path':str(poolpath),'sha256':sha(poolpath),'claim_count':len(pool['claims']),'stage_claims_exact':True,'registered_request_roots':registered_roots,'predeclared_request_roots':oracle_roots,'owner_pid':pool['owner_pid'],'owner_start_ticks':pool['owner_start_ticks']}
 else:
  require(all(x not in reg['registered_future_requests']for x in oracle_roots),'SHARED_POOL_MISSING_AFTER_REGISTRATION')
  require(all(not stage_claims[x]and not stage_q[x]['consumed']for x in oracle_roots),'SHARED_POOL_MISSING_AFTER_CLAIM_OR_CONSUMPTION')
  sharedproof={'path':str(poolpath),'stage':'UNREGISTERED_EMPTY_PREFLIGHT_ONLY','claim_count':0,'stage_claims_exact':True}
 own=stage_windows[ownrequest]
 cross_oracle=sum(v['live_actual_projection_bytes']for request,v in stage_windows.items()if request!=ownrequest)
 # Unknown/foreign EP reservations are retained byte-for-byte; closed roots
 # above are replaced only by the fresh exact lifecycle evidence projection.
 foreign=[x for x in b['peer_reservations']if x['request']not in roots and x['request']not in oracle_roots]
 peerbytes=legacy+sum(x['projected_future_write_restore_bytes']for x in projections.values())+sum(x['reserved_write_bytes']for x in foreign)+cross_oracle
 after,afterep=r1.bounded_authority(timeout_seconds=.20);require(digest(after)==regsha,'REGISTRY_CHANGED_DURING_ADMISSION_PAUSE_NEW')
 now=time.time();sv=os.statvfs(root)
 return {'schema':'DTC_CONTROLLED_ORACLE_BOUNDED_NATIVE_PEER_ADAPTER_V4_DYNAMIC_WINDOWS','status':'PASS','fresh_local_native_peer_reservations':True,'native_device':root.stat().st_dev,'bounded_runtime_seconds':time.monotonic()-start,'sample_unix_seconds':now,'registry_canonical_sha256':regsha,'registry_epoch':ep['epoch'],'own_future_write_bytes':own['own_future_write_bytes'],'native_restore_bytes':own['native_restore_bytes'],'peer_future_write_bytes':peerbytes,'native_free_bytes':sv.f_bavail*sv.f_frsize,'floor_and_own_metadata_added_by_caller':True,'legacy_R20_known_future_write_restore_bytes':legacy,'legacy_R20_original356_projection_bytes':b['known_remaining_writes_by_request'][peer.ORIG],'closed_legacy_metadata_forward_projection':closed,'DTC_peer_fresh_projections':projections,'foreign_reservations_retained_unchanged':foreign,'own_metadata_reserve_bytes_added_by_caller':own['metadata_reserve_bytes'],'own_live_actual_projection_bytes':own['live_actual_projection_bytes'],'own_prospective_candidate_extra_bytes':own['prospective_candidate_extra_bytes'],'own_prospective_projection_bytes':own['prospective_projection_bytes'],'own_projection':own,'cross_oracle_stage_future_write_restore_bytes':cross_oracle,'all_oracle_stage_dynamic_windows':stage_windows,'shared_pool_proof':sharedproof,'reference_sources':[{'path':str(R1),'sha256':R1_SHA},{'path':str(r1.PEER),'sha256':r1.PEER_SHA}],'registry_or_peer_mutations':0,'signals_sent':0,'model_invocations':0}
def admission_disk_reservations(spec,plan):
 """EX-outside only. Entire child read bounded; unknown/busy => HOLD new work."""
 begin=time.monotonic();limit=float(plan.get('admission_peer_timeout_seconds',5));require(0<limit<=30,'INVALID_PEER_TIMEOUT')
 args=[sys.executable,'-I','-B',str(P(__file__).resolve()),'--worker']
 p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 try:
  out,err=p.communicate(json.dumps({'spec':spec,'plan':plan}).encode(),timeout=max(.05,limit-.05))
 except subprocess.TimeoutExpired:
  p.kill()
  try:out,err=p.communicate(timeout=.02)
  except subprocess.TimeoutExpired:out,err=b'',b'BOUNDED_READONLY_WORKER_REAP_PENDING'
  return {'status':'HOLD','reason':'BOUNDED_PEER_READ_TIMEOUT_PAUSE_NEW_ONLY','fresh_local_native_peer_reservations':False,'bounded_runtime_seconds':time.monotonic()-begin,'registry_or_peer_mutations':0,'signals_sent_to_models':0}
 elapsed=time.monotonic()-begin
 if p.returncode!=0:return {'status':'HOLD','reason':'PEER_EVIDENCE_BUSY_UNKNOWN_OR_DRIFT','detail':err.decode(errors='replace')[-4000:],'fresh_local_native_peer_reservations':False,'bounded_runtime_seconds':elapsed,'registry_or_peer_mutations':0,'signals_sent_to_models':0}
 try:value=json.loads(out)
 except ValueError:return {'status':'HOLD','reason':'PEER_WORKER_INVALID_JSON','fresh_local_native_peer_reservations':False,'bounded_runtime_seconds':elapsed}
 if elapsed>limit:return {'status':'HOLD','reason':'PEER_DEADLINE_EXCEEDED','fresh_local_native_peer_reservations':False,'bounded_runtime_seconds':elapsed}
 value['bounded_runtime_seconds']=elapsed;return value
if __name__=='__main__':
 require(sys.argv[1:]==['--worker'],'WORKER_ONLY_NO_CLI_MUTATION');v=json.loads(sys.stdin.buffer.read());print(json.dumps(_worker(v['spec'],v['plan']),sort_keys=True))
