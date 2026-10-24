"""Rebuild only unpublished metadata integration in an isolated full index."""
from pathlib import Path
import subprocess,os,hashlib,json,shutil,time
W=Path('/root/data/ep_l2_main_20261023_v1/worktree');R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
REPAIR=Path('/root/data/ep_main_git_metadata_repair_20261024_v1');A=R/'control/GIT_METADATA_REPAIR';A.mkdir(parents=True,exist_ok=True)
OLD='85d98acabd6915c7cd62d5c57f7aa10b826c1fcf';BASE='cdbf3ae';SOURCE='72a5037fff37a2a7e5180c104e5cc59d3ff8ed48'
BRANCH='refs/heads/hrl/ep-l2-main-native-174new-20261023-v1'
def run(where,*args,input=None,check=True):
 p=subprocess.run(['git','-C',str(where),'-c','core.sparseCheckout=false','-c','index.sparse=false',*args],input=input,capture_output=True)
 if check:assert p.returncode==0,(args,p.stderr.decode(errors='replace')[-2000:])
 return p
def out(where,*args):return run(where,*args).stdout
assert out(W,'rev-parse','HEAD').decode().strip()==OLD
assert not out(W,'status','--porcelain=v1'),'primary has unstaged work; preserve and inspect before metadata repair'
common=Path(out(W,'rev-parse','--git-common-dir').decode().strip());common=common if common.is_absolute() else (W/common).resolve()
index=Path(out(W,'rev-parse','--git-path','index').decode().strip());index=index if index.is_absolute() else (W/index).resolve()
index_raw=index.read_bytes();(A/'PRIMARY_INDEX_BEFORE').write_bytes(index_raw)
cfg={}
for key in ['core.sparseCheckout','core.sparseCheckoutCone','index.sparse','core.ignorecase','core.bare','extensions.worktreeConfig']:
 cfg[key]=run(W,'config','--get',key,check=False).stdout.decode().strip()
version=out(W,'--version').decode().strip()
run(W,'update-ref','refs/ep_l2/forensics/unpublished_sparse_integration_20261024_v1',OLD)
run(W,'-c','pack.useBitmaps=false','bundle','create',str(A/'ORIGINAL_UNPUBLISHED.bundle'),BASE+'..HEAD')

# Preserve all path/blob/mode observations, including repeated equal entries.
def leaves(where,rev):
 rows=out(where,'ls-tree','-r','-z','--full-tree',rev).split(b'\0');result={};duplicates=[]
 for row in rows:
  if not row:continue
  header,name=row.split(b'\t',1);mode,kind,oid=header.split();value=(mode.decode(),kind.decode(),oid.decode())
  if name in result:assert result[name]==value,('DIFFERENT_BLOBS_AT_DUPLICATE_PATH',name);duplicates.append(name.decode())
  result[name]=value
 return result,duplicates
before,duplicates=leaves(W,OLD)
assert not REPAIR.exists(),'use a new absent repair namespace; do not reset previous repair evidence'
REPAIR.mkdir();run(REPAIR,'init')
run(REPAIR,'config','core.sparseCheckout','false');run(REPAIR,'config','index.sparse','false');run(REPAIR,'config','core.ignorecase','false')
for key in ['user.name','user.email']:
 value=run(W,'config','--get',key).stdout.decode().strip();assert value;run(REPAIR,'config',key,value)
(REPAIR/'.git/objects/info/alternates').write_text(str(common/'objects')+'\n')
run(REPAIR,'checkout','--detach',BASE)
p=run(REPAIR,'cherry-pick',SOURCE);print(p.stdout.decode().splitlines()[0],flush=True)
source_reintegrated=out(REPAIR,'rev-parse','HEAD').decode().strip()
prefixes=['util/ep_l2/shared_trace_library_20261024_v1','docs/ep_l2/operations/shared_sm70_trace_library_20261024_v1']
selected={name:value for name,value in before.items() if any(name.decode().startswith(prefix+'/') for prefix in prefixes)}
for prefix in prefixes:
 directory=REPAIR/prefix
 if directory.exists():
  for p in directory.rglob('*'):
   if p.is_file() or p.is_symlink():
    rel=p.relative_to(REPAIR).as_posix().encode()
    if rel not in selected:p.unlink()
