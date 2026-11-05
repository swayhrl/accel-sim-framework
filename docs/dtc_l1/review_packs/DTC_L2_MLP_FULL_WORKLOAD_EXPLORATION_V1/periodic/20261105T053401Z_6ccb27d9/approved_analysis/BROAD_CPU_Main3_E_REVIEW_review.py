"""One-shot source/config review only. Never calls candidate apply/owner API."""
import pathlib,json,hashlib,importlib.util,copy,ast,datetime,sys
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');M=R/'control/operational_amendments/broad_shared_cpu_v1'
CP=M/'actual_install_v2/CONFIGURATION.json';CPSHA='0bee1d191bb0f18f8fb3cecb71d4f6f9c191efe9a6afc678eb02b83102d71612';SSHA='7b4c5f4312fb95f6ba770cb366f82bffeeff13396e5c6a3a913dd5e133216a7f'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 assert not p.exists(),'Immutable review exists'
 p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('Readonly review: no process/signal')
sys.addaudithook(audit)
assert sha(CP)==CPSHA;cfg=read(CP);assert sha(cfg['installer_path'])==cfg['installer_sha256']==SSHA
assert len(cfg['source_pins'])==107
pins=[dict(path=p,sha256=sha(p),expected=h)for p,h in cfg['source_pins'].items()];assert all(x['sha256']==x['expected']for x in pins)
binding=CP.parent/'MAIN_SOURCE_BINDING.json';assert sha(binding)=='5e487c667a9a9ad31969fcbe1493d983934de4718df84eff3bac1a7bed431e21'
assert read(binding)==dict(schema='CPU_SHARED_MAIN_HASH_BOUND_APPLY_BRIDGE_V1',configuration_path=str(CP),configuration_sha256=CPSHA,installer_path=cfg['installer_path'],installer_sha256=SSHA)
rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
assert sha(cfg['resource_configuration_path'])=='a310313cf5c94e4e80391c772891711a13cde1abd5260f24801488313908c01e'
assert sha(cfg['observation_configuration_path'])=='7f3966c279c157a1217b62dd0cc137138edb0ca3f06a853256972d08970e245c'
assert set(cfg['modules'])=={'library','producer','consumer','owner_frame','IR_view'}
assert cfg['modules']['library']==rcfg['source_paths']['library']and cfg['modules']['producer']==rcfg['source_paths']['owner']==ocfg['source_paths']['producer']and cfg['modules']['consumer']==rcfg['source_paths']['consumer']==ocfg['source_paths']['consumer']
for path in cfg['modules'].values():assert cfg['source_pins'][path]==sha(path)
for contract in [rcfg,ocfg]:
 for role,path in contract['source_paths'].items():assert sha(path)==cfg['source_pins'][path]==contract['qualified_sources'][role]
source_dir=A/'coordinator/BROAD_SHARED_CPU_MAIN3_SOURCE_V1';delta=source_dir/'FINAL_NESTED_PREARM_DELTA_QUALIFICATION.json';assert sha(delta)=='73ca712746b1551cc726c3999116ea6ba59b0bd0d712f9a193aed2ea47f35b9f'
dq=read(delta);assert dq['status']=='PASS'and dq['source_sha256']==SSHA and dq['count']==9 and dq['old83_real_extracted_prearm_counterexample_confirmed']is True
current=ast.parse(P(cfg['installer_path']).read_text());previous=ast.parse((source_dir/'PREIMAGE_47ce020d.py').read_text());same=[]
for name in ['check_unused','append_records_locked']:
 now=next(x for x in current.body if isinstance(x,ast.FunctionDef)and x.name==name);old=next(x for x in previous.body if isinstance(x,ast.FunctionDef)and x.name==name);assert ast.dump(now,include_attributes=False)==ast.dump(old,include_attributes=False);same.append(name)
