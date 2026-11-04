import pathlib,hashlib,importlib.util,json,copy,os,time,fcntl,math
P=pathlib.Path;G=1<<30;M=1<<20
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1')
PRIOR=J/'research/performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/agent_c_resources/resources_recovery.py'
PRIOR_SHA='4e0e21cb4c5e20a4c996c2b89765e3bcdde42c2c16c51b9bcce2db8461ff8423'
REQUESTS={'midtag':'EP_L2_MID_TAG_850MHZ_V1_20261104','vector1700':'EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104'}
SCOPES={REQUESTS['midtag']:J/'execution_midtag_v3_20261104_v1/midtag',REQUESTS['vector1700']:J/'execution_vector1700_decomposition_v3_20261104_v1/vector1700'}
DTC='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1';DTCROOT=P('/root/data/dtc_stage_iia_remaining48_20261104_v1')
LOCKS=J/'execution_performance_first_20261103_v1/control'
def need(v,msg):
 if not v:raise ValueError(msg)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(path,name,pin=None):
 if pin:need(sha(path)==pin,'pinned resource dependency drift '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def classify(argv):
 ix=[i for i,x in enumerate(argv) if P(x).name=='accel-sim.out']
 if not ix:return 'NOT_MODEL'
 i=ix[0]
 if any(P(x).name=='strace' for x in argv[:i]):return 'WRAPPER_NOT_MODEL'
 return 'MODEL' if i==0 or 'ld-linux' in P(argv[0]).name else 'UNKNOWN_MODEL_WRAPPER'
def remaining_growth(estimate,hard,rss):
 need(all(type(x)is int and x>=0 for x in [estimate,hard,rss]) and estimate<=hard,'bad growth bound')
 return max(0,min(hard,max(estimate,rss))-rss)
def dtc48_mapping(q,m,existing):
 need(q.get('request')==DTC and q.get('schema')=='DTC_STAGEII_REMAINING48_REGISTERED_REQUEST_V1','DTC48 owner schema')
 planpath=DTCROOT/'control/EXECUTION_PLAN.json';need(sha(planpath)==q['execution_plan_sha256'],'DTC48 plan drift');plan=read(planpath)
 need(plan['request']==DTC and plan['no_extensions'] and q['budget']==48 and q['remaining']==48-len(q['consumed']),'DTC48 exact scope/arithmetic')
 pref=next(z for z in plan['source_pins'] if z['path']==str(DTCROOT/'control/RESOURCE_POLICY.json'));need(sha(pref['path'])==pref['sha256'],'DTC48 policy drift');policy=read(pref['path'])
 cp=DTCROOT/'control/POOL_DISPATCH_RESERVATIONS.json';cp_sha=sha(cp);claims=read(cp)['claims'];rows=q['consumed'];need(set(claims)<=set(q['admitted_specs']),'DTC48 unknown claims')
 ram=[];writes=[];models=[];reserved_cpu=[]
 for cohort in sorted(set(rows)|set(claims)):
  row=rows.get(cohort);claim=claims.get(cohort,{});sp=DTCROOT/'control'/(cohort+'_SPEC.json');need(sha(sp)==q['admitted_specs'][cohort],'DTC48 spec drift');spec=read(sp);cap=spec['limits']['max_result_directory_bytes'];hard=spec['limits']['max_process_tree_rss_bytes'];estimate=spec['estimated_peak_model_RAM_bytes'];pr=dict(live=False,RSS_bytes=0,PSS_bytes=0);used=0;done=False;arch=False
  if row:
   ip=P(row['intent']);need(sha(ip)==row['intent_sha256'],'DTC48 intent drift');intent=read(ip);need(intent['uuid']==row['uuid'],'DTC48 UUID');out=DTCROOT/'DTC/run/results'/row['uuid'];mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';done=bool(row.get('execution_receipt'));arch=m.archived(DTCROOT,cohort,row)
   if mp.exists():
    ident=read(mp);pr=m.process(ident['pid'],ident['start_ticks'])
    if pr['live']:
     proc=P('/proc')/str(pr['pid']);argv=[x.decode(errors='replace') for x in (proc/'cmdline').read_bytes().split(bytes([0])) if x];expected=spec['native_simulator_argv'];need(classify(argv)=='MODEL' and argv[-len(expected):]==expected,'DTC48 loader argv/config mismatch');maps=(proc/'maps').read_text();need(any(line.split()[-1]==expected[0] for line in maps.splitlines() if line.split()),'DTC48 loadedELF map mismatch');models.append(dict(request=DTC,cohort=cohort,uuid=row['uuid'],pid=pr['pid'],start_ticks=pr['start_ticks'],RSS_bytes=pr['RSS_bytes'],CPU_affinity=pr['affinity'],loader_argv_join=True,input_digest=spec['input_digest']));reserved_cpu+=pr['affinity']
   if done:need(not pr['live'],'DTC48 DONE with live generation')
   if arch:continue
   used=m.size(out)
  need(cohort in claims or done,'DTC48 unresolved consumed without claim')
  if claim.get('host_cpu')is not None:reserved_cpu.append(claim['host_cpu'])
  growth=0 if done else remaining_growth(estimate,hard,pr['RSS_bytes']);remain=used+16*M if done else max(0,2*cap-used)
  ram.append(dict(request=DTC,cohort=cohort,additional_RAM_bytes=growth,estimate_bytes=estimate,hard_bytes=hard,**pr));writes.append(dict(request=DTC,cohort=cohort,bytes=remain,already_written_bytes=used,kind='DTC48_EXACT_REMAINING_SOURCE_RESTORE_NOT_LIFETIME_CEILING'))
 owner=m.process(q['owner_pid'],q['owner_start_ticks']);need(plan['parent_pid']==q['owner_pid'] and plan['parent_start_ticks']==q['owner_start_ticks'],'DTC48 parent identity');need(sha(plan['parent_controller_path'])==plan['parent_controller_sha256'],'DTC48 parent source drift')
 prior=load(PRIOR,'v3_prior_controller_margin',PRIOR_SHA);extra,margin=prior.controller_margin(owner,policy,existing+ram)
 if extra:ram.append(dict(request=DTC,kind='SHARED_PARENT_GROWTH_DEDUP_PID_GENERATION',additional_RAM_bytes=extra,pid=owner['pid'],start_ticks=owner['start_ticks'],RSS_bytes=owner['RSS_bytes']))
 metadata=policy['metadata_reserve_bytes'];writes.append(dict(request=DTC,bytes=metadata,kind='DTC48_FUTURE_METADATA'));need(sum(x['bytes'] for x in writes)<=q['reserved_write_bytes'],'DTC48 actual writes exceed advertised lifetime carrier');need(sha(cp)==cp_sha,'DTC48 claims transitioned;resample')
 return dict(ram=ram,writes=writes,models=models,reserved_cpus=sorted(set(reserved_cpu)),pin=dict(path=str(cp),sha256=cp_sha,claims=len(claims)),owner=owner,derived_remaining_write_bytes=sum(x['bytes'] for x in writes),published_lifetime_ceiling_bytes=q['reserved_write_bytes'],policy_ref=pref,confirmed_foreign_host_floor_bytes=policy['min_host_headroom_bytes'],confirmed_foreign_cgroup_floor_bytes=policy['min_cgroup_headroom_bytes'],confirmed_foreign_native_floor_bytes=policy['native_safety_floor_bytes'])
def runtime():
 prior=load(PRIOR,'v3_prior_DTC16_runtime',PRIOR_SHA);v=prior.base_runtime();factory=v.qualified_math
 def qualified():
  h=factory();h.SCOPES.update(SCOPES);base=h.base
  def mapped_base():
   m=base();foreign=m.foreign_commitments
   def mapped(reg):
    legacy=copy.deepcopy(reg);q=legacy['registered_future_requests'].pop(DTC,None);f=foreign(legacy)
    if q is not None:
     try:
      d=dtc48_mapping(q,m,f['foreign_RAM_entries']);f['foreign_RAM_entries']+=d['ram'];f['foreign_write_entries']+=d['writes'];f['foreign_claims_pins'][DTC]=d['pin'];f['DTC48_accounting']=d
      for k in ['confirmed_foreign_host_floor_bytes','confirmed_foreign_cgroup_floor_bytes','confirmed_foreign_native_floor_bytes']:f[k]=max(f.get(k,0),d[k])
     except Exception as e:f['foreign_metadata_errors'].append('DTC48_MAPPING_HOLD '+repr(e))
    f['foreign_additional_RAM_bytes']=sum(z['additional_RAM_bytes'] for z in f['foreign_RAM_entries']);f['foreign_remaining_write_bytes']=sum(z['bytes'] for z in f['foreign_write_entries']);return f
   m.foreign_commitments=mapped;return m
  h.base=mapped_base;return h
 v.qualified_math=qualified;return v
DEFAULT_POLICY=dict(runtime().DEFAULT_POLICY)
def global_activity(reg):
 rows=[];errors=[]
 for req,q in reg['registered_future_requests'].items():
  if not req.startswith('EP_'):continue
  cs=q.get('consumed',{})
  if isinstance(cs,dict):
   for c,row in cs.items():
    if row.get('state')in ['CONSUMED_BEFORE_FORK','RUNNING']:rows.append(dict(request=req,cohort=c,state=row['state']))
  elif q.get('state')=='RUNNING' and cs:errors.append('untyped activeEP '+req)
 return rows,errors
def snapshot(request):
 need(request in SCOPES,'unknown V3 scope');v=runtime();h=v.qualified_math();s=h.snapshot(request);m=h.base()
 with m.LOCK.open('rb')as f:
  fcntl.flock(f,fcntl.LOCK_SH);raw=m.REG.read_bytes();reg=json.loads(raw);fcntl.flock(f,fcntl.LOCK_UN)
 if hashlib.sha256(raw).hexdigest()!=s.get('registry_sha256'):s['foreign_metadata_errors'].append('registry changed during globalcap sample')
 entries,errors=global_activity(reg);s['foreign_metadata_errors']+=errors;cpu_claims=[];own_window=0
 for req,root in h.SCOPES.items():
  cp=root/'control/DISPATCH_CLAIMS.json'
  if cp.exists():
   before=sha(cp);claims=read(cp)['claims']
   for case,c in claims.items():
    if req==request:
     sp=root/'cases'/case/'control/FROZEN_SPEC.json';own_window=max(own_window,read(sp)['limits']['result_bytes'])
    cpu=c.get('host_cpu')
    if cpu is not None:cpu_claims.append(dict(request=req,cohort=case,cpu=cpu,state=c.get('state')))
   if sha(cp)!=before:s['foreign_metadata_errors'].append('CPU claims changed '+req)
 foreign=s.get('DTC48_accounting',{});occupied=set(foreign.get('reserved_cpus',[]))|{x['cpu'] for x in cpu_claims};known={(x['pid'],x['start_ticks']) for x in foreign.get('models',[])};unmapped=[];allmodels=[];wrappers=0
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   argv=[x.decode(errors='replace') for x in (proc/'cmdline').read_bytes().split(bytes([0])) if x];kind=classify(argv)
   if kind=='WRAPPER_NOT_MODEL':wrappers+=1;continue
   if kind=='NOT_MODEL':continue
   pr=m.process(int(proc.name));
   if not pr['live']:continue
   allmodels.append(dict(pid=pr['pid'],start_ticks=pr['start_ticks'],kind=kind,CPU_affinity=pr['affinity']));occupied.update(pr['affinity'])
   if (pr['pid'],pr['start_ticks'])not in known:
    matched=any(z.get('pid')==pr['pid'] and z.get('start_ticks')==pr['start_ticks'] for z in s.get('foreign_RAM_entries',[]))
    if not matched and not any(z.get('model_pid')==pr['pid'] and z.get('model_start_ticks')==pr['start_ticks'] for root in h.SCOPES.values() if (root/'control/DISPATCH_CLAIMS.json').exists() for z in read(root/'control/DISPATCH_CLAIMS.json')['claims'].values()):unmapped.append(dict(pid=pr['pid'],kind=kind))
  except (OSError,ValueError,IndexError):continue
 if unmapped:s['foreign_metadata_errors'].append('UNMAPPED_LIVE_SIMULATOR '+repr(unmapped))
 mount=P('/proc/mounts').read_text();true164=any(x.split()[1]=='/root/share/mnt164' and '164:' in x.split()[0] for x in mount.splitlines());nas=os.statvfs('/root/share/mnt164')
 s.update(schema='EP_MAIN_V3_GLOBAL_CAP_RESOURCE_SNAPSHOT_V1',current_request=request,global_EP_consumed_active_entries=entries,global_EP_consumed_active_count=len(entries),current_scope_registered=request in reg['registered_future_requests'],occupied_model_or_claim_cpus=sorted(occupied),EP_CPU_claims=cpu_claims,current_own_restore_window_bytes=own_window,actual_loader_aware_models=allmodels,strace_wrappers_excluded=wrappers,true164_mount_verified=true164,true164_free_bytes=nas.f_bavail*nas.f_frsize,resource_admission_is_not_science_permission=True,shared_admission_lock=str(LOCKS/'ADMISSION.lock'),shared_archive_lock=str(LOCKS/'ARCHIVE_SHARED_WINDOW.lock'),pool_ceiling_added_to_remaining_writes=False)
 return s
def own_claim(c,s,p):
 return c.get('request')==p.get('requested_request_id')==s.get('current_request') and c.get('cohort')==p.get('requested_cohort') and c.get('state')=='CLAIMED'
def cpu_checks(s,p):
 reasons=[];cpu=p.get('requested_host_cpu');claimed=s.get('EP_CPU_claims',[])
 occupied=set(s.get('DTC48_accounting',{}).get('reserved_cpus',[]))
 for model in s.get('actual_loader_aware_models',[]):occupied.update(model['CPU_affinity'])
 for c in claimed:
  if not own_claim(c,s,p):occupied.add(c['cpu'])
 if type(cpu)is not int:reasons.append('REQUESTED_HOST_CPU_MISSING')
 elif cpu not in s.get('cpu_allowed',[]):reasons.append('REQUESTED_CPU_OUTSIDE_CALLER_ALLOWED_AFFINITY')
 elif cpu in occupied:reasons.append('REQUESTED_CPU_CONFLICT_WITH_MODEL_OR_CLAIM')
 quota=s.get('cpu_quota_equivalent');pending=sum(c.get('state')=='CLAIMED' and not own_claim(c,s,p) for c in claimed)
 if quota is not None and len(s.get('actual_loader_aware_models',[]))+pending+1>math.floor(quota):reasons.append('CGROUP_CPU_QUOTA_MODEL_EQUIVALENT_EXHAUSTED')
 return reasons
def dedup_restore(s,own_writes):
 z=copy.deepcopy(s);removed=0;peer_max=0
 for row in z.get('foreign_write_entries',[]):
  if row.get('request')in SCOPES and row.get('kind')=='ONE_SHARED_RESTORE_WINDOW_AND_2M_METADATA':
   window=max(0,row['bytes']-2*M);removed+=window;peer_max=max(peer_max,window);row['bytes']-=window
 own_window=s.get('current_own_restore_window_bytes',0)
 z['foreign_remaining_write_bytes']=s.get('foreign_remaining_write_bytes',0)-removed
 return z,own_writes+max(0,peer_max-own_window),dict(removed_duplicate_peer_restore_bytes=removed,own_restore_window_already_in_caller_bytes=own_window,global_window_max_bytes=max(own_window,peer_max),added_global_window_increment_bytes=max(0,peer_max-own_window),shared_restore_lock=str(LOCKS/'ARCHIVE_SHARED_WINDOW.lock'))
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 need(s.get('current_request')in SCOPES,'cross-scope resource snapshot');p=dict(DEFAULT_POLICY,**(policy or {}));cap=p.get('max_global_EP_models',2);need(cap in [2,10],'unapproved EP cap');p['native_safety_floor_bytes']=max(p['native_safety_floor_bytes'],s.get('confirmed_foreign_native_floor_bytes',0));adjusted,writes,restore_receipt=dedup_restore(s,own_remaining_writes);d=runtime().qualified_math().admit(adjusted,own_pending_additional_RAM,writes,policy=p);d['global_restore_dedup']=restore_receipt;n=s.get('global_EP_consumed_active_count');reasons=d['hold_reasons']
 if type(n)is not int or n<0:reasons.append('UNKNOWN_GLOBAL_EP_ACTIVE_COUNT')
 elif n>=cap:reasons.append('GLOBAL_EP_CAP_'+str(cap)+'_REACHED')
 reasons+=cpu_checks(s,p)
 if not s.get('true164_mount_verified'):reasons.append('TRUE164_MOUNT_UNVERIFIED')
 if s.get('true164_free_bytes',0)<own_remaining_writes:reasons.append('TRUE164_INCREMENTAL_WRITE_HEADROOM')
 if p.get('stage_ready') is False:reasons.append('SCIENTIFIC_STAGE_HOLD')
 d.update(pass_admission=not reasons,global_EP_active_count=n,global_EP_cap=cap,requested_host_cpu=p.get('requested_host_cpu'),new_science_permission=False,terminate_existing_models=False,large_assets_location='true164',restore_serialization='Main shared ARCHIVE_SHARED_WINDOW.lock; existing per-scope finite write bounds retained, no added duplicate window')
 return d
def forecast(input_id,history,policy=None):return runtime().qualified_math().forecast(input_id,history,policy=policy)