for name,(mode,kind,oid) in selected.items():
 assert kind=='blob' and mode in ['100644','100755'],'owned metadata namespace must contain ordinary files'
 p=REPAIR/name.decode();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(out(W,'cat-file','blob',oid));p.chmod(0o755 if mode=='100755' else 0o644)
run(REPAIR,'add','--',*prefixes);run(REPAIR,'diff','--cached','--check')
p=run(REPAIR,'commit','-m','Reapply qualified IO and parent evidence through a canonical full index');print(p.stdout.decode().splitlines()[0],flush=True)
fixed=out(REPAIR,'rev-parse','HEAD').decode().strip();after,after_duplicates=leaves(REPAIR,fixed)
assert not after_duplicates and before==after,'repair must preserve every original unique path/mode/blob exactly'
def fingerprint(rows):return hashlib.sha256(b'\n'.join(name+b'\t'+(' '.join(rows[name])).encode() for name in sorted(rows))).hexdigest()
assert fingerprint(before)==fingerprint(after)

# Transfer only the new canonical objects to the shared store. The old objects
# and branch history remain retained under the forensic ref and bundle.
run(W,'fetch',str(REPAIR),fixed+':refs/ep_l2/forensics/canonical_repair_candidate_20261024_v1')
assert out(W,'rev-parse','HEAD').decode().strip()==OLD and index.read_bytes()==index_raw,'primary changed during repair'
temp_index=A/'CANONICAL_FULL_INDEX'
env=dict(os.environ,GIT_INDEX_FILE=str(temp_index))
def temp_git(*args,input=None):
 p=subprocess.run(['git','-C',str(W),'-c','core.sparseCheckout=false','-c','index.sparse=false',*args],input=input,env=env,capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
temp_git('read-tree',fixed)
missing=[name for name in after if not os.path.lexists(W/name.decode())]
if missing:temp_git('update-index','--skip-worktree','-z','--stdin',input=b'\0'.join(missing)+b'\0')
assert temp_git('write-tree').strip()==out(REPAIR,'rev-parse',fixed+'^{tree}').strip()
index_lock=index.with_name(index.name+'.lock');fd=os.open(index_lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
try:
 with os.fdopen(fd,'wb') as f:f.write(temp_index.read_bytes());f.flush();os.fsync(f.fileno())
 run(W,'update-ref',BRANCH,fixed,OLD)
 os.replace(index_lock,index)
finally:
 if index_lock.exists():index_lock.unlink()
assert not out(W,'status','--porcelain=v1'),'canonical metadata switch unexpectedly changed working files'
proof={'status':'CANONICAL_FULL_INDEX_REBUILD_IDENTICAL_UNIQUE_BLOBS','git_version':version,'primary_sparse_configuration':cfg,'original_unpublished_head':OLD,'original_source_commit':SOURCE,'valid_base':out(W,'rev-parse',BASE).decode().strip(),'corrected_source_integration_commit':source_reintegrated,'corrected_head':fixed,'unique_file_paths':len(before),'duplicate_equal_paths_in_original':duplicates,'before_unique_path_mode_blob_sha256':fingerprint(before),'after_unique_path_mode_blob_sha256':fingerprint(after),'working_file_or_scientific_payload_bytes_changed':0,'consumed_scientific_specs_and_old_commits_changed':False,'forensic_ref':'refs/ep_l2/forensics/unpublished_sparse_integration_20261024_v1','original_bundle':str(A/'ORIGINAL_UNPUBLISHED.bundle'),'primary_original_index_sha256':hashlib.sha256(index_raw).hexdigest(),'verification_pending':'isolated reachable-only clone strict fsck before GitHub publication','observed_unix':time.time()}
(A/'REPAIR_RESULT.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
