"""Independent read-only package/source review. Never runs qualification suites."""
import datetime,hashlib,json,pathlib
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
O=A/'agents/E/main_joint_bpf_review_v1';J=A/'coordinator/strace_bpf_main_joint_cpu_v1';S=A/'coordinator/bpf_canary_orchestration_v2'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(J/'COMBINED_CPU_QUALIFICATION.json')=='6ba5386b0e5e9fdbea15c2e7aa102256358ebabdb5ca152ccf128a6d1ec8a3aa'
qa=read(J/'COMBINED_CPU_QUALIFICATION.json');manifest=read(J/'MANIFEST.json')
checked=[]
for name,e in manifest['files'].items():
 path=J/name;assert sha(path)==e['sha256']and path.stat().st_size==e['bytes'];checked.append(str(path))
package_members={}
for label,root in [('B',A/'agents/B/strace_bpf_future_entry_v2'),('E',A/'agents/E/strace_bpf_strict_consumer_v2')]:
 m=read(J/(label+'_MANIFEST.json'));entries=m.get('files',m.get('entries',m.get('members')))
 if isinstance(entries,dict):entries=[dict(v,path=k)for k,v in entries.items()]
 pins=[]
 for e in entries:
  name=e.get('relative_path',e.get('path',e.get('name')));path=root/name
  assert sha(path)==e['sha256'];assert path.stat().st_size==e.get('bytes',path.stat().st_size);pins.append(dict(path=str(path),sha256=e['sha256']))
 package_members[label]=pins
runtime=[]
for role,h in qa['qualified_sources'].items():
 assert sha(J/('source_'+role+'.txt'))==h==sha(qa['original_source_paths'][role])
 destination=P(qa['source_paths'][role]);runtime.append(dict(role=role,sha256=h,original=qa['original_source_paths'][role],future_native_path=str(destination),future_path_exists=destination.exists()))
for path,h in qa['expected_pins'].items():assert sha(path)==h
for r in qa['reference_results_verified']:
 p=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis')/(r['reference']+'.RESULT.json');assert sha(p)==r['reference_result_sha256']and read(p)['cycles']==r['cycles']
