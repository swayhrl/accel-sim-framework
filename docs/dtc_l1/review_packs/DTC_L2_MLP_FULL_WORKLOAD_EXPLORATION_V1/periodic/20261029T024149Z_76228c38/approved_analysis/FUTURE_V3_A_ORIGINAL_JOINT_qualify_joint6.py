"""Exactly six new V3 joint groups; no old-suite repetition or real processes."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,copy,importlib.util,tempfile,os,shutil,types,time
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/future_bpf_v3_joint_qualification_v1';B=A/'agents/B/strace_bpf_future_entry_v3';E=A/'agents/E/strace_bpf_future_strict_consumer_v3';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in['os.system','os.kill','os.killpg']:raise RuntimeError('JOINT6_NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if(isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'WRITE_OUTSIDE_A_PRIVATE_JOINT_ROOT'
sys.addaudithook(audit)
pins={str(p):sha(p)for p in[B/'strace_entry.py',B/'bpf_frontend.py',B/'native-entry/bin/experiment',B/'cpu_prefix_fixture.py',E/'bpf_extra_strict.py',E/'consumer_bridge.py',A/'agents/E/strace_bpf_future_policy_v3/future_policy.py']}
assert pins[str(A/'agents/E/strace_bpf_future_policy_v3/future_policy.py')]=='389be2e9dc01e071bc4c3edae10f8fa67ba1555c357840225b4a9687b8622b91'
builder=load('A_actual_B_V3_fixture',B/'cpu_prefix_fixture.py');extra=load('A_actual_E_V3_extra',E/'bpf_extra_strict.py');bridge=load('A_actual_E_V3_consumer',E/'consumer_bridge.py')
cases=[];runs={}
def reject(fn):
 try:fn()
 except Exception as e:return dict(type=type(e).__name__,reason=str(e)[:400])
 raise AssertionError('Required explicit rejection did not occur')
def check(name,conditions,evidence):
 assert all(conditions),name;cases.append(dict(case=name,status='PASS',evidence=evidence))
def archive_leaf(run):
 out=run.out;bundle=run.root/'ARCHIVE_TRANSPORT_MOCK';restore=run.root/'DTC/run/recovery/CPU_ARCHIVE_MOCK';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True);entries=[]
 for p in sorted(out.iterdir()):
  if p.is_file():entries.append(dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size));shutil.copyfile(p,restore/p.name)
 manifest=dict(cohort=run.c,source_root=str(out),entries=entries);put(bundle/'SOURCE_MANIFEST.json',manifest);h=hashlib.sha256((json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
 return dict(receipt=dict(cohort=run.c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=h,archive_sha256='CPU_TRANSPORT_LEAF_MOCK_NO_REAL_164_ARCHIVE'),independently_verified_entries=len(entries))
for kind in ['PRIMARY','IR']:
 root=P(tempfile.mkdtemp(prefix='A_JOINT6_'+kind+'_',dir=D));f=builder.build_fixture(root=root,extra_path=E/'bpf_extra_strict.py',consumer_path=E/'consumer_bridge.py',kind=kind)
 run=builder.run_prefix(f);oldproof=builder.replay_old_additional(run);contract=extra.normalize_contract(f.cfg,f.root,qualification_only=True);proof=extra.terminal(f.c,oldproof,root=f.root,contract=contract,authority=f.q)
 docs=[run.intent,read(run.out/'NATIVE_LAUNCH.json'),read(run.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];snapshot=read(run.out/extra.SNAP)
 assert f.q['qualification_only']is True and f.cfg['qualification_only']is True
 assert all(x[extra.FIELD]==docs[0][extra.FIELD]for x in docs)and docs[0][extra.FIELD]['schema']=='DTC_STRACE_FUTURE_ENTRY_V3'
 assert all(x['additional_cpu_spare_memory_admission_binding']==docs[0]['additional_cpu_spare_memory_admission_binding']for x in docs)
 assert oldproof['additional_cpu_spare_memory_admission_strict']['status']=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'
 assert snapshot['scope_policy']['primary_statistics_excluded']==(kind=='IR')
 runs[kind]=dict(f=f,run=run,old=oldproof,contract=contract,proof=proof,snapshot=snapshot)
 if kind=='PRIMARY':
  check('PRIMARY_UNSPENT_actual_prefix_mockPopen_real_CPU2_IO_then_V3', [len(f.calls)==1,proof[extra.KEY]['schema']==extra.ID,proof[extra.KEY]['cross_profile_or_failed_cycles_equality_required']is False],dict(root=str(root),cohort=f.c,UUID=run.intent['uuid'],actual_native_observer_atomic_IO_CPU2_executed=True,all3bindings_equal=True,physics_and_Popen_are_explicit_mocks=True,source_runtime_snapshot_retained=True))
 else:
  consumer=load('A_private_original_consumer_IR',R/'tools/l2_results.py');cache={};sentinel=object();delegated=[]
  def oldsafe(c):delegated.append(c);return sentinel
  def loader(n,file):
   if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
   if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:oldproof)
   if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:cache['archive'])
   raise AssertionError('UNKNOWN_PHYSICS_ARCHIVE_FIXTURE_LEAF')
  def oldarchive(c):cache['archive']=archive_leaf(run);return cache['archive']
  consumer.safe_finish=oldsafe;consumer.load=loader;consumer.archive_closed=oldarchive;contract['qualification_loader_sha256']=sha(__file__)
  api=bridge.make_private_consumer(consumer,contract,extra,lambda:run.q);value=api['safe_finish'](run.c);assert value['state']==consumer.PASS,str(value)
  readonly=api['readonly_replay'](run.c);mirror=read(api['recovery_path'](run.c));canonical=read(api['result_path'](run.c))
  check('IR11_actual_prefix_real_CPU2_IO_V3_private_consumer_exclusion', [len(f.calls)==1,value['primary_statistics_excluded']is True,value['validated_union_authorized']is False,readonly==value,mirror==canonical],dict(root=str(root),cohort=f.c,UUID=run.intent['uuid'],IR_mirror_equals_privatecanonical=True,physics_archive_transport_device_are_explicit_mocks=True,old_negative_not_replaced=True))
  runs['IR'].update(api=api,sentinel=sentinel,delegated=delegated,consumer=consumer)
# Exact engineering four and old nonselected paths must never be reinterpreted
# as V3 PRIMARY/IR. Exercise actual frontend and actual private consumer routing.
f=runs['PRIMARY']['f'];q=f.q;contract4=read(f.cfg['exclusion_contract_path']);delegates=[]
def delegate(path,args):delegates.append(dict(path=path,args=args));return 'EXACT_OLD_ROUTE_SENTINEL'
for c in contract4['scope_cohorts']:
 value=f.front.main(['experiment','prepare',c,'--project','DTC_L1'],cfg=f.cfg,native_module=f.native,delegate=delegate)
 assert value=='EXACT_OLD_ROUTE_SENTINEL'and delegates[-1]['path']==f.cfg['v2_entry_path']
ir=runs['IR'];old4=next(iter(contract4['scope_cohorts']));oldout=ir['run'].root/'DTC/run/results/OLD_V2_PRIVATE';put(ir['run'].root/'control/qualification_ledger'/(old4+'.INTENT.json'),dict(output=str(oldout),**{extra.FIELD:dict(schema='DTC_STRACE_FUTURE_ENTRY_V2')}))
assert ir['api']['safe_finish'](old4)is ir['sentinel']
check('EXACT4_frontend_and_new_consumer_exact_current_V2_delegate',[len(delegates)==4],dict(frontend_delegated_exact4=[x['path']for x in delegates],consumer_oldsafe_value_preserved=True,actual4_qualified=False,no_V3_binding_created=True))
# Missing real four remains a production block. Check current readonly replay,
# reject CPU gate masquerading as production, and run actual private frontend
# with missing quorum BEFORE INTENT/Popen (no second mock model prefix).
actualq=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][extra.REQ]
missing=[]
for c in contract4['scope_cohorts']:missing.append(dict(cohort=c,error=reject(lambda c=c:extra.replay_v2_canary(c,actualq))))
prod_cfg=copy.deepcopy(f.cfg);prod_cfg.update(root=str(R),qualification_only=False);prod_q=copy.deepcopy(actualq);prod_q.pop('qualification_only',None)
prod_rejection=reject(lambda:extra.verify_release_prerequisite(prod_cfg,prod_q))
root=P(tempfile.mkdtemp(prefix='A_JOINT6_GATE_',dir=D));g=builder.build_fixture(root=root,extra_path=E/'bpf_extra_strict.py',consumer_path=E/'consumer_bridge.py',kind='PRIMARY');gate=P(g.cfg['canary4_prerequisite_path']);bad=read(gate);bad['kind']='MISSING_ACTUAL4_NOT_AN_ACCEPTED_CPU_STANDIN';put(gate,bad);g.cfg['canary4_prerequisite_sha256']=sha(gate);g.q['additional_operational_overlays'][g.producer.ID]=dict(g.producer.record(g.cfg),status='ACTIVE')
front_rejection=reject(lambda:g.front.main(['experiment','run-native',g.c,'--project','DTC_L1'],cfg=g.cfg,native_module=g.native,hooks=g.hooks,memory_cfg_override=g.memcfg))
check('ACTUAL4_current_missing_production_block_and_prefork_HOLD',[len(missing)==4,len(g.calls)==0,not(g.root/'control/qualification_ledger'/(g.c+'.INTENT.json')).exists()],dict(actual_current_four_readonly_replay_errors=missing,production_reject=prod_rejection,private_actual_front_reject=front_rejection,INTENT_written=False,Popen_calls=0,quorum_standin_not_actualrelease=True))
# A few bound negatives reuse the two prefixes, not another old suite/model.
tamper=[]
for kind,row in runs.items():
 if kind not in ['PRIMARY','IR']:continue
 run=row['run'];base=row['old'];contract=row['contract']
 bad=copy.deepcopy(base);bad['effective_options']['JOINT_CPU_BAD_OPTION']='forbidden';tamper.append(reject(lambda:extra.terminal(run.c,bad,run.root,contract,run.q)))
 bad=copy.deepcopy(base);bad.pop('additional_cpu_spare_memory_admission_strict');tamper.append(reject(lambda:extra.terminal(run.c,bad,run.root,contract,run.q)))
 path=run.out/'NATIVE_LAUNCH.json';saved=path.read_bytes();doc=read(path);doc.pop(extra.FIELD);put(path,doc)
 try:tamper.append(reject(lambda:extra.terminal(run.c,base,run.root,contract,run.q)))
 finally:path.write_bytes(saved)
 assert row['proof'][extra.KEY]['cross_profile_or_failed_cycles_equality_required']is False
check('positive_cycles_not_crossprofile_equal_full270_oldCPU2_3binding_tamper_reject',[len(tamper)==6],dict(rejections=tamper,PRIMARY_mock_cycles=runs['PRIMARY']['proof']['cycles'],IR_mock_cycles=runs['IR']['proof']['cycles'],not_measured_performance=True))
f=runs['PRIMARY']['f'];unselected='E2-DTCL2MLP-UNSELECTED-CPU-V1';value=f.front.main(['experiment','prepare',unselected,'--project','DTC_L1'],cfg=f.cfg,native_module=f.native,delegate=delegate);assert value=='EXACT_OLD_ROUTE_SENTINEL'and delegates[-1]['path']==f.cfg['default_native_entry']
spent=runs['PRIMARY']['run'].c;value=f.front.main(['experiment','prepare',spent,'--project','DTC_L1'],cfg=f.cfg,native_module=f.native,delegate=delegate);assert value=='EXACT_OLD_ROUTE_SENTINEL'and delegates[-1]['path']==f.cfg['default_native_entry']
assert ir['api']['safe_finish'](unselected)is ir['sentinel']
unknown='E2-DTCL2MLP-UNKNOWN-OBS-V99';unknownout=ir['run'].root/'DTC/run/results/UNKNOWN';put(ir['run'].root/'control/qualification_ledger'/(unknown+'.INTENT.json'),dict(output=str(unknownout),**{extra.FIELD:dict(schema='UNQUALIFIED_V99')}));before=len(ir['delegated']);hold=ir['api']['safe_finish'](unknown)
check('NONSELECTED_spent_exact_old_delegate_unknown_generation_HOLD',[hold['state']=='STRACE_V3_OBSERVATION_HOLD_PRESERVE',len(ir['delegated'])==before,not ir['api']['result_path'](unknown).exists()],dict(nonselected_and_spent_default_entry_exact=True,old_consumer_value_identity_preserved=True,unknown_generation_no_acceptance=True))
assert len(cases)==6
for path,h in pins.items():assert sha(path)==h,'SOURCE_DRIFT_DURING_JOINT6 '+path
output=dict(schema='FUTURE_BPF_V3_NEW_JOINT6_CPU_QUALIFICATION_V1',status='PASS_CPU_ONLY_NOT_ACTUAL4_RELEASE',UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),cases=cases,count=6,source_pins=pins,driver_sha256=sha(__file__),actual_native_observer_and_atomic_IO_CPU2_prefix_executed=True,actual_old_CPU2_IO_and_new_strict_replayed=True,physics_Popen_archive_transport_native_device_and_canaryquorum_leaves='EXPLICIT_PRIVATE_CPU_STANDINS_NOT_REAL_PERFORMANCE',actual4_qualified=False,production_release_eligible=False,production_mutations=0,actual_model_starts=0,new_grants=0,old_suites_rerun=False)
put(D/'JOINT6_CPU_QUALIFICATION.json',output);print(json.dumps(dict(path=str(D/'JOINT6_CPU_QUALIFICATION.json'),sha256=sha(D/'JOINT6_CPU_QUALIFICATION.json'),cases=6,source_pins=pins)))
