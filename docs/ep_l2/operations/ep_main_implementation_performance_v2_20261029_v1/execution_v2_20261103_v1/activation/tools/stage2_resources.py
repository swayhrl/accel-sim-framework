"""Read-only scoped resource admission. No fork/signals/controllers/registry writes.
Reuse pinned owner contracts; current RSS/df already accounts allocated resources.
Historical pool ceiling is checked, never added to derived remaining writes.
"""
import pathlib,json,hashlib,time,copy,importlib.util,fcntl
P=pathlib.Path;G=1<<30;M=1<<20
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1'
OLD_PATH=J/'tools/qualified_v1/dynamic_resources_v3.py';OLD_SHA='3e216a1dfc5f9ea8ef639c806e9c5ebcc8a715b955c43fd6d2cf57c9273aec81'
SCOPES={'EP_L2_WV_DECOMPOSITION_V2':E/'wv','EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1':E/'t3'}
OLD_EP='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
TERMINAL={'CLOSED_ACCEPTED','CLOSED_UNACCEPTED'}
NO_RAM={'NATURAL_COMPLETE_PENDING_VALIDATION','UNACCEPTED_ENGINEERING_FAILURE','ACCEPTED_PENDING_ARCHIVE','PARSE_HOLD','CLOSED_ACCEPTED','CLOSED_UNACCEPTED'}
def need(v,msg):
 if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def base():
 need(sha(OLD_PATH)==OLD_SHA,'frozen resource mathematics/foreign contract drift')
 sp=importlib.util.spec_from_file_location('stage2_frozen_readonly_resources',OLD_PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
DEFAULT_POLICY={'memory_utilization_fraction':.88,'min_host_headroom_bytes':1*G,'min_cgroup_headroom_bytes':1*G,'native_safety_floor_bytes':G,'min_free_inodes':10000,'max_snapshot_age_seconds':5,'minimum_prediction_bytes':256*M,'history_multiplier':1.1,'history_additive_bytes':16*M,'unknown_prediction_bytes':4*G,'require_foreign_lease':False}
def fresh_scope(req,q,root,m):
 cp=root/'control/DISPATCH_CLAIMS.json';claims=read(cp).get('claims',{})if cp.exists()else{};pin=dict(path=str(cp),sha256=sha(cp)if cp.exists()else None,claims=len(claims));errors=[];ram=[];writes=[];max_window=0
 need(type(claims)is dict,'fresh scope claims not object')
 rows=q.get('consumed',{});need(type(rows)is dict,'fresh scope consumed not object')
 for cohort,row in rows.items():
  if row.get('state')not in TERMINAL and cohort not in claims:errors.append(req+'/'+cohort+': consumed nonclosed row has no remaining resource claim')
 for cohort,c in claims.items():
  try:
   sp=root/'cases'/cohort/'control/FROZEN_SPEC.json';s=read(sp);need(sha(sp)==q['admitted_specs'][cohort]==c['spec_sha256'],'fresh claim/spec/registered digest drift')
   need(s['science_request_id']==req and s['cohort']==cohort,'fresh claim scope')
   cap=s['limits']['result_bytes'];estimate=c['estimated_peak_RAM_bytes'];hard=s['limits']['RSS_bytes'];remain=c['remaining_write_bytes'];need(all(type(x)is int and x>=0 for x in [cap,estimate,hard,remain])and cap>0 and hard>0 and estimate<=hard,'invalid fresh resource bounds')
   max_window=max(max_window,cap);row=rows.get(cohort);state=c.get('state');need(state in ['CLAIMED','RUNNING','TERMINAL_PENDING_VALIDATION'],'unrecognized fresh claim state')
   pr=dict(live=False,RSS_bytes=0,PSS_bytes=0)
   if c.get('model_pid'):
    need(type(c.get('model_start_ticks'))is int,'fresh model generation missing');pr=m.process(c['model_pid'],c['model_start_ticks'])
   if row and row.get('state')in NO_RAM:
    need(not pr['live'],'terminal fresh row model generation still live');growth=0;kind='FRESH_TERMINAL_PENDING_ARCHIVE'
   else:
    need(state!='TERMINAL_PENDING_VALIDATION','terminal fresh claim without terminal ledger row')
    growth=m.owner_growth(req,estimate,hard,pr['RSS_bytes']);kind='FRESH_LIVE_MODEL'if pr['live']else'FRESH_PENDING_OR_UNRESOLVED_CONSUMED'
   ram.append(dict(request=req,cohort=cohort,kind=kind,additional_RAM_bytes=growth,estimate_bytes=estimate,hard_bytes=hard,**pr))
   writes.append(dict(request=req,cohort=cohort,kind='FRESH_ACTUAL_REMAINING_CLAIM',bytes=remain))
  except Exception as exc:errors.append(req+'/'+cohort+': '+repr(exc))
 if claims:writes.append(dict(request=req,kind='ONE_SHARED_RESTORE_WINDOW_AND_2M_METADATA',bytes=max_window+2*M))
 actual=sum(x['bytes']for x in writes);advertised=q.get('reserved_write_bytes',0)
 if not(type(advertised)is int and advertised>=actual):errors.append(req+': actual claims exceed registered remaining-write carrier')
 if cp.exists()and sha(cp)!=pin['sha256']:errors.append(req+': claims transitioned during sample; resample')
 return dict(ram=ram,writes=writes,errors=errors,pin=pin)
def commitments(reg,current_request,m):
 need(current_request in SCOPES,'unrecognized current resource owner')
 qs=reg['registered_future_requests'];legacy=copy.deepcopy(reg)
 for req in SCOPES:legacy['registered_future_requests'].pop(req,None)
 # Old main top-level RUNNING is stale, so require actual terminal population.
 old=qs.get(OLD_EP)
 if old is not None:
  need(old.get('remaining')==0 and old.get('reserved_write_bytes')==0 and isinstance(old.get('consumed'),dict)and all(x.get('state')in TERMINAL for x in old['consumed'].values()),'old227 not terminal/zero-guarantee; cannot erase its future commitments')
 f=m.foreign_commitments(legacy)
 for req,root in SCOPES.items():
  if req==current_request or req not in qs:continue
  d=fresh_scope(req,qs[req],root,m);f['foreign_RAM_entries'].extend(d['ram']);f['foreign_write_entries'].extend(d['writes']);f['foreign_metadata_errors'].extend(d['errors']);f['foreign_claims_pins'][req]=d['pin']
 f['foreign_additional_RAM_bytes']=sum(x['additional_RAM_bytes']for x in f['foreign_RAM_entries']);f['foreign_remaining_write_bytes']=sum(x['bytes']for x in f['foreign_write_entries'])
 return f
def snapshot(current_request):
 m=base();began=time.monotonic()
 try:
  with m.LOCK.open('rb')as lock:
   fcntl.flock(lock,fcntl.LOCK_SH);raw=m.REG.read_bytes();reg=json.loads(raw);regsha=hashlib.sha256(raw).hexdigest();fcntl.flock(lock,fcntl.LOCK_UN)
  f=commitments(reg,current_request,m)
  if sha(m.REG)!=regsha:f['foreign_metadata_errors'].append('registry transitioned during sample; resample')
  return dict(m.sample_system(),**f,schema='EP_STAGE2_SCOPED_READONLY_RESOURCE_SNAPSHOT_V1',current_request=current_request,registry_sha256=regsha,no_actors_imported=True,runtime_kill_authorized=False,metadata_snapshot_cache_used=False,foreign_lease_required=False,foreign_lease_semantics='existing owner promises verified via pinned plans/specs/claims/intents/generations; does not require historical controller to be live',sample_started_monotonic=began,foreign_metadata_elapsed_seconds=time.monotonic()-began,pool_ceiling_added_to_remaining_writes=False,resource_source_semantics={'own':'caller computes own pending growth only; actualRSS/df already charged','otherfresh':'exact claims growth minus same-generation RSS + remaining writes + one restore window','DTC':'frozen owner contract/ghost/plan/spec bounds and floors preserved'})
 except Exception as exc:return dict(m.sample_system(),schema='EP_STAGE2_SCOPED_READONLY_RESOURCE_SNAPSHOT_V1',current_request=current_request,foreign_metadata_errors=[repr(exc)],foreign_additional_RAM_bytes=0,foreign_remaining_write_bytes=0,runtime_kill_authorized=False)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 return base().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=dict(DEFAULT_POLICY,**(policy or {})))
def forecast(input_id,history,policy=None):return base().forecast(input_id,history,policy=dict(DEFAULT_POLICY,**(policy or {})))
