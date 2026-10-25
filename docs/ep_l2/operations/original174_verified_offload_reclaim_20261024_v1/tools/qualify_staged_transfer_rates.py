"""Rate-only directed qualification in task-owned synthetic control files."""
from local_common import *

CODE=r'''
import pathlib,sys,json,hashlib,ast,importlib.util,time,tempfile
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');Q=T/'qualification/staged_transfer_rates_v1'
sys.path.insert(0,str(T/'tools'));sys.path.insert(0,str(Q))
spec=importlib.util.spec_from_file_location('qualified_rate_engine',Q/'copy_engine.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
auth=(Q/'TRANSFER_RATE_USER_AUTHORIZATION.json').read_bytes();assert hashlib.sha256(auth).hexdigest()==c.RATE_AUTH_SHA256
checks={}
with tempfile.TemporaryDirectory(prefix='rate_qualification_',dir=Q) as tmp:
 c.TASK=P(tmp);d=c.TASK/'control';d.mkdir();policy=d/'TRANSFER_RATE_POLICY.json';ap=d/'TRANSFER_RATE_USER_AUTHORIZATION.json'
 def get():c._rate_cache=None;return c.rate_limits(force=True)
 def tier(s,t):policy.write_bytes(c.canon(dict(schema='LANE_T2_ACTIVE_TRANSFER_RATE_TIER_V1',authorization_sha256=c.RATE_AUTH_SHA256,source_MiB_per_second=s,total_MiB_per_second=t)))
 def reject(name,fn):
  try:fn()
  except (RuntimeError,ValueError,KeyError):checks[name]='PASS'
  else:raise AssertionError(name+' did not fail closed')
 x=get();assert (x['source_MiB_per_second'],x['total_MiB_per_second'])==(15,30);checks['no_policy_preserves_original_limits']='PASS'
 tier(30,60);reject('missing_authorization_rejected',get)
 ap.write_bytes(auth+b' ');reject('changed_authorization_rejected',get);ap.write_bytes(auth)
 for s,t in [(30,60),(60,120),(15,30)]:
  tier(s,t);x=get();assert (x['source_MiB_per_second'],x['total_MiB_per_second'])==(s,t);checks['authorized_tier_%d_%d'%(s,t)]='PASS'
 for s,t in [(61,122),(30,120),(True,30),(0,0)]:
  tier(s,t);reject('invalid_tier_%s_%s'%(s,t),get)
 tier(30,60);p=json.loads(policy.read_bytes());p['authorization_sha256']='0'*64;policy.write_bytes(c.canon(p));reject('changed_policy_identity_rejected',get)
 tier(30,60);get();sleeps=[];real_sleep=c.time.sleep;c.time.sleep=sleeps.append
 try:
  c.pace_bytes(c.MIB,c.payload_rate);assert sleeps[-1]==1/30
  c.pace_bytes(c.MIB,c.io_rate);assert sleeps[-1]==1/60
  tier(60,120);get();c.pace_bytes(c.MIB,c.payload_rate);assert sleeps[-1]==1/60
  c.pace_bytes(c.MIB,c.io_rate);assert sleeps[-1]==1/120
  checks['live_tier_reloads_without_restart_or_catchup_burst']='PASS'
  fixture=P(tmp)/'fixture';body=b'qualified-rate-control-fixture\n'*128;fixture.write_bytes(body);gate=[]
  assert c.hash_file(fixture,gate=lambda:gate.append(True))==hashlib.sha256(body).hexdigest() and gate
  assert sleeps[-1]==len(body)/(120*c.MIB);checks['real_hash_bytes_and_resource_callback_preserved']='PASS'
  class Active:
   def poll(self):return None
  c.ACTIVE_SENDER=Active();c.hash_file(fixture);assert sleeps[-1]==len(body)/(60*c.MIB);checks['hash_concurrent_sender_uses_half_aggregate_budget']='PASS'
  c.ACTIVE_SENDER=None
 finally:c.time.sleep=real_sleep
before=(Q/'BEFORE_copy_engine.py').read_text();after=(Q/'copy_engine.py').read_text()
bt=ast.parse(before);at=ast.parse(after)
added={'rate_limits','payload_rate','io_rate','pace_bytes'}
def functions(tree):
 return [(n.name,ast.dump(n,include_attributes=False)) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name not in added]
b=functions(bt);a=functions(at);assert [x[0] for x in a]==[x[0] for x in b]
changed=[(i,n) for i,((n,x),(_,y)) in enumerate(zip(b,a)) if x!=y]
assert [n for i,n in changed]==['hash_file','migrate','Resources','hash_file','prepare_source','source_send'],changed
checks['only_six_expected_rate_implementation_bodies_changed']='PASS'
for n in ['verify_tree','verify_committed','restore_native','source_gate','check_source_role','normalize_frozen','source_boot','publish_bytes','identity','same_source','safe','v9']:
 assert [v for name,v in a if name==n]==[v for name,v in b if name==n]
checks['all_identity_SHA_COMMIT_reader_resource_and_restore_guards_unchanged']='PASS'
assert (T/'tools/server_resources.py').read_bytes()==(Q/'BEFORE_server_resources.py').read_bytes()
assert (T/'tools/continuation_supervisor.py').read_bytes()==(Q/'BEFORE_continuation_supervisor.py').read_bytes()
checks['resource_contract_and_supervisor_code_unchanged']='PASS'
before_driver=(Q/'BEFORE_offload_driver.py').read_text();after_driver=(Q/'offload_driver.py').read_text()
assert before_driver.replace("current_host_io=x['IO']);return x", "current_host_io=x['IO'],archive_transfer_rate_policy=x.get('archive_transfer_rate_policy'));return x")==after_driver
checks['driver_change_is_rate_telemetry_only']='PASS'
x=dict(schema='LANE_T2_STAGED_TRANSFER_RATE_QUALIFICATION_V1',unix=time.time(),checks=checks,authorization_sha256=c.RATE_AUTH_SHA256,staged_sha256={n:hashlib.sha256((Q/n).read_bytes()).hexdigest() for n in ['copy_engine.py','offload_driver.py']},payload_fixture_bytes=len(body),scientific_data_reads=0,scientific_starts_or_signals=0)
(Q/'QUALIFICATION.json').write_bytes(c.canon(x));print(json.dumps(x))
'''

if __name__=='__main__':
    q='qualification/staged_transfer_rates_v1/'
    for n in ['copy_engine.py','offload_driver.py','server_resources.py','continuation_supervisor.py']:
        raw=remote('hrl-174-new',"import pathlib,json,base64\np=pathlib.Path("+repr(NATIVE+'/tools/'+n)+");print(json.dumps({'base64':base64.b64encode(p.read_bytes()).decode()}))")
        install(q+'BEFORE_'+n,base64.b64decode(raw['base64']))
    for n in ['copy_engine.py','offload_driver.py']:
        install(q+n,(R/'tools'/n).read_bytes())
    install(q+'TRANSFER_RATE_USER_AUTHORIZATION.json',(R/'t2/TRANSFER_RATE_USER_AUTHORIZATION.json').read_bytes())
    x=remote('hrl-174-new',CODE,90);save('t2/rate_transition/QUALIFICATION.json',x)
    print(json.dumps(x))
