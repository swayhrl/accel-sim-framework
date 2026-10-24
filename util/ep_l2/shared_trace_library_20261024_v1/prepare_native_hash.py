from pathlib import Path
import json,os,stat,fcntl
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
lease=(R/'control/174-new_HASH_DRIVER.lock').open('a')
try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:print('NATIVE_HASH_ALREADY_LIVE_SEED_SKIPPED',flush=True);raise SystemExit(0)
if (R/'control/174_HASH_COMPLETE.json').exists():source=json.loads((R/'control/174_HASH_COMPLETE.json').read_text())['files']
else:source={json.loads(line)['key']:json.loads(line) for line in (R/'control/174_FILE_SHA.jsonl').read_text().splitlines()}
native=json.loads((R/'control/174-new_FROZEN_METADATA.json').read_text())['files']
fields=['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type']
byid={tuple(v['identity'][k] for k in fields):v for v in source.values()}
path=R/'control/174-new_FILE_SHA.jsonl';existing={}
prior={}
catalog=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())
for asset in catalog['assets']:
 for member in asset['members']:
  p=Path(asset['mount_tree'])/member['relative_path'];s=p.stat()
  assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==member['verified_tree_identity']
  prior[str(p.resolve())]={'sha256':member['sha256'],'verified_identity':member['verified_tree_identity'],'proof_reference':asset['proof_reference'],'path':str(p)}
if path.exists():
 for l in path.read_text().splitlines():
  d=json.loads(l);existing[d['key']]=d
for r in native:
 if r['key'] in existing or r.get('sha256'):continue
 old=byid.get(tuple(r['identity'][k] for k in fields))
 if old:
  s=os.stat(r['path']);assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==tuple(r['identity'][k] for k in ['dev','inode','size','mtime_ns','ctime_ns'])
  existing[r['key']]={'event':'FILE_SHA','key':r['key'],'path':r['path'],'identity':r['identity'],'sha256':old['sha256'],'bytes':r['identity']['size'],'source_before_after_unchanged':True,'reused_identical_current_file_object_source_sha':old['key']}
 elif r['realpath'] in prior:
  old=prior[r['realpath']];s=os.stat(r['path']);current={'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'type':'file'if stat.S_ISREG(s.st_mode)else'other'}
  assert all(current[k]==r['identity'][k] for k in fields)
  assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==old['verified_identity']
  existing[r['key']]={'event':'FILE_SHA','key':r['key'],'path':r['path'],'identity':r['identity'],'sha256':old['sha256'],'bytes':r['identity']['size'],'source_before_after_unchanged':True,'sha_source':'PRIOR_SEALED_TRUE164_OBJECT_IDENTITY_REUSE_NOT_NEW_BODY_READ','prior_proof':old}
path.write_text(''.join(json.dumps(r)+'\n' for r in existing.values()))
print(json.dumps({'same_physical_objects_reused':len(existing),'native_files':len(native)}))
