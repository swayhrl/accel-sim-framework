"""Readonly concrete native Stage2 handoff configuration review. Never apply."""
import pathlib,hashlib,json,copy,importlib.util,datetime,sys
P=pathlib.Path;D=P(__file__).parent
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
M=R/'control/operational_amendments/cpu_shared_timeslice_stage2_v1'
CP=M/'actual_handoff_v1/CONFIGURATION.json'
CONFIG_SHA='467353e6c1b237fd436158ebfc8da7bbe029ec52d5ef75d312263d75c7472b4d'
SOURCE_SHA='06aee02a8a6476c4ea071063b5aa9cfb989ca7ec149b86093d7e62a904dd2118'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 assert not p.exists(),'Do not overwrite immutable review'
 p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('Readonly review, no model/process/signal')
sys.addaudithook(audit)
assert sha(CP)==CONFIG_SHA;cfg=read(CP);assert sha(cfg['installer_path'])==cfg['installer_sha256']==SOURCE_SHA
assert len(cfg['source_pins'])==67
pins=[dict(path=p,sha256=sha(p),expected_sha256=h)for p,h in cfg['source_pins'].items()]
assert all(x['sha256']==x['expected_sha256']for x in pins)
binding=CP.parent/'MAIN_SOURCE_BINDING.json';assert sha(binding)=='0a7487269001f5908deca264e411e59b44b00c8ec46b9a3aa788cdced733f8b8'
assert read(binding)==dict(schema='CPU_SHARED_MAIN_HASH_BOUND_APPLY_BRIDGE_V1',configuration_path=str(CP),configuration_sha256=CONFIG_SHA,installer_path=cfg['installer_path'],installer_sha256=SOURCE_SHA)
assert sha(cfg['resource_configuration_path'])=='0c1d7af7de0085a9cd7fcaf34f2e7c1a0f705ad28b9d022d368af09083047a20'
assert sha(cfg['observation_configuration_path'])=='10caa5514597a872df13062ba4b01d4c8cff9dc6e0548b036364f0da9200dada'
rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
assert cfg['modules']==dict(library=rcfg['source_paths']['library'],producer=ocfg['source_paths']['producer'],consumer=ocfg['source_paths']['consumer'])
for contract in [rcfg,ocfg]:
 for role,path in contract['source_paths'].items():assert sha(path)==cfg['source_pins'][path]==contract['qualified_sources'][role]
assert rcfg['scope_extension_approval_path']==ocfg['scope_extension_approval_path']and rcfg['scope_extension_approval_sha256']==ocfg['scope_extension_approval_sha256']=='30bd502f7fe6653907b3e835c2b7aee78c780c65ecde758df473942158d1b895'
assert ocfg['resource_configuration_path']==cfg['resource_configuration_path']and ocfg['resource_configuration_sha256']==sha(cfg['resource_configuration_path'])
assert cfg['owner']==dict(pid=1498278,start_ticks=977758783)
owner_stat=P('/proc/1498278/stat').read_text();assert int(owner_stat.rsplit(')',1)[1].split()[19])==cfg['owner']['start_ticks']
assert sha(R/'control/MATRIX_CURRENT.json')==cfg['matrix_sha256']and sha(R/'control/SCOPE.json')==cfg['scope_sha256']
assert sha(cfg['old_memory_active_path'])==cfg['old_memory_active_sha256']=='b7cdb2ac044ea668960e2e3ba8c5a0e6eb20e177db673e9b6fa3411fdce08a8f'
main2=load('review_Main2_inert',cfg['installer_path']);engine=load('review_native_readonly',R/'tools/l2_native.py');q=engine.registered()[2];before=copy.deepcopy(q)
scope=main2.fresh_scope(q);assert len(scope)==3 and main2.FIRST not in scope
lib=load('review_shared_stage2_lib',cfg['modules']['library']);producer=load('review_shared_stage2_producer',cfg['modules']['producer'])
specs=[]
for c in scope:
 spec=main2.unused_identity(R,q,c,{})
 producer.verify_engineering_spec(ocfg,c,ocfg['modes'][c],spec)
 specs.append(dict(cohort=c,current_canonical_sha256=q['admitted_specs'][c],host_cpu=spec['host_cpu'],scientific_role=spec['scientific_role']))
