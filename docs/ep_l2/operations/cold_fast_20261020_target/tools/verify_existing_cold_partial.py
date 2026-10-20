"""Retry only validation of a complete, Source-hash-bound NAS partial."""
import base64,json,pathlib,shlex,subprocess,sys
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import tls_target as t
tag,attempt=sys.argv[1:];assert attempt.isdigit()
lines=(D/(tag+'_SOURCE_STDERR.log')).read_bytes().splitlines()
source=[json.loads(x[len(b'COLD_SOURCE_DONE '):]) for x in lines if x.startswith(b'COLD_SOURCE_DONE ')]
assert len(source)==1;source=source[0];assert source['status']=='SOURCE_READONLY_STREAM_COMPLETE' and source['frozen_metadata_before_after_exact']
C=json.loads((D/(tag+'_CONFIG.json')).read_bytes());C.update(validation_only=True,expected_archive_sha256=source['archive_sha256'],expected_archive_bytes=source['compressed_bytes'],sample_run_tag=C['tag']+'_VERIFY_RETRY'+attempt)
C['bounded_existing_small_V3_validation']=(tag=='463600cb')
code="""import pathlib,json,os
p=pathlib.Path(__BASE__)/'MEMBER_SHA256_AND_METADATA.jsonl.gz.partial';q=p.with_name('MEMBER_SHA256_AND_METADATA.jsonl.gz.INCOMPLETE_RETAINED_'+__ATTEMPT__)
if p.exists():
 assert not q.exists();p.rename(q)
print(json.dumps({'source_data_retransferred':False,'archive_reused':True,'previous_incomplete_metadata_preserved':q.exists()}))
""".replace('__BASE__',repr(C['target_root'])).replace('__ATTEMPT__',repr(attempt))
t.remote(code,'COLD_'+tag+'_VALIDATION_ONLY_REUSE_'+attempt,timeout=30,save_receipt=False)
cmd='python3 -B -c '+shlex.quote('import base64;exec(compile(base64.b64decode('+repr(base64.b64encode((D/'cold_receive.py').read_bytes()).decode())+'),"<cold_verify_existing>","exec"))')+' '+shlex.quote(json.dumps(C,separators=(',',':')))
p=subprocess.run(['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl-174-new','timeout -k 10s 1800s '+cmd],stdin=subprocess.DEVNULL,capture_output=True,timeout=1820)
(D/(tag+'_VALIDATION_ONLY_'+attempt+'_STDERR.log')).write_bytes(p.stderr)
assert p.returncode==0,p.stderr.decode(errors='replace')[-1800:]
target=json.loads(p.stdout)
for a,b in [('archive_sha256','archive_sha256'),('compressed_bytes','archive_bytes'),('tar_stream_sha256','tar_stream_sha256'),('tar_stream_bytes','tar_stream_bytes')]:assert source[a]==target[b]
handoff=json.loads((D/'SOURCE_HANDOFF.json').read_bytes());binding=next(b for b in handoff['batches'] if b['batch']=='V3_'+tag)
probe=binding['source_identity_challenge'];sample=next(x for x in target['samples'] if x['relative_path']==probe['frozen_metadata_row'][0]);assert sample['sha256']==probe['sha256']
result=dict(source=source,target=target,config=C,source_handoff_commit='ed5c1c48e73c70927dfc3c909e3a096a90913b07',source_and_target_archive_and_decoded_tar_SHA_equal=True,source_originals='SOURCE_KEEP',source_actual_released_bytes=0,source_archive_retransferred=False,validation_only_retry=attempt)
(D/(tag+'_CROSS_VERIFIED.json')).write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps({'status':'EXISTING_NAS_ARCHIVE_FULLY_VERIFIED','tag':tag,'source_retransferred_bytes':0,'files':target['regular_files'],'directories':target['directories_including_root'],'archive_sha256':target['archive_sha256']}),flush=True)
