#!/usr/bin/env python3
import gzip,hashlib,json,os,pathlib,stat,sys
here=pathlib.Path(__file__).resolve().parent;root=pathlib.Path(sys.argv[1]);count=0
with gzip.open(here/'MEMBER_SHA256_AND_METADATA.jsonl.gz','rt') as rows:
 for line in rows:
  r=json.loads(line);p=root/r['relative_path'];s=p.lstat()
  assert not p.is_symlink()
  assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_mtime_ns)==(r['uid'],r['gid'],r['mode'],r['mtime_ns']),str(p)
  if r['type']=='regular':
   assert stat.S_ISREG(s.st_mode) and s.st_size==r['size'];h=hashlib.sha256()
   with p.open('rb') as f:
    while b:=f.read(1024**2):h.update(b)
   assert h.hexdigest()==r['sha256'],str(p)
  else:assert stat.S_ISDIR(s.st_mode)
  count+=1
print('ALL_RESTORED_CONTENT_AND_NUMERIC_METADATA_MATCH',count)