assert rcfg['max_shared_running']==1 and set(rcfg['allowed_cohorts'])==set(main2.FOUR)and set(ocfg['modes'])==set(main2.FOUR)
assert rcfg['qualification_only']is ocfg['qualification_only']is False and ocfg['future_primary_policy']=='NONE'
assert rcfg['host_floor_bytes']==rcfg['cgroup_floor_bytes']==10*1024**3 and rcfg['memory_utilization_fraction']==.95
old_records={k:copy.deepcopy(q['additional_operational_overlays'][k])for k in [main2.RESOURCE_ID,main2.OBSERVATION_ID]}
shadow=copy.deepcopy(q)
for key,new in [(lib.ID,lib.record(rcfg)),(producer.ID,producer.record(ocfg))]:shadow['additional_operational_overlays'][key].update(dict(new,status='ACTIVE'))
lib.validate(rcfg,shadow);producer.validate(ocfg,shadow);assert q==before
first=read(R/'analysis'/(main2.FIRST+'.RESULT.json'));assert first['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and first['uuid']==q['consumed'][main2.FIRST]['uuid']=='2d24a1be-db7b-4100-9752-42b16ea46035'
preparation=A/'coordinator/CPU_SHARED_MAIN2_PREPARED_HANDOFF_V1/PREPARATION.json';assert sha(preparation)=='b30a5aac515acd0153a9f04bd28a5a5ee54f74645eab00b3f4020703e9bd9561'
prepared=read(preparation);assert prepared['installer_source_sha256']==SOURCE_SHA and prepared['installer_configuration_sha256']==CONFIG_SHA and prepared['registry_mutations']==prepared['callbacks_queued']==0
oldack=read(R/'control/operational_amendments/cpu_shared_timeslice_v1/actual_install_v1/ACK.json')
oldconfig=read(oldack['configuration_path']);assert sha(oldack['configuration_path'])==oldack['configuration_sha256']
# Object IDs are fresh-runtime assertions in apply; compare original hash-bound configuration provenance only.
assert oldconfig['expected_frame_object_ids']==cfg['expected_frame_object_ids']
review=dict(schema='E_SHARED_STAGE2_CONCRETE_HANDOFF_REVIEW_V1',status='APPROVED_FOR_EXPLICIT_SAME_OWNER_CANARY_INSTALL',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_source_sha256=SOURCE_SHA,owner_config_sha256=CONFIG_SHA,owner_config_path=str(CP),actual_models_qualified=False,new_three_models_qualified=False,actual_four_gate_qualified=False,review_production_changes=0,new_grants=0,models_started=0,conclusion='Concrete native source/configuration joins pass; no source/configuration blocker found for one contained existing-owner Stage2 handoff. It is not simulation acceptance or primary/IR rollout.',pin_count=len(pins),pin_readback=pins,Main_binding_sha256=sha(binding),resource_configuration_sha256=sha(cfg['resource_configuration_path']),observation_configuration_sha256=sha(cfg['observation_configuration_path']),current_unused_scope=specs,accepted_C0=dict(cohort=main2.FIRST,uuid=first['uuid'],RESULT_sha256=sha(R/'analysis'/(main2.FIRST+'.RESULT.json')),cycles=first['cycles'],rerun_authorized=False),shadow_only_validation=dict(status='PASS',actual_authority_mutation=False,budget=q['budget'],remaining=q['remaining'],actual_operational_records_unchanged=True),same_owner=dict(pid=1498278,start_ticks=977758783),source_only_review=dict(path=str(A/'agents/E/main_shared_stage2_handoff_review_v1/REVIEW.json'),sha256=sha(A/'agents/E/main_shared_stage2_handoff_review_v1/REVIEW.json')),pending_execution_assertions=['Apply must fresh-check actual Main thread/frame/live object identities, unchanged Main1 marker/old mask/callbacks, no claims/INTENT for remaining scope and all current source pins; independent review does not claim live closure inspection.','A final focused Main2 helper/real EX qualifications are still pending at review time and must correspond to source06aee before Main queues; no old810 qualification substitution.','Caller must contain BaseException for source loading and apply. No blind reapply after partial change; precise four-cohort containment retains mandatory current consumer routes.','Maxshared1 and full RAM/disk/CPU/IO/forecast/native sampling stay in force. Actual remaining three natural strict/archive/native acceptance and mixed-generation actual four gate are still required.'],limitations=['No apply, queue, authority write, Main private-object mutation, model, signal or Git action performed.','Exact object identities are checked against original Main1 hash-bound configuration here and are enforced fresh by actual apply; this review does not attach to Main.'])
put(D/'REVIEW.json',review)
put(D/'MANIFEST.json',dict(schema='E_CONCRETE_READONLY_REVIEW_MANIFEST_V1',members=[dict(path=n,sha256=sha(D/n),bytes=(D/n).stat().st_size)for n in ['review_concrete.py','REVIEW.json']],production_changes=0))
print(json.dumps(dict(status=review['status'],review_sha256=sha(D/'REVIEW.json'),manifest_sha256=sha(D/'MANIFEST.json'),scope=list(scope),pins=len(pins))))
