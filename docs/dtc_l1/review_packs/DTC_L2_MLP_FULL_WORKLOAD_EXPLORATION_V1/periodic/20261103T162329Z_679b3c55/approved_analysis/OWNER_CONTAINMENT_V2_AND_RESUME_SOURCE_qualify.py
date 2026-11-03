"""Focused race/cleanup qualification; no simulator or production access."""
import importlib.util,pathlib,types,json,hashlib
P=pathlib.Path
source=P(__file__).with_name('failure_containment.py')
sp=importlib.util.spec_from_file_location('failure_containment_qa',source);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def ok(name,v):assert v;checks.append(name)
def rejects(name,fn):
    try:fn()
    except AssertionError:checks.append(name)
    else:raise AssertionError(name)
before={'old':dict(uuid='old-uuid',charged=1,intent_sha256='immutable')}
after={'old':dict(**before['old'],execution_receipt={'natural':True})}
ok('old natural receipt append remains legal',m.verify_old_consumption(before,after))
rejects('old UUID alteration rejected',lambda:m.verify_old_consumption(before,{'old':dict(uuid='NEW',charged=1,intent_sha256='immutable')}))
rejects('old immutable field alteration rejected',lambda:m.verify_old_consumption(before,{'old':dict(uuid='old-uuid',charged=2,intent_sha256='immutable')}))
rejects('existing receipt rewrite rejected',lambda:m.verify_old_consumption(after,{'old':dict(**before['old'],execution_receipt={'natural':False})}))
called=[];cohorts=['e1','e2','e3','e4'];q={'consumed':{}}
def prior_safe(c):called.append(('safe',c));return c
def prior_worker(c):called.append(('worker',c));return c
def prior_choose(pool,*a,**k):called.append(('choose',pool));return {'cohort':pool[0]['cohort']}if pool else None
res=types.SimpleNamespace(choose_dispatch=prior_choose)
frame=types.SimpleNamespace(f_globals={'safe':prior_safe,'worker':prior_worker},f_locals={'res':res})
engine=types.SimpleNamespace(registered=lambda:(None,None,q,None))
guard=m.install_execution_guards(frame,cohorts,engine,'CPU_FIXTURE_INSTALL_FAILURE')
ok('cached engineering decision cannot reach old safe route',frame.f_globals['safe']('e1')['state']=='ZERO_START_ENGINEERING'and not called)
ok('direct cached engineering worker cannot reach old entry',frame.f_globals['worker']('e2')['model_starts']==0 and not called)
q['consumed']['e3']={'uuid':'new-consumed'}
ok('spent engineering identity preserved without retry',frame.f_globals['safe']('e3')['state']=='SPENT_ENGINEERING_PRESERVE'and not called)
ok('non-scope safe exact delegate',frame.f_globals['safe']('ordinary')=='ordinary'and called[-1]==('safe','ordinary'))
ok('non-scope worker exact delegate',frame.f_globals['worker']('ordinary')=='ordinary'and called[-1]==('worker','ordinary'))
cleanup=m.best_effort([('failing priority',lambda:(_ for _ in()).throw(RuntimeError('expected'))),('later protection',lambda:called.append(('cleanup','continued')))])
ok('cleanup failure cannot prevent later action or error evidence',len(cleanup)==2 and cleanup[0]['status']=='RESTORE_ERROR_PRESERVED'and cleanup[1]['status']=='RESTORED')
admission=m.install_admission_guard(frame,cohorts)
ok('cached engineering-only pending pool denied',res.choose_dispatch([{'cohort':'e4'}])is None)
pool=[{'cohort':'e1'},{'cohort':'ordinary'}]
ok('mixed cached pending pool can only dispatch ordinary',res.choose_dispatch(pool)=={'cohort':'ordinary'})
pool=[{'cohort':'ordinary'}];res.choose_dispatch(pool)
ok('unchanged ordinary pool passed with exact original object',called[-1][0]=='choose'and called[-1][1]is pool)
engine.registered=lambda:(_ for _ in()).throw(RuntimeError('unknown identity'))
ok('identity lookup failure never falls back',frame.f_globals['safe']('e4')['state']=='ENGINEERING_PRESERVE')
result=dict(schema='MAIN_BPF_FAILURE_CONTAINMENT_CPU_V2',status='PASS',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checks=checks,count=len(checks),scope='Private frame/call-site race fixtures; not actual owner or model qualification.',models_started=0,production_changes=0)
out=P(__file__).with_name('FAILURE_CONTAINMENT_CPU_QUALIFICATION.json')
with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
