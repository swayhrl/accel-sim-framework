"""Root-review metadata snapshot/closure helper. No registry/controller writer.
No function runs by import. Candidate closure is never accepted automatically.
"""
import hashlib,json,os,re,stat,subprocess,tempfile
from pathlib import Path
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
OUTPUT=Path('/workspace/ep_l2_ms20261019_e_results')
ACCOUNT=OUTPUT/'E2_R5_IMMUTABLE_PUBLICATION_METADATA_ACCOUNTING_r1'
REGISTRY=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
FIELD='mechanism_study_20261019_v1';BATCH='tagpressure_observer_successor_batch';CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1';LIMIT=640*2**20;TOTAL=640*2**20

def require(ok,message):
 if not ok:raise ValueError(message)
def unique(pairs):
 d={}
 for k,v in pairs:require(k not in d,'duplicate JSON key');d[k]=v
 return d
def body(path):
 p=Path(path);s=p.lstat();require(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_size<=LIMIT,'bounded regular metadata only');return p.read_bytes()
def ref(path):b=body(path);return {'path':str(Path(path).resolve()),'sha256':hashlib.sha256(b).hexdigest()}
def read(r):require(ref(r['path'])['sha256']==r['sha256'],'exact metadata SHA changed');return json.loads(body(r['path']),object_pairs_hook=unique)
def allocated_unique(paths):
 seen=set();allocated=logical=0;rows=[]
 for path in paths:
  p=Path(path);s=p.lstat();require(stat.S_ISREG(s.st_mode) and not p.is_symlink(),'only regular metadata files');key=(s.st_dev,s.st_ino);fresh=key not in seen
  if fresh:seen.add(key);allocated+=s.st_blocks*512;logical+=s.st_size
  rows.append({'path':str(p),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'bytes':s.st_size,'allocated_bytes':s.st_blocks*512,'counted_unique':fresh})
 return {'allocated_bytes_unique_dev_inode':allocated,'logical_bytes_unique_dev_inode':logical,'unique_inode_count':len(seen),'files':rows}
