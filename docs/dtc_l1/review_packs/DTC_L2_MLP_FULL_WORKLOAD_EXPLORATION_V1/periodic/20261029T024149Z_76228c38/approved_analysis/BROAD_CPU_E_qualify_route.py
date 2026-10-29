"""Reuse closed CPU IR fixture for frame-private routing/restore only; no prefix rerun."""
import pathlib,json,hashlib,importlib.util,copy,types,threading,sys
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No model/process/signal')
sys.addaudithook(audit)
case=next(x for x in read(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json')['cases']if x['kind']=='IR');root=P(case['root']);c=case['cohort'];q=read(root/'CPU_ONLY_REGISTRY.json');cfg=read(root/'CONFIG.json')
bridge=load('actual_broad_consumer_route',D/'consumer_bridge.py');consumer=load('actual_private_original_consumer_route',R/'tools/l2_results.py')
value=read(root/'analysis'/(c+'.RESULT.json'));base={k:v for k,v in value['proof'].items()if k not in ['additional_cpu_shared_timeslice_strict','additional_strace_bpf_observation_strict','additional_shared_json_io_strict','additional_future_memory_io_strict']}
archive={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'}
# Prior qualification intentionally left its private mock transport manifest
# missing one member after the negative check. Restore ONLY that CPU leaf to
# the already accepted fixture's exact hash; no real archive/model is changed.
out=P(read(root/'control/qualification_ledger'/(c+'.INTENT.json'))['output'])
mp=P(archive['receipt']['target_mount_path'])/'SOURCE_MANIFEST.json';manifest=read(mp)
manifest['entries']=[dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size)for p in sorted(out.iterdir())if p.is_file()]
raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
assert hashlib.sha256(raw).hexdigest()==archive['receipt']['manifest_sha256']
put(mp,manifest)
sentinel=object()
def oldsafe(c):return sentinel
def loader(n,file):
 if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,q,None))
 if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:base)
 if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:archive)
 raise AssertionError('Unknown private fixture leaf '+file)
consumer.safe_finish=oldsafe;consumer.load=loader;consumer.archive_closed=lambda c:archive
aging=types.SimpleNamespace(lock=threading.RLock());engine=types.SimpleNamespace(registered=lambda:(None,None,q,None))
frame=types.SimpleNamespace(f_locals={'consumer':consumer,'engine':engine,'res':types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=aging)})
checks=[]
def ok(n,v):assert v,n;checks.append(dict(name=n,status='PASS'))
def reject(fn):
 try:fn()
 except Exception:return True
 return False
refs=(consumer.safe_finish,consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
receipt=bridge.install_on_frame(frame,root/'CONFIG.json',lambda:None,qualification_loader_sha256=sha(__file__))
ok('actual_frame_private_safe_readiness_and_original_four_callbacks_preserved',bridge.consumer_check(frame,cfg)is True and refs[1:]==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)and consumer.safe_finish(c)==value)
rp=root/'analysis'/(c+'.RESULT.json');saved=rp.read_bytes();bad=read(rp);bad['uuid']='WRONG_UUID';put(rp,bad)
ok('restore_refuses_wrong_q_INTENT_RESULT_UUID',reject(lambda:bridge.restore_in_owner(lambda:None)));rp.write_bytes(saved)
dangling=next(x for x in read(cfg['resource_configuration_path'])['allowed_cohorts']if x not in q['consumed']);claim=root/'control/broad_shared_cpu_route_claims'/(dangling+'.json');assert not claim.exists();put(claim,dict(schema='BROAD_SHARED_CPU_FUTURE_ROUTE_CLAIM_V1',overlay_id=bridge.ID,cohort=dangling))
ok('admitted_unused_dangling_routeclaim_preserves_mandatory_consumer',reject(lambda:bridge.restore_in_owner(lambda:None)));claim.unlink()
bridge.restore_in_owner(lambda:None)
ok('accepted_same_generation_restore_exact_original_safe_and_callbacks',refs==(consumer.safe_finish,consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed))
report=dict(schema='E_BROAD_SHARED_PRIVATE_FRAME_ROUTE_CPU_QUALIFICATION_V1',status='PASS',count=len(checks),checks=checks,reused_closed_fixture=str(root),reused_prefix_QA_sha256=sha(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json'),consumer_sha256=sha(D/'consumer_bridge.py'),observation_sha256=sha(D/'bpf_extra_strict.py'),driver_sha256=sha(__file__),models_started=0,new_grants=0,production_changes=0,actual_Main_installed=False,limitations=['Private frame and loader are explicit qualification stand-ins; original safe_finish attribute routing/install/readiness/restore APIs execute.','Reuses prior new-prefix closed fixture and full strict snapshot evidence without rerunning that prefix; original physics/archive transport are still stand-ins.'])
assert not(D/'CPU_ROUTE_QUALIFICATION.json').exists();put(D/'CPU_ROUTE_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',count=len(checks))))
