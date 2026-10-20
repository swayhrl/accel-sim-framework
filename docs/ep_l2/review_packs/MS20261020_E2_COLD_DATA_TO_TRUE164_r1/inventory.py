"""Bounded read-only EP-L2 metadata census. Never hash payload or read traces."""
from pathlib import Path
import os,sys,json,time,stat,re,collections,hashlib,signal
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
START=time.monotonic();MAX_SECONDS=40;MAX_FILES=30000
signal.alarm(MAX_SECONDS)
BUILDS=[Path('/workspace/build')/n for n in ['ep-l2-potential20261017-lane1-all-data-r1','ep-l2-potential20261017-lane1-p2-r1','ep-l2-potential20261017-lane1-structure-r1','ep-l2-microopt20261018-lane1-v1']]
if len(sys.argv)>1 and sys.argv[1]=='r2':
 P=P/'r2';P.mkdir(exist_ok=True)
 BUILDS += [Path('/workspace/build')/n for n in ['ep-l2-ft20261017-lane1-r0-1-buildfix-r1','ep-l2-ft20261017-lane1-r0-1-buildfix-r2']]
RESULTS=[Path('/workspace/ep_l2_potential20261017_lane5_results'),Path('/workspace/results/ep_l2_ft20261016'),Path('/workspace/ep_l2_ms20261019_e_results')]
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');data=json.loads(REG.read_text());campaign=data['mechanism_study_20261019_v1'];assert campaign['actual_starts']==14 and campaign['controller']['state']=='STOPPED'
def write(name,value):
 (P/name).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
def meta(p):
 s=p.lstat();return dict(path=str(p),device=s.st_dev,device_major=os.major(s.st_dev),device_minor=os.minor(s.st_dev),inode=s.st_ino,nlink=s.st_nlink,mode=s.st_mode,size=s.st_size,allocated_bytes=s.st_blocks*512,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,symlink_target=os.readlink(p) if stat.S_ISLNK(s.st_mode) else None)
def inside(path,root):return path==str(root) or path.startswith(str(root)+'/')
# Metadata-only file listing; no walk of input trace/source trees.
entries=[];directories=[]
for root in BUILDS+RESULTS:
 for parent,dirs,files in os.walk(root,followlinks=False):
  directories.append(meta(Path(parent)))
  for name in files:
   assert time.monotonic()-START<MAX_SECONDS and len(entries)<MAX_FILES,'bounded census limit reached'
   entries.append(meta(Path(parent)/name))
write('FILE_METADATA.json',entries);write('DIRECTORY_METADATA.json',directories)
# All process FD/map/cwd/exe/argument checks. Only EP-L2 matches are retained.
readers=[];errors=[];observed=0;vanished=0
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 pid=int(process.name);observed+=1
 try:
  links=[]
  for which in ['cwd','exe']:
   try:links.append((which,os.readlink(process/which)))
   except FileNotFoundError:pass
  for fd in (process/'fd').iterdir():
   try:links.append(('fd:'+fd.name,os.readlink(fd)))
   except FileNotFoundError:pass
  for kind,target in links:
   if any(inside(target.removesuffix(' (deleted)'),r) for r in BUILDS+RESULTS):readers.append(dict(pid=pid,kind=kind,target=target))
  maps=(process/'maps').read_text()
  for line in maps.splitlines():
   if any(str(r) in line for r in BUILDS+RESULTS):readers.append(dict(pid=pid,kind='mmap',target=line.split(maxsplit=5)[-1]))
  args=(process/'cmdline').read_bytes().split(b'\0')
  for arg in args:
   v=arg.decode(errors='replace')
   if v.startswith('/workspace/') and any(inside(v,r) for r in BUILDS+RESULTS):readers.append(dict(pid=pid,kind='argv_path',target=v))
 except (FileNotFoundError,ProcessLookupError):vanished+=1
 except PermissionError as e:errors.append(dict(pid=pid,kind='permission',path=str(e.filename)))
