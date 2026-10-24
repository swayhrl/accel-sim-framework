"""Finite metadata-only scanner; input roots externally positively attributed."""
import os,stat,time,json,collections
from pathlib import Path
def scan(roots,seconds=22,max_entries=180000):
 started=time.monotonic();out=[];total=0
 for root in roots:
  if not root or not root.startswith(('/workspace/','/tmp/','/root/data/','/root/workspace/','/root/share/workspace_migrated_20260905/','/root/share/accel-sim/')) or '..' in Path(root).parts:
   out.append(dict(path=root,status='IDENTITY_HOLD'));continue
  if total>=max_entries or time.monotonic()-started>seconds:
   out.append(dict(path=root,status='BATCH_BUDGET_NOT_SCANNED'));continue
  try:rs=os.lstat(root)
  except OSError as e:out.append(dict(path=root,status='ABSENT_OR_UNREADABLE',error=str(e)));continue
  if stat.S_ISLNK(rs.st_mode):out.append(dict(path=root,status='SYMLINK_NOT_FOLLOWED',target=os.readlink(root),dev=rs.st_dev,inode=rs.st_ino));continue
  r=dict(path=root,dev=rs.st_dev,inode=rs.st_ino,root_mtime_ns=rs.st_mtime_ns,root_ctime_ns=rs.st_ctime_ns,status='COMPLETE_METADATA_ONLY',files=0,dirs=0,symlinks=0,logical=0,allocated=0,unique_inode_logical=0,unique_inode_allocated=0,hardlink_entries=0,errors=[],pruned=[],types={},assets=[],large_files=[])
  seen=set();stack=[(root,0)];t0=time.monotonic();n=0;acc={};dirs=[];ty=collections.defaultdict(lambda:[0,0,0])
  while stack:
   p,d=stack.pop()
   if total>=max_entries or time.monotonic()-started>seconds or n>220000 or time.monotonic()-t0>12:
    r['status']='INCOMPLETE_BUDGET';r['pending_dirs']=len(stack)+1;break
   try:
    s=os.lstat(p);total+=1;n+=1
    if total%256==0:time.sleep(.002)
    if s.st_dev!=rs.st_dev:r['pruned'].append(dict(path=p,why='DEVICE_BOUNDARY'));continue
    mode=s.st_mode
    if stat.S_ISLNK(mode):r['symlinks']+=1;continue
    if stat.S_ISDIR(mode):
     r['dirs']+=1;dirs.append((p,d));acc[p]=[0,0,0,1]
     try:
      with os.scandir(p) as it:
       for e in it:
        if e.name in ['.git','.ssh','.aws','.azure','.env','node_modules','__pycache__','.venv','venv']:
         if len(r['pruned'])<50:r['pruned'].append(dict(path=e.path,why='GIT_PRIVATE_OR_ENV_PRUNED'))
         continue
        stack.append((e.path,d+1))
     except OSError as e:r['errors'].append(dict(path=p,error=str(e)))
    elif stat.S_ISREG(mode):
     r['files']+=1;r['logical']+=s.st_size;r['allocated']+=s.st_blocks*512
     key=(s.st_dev,s.st_ino)
     if key not in seen:r['unique_inode_logical']+=s.st_size;r['unique_inode_allocated']+=s.st_blocks*512;seen.add(key)
     else:r['hardlink_entries']+=1
     ext=''.join(Path(p).suffixes[-2:]).lower() or '[no_extension]';ext=ext if len(ext)<=40 else '[long_extension]'
     ty[ext][0]+=1;ty[ext][1]+=s.st_size;ty[ext][2]+=s.st_blocks*512
     parent=str(Path(p).parent)
     if parent in acc:acc[parent][0]+=s.st_size;acc[parent][1]+=s.st_blocks*512;acc[parent][2]+=1
     if s.st_size>=128*1024**2:r['large_files'].append(dict(path=p,dev=s.st_dev,inode=s.st_ino,size=s.st_size,allocated=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,nlink=s.st_nlink))
   except OSError as e:
    if len(r['errors'])<20:r['errors'].append(dict(path=p,error=str(e)))
  for p,d in sorted(dirs,key=lambda z:z[1],reverse=True):
   if p==root:continue
   parent=str(Path(p).parent)
   if parent in acc:
    for i in range(4):acc[parent][i]+=acc[p][i]
  for p,d in dirs:
   a=acc[p];name=Path(p).name.lower()
   if (d<=3 and a[1]>=32*1024**2) or name in ['traces','raw','results','postcheck','ptw','tlb','calibration','build']:
    r['assets'].append(dict(path=p,depth=d,logical=a[0],allocated=a[1],files=a[2],dirs=a[3]))
  r['types']={k:dict(files=v[0],logical=v[1],allocated=v[2]) for k,v in ty.items()}
  r['entries']=n;r['seconds']=time.monotonic()-t0
  try:
   after=os.lstat(root);r['root_identity_changed']=any(getattr(rs,k)!=getattr(after,k) for k in ['st_dev','st_ino','st_mtime_ns','st_ctime_ns'])
  except OSError:r['root_identity_changed']=True
  if r['errors']:r['status']='INCOMPLETE_ERRORS'
  out.append(r)
 return dict(utc=time.time(),seconds=time.monotonic()-started,entries=total,roots=out,scope='regular file st_size/st_blocks only; directory blocks omitted; no symlink following; no file content reads; root mtime does NOT prove closed tree')
