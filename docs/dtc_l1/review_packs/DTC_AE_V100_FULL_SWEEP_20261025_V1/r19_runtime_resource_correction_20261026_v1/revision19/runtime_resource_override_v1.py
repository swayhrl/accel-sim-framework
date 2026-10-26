"""R19 exact-generation main-thread resource lookup transition, not yet armed.
Retains run_native frame/process/log/UDS/BA/RSS/AS and all frozen sources.
Only effective RAM/disk booleans gain independently source-bound five-scope
accounting; old counters remain as preimages and corrected values are logged.
"""
import pathlib,json,hashlib,importlib.util,os,sys,threading,time,datetime,gzip
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';PROFILE='R19_EXACT_FIVE_SCOPE_RUNTIME_RESOURCE_ACCOUNTING_V1';FIELD='live_resource_accounting_correction_profile_R19';PLAN=F/'control/R19_LIVE_RESOURCE_OVERRIDE_PLAN_V1.json';ACKROOT=F/'control/live_resource_accounting_R19';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def require(v,why):
 if not v:raise RuntimeError(why)
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def generation(pid):
 s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return dict(pid=pid,start_ticks=int(s[19]),state=s[0],parent_pid=int(s[1]))
def identity(fn):return load('r19_exact_code_identity',T/'tools/sweep_live_ram_override_v1.py').code_identity(fn)
def authorized(authority,binding,plan_sha,source_sha,policy_sha):
 q=authority()[0]['registered_future_requests'][ORIG];p=q[FIELD];require(p['profile_id']==PROFILE and p['plan_sha256']==plan_sha and p['patch_source_sha256']==source_sha and p['policy_sha256']==policy_sha,'runtime correction authority mismatch');target=p['targets'][binding['cohort']];require(all(target[k]==binding[k]for k in ['uuid','frontend_pid','frontend_start_ticks','model_pid','model_start_ticks','launcher_pid','launcher_start_ticks']),'runtime correction target mismatch')
def make_wrapper(original,authority,binding,plan_sha,source_sha,resource_module,policy_sha):
 resource_sha=sha(resource_module.__file__)
 def resources(spec,fresh_source=False):
  base=original(spec,fresh_source)
  if fresh_source:return base
  try:
   authorized(authority,binding,plan_sha,source_sha,policy_sha);require(sha(resource_module.__file__)==resource_sha and sha(__file__)==source_sha,'installed resource/payload source changed');effective=resource_module.resources(spec,False);require(effective['schema']=='R19_FIVE_SCOPE_EXACT_FUTURE_WRITES_ACTUAL_RAM_V1' and effective['policy_sha256']==policy_sha and effective['resource_module_sha256']==resource_sha,'five-scope source/policy changed');require(effective['local_safety_floor_bytes']==5*G and effective['host_floor_bytes']==64*G and effective['cgroup_floor_bytes']==48*G,'resource floors changed')
   note=dict(schema=PROFILE,status='EFFECTIVE_ACCOUNTING_APPLIED',plan_sha256=plan_sha,patch_source_sha256=source_sha,policy_sha256=policy_sha,frontend_pid=binding['frontend_pid'],frontend_start_ticks=binding['frontend_start_ticks'],cohort=binding['cohort'],uuid=binding['uuid'],prior_physical_RAM_pass=base['physical_RAM_pass'],prior_physical_disk_pass=base['physical_disk_pass'],prior_required_free_bytes=base['required_free_bytes'],effective_resource_sample=effective,only_effective_resources_changed=True,BA_retirement_and_telemetry_and_hardlimits_unchanged=True)
   result=dict(base);result['physical_RAM_pass']=effective['physical_RAM_pass'];result['physical_disk_pass']=effective['physical_disk_pass'];result['live_resource_accounting_correction_R19']=note;return result
  except(OSError,ValueError,KeyError,RuntimeError)as e:
   # Missing evidence never relaxes a guard or tears down the observer.
   result=dict(base);result['live_resource_accounting_correction_R19']=dict(schema=PROFILE,status='NO_RELAXATION_INVALID_EVIDENCE',error=repr(e),plan_sha256=plan_sha);return result
 return resources
