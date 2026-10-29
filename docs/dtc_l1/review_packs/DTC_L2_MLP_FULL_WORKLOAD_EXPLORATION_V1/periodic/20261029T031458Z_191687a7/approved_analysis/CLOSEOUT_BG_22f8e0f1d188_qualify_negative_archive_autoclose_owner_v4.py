"""Reference stability delta: real private FrameGuard/ScopeSync classes only."""
from pathlib import Path
import ast,copy,importlib.util,json,sys,threading,types
sys.dont_write_bytecode=True
D=Path(__file__).parent
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('NO_PROCESS_OR_SIGNAL')
sys.addaudithook(audit)
m=load('V4_delta',D/'negative_archive_autoclose_owner_v4.py');R=m.ROOT
fg=load('real_private_FrameGuard',R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py')
ss=load('real_private_ScopeSync',R/'control/operational_amendments/future_memory_scope_sync_v1/scope_sync.py')
sync=ss.ScopeSync.__new__(ss.ScopeSync)
aging=types.SimpleNamespace(lock=threading.RLock(),original=lambda:None,frame_provider=lambda:None,state=types.SimpleNamespace(advance=lambda:None),calls=0)
entered=threading.Event();release=threading.Event();checked=threading.Event();errors=[]
def private_choose():
 entered.set();assert release.wait(2);return None
aging.wrapper=private_choose
gate=fg.FrameReadGuard(aging)
consumer=types.SimpleNamespace(safe_finish=lambda:None,finish_evidence=lambda:None,put=lambda:None,archive_closed=lambda:None,load=lambda:None)
res=types.SimpleNamespace(choose_dispatch=lambda:None,resources=lambda:None)
frame=types.SimpleNamespace(f_locals=dict(engine=object(),consumer=consumer,claims={},pool=object(),running={},post={},res=res,adaptive=types.SimpleNamespace(recommend=lambda:None),registry=sync),f_globals=dict(worker=lambda:None))
bridge=dict(selected=lambda:None,original_refs=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed))
marker=dict(frame=frame,consumer=consumer,aging=aging,wrapper=consumer.safe_finish,bridge=bridge)
main=types.SimpleNamespace();setattr(main,m.MARKER,marker)
saved=m.refs(main,marker);checks=[]
owner=threading.Thread(target=gate.choose,name='CPU_PRIVATE_OWNER');owner.start();assert entered.wait(1)
# Prove the old unsynchronized provider check sees a real temporary reference.
assert m._refs_locked(main,marker)[12]!=saved[12]
def validate():
 try:m.validate_invariant(main,marker,saved,lambda:None);checked.set()
 except BaseException as e:errors.append(repr(e))
collector=threading.Thread(target=validate,name='CPU_PRIVATE_COLLECTOR');collector.start()
assert not checked.wait(.03)
release.set();owner.join(2);collector.join(2)
assert not owner.is_alive()and not collector.is_alive()and checked.is_set()and not errors
assert aging.frame_provider is gate.original_provider and not aging.lock._is_owned()
# Exact invariant releases the lock; no archive callback is inside any aging-lock with.
m.validate_invariant(main,marker,saved,lambda:None);assert not aging.lock._is_owned()
tree=ast.parse((D/'negative_archive_autoclose_owner_v4.py').read_text())
for node in ast.walk(tree):
 if isinstance(node,ast.With)and any('aging' in ast.unparse(x.context_expr)for x in node.items):
  assert not any(isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr in ['close_negative']for x in ast.walk(node))
checks.append('actual_FrameGuard_private_temporary_provider_swap_waits_same_mutex_then_restores_no_archive_lock')
b1=sync.extend;b2=sync.extend;assert b1 is not b2 and m.reference_identity(b1)==m.reference_identity(b2)
assert m.refs(main,marker)==saved
other=ss.ScopeSync.__new__(ss.ScopeSync);frame.f_locals['registry']=other
try:m.validate_invariant(main,marker,saved,lambda:None)
except RuntimeError:pass
else:raise AssertionError('changed bound self allowed')
frame.f_locals['registry']=sync;sync.extend=types.MethodType(lambda self:None,sync)
try:m.validate_invariant(main,marker,saved,lambda:None)
except RuntimeError:pass
else:raise AssertionError('changed bound func allowed')
del sync.extend;assert m.refs(main,marker)==saved
checks.append('actual_ScopeSync_bound_extend_fresh_method_identity_normalized_changed_self_or_func_rejected')
cfg=m.read(D/'PREEXISTING_F3_INPUTS.json');native=load('V4_readonly_native',R/'tools/l2_native.py');q=native.registered()[2]
before={c:m.sha(R/'analysis'/(c+'.NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE.json'))for c in m.F3_CERTIFICATES}
for c in before:assert m.verify_preexisting(R,q,c,cfg)
c=next(iter(before));bad=copy.deepcopy(cfg);bad['preexisting_verified_certificates'][c]='0'*64
try:m.verify_preexisting(R,q,c,bad)
except RuntimeError:pass
else:raise AssertionError('changed historical pin allowed')
badq=copy.deepcopy(q);badq['consumed'][c]['uuid']='different'
try:m.verify_preexisting(R,badq,c,cfg)
except RuntimeError:pass
else:raise AssertionError('changed historical UUID allowed')
assert all(m.sha(R/'analysis'/(c+'.NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE.json'))==h for c,h in before.items())
checks.append('two_actual_F3_certificates_readonly_full_metadata_installation_pin_replay_no_archive_no_overwrite')
prior=dict(phase='FAILED_SOURCE_KEEP',thread=types.SimpleNamespace(is_alive=lambda:False));oldmain=types.SimpleNamespace();setattr(oldmain,'DTC_MAIN_NEGATIVE_ARCHIVE_AUTOCLOSE_OWNER_V3',prior)
m.validate_predecessor(oldmain);prior['thread']=types.SimpleNamespace(is_alive=lambda:True)
try:m.validate_predecessor(oldmain)
except RuntimeError:pass
else:raise AssertionError('live predecessor allowed')
checks.append('preserved_terminal_F3_marker_allowed_live_predecessor_rejected')
report=dict(schema=m.ID+'_REFERENCE_STABILITY_CPU',status='PASS_NEGATIVE_ARCHIVE_OWNER_V4_REFERENCE_STABILITY_CPU',source_sha256=m.sha(D/'negative_archive_autoclose_owner_v4.py'),helper_sha256=m.H_SHA,count=len(checks),checks=checks,real_FrameGuard_source_sha256=m.sha(fg.__file__),real_ScopeSync_source_sha256=m.sha(ss.__file__),old_pipeline_checks_not_rerun=True,actual_Main_not_used=True,private_fixture_threads_started=2,production_threads_started=0,original_archive_calls=0,models_started=0,new_grants=0,production_writes=0)
m.exclusive(D/'CPU_QUALIFICATION.json',report);print(json.dumps(report))
