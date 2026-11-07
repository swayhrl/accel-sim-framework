from pathlib import Path
import hashlib,importlib.util,json,subprocess,time,types
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/D_independent_review_v1/unified_publication_commit_timeout_source_review_v2/cpu_replay');old=A/'agents/M_unified_publication_proposal_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v1=load(old/'unified_watch_publish_source_proposal.py','CPU_V1').source_module()
v2=load(O/'unified_watch_publish_source_proposal.py','CPU_V2').source_module()
tests=[]
def check(n,x):assert x,n;tests.append({'name':n,'pass':True})
def semantics(c):
 return (c.co_code,tuple(semantics(x)if isinstance(x,types.CodeType)else x for x in c.co_consts),c.co_names,c.co_varnames,c.co_freevars,c.co_cellvars)
check('bridge_identical',sha(old/'unified_consumer_publisher_bridge.py')==sha(O/'unified_consumer_publisher_bridge.py'))
calls=[]
def fake(argv,**kw):
 calls.append({'args':argv,'timeout':kw['timeout']})
 return types.SimpleNamespace(returncode=0,stdout=b'CPU_NO_GIT',stderr=b'')
g=v2.GitPublication.__new__(v2.GitPublication);g.runner=fake;g.prefix=['CPU_NOT_EXECUTABLE'];g.env={}
for arg in [('commit','-m','CPU'),('read-tree','HEAD'),('add','x'),('push','origin'),('ls-remote','origin'),('fetch','origin'),('show','HEAD:MANIFEST')]:
 g.run(arg);check('timeout_'+arg[0],calls[-1]['timeout']==(300 if arg[0]=='commit' else 60))
def timeout(argv,**kw):raise subprocess.TimeoutExpired(argv,kw['timeout'])
g.runner=timeout
try:g.run(['commit','-m','CPU'])
except subprocess.TimeoutExpired as e:check('commit_timeout_propagates_failclosed_no_retry',e.timeout==300)
else:raise AssertionError('timeout swallowed')
def bad(argv,**kw):return types.SimpleNamespace(returncode=1,stdout=b'',stderr=b'CPU_NEGATIVE')
g.runner=bad
try:g.run(['commit','-m','CPU'])
except ValueError:tests.append({'name':'nonzero_return_remains_failclosed','pass':True})
else:raise AssertionError('failed Git accepted')
for name in ['cycle','due','build_payload','publication_view','normalize_report','exclusive','main']:
 a,b=getattr(v1,name),getattr(v2,name)
 check('unchanged_runtime_function_'+name,semantics(a.__code__)==semantics(b.__code__))
for name in ['commit_snapshot','validate_head','remote_sha','__init__']:
 a,b=getattr(v1.GitPublication,name),getattr(v2.GitPublication,name)
 check('unchanged_Git_transaction_'+name,semantics(a.__code__)==semantics(b.__code__))
observed=A/'control/publication_unified_v1/background_state/LAST_WATCH_ERROR.json'
if observed.exists():
 (O/'OBSERVED_LAST_WATCH_ERROR.data_only.json').write_bytes(observed.read_bytes())
 evidence={'path':str(observed),'sha256':sha(observed),'note':'Read-only observation; not a HEAD/remote outcome proof.'}
else:evidence=None
report={'status':'PASS_COMMIT_TIMEOUT_ONLY_CPU','cases':len(tests),'tests':tests,'actual_Git_commands':0,'actual_process_control':0,'publisher_started':False,'models_started':0,'registrations':0,'incident_observation':evidence}
(O/'CPU_QUALIFICATION.fixed.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
files=sorted(p for p in O.iterdir()if p.is_file()and p.name!='MANIFEST.fixed.json')
mf={'schema':'DTC_UNIFIED_PUBLISHER_COMMIT_TIMEOUT_ONLY_V2','created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'running_source_changed':False,'actual_Git_commands':0,'members':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in files]}
p=O/'MANIFEST.fixed.json';p.write_text(json.dumps(mf,sort_keys=True,indent=2)+'\n')
print(json.dumps({'cases':len(tests),'manifest_sha256':sha(p),'source_sha256':sha(O/'unified_watch_publish_source_proposal.py'),'members':len(files)}))