assert qa['status']=='PASS'and qa['qualification_scope']=='CPU_COMPONENTS_ONLY_FOR_FRESH_ENGINEERING_CANARIES'
assert qa['actual_native_canary_qualified']is False and qa['production_release_eligible']is False and qa['future_primary_policy']=='NONE'
assert qa['model_starts']==qa['production_changes']==qa['registry_changes']==0
assert sha(S/'scope_bridge.py')=='2a82ae5fdab944801422e7f9c4a236adc4221f1b90675282b2434f42c3997e6d'
sq=read(S/'SCOPE_BRIDGE_CPU_QUALIFICATION.json');assert sq['count']==21 and sq['status']=='PASS_PURE_SCOPE_COMPONENTS_NOT_INSTALLED'and sq['full_native_prefix_qualification']is False
review=dict(schema='E_MAIN_JOINT_BPF_READONLY_REVIEW_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 status='PASS_CPU_COMPONENT_SOURCE_AGGREGATION_WITH_REQUIRED_INSTALL_GATES',actual_execution_pass_claimed=False,production_deployment_approved_by_this_review=False,
 reviewed_main_QA_sha256=sha(J/'COMBINED_CPU_QUALIFICATION.json'),reviewed_main_manifest_sha256=sha(J/'MANIFEST.json'),
 verified_joint_members=len(checked),verified_component_members={k:len(v)for k,v in package_members.items()},package_member_pins=package_members,runtime_mapping=runtime,
 expected_original_pins_checked=len(qa['expected_pins']),scope_source_sha256=sha(S/'scope_bridge.py'),scope_CPU_QA_sha256=sha(S/'SCOPE_BRIDGE_CPU_QUALIFICATION.json'),
 findings=[
  'Main source text/old package members/runtime source hashes and reference SHA/cycles agree; future native-path mapping is a plan, not proof of installed source or owner routing.',
  'PASS/native_prefix/extra/consumer_archive flags are bounded by explicit CPU_COMPONENTS_ONLY scope. Actual canary/production release flags remain false; copied-archive and physics-leaf caveats are explicit, so no actual-run or simulation-speedup conclusion is supported.',
  'Scope_v2 validates exact4/current admitted SHA/frozen science projection, unbound canonical CPU and lineage/authorized rows. It strips only announced exact engineers outside the unchanged R2 wrapper, hashes back to the previous view, rejects unknown engineer roles and contaminated summaries, and preserves nonfinal guarded HOLD on errors.',
  'Official resource amendments may change current canonical RAM fields; actual host CPU belongs only to independently hashed resolved DB. Initial MATRIX SHA is provenance, not an immutable future matrix pin.',
  'Source package integrity review is not transaction/owner-install qualification. New registration/CPU2 append/priority adapters need their own source/receipt checks and sole-owner staged integration.'
 ],required_install_gates=[
  'Verify complete B/E/runtime/QA/exclusion/source pins at genuine164 and the new native directory, including executable entry and exact path layout. Real byte/SHA readback with matching QA/qualified_sources/expected_pins is sufficient; no new Git/HTTPS prerequisite is imposed.',
  'Main sole owner: exact4 fresh registered identities, legal additional technical allowance, committed/reconciled transaction, no reused/spent UUID/reset/refund/old-budget borrowing; current admitted spec plus canonical host_cpu=None and resolved DB/hash.',
  'Official exact4 CPU2 allowed append and q operational record with extras preserved; old cfg/source/old-generation snapshots retained. Full forecast, pressure/CPU/claims/disk/IO/fresh resource and lease gates remain unchanged. Any narrow aging priority exception must be explicitly versioned.',
  'Real SCOPE/MATRIX exclude all exact engineers/unknown engineer roles. Outer engineering adapter strips to the exact prior R2 view, preserving existing R2 whitelist, journal/final guards and full35 primary-parent rules. Canonical engineer RESULT is genuine all-strict/archived output, not a release stub.',
  'On actual frame-private consumer install E safe route first; verify same-object actual ops.post path, old load/finish/put refs and exact non-scope delegation. Then B N-only scoped worker/private absolute entry. Preserve shared native46/fa3/CPU2 source bytes and healthy attempts. Reverse restore B before E; do not remove a consumed-HOLD strict route silently.',
  'Use real qualified config/QA/readback, q.qualification_only absent/false and production root; reject CPU stand-ins. Only exact4 engineer modes and future_primary_policy NONE may be active. DEFAULT_CONTROL is deliberate, never fallback.',
  'Before treating real canaries as passed: actual PID/start/tracer/baseline-mode proof, all original physics plus CPU2 plus IO plus observation strict, exact frozen reference counts/cycles, genuine true164 archive/native2128 restore plus required new file SHA, and host-impact evidence. Unknown/fallback/failure retains its consumed identity unaccepted.',
  'Broad primary or new-combination BPF adoption is not authorized by these CPU flags; it requires the subsequent real-canary review and separately qualified generation.'
 ],limits=['No old24/11/74 or scope21 suite rerun; source/JSON/hash review only.','No actual model, registration, controller mutation, signals, Git or installation.','Fresh4 registration/CPU2-append/sole-owner integration candidates are not independently certified by this source-only joint aggregation review.'],model_starts=0,registry_writes=0,production_changes=0,Git_accessed=False)
(O/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
m=dict(schema='E_MAIN_JOINT_BPF_REVIEW_MANIFEST_V1',status=review['status'],files=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(O.iterdir())if p.is_file()and p.name!='MANIFEST.json'])
(O/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(status=review['status'],B_members=len(package_members['B']),E_members=len(package_members['E']),REVIEW_sha256=sha(O/'REVIEW.json'),MANIFEST_sha256=sha(O/'MANIFEST.json'))))
