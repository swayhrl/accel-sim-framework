"""Five targeted real-flock checks, CPU/files only, no production transaction."""
import pathlib,json,hashlib,copy,types,tempfile,fcntl,ast,importlib.util,os
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/bpf_memory_scope_transaction_v2';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
new=load('scope_v2',D/'scope_transaction.py');oldpath=A/'agents/A/bpf_memory_scope_transaction_v1/scope_transaction.py';old=load('frozen46b',oldpath);assert sha(oldpath)=='46b6a805dc5e2e7ef9afee1222ff2ae8764fc49512caafc4d7811f0929123c3f'
bp=A/'coordinator/bpf_canary_orchestration_v2/scope_bridge.py';bridge=load('main2a82',bp);plan=read(A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json');scope=bridge.CanaryScope(plan)
root=P(tempfile.mkdtemp(prefix='REAL_FLOCK_PRIVATE_',dir=D));q=copy.deepcopy(read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'])
for n in ['MATRIX_CURRENT.json','SCOPE.json']:put(root/'control'/n,read(R/'control'/n))
put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}});exact=[]
for c in scope.rows:
 source=R/'control/specs'/(c+'.json');s=read(source);h=sha(source);assert s['host_cpu']is None and q['admitted_specs'][c]==h
 for p in [root/'control/specs'/(c+'.json'),root/'control'/(c+'_SPEC.json')]:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read_bytes())
 exact.append(scope.validate(c,s,h,q))
oldrecord=copy.deepcopy(q['additional_operational_overlays']['CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V2']);newrecord=copy.deepcopy(oldrecord);newrecord['allowed_cohorts']+=sorted(scope.rows)
tx=dict(request=q['request'],added_cohorts=sorted(scope.rows),exact_registered_cohorts=exact,old_record=oldrecord,new_record=newrecord)
lockpath=root/'PRIVATE_REGISTRY_UPDATE.lock';calls=[]
def reentrant_authority(*args):
 calls.append('ATTEMPTED_SEPARATE_FD_SHARED_LOCK')
 with lockpath.open('a+b')as fd:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB)
 raise AssertionError('Expected EWOULDBLOCK under held EX')
engine=types.SimpleNamespace(canonical=reentrant_authority,registered=reentrant_authority,authority=reentrant_authority,assert_parent_lease=reentrant_authority)
a=object.__new__(new.ScopeTransaction);a.root=root;a.scope=scope;a.engine=engine;a.lib=types.SimpleNamespace(ID='CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V2')
before=copy.deepcopy(q);checks=[]
def check(n,v):assert v,n;checks.append(dict(name=n,status='PASS'))
def refuses(fn):
 try:fn()
 except Exception:return True
 return False
with lockpath.open('a+b')as held:
 fcntl.flock(held,fcntl.LOCK_EX)
 # The old exact call path attempts canonical->authority under a second FD.
 try:old.ScopeTransaction.evidence(a,q,tx,True);blocked=False
 except BlockingIOError:blocked=True
 check('old46b_canonical_reentry_real_secondFD_SH_NB_rejected_without_hang',blocked and len(calls)==1)
 calls.clear();a.locked_evidence(q,tx)
 check('new_locked_validation_passes_with_real_EX_and_zero_engine_calls',calls==[]and q==before)
 tree=ast.parse(P(new.__file__).read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='ScopeTransaction');apply=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='apply');nested=next(x for x in ast.walk(apply)if isinstance(x,ast.FunctionDef)and x.name=='mutate')
 ns={'self':a,'tx':tx,'copy':copy};exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(nested)],type_ignores=[])),str(new.__file__),'exec'),ns)
 reg={'registered_future_requests':{q['request']:copy.deepcopy(q)}};reg['registered_future_requests'][q['request']]['benign_other_receipt']={'uuid':'PRIVATE_RECEIPT'};expected=copy.deepcopy(reg);expected['registered_future_requests'][q['request']]['additional_operational_overlays']['CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V2']=newrecord
 ns['mutate'](reg)
 check('actual_extracted_mutate_body_under_real_EX_only_CPU2row_changes_no_authority_read',reg==expected and calls==[])
 alias=root/'control'/(next(iter(scope.rows))+'_SPEC.json');prior=alias.read_bytes();alias.write_bytes(b'{}\n');badreg={'registered_future_requests':{q['request']:copy.deepcopy(q)}};pre=copy.deepcopy(badreg)
 check('alias_drift_fail_before_row_mutation_under_EX',refuses(lambda:ns['mutate'](badreg))and badreg==pre and calls==[]);alias.write_bytes(prior)
 badreg={'registered_future_requests':{q['request']:copy.deepcopy(q)}};badreg['registered_future_requests'][q['request']]['consumed'][next(iter(scope.rows))]={'uuid':'PRIVATE_NEW_SPENT'};badreg['registered_future_requests'][q['request']]['remaining']-=1;pre=copy.deepcopy(badreg)
 check('current_locked_q_spent_rejected_before_mutation_preserves_grants',refuses(lambda:ns['mutate'](badreg))and badreg==pre and calls==[])
proof=dict(schema='BPF_MEMORY_SCOPE_V2_REAL_FLOCK_DELTA_CPU_QUALIFICATION',status='PASS',checks=checks,source_sha256=sha(new.__file__),old_source_sha256=sha(oldpath),driver_sha256=sha(__file__),scope_bridge_sha256=sha(bp),fixture_path=str(root),actual_flock=True,old_hang_reproduced_as_nonblocking_EWOULDBLOCK=True,production_lock_used=False,source_role='actual V2 nested mutate AST body extracted and executed; no full25suite repeat, no production apply',production_mutations=0,models_started=0,new_grants=0)
put(D/'CPU_LOCK_DELTA_QUALIFICATION.json',proof)
print(json.dumps(dict(source_sha256=sha(new.__file__),QA_sha256=sha(D/'CPU_LOCK_DELTA_QUALIFICATION.json'),checks=len(checks),path=str(D))))
