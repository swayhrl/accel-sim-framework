"""New actual-prefix V3 consumer cases, mocked process/physics/archive leaves."""
import copy,hashlib,importlib.util,json,pathlib,tempfile,shutil,types,sys
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('CPU qualification forbids actual process/signal '+event)
sys.addaudithook(audit)
B=A/'agents/B/strace_bpf_future_entry_v3'
builder=load('E_actual_B_V3_prefix_fixture',B/'cpu_prefix_fixture.py')
extra=load('E_actual_V3_extra',D/'bpf_extra_strict.py');bridge=load('E_actual_V3_bridge',D/'consumer_bridge.py')
checks=[];cases=[]
def ok(n,fn):fn();checks.append({'name':n,'status':'PASS'})
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected explicit rejection')
def archive_fixture(run):
 out=run.out;bundle=run.root/'ARCHIVE_LEAF_STANDIN';restore=run.root/'DTC/run/recovery/CPU_LEAF_STANDIN';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True)
 entries=[]
 for p in sorted(out.iterdir()):
  if p.is_file():entries.append(dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size));shutil.copyfile(p,restore/p.name)
 manifest=dict(cohort=run.c,source_root=str(out),entries=entries);put(bundle/'SOURCE_MANIFEST.json',manifest)
 canonical=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 return dict(receipt=dict(cohort=run.c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=hashlib.sha256(canonical).hexdigest(),archive_sha256='CPU_ARCHIVE_LEAF_STANDIN_NOT_TRANSPORT'),independently_verified_entries=len(entries))
