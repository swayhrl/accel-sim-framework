from closure_local import *
from closure_resources import UTIL,checkpoint
top=rows(B/'LARGE_ASSETS_TOP30.csv');poly=rows(B/'POLYBENCH_TRACE_INVENTORY.csv')
roots=list(dict.fromkeys(r['source_path'] for r in top+poly))
# Existing exact trace members are checked once for Source-directory extras, not rehashed.
tr=load(T/'TRUE164_TRACE_RECOVERY_INDEX.json')['records']
roots+= [r['source_root'] for r in tr if r['source_root'] not in roots]
code=UTIL+'\nroots='+repr(roots)+r'''
import hashlib,re,gzip
out=[];total_entries=0;start=time.monotonic()
allowed=('/workspace/','/root/share/accel-sim/','/root/share/workspace_migrated_20260905/')
for root in roots:
 if not root or not root.startswith(allowed) or '..' in Path(root).parts:
  out.append(dict(path=root,status='IDENTITY_HOLD'));continue
 s=meta(root);r=dict(path=root,root=s,realpath=os.path.realpath(root),namespace=os.readlink('/proc/self/ns/mnt'),mount=cmd(['findmnt','-J','-T',root]),status='CURRENT_METADATA_COMPLETE',members=[],commandlists=[],header_samples=[],symlinks=[],pruned=[])
 if 'error' in s:r['status']='ABSENT_OR_UNREADABLE';out.append(r);continue
 if s['type']=='file':r['asset_kind']='COMPRESSED_PACKAGE_FILE';r['members']=[s];r['archive_inner_members']='REQUIRES_EXISTING_TRUSTED_TAR_INDEX_OR_FUTURE_STREAM_INSPECTION';out.append(r);continue
 r['asset_kind']='TRACE_DIRECTORY';q=[(root,0)];t0=time.monotonic()
 while q:
  p,d=q.pop()
  if total_entries>55000 or time.monotonic()-start>30 or time.monotonic()-t0>4:
   r['status']='INCOMPLETE_METADATA_BUDGET';r['pending_dirs']=len(q)+1;break
  try:
   with os.scandir(p) as it:
    for e in it:
     total_entries+=1;m=meta(e.path);m['relative_path']=os.path.relpath(e.path,root)
     if m.get('type')=='symlink':m['resolved_path']=os.path.realpath(e.path);r['symlinks'].append(m);continue
     if m.get('type')=='dir':
      r['members'].append(m)
      if d<12 and e.name not in ['.git','.ssh','.env']:q.append((e.path,d+1))
      else:r['pruned'].append(e.path)
     elif m.get('type')=='file':
      r['members'].append(m)
      if e.name in ['kernelslist.g','kernelslist','commandlist','commandlist.txt'] and m['size']<=1024*1024:
       b=Path(e.path).read_bytes();txt=b.decode(errors='replace');lines=[x.strip() for x in txt.splitlines() if '.traceg' in x and not x.lstrip().startswith('#')]
       r['commandlists'].append(dict(path=e.path,relative_path=m['relative_path'],sha256=hashlib.sha256(b).hexdigest(),size=len(b),original_text=txt,ordered_kernel_lines=lines))
      if ('.traceg' in e.name) and len(r['header_samples'])<2:
       try:
        with (gzip.open(e.path,'rb') if e.name.endswith('.gz') else open(e.path,'rb')) as f:hdr=f.read(2048)
        r['header_samples'].append(dict(path=e.path,read_scope='decoded prefix <=2048B; no complete payload SHA',header=hdr.decode(errors='replace')))
       except (OSError,EOFError) as ex:r['header_samples'].append(dict(path=e.path,error=str(ex)))
  except OSError as ex:r['pruned'].append(dict(path=p,error=str(ex)))
 if r['pruned']:r['status']='INCOMPLETE_PRUNED'
 r['files']=sum(m.get('type')=='file' for m in r['members']);r['directories']=1+sum(m.get('type')=='dir' for m in r['members']);r['logical_bytes']=sum(m.get('size',0) for m in r['members'] if m.get('type')=='file');r['allocated_bytes']=sum(m.get('allocated',0) for m in r['members'] if m.get('type')=='file')
 after=meta(root);r['root_identity_stable']=all(s.get(k)==after.get(k) for k in ['dev','inode','mtime_ns','ctime_ns']);out.append(r)
print(json.dumps(dict(utc=time.time(),roots=out,entries=total_entries,seconds=time.monotonic()-start,large_content_SHA_bytes=0)))
'''
checkpoint('P0_BEFORE_METADATA')
x=remote('hrl',code,75);save('evidence/P0_P1_EXACT_SOURCE_MEMBER_AND_COMMANDLIST_AUDIT.json',x)
print('exactroots',len(x['roots']),'entries',x['entries'],'statuscounts',__import__('collections').Counter(r['status'] for r in x['roots']))
checkpoint('P0_AFTER_METADATA')
