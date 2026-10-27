"""Existing-owner instance installation candidate. No action on import."""
import pathlib,json,hashlib,importlib.util,threading,sys,os,copy,subprocess,uuid,time
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';MARKER='DTC_L2_MLP_PADDING_ONLY_OWNER_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def install_on_frame(frame,config_path,fixture=False):
 assert threading.current_thread()is threading.main_thread();core=load('padding_owner_core',P(__file__).with_name('padding_overlay.py'));cfg=read(config_path);assert cfg['owner_sha256']==sha(__file__);engine=frame.f_locals['engine'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer'];q=engine.registered()[2];record=core.validate_active_config(cfg,q);main=sys.modules['__main__'];assert not hasattr(main,MARKER);original_resources=res.resources;original_choose=res.choose_dispatch;original_worker=frame.f_globals['worker'];original_consumer_load=consumer.load;reference=next(iter(q['consumed']));reference_spec=engine.canonical(reference);local=threading.local();overlay=core.PaddingOverlay(R,cfg['policy_path'],cfg['certificate_path'],cfg['policy_sha256'],cfg['certificate_sha256'],lambda:engine.registered()[2],original_resources)
 def resource(s,fresh_source=False):
  if fresh_source and getattr(local,'padding',False):
   cached=getattr(local,'cached',None)
   if cached is not None and s['cohort']==reference:return cached
   return overlay.resources(s,True)
  return original_resources(s,fresh_source)
 def choose(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  try:active=read(config_path);core.validate_active_config(active,engine.registered()[2])
  except(OSError,ValueError,AssertionError,KeyError)as error:
   state=getattr(main,MARKER,{});state['activation_hold']=dict(monotonic=time.monotonic(),reason=repr(error));return None
  scoped=[s for s in pending if s['cohort']in active['allowed_cohorts']];outside=[s for s in pending if s['cohort']not in active['allowed_cohorts']]
  if scoped:
   local.padding=True
   try:
    exact=overlay.resources(reference_spec,True);local.cached=exact;view=overlay.claims_view(claims,exact['additional_padding_admission_proof']);decision=original_choose(scoped,sample,view,history,previous,policy,dispatch_index)
    if decision is not None:return dict(decision,padding_only_owner_proof=exact['additional_padding_admission_proof'])
   finally:local.cached=None;local.padding=False
  return original_choose(outside,sample,claims,history,previous,policy,dispatch_index)if outside else None
 def worker(c):
  try:active=read(config_path);core.validate_active_config(active,engine.registered()[2])
  except(OSError,ValueError,AssertionError,KeyError)as error:return dict(state='ZERO_START_DEFERRED',cohort=c,error='PADDING_ACTIVATION_HOLD '+repr(error),model_starts=0)
  if c not in active['allowed_cohorts']:return original_worker(c)
  core.validate_active_config(active,engine.registered()[2]);e=frame.f_globals['load']('padding_worker_engine','l2_native.py');e.assert_parent_lease();ip=R/'control/qualification_ledger'/(c+'.INTENT.json');assert not ip.exists();token=uuid.uuid4().hex;put=frame.f_globals['put'];N=frame.f_globals['N']
  for stage in['prepare','run-native']:
   command=[str(N/'bin/experiment'),stage,c,'--project','DTC_L1','--padding-only-admission-v1'];r=subprocess.run(command,capture_output=True,text=True);put(R/'logs'/(c+'.'+stage+'.'+token+'.json'),dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,additional_cli_flag='--padding-only-admission-v1'),True)
   if r.returncode:
    if not ip.exists()and c not in e.registered()[2]['consumed']:return dict(state='ZERO_START_DEFERRED'if'RESOURCE_HOLD'in r.stderr else'ZERO_START_ENGINEERING',cohort=c,error=r.stderr,model_starts=0)
    return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,error=r.stderr,model_retries=0)
  return dict(state='EXECUTION_CLOSED',cohort=c)
 def consumer_load(n,f):
  module=original_consumer_load(n,f)
  if f=='l2_strict.py':
   old=module.terminal
   def terminal(c):
    proof=old(c);intent=read(R/'control/qualification_ledger'/(c+'.INTENT.json'))
    if'additional_padding_admission_binding'not in intent:return proof
    validator=load('padding_closed_extra_strict',P(cfg['extra_strict_path']));extra=validator.terminal(c,cfg,proof);return dict(proof,additional_padding_admission_strict=extra)
   module.terminal=terminal
  return module
 res.resources=resource;res.choose_dispatch=choose;frame.f_globals['worker']=worker;consumer.load=consumer_load;saved=dict(resource=original_resources,choose=original_choose,worker=original_worker,consumer_load=original_consumer_load,res=res,consumer=consumer,globals=frame.f_globals,overlay=overlay,config_path=str(config_path));setattr(main,MARKER,saved)
 return dict(status='PADDING_ONLY_INSTANCE_WRAPPERS_INSTALLED',owner_pid=os.getpid(),pool_object_id=id(frame.f_locals['pool']),worker_capacity=frame.f_locals['max_workers'],claims_object_id=id(frame.f_locals['claims']),allowed_cohorts=cfg['allowed_cohorts'],source_sha256=sha(P(__file__).with_name('padding_overlay.py')),original_worker_filename=original_worker.__code__.co_filename,all_running_worker_frames_unchanged=True,no_signals=True,no_registered_spec_mutation=True)
def apply_in_owner(config_path):
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks'];thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;return install_on_frame(frame,config_path)
def restore_in_owner():
 assert threading.current_thread()is threading.main_thread();saved=getattr(sys.modules['__main__'],MARKER);saved['res'].resources=saved['resource'];saved['res'].choose_dispatch=saved['choose'];saved['globals']['worker']=saved['worker']
 # Keep consumer additional strict active until every overlay identity closes.
 return dict(status='RESTORED_DISPATCH_RESOURCES_WORKER_ONLY',additional_strict_consumer_retained=True,existing_jobs_untouched=True)
