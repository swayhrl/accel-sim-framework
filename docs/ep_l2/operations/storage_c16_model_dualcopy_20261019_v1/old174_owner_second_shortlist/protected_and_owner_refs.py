import subprocess,json,re,hashlib,os
from pathlib import Path
O=Path(__file__).parent; repos=['accel-sim-ep-l2-ms20261019-a-runtime-v1','accel-sim-ep-l2-ms20261019-b-victim-v1','accel-sim-ep-l2-ms20261019-c-ro-v1','accel-sim-ep-l2-ms20261019-d-analysis-v1','accel-sim-ep-l2-ms20261019-e-eval-v1','accel-sim-decoupled-l1-fast64','accel-sim-vm-llm-m4b-c4-analysis-20260907','accel-sim-vm-m4b-speculative','accel-sim-vm-m4b-c13-diagnostics','accel-sim-l2-resource-char','accel-sim-frc-v1','accel-sim-latebind-mvp-v1']
patterns=['/workspace/c16_assets','/workspace/c16_exchange','m4c-c4-early-export-20260907-v1','m4c-c4-final-inputs-20260908-v3','m4c-c4-final-inputs-20260908-v2','/workspace/vm-m4b-speculative','/workspace/vm-m4b-c13-diagnostics','/workspace/m4c-c3-formal-20260905-v1','l2_char_v1/round1_formal_32f9b8d5','frc_core','latebind-mvp-v1/results']
results=[]
for name in repos:
 repo='/workspace/worktrees/'+name
 if not os.path.isdir(repo):results.append(dict(repo=repo,error='ABSENT'));continue
 head=subprocess.check_output(['git','-C',repo,'rev-parse','HEAD']).decode().strip();protected='ms20261019' in name or 'fast64' in name
 dirs=['docs/ep_l2','util/ep_l2','configs','experiments','scripts'] if 'ms20261019' in name else (['docs/dtc_l1','util/dtc_l1','configs'] if 'fast64' in name else ['docs','util','configs','scripts','experiments'])
 try:
  r=subprocess.run(['git','-C',repo,'grep','-l','-I','-E','|'.join(re.escape(p) for p in patterns),head,'--',*dirs],capture_output=True,text=True,timeout=5);files=[l.split(':',1)[1] for l in r.stdout.splitlines()];hits=[]
  for p in files[:28]:
   b=subprocess.check_output(['git','-C',repo,'show',head+':'+p])
   if len(b)>512000:continue
   lines=b.decode(errors='replace').splitlines();ms=[]
   for i,l in enumerate(lines):
    found=[p for p in patterns if p in l]
    if found:ms.append(dict(line=i+1,patterns=found,excerpt=l[:450]))
   hits.append(dict(path=p,blob_sha256=hashlib.sha256(b).hexdigest(),matches=ms[:10]))
  results.append(dict(repo=repo,head=head,protected=protected,matching_files=len(files),matches=hits,truncated=len(files)>28,working_and_remote_future_clearance=False));print(name,head[:12],len(files),'matches')
 except subprocess.TimeoutExpired:results.append(dict(repo=repo,head=head,protected=protected,status='BOUNDED_SEARCH_TIMEOUT_HOLD'))
(O/'protected_and_owner_reference_join.json').write_text(json.dumps(dict(patterns=patterns,scope='Tracked immutable HEAD in original174 working namespace only; no match is not untracked/remote future clearance',repositories=results),indent=2)+'\n')
