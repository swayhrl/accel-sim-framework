"""Isolated interface fixtures + real frozen CPU2 proof arithmetic; zero models."""
import copy,hashlib,json,pathlib,types,tempfile,time,threading,importlib.util
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/bpf_engineering_resource_priority_v1';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');G=1024**3
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
m=load('candidate',D/'resource_priority.py');planpath=A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json';plan=read(planpath);cp=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';contract=read(cp)
bridgepath=A/'coordinator/bpf_canary_orchestration_v1/scope_bridge.py';bridge=load('frozen_scope_bridge',bridgepath);scope=bridge.CanaryScope(plan)
libpath=R/'control/operational_amendments/cpu_spare_memory_v2/cpu_memory.py';lib=load('actual_frozen_cpu2',libpath);cfgpath=R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json';cfg=read(cfgpath);q=copy.deepcopy(read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ]);lib.validate(cfg,q)
matrix=read(R/'control/MATRIX_CURRENT.json');primary=read(R/'control/SCOPE.json');specs={r['cohort']:read(r['draft_spec_path'])for r in plan['rows']};hashes={c:r['draft_spec_sha256']for c,r in zip(specs,plan['rows'])}
privateq=copy.deepcopy(q);privateq['admitted_specs'].update(hashes);privateq['authorized_engineering_observation_canaries']=[dict(cohort=c,role=bridge.ROLE,mode=r['mode'],science_projection_sha256=r['science_projection_sha256'],primary_statistics_excluded=True,validated_union_authorized=False)for c,r in scope.rows.items()]
canonical=lambda c:(specs[c],hashes[c]);proposal=m.propose_scope_append(cfg,privateq,scope,contract,matrix,primary,canonical,lib);newcfg=proposal['new_config'];newq=copy.deepcopy(privateq);newq['additional_operational_overlays'][lib.ID]=proposal['new_full_record'];lib.validate(newcfg,newq)
checks=[]
def check(name,fn):
 try:assert fn();checks.append(dict(name=name,status='PASS'))
 except Exception as e:checks.append(dict(name=name,status='FAIL',error=repr(e)));raise
def refuses(fn):
 try:fn()
 except Exception:return True
 return False
check('real_cpu2_frozen_library_accepts_official_registered_private_append',lambda:set(specs)<=set(newcfg['allowed_cohorts']))
check('scope_only_changes_allowed_and_preserves_old_extra_provenance',lambda:proposal['new_full_record'].get('publication_commit')==proposal['old_full_record'].get('publication_commit')and all(newcfg[k]==cfg[k]for k in cfg if k!='allowed_cohorts'))
check('no_grant_budget_remaining_or_science_matrix_changed',lambda:privateq['budget']==q['budget']and privateq['remaining']==q['remaining']and privateq['consumed']==q['consumed']and proposal['grant_changes']==0)
check('unregistered_four_rejected_not_injected',lambda:refuses(lambda:m.propose_scope_append(cfg,q,scope,contract,matrix,primary,canonical,lib)))
bad=copy.deepcopy(privateq);bad['authorized_engineering_observation_canaries'][0]['primary_statistics_excluded']=False
check('engineering_contract_authority_role_exclusion_required',lambda:refuses(lambda:m.propose_scope_append(cfg,bad,scope,contract,matrix,primary,canonical,lib)))
badmatrix=copy.deepcopy(matrix);badmatrix['points'].append(dict(cohort=next(iter(specs))))
check('engineering_in_primary_matrix_rejected',lambda:refuses(lambda:m.propose_scope_append(cfg,privateq,scope,contract,badmatrix,primary,canonical,lib)))
oldfixture=load('frozen_cpu1_evidence_fixture',A/'agents/A/cpu_spare_memory_v1/cpu_fixture.py')
class FrameUnavailable(Exception):pass
class Gate:
 def choose(self):return FrameUnavailable
class Exclusive:
 def atomic_exclusive(self,p,v):
  p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
  import os
  with p.open('x')as f:f.write(m.js(v).decode());f.flush();os.fsync(f.fileno())
class BrokenExclusive:
 def atomic_exclusive(self,p,v):raise OSError('CPU_FIXTURE_DISK_ERROR')

