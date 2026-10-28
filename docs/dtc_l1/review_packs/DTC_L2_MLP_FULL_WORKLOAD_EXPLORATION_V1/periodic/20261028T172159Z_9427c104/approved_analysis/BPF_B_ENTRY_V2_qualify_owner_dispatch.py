"""Private frame only: real worker code/consumer installer; every spawn forbidden."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,types,threading,importlib.util,os
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
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append(n)
def reject(f):
 try:f()
 except Exception:return
 raise AssertionError('Expected reject')
fmod=load('B_owner_actual_fixture',D/'cpu_prefix_fixture.py')
contract_path=D.parents[2]/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';contract=fmod.read(contract_path)
c=next(c for c,r in contract['scope_cohorts'].items()if r['program']=='heartwall'and r['mode']=='BPF_REQUIRED')
f=fmod.build_fixture(cohort=c);root=f.root;(root/'logs').mkdir();producer=f.producer
consumer=load('B_actual_private_consumer',fmod.R/'tools/l2_results.py')
def fixture_loader(name,file):raise AssertionError('Owner closure test must not finish physics')
consumer.load=fixture_loader
res=types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=types.SimpleNamespace(lock=threading.RLock()))
oldcalls=[];runcalls=[]
def old_worker(c):oldcalls.append(c);return {'state':'EXACT_OLD_WORKER_STANDIN','cohort':c}
frame=types.SimpleNamespace(f_locals=dict(engine=f.native,res=res,consumer=consumer,claims={}),f_globals={'worker':old_worker})
main=sys.modules['__main__'];E=load('B_qualified_E_consumer',f.cfg['source_paths']['consumer'])
before=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
E.install_on_frame(frame,root/'CONFIG.json',contract_path,sha(contract_path),f.native.assert_parent_lease,qualification_loader_sha256=sha(__file__))
ck('Actual E installer changes only private safe_finish and real readiness passes',before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)and E.consumer_check(frame,f.cfg)is True)
ops=load('B_unchanged_ops',fmod.R/'tools/l2_ops.py')
def run(argv,**kw):runcalls.append(list(argv));return types.SimpleNamespace(returncode=0,stdout='CPU_ROUTING_STANDIN_NO_MODEL',stderr='')
namespace=dict(ops.worker.__globals__,R=root,load=lambda *a:f.native,subprocess=types.SimpleNamespace(run=run))
raw=types.FunctionType(ops.worker.__code__,namespace,ops.worker.__name__,ops.worker.__defaults__,ops.worker.__closure__)
main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1={'worker':raw}
producer.install_owner_dispatch(frame,root/'CONFIG.json',E.consumer_check)
m=getattr(main,producer.OWNER_MARKER)
ck('Same original worker code/private N is sole additional globals change',m['clone'].__code__ is raw.__code__ and all(m['clone'].__globals__[k]is raw.__globals__[k]for k in raw.__globals__ if k!='N'))
value=frame.f_globals['worker'](c)
ck('Selected cohort uses actual worker prepare/run-native CLI with new absolute entry',value['state']=='EXECUTION_CLOSED'and len(runcalls)==2 and all(x[0]==str(P(f.cfg['source_paths']['entry']))and x[-2:]==['--project','DTC_L1']for x in runcalls))
other='E2-DTCL2MLP-UNSELECTED-DH-P0-V1';ck('Nonselected exact previous worker delegate',frame.f_globals['worker'](other)['state']=='EXACT_OLD_WORKER_STANDIN'and oldcalls==[other])
q=f.q;prior=len(runcalls);q['consumed'][c]={'uuid':'PRIVATE_FAKE_ALREADY_CONSUMED'}
ck('Consumed identity preserved without a second worker invocation',frame.f_globals['worker'](c)['state']=='SPENT_ENGINEERING_PRESERVE'and len(runcalls)==prior)
del q['consumed'][c]
original=(root/'CONFIG.json').read_bytes();(root/'CONFIG.json').write_bytes(b'{')
ck('Selected invalid configuration is contained zero-start HOLD',frame.f_globals['worker'](c)['state']=='ZERO_START_ENGINEERING'and len(runcalls)==prior)
ck('Old nonselected worker remains usable during new config HOLD',frame.f_globals['worker'](other)['state']=='EXACT_OLD_WORKER_STANDIN')
(root/'CONFIG.json').write_bytes(original)
reject(lambda:producer.install_owner_dispatch(frame,root/'CONFIG.json',E.consumer_check));ck('Duplicate owner install rejects',hasattr(main,producer.OWNER_MARKER))
producer.restore_owner_dispatch();ck('Reverse owner restore returns exact prior callable and retains strict consumer',frame.f_globals['worker']is old_worker and consumer.safe_finish is getattr(main,E.MARKER)['wrapper'])
E.restore_in_owner(f.native.assert_parent_lease);ck('Then reverse consumer restore retains original callbacks',before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)and not hasattr(main,E.MARKER))
frame.f_locals['claims']={c:{'qualification_only':True}}
reject(lambda:producer.install_owner_dispatch(frame,root/'CONFIG.json',E.consumer_check));ck('Preexec claim rejects before dispatch mutation',frame.f_globals['worker']is old_worker)
del main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1
out=dict(status='PASS_PRIVATE_OWNER_CLOSURE_CPU_ONLY',count=len(checks),checks=checks,source_sha256={str(p):sha(p)for p in[D/'strace_entry.py',D/'qualify_owner_dispatch.py',P(f.cfg['source_paths']['consumer'])]},actual_ops_source_sha256=sha(ops.__file__),actual_consumer_source_sha256=sha(consumer.__file__),fixture_root=str(root),standins=['frame/owner lease/private authority','old existing worker globals resource loader and subprocess.run','original consumer load not invoked'],actual_E_installer_and_readiness_executed=True,actual_original_worker_code_executed=True,production_release_eligible=False,actual_model_starts=0,production_changes=0)
fmod.put(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json',out);print(json.dumps(dict(path=str(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json'),sha256=sha(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json'),status=out['status'],count=len(checks))))
