"""Independent verification of explicitly published runtime-only RAM overrides.

Never attaches, patches, signals, launches or changes any scientific process.
Historical verifier inputs are transformed only in private in-memory stream views.
"""
import pathlib,json,hashlib,gzip,importlib.util,types
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
PROFILE='HOST_RUNTIME_ACTUAL_RAM_R12_V1';SCHEMA='LIVE_RAM_GUARD_OVERRIDE_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def constant_view(value):
 if isinstance(value,types.CodeType):return {'type':'code','value':code_view(value)}
 if value is None:return {'type':'none'}
 if value is Ellipsis:return {'type':'ellipsis'}
 if isinstance(value,bool):return {'type':'bool','value':value}
 if isinstance(value,int):return {'type':'int','value':str(value)}
 if isinstance(value,float):return {'type':'float','value':value.hex()}
 if isinstance(value,complex):return {'type':'complex','real':value.real.hex(),'imag':value.imag.hex()}
 if isinstance(value,str):return {'type':'str','value':value}
 if isinstance(value,bytes):return {'type':'bytes','value':value.hex()}
 if isinstance(value,tuple):return {'type':'tuple','value':[constant_view(v) for v in value]}
 if isinstance(value,frozenset):
  items=[constant_view(v) for v in value];items.sort(key=lambda item:json.dumps(item,sort_keys=True,separators=(',',':')));return {'type':'frozenset','value':items}
 raise TypeError('Unsupported independent code constant: '+type(value).__name__)
def code_view(code):
 out={key:getattr(code,'co_'+key) for key in ['filename','name','argcount','posonlyargcount','kwonlyargcount','nlocals','stacksize','flags','firstlineno']}
 for key in ['code','lnotab','exceptiontable']:out[key]=getattr(code,'co_'+key,b'').hex()
 for key in ['names','varnames','freevars','cellvars']:out[key]=list(getattr(code,'co_'+key))
 out['consts']=[constant_view(v) for v in code.co_consts];return out
