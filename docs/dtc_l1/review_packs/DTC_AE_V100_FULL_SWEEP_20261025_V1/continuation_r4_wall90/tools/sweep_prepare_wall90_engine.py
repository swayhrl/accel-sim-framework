import pathlib,json,hashlib,ast
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');oldpolicy=N/'DTC/src/owner-control/docs/dtc_l1/review_packs/DTC_AG8R1_FINITE_RESUME_20261021_V1/prepared_ag8r1/runtime_io_warning.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,text):ast.parse(text);p.write_text(text)
src=oldpolicy.read_text();assert src.count('21600')==3 and sha(oldpolicy)=='362fd84969b03f74c31e68001971a8b59893c3eae067f155260ebad0b736fdc2'
policy=T/'tools/runtime_policy_wall90_v1.py';assert not policy.exists();put(policy,src.replace('21600','7776000'))
guard=T/'tools/sweep_storage_guard_wall90_v1.py'
guard_source='''"""Independent future-start wall profile; original receiver and non-wall guards."""
import pathlib,sys,importlib.util,hashlib
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools')
import native_dtc_guard as original
from sweep_storage_guard import native_admission
p=T/'tools/runtime_policy_wall90_v1.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='POLICY_SHA'
s=importlib.util.spec_from_file_location('wall90_frozen_policy',p);wall=importlib.util.module_from_spec(s);s.loader.exec_module(wall)
class NativeDTCGuard(original.NativeDTCGuard):
 def __init__(self,channel,binding,output,started_ns):
  super().__init__(channel,binding,output,started_ns)
  self.policy=wall.RuntimePolicyB(self.policy.original.first,output,resource_module=original.resources,started_ns=started_ns,opt_in=True)
'''.replace('POLICY_SHA',sha(policy))
assert not guard.exists();put(guard,guard_source)
old=T/'tools/sweep_native.py';s=old.read_text();changes=[]
def replace(a,b,n=1):
 global s
 assert s.count(a)==n,(a,s.count(a));s=s.replace(a,b);changes.append(a[:120])
replace('from sweep_storage_guard import NativeDTCGuard','from sweep_storage_guard_wall90_v1 import NativeDTCGuard')
replace("q['controller_sha256']==sha(__file__)","operational_wall_profile(q)['engine_sha256']==sha(__file__)",2)
replace("'old_ledger_mutations':0,'output':str(out)","'old_ledger_mutations':0,'operational_resource_profile':prepared['operational_resource_profile'],'output':str(out)")
replace("'finite_native_launcher_sha256':sha(__file__)","'finite_native_launcher_sha256':sha(__file__),'operational_resource_profile':prepared['operational_resource_profile']")
replace("'request':REQUEST,'scientific_starts':0}","'request':REQUEST,'operational_resource_profile':operational_wall_profile(q),'scientific_starts':0}")
s+='''
def operational_wall_profile(q):
 profile=q.get('operational_engine_profiles',{}).get('WALL90_V1')
 require(isinstance(profile,dict) and profile.get('engine_sha256')==sha(__file__) and profile.get('wall_deadline_seconds')==7776000,'future wall profile not precisely registered')
 expected={'runtime_policy_wall90_v1.py','sweep_storage_guard_wall90_v1.py','sweep_native_wall90_v1.py','sweep_frontend_wall90_v1.py'}
 require({r['name'] for r in profile['source_pins']}==expected,'operational profile source membership changed')
 for row in profile['source_pins']:require(sha(ROOT/'tools'/row['name'])==row['sha256'],'operational wall source drift')
 require(profile['original_policy_sha256']=='362fd84969b03f74c31e68001971a8b59893c3eae067f155260ebad0b736fdc2' and profile['finite_budget']==356 and profile['model_retries']==0,'wall amendment outside frozen scope')
 return profile
'''
engine=T/'tools/sweep_native_wall90_v1.py';assert not engine.exists();put(engine,s)
frontsrc=(T/'tools/sweep_frontend.py').read_text().replace("T/'tools/sweep_native.py'","T/'tools/sweep_native_wall90_v1.py'")
front=T/'tools/sweep_frontend_wall90_v1.py';assert not front.exists();put(front,frontsrc)
proof={'status':'PREPARED_NOT_REGISTERED_OR_ACTIVE','profile':'WALL90_V1','wall_deadline_seconds':7776000,'original_policy_source':str(oldpolicy),'original_policy_sha256':sha(oldpolicy),'policy_delta':'Exact source replacement of the three21600wall tokens with7776000. No other policy byte changed. Actual monotonic clocks and every non-wall decision remain unchanged.','original_engine_source':str(old),'original_engine_sha256':sha(old),'engine_adaptation_sites':changes,'engine_sha256':sha(engine),'source_pins':[{'name':p.name,'sha256':sha(p)} for p in [policy,guard,engine,front]],'native_binary_configs_inputs_changed':False,'existing_models_or_authority_changed':False,'finite_budget':356,'model_retries':0}
with (T/'control/WALL90_PROFILE_CANDIDATE.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
