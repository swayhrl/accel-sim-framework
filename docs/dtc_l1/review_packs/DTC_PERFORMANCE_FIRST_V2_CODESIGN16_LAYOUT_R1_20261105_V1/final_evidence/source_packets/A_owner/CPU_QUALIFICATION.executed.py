from pathlib import Path
import json,types,copy,hashlib,os,time,fcntl,gzip,zlib,ast
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1/agents/A_owner_resource_v1');records=[]
def ck(n,v):assert v,n;records.append(dict(check=n,pass_=True))
def load(n):
 p=O/(n+'.py');m=types.ModuleType(n+'_cpu');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
r=load('perf16r1_resources');a=load('perf16r1_parent_addon');ops=load('perf16r1_ops');policy=r.read(O/'RESOURCE_POLICY.template.json');evidence=r.verify_direction_release(policy)
ck('authority425 exact user approval and latest direction933',evidence['authority_commit']=='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe')
q=dict(request=r.REQ,budget=16,remaining=16,admitted_specs={c:'CPU_SPEC'for c in r.EXPECTED16_COHORTS},consumed={});old={'OLD16':dict(budget=16,remaining=0,consumed={'old':'unchanged'})};reg=dict(registered_future_requests=copy.deepcopy(old));a.register_exact_request(reg,q,evidence);ck('pure newR1 registration preserves old16 no refund',reg['registered_future_requests']['OLD16']==old['OLD16']and reg['registered_future_requests'][r.REQ]['budget']==16)
# A real, separate-open-file-description EX lock fixture; never global native lock.
F=O/'cpu_fixture';d=F/'control/science_authority';d.mkdir(parents=True,exist_ok=True);lockp=d/'REGISTRY_UPDATE.lock';lockp.touch();rp=d/'NATIVE_SCIENCE_REGISTRY.json';rp.write_text('{"CPU_ONLY":true}');(F/'control/CURRENT_SCIENCE_EPOCH.json').write_text(json.dumps(dict(native_registry_sha256=r.sha(rp))))
with lockp.open('r+b')as held:
 fcntl.flock(held,fcntl.LOCK_EX);t=time.monotonic();hit=False
 try:r.bounded_authority(.05,root=F)
 except RuntimeError:hit=True
 ck('real samePID separateFD EX toSH bounded reject no selfdeadlock',hit and time.monotonic()-t<.5)
 # Runtime local safety cannot wait on authority/peer/archive, even while EX held.
 oldpeer,oldpure,oldauth=r._peer,r._pure,r.bounded_authority
 def forbidden(*x,**y):raise AssertionError('runtime touched forbidden registry/peer')
 r._peer=forbidden;r._pure=forbidden;r.bounded_authority=forbidden
 durations=[]
 for i in range(10):
  t=time.monotonic();v=r.resources({},False);durations.append(time.monotonic()-t);assert v['physical_RAM_pass']and v['registry_or_peer_reads']==v['true164_reads']==0 and v['admission_disk_pass']is False
 r._peer=oldpeer;r._pure=oldpure;r.bounded_authority=oldauth
 ck('ten real local samples ignore heldregistry no peer no164',max(durations)<.5)
