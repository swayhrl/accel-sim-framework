import pathlib,json,gzip,hashlib,datetime,collections,re,ast
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');CELL='E2-AEV100-e7bb67e63e3c3847-DH';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
i=read(T/'control/qualification_ledger'/(CELL+'.INTENT.json'));out=P(i['output']);done=read(T/'control/qualification_ledger'/(CELL+'.DONE.json'));original=read(T/'control'/(CELL+'_SPEC.json'));launch=read(out/'NATIVE_LAUNCH.json');resources=[];decisions=[]
with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if 'physical_RAM_pass' in r:resources.append(r)
  if 'DTC_exact_original_policy' in r:decisions.append(r['DTC_exact_original_policy'])
progress=[]
with gzip.open(out/'progress.jsonl.gz','rt') as f:
 for line in f:progress.append(json.loads(line))
h=hashlib.sha256();size=0;tail=collections.deque(maxlen=12);hits=[]
pattern=re.compile(br'out.of.memory|bad_alloc|cannot allocate|oom.kill|killed process|CRASH|Assertion|SIGKILL|SIGTERM|deadlock',re.I)
with gzip.open(out/'raw.log.gz','rb') as f:
 for num,line in enumerate(f,1):
  h.update(line);size+=len(line);tail.append(line.decode(errors='replace').rstrip())
  if pattern.search(line):hits.append({'line':num,'text':line.decode(errors='replace').rstrip()})
assert h.hexdigest()==done['raw_uncompressed_sha256'] and size==done['raw_uncompressed_bytes'] and sha(out/'raw.log.gz')==done['raw_sha256']
bad=[r for r in resources if not r['physical_RAM_pass']];assert len(bad)==1;failed=bad[0];maximum=int(failed['cgroup_memory_max']);current=failed['cgroup_memory_current'];reservation=failed['reserved_additional_live_and_candidate_RAM_bytes'];free=maximum-current;threshold=48*G+reservation;gap=threshold-free
def sample_info(r):return {k:r[k] for k in ['utc','elapsed_seconds','host_MemAvailable_bytes','cgroup_memory_current','cgroup_memory_max','reserved_additional_live_and_candidate_RAM_bytes','physical_RAM_pass','physical_disk_pass','process_tree_observed_rss_bytes']}
failed_time=datetime.datetime.fromisoformat(failed['utc']);peer=[]
for reserve in failed['own_reservations']:
 cell=reserve['cohort'];ii=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));oo=P(ii['output']);ss=read(T/'control'/(cell+'_SPEC.json'));samples=[]
 with gzip.open(oo/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line)
   if 'process_tree_observed_rss_bytes' in r:samples.append(r)
 nearest=min(samples,key=lambda r:abs((datetime.datetime.fromisoformat(r['utc'])-failed_time).total_seconds()))
 before=[r for r in samples if datetime.datetime.fromisoformat(r['utc'])<=failed_time];last_before=before[-1] if before else None
 dp=T/'control/qualification_ledger'/(cell+'.DONE.json');dd=read(dp) if dp.exists() else None
 peer.append({'cohort':cell,'program':ss['program'],'arm':ss['cell'],'uuid':ii['uuid'],'hard_RSS_AS_cap_bytes':ss['limits']['max_process_tree_rss_bytes'],'recorded_write_reservation_bytes':reserve.get('remaining_write_and_restore_bytes'),'output':str(oo),'nearest_recorded_process_tree_RSS_bytes':nearest['process_tree_observed_rss_bytes'],'nearest_sample_time':nearest['utc'],'nearest_sample_offset_seconds':(datetime.datetime.fromisoformat(nearest['utc'])-failed_time).total_seconds(),'last_sample_at_or_before':sample_info(last_before) if last_before else None,'eventual_observed_peak_RSS_bytes_not_known_at_failure':None if dd is None else dd['peak_observed_rss_bytes'],'RSS_scope_caveat':'peer stream is 10-second process-tree RSS;original reservation reads only model VmRSS at its own sampling instant;per-peer exact contemporaneous model RSS was not recorded','resource_samples_sha256':sha(oo/'RESOURCE_SAMPLES.jsonl.gz'),'original_spec_sha256':sha(T/'control'/(cell+'_SPEC.json')),'intent_sha256':sha(T/'control/qualification_ledger'/(cell+'.INTENT.json')),'done_sha256':sha(dp) if dp.exists() else None})
def fields(value,path=''):
 found=[]
 if isinstance(value,dict):
  for key,val in value.items():
   sub=path+'.'+key
   if re.search(r'oom|swap|pressure|psi|memory.stat|memory.events|fault',key,re.I):found.append({'field':sub,'value':val})
   found.extend(fields(val,sub))
 elif isinstance(value,list):
  for index,val in enumerate(value):found.extend(fields(val,path+'['+str(index)+']'))
 return found
