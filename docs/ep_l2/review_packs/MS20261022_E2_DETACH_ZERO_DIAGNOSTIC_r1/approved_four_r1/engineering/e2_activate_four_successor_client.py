from pathlib import Path
import json,hashlib,fcntl,time,subprocess,sys,os,tempfile,copy
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';S=Path('/workspace/ep_l2_ft20261016_shared');F='mechanism_study_20261019_v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes());stage=read(A/'engineering/SOURCE_STAGE_RECEIPT.json');pub=read(A/'engineering/SOURCE_PUBLICATION_REMOTE_READBACK.json');h=pub['remote_commit'];clientpath=S/F/'CLIENT_CONTRACT.json'
with (S/F/'CONTROLLER.lock').open('a+') as cl,(S/'REGISTRY.lock').open('a+') as rl:
 fcntl.flock(cl,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(rl,fcntl.LOCK_EX)
 raw=(S/'RUN_REGISTRY.json').read_bytes();data=json.loads(raw);i=data[F];assert i['controller']['state']=='STOPPED' and len(i['attempts'])==i['actual_starts']==51;assert sha(clientpath)==stage['old_client_sha256']
 assert not [r for g in ('runs','resource_leases') for r in data[g].values() if r.get('experiment_id')=='EPL2_MECHANISM_STUDY_20261019_V1' and r.get('status') in ('RESERVED','RUNNING')]
 old=read(clientpath);new=copy.deepcopy(old);files={}
 for p in sorted((E/'util/ep_l2/mechanism_e').glob('*.py')):
  if p.name.startswith('test_'):continue
  name=str(p.relative_to(E));blob=subprocess.check_output(['git','show',h+':'+name]);assert blob==p.read_bytes(),name;files[name]=sha(p)
 new.setdefault('source_activation_history',[]).append({'at_unix':time.time(),'source_publication_commit':old['source_publication_commit'],'source_files':old['source_files'],'resource_lease_api_sha256':old['resource_lease_api_sha256'],'reason':'Exact user approved4 Fdiagnostic successor; original51/source/protocol/resources retained'})
 new.update(source_publication_commit=h,source_files=files,resource_lease_api_sha256=sha(E/'util/ep_l2/mechanism_e/coordinator.py'),source_remote_readback_path=str(A/'engineering/SOURCE_PUBLICATION_REMOTE_READBACK.json'),source_remote_readback_sha256=sha(A/'engineering/SOURCE_PUBLICATION_REMOTE_READBACK.json'),positive_ro_successor_manifest={'path':str(A/'FINAL_MANIFEST.json'),'sha256':sha(A/'FINAL_MANIFEST.json')},positive_ro_successor_user_approval={'path':str(A/'USER_APPROVAL.json'),'sha256':sha(A/'USER_APPROVAL.json')})
 b=(json.dumps(new,sort_keys=True,indent=2)+'\n').encode();fd,tmp=tempfile.mkstemp(prefix='.four-client-',dir=clientpath.parent)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(tmp,clientpath);directory=os.open(clientpath.parent,os.O_RDONLY);os.fsync(directory);os.close(directory)
 (A/'engineering/ACTIVE_CLIENT_CONTRACT.json').write_bytes(b);assert (S/'RUN_REGISTRY.json').read_bytes()==raw
sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'));from coordinator import Coordinator,tooling_binding
binding=tooling_binding();i=Coordinator().snapshot();assert i['actual_starts']==51 and i['controller']['state']=='STOPPED'
r={'schema':'E2_APPROVED_FOUR_ACTUAL_SOURCE_CLIENT_ACTIVATION_V1','at_unix':time.time(),'status':'PUBLISHED_SOURCE_CLIENT_ACTIVE_ORIGINAL_REGISTRY_UNCHANGED','source_publication_commit':h,'source_file_count':len(files),'actual_client_sha256':sha(clientpath),'old_client_sha256':stage['old_client_sha256'],'actual_starts':51,'controller':i['controller'],'original_registry_mutated':False,'new_qualifications_registered':0,'new_actual_starts':0,'original_tooling_binding':'PASS'};(A/'engineering/ACTUAL_CLIENT_ACTIVATION_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