def fsync_dir(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def create_immutable(path,data):
 """Never links a mutable source inode and never overwrites prior versions."""
 path=Path(path)
 if path.exists():require(body(path)==data,'immutable metadata collision/change');return False
 fd,tmp=tempfile.mkstemp(prefix='.snapshot-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
  try:os.link(tmp,path)  # O_EXCL-like install, preserving a concurrent prior body.
  except FileExistsError:require(body(path)==data,'immutable metadata race differs')
  fsync_dir(path.parent)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 return True

def verified_publication(request):
 rb=read(request['publication_remote_readback_ref']);commit=request['publication_commit']
 require(re.fullmatch('[0-9a-f]{40}',commit) and rb.get('remote_commit')==commit and rb.get('verified') is True,'root actual remote readback with verified=true required')
 verified=set(rb['verified_paths']);require(len(request['metadata_refs'])>0,'explicit complete resultmetadata file list required')
 rows=[];total=0
 for r in request['metadata_refs']:
  p=Path(r['path']).resolve();require(p.is_relative_to(E),'published resultmetadata must belong to original E tree');rel=str(p.relative_to(E));require(rel in verified,'metadata absent from actual remote verified paths')
  b=body(p);require(hashlib.sha256(b).hexdigest()==r['sha256'],'published metadata body changed')
  # Read only the exact small committed blob. No tree scan/fetch/large raw.
  size=int(subprocess.check_output(['git','-C',str(E),'cat-file','-s',commit+':'+rel],text=True));require(size<=LIMIT,'published metadata blob cap')
  blob=subprocess.check_output(['git','-C',str(E),'show',commit+':'+rel]);require(blob==b,'actual publication blob differs')
  require(p.suffix.lower() in {'.json','.csv','.md','.txt'},'metadata formats only; never raw/trace/ELF/source trees')
  if p.suffix=='.json':json.loads(b,object_pairs_hook=unique)
  total+=len(b);require(total<=TOTAL,'explicit metadata I/O scope exceeds640MiB batch forecast; root must independently review actualgeneration rather than silently omit bodies')
  rows.append((r,p.suffix.lower(),b))
 return rows

def snapshot_publication(request,immutable_store):
 """Root may execute only after review. Writes metadata versions, no central API.
 Existing accounting root retained; all versions are append-only. JSON remains
 JSON; explicit published CSV/MD/TXT may also be accounted without omission.
 """
 rows=verified_publication(request);store=Path(immutable_store).resolve();require(store.is_relative_to(E),'new immutable version store must be in original E resultpack')
 store.mkdir(parents=True,exist_ok=True);require(ACCOUNT.is_dir() and store.stat().st_dev==ACCOUNT.stat().st_dev==OUTPUT.stat().st_dev==Path('/workspace').stat().st_dev,'original same-device accounting roots only')
 require(request.get('root_complete_metadata_inventory_reviewed') is True,'root must review explicit full publication metadata inventory, not sample onlypoint')
 result=[]
 for original,suffix,b in rows:
  name=original['sha256']+suffix;version=store/name;target=ACCOUNT/name
  if target.exists():
   require(body(target)==b,'existing accounting content changed')
   if not version.exists():os.link(target,version);fsync_dir(store)
   else:require(body(version)==b,'existing immutable version changed')
  else:
   create_immutable(version,b);os.link(version,target);fsync_dir(ACCOUNT)
  require((version.stat().st_dev,version.stat().st_ino)==(target.stat().st_dev,target.stat().st_ino),'version/accounting must be actual hardlink aliases')
  # A preexisting same-content target may use a different immutable inode;
  # count actual OUTPUT targets, never assume matching contents share allocation.
  result.append({'published_ref':original,'immutable_version_ref':ref(version),'accounting_ref':ref(target),'publication_commit':request['publication_commit']})
 measured=allocated_unique([r['accounting_ref']['path'] for r in result])
 return {'schema':'E2_R5_ACCEPTED_POINT_IMMUTABLE_METADATA_SNAPSHOT_V1','status':'ACTUAL_METADATA_SNAPSHOTTED_IN_ORIGINAL_OUTPUT_NO_CLOSURE','attempt_id':request['attempt_id'],'publication_commit':request['publication_commit'],'publication_remote_readback_ref':request['publication_remote_readback_ref'],'records':result,'measurement':measured,'generation_accounting_method':'Original retained_tree_bytes sums actual logical file sizes in OUTPUT; allocated physical measurement separately deduplicates(device,inode). No generated body/version removed.','no_registry_or_controller_mutation':True}

def closure_candidate(request,snapshot_ref):
 """Read-only current accepted pointers + real accounted bodies -> UNSIGNED JSON.
 Root must independently sign, account final controlreceipts in OUTPUT, publish/
 readback then call original Coordinator.close_tagpressure_metadata itself.
 """
 snap=read(snapshot_ref);require(snap['attempt_id']==request['attempt_id'] and snap['publication_commit']==request['publication_commit'],'snapshot point/publication differs')
 verified_publication(request);require(snap['publication_remote_readback_ref']==request['publication_remote_readback_ref'],'snapshot remote proof differs')
 data=json.loads(REGISTRY.read_bytes());item=data[FIELD];require(item['campaign_id']==CAMPAIGN and item['t0_unix']==1792414193,'original campaign/T0')
 attempts=[a for a in item['attempts'][55:] if a['attempt_id']==request['attempt_id']];require(len(attempts)==1,'one actual exact tail attempt required');a=attempts[0]
 require(a['state']=='COMPLETE_VALID' and a['actual_start'] is True,'FAILED/unaccepted/notstarted cannot close metadata')
 accepted=item['accepted_results'][a['attempt_id']];ar={'path':accepted['path'],'sha256':accepted['sha256']};run=read(ar)
 require(run['status']=='COMPLETE_VALID' and run['independent_acceptance']=='PASS' and run['complete_input_verified'] is True,'true accepted complete-input receipt required')
 point=read(request['point_ref']);require(point['attempt_id']==a['attempt_id'] and point['status']=='CURRENT_ACCEPTED_DIAGNOSTIC_POINT' and point['endpoint_status']=='COMPLETE_VALID' and point['pair'] is False,'root independently accepted diagnosticpoint required')
 require(point['scientific_scope']=='TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1' and point['identity']==a['identity'] and point['qualification_id']==a['qualification_id'],'point exactnewscope/input/source/Q')
 require(point['actual_terminal_receipt']==accepted and point['independent_terminal_review']==request['independent_review_ref'],'root point exact accepted/independentreview refs')
 read(request['independent_review_ref'])  # Upstream independentacceptance remains authority.
 metadatarefs={r['published_ref']['sha256'] for r in snap['records']};require(request['point_ref']['sha256'] in metadatarefs and request['independent_review_ref']['sha256'] in metadatarefs,'full actual point/review must be accounted')
 paths=[]
 for r in snap['records']:
  account=Path(r['accounting_ref']['path']).resolve();require(account.parent==ACCOUNT and account.stat().st_dev==OUTPUT.stat().st_dev,'accounted body must be in original OUTPUT same device')
  require(ref(account)==r['accounting_ref'],'accounted immutable body changed');require(ref(r['immutable_version_ref']['path'])==r['immutable_version_ref'],'ownerimmutable version changed');paths.append(account)
 measured=allocated_unique(paths)
 fields=('path','device','inode','bytes','allocated_bytes','counted_unique')
 before={x['path']:{k:x[k] for k in fields} for x in snap['measurement']['files']}
 after={x['path']:{k:x[k] for k in fields} for x in measured['files']}
 require(before==after,'metadata device/inode/allocation changed since snapshot; nlink may increase with valid immutable aliases')
 manifest=read(item[BATCH]['manifest_ref']);require(point['source_identity']==manifest['source_identity'],'exact same releasednewbinary')
 return {'schema':'E2_R5_ENDPOINT_METADATA_PUBLICATION_CLOSED_V1','status':'ROOT_REVIEW_REQUIRED_METADATA_CLOSURE_CANDIDATE','campaign_id':CAMPAIGN,'condition_id':a['condition_id'],'source_identity':point['source_identity'],'attempt_id':a['attempt_id'],'accepted_result_ref':ar,'actual_metadata_allocated_bytes':measured['allocated_bytes_unique_dev_inode'],'metadata_allocation_scope':'Exact immutable published endpointmetadata bodies listed in snapshot; controlreceipt overhead must also be snapshotted/accounted before root calls close.','metadata_logical_bytes_unique':measured['logical_bytes_unique_dev_inode'],'metadata_snapshot_ref':snapshot_ref,'actual_generation_retained_in_accounting':True,'retired_remaining_forecast_bytes':160*2**20,'released_forecast_is_not_generated_result_refund':True,'immutable_publication_commit':request['publication_commit'],'publication_remote_readback_ref':request['publication_remote_readback_ref'],'root_signature_required':True,'actual_closure_or_registry_write_by_this_helper':False}
