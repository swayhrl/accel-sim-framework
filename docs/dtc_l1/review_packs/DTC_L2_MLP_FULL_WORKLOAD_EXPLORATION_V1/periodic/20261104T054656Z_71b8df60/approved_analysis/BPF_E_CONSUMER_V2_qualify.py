"""New targeted CPU checks, actual B native-prefix with mocked fork only."""
import sys
sys.dont_write_bytecode=True
import ast,copy,hashlib,importlib.util,json,pathlib,tempfile,threading,types
P=pathlib.Path;HERE=P(__file__).resolve().parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def audit(event,args):
 if event in ['subprocess.Popen','os.system','os.fork','os.forkpty','os.exec','os.kill','os.killpg']:raise RuntimeError('CPU_QUALIFICATION_FORBIDS_REAL_SPAWN_OR_SIGNAL '+event)
sys.addaudithook(audit)
def loadmod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
extra=loadmod('new_real_observation_strict',HERE/'bpf_extra_strict.py');bridge=loadmod('new_real_consumer_bridge',HERE/'consumer_bridge.py')
prefix=loadmod('actual_B_cpu_prefix',A/'agents/B/strace_bpf_future_entry_v2/cpu_prefix_fixture.py')
archive_fixture=loadmod('E_archive_fixture',HERE/'cpu_fixture.py')
plan=read(A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json')
main_spec=read(HERE/'MAIN_DRAFT_SPEC.source.json')
checks=[];limits=['Actual native/observer/atomicIO/CPU2 prefix ends at MOCK Popen; audit hook forbids every real spawn/exec/kill.',
 'Original physics proof is a labelled accepted-reference CPU leaf stand-in; actual old CPU2 and IO strict replay is performed; no simulator raw physics is claimed.',
 'Archive gate uses synthetic independently-reported full archive plus copied required files; not a genuine tar/native2128 acceptance.',
 'Temporary QA/readback are explicitly qualification-only stand-ins, forbidden for production q.qualification_only absent.']
def ck(n,c):
 assert c,n
 checks.append(n)
def build(mode):
 root=P(tempfile.mkdtemp(prefix='CPU_COUPLE_',dir=HERE));row=copy.deepcopy(next(x for x in plan['rows']if x['program']=='heartwall'and x['mode']==mode))
 lineage=copy.deepcopy(main_spec['engineering_observation_canary_lineage']);lineage['mode']=mode
 f=prefix.build_fixture(root=root,extra_path=HERE/'bpf_extra_strict.py',consumer_path=HERE/'consumer_bridge.py',mode=mode,cohort=row['cohort'],lineage=lineage)
 # Resource adjustment remains outside science projection, before new binding.
 f.spec['estimated_peak_model_RAM_bytes']+=1024;f.resolved['estimated_peak_model_RAM_bytes']+=1024
 put(root/'control/specs'/(f.c+'.json'),f.spec);put(root/'control'/(f.c+'_SPEC.json'),f.spec)
 db=read(root/'control/dispatch_bindings'/(f.c+'.json'));db['canonical_spec_sha256']=sha(root/'control/specs'/(f.c+'.json'));db['resolved_spec_sha256']=extra.objsha(f.resolved);put(root/'control/dispatch_bindings'/(f.c+'.json'),db);f.q['admitted_specs'][f.c]=db['canonical_spec_sha256']
 reference_path=R/'analysis'/(row['reference_cohort']+'.RESULT.json');dest=root/'analysis'/reference_path.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(reference_path.read_bytes())
 formal=extra.MAIN_EXCLUSION_PATH;contract=extra.normalize_contract(read(formal),root,sha(formal),True);contract['qualification_loader_sha256']=sha(__file__)
 result=prefix.run_prefix(f);physics={k:v for k,v in copy.deepcopy(read(reference_path)['proof']).items()if not k.startswith('additional_')}
 physics.update(result.base_proof);physics['CPU_PHYSICS_LEAF_STANDIN']=True;result.base_proof=physics
 proof=prefix.replay_old_additional(result)
 return dict(root=root,c=f.c,q=f.q,contract=contract,out=result.out,proof=proof,prefix=result,CPU_ONLY=True)
def verify(f):return extra.terminal(f['c'],copy.deepcopy(f['proof']),root=f['root'],contract=f['contract'],authority=f['q'],readonly=False)
def expect_hold(name,fn):
 try:fn()
 except Exception:checks.append(name);return
 raise AssertionError('Expected HOLD '+name)
bpff=build('BPF_REQUIRED');ctrl=build('DEFAULT_CONTROL')
for f in [bpff,ctrl]:
 proof=verify(f);ck('actual producer '+proof[extra.KEY]['mode']+' strict and private resource amendment pass',proof[extra.KEY]['activation']['status'].startswith('PASS_'))
ck('DEFAULT_CONTROL is explicit no BPF rather than automatic fallback',read(ctrl['out']/extra.ACT)['verdict']['explicit_default_control']is True)
def mutate_file(f,path,change,action):
 data=P(path).read_bytes();saved=copy.deepcopy(f['q']['consumed'][f['c']])
 try:
  obj=json.loads(data);change(obj);put(path,obj);action()
 finally:P(path).write_bytes(data);f['q']['consumed'][f['c']]=saved
pidpath=bpff['out']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
mutate_file(bpff,pidpath,lambda x:x.pop(extra.FIELD),lambda:expect_hold('missing third binding blocks strict',lambda:verify(bpff)))
snap=read(bpff['out']/extra.SNAP);fork=read(bpff['out']/extra.FORK);act=read(bpff['out']/extra.ACT);launch=read(bpff['out']/'NATIVE_LAUNCH.json');pid=read(pidpath)
bad=copy.deepcopy(act);bad['model']['status_utf8']=bad['model']['status_utf8'].replace('Seccomp:\t2','Seccomp:\t0').replace('Seccomp_filters:\t1','Seccomp_filters:\t0')
expect_hold('silent fallback rejected despite spoofed PASS verdict',lambda:extra.verify_activation(bad,snap,fork,launch,pid))
bad=copy.deepcopy(act);bad['model']['start_ticks']+=1
expect_hold('wrong model start generation rejected',lambda:extra.verify_activation(bad,snap,fork,launch,pid))
badlaunch=dict(launch,launcher_pid=launch['launcher_pid']+7)
expect_hold('wrong tracer launcher rejected',lambda:extra.verify_activation(act,snap,fork,badlaunch,pid))
bad=copy.deepcopy(snap);bad['baseline_preINTENT']['status_utf8']=bad['baseline_preINTENT']['status_utf8'].replace('Seccomp_filters:\t0','Seccomp_filters:\t1')
expect_hold('inherited unknown baseline rejected',lambda:extra.verify_activation(act,bad,fork,launch,pid))
mutate_file(bpff,bpff['out']/extra.SNAP,lambda x:x['source_snapshots']['producer'].update(utf8='WRONG_SOURCE'),lambda:expect_hold('snapshot source tamper rejected',lambda:verify(bpff)))
spec=read(bpff['root']/'control/specs'/(bpff['c']+'.json'));bad=copy.deepcopy(spec);bad['expected_options']['-gpgpu_clock_domains']=['1:1:1:1']
expect_hold('science projection refuses physics change',lambda:extra.verify_science_rule(bad,bpff['contract']['cohorts'][bpff['c']],bpff['contract']))
bad=copy.deepcopy(spec);bad['host_cpu']=131
expect_hold('canonical CPU cannot be rebound instead of separate dispatch resolved spec',lambda:extra.verify_science_rule(bad,bpff['contract']['cohorts'][bpff['c']],bpff['contract']))
badbase=copy.deepcopy(bpff['proof']);badbase['performance_accepted']=False
expect_hold('old original performance strict cannot be waived',lambda:extra.terminal(bpff['c'],badbase,root=bpff['root'],contract=bpff['contract'],authority=bpff['q']))
badbase=copy.deepcopy(bpff['proof']);badbase.pop('additional_cpu_spare_memory_admission_strict')
expect_hold('old CPU2 strict cannot be waived',lambda:extra.terminal(bpff['c'],badbase,root=bpff['root'],contract=bpff['contract'],authority=bpff['q']))
# A real original finisher code object with isolated IO/physics/archive leaves.
consumer=loadmod('isolated_original_consumer',R/'tools/l2_results.py');consumer.R=bpff['root'];events=[];archive_box={}
def fake_loader(name,file):
 if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,bpff['q'],None))
 if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:(events.append('OLD_STRICT')or prefix.replay_old_additional(bpff['prefix'])))
 if file=='l2_outbox.py':
  def archive(c):archive_box['value']=archive_fixture.archive(bpff);put(bpff['root']/'control'/(c+'_ARCHIVE_RECEIPT.json'),archive_box['value'])
  return types.SimpleNamespace(archive=archive,verify=lambda c:copy.deepcopy(archive_box['value']))
 raise AssertionError(file)
