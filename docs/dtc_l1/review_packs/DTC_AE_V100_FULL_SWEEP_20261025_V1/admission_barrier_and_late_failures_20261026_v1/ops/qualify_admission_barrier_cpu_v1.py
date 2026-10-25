"""CPU-only actual main and original authority writer in an isolated fakeRoot."""
import ast,contextlib,copy,fcntl,hashlib,importlib.util,io,json,os,pathlib,sys,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');SRC=F/'ops/reconcile_r1_admission_barrier_v1.py';WRITER=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')
spec=importlib.util.spec_from_file_location('cpu_barrier',SRC);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);production_roots=(m.N,m.T,m.V)
W=P(tempfile.mkdtemp(prefix='ADMISSION_BARRIER_CPU_',dir=F/'control'));N=W/'native';T=W/'original';V=W/'validation';m.N=N;m.T=T;m.V=V
checks=[]
def check(name,fn):
 fn();checks.append(dict(name=name,status='PASS'))
def reject(name,fn):
 try:fn()
 except (RuntimeError,KeyError,AssertionError):checks.append(dict(name=name,status='PASS'));return
 raise RuntimeError('negative accepted: '+name)
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.json_bytes(x))
def fixture():
 q=dict(budget=23,remaining=0,consumed={f'R1-{i:02}':{'uuid':f'cpu-{i:02}','execution_receipt':{'keep':'unchanged'}} for i in range(23)},admitted_specs={},state='RUNNING',reserved_write_bytes=int(8.125*m.G),source_sha256='f'*64,orchestrator_sha256='e'*64)
 rows=[]
 for i,(c,r) in enumerate(q['consumed'].items()):
  sp=V/'control/specs'/(c+'.json');cp=V/'control'/('OPERATIONAL_OUTPUT_CAP_'+c+'.json');write(cp,dict(effective_result_cap_bytes=256*m.M));write(sp,dict(operational_output_cap_sha256=m.sha(cp),limits={'max_result_directory_bytes':256*m.M}));q['admitted_specs'][c]=m.sha(sp)
  out=V/'DTC/run/results'/r['uuid'];out.mkdir(parents=True,exist_ok=True);(out/'cpu.txt').write_text('CPU fixture only')
  if i<18:
   done=V/'control/qualification_ledger'/(c+'.DONE.json');ap=V/'control'/(c+'_ARCHIVE_RECEIPT.json');pp=V/'analysis/postprocess_v2'/(c+'.POSTPROCESS_V2.RESULT.json');proof=pp.with_name(c+'.PROOF.json');write(done,dict(cohort=c,uuid=r['uuid']));write(proof,dict(cohort=c,uuid=r['uuid']));receipt=dict(cohort=c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET');write(ap,receipt);write(pp,dict(cohort=c,uuid=r['uuid'],consumer_sha256=m.CONSUMER,DONE_path=str(done),DONE_sha256=m.sha(done),proof_path=str(proof),proof_sha256=m.sha(proof),model_starts=0,model_retries=0,registered_R14_result_preserved=True,state='PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE',archive={'receipt':receipt,'independently_verified_restored_entries':1}))
 oq=dict(budget=288,remaining=36,admitted_specs={'LIVE':'a','SPENT':'b','HISTORICAL_HOLD':'c','NEW-1':'d','NEW-2':'e'},consumed={'LIVE':{'uuid':'live-cpu','execution_receipt':None},'SPENT':{'uuid':'spent-cpu'}},sealed=['HISTORICAL_HOLD'],state='RUNNING',orchestrator_sha256='a'*64)
 reg=dict(registered_future_requests={m.ORIGINAL:oq,m.R1:q,'LEGACY_EP_NO_REMAINING':{'budget':50,'consumed':50,'state':'CLOSED','reserved_write_bytes':0}},new_scientific_budget_remaining=36,untouched={'history':[1,2,3]})
 write(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',reg);rb=(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes();write(N/'control/CURRENT_SCIENCE_EPOCH.json',dict(native_registry_sha256=m.digest(rb),new_budget_remaining=36,epoch=2));(N/'control/science_authority/REGISTRY_UPDATE.lock').touch();write(T/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={'LIVE':{'host_cpu':64}}));write(V/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={'R1-22':{'host_cpu':160}}));(T/'tools').mkdir(exist_ok=True);(T/'tools/sweep_native_cap1m.py').write_bytes(WRITER.read_bytes())
 return reg
reg=fixture();rb=(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes();eb=(N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes();rows=m.gather_rows(reg['registered_future_requests'][m.R1]);oc=m.claims(T);rc=m.claims(V)
def make(r=reg,o=oc,c=rc,a=rows):
 bb=m.json_bytes(r);return m.build_plan(r,dict(native_registry_sha256=m.digest(bb)),bb,eb,o,c,a)
p=make();q=reg['registered_future_requests'][m.R1]
check('18 independent archives plus 5 future writers gives exactly 3.5GiB',lambda: m.require(p['new_reserved_write_bytes']==int(3.5*m.G),'wrong bound'))
check('barrier covers only unconsumed eligible; preserves HOLD and live cohort',lambda:m.require(p['added_cells']==['NEW-1','NEW-2'] and p['original_sealed']==['HISTORICAL_HOLD'],'wrong eligibility'))
for field,value in [('remaining',1),('budget',24)]:
 r=copy.deepcopy(reg);r['registered_future_requests'][m.R1][field]=value;reject('R1 '+field+' mismatch rejects',lambda r=r:make(r))
r=copy.deepcopy(reg);r['registered_future_requests'][m.R1]['consumed'].pop('R1-22');reject('missing consumed identity rejects',lambda:make(r))
reject('unspent R1 claim rejects',lambda:make(c={'UNSPENT':{}}));reject('unspent original claim rejects',lambda:make(o={'NEW-1':{}}))
for field,value in [('closed',False),('model_live',True)]:
 rr=copy.deepcopy(rows);rr[0][field]=value;reject('archived '+field+' unsafe rejects',lambda rr=rr:make(a=rr))
rr=copy.deepcopy(rows)
for row in rr:
 if not row['archived_verified']:row['size_bytes']=row['cap_bytes']
check('all unarchived grow to output cap still covered',lambda:m.require(make(a=rr)['new_reserved_write_bytes']==p['new_reserved_write_bytes'],'growth uncovered'))
rr=copy.deepcopy(rows);rr[-1]['size_bytes']=513*m.M
check('ceil64MiB covers size+16MiB branch',lambda:m.require(make(a=rr)['new_reserved_write_bytes']==int(3.5625*m.G),'rounding wrong'))
modified=copy.deepcopy(reg);m.mutate(modified,p,'b'*64)
check('mutation whitelist preserves state budgets history sources and live consumed',lambda:m.require(modified['registered_future_requests'][m.R1]['state']==q['state'] and modified['registered_future_requests'][m.ORIGINAL]['consumed']==reg['registered_future_requests'][m.ORIGINAL]['consumed'] and modified['untouched']==reg['untouched'],'identity changed'))
check('legacy EP integer consumed row without remaining preserved exactly',lambda:m.require(modified['registered_future_requests']['LEGACY_EP_NO_REMAINING']==reg['registered_future_requests']['LEGACY_EP_NO_REMAINING'],'legacy row changed'))
reject('repeat apply rejects',lambda:m.mutate(modified,p,'b'*64))
drift=copy.deepcopy(reg);drift['registered_future_requests'][m.ORIGINAL]['consumed']['NEW-1']={'uuid':'changed'};reject('prefix changed rejects before mutation',lambda:m.mutate(drift,p,'b'*64))
released=copy.deepcopy(modified['registered_future_requests'][m.ORIGINAL]);bs=m.digest(m.canonical(released['operational_repair_admission_barrier']));m.release_barrier(released,bs,'c'*64,'cpu-publication')
check('R16 pure release restores exact prior HOLD and eligibility without budget change',lambda:m.require(released['sealed']==['HISTORICAL_HOLD'] and released['remaining']==36 and released['consumed']==reg['registered_future_requests'][m.ORIGINAL]['consumed'],'bad release'))
reject('repeat release rejects',lambda:m.release_barrier(released,m.digest(m.canonical(released['operational_repair_admission_barrier'])),'c'*64,'cpu-publication'))
reject('wrong barrier hash rejects',lambda:m.release_barrier(copy.deepcopy(modified['registered_future_requests'][m.ORIGINAL]),'0'*64,'c'*64,'cpu-publication'))
closed=copy.deepcopy(reg);closed['registered_future_requests'][m.R1].update(state='CLOSED_ALL_ARCHIVED',reserved_write_bytes=0);allclosed=copy.deepcopy(rows)
for row in allclosed:row.update(archived_verified=True,closed=True,model_live=False)
pc=make(closed,a=allclosed);mc=copy.deepcopy(closed);m.mutate(mc,pc,'d'*64)
check('already CLOSED consumer q byte-semantic unchanged; zero not raised to floor',lambda:m.require(mc['registered_future_requests'][m.R1]==closed['registered_future_requests'][m.R1],'CLOSED overwritten'))
reject('CLOSED with unarchived writers rejects',lambda:make(closed))
# Real independent receipt joins are validated by the source gatherer.
pp=V/'analysis/postprocess_v2/R1-00.POSTPROCESS_V2.RESULT.json';saved=pp.read_bytes();rr=m.read(pp);rr['uuid']='wrong';write(pp,rr);reject('V2 UUID mismatch rejects',lambda:m.gather_rows(q));pp.write_bytes(saved)
proof=V/'analysis/postprocess_v2/R1-00.PROOF.json';savedproof=proof.read_bytes();write(proof,{'uuid':'bad','cohort':'R1-00'});reject('proof SHA mismatch rejects',lambda:m.gather_rows(q));proof.write_bytes(savedproof)
# Execute the real original transaction implementation; globals point only at W.
tree=ast.parse(WRITER.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['update_authority','read_current_authority']]
ng=dict(NATIVE=N,REQUEST=m.ORIGINAL,read=m.read,sha=m.sha,require=m.require,now=m.now,P=P,fcntl=fcntl,json=json,os=os)
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(WRITER),'exec'),ng)
orig_spec=m.importlib.util.spec_from_file_location;orig_module=m.importlib.util.module_from_spec
class Loader:
 def create_module(self,spec):return None
 def exec_module(self,module):
  module.update_authority=ng['update_authority'];module.read_current_authority=ng['read_current_authority']
def patched_spec(name,path,*args,**kwargs):
 if name=='barrier_original_authority':return importlib.util.spec_from_loader(name,Loader())
 return orig_spec(name,path,*args,**kwargs)
m.importlib.util.spec_from_file_location=patched_spec
planpath=W/'PLAN.json';out=W/'ops';before_registry=(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes();before_epoch=(N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes();argv=sys.argv
def run(args):
 sys.argv=[str(SRC),*args]
 with contextlib.redirect_stdout(io.StringIO()):m.main()
try:
 run(['--plan',str(planpath),'--output-root',str(out)])
 check('actual main default leaves exact registry and epoch bytes unchanged',lambda:m.require((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes()==before_registry and (N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes()==before_epoch,'default mutation'))
 run(['--apply','--plan',str(planpath),'--output-root',str(out)])
 after=m.read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');epoch=m.read(N/'control/CURRENT_SCIENCE_EPOCH.json');dest=out/m.sha(planpath)
 check('actual main apply + original writer registry/epoch atomic replace and SHA readback',lambda:m.require(epoch['native_registry_sha256']==m.sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json') and after['registered_future_requests'][m.R1]['reserved_write_bytes']==int(3.5*m.G),'transaction wrong'))
 check('exact registry epoch q preimages saved before mutation',lambda:m.require((dest/'registry.before.json').read_bytes()==before_registry and (dest/'epoch.before.json').read_bytes()==before_epoch and (dest/'original_q.before.json').read_bytes()==m.q_span(before_registry,m.ORIGINAL) and (dest/'r1_q.before.json').read_bytes()==m.q_span(before_registry,m.R1),'preimage mismatch'))
 check('global budget and scientific histories unchanged across real writer',lambda:m.require(after['new_scientific_budget_remaining']==36 and epoch['new_budget_remaining']==36 and after['untouched']==reg['untouched'],'budget changed'))
 reject('actual main repeat apply rejects without changing committed authority',lambda:run(['--apply','--plan',str(planpath),'--output-root',str(out)]))
finally:sys.argv=argv;m.importlib.util.spec_from_file_location=orig_spec
# Pure transformation of a shared-locked live snapshot: no writer is invoked.
m.N,m.T,m.V=production_roots
with (m.N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as shared:
 fcntl.flock(shared,fcntl.LOCK_SH);real,realplan,realrb,realeb=m.locked_snapshot();pure=copy.deepcopy(real);m.mutate(pure,realplan,'0'*64)
 check('actual production registry shape pure dry mutation; exact authority bytes remain unchanged',lambda:m.require((m.N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes()==realrb and (m.N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes()==realeb,'readonly changed authority'))
report=dict(schema='ADMISSION_BARRIER_AND_R1_RECONCILIATION_CPU_QUALIFICATION_V1',status='PASS',utc=m.now(),source_path=str(SRC),source_sha256=m.sha(SRC),driver_path=str(P(__file__)),driver_sha256=m.sha(__file__),original_authority_writer_path=str(WRITER),original_authority_writer_sha256=m.sha(WRITER),fixture_root=str(W),checks=checks,check_count=len(checks),actual_main_scenarios=['default readonly exactbytes','apply using actual original update_authority AST function and fakeRoot','repeat rejection'],limitations=['Registry and epoch replacements follow original sequential fsync/hash protocol, not a cross-file atomic transaction; interrupted pair stays fail-closed.','Claims are checked twice under registry EX; the old dispatcher writes its claim sidecar separately. A racing unconsumed attempt is rejected by native sealed check before scientific consume; no claim or model is fabricated.','No actual production apply, register, model start, signal, entry edit or ledger edit.'],real_authority_writes=0,real_model_starts=0,signals=0)
target=F/'ops/ADMISSION_BARRIER_AND_R1_RECONCILIATION_CPU_QUALIFICATION_V1.json';write(target,report);print(json.dumps(dict(status='PASS',checks=len(checks),result=str(target),sha256=m.sha(target),source_sha256=m.sha(SRC),fixture_root=str(W))))