def stable_code_sha(code):return hashlib.sha256(json.dumps(code_view(code),sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def nested_resource_code_sha(path):
 code=compile(P(path).read_bytes(),str(path),'exec');found=[]
 def walk(c):
  for item in c.co_consts:
   if isinstance(item,types.CodeType):
    if item.co_name=='resources':found.append(item)
    walk(item)
 walk(code);assert len(found)==1,(str(path),len(found));return stable_code_sha(found[0])
def verify_ack(ack,expected,certificate):
 assert ack['schema']=='LIVE_RAM_OVERRIDE_ACK_V1' and ack['status']=='LIVE_RAM_OVERRIDE_INSTALLED'
 for key in ['cohort','uuid','frontend_pid','frontend_start_ticks','model_pid','model_start_ticks']:assert ack[key]==expected[key]
 assert ack['plan_sha256']==certificate['plan_sha256'] and ack['patch_source_sha256']==certificate['patch_source_sha256']
 assert ack['original_native_function_file_sha256']==certificate['unchanged_native_source_sha256']==sha(T/'tools/sweep_native_cap1m.py')
 before=ack['before_resource_function'];after=ack['after_resource_function'];path=P(expected['resource_function_source_path']);assert sha(path)==expected['resource_function_source_sha256']
 assert before=={'filename':str(path),'qualname':'install.<locals>.resources','code_sha256':nested_resource_code_sha(path)}
 assert before==expected['expected_resource_function_code_identity']
 patch=P(certificate['patch_source_path']);assert sha(patch)==certificate['patch_source_sha256']
 assert after=={'filename':str(patch),'qualname':'make_wrapper.<locals>.resources','code_sha256':nested_resource_code_sha(patch)}
 assert ack['only_global_resources_lookup_replaced'] and ack['signals_to_model']==0 and not ack['telemetry_guard_changed'] and not ack['hard_AS_RSS_cap_changed'] and not ack['disk_guard_changed'] and ack['model_generation_preserved']
 assert type(ack['patch_monotonic_ns']) is int and ack['patch_monotonic_ns']>0
 return {'ACK_source_code_and_exact_generations_replayed':True,'patch_monotonic_ns':ack['patch_monotonic_ns'],'prior_resources_code_sha256':before['code_sha256'],'replacement_resources_code_sha256':after['code_sha256']}
def bind(q):
 pp=T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json';plan=read(pp);patch=T/'tools/sweep_live_ram_override_v1.py';pub=read(T/'control/CONTINUATION_R12_PUBLICATION_READBACK.json');qp=T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json';qual=read(qp)
 assert plan['profile_id']==PROFILE and plan['request']=='DTC_AE_V100_FULL_SWEEP_20261025_V1' and plan['patch_source_sha256']==sha(patch) and plan['unchanged_native_source_sha256']==sha(T/'tools/sweep_native_cap1m.py')
 assert pub['verified'] and qual['status']=='PASS' and pub['qualification_sha256']==sha(qp) and qual['live_override_plan_sha256']==sha(pp) and qual['patch_source_sha256']==sha(patch) and qual['controller_sha256']==pub['controller_sha256']==sha(T/'tools/revision12/sweep_controller.py')
 assert q['live_RAM_guard_override_profile']==dict(plan,plan_sha256=sha(pp),qualification_sha256=sha(qp),publication_commit=pub['commit'])
 assert plan['maximum_model_jobs']==40 and plan['initial_future_RAM_reservation_bytes']==4*G and plan['hard_process_AS_RSS_cap_bytes']==16*G and plan['actual_runtime_host_reserve_bytes']==64*G and plan['actual_runtime_cgroup_effective_reserve_bytes']==48*G and plan['only_old_field_changed']=='physical_RAM_pass' and plan['new_metadata_field']=='live_RAM_guard_override' and plan['telemetry_raw_capture_BA_policy_hard_caps_unchanged'] and plan['disk_guard_unchanged'] and plan['no_model_restart_or_retry']
 certificate={'patch_source_path':str(patch),'patch_source_sha256':sha(patch),'plan_sha256':sha(pp),'unchanged_native_source_sha256':plan['unchanged_native_source_sha256'],'publication_commit':pub['commit']}
 extension=read(T/'control/CONTINUATION_R12B_PUBLICATION_READBACK.json');eqp=T/'control/CONTINUATION_R12B_ZERO_MODEL_QUALIFICATION.json';extra=read(eqp);assert extension['verified'] and extra['status']=='PASS' and extension['qualification_sha256']==sha(eqp) and extension['controller_sha256']==extra['controller_sha256']==sha(T/'tools/revision12b/sweep_controller.py')
 bp=T/'control/LIVE_RAM_OVERRIDE_ACTIVATION_BARRIER_R12B.json';barrier=read(bp);assert barrier['status']=='ALL_LIVE_TARGET_RAM_OVERRIDES_OBSERVED_OR_ORIGINAL_CLOSED_DONE' and barrier['closed_target_extension_publication_commit']==extension['commit'] and barrier['plan_sha256']==sha(pp) and barrier['patch_source_sha256']==sha(patch) and barrier['target_count']==len(plan['targets']) and set(barrier['rows'])==set(plan['targets']) and barrier['model_processes_attached']==barrier['model_restarts']==barrier['model_signals']==0
 contexts={};counts={}
 for cell,target in plan['targets'].items():
  ctx=dict(target,cohort=cell);row=barrier['rows'][cell];assert row['cohort']==cell and row['uuid']==target['uuid']==q['consumed'][cell]['uuid'];ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);assert sha(ip)==q['consumed'][cell]['intent_sha256'] and intent['uuid']==target['uuid'];out=T/'DTC/run/results'/target['uuid'];pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert (pid['pid'],pid['start_ticks'])==(target['model_pid'],target['model_start_ticks']) and intent['host_execution_binding']['profile']==target['original_host_profile']
  ap=T/'control/live_ram_override'/(cell+'.ACK.json');ctx['ACK_present']=ap.exists()
  if ap.exists():
   ack=read(ap);proof=verify_ack(ack,ctx,certificate);ctx['patch_monotonic_ns']=proof['patch_monotonic_ns'];ctx['ACK_sha256']=sha(ap)
  state=row['state'];counts[state]=counts.get(state,0)+1
  if state=='OVERRIDE_RESOURCE_SAMPLE_OBSERVED':
   assert ctx['ACK_present'] and row['ack_path']==str(ap) and row['ack_sha256']==sha(ap) and (row['model_pid'],row['model_start_ticks'])==(target['model_pid'],target['model_start_ticks']);sp=T/'control/live_ram_override'/(cell+'.FIRST_OVERRIDE_SAMPLE.json');assert row['sample_proof_path']==str(sp) and row['sample_proof_sha256']==sha(sp);first=read(sp);verify_override_sample(first,ctx,certificate);ctx['first_sample_proof']=first;ctx['require_override']=True
  else:
   assert state in ['ORIGINAL_NATURAL_DONE','ORIGINAL_CLASSIFIED_UNACCEPTED_DONE'];dp=T/'control/qualification_ledger'/(cell+'.DONE.json');assert row['done_path']==str(dp) and row['done_sha256']==sha(dp);done=read(dp);assert done['uuid']==target['uuid'] and done==read(out/'NATIVE_EXIT.json')
   if state=='ORIGINAL_NATURAL_DONE':assert done['stop_reason'] is None and done['launcher_wait_returncode']==0
   else:
    cp=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json');assert row['classification_path']==str(cp) and row['classification_sha256']==sha(cp);spec=importlib.util.spec_from_file_location('R12B_independent_closed_target_assert_replay_'+cell,T/'tools/sweep_failure_review_runtime_assert_v1.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);classification=module.classify(cell);assert classification==read(cp) and classification['accepted_cycles'] is None and classification['scientific_acceptance'] is False and classification['cohort']==cell and classification['uuid']==target['uuid']
   ctx['require_override']=False
  contexts[cell]=ctx
 assert counts.get('OVERRIDE_RESOURCE_SAMPLE_OBSERVED',0)==barrier['actual_live_runtime_overrides_observed'] and counts.get('ORIGINAL_NATURAL_DONE',0)==barrier['original_natural_done_targets']
 assert counts.get('ORIGINAL_CLASSIFIED_UNACCEPTED_DONE',0)==barrier['original_closed_unaccepted_targets']
 return {'certificate':certificate,'targets':contexts,'barrier_sha256':sha(bp),'barrier_counts':counts}