ck('unlocked bounded authority actual fixture pair valid',r.bounded_authority(.05,root=F)[0]['CPU_ONLY']is True)
# Actual request source API has only declaration-level counterexamples here.
ck('runtime return never masquerades as archive restore forecast',v['full_restore_budget_not_evaluated']and not v['admission_disk_pass'])
# Private gate filesystem fixture; override ONLY native-device predicate, preserving all semantic checks.
G=O/'cpu_gate_fixture';G.mkdir(exist_ok=True);oldR=r.R;r.R=G;r.INITIAL_GATE_PATH=G/'control/INITIAL_RUNTIME_RELEASE.json';(G/'common-lib').symlink_to('/root/data/ep_l2_dtc_l1_native_v2/common-lib',target_is_directory=True)if not(G/'common-lib').exists()else None
realguard=r._assert_native_small
r._assert_native_small=lambda p,cap:ck('privatefixture_bounded_'+str(len(records)),Path(p).resolve().is_relative_to(G.resolve())and Path(p).stat().st_size<=cap)
co=r.FIRST_COHORT;uid='00000000-0000-0000-0000-000000000001';out=G/'DTC/run/results'/uid
for p in [out,G/'control/specs',G/'control/dispatch_bindings',G/'control/qualification_ledger',G/'analysis']:p.mkdir(parents=True,exist_ok=True)
def put(p,v):p.write_text(json.dumps(v))
digest='e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799';roi='CPU_ROI';spec=dict(program='vectorAdd',request=r.REQ,cohort=co,input_digest=digest,profile='PHYS768_OOPIB192_TAG64x8',structure_variant='PHYS768_OOPIB192_TAG64x8',native_simulator_argv=['/root/data/dtc_failure_repair_20261025_v1/framework-build/accel-sim.out'],execution_mnt_namespace='CPU_MNT',original_environment=dict(DTC_AG7_INPUT_SHA=digest,DTC_AG7_ROI_SHA=roi));sp=G/'control/specs'/(co+'.json');put(sp,spec)
plan=dict(runtime_guard=dict(sha256='CPU_GUARD',policy_sha256='CPU_POLICY'));bind=dict(request=r.REQ,engine_sha256='CPU_ENGINE',plan_sha256='CPU_PLAN',runtime_release_evidence=evidence,runtime_guard_sha256='CPU_GUARD',runtime_guard_policy_sha256='CPU_POLICY')
ip=G/'control/qualification_ledger'/(co+'.INTENT.json');put(ip,dict(uuid=uid,l2_mlp_execution_binding=bind));done=dict(uuid=uid,cohort=co,launcher_wait_returncode=0,stop_reason=None,native_simulator_observed=True);dp=G/'control/qualification_ledger'/(co+'.DONE.json');put(dp,done);put(out/'NATIVE_EXIT.json',done);put(G/'analysis'/(co+'.RESULT.json'),dict(state='PASS_PERFV2_CODESIGN16_LAYOUT_R1_DH_STRICT_ARCHIVE_NATIVE_RESTORE',proof=dict(performance_accepted=True),uuid=uid,cohort=co));dbp=G/'control/dispatch_bindings'/(co+'.json');put(dbp,dict(host_cpu=1))
pm=dict(pid=123,start_ticks=456,exe='/root/data/ep_l2_dtc_l1_native_v2/common-lib/ld-linux-x86-64.so.2',maps=spec['native_simulator_argv'][0]+'\n/root/data/dtc_failure_repair_20261025_v1/core-build/libcudart.so',mnt_namespace='CPU_MNT',host_cpu_affinity_actual=[1],dispatch_binding_sha256=r.sha(dbp),l2_mlp_execution_binding=bind);put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',pm);put(out/'NATIVE_LAUNCH.json',dict(scientific_qualification_uuid=uid,argv=spec['native_simulator_argv'],l2_mlp_execution_binding=bind))
progress=[dict(v=1,pid=123,start_ticks=456,generation=uid,input=digest,roi=roi,seq=i+1,mono_ns=100+i,completed=i,end='NONE')for i in range(2)]
def gz(p,rows):p.write_bytes(gzip.compress(('\n'.join(json.dumps(v)for v in rows)+'\n').encode()))
gz(out/'progress.jsonl.gz',progress);guards=[dict(DTC_exact_original_policy=dict(runtime_policy_binding=dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_ADMISSION_PRESSURE_ONLY_RUNTIME_V1',guard_sha256='CPU_GUARD',policy_sha256='CPU_POLICY',telemetry_receiver_sha256='f523975b9780b498b988e2b3145ba5b4aebdef4d0e9b0146392d3a31a99a4ec1'),decision=dict(decision='CONTINUE')))];gz(out/'RESOURCE_SAMPLES.jsonl.gz',guards)
q=dict(request=r.REQ,budget=16,remaining=15,consumed={co:dict(uuid=uid,intent_sha256=r.sha(ip),execution_receipt=done)},admitted_specs={co:r.sha(sp)},engine_sha256='CPU_ENGINE',execution_plan_sha256='CPU_PLAN',runtime_release_evidence=evidence)
other=next(c for c in r.EXPECTED16_COHORTS if c!=co);hit=False
try:r.verify_initial_runtime_gate(plan,other,q=q)
except r.WaitInitialRuntimeGate:hit=True
ck('missing first gate ordinary WAIT not safetyHOLD',hit and'q.admission_holds'not in q)
payload=r.inspect_first_closed(plan,q);put(r.INITIAL_GATE_PATH,payload);ck('short finished firstpoint accepted mapsROIpositive releases15 withoutproc',r.verify_initial_runtime_gate(plan,other,q=q)['release15']is True)
wrong=copy.deepcopy(progress);wrong[1]['roi']='WRONG';gz(out/'progress.jsonl.gz',wrong);hit=False
try:r.verify_initial_runtime_gate(plan,other,q=q)
except AssertionError:hit=True
ck('wrongROI refuses release',hit);gz(out/'progress.jsonl.gz',progress)
bad=copy.deepcopy(done);bad['launcher_wait_returncode']=127;bad['native_simulator_observed']=False;put(dp,bad);put(out/'NATIVE_EXIT.json',bad);q['consumed'][co]['execution_receipt']=bad;hit=False
try:r.inspect_first_closed(plan,q)
except RuntimeError as e:hit='PAUSE_ALL_NEW_ADMISSION'in str(e)
ck('actual launcher failure blocksremaining15',hit)
# zlib tolerates unfinished gzip footer: never infer a STOP from normal stream footer absence.
raw=gzip.compress((json.dumps(progress[0])+'\n').encode());pp=out/'partial_progress.gz';pp.write_bytes(raw[:-8]);ck('unfinished gzip footer accepts complete prefix',r._closed_progress_rows(pp)==[progress[0]])
r.R=oldR;r._assert_native_small=realguard
ck('ops has async stop event checked before eachdispatch',all(x in(O/'perf16r1_ops.py').read_text()for x in ['admission_paused.set()','KNOWN_LAUNCHER_FAILURE_IMMEDIATE_PAUSE',"if gate_state['state']!='QUALIFIED_FIRST_NATURAL_ACCEPTED_RUNTIME_GATE'"]))
(O/'CPU_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS_CPU_ONLY_NO_NATIVE_START',checks=records,check_n=len(records),runtime_sample_max_wall_seconds=max(durations),source_sha256={n:r.sha(O/(n+'.py'))for n in ['perf16r1_resources','perf16r1_parent_addon','perf16r1_ops']},synthetic_gate_fixture=True,native_device_predicate_only_overridden_for_fixture=True,real_separateFDflock=True,actual_requests_registered=0,actual_callbacks=0,models_started=0,old_science_changed=False),indent=2)+'\n');print(json.dumps(dict(status='PASS_CPU_ONLY_NO_NATIVE_START',checks=len(records),runtime_max=max(durations))))

