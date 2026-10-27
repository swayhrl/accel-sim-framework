"""CANDIDATE ONLY. Private module-instance admission overlay; never install itself.

Frozen l2_native.py, plan/spec/RSS/AS/binding/argv/strict stay unchanged.
Registry metadata and fresh independent guard heartbeat are mandatory.
"""
import hashlib,importlib.util,json,os,pathlib,time
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
OVERLAY_ID='L2MLP_GUARDED_ADMISSION_LAVA_PILOT_V1'
PILOT='E2-DTCL2MLP-ddb6806316876a85-DH-P0-V1'
PILOT_CANDIDATES=[PILOT,'E2-DTCL2MLP-ffc8a89493c8a211-DH-P0-V1','E2-DTCL2MLP-2b93f70cd0666c51-DH-P0-V1']
HERE=P(__file__).resolve().parent
G=1024**3

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def jsonsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def proc_start(pid):return int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
def thread_state(pid,tid):
 try:
  fields=(P('/proc')/str(pid)/'task'/str(tid)/'stat').read_text().rsplit(')',1)[1].split()
 except OSError as exc:raise RuntimeError('GUARD_THREAD_NOT_ALIVE')from exc
 return fields[0],int(fields[19])
def journal_prefix_hash(path,n):
 if type(n)is not int or not 0<=n<=256*1024**2:raise RuntimeError('GUARD_JOURNAL_PREFIX_BOUND')
 with P(path).open('rb')as f:raw=f.read(n)
 if len(raw)!=n:raise RuntimeError('GUARD_JOURNAL_TRUNCATED')
 return hashlib.sha256(raw).hexdigest()

def approval(e,c):
 if c not in PILOT_CANDIDATES:raise RuntimeError('GUARD_PILOT_ONLY_NO_OLD_REQUESTS')
 reg,ep,q,plan=e.registered()
 record=q.get('resource_admission_overlays',{}).get(OVERLAY_ID)
 if not record or record.get('status')!='APPROVED_CPU_NATIVE_PREFIX_QUALIFIED':raise RuntimeError('GUARD_NOT_REGISTERED_NO_START')
 if record.get('request')!=REQ or record.get('allowed_cohorts')!=PILOT_CANDIDATES:raise RuntimeError('GUARD_SCOPE_MISMATCH')
 if record.get('changes_scientific_identity')is not False:raise RuntimeError('GUARD_IDENTITY_RULE')
 if record.get('original_engine_sha256')!=e.sha(e.__file__):raise RuntimeError('GUARD_BASE_ENGINE_MISMATCH')
 if record.get('original_binding_sha256')!=jsonsha(e.binding()):raise RuntimeError('GUARD_BASE_BINDING_MISMATCH')
 for key in ['overlay_source','policy','monitor_source','additional_strict_source','cpu_native_prefix_qualification','publication_readback']:
  row=record[key]
  if sha(row['path'])!=row['sha256']:raise RuntimeError('GUARD_PIN_MISMATCH_'+key)
 if P(record['overlay_source']['path']).resolve()!=P(__file__).resolve():raise RuntimeError('GUARD_SOURCE_NOT_THIS_MODULE')
 qual=read(record['cpu_native_prefix_qualification']['path'])
 if qual.get('status')!='PASS' or qual.get('actual_model_starts')!=0 or not all(qual.get(k)is True for k in ['full_native_prefix_intercepted','actual_compiled_INTENT_LAUNCH_PID_triple_qualified','additional_strict_cpu_qualified','no_overlay_original_strict_qualified','actual_B_guard_empty_resolver_native_prepare_qualified']):raise RuntimeError('GUARD_CPU_NATIVE_QUALIFICATION_REQUIRED')
 if qual.get('source_sha256',{}).get('guarded_native.py')!=record['overlay_source']['sha256']or qual.get('source_sha256',{}).get('additional_strict.py')!=record['additional_strict_source']['sha256']or qual.get('policy_sha256')!=record['policy']['sha256']or qual.get('B_guard_source_sha256')!=record['monitor_source']['sha256']:raise RuntimeError('GUARD_QUALIFICATION_SOURCE_SET_MISMATCH')
 pub=read(record['publication_readback']['path'])
 if pub.get('status')!='READBACK_VERIFIED' or not isinstance(pub.get('commit'),str)or len(pub['commit'])!=40:raise RuntimeError('GUARD_PUBLICATION_BEFORE_NATIVE_REQUIRED')
 for key in ['overlay_source','policy','monitor_source','additional_strict_source','cpu_native_prefix_qualification']:
  if pub.get('source_sha256',{}).get(key)!=record[key]['sha256']:raise RuntimeError('GUARD_PUBLICATION_SOURCE_MISMATCH_'+key)
 if e.R==R and(qual.get('fixture_only')or pub.get('fixture_only')):raise RuntimeError('GUARD_CPU_FIXTURE_IS_NOT_PRODUCTION_AUTHORIZATION')
 policy=read(record['policy']['path'])
 if policy.get('schema')!='L2MLP_GUARDED_ADMISSION_POLICY_V1' or policy.get('allowed_cohorts')!=PILOT_CANDIDATES:raise RuntimeError('GUARD_POLICY_SCOPE')
 if policy['host_floor_bytes']<10*G or policy['cgroup_floor_bytes']<10*G:raise RuntimeError('GUARD_MINIMUM_10G_FLOOR')
 return record,policy,ep,q