consumer.load=fake_loader
private=bridge.make_private_consumer(consumer,bpff['contract'],extra,lambda:bpff['q'])
value=private['finish_evidence'](bpff['c'])
ck('actual original finish code writes canonical plus independent engineer mirror only after archive gate',consumer.accepted(value)and private['result_path'](bpff['c']).exists()and read(private['engineering_path'](bpff['c']))==value and value['primary_statistics_excluded'])
oldbytes=private['result_path'](bpff['c']).read_bytes();ck('readonly replay accepts exact chain without changing RESULT',private['readonly_replay'](bpff['c'])==value and oldbytes==private['result_path'](bpff['c']).read_bytes())
archive=archive_box['value'];manifestpath=P(archive['receipt']['target_mount_path'])/'SOURCE_MANIFEST.json'
def missing_key(m):m['entries']=[x for x in m['entries']if x['path']!=extra.ACT]
mutate_file(bpff,manifestpath,missing_key,lambda:expect_hold('missing archive activation refuses final verification',lambda:extra.verify_archive(bpff['c'],archive,root=bpff['root'],contract=bpff['contract'])))
restore=P(archive['receipt']['native_restore'])/extra.ACT;data=restore.read_bytes();restore.write_bytes(b'corrupted restoration')
expect_hold('native restored sidecar SHA mismatch rejected',lambda:extra.verify_archive(bpff['c'],archive,root=bpff['root'],contract=bpff['contract']));restore.write_bytes(data)
# Pure existing summary consumes exact MATRIX cohorts only, even with malicious1cycle.
scope=read(R/'control/MATRIX_CURRENT.json');refC=bpff['contract']['cohorts'][bpff['c']]['reference_cohort'];reference=read(bpff['root']/'analysis'/(refC+'.RESULT.json'))
before=consumer.summarize(scope,{refC:reference});malicious=copy.deepcopy(value);malicious['cycles']=1;malicious['proof']['cycles']=1
after=consumer.summarize(scope,{refC:reference,bpff['c']:malicious})
ck('malicious same-input P0 engineer1cycle cannot change original primary table GM or parents',all(before[k]==after[k]for k in ['table','comparisons','aggregates','programs']))
legacy='CPU_LEGACY';put(bpff['root']/'analysis'/(legacy+'.RESULT.json'),dict(state='LEGACY_EXACT',cohort=legacy))
count=len(events);ck('non-scope exact original finish bypasses new observation reads',private['finish_evidence'](legacy)['state']=='LEGACY_EXACT'and len(events)==count)
# Archive incompleteness is refused BEFORE either accepted RESULT is created.
badconsumer=loadmod('isolated_incomplete_archive_consumer',R/'tools/l2_results.py');badconsumer.R=ctrl['root'];badarchive={}
def bad_loader(name,file):
 if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,ctrl['q'],None))
 if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:prefix.replay_old_additional(ctrl['prefix']))
 if file=='l2_outbox.py':
  def archive(c):
   a=archive_fixture.archive(ctrl);mp=P(a['receipt']['target_mount_path'])/'SOURCE_MANIFEST.json';m=read(mp);m['entries']=[x for x in m['entries']if x['path']!=extra.ACT];put(mp,m)
   a['receipt']['manifest_sha256']=hashlib.sha256((json.dumps(m,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest();a['independently_verified_entries']=len(m['entries']);badarchive['a']=a;put(ctrl['root']/'control'/(c+'_ARCHIVE_RECEIPT.json'),a)
  return types.SimpleNamespace(archive=archive,verify=lambda c:badarchive['a'])
 raise AssertionError(file)
badconsumer.load=bad_loader;badbridge=bridge.make_private_consumer(badconsumer,ctrl['contract'],extra,lambda:ctrl['q'])
negative=badbridge['safe_finish'](ctrl['c'])
ck('missing archived activation blocks canonical AND mirror accepted writes',negative['state']=='ENGINEERING_OBSERVATION_HOLD_PRESERVE'and not badbridge['result_path'](ctrl['c']).exists()and not badbridge['engineering_path'](ctrl['c']).exists())
# Actual ops.post expression, same frame-private consumer instance, exact restore.
fakeframe=types.SimpleNamespace(f_locals=dict(consumer=consumer,engine=types.SimpleNamespace(registered=lambda:(None,None,bpff['q'],None)),res=types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=types.SimpleNamespace(lock=threading.RLock()))))
oldrefs=(consumer.safe_finish,consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
cfgfile=bpff['root']/'CONFIG.json'
bridge.install_on_frame(fakeframe,cfgfile,extra.MAIN_EXCLUSION_PATH,extra.MAIN_EXCLUSION_SHA,lambda:None,qualification_loader_sha256=sha(__file__))
ck('readiness checks actual frame-private safe path and preserves every old callback',bridge.consumer_check(fakeframe,read(cfgfile))and oldrefs[1:]==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed))
text=(R/'tools/l2_ops.py').read_text();tree=ast.parse(text);calls=[x for x in ast.walk(tree)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=='submit'and x.args and isinstance(x.args[0],ast.Attribute)and isinstance(x.args[0].value,ast.Name)and x.args[0].value.id=='consumer'and x.args[0].attr=='safe_finish'];assert len(calls)==1
class Immediate:
 def submit(self,fn,c):return fn(c)
expression=ast.fix_missing_locations(ast.Expression(calls[0]));post_value=eval(compile(expression,'actual_ops_post_expression','eval'),dict(archive_pool=Immediate(),consumer=consumer,c=bpff['c']))
ck('actual ops.post expression hits mandatory new chain on same consumer',post_value==value and consumer.safe_finish is not oldrefs[0])
setattr(sys.modules['__main__'],bridge.B_OWNER_MARKER,object())
expect_hold('consumer restore rejects wrong order before future dispatcher',lambda:bridge.restore_in_owner(lambda:None));delattr(sys.modules['__main__'],bridge.B_OWNER_MARKER)
bridge.restore_in_owner(lambda:None)
ck('same-object restore exactly recovers all original callbacks',oldrefs==(consumer.safe_finish,consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed))
o=dict(schema='STRACE_BPF_E_CPU_DISCRIMINATION_V2',status='PASS_TARGETED_CPU_NOT_PRODUCTION_ACCEPTANCE',checks=checks,check_count=len(checks),
 sources={str(p):sha(p)for p in [HERE/'bpf_extra_strict.py',HERE/'consumer_bridge.py',A/'agents/B/strace_bpf_future_entry_v2/strace_entry.py',A/'agents/B/strace_bpf_future_entry_v2/cpu_prefix_fixture.py',R/'tools/l2_results.py']},
 actual_B_prefix_roots=[str(bpff['root']),str(ctrl['root'])],limitations=limits,old_tests_rerun=False,actual_simulations=0,real_spawns=0,production_mutations=False,new_grants=0,Git_accessed=False)
put(HERE/'CPU_QUALIFICATION.json',o);print(json.dumps(o))
