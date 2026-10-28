"""Real artifacts/CanaryScope, isolated copy authority; no production writes."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,copy,tempfile,types,threading,os,importlib.util
P=pathlib.Path;D=P(__file__).parent;A=D.parents[2];R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');checks=[]
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('NO_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'NO_WRITE_OUTSIDE_FIXTURE'
sys.addaudithook(guard)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('B_exact4_registry',D/'engineering_registry.py')
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(M.js(v))
def ck(n,b):assert b,n;checks.append(n)
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected HOLD')
planpath=A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json';contractpath=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';scopepath=A/'coordinator/bpf_canary_orchestration_v2/scope_bridge.py';plan=read(planpath)
birth=read(A/'agents/B/strace_bpf_future_entry_v2/DELIVERY.json')
baseline=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
cs={r['cohort']for r in plan['rows']}
def fixture(fault=None):
 root=P(tempfile.mkdtemp(prefix='CPU_REGISTRATION_',dir=D));(root/'control').mkdir();(root/'analysis').mkdir()
 for file in ['SCOPE.json','MATRIX_CURRENT.json']:(root/'control'/file).write_bytes((R/'control'/file).read_bytes())
 for row in plan['rows']:(root/'analysis'/(row['reference_cohort']+'.RESULT.json')).write_bytes((R/'analysis'/(row['reference_cohort']+'.RESULT.json')).read_bytes())
 reg=copy.deepcopy(baseline);q=reg['registered_future_requests'][M.REQ];q['qualification_only']=True
 actualplan=dict(parent_pid=os.getpid(),parent_start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]))
 e=load('B_exact4_private_native_'+root.name,R/'tools/l2_native.py');e.R=root;e.registered=lambda:(reg,{'qualification_only':True},reg['registered_future_requests'][M.REQ],actualplan);e.assert_parent_lease=lambda:dict(**actualplan,qualification_only=True)
 def canonical(c):return read((root if c in cs else R)/'control/specs'/(c+'.json'))
 e.canonical=canonical;count=[0]
 def update(fn):
  nonlocal reg
  target=copy.deepcopy(reg);fn(target);put(root/'CPU_ONLY_AUTHORITY.json',target);reg=target;count[0]+=1
 e.update_authority=update
 frame=types.SimpleNamespace(f_locals=dict(engine=e,res=types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=types.SimpleNamespace(lock=threading.RLock()))))
 qa=root/'CPU_ONLY_COMBINED_QA.json';back=root/'CPU_ONLY_READBACK.json';put(qa,dict(status='PASS',native_prefix_qualified=True,extra_strict_qualified=True,consumer_archive_qualified=True,qualified_sources=birth['qualified_sources'],expected_pins=birth['expected_pins'],qualification_only=True,NOT_ACTUAL_RELEASE=True));put(back,dict(verified=True,QA_sha256=M.sha(qa),qualified_sources=birth['qualified_sources'],expected_pins=birth['expected_pins'],qualification_only=True,NOT_GITHUB_READBACK=True))
 cfg=dict(schema='BPF_EXACT4_REGISTRATION_CONFIGURATION_V1',request=M.REQ,qualification_only=True,registration_source_sha256=M.sha(M.__file__),entry_delivery_path=str(A/'agents/B/strace_bpf_future_entry_v2/DELIVERY.json'),entry_delivery_sha256=M.ENTRY_DELIVERY_SHA,draft_plan_path=str(planpath),draft_plan_sha256=M.PLAN_SHA,exclusion_contract_path=str(contractpath),exclusion_contract_sha256=M.CONTRACT_SHA,scope_source_path=str(scopepath),scope_source_sha256=M.SCOPE_SHA,original_results_source_path=str(R/'tools/l2_results.py'),source_paths=birth['source_paths'],qualified_sources=birth['qualified_sources'],expected_pins=birth['expected_pins'],QA_path=str(qa),QA_sha256=M.sha(qa),readback_path=str(back),readback_sha256=M.sha(back))
 store=M.EngineeringCanaryRegistry(root,e,frame,cfg,fault_hook=fault)
 return types.SimpleNamespace(root=root,e=e,reg=lambda:reg,q=lambda:reg['registered_future_requests'][M.REQ],count=count,store=store,auth=store.expected_authorization(),plan=actualplan,frame=frame,cfg=cfg)
f=fixture();before=copy.deepcopy(f.reg());a=f.store.prepare(f.auth)
ck('prepare creates immutable intent only, no specs/no grant',a['state']=='PREPARED_NO_GRANT'and f.count[0]==0 and all(not(f.root/'control/specs'/(c+'.json')).exists()for c in cs))
result=f.store.register(f.auth);q=f.q()
ck('single callback adds exact4 budget and 4 matching CanaryScope authorization rows',result['new_grants']==4 and f.count[0]==1 and q['budget']==before['registered_future_requests'][M.REQ]['budget']+4 and len(q['authorized_engineering_observation_canaries'])==4)
ck('all eight immutable canonical/alias specs and unchanged primary matrices',all(M.sha(f.root/'control/specs'/(c+'.json'))==M.sha(f.root/'control'/(c+'_SPEC.json'))==q['admitted_specs'][c]for c in cs)and all(M.sha(f.root/'control'/name)==M.sha(R/'control'/name)for name in ['SCOPE.json','MATRIX_CURRENT.json']))
ck('retry is idempotent no second grant',f.store.register(f.auth)['new_grants']==0 and f.count[0]==1)
c=sorted(cs)[0];s=f.e.canonical(c);s['estimated_peak_model_RAM_bytes']+=12345;put(f.root/'control/specs'/(c+'.json'),s);put(f.root/'control'/(c+'_SPEC.json'),s);q['admitted_specs'][c]=M.sha(f.root/'control/specs'/(c+'.json'));q['consumed'][c]={'uuid':'CPU_FAKE_FRESH_NEW_UUID_NO_MODEL'};q['remaining']-=1
ck('legal postgrant resource refresh and new consumption reconcile science not obsolete draft SHA',f.store.reconcile()['state']=='COMMITTED_RECONCILED'and f.store.register(f.auth)['new_grants']==0 and f.count[0]==1)
for stage in ['AFTER_PREPARED','AFTER_SPEC_1','AFTER_SPEC_PUBLICATION','AFTER_AUTHORITY','AFTER_COMMITTED']:
 def fault(name):
  if name==stage:raise RuntimeError('CPU_INJECTED_CRASH '+stage)
 x=fixture(fault);reject(lambda:x.store.register(x.auth));n=x.count[0];x.store.fault_hook=None;r=x.store.reconcile();x.store.register(x.auth)
 ck(stage+' forward recovery exactly one final grant, no repeat after authority witness',x.count[0]==1 and x.q()['budget']==before['registered_future_requests'][M.REQ]['budget']+4 and(n==0 or r['state']=='COMMITTED_RECONCILED'))
x=fixture();x.store.cfg['expected_pins'][str(R/'tools/l2_native.py')]='0'*64;reject(lambda:x.store.prepare(x.auth));ck('source drift rejects before PREPARED/spec/grant',x.count[0]==0 and not x.store.folder.exists())
x=fixture();old=x.e.canonical
def badscience(c):
 s=old(c);s['program']='CORRUPTED_REFERENCE_PROJECTION';return s
x.e.canonical=badscience;reject(lambda:x.store.prepare(x.auth));ck('accepted reference bytes do not excuse changed reference scientific projection',x.count[0]==0 and not x.store.folder.exists())
x=fixture();bad=copy.deepcopy(x.auth);bad['additional_starts']=3;reject(lambda:x.store.register(bad));ck('Main explicit exact4 authorization required',x.count[0]==0)
x=fixture();x.store.register(x.auth);c=sorted(cs)[0];del x.q()['admitted_specs'][c];x.q()['budget']-=1;x.q()['remaining']-=1;reject(x.store.reconcile);reject(lambda:x.store.register(x.auth));ck('partial authority witness fails closed without repairing/regranting',x.count[0]==1)
x=fixture();x.store.register(x.auth);q=x.q()
for c in cs:del q['admitted_specs'][c]
q['budget']-=4;q['remaining']-=4;q['authorized_engineering_observation_canaries']=[];q['authorized_engineering_observation_transactions']=[]
reject(x.store.reconcile);reject(lambda:x.store.register(x.auth));ck('COMMITTED without authority never resets or regrants',x.count[0]==1)
x=fixture();errors=[]
def otherthread():
 try:x.store.prepare(x.auth)
 except Exception as e:errors.append(type(e).__name__)
t=threading.Thread(target=otherthread);t.start();t.join();ck('non Main thread denied before writes',bool(errors)and not x.store.folder.exists())
x=fixture();x.plan['parent_pid']+=1;reject(lambda:x.store.register(x.auth));ck('wrong actual owner PID denied',x.count[0]==0)
x=fixture();x.store.prepare(x.auth);pp=x.store.folder/x.store.transaction_id/'PREPARED.json';v=read(pp);v['specs'][sorted(cs)[0]]['native_simulator_argv'].append('UNAPPROVED');put(pp,v);reject(lambda:x.store.register(x.auth));ck('corrupt prepared science cannot pass through immutable source preflight',x.count[0]==0)
out=dict(schema='B_EXACT4_REGISTRATION_CPU_QUALIFICATION_V1',status='PASS_ISOLATED_FAKE_AUTHORITY_ONLY',count=len(checks),checks=checks,source_sha256={str(D/'engineering_registry.py'):M.sha(D/'engineering_registry.py'),str(D/'qualify_registration.py'):M.sha(D/'qualify_registration.py')},actual_evidence_pins=dict(plan=M.sha(planpath),exclusion_contract=M.sha(contractpath),scope_source=M.sha(scopepath)),qualified_sources=birth['qualified_sources'],real_immutable_Main_artifacts_consumed=True,actual_CanaryScope_validate_executed=True,original_reference_RESULT_SHA_cycles_science_verified=True,authority_backend='EXPLICIT_COPY_ISOLATED_FAKE',real_native_update_authority_NOT_called=True,QA_readback_backend='EXPLICIT_CPU_STANDINS',production_release_eligible=False,actual_model_starts=0,production_registry_changes=0,production_changes=0)
put(D/'CPU_QUALIFICATION.json',out);print(json.dumps(dict(path=str(D/'CPU_QUALIFICATION.json'),sha256=M.sha(D/'CPU_QUALIFICATION.json'),status=out['status'],count=len(checks))))