def selected_token(e,c,record,policy,ep,q):
 active=q.get('active_resource_admission_token',{})
 if active.get('overlay_id')!=OVERLAY_ID or active.get('cohort')!=c:raise RuntimeError('GUARD_OWNER_HAS_NOT_SELECTED_THIS_PILOT')
 raw=P(active['path']).read_bytes();token=json.loads(raw);h=hashlib.sha256(raw).hexdigest()
 if h!=active['sha256'] or token.get('nonce')!=active.get('nonce'):raise RuntimeError('GUARD_TOKEN_MISMATCH')
 hist=q.get('resource_admission_token_history',{}).get(token['nonce'])
 if hist!={'path':active['path'],'sha256':h,'cohort':c}:raise RuntimeError('GUARD_TOKEN_IMMUTABLE_HISTORY_REQUIRED')
 if token.get('request')!=REQ or token.get('cohort')!=c or token.get('epoch')!=ep['epoch'] or ep['epoch']!=2:raise RuntimeError('GUARD_TOKEN_EPOCH_OR_COHORT_MISMATCH')
 if token.get('boot_id')!=P('/proc/sys/kernel/random/boot_id').read_text().strip():raise RuntimeError('GUARD_TOKEN_BOOT_MISMATCH')
 now=time.monotonic();issued=token['issued_monotonic'];expires=token['expires_monotonic']
 if not issued<=now<=expires or not 0<expires-issued<=policy['token_max_lifetime_seconds']:raise RuntimeError('GUARD_TOKEN_EXPIRED_OR_FUTURE')
 lease=e.assert_parent_lease()
 if (token['owner_pid'],token['owner_start_ticks'])!=(lease['pid'],lease['start_ticks']):raise RuntimeError('GUARD_TOKEN_OWNER_MISMATCH')
 if token['canonical_spec_sha256']!=e.sha(e.R/'control/specs'/(c+'.json')):raise RuntimeError('GUARD_TOKEN_SPEC_MISMATCH')
 if token['dispatch_binding_sha256']!=e.sha(e.R/'control/dispatch_bindings'/(c+'.json')):raise RuntimeError('GUARD_TOKEN_DISPATCH_MISMATCH')
 return token,h