def verify_override_sample(row,expected,certificate):
 m=row['live_RAM_guard_override'];assert m['schema']==SCHEMA and m['profile']==PROFILE and m['scope']=='RUNTIME_ACTUAL_HEADROOM_ONLY'
 assert m['patch_source_sha256']==certificate['patch_source_sha256'] and m['plan_sha256']==certificate['plan_sha256']
 assert m['cohort']==expected['cohort'] and m['uuid']==expected['uuid'] and (m['frontend_pid'],m['frontend_start_ticks'])==(expected['frontend_pid'],expected['frontend_start_ticks'])
 assert type(m['prior_physical_RAM_pass']) is bool and type(m['effective_physical_RAM_pass']) is bool and type(row['physical_RAM_pass']) is bool
 s=m['override_resource_sample'];stat=s['cgroup_memory_stat_for_credit']
 assert (s['frontend_pid'],s['frontend_start_ticks'])==(expected['frontend_pid'],expected['frontend_start_ticks'])
 assert type(s['sample_begin_monotonic_ns']) is int and type(s['sample_end_monotonic_ns']) is int and s['sample_end_monotonic_ns']>=s['sample_begin_monotonic_ns']>0
 if 'patch_monotonic_ns' in expected:assert s['sample_begin_monotonic_ns']>=expected['patch_monotonic_ns']
 for key in ['file','inactive_file','shmem','file_mapped','file_dirty','file_writeback']:assert type(stat[key]) is int and stat[key]>=0
 clean=max(0,stat['file']-stat['shmem']-stat['file_mapped']-stat['file_dirty']-stat['file_writeback']);credit=max(0,min(stat['inactive_file'],clean)-8*G)
 assert credit==s['cgroup_reclaimable_clean_inactive_file_credit_bytes']
 mem=s['host_MemAvailable_bytes'];cur=s['cgroup_memory_current'];maximum=s['cgroup_memory_max'];assert type(mem) is int and mem>=0 and type(cur) is int and cur>=0
 assert maximum=='max' or int(maximum)>=0
 effective=None if maximum=='max' else int(maximum)-cur+credit
 assert effective==s['cgroup_effective_headroom_bytes']
 passed=mem>=64*G and (effective is None or effective>=48*G)
 assert passed==m['effective_physical_RAM_pass']==row['physical_RAM_pass'],'fresh actual RAM override verdict not independently reproduced'
 return {'prior_physical_RAM_pass':m['prior_physical_RAM_pass'],'effective_physical_RAM_pass':passed,'cache_credit_bytes':credit,'effective_headroom_bytes':effective,'prior_and_actual_may_differ':m['prior_physical_RAM_pass']!=passed}
