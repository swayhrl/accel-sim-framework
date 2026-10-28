"""CPU2 private fixture. Explicit stand-in natural gate; never real authority."""
import pathlib,json,hashlib,copy,tempfile,time,types,importlib.util
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=P(__file__).parent;G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fixture(owner_path=None,extra_path=None):
 root=P(tempfile.mkdtemp(prefix='CPU2_SCOPE_',dir=D));lib=load('cpu2_fixture_'+str(time.time_ns()),D/'cpu_memory.py');previous=read(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');assert previous['overlay_id']=='CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V1','CPU1 ACTIVE required, never mistake it for old95'
 old=copy.deepcopy(previous['fallback_v2_config']);q=copy.deepcopy(read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ]);q['qualification_only']=True;canary=previous['cpu_exception_scope']['allowed_cohorts'][0]
 q['consumed'][canary]=dict(uuid='CPU2_STANDIN_PREVIOUS_CANARY',execution_receipt=dict(launcher_wait_returncode=0,stop_reason=None,CPU_fixture_only=True))
 receipt=dict(status='PASS_CPU_SPARE_CANARY_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE',production_release_eligible=True,original_performance_accepted=True,cohort=canary,uuid=q['consumed'][canary]['uuid'],input_digest='CPU_STANDIN_INPUT',qualification_only=True,note='CPU-only stand-in; not actual Main canary acceptance or deployment authority')
 gate=root/'CPU_ONLY_CANARY_QUALIFICATION.json';put(gate,receipt);cfg=copy.deepcopy(previous);cfg.update(overlay_id=lib.ID,qualification_only=True,previous_cpu_v1_config=copy.deepcopy(previous),previous_cpu_v1_config_sha256=lib.objsha(previous),fallback_v2_config=old,cpu_exception_scope=dict(mode='ALL_ALLOWED_ADMITTED_UNSPENT'),canary_qualification_path=str(gate),canary_qualification_sha256=sha(gate),library_path=str(D/'cpu_memory.py'),library_sha256=sha(D/'cpu_memory.py'))
 points=['CPU2_PRIMARY_FIRST','CPU2_PRIMARY_SECOND']
 for c in points:q['admitted_specs'][c]='CPU2_FIXTURE_SPEC';cfg['allowed_cohorts'].append(c)
 if owner_path:cfg['owner_path']=str(owner_path)
 if extra_path:cfg['extra_strict_path']=str(extra_path)
 for r in lib.ROLES:cfg[r+'_sha256']=sha(cfg[r+'_path'])
 qa=root/'CPU_ONLY_QA.json';back=root/'CPU_ONLY_READBACK.json';sources={r:cfg[r+'_sha256']for r in lib.ROLES};put(qa,dict(status='PASS',cpu_spare_library_qualified=True,native_binding_qualified=True,qualified_sources=sources,expected_pins=cfg['expected_pins'],qualification_only=True));put(back,dict(verified=True,QA_sha256=sha(qa),qualified_sources=sources,expected_pins=cfg['expected_pins'],qualification_only=True));cfg.update(QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back));q['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE')
 oldfixture=load('frozen_cpu1_evidence_builder',D.parent/'cpu_spare_memory_v1/cpu_fixture.py')
 boot=read(R/'control/RESOURCE_OBSERVER.json')['boot_id'];base=dict(boot_id=boot,source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),host_MemAvailable_bytes=200*G,cgroup_effective_headroom_bytes=220*G,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,monotonic=time.monotonic(),utc='CPU2_FIXTURE',physical_disk_pass=True,own_write_ceiling_pass=True,total_projected_additional_RAM_bytes=12*G,RAM_reservation_entries=[dict(additional_reserved_bytes=3*G)],own_ram_forecasts=[dict(cohort=points[0],kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=9*G)],admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(.88*192*G),additional_reserved_RAM_bytes=12*G,pressure_reasons=['cpu_pressure_full'],pressure_pause_new=True,pass_admission=False),physical_RAM_pass=False)
 return types.SimpleNamespace(root=root,lib=lib,cfg=cfg,q=q,previous=previous,old=old,canary=canary,points=points,gate=gate,receipt=receipt,base=base,evidence=lambda cpu=None:oldfixture.evidence(lib,cpu))
