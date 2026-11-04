from pathlib import Path
import hashlib,json,datetime,ast
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');A=P/'research/performance_first_v4_20261104_v1/track_a';O=A/'private_main_integration'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=Path(p).stat().st_size)
def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
index=read(O/'PRIVATE_GRAPH_INDEX.json');regpath=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reg=read(regpath);anchors=[]
for g in index['graphs']:
 for row in read(Path(g['runtime'])/'FAMILY_SCOPE.json')['points']:
  r=row['accepted_same_mode_ref'];point=read(r['accepted_point_ref']['path']);namespace=r.get('request')or point.get('goal','EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1');actual=reg['registered_future_requests'][namespace]['consumed'].get(r['cohort'],{})
  assert actual.get('state')=='CLOSED_ACCEPTED'and actual.get('accepted_point_ref')==r['accepted_point_ref']
  anchors.append(dict(candidate_cohort=row['id'],reference_cohort=r['cohort'],official_namespace=namespace,state=actual['state'],exact_point_ref=actual['accepted_point_ref']))
write(O/'CURRENT_ACCEPTED_REFERENCE_POPULATION.json',dict(schema='EP_PFV4_A1_A3_CURRENT_ACCEPTED_REF_REVIEW_V1',registry_observation_ref=ref(regpath),rows=anchors,registry_modified=False,archive_or_Trace_body_rehash=False))
oldmanifest=A/'DELIVERY_MANIFEST.json';old=read(oldmanifest)
assert sha(oldmanifest)=='16e71e3887c60eba1b788473e9d0319506b52d087687149e0b85b857e998b4cf'
assert all(sha(f['path'])==f['sha256']for f in old['files'])
write(O/'OLD_REQUEST_PACK_FROZEN_CHECK.json',dict(status='PASS',prior_manifest_ref=ref(oldmanifest),prior_file_count=len(old['files']),all_prior_file_bytes_unchanged=True))
write(O/'MAIN_APPROVAL_INSTALL_DELTA.json',dict(schema='EP_PFV4_A1_A3_MAIN_REVIEW_INSTALL_DELTA_V1',status='PRIVATE_ENGINEERING_DELTA_PASS_READY_FOR_MAIN_REVIEW_NO_SCIENCE_AUTHORITY',graphs=index['graphs'],A1_priority=True,A3_optional_separate_approval=True,A2_excluded_and_conditional_WV_eligibility_gap=True,engineering_ready=dict(full43_positive_points=4,native_Source78_pins=22,extra_helper_dependencies=5,current_domain_and_dependencies=True,claim_before_schema_negative_tests=4,metadata_control_negative_tests=32,actual_private_Native_prepare_HOLDs=4,original_monitor_AST_preserved=True,original_mode_aware_parser_functions_preserved=True,full282_hardware_background_vs_prior_actual_echo='All281 non-trace values exactly equal same Source78 G64x8 mode actual echo; trace rebound to own accepted input',current_genuine164_storage_and_Source_clean=True),science_state=dict(real_registered_budget=0,real_consumes=0,model_starts=0,shared_installs=0,old_geometry_mode_CPU_tests_rerun=0,applicationNI_new_runs=0),Main_only_release_steps=[
 'Review this private graph manifest and finite metadata delta evidence; rebind engineering review without rerunning unchanged Source/geometry/mode CPU tests.',
 'Independently select A1 request2 or optional A3 request2. Fresh exact scientific authorization must identify request_id, exactly its two allowed cohorts and Source5; old8 approval and approval from another request are rejected.',
 'Materialize fresh authorization_ref into exactly the selected two private candidate Specs; their application_budget=approved_launches=1 are conditional schema cardinalities, not registered approvals. Current authority documents explicitly approve0.',
 'Main alone installs an additive exact-cohort shared Native route and immutable reviewed route contract/owned graph, then fills NATIVE_ENTRY_ROUTE_V4.json with exact installed baseline/entry/frontend/guard pins and activation receipt. No source/native/shared file was modified by this lane.',
 'Main alone registers exact fresh budget2, own admitted Spec SHAs, authorization_ref, native_entry_ref and runtime_versions(engine/common) under that selected request_id. Preserve all foreign rows and consumed terminal points.',
 'Refresh native boot/mount/CPU binding and current dynamic RAM/SSD/NAS commitments. Call private_main_dispatcher.claim so schema+fresh authorization run before claim writes; run_native repeats bound-CPU/current-domain/native dependencies schema before helper/output/locks/transaction/fork.',
 'Dispatch through sole Native entry; existing verify_actual/limits/process-tree/syscall/lossless output/resource monitor, terminal mode-aware parser and SOURCE_KEEP archive/two-restore flow remain intact. No auto retry/refund.'
],not_release_blockers=['application_NI=NOT_MEASURED and B0_M0a_application_NI=NOT_PROVEN_HELD_ON remain scientific limits, not a new qualification rerun requirement','A2 missing 3MM WV input/mode eligibility never blocks independent A1/A3'],actual_remaining_release_gates=['fresh exact per-request scientific approval','Main immutable additive route installation and exact budget registration','fresh dispatch binding and dynamic resource admission'],no_new_model_needed_for_engineering=True))
(O/'README.md').write_text("""# Source78 private Main integration delta
A1 Stencil and optional independent A3 Transpose each have a complete request2 consumer graph under their own runtime/execution roots. PRIVATE_GRAPH_INDEX.json identifies all four conditional exact Specs. This version leaves the prior Track A requests and delivery manifest byte-for-byte frozen.

Four positive engineering_spec_for paths passed the strict full43 shape, exact Source78 original22 native pins, five independently pinned helper dependency rows, fresh native boot/mount, current resolved dependency bytes, full282 identity, original mode/geometry rules, real per-mode accepted input eligibility and prior Source CPU evidence. The two current inputs also passed genuine164 mount, recorded full member stat/resolution and small whole-commandlist SHA checks; no Trace body was read or hashed. Source worktrees were checked at exact accepted commits and clean.

The old Source78 G64x8 actual282 CPU receipt is reused with an explicit stronger rebind: every non-trace option (281) equals the matching S/WV prior actual echo; only the exact new accepted input trace path differs. Source/mode/geometry CPU qualification and all original parser/monitor protections are retained. No old126 suite, geometry tests or application NI was rerun.

Thirty-two control/schema metadata negatives were rejected, including cross-Source, missing native/helper pin, malformed limits/domain, altered282 background and cross-request cohorts. Actual private dispatcher calls prove schema precedes claim writes and hold without approval. All four actual private Native prepare commands exited2 specifically for missing fresh request2 scientific authorization after engineering schema passed. Shared Native/registry/epoch preimages remained unchanged. The event loop/verify_actual/resource_gate/fresh_input/dispatch_binding AST matches the original, except the new bound-CPU strict43 call before helpers/consume/fork; all mode-aware terminal parser function ASTs are unchanged.

The private Main one-start Spec fields are conditional contract cardinalities. Real approval/registration/consumption remains0; USER_AUTHORIZATION.json explicitly approves0. Only Main may finalize fresh authorization refs, install an exact additive route, register budget2 and dispatch after current resource admission. A3 remains optional and separate; A2 remains outside this graph with its real WV input/mode eligibility gap. Application NI_NOT_MEASURED is preserved as a limit, not imposed as a new launch gate. See MAIN_APPROVAL_INSTALL_DELTA.json for exact release steps.
""")
# Verify private immutable references and all candidate key completeness without chasing genuine input bodies.
errors=[];count=0
for p in sorted(O.rglob('*.json')):
 if p.name=='PRIVATE_MAIN_INTEGRATION_MANIFEST.json':continue
 def walk(x):
  global count
  if isinstance(x,dict):
   if isinstance(x.get('path'),str)and isinstance(x.get('sha256'),str)and x['path'].startswith(str(O)+'/'):
    count+=1
    if not Path(x['path']).is_file()or sha(x['path'])!=x['sha256']:errors.append(dict(referrer=str(p),target=x['path']))
   for y in x.values():walk(y)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(read(p))
