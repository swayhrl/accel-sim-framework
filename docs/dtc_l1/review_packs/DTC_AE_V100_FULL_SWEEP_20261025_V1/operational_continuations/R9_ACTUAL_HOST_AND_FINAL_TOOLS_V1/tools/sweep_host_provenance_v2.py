"""Independent host V2 replay; preserves the original V1 history verifier."""
import pathlib,json,hashlib,gzip,importlib.util,math
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');ID='HOST_WORKINGSET40_V2';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def bind(q):
 old=load('host_V2_preserved_V1_verifier','sweep_host_provenance_v1.py');old_binding=old.bind(q);pp=T/'control/HOST_EXECUTION_PLAN_V2.json';p=read(pp);profile=q['host_execution_profiles'][ID];pub=read(T/'control/CONTINUATION_R9_PUBLICATION_READBACK.json');qual=read(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json')
 assert profile['plan_sha256']==sha(pp) and all(profile[k]==v for k,v in p.items()) and pub['verified'] and pub['commit']==profile['publication_commit']
 assert qual['status']=='PASS' and pub['qualification_sha256']==profile['qualification_sha256']==sha(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json') and qual['controller_sha256']==pub['controller_sha256']==sha(T/'tools/revision9/sweep_controller.py')
 for row in p['source_pins']:assert sha(row['path'])==row['sha256']
 before=read(T/'control/REQUEST_BEFORE_CONTINUATION_R9.json');prefix=set(p['preserved_prefix_cells']);assert len(prefix)==141 and prefix==set(before['consumed'])
 for c,row in before['consumed'].items():assert all(q['consumed'][c][k]==v for k,v in row.items()),'R9 changed a spent identity/receipt'
 assert p['maximum_jobs']==40
 transport=read(T/'control/R8_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R9.json');assert transport['signals_to_scientific_models']==transport['signals_to_original_frontends']==0 and transport['authority_writer_serialized_quiescent_retirement'] and all(r['preserved_or_naturally_closed'] for r in transport['active_generations_after'])
 return {'old_module':old,'old_binding':old_binding,'prefix':prefix,'profile':profile,'plan_sha256':sha(pp),'adapter_sha256':p['adapter_sha256'],'publication_commit':pub['commit']}
def verify_sample(r):
 assert r['host_execution_accounting']==ID and r['working_set_reservation_is_not_a_hard_cap'] is True
 s=r['cgroup_memory_stat_for_credit'];clean=max(0,s['file']-s['shmem']-s['file_mapped']-s['file_dirty']-s['file_writeback']);credit=max(0,min(s['inactive_file'],clean)-8*G);assert credit==r['cgroup_reclaimable_clean_inactive_file_credit_bytes']
 projected=0;legacy=[];seen=set()
 for e in r['RAM_reservation_entries']:
  assert e['cohort'] not in seen;seen.add(e['cohort']);hard=e['hard_cap_bytes'];rss=e['observed_model_RSS_bytes'];size=e['largest_member_bytes'];assert hard==16*G and rss>=0 and size>=0
  expected=hard if e['legacy_V1'] else min(hard,max(4*G,((8*size+G+G-1)//G)*G,((2*rss+G+G-1)//G)*G))
  assert expected==e['working_set_envelope_bytes'] and max(0,expected-rss)==e['additional_reserved_bytes'];projected+=max(0,expected-rss)
  if e['legacy_V1']:legacy.append(e['cohort'])
 assert projected==r['reserved_additional_live_and_candidate_RAM_bytes'] and set(legacy)==set(r['legacy_host_V1_live_cells'])
 free=None if r['cgroup_memory_max']=='max' else int(r['cgroup_memory_max'])-r['cgroup_memory_current'];eff=None if free is None else free+credit;assert eff==r['cgroup_effective_headroom_bytes'];hard_remaining=r['original_full_hard_cap_RAM_reservation_bytes'];mem=r['host_MemAvailable_bytes']
 old=mem>=64*G+hard_remaining and (eff is None or eff>=48*G+hard_remaining);raw=mem>=64*G+hard_remaining and (free is None or free>=48*G+hard_remaining)
 assert old==r['legacy_full_hard_cap_predicate_pass'] and raw==r['original_raw_cgroup_RAM_pass']
 scope=r['RAM_decision_scope'];assert scope in ['ADMISSION_PROJECTED_WORKINGSET','RUNTIME_ACTUAL_HEADROOM'];fresh=scope=='ADMISSION_PROJECTED_WORKINGSET';need=projected if fresh else 0;passed=mem>=64*G+need and (eff is None or eff>=48*G+need)
 if legacy:passed=passed and old and (not fresh or eff is None or eff>=56*G+hard_remaining)
 assert passed==r['physical_RAM_pass'],'recorded V2 RAM verdict not independently reproduced'
 return {'scope':scope,'legacy':bool(legacy),'pass':passed,'cache_credit':credit,'reserved_working_set_bytes':projected}
def verify(cell,binding,native):
 if cell in binding['prefix']:return binding['old_module'].verify(cell,binding['old_binding'],native)
 q=native.read_current_authority()[0]['registered_future_requests'][native.REQUEST];row=q['consumed'][cell];ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);assert sha(ip)==row['intent_sha256'] and intent['uuid']==row['uuid'];out=P(intent['output']);launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');b=intent['host_execution_binding'];assert b==launch['host_execution_binding']==pid['host_execution_binding']
 original=read(T/'control'/(cell+'_SPEC.json'));assert b['profile']==ID and b['adapter_sha256']==binding['adapter_sha256'] and b['plan_sha256']==binding['plan_sha256'] and b['original_spec_sha256']==sha(T/'control'/(cell+'_SPEC.json'))
 assert b['original_host_cpu']==original['host_cpu'] and b['actual_host_cpu'] in binding['profile']['allowed_CPUs'] and pid['host_cpu_affinity_actual']==[b['actual_host_cpu']]
 assert b['scientific_fields_changed'] is False and b['outer_RAM_accounting_changed'] is True and b['hard_cap_bytes']==original['limits']['max_process_tree_rss_bytes']==16*G and b['working_set_floor_bytes']==4*G and b['reservation_not_hard_cap'] is True and b['unchanged_original_native_function_source_sha256']==sha(T/'tools/sweep_native_cap1m.py')
 count=0;legacy=0;modes={}
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as stream:
  for line in stream:
   r=json.loads(line)
   if 'physical_RAM_pass' not in r:continue
   proof=verify_sample(r);count+=1;legacy+=int(proof['legacy']);modes[proof['scope']]=modes.get(proof['scope'],0)+1
 assert count>0
 return {'profile':ID,'host_adapter_applied':True,'actual_CPU':b['actual_host_cpu'],'original_spec_CPU':b['original_host_cpu'],'actual_PID_affinity_record_replayed':True,'adapter_sha256':binding['adapter_sha256'],'plan_sha256':binding['plan_sha256'],'publication_commit':binding['publication_commit'],'outer_RAM_sample_arithmetic_replayed':count,'sample_decision_modes':modes,'samples_with_legacy_guard_compatibility':legacy,'credit_derivation':'All six recorded memory.stat inputs independently replayed','hard_cap_unchanged_bytes':16*G,'working_set_floor_is_estimate_not_hard_cap':True,'scientific_Core_cache_config_unchanged':True}
