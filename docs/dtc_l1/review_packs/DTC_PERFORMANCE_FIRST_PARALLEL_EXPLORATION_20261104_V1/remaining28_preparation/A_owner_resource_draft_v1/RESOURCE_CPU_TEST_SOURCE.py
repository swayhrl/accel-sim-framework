from pathlib import Path
import json,sys,importlib.util,copy,hashlib,os
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/A_remaining28_owner_resource_v1');p=O/'perf28_resources.py';sp=importlib.util.spec_from_file_location('a3_resource_CPU_fixture',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);P=json.loads((O/'RESOURCE_POLICY.template.json').read_text());PRODUCTION_POLICY=copy.deepcopy(P);P['old_final_review_release']=None;s=m.sample_system();tests=[]
def test(name,condition):assert condition,name;tests.append(dict(name=name,PASS=True))
test('sample_excludes_GES_and_Main_SMT',not(set(s['cpu_allowed'])&m.PROTECTED_CPUS));test('new_private_pure_RREQ_only',m._pure().R==m.R and m._pure().REQ==m.REQ)
# Isolated pure sample, no production registration and no model launch.
bare=copy.deepcopy(s);bare.update(host_MemAvailable_bytes=100*m.G,cgroup_effective_headroom_bytes=100*m.G,native_free_bytes=30*m.G,archive_free_bytes=100*m.G,true164_mount_verified=True,free_inodes=200000,old_remaining48_completion=dict(verified=True,all_terminal=False,manifest_sha256='7aa37a91d6506c4de5033cc72f3b0f4233bc43e64e5724128f308423a3809566'),first4_completion_gate={'pass':True,'reasons':[]})
for f in ['memory_pressure','io_pressure','cpu_pressure','host_memory_pressure','host_io_pressure','host_cpu_pressure']:bare[f]={}
baseB=dict(required_free_bytes=5*m.G+768*m.M+9*m.G,peer_reservations=[dict(request=m.REQ,reserved_write_bytes=768*m.M),dict(request=m.REMAINING48_REQ,reserved_write_bytes=9*m.G)],reserved_additional_live_and_candidate_RAM_bytes=0,per_scope_write_ceiling_pass={},known_remaining_writes_by_request={})
own=dict(projected_write_bytes=384*m.M,actual_unarchived_output_bytes=256*m.M,projection_within_registered_ceiling=True,additional_RAM_bytes=m.G,ram=[],writes=[])
peer={m.REMAINING48_REQ:dict(projected_write_bytes=256*m.M,additional_RAM_bytes=m.G,projection_within_registered_ceiling=True)};q=dict(reserved_write_bytes=768*m.M);spec={}
def ev(sample,fresh=True,ownval=None):return m._evaluate(spec,fresh,sample,None,baseB,peer,ownval or own,q,P)
r=ev(bare);test('fresh_pass_under_real_headroom_fixture',r['physical_RAM_pass']and r['admission_disk_pass']);test('R2_static9GiB_replaced_only_with_dynamic_evidence',r['required_free_bytes']==5*m.G+640*m.M)
x=copy.deepcopy(bare);x['host_memory_pressure']={'full':{'avg10':.75}};test('host_PSI_pauses_new',not ev(x)['physical_RAM_pass']);test('host_PSI_does_not_kill_runtime',ev(x,False)['physical_RAM_pass']and ev(x,False)['physical_disk_pass'])
x=copy.deepcopy(bare);x['native_free_bytes']=5*m.G+128*m.M;test('forecast_disk_blocks_new_only',not ev(x)['admission_disk_pass']and ev(x,False)['physical_disk_pass']);x['native_free_bytes']=5*m.G;test('native_floor_exact5GiB_is_unsafe',not ev(x,False)['physical_disk_pass'])
x=copy.deepcopy(bare);x['true164_mount_verified']=False;test('false164_prevents_new_and_restore_admission',not ev(x)['admission_disk_pass']);test('false164_does_not_convert_forecast_to_runtime_kill',ev(x,False)['physical_disk_pass'])
x=copy.deepcopy(bare);x['free_inodes']=99999;test('inode_unsafe_runtime',not ev(x,False)['physical_disk_pass'])
o=copy.deepcopy(own);o['actual_unarchived_output_bytes']=q['reserved_write_bytes']+1;test('actual_own_output_over_contract_unsafe',not ev(bare,False,o)['physical_disk_pass'])
x=copy.deepcopy(bare);x['old_remaining48_completion']['all_terminal']=True;test('old_allterminal_pauses_new',not ev(x)['physical_RAM_pass']);test('old_allterminal_runtime_healthy_continues',ev(x,False)['physical_RAM_pass']and ev(x,False)['physical_disk_pass'])
x=copy.deepcopy(bare);x['old_remaining48_all_execution_receipted']=True;test('old_all_native_receipted_pauses_before_final_provider',not ev(x)['physical_RAM_pass'])
x=copy.deepcopy(bare);x['old_remaining48_completion']={'verified':False};test('missing_old_provider_conservative_pause_new',not ev(x)['physical_RAM_pass'])
x=copy.deepcopy(bare);x['old_remaining48_completion']['all_terminal']=True;pol=copy.deepcopy(P);pol['old_final_review_release']=dict(approved=True,request=m.REQ,old_request=m.REMAINING48_REQ,old_terminal_manifest_sha256='wrong');test('wrong_old_review_pin_holds',m.old_completion_gate(x,pol)['pause_new']);pol['old_final_review_release']['old_terminal_manifest_sha256']='7aa37a91d6506c4de5033cc72f3b0f4233bc43e64e5724128f308423a3809566';direction=m.ROOT_FULL32_DIRECTION_PATH;pol['old_final_review_release'].update(direction_review_path=str(direction),direction_review_sha256=m.ROOT_FULL32_DIRECTION_SHA);test('explicit_matched_Root_release_only',not m.old_completion_gate(x,pol)['pause_new'])
x=copy.deepcopy(bare);x['host_MemAvailable_bytes']=7*m.G;test('host8GiB_floor_holds',not ev(x)['physical_RAM_pass']);x=copy.deepcopy(bare);x['cgroup_effective_headroom_bytes']=7*m.G;test('cgroup8GiB_floor_holds',not ev(x)['physical_RAM_pass'])
prev=copy.deepcopy(bare);prev['monotonic']=1;x=copy.deepcopy(bare);x['monotonic']=2;x['host_oom_kill_count']=prev['host_oom_kill_count']+1;test('fresh_host_OOM_increment_holds','HOST_OOM_KILL_INCREASE'in m.pressure_reasons(x,prev,P));x=copy.deepcopy(bare);x['monotonic']=2;x['host_pswpout_pages']=prev['host_pswpout_pages']+20000;test('active_swapout_holds','ACTIVE_SWAP_OUT'in m.pressure_reasons(x,prev,P))
# Fresh actual old48 peer join is read-only. No production newREQ registry lookup is attempted.
peerModule=m._peer();reg,epoch=peerModule.authority();d=m._closed_remaining48(peerModule,reg);test('actual_old48_complete_archive_nonlive_zero_future',d['projected_write_bytes']==0 and d['exact_archived_nonlive_count']==48)
(O/'ACTUAL_OLD48_PEER_JOIN.json').write_text(json.dumps(d,indent=2)+'\n')
(O/'ACTUAL_FIRST4_COMPLETION_GATE_OBSERVATION.json').write_text(json.dumps(m.first4_completion_gate(reg,peerModule),indent=2)+'\n')
# Additional minimal native-free metadata/selection invariants; no real registration.
test('actual_Root_full32_direction_release_SHA_matches',not m.old_completion_gate(s,PRODUCTION_POLICY)['pause_new'])
x=copy.deepcopy(bare);x['first4_completion_gate']={'pass':False};test('first4_gate_blocks_new_admission',not ev(x)['physical_RAM_pass']);test('first4_gate_does_not_kill_healthy_runtime',ev(x,False)['physical_RAM_pass'])
no_static=copy.deepcopy(baseB);no_static['peer_reservations']=[];no_static['required_free_bytes']=5*m.G
rr=m._evaluate(spec,True,bare,None,no_static,peer,own,q,P)
test('dynamic_peer_not_lost_when_static_reservation_absent',rr['required_free_bytes']==5*m.G+640*m.M)
profiles=json.loads((O/'REMAINING28_RESOURCE_SPEC_FIELDS.json').read_text())['points'];pending=[]
for row in [next(x for x in profiles if x['program']==p and x['profile']=='PHYS1024_TAG64x8')for p in ['2DCONV','GEMM']]:
 ss=copy.deepcopy(row);ss['workload']=row['input_digest'];pending.append(ss)
oldres=m.resources
m.resources=lambda ss,fresh=False:dict(physical_RAM_pass=True,admission_disk_pass=ss['program']=='GEMM',required_free_bytes=6*m.G,native_free_bytes=30*m.G,admission_decision=dict(pressure_reasons=[]))
claims={};choice=m.choose_dispatch(pending,bare,claims,[],policy=P,dispatch_index=1)
test('disk_before_claim_can_try_other_fitting_candidate',choice is not None and choice['cohort']==pending[1]['cohort'])
test('choose_dispatch_never_writes_claims',claims=={})
test('choice_cpu_does_not_overlap_protected',choice['host_cpu']not in m.PROTECTED_CPUS)
m.resources=oldres
(O/'CPU_QUALIFICATION.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='PASS_CPU_ONLY',tests=tests,n=len(tests),new_model_starts=0,registered_newREQ=False,actual_old_peer_reads_only=True,services_started=0,source_or_old_global_mutations=0),indent=2)+'\n');print('CPU_PASS',len(tests),'old48closed; new4 actual gate separately observed','source',hashlib.sha256(p.read_bytes()).hexdigest())