write('READER_SNAPSHOT.json',dict(at_unix=time.time(),processes_observed=observed,vanished_during_snapshot=vanished,permission_gaps=errors,matches=readers,scope='FD + mmap + cwd + exe + absolute argv; snapshot only, repeat under source quiescence before sealing/copy/release. No environment or unrelated project content retained.'))
# Current authorised runtime/config/input/acceptance path closure. Historical
# citations are separate from an actual scheduled or current reader dependency.
seeds=[REG,Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json'),Path('/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/CLIENT_CONTRACT.json')]
roll=ROOT/'docs/ep_l2/review_packs/MS20261020_E2_MAIN_ROLLING_r1'
seeds += list(roll.glob('*.json'))
for row in campaign['qualifications'].values():seeds.append(Path(row['path']))
for row in campaign['accepted_results'].values():seeds.append(Path(row['path']))
for path in (ROOT/'util/ep_l2/mechanism_e').glob('*.py'):seeds.append(path)
queue=collections.deque(seeds);visited=set();live_paths=set();references=[];skipped=[];text_bytes=0
while queue:
 p=queue.popleft();key=str(p)
 if key in visited:continue
 visited.add(key)
 if not p.is_file() or p.is_symlink():continue
 if p.suffix not in ['.json','.py','.md','.config','.yaml','.yml']:continue
 if p.stat().st_size>2*2**20:skipped.append(dict(path=key,reason='metadata file over2MiB bound'));continue
 text_bytes+=p.stat().st_size
 if text_bytes>64*2**20 or len(visited)>3000:raise RuntimeError('current-dependency metadata bound reached')
 text=p.read_text(errors='replace')
 for value in re.findall(r'/workspace/[A-Za-z0-9_./+,:=@%~ -]+',text):
  # JSON paths are quoted; split whitespace only for non-existing command text.
  v=value.rstrip(' .,;:')
  if not Path(v).exists():v=v.split()[0]
  if not Path(v).exists():continue
  live_paths.add(v)
  if any(inside(v,r) for r in BUILDS):references.append(dict(metadata=key,target=v))
  if Path(v).suffix=='.json':queue.append(Path(v))
write('CURRENT_PATH_DEPENDENCY_PROBE.json',dict(at_unix=time.time(),seeds=[str(x) for x in seeds],metadata_files=len(visited),metadata_bytes=text_bytes,payloads_hashed=0,trace_bodies_read=0,skipped=skipped,candidate_references=references,definition='Conservative existing absolute paths reached from canonical registry, CLIENT, current E specs/qualifications/accepted records, source control and recursively named JSON. Existing historical current-plan files may overclassify WARM; no historical citation is silently deleted.'))
# Prior published SHA identities only. These are inventory records, not a new
# content verification or guessed equality to another file with same basename.
identity_docs=[Path('/workspace/ep_l2_ft20261016_shared/lane1')]
identity_docs += [Path('/workspace/ep_l2_parallel_lane1')]
sha_map=collections.defaultdict(list);identity_sources=[]
def visit(obj,source):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if isinstance(k,str) and k.startswith('/workspace/') and isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v):sha_map[k].append(dict(sha256=v,source=source,kind='published_exact_path_key'))
  for k,v in obj.items():
   if isinstance(v,str) and v.startswith('/workspace/'):
    for hk in (k+'_sha256','sha256' if k=='path' else '', 'binary_sha256' if k in ['binary','executable'] else ''):
     h=obj.get(hk)
     if isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h):sha_map[v].append(dict(sha256=h,source=source,kind='published_exact_path_field'))
   visit(v,source)
 elif isinstance(obj,list):
  for v in obj:visit(v,source)
for base in identity_docs:
 for p in base.rglob('*.json'):
  if p.stat().st_size>2*2**20:continue
  if len(identity_sources)>1800:raise RuntimeError('SHA metadata source bound reached')
  identity_sources.append(str(p))
  try:visit(json.loads(p.read_text()),str(p))
  except (ValueError,UnicodeError):pass
write('PRIOR_SHA_METADATA_SOURCES.json',identity_sources)
files=[e for e in entries if stat.S_ISREG(e['mode'])];by_inode=collections.defaultdict(list)
for e in files:by_inode[(e['device'],e['inode'])].append(e)
candidate_live=[v for v in live_paths if any(inside(v,r) for r in BUILDS)]
candidate_dirs=[v for v in candidate_live if Path(v).is_dir()]
selected=[];warm=[];summaries=[]
for root in BUILDS:
 root_entries=[e for e in files if inside(e['path'],root)];cold=[];hot=[]
 for e in root_entries:
  active=[r for r in readers if r['target'].removesuffix(' (deleted)')==e['path'] or (r['kind']=='cwd' and inside(e['path'],Path(r['target'])))]
  direct=[v for v in candidate_live if v==e['path']]+[v for v in candidate_dirs if inside(e['path'],Path(v))]
  item={**e, 'original_sha256_records':sha_map.get(e['path'],[]),'original_sha256_status':'PUBLISHED_EXACT_PATH_NOT_REHASHED' if sha_map.get(e['path']) else 'NOT_PREVIOUSLY_RECORDED_TRANSFER_STREAM_HASH_REQUIRED', 'scientific_project':'EP-L2 legacy20261017/18 Lane1 producer build; not current main61', 'classification':'HOT' if active else 'WARM' if direct or errors else 'COLD', 'active_readers':active,'current_direct_dependency_paths':direct,'owner_review':'E_SCIENTIFIC_CANDIDATE_REVIEW_ONLY_NO_SOURCE_RELEASE','restore_requirement':'Independent true164 complete file-content/tree restore verification against sealed transfer manifest; preserve path/link metadata and original SHA records; E rechecks canonical references before any source release. Rebuild from Git is not restore evidence.', 'source_release_authorized':False}
  (cold if item['classification']=='COLD' else hot).append(item)
 selected+=cold;warm+=hot
 summaries.append(dict(path=str(root),root_metadata=meta(root),regular_files=len(root_entries),allocated_unique_inode_bytes=sum(group[0]['allocated_bytes'] for key,group in by_inode.items() if any(inside(e['path'],root) for e in group)),COLD_files=len(cold),COLD_allocated_bytes=sum(e['allocated_bytes'] for e in cold),HOT_WARM_files=len(hot),original_sha_records_found=sum(bool(e['original_sha256_records']) for e in cold),reader_count=sum(bool(e['active_readers']) for e in hot)))
