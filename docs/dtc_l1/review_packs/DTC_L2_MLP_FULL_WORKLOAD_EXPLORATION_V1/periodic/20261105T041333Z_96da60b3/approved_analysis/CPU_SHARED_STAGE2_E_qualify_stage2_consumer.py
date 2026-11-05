"""Focused Stage2 delta qualification: no real spawn, signal or model."""
import copy,hashlib,importlib.util,json,pathlib,tempfile,shutil,sys,types
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen':
  argv=args[1]
  if isinstance(argv,(list,tuple))and argv[:3]==['findmnt','-J','-T']:return
  raise AssertionError('No model/CPU fixture process spawn')
 if event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No process exec or signal')
sys.addaudithook(audit)
extra=load('stage2_observation',D/'bpf_extra_strict.py');bridge=load('stage2_consumer',D/'consumer_bridge.py')
checks=[]
def ok(n,v):assert v,n;checks.append(dict(name=n,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return True
 return False
# Real closed C0, exact historical sources and full original archive/native replay.
engine=load('actual_native_readonly',R/'tools/l2_native.py');q=engine.registered()[2]
gate=extra.replay_mixed_four_gate(q)
put(D/'ACTUAL_MIXED_GENERATION_GATE_READONLY.json',gate)
ok('actual_C0_old_byte_sources_full_replayed_gate_stays_one_of_four_HOLD',gate['accepted_real_count']==1 and gate['four_point_qualified']is False and gate['status']=='HOLD_REAL_ENGINEERING_FOUR_INCOMPLETE'and gate['rows'][0]['resource_source_sha256']==extra.OLD_SHARED_RESOURCE_SHA and gate['rows'][0]['observation_source_sha256']==extra.OLD_SHARED_OBSERVATION_SHA)
ok('qualification_authority_cannot_mint_real_gate',reject(lambda:extra.replay_closed_generation(gate['rows'][0]['cohort'],dict(q,qualification_only=True))))
# New Gaussian BPF path: actual producer/native/IO/resource prefix to mockPopen.
B=A/'agents/B/cpu_shared_timeslice_stage2_v1';builder=load('stage2_prefix_builder',B/'cpu_prefix_fixture.py')
root=P(tempfile.mkdtemp(prefix='CPU_STAGE2_CONSUMER_',dir=D));c='E2-DTCL2MLP-16f4c42373e4961e-DH-P0-OBSBPF-V1'
f=builder.build_fixture(root=root,extra_path=D/'bpf_extra_strict.py',consumer_path=D/'consumer_bridge.py',mode='BPF_REQUIRED',cohort=c)
run=builder.run_prefix(f);shared=builder.replay_new_resource(run)
contract=extra.normalize_contract(read(f.cfg['exclusion_contract_path']),root,f.cfg['exclusion_contract_sha256'],True,cfg=f.cfg)
consumer=load('stage2_original_finisher',R/'tools/l2_results.py');cache={};sentinel=object();delegates=[]
def oldsafe(c):delegates.append(c);return sentinel
def physics_loader(n,file):
 if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
 if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:run.base_proof)
 if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:cache['archive'])
 raise AssertionError('Unexpected fixture leaf '+file)
def archive_fixture(c):
 bundle=root/'ARCHIVE_TRANSPORT_STANDIN';restore=root/'DTC/run/recovery/CPU_STANDIN';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True);entries=[]
 for p in sorted(run.out.iterdir()):
  if p.is_file():entries.append(dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size));shutil.copyfile(p,restore/p.name)
 manifest=dict(cohort=c,source_root=str(run.out),entries=entries);put(bundle/'SOURCE_MANIFEST.json',manifest)
 raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 cache['archive']=dict(receipt=dict(cohort=c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=hashlib.sha256(raw).hexdigest(),archive_sha256='CPU_STANDIN_NOT_REAL_TRANSPORT'),independently_verified_entries=len(entries))
 if cache.get('deny_archive'):(restore/'CPU_SHARED_TIMESLICE_SNAPSHOT.json').write_bytes(b'CPU corrupted archive member')
 return cache['archive']
consumer.safe_finish=oldsafe;consumer.load=physics_loader;consumer.archive_closed=archive_fixture
contract['qualification_loader_sha256']=sha(__file__)
api=bridge.make_private_consumer(consumer,contract,extra,lambda:run.q);value=api['safe_finish'](c)
ok('actual_original_finish_clone_gaussian_BPF_complete_new_strict_before_accept',value.get('state')==consumer.PASS)
ok('Gaussian_ref_cycles_126kernels_and_honest_Shared_not_CPU2',value['cycles']==740717 and value['proof']['kernel_count']==126 and 'additional_cpu_spare_memory_admission_strict'not in value['proof'])
ok('canonical_mirror_equal_excluded_no_union',read(api['result_path'](c))==read(api['engineering_path'](c))and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False)
ok('new_generation_readonly_consumer_archive_replay',api['readonly_replay'](c)==value)
restore=P(cache['archive']['receipt']['native_restore'])/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';saved=restore.read_bytes();restore.write_bytes(saved+b' ')
ok('missing_or_tampered_new_resource_archive_member_rejected',reject(lambda:extra.verify_archive(c,cache['archive'],root,contract)));restore.write_bytes(saved)
rp=api['result_path'](c);ep=api['engineering_path'](c);rp.rename(rp.with_suffix('.PREIMAGE'));ep.rename(ep.with_suffix('.PREIMAGE'))
cache['deny_archive']=True;held=api['safe_finish'](c);cache['deny_archive']=False
ok('new_archive_failure_prevents_both_accepted_writes',held['state']=='CPU_SHARED_OBSERVATION_HOLD_PRESERVE'and not rp.exists()and not ep.exists())
rp.with_suffix('.PREIMAGE').rename(rp);ep.with_suffix('.PREIMAGE').rename(ep)
ok('nonselected_exact_previous_safe_no_newcfg_read',api['safe_finish']('UNSELECTED_OLD_COHORT')is sentinel and delegates==['UNSELECTED_OLD_COHORT'])
report=dict(schema='CPU_SHARED_STAGE2_CONSUMER_DELTA_QUALIFICATION',status='PASS',count=len(checks),checks=checks,root=str(root),sources={p:sha(D/p)for p in ['resource_extra_strict.py','bpf_extra_strict.py','consumer_bridge.py']},driver_sha256=sha(__file__),actual_C0_gate_file_sha256=sha(D/'ACTUAL_MIXED_GENERATION_GATE_READONLY.json'),new_scope_actual_models_qualified=False,production_four_gate_qualified=False,models_started=0,new_grants=0,production_changes=0,limitations=['New Gaussian original physics/progress/guard/resource sampling and archive transport/device are CPU stand-ins; actual prefix, IO, resource/observation strict and original finish code execute.','Actual C0 full real archive/native readonly replay uses captured old byte sources. Other three have no actual acceptance; genuine four gate remains HOLD.'])
put(D/'CPU_STAGE2_CONSUMER_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',count=len(checks),root=str(root),sources=report['sources'])))
