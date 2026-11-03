"""Exercise actual frontend's immutable checks; delegate stubs cannot launch/accept."""
from pathlib import Path
import sys,json,hashlib,types,os,copy,uuid
A=Path(__file__).resolve().parent;R=A/'qualified_runtime';sys.path.insert(0,str(R))
import ep_perf_frontend as f
T=A/'TEST_ONLY_FRONTEND'/str(uuid.uuid4());T.mkdir(parents=True)
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
scope=json.loads((R/'FAMILY_SCOPE.json').read_text());q=dict(admitted_specs={});reg=dict(registered_future_requests={f.GOAL:q});f.ROOT=T;f.authority=lambda:(reg,{})
for r in scope['points']:
 p=T/'cases'/r['id']/'control/FROZEN_SPEC.json';p.parent.mkdir(parents=True)
 p.write_text(json.dumps(dict(TEST_ONLY=True,host_engine_ref=ref(R/'ep_perf_native_wv_modes_draft.py'),postprocess_module_ref=ref(R/'ep_perf_postprocess.py'))));q['admitted_specs'][r['id']]=ref(p)['sha256']
def delegate(item,name):
 assert Path(item['path']).is_relative_to(R) and ref(item['path'])['sha256']==item['sha256']
 return types.SimpleNamespace(main=lambda args:dict(TEST_ONLY=True,delegate='ENGINE',args=args,no_science_start=True),postprocess=lambda case:dict(TEST_ONLY=True,delegate='POSTPROCESS',case=case,no_acceptance_write=True))
f.module=delegate
rows=[]
def check(name,fn,reject=False):
 try:v=fn();ok=not reject;err=None
 except Exception as e:v=None;err=repr(e);ok=reject
 rows.append(dict(label=name,PASS=ok,error=err,result=v))
 assert ok,rows[-1]
 return v
old=os.environ.pop('EP_FULL_PERF_NATIVE_ENTRY',None)
case=scope['points'][0]['id'];check('missing_native_env_guard',lambda:f.main(['experiment','prepare',case,'--project','EP_L2']),True)
os.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'
for r in scope['points']:
 for op in ['prepare','inspect','accept']:
  v=check(r['id']+'_'+op+'_actual_frontend_route',lambda r=r,op=op:f.main(['experiment',op,r['id'],'--project','EP_L2']))
  check(r['id']+'_'+op+'_correct_delegate_no_actor',lambda v=v,op=op:f.need(v['delegate']==('POSTPROCESS'if op=='accept'else'ENGINE')and v['TEST_ONLY'],'bad leaf'))
for label,args in [('oldDRAM16',['experiment','prepare','EP_PERF_PF_DRAM_FWT_S_1020_V1','--project','EP_L2']),('unknown',['experiment','prepare','EP_PERF_UNKNOWN','--project','EP_L2']),('wrong_project',['experiment','prepare',case,'--project','DTC']),('bad_verb',['experiment','prepare-bypass',case,'--project','EP_L2']),('extraarg',['experiment','prepare',case,'--project','EP_L2','EXTRA'])]:
 check(label,lambda args=args:f.main(args),True)
saved=q['admitted_specs'].pop(case);check('unregistered_exact_case',lambda:f.main(['experiment','prepare',case,'--project','EP_L2']),True);q['admitted_specs'][case]=saved
path=T/'cases'/case/'control/FROZEN_SPEC.json';original=path.read_bytes();path.write_bytes(original+b' ');check('registered_spec_drift',lambda:f.main(['experiment','prepare',case,'--project','EP_L2']),True);path.write_bytes(original)
spec=json.loads(original);spec['host_engine_ref']['sha256']='0'*64;path.write_text(json.dumps(spec));q['admitted_specs'][case]=ref(path)['sha256'];check('engine_byte_drift',lambda:f.main(['experiment','inspect',case,'--project','EP_L2']),True)
foreign=T/'TEST_ONLY_FOREIGN_ENGINE.py';foreign.write_bytes((R/'ep_perf_native_wv_modes_draft.py').read_bytes());spec['host_engine_ref']=ref(foreign);path.write_text(json.dumps(spec));q['admitted_specs'][case]=ref(path)['sha256'];check('engine_outside_qualified_runtime',lambda:f.main(['experiment','prepare',case,'--project','EP_L2']),True)
path.write_bytes(original);q['admitted_specs'][case]=saved
if old is None:os.environ.pop('EP_FULL_PERF_NATIVE_ENTRY',None)
else:os.environ['EP_FULL_PERF_NATIVE_ENTRY']=old
receipt=dict(schema='EP_SYSTEM850_ACTUAL_FRONTEND_EXACT12_ROUTING_CPU_V1',status='PASS_ACTUAL_ROUTER_WITH_HASH_CHECKED_CPU_DELEGATES_NOT_NATIVE_OR_SCIENCE',controls=rows,total=len(rows),passed=sum(z['PASS']for z in rows),frontend_ref=ref(R/'ep_perf_frontend.py'),scope='Actual nativeguard/cohort/registeredSpecSHA/engine path+SHA code; downstream engine/postprocessor leaf delegates are CPU stubs and do not prepareTrace/launch/accept. Realengine+wholeterminal tested independently in102-control regression.',new_model_starts=0,real_ledger_writes=0,real_native_writes=0)
(A/'FRONTEND_EXACT12_ROUTING_CPU_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows),'actualfrontend route/check controls')