for kind in ('PRIMARY','IR'):
 root=P(tempfile.mkdtemp(prefix='CPU_V3_'+kind+'_',dir=D))
 f=builder.build_fixture(root=root,extra_path=D/'bpf_extra_strict.py',consumer_path=D/'consumer_bridge.py',kind=kind)
 run=builder.run_prefix(f);old=builder.replay_old_additional(run)
 contract=extra.normalize_contract(run.cfg,root,qualification_only=True)
 complete=extra.terminal(run.c,old,root,contract,run.q)
 ok(kind+'_actual_native_observer_IO_CPU2_to_mockPopen_then_new_strict',lambda:extra.require(complete[extra.KEY]['schema']==extra.ID,'V3strict'))
 ok(kind+'_actual_cycles_not_reference_P0_or_failed_equality',lambda:extra.require(complete[extra.KEY]['cross_profile_or_failed_cycles_equality_required']is False and complete['cycles']==f.reference_cycles,'cycles'))
 pp=copy.deepcopy(old);pp['effective_options']['CPU_ONLY_BAD_OPTION']='bad'
 ok(kind+'_actual270_option_tamper_rejected',lambda:reject(lambda:extra.terminal(run.c,pp,root,contract,run.q)))
 pp=copy.deepcopy(old);pp['kernel_count']-=1
 ok(kind+'_partial_ROI_count_rejected',lambda:reject(lambda:extra.terminal(run.c,pp,root,contract,run.q)))
 launch=run.out/'NATIVE_LAUNCH.json';saved=launch.read_bytes();bad=read(launch);bad.pop(extra.FIELD);put(launch,bad)
 ok(kind+'_missing_one_of_three_observation_bindings_rejected',lambda:reject(lambda:extra.terminal(run.c,old,root,contract,run.q)))
 launch.write_bytes(saved)
 act=run.out/extra.ACT;pid=run.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';sa,sp=act.read_bytes(),pid.read_bytes();bad=read(act);bad['model']['status_utf8']=bad['model']['status_utf8'].replace('Seccomp:\t2','Seccomp:\t0').replace('Seccomp_filters:\t1','Seccomp_filters:\t0');put(act,bad);pd=read(pid);pd['strace_observation_activation_sha256']=sha(act);put(pid,pd)
 ok(kind+'_silent_fallback_after_rebinding_ACT_SHA_rejected',lambda:reject(lambda:extra.terminal(run.c,old,root,contract,run.q)))
 act.write_bytes(sa);pid.write_bytes(sp)
 if kind=='IR':
  original=run.root/'analysis'/(f.spec['incident_recovery_trial_lineage']['original_cohort']+'.RESULT.json');saved=original.read_bytes();bad=read(original);bad['cycles']=1;put(original,bad)
  ok('IR_old_negative_is_immutable_and_never_accepted_substitute',lambda:reject(lambda:extra.terminal(run.c,old,root,contract,run.q)))
  original.write_bytes(saved)
 consumer=load('E_actual_original_consumer_'+kind,R/'tools/l2_results.py');delegated=[];sentinel=object()
 def oldsafe(c):delegated.append(c);return sentinel
 archive_cache={}
 def loader(n,file):
  if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
  if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:old)
  if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:archive_cache['value'])
  raise AssertionError('Unknown fixture leaf '+file)
 def oldarchive(c):
  archive_cache['value']=archive_fixture(run);return archive_cache['value']
 consumer.safe_finish=oldsafe;consumer.load=loader;consumer.archive_closed=oldarchive
 contract['qualification_loader_sha256']=sha(__file__)
 api=bridge.make_private_consumer(consumer,contract,extra,lambda:run.q)
 value=api['safe_finish'](run.c)
 extra.require(value['state']==consumer.PASS,str(value))
 ok(kind+'_actual_original_finish_clone_writes_only_after_new_strict_archive_AND',lambda:extra.require(api['result_path'](run.c).exists()and extra.KEY in value['proof']and 'additional_strace_bpf_archive_verification'in value['archive'],'publish'))
 ok(kind+'_complete_readonly_consumer_replay',lambda:extra.require(api['readonly_replay'](run.c)==value,'replay'))
 if kind=='IR':
  ok('IR_canonical_and_independent_mirror_equal_unionFalse',lambda:extra.require(read(api['recovery_path'](run.c))==read(api['result_path'](run.c))and value['validated_union_authorized']is False and value['primary_statistics_excluded']is True,'IRmirror'))
  source=load('E_actual_350_summary_only',R/'tools/l2_results.py');matrix=read(R/'control/MATRIX_CURRENT.json')
  a=source.summarize(matrix,{run.c:dict(value,cycles=1)});b=source.summarize(matrix,{})
  a.pop('utc');b.pop('utc')
  ok('IR_malicious_one_cycle_cannot_enter_actual350_GM_or_coverage',lambda:extra.require(a==b,'primarycontamination'))
 else:ok('PRIMARY_has_no_recovery_mirror',lambda:extra.require(not api['recovery_path'](run.c).exists()and value['primary_statistics_excluded']is False,'primary'))
 ar=copy.deepcopy(archive_cache['value']);manifest_path=P(ar['receipt']['target_mount_path'])/'SOURCE_MANIFEST.json';saved=manifest_path.read_bytes();manifest=read(manifest_path);manifest['entries']=[x for x in manifest['entries']if x['path']!=extra.SNAP];put(manifest_path,manifest);raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode();ar['receipt']['manifest_sha256']=hashlib.sha256(raw).hexdigest();ar['independently_verified_entries']=len(manifest['entries'])
 ok(kind+'_missing_archived_snapshot_even_rehashed_manifest_rejected',lambda:reject(lambda:extra.verify_archive(run.c,ar,root,contract)))
 manifest_path.write_bytes(saved)
 restored=P(archive_cache['value']['receipt']['native_restore'])/extra.SNAP;saved=restored.read_bytes();restored.write_bytes(saved+b' ')
 ok(kind+'_wrong_native_restore_SHA_rejected',lambda:reject(lambda:extra.verify_archive(run.c,archive_cache['value'],root,contract)))
 restored.write_bytes(saved)
 # A separate unaccepted fixture result path cannot be promoted if the archive
 # verifier fails. Reuse immutable execution files, not a second model start.
 value_path=api['result_path'](run.c);existing=value_path.read_bytes();value_path.rename(value_path.with_suffix('.ACCEPTED_FIXTURE_PREIMAGE'))
 if api['recovery_path'](run.c).exists():api['recovery_path'](run.c).rename(api['recovery_path'](run.c).with_suffix('.MIRROR_PREIMAGE'))
 oldverify=extra.verify_archive
 def reject_archive(*a,**k):raise extra.ObservationHold('CPU deliberate new archive failure')
 extra.verify_archive=reject_archive
 failed=api['safe_finish'](run.c);extra.verify_archive=oldverify
 ok(kind+'_archive_failure_HOLD_before_any_accepted_write',lambda:extra.require(failed['state']=='STRACE_V3_OBSERVATION_HOLD_PRESERVE'and not api['result_path'](run.c).exists()and not api['recovery_path'](run.c).exists(),'order'))
 value_path.with_suffix('.ACCEPTED_FIXTURE_PREIMAGE').rename(value_path)
 if api['recovery_path'](run.c).with_suffix('.MIRROR_PREIMAGE').exists():api['recovery_path'](run.c).with_suffix('.MIRROR_PREIMAGE').rename(api['recovery_path'](run.c))
 ok(kind+'_nonselected_exact_previous_V2_safe_delegate',lambda:extra.require(api['safe_finish']('OLD_V2_ENGINEER_UNCHANGED')is sentinel,'delegate'))
 cases.append({'kind':kind,'root':str(root),'cohort':run.c,'cycles':value['cycles'],'q_uuid':run.intent['uuid'],'role':value['scientific_role'],'RESULT_sha256':sha(api['result_path'](run.c))})
result={'schema':'DTC_BPF_V3_ACTUAL_PREFIX_CONSUMER_CPU_QUALIFICATION','status':'PASS','checks':checks,'count':len(checks),'cases':cases,
 'sources':{'extra':sha(D/'bpf_extra_strict.py'),'consumer':sha(D/'consumer_bridge.py'),'producer':sha(B/'strace_entry.py'),'frontend':sha(B/'bpf_frontend.py'),'entry':sha(B/'native-entry/bin/experiment'),'fixture':sha(B/'cpu_prefix_fixture.py')},'driver_sha256':sha(__file__),
 'scope':'Actual native/observer/atomic IO/CPU2 prefix to mocked Popen and oldCPU2+IO strict, then actual new V3 strict and cloned original consumer. Physics original terminal and archive transport/native-device leaves are explicit stand-ins.',
 'actual_physics_qualified':False,'actual_archive_transport_qualified':False,'production_release_qualified':False,'models_started':0,'new_grants':0,'production_changes':0}
put(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json',result)
print(json.dumps({'status':'PASS','checks':len(checks),'cases':cases}))
