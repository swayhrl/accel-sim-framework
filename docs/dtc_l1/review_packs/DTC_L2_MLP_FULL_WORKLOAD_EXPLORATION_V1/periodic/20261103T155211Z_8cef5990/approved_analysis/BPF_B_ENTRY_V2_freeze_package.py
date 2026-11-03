"""Freeze own read-only delivery metadata, not registry or production config."""
import pathlib,json,hashlib,datetime
P=pathlib.Path;D=P(__file__).parent
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
prefix=read(D/'CPU_NATIVE_PREFIX_QUALIFICATION.json');owner=read(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json')
assert prefix['count']==23 and owner['count']==11 and not prefix['production_release_eligible']and not owner['production_release_eligible']
cfg=read(P(prefix['fixtures'][0]['root'])/'CONFIG.json')
for role,path in cfg['source_paths'].items():assert sha(path)==cfg['qualified_sources'][role]
for path,h in cfg['expected_pins'].items():assert sha(path)==h
for path,h in prefix['qualified_B_sources'].items():assert sha(path)==h
for path,h in prefix['E_sources_used'].items():assert sha(path)==h
for path,h in owner['source_sha256'].items():assert sha(path)==h
out=dict(schema='B_STRACE_FUTURE_ENTRY_V2_DELIVERY',status='CPU_COMPONENT_QUALIFIED_PENDING_MAIN_AND_ACTUAL_CANARY',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),qualified_sources=cfg['qualified_sources'],source_paths=cfg['source_paths'],expected_pins=cfg['expected_pins'],B_native_prefix=dict(path=str(D/'CPU_NATIVE_PREFIX_QUALIFICATION.json'),sha256=sha(D/'CPU_NATIVE_PREFIX_QUALIFICATION.json'),count=23),B_owner_closure=dict(path=str(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json'),sha256=sha(D/'CPU_OWNER_DISPATCH_QUALIFICATION.json'),count=11),formal_exclusion_contract=dict(path=cfg['exclusion_contract_path'],sha256=cfg['exclusion_contract_sha256']),E_additional_qualification=dict(path=str(D.parents[1]/'E/strace_bpf_strict_consumer_v2/CPU_QUALIFICATION.json'),sha256=sha(D.parents[1]/'E/strace_bpf_strict_consumer_v2/CPU_QUALIFICATION.json')),future_primary_policy='NONE',preserved_original_paths_and_sources=True,original_physics_leaf_not_run=True,all_model_launches_mocked=True,remaining_gates=['Main joint QA and source/readback review','Main independent engineering registry/technical credits and official CPU2 scope append','Main consumer and worker installation under sole owner','Actual paired control/BPF activation and original physics strict/natural lifecycle','Actual 164 archive/native2128 restore and observation sidecar replay','Actual cycles and host impact assessment before any new broad policy'],production_release_eligible=False,actual_model_starts=0,registry_changes=0,production_changes=0)
put(D/'DELIVERY.json',out)
files=['strace_entry.py','bpf_frontend.py','native-entry/bin/experiment','cpu_prefix_fixture.py','qualify_native_prefix.py','qualify_owner_dispatch.py','freeze_package.py','SCHEMA_DRAFT.json','INTERFACE.json','README.md','CPU_NATIVE_PREFIX_QUALIFICATION.json','CPU_OWNER_DISPATCH_QUALIFICATION.json','DELIVERY.json']
manifest=dict(schema='B_STRACE_FUTURE_ENTRY_V2_MANIFEST',status='FROZEN_CPU_CANDIDATE_NO_DEPLOYMENT',members=[dict(path=str(D/f),relative_path=f,sha256=sha(D/f),bytes=(D/f).stat().st_size)for f in files],referenced_E_sources={r:dict(path=cfg['source_paths'][r],sha256=cfg['qualified_sources'][r])for r in ['extra_strict','consumer']},production_release_eligible=False)
put(D/'MANIFEST.json',manifest);print(json.dumps(dict(manifest=str(D/'MANIFEST.json'),manifest_sha256=sha(D/'MANIFEST.json'),delivery_sha256=sha(D/'DELIVERY.json'),members=len(files),qualified_sources=cfg['qualified_sources'])))
