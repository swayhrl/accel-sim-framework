"""IR11 only: real independent-FD flock test, fake authority, no models."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,copy,tempfile,types,threading,fcntl,errno,os,time,importlib.util
P=pathlib.Path;D=P(__file__).parent;A=D.parents[2];R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');checks=[]
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve())
sys.addaudithook(guard)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);s.loader.exec_module if False else None;return m
M=load('IR11_frozen_registry',D/'incident_registry.py')
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(M.js(v))
def ck(n,v):assert v,n;checks.append(n)
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected HOLD')
planpath=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';plan=read(planpath);base=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');metrics=[]
def fixture(fault=None):
 root=P(tempfile.mkdtemp(prefix='CPU_IR11_',dir=D));reg=copy.deepcopy(base);reg['registered_future_requests'][M.REQ]['qualification_only']=True;active=[False];forbidden=[0];grants=[0];blocked_probe=[0];EXdurations=[]
 for name in ['SCOPE.json','MATRIX_CURRENT.json']:(root/'control').mkdir(exist_ok=True);(root/'control'/name).write_bytes((R/'control'/name).read_bytes())
 for r in plan['rows']:
  c=r['original_cohort'];src={P(x['path']).name:x['path']for x in r['original_sources']}
  for source,dest in [('ORIGINAL_CANONICAL_SPEC.json',root/'control/specs'/(c+'.json')),('ORIGINAL_NEGATIVE_RESULT.json',root/'analysis'/(c+'.RESULT.json')),('ORIGINAL_DONE.json',root/'control/qualification_ledger'/(c+'.DONE.json'))]:
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(P(src[source]).read_bytes())
 e=load('IR11_private_native_'+root.name,R/'tools/l2_native.py');e.R=root;ep=dict(parent_pid=os.getpid(),parent_start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]))
 def not_inside():
  if active[0]:forbidden[0]+=1;raise RuntimeError('ENGINE_AUTHORITY_CALL_INSIDE_EX_CALLBACK')
 def registered():not_inside();return reg,{'qualification_only':True},reg['registered_future_requests'][M.REQ],ep
 def canonical(c):not_inside();return read(root/'control/specs'/(c+'.json'))
 def authority():not_inside();return reg,{'qualification_only':True}
 e.registered=registered;e.canonical=canonical;e.authority=authority;e.assert_parent_lease=lambda:(not_inside()or ep)
 def update(fn):
  nonlocal reg
  not_inside();target=copy.deepcopy(reg)
  with(root/'INDEPENDENT_REGISTRY.lock').open('a+b')as held:
   fcntl.flock(held,fcntl.LOCK_EX)
   # A second independent open genuinely conflicts. Never wait/block on it.
   with(root/'INDEPENDENT_REGISTRY.lock').open('a+b')as second:
    try:fcntl.flock(second,fcntl.LOCK_SH|fcntl.LOCK_NB)
    except BlockingIOError:blocked_probe[0]+=1
    else:raise AssertionError('Independent SH unexpectedly succeeded under EX')
   start=time.monotonic();active[0]=True
   try:fn(target)
   finally:active[0]=False;EXdurations.append(time.monotonic()-start)
   put(root/'CPU_ONLY_REGISTRY.json',target);reg=target;grants[0]+=1
  assert forbidden[0]==0
 e.update_authority=update;frame=types.SimpleNamespace(f_locals=dict(engine=e,res=types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=types.SimpleNamespace(lock=threading.RLock()))))
 qa=root/'CPU_ONLY_QA.json';put(qa,dict(status='PASS_IR11_ISOLATED_REGISTRY_CPU_QUALIFICATION',source_sha256=M.sha(M.__file__),real_independent_FD_EX_callback_pure=True,qualification_only=True,NOT_ACTUAL_COMPONENT_QUALIFICATION=True));back=root/'CPU_ONLY_READBACK.json';put(back,dict(verified=True,source_sha256=M.sha(M.__file__),QA_sha256=M.sha(qa),qualification_only=True,NOT_ACTUAL_DEPLOYMENT_READBACK=True))
 cfg=dict(schema='IR11_REGISTRATION_CONFIGURATION_V1',qualification_only=True,source_sha256=M.sha(M.__file__),plan_path=str(planpath),plan_sha256=M.PLAN_SHA,manifest_path=str(planpath.parent/'MANIFEST.json'),manifest_sha256=M.MANIFEST_SHA,identity_proof_path=str(planpath.parent/'SCIENCE_IDENTITY_PROOF.json'),identity_proof_sha256=M.IDENTITY_SHA,accepted_snapshot_path=str(A/'agents/B/bpf_install_cadence_incident_v1/SOURCE_ARCHIVE_ACCEPTED_CHECKS.json'),accepted_snapshot_sha256=M.ACCEPTED_SHA,QA_path=str(qa),QA_sha256=M.sha(qa),readback_path=str(back),readback_sha256=M.sha(back))
 store=M.IncidentRecoveryRegistry(root,e,frame,cfg,fault_hook=fault);f=types.SimpleNamespace(root=root,e=e,store=store,reg=lambda:reg,q=lambda:reg['registered_future_requests'][M.REQ],ep=ep,grants=grants,forbidden=forbidden,probe=blocked_probe,EXdurations=EXdurations,auth=store.expected_authorization());metrics.append(f);return f
f=fixture();before=copy.deepcopy(f.reg());f.store.prepare(f.auth);ck('prepare has zero grants and no runtime scope',f.grants[0]==0 and not(f.root/'control/specs'/plan['rows'][0]['new_cohort']).exists())
result=f.store.register(f.auth);ck('independent FD EX held during real callback, SH demonstrably conflicts, forbidden engine calls0',f.probe[0]==1 and f.forbidden[0]==0 and f.grants[0]==1 and result['new_grants']==11)
q=f.q();ck('exact11 registered excluded rows, +11 and old consumed+all peers unchanged',len(q['authorized_incident_recovery_trials'])==11 and q['budget']==before['registered_future_requests'][M.REQ]['budget']+11 and q['consumed']==before['registered_future_requests'][M.REQ]['consumed']and all(f.reg()['registered_future_requests'][k]==v for k,v in before['registered_future_requests'].items()if k!=M.REQ))
ck('repeat reconcile/register does not grant again',f.store.reconcile()['new_grants']==0 and f.store.register(f.auth)['new_grants']==0 and f.grants[0]==1)
c=plan['rows'][0]['new_cohort'];s=f.e.canonical(c);s['estimated_peak_model_RAM_bytes']+=12345;put(f.root/'control/specs'/(c+'.json'),s);put(f.root/'control'/(c+'_SPEC.json'),s);q['admitted_specs'][c]=M.sha(f.root/'control/specs'/(c+'.json'));ck('official-style postgrant RAM refresh retains full science and reconciles without obsolete draftSHA',f.store.reconcile()['state']=='COMMITTED_RECONCILED'and f.grants[0]==1)
for stage in ['AFTER_SPEC_PUBLICATION','AFTER_AUTHORITY']:
 def fault(n):
  if n==stage:raise RuntimeError('INJECTED '+stage)
 x=fixture(fault);reject(lambda:x.store.register(x.auth));x.store.fault_hook=None;n=x.grants[0];recovered=x.store.reconcile();ck(stage+' reconcile is nongranting then explicit forward continuation grants at most once',x.grants[0]==n and(n==0 or recovered['state']=='COMMITTED_RECONCILED'))
 x.store.register(x.auth);assert x.grants[0]==1
x=fixture();old=plan['rows'][0]['original_cohort'];path=x.root/'analysis'/(old+'.RESULT.json');v=read(path);v['proof']['performance_accepted']=True;put(path,v);reject(lambda:x.store.register(x.auth));ck('tampered original negative evidence rejects before PREPARED or grants',x.grants[0]==0 and not(x.store.folder/'PREPARED.json').exists())
x=fixture();x.ep['parent_start_ticks']+=1;reject(lambda:x.store.register(x.auth));ck('wrong Main owner generation rejects',x.grants[0]==0)
durations=[v for f in metrics for v in f.EXdurations];out=dict(schema='IR11_REGISTRY_CPU_QUALIFICATION_V1',status='PASS_IR11_ISOLATED_REGISTRY_CPU_QUALIFICATION',source_sha256=M.sha(M.__file__),test_source_sha256=M.sha(__file__),count=len(checks),checks=checks,real_independent_FD_EX_callback_pure=True,independent_SH_conflict_probe_count=sum(f.probe[0]for f in metrics),forbidden_authority_calls_in_callback=sum(f.forbidden[0]for f in metrics),measured_callback_seconds=durations,authority_backend='ISOLATED_DEEP_COPY_FAKE',real_global_registry_lock_NOT_opened=True,real_native_update_authority_NOT_called=True,production_release_eligible=False,actual_model_starts=0,production_registry_changes=0,runtime_scope_installs=0,unchanged_draft_plan_sha256=M.PLAN_SHA,unchanged_draft_manifest_sha256=M.MANIFEST_SHA)
put(D/'CPU_QUALIFICATION.json',out);print(json.dumps(dict(path=str(D/'CPU_QUALIFICATION.json'),sha256=M.sha(D/'CPU_QUALIFICATION.json'),source_sha256=M.sha(M.__file__),count=len(checks),callback_seconds=durations)))
