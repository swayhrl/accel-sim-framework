"""Real A native-binding/IO-producer/new extra replay CPU fixture, no model."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys,types
P=pathlib.Path;H=P(__file__).resolve().parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
af=load('actual_A_fixture',A/'agents/A/cpu_spare_memory_v2/cpu_fixture_v2.py')
f=af.fixture(owner_path=H/'cpu_owner.py',extra_path=H/'cpu_extra_strict.py')
lib=f.lib;cfg=f.cfg;q=f.q;root=f.root;C=f.points[1]
joint_path=P(sys.argv[1])if len(sys.argv)>1 else None
if joint_path:
 qa=read(joint_path);assert qa['status']=='PASS'and qa['qualified_sources']=={r:cfg[r+'_sha256']for r in lib.ROLES}
 P(cfg['QA_path']).write_bytes(joint_path.read_bytes())
else:
 qa=read(cfg['QA_path']);qa.update(native_prefix_qualified=True,joint_strict_qualified=True);put(cfg['QA_path'],qa)
cfg['QA_sha256']=sha(cfg['QA_path'])
back=read(cfg['readback_path']);back['QA_sha256']=cfg['QA_sha256'];put(cfg['readback_path'],back);cfg['readback_sha256']=sha(cfg['readback_path']);q['additional_operational_overlays'][lib.ID]=dict(lib.record(cfg),status='ACTIVE');lib.validate(cfg,q)
spec=read(R/'control/specs'/(f.canary+'.json'));spec['cohort']=C;res=load('original_forecast',R/'tools/l2_resources.py');forecast=res.forecast(spec,read(R/'control/HISTORICAL_RSS.json'),read(R/'control/RESOURCE_POLICY.json'))
spec['estimated_peak_model_RAM_bytes']=max(spec['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes']);spec['host_cpu']=0
canonical=copy.deepcopy(spec);canonical['host_cpu']=None;put(root/'control/specs'/(C+'.json'),canonical);q['admitted_specs'][C]=sha(root/'control/specs'/(C+'.json'))
db=dict(cohort=C,host_cpu=0,canonical_spec_sha256=sha(root/'control/specs'/(C+'.json')),resolved_spec_sha256=lib.objsha(spec));dbp=root/'control/dispatch_bindings'/(C+'.json');put(dbp,db)
base=copy.deepcopy(f.base);base['own_ram_forecasts'][0].update(cohort=C,RSS_bytes=0,additional_reserved_bytes=spec['estimated_peak_model_RAM_bytes'])
base['total_projected_additional_RAM_bytes']=3*1024**3+spec['estimated_peak_model_RAM_bytes'];base['admission_decision']['additional_reserved_RAM_bytes']=base['total_projected_additional_RAM_bytes']
# Genuine producer functions, synthetic CPU evidence for deterministic negatives.
# Owner integration separately used REAL sample_cpu_evidence against this host.
lib.sample_cpu_evidence=lambda selected_cpu=None,**kw:f.evidence(selected_cpu)
sweep_path=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');sweep=load('actual_atomic_leaf_source',sweep_path)
leaf=types.SimpleNamespace(__file__=str(sweep_path),_original_exclusive=sweep._original_exclusive)
leaf.exclusive=lambda p,v:leaf._original_exclusive(p,v)
iocfg=read(cfg['io_active_path']);helper=load('actual_IO_atomic',iocfg['source_path']);helper.install_private_module(leaf,iocfg['expected_pins'],1.0)
native=types.SimpleNamespace(__file__=str(R/'tools/l2_native.py'),resources=lambda s,fresh_source=False:copy.deepcopy(base),
 engine=lambda:leaf,registered=lambda:({}, {},q,{}),spec_for=lambda c:copy.deepcopy(spec),assert_parent_lease=lambda:dict(pid=1498278,CPU_FIXTURE_ONLY=True))
iofront=load('actual_IO_front',iocfg['frontend_path']);iofront.configure_native(native,dict(iocfg,_padding_optin=False))
lib.install_future_native(native,cfg,padding=False,invocation_cohort=C)
native.resources(spec,True);n=native.engine();out=root/'out';out.mkdir()
(root/'control/qualification_ledger').mkdir(parents=True,exist_ok=True)
intent=dict(cohort=C,output=str(out),uuid='CPU_FIXTURE_NO_MODEL_UUID',dispatch_binding_sha256=sha(dbp))
n.exclusive(root/'control/qualification_ledger'/(C+'.INTENT.json'),intent)
n.exclusive(out/'NATIVE_LAUNCH.json',dict(dispatch_binding_sha256=sha(dbp),scientific_qualification_uuid='CPU_FIXTURE_NO_MODEL_UUID'))
n.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(dispatch_binding_sha256=sha(dbp),host_cpu_affinity_actual=[0]))
extra=load('actual_new_extra_strict',H/'cpu_extra_strict.py');extra.R=root
proof=extra.terminal(C,dict(performance_accepted=True,CPU_ONLY_ORIGINAL_PERFORMANCE_PROOF_STANDIN=True))
checks=[]
def ck(n,b):assert b,n;checks.append(n)
ck('actual A native producer plus real oldIO helper/front and new extra replay passes',proof['additional_cpu_spare_memory_admission_strict']['status']=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE')
ck('explicit new sidecar refuses to claim old CPU or B5 gate PASS',proof['additional_cpu_spare_memory_admission_strict']['old_CPU_full_gate_PASS_claimed']is False and proof['additional_cpu_spare_memory_admission_strict']['old_B5_strict_PASS_claimed']is False)
paths=[root/'control/qualification_ledger'/(C+'.INTENT.json'),out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json']
snap_path=out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json';snap=read(snap_path);docs=[read(p)for p in paths]
def reject(name,mutator):
 before=[p.read_bytes()for p in paths];sb=snap_path.read_bytes();mutator()
 try:extra.terminal(C,dict(performance_accepted=True))
 except Exception:bad=True
 else:bad=False
 for p,b in zip(paths,before):p.write_bytes(b)
 snap_path.write_bytes(sb);ck(name,bad)
def bind_snapshot(snapshot):
 put(snap_path,snapshot)
 for p in paths:
  d=read(p);d['additional_cpu_spare_memory_admission_binding']['snapshot_sha256']=sha(snap_path);put(p,d)
reject('original performance remains mandatory',lambda:None)if False else None
try:extra.terminal(C,dict(performance_accepted=False))
except AssertionError:bad=True
else:bad=False
ck('original performance remains mandatory',bad)
def wrongcpu():
 for p in paths:
  d=read(p);d['additional_cpu_spare_memory_admission_binding']['selected_cpu']=1;put(p,d)
reject('three equal selected fields cannot diverge from actual DB and PID CPU',wrongcpu)
def ownerproof():
 s=copy.deepcopy(snap);s['fresh_preflights'][0]['context']['kind']='OWNER_FRAME';bind_snapshot(s)
reject('OWNER_FRAME proof cannot stand in for NATIVE proof',ownerproof)
def missingcandidate():
 s=copy.deepcopy(snap);p=s['fresh_preflights'][0];raw=p['base_resource_snapshot'];raw['own_ram_forecasts']=[];raw['total_projected_additional_RAM_bytes']=3*1024**3;raw['admission_decision']['additional_reserved_RAM_bytes']=3*1024**3
 p['old95_resource_snapshot']=lib.project(raw);p['growth_unchanged_bytes']=3*1024**3;p['effective_decision']['additional_reserved_RAM_bytes']=3*1024**3;bind_snapshot(s)
reject('missing canonical candidate rejected even after total math recomputation',missingcandidate)
def duplicateold():
 for p in paths:
  d=read(p);d['additional_future_memory_admission_binding']={};put(p,d)
reject('new generation cannot also claim old memory binding',duplicateold)
def wrongsource():
 s=copy.deepcopy(snap);s['source_snapshots']['owner']['utf8']+='\n# CPU_TAMPER';bind_snapshot(s)
reject('source snapshot tamper fails closed',wrongsource)
outrec=dict(status='PASS',count=len(checks),checks=checks,fixture_root=str(root),model_starts=0,new_grants=0,production_changes=0,
 actual_candidate_joint_QA=dict(path=str(joint_path),sha256=sha(joint_path))if joint_path else None,
 native_prefix_qualified=True,extra_strict_qualified=True,native_prefix_scope='Actual new library engine/exclusive binding plus actual sharedIO helper/frontend; no GPU execution',
 library_sha256=sha(lib.__file__),owner_sha256=sha(H/'cpu_owner.py'),extra_sha256=sha(H/'cpu_extra_strict.py'),
 caveat='Real A native binding and old sharedIO producers/verifiers; controlled CPU/RAM/authority/exclusive leaf and original-performance proof stand-in. No original GPU performance or production native lease is claimed.')
put(H/('EXTRA_CANDIDATE_JOINT_QA_INTEGRATION.json'if joint_path else'EXTRA_CPU_QUALIFICATION.json'),outrec);print(json.dumps(outrec))
