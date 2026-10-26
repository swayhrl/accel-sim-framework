"""Main-thread-only RAM predicate transition; no scientific model/telemetry edits."""
import pathlib,json,hashlib,os,sys,time,datetime,threading,types
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3;PROFILE='HOST_RUNTIME_ACTUAL_RAM_R12_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def generation(pid):
 s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return {'pid':pid,'start_ticks':int(s[19]),'state':s[0]}
def constant_shape(value):
 if isinstance(value,types.CodeType):return {'type':'code','value':code_shape(value)}
 if value is None:return {'type':'none'}
 if value is Ellipsis:return {'type':'ellipsis'}
 if isinstance(value,bool):return {'type':'bool','value':value}
 if isinstance(value,int):return {'type':'int','value':str(value)}
 if isinstance(value,float):return {'type':'float','value':value.hex()}
 if isinstance(value,complex):return {'type':'complex','real':value.real.hex(),'imag':value.imag.hex()}
 if isinstance(value,str):return {'type':'str','value':value}
 if isinstance(value,bytes):return {'type':'bytes','value':value.hex()}
 if isinstance(value,tuple):return {'type':'tuple','value':[constant_shape(v) for v in value]}
 if isinstance(value,frozenset):return {'type':'frozenset','value':sorted((constant_shape(v) for v in value),key=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')))}
 raise TypeError('Unsupported code constant:'+type(value).__name__)
def code_shape(code):
 return {'filename':code.co_filename,'name':code.co_name,'argcount':code.co_argcount,'posonlyargcount':code.co_posonlyargcount,'kwonlyargcount':code.co_kwonlyargcount,'nlocals':code.co_nlocals,'stacksize':code.co_stacksize,'flags':code.co_flags,'firstlineno':code.co_firstlineno,'code':code.co_code.hex(),'lnotab':code.co_lnotab.hex(),'exceptiontable':getattr(code,'co_exceptiontable',b'').hex(),'names':list(code.co_names),'varnames':list(code.co_varnames),'freevars':list(code.co_freevars),'cellvars':list(code.co_cellvars),'consts':[constant_shape(v) for v in code.co_consts]}
def code_fingerprint(code):return hashlib.sha256(json.dumps(code_shape(code),sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def code_identity(fn):return {'filename':fn.__code__.co_filename,'qualname':fn.__qualname__,'code_sha256':code_fingerprint(fn.__code__)}
def snapshot():
 began=time.monotonic_ns();mem=int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;c=P('/sys/fs/cgroup');maximum=(c/'memory.max').read_text().strip();current=int((c/'memory.current').read_text());stat={k:int(v) for k,v in (l.split() for l in (c/'memory.stat').read_text().splitlines())};fields={k:stat.get(k,0) for k in ['file','inactive_file','shmem','file_mapped','file_dirty','file_writeback']};clean=max(0,fields['file']-fields['shmem']-fields['file_mapped']-fields['file_dirty']-fields['file_writeback']);credit=max(0,min(fields['inactive_file'],clean)-8*G);effective=None if maximum=='max' else int(maximum)-current+credit
 return {'sample_begin_monotonic_ns':began,'sample_end_monotonic_ns':time.monotonic_ns(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frontend_pid':os.getpid(),'frontend_start_ticks':generation(os.getpid())['start_ticks'],'host_MemAvailable_bytes':mem,'cgroup_memory_max':maximum,'cgroup_memory_current':current,'cgroup_memory_stat_for_credit':fields,'cgroup_reclaimable_clean_inactive_file_credit_bytes':credit,'cgroup_effective_headroom_bytes':effective}
def decision(sample):
 eff=sample['cgroup_effective_headroom_bytes'];return sample['host_MemAvailable_bytes']>=64*G and (eff is None or eff>=48*G)
def make_wrapper(original,authority,binding,plan_sha,patch_sha,sampler=snapshot):
 def resources(spec,fresh_source=False):
  # Original dict/counters/disk and all native hard-cap/BA checks are retained.
  base=original(spec,fresh_source);reg=authority()[0];profile=reg['registered_future_requests']['DTC_AE_V100_FULL_SWEEP_20261025_V1']['live_RAM_guard_override_profile'];assert profile['profile_id']==PROFILE and profile['plan_sha256']==plan_sha and profile['patch_source_sha256']==patch_sha
  target=profile['targets'][binding['cohort']];assert all(target[k]==binding[k] for k in ['uuid','frontend_pid','frontend_start_ticks','model_pid','model_start_ticks'])
  actual=sampler();assert actual['frontend_pid']==binding['frontend_pid'] and actual['frontend_start_ticks']==binding['frontend_start_ticks'];passed=decision(actual)
  override={'schema':'LIVE_RAM_GUARD_OVERRIDE_V1','profile':PROFILE,'patch_source_sha256':patch_sha,'plan_sha256':plan_sha,'frontend_pid':binding['frontend_pid'],'frontend_start_ticks':binding['frontend_start_ticks'],'cohort':binding['cohort'],'uuid':binding['uuid'],'prior_physical_RAM_pass':base['physical_RAM_pass'],'override_resource_sample':actual,'effective_physical_RAM_pass':passed,'scope':'RUNTIME_ACTUAL_HEADROOM_ONLY'}
  result=dict(base);result['physical_RAM_pass']=passed;result['live_RAM_guard_override']=override;return result
 return resources
def exclusive(path,data):
 with P(path).open('x') as f:json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def apply():
 assert threading.current_thread() is threading.main_thread(),'Pending callback must run in main interpreter thread'
 planpath=T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json';plan=read(planpath);plan_sha=sha(planpath);patch_sha=sha(__file__);assert plan['profile_id']==PROFILE and plan['patch_source_sha256']==patch_sha
 current=generation(os.getpid());targets=[dict(v,cohort=k) for k,v in plan['targets'].items() if v['frontend_pid']==os.getpid() and v['frontend_start_ticks']==current['start_ticks']];assert len(targets)==1;binding=targets[0];cell=binding['cohort'];ackpath=T/'control/live_ram_override'/(cell+'.ACK.json')
 frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='run_native' and frame.f_globals.get('__file__')==str(T/'tools/sweep_native_cap1m.py') and frame.f_locals.get('cohort')==cell:break
  frame=frame.f_back
 assert frame is not None,'Exact native run frame absent;no resource mutation'
 assert frame.f_locals['ident']==binding['uuid'] and str(frame.f_locals['out'])==str(T/'DTC/run/results'/binding['uuid']);globals_=frame.f_globals;assert sha(globals_['__file__'])==plan['unchanged_native_source_sha256']
 model=generation(binding['model_pid']);assert model['start_ticks']==binding['model_start_ticks'] and model['state'] not in ['Z','X'];observations=frame.f_locals['observations'];assert observations and (observations[0]['pid'],observations[0]['start_ticks'])==(model['pid'],model['start_ticks'])
 if '_LIVE_RAM_OVERRIDE_STATE_R12' in globals_:
  saved=globals_['_LIVE_RAM_OVERRIDE_STATE_R12'];assert saved['plan_sha256']==plan_sha and saved['patch_source_sha256']==patch_sha and read(ackpath)==saved;return saved
 original=globals_['resources'];before=code_identity(original);assert before==binding['expected_resource_function_code_identity'] and before['filename']==binding['resource_function_source_path'] and sha(before['filename'])==binding['resource_function_source_sha256'] and not ackpath.exists();reg=globals_['read_current_authority']()[0];profile=reg['registered_future_requests'][plan['request']]['live_RAM_guard_override_profile'];assert profile['plan_sha256']==plan_sha and profile['patch_source_sha256']==patch_sha
 replacement=make_wrapper(original,globals_['read_current_authority'],binding,plan_sha,patch_sha);ack={'schema':'LIVE_RAM_OVERRIDE_ACK_V1','status':'LIVE_RAM_OVERRIDE_INSTALLED','cohort':cell,'uuid':binding['uuid'],'frontend_pid':current['pid'],'frontend_start_ticks':current['start_ticks'],'model_pid':model['pid'],'model_start_ticks':model['start_ticks'],'plan_sha256':plan_sha,'patch_source_sha256':patch_sha,'original_native_function_file_sha256':plan['unchanged_native_source_sha256'],'before_resource_function':before,'after_resource_function':code_identity(replacement),'patch_monotonic_ns':time.monotonic_ns(),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'only_global_resources_lookup_replaced':True,'signals_to_model':0,'telemetry_guard_changed':False,'hard_AS_RSS_cap_changed':False,'disk_guard_changed':False,'model_generation_preserved':True}
 globals_['resources']=replacement
 try:exclusive(ackpath,ack)
 except BaseException:globals_['resources']=original;raise
 globals_['_LIVE_RAM_OVERRIDE_STATE_R12']=ack;return ack
