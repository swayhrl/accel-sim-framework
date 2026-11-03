"""Private CPU-only finite-controller controls. No native/registry/Git operation."""
import copy,importlib.util,json,pathlib,tempfile,types
P=pathlib.Path
mod=importlib.util.spec_from_file_location('candidate',P(__file__).with_name('finite_main_executor.py'));x=importlib.util.module_from_spec(mod);mod.loader.exec_module(x)
E=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_v2_20261103_v1')
results=[]
def test(name,fun):
 fun();results.append({'control':name,'status':'PASS'})
def reject(fn):
 try:fn()
 except (RuntimeError,KeyError,FileNotFoundError):return
 raise AssertionError('negative unexpectedly passed')
m=x.read(E/'control/EXACT_EXECUTION_MANIFEST.json');m.update(root=str(E),new_model_start_ceiling=8,authorization_ref=x.ref(E/'control/USER_AUTHORIZATION_MASTER.json'),publication=dict(repo='/root/data/ep_l2_full_workload_performance_20261027_v1/receipts/lane_o_v1r2_20261029/review',branch='hrl/ep-l2-main-implementation-performance-v2-20261029-v1',relative_directory='docs/ep_l2/operations/ep_main_implementation_performance_v2_20261029_v1/execution_v2_20261103_v1'),summary_archive_root='/root/share/mnt164/huangrulin/test_not_created')
test('Actual8spec/entry/authorization/criteria immutable read-only validation',lambda:x.validate_manifest(m))
for name,mutate in [('Extra9thpoint rejected',lambda n:n['points'].append(n['points'][0])),('Wrongbudgetcap rejected',lambda n:n.update(new_model_start_ceiling=9)),('Concurrency3 rejected',lambda n:n.update(max_concurrent_models=3)),('Retryallowed rejected',lambda n:n.update(automatic_retry=True)),('NativeSHA drift rejected',lambda n:n['native_entry_ref'].update(sha256='0'*64)),('EscapingGitpath rejected',lambda n:n['publication'].update(relative_directory='../execution_v2_20261103_v1')),('Oldledgernamespace rejected',lambda n:n['points'][0].update(science_request_id='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'))]:
 n=copy.deepcopy(m);mutate(n);test(name,lambda n=n:reject(lambda:x.validate_manifest(n)))
points=m['points']
def no_on_without_three():
 for k in range(3):
  rows={c:{'state':'CLOSED_ACCEPTED','archive_receipt_ref':{'dummy':True}} for c in x.T_OFF[:k]}
  e,ready,bad=x.runnable(points,rows,{})
  assert not ready and not any(p['cohort'] in x.T_ON for p in e)
test('Zero/one/two accepted primaries do not release ANY ON',no_on_without_three)
def on_afterall():
 rows={c:{'state':'CLOSED_ACCEPTED','archive_receipt_ref':{'dummy':True}} for c in x.T_OFF};e,ready,bad=x.runnable(points,rows,{})
 assert ready and sum(p['cohort'] in x.T_ON for p in e)==3
test('All3 accepted+archive refs release3ON independent of speedup/detach',on_afterall)
def noarchive():
 rows={c:{'state':'CLOSED_ACCEPTED'} for c in x.T_OFF};e,ready,bad=x.runnable(points,rows,{})
 assert not ready and not any(p['cohort'] in x.T_ON for p in e)
test('Accepted but missingarchive proof does not releaseON',noarchive)
def primaryfail():
 rows={x.T_OFF[0]:{'state':'CLOSED_UNACCEPTED'}};e,ready,bad=x.runnable(points,rows,{})
 assert bad and not any(p['cohort'] in x.T_ON for p in e)
test('Negative primary preservesconditionalhold',primaryfail)
def claimnotretry():
 rows={p['cohort']:{'state':'CONSUMED_BEFORE_FORK'} for p in points};e,_,_=x.runnable(points,rows,{})
 assert not e
