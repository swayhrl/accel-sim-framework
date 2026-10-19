#!/usr/bin/env python3
"""One bounded metadata pass. No file content reads, symlink traversal or Git object walks."""
import os,sys,time,json,stat,subprocess,collections,datetime
O=os.path.dirname(os.path.abspath(__file__)); start=time.time(); rows={}; links={}; skipped=[]; errors=[]; n=0

def space():
 r={}
 for p in ['/workspace','/root/data','/root/share']:
  s=os.statvfs(p); t=os.stat(p); r[p]=dict(device=t.st_dev,fsid=s.f_fsid,f_bavail=s.f_bavail,f_bfree=s.f_bfree,f_frsize=s.f_frsize,available_bytes=s.f_bavail*s.f_frsize,free_bytes=s.f_bfree*s.f_frsize)
 return r

def snap():
 return dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space(),mount_namespace=os.readlink('/proc/self/ns/mnt'),io_pressure=open('/proc/pressure/io').read(),cgroup_io_pressure=open('/sys/fs/cgroup/io.pressure').read(),ram_available_bytes=int(next(l.split()[1] for l in open('/proc/meminfo') if l.startswith('MemAvailable:')))*1024,cgroup_memory_current=open('/sys/fs/cgroup/memory.current').read().strip(),cgroup_memory_max=open('/sys/fs/cgroup/memory.max').read().strip())
json.dump(snap(),open(O+'/space_continuation_start.json','w'),indent=2)
roots=[]
for parent in ['/workspace','/tmp','/root/.cache','/root/.local']:
 for e in sorted(os.scandir(parent),key=lambda e:e.name):
  if parent=='/workspace' and e.name in ['worktrees','repos','build','builds']:
   roots.extend(x.path for x in sorted(os.scandir(e.path),key=lambda e:e.name))
  elif e.name!='.git': roots.append(e.path)
for p in ['/root/tools','/root/Sixth','/root/Desktop']: roots.append(p)
# Largest likely payloads first so a bounded partial run is useful.
previous=json.load(open(O+'/scan_checkpoint.json')); visited={r['scan_root'] for r in previous['rows']}; roots=[p for p in roots if p not in visited]; roots.sort(key=lambda p:(0 if 'm2d' in p or 'tls' in p or 'c2p' in p else 1,0 if not os.path.islink(p) and os.path.isdir(p) else 1,p))

def flush(done=False):
 json.dump(dict(start_utc=datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),elapsed_seconds=time.time()-start,entries=n,complete=done,roots=roots,rows=sorted(rows.values(),key=lambda r:-r['allocated_bytes']),skipped=skipped,errors=errors),open(O+'/scan_continuation.json','w'),indent=2)
last=time.time()
for root in roots:
 if time.time()-start>90 or n>2500000: skipped.append(dict(path=root,reason='GLOBAL_BUDGET')); continue
 try: st=os.lstat(root)
 except OSError as e: errors.append([root,str(e)]); continue
 if stat.S_ISLNK(st.st_mode): skipped.append(dict(path=root,reason='SYMLINK',target=os.readlink(root))); continue
 if st.st_dev!=os.stat('/workspace').st_dev: skipped.append(dict(path=root,reason='OTHER_DEVICE',device=st.st_dev)); continue
 rootstart=time.time(); stack=[root]; complete=True; touched=set()
 while stack:
  p=stack.pop()
  if time.time()-start>90 or time.time()-rootstart>35 or n>2500000:
   complete=False; skipped.append(dict(path=root,reason='ROOT_OR_GLOBAL_TIME_BUDGET',unvisited_stack=len(stack)+1)); break
  try: s=os.lstat(p)
  except OSError as e: errors.append([p,str(e)]); continue
  n+=1
  if s.st_dev!=st.st_dev: skipped.append(dict(path=p,reason='MOUNT_DEVICE')); continue
  rel=os.path.relpath(p,root); parts=[] if rel=='.' else rel.split('/')
  keys=[root]+[root+'/'+ '/'.join(parts[:i]) for i in range(1,min(len(parts),3)+1) if (i<len(parts) or stat.S_ISDIR(s.st_mode))]
  alloc=s.st_blocks*512; logical=s.st_size; duplicate=False
  if stat.S_ISREG(s.st_mode) and s.st_nlink>1:
   ident=(s.st_dev,s.st_ino)
   if ident in links: duplicate=True
   else: links[ident]=p
  for k in keys:
   if k not in rows:
    ks=os.lstat(k); rows[k]=dict(path=k,scan_root=root,device=ks.st_dev,inode=ks.st_ino,uid=ks.st_uid,gid=ks.st_gid,allocated_bytes=0,logical_bytes=0,files=0,dirs=0,symlinks=0,multiple_link_entries=0,duplicate_link_bytes=0,max_mtime_ns=0,sparse_files=0,complete=False)
   touched.add(k); r=rows[k]; r['allocated_bytes']+=0 if duplicate else alloc; r['logical_bytes']+=0 if duplicate else logical; r['duplicate_link_bytes']+=alloc if duplicate else 0
   r['files']+=stat.S_ISREG(s.st_mode); r['dirs']+=stat.S_ISDIR(s.st_mode); r['symlinks']+=stat.S_ISLNK(s.st_mode); r['multiple_link_entries']+=stat.S_ISREG(s.st_mode) and s.st_nlink>1; r['sparse_files']+=stat.S_ISREG(s.st_mode) and logical>alloc+4096; r['max_mtime_ns']=max(r['max_mtime_ns'],s.st_mtime_ns)
  if stat.S_ISDIR(s.st_mode):
   if os.path.basename(p)=='.git': skipped.append(dict(path=p,reason='GIT_CONTENT_PRUNED')); continue
   try: stack.extend(sorted((e.path for e in os.scandir(p)),reverse=True))
   except OSError as e: errors.append([p,str(e)]); complete=False
  if n%10000==0: time.sleep(.03)
  if time.time()-last>12: flush(); last=time.time()
 for k in touched: rows[k]['complete']=complete
 print(json.dumps(dict(root=root,allocated=rows.get(root,{}).get('allocated_bytes'),complete=complete)),flush=True)
flush(True); json.dump(snap(),open(O+'/space_continuation_end.json','w'),indent=2)
