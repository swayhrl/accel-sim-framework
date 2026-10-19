import subprocess,json,os,hashlib,re,time
O=os.path.dirname(os.path.abspath(__file__)); patterns=['decoupled-l2-extract','m5-trace-immutable','C16_GPU_PACKAGE_P2_168c9714','C16_GPU_PACKAGE_P3_168c9714','c16_exchange','c16_assets','c2p-polybench-full-20260821','tls-c2p-v100-20260822','decoupled-l2-pretraces']
repos=['/workspace/worktrees/accel-sim-decoupled-l2','/workspace/worktrees/accel-sim-decoupled-l1-fast64','/workspace/worktrees/accel-sim-vm-c16-g','/workspace/worktrees/accel-sim-vm-c16-p','/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1','/workspace/worktrees/accel-sim-c2p-cache','/workspace/worktrees/accel-sim-c2p-addr-observe']
out=[]
for repo in repos:
 if not os.path.isdir(repo): continue
 head=subprocess.run(['git','-C',repo,'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
 try:
  r=subprocess.run(['git','-C',repo,'grep','-l','-I','-E','|'.join(patterns),'HEAD','--','docs','util','scripts','configs','experiments'],capture_output=True,timeout=6,text=True); files=r.stdout.splitlines(); hits=[]
  for f in files[:60]:
   path=f.removeprefix('HEAD:'); b=subprocess.check_output(['git','-C',repo,'show','HEAD:'+path])
   if len(b)>1048576: continue
   text=b.decode(errors='replace'); hits.append(dict(file=path,blob_sha256=hashlib.sha256(b).hexdigest(),tokens=[p for p in patterns if p in text]))
  out.append(dict(repo=repo,head=head,matching_files_total=len(files),matches=hits,truncated=len(files)>60,git_grep_returncode=r.returncode))
 except subprocess.TimeoutExpired: out.append(dict(repo=repo,head=head,status='SEARCH_TIME_BUDGET_HOLD'))
json.dump(dict(at_epoch=time.time(),scope='Pinned tracked HEAD documents/configs/scripts only. Historical text references show dependency, not inactivity. Untracked and remote planned references remain HOLD.',repositories=out),open(O+'/SOURCE_TRACKED_REFERENCE_EVIDENCE.json','w'),indent=2)
for r in out: print(r['repo'],r.get('matching_files_total',r.get('status')))