test('Everyconsumedstate blocks launch retry',claimnotretry)
class Fake(x.Executor):
 def __init__(self,root,bad=False):
  self.E=root;self.C=root/'control';self.C.mkdir(parents=True);self.m=copy.deepcopy(m);self.m['root']=str(root);self.manifest_path=root/'manifest.json';x.put(self.manifest_path,self.m)
  self.points=sorted(copy.deepcopy(points),key=lambda p:(0 if p['cohort'] in x.T_OFF else (1 if p['group']=='wv' else 2),0 if 'GEMM' in p['cohort'] else 1,p['cohort']))
  self.states={};self.running={};self.pending_accept=[];self.lastpublish=0;self.started=x.time.monotonic();self.session='cpu-fixture';self.fake={};self.started_names=[];self.peak=0;self.bad=bad;self.fatal=[];self.phase_written=False
 def check_activation(self):pass
 def rows(self):return {},copy.deepcopy(self.fake)
 def start(self,p):
  c=p['cohort'];assert c not in self.started_names;self.started_names.append(c);self.running[c]={'round':0};self.fake[c]={'state':'CONSUMED_BEFORE_FORK'};self.peak=max(self.peak,len(self.running));assert self.peak<=2;return True
 def poll(self):
  for c in list(self.running):self.running.pop(c);self.pending_accept.append(c);self.fake[c]['state']='NATURAL_COMPLETE_PENDING_VALIDATION'
 def accept_one(self):
  if self.pending_accept:
   c=self.pending_accept.pop(0);self.fake[c]=dict(state='CLOSED_UNACCEPTED' if self.bad and c==x.T_OFF[0] else 'CLOSED_ACCEPTED',archive_receipt_ref={'dummy':True})
 def phase(self,rows):
  if all(rows.get(c,{}).get('state')=='CLOSED_ACCEPTED' for c in x.T_OFF):self.phase_written=True
 def ni(self,rows):pass
 def summary(self):return {}
 def publish(self,final=False):self.lastpublish=x.time.monotonic()
 def archive_summary(self):pass
 def event(self,*a,**k):pass
old_sleep=x.time.sleep;x.time.sleep=lambda n:None
try:
 def full():
  with tempfile.TemporaryDirectory() as t:
   f=Fake(P(t));f.run();assert len(f.started_names)==8 and len(set(f.started_names))==8 and f.peak==2 and f.phase_written
   assert f.started_names[0]==x.T_OFF[0]
   assert f.started_names.index('EP_PERF_V2_PROPOSED_GEMM_140F6ED3_W_ONLY')<f.started_names.index('EP_PERF_V2_PROPOSED_FASTWALSHTRANSFORM_FC3A9062_W_ONLY')
   assert max(f.started_names.index(c) for c in x.T_OFF)<min(f.started_names.index(c) for c in x.T_ON)
 test('Fullfinite8 private CPU scheduler max2/notretry/phaseorder',full)
 def negative():
  with tempfile.TemporaryDirectory() as t:
   f=Fake(P(t),bad=True);f.run();assert len(f.started_names)==5 and not f.phase_written and not any(c in f.started_names for c in x.T_ON)
 test('Private primarynegative consumes5total and holds3ON withoutretry',negative)
finally:x.time.sleep=old_sleep
with tempfile.TemporaryDirectory() as t:
 a=object.__new__(x.Executor);a.C=P(t);a.manifest_path=P(t)/'m.json';x.put(a.manifest_path,m)
 test('MissingMainactivation rejects before operation',lambda:reject(a.check_activation))
out=dict(schema='EP_MAIN_FINITE_EXECUTOR_CPU_CONTROLS_V1',status='PASS',controls=results,actual_native_calls=0,actual_model_starts=0,real_registry_writes=0,git_operations=0,tests_are_scheduler_and_artifact_contract_not_application_NI=True)
x.put(P(__file__).with_name('CPU_CONTROLS.json'),out);print(json.dumps(out,indent=2))
