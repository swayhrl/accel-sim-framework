from pathlib import Path
import json,types,tempfile,copy,hashlib,tarfile,io,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');X=A/'agents/R_clean_successor_cpu_preparation_v1';R=Path('/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24');p=R/'tools/oracle_clean_peer_disk_adapter.py';m=types.ModuleType('CLEAN_PEER_CPU_FIXTURES');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);q0=json.loads((R/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json').read_bytes());pl0=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());REQ=pl0['request'];base=R/'engineering_cpu/peer_source_fixtures';base.mkdir(exist_ok=True);enc=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();tests=[]
def fixture(name,mutator=None,accepted=False):
 root=Path(tempfile.mkdtemp(prefix=name+'_',dir=base));(root/'control/qualification_ledger').mkdir(parents=True);(root/'DTC/run/results').mkdir(parents=True);q=copy.deepcopy(q0);pl=copy.deepcopy(pl0);q['execution_plan_sha256']=hashlib.sha256(enc(pl)).hexdigest();mf={'schema':'DTC_CLEAN_SUCCESSOR_CPU_ARTIFACTS_MANIFEST_V1','request':REQ,'registered':False,'models_started':0,'scientific_UUIDs_allocated':0,'plan_sha256':q['execution_plan_sha256'],'resource_candidate_sha256':hashlib.sha256(enc(q)).hexdigest()}
 for n,v in [('EXECUTION_PLAN.json',pl),('RESOURCE_REQUEST_CANDIDATE.CPU.json',q),('CLEAN_CPU_ARTIFACTS_MANIFEST.json',mf)]: (root/'control'/n).write_bytes(enc(v))
 if mutator:mutator(root)
 try:
  v,proof=m._clean_cpu_resource_candidate(root,REQ);observed=True;detail=proof['kind']
 except BaseException as error:observed=False;detail=repr(error)
 tests.append({'test':name,'expected_PASS':accepted,'observed_PASS':observed,'test_PASS':accepted==observed,'detail':detail});assert accepted==observed,name

def edit(root,name,key,value):
 p=root/'control'/name;v=json.loads(p.read_bytes());v[key]=value;p.write_bytes(enc(v))