def heartbeat(record,policy,ep,q,now=None,owner_lease=None):
 now=time.monotonic()if now is None else now
 path=P(record['heartbeat_path']);raw=path.read_bytes();h=json.loads(raw)
 if h.get('schema')!='L2MLP_GUARD_HEARTBEAT_V1' or h.get('request')!=REQ or h.get('overlay_id')!=OVERLAY_ID:raise RuntimeError('GUARD_HEARTBEAT_IDENTITY')
 if h.get('registry_overlay_record_sha256')!=jsonsha(record):raise RuntimeError('GUARD_HEARTBEAT_APPROVAL_MISMATCH')
 if h.get('policy_sha256')!=record['policy']['sha256'] or h.get('monitor_source_sha256')!=record['monitor_source']['sha256']:raise RuntimeError('GUARD_HEARTBEAT_SOURCE_MISMATCH')
 if ep.get('epoch')!=2 or h.get('epoch')!=2 or h.get('boot_id')!=P('/proc/sys/kernel/random/boot_id').read_text().strip():raise RuntimeError('GUARD_EPOCH_OR_BOOT_MISMATCH')
 age=now-h.get('monotonic',float('-inf'))
 if not 0<=age<=policy['heartbeat_max_age_seconds']:raise RuntimeError('GUARD_STALE_HEARTBEAT_HOLD')
 if not h.get('warmup_complete'):raise RuntimeError('GUARD_MONITOR_WARMUP_HOLD')
 if h.get('shadow_mode')is not False or h.get('signals_enabled')is not True:raise RuntimeError('GUARD_SHADOW_OR_SIGNALS_DISABLED_HOLD')
 if h.get('aggressive_admission_armed')is not True:raise RuntimeError('GUARD_AGGRESSIVE_FAILSAFE_NOT_ARMED_HOLD')
 if h.get('healthy')is not True or h.get('fault')is not None or h.get('fresh_admission_allowed')is not True:raise RuntimeError('GUARD_UNHEALTHY_OR_NO_FRESH_ADMISSION_HOLD')
 if not owner_lease:raise RuntimeError('GUARD_PARENT_LEASE_REQUIRED')
 owner=(owner_lease['pid'],owner_lease['start_ticks'])
 if (h.get('owner_pid'),h.get('owner_start_ticks'))!=owner or(h.get('monitor_pid'),h.get('monitor_start_ticks'))!=owner or proc_start(owner[0])!=owner[1]:raise RuntimeError('GUARD_MONITOR_GENERATION_MISMATCH')
 state,start=thread_state(owner[0],h['guard_tid'])
 if h['guard_tid']==owner[0]or start!=h['guard_start_ticks']or state in['T','t','Z','X']:raise RuntimeError('GUARD_THREAD_IDENTITY_OR_STATE_HOLD')
 if h.get('guard_token')!=record.get('guard_token')or not record.get('guard_token'):raise RuntimeError('GUARD_THREAD_TOKEN_MISMATCH')
 if h.get('active_admission_token_sha256')!=q.get('active_resource_admission_token',{}).get('sha256'):raise RuntimeError('GUARD_ACTIVE_PILOT_TOKEN_MISMATCH')
 if h.get('pause_journal_path')!=record['pause_journal_path']or journal_prefix_hash(h['pause_journal_path'],h['pause_journal_prefix_bytes'])!=h['pause_journal_sha256']:raise RuntimeError('GUARD_PAUSE_JOURNAL_MISMATCH')
 if h.get('handle_state_sha256')!=jsonsha(h['paused_handles']):raise RuntimeError('GUARD_PAUSED_HANDLE_STATE_MISMATCH')
 if not h.get('pause_new_admission'):return h,hashlib.sha256(raw).hexdigest(),age,raw.decode('utf-8')
 raise RuntimeError('GUARD_MONITOR_PRESSURE_HOLD:'+','.join(h.get('pause_reasons',[])))

