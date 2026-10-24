"""Re-use four exactly bound prior164 copies after another authorized task retired originals."""
from pathlib import Path
import json,hashlib,time,sys
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
O=Path('/root/data/research_asset_verified_offload_20261024_v1')
sys.path.insert(0,str(R/'tools'));import library_copy as e
frozen={r['path']:r for r in json.loads((R/'control/174_FROZEN_METADATA.json').read_text())['files']}
rows=[json.loads(l)for l in(O/'release/SOURCE.jsonl').read_text().splitlines()]
intents=[r for r in rows if r['event']=='INTENT'];assert len(intents)==4
cat=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())
prior={str(Path(a['mount_tree'])/m['relative_path']):dict(member=m,proof=a['proof_reference'])for a in cat['assets']for m in a['members']}
out=[];fields=['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','nlink']
for old in intents:
 r=frozen[old['path']];assert all(old['identity'][k]==r['identity'][k]for k in fields)
 assert any(x['event']=='DONE'and x.get('path')==old['path']for x in rows)
 p=Path(old['recovery'].replace('/home/shared','/root/share/mnt164',1));before=p.stat();binding=prior[str(p)]
 assert [before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns]==binding['member']['verified_tree_identity']
 assert binding['member']['sha256']==old['expected_sha256'] and before.st_size==r['identity']['size']
 actual=e.hash_file(p);assert actual==old['expected_sha256']
 after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 out.append(dict(event='FILE_SHA',key=r['key'],path=r['path'],identity=r['identity'],sha256=actual,bytes=before.st_size,sha_source='REUSED_EXACT_PRIOR_SEALED_OBJECT_AFTER_OTHER_AUTHORIZED_RETIREMENT',source_original_path_currently_exists=False,new_original_source_body_read_claimed=False,prior_source_release_intent=old,prior_full_SHA_proof=binding['proof'],current_true164_storage=dict(path=str(p),identity=[after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns]),current_true164_closed_reopen_full_sha_verified=True))
log=R/'control/174_FILE_SHA.jsonl';done={json.loads(l)['key']for l in log.read_text().splitlines()}
with log.open('a')as f:
 for r in out:
  if r['key']not in done:f.write(json.dumps(r)+'\n');f.flush()
receipt=dict(status='PASS_FOUR_EXACT_FROZEN_SOURCE_CONTENTS_FROM_PRIOR_VERIFIED_164',objects=out,bytes=sum(r['bytes']for r in out),this_goal_source_writes=0,this_goal_released_source_bytes=0,retirement_actor=str(O),observed_unix=time.time())
(R/'control/RETIRED_SOURCE_CONTENT_REUSE.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='objects'}),flush=True)
