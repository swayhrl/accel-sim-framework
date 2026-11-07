from pathlib import Path
import json,hashlib,types,copy,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');OLD=Path('/root/data/dtc_controlled_oracle_20261106_v1/remaining24');BASE=Path('/root/data/dtc_oracle_clean_successor_20261107_v1');R=BASE/'remaining24';X=A/'agents/R_clean_successor_cpu_preparation_v1';S=A/'agents/S_clean_main_successor_preparation_v1'
assert not R.exists(),'NEW_CPU_ROOT_MUST_NOT_EXIST';R.mkdir(parents=True);assert R.stat().st_dev==2128
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rd=lambda p:json.loads(Path(p).read_bytes());enc=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=v if isinstance(v,bytes)else enc(v)
 with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def load(p):m=types.ModuleType('CPU_ONLY_PURE_ADAPTER');m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
source_snapshots=[]
for name in ['oracle_clean_main.py','oracle_clean_owner_guard.py','oracle_successor_engine.py']:
 p=S/name;raw=p.read_bytes();write(R/'tools'/name,raw);source_snapshots.append({'path':str(p),'sha256':sha(p),'snapshot_path':str(R/'tools'/name),'snapshot_sha256':sha(R/'tools'/name)})
adapter=load(R/'tools/oracle_successor_engine.py');b2=rd(S/'CPU_SOURCE_INPUTS.fixed.json')['B2'];assert sha(b2['path'])==b2['sha256'];oldnative=(OLD/'tools/oracle_native.py').read_bytes();oldops=(OLD/'tools/oracle_ops.py').read_bytes();native,np=adapter.derive_native(oldnative);ops,op=adapter.derive_ops(oldops,Path(b2['path']).read_bytes())
for p in (OLD/'tools').glob('*.py'):
 if p.name not in ['oracle_native.py','oracle_ops.py']:write(R/'tools'/p.name,p.read_bytes())
write(R/'tools/oracle_native.py',native.encode());write(R/'tools/oracle_ops.py',ops.encode());write(R/'tools/oracle_clean_peer_disk_adapter.py',(X/'oracle_clean_peer_disk_adapter.py').read_bytes())
for name in['BUILD_PROFILE.json','SOURCE_FREEZE.fixed.json','INDEPENDENT_CPU_REVIEW_MANIFEST.fixed.json','RESULT_ENGINE_PIN.json','RESULT_ENGINE_PIN.fixed.json','RESOURCE_POLICY.json','RESOURCE_POLICY.fixed.json','PROJECT_AUTHORITY.fixed.json','MATRIX.fixed.json']:
 write(R/'control'/name,(OLD/'control'/name).read_bytes())
for d in['DTC/run/results','DTC/run/recovery','control/input_bindings','control/specs','control/qualification_ledger','control/dispatch_bindings','analysis','logs','engineering_cpu']: (R/d).mkdir(parents=True,exist_ok=True)
(BASE/'control').mkdir(exist_ok=True)
oldplan=rd(OLD/'control/EXECUTION_PLAN.json');matrix=rd(R/'control/MATRIX.fixed.json');specs=[];inputs={};copied_875f_sha=sha(OLD/'control/CPU_DRAFT_BUILD.json');assert copied_875f_sha=='875f13222f959986bb88533041180f88cba30070a42805216ea9bb5c06ebb02a'
layout_pending={'path':str(R/'control/LAUNCHER_LAYOUT.fixed.json'),'sha256':None,'status':'CPU_TRUE_PENDING_NOT_SCIENCE_READY'}
for pt in matrix['points']:
 old=rd(OLD/'control/specs'/(pt['cohort']+'.json'));s=copy.deepcopy(old);s['host_launcher_layout']=layout_pending;adapter.require_science_equal(old,s);specs.append(s)
 for rf in s['runtime_files']:
  dest=R/rf['target'];dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists()and not dest.is_symlink():dest.symlink_to(rf['actual_realpath'])
  assert dest.resolve()==Path(rf['actual_realpath']).resolve()and sha(dest)==rf['sha256']
 if s['input_digest']not in inputs:
  ib=OLD/'control/input_bindings'/(s['input_digest']+'.json');assert sha(ib)==s['input_binding_sha256'];write(R/'control/input_bindings'/ib.name,ib.read_bytes());inputs[s['input_digest']]=s['input_binding_sha256']
 write(R/'control/specs'/(s['cohort']+'.json'),s);write(R/'control'/(s['cohort']+'_SPEC.json'),s)
