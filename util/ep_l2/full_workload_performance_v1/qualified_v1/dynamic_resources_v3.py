"""Read-only dynamic admission. No actors/imported controllers/signals/ledger writes.
Forecast disagreement or transient metadata pauses NEW admissions only; never kills.
Existing allocation is already charged by MemAvailable/cgroup.current/df; add growth only.
"""
import os,json,pathlib,hashlib,time,math,datetime,fcntl
P=pathlib.Path;G=1<<30;M=1<<20
ROOT=P('/root/data/ep_l2_full_workload_performance_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';LOCK=REG.with_name('REGISTRY_UPDATE.lock')
F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');MLP=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';MR='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';OWN='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
ROOTS={ORIG:T,'DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1':F/'validation','DTC_AE_LAVAMEM_REPAIR_20261026_V2':F/'validation_lava_memory_v2','DTC_AE_LATE_FAILURE_REPAIR_20261026_V1':F/'validation_late_failure_v1','DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1':F/'validation_remaining_failure_v1','DTC_AE_STORAGE_RECOVERY12_20261026_V1':F/'validation_storage_recovery12_v1',MR:MLP}
DEFAULT_POLICY={'memory_utilization_fraction':.88,'min_host_headroom_bytes':8*G,'min_cgroup_headroom_bytes':8*G,'native_safety_floor_bytes':5*G,'min_free_inodes':100000,'max_snapshot_age_seconds':5,'minimum_prediction_bytes':768*M,'history_multiplier':1.2,'history_additive_bytes':256*M,'unknown_prediction_bytes':4*G,'require_foreign_lease':True}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise ValueError(msg)
def kv(p):
 try:return {a:int(b)for a,b in(x.split()for x in P(p).read_text().splitlines())}
 except(OSError,ValueError):return {}
def pressure_file(p):
 try:return {x[0]:{a:float(b)for a,b in(y.split('=')for y in x[1:])}for x in (l.split()for l in P(p).read_text().splitlines())}
 except(OSError,ValueError):return {}
def process(pid,start_ticks=None):
 try:
  p=P('/proc')/str(pid);st=(p/'stat').read_text().rsplit(')',1)[1].split();ticks=int(st[19]);live=st[0]not in ('Z','X')and(start_ticks is None or ticks==start_ticks)
  if not live:return {'live':False,'pid':pid,'start_ticks':ticks,'RSS_bytes':0,'PSS_bytes':0}
  status=(p/'status').read_text();rss=int(next(x.split()[1]for x in status.splitlines()if x.startswith('VmRSS:')))*1024;pss=rss;measured=False
  try:pss=int(next(x.split()[1]for x in(p/'smaps_rollup').read_text().splitlines()if x.startswith('Pss:')))*1024;measured=True
  except(OSError,StopIteration):pass
  return dict(live=True,pid=pid,start_ticks=ticks,RSS_bytes=rss,PSS_bytes=pss,PSS_measured=measured,affinity=sorted(os.sched_getaffinity(pid)))
 except(OSError,ValueError,StopIteration,ProcessLookupError):return dict(live=False,pid=pid,start_ticks=start_ticks,RSS_bytes=0,PSS_bytes=0)
def size(root):
 n=0;seen=set()
 if not root.exists():return 0
 for parent,dirs,files in os.walk(root):
  for name in files:
   p=P(parent)/name;t=p.lstat()
   # Peer config links charge their own inode, never external targets/Trace.
   if p.is_symlink():n+=max(t.st_size,t.st_blocks*512);continue
   key=(t.st_dev,t.st_ino)
   if key not in seen:seen.add(key);n+=max(t.st_size,t.st_blocks*512)
 return n

def verified_ghosts(q):
 policy=read(F/'control/R20_RESOURCE_ACCOUNTING_POLICY_V1.json');gp=P(policy['ghost_certificate_path']);need(sha(gp)==policy['ghost_certificate_sha256'],'ghost certificate drift');cert=read(gp);out={}
 for pin in cert['forensic_pins']:need(sha(pin['path'])==pin['sha256'],'ghost forensic pin drift')
 for x in cert['targets']:
  row=q['consumed'].get(x['cohort'],{});o=P(x['output']);ip=P(x['intent_path']);maps=o/'NATIVE_SIMULATOR_PID_AND_MAPS.json';launch=o/'NATIVE_LAUNCH.json'
  need(row.get('uuid')==x['uuid']and row.get('intent_sha256')==x['intent_sha256']and sha(ip)==x['intent_sha256'],'ghost registry tuple drift')
  need(sha(maps)==x['PID_receipt_sha256']and sha(launch)==x['launch_receipt_sha256'],'ghost generation proof drift')
  need(not process(x['model_pid'],x['model_start_ticks'])['live']and not process(x['launcher_pid'])['live'],'ghost generation became live')
  out[x['cohort']]=x['uuid']
 return out

def archived(root,c,row):
 p=root/'control'/(c+'_ARCHIVE_RECEIPT.json');ip=root/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');out=root/'DTC/run/results'/row['uuid']
 if not p.exists():return False
 try:
  a=read(p);d=read(dp)
  return d==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and d['uuid']==read(ip)['uuid']==row['uuid']and sha(ip)==row['intent_sha256']and a['cohort']==c and a['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and a['source_disposition']=='SOURCE_KEEP'
 except(OSError,KeyError,ValueError):return False

def lease():
 p=T/'control/BATCH_LEASE.json';x=read(p);v=process(x['pid'],x['start_ticks']);need(v['live'],'foreign BATCH_LEASE generation absent');fd=P('/proc')/str(x['pid'])/'fd'/str(x['fd']);need(os.readlink(fd)==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'),'foreign lease FD mismatch');need('FLOCK'in(fd.parent.parent/'fdinfo'/str(x['fd'])).read_text(),'foreign lease flock absent');need(MR in x['additional_requests'],'MLP absent from actual foreign lease');need('sweep_controller.py'in(P('/proc')/str(x['pid'])/'cmdline').read_bytes().decode(errors='replace'),'foreign parent command mismatch');need(sha(F/'ops/revision20/sweep_controller.py')==x['controller_sha256'],'foreign lease controller source pin drift');return dict(path=str(p),sha256=sha(p),pid=x['pid'],start_ticks=x['start_ticks'],live=True,additional_requests=x['additional_requests'])

def sample_system():
 c=P('/sys/fs/cgroup');mem={x.split(':')[0]:int(x.split()[1])*1024 for x in P('/proc/meminfo').read_text().splitlines()if len(x.split())>1 and x.split()[1].isdigit()};mx=(c/'memory.max').read_text().strip();cur=int((c/'memory.current').read_text());st=kv(c/'memory.stat');clean=max(0,st.get('file',0)-sum(st.get(k,0)for k in ['shmem','file_mapped','file_dirty','file_writeback']));credit=max(0,min(st.get('inactive_file',0),clean)-8*G);v=os.statvfs(ROOT);quota=(c/'cpu.max').read_text().split()
 return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=time.monotonic(),host_MemAvailable_bytes=mem['MemAvailable'],cgroup_memory_max=mx,cgroup_memory_current=cur,cgroup_reclaimable_clean_credit_bytes=credit,cgroup_effective_headroom_bytes=None if mx=='max'else max(0,int(mx)-cur+credit),native_free_bytes=v.f_bavail*v.f_frsize,free_inodes=v.f_favail,cpu_allowed=sorted(os.sched_getaffinity(0)),cpu_quota_equivalent=None if quota[0]=='max'else int(quota[0])/int(quota[1]),memory_pressure=pressure_file(c/'memory.pressure'),io_pressure=pressure_file(c/'io.pressure'),cpu_pressure=pressure_file(c/'cpu.pressure'),cgroup_memory_events=kv(c/'memory.events'),host_pswpout_pages=kv('/proc/vmstat').get('pswpout',0))

def owner_growth(request,estimate,hard,actual_RSS):
 need(all(type(x)is int and x>=0 for x in [estimate,hard,actual_RSS])and estimate<=hard,'invalid owner growth inputs')
 envelope=math.ceil(actual_RSS*1.10)if request==MR else actual_RSS
 return max(0,min(hard,max(estimate,envelope))-actual_RSS)

def foreign_commitments(reg):
 qs=reg['registered_future_requests'];ram=[];writes=[];errors=[];claims_pins={};floor_host=floor_cg=0;ghost={}
 try:ghost=verified_ghosts(qs[ORIG])
 except Exception as e:errors.append('departed certificate: '+repr(e))
 for req,q in qs.items():
  if req==OWN:continue
  root=ROOTS.get(req)
  if root is not None and req in [MR,'DTC_AE_STORAGE_RECOVERY12_20261026_V1','DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1']:
   planpath=root/'control'/('EXECUTION_PLAN.json'if req==MR else'EXECUTION_PLAN_V1.json')
   try:need(sha(planpath)==q['execution_plan_sha256'],'foreign memory plan pin drift')
   except Exception as e:errors.append(req+': '+repr(e))
  if root is None:
   # Existing external advertised future bytes are a real promise until owner closes it.
   if q.get('state')not in ['COMPLETE','CLOSED','SEALED','STOP_UNACCEPTED','COMPAT_PARTIAL_COMPLETE']:
    n=q.get('reserved_write_bytes');need(type(n)is int and n>=0,'unknown unbounded foreign writer '+req);writes.append(dict(request=req,kind='ADVERTISED_UNKNOWN_WRITER',bytes=n))
    if q.get('consumed'):errors.append('unmapped active foreign RAM owner '+req)
   continue
  cp=root/'control/POOL_DISPATCH_RESERVATIONS.json';cs=read(cp).get('claims',{})if cp.exists()else{};claims_pins[req]=dict(path=str(cp),sha256=sha(cp)if cp.exists()else None,claims=len(cs))
  rows=q.get('consumed',{});active=q.get('state')not in ['COMPLETE','CLOSED','SEALED'];subtotal=G if active else 0
  for cohort in sorted(set(rows)|set(cs)):
   row=rows.get(cohort);pending=row is None
   if row and archived(root,cohort,row):continue
   if not active and pending:errors.append('closed foreign owner has unspent claim '+req);continue
   try:
    sp=root/'control'/((cohort+'_SPEC.json')if root==T else('specs/'+cohort+'.json'));s=read(sp);need(sha(sp)==q['admitted_specs'][cohort],'foreign resource spec pin drift');cap=s['limits']['max_result_directory_bytes'];op=root/'control'/('OPERATIONAL_OUTPUT_CAP_'+cohort+'.json')
    if op.exists():
     override=read(op);cap2=override['effective_result_cap_bytes'];need(0<cap2<=cap,'invalid foreign output cap');need(root==T or sha(op)==s['operational_output_cap_sha256'],'foreign output cap drift');cap=cap2
    estimate=s.get('estimated_peak_model_RAM_bytes',96*G if 'LAVAMEM'in req else 4*G);hard=s['limits']['max_process_tree_rss_bytes'];need(0<estimate<=hard,'foreign RAM estimate')
    if pending:
     need(cs[cohort]['result_cap_bytes']==cap,'pending foreign claim output cap');growth=estimate;used=0;kind='CLAIM_PENDING';pr=dict(live=False,RSS_bytes=0,PSS_bytes=0)
    else:
     ip=P(row['intent']);need(sha(ip)==row['intent_sha256'],'foreign INTENT drift');intent=read(ip);o=root/'DTC/run/results'/row['uuid'];used=size(o);mp=o/'NATIVE_SIMULATOR_PID_AND_MAPS.json';pr=process(**{k:read(mp)[k]for k in ['pid','start_ticks']})if mp.exists()else dict(live=False,RSS_bytes=0,PSS_bytes=0)
     done=row.get('execution_receipt');departed=ghost.get(cohort)==row['uuid']
     if done:
      need(not pr['live'],'DONE while foreign model live');growth=0;kind='COMPLETED_STALE_CLAIM_NO_RAM'
     elif departed:growth=0;kind='CERTIFIED_DEPARTED_NO_FUTURE_FORK'
     else:
      growth=owner_growth(req,estimate,hard,pr['RSS_bytes']);kind='LIVE_MODEL'if pr['live']else'UNRESOLVED_CONSUMED_GENERATION'
     binding=intent.get('resource_accounting_binding_R20',{})
     if pr['live']and binding:
      floor_host=max(floor_host,binding.get('host_runtime_floor_bytes',0));floor_cg=max(floor_cg,binding.get('cgroup_runtime_floor_bytes',0))
    remain=2*cap if pending else used+16*M if row.get('execution_receipt')or ghost.get(cohort)==row['uuid']else max(0,2*cap-used)
    subtotal+=remain;writes.append(dict(request=req,cohort=cohort,kind=kind,bytes=remain,already_written_bytes=used,restore_rule='foreign own registered existing-result/one-restore bound'))
    ram.append(dict(request=req,cohort=cohort,kind=kind,additional_RAM_bytes=growth,estimate_bytes=estimate,hard_bytes=hard,**pr))
   except Exception as e:errors.append(req+'/'+cohort+': '+repr(e))
  if active:writes.append(dict(request=req,kind='OWNER_METADATA',bytes=G))
  if subtotal>q.get('reserved_write_bytes',0):errors.append('foreign published write ceiling under actual bound '+req)
 return dict(foreign_RAM_entries=ram,foreign_write_entries=writes,foreign_additional_RAM_bytes=sum(x['additional_RAM_bytes']for x in ram),foreign_remaining_write_bytes=sum(x['bytes']for x in writes),foreign_metadata_errors=errors,foreign_claims_pins=claims_pins,confirmed_foreign_host_floor_bytes=floor_host,confirmed_foreign_cgroup_floor_bytes=floor_cg)

def snapshot():
 began=time.monotonic();errors=[]
 try:
  with LOCK.open('rb')as lock:
   fcntl.flock(lock,fcntl.LOCK_SH);raw=REG.read_bytes();reg=json.loads(raw);regsha=hashlib.sha256(raw).hexdigest();fcntl.flock(lock,fcntl.LOCK_UN)
  foreign=foreign_commitments(reg)
  # Cross-file owner transitions may race. HOLD new admission; do not erase old promises or signal models.
  if sha(REG)!=regsha:foreign['foreign_metadata_errors'].append('registry transitioned during resource sample; resample')
  try:l=lease()
  except Exception as e:l={'live':False,'error':repr(e)};foreign['foreign_metadata_errors'].append('foreign lease: '+repr(e))
  return dict(sample_system(),**foreign,schema='EP_FULL_PERF_DYNAMIC_ADMISSION_SNAPSHOT_V1',registry_sha256=regsha,foreign_batch_lease=l,no_actors_imported=True,runtime_kill_authorized=False,sample_started_monotonic=began,foreign_metadata_elapsed_seconds=time.monotonic()-began,metadata_snapshot_cache_used=False,resource_source_semantics={'MLP':'min(hard,max(estimate,ceil(actualRSS*1.10)))-actualRSS','R20':'min(hard,max(estimate,actualRSS))-actualRSS','own':'caller pending growth not hardcap sum'})
 except Exception as e:return dict(sample_system(),schema='EP_FULL_PERF_DYNAMIC_ADMISSION_SNAPSHOT_V1',foreign_metadata_errors=[repr(e)],foreign_additional_RAM_bytes=0,foreign_remaining_write_bytes=0,runtime_kill_authorized=False)

def forecast(input_id,history,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));rows=history.get('records',[])if isinstance(history,dict)else history;rows=[x for x in rows if x.get('input_identity_sha256',x.get('workload'))==input_id];valid=[x for x in rows if x.get('peak_observed_rss_bytes',x.get('rss',0))>0];peak=max([x.get('peak_observed_rss_bytes',x.get('rss',0))for x in valid]+[0]);estimated=max(p['minimum_prediction_bytes'],math.ceil(peak*p['history_multiplier'])+p['history_additive_bytes'])if valid else p['unknown_prediction_bytes']
 return dict(input_identity_sha256=input_id,estimated_peak_RAM_bytes=estimated,actual_historical_peak_bytes=peak,history_rows=len(valid),kind='FORECAST_NOT_HARD_CAP',failed_history_is_lower_bound=any(not x.get('success',False)for x in valid),performance_identity_inherited=False)

def pressure(s,previous=None,policy=None):
 reasons=[]
 for field,kind,limit in [('memory_pressure','some',2.),('memory_pressure','full',.5),('io_pressure','full',30.)]:
  if s.get(field,{}).get(kind,{}).get('avg10',0)>limit:reasons.append(field+'/'+kind)
 if previous and any(s.get('cgroup_memory_events',{}).get(k,0)>previous.get('cgroup_memory_events',{}).get(k,0)for k in ['oom','oom_kill']):reasons.append('new cgroup OOM event')
 return dict(pause_new_admission=bool(reasons),reasons=reasons,terminate_existing_models=False)

def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 p=dict(DEFAULT_POLICY,**(policy or {}));need(type(own_pending_additional_RAM)is int and own_pending_additional_RAM>=0,'nonnegative own future RAM');need(type(own_remaining_writes)is int and own_remaining_writes>=0,'nonnegative own future writes');reasons=list(s.get('foreign_metadata_errors',[]));age=time.monotonic()-s['monotonic']
 if not 0<=age<=p['max_snapshot_age_seconds']:reasons.append('snapshot stale')
 host_floor=max(p['min_host_headroom_bytes'],s.get('confirmed_foreign_host_floor_bytes',0));cg_floor=max(p['min_cgroup_headroom_bytes'],s.get('confirmed_foreign_cgroup_floor_bytes',0));host=max(0,s['host_MemAvailable_bytes']-host_floor);cg=s.get('cgroup_effective_headroom_bytes');usable=host if cg is None else min(host,max(0,cg-cg_floor));budget=int(usable*p['memory_utilization_fraction']);required_ram=s.get('foreign_additional_RAM_bytes',0)+own_pending_additional_RAM;required_disk=s.get('foreign_remaining_write_bytes',0)+own_remaining_writes+p['native_safety_floor_bytes'];pr=pressure(s,policy=p);reasons+=pr['reasons']
 if required_ram>budget:reasons.append('confirmed peer growth + own pending forecast exceeds usable RAM')
 if required_disk>s['native_free_bytes']:reasons.append('confirmed remaining writes + own future writes exceeds native free')
 if s['free_inodes']<p['min_free_inodes']:reasons.append('free inode safety')
 return dict(schema='EP_FULL_PERF_ADMISSION_DECISION_V1',pass_admission=not reasons,hold_reasons=reasons,own_pending_additional_RAM_bytes=own_pending_additional_RAM,own_remaining_write_bytes=own_remaining_writes,foreign_pending_additional_RAM_bytes=s.get('foreign_additional_RAM_bytes',0),foreign_remaining_write_bytes=s.get('foreign_remaining_write_bytes',0),admission_RAM_budget_bytes=budget,required_additional_RAM_bytes=required_ram,required_free_bytes=required_disk,host_floor_bytes=host_floor,cgroup_floor_bytes=cg_floor,memory_utilization_fraction=p['memory_utilization_fraction'],snapshot_age_seconds=age,forecast_is_not_runtime_hard_limit=True,terminate_existing_models=False)