def apply(plan_path=PLAN):
 require(threading.current_thread()is threading.main_thread(),'pending callback must run on frontend main interpreter thread');plan=read(plan_path);ps=sha(plan_path);ss=sha(__file__);require(plan['profile_id']==PROFILE and plan['patch_source_sha256']==ss,'wrong exact patch plan');current=generation(os.getpid());targets=[dict(v,cohort=k)for k,v in plan['targets'].items()if(v['frontend_pid'],v['frontend_start_ticks'])==(current['pid'],current['start_ticks'])];require(len(targets)==1,'no unique current frontend target');binding=targets[0];cell=binding['cohort'];frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='run_native'and frame.f_globals.get('__file__')==plan['unchanged_native_source_path']and frame.f_locals.get('cohort')==cell:break
  frame=frame.f_back
 require(frame is not None,'exact native run frame absent');g=frame.f_globals;require(g.get('REQUEST')==ORIG and sha(g['__file__'])==plan['unchanged_native_source_sha256'],'wrong frozen native source/request');require(frame.f_locals['ident']==binding['uuid']and str(frame.f_locals['out'])==binding['output'],'native frame UUID/output mismatch');model=generation(binding['model_pid']);require(model['start_ticks']==binding['model_start_ticks']and model['state']not in ['Z','X'],'model generation gone');launcher=generation(binding['launcher_pid']);require(frame.f_locals['p'].pid==launcher['pid']and launcher['start_ticks']==binding['launcher_start_ticks']and launcher['state']not in ['Z','X'],'launcher generation/frame mismatch');observations=frame.f_locals['observations'];require(observations and(observations[0]['pid'],observations[0]['start_ticks'])==(model['pid'],model['start_ticks']),'observed model generation mismatch');authorized(g['read_current_authority'],binding,ps,ss,plan['policy_sha256']);ackpath=ACKROOT/(cell+'.'+binding['uuid']+'.ACK.json')
 if '_LIVE_RESOURCE_ACCOUNTING_STATE_R19'in g:
  saved=g['_LIVE_RESOURCE_ACCOUNTING_STATE_R19'];require(saved['plan_sha256']==ps and saved['patch_source_sha256']==ss and read(ackpath)==saved,'incompatible existing correction');return saved
 original=g['resources'];before=identity(original);require(before==binding['expected_resource_function_code_identity']and sha(before['filename'])==binding['resource_function_source_sha256'],'before function/source mismatch');require(not ackpath.exists(),'ACK collision');require(sha(plan['resource_module_path'])==plan['resource_module_sha256']and sha(plan['policy_path'])==plan['policy_sha256'],'new module/policy source changed');module=load('r19_qualified_runtime_five_scope_resources',P(plan['resource_module_path']));replacement=make_wrapper(original,g['read_current_authority'],binding,ps,ss,module,plan['policy_sha256']);ack=dict(schema=PROFILE,status='EXACT_RUNTIME_RESOURCE_LOOKUP_INSTALLED',cohort=cell,uuid=binding['uuid'],frontend_pid=current['pid'],frontend_start_ticks=current['start_ticks'],model_pid=model['pid'],model_start_ticks=model['start_ticks'],launcher_pid=launcher['pid'],launcher_start_ticks=launcher['start_ticks'],plan_sha256=ps,patch_source_sha256=ss,policy_sha256=plan['policy_sha256'],resource_module_sha256=plan['resource_module_sha256'],before_resource_function=before,after_resource_function=identity(replacement),observed_monotonic_ns=time.monotonic_ns(),observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_native_source_SHA_preserved=True,run_native_frame_and_local_process_and_streams_preserved=True,BA_hardlimits_telemetry_unchanged=True,model_signals=0,model_starts=0)
 ACKROOT.mkdir(parents=True,exist_ok=True);g['resources']=replacement
 try:
  with ackpath.open('x')as f:json.dump(ack,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 except BaseException:g['resources']=original;raise
 g['_LIVE_RESOURCE_ACCOUNTING_STATE_R19']=ack;return ack
def _gone(pid,ticks):
 try:b=generation(pid);return b['start_ticks']!=ticks or b['state']in ['Z','X']
 except(FileNotFoundError,ProcessLookupError):return True
def require_all_live_original_runtime_corrections(registry,plan_path=PLAN):
 """Read-only mandatory pre-transfer gate. Never fabricates activation proof."""
 plan=read(plan_path);ps=sha(plan_path);ss=sha(__file__);require(plan['profile_id']==PROFILE and plan['patch_source_sha256']==ss,'unqualified runtime plan');require(sha(plan['resource_module_path'])==plan['resource_module_sha256']and sha(plan['policy_path'])==plan['policy_sha256'],'runtime accounting dependency drift');q=registry['registered_future_requests'][ORIG];require(q['budget']==356 and len(q['consumed'])>=plan['observed_original_consumed_prefix_count'] and set(plan['targets'])<=set(q['consumed']),'original consumed prefix not compatible with runtime inventory');module=load('r19_gate_qualified_accounting',P(plan['resource_module_path']));_,ghost,_,_=module.policy_and_ghosts(registry)
 class Authority:
  def __call__(self):return registry,{}
 authority=Authority();expected_after=identity(make_wrapper(lambda *a:{},authority,{},ps,ss,module,plan['policy_sha256']));live=[];closed=[];departed=[]
 for c,row in q['consumed'].items():
  ip=T/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=T/'DTC/run/results'/row['uuid'];require(sha(ip)==row['intent_sha256']and intent['cohort']==c and intent['uuid']==row['uuid']and intent['output']==str(out),'native INTENT/row mismatch');pp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';lp=out/'NATIVE_LAUNCH.json';dp=ip.with_name(c+'.DONE.json')
  if 'execution_receipt'in row:
   require(dp.exists()and(out/'NATIVE_EXIT.json').exists()and read(dp)==read(out/'NATIVE_EXIT.json')==row['execution_receipt'],'closed q lacks real DONE/EXIT');require(read(dp)['uuid']==row['uuid'],'DONE generation mismatch');require(pp.exists()and _gone(read(pp)['pid'],read(pp)['start_ticks']),'DONE generation still live');closed.append(dict(cohort=c,uuid=row['uuid'],DONE_sha256=sha(dp)));continue
  if c in ghost and ghost[c]==row['uuid']:departed.append(dict(cohort=c,uuid=row['uuid'],status='CERTIFIED_DEPARTED_NO_RECEIPT_STILL_UNACCEPTED'));continue
  require(c in plan['targets']and pp.exists()and lp.exists(),'unknown live or missing identity not in qualified inventory');b=dict(plan['targets'][c],cohort=c);p=read(pp);l=read(lp);require(row['uuid']==b['uuid']and(p['pid'],p['start_ticks'],l['launcher_pid'])==(b['model_pid'],b['model_start_ticks'],b['launcher_pid']),'current receipt generation differs from plan')
  for kind in ['frontend','model','launcher']:
   state=generation(b[kind+'_pid']);require(state['start_ticks']==b[kind+'_start_ticks']and state['state']not in ['Z','X'],'runtime inventory generation gone without DONE')
  require(generation(b['launcher_pid'])['parent_pid']==b['frontend_pid'],'launcher no longer belongs to exact frontend');authorized(authority,b,ps,ss,plan['policy_sha256']);ackpath=ACKROOT/(c+'.'+row['uuid']+'.ACK.json');require(ackpath.exists(),'active generation missing correction ACK');a=read(ackpath);require(a['status']=='EXACT_RUNTIME_RESOURCE_LOOKUP_INSTALLED'and a['plan_sha256']==ps and a['patch_source_sha256']==ss and a['policy_sha256']==plan['policy_sha256']and a['resource_module_sha256']==plan['resource_module_sha256'],'ACK source/policy mismatch');require(all(a[k]==b[k]for k in ['uuid','frontend_pid','frontend_start_ticks','model_pid','model_start_ticks','launcher_pid','launcher_start_ticks']),'ACK generation mismatch');require(a['before_resource_function']==b['expected_resource_function_code_identity']and a['after_resource_function']==expected_after,'ACK code identity mismatch');matched=None
  try:
   with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt')as f:
    for line in f:
     try:r=json.loads(line)
     except ValueError:continue
     if 'physical_RAM_pass'not in r:continue
     matched=None;note=r.get('live_resource_accounting_correction_R19',{});e=note.get('effective_resource_sample',{})
     if note.get('status')=='EFFECTIVE_ACCOUNTING_APPLIED'and note.get('cohort')==c and note.get('uuid')==row['uuid']and note.get('plan_sha256')==ps and note.get('patch_source_sha256')==ss and note.get('policy_sha256')==plan['policy_sha256']and e.get('policy_sha256')==plan['policy_sha256']and e.get('resource_module_sha256')==plan['resource_module_sha256']and e.get('schema')=='R19_FIVE_SCOPE_EXACT_FUTURE_WRITES_ACTUAL_RAM_V1':
      require(note['frontend_pid']==b['frontend_pid']and note['frontend_start_ticks']==b['frontend_start_ticks'],'sample frontend mismatch');require(e['local_safety_floor_bytes']==5*G and e['host_floor_bytes']==64*G and e['cgroup_floor_bytes']==48*G,'sample safety floor changed');require(datetime.datetime.fromisoformat(e['utc'])>=datetime.datetime.fromisoformat(a['observed_utc']),'sample predates installed ACK');require(r['physical_RAM_pass']==e['physical_RAM_pass']and r['physical_disk_pass']==e['physical_disk_pass'],'effective booleans not actually used');matched=dict(sample_utc=e['utc'],RAM_pass=r['physical_RAM_pass'],disk_pass=r['physical_disk_pass'],required_free_bytes=e['required_free_bytes'],native_free_bytes=e['native_free_bytes'])
  except EOFError:pass # an actively flushed gzip member need not yet have a trailer
  require(matched is not None,'active generation has ACK but latest actual outer sample lacks post-ACK effective correction');age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(matched['sample_utc'])).total_seconds();require(0<=age<=40,'latest correction sample is not fresh');live.append(dict(cohort=c,uuid=row['uuid'],frontend_pid=b['frontend_pid'],model_pid=b['model_pid'],ACK_path=str(ackpath),ACK_sha256=sha(ackpath),sample=matched))
 return dict(schema='R19_ALL_LIVE_ORIGINAL_RUNTIME_ACCOUNTING_PRECONDITION_V1',status='ALL_CURRENT_LIVE_CORRECTIONS_OBSERVED_OR_REAL_DONE',plan_sha256=ps,payload_sha256=ss,resource_module_sha256=plan['resource_module_sha256'],policy_sha256=plan['policy_sha256'],observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checked_consumed=len(q['consumed']),live_count=len(live),live=live,real_closed_count=len(closed),real_closed=closed,certified_receiptless_departed_count=len(departed),certified_receiptless_departed=departed,scientific_starts=0,signals=0,authority_mutations=0)