def fixture():
 root=P(tempfile.mkdtemp(prefix='PRIVATE_PRIORITY_',dir=D));put(root/'control/MATRIX_CURRENT.json',matrix);put(root/'control/SCOPE.json',primary);put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}});put(root/'control/RESOURCE_POLICY.json',read(R/'control/RESOURCE_POLICY.json'))
 for c,s in specs.items():put(root/'control/specs'/(c+'.json'),s)
 # Real draft files use exact same sorted pretty JSON serialization.
 qq=copy.deepcopy(newq);qq['admitted_specs'].update({c:sha(root/'control/specs'/(c+'.json'))for c in specs})
 mmcfg=copy.deepcopy(newcfg);memorypath=root/'ACTIVE_MEMORY.json';put(memorypath,mmcfg);qq['additional_operational_overlays'][lib.ID]=dict(qq['additional_operational_overlays'][lib.ID],**lib.record(mmcfg))
 engine=types.SimpleNamespace(registered=lambda:(None,None,qq,None),canonical=lambda c:copy.deepcopy(specs[c]),assert_parent_lease=lambda:True)
 state=types.SimpleNamespace(protected=36*G,pending_releases={},previous_C=9*G,calls=5,tokens=17)
 aging=types.SimpleNamespace(lock=threading.RLock(),state=state,frame_provider=lambda *a:dict(pressure_reasons=[],consumed=qq['consumed'],claim_cohorts=list(a[2]),pending=a[0]))
 res=types.SimpleNamespace(resources=lambda *a:None,cpu_candidates=lambda *a:[0,1],forecast=lambda s,h,p:dict(predicted_peak_RAM_bytes=s['estimated_peak_model_RAM_bytes']))
 base0=dict(boot_id=read(R/'control/RESOURCE_OBSERVER.json')['boot_id'],source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),host_MemAvailable_bytes=200*G,cgroup_effective_headroom_bytes=220*G,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,monotonic=time.monotonic(),physical_disk_pass=True,own_write_ceiling_pass=True,total_projected_additional_RAM_bytes=0,RAM_reservation_entries=[dict(additional_reserved_bytes=3*G)],own_ram_forecasts=[],admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(.88*192*G),additional_reserved_RAM_bytes=0,pressure_reasons=['cpu_pressure_full'],pressure_pause_new=True,pass_admission=False),physical_RAM_pass=False)
 env=types.SimpleNamespace(base=base0,qq=qq,root=root,mode=None,evidence=lambda cpu:oldfixture.evidence(lib,cpu))
 def choose(pool,*args):
  s=pool[0];c=s['cohort'];base=copy.deepcopy(env.base);base['own_ram_forecasts']=[dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=s['estimated_peak_model_RAM_bytes'])];base['total_projected_additional_RAM_bytes']=3*G+s['estimated_peak_model_RAM_bytes'];base['admission_decision']['additional_reserved_RAM_bytes']=base['total_projected_additional_RAM_bytes']
  projected=lib.project_for_candidate(base,mmcfg,c,0,env.evidence(0),dict(kind='OWNER_CHOOSE'));proof=projected['additional_cpu_spare_memory_admission_proof']
  if env.mode=='omit_candidate':proof['base_resource_snapshot']['own_ram_forecasts']=[]
  return dict(cohort=c,host_cpu=0,new_execution_no_padding=True,forecast=res.forecast(s,None,None),cpu_spare_owner_proof=proof)
 aging.original=choose;gate=Gate();gate.aging=aging;gate.original_choose=lambda *a:None
 # Fixture outer models preserved CPU/FrameGuard chain; not a real native launch.
 res.choose_dispatch=lambda *a,**k:gate.original_choose(*a,**k)
 memory=dict(lib=lib,context={'cfg':mmcfg},new_choose=choose,new_resources=res.resources)
 frame=types.SimpleNamespace(f_locals=dict(engine=engine,res=res,claims={},running={}))
 qa=root/'CPU_ONLY_QA.json';back=root/'CPU_ONLY_READBACK.json';put(qa,dict(status='PASS',source_sha256=sha(m.__file__),qualification_only=True));put(back,dict(verified=True,source_sha256=sha(m.__file__),QA_sha256=sha(qa),qualification_only=True))
 acfg=dict(root=str(root),status='ACTIVE_PRIORITY_ONLY',allowed_cohorts=list(specs),priority_only=True,source_sha256=sha(m.__file__),dependency_pins={str(libpath):sha(libpath),str(bridgepath):sha(bridgepath)},contract_path=str(cp),contract_sha256=sha(cp),QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back),memory_active_path=str(memorypath),token_directory=str(root/'attempts'),qualification_only=True)
 qq['additional_operational_overlays'][m.ID]=m.record(acfg);a=m.Priority(frame,acfg,gate,memory,scope,Exclusive());env.a=a;env.gate=gate;env.res=res;env.aging=aging;env.args=([copy.deepcopy(next(iter(specs.values())))],{}, {}, {},None,None,1)
 return env
def one(change=lambda e:None,outer=False):
 e=fixture();change(e);m.install(e.a);value=e.res.choose_dispatch(*e.args)if outer else e.gate.original_choose(*e.args);return e,value
