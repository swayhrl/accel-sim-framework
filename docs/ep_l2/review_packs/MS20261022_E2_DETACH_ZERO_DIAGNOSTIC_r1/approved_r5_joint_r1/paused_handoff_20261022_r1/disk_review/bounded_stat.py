import os,json,time,stat,subprocess
from pathlib import Path
out=Path('/tmp/e2_r5_space_delta_readonly_r1');initial=json.load(open(out/'INITIAL.json'));cutoff=1792681454;limit=20000;seen_global=set();items=0
def statwalk(root):
 global items
 stack=[Path(root)];rows=[];errors=[];seen=set();total=recent=0;files=0
 while stack:
  p=stack.pop();items+=1
  if items>limit:errors.append('GLOBAL20000ENTRY_CAP');break
  try:s=p.lstat()
  except OSError as e:errors.append(str(e));continue
  if stat.S_ISLNK(s.st_mode):continue
  key=(s.st_dev,s.st_ino);fresh=key not in seen
  if fresh:seen.add(key);total+=s.st_blocks*512
  if s.st_mtime>=cutoff and fresh:recent+=s.st_blocks*512
  if stat.S_ISDIR(s.st_mode):
   try:stack.extend(p.iterdir())
   except OSError as e:errors.append(str(e))
  elif stat.S_ISREG(s.st_mode):
   files+=1
   if s.st_blocks*512>=1024*1024 or s.st_mtime>=cutoff:rows.append({'path':str(p),'bytes':s.st_size,'allocated':s.st_blocks*512,'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'mtime':s.st_mtime,'ctime':s.st_ctime,'mtime_local':time.strftime('%m-%d %H:%M:%S',time.localtime(s.st_mtime)),'recent_after_activation_commit_mtime':s.st_mtime>=cutoff})
 return {'root':str(root),'unique_allocated_bytes':total,'after_cutoff_mtime_allocated_bytes':recent,'file_count':files,'top_or_recent_files':sorted(rows,key=lambda x:x['allocated'],reverse=True),'errors':errors}
roots=[x['path'] for x in initial['tmp_top_level_r5'] if x.get('kind')=='dir'];roots+=['/workspace/build/ep-l2-ms20261022-e2-tagpressure-observer-r5']
rows=[statwalk(r) for r in roots]
# /proc fd links only, bounded no target file body; maps lines only for deleted mappings.
deleted=[];pids=0;fds=0;maps_bytes=0;errors=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 pids+=1
 if pids>512:errors.append('PID512CAP');break
 try:links=list((proc/'fd').iterdir())
 except OSError:continue
 for fd in links:
  fds+=1
  if fds>20000:errors.append('FD20000CAP');break
  try:
   target=os.readlink(fd)
   if target.endswith(' (deleted)'):
    s=fd.stat();deleted.append({'pid':int(proc.name),'fd':fd.name,'target':target,'bytes':s.st_size,'allocated':s.st_blocks*512,'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'comm':(proc/'comm').read_text().strip()})
  except OSError:pass
 try:
  b=(proc/'maps').read_bytes();maps_bytes+=len(b)
  if maps_bytes>4*2**20:errors.append('MAPS4MIBCAP');break
  for line in b.decode(errors='replace').splitlines():
   if '(deleted)' in line:deleted.append({'pid':int(proc.name),'map_line':line,'comm':(proc/'comm').read_text().strip(),'allocated':'UNKNOWN_MAP_NO_FD'})
 except OSError:pass
r={'activation_commit_time_cutoff':cutoff,'activation_cutoff_local':time.strftime('%m-%d %H:%M:%S',time.localtime(cutoff)),'note':'mtime after cutoff is supporting metadata only, not complete proof of allocation delta; no prior allocated snapshot for all paths','scope_entries_statted':items,'walks':sorted(rows,key=lambda x:x['unique_allocated_bytes'],reverse=True),'deleted_open_or_maps':deleted,'proc_scan':{'pids':pids,'fds':fds,'maps_bytes':maps_bytes,'errors':errors}};(out/'BOUNDED_STAT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'cutoff':r['activation_cutoff_local'],'statted':items,'walk_top':[(x['root'],x['unique_allocated_bytes'],x['after_cutoff_mtime_allocated_bytes']) for x in r['walks'][:15]],'recentlarge':[[x for x in w['top_or_recent_files'] if x['allocated']>2**20 and x['recent_after_activation_commit_mtime']]for w in r['walks'] if w['after_cutoff_mtime_allocated_bytes']>2**20],'deleted':deleted,'proc':r['proc_scan']},indent=2))
