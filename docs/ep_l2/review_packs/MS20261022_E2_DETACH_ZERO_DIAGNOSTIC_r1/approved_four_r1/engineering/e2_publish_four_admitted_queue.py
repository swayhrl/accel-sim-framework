from pathlib import Path
import json,sys,time,shutil,fcntl,subprocess,importlib.util,contextlib,io
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';S=Path('/workspace/ep_l2_ft20261016_shared');H=S/'mechanism_study_20261019_v1';sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'));from coordinator import Coordinator,digest,write_json
with (H/'CONTROLLER.lock').open('a+') as cl,(S/'REGISTRY.lock').open('a+') as rl:
 fcntl.flock(cl,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(rl,fcntl.LOCK_EX);i=Coordinator().snapshot();assert i['actual_starts']==51 and i['controller']['state']=='STOPPED' and not i['positive_ro_successor_batch']['attempt_ids']
 old=A/'engineering/pre_execution_projection';old.mkdir(exist_ok=True)
 for name,p in [('READY_QUEUE.json',H/'inbox/READY_QUEUE.json'),('CONTROLLER_STEP.json',H/'CONTROLLER_STEP.json')]:
  if p.exists() and not (old/name).exists():shutil.copyfile(p,old/name)
 (H/'inbox/READY_QUEUE.json').write_bytes((A/'QUEUE.json').read_bytes());assert digest(H/'inbox/READY_QUEUE.json')==digest(A/'QUEUE.json')
for n in ['STATUS.json','RECEIPT.json']:
 p=P/n;d=json.loads(p.read_bytes());d['state']='PRIMARY_FOUR_QUALIFIED_REGISTERED_BOUND_READY_ORIGINAL_CONTROLLER';d['status']='PRIMARY_FOUR_QUALIFIED_REGISTERED_BOUND_READY_ORIGINAL_CONTROLLER';d['approved_successor_scope']['state']='FOUR_NEW_Q_REGISTERED_BOUND_CFD_RESOURCE_FORECAST_PASS';d['approved_successor_scope']['queued']=True;d['actual_starts']=51;d['controller']='STOPPED';d['actual_api_adoption_receipt']='approved_four_r1/ACTUAL_API_ADOPTION_RECEIPT.json';d['source_client_activation_receipt']='approved_four_r1/engineering/ACTUAL_CLIENT_ACTIVATION_RECEIPT.json';d['full_goal_complete']=False;p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
for src in ['/tmp/e2_activate_four_successor_client.py','/tmp/e2_adopt_four_and_prepare_queue.py','/tmp/e2_publish_four_admitted_queue.py']:shutil.copyfile(src,A/'engineering'/Path(src).name)
paths=[A/'QUEUE.json',A/'ACTUAL_API_ADOPTION_RECEIPT.json',P/'STATUS.json',P/'RECEIPT.json']+[p for p in (A/'engineering').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
s=importlib.util.spec_from_file_location('pub',E/'docs/ep_l2/review_packs/MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(s);s.loader.exec_module(pub)
with open('/workspace/ep_l2_ms20261019_shared/E2_GIT_PUBLICATION.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not subprocess.check_output(['git','diff','--cached','--name-only']).strip()
 with contextlib.redirect_stdout(io.StringIO()):r=pub.publish('ep-l2 E2: activate original client and register exact four qualified diagnostics for CFD-first dispatch',paths)
Path('/tmp/e2_four_actual_adoption_readback.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'remote_commit':r['remote_commit'],'exact_blobs':len(r['verified_paths']),'central_queue_sha256':digest(H/'inbox/READY_QUEUE.json'),'actual_starts':51}))
