"""Private resource fixture: no production authority or model evidence."""
import pathlib,json,hashlib,copy,tempfile,time,types,importlib.util,os
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fixture():
 root=P(tempfile.mkdtemp(prefix='CPU_SHARED_UNIT_',dir=D));lib=load('actual_shared_'+root.name,D/'cpu_shared.py');scope_contract=read('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json');primary=[r['cohort']for r in scope_contract['rows']if r['role']!='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'];c=min(primary,key=lambda x:read(R/'control/specs'/(x+'.json'))['estimated_peak_model_RAM_bytes']);s=read(R/'control/specs'/(c+'.json'));hist=read(R/'control/HISTORICAL_RSS.json');res=load('frozen_allocator_fixture',R/'tools/l2_resources.py');forecast=res.forecast(dict(s,host_cpu=0),hist,read(R/'control/RESOURCE_POLICY.json'));s['estimated_peak_model_RAM_bytes']=max(s['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes'])
 for p in[root/'control/specs'/(c+'.json'),root/'control'/(c+'_SPEC.json')]:put(p,s)
 put(root/'control/dispatch_bindings'/(c+'.json'),dict(cohort=c,host_cpu=0,canonical_spec_sha256=sha(root/'control/specs'/(c+'.json')),resolved_spec_sha256=lib.objsha(dict(s,host_cpu=0))))
 q=copy.deepcopy(read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ]);q['qualification_only']=True;q['admitted_specs'][c]=sha(root/'control/specs'/(c+'.json'));q['consumed'].pop(c,None)
 claims={c:dict(host_cpu=0,cpu_shared_timeslice_overlay_id=lib.ID)};put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
 roles={'library':str(D/'cpu_shared.py')}
 for role in ['owner','frontend','extra_strict','consumer']:
  p=root/('PRIVATE_'+role+'.py');p.write_text('# EXPLICIT CPU UNIT ROLE STANDIN; not an implementation or Main source\n');roles[role]=str(p)
 pins={str(p):sha(p)for p in[R/'tools/l2_resources.py',R/'control/RESOURCE_POLICY.json',P(lib._CPU2.__file__)]};sources={k:sha(v)for k,v in roles.items()};qa=root/'CPU_ONLY_QA.json';rb=root/'CPU_ONLY_READBACK.json';put(qa,dict(status='PASS',cpu_shared_resource_qualified=True,native_binding_qualified=True,dynamic_concurrency_qualified=True,qualified_sources=sources,expected_pins=pins,qualification_only=True));put(rb,dict(verified=True,QA_sha256=sha(qa),qualified_sources=sources,expected_pins=pins,qualification_only=True))
 iop=R/'control/operational_amendments/shared_json_io_v1/ACTIVE_IO.json';cfg=dict(schema=lib.ID,request=lib.REQ,overlay_id=lib.ID,status='ACTIVE_FUTURE_ONLY',root=str(root),qualification_only=True,scope_mode='ALL_ALLOWED_ADMITTED_UNSPENT',qualification_stage='AFTER_REAL_ENGINEERING4_GATE',allowed_cohorts=[r['cohort']for r in scope_contract['rows']],max_shared_running=None,memory_utilization_fraction=.95,host_floor_bytes=10*G,cgroup_floor_bytes=10*G,cpu_shared_policy=copy.deepcopy(lib.POLICY),source_paths=roles,qualified_sources=sources,library_path=roles['library'],expected_pins=pins,QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(rb),readback_sha256=sha(rb),io_active_path=str(iop),io_active_sha256=sha(iop),design_contract_path=str(lib.DESIGN),design_contract_sha256=lib.DESIGN_SHA)

 for ac in cfg['allowed_cohorts']:
  if ac==c:continue
  for rel in ['control/specs/'+ac+'.json','control/'+ac+'_SPEC.json']:
   dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/rel).read_bytes())
 rows=[];refs={}
 for ec in lib.ORIGINAL_FOUR:
  uuid='CPU_ONLY_FIXTURE_NOT_ACTUAL_'+ec;ar=dict(archive_sha256='PRIVATE_ARCHIVE',manifest_sha256='PRIVATE_MANIFEST')
  result=dict(state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE',cohort=ec,uuid=uuid,cycles=8551,archive={'receipt':ar},qualification_only=True)
  done=dict(cohort=ec,uuid=uuid,stop_reason=None,launcher_wait_returncode=0,qualification_only=True)
  for suffix,doc in [('RESULT',result),('DONE',done)]:
   target=root/(ec+'.'+suffix+'.json');put(target,doc);refs[ec+'.'+suffix]=dict(path=str(target),sha256=sha(target))
  rows.append(dict(cohort=ec,uuid=uuid,RESULT_sha256=refs[ec+'.RESULT']['sha256'],cycles=8551,archive_sha256='PRIVATE_ARCHIVE',archive_manifest_sha256='PRIVATE_MANIFEST',actual_full_chain_replayed=True,qualification_only=True))
 gate_source=R/'control/operational_amendments/cpu_shared_timeslice_stage2_v1/bpf_extra_strict.py';pins[str(gate_source)]=sha(gate_source);cfg['expected_pins']=pins
 gate=dict(gate_source_sha256=sha(gate_source),status='PASS_REAL_MIXED_GENERATION_ENGINEERING_FOUR_FULL_CHAIN',accepted_real_count=4,four_point_qualified=True,rows=rows,primary_rollout_eligible=False,IR_rollout_eligible=False,actual_owner_pid=1498278,actual_owner_start_ticks=977758783,qualification_only=True,backend='CPU_ONLY_STANDIN_NOT_ACTUAL_ENGINEERING_GATE')
 gp=root/'CPU_ONLY_GATE.json';put(gp,gate);ap=root/'CPU_ONLY_APPROVAL.json'
 put(ap,dict(schema='DTC_MAIN_BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1',Main_broad_operational_rollout_approved=True,eligible_conditional_new_operational_registration=True,new_grants=0,qualification_only=True,allowed_cohorts=cfg['allowed_cohorts'],scope_contract=dict(path=str('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json'),sha256=sha('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json')),actual_gate=dict(path=str(gp),sha256=sha(gp),source_path=str(gate_source),source_sha256=sha(gate_source)),source_artifacts=refs,backend='CPU_ONLY_STANDIN_NOT_MAIN_APPROVAL'))
 cfg.update(broad_approval_path=str(ap),broad_approval_sha256=sha(ap),scope_contract_path=str('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json'),scope_contract_sha256=sha('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json'))
 put(qa,dict(status='PASS',cpu_shared_resource_qualified=True,native_binding_qualified=True,dynamic_concurrency_qualified=True,qualified_sources=sources,expected_pins=pins,qualification_only=True));put(rb,dict(verified=True,QA_sha256=sha(qa),qualified_sources=sources,expected_pins=pins,qualification_only=True));cfg.update(QA_sha256=sha(qa),readback_sha256=sha(rb))
 q['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE');lib.validate(cfg,q)

 oldf=load('CPU2_frozen_evidence_builder',A/'agents/A/cpu_spare_memory_v1/cpu_fixture.py')
 def cpu(selected=0,prospective_cpu_threads=1):
  raw=oldf.evidence(lib._CPU2,selected)
  for key,t in raw['second']['cpu_ticks'].items():raw['second']['cpu_ticks'][key]=[190,0,0,910,0,0,0,0]
  return lib.wrap_cpu_evidence(raw,prospective_cpu_threads)
 def legal(cfg,claims,cohort,selected_cpu=None):
  e=cpu(selected_cpu);b=e['raw_cpu2_evidence']['second'];sample=dict(boot_id=b['boot_id'],monotonic=time.monotonic(),cpu_allowed=b['allowed'],cpu_topology=[dict(x,node=x['socket'])for x in b['topology']],observed_affinity_claims=[],observed_models=[],cpu_ticks=b['cpu_ticks']);others={k:v for k,v in claims.items()if k!=cohort};mod=load('real_allocator_in_private_fixture',R/'tools/l2_resources.py')
  return dict(schema=lib.ID+'_LEGAL_CPU',source_sha256=sha(R/'tools/l2_resources.py'),sample=sample,other_claims=copy.deepcopy(others),candidate_cohort=cohort,selected_cpu=selected_cpu,legal_cpu_candidates=mod.cpu_candidates(sample,others,None),created_monotonic=time.monotonic())
 def base(*args):
  cost=s['estimated_peak_model_RAM_bytes'];return dict(boot_id=read(R/'control/RESOURCE_OBSERVER.json')['boot_id'],source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),host_MemAvailable_bytes=200*G,cgroup_effective_headroom_bytes=220*G,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,monotonic=time.monotonic(),physical_disk_pass=True,own_write_ceiling_pass=True,total_projected_additional_RAM_bytes=cost+3*G,RAM_reservation_entries=[dict(additional_reserved_bytes=3*G)],own_ram_forecasts=[dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=cost)],admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(.88*192*G),additional_reserved_RAM_bytes=cost+3*G,pressure_reasons=['cpu_pressure_full'],pressure_pause_new=True,pass_admission=False),physical_RAM_pass=False)
 def inputs(kind='OWNER_CHOOSE'):
  slot=lib.capture_slot_evidence(cfg,q,c,0,root=root);return dict(base=base(),cfg=cfg,cohort=c,selected_cpu=0,evidence=cpu(0,slot['prospective_cpu_threads']),slot_evidence=slot,context={'kind':kind},legal_cpu_evidence=legal(cfg,json.loads(slot['claims_utf8'])['claims'],c,0))
 return types.SimpleNamespace(root=root,lib=lib,cfg=cfg,q=q,c=c,spec=s,claims=claims,cpu=cpu,legal=legal,base=base,inputs=inputs)
