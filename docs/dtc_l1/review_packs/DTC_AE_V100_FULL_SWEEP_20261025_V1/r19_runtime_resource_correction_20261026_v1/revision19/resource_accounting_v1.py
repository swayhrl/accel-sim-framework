"""R19 five-scope actual RAM and bounded future native writes.
No ledger/claim/source edits. Exact departed generations lose future model
growth, retaining existing-file native restore+16MiB. Closed peers require a
source-pinned all-DONE/archive certificate. Runtime floors remain64/48GiB.
"""
import pathlib,json,hashlib,importlib.util,os,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');G=1024**3;M=1024**2;ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';OLD='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';LAVA='DTC_AE_LAVAMEM_REPAIR_20261026_V2';LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';NEW='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1';ROOTS={ORIG:T,OLD:F/'validation',LAVA:F/'validation_lava_memory_v2',LATE:F/'validation_late_failure_v1',NEW:F/'validation_remaining_failure_v1'};POLICY=F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json';_native=None
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def require(x,msg):
 if not x:raise RuntimeError(msg)
def authority():
 global _native
 if _native is None:
  s=importlib.util.spec_from_file_location('r19_private_readonly_authority',T/'tools/sweep_native_cap1m.py');_native=importlib.util.module_from_spec(s);s.loader.exec_module(_native)
 return _native.read_current_authority()
def claims(root):return read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']if(root/'control/POOL_DISPATCH_RESERVATIONS.json').exists()else{}
def point_spec(root,c,q=None):
 path=root/'control'/((c+'_SPEC.json')if root==T else('specs/'+c+'.json'));data=path.read_bytes();s=json.loads(data);require(s['cohort']==c,'spec cohort mismatch')
 if q is not None:require(q['admitted_specs'].get(c)==hashlib.sha256(data).hexdigest(),'registered resource spec pin changed')
 return s
def output_cap(root,s):
 upper=s['limits']['max_result_directory_bytes'];p=root/'control'/('OPERATIONAL_OUTPUT_CAP_'+s['cohort']+'.json')
 if not p.exists():return upper
 cap=read(p);require(type(cap['effective_result_cap_bytes'])is int and 0<cap['effective_result_cap_bytes']<=upper,'invalid effective cap')
 if root!=T:require(sha(p)==s['operational_output_cap_sha256'],'effective cap pin changed')
 return cap['effective_result_cap_bytes']
def proc(pid,ticks):
 try:
  p=P('/proc')/str(pid);st=(p/'stat').read_text().rsplit(')',1)[1].split()
  if int(st[19])!=ticks or st[0]in ['Z','X']:return 0,False
  rss=int(next(x.split()[1]for x in(p/'status').read_text().splitlines()if x.startswith('VmRSS:')))*1024;return rss,True
 except(FileNotFoundError,ProcessLookupError,StopIteration):return 0,False
def rss(root,row):
 p=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if not p.exists():return 0,False
 b=read(p);return proc(b['pid'],b['start_ticks'])