assert not errors,errors
write(O/'FINAL_PRIVATE_REFERENCE_AUDIT.json',dict(status='PASS',owned_references_checked=count,drift=errors,old_pack_unchanged=True))
files=[dict(member=str(p.relative_to(O)),**ref(p))for p in sorted(O.rglob('*'))if p.is_file()and '__pycache__'not in str(p)and p.name!='PRIVATE_MAIN_INTEGRATION_MANIFEST.json']
manifest=dict(schema='EP_PFV4_SOURCE78_PRIVATE_MAIN_INTEGRATION_DELIVERY_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FINITE_ENGINEERING_DELTA_PASS_NO_SCIENTIFIC_AUTHORITY',entry_ref=ref(O/'PRIVATE_GRAPH_INDEX.json'),review_delta_ref=ref(O/'MAIN_APPROVAL_INSTALL_DELTA.json'),mandatory_A1_requested_starts=2,optional_A3_requested_starts=2,A2_unchanged_conditional=True,approved_registered_consumed_starts=0,Source_KEEP=True,files=files)
write(O/'PRIVATE_MAIN_INTEGRATION_MANIFEST.json',manifest)
print(json.dumps(dict(status='PASS',manifest_ref=ref(O/'PRIVATE_MAIN_INTEGRATION_MANIFEST.json'),files=len(files),bytes=sum(x['bytes']for x in files),private_references_checked=count,old_request_pack_unchanged=True)))