fixture('explicit_CPU_resource_only',accepted=True)
fixture('manifest_candidate_sha_drift',lambda r:edit(r,'CLEAN_CPU_ARTIFACTS_MANIFEST.json','resource_candidate_sha256','0'*64))
fixture('phase_science_without_auth',lambda r:edit(r,'EXECUTION_PLAN.json','preparation_phase','SCIENCE_FINAL_FROZEN'))
fixture('CPU_ready_true_not_authority',lambda r:edit(r,'RESOURCE_REQUEST_CANDIDATE.CPU.json','ready_for_registration',True))
fixture('spent_CPU_identity_reject',lambda r:edit(r,'RESOURCE_REQUEST_CANDIDATE.CPU.json','consumed',{'CPU_ONLY':'NOT_A_UUID'}))
fixture('CPU_candidate_renamed_normal_reject',lambda r:(r/'control/REGISTRY_REQUEST_CANDIDATE.json').write_bytes((r/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json').read_bytes()))
fixture('normal_authorization_in_CPU_reject',lambda r:(r/'control/SCIENCE_AUTHORIZATION.json').write_text('{}'))
fixture('CPU_claim_reject',lambda r:(r/'control/POOL_DISPATCH_RESERVATIONS.json').write_text('{"claims":{"CPU_ONLY":{}}}'))
fixture('INTENT_reject',lambda r:(r/'control/qualification_ledger/CPU_ONLY.INTENT.json').write_text('{}'))
fixture('DONE_reject',lambda r:(r/'control/qualification_ledger/CPU_ONLY.DONE.json').write_text('{}'))
fixture('result_member_reject',lambda r:(r/'DTC/run/results/CPU_ONLY_NOT_UUID').write_text('fixture'))
fixture('manifest_model_state_reject',lambda r:edit(r,'CLEAN_CPU_ARTIFACTS_MANIFEST.json','models_started',1))
# A normal finalcandidate guard test is in an isolated resource mock only, and
# never invokes registry, owner, model or grants authority.
def finalmock(r):
 pl=json.loads((r/'control/EXECUTION_PLAN.json').read_bytes());pl.update(preparation_phase='SCIENCE_FINAL_FROZEN',actual_execution_authorized=True);(r/'control/EXECUTION_PLAN.json').write_bytes(enc(pl));q=json.loads((r/'control/RESOURCE_REQUEST_CANDIDATE.CPU.json').read_bytes());q.update(ready_for_registration=True,execution_plan_sha256=sha(r/'control/EXECUTION_PLAN.json'));(r/'control/REGISTRY_REQUEST_CANDIDATE.json').write_bytes(enc(q));(r/'control/SCIENCE_AUTHORIZATION.json').write_bytes(enc({'schema':'DTC_ORACLE_SCIENCE_AUTHORIZATION_V1','ready_for_registration':True,'owner_bindings_ratified':True,'target_resource_policy_ratified':True,'CPU_FIXTURE_NOT_A_SCIENCE_GRANT':True}))
fixture('normal_final_guard_mock_only',finalmock,accepted=True)
# Native -> true164 -> native typed small CPU fixture, SOURCE_KEEP retained.
arc=R/'engineering_cpu/archive_qualification';src=arc/'source';dst=arc/'restored';src.mkdir(parents=True);dst.mkdir();(src/'payload.bin').write_bytes(bytes(range(256))*256);(src/'meta.json').write_text('{"CPU_only":true,"scientific_UUID":null}\n');(src/'nested').mkdir();(src/'nested/payload_link').symlink_to('../payload.bin')
archive=X/'CPU_NATIVE_TRUE164_NATIVE_FIXTURE.tar';
with tarfile.open(archive,'w')as t:t.add(src,arcname='CPU_SOURCE',recursive=True)
assert archive.stat().st_dev!=2128
# Generated fixed-member tar is extracted manually into checked fresh root.
with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()),mode='r')as t:
 for member in t.getmembers():
  target=(dst/member.name).resolve(strict=False);assert target.is_relative_to(dst.resolve())
  if member.isdir():target.mkdir(parents=True,exist_ok=True)
  elif member.isfile():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(member).read())
  elif member.issym():
   direct=dst/member.name;direct.parent.mkdir(parents=True,exist_ok=True);assert(direct.parent/member.linkname).resolve(strict=False).is_relative_to(dst.resolve());direct.symlink_to(member.linkname)
  else:raise AssertionError('UNEXPECTED_CPU_TAR_TYPE')
checks=[]
for rel in['payload.bin','meta.json']:
 a=src/rel;b=dst/'CPU_SOURCE'/rel;checks.append({'path':rel,'type':'regular','source_sha256':sha(a),'restored_sha256':sha(b),'match':sha(a)==sha(b)})
checks.append({'path':'nested/payload_link','type':'symlink','source_target':os.readlink(src/'nested/payload_link'),'restored_target':os.readlink(dst/'CPU_SOURCE/nested/payload_link'),'match':os.readlink(src/'nested/payload_link')==os.readlink(dst/'CPU_SOURCE/nested/payload_link')})
assert all(v['match']for v in checks)
report={'schema':'DTC_CLEAN_SUCCESSOR_CPU_PEER_AND_ARCHIVE_QUALIFICATION_V1','status':'PASS','peer_source_sha256':sha(p),'tests':tests,'actual_sources_unchanged':True,'scientific_registrations':0,'scientific_UUIDs':0,'models_started':0,'production_locks_acquired':0,'archive_fixture':{'source':str(src),'target_true164':str(archive),'archive_sha256':sha(archive),'restored_native':str(dst),'SOURCE_KEEP':src.is_dir()and(src/'payload.bin').exists(),'typed_checks':checks,'CPU_only_not_a_scientific_archive_or_restore_receipt':True}}
(X/'PEER_AND_RESTORE_CPU_QUALIFICATION.json').write_bytes(enc(report));print(json.dumps({'tests':len(tests),'all_PASS':all(t['test_PASS']for t in tests),'archive_typed_PASS':all(t['match']for t in checks),'source_sha256':sha(p),'qualification_sha256':sha(X/'PEER_AND_RESTORE_CPU_QUALIFICATION.json')}))
