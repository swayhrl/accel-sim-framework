#!/usr/bin/env python3
"""Finite EP-MAIN workload metadata inventory; no trace bodies or model launch."""
from pathlib import Path
import json,hashlib,subprocess,csv,io,datetime,base64,shlex,sys,os
W=Path('/root/data/ep_l2_main_20261023_v1/worktree')
O=W/'docs/ep_l2/operations/ep_main_workload_inventory_20261024_v1'
O.mkdir(exist_ok=True)
(O/'evidence').mkdir(exist_ok=True)
G='/root/data/ep_l2_main_20261023_v1/repo.git'
E='7c2f830175f40e16651eab4a3cd3a7af73e9927b';D='0d8fec555d9ec8582404fe17b6eae06922dc8a95';F='ab8e04dce031aee26e9f92e1b9cebe88fd9f8c2f';C='ef6d9127eb4882229efc561d832a5985780cea60'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):(O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
reqs=[
('legacy_roster.csv',E,'docs/ep_l2/review_packs/FT20261016_LANE5_TOOLING_r1/WORKLOAD_ROSTER.csv'),
('local_coverage.json',D,'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/E_workload_research/LOCAL_COVERAGE_INVENTORY.json'),
('rodinia_metadata.json',D,'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/RODINIA_LOCAL_METADATA.json'),
('candidate_shortlist.csv',D,'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/CANDIDATE_SHORTLIST.csv'),
('exclusions.json',D,'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/EXCLUSIONS_AND_HOLDS.json'),
('candidate_review.csv',D,'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/CANDIDATE_REVIEW.csv'),
('candidate_audit.json',D,'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/CANDIDATE_AUDIT.json'),
('existing_candidate_manifests.json',D,'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/EXISTING_CANDIDATE_MANIFESTS.json'),
('decision_readiness.csv',D,'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_DECISION_BUNDLE_r2/READINESS.csv'),
('bfs_input_packet.json',F,'docs/ep_l2/review_packs/MS20261021_F_BFS_INPUT_PACKET_r1/INPUT_PACKET.json'),
('bfs_missing_historical.json',F,'docs/ep_l2/review_packs/MS20261021_F_BFS_INPUT_PACKET_r1/MISSING.json'),
('bfs_C_dependency_update.json',F,'docs/ep_l2/lane_collaboration_v1/state/F/BFS_C_DEPENDENCY_UPDATE_r1.json'),
('bfs_C_host_boundaries.json',C,'docs/ep_l2/review_packs/MS20261021_C_SGEMM_FALLBACK_BFS_HOST_r1/BFS_HOST_BOUNDARIES.json'),
('bfs_C_missing.json',C,'docs/ep_l2/review_packs/MS20261021_C_SGEMM_FALLBACK_BFS_HOST_r1/MISSING.json'),
('primary_source_survey.md',E,'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/workload_research_r1/PRIMARY_SOURCE_WORKLOAD_SURVEY.md')]
fallback={x['dest']:x for x in json.loads((O/'remaining_meta.json').read_text())}
refs=[]
for dest,commit,path in reqs:
 if dest in fallback:data=fallback[dest]['content'].encode()
 elif (O/'evidence'/dest).exists():data=(O/'evidence'/dest).read_bytes()
 else:data=subprocess.check_output(['git','--git-dir='+G,'-c','http.curloptResolve=github.com:443:140.82.112.3','show',commit+':'+path],timeout=40)
 p=O/'evidence'/dest;p.write_bytes(data)
 tree=subprocess.check_output(['git','--git-dir='+G,'ls-tree',commit,'--',path],text=True).split()[2]
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==tree
 refs.append({'commit':commit,'path':path,'git_blob_sha':tree,'sha256':sha(p),'bytes':len(data),'local_path':'evidence/'+dest})
put('SOURCE_REFERENCES.json',refs)
roster=list(csv.DictReader((O/'evidence/legacy_roster.csv').open()))
rod=json.loads((O/'evidence/rodinia_metadata.json').read_text())['inputs']
entries=[x['trace_list'] for x in roster]+[x['entry'] for x in rod]
assert len(set(entries))==18
# Read only the eighteen exact commandlists and adjacent existing run.sh files.
# Derive member paths from commandlist bytes, never enumerate directories/bodies.
source_code=r"""
import os,json,pathlib,hashlib,stat,datetime
P=pathlib.Path
assert os.uname().nodename=='huangrulin-174'
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
def ident(s):return {'dev':s.st_dev,'inode':s.st_ino,'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'mode':stat.S_IMODE(s.st_mode)}
def readsmall(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0))
 with os.fdopen(fd,'rb') as f:
  before=ident(os.fstat(f.fileno()));assert before['bytes']<=65536
  data=f.read(65537);assert before==ident(os.fstat(f.fileno()))==ident(p.stat())
 return data,before
out=[]
for entry in ENTRIES:
 p=P(entry);assert entry.startswith('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/') and p.name=='kernelslist.g' and '..' not in p.parts
 row={'entry':entry,'exists':p.exists(),'readable':os.access(p,os.R_OK)}
 if p.exists():
  data,s=readsmall(p);row.update(commandlist=data.decode(),commandlist_sha256=hashlib.sha256(data).hexdigest(),entry_stat=s)
  files=[];order=[];commands=[]
  for line in data.decode().splitlines():
   name=line.strip()
   if not name or name.startswith('#'):continue
   if name.startswith('Memcpy'):
    commands.append(name);continue
   q=pathlib.PurePosixPath(name);assert not q.is_absolute() and '..' not in q.parts and len(q.parts)==1
   order.append(name)
  for name in dict.fromkeys(order):
   q=p.parent/name
   try:
    s=q.stat();files.append({'path':str(q),'name':name,'exists':True,'readable':os.access(q,os.R_OK),'stat':ident(s),'content_read_or_rehashed':False})
   except FileNotFoundError:files.append({'path':str(q),'name':name,'exists':False,'readable':False,'content_read_or_rehashed':False})
  row.update(kernel_order=order,kernel_launches=len(order),unique_kernel_files=len(files),members=files,memcpy_commands=commands,all_bodies_metadata_present=all(f['exists'] and f['readable'] for f in files),body_logical_bytes=sum(f.get('stat',{}).get('bytes',0) for f in files))
  run=p.parent.parent/'run.sh';row['capture_script_path']=str(run)
  if run.is_file():
   b,st=readsmall(run);row.update(capture_script=b.decode(errors='replace'),capture_script_sha256=hashlib.sha256(b).hexdigest(),capture_script_stat=st)
 out.append(row)
print(json.dumps({'schema':'EP_MAIN_EXACT_18_INPUT_READONLY_METADATA_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_host':os.uname().nodename,'source_namespace':os.readlink('/proc/self/ns/mnt'),'inputs':out,'trace_body_bytes_read':0,'source_new_files':0,'simulator_or_compiler_invocations':0,'source_mutations':0}))
"""
source_code="ENTRIES="+repr(entries)+"\n"+source_code
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_management_20261023_v1/tools')
import manage
cp=subprocess.run(manage.SSH+['python3 -B -c '+shlex.quote(source_code)],capture_output=True,timeout=60)
if cp.returncode:raise RuntimeError(cp.stderr.decode(errors='replace'))
observed=json.loads(cp.stdout);put('SOURCE_CURRENT_EXACT_METADATA.json',observed)
old_status=manage.status('EP_L2');assert old_status['data']['actual_starts']==57
put('OLD_EP_STATUS_READONLY.json',old_status)
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools');import native_v2
put('NATIVE_CURRENT_EXACT_ASSETS.json',native_v2.current_assets(['EP_VECTORADD_S','DTC_AD_GEMM']))
n=Path('/root/data/ep_l2_dtc_l1_native_v2')
put('PROTECTED_PREIMAGE_SHA256.json',{str(p):sha(p) for p in [n/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',n/'control/CURRENT_SCIENCE_EPOCH.json',next((n/'control/source_historical_preimages').glob('EP_REGISTRY_*')),n/'tools/native_v2.py',n/'bin/native']})
print(json.dumps({'source_refs':len(refs),'exact_input_variants':len(entries),'currently_complete_by_metadata':sum(x.get('all_bodies_metadata_present',False) for x in observed['inputs']),'declared_kernel_files':sum(x.get('unique_kernel_files',0) for x in observed['inputs']),'body_bytes_read':0,'output':str(O)},ensure_ascii=False))
