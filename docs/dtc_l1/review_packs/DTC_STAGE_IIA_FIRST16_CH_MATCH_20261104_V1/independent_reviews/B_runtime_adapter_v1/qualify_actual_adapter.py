"""Synthetic CPU-only archive adapter tests. No simulator/native-science fixtures are emitted."""
from pathlib import Path
import tempfile,copy,json,hashlib,importlib.util,os,stat,shutil
from unittest.mock import patch
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('actual_adapter',B/'actual_readonly_adapter.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
def check(name,fn,fail=False):
 try:fn();ok=not fail
 except (ValueError,KeyError,OSError) as exc:
  if not fail:print('UNEXPECTED',name,repr(exc))
  ok=fail
 assert ok,name;checks.append({'name':name,'pass':True})
check('unsafe_parent_path_rejected',lambda:m.exact_safe(B,'../bad'),True)
check('unsafe_absolute_path_rejected',lambda:m.exact_safe(B,str(B/'bad')),True)
check('restore_row_count_rejected',lambda:m.verify_restore_rows({'entries':[{'path':'x'}]},{'rows':[]},B),True)
check('restore_duplicate_path_rejected',lambda:m.verify_restore_rows({'entries':[{},{}]},{'rows':[{'path':'x'},{'path':'x'}]},B),True)
# Namespace, JSON, file SHA and archive-stream logic are exercised with explicitly synthetic data.
# Only st_dev is mocked to the expected native number: no hardware qualification is inferred.
original_lstat=Path.lstat

def fake_native_lstat(p):
 x=original_lstat(p);v=list(x);v[2]=2128;return os.stat_result(v)

def fixture(parent,successful=True):
 m.R=parent/'native_fixture';m.NAS=parent/'archive_fixture';c='SYNTHETIC_ONLY_NO_SCIENTIFIC_IDENTITY';tx='b'*64;out=m.R/'DTC/run/results'/'fixture_uuid';restore=m.R/'DTC/run/recovery'/tx;target=m.NAS/c/tx
 for p in [out,restore,target/'chunks',m.R/'control']:p.mkdir(parents=True,exist_ok=True)
 done={'uuid':'fixture_uuid','raw_sha256':hashlib.sha256(b'compressed_fixture').hexdigest()};data={'NATIVE_EXIT.json':json.dumps(done).encode(),'DOWNSTREAM_FROZEN_SPEC.json':b'{"fixture":true}','DISPATCH_BINDING.json':b'{"fixture":true}','raw.log.gz':b'compressed_fixture'}
 if successful:data['L2_STRICT.json']=b'{"fixture":"strict"}'
 entries=[{'path':'.','type':'directory'}];proofrows=[{'path':'.','type':'directory','identity':{'dev':2128},'sha256':None,'target':None}]
 for n,b in data.items():
  (out/n).write_bytes(b);(restore/n).write_bytes(b);sha=hashlib.sha256(b).hexdigest();entries.append({'path':n,'type':'file','size':len(b),'sha256':sha});proofrows.append({'path':n,'type':'file','sha256':sha,'identity':{'dev':2128},'target':None})
 manifest={'cohort':c,'txid':tx,'source_root':str(out),'scientific_status':m.STRICT_STATUS if successful else 'STOP_UNACCEPTED','native_execution_receipt_sha256':m.sha(out/'NATIVE_EXIT.json'),'entries':entries};payload=b'SYNTHETIC_ARCHIVE_STREAM_INTEGRITY_FIXTURE_NOT_ACTUAL_TAR';(target/'chunks/00000000000000000000.part').write_bytes(payload);index={'archive_bytes':len(payload),'archive_sha256':m.hashbytes(payload),'chunks':[{'name':'00000000000000000000.part','offset':0,'txid':tx,'size':len(payload),'sha256':m.hashbytes(payload)}]};commit={'manifest_sha256':m.hashbytes(m.canon(manifest)),'archive_index_sha256':m.hashbytes(m.canon(index)),'txid':tx};receipt={'cohort':c,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','source_disposition':'SOURCE_KEEP','source_release_bytes':0,'scientific_acceptance_granted_by_archive':False,'target_mount_path':str(target),'native_restore':str(restore),'txid':tx,'true164_root':str(target).replace('/root/share/mnt164','/home/shared',1),'scientific_status':manifest['scientific_status'],'manifest_sha256':commit['manifest_sha256'],'archive_sha256':index['archive_sha256'],'archive_bytes':index['archive_bytes']}
 for p,d in [(target/'RECEIPT.json',receipt),(m.R/'control'/(c+'_ARCHIVE_RECEIPT.json'),receipt),(target/'SOURCE_MANIFEST.json',manifest),(target/'ARCHIVE_INDEX.json',index),(target/'COMMIT.json',commit),(target/'RESTORE_VERIFIED_NATIVE_TARGET.json',{'txid':tx,'rows':proofrows})]:p.write_text(json.dumps(d))
 result={'archive':{'receipt':receipt,'independently_verified_entries':len(entries),'archive_overlay_sha256':'a'*64}}
 return c,result,out,done,successful,{'outbox_sha256':'a'*64},target,restore

def one(name,mutation=None,fail=False,successful=True):
 with tempfile.TemporaryDirectory(prefix='CPU_SYNTHETIC_',dir=B) as t:
  c,r,o,d,s,ctx,target,restore=fixture(Path(t),successful)
  if mutation:mutation(c,r,o,d,s,ctx,target,restore)
  check(name,lambda:m.verify_archive(c,r,o,d,s,ctx,check_mount=False),fail)
with patch.object(Path,'lstat',fake_native_lstat):
 one('success_archive_and_restored_member_integrity')
 one('negative_archive_without_strict_is_archive_only',successful=False)
 one('corrupted_chunk_rejected',lambda c,r,o,d,s,x,t,z:(t/'chunks/00000000000000000000.part').write_bytes(b'corrupt'),True)
 one('corrupted_native_restore_rejected',lambda c,r,o,d,s,x,t,z:(z/'raw.log.gz').write_bytes(b'corrupt'),True)
 one('corrupted_source_critical_member_rejected',lambda c,r,o,d,s,x,t,z:(o/'raw.log.gz').write_bytes(b'corrupt'),True)
 one('success_without_strict_member_rejected',lambda c,r,o,d,s,x,t,z:(z/'L2_STRICT.json').unlink(),True)
 one('outbox_source_pin_mismatch_rejected',lambda c,r,o,d,s,x,t,z:x.update(outbox_sha256='c'*64),True)
 one('wrong_overlay_pin_rejected',lambda c,r,o,d,s,x,t,z:r['archive'].update(archive_overlay_sha256='c'*64),True)
 one('negative_cannot_claim_qualified_scientific_status',lambda c,r,o,d,s,x,t,z:r['archive']['receipt'].update(scientific_status=m.STRICT_STATUS),True,False)
 one('receipt_cannot_grant_science',lambda c,r,o,d,s,x,t,z:r['archive']['receipt'].update(scientific_acceptance_granted_by_archive=True),True)
 one('receipt_wrong_restore_namespace_rejected',lambda c,r,o,d,s,x,t,z:r['archive']['receipt'].update(native_restore=str(z.parent/'wrong')),True)
 one('restore_manifest_member_mismatch_rejected',lambda c,r,o,d,s,x,t,z:(t/'RESTORE_VERIFIED_NATIVE_TARGET.json').write_text(json.dumps({'txid':'b'*64,'rows':[]})),True)
 one('canonical_commit_index_mismatch_rejected',lambda c,r,o,d,s,x,t,z:(t/'COMMIT.json').write_text(json.dumps({'txid':'b'*64,'manifest_sha256':r['archive']['receipt']['manifest_sha256'],'archive_index_sha256':'0'*64})),True)
result={'schema':'DTC_STAGEIIA_READONLY_RUNTIME_ADAPTER_CPU_QA_V1','synthetic_only':True,'not_native_hardware_qualification':True,'native_device_mocked_only_for_synthetic_restore_tests':2128,'archive_fixture_not_real_tar':'only stream-integrity and linked restore/manifest checks tested; source-authoritative original outbox owns tar construction/verification','checks':checks,'all_pass':all(x['pass'] for x in checks),'adapter_sha256':m.sha(B/'actual_readonly_adapter.py'),'new_models':0,'original_or_native_scientific_mutations':0};(B/'CPU_RUNTIME_ADAPTER_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(len(checks),'PASS')


