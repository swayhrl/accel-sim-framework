from pathlib import Path
import ast,contextlib,copy,hashlib,importlib.util,io,json,sys,time
R=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');P=R/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1';D=P/'terminal_preparation';U=R/'util/ep_l2/mechanism_e';sys.path.insert(0,str(U));import coordinator as c
c.tooling_binding();manifest=json.loads((D/'CANDIDATE_MANIFEST.json').read_text());clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';previous=json.loads(clientpath.read_text())
sp=importlib.util.spec_from_file_location('publisher',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(sp);sp.loader.exec_module(pub)
with c.Coordinator().registry.locked() as data:
 s=data[c.FIELD];assert s['actual_starts']==36 and s['controller']['state']=='STOPPED'
 assert not any(v['status'] in c.ACTIVE and v.get('experiment_id')==c.CAMPAIGN for g in ['runs','resource_leases'] for v in data[g].values()),'Owned active work; leave source unchanged until safe boundary'
 for name,row in manifest['candidate_files'].items():
  source=D/row['candidate_path'];assert c.digest(source)==row['sha256'];target=R/name
  if row['action']=='ADD':assert not target.exists()
  else:assert c.digest(target)==manifest['base']['base_files'][target.name]
  tree=ast.parse(source.read_text());names=[x.name for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))];assert len(names)==len(set(names)),name
 c.write_json(P/'CLIENT_BEFORE_TERMINAL_ROUTE.json',previous)
 actual={}
 for name,row in manifest['candidate_files'].items():
  content=(D/row['candidate_path']).read_text()
  if name.endswith('controller.py'):
   seen=False;lines=[]
   for line in content.splitlines(keepends=True):
    if line.strip()=='import capacity_policy':
     if seen:continue
     seen=True
    lines.append(line)
   content=''.join(lines)
  (R/name).write_text(content);actual[name]=c.digest(R/name)
 c.write_json(P/'TERMINAL_ROUTE_OWNER_REVIEW.json',dict(status='REVIEWED_AND_APPLIED_NO_QUALIFICATION_OR_APPLICATION',at_unix=time.time(),candidate_manifest_sha256=c.digest(D/'CANDIDATE_MANIFEST.json'),actual_applied_source_files=actual,owner_cleanup='Remove duplicate harmless capacity_policy import in candidate controller; no behavior change',new_native_or_application_starts=0,new_native_qualification=False,legacy_validator_and_requested_dump_unchanged=True))
 paths=[R/n for n in manifest['candidate_files']]+[p for p in D.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.patch']]+[P/'CLIENT_BEFORE_TERMINAL_ROUTE.json',P/'TERMINAL_ROUTE_OWNER_REVIEW.json']
 with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('ep-l2 E2: bind independent capacity summary validation and stop failed diagnostic admissions',paths)
 client=copy.deepcopy(previous);client.setdefault('source_binding_history',[]).append(dict(at_unix=time.time(),source_publication_commit=previous['source_publication_commit'],source_files=previous['source_files'],resource_lease_api_sha256=previous['resource_lease_api_sha256'],reason='New explicit capacity terminal validator route; legacy geometry/validation retained'))
 client['source_publication_commit']=rb['remote_commit'];client['resource_lease_api_sha256']=c.digest(U/'coordinator.py');client['source_files']={p.relative_to(R).as_posix():c.digest(p) for p in U.glob('*.py') if not p.name.startswith('test_')};client['capacity_terminal_adapter_status']='SCOPED_VALIDATION_ROUTE_READY_ACTUAL_A2_NATIVE_DECODER_AND_QUALIFICATION_PENDING'
 c.write_json(clientpath,client);c.write_json(P/'CLIENT_TERMINAL_ROUTE_BOUND.json',client);c.write_json(P/'TERMINAL_ROUTE_REMOTE_READBACK.json',rb)
print('TERMINAL_ROUTE_SOURCE_CLIENT_BOUND',rb['remote_commit'],c.verify_extension_binding(clientpath),flush=True)
