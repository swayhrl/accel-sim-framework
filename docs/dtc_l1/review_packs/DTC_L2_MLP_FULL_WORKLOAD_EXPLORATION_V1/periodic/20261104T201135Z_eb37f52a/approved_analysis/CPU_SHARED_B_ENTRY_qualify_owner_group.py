"""One new prearm/fallback/restore integration group; private frame only."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,os,types,threading,importlib.util
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
F=load('Shared_owner_actual_fixture',D/'cpu_prefix_fixture.py');f=F.build_fixture();F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}));consumer=load('actual_shared_private_consumer',F.R/'tools/l2_results.py')
def fixture_loader(*a):raise AssertionError('No physics finish in owner qualification')
consumer.load=fixture_loader;old=[];original_decision=None
def previous(c):old.append(c);return dict(state='EXACT_OLD',cohort=c)
def oldchoose(*a):return original_decision
origres=load('actual_original_allocator_owner',F.R/'tools/l2_resources.py');aging=types.SimpleNamespace(lock=threading.RLock(),state=types.SimpleNamespace(protected=0,target=None))
res=types.SimpleNamespace(choose_dispatch=oldchoose,resources=f.native.resources,forecast=origres.forecast,cpu_candidates=origres.cpu_candidates,DTC_LARGE_JOB_AGING_INSTALLED=aging)
frame=types.SimpleNamespace(f_locals=dict(engine=f.native,res=res,consumer=consumer,claims={}),f_globals={'worker':previous});main=sys.modules['__main__'];E=load('actual_shared_E_owner_consumer',f.cfg['source_paths']['consumer']);E.install_on_frame(frame,f.root/'CONFIG.json',f.cfg['exclusion_contract_path'],f.cfg['exclusion_contract_sha256'],f.native.assert_parent_lease,qualification_loader_sha256=F.sha(__file__))
ops=load('actual_old_ops_owner',F.R/'tools/l2_ops.py');main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1={'worker':ops.worker}
f.producer.install_owner_dispatch(frame,f.root/'CONFIG.json',E.consumer_check,armed=False,hooks={'memory_lib':f.hooks['memory_lib']});m=getattr(main,f.producer.OWNER_MARKER)
ck('unarmed actual new wrapper returns deferred before entry or INTENT',frame.f_globals['worker'](f.c)['state']=='ZERO_START_DEFERRED'and not f.calls and f.c not in f.q['consumed'])
ck('other identities exactdelegate previous worker',frame.f_globals['worker']('OTHER')['state']=='EXACT_OLD'and old==['OTHER'])
f.producer.restore_owner_dispatch();ck('neverarmed no claim restores exact worker and chooser',frame.f_globals['worker']is previous and res.choose_dispatch is oldchoose)
f.producer.install_owner_dispatch(frame,f.root/'CONFIG.json',E.consumer_check,armed=False,hooks={'memory_lib':f.hooks['memory_lib']});f.producer.arm_owner_dispatch();m=getattr(main,f.producer.OWNER_MARKER)
ck('explicit arm changes flags only, zero execution',m['armed']and m['ever_armed']and not f.calls)
reject(f.producer.restore_owner_dispatch);ck('everarmed unaccepted even unspent retains worker chooser marker',frame.f_globals['worker']is m['wrapper']and res.choose_dispatch is m['chooser']and getattr(main,f.producer.OWNER_MARKER)is m)
original_decision={'cohort':'OTHER_ORDINARY','host_cpu':123};ck('ordinary real chooser result passes unchanged',res.choose_dispatch([f.spec],{}, {},F.read(F.R/'control/HISTORICAL_RSS.json'))is original_decision);original_decision=None
decision=res.choose_dispatch([f.spec],{}, {},F.read(F.R/'control/HISTORICAL_RSS.json'));print(json.dumps(dict(owner_choice=decision,hold=m['last_hold'])));ck('exact1 fallback runs true shared projection and legal allocator with zero grant',decision is not None and decision['cohort']==f.c and m['last_proof']['CPU2_spare_PASS_claimed']is False and f.c not in f.q['consumed'])
aging.state.protected=2**60;reject_before=len(f.calls);ck('protectedR cannot be spent by fallback, no bookkeeping mutation',res.choose_dispatch([f.spec],{}, {},F.read(F.R/'control/HISTORICAL_RSS.json'))is None and aging.state.protected==2**60 and len(f.calls)==reject_before)
out=dict(status='PASS_SHARED_SINGLE_PREARM_RESTORE_OWNER_GROUP_CPU_ONLY',count=len(checks),checks=checks,source_sha256=F.sha(D/'strace_entry.py'),consumer_source_sha256=F.sha(E.__file__),resource_source_sha256=f.memcfg['qualified_sources']['library'],actual_old_chooser_and_pristine_consumer_code_bound=True,standins=['frame/owner lease/private authority','old chooser outputs','CPU/resource evidence only via dual qualification hooks'],actual_model_starts=0,production_changes=0,production_release_eligible=False);F.put(D/'CPU_OWNER_GROUP.json',out);print(json.dumps(dict(path=str(D/'CPU_OWNER_GROUP.json'),sha256=F.sha(D/'CPU_OWNER_GROUP.json'),count=len(checks),last_hold=m['last_hold'])))
