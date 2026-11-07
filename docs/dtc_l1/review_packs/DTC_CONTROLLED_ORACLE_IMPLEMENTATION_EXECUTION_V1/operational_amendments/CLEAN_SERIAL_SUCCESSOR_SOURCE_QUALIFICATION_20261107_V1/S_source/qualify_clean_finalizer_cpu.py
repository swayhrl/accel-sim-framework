"""Complete finalizer call on a disposable CPU tree; zero real science writes.

Only live-parent assertion and path roots are explicit CPU backends. The actual
finalizer source,96 original/private specs, actual native layout verification,
normal auth/source pins/candidate/route closure are exercised unchanged.
"""
from pathlib import Path
import copy,hashlib,json,shutil,tempfile,types
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def rd(p):return json.loads(Path(p).read_bytes())
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v if isinstance(v,bytes)else(json.dumps(v,sort_keys=True,indent=2)+'\n').encode())
def load(name,p):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
source=HERE/'oracle_clean_finalizer.py';f=load('CPU_ACTUAL_FINALIZER_SOURCE',source)
r=load('CPU_ACTUAL_PURE_REGISTER_SOURCE',HERE/'oracle_clean_runtime.py')
original=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24')
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
original_report=A/'agents/R_clean_successor_cpu_preparation_v1/CPU_PREPARATION_REPORT.fixed.json'
checks=[]
def check(name,ok):
 checks.append(dict(name=name,status='PASS'if ok else'FAIL'));assert ok,name
