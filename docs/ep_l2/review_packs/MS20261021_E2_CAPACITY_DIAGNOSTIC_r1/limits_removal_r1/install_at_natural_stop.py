"""OWNER DRAFT: install sealed limits-removal sources at original natural STOPPED.

Never launches applications/native tests/controllers or terminates a process.
Run only after root review; activation is a separate fresh Python invocation.
"""
from pathlib import Path
import argparse,ast,contextlib,copy,importlib.util,io,json,sys,time
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PACK=ROOT/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1'
P=PACK/'limits_removal_r1';U=ROOT/'util/ep_l2/mechanism_e'
sys.path.insert(0,str(U));import coordinator as c
read=lambda p:json.loads(Path(p).read_text())
ref=lambda p:dict(path=str(Path(p).resolve()),sha256=c.digest(p))

def safe_boundary(data):
 item=data[c.FIELD]
 c.require(item['controller']['state']=='STOPPED' and item['uncertain_start_intents']==0,'original controller/uncertain intents not at safe stop')
 process=item['controller'].get('process')
 if process:
  try:alive=c.process_identity(process['pid'])==process
  except (FileNotFoundError,ProcessLookupError):alive=False
  c.require(not alive,'original supervisor/controller process still exists')
 c.require(not any(r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),'E active app/test/build lease prevents source switch')
 c.require(item['actual_starts']==sum(a.get('actual_start') is True for a in item['attempts']),'charged history inconsistent')
 return item

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply-after-original-controller-natural-stop',action='store_true',required=True);ap.parse_args()
 c.tooling_binding();manifest=read(P/'OWNER_INSTALL_CANDIDATE_MANIFEST.json')
 c.require(c.digest(P/'USER_APPROVAL.json')==manifest['approval']['sha256'],'approval changed')
 for name,row in manifest['input_manifests'].items():c.require(c.digest(row['path'])==row['sha256'],'input manifest changed: '+name)
 sp=importlib.util.spec_from_file_location('publisher',PACK.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(sp);sp.loader.exec_module(pub)
 cp=c.HANDOFF/'CLIENT_CONTRACT.json';previous=read(cp)
 with c.Coordinator().registry.locked() as data:
  item=safe_boundary(data)
  for name,row in manifest['files'].items():
   target=ROOT/name;candidate=Path(row['candidate_path'])
   c.require((not target.exists()) if row['current_util_base_sha256'] is None else c.digest(target)==row['current_util_base_sha256'],'base source changed: '+name)
   c.require(c.digest(candidate)==row['candidate_sha256'],'sealed candidate changed: '+name)
   tree=ast.parse(candidate.read_text());names=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
   c.require(len(names)==len(set(names)),'duplicate declarations: '+name)
  c.write_json(P/'CLIENT_BEFORE_SOURCE_SWITCH.json',previous)
  for name,row in manifest['files'].items():(ROOT/name).write_bytes(Path(row['candidate_path']).read_bytes())
  receipt=dict(status='SOURCE_APPLIED_AT_NATURAL_STOP_PENDING_REMOTE_AND_CLIENT',at_unix=time.time(),actual_starts=item['actual_starts'],controller=item['controller'],files=manifest['files'],approval=manifest['approval'],application_starts=0,old_spec_identity_native_and_results_unchanged=True)
  c.write_json(P/'OWNER_SOURCE_INSTALL_RECEIPT.json',receipt)
  paths=[ROOT/name for name in manifest['files']]+[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
  with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('ep-l2 E2: install approved start and time limit removal at natural stop',paths)
  client=copy.deepcopy(previous);client.setdefault('source_binding_history',[]).append(dict(at_unix=time.time(),source_publication_commit=previous['source_publication_commit'],source_files=previous['source_files'],resource_lease_api_sha256=previous['resource_lease_api_sha256'],reason='Exact approved start/intake/per-app/count removal; scientific ten-condition scope and physical/output guards retained'))
  client['source_publication_commit']=rb['remote_commit'];client['source_files']={p.relative_to(ROOT).as_posix():c.digest(p) for p in U.glob('*.py') if not p.name.startswith('test_')};client['resource_lease_api_sha256']=c.digest(U/'coordinator.py')
  c.write_json(cp,client);c.write_json(P/'CLIENT_SOURCE_SWITCH_BOUND.json',client);c.write_json(P/'SOURCE_REMOTE_READBACK.json',rb)
 print(json.dumps(dict(status='SOURCE_REMOTE_AND_CLIENT_BOUND_ADOPTION_NOT_YET_RUN',remote_commit=rb['remote_commit'],next='Fresh process: prepare_pending_conv_on.py --adopt-and-prepare-only',new_application_starts=0)),flush=True)

if __name__=='__main__':main()