selected_keys={(e['device'],e['inode']) for e in selected};selected_count=collections.Counter((e['device'],e['inode']) for e in selected)
reclaimable=sum(by_inode[k][0]['allocated_bytes'] for k in selected_keys if selected_count[k]>=by_inode[k][0]['nlink'])
external_links=[dict(device=k[0],inode=k[1],nlink=by_inode[k][0]['nlink'],selected_links=selected_count[k],allocated_bytes=by_inode[k][0]['allocated_bytes']) for k in selected_keys if selected_count[k]<by_inode[k][0]['nlink']]
write('COLD_FILE_CANDIDATES_V1.json',sorted(selected,key=lambda e:e['allocated_bytes'],reverse=True));write('HOT_WARM_BUILD_FILES_V1.json',warm)
root_totals=[]
for r in RESULTS:
 keys={(e['device'],e['inode']) for e in files if inside(e['path'],r)};root_totals.append(dict(path=str(r),allocated_bytes=sum(by_inode[k][0]['allocated_bytes'] for k in keys),classification='HOT_ACCOUNTING_ROOT_AND_WARM_HISTORICAL_CONTENT',reason='Coordinator.output_usage resolves and traverses these roots. Preserve current acceptance/qualification/failure/HOLD paths. No payload is released by this inventory; future migration requires generated-byte accounting baseline plus receipt/link/restore protocol, never reset6/20GiB.'))
v=os.statvfs('/workspace');summary=dict(schema='EP_L2_E_OWNER_COLD_INVENTORY_V1',at_unix=time.time(),elapsed_seconds=time.monotonic()-START,host=os.uname().nodename,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),E_HEAD_before_inventory='c9a3622eee6e73371fc1c4add2bae4bea6e123ee',read_only_payload_audit=True,full_payload_SHA_computations=0,large_trace_body_scans=0,device=meta(Path('/workspace')),workspace_available_bytes=v.f_bavail*v.f_frsize,workspace_free_blocks_bytes=v.f_bfree*v.f_frsize,filesystem='overlayfs',inode_available=v.f_favail,regular_files_stat=len(files),COLD_candidate_files=len(selected),COLD_allocated_unique_reclaim_upper_bound_bytes=reclaimable,hardlink_external_groups=external_links,candidates=summaries,results_roots=root_totals,open_reader_permission_gaps=errors,owner_review='E_CANDIDATE_LIST_APPROVED_FOR_S_T_REVIEW_ONLY',source_release_authorized=False,actual_freed_bytes=0,estimated_df_gain_caveat='Allocated unique inodes/nlink provide an upper-bound estimate. Overlay upper/lower provenance and shared extents not proved in container; only observed source df growth after exact target acceptance and authorised release counts as freed.',identity_gap='Missing per-file original SHA is explicit, never invented. S must seal immutable selected transfer-stream SHA manifest; T independently full-restore verifies all content and metadata on genuine164. No source release while any identity/restore/reference/accounting gate missing.',source_budget=dict(T0=campaign['t0_unix'],actual_starts=14,maximum=40,remaining=26,reservations=campaign['reservations'],result_new_limit_bytes=campaign['additional_results_max_bytes'],result_total_limit_bytes=campaign['old_plus_new_results_max_bytes'],historical_generation_must_not_reset=True),no_simulations_started=True,no_source_file_moved_copied_deleted=True)
write('FIRST_CANDIDATES_AND_E_OWNER_REVIEW_V1.json',summary);print(json.dumps(dict(COLD_candidate_files=len(selected),COLD_reclaim_upper_bound_bytes=reclaimable,GiB=reclaimable/2**30,summaries=summaries,reader_permission_gaps=errors,elapsed=time.monotonic()-START)))
