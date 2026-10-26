"""Finite9 R19 metadata-only correction for a real pre-INTENT admission HOLD.
No scientific process, source, authority, budget, wait or archive mutation.
"""
import pathlib,json,hashlib,importlib.util,os,sys,threading,time,datetime,copy
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=F/'ops/zero_start_deferral_v1';PLAN=D/'PLAN.json';PUB=D/'PUBLICATION_READBACK.json';ACK=D/'ACTUAL_MAIN_THREAD_ACK.json';CONT=F/'ops/revision19/sweep_controller.py';EXPECTED='c4cc1f48e404f949afb5bfe942044031bfc6650fe6f4032b97757b370f82f532'
SIGNATURE=json.dumps(dict(status='HOLD',reason='DTC original memory/paired/native-device admission HOLD',error_type='RuntimeError',model_retry=False))
STATES={'RESOLVING_ISSUE_NO_MODEL_RETRY','REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,why):
 if not v:raise RuntimeError(why)
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def is_exact_hold(value):return isinstance(value,dict)and value.get('state')in STATES and SIGNATURE in value.get('error','')
def unspent(c,item,reg):
 q=reg['registered_future_requests'][item['request']];root=P(item['root']);need(c in q['admitted_specs']and q['admitted_specs'][c]==item['spec_sha256'],'not the exact finite admitted spec');need(c not in q['consumed']and c not in q.get('sealed',[]),'consumed/sealed point cannot be deferred');need(not(root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(root/'control/qualification_ledger'/(c+'.DONE.json')).exists(),'INTENT or DONE exists; never retry/refund')
def make_wrapper(original,points,authority):
 def safe_call(fn,c):
  result=original(fn,c)
  if c not in points or not is_exact_hold(result)or result.get('cohort')!=c or result.get('error')!=points[c]['exact_error']:return result
  try:unspent(c,points[c],authority()[0])
  except(OSError,KeyError,ValueError,RuntimeError):return result
  return dict(state='ADMISSION_DEFERRED_ZERO_START',cohort=c,error=result['error'],model_starts=0,consumed_attempts=0,reason='EXACT_PAIRED_ADMISSION_HOLD_BEFORE_INTENT',operational_deferral_source_sha256=sha(__file__),scientific_guard_unchanged=True)
 return safe_call
def state_transition(g,local,plan,authority,backup_root):
 points=plan['points'];blocked=local['blocked'];results=local['results'];running=local['running'];cooldown=local['cooldown'];need(not any(m['cell']in points for m in running.values()),'target is already an active future');oldg=g['safe_call'];b0=copy.deepcopy(blocked);r0=copy.deepcopy(results);c0=copy.deepcopy(cooldown)
 for c,item in points.items():
  unspent(c,item,authority()[0]);root=P(item['root']);need(c in blocked[item['request']]and c in results[item['request']],'target is not the exact blocked completed metadata row');path=root/'analysis'/(c+'.RESULT.json');need(sha(path)==item['RESULT_sha256']and is_exact_hold(read(path))and read(path)['error']==item['exact_error']and results[item['request']][c]==read(path),'wrong historical pre-INTENT error');need(c not in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'],'target claim still active');need(sha(backup_root/(c+'.RESULT.json'))==item['RESULT_sha256'],'audit preimage missing or drifted');need(not(root/'analysis/zero_start_preimages_R19'/(c+'.RESULT.json')).exists(),'parent preimage target collision')
 try:
  g['safe_call']=make_wrapper(oldg,points,authority)
  for c,item in points.items():blocked[item['request']].remove(c);results[item['request']].pop(c);cooldown[c]=time.monotonic()+10
  for req in blocked:need(blocked[req]==b0[req]-{c for c,x in points.items()if x['request']==req},'unrelated block changed')
  return dict(cleared_cohorts=sorted(points),preserved_preimages=[dict(path=str(backup_root/(c+'.RESULT.json')),sha256=item['RESULT_sha256'])for c,item in points.items()],old_safe_call_source=oldg.__code__.co_filename,new_safe_call_source=g['safe_call'].__code__.co_filename,before_blocked={k:sorted(v)for k,v in b0.items()},after_blocked={k:sorted(v)for k,v in blocked.items()},no_non_target_metadata_changed=True,active_RESULT_files_unchanged_by_callback=True)
 except BaseException:
  g['safe_call']=oldg;blocked.clear();blocked.update(b0);results.clear();results.update(r0);cooldown.clear();cooldown.update(c0)
  raise
def write_ack(path,ack,created):
 with path.open('x')as f:created[0]=True;json.dump(ack,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def transition_and_ack(g,local,plan,authority,backup,path,base,writer=write_ack):
 need(not path.exists(),'ACK already exists');oldg=g['safe_call'];snap={k:copy.deepcopy(local[k])for k in['blocked','results','cooldown']};created=[False]
 try:
  transition=state_transition(g,local,plan,authority,backup);ack=dict(base,transition=transition);writer(path,ack,created);return ack
 except BaseException:
  g['safe_call']=oldg
  for k,v in snap.items():local[k].clear();local[k].update(v)
  if created[0]:path.unlink()
  raise
def apply():
 need(threading.current_thread()is threading.main_thread(),'must execute on metadata parent main thread');plan=read(PLAN);pub=read(PUB);qual=read(D/'CPU_QUALIFICATION.json');need(pub['verified']and pub['adapter_sha256']==sha(__file__)and pub['plan_sha256']==sha(PLAN)and pub['qualification_sha256']==sha(D/'CPU_QUALIFICATION.json'),'publication gate');need(qual['status']=='PASS'and qual['adapter_sha256']==sha(__file__)and qual['plan_sha256']==sha(PLAN),'CPU/source/plan gate');need(plan['parent_path']==str(CONT)and plan['parent_sha256']==sha(CONT)==EXPECTED,'frozen parent source changed');need(os.getpid()==plan['parent_pid'],'wrong parent PID');st=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();need(int(st[19])==plan['parent_start_ticks'],'wrong parent generation');frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='main'and frame.f_globals.get('__file__')==str(CONT):break
  frame=frame.f_back
 need(frame is not None,'exact actual parent main frame absent');g=frame.f_globals;local=frame.f_locals;need(g['sha'](g['__file__'])==EXPECTED,'executing parent source drift');reg,epoch=local['n'].read_current_authority();lease=read(T/'control/BATCH_LEASE.json');need((lease['pid'],lease['start_ticks'],lease['controller_sha256'])==(os.getpid(),plan['parent_start_ticks'],EXPECTED),'not actual sole lease');need(g['safe_call'].__code__.co_filename==str(CONT)and g['safe_call'].__code__.co_name=='safe_call','prior callback not the qualified original');need(not ACK.exists()and not g.get('_FINITE9_ZERO_START_DEFERRAL_STATE'),'already applied; no duplicate callback');backup=D/'preserved_zero_start_preimages';backup.mkdir(exist_ok=True)
 base=dict(status='ACTUAL_R19_MAIN_THREAD_FINITE9_DEFERRAL_INSTALLED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),start_ticks=plan['parent_start_ticks'],parent_source_sha256=EXPECTED,adapter_sha256=sha(__file__),plan_sha256=sha(PLAN),qualification_sha256=sha(D/'CPU_QUALIFICATION.json'),publication_commit=pub['commit'],authority_or_ledger_mutations=0,scientific_model_starts_by_callback=0,scientific_model_attaches_or_signals=0,scientific_guards_unchanged=True)
 ack=transition_and_ack(g,local,plan,local['n'].read_current_authority,backup,ACK,base)
 g['_FINITE9_ZERO_START_DEFERRAL_STATE']=ack;return ack
