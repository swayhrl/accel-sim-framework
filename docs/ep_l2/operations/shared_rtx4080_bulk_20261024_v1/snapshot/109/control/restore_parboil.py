#!/usr/bin/env python3
import pathlib,tarfile,hashlib,json,os
r=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
tree={x['path']:x for x in json.loads((r/'control/parboil_tree.json').read_text())}
root=r/'assets/parboil_source_verified';root.mkdir(exist_ok=False)
rec={'source':'https://codeload.github.com/palmer-dabbelt/parboil/tar.gz/4e0fc54866546efa44fe93af57c9cef62f6c8eb9','commit':'4e0fc54866546efa44fe93af57c9cef62f6c8eb9','archive_complete':False,'member_verification':'Git SHA1(blob length plus content) against immutable GitHub tree','members':[]}
try:
 with tarfile.open(r/'assets/parboil_4e0fc548.source_dataset.tar.gz.part',mode='r|gz') as t:
  for m in t:
   if not m.isfile():continue
   rel='/'.join(pathlib.PurePosixPath(m.name).parts[1:])
   if not rel:continue
   assert not pathlib.PurePosixPath(rel).is_absolute() and '..' not in pathlib.PurePosixPath(rel).parts
   if rel not in tree:continue
   b=t.extractfile(m).read()
   sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   assert sha==tree[rel]['sha'],rel
   p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);p.chmod(0o755 if tree[rel]['mode']=='100755' else 0o644)
   rec['members'].append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':sha})
except (tarfile.ReadError,EOFError,OSError) as e:rec['archive_read_stop']=repr(e)
rec['verified_files']=len(rec['members']);rec['verified_bytes']=sum(x['bytes'] for x in rec['members']);rec['remaining']=[x for x in tree if x not in {m['path'] for m in rec['members']}]
(r/'control/PARBOIL_PARTIAL_ARCHIVE_MEMBER_RECOVERY.json').write_text(json.dumps(rec,indent=2)+'\n')
print(rec['verified_files'],rec['verified_bytes'],'remaining',len(rec['remaining']),rec.get('archive_read_stop'))