def decision(original,h,policy,c,q):
 """Only discount known LIVE_MODEL forecast deltas. Others remain full."""
 ram=original['own_ram_forecasts'];unchanged=[];changed=[];new_total=original['total_projected_additional_RAM_bytes']
 for row in ram:
  old=row['additional_reserved_bytes'];reserve=old;reason='ORIGINAL_UNCHANGED'
  own=h.get('own_live_generations',{})
  obs=own.get(row['cohort'])if isinstance(own,dict)else next((v for v in own if v.get('cohort')==row['cohort']),None)
  if obs is None:
   item=next((v for v in h.get('live_generation_states',[])if v.get('cohort')==row['cohort']),None)
   if item and type(item.get('rss_bytes'))is int and isinstance(item.get('growth_rate'),(int,float)):
    obs=item
  if obs is not None and 'RSS_bytes'not in obs and type(obs.get('rss_bytes'))is int and isinstance(obs.get('growth_rate'),(int,float)):
   obs=dict(obs,RSS_bytes=obs['rss_bytes'],growth_reserve_bytes=max(policy['minimum_live_growth_reserve_bytes'],int(obs['rss_bytes']*.1),int(max(0,obs['growth_rate'])*policy['growth_forecast_horizon_seconds']*policy['growth_rate_multiplier'])))
  if row['cohort']!=c and row.get('kind')=='LIVE_MODEL' and obs and row['cohort']in q['consumed']:
   consumed=q['consumed'][row['cohort']]
   try:identity=obs['uuid']==consumed['uuid'] and proc_start(obs['pid'])==obs['start_ticks']
   except(OSError,ValueError,KeyError):identity=False
   # Sampling differences cannot erase already observed RSS growth.
   if identity and isinstance(obs.get('growth_reserve_bytes'),int)and obs['growth_reserve_bytes']>=policy['minimum_live_growth_reserve_bytes']:
    reserve=min(old,max(policy['minimum_live_growth_reserve_bytes'],obs['growth_reserve_bytes'],row['RSS_bytes']-obs.get('RSS_bytes',0)))
    reason='FRESH_MONITORED_SAME_GENERATION_GROWTH_ENVELOPE'
  new_total+=reserve-old
  item=dict(row,original_reserved_bytes=old,guarded_reserved_bytes=reserve,reason=reason)
  (changed if reserve!=old else unchanged).append(item)
 head=h.get('headroom_sample',{});host=min(original['host_MemAvailable_bytes'],head.get('host_available_bytes',original['host_MemAvailable_bytes']));cg=original.get('cgroup_effective_headroom_bytes');guard_cg=head.get('cgroup_effective_headroom_bytes')
 if guard_cg is not None:cg=min(cg,guard_cg)if cg is not None else guard_cg
 guard_raw=head.get('cgroup_raw_headroom_bytes')
 if guard_raw is not None:cg=min(cg,guard_raw)if cg is not None else guard_raw
 # No clean-cache credit beyond the frozen base calculation is added.
 ceiling=min(host-policy['host_floor_bytes'],cg-policy['cgroup_floor_bytes']if cg is not None else host-policy['host_floor_bytes'])
 reasons=list(original.get('admission_decision',{}).get('pressure_reasons',[]))
 if h.get('pause_new_admission'):reasons+=h.get('pause_reasons',[])
 passed=not reasons and ceiling>=new_total and original['physical_disk_pass']
 return {'schema':'L2MLP_GUARDED_ADMISSION_DECISION_V1','pass_admission':passed,'cohort':c,'original_total_projected_additional_RAM_bytes':original['total_projected_additional_RAM_bytes'],'guarded_total_additional_RAM_bytes':new_total,'RAM_available_after_10G_floors_bytes':ceiling,'changed_live_rows':changed,'unchanged_rows':unchanged,'pressure_reasons':reasons,'candidate_estimate_unchanged':True,'RSS_AS_caps_unchanged':True,'foreign_and_unresolved_reservations_unchanged':True}

