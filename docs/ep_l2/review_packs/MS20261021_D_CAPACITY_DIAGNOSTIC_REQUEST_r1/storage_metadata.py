"""Bounded metadata-only inventory of named EP-L2 roots; no raw/trace reads."""
import csv,datetime,fcntl,hashlib,json,os,re,stat,time
from pathlib import Path
from zoneinfo import ZoneInfo
OUT=Path(__file__).resolve().parent
NOW=time.time();CUT=NOW-48*3600;CAL=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).replace(hour=0,minute=0,second=0,microsecond=0).timestamp()-24*3600
roots=[('current_application_and_native_results',Path('/workspace/ep_l2_ms20261019_e_results')),('historical_potential_results',Path('/workspace/ep_l2_potential20261017_lane5_results')),('historical_fasttrack_results',Path('/workspace/results/ep_l2_ft20261016'))]
roots += [('current_mechanism_preparation',p) for p in sorted(Path('/workspace').glob('ep_l2_ms20261019_*')) if p.is_dir() and p.name!='ep_l2_ms20261019_e_results']
roots += [('current_mechanism_build',p) for p in sorted(Path('/workspace/build').glob('ep-l2-ms202610*')) if p.is_dir()]
roots += [('coordination',Path('/workspace/ep_l2_ft20261016_shared'))]
rows=[];details=[];errors=[]
for group,root in roots:
 seen=set();allocated=logical=count=recentalloc=recentlogical=calalloc=dirs=symlinks=0;sub={}
 for base,ds,fs in os.walk(root,followlinks=False):
  for name in ['.']+ds+fs:
   p=Path(base) if name=='.' else Path(base)/name
   try:s=p.lstat()
   except OSError as e:errors.append(dict(path=str(p),error=str(e)));continue
   inode=(s.st_dev,s.st_ino)
   if inode in seen:continue
   seen.add(inode);isfile=stat.S_ISREG(s.st_mode);isdir=stat.S_ISDIR(s.st_mode);issymlink=stat.S_ISLNK(s.st_mode)
   allocated+=s.st_blocks*512;logical+=s.st_size;count+=isfile;dirs+=isdir;symlinks+=issymlink
   if isfile:
    if s.st_mtime>=CUT:recentalloc+=s.st_blocks*512;recentlogical+=s.st_size
    if s.st_mtime>=CAL:calalloc+=s.st_blocks*512
    if group=='current_application_and_native_results':
     rel=p.relative_to(root);key=rel.parts[0] if len(rel.parts)>1 else 'ROOT_FILES';q=sub.setdefault(key,dict(path=str(root/key),allocated_file_bytes=0,logical_file_bytes=0,files=0,recent48h_allocated_file_bytes=0));q['allocated_file_bytes']+=s.st_blocks*512;q['logical_file_bytes']+=s.st_size;q['files']+=1;q['recent48h_allocated_file_bytes']+=(s.st_blocks*512 if s.st_mtime>=CUT else 0)
  # os.walk will visit child dirs again; inode dedup prevents repeated directory sizes.
 st=root.stat();v=os.statvfs(root)
 rows.append(dict(group=group,path=str(root),resolved_path=str(root.resolve()),st_dev=st.st_dev,allocated_bytes=allocated,allocated_GiB=allocated/2**30,logical_bytes=logical,regular_files=count,directories=dirs,symlinks=symlinks,last48h_modified_files_allocated_bytes=recentalloc,last48h_modified_files_logical_bytes=recentlogical,calendar_20_21_modified_files_allocated_bytes=calalloc,FS_available_bytes=v.f_bavail*v.f_frsize))
 details.extend(dict(root=str(root),**r) for r in sub.values())
fs=[]
for path in ['/workspace','/root/share']:
 s=os.stat(path);v=os.statvfs(path);fs.append(dict(path=path,resolved_path=str(Path(path).resolve()),st_dev=s.st_dev,total_bytes=v.f_blocks*v.f_frsize,free_available_bytes=v.f_bavail*v.f_frsize,free_available_GiB=v.f_bavail*v.f_frsize/2**30))
lock=Path('/workspace/ep_l2_ft20261016_shared/REGISTRY.lock');registry=lock.with_name('RUN_REGISTRY.json')
with lock.open() as f:
 fcntl.flock(f,fcntl.LOCK_SH);raw=registry.read_bytes();reg=json.loads(raw);m=reg['mechanism_study_20261019_v1']
state=dict(registry_sha256=hashlib.sha256(raw).hexdigest(),registry_mutated=False,actual_starts=m['actual_starts'],maximum=m['maximum_actual_starts'],remaining=m['remaining_start_capacity'],controller=m.get('controller'),start_deadline=m['no_new_full_application_after'],intake_deadline=m['result_intake_freeze'],workspace_disk_policy=m['workspace_disk_policy'],additional_results_max_bytes=m['additional_results_max_bytes'],old_plus_new_results_max_bytes=m['old_plus_new_results_max_bytes'],leases=reg.get('resource_leases'))
summary=dict(observed_BJT=datetime.datetime.fromtimestamp(NOW,ZoneInfo('Asia/Shanghai')).isoformat(),window48h_start_BJT=datetime.datetime.fromtimestamp(CUT,ZoneInfo('Asia/Shanghai')).isoformat(),calendar_window_start_BJT=datetime.datetime.fromtimestamp(CAL,ZoneInfo('Asia/Shanghai')).isoformat(),method='lstat only; allocated st_blocks*512; per-root inode dedup; symlinks not followed; no file contents read except own central state under shared lock',mtime_limit='Modified files current allocation, not exact historical allocation delta; no birthtime attribution or time-series growth reconstructed',scope='Named EP-L2 result/preparation/build/coordination roots only. Excludes traces, source/worktree/Git storage and other projects; shared ancestors not additive.',rows=rows,current_result_subdirectories=sorted(details,key=lambda x:-x['allocated_file_bytes']),filesystems=fs,errors=errors,central_state=state)
(OUT/'STORAGE_METADATA.json').write_text(json.dumps(summary,indent=2)+'\n')
with (OUT/'STORAGE_ROOTS.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps(dict(observed=summary['observed_BJT'],rows=rows,filesystems=fs,errors=errors),indent=2))