peer={'path':str(R/'tools/oracle_clean_peer_disk_adapter.py'),'sha256':sha(R/'tools/oracle_clean_peer_disk_adapter.py'),'function':'admission_disk_reservations'};guard={'path':str(R/'tools/oracle_clean_owner_guard.py'),'sha256':sha(R/'tools/oracle_clean_owner_guard.py')};lease={'path':str(R/'control/CLEAN_OWNER_PRIVATE_LEASE.json'),'sha256':None,'status':'NO_ACTUAL_PARENT_NO_LEASE_CREATED'};parent={'pid':None,'start_ticks':None,'controller':{'path':str(R/'tools/oracle_clean_main.py'),'sha256':sha(R/'tools/oracle_clean_main.py')}}
plan=adapter.plan_projection(oldplan,root=R,parent=parent,guard_ref=guard,lease_ref=lease,source_pins=[],layout_ref=layout_pending,engine_pin_ref={'path':str(R/'control/RESULT_ENGINE_PIN.json'),'sha256':sha(R/'control/RESULT_ENGINE_PIN.json')},peer_ref=peer)
plan.update(oracle_request_roots={plan['request']:str(R)},mode_gate2_reviews=oldplan['mode_gate2_reviews'],new_scientific_starts_permitted=False)
write(R/'control/EXECUTION_PLAN.json',plan)
# Use the byte-identical previously qualified CPU-only actual-native-layout helper.
layout=load(R/'tools/oracle_layout.py');qualified=layout.initialize(specs,R/'engineering_cpu/layout_v1');assert len(rd(qualified['path'])['CPU_probes'])==96
# Parent identity and all science-execution permission remain absent. Binding the
# completed CPU proof changes only the allowed launcher proof field in96 specs.
for s in specs:
 old=rd(OLD/'control/specs'/(s['cohort']+'.json'));s['host_launcher_layout']=qualified;adapter.require_science_equal(old,s)
 for pp in[R/'control/specs'/(s['cohort']+'.json'),R/'control'/(s['cohort']+'_SPEC.json')]:pp.write_bytes(enc(s))
plan['launcher_layout']=qualified;plan['launcher_native_cwd_qualification']=qualified;plan['result_engine_pin']={'path':str(R/'control/RESULT_ENGINE_PIN.json'),'sha256':sha(R/'control/RESULT_ENGINE_PIN.json')}
# Do not retain old-root tool source pins as the new operational source identity.
pins=[]
for pp in sorted((R/'tools').glob('*.py')):pins.append({'path':str(pp),'sha256':sha(pp)})
for name in['SOURCE_FREEZE.fixed.json','INDEPENDENT_CPU_REVIEW_MANIFEST.fixed.json','RESULT_ENGINE_PIN.json','RESULT_ENGINE_PIN.fixed.json','RESOURCE_POLICY.json','RESOURCE_POLICY.fixed.json','PROJECT_AUTHORITY.fixed.json','LAUNCHER_LAYOUT.fixed.json']:
 pp=R/'control'/name;pins.append({'path':str(pp),'sha256':sha(pp)})
for s in specs:pp=R/'control/specs'/(s['cohort']+'.json');pins.append({'path':str(pp),'sha256':sha(pp)})
plan['source_pins']=pins;(R/'control/EXECUTION_PLAN.json').write_bytes(enc(plan))
q=rd(OLD/'control/REGISTRY_REQUEST_CANDIDATE.DRAFT.json');q.update(owner_pid=None,owner_start_ticks=None,controller_path=parent['controller']['path'],controller_sha256=parent['controller']['sha256'],execution_plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),engine_sha256=sha(R/'tools/oracle_native.py'),strict_sha256=sha(R/'tools/oracle_strict.py'),outbox_sha256=sha(R/'tools/oracle_outbox.py'),ready_for_registration=False,science_authority=False,state='CPU_RESOURCE_ONLY_NOT_A_SCIENTIFIC_CANDIDATE',admitted_specs={s['cohort']:sha(R/'control/specs'/(s['cohort']+'.json'))for s in specs},reserved_write_bytes=256*1024**2)
write(R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json',q)
manifest={'schema':'DTC_CLEAN_SUCCESSOR_CPU_ARTIFACTS_MANIFEST_V1','request':plan['request'],'stage':'remaining24','registered':False,'models_started':0,'scientific_UUIDs_allocated':0,'plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'resource_candidate_sha256':sha(R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json'),'source_draft875f':{'path':str(OLD/'control/CPU_DRAFT_BUILD.json'),'sha256':copied_875f_sha},'layout_ref':qualified,'science_projection_comparison_count':96,'science_projection_equal':True,'new_parent_pid_start':None,'actual_owner_lease_created':False,'source_snapshots':source_snapshots,'native_transform':np,'ops_transform':op,'files':[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in sorted((R/'control').rglob('*.json'))if p.name!='CLEAN_CPU_ARTIFACTS_MANIFEST.json']}
write(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json',manifest);write(X/'NATIVE_CPU_ARTIFACT_RESULT.json',{'schema':'DTC_CLEAN_SUCCESSOR_CPU_ARTIFACT_RESULT_V1','root':str(R),'status':'CPU_TRUE96_PASS_ACTUAL_REGISTRATION_HELD','manifest':{'path':str(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json'),'sha256':sha(R/'control/CLEAN_CPU_ARTIFACTS_MANIFEST.json')},'layout_ref':qualified,'source_snapshots':source_snapshots,'new_parent':None,'new_scientific_models':0,'new_scientific_UUIDs':0,'old875f_sha_after':sha(OLD/'control/CPU_DRAFT_BUILD.json')});print(json.dumps(rd(X/'NATIVE_CPU_ARTIFACT_RESULT.json'),indent=2))
