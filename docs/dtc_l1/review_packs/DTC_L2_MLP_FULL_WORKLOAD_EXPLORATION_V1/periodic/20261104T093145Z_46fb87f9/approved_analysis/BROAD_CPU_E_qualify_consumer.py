"""Focused broad SharedCPU primary/IR integration; no real model/process."""
import copy,hashlib,importlib.util,json,pathlib,tempfile,shutil,types,sys
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No actual spawn/signal')
sys.addaudithook(audit)
B=A/'agents/B/broad_shared_cpu_v1';builder=load('E_broad_actual_prefix_fixture',B/'cpu_prefix_fixture.py')
extra=load('E_broad_extra',D/'bpf_extra_strict.py');bridge=load('E_broad_bridge',D/'consumer_bridge.py');resource=load('E_broad_resource',D/'resource_extra_strict.py')
checks=[];cases=[]
def ok(name,condition):assert condition,name;checks.append(dict(name=name,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return True
 return False
for kind in ['PRIMARY','IR']:
 root=P(tempfile.mkdtemp(prefix='CPU_BROAD_'+kind+'_',dir=D));f=builder.build_fixture(root=root,extra_path=D/'bpf_extra_strict.py',consumer_path=D/'consumer_bridge.py',kind=kind)
 run=builder.run_prefix(f);shared=builder.replay_new_resource(run)
 contract=extra.normalize_contract(run.cfg,root,qualification_only=True);complete=extra.terminal(run.c,shared,root,contract,run.q)
 ok(kind+'_real_native_IO_dynamic_resource_and_BPF_strict_to_mockPopen',complete[extra.KEY]['schema']==extra.ID and complete[extra.KEY]['status']=='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO'and complete['additional_cpu_shared_timeslice_strict']['schema']==resource.ID and 'additional_cpu_spare_memory_admission_strict'not in complete)
 ok(kind+'_no_crossprofile_or_failed_cycles_equality',complete[extra.KEY]['cross_profile_or_failed_cycles_equality_required']is False and complete['cycles']>0)
 bad=copy.deepcopy(shared);bad['effective_options']['CPU_BAD_EXTRA']='tampered'
 ok(kind+'_full270_actual_options_still_mandatory',reject(lambda:extra.terminal(run.c,bad,root,contract,run.q)))
 bad=copy.deepcopy(shared);bad['kernel_count']-=1
 ok(kind+'_complete_frozen_kernel_population_mandatory',reject(lambda:extra.terminal(run.c,bad,root,contract,run.q)))
 consumer=load('E_broad_original_consumer_'+kind,R/'tools/l2_results.py');cache={};sentinel=object();delegates=[]
 def oldsafe(c):delegates.append(c);return sentinel
 def loader(n,file):
  if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
  if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:run.base_proof)
  if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:cache['archive'])
  raise AssertionError('Unexpected fixture leaf '+file)
 def oldarchive(c):
  bundle=root/'ARCHIVE_TRANSPORT_STANDIN';restore=root/'DTC/run/recovery/CPU_STANDIN';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True);entries=[]
  for p in sorted(run.out.iterdir()):
   if p.is_file():entries.append(dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size));shutil.copyfile(p,restore/p.name)
  if cache.get('bad_archive'):entries=[x for x in entries if x['path']!='CPU_SHARED_TIMESLICE_SNAPSHOT.json']
  manifest=dict(cohort=c,source_root=str(run.out),entries=entries);put(bundle/'SOURCE_MANIFEST.json',manifest);raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
  cache['archive']=dict(receipt=dict(cohort=c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=hashlib.sha256(raw).hexdigest(),archive_sha256='CPU_TRANSPORT_STANDIN'),independently_verified_entries=len(entries));return cache['archive']
 consumer.safe_finish=oldsafe;consumer.load=loader;consumer.archive_closed=oldarchive;contract['qualification_loader_sha256']=sha(__file__)
 api=bridge.make_private_consumer(consumer,contract,extra,lambda:run.q);value=api['safe_finish'](run.c)
 ok(kind+'_actual_original_finisher_accepts_only_complete_dynamic_AND_archive',value.get('state')==consumer.PASS and api['readonly_replay'](run.c)==value)
 ok(kind+'_exact_Stage2_engineering_underlay_delegation',api['safe_finish']('E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1')is sentinel and delegates[-1].endswith('-OBSCTRL-V1'))
 if kind=='IR':
  ok('IR_new_result_mirror_preserves_exclusion_unionFalse',read(api['recovery_path'](run.c))==value and value['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False)
  original=root/'analysis'/(f.spec['incident_recovery_trial_lineage']['original_cohort']+'.RESULT.json');oldbytes=original.read_bytes();bad=read(original);bad['cycles']=1;put(original,bad)
  ok('IR_old_negative_cannot_be_substituted_by_new_performance',reject(lambda:extra.terminal(run.c,shared,root,contract,run.q)));original.write_bytes(oldbytes)
  summary=load('E_broad_unchanged_primary_summary',R/'tools/l2_results.py');matrix=read(R/'control/MATRIX_CURRENT.json');a=summary.summarize(matrix,{run.c:dict(value,cycles=1)});b=summary.summarize(matrix,{});a.pop('utc');b.pop('utc')
  ok('IR_even_one_cycle_cannot_enter_primary350_GM',a==b)
 else:ok('PRIMARY_result_is_main_identity_without_recovery_mirror',value['primary_statistics_excluded']is False and not api['recovery_path'](run.c).exists())
 rp=api['result_path'](run.c);ep=api['recovery_path'](run.c);rp.rename(rp.with_suffix('.PREIMAGE'))
 if ep.exists():ep.rename(ep.with_suffix('.PREIMAGE'))
 cache['bad_archive']=True;held=api['safe_finish'](run.c);cache['bad_archive']=False
 ok(kind+'_missing_new_resource_archive_member_rehashed_manifest_blocks_accepted',held['state']=='BROAD_SHARED_OBSERVATION_HOLD_PRESERVE'and not rp.exists()and not ep.exists())
 rp.with_suffix('.PREIMAGE').rename(rp)
 if ep.with_suffix('.PREIMAGE').exists():ep.with_suffix('.PREIMAGE').rename(ep)
 launch=run.out/'NATIVE_LAUNCH.json';saved=launch.read_bytes();bad=read(launch);bad.pop('additional_cpu_shared_timeslice_binding');put(launch,bad)
 ok(kind+'_missing_one_dynamic_resource_binding_HOLD',reject(lambda:resource.terminal(run.c,run.base_proof,root,run.q)));launch.write_bytes(saved)
 cases.append(dict(kind=kind,root=str(root),cohort=run.c,cycles=value['cycles'],scientific_role=value['scientific_role'],RESULT_sha256=sha(rp)))
report=dict(schema='E_BROAD_SHARED_PREFIX_CONSUMER_CPU_QUALIFICATION_V1',status='PASS',count=len(checks),checks=checks,cases=cases,sources={n:sha(D/n)for n in ['resource_extra_strict.py','bpf_extra_strict.py','consumer_bridge.py']},driver_sha256=sha(__file__),actual_Main_gate_sha256=extra.ACTUAL_FOUR_GATE_SHA,models_started=0,new_grants=0,production_changes=0,actual_primary_or_IR_physics_qualified=False,actual_archive_transport_qualified=False,limitations=['Actual original native/observer/atomic IO/new dynamic resource and observation strict execute to mocked Popen; actual original consumer finish code is privately cloned.','Original physics/progress/native resource sampling and archive transport/device leaves are explicit CPU stand-ins.','Uses real source-bound Main four-gate and separate Main scope approval. These qualify the observation policy prerequisite, not actual PRIMARY/IR results.'])
put(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',count=len(checks),cases=cases,sources=report['sources'])))
