import os,json,subprocess,hashlib,re,glob,time
O=os.path.dirname(os.path.abspath(__file__)); fw='/workspace/repos/accel-sim-framework'; rev='dc2f32bf28c85fded91beead53a2a3fd650de202'; pre='docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261018_storageops_v9_target_01/'
idx=json.load(open(O+'/V9_COLD_ARCHIVE_AND_RESTORE_INDEX.json')); out=[]
for p in idx['projects']:
 rows=[json.loads(l) for l in subprocess.check_output(['git','-C',fw,'show',rev+':'+pre+'SOURCE_'+p['project']+'_COPY_READY_FILES_V9.jsonl']).splitlines()]; good=0; mismatch=[]
 for r in rows:
  try:
   s=os.lstat(r['source_path']); actual=dict(dev=s.st_dev,inode=s.st_ino,size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,allocated_bytes=s.st_blocks*512,mode_octal=oct(s.st_mode&0o7777)); bad={k:[r[k],v] for k,v in actual.items() if k in r and r[k]!=v}
   if bad: mismatch.append(dict(path=r['source_path'],mismatches=bad))
   else: good+=1
  except OSError as e: mismatch.append(dict(path=r['source_path'],error=str(e)))
 s=os.lstat(p['original_root']); out.append(dict(project=p['project'],root=p['original_root'],current_root_device=s.st_dev,current_root_inode=s.st_ino,prior_root_inode=p['source_root_inode'],prior_root_identity_matches=s.st_ino==p['source_root_inode'] and s.st_dev==p['source_root_device'],file_count=len(rows),metadata_matches=good,mismatches=mismatch,content_rehashed=False,restore_receipt=p['restore_receipt'],selector_sha256=p['selector_sha256'],manifest_sha256=p['canonical_archive_manifest_sha256'],native164_archive_tree=p['native164_archive_tree'],native_metadata_scope=p['native_metadata_scope'],release_authority='NOT_GRANTED'))
json.dump(out,open(O+'/SOURCE_V9_CURRENT_METADATA_JOIN.json','w'),indent=2); print(json.dumps(out,indent=2)[:7000])
# Scheduler outputs remain digests and explicit local paths only, never raw commands.
sched=[]
for cmd in [['crontab','-l'],['systemctl','list-timers','--all','--no-pager'],['tmux','list-sessions','-F','#{session_id} #{session_name} #{session_windows}']]:
 try:
  r=subprocess.run(cmd,capture_output=True,timeout=4); b=r.stdout+r.stderr; sched.append(dict(command=cmd,returncode=r.returncode,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),local_paths=sorted(set(re.findall(rb'/(?:workspace|tmp)/[A-Za-z0-9_./+@:=,~-]+',b)))[0:80] if False else sorted(set(s.decode() for s in re.findall(rb'/(?:workspace|tmp)/[A-Za-z0-9_./+@:=,~-]+',b))),empty_stdout=not r.stdout))
 except (OSError,subprocess.TimeoutExpired) as e: sched.append(dict(command=cmd,error=type(e).__name__))
for p in glob.glob('/etc/cron*/*')+['/etc/crontab']:
 if os.path.isfile(p):
  b=open(p,'rb').read(262144); sched.append(dict(path=p,sha256=hashlib.sha256(b).hexdigest(),local_paths=sorted(set(s.decode() for s in re.findall(rb'/(?:workspace|tmp)/[A-Za-z0-9_./+@:=,~-]+',b)))))
json.dump(dict(at_epoch=time.time(),probes=sched,coverage='Bounded local scheduler discovery; absence is not proof of no remote/planned consumers'),open(O+'/SOURCE_SCHEDULED_CONSUMER_PROBE.json','w'),indent=2)