class HistoricalResourceStream:
 def __init__(self,stream,expected,certificate,proofs):self.stream=stream;self.expected=expected;self.certificate=certificate;self.proofs=proofs;self.last_override_ns=0
 def __enter__(self):self.stream.__enter__();return self
 def __exit__(self,*args):return self.stream.__exit__(*args)
 def __iter__(self):return self
 def __next__(self):
  line=next(self.stream);row=json.loads(line)
  if 'live_RAM_guard_override' not in row:
   assert not ('physical_RAM_pass' in row and self.last_override_ns),'override disappeared after activation in target stream'
   return line
  proof=verify_override_sample(row,self.expected,self.certificate);proof['matches_first_barrier_sample']=row==self.expected.get('first_sample_proof');mono=row['live_RAM_guard_override']['override_resource_sample']['sample_begin_monotonic_ns'];assert mono>self.last_override_ns;self.last_override_ns=mono;self.proofs.append(proof);view=dict(row,physical_RAM_pass=proof['prior_physical_RAM_pass']);text=json.dumps(view)+'\n';return text.encode() if isinstance(line,bytes) else text
 def __getattr__(self,key):return getattr(self.stream,key)
class PrivateGzipProxy:
 def __init__(self,real,output,expected,certificate,proofs):self.real=real;self.output=P(output);self.expected=expected;self.certificate=certificate;self.proofs=proofs
 def open(self,path,*args,**kwargs):
  stream=self.real.open(path,*args,**kwargs)
  if P(path)==self.output/'RESOURCE_SAMPLES.jsonl.gz':return HistoricalResourceStream(stream,self.expected,self.certificate,self.proofs)
  return stream
 def __getattr__(self,key):return getattr(self.real,key)
def historical_modules(root,binding):
 yield root
 while 'old_module' in binding:
  yield binding['old_module'];binding=binding['old_binding']
def replay_preserved_host(cell,native,expected,certificate,require_override=True):
 spec=importlib.util.spec_from_file_location('R12_private_preserved_host_'+cell,T/'tools/sweep_host_provenance_v3.py');root=importlib.util.module_from_spec(spec);spec.loader.exec_module(root)
 q=native.read_current_authority()[0]['registered_future_requests'][native.REQUEST];binding=root.bind(q);output=T/'DTC/run/results'/q['consumed'][cell]['uuid'];proofs=[];changed=[];global_open=gzip.open
 try:
  for module in historical_modules(root,binding):
   if hasattr(module,'gzip'):
    original=module.gzip;assert original is gzip;module.gzip=PrivateGzipProxy(original,output,expected,certificate,proofs);changed.append((module,original))
  result=root.verify(cell,binding,native)
 finally:
  for module,original in reversed(changed):module.gzip=original
  assert gzip.open is global_open,'global gzip implementation was mutated'
 assert proofs or not require_override,'published patched point has no independently verified override resource sample'
 if require_override:assert any(p['matches_first_barrier_sample'] for p in proofs),'barrier sample not present in actual point resource stream'
 return dict(result,live_RAM_guard_override={'profile':PROFILE,'schema':SCHEMA,'sample_count':len(proofs),'prior_negative_actual_positive_samples':sum(not p['prior_physical_RAM_pass'] and p['effective_physical_RAM_pass'] for p in proofs),'all_prior_arithmetic_and_actual_override_arithmetic_replayed':True,'patch_source_sha256':certificate['patch_source_sha256'],'plan_sha256':certificate['plan_sha256'],'producer_and_archived_resource_bytes_unchanged':True,'global_gzip_module_unchanged':True})
def verify_preserved(cell,native,binding,old_module,old_binding):
 if cell in binding['targets'] and binding['targets'][cell]['ACK_present']:
  ctx=binding['targets'][cell];result=replay_preserved_host(cell,native,ctx,binding['certificate'],ctx['require_override']);result['live_RAM_guard_override']['activation_barrier_sha256']=binding['barrier_sha256'];result['live_RAM_guard_override']['ACK_sha256']=ctx['ACK_sha256'];return result
 q=native.read_current_authority()[0]['registered_future_requests'][native.REQUEST]
 with gzip.open(T/'DTC/run/results'/q['consumed'][cell]['uuid']/'RESOURCE_SAMPLES.jsonl.gz','rt') as stream:
  for line in stream:assert 'live_RAM_guard_override' not in json.loads(line),'unregistered override sample on an unpatched point'
 return old_module.verify(cell,old_binding,native)
