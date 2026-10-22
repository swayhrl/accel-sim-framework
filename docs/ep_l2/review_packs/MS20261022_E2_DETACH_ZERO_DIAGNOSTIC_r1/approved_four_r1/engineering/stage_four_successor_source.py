from pathlib import Path
import json,hashlib,fcntl,time,os,shutil,subprocess
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';C=Path('/tmp/e2_positive_ro_successor_candidate');S=Path('/workspace/ep_l2_ft20261016_shared');F='mechanism_study_20261019_v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'path':str(p),'sha256':sha(p)}
names=['detach_successor.py','detach_diagnostic_policy.py','coordinator.py','controller.py'];log=Path('/tmp/e2_four_root_control_output.txt').read_text();assert 'Ran 27 tests' in log and log.rstrip().endswith('OK')
review=json.loads(Path('/tmp/e2_four_successor_independent_review.json').read_bytes());assert review['status'].startswith('PASS') and not review.get('unresolved_design_blockers',[]) 
manifest=ref(A/'FINAL_MANIFEST.json');out=A/'engineering';out.mkdir(exist_ok=True)
for p,name in [(Path('/tmp/e2_four_root_control_output.txt'),'ROOT_CONTROL_OUTPUT.txt'),(Path('/tmp/e2_four_successor_independent_review.json'),'INDEPENDENT_CENTRAL_REVIEW.json'),(C/'REAL_METADATA_DRY_CONTROL.json','REAL_METADATA_DRY_CONTROL.json'),(C/'test_successor.py','test_successor.py'),(C/'test_real_metadata_dry.py','test_real_metadata_dry.py')]:shutil.copyfile(p,out/name)
with (S/F/'CONTROLLER.lock').open('a+') as cl,(S/'REGISTRY.lock').open('a+') as rl:
 fcntl.flock(cl,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(rl,fcntl.LOCK_EX)
 registry=(S/'RUN_REGISTRY.json').read_bytes();data=json.loads(registry);item=data[F];assert len(item['attempts'])==item['actual_starts']==51 and item['controller']['state']=='STOPPED';assert item['t0_unix']==1792414193
 active=[r for group in ('runs','resource_leases') for r in data[group].values() if r.get('experiment_id')=='EPL2_MECHANISM_STUDY_20261019_V1' and r.get('status') in ('RESERVED','RUNNING','START_INTENT_UNRECONCILED')];assert not active,active
 processes=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:args=(p/'cmdline').read_bytes()[:16384].decode(errors='replace').replace('\0',' ')
  except (OSError,ProcessLookupError):continue
  if any(str(E/'util/ep_l2/mechanism_e'/n) in args for n in ['controller.py','runner.py','coordinator.py','parse_detach_terminal.py']):processes.append({'pid':int(p.name),'cmdline':args})
 assert not processes,processes
 old=out/'pre_source_switch';old.mkdir(exist_ok=True);clientpath=S/F/'CLIENT_CONTRACT.json';assert not (old/'CLIENT_CONTRACT.json').exists(),'neveroverwrite previousactivation backup';shutil.copyfile(clientpath,old/'CLIENT_CONTRACT.json');sources=[]
 for name in names:
  dest=E/'util/ep_l2/mechanism_e'/name;before=sha(dest) if dest.exists() else None
  if dest.exists():shutil.copyfile(dest,old/name)
  content=(C/name).read_text()
  if name=='detach_successor.py':assert 'FINAL_SUCCESSOR_REF=None' in content;content=content.replace('FINAL_SUCCESSOR_REF=None','FINAL_SUCCESSOR_REF='+repr(manifest),1)
  dest.write_text(content);sources.append({'path':str(dest),'old_sha256':before,'candidate_sha256':sha(C/name),'deployed_sha256':sha(dest)})
 assert (S/'RUN_REGISTRY.json').read_bytes()==registry
 receipt={'schema':'E2_APPROVED_FOUR_SOURCE_STAGE_AT_ORIGINAL_QUIESCENCE_V1','status':'SOURCE_STAGED_CLIENT_NOT_YET_ACTIVATED','at_unix':time.time(),'actual_starts':51,'controller':item['controller'],'controller_lock':'Original CONTROLLER.lock EX_NB acquired','registry_lock':'Original REGISTRY.lock EX acquired','active_campaign_rows':active,'source_dependent_processes':processes,'old_client_sha256':sha(old/'CLIENT_CONTRACT.json'),'registry_sha256':hashlib.sha256(registry).hexdigest(),'registry_mutated':False,'source':sources,'manifest_ref':manifest,'normal_fixed_production_main_changed':False,'new_applications':0,'root_control_count':27}
 (out/'SOURCE_STAGE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'source_files':len(sources),'actual_starts':51}))
