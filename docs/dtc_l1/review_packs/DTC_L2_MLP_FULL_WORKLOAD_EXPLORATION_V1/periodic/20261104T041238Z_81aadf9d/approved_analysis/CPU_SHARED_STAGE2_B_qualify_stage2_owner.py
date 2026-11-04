"""Focused new Stage2 scope/prearm generation group, zero real execution."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,os,types,threading,importlib.util,copy
P=pathlib.Path;D=P(__file__).parent;checks=[]
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve())
sys.addaudithook(guard)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ck(n,v):assert v,n;checks.append(n)
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected HOLD')
F=load('Stage2_owner_native_fixture',D/'cpu_prefix_fixture.py');f=F.build_fixture(mode='BPF_REQUIRED');F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}))
consumer=load('actual_pristine_consumer_stage2',F.R/'tools/l2_results.py')
def fixture_loader(*a):raise AssertionError('No terminal finish in owner qualification')
consumer.load=fixture_loader;old=[]
def previous(c):old.append(c);return dict(state='EXACT_OLD',cohort=c)
def oldchoose(*a):return None
res0=load('actual_stage2_resource_allocator',F.R/'tools/l2_resources.py');aging=types.SimpleNamespace(lock=threading.RLock(),state=types.SimpleNamespace(protected=0,target=None));res=types.SimpleNamespace(choose_dispatch=oldchoose,resources=f.native.resources,forecast=res0.forecast,cpu_candidates=res0.cpu_candidates,DTC_LARGE_JOB_AGING_INSTALLED=aging)
frame=types.SimpleNamespace(f_locals=dict(engine=f.native,res=res,consumer=consumer,claims={}),f_globals={'worker':previous});main=sys.modules['__main__'];E=load('actual_stage2_E_consumer',f.cfg['source_paths']['consumer']);E.install_on_frame(frame,f.root/'CONFIG.json',f.cfg['exclusion_contract_path'],f.cfg['exclusion_contract_sha256'],f.native.assert_parent_lease,qualification_loader_sha256=F.sha(__file__))
ops=load('actual_qualified_old_worker_stage2',F.R/'tools/l2_ops.py');main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1={'worker':ops.worker}
def install():return f.producer.install_owner_dispatch(frame,f.root/'CONFIG.json',E.consumer_check,armed=False,hooks={'memory_lib':f.hooks['memory_lib']})
install();m=getattr(main,f.producer.OWNER_MARKER)
ck('exact unused3 scope excludes consumed real firstC',len(m['install_scope'])==3 and f.producer.INITIAL not in m['install_scope'])
ck('all three unarmed return deferred with zero entry',all(frame.f_globals['worker'](c)['state']=='ZERO_START_DEFERRED'for c in m['install_scope'])and not f.calls)
ck('consumed firstC and non-scope exact old delegate',frame.f_globals['worker'](f.producer.INITIAL)['state']=='EXACT_OLD'and frame.f_globals['worker']('OTHER')['state']=='EXACT_OLD')
f.producer.restore_owner_dispatch();ck('neverarmed reverse restores exact previous references',frame.f_globals['worker']is previous and res.choose_dispatch is oldchoose)
install();f.producer.arm_owner_dispatch();m=getattr(main,f.producer.OWNER_MARKER)
reject(f.producer.restore_owner_dispatch);ck('everarmed unaccepted unused identities preserve mandatory route',getattr(main,f.producer.OWNER_MARKER)is m and res.choose_dispatch is m['chooser']and not f.calls)
decision=res.choose_dispatch([f.spec],{}, {},F.read(F.R/'control/HISTORICAL_RSS.json'));ck('new scope fallback uses true full-cost shared resource and legal CPU',decision is not None and decision['cohort']==f.c and m['last_proof']['context']['cohort']==f.c and f.c not in f.q['consumed'])
other=next(c for c in m['install_scope']if c!=f.c);F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={other:dict(host_cpu=1,cpu_shared_timeslice_overlay_id='CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1')}))
ck('another shared claim holds max1 without births or budget changes',res.choose_dispatch([f.spec],{}, {},F.read(F.R/'control/HISTORICAL_RSS.json'))is None and not f.calls)
out=dict(status='PASS_STAGE2_UNUSED_SCOPE_PREARM_RESTORE_AND_SLOT_CPU_ONLY',count=len(checks),checks=checks,source_sha256=F.sha(D/'strace_entry.py'),source_resource=f.memcfg['qualified_sources'],source_observation=f.cfg['qualified_sources'],actual_model_starts=0,new_grants=0,production_changes=0,production_release_eligible=False,standins=['private frame/lease/authority and CPU counters','captured old chooser output and no physics finish','real owner closures, qualified raw worker and real E readiness executed'])
old=D/'CPU_STAGE2_OWNER_QUALIFICATION.json'
if old.exists():
 pre=D/('DEVELOPMENT_PREIMAGE_'+F.sha(old)+'.json')
 if not pre.exists():pre.write_bytes(old.read_bytes())
F.put(D/'CPU_STAGE2_OWNER_QUALIFICATION.json',out);print(json.dumps(dict(path=str(D/'CPU_STAGE2_OWNER_QUALIFICATION.json'),sha256=F.sha(D/'CPU_STAGE2_OWNER_QUALIFICATION.json'),count=len(checks))))
