from pathlib import Path
import hashlib,importlib.util,json,os,sys,datetime
sys.dont_write_bytecode=True
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');A=P/'research/performance_first_v4_20261104_v1/track_a';O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text())
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
helper=Path(sys.argv[1]);helper_sha=sys.argv[2];assert sha(helper)==helper_sha
graphs=read(A/'private_main_integration/PRIVATE_GRAPH_INDEX.json')['graphs'];outputs=[]
for g in graphs:
 lane=g['lane'];H=O/lane;H.mkdir(exist_ok=True);wrapper=H/'resources_request2_v4.py'
 wrapper.write_text('''# Read-only exact request2 adapter to Main V4 qualified resource wiring.
import pathlib,hashlib,importlib.util
PATH=pathlib.Path('''+repr(str(helper))+''');SHA='''+repr(helper_sha)+''';REQUEST='''+repr(g['request_id'])+'''
def shared():
    if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('Main V4 qualified resource adapter drift')
    sp=importlib.util.spec_from_file_location('main_v4_exact_request_resource',PATH)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
    if s.get('current_request')!=REQUEST:raise ValueError('cross-family resource snapshot')
    return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
''')
 # Supplement HostQ retains the original review limitations and exact immutable source/monitor/parser.
 oldhostq=read(g['hostq_ref']['path']);hostq=dict(oldhostq)
 hostq['prior_private_hostq_ref']=g['hostq_ref'];hostq['resource_wiring_revision']='MAIN_V4_ADDITIVE_EXACT_NEW_SCOPE_REQUEST_ROOTS'
 hostq['modules']=oldhostq['modules']+[ref(helper),ref(wrapper)]
 hostq['prior_qualification_scope_limit']='Original full43/monitor/parser tests did not exercise resources_request2.snapshot; old unknown V3 scope defect reproduced and disclosed.'
 hostq['actual_resource_snapshot_evidence_ref_pending']=True
 hq=H/'HOST_RESOURCE_WIRING_QUALIFICATION_SUPPLEMENT.json';write(hq,hostq)
 # New immutable revision candidates; no overwrite or installation at the old hardbound spec_path.
 specs=[]
 for r in g['candidate_specs']:
  s=read(r['path']);s['prior_frozen_private_spec_ref']=r;s['resource_module_ref']=ref(wrapper);s['host_qualification_ref']=ref(hq)
  s['resource_wiring_supplement']=dict(status='REVISED_CANDIDATE_NOT_INSTALLED_AT_ENGINE_SPEC_PATH',Main_helper_ref=ref(helper),old_resource_wrapper_ref=read(r['path'])['resource_module_ref'],source_engine_and_dispatcher_bytes_unchanged=True)
  s['pinned_files'][str(wrapper)]=sha(wrapper);s['pinned_files'][str(helper)]=helper_sha;s['pinned_files'][str(hq)]=sha(hq)
  dest=H/'spec_revision_candidates'/(s['cohort']+'.json');write(dest,s);specs.append(ref(dest))
 sp=importlib.util.spec_from_file_location('resource_delta_'+lane,wrapper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 snap=m.snapshot();assert snap.get('current_request')==g['request_id'];assert snap.get('resource_admission_is_not_science_permission')is True
 receipt=H/'ACTUAL_READONLY_SNAPSHOT.json';write(receipt,dict(schema='EP_PFV4_ACTUAL_NEW_REQUEST_RESOURCE_WIRING_SNAPSHOT_V1',status='REAL_SNAPSHOT_RETURNED_NO_UNKNOWN_SCOPE',lane=lane,request_id=g['request_id'],wrapper_ref=ref(wrapper),Main_helper_ref=ref(helper),snapshot=snap,admission_executed=False,science_permission=False,model_starts=0))
 # Exact same admit function remains in Main additive loader; no permission is inferred from a snapshot.
 supplement=dict(schema='EP_PFV4_RESOURCE_OWNED_GRAPH_SUPPLEMENT_V1',lane=lane,request_id=g['request_id'],prior_private_graph=g,resource_wrapper_ref=ref(wrapper),Main_helper_ref=ref(helper),host_qualification_supplement_ref=ref(hq),candidate_spec_revision_refs=specs,owned_runtime_pins_append=[ref(wrapper),ref(helper),ref(hq)],actual_snapshot_ref=ref(receipt),actual_native_entry_and_dispatcher_refs_unchanged=True,installed=False,real_budget_registered_or_consumed=0)
 write(H/'MAIN_INSTALL_OWNED_GRAPH_SUPPLEMENT.json',supplement);outputs.append(supplement)
oldcheck=read(O/'OLD_RESOURCE_DEFECT_AND_FROZEN_PREIMAGE.json')
for old in oldcheck['frozen_manifests']:
 assert sha(old['manifest_path'])==old['sha256']
 assert all(sha(f['path'])==f['sha256']for f in read(old['manifest_path'])['files'])
write(O/'RESOURCE_FOLLOWUP_INDEX.json',dict(schema='EP_PFV4_A1_A3_RESOURCE_FOLLOWUP_INDEX_V2',status='ACTUAL_READONLY_SNAPSHOT_WIRING_PASS_NOT_INSTALLED',graphs=outputs,prior60_and111_file_bytes_unchanged=True,original_qualification_limit='Schema and unchanged monitor/parser pass do not imply previous resource wrapper worked; actual old snapshot bug is documented.',Main_required_install_binding='Main must bind each new Spec revision to the actual installed consumer spec_path/ROOT and admitted SHA. This supplement does not silently replace the old frozen execution Spec or alter entry/dispatcher source.',science_permission=False,shared_route_registry_model_changes=0))
(O/'README.md').write_text('''# Resource wiring follow-up
The original A1/A3 request wrappers failed real snapshot calls with unknown V3 scope. Earlier schema/monitor qualification did not cover this resource scope lookup. The defect is reproduced in OLD_RESOURCE_DEFECT_AND_FROZEN_PREIMAGE.json.

This separate supplement pins Main's additive V4 helper and two exact-request wrappers. Each real read-only snapshot executes the helper for its actual A1/A3 request and records the full result. Snapshot success establishes wiring; it does not grant scientific permission or claim that current resource admission would pass. Existing foreign metadata/resource constraints remain visible.

Spec revision candidates change resource_module_ref, add the private Host resource qualification supplement and corresponding owned pins; Source78, original282 options, inputs, monitor, parser, entry and dispatcher sources are unchanged. Original60/111 frozen file bytes remain intact. No old32-negative suite, eventloop or geometry tests were repeated. There were no shared Native, registry, budget or model changes.

Main must publish/install the selected revised Spec at the actual consumer spec_path/ROOT and bind its admitted SHA and owned graph. New sidecar Spec files alone do not change what the old hardbound entry reads. A1 remains2starts; optional A3 remains a separate2start decision; A2 remains conditional and unchanged.
''')
files=[dict(member=str(p.relative_to(O)),**ref(p),bytes=p.stat().st_size)for p in sorted(O.rglob('*'))if p.is_file()and '__pycache__'not in str(p)and p.name!='RESOURCE_FOLLOWUP_MANIFEST.json']
write(O/'RESOURCE_FOLLOWUP_MANIFEST.json',dict(schema='EP_PFV4_A1_A3_RESOURCE_FOLLOWUP_DELIVERY_V2',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='REAL_READONLY_RESOURCE_SNAPSHOT_WIRING_PASS_CANDIDATES_NOT_INSTALLED',Main_helper_ref=ref(helper),index_ref=ref(O/'RESOURCE_FOLLOWUP_INDEX.json'),files=files,model_starts=0,budget_or_shared_writes=0,prior60_111_files_unchanged=True))
print(json.dumps(dict(status='PASS',manifest_ref=ref(O/'RESOURCE_FOLLOWUP_MANIFEST.json'),request_snapshots=[dict(lane=o['lane'],ref=o['actual_snapshot_ref'])for o in outputs],files=len(files))))

