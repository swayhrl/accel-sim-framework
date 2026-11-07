"""New-root-only forward finalization; no registry or model operations.

Called only inside the real clean Main's four-lock lifetime after final D/Main
release. Original CPU875f, original leases/q32/journal remain read-only.
"""
from pathlib import Path
import copy,hashlib,json,os,types
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1'
NATIVE=Path('/root/data/ep_l2_dtc_l1_native_v2/bin/native')
NEWROOT=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24')
OLDROOT=Path('/root/data/dtc_controlled_oracle_20261106_v1/remaining24')
class Hold(RuntimeError):pass
def need(x,why):
 if not x:raise Hold(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def pinned(ref):
 p=Path(ref['path']);need(sha(p)==ref['sha256'],'PIN_DRIFT:'+str(p));return p
def load(ref,name):
 p=pinned(ref);m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as h:h.write(v if isinstance(v,bytes)else encoded(v));h.flush();os.fsync(h.fileno())
def forward(p,v,preimages):
 p=Path(p);need(NEWROOT in p.parents,'ONLY_NEW_PRIVATE_ROOT_FORWARD_METADATA')
 if p.exists():put(preimages/(p.name+'.'+sha(p)+'.preimage'),p.read_bytes())
 tmp=p.with_name('.'+p.name+'.CLEAN_PARENT_BINDING.writing')
 put(tmp,v);os.replace(tmp,p)
def route_projection(before,block):
 anchor=b'#!/bin/sh\nset -eu\n';marker=b'DTC_ORACLE_CLEAN_SUCCESSOR_REMAINING24_V1_ROUTE'
 need(before.startswith(anchor)and marker in block and marker not in before,'PREVIOUS_ROUTE_OR_SCOPE_CONFLICT_FORWARD_HOLD')
 after=anchor+block+before[len(anchor):]
 need(after.replace(block,b'',1)==before,'ALL_OLD_NATIVE_ROUTE_BYTES_RETAINED')
 return after
def bind_metadata(plan,candidate,parent,lease_ref,source_pins,route_ref,plan_sha):
 """Pure owner/profile binding. Scientific admitted-spec digests stay intact."""
 need(plan['request']==candidate['request']==parent['request']==REQUEST,'FIXED_REQUEST_SCOPE')
 need(plan['expected_new_starts']==candidate['budget']==candidate['remaining']==96
      and candidate['consumed']=={} and candidate['sealed']=={},'ONLY_UNUSED_NEW96')
 p=copy.deepcopy(plan);q=copy.deepcopy(candidate)
 p.update(parent_pid=parent['pid'],parent_start_ticks=parent['start_ticks'],
   parent_controller_path=parent['controller']['path'],parent_controller_sha256=parent['controller']['sha256'],
   clean_owner_lease=lease_ref,source_pins=source_pins,installed_native_route=route_ref,
   preparation_phase='SCIENCE_FINAL_FROZEN',actual_execution_authorized=True,extension_automation=None)
 q.update(owner_pid=parent['pid'],owner_start_ticks=parent['start_ticks'],ready_for_registration=True)
 q.pop('science_authority',None)
 q['execution_plan_sha256']=plan_sha
 need(q['admitted_specs']==candidate['admitted_specs'],'NO_ADMITTED_SPEC_REBINDING_DURING_OWNER_BIND')
 return p,q
def finalize_and_qualify_parent(release,parent,lease_ref):
 need(release['actual_execution_authorized']is True,'CPU_PACKAGE_HAS_NO_ACTUAL_RELEASE')
 root=Path(release['execution_root']);need(root==NEWROOT and root.stat().st_dev==2128,'NEW_PRIVATE_NATIVE_ROOT_ONLY')
 review=rd(pinned(release['independent_live_review']))
 need(review['artifact_finalizer_sha256']==sha(__file__)and review['cpu_preparation_sha256']==release['cpu_preparation']['sha256'],
      'EXACT_FINALIZER_AND_ARTIFACT_CPU_REVIEW_BINDING')
 need(review['engine_adapter_sha256']==release['engine_adapter']['sha256'],
      'INDEPENDENTLY_REVIEWED_ENGINE_ADAPTER_BEFORE_LOAD')
 prep=rd(pinned(release['cpu_preparation']))
 need(prep['status']=='PASS_CPU_CLEAN_SUCCESSOR_ARTIFACTS_AND_LAYOUT'and prep['root']==str(root)
      and prep['scientific_models_started']==prep['science_registrations']==0
      and prep['science_projection_equal_96']is True,'REAL_FULL_PRIVATE_CPU_QUALIFICATION_REQUIRED')
 for ref in prep['files']:pinned(ref)
 for ref in release['immutable_historical_refs']:pinned(ref)
 need(not(root/'control/REGISTRY_REQUEST_CANDIDATE.json').exists()
      and not(root/'control/SCIENCE_AUTHORIZATION.json').exists(),'NORMAL_ARTIFACT_ALREADY_EXISTS_FORWARD_HOLD')
 plan=rd(root/'control/EXECUTION_PLAN.json');candidate=rd(root/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json')
 need(plan['preparation_phase']=='CPU_CLEAN_SUCCESSOR_DRAFT_NOT_REGISTERED','PRECISE_CPU_DRAFT_PHASE')
 need(plan['parent_pid']is None and plan['parent_start_ticks']is None,'CPU_DRAFT_MUST_NOT_FAKE_FUTURE_PARENT')
 engine=load(release['engine_adapter'],'CLEAN_FINALIZER_PURE_SOURCE_ADAPTER')
 matrix=rd(root/'control/MATRIX.fixed.json');need(len(matrix['points'])==96,'EXACT96_POINTS')
 for point in matrix['points']:
  c=point['cohort'];old=rd(OLDROOT/'control/specs'/(c+'.json'));new=rd(root/'control/specs'/(c+'.json'))
  engine.require_science_equal(old,new)
  need(sha(root/'control/specs'/(c+'.json'))==candidate['admitted_specs'][c],'NEW_PRIVATE_SPEC_SHA')
 need(candidate['engine_sha256']==sha(root/'tools/oracle_native.py')
      and candidate['outbox_sha256']==sha(root/'tools/oracle_outbox.py')
      and candidate['strict_sha256']==sha(root/'tools/oracle_strict.py'),'NEW_ENGINE_STRICT_OUTBOX_PINS')
 block=(root/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();before=NATIVE.read_bytes();after=route_projection(before,block)
 route_ref=dict(path=str(NATIVE),sha256=hashlib.sha256(after).hexdigest())
 route_receipt=dict(schema='DTC_CLEAN_MAIN_PRECOMPUTED_NATIVE_ROUTE_V1',before_sha256=hashlib.sha256(before).hexdigest(),
   after_sha256=route_ref['sha256'],block_sha256=sha(root/'control/NATIVE_ROUTE_BLOCK.sh'),
   old_bytes_exactly_preserved=True,exact_cohorts=plan['authorized_cohorts'])
 preimages=root/'control/CLEAN_PARENT_BIND_PREIMAGES';preimages.mkdir(exist_ok=False)
 put(preimages/'NATIVE_ROUTE_PREIMAGE.bytes',before);put(preimages/'NATIVE_ROUTE_PLANNED.bytes',after)
 put(preimages/'ROUTE_PROJECTION.fixed.json',route_receipt)
 # CPU draft gate0 is deliberately PENDING and gate2 absent. Generate new,
 # explicit gates from real accepted original mechanism qualification plus
 # this reviewed operational/CPU-layout release, never relabel the old draft.
 initial=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
 original_gate_ref=rd(initial/'control/EXECUTION_PLAN.json')['gate0_release']
 original_gate=rd(pinned(original_gate_ref));build=rd(root/'control/BUILD_PROFILE.json')
 need(original_gate['status']=='PASS'and set(original_gate['qualified_modes'])==set(plan['qualified_modes'])
      and original_gate['binary_sha256']==build['binary_sha256']and original_gate['core_commit']==build['core_commit']
      and original_gate['source_lifecycle_independent_review']=='PASS'and original_gate['CPU_lifecycle_qualification']=='PASS',
      'ORIGINAL_REAL_CORE_ORACLE_QUALIFICATION_REQUIRED')
 gate0=dict(schema='DTC_CLEAN_SUCCESSOR_EXPLICIT_GATE0_V1',status='PASS',qualified_modes=plan['qualified_modes'],
    binary_sha256=build['binary_sha256'],core_commit=build['core_commit'],source_lifecycle_independent_review='PASS',
    CPU_lifecycle_qualification='PASS',original_mechanism_qualification=original_gate_ref,
    new_operational_source_review=release['independent_live_review'],new_private_CPU_artifacts=release['cpu_preparation'],
    actual_model_starts=0,not_a_relabel_of_old_pending_gate=True)
 gate0path=root/'control/CLEAN_SUCCESSOR_GATE0.fixed.json';put(gate0path,gate0)
 plan['gate0_release']=dict(path=str(gate0path),sha256=sha(gate0path))
 resources=load(dict(path=str(root/'tools/oracle_resources.py'),sha256=sha(root/'tools/oracle_resources.py')),
                'CLEAN_FINALIZER_TRUE_MODE_RELEASES')
 witnesses=[]
 for mode in plan['qualified_modes']:
  try:witnesses.append(resources.verify_mode_extension_receipt(plan,mode))
  except resources.WaitInitialRuntimeGate:pass
 need(witnesses,'NO_ACTUAL_MODE_PLUS_SHARED_OFF8_GATE2')
 gate2=dict(schema='DTC_CLEAN_SUCCESSOR_TRUE_GATE2_V1',status='PASS',released_modes=[v['mode']for v in witnesses],
    fixed8_matched_OFF_and_mode_strict_archive_restore_independently_reviewed=True,
    independent_real_mode_witnesses=witnesses,unreleased_modes_remain_held=True)
 gate2path=root/'control/CLEAN_SUCCESSOR_GATE2.fixed.json';put(gate2path,gate2)
 plan['gate2_release']=dict(path=str(gate2path),sha256=sha(gate2path))
 sourcepins=[x for x in plan['source_pins']if Path(x['path'])not in[NATIVE]]
 for ref in [lease_ref,release['guard'],release['runtime_adapter'],release['artifact_finalizer'],release['RSS_history_adapter'],
             release['engine_adapter'],release['independent_live_review'],release['cpu_preparation'],parent['controller'],
             plan['gate0_release'],plan['gate2_release']]:
  pinned(ref)
  if ref not in sourcepins:sourcepins.append(ref)
 plan,candidate=bind_metadata(plan,candidate,parent,lease_ref,sourcepins,route_ref,None)
 plan['clean_owner_guard']=release['guard'];plan['clean_operational_generation']=dict(kind='SERIAL_LEGAL_DTC_MAIN_SUCCESSOR',
   pid=parent['pid'],start_ticks=parent['start_ticks'],old32_new_starts=0,old_q_lease_journal_modified=False,
   no_same_PID_exec_continuation=True)
 plan_ref=dict(path=str(root/'control/EXECUTION_PLAN.json'),sha256=hashlib.sha256(encoded(plan)).hexdigest())
 candidate['execution_plan_sha256']=plan_ref['sha256']
 candidate['controller_path']=str(root/'tools/oracle_ops.py');candidate['controller_sha256']=sha(root/'tools/oracle_ops.py')
 forward(root/'control/EXECUTION_PLAN.json',plan,preimages)
 put(root/'control/REGISTRY_REQUEST_CANDIDATE.json',candidate)
 approval=root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'
 request=rd(approval)
 need(request['authority_commit']=='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
      and request['exact_budget']==96 and set(request['cohorts'])==set(candidate['admitted_specs']),
      'UNCHANGED_ORIGINAL_USER_SCIENTIFIC_APPROVAL_DOMAIN')
 auth=dict(schema='DTC_ORACLE_SCIENCE_AUTHORIZATION_V1',explicit_user_approval=True,
    ready_for_registration=True,owner_bindings_ratified=True,target_resource_policy_ratified=True,
    authority_commit=request['authority_commit'],stage='remaining24',approval_request_sha256=sha(approval),
    budgets=dict.fromkeys(candidate['admitted_specs'],1),
    operational_release_review=release['independent_live_review'],
    source_of_scientific_authority='Original18b user authorization; new private operational binding only')
 need(auth['explicit_user_approval']is True and set(auth['budgets'])==set(candidate['admitted_specs'])
      and all(v==1 for v in auth['budgets'].values()),'EXACT96_ORIGINAL_USER_SCIENCE_AUTHORIZATION')
 put(root/'control/SCIENCE_AUTHORIZATION.json',auth)
 guard=load(release['guard'],'CLEAN_FINALIZER_ACTUAL_LEASE_GUARD');guard.verify_parent_lease(plan)
 native=load(dict(path=str(root/'tools/oracle_native.py'),sha256=sha(root/'tools/oracle_native.py')),'CLEAN_FINALIZER_LAYOUT_ONLY')
 native.verify_launcher_layout(plan)
 need(sha(root/'control/EXECUTION_PLAN.json')==plan_ref['sha256'],'FINAL_BIND_PLAN_PIN')
 for ref in release['immutable_historical_refs']:pinned(ref)
 receipt=dict(status='PASS_NEW_PRIVATE_CPU_LAYOUT_SOURCE_RESOURCE_QUALIFICATION',root=str(root),plan=plan_ref,
    candidate=dict(path=str(root/'control/REGISTRY_REQUEST_CANDIDATE.json'),sha256=sha(root/'control/REGISTRY_REQUEST_CANDIDATE.json')),
    parent_pid=parent['pid'],parent_start_ticks=parent['start_ticks'],source_scientific_projection_equal=True,
    native_route_planned=route_receipt,scientific_models_started=0,science_registrations=0)
 put(root/'control/CLEAN_PARENT_FINAL_BIND_CPU_QUALIFICATION.fixed.json',receipt);return receipt
def install_reviewed_native_route(release,parent):
 need(release['actual_execution_authorized']is True,'NO_ACTUAL_ROUTE_RELEASE')
 root=Path(release['execution_root']);need(root==NEWROOT,'ONLY_NEW_PRIVATE_ROOT')
 plan=rd(root/'control/EXECUTION_PLAN.json');g=load(release['guard'],'CLEAN_ROUTE_LIVE_OWNER_GUARD');g.verify_parent_lease(plan)
 p=root/'control/CLEAN_PARENT_BIND_PREIMAGES';proof=rd(p/'ROUTE_PROJECTION.fixed.json')
 need(sha(NATIVE)==proof['before_sha256'],'CONCURRENT_NATIVE_ROUTE_CHANGE_FORWARD_HOLD')
 before=(p/'NATIVE_ROUTE_PREIMAGE.bytes').read_bytes();after=(p/'NATIVE_ROUTE_PLANNED.bytes').read_bytes()
 need(NATIVE.read_bytes()==before and hashlib.sha256(after).hexdigest()==proof['after_sha256'],
      'EXACT_ROUTE_PREIMAGE_AND_PROJECTION_PINS')
 block=(root/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();need(route_projection(before,block)==after,'EXACT_ONLY_NEW96_ROUTE')
 tmp=NATIVE.with_name('.native.CLEAN_SUCCESSOR.writing');put(tmp,after);tmp.chmod(NATIVE.stat().st_mode&0o777)
 os.replace(tmp,NATIVE)
 need(sha(NATIVE)==plan['installed_native_route']['sha256'],'POST_INSTALL_ROUTE_PIN')
 return dict(status='PASS_ADDITIVE_EXACT_NEW96_NATIVE_ROUTE',before_sha256=proof['before_sha256'],after_sha256=sha(NATIVE))

if __name__=='__main__':print(json.dumps(dict(status='CPU_FINALIZER_CANDIDATE_ONLY',registrations=0,models=0)))
