from pathlib import Path
import json,os,stat
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
source=json.loads((R/'control/174_HASH_COMPLETE.json').read_text())['files']
native=json.loads((R/'control/174-new_FROZEN_METADATA.json').read_text())['files']
fields=['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type']
byid={tuple(v['identity'][k] for k in fields):v for v in source.values()}
path=R/'control/174-new_FILE_SHA.jsonl';existing={}
if path.exists():
 for l in path.read_text().splitlines():
  d=json.loads(l);existing[d['key']]=d
for r in native:
 if r['key'] in existing or r.get('sha256'):continue
 old=byid.get(tuple(r['identity'][k] for k in fields))
 if old:
  s=os.stat(r['path']);assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==tuple(r['identity'][k] for k in ['dev','inode','size','mtime_ns','ctime_ns'])
  existing[r['key']]={'event':'FILE_SHA','key':r['key'],'path':r['path'],'identity':r['identity'],'sha256':old['sha256'],'bytes':r['identity']['size'],'source_before_after_unchanged':True,'reused_identical_current_file_object_source_sha':old['key']}
path.write_text(''.join(json.dumps(r)+'\n' for r in existing.values()))
print(json.dumps({'same_physical_objects_reused':len(existing),'native_files':len(native)}))