e,value=one(outer=True)
check('full_real_cpu2_proof_math_and_two_frame_ordering_exception',lambda:value is not None and 'bpf_engineering_priority_dispatch'in value)
check('virtual_R_previous_C_credit_tokens_unchanged',lambda:e.aging.state.__dict__==dict(protected=36*G,pending_releases={},previous_C=9*G,calls=5,tokens=17))
check('durable_reserved_and_cpu_return_receipts_before_claim',lambda:len(list((e.root/'attempts').glob('*.json')))==2 and not e.qq['consumed'].get(value['cohort']))
oldrefs=(e.a.old_e,e.a.old_outer);m.restore(e.a)
check('exact_restore_retains_original_outer_inner_and_other_refs',lambda:e.gate.original_choose is oldrefs[0]and e.res.choose_dispatch is oldrefs[1])
for name,change in [
 ('physical_RAM_hold',lambda e:e.base.update(host_MemAvailable_bytes=10*G)),
 ('disk_hold',lambda e:e.base.update(physical_disk_pass=False)),
 ('own_write_hold',lambda e:e.base.update(own_write_ceiling_pass=False)),
 ('inodes_hold',lambda e:e.base.update(free_inodes=10)),
 ('stale_resource_sample_hold',lambda e:e.base.update(monotonic=time.monotonic()-10)),
 ('nonCPU_pressure_hold',lambda e:e.base['admission_decision'].update(pressure_reasons=['cpu_pressure_full','memory_pressure_full'])),
 ('CPU_no_candidate',lambda e:setattr(e.res,'cpu_candidates',lambda *a:[])),
 ('CPU_throttle_hold',lambda e:setattr(e,'evidence',lambda cpu:dict(oldfixture.evidence(lib,cpu),selected_cpu=99))),
 ('candidate_missing_cannot_discount',lambda e:setattr(e,'mode','omit_candidate')),
 ('full_forecast_growth_hold',lambda e:setattr(e.res,'forecast',lambda s,*a:dict(predicted_peak_RAM_bytes=s['estimated_peak_model_RAM_bytes']+1))),
 ('already_claimed',lambda e:e.args[2].update({e.args[0][0]['cohort']:{}})),
 ('already_consumed',lambda e:e.qq['consumed'].update({e.args[0][0]['cohort']:dict(uuid='CPU_FIXTURE_SPENT')})),
 ('already_INTENT',lambda e:put(e.root/'control/qualification_ledger'/(e.args[0][0]['cohort']+'.INTENT.json'),{})),
 ('wrong_parent_lease',lambda e:setattr(e.a.engine,'assert_parent_lease',lambda:(_ for _ in()).throw(RuntimeError('WRONG_LEASE')))),
 ('source_drift',lambda e:e.a.cfg['dependency_pins'].update({str(libpath):'0'*64})),
 ('token_write_failure',lambda e:setattr(e.a,'helper',BrokenExclusive())),
 ('nonengineering_pool',lambda e:e.args[0].__setitem__(0,dict(cohort='PRIMARY_NON_ENGINEERING'))),
]:
 ee=fixture();change(ee)
 # Source/config drift should hold engineering, but installation itself refuses.
 if name in ['source_drift','wrong_parent_lease']:check(name,lambda:refuses(lambda:m.install(ee.a)));continue
 m.install(ee.a);v=ee.gate.original_choose(*ee.args);check(name,lambda:v is None)
e=fixture();normal={'cohort':'NORMAL_E_DECISION','unchanged':True};e.gate.original_choose=lambda *a:normal;e.a.old_e=e.gate.original_choose;m.install(e.a)
check('normal_E_choice_unchanged_and_always_first',lambda:e.gate.original_choose(*e.args)is normal)
e=fixture();e.a.old_e=lambda *a:(_ for _ in()).throw(FrameUnavailable('EXACT_SENTINEL'))
check('exact_FrameUnavailable_propagates_to_original_guard',lambda:refuses(lambda:e.a.inner(*e.args)))
e=fixture();e.a.old_outer=lambda *a:(_ for _ in()).throw(RuntimeError('CPU_OUTER_ERROR'))
check('outer_exception_contained_without_controller_escape',lambda:e.a.outer(*e.args)is None)
result=dict(schema='BPF_ENGINEERING_RESOURCE_PRIORITY_CPU_QUALIFICATION_V1',status='PASS',qualification_only=True,checks=checks,source_sha256=sha(m.__file__),source_pins={str(p):sha(p)for p in [P(__file__),libpath,bridgepath,planpath,cp]},scope='Pure private authority/config clones + mocked E/CPU/frame interfaces with REAL frozenCPU2 validate/project/verify and frozen CPU evidence fixture. No actual owner installation, Popen, grant, registry or model.',not_qualified=['Actual same-owner install/source publication and legal grant transaction','Actual native private entry, IO+CPU2+newextra terminal/archive closure (B/E)'],production_changes=0,model_starts=0,grants_added=0)
put(D/'CPU_QUALIFICATION.json',result);print(json.dumps({'path':str(D/'CPU_QUALIFICATION.json'),'sha256':sha(D/'CPU_QUALIFICATION.json'),'checks':len(checks),'source_sha256':sha(m.__file__)}))