def install(e,c):
 """Mutates ONLY supplied fresh private Python module object; no disk writes."""
 record,policy,ep,q=approval(e,c)
 token,token_sha=selected_token(e,c,record,policy,ep,q)
 initial_h,_,_,_=heartbeat(record,policy,ep,q,owner_lease=e.assert_parent_lease())
 binding={'schema':'L2MLP_ADDITIONAL_RESOURCE_OVERLAY_BINDING_V1','overlay_id':OVERLAY_ID,'request':REQ,'cohort':c,'owner_selected_token_sha256':token_sha,'owner_selected_token_nonce':token['nonce'],'registry_overlay_record_sha256':jsonsha(record),'base_provider_sha256':e.sha(e.R/'tools/l2_resources.py'),'overlay_source_sha256':record['overlay_source']['sha256'],'policy_sha256':record['policy']['sha256'],'monitor_source_sha256':record['monitor_source']['sha256'],'additional_strict_source_sha256':record['additional_strict_source']['sha256'],'cpu_native_prefix_qualification_sha256':record['cpu_native_prefix_qualification']['sha256'],'original_l2_execution_binding_unmodified':True,'scientific_spec_and_limits_unmodified':True,'base_forecast_fields_are_not_the_effective_admission_gate':True}
 binding['publication_readback_sha256']=record['publication_readback']['sha256']
 binding['guard_identity']={k:initial_h[k]for k in ['owner_pid','owner_start_ticks','guard_tid','guard_start_ticks','guard_token','pause_journal_path']}
 original_resources=e.resources;original_engine=e.engine;original_prepare=e.prepare
 context={'last_admission':None}
 def resources(spec,fresh_source=False):
  special=spec.get('cohort')=='L2_MLP_ADMISSION_ALREADY_CLAIMED'
  active=spec.get('cohort')==c or special
  if not active:return original_resources(spec,fresh_source)
  if not fresh_source and not special:
   # Frozen runtime resources deliberately do not kill healthy jobs on pressure.
   return dict(original_resources(spec,fresh_source),resource_overlay_binding=binding,resource_overlay_affects_admission_only=True)
  rec,pol,epoch,currentq=approval(e,c);current_token,current_token_sha=selected_token(e,c,rec,pol,epoch,currentq)
  if current_token_sha!=token_sha:raise RuntimeError('GUARD_TOKEN_ROTATED_DURING_PREPARE')
  h,hs,age,heartbeat_raw=heartbeat(rec,pol,epoch,currentq,owner_lease=e.assert_parent_lease())
  if any(h[k]!=v for k,v in binding['guard_identity'].items()):raise RuntimeError('GUARD_IDENTITY_CHANGED_DURING_PREPARE')
  base=original_resources(e.spec_for(c)if special else spec,True)
  d=decision(base,h,pol,c,currentq)
  evidence={'decision':d,'heartbeat_path':rec['heartbeat_path'],'heartbeat_sha256':hs,'heartbeat_age_seconds':age,'heartbeat_raw_utf8':heartbeat_raw,'registry_record_sha256':jsonsha(rec),'base_resource_receipt':base,'owner_selected_token':current_token,'owner_selected_token_sha256':current_token_sha,'effective_admission_provider_sha256':record['overlay_source']['sha256']}
  context['last_admission']=evidence
  return dict(base,physical_RAM_pass=d['pass_admission'],resource_overlay_binding=binding,resource_overlay_admission_evidence=evidence,base_resource_forecasts_retained=True,effective_admission_provider_sha256=record['overlay_source']['sha256'],base_resource_fields_are_evidence_not_effective_admission_gate=True)
 def engine():
  n=original_engine();original_exclusive=n.exclusive
  def exclusive(path,obj):
   p=P(path)
   if p.name.endswith('.INTENT.json')or p.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    if not context['last_admission']:raise RuntimeError('GUARD_NO_ADMISSION_EVIDENCE')
    obj=dict(obj,resource_overlay_binding=binding,resource_overlay_admission_evidence=context['last_admission'])
   return original_exclusive(path,obj)
  n.exclusive=exclusive
  return n
 e.resources=resources;e.engine=engine
 # No e.binding, spec_for, limits, binary, argv, finish/observer code replacements.
 return {'private_engine':e,'additional_binding':binding,'context':context}

def guarded(c):
 e=load('l2_guarded_private_base',R/'tools/l2_native.py');install(e,c);return e