def size(path):return sum(p.stat().st_size for p in path.rglob('*')if p.is_file())if path.exists()else 0
def archived(root,c,row):
 p=root/'control'/(c+'_ARCHIVE_RECEIPT.json')
 if not p.exists():return False
 try:
  ip=root/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');out=root/'DTC/run/results'/row['uuid']
  # Registry was sampled before local closure files. A newly visible receipt or
  # an exclusive-json writer not yet flushed is not proof and not an exception.
  if not(dp.exists()and(out/'NATIVE_EXIT.json').exists()and'execution_receipt'in row):return False
  done=read(dp)
  if not(done==read(out/'NATIVE_EXIT.json')==row['execution_receipt']and done['uuid']==read(ip)['uuid']==row['uuid']and sha(ip)==row['intent_sha256']):return False
  a=read(p);return a['cohort']==c and a['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and a['source_disposition']=='SOURCE_KEEP'
 except(OSError,ValueError,KeyError):return False
def policy_and_ghosts(reg):
 p=read(POLICY);require(p['schema']=='R19_FIVE_SCOPE_RESOURCE_ACCOUNTING_POLICY_V1','wrong policy');gp=P(p['ghost_certificate_path']);require(sha(gp)==p['ghost_certificate_sha256'],'ghost certificate changed');s=importlib.util.spec_from_file_location('r19_private_departed_verifier',P(p['ghost_verifier_path']));v=importlib.util.module_from_spec(s);s.loader.exec_module(v);require(sha(v.__file__)==p['ghost_verifier_sha256'],'departed verifier source changed');ghost,retained=v.verified_departed(reg,read(gp));cp=P(p['closed_scope_certificate_path']);require(sha(cp)==p['closed_scope_certificate_sha256'],'closed-scope certificate changed');return p,ghost,retained,read(cp)
def closed_verified(request,q,root,cs,certificate):
 if q.get('state')!='CLOSED':return False
 try:
  proof=certificate['scopes'].get(request)
  if not proof:return False # Later normal CLOSED requests keep ordinary1GiB accounting.
  if not(q['budget']==proof['budget']and q['remaining']==0 and set(q['consumed'])==set(proof['points'])and set(cs)<=set(q['consumed'])):return False
  for c,row in q['consumed'].items():
   x=proof['points'][c]
   if not(row['uuid']==x['uuid']and row['intent_sha256']==x['intent_sha256']):return False
   for pin in x['pins']:
    if sha(pin['path'])!=pin['sha256']:return False
   if not archived(root,c,row)or rss(root,row)[1]:return False
  return True
 except(OSError,ValueError,KeyError):return False
def memory(request,s):
 hard=s['limits']['max_process_tree_rss_bytes'];estimate=96*G if request==LAVA else 4*G
 if request==NEW:
  planpath=ROOTS[NEW]/'control/EXECUTION_PLAN_V1.json';plan=read(planpath);binding=plan['per_cohort_memory'][s['cohort']];estimate=s['estimated_peak_model_RAM_bytes'];require(binding['max_process_tree_rss_bytes']==hard and binding['estimated_peak_model_RAM_bytes']==estimate and binding['initial_working_set_floor_bytes']==4*G,'mixed NEW4 memory profile mismatch')
 require(type(hard)is int and type(estimate)is int and 4*G<=estimate<=hard,'invalid working-set estimate');return hard,estimate
def system_sample():
 mem=int(next(x.split()[1]for x in P('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024;c=P('/sys/fs/cgroup');maximum=(c/'memory.max').read_text().strip();current=int((c/'memory.current').read_text());stat={k:int(v)for k,v in(x.split()for x in(c/'memory.stat').read_text().splitlines())};fields={k:stat.get(k,0)for k in ['file','inactive_file','shmem','file_mapped','file_dirty','file_writeback']};clean=max(0,fields['file']-fields['shmem']-fields['file_mapped']-fields['file_dirty']-fields['file_writeback']);credit=max(0,min(fields['inactive_file'],clean)-8*G);effective=None if maximum=='max'else int(maximum)-current+credit;v=os.statvfs(T);return dict(host_MemAvailable_bytes=mem,cgroup_memory_max=maximum,cgroup_memory_current=current,cgroup_memory_stat_for_credit=fields,cgroup_reclaimable_clean_inactive_file_credit_bytes=credit,cgroup_effective_headroom_bytes=effective,native_free_bytes=v.f_bavail*v.f_frsize,free_inodes=v.f_favail)
def resources(s,fresh_source=False):
 reg,epoch=authority();qs=reg['registered_future_requests'];owner=s.get('request',ORIG);require(owner in ROOTS,'unknown resource owner');p,ghost,retained,closure=policy_and_ghosts(reg);ram=[];writes={};details={};closed=[];quotas={};claim_snapshots={};ghost_rows=[]
 for request,root in ROOTS.items():
  if request not in qs:
   require(not(fresh_source and owner==request),'unregistered candidate cannot consume capacity');continue
  q=qs[request];cs=claims(root);claim_snapshots[request]=cs
  if closed_verified(request,q,root,cs,closure):writes[request]=0;details[request]=[];quotas[request]=True;closed.append(request);continue
  total=G;wr=[]
  for c,row in q['consumed'].items():
   if archived(root,c,row):continue
   spec=point_spec(root,c,q);cap=output_cap(root,spec);out=root/'DTC/run/results'/row['uuid'];nbytes=size(out);done=row.get('execution_receipt');departed=request==ORIG and c in ghost and ghost[c]==row['uuid'];reserve=nbytes+16*M if done or departed else max(0,2*cap-nbytes);total+=reserve;wr.append(dict(cohort=c,uuid=row['uuid'],remaining_write_and_native_restore_bytes=reserve,observed_result_bytes=nbytes,real_execution_receipt_present=bool(done),certified_departed_generation=departed))
   if departed:ghost_rows.append(dict(cohort=c,uuid=row['uuid'],existing_file_native_restore_bound_bytes=reserve,future_model_RAM_bytes=0));continue
   if not done:
    used,live=rss(root,row);hard,estimate=memory(request,spec);envelope=min(hard,max(4*G,estimate,used));ram.append(dict(request=request,cohort=c,kind='OBSERVED_MODEL'if live else'UNRESOLVED_CONSUMED_GENERATION',RSS_bytes=used,model_generation_observed_live=live,hard_cap_bytes=hard,estimated_peak_model_RAM_bytes=estimate,envelope_bytes=envelope,additional_reserved_bytes=max(0,envelope-used)))
  pending=set(cs)-set(q['consumed'])
  if fresh_source and owner==request and s['cohort']not in q['consumed']:pending.add(s['cohort'])
  for c in sorted(pending):
   canonical=point_spec(root,c,q);spec=s if owner==request and c==s.get('cohort')else canonical
   require(all(spec['limits'][key]==canonical['limits'][key]for key in ['max_process_tree_rss_bytes','max_result_directory_bytes']),'candidate resource limits differ from registered spec');cap=output_cap(root,spec)
   if c in cs:require(cs[c]['result_cap_bytes']==cap,'serialized claim output cap mismatch')
   reserve=2*cap;total+=reserve;wr.append(dict(cohort=c,claimed_or_new_candidate=True,remaining_write_and_native_restore_bytes=reserve));hard,estimate=memory(request,spec);envelope=min(hard,max(4*G,estimate));ram.append(dict(request=request,cohort=c,kind='CLAIM_NOT_OBSERVED_MODEL'if c in cs else'NEW_CANDIDATE',RSS_bytes=0,model_generation_observed_live=False,hard_cap_bytes=hard,estimated_peak_model_RAM_bytes=estimate,envelope_bytes=envelope,additional_reserved_bytes=envelope))
  writes[request]=total;details[request]=wr;quotas[request]=total<=q['reserved_write_bytes']
 peers=[]
 for key,q in qs.items():
  if key in ROOTS or q.get('state')in ['COMPLETE','CLOSED','STOP_UNACCEPTED','COMPAT_PARTIAL_COMPLETE']:continue
  v=q.get('reserved_write_bytes');require(type(v)is int and v>=0,'unbounded foreign writer');peers.append(dict(request=key,reserved_write_bytes=v))
 actual=system_sample();projected=sum(x['additional_reserved_bytes']for x in ram);required=5*G+sum(writes.values())+sum(x['reserved_write_bytes']for x in peers);need=projected if fresh_source else 0;eff=actual['cgroup_effective_headroom_bytes'];return dict(actual,schema='R19_FIVE_SCOPE_EXACT_FUTURE_WRITES_ACTUAL_RAM_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),resource_module_sha256=sha(__file__),policy_sha256=sha(POLICY),local_safety_floor_bytes=5*G,required_free_bytes=required,known_remaining_writes_by_request=writes,write_entries_by_request=details,per_scope_write_ceiling_pass=quotas,closed_scopes_independently_proven=closed,certified_departed_generation_entries=ghost_rows,uncertain_ghosts_retained=retained,peer_reservations=peers,other_outstanding_write_reservations_bytes=sum(x['reserved_write_bytes']for x in peers),RAM_reservation_entries=ram,reserved_additional_live_and_candidate_RAM_bytes=projected,RAM_decision_scope='ADMISSION_PROJECTED_WORKINGSET'if fresh_source else'RUNTIME_ACTUAL_HEADROOM',host_floor_bytes=64*G,cgroup_floor_bytes=48*G,physical_RAM_pass=actual['host_MemAvailable_bytes']>=64*G+need and(eff is None or eff>=48*G+need),physical_disk_pass=actual['native_free_bytes']>required and actual['free_inodes']>=100000 and all(quotas.values()),claim_is_not_an_observed_active_model=True,no_scientific_receipt_or_history_mutation=True)
def future_engine_install(native):
 require(not hasattr(native,'_R19_FUTURE_RESOURCE_BINDING'),'do not install resource binding twice');binding=dict(schema='EXPLICIT_R19_FIVE_SCOPE_FUTURE_RESOURCE_ACCOUNTING_BINDING_V1',resource_module_path=str(P(__file__).resolve()),resource_module_sha256=sha(__file__),policy_path=str(POLICY),policy_sha256=sha(POLICY),resource_schema='R19_FIVE_SCOPE_EXACT_FUTURE_WRITES_ACTUAL_RAM_V1',host_runtime_floor_bytes=64*G,cgroup_runtime_floor_bytes=48*G,disk_safety_floor_bytes=5*G,initial_working_set_floor_bytes=4*G,scientific_loop_or_options_changed=False)
 old=native.exclusive
 def exclusive(path,obj):
  if P(path).name.endswith('.INTENT.json')or P(path).name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:obj=dict(obj,resource_accounting_binding_R19=binding)
  return old(path,obj)
 native.resources=resources;native.exclusive=exclusive;native._R19_FUTURE_RESOURCE_BINDING=binding;return native
