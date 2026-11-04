import pathlib,json,hashlib,copy,importlib.util
P=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('binder',P/'bind_unconsumed_resources.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
reg=m.read(m.REG);before=m.ref(m.REG);fixture=P/'cpu_fixture';fixture.mkdir(exist_ok=True)
for f in ['system.py','highclock.py','shared.py']:(fixture/f).write_text('# CPU binder dependency fixture only\n')
m.write(fixture/'policy.json',dict(CPU_ONLY=True))
bindings=dict(scope=dict(global_EP_model_limit=10,scientific_budget_changed=False),module_refs={k:m.ref(fixture/(k+'.py'))for k in ['system','highclock','shared']},policy_ref=m.ref(fixture/'policy.json'),additional_pinned_refs=[m.ref(fixture/'shared.py')])
def reader(tag,g,case):
 p=pathlib.Path(g['data_ROOT'])/'cases'/case/'control/FROZEN_SPEC.json';return m.ref(p),m.read(p)
rows=[]
def check(name,fn,negative=False):
 try:
  fn()
  if negative:raise RuntimeError('negative not rejected')
 except (AssertionError,KeyError,ValueError)as e:
  if not negative:raise
  rows.append(dict(name=name,status='PASS_EXPECTED_REJECT',reason=str(e)));return
 rows.append(dict(name=name,status='PASS'))
x,protected,snap=m.compute(reg,bindings,reader)
check('current dynamic count equals sum remaining',lambda: m.__dict__['ALLOWED']if len(x)==sum(s['remaining']for s in snap.values())else (_ for _ in ()).throw(AssertionError('count')))
assert all(z['cohort']not in reg['registered_future_requests'][z['request_id']]['consumed']for z in x)
rows.append(dict(name='every currently consumed state excluded including CLOSED/RUNNING/pre-fork',status='PASS',protected=len(protected),unconsumed=len(x)))
for row in x:
 a=reader(row['group'],m.GROUPS[row['group']],row['cohort'])[1];b=row['candidate'];assert set(a)==set(b);assert {k for k in a if a[k]!=b[k]}<=m.ALLOWED
 for k in set(a)-m.ALLOWED:assert a[k]==b[k]
rows.append(dict(name='all non-resource fields byte-value identical incl source input 282 observer argv native HostQ stage limits',status='PASS',count=len(x)))
qcopy=copy.deepcopy(reg);picked=x[0];q=qcopy['registered_future_requests'][picked['request_id']];q['consumed'][picked['cohort']]=dict(state='CONSUMED_BEFORE_FORK');q['remaining']-=1;xx,pp,ss=m.compute(qcopy,bindings,reader);assert len(xx)==len(x)-1 and picked['cohort']not in [z['cohort']for z in xx];rows.append(dict(name='freshly consumed between bindings automatically skipped without refund',status='PASS'))
for state in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED','RUNNING','CONSUMED_BEFORE_FORK']:
 z=copy.deepcopy(reg);q=z['registered_future_requests'][picked['request_id']];q['consumed'][picked['cohort']]=dict(state=state);q['remaining']-=1
 xx,_,_=m.compute(z,bindings,reader);assert picked['cohort']not in [r['cohort']for r in xx];rows.append(dict(name='exclude '+state,status='PASS'))
for name,mut in [('extra_module',lambda z:z['module_refs'].update(unapproved=z['module_refs']['system'])),('cap9',lambda z:z['scope'].update(global_EP_model_limit=9)),('budget_change',lambda z:z['scope'].update(scientific_budget_changed=True)),('bad_module_sha',lambda z:z['module_refs']['system'].update(sha256='0'*64))]:
 z=copy.deepcopy(bindings);mut(z);check(name,lambda z=z:m.compute(reg,z,reader),True)
z=copy.deepcopy(reg);z['registered_future_requests'][picked['request_id']]['remaining']+=1;check('budget arithmetic mismatch',lambda:m.compute(z,bindings,reader),True)
z=copy.deepcopy(reg);q=z['registered_future_requests'][picked['request_id']];q['admitted_specs']['UNAPPROVED_CASE']='0'*64;q['budget']+=1;q['remaining']+=1;check('outside original exact cohort set',lambda:m.compute(z,bindings,reader),True)
assert m.ref(m.REG)==before
result=dict(status='PASS',checks=len(rows),rows=rows,registry_snapshot_ref=before,current_unconsumed_observed=len(x),official_registry_spec_native_writes=0,model_starts=0,CPU_fixture_not_cap10_resource_qualification=True)
m.write(P/'CPU_BINDER_CONTROLS.json',result);print(json.dumps(dict(status='PASS',checks=len(rows),unconsumed=len(x))))