with tempfile.TemporaryDirectory(dir='/root/data',prefix='DTC_MOCK_NO_SCIENCE_COMPLETE_FINALIZER_')as d:
 t=Path(d);root=t/'newbase/remaining24';root.parent.mkdir()
 shutil.copytree(original,root,symlinks=True)
 if not(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json').exists():
  shutil.copyfile(f.OLDROOT/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 # No production file may be a write target; old references remain read-only.
 f.NEWROOT=root;f.NATIVE=t/'MOCK_NATIVE_ROUTE';write(f.NATIVE,b'#!/bin/sh\nset -eu\n# MOCK_NO_SCIENCE_ORIGINAL_ROUTE\n')
 guard=t/'MOCK_ONLY_LIVE_PARENT_BACKEND.py'
 write(guard,b"def verify_parent_lease(plan):\n assert plan['parent_pid']==999999991 and plan['parent_start_ticks']==777\n return {'MOCK_CPU_ONLY_NO_LIVE_OWNER':True}\n")
 # This backend substitutes the already separately tested real-process guard;
 # it does not substitute native/spec/layout/auth/source/route finalizer logic.
 parent=dict(pid=999999991,start_ticks=777,request=f.REQUEST,controller=ref(HERE/'oracle_clean_main.py'))
 lp=root/'control/CLEAN_MAIN_PRIVATE_LEASE.fixed.json';write(lp,dict(parent,MOCK_CPU_ONLY=True));lease=ref(lp)
 plan=rd(root/'control/EXECUTION_PLAN.json');plan['execution_root']=str(root)
 write(root/'control/EXECUTION_PLAN.json',plan)
 if not(root/'control/NATIVE_ROUTE_BLOCK.sh').exists():
  points=rd(root/'control/MATRIX.fixed.json')['points'];cases='|'.join(k+':'+p['cohort']for p in points for k in['experiment','result'])
  block=('# DTC_ORACLE_CLEAN_SUCCESSOR_REMAINING24_V1_ROUTE MOCK_CPU_ONLY\ncase "$1:$3" in\n'+cases+')\n true ;;\nesac\n').encode()
  write(root/'control/NATIVE_ROUTE_BLOCK.sh',block)
 prep=dict(status='PASS_CPU_CLEAN_SUCCESSOR_ARTIFACTS_AND_LAYOUT',root=str(root),scientific_models_started=0,
   science_registrations=0,science_projection_equal_96=True,files=[ref(p)for p in root.rglob('*')if p.is_file()],
   MOCK_CPU_FIXTURE_NOT_ACTUAL_PASS=True,actual_report_context=ref(original_report))
 prepfile=t/'MOCK_CPU_PREPARATION.json';write(prepfile,prep)
 review=t/'MOCK_CPU_REVIEW_NOT_AN_ACTUAL_RELEASE.json'
 release=dict(actual_execution_authorized=True,execution_root=str(root),cpu_preparation=ref(prepfile),guard=ref(guard),
   engine_adapter=ref(HERE/'oracle_successor_engine.py'),immutable_historical_refs=[ref(f.OLDROOT/'control/CPU_DRAFT_BUILD.json')],
   runtime_adapter=ref(HERE/'oracle_clean_runtime.py'),artifact_finalizer=ref(source),RSS_history_adapter=ref(A/'agents/S_owner_image_B_preparation_v2/oracle_exact_rss_history.py'))
 write(review,dict(artifact_finalizer_sha256=sha(source),cpu_preparation_sha256=sha(prepfile),
   engine_adapter_sha256=sha(HERE/'oracle_successor_engine.py'),MOCK_CPU_NOT_ACTUAL_D_REVIEW=True))
 release['independent_live_review']=ref(review)
 before_old=sha(f.OLDROOT/'control/CPU_DRAFT_BUILD.json');before_native=sha(f.NATIVE)
 value=f.finalize_and_qualify_parent(release,parent,lease)
 check('ACTUAL_FINALIZER_FULL_CALL_COMPLETES_ON_DISPOSABLE_TREE',value['status']=='PASS_NEW_PRIVATE_CPU_LAYOUT_SOURCE_RESOURCE_QUALIFICATION')
 newplan=rd(root/'control/EXECUTION_PLAN.json');q=rd(root/'control/REGISTRY_REQUEST_CANDIDATE.json');auth=rd(root/'control/SCIENCE_AUTHORIZATION.json')
 check('TRUE_METADATA_BINDING_WITHOUT_FAKE_OLD_PARENT',newplan['parent_pid']==999999991 and newplan['parent_start_ticks']==777)
 check('NORMAL_AUTH_EXACT96_AND_THREE_RATIFICATIONS',len(auth['budgets'])==96 and all(v==1 for v in auth['budgets'].values())and auth['owner_bindings_ratified']and auth['target_resource_policy_ratified'])
 check('CANDIDATE_PLAN_SOURCE_CLOSURE',q['execution_plan_sha256']==sha(root/'control/EXECUTION_PLAN.json')and q['engine_sha256']==sha(root/'tools/oracle_native.py')and q['outbox_sha256']==sha(root/'tools/oracle_outbox.py'))
 resource=load('CPU_ACTUAL_REGISTRATION_RELEASE_SOURCE',root/'tools/oracle_resources.py')
 # The physical sampler/peer probe has its separate actual R/P6 CPU evidence.
 # Here only that terminal probe is mocked so the temporary tree cannot be
 # confused with the production root. Source/gate/96spec/schema checks run real.
 probe_calls=[]
 def CPU_resource_probe(spec,fresh):
  probe_calls.append((spec['cohort'],fresh))
  return dict(physical_RAM_pass=True,physical_disk_pass=True,admission_disk_pass=True,admission_pressure_pass=True,
              MOCK_CPU_NO_ADMISSION_OR_AUTHORITY=True)
 resource.resources=CPU_resource_probe
 full_evidence=resource.verify_registration_release(newplan,q)
 check('ACTUAL_REGISTRATION_RELEASE_SCHEMA_SOURCE_AND_GATES_WITH_CPU_PHYSICAL_BACKEND',
   full_evidence['exact_candidate_count']==96 and len(probe_calls)==1 and full_evidence['resource_sample']['MOCK_CPU_NO_ADMISSION_OR_AUTHORITY'])
 check('CPU_PREIMAGES_PRESERVED',(root/'control/CLEAN_PARENT_BIND_PREIMAGES/NATIVE_ROUTE_PREIMAGE.bytes').exists())
 check('FINALIZER_DOES_NOT_INSTALL_OR_MODIFY_NATIVE_ROUTE',sha(f.NATIVE)==before_native)
 reg=dict(registered_future_requests={'MOCK_OLD32':{'exact':'untouched'}},old_source_history={'old':'retained'})
 resources=rd(root/'control/EXECUTION_PLAN.json')
 ev=dict(authority_commit=r.AUTHORITY,exact_candidate_count=96,Gate0_CPU_source_strict_independent_review='PASS',Gate2_any_mode_fixed8_and_shared_OFF_accepted_independently_reviewed='PASS',Gate2_released_modes=['M_DATAREAD'])
 r.register_exact_request(reg,q,resources,parent,ev)
 check('PURE_CALLBACK_ACCEPTS_COMPLETE_SCHEMA_NO_REAL_REGISTRY_WRITE',reg['registered_future_requests']['MOCK_OLD32']=={'exact':'untouched'})
 route=f.install_reviewed_native_route(release,parent)
 check('TEMP_ONLY_ADDITIVE_NATIVE_ROUTE_CLOSED',route['status']=='PASS_ADDITIVE_EXACT_NEW96_NATIVE_ROUTE'and sha(f.NATIVE)==newplan['installed_native_route']['sha256'])
 check('ALL_OLD875F_BYTES_UNCHANGED',sha(f.OLDROOT/'control/CPU_DRAFT_BUILD.json')==before_old)
 report=dict(status='PASS_CPU_COMPLETE_FINALIZER_DISPOSABLE_TREE',source_sha256=sha(source),checks=checks,
  original_report_context=ref(original_report),actual_registry_writes=0,actual_native_route_writes=0,actual_science_starts=0,
  actual_production_locks=0,actual_owner_or_tracer_actions=0,
  explicit_MOCK_PARENT_GUARD_BACKEND=True,original_spec_and_native_layout_checks_unmocked=True,
  explicit_MOCK_PHYSICAL_RESOURCE_BACKEND_only_terminal_probe=True,
  mock_status_fields_never_a_real_execution_authority=True)
 (HERE/'COMPLETE_FINALIZER_DISPOSABLE_CPU_QUALIFICATION.fixed.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print(json.dumps(report,indent=2))
