"""Focused actual mixed-four prerequisite API qualification, no raw replay/model."""
import pathlib,json,copy,hashlib,importlib.util,tempfile,sys
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No process/signal')
sys.addaudithook(audit)
extra=load('broad_release_actual',D/'bpf_extra_strict.py');engine=load('broad_release_authority_ro',R/'tools/l2_native.py');q=engine.registered()[2]
q=copy.deepcopy(q);q['qualification_only']=True
appath=A/'coordinator/BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1/APPROVAL.json';assert sha(appath)=='5c5124f795bb46e0883d1aa8b2ab12144c162bb179fe9d453a18b7022062d682';app=read(appath)
lp=A/'agents/A/broad_shared_cpu_v1/cpu_shared.py';assert sha(lp)=='c761f23333a0cb1d95a4926cc671b13f827dfecc10a434d0a3249c97cbba5d41'
root=P(tempfile.mkdtemp(prefix='CPU_BROAD_REAL_GATE_',dir=D))
rcfg=dict(source_paths={'library':str(lp)},qualified_sources={'library':sha(lp)},expected_pins={app['actual_gate']['source_path']:app['actual_gate']['source_sha256']},allowed_cohorts=app['allowed_cohorts'],scope_contract_path=app['scope_contract']['path'],scope_contract_sha256=app['scope_contract']['sha256'],broad_approval_path=str(appath),broad_approval_sha256=sha(appath),qualification_only=True)
rp=root/'RESOURCE_REFERENCE_ONLY_NOT_DEPLOYABLE.json';put(rp,rcfg)
cfg=dict(root=str(root),qualification_only=True,resource_configuration_path=str(rp),resource_configuration_sha256=sha(rp),memory_configuration_path=str(rp),canary4_prerequisite_path=app['actual_gate']['path'],canary4_prerequisite_sha256=app['actual_gate']['sha256'])
checks=[]
def ok(n,v):assert v,n;checks.append(dict(name=n,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return True
 return False
value=extra.verify_release_prerequisite(cfg,q)
ok('actual_Main_gate_plus_actual_scope_approval_api_passes_without_CPU_release',value['status']=='PASS_ACTUAL_MAIN_MIXED_FOUR_AND_EXPLICIT_BROAD_SCOPE'and value['production_release_eligible']is False)
bad=copy.deepcopy(cfg);bad['canary4_prerequisite_sha256']='0'*64
ok('fake_bool_or_different_gate_SHA_cannot_substitute',reject(lambda:extra.verify_release_prerequisite(bad,q)))
badq=copy.deepcopy(q);c=read(app['actual_gate']['path'])['rows'][0]['cohort'];badq['consumed'][c]['uuid']='DIFFERENT_UUID'
ok('four_current_consumed_UUIDs_mandatory',reject(lambda:extra.verify_release_prerequisite(cfg,badq)))
lib=load('actual_broad_release_lib',lp);evidence=lib.validate_broad_approval(rcfg,q)
snapshot=dict(config=rcfg,broad_approval_utf8=evidence['certificate_utf8'],broad_gate_utf8=evidence['gate_utf8'],broad_source_artifacts_utf8=evidence['source_artifacts_utf8'],scope_contract_utf8=evidence['scope_contract_utf8'])
ok('historical_captured_resource_and_artifact_UTF8_replay_same_evidence',extra.verify_release_prerequisite(cfg,q,rp.read_text(),snapshot)==value)
bad=copy.deepcopy(snapshot);key=next(iter(bad['broad_source_artifacts_utf8']));bad['broad_source_artifacts_utf8'][key]+=' '
ok('tampered_historical_source_artifact_cannot_release',reject(lambda:extra.verify_release_prerequisite(cfg,q,rp.read_text(),bad)))
report=dict(schema='BROAD_SHARED_REAL_GATE_API_CPU_QUALIFICATION_V1',status='PASS',checks=checks,count=len(checks),actual_gate_sha256=extra.ACTUAL_FOUR_GATE_SHA,actual_broad_approval_sha256=sha(appath),resource_library_sha256=sha(lp),observation_extra_sha256=sha(D/'bpf_extra_strict.py'),driver_sha256=sha(__file__),qualification_only=True,production_configuration_qualified=False,models_started=0,new_grants=0,production_changes=0,scope='Actual Main gate and artifacts/auth records read with private reference-only resource config; not a complete resource/owner configuration')
assert not(D/'CPU_RELEASE_QUALIFICATION.json').exists();put(D/'CPU_RELEASE_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),extra_sha256=report['observation_extra_sha256'])))