main3=load('review_broad_Main3_inert',cfg['installer_path']);engine=load('review_broad_native_ro',R/'tools/l2_native.py');q=engine.registered()[2];before=copy.deepcopy(q)
scope=read(cfg['scope_contract_path']);assert len(scope['rows'])==26 and len({r['cohort']for r in scope['rows']})==26
assert sum(r['role']=='PRIMARY'for r in scope['rows'])==15 and sum(r['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'for r in scope['rows'])==11
canonical=main3.check_unused(R,q,scope,{})
assert len(canonical)==26 and main3.RESOURCE_ID not in q['additional_operational_overlays']and main3.OBSERVER_ID not in q['additional_operational_overlays']
lib=load('review_broad_library',cfg['modules']['library']);producer=load('review_broad_producer',cfg['modules']['producer']);extra=load('review_broad_extra',ocfg['source_paths']['extra_strict'])
actualgate=extra.verify_release_prerequisite(ocfg,q);assert actualgate['production_release_eligible']is True
assert rcfg['max_shared_running']is None and rcfg['host_floor_bytes']==rcfg['cgroup_floor_bytes']==10*1024**3 and rcfg['memory_utilization_fraction']==.95
shadow=copy.deepcopy(q)
for key,row in [(lib.ID,lib.record(rcfg)),(producer.ID,producer.record(ocfg))]:shadow['additional_operational_overlays'][key]=dict(row,status='ACTIVE')
lib.validate(rcfg,shadow);producer.validate(ocfg,shadow);assert q==before
assert sha(R/'control/MATRIX_CURRENT.json')==cfg['matrix_sha256']and sha(R/'control/SCOPE.json')==cfg['scope_sha256']and sha(cfg['old_memory_active_path'])==cfg['old_memory_active_sha256']
oldack=read(R/'control/operational_amendments/cpu_shared_timeslice_stage2_v1/actual_handoff_v1/ACK.json');assert oldack['status']=='ARMED_SAME_OWNER_NOT_SIMULATION_ACCEPTANCE'and oldack['same_frame_object_ids']==cfg['expected_frame_object_ids']
assert cfg['owner']==dict(pid=1498278,start_ticks=977758783)and int(P('/proc/1498278/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
review=dict(schema='E_MAIN_BROAD_SHARED_FINAL_SOURCE_CONFIG_REVIEW_V1',status='APPROVED_FOR_EXPLICIT_SAME_OWNER_CANARY_INSTALL',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_source_sha256=SSHA,owner_config_sha256=CPSHA,owner_config_path=str(CP),actual_models_qualified=False,actual_primary_IR_models_qualified=False,source_pin_count=107,source_pin_readback=pins,current_unused_scope_counts=dict(PRIMARY=15,IR=11),current_canonical_shas=canonical,actual_Main_four_gate=actualgate,budget=q['budget'],remaining=q['remaining'],actual_authority_mutation=False,shadow_resource_and_observer_validation='PASS',pure_EX_functions_AST_identical_to_A47ce=same,final_nested_prearm_QA_sha256=sha(delta),findings=['Preload module/source/config role joins close previously identified unqualified-load gap; all five loaded modules and self/Main1 sources are pinned.','Authority EX callback uses passed q and bounded file/scientific/IR-lineage checks only, no engine/lease/library authority reentry; exactly two new operational IDs append, no grants/refunds or old-record replacement.','Stage2 B2/E2 remain exact underlays; typed consumer then actual frame resource helper then new closed/unarmed dispatcher install, optional IR runtime view last, then arm.','Final prearm and containment both pass the same complete pending object through previous chooser once before suppressing selected returned decisions; actual extracted nested counterexample fixed and delta qualification bound to7b4. Worker fence preserves spent identity and prevents stale selected decision birth.','Same pool/claims/registry/running/post IDs have Stage2 ACK provenance and fresh runtime assertions; no scientific MATRIX/SCOPE/globalCPU2 context or original results are written.','New dynamic resource schema/mode/status is honest SharedCPU, all old/source generations retained; resource scheduling has full forecasts, RAM95/floor10 and dynamic quota/claim reservations, original legal allocator and E target75/25 barriers.'],execution_constraints=['Caller must contain BaseException during source load/preflight/apply; one explicit callback only, no blind reapply after partial exposure.','Actual Main must recheck actual thread/frame/oldStage2 markers, same references, current26 unused/unclaimed/noINTENT and all sources before arm; this independent review does not attach to Main.','Actual primary and IR natural physics, all270/counts/UUID/resource/IO/BPF and true164/native archive acceptance are required after dispatch. CPU qualification is not actual new model acceptance.','IR11 remain separate/statistically excluded/unionFalse; old negatives and old primary350 stay unchanged. Future scope additions need lawful new metadata/source-bound scope amendment.'],review_models_started=0,review_new_grants=0,review_production_changes=0,limitations=['No candidate apply, queue, owner mutation, signal or Git action by reviewer.','A/B/E mechanics/prefix/owner qualifications are separately pinned; original new-primary/IR physics and archive-transport leaves in CPU fixtures are stand-ins.'])
put(D/'REVIEW.json',review);put(D/'MANIFEST.json',dict(schema='E_FINAL_SOURCE_CONFIG_REVIEW_MANIFEST_V1',members=[dict(path=n,sha256=sha(D/n),bytes=(D/n).stat().st_size)for n in ['review.py','REVIEW.json']],production_changes=0))
print(json.dumps(dict(status=review['status'],REVIEW_sha256=sha(D/'REVIEW.json'),MANIFEST_sha256=sha(D/'MANIFEST.json'),pins=len(pins),budget=q['budget'],remaining=q['remaining'])))
