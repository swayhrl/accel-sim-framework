"""Read-only successor resource view: add exact DTC16 owner; no actors/writes."""
import pathlib,hashlib,importlib.util,json,copy,math
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1')
OLD=J/'research/performance_first_v2_20261103_v1/agent_d/resources_v2_candidate/resources_v2.py'
OLD_SHA='cd11412b41a754fddbd66c836a4fda59ac4f31683b0677d9f67faa7bd5652da6'
DTC='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1';DTCROOT=P('/root/data/dtc_stage_iia_first16_20261104_v1')
G=1<<30;M=1<<20
def need(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def exact(r):need(sha(r['path'])==r['sha256'],'pinned resource owner artifact drift '+r['path']);return read(r['path'])
def controller_margin(pr,policy,existing):
 """Only future growth; current RSS is already in host/cgroup used. Dedup PID/gen."""
 if not pr['live']:return 0,0
 rss=pr['RSS_bytes'];target=max(policy['minimum_prediction_bytes'],math.ceil(rss*policy['history_multiplier'])+policy['history_additive_bytes'])
 margin=max(0,target-rss)
 previous=sum(r.get('additional_RAM_bytes',0)for r in existing if r.get('pid')==pr['pid']and r.get('start_ticks')==pr['start_ticks'])
 return max(0,margin-previous),margin
def owner_mapping(q,m,existing_RAM):
 need(q.get('request')==DTC and q.get('schema')=='DTC_STAGEII_FIRST16_REGISTERED_REQUEST_V1','unexpected DTC16 contract/schema')
 need(q.get('budget')==len(q.get('admitted_specs',{}))==16 and type(q.get('remaining'))is int,'DTC16 exact fixedscope')
 planpath=DTCROOT/'control/EXECUTION_PLAN.json';need(sha(planpath)==q['execution_plan_sha256'],'DTC16 plan pin drift');plan=read(planpath)
 need(plan['request']==DTC and plan.get('no_extensions')is True,'DTC16 scope extended')
 need(plan['parent_pid']==q['owner_pid']and plan['parent_start_ticks']==q['owner_start_ticks'],'DTC16 owner attach mismatch')
 policyref=next(z for z in plan['source_pins']if z['path']==str(DTCROOT/'control/RESOURCE_POLICY.json'));policy=exact(policyref)
 cp=DTCROOT/'control/POOL_DISPATCH_RESERVATIONS.json';csha=sha(cp);claims=read(cp)['claims'];need(type(claims)is dict,'DTC16 claims type')
 rows=q.get('consumed',{});need(type(rows)is dict and set(rows)<=set(q['admitted_specs'])and set(claims)<=set(q['admitted_specs']),'DTC16 populations')
 need(q['remaining']==16-len(rows),'DTC16 consumed arithmetic')
 reserved=q.get('reserved_write_bytes');need(type(reserved)is int and reserved>=0,'DTC16 published writer unbounded')
 ram=[];checks=[];all_done=True;all_archived=True;derived_writes=policy['metadata_reserve_bytes']
 for case in sorted(set(rows)|set(claims)):
  sp=DTCROOT/'control/specs'/(case+'.json');need(sha(sp)==q['admitted_specs'][case],'DTC16 exactspec drift');s=read(sp)
  cap=s['limits']['max_result_directory_bytes'];hard=s['limits']['max_process_tree_rss_bytes'];estimate=s['estimated_peak_model_RAM_bytes']
  need(all(type(x)is int and x>0 for x in [cap,hard,estimate])and estimate<=hard,'DTC16 resource bounds')
  row=rows.get(case);pr=dict(live=False,RSS_bytes=0,PSS_bytes=0);done=False;arch=False
  if row:
   ip=P(row['intent']);need(sha(ip)==row['intent_sha256'],'DTC16 intent drift');intent=read(ip);need(intent['uuid']==row['uuid'],'DTC16 UUID')
   out=DTCROOT/'DTC/run/results'/row['uuid'];mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
   if mp.exists():
    ident=read(mp);pr=m.process(ident['pid'],ident['start_ticks'])
   rec=row.get('execution_receipt')
   if rec:
    dp=DTCROOT/'control/qualification_ledger'/(case+'.DONE.json')
    need(read(dp)==rec==read(out/'NATIVE_EXIT.json')and rec['uuid']==row['uuid'],'DTC16 DONE/EXIT/registry mismatch')
    need(not pr['live'],'DTC16 DONE but same-generation model still live')
    done=True;arch=m.archived(DTCROOT,case,row)
   growth=0 if done else m.owner_growth(DTC,estimate,hard,pr['RSS_bytes'])
  else:
   need(case in claims,'DTC16 unconsumed claim missing');growth=estimate
  all_done=all_done and done;all_archived=all_archived and arch
  # Existing writes are in df. Preserve advertised carrier once, not full budget or each cap.
  if not arch:derived_writes+=cap if done else 2*cap
  ram.append(dict(request=DTC,cohort=case,kind='DTC16_COMPLETED_NO_MODEL_RAM'if done else'DTC16_LIVE_OR_CLAIM_PENDING',additional_RAM_bytes=growth,estimate_bytes=estimate,hard_bytes=hard,**pr))
  checks.append(dict(cohort=case,DONE=done,archived=arch,model_live=pr['live']))
 need(derived_writes<=reserved or(reserved==0 and not claims and all_done and all_archived),'DTC16 derived pending writes exceed published carrier')
 terminalpath=DTCROOT/'analysis/EXECUTION_TERMINAL.json';terminal=read(terminalpath)if terminalpath.exists()else{}
 batch_terminal=(len(rows)==16 and q['remaining']==0 and not claims and all_done and all_archived and terminal.get('status')=='ALL16_STRICT_OR_ARCHIVED_NEGATIVE_TERMINAL'and set(terminal.get('states',{}))==set(rows))
 closed_released=q.get('state')in ['COMPLETE','CLOSED','SEALED']and reserved==0 and batch_terminal
 owner=m.process(q['owner_pid'],q['owner_start_ticks'])
 # A reused live PID is not evidence the registered owner departed.
 proc=P('/proc')/str(q['owner_pid'])/'stat'
 if proc.exists():
  observed=int(proc.read_text().rsplit(')',1)[1].split()[19]);need(observed==q['owner_start_ticks'],'DTC16 owner PID generation changed')
 leasepath=m.T/'control/BATCH_LEASE.json';lease=read(leasepath)
 need(lease['pid']==q['owner_pid']and lease['start_ticks']==q['owner_start_ticks']and DTC in lease['additional_requests'],'DTC16 not attached to registered shared-parent lease')
 if owner['live']:
  need(sha(plan['parent_controller_path'])==plan['parent_controller_sha256'],'DTC16 actual parent code drift')
  fd=P('/proc')/str(owner['pid'])/'fd'/str(lease['fd']);need(fd.exists()and str(m.N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')==str(fd.resolve()),'DTC16 shared-parent native lease FD mismatch')
  need('FLOCK'in(fd.parent.parent/'fdinfo'/str(lease['fd'])).read_text(),'DTC16 shared-parent lease not held')
 added,margin=(0,0)if closed_released else controller_margin(owner,policy,existing_RAM+ram)
 if added:ram.append(dict(request=DTC,kind='SHARED_PARENT_FUTURE_MARGIN_ONCE_NOT_CURRENT_RSS',pid=owner['pid'],start_ticks=owner['start_ticks'],RSS_bytes=owner['RSS_bytes'],additional_RAM_bytes=added,estimated_incremental_margin_bytes=margin,shared_with_old_DTC_parent=True))
 if not owner['live']and not closed_released:
  # No claimed controller departure/release; preserve a conservative one-process future allowance.
  ram.append(dict(request=DTC,kind='OWNER_NOT_LIVE_UNRELEASED_METADATA_FORECAST',additional_RAM_bytes=policy['minimum_prediction_bytes'],RSS_bytes=0,shared_with_old_DTC_parent=True))
 need(sha(cp)==csha,'DTC16 claims changed during read; resample')
 writes=[dict(request=DTC,kind='PUBLISHED_WRITE_CARRIER_PRESERVED_ONCE_NOT_BUDGET_MULTIPLIED',bytes=reserved,derived_remaining_bound_bytes=derived_writes,closed_released=closed_released)]
 return dict(ram=ram,writes=writes,pin=dict(path=str(cp),sha256=csha,claims=len(claims)),owner=owner,batch_terminal=batch_terminal,owner_closed_released=closed_released,published_write_bytes=reserved,policy_ref=policyref,terminal_ref=dict(path=str(terminalpath),sha256=sha(terminalpath)if terminalpath.exists()else None),model_checks=checks,confirmed_foreign_host_floor_bytes=0 if closed_released else policy['min_host_headroom_bytes'],confirmed_foreign_cgroup_floor_bytes=0 if closed_released else policy['min_cgroup_headroom_bytes'],confirmed_foreign_native_floor_bytes=0 if closed_released else policy['native_safety_floor_bytes'],current_controller_RSS_not_added_as_future_RAM=True)
def base_runtime():
 need(sha(OLD)==OLD_SHA,'frozen prior V2 adapter drift');sp=importlib.util.spec_from_file_location('readonly_recovery_original_v2',OLD);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);factory=v.qualified_math
 def qualified():
  h=factory();bf=h.base
  def base():
   m=bf();foreign=m.foreign_commitments
   def mapped(reg):
    legacy=copy.deepcopy(reg);q=legacy['registered_future_requests'].pop(DTC,None);f=foreign(legacy)
    if q is not None:
     try:
      d=owner_mapping(q,m,f['foreign_RAM_entries']);f['foreign_RAM_entries'].extend(d['ram']);f['foreign_write_entries'].extend(d['writes']);f['foreign_claims_pins'][DTC]=d['pin'];f['DTC16_owner_accounting']=d
      for k in ['confirmed_foreign_host_floor_bytes','confirmed_foreign_cgroup_floor_bytes','confirmed_foreign_native_floor_bytes']:f[k]=max(f.get(k,0),d[k])
     except Exception as e:
      # Keep the entire explicit promise even when metadata fails; the error forbids admission.
      n=q.get('reserved_write_bytes');f['foreign_write_entries'].append(dict(request=DTC,kind='INVALID_MAPPING_PROMISE_NOT_RELEASED',bytes=n if type(n)is int and n>=0 else 0));f['foreign_metadata_errors'].append('DTC16 mapping HOLD: '+repr(e))
    f['foreign_additional_RAM_bytes']=sum(x['additional_RAM_bytes']for x in f['foreign_RAM_entries']);f['foreign_remaining_write_bytes']=sum(x['bytes']for x in f['foreign_write_entries'])
    return f
   m.foreign_commitments=mapped;return m
  h.base=base;return h
 v.qualified_math=qualified;return v
def snapshot(current_request):
 v=base_runtime();s=v.snapshot(current_request)
 s.update(schema='EP_MAIN_RECOVERY_KNOWN_DTC16_READONLY_RESOURCE_SNAPSHOT_V1',one_scope_restore_bound_bytes=None,scope_restore_upper_bounds_bytes={v.REQUESTS['system']:256*M,v.REQUESTS['highclock']:128*M},two_new_scope_restore_window_upper_bound_bytes=384*M,restore_math='ACTUAL_SYSTEM256_PLUS_HIGH128=384MiB_CONSERVATIVE_BOUND; existing caller/peer restore charges retained, not added twice',unknown_owners_still_fail_closed=True,minimum_emergency_floor_bytes=G,no_DTC_contract_or_ledger_mutated=True)
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 v=base_runtime();p=dict(v.DEFAULT_POLICY,**(policy or{}));own_floor=p.get('native_safety_floor_bytes',G);p['native_safety_floor_bytes']=max(own_floor,s.get('confirmed_foreign_native_floor_bytes',0));d=v.admit(s,own_pending_additional_RAM,own_remaining_writes,policy=p);d.update(own_emergency_floor_bytes=own_floor,confirmed_foreign_native_floor_bytes=s.get('confirmed_foreign_native_floor_bytes',0),restore_upper_bound_bytes=384*M,unknown_owners_fail_closed=True);return d
def forecast(input_id,history,policy=None):return base_runtime().forecast(input_id,history,policy=policy)
