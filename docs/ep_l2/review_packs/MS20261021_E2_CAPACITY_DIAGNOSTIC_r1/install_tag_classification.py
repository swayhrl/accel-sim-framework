"""Adopt reviewed native Tag observation decoding only at the original idle boundary."""
from pathlib import Path
import ast,contextlib,copy,importlib.util,io,json,sys,time
R=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');P=R/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1';D=P/'terminal_preparation/tag_replacement_delta';U=R/'util/ep_l2/mechanism_e';sys.path.insert(0,str(U));import coordinator as c
c.tooling_binding();target=U/'capacity_validation.py';candidate=D/'candidate/capacity_validation.py';clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';previous=json.loads(clientpath.read_text())
sp=importlib.util.spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(sp);sp.loader.exec_module(pub)
with c.Coordinator().registry.locked() as data:
 s=data[c.FIELD];assert s['actual_starts']==36 and s['controller']['state']=='STOPPED'
 assert not any(v['status'] in c.ACTIVE and v.get('experiment_id')==c.CAMPAIGN for g in ['runs','resource_leases'] for v in data[g].values()),'Original owned work active: no source replacement'
 assert c.digest(target)=='0d69b0d2e1434003133c168b8c1bfb66a59f9cc9a00317187708751cd08caac7'
 assert c.digest(candidate)=='5d4bb90db414042f5c6a6efdbde36e193564791a778a69ede9e24c0403c1c58d'
 names=[n.name for n in ast.parse(candidate.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))];assert len(names)==len(set(names))
 c.write_json(P/'CLIENT_BEFORE_TAG_CLASSIFICATION.json',previous);target.write_bytes(candidate.read_bytes())
 c.write_json(P/'TAG_CLASSIFICATION_OWNER_REVIEW.json',dict(status='REVIEWED_APPLIED_NO_NATIVE_OR_APPLICATION_QUALIFICATION',at_unix=time.time(),purpose='Successful native Tag replacement is a valid large-finite observation; missing complete replacement coverage remains UNKNOWN. No mechanism/binary/MAIN identity change.',original_source_pin=previous['source_publication_commit'],source_sha256=c.digest(target),old_attempts=36,full_application_starts=0))
 paths=[target,P/'install_tag_classification.py',P/'CLIENT_BEFORE_TAG_CLASSIFICATION.json',P/'TAG_CLASSIFICATION_OWNER_REVIEW.json']+[p for root in [D,P/'terminal_preparation/parser_draft'] for p in root.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.patch']]
 with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('ep-l2 E2: retain successful Tag replacement as finite diagnostic evidence',paths)
 client=copy.deepcopy(previous);client.setdefault('source_binding_history',[]).append(dict(at_unix=time.time(),source_publication_commit=previous['source_publication_commit'],source_files=previous['source_files'],resource_lease_api_sha256=previous['resource_lease_api_sha256'],reason='Exact new native Tag replacement observations; negative diagnostic acceptance retained'))
 client['source_publication_commit']=rb['remote_commit'];client['source_files']={p.relative_to(R).as_posix():c.digest(p) for p in U.glob('*.py') if not p.name.startswith('test_')};client['resource_lease_api_sha256']=c.digest(U/'coordinator.py');c.write_json(clientpath,client);c.write_json(P/'CLIENT_TAG_CLASSIFICATION_BOUND.json',client);c.write_json(P/'TAG_CLASSIFICATION_REMOTE_READBACK.json',rb)
print(json.dumps(dict(source_publication=rb['remote_commit'],verified_source=c.verify_extension_binding(clientpath),actual_starts=36,native_tests_started=0,full_application_starts=0)),flush=True)
