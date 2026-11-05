import sys,pathlib,json,hashlib,copy,types,tempfile,threading,fcntl,importlib.util
sys.dont_write_bytecode=True
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
D=A/'agents/B/pending_resource_forecast_refresh_v1'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_positive_refresh',D/'resource_refresh.py');res=load('B_real_forecast',R/'tools/l2_resources.py')
scope=A/'coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json';rows=m.scope_rows(scope)
H=m.read(R/'control/HISTORICAL_RSS.json');policy=m.read(R/'control/RESOURCE_POLICY.json')
class Engine:
 def __init__(self,root,q):self.root=root;self.q=q;self.inside=False;self.ex_proved=False;self.calls=0;self.fail=False
 def registered(self):assert not self.inside;return None,None,copy.deepcopy(self.q)
 def canonical(self,c):assert not self.inside;return m.read(self.root/'control/specs'/(c+'.json'))
 def spec_for(self,c):
  s=self.canonical(c);b=m.read(self.root/'control/dispatch_bindings'/(c+'.json'));assert b['canonical_spec_sha256']==m.digest(m.js(s));s['host_cpu']=b['host_cpu'];assert m.digest(m.js(s))==b['resolved_spec_sha256'];return s
 def update_authority(self,fn):
  self.calls+=1
  with(self.root/'EX.lock').open('a+b')as first:
   fcntl.flock(first,fcntl.LOCK_EX)
   with(self.root/'EX.lock').open('a+b')as other:
    try:fcntl.flock(other,fcntl.LOCK_EX|fcntl.LOCK_NB);raise AssertionError('SECOND_FD_NOT_BLOCKED')
    except BlockingIOError:self.ex_proved=True
   reg=dict(registered_future_requests={m.REQ:copy.deepcopy(self.q)});self.inside=True
   try:fn(reg)
   finally:self.inside=False
   if self.fail:self.fail=False;raise RuntimeError('CPU_CRASH_AFTER_FILES_BEFORE_AUTHORITY_COMMIT')
   self.q=reg['registered_future_requests'][m.REQ]
def fixture():
 root=P(tempfile.mkdtemp(prefix='CPU_REFRESH_',dir=D));(root/'control/specs').mkdir(parents=True);(root/'control/dispatch_bindings').mkdir();(root/'control/qualification_ledger').mkdir()
 q=dict(request=m.REQ,budget=360,remaining=24,consumed={'old':{'uuid':'preserved'}},admitted_specs={},authorized_incident_recovery_trials=[{'preserved':'actual-test-placeholder'}],additional_operational_overlays={'unchanged':True})
 for c in rows:
  raw=(R/'control/specs'/(c+'.json')).read_bytes();s=json.loads(raw)
  if s['program']!='SYRK':continue
  for p in[root/'control/specs'/(c+'.json'),root/'control'/(c+'_SPEC.json')]:p.write_bytes(raw)
  q['admitted_specs'][c]=m.digest(raw);db=R/'control/dispatch_bindings'/(c+'.json')
  if db.exists():(root/'control/dispatch_bindings'/db.name).write_bytes(db.read_bytes())
 (root/'control/POOL_DISPATCH_RESERVATIONS.json').write_bytes(m.js({'claims':{}}))
 e=Engine(root,q);aging=types.SimpleNamespace(lock=threading.RLock());p=m.prepare(root,e,res,H,policy,scope,{})
 return root,e,aging,p
checks=[]
def ok(name,fn):fn();checks.append({'case':name,'status':'PASS'})
def reject(fn):
 try:fn()
 except(AssertionError,RuntimeError,BlockingIOError):return
 raise AssertionError('EXPECTED_HOLD')
def positive():
 root,e,a,p=fixture();old=copy.deepcopy(e.q);result=m.apply(p,e,res,H,{},a,lambda:None);assert e.ex_proved and e.calls==1
 assert m.apply(p,e,res,H,{},a,lambda:None)==result and e.calls==1
 new=copy.deepcopy(e.q);new['admitted_specs']=old['admitted_specs'];assert new==old
 assert sum(i['DB_present']for i in p['items'])==1
 for i in p['items']:
  assert json.loads(i['files'][0]['new_utf8'])['estimated_peak_model_RAM_bytes']>=json.loads(i['files'][0]['old_utf8'])['estimated_peak_model_RAM_bytes']
  if i['DB_present']:assert e.spec_for(i['cohort'])['host_cpu']==26
ok('10_actual_science_copy_positive_real_forecast_EX_separateFD_no_recursive_authority_DB_CPU26_and_idempotent',positive)
def crash():
 root,e,a,p=fixture();e.fail=True
 reject(lambda:m.apply(p,e,res,H,{},a,lambda:None));assert all(e.q['admitted_specs'][i['cohort']]==i['old_spec_sha256']for i in p['items'])
 m.apply(p,e,res,H,{},a,lambda:None);assert e.calls==2
 assert all(e.q['admitted_specs'][i['cohort']]==i['new_spec_sha256']for i in p['items'])
ok('crash_after_file_publication_before_registry_commit_forward_reconcile_no_new_grant',crash)
def bad(kind):
 root,e,a,p=fixture();c=p['items'][0]['cohort']
 if kind=='spent':e.q['consumed'][c]={'uuid':'newbirth'}
 elif kind=='claim':(root/'control/POOL_DISPATCH_RESERVATIONS.json').write_bytes(m.js({'claims':{c:{'host_cpu':1}}}))
 elif kind=='intent':(root/'control/qualification_ledger'/(c+'.INTENT.json')).write_text('{}')
 elif kind=='science':p['items'][0]['files'][0]['new_utf8']=p['items'][0]['files'][0]['new_utf8'].replace('"SYRK"','"GEMM"')
 elif kind=='forecast':p['items'][0]['forecast']['predicted_peak_RAM_bytes']+=1
 elif kind=='binding_birth':
  absent=next(i for i in p['items']if not i['DB_present']);(root/'control/dispatch_bindings'/(absent['cohort']+'.json')).write_text('{}')
 before={v['path']:P(v['path']).read_bytes()for i in p['items']for v in i['files']}
 reject(lambda:m.apply(p,e,res,H,{},a,lambda:None));assert all(P(path).read_bytes()==raw for path,raw in before.items())and e.calls==0
for name in['spent','claim','intent','science','forecast','binding_birth']:ok(name+'_reject_without_canonical_or_authority_mutation',lambda name=name:bad(name))
qa=dict(status='PASS',schema='CPU_ONLY_PENDING_RESOURCE_REFRESH_QUALIFICATION_V1',qualification_only=True,production_actions=0,model_starts=0,source_sha256=m.digest((D/'resource_refresh.py').read_bytes()),forecast_source_sha256=m.digest((R/'tools/l2_resources.py').read_bytes()),scope_sha256=m.SCOPE_SHA,checks=checks,count=len(checks),limitations=['All writes target isolated CPU roots. Actual science and current history copied read-only. No production apply, registry, models, or scheduler changes.'])
(D/'CPU_QUALIFICATION.json').write_bytes(m.js(qa));print(json.dumps(qa,indent=2))
