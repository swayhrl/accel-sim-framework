import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,copy,ast
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
B=A/'agents/B/cpu_spare_policy_review_v2';B.mkdir(exist_ok=True)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
paths=dict(library=A/'agents/A/cpu_spare_memory_v2/cpu_memory.py',owner=A/'agents/E/cpu_spare_execution_v2/cpu_owner.py',extra_strict=A/'agents/E/cpu_spare_execution_v2/cpu_extra_strict.py')
pins={k:sha(v)for k,v in paths.items()}
lib=load('b_independent_cpu2_library',paths['library']);owner=load('b_independent_cpu2_owner',paths['owner'])
eq=read(A/'agents/E/cpu_spare_execution_v2/EXTRA_CPU_QUALIFICATION.json');oq=read(A/'agents/E/cpu_spare_execution_v2/OWNER_CPU_QUALIFICATION.json')
assert eq['library_sha256']==pins['library']and eq['owner_sha256']==pins['owner']and eq['extra_sha256']==pins['extra_strict']
assert all(oq['sources'][str(p)]==pins[k]for k,p in paths.items())
root=P(eq['fixture_root']);snap=read(root/'out/CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json');cfg=snap['config']
q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ]
checks=[]
def ck(name,body):
 body();checks.append(dict(name=name,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected fail-closed rejection')
def scope():
 c=cfg['allowed_cohorts'][-1];qq=dict(admitted_specs={c:'x'},consumed={},sealed=[])
 assert lib.eligible_cohort(cfg,qq,c,'NATIVE')
 assert not lib.eligible_cohort(cfg,qq,c+'FOREIGN','NATIVE')
 assert not lib.eligible_cohort(cfg,dict(qq,admitted_specs={}),c,'NATIVE')
 assert not lib.eligible_cohort(cfg,dict(qq,consumed={c:{}}),c,'NATIVE')
 assert not lib.eligible_cohort(cfg,dict(qq,sealed=[c]),c,'NATIVE')
 assert not lib.eligible_cohort(cfg,qq,c,'OWNER_CHOOSE',{c:{}})
ck('single allowlist and admitted/unspent/unsealed/unclaimed stage gates',scope)
approval=R/'control/operational_amendments/cpu_spare_memory_v1/ACTUAL_CPU_CANARY_ROLLOUT_QUALIFICATION.json'
def realapproval():
 cc=copy.deepcopy(cfg);cc.pop('qualification_only',None);cc['canary_qualification_path']=str(approval);cc['canary_qualification_sha256']=sha(approval)
 receipt=lib.canary_qualification(cc,q)
 assert receipt['status']=='PASS_CPU_SPARE_CANARY_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE'
 assert sha(approval)=='7438a6ec070eedd08f41bc31f038377d1b90d1ad854f084f02e04b6aa7ba5136'
 reject(lambda:lib.canary_qualification(dict(cc,canary_qualification_sha256='0'*64),q))
 reject(lambda:lib.canary_qualification(cfg,q))
ck('real immutable natural approval SHA and q receipt; CPU stand-in cannot authorize actual q',realapproval)
def lineage():
 qq=copy.deepcopy(q);qq['qualification_only']=True
 for c in cfg['allowed_cohorts']:qq['admitted_specs'].setdefault(c,'CPU2_FIXTURE_SPEC')
 oldc=cfg['previous_cpu_v1_config']['cpu_exception_scope']['allowed_cohorts'][0]
 gate=read(cfg['canary_qualification_path']);qq['consumed'][oldc]=dict(uuid=gate['uuid'],execution_receipt=dict(launcher_wait_returncode=0,stop_reason=None,CPU_fixture_only=True))
 qq['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE')
 lib.validate(cfg,qq)
 bad=copy.deepcopy(cfg);bad['previous_cpu_v1_config']['cpu_spare_policy']['quota_fraction']=.9
 reject(lambda:lib.validate(bad,qq))
ck('actual CPU1 immutable preimage/fallback/source lineage and mutated-preimage rejection',lineage)
def nativeproof():
 p=copy.deepcopy(snap['fresh_preflights'][0]);lib.verify_memory_proof(p,require_native=True)
 bad=copy.deepcopy(p);bad['context']['kind']='OWNER_FRAME';reject(lambda:lib.verify_memory_proof(bad,require_native=True))
 bad=copy.deepcopy(p);bad['context']['cohort']='CPU2_UNADMITTED_FOREIGN';reject(lambda:lib.verify_memory_proof(bad,require_native=True))
ck('actual saved native CPU2 proof accepts; frame and foreign context cannot substitute',nativeproof)
def historic():
 c=cfg['previous_cpu_v1_config']['cpu_exception_scope']['allowed_cohorts'][0]
 i1=read(R/'control/qualification_ledger'/(c+'.INTENT.json'))
 e1=owner.historical_extra(i1,i1['output']);assert sha(e1.__file__)==cfg['previous_cpu_v1_config']['extra_strict_sha256']
 c2=snap['invocation']['cohort'];i2=read(root/'control/qualification_ledger'/(c2+'.INTENT.json'))
 e2=owner.historical_extra(i2,i2['output']);assert sha(e2.__file__)==pins['extra_strict']
 bad=copy.deepcopy(i2);bad['additional_future_memory_admission_binding']={};reject(lambda:owner.historical_extra(bad,i2['output']))
ck('actual CPU1 and saved CPU2 INTENT select exact historical strict; ambiguous binding rejects',historic)
def rollback():
 src=paths['owner'].read_text();tree=ast.parse(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='restore_in_owner')
 text=ast.get_source_segment(src,fn)
 assert "s['retained_cpu_generation_consumer']=dispatch_consumer"in text and 'consumer.load=dispatch_consumer'in text
 assert "s.clear();s.update(v['preimage'])"in text and "tiny.facade.resources=old['tiny_resource']"in text
 assert "aging.original=old['choose']"in text and "frame.f_globals['worker']=old['worker']"in text
 assert oq['status']=='PASS'and 'CPU1 and CPU2 receipts remain consumable by retained snapshot dispatcher'in oq['checks']
ck('restore source retains multi-generation consumer and exact dispatch/facade preimage; actual owner CPU qualification joined',rollback)
out=dict(schema='B_CPU2_LIMITED_INDEPENDENT_REVIEW_V1',status='PASS_LIMITED_REVIEW_PENDING_FINAL_CANDIDATE_FREEZE',checks=checks,count=len(checks),source_sha256=pins,source_paths={k:str(v)for k,v in paths.items()},canary_approval_path=str(approval),canary_approval_sha256=sha(approval),joined_qualification={str(p):sha(p)for p in[A/'agents/E/cpu_spare_execution_v2/OWNER_CPU_QUALIFICATION.json',A/'agents/E/cpu_spare_execution_v2/EXTRA_CPU_QUALIFICATION.json',A/'agents/A/cpu_spare_memory_v2/CPU_SCOPE_QUALIFICATION.json']},models_started=0,production_changes=0,new_grants=0,broad_release_approved=False,scope='Six limited interface/static checks; existing GPU canary is approval evidence, not a new experiment. Rollback uses source+existing owner qualification, not a production rollback.')
f=B/'B_LIMITED_INTERFACE_REVIEW.json';f.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(f),sha256=sha(f),status=out['status'],checks=len(checks))))
