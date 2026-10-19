import csv,json,os,stat,time,datetime,collections
from pathlib import Path
O=Path(__file__).parent
ledger=list(csv.DictReader(open(O/'census/SOURCE_COLD_CENSUS_ROOT_LEDGER.csv')))
# Frozen published named-root shortlist only; no top-level source re-enumeration.
paths=['/workspace/m4c-c4-early-export-20260907-v1','/workspace/vm-m4b-speculative','/workspace/vm-m4b-c13-diagnostics','/workspace/m4c-c3-formal-20260905-v1','/workspace/m4c-c4-final-inputs-20260908-v3','/workspace/m4c-c4-final-inputs-20260908-v2','/workspace/worktrees/accel-sim-l2-resource-char/hw_run','/workspace/worktrees/accel-sim-l2-resource-char/artifacts','/workspace/worktrees/accel-sim-frc-v1/hw_run','/workspace/worktrees/accel-sim-latebind-mvp-v1/hw_run','/tmp/v100-campaign-build2.jlh3pI','/tmp/m4c-native-export-test-20260905','/tmp/m4c-export-smoke-fP8Ns4','/tmp/tmp7lh43b0q']
prior={r['source_path']:r for r in ledger};rows=[];summ=[];start=time.monotonic();seen={};n=0
for root in paths:
 if not os.path.lexists(root):summ.append(dict(root=root,status='ABSENT',allocated_bytes_observed=0));continue
 s=os.lstat(root);counts=collections.Counter();stack=[(root,0)];complete=True;maxdepth=3;rootid=dict(device=s.st_dev,inode=s.st_ino,uid=s.st_uid,gid=s.st_gid);files=[]
 while stack:
  p,d=stack.pop()
  if n>=6000 or time.monotonic()-start>18:complete=False;counts['budget_unvisited']=len(stack)+1;break
  try:s=os.lstat(p)
  except OSError as e:complete=False;counts['errors']+=1;continue
  n+=1
  if s.st_dev!=rootid['device']:complete=False;counts['device_pruned']+=1;continue
  if stat.S_ISLNK(s.st_mode):counts['symlinks']+=1;continue
  a=s.st_blocks*512
  if stat.S_ISREG(s.st_mode) and s.st_nlink>1:
   ident=(s.st_dev,s.st_ino)
   if ident in seen:counts['shared_inode_bytes']+=a;a=0
   else:seen[ident]=p
  counts['allocated_bytes_observed']+=a;counts['logical_bytes_observed']+=s.st_size
  if stat.S_ISREG(s.st_mode):
   counts['files']+=1
   if s.st_size>=16*2**20:files.append(dict(path=p,size=s.st_size,allocated_bytes=a,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid))
  elif stat.S_ISDIR(s.st_mode):
   counts['dirs']+=1
   if os.path.basename(p)=='.git':complete=False;counts['git_pruned']+=1;continue
   if d==maxdepth:
    complete=False;counts['depth_boundary_dirs']+=1;continue
   try:stack.extend((e.path,d+1) for e in os.scandir(p))
   except OSError:complete=False;counts['errors']+=1
 summ.append(dict(root=root,**rootid,**dict(counts),complete_at_depth3=complete,historical_root_allocated_bytes=int(prior[root]['allocated_bytes']) if root in prior else None,status='HOLD_IDENTITY_PROVENANCE_READER_RESTORE_REQUIRED',source_role='OUTPUT_CANDIDATE_NOT_CLEANUP_AUTHORITY'));rows.extend(files)
(O/'second_bounded_metadata.json').write_text(json.dumps(dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),depth=3,entry_budget=6000,deadline_seconds=18,elapsed_seconds=time.monotonic()-start,entries=n,roots=summ,large_files=sorted(rows,key=lambda r:-r['allocated_bytes']),payload_hashes=0,protected_parent_trees_traversed=0),indent=2)+'\n')
for r in summ:print(f"{r.get('allocated_bytes_observed',0)/2**30:.3f} GiB depth_complete={r.get('complete_at_depth3')} {r['root']}")
print('entries',n,'seconds',time.monotonic()-start,'large_files',len(rows))