trace=(out/'actual_file_process_network.log').read_text();signal_hits=[line for line in trace.splitlines() if re.search(r'kill\(|SIGTERM|SIGKILL|SIGABRT|ENOMEM',line)]
paths=[T/'control/qualification_ledger'/(CELL+'.INTENT.json'),T/'control/qualification_ledger'/(CELL+'.DONE.json'),T/'control'/(CELL+'_SPEC.json'),out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',out/'NATIVE_EXIT.json',out/'raw.log.gz',out/'progress.jsonl.gz',out/'RESOURCE_SAMPLES.jsonl.gz',out/'actual_file_process_network.log',T/'analysis'/(CELL+'.FAILURE_CLASSIFICATION_R5.json'),T/'analysis'/(CELL+'.RESULT.json'),T/'control'/(CELL+'_ARCHIVE_RECEIPT.json'),T/'tools/sweep_native_cap1m.py',T/'tools/sweep_frontend_cap1m.py',T/'tools/sweep_failure_review_host_v1.py',T/'tools/sweep_host_execution_v1.py',T/'tools/sweep_host_execution_v4.py',T/'tools/sweep_live_ram_override_v1.py']
effective=T/'control/effective_specs'/(CELL+'.json')
if effective.exists():paths.append(effective)
for p in peer:
 for item in [T/'control'/(p['cohort']+'_SPEC.json'),T/'control/qualification_ledger'/(p['cohort']+'.INTENT.json'),T/'control/qualification_ledger'/(p['cohort']+'.DONE.json'),P(p['output'])/'RESOURCE_SAMPLES.jsonl.gz']:
  if item.exists() and item not in paths:paths.append(item)
report={'cell':CELL,'uuid':done['uuid'],'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'done':done,'intent':i,'original_spec_limits':original['limits'],'original_expected':original['expected'],'launch_resources':launch['resources'],'resource_count':len(resources),'decision_count':len(decisions),'decisions_last':decisions[-1],'RAM_fail_samples':bad,'resource_neighborhood':[sample_info(r) for r in resources[-5:]],'formula':{'cgroup_free_bytes':free,'required_with_old_reservation_bytes':threshold,'shortage_bytes':gap,'shortage_MiB':gap/1024**2,'host_required_bytes':64*G+reservation,'host_margin_bytes':failed['host_MemAvailable_bytes']-(64*G+reservation),'counterfactual_actual_only_no_cache_credit_pass':failed['host_MemAvailable_bytes']>=64*G and free>=48*G,'counterfactual_R7_cache_credit_minimum_bytes':max(0,gap),'counterfactual_R7_min_clean_inactive_before_8GiB_margin_bytes':8*G+max(0,gap)},'all_failure_time_budget_entries':peer,'progress':{'count':len(progress),'first':progress[0],'last':progress[-1],'phases':dict(collections.Counter(r['phase'] for r in progress)),'ends':dict(collections.Counter(r['end'] for r in progress))},'raw':{'full_uncompressed_sha256':h.hexdigest(),'full_uncompressed_bytes':size,'diagnostic_pattern_hits':hits,'last12_lines':list(tail)},'trace_signal_hits':signal_hits,'historical_oom_swap_PSI_fault_related_fields_found':fields(resources)+fields(decisions)+fields(launch['resources']),'evidence':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]}
del report['historical_oom_swap_PSI_fault_related_fields_found']
def series(values):return {'first':values[0],'last':values[-1],'min':min(values),'max':max(values),'net_change':values[-1]-values[0]}
report['historical_guard_summary']={'cgroup_events':{k:series([d['sample']['cgroup']['events'][k] for d in decisions]) for k in decisions[0]['sample']['cgroup']['events']},'host_oom_kill':series([d['sample']['host_oom_kill'] for d in decisions]),'cgroup_swap_current_bytes':series([int(d['sample']['cgroup']['memory.swap.current']) for d in decisions]),'host_pswpin_pages':series([d['sample']['pswpin'] for d in decisions]),'host_pswpout_pages':series([d['sample']['pswpout'] for d in decisions]),'policy_decision_counts':dict(collections.Counter(d['decision']['decision'] for d in decisions)),'host_and_cgroup_memory_PSI':{scope:{kind:{k:series([float((d['sample']['pressure'] if scope=='host' else d['sample']['cgroup_pressure_parsed'])['memory'][kind][k]) for d in decisions]) for k in ['avg10','avg60','avg300','total']} for kind in ['some','full']} for scope in ['host','cgroup']},'own_major_fault_delta':series([d['decision']['domains']['host']['own_major_fault_delta'] for d in decisions]),'historical_memory_stat_cache_inputs_recorded':False}
replay=[]
for r in resources:
 reserve=r['reserved_additional_live_and_candidate_RAM_bytes'];hostok=r['host_MemAvailable_bytes']>=64*G+reserve;cgroupok=r['cgroup_memory_max']=='max' or int(r['cgroup_memory_max'])-r['cgroup_memory_current']>=48*G+reserve;assert r['physical_RAM_pass']==(hostok and cgroupok);replay.append({'utc':r['utc'],'host_pass':hostok,'cgroup_pass':cgroupok,'cgroup_budget_margin_bytes':None if r['cgroup_memory_max']=='max' else int(r['cgroup_memory_max'])-r['cgroup_memory_current']-(48*G+reserve)})
assert all(p['seq']==idx+1 and p['generation']==done['uuid'] and p['pid']==progress[0]['pid'] and p['input']==original['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==original['original_environment']['DTC_AG7_ROI_SHA'] and (idx==0 or p['mono_ns']>progress[idx-1]['mono_ns'] and p['completed']>=progress[idx-1]['completed']) for idx,p in enumerate(progress))
report['all_resource_predicate_replays']=replay;report['progress']['all_sequence_identity_monotonic_checks_passed']=True
print(json.dumps(report,ensure_ascii=False,indent=2))
