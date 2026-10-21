"""Install reviewed count-cap removal only after the old controller fully exits.

No application, native, compiler, process termination or new controller is run.
Original registry lock, publication/readback and CLIENT source binding remain.
"""
from pathlib import Path
import argparse,ast,contextlib,copy,importlib.util,io,json,sys,time
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PACK=ROOT/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1'
P=PACK/'concurrency_amendment';U=ROOT/'util/ep_l2/mechanism_e'
sys.path.insert(0,str(U));import coordinator as c
read=lambda p:json.loads(Path(p).read_text())
ref=lambda p:dict(path=str(Path(p).resolve()),sha256=c.digest(p))

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--apply-after-original-controller-natural-stop',action='store_true',required=True)
 ap.parse_args();c.tooling_binding()
 manifest=read(P/'CANDIDATE_MANIFEST.json');controller=read(P/'CONTROLLER_CANDIDATE_MANIFEST.json')
 files=copy.deepcopy(manifest['files'])
 files['util/ep_l2/mechanism_e/controller.py']=dict(candidate=str((P/controller['candidate_source']['path']).relative_to(ROOT)),
  old_sha256=controller['base_source']['sha256'],sha256=controller['candidate_source']['sha256'])
 for filename,review in [('run.py','RUN_FEEDER_CHANGE_REVIEW.json'),('input_preparation/materialize.py','MATERIALIZER_REVISION_REVIEW.json')]:
  r=read(P/review);candidate=P/'candidate'/Path(filename).name
  files[str((PACK/filename).relative_to(ROOT))]=dict(candidate=str(candidate.relative_to(ROOT)),old_sha256=r['base_sha256'] if 'base_sha256' in r else r['base_run_sha256'],sha256=r['candidate_sha256'])
 publisher=importlib.util.spec_from_file_location('publisher',PACK.parent/'MS20261020_E2_TAKEOVER_r1/publish.py')
 pub=importlib.util.module_from_spec(publisher);publisher.loader.exec_module(pub)
 cp=c.HANDOFF/'CLIENT_CONTRACT.json';previous=read(cp)
 with c.Coordinator().registry.locked() as data:
  item=data[c.FIELD]
  c.require(item['controller']['state']=='STOPPED','old controller still active; no source replacement')
  prior=item['controller'].get('process')
  if prior:
   try:alive=c.process_identity(prior['pid'])==prior
   except (FileNotFoundError,ProcessLookupError):alive=False
   c.require(not alive,'old controller callbacks/process not fully exited')
  c.require(not any(r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),'owned active process/lease prevents source replacement')
  c.require(38<=item['actual_starts']<=46 and item['uncertain_start_intents']==0,'charged/uncertain history changed')
  amendment=item['formal_simulator_concurrency']
  c.require(amendment['mode']=='RESOURCE_ONLY' and amendment['approval']['sha256']==manifest['approval_sha256']==c.digest(P/'USER_APPROVAL.json'),'exact count-only approval missing')
  for name,row in files.items():
   target=ROOT/name;candidate=ROOT/row['candidate']
   c.require((not target.exists()) if row['old_sha256'] is None else c.digest(target)==row['old_sha256'],'source base changed: '+name)
   c.require(c.digest(candidate)==row['sha256'],'reviewed candidate changed: '+name)
   tree=ast.parse(candidate.read_text());names=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
   c.require(len(names)==len(set(names)),'duplicate top-level declaration: '+name)
  c.write_json(P/'CLIENT_BEFORE_RESOURCE_ONLY.json',previous)
  for name,row in files.items():(ROOT/name).write_bytes((ROOT/row['candidate']).read_bytes())
  c.write_json(P/'OWNER_INSTALL_RECEIPT.json',dict(status='SOURCE_APPLIED_AT_NATURAL_STOP_PENDING_CLIENT_REBIND',at_unix=time.time(),actual_starts=item['actual_starts'],controller=item['controller'],files=files,approval=ref(P/'USER_APPROVAL.json'),old_attempts_and_native_processes_unchanged=True,new_application_starts=0,other_project_policy_records_unchanged=True))
  paths=[ROOT/name for name in files]+[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
  with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('ep-l2 E2: remove fixed simulator counts after original controller naturally stops',paths)
  client=copy.deepcopy(previous);client.setdefault('source_binding_history',[]).append(dict(at_unix=time.time(),source_publication_commit=previous['source_publication_commit'],source_files=previous['source_files'],resource_lease_api_sha256=previous['resource_lease_api_sha256'],reason='Explicit user removed fixed E formal simulator-count caps; physical resource/scientific/history guards unchanged'))
  client['source_publication_commit']=rb['remote_commit'];client['source_files']={p.relative_to(ROOT).as_posix():c.digest(p) for p in U.glob('*.py') if not p.name.startswith('test_')};client['resource_lease_api_sha256']=c.digest(U/'coordinator.py')
  c.write_json(cp,client);c.write_json(P/'CLIENT_RESOURCE_ONLY_BOUND.json',client);c.write_json(P/'SOURCE_REMOTE_READBACK.json',rb)
 print(json.dumps(dict(status='SOURCE_AND_CLIENT_BOUND_ACTIVATION_PENDING',remote_commit=rb['remote_commit'],source_binding=c.verify_extension_binding(cp),new_application_starts=0)),flush=True)

if __name__=='__main__':main()
