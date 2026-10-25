"""40-slot host plan with4GiB initial admission and measured RSS growth.

FourGiB is an estimated reservation floor, never the16GiB hard RSS/AS cap.
Existing frontend RAM predicates transition explicitly before V4 dispatch.
"""
import pathlib,json,hashlib,importlib.util,os,copy,math
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');ID='HOST_ACTUAL4G40_V4';G=1024**3;BODY_CACHE={}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def credit(stat):
 clean=max(0,stat.get('file',0)-stat.get('shmem',0)-stat.get('file_mapped',0)-stat.get('file_dirty',0)-stat.get('file_writeback',0));return max(0,min(stat.get('inactive_file',0),clean)-8*G)
def envelope(hard,rss,largest_member,legacy=False):
 if legacy:return hard
 return min(hard,max(4*G,rss))
def ram_decision(mem,maximum,current,cache,projected,hard_remaining,fresh,legacy):
 effective=None if maximum=='max' else int(maximum)-current+cache
 hard_pass=mem>=64*G+hard_remaining and (effective is None or effective>=48*G+hard_remaining)
 need=projected if fresh else 0
 passed=mem>=64*G+need and (effective is None or effective>=48*G+need)
 if legacy:passed=passed and hard_pass
 return passed,hard_pass,effective
def plan(native):
 q=native.read_current_authority()[0]['registered_future_requests'][native.REQUEST];p=q['host_execution_profiles'][ID];assert p['adapter_sha256']==sha(__file__)
 for row in p['source_pins']:assert sha(row['path'])==row['sha256'],('changed working-set host source',row['path'])
 return q,p
def largest(spec):
 key=spec['input_binding_sha256']
 if key not in BODY_CACHE:
  path=T/'control/input_bindings'/(spec['input_digest']+'.json');assert sha(path)==key;BODY_CACHE[key]=max((r['full_SHA_current_size_mtime'][0] for r in read(path)['qualification']['rows']),default=0)
 return BODY_CACHE[key]
def rss_for(row):
 p=T/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if not p.exists():return 0
 b=read(p);proc=P('/proc')/str(b['pid'])
 try:
  s=(proc/'stat').read_text().rsplit(')',1)[1].split()
  if int(s[19])!=b['start_ticks'] or s[0] in ['Z','X']:return 0
  return int(next(l.split()[1] for l in (proc/'status').read_text().splitlines() if l.startswith('VmRSS:')))*1024
 except (FileNotFoundError,ProcessLookupError,StopIteration):return 0
def install(native):
 q,profile=plan(native);original_spec=native.spec_for;original_resources=native.resources;original_exclusive=native.exclusive;original_child=native.child_info;os.sched_setaffinity(0,set(profile['control_CPUs']))
 def spec_for(cell):
  s=original_spec(cell)
  if cell in profile['preserved_prefix_cells']:return s
  claim=read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].get(cell)
  if claim is None:return s
  assert claim['host_cpu'] in profile['allowed_CPUs'];s=copy.deepcopy(s);s['host_cpu']=claim['host_cpu'];return s
 def resources(s,fresh_source=False):
  base=original_resources(s,fresh_source);q,_=plan(native);stat={a:int(b) for a,b in (l.split() for l in P('/sys/fs/cgroup/memory.stat').read_text().splitlines())};entries=[];legacy=[];claims=read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
  for cell,row in q['consumed'].items():
   if 'execution_receipt' in row:continue
   old=cell in profile['legacy_V1_cells'];spec=original_spec(cell);rss=rss_for(row);size=largest(spec);e=envelope(spec['limits']['max_process_tree_rss_bytes'],rss,size,old);entries.append({'cohort':cell,'legacy_V1':old,'hard_cap_bytes':spec['limits']['max_process_tree_rss_bytes'],'observed_model_RSS_bytes':rss,'largest_member_bytes':size,'working_set_envelope_bytes':e,'additional_reserved_bytes':max(0,e-rss)})
   if old:legacy.append(cell)
  pending=set(claims)-set(q['consumed'])
  if fresh_source and s['cohort'] not in q['consumed']:pending.add(s['cohort'])
  for cell in sorted(pending):
   spec=original_spec(cell);size=largest(spec);e=envelope(spec['limits']['max_process_tree_rss_bytes'],0,size,False);entries.append({'cohort':cell,'legacy_V1':False,'hard_cap_bytes':spec['limits']['max_process_tree_rss_bytes'],'observed_model_RSS_bytes':0,'largest_member_bytes':size,'working_set_envelope_bytes':e,'additional_reserved_bytes':e})
  projected=sum(r['additional_reserved_bytes'] for r in entries);c=credit(stat);hard=base['reserved_additional_live_and_candidate_RAM_bytes'];passed,oldpass,effective=ram_decision(base['host_MemAvailable_bytes'],base['cgroup_memory_max'],base['cgroup_memory_current'],c,projected,hard,fresh_source,bool(legacy))
  r=dict(base,host_execution_accounting=ID,physical_RAM_pass=passed,original_raw_cgroup_RAM_pass=base['physical_RAM_pass'],original_full_hard_cap_RAM_reservation_bytes=hard,reserved_additional_live_and_candidate_RAM_bytes=projected,cgroup_reclaimable_clean_inactive_file_credit_bytes=c,cgroup_effective_headroom_bytes=effective,cgroup_memory_stat_for_credit={k:stat.get(k,0) for k in ['file','inactive_file','shmem','file_mapped','file_dirty','file_writeback']},RAM_reservation_entries=entries,legacy_host_V1_live_cells=legacy,legacy_full_hard_cap_predicate_pass=oldpass,RAM_decision_scope='ADMISSION_PROJECTED_WORKINGSET' if fresh_source else 'RUNTIME_ACTUAL_HEADROOM',working_set_reservation_is_not_a_hard_cap=True)
  return r
 def exclusive(path,obj):
  path=P(path);cell=obj.get('cohort')
  if path.name.endswith('.INTENT.json') and cell not in profile['preserved_prefix_cells']:
   selected=spec_for(cell);original=original_spec(cell);obj=dict(obj,host_execution_binding={'profile':ID,'adapter_sha256':sha(__file__),'plan_sha256':profile['plan_sha256'],'original_host_cpu':original['host_cpu'],'actual_host_cpu':selected['host_cpu'],'original_spec_sha256':sha(T/'control'/(cell+'_SPEC.json')),'scientific_fields_changed':False,'outer_RAM_accounting_changed':True,'hard_cap_bytes':original['limits']['max_process_tree_rss_bytes'],'working_set_floor_bytes':4*G,'reservation_not_hard_cap':True,'unchanged_original_native_function_source_sha256':sha(T/'tools/sweep_native_cap1m.py')})
  if path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
   q,_=plan(native);uid=obj['scientific_qualification_uuid'] if path.name=='NATIVE_LAUNCH.json' else path.parent.name;cells=[c for c,r in q['consumed'].items() if r['uuid']==uid];assert len(cells)==1;i=read(T/'control/qualification_ledger'/(cells[0]+'.INTENT.json'))
   if 'host_execution_binding' in i:
    obj=dict(obj,host_execution_binding=i['host_execution_binding'])
    if path.name=='NATIVE_SIMULATOR_PID_AND_MAPS.json':assert obj['host_cpu_affinity_actual']==[i['host_execution_binding']['actual_host_cpu']]
  return original_exclusive(path,obj)
 def child_info(pid):
  r=original_child(pid);r['host_cpu_affinity_actual']=sorted(os.sched_getaffinity(pid));return r
 native.spec_for=spec_for;native.resources=resources;native.exclusive=exclusive;native.child_info=child_info;return native
