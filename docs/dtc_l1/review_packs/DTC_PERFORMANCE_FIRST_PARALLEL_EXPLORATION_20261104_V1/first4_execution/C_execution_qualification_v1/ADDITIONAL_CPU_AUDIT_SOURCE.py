import pathlib,json,hashlib,sys,types,os,copy,ast,fcntl,datetime,gzip
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'C_first4_execution_qualification_v1';R=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1');F=O/'private_fixtures';checks=[]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rd(p):return json.loads(P(p).read_bytes())
def write(p,v):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def check(n,v):assert v,n;checks.append(dict(name=n,PASS=True))
def reject(n,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError):check(n,True);return
 raise AssertionError(n)
def load(n,p):m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
ops=load('C_ops_cpu_extra',R/'tools/perf4_ops.py');ops.R=F/'ops';co='CPU_ONLY_NOT_SCIENCE';out=ops.R/'DTC/run/results/CPU_ONLY_UUID';out.mkdir(parents=True,exist_ok=True);mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';tick=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);write(mp,dict(pid=os.getpid(),start_ticks=tick));e=types.SimpleNamespace(registered=lambda:(None,None,dict(consumed={co:dict(uuid='CPU_ONLY_UUID')})),binding=lambda:dict(runtime_guard_sha256='source-pin'))
check('PID_generation_exact',ops.native_live(mp));write(mp,dict(pid=os.getpid(),start_ticks=tick+1));check('PID_generation_drift_rejected',not ops.native_live(mp));write(mp,dict(pid=os.getpid(),start_ticks=tick))
for name,decision,pin,expect in [('continue','CONTINUE','source-pin',True),('stop','STOP','source-pin',False),('guarddrift','CONTINUE','other',False)]:
 (out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(gzip.compress((json.dumps(dict(DTC_exact_original_policy=dict(decision=dict(decision=decision),runtime_policy_binding=dict(guard_sha256=pin))))+'\n').encode()));check('actual_runtime_guard_'+name,ops.actual_runtime_witness(co,e)==expect)
(out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(b'notgzip');check('badgzip_runtime_not_qualified',not ops.actual_runtime_witness(co,e));write(mp,dict(pid=999999999,start_ticks=1));check('absent_PID_not_live',not ops.native_live(mp));check('nonlive_unaccepted_not_runtime_qualified',not ops.actual_runtime_witness(co,e));write(ops.R/'analysis'/(co+'.RESULT.json'),dict(state='PASS_PERFFIRST4_DH_STRICT_ARCHIVE_NATIVE_RESTORE'));check('strict_accepted_closed_runtime_alternative',ops.actual_runtime_witness(co,e))
# Execute production registry update function only against a private synthetic filesystem root.
fn=next(n for n in ast.parse((R/'tools/perf4_native.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='update_authority');V=F/'synthetic_registry';rp=V/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=V/'control/CURRENT_SCIENCE_EPOCH.json';(rp.parent/'request_history').mkdir(parents=True,exist_ok=True)
request='CPU_PRIVATE_ONLY';base=dict(registered_future_requests={'PEER':dict(budget=3,remaining=0,consumed={'old':dict(uuid='immutable')})},old_source_history={'H':['unchanged']},qualification_history={'Q':['unchanged']});write(rp,base);write(ep,dict(epoch=2,native_registry_sha256=sha(rp)));ns=dict(N=V,REQ=request,read=rd,sha=sha,copy=copy,fcntl=fcntl,os=os,json=json,datetime=datetime);exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_production_update_CPU_fixture','exec'),ns)
ns['update_authority'](lambda reg:reg['registered_future_requests'].update({request:dict(budget=4,remaining=4,consumed={})}));fresh=rd(rp);check('production_atomic_add_preserves_old_peers',fresh['registered_future_requests']['PEER']==base['registered_future_requests']['PEER']);check('production_atomic_histories_unchanged',fresh['old_source_history']==base['old_source_history']and fresh['qualification_history']==base['qualification_history']);check('production_epoch_hash_matches',rd(ep)['native_registry_sha256']==sha(rp));check('synthetic_budget4_new_not_old',fresh['registered_future_requests'][request]['remaining']==4 and fresh['new_scientific_budget_remaining']==4)
prior=sha(rp);reject('production_rejects_peer_budget_mutation',lambda:ns['update_authority'](lambda reg:reg['registered_future_requests']['PEER'].update(budget=4)));check('rejected_peer_mutation_not_committed',sha(rp)==prior);reject('production_rejects_history_mutation',lambda:ns['update_authority'](lambda reg:reg['old_source_history'].update(H=['different'])));check('rejected_history_mutation_not_committed',sha(rp)==prior)
actual=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');now=rd(actual);old=rd(O/'OLD_IDENTITIES_PRE_REGISTRATION.json');check('real_old_identities_exactly_preserved_by_audit',{k:dict(budget=v.get('budget'),remaining=v.get('remaining'),consumed=v.get('consumed'))for k,v in now['registered_future_requests'].items()}==old)
check('actual_REQ_remains_absent','DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'not in now['registered_future_requests'])
write(O/'ADDITIONAL_OWNER_AND_ATOMIC_CPU_CHECKS.json',dict(status='PASS',count=len(checks),checks=checks,all_registry_writes_synthetic_private_fixture_only=True,no_modelentry=True))
basechecks=rd(O/'CPU_CHECKS.json')
for c in basechecks['checks']:c['name']=c['name'].replace('actual_all270_options:','explicit_config_options_match270_contract:')
write(O/'CPU_CHECKS.json',basechecks)
report=rd(O/'FINAL_CPU_QUALIFICATION.json');report['count']=basechecks['count']+len(checks);report['evidence']['CPU_CHECKS.json']['sha256']=sha(O/'CPU_CHECKS.json');report['evidence']['ADDITIONAL_OWNER_AND_ATOMIC_CPU_CHECKS.json']=dict(path=str(O/'ADDITIONAL_OWNER_AND_ATOMIC_CPU_CHECKS.json'),sha256=sha(O/'ADDITIONAL_OWNER_AND_ATOMIC_CPU_CHECKS.json'));write(O/'FINAL_CPU_QUALIFICATION.json',report)
print('FINAL',report['count'],sha(O/'FINAL_CPU_QUALIFICATION.json'))
