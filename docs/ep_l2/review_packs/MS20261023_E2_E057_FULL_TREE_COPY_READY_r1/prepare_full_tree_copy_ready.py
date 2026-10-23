"""Fresh whole E057 owner inventory; no copying, release or experiment."""
from pathlib import Path
import os, stat, json, hashlib, datetime, collections, shutil

E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
ROOT=Path('/workspace/ep_l2_ms20261019_e_results');S=ROOT/'E057_b4a7e175'
PACK=E/'docs/ep_l2/review_packs/MS20261023_E2_E057_FULL_TREE_COPY_READY_r1'
A=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1'
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
assert not PACK.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
def meta(p):
 t=p.lstat()
 return dict(absolute_path=str(p),dev=t.st_dev,dev_major=os.major(t.st_dev),dev_minor=os.minor(t.st_dev),inode=t.st_ino,nlink=t.st_nlink,
  size=t.st_size,allocated_bytes=t.st_blocks*512,uid=t.st_uid,gid=t.st_gid,mode=stat.S_IMODE(t.st_mode),mode_octal=format(stat.S_IMODE(t.st_mode),'04o'),
  atime_ns=t.st_atime_ns,mtime_ns=t.st_mtime_ns,ctime_ns=t.st_ctime_ns,
  kind='regular' if stat.S_ISREG(t.st_mode) else 'directory' if stat.S_ISDIR(t.st_mode) else 'symlink' if stat.S_ISLNK(t.st_mode) else 'special')
def names(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  with os.scandir(fd) as it:return sorted(x.name for x in it)
 finally:os.close(fd)
def small(p,cap=2*1024*1024):
 before=meta(p);assert before['kind']=='regular' and before['size']<=cap
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:b=f.read(cap+1)
 finally:os.close(fd)
 assert len(b)==before['size'] and before==meta(p)
 return b
def jdoc(p,cap=2*1024*1024):
 b=small(p,cap);return json.loads(b),dict(path=str(p),sha256=sha(b),bytes=len(b))
reg=small(REG,8*1024*1024);data=json.loads(reg);item=data['mechanism_study_20261019_v1']
assert item['actual_starts']==57 and item['controller']['state']=='STOPPED'
attempt=next(x for x in item['attempts'] if x['attempt_id']=='E057_b4a7e175')
assert attempt['actual_start'] is True and attempt['state']=='COMPLETE_VALID'
accepted=item['accepted_results'][attempt['attempt_id']]
active=[dict(kind=k,key=n,record=v) for k in ('runs','resource_leases') for n,v in data[k].items() if v['status'] in ('RESERVED','RUNNING','START_INTENT_UNRECONCILED') and v.get('experiment_id')=='EPL2_MECHANISM_STUDY_20261019_V1']
assert not active
point,pointref=jdoc(A/'results/dwt2d/CURRENT_ACCEPTED_POINT.json')
review,reviewref=jdoc(A/'results/dwt2d/INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json')
assert point['status']=='CURRENT_ACCEPTED_DIAGNOSTIC_POINT' and point['actual_terminal_receipt']==accepted
assert point['independent_terminal_review']['sha256']==reviewref['sha256']
freeze,freezeref=jdoc(A/'engineering/remaining_two_lossless_storage_r1/ACTUAL_BINARY_FREEZE_AUTHORITY.json')
source_before={};directory_names={};todo=[S]
while todo:
 d=todo.pop();source_before[d]=meta(d);assert source_before[d]['kind']=='directory'
 children=names(d);directory_names[d]=children
 for n in children:
  p=d/n;v=meta(p);source_before[p]=v
  assert len(source_before)<=4096 and v['kind']!='special','unsupported special file or inventory bound'
  if v['kind']=='directory':todo.append(p)
assert not any(x['kind']=='symlink' for x in source_before.values()),'symlink requires exact literal and target review before owner signature'
files=[];directories=[];cached={};inode_hash={};bytes_read=0
for p,v in sorted(source_before.items(),key=lambda x:str(x[0])):
 rel=str(p.relative_to(ROOT));entry=dict(v,relative_path=rel)
 if v['kind']=='directory':
  entry.update(children=directory_names[p],empty=not directory_names[p]);directories.append(entry);continue
 assert v['kind']=='regular'
 key=(v['dev'],v['inode']);cache=p.suffix in ('.json','.config') and v['size']<=32*1024*1024
 if key in inode_hash:
  digest=inode_hash[key];assert meta(p)==v
 else:
  assert v['size']<=384*1024*1024 and bytes_read+v['size']<=384*1024*1024
  h=hashlib.sha256();chunks=[];fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
  try:
   with os.fdopen(fd,'rb',closefd=False) as f:
    while True:
     b=f.read(4*1024*1024)
     if not b:break
     h.update(b);bytes_read+=len(b)
     if cache:chunks.append(b)
  finally:os.close(fd)
  assert meta(p)==v
  digest=h.hexdigest();inode_hash[key]=digest
  if cache:cached[p.name]=b''.join(chunks)
 entry['sha256']=digest;entry['sha_scope']='entire regular file including zero-length files';files.append(entry)
byname={Path(x['absolute_path']).name:x for x in files}
assert byname['accel-sim.out']['sha256']==point['source_identity']['binary_sha256']==freeze['binary_sha256']
assert byname['raw.log']['sha256']==review['evidence']['raw']['sha256']
for name,ref in [('run_status.json',accepted),('terminal_summary.json',review['evidence']['terminal_summary']),('input_audit.json',review['evidence']['input_audit'])]:assert byname[name]['sha256']==ref['sha256']
audit=json.loads(cached['input_audit.json']);spec=json.loads(cached['input_spec.json']);exitdoc=json.loads(cached['NATIVE_EXIT.json'])
run_status=json.loads(cached['run_status.json'])
assert run_status['status']=='COMPLETE_VALID' and run_status['exit_code']==0 and run_status['independent_acceptance']=='PASS'
assert run_status['identity']==point['identity']==spec['identity']==attempt['identity']==exitdoc['binding']['identity']
assert exitdoc['exit_code']==exitdoc['wait_status']==0 and exitdoc['exited_normally'] and exitdoc['released_to_native']
for label,ref in review['evidence']['native4docs'].items():assert byname[Path(ref['path']).name]['sha256']==ref['sha256']
for i,row in enumerate(audit['configs']):assert byname[f'config-{i}.config']['sha256']==row['sha256']
for row in audit['auxiliary_assets']:assert byname[row['name']]['sha256']==row['sha256']
# All hardlink groups inside the selected tree, with known outside aliases explicit.
groups=collections.defaultdict(list)
for x in files:groups[(x['dev'],x['inode'])].append(x)
hardlinks=[]
for key,group in groups.items():
 nlink=group[0]['nlink']
 if nlink==1:continue
 known=[]
 for raw in freeze['known_aliases']:
  p=Path(raw);v=meta(p)
  if (v['dev'],v['inode'])==key:known.append(v)
 assert len(known)==nlink and all(v['mode']==0o555 for v in known),'hardlink aliases not fully accounted'
 hardlinks.append(dict(dev=key[0],inode=key[1],source_nlink=nlink,selected_paths=[x['absolute_path'] for x in group],known_aliases=known,
  sha256=group[0]['sha256'],selected_link_count=len(group),external_link_count=nlink-len(group),all_source_aliases_known=True,
  target_semantics='Preserve equivalence among any selected in-tree aliases. This group has one selected path; materialize its full bytes as an independent target file. Do not include, alter or dereference-copy external aliases; source nlink need not equal target nlink.',
  source_semantics='Source aliases remain shared and owner-write-frozen0555; no chmod/chown/unlink/rename/rebuild of any alias.'))
# Preserve filesystem and embedded reference semantics, without following trace data.
refs=[];nodes=0
def classify(document,pointer,value):
 lexical=Path(value)
 internal=lexical.is_relative_to(S)
 if internal:return 'IN_TREE_ABSOLUTE_REFERENCE_PRESERVE_LITERAL'
 if document.startswith('NATIVE_') and pointer.startswith('/command/'):return 'ACTUAL_RUNTIME_EXTERNAL_COMMAND_ARGUMENT'
 if document=='input_spec.json' and pointer.startswith(('/trace_files/','/configs/','/auxiliary_assets/','/binary','/parser/')):return 'DECLARED_EXTERNAL_SOURCE_RUNTIME_OR_REPLAY_DEPENDENCY'
 if document.endswith('.config'):return 'ACTUAL_CONFIG_EXTERNAL_DEPENDENCY'
 return 'RETAINED_EVIDENCE_OR_PROVENANCE_REFERENCE_NOT_AUTO_EXECUTION_AUTHORITY'
def walk(obj,document,pointer=''):
 global nodes
 nodes+=1;assert nodes<=2000000
 if isinstance(obj,dict):
  for k,v in obj.items():walk(v,document,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
 elif isinstance(obj,list):
  for n,v in enumerate(obj):walk(v,document,pointer+'/'+str(n))
 elif isinstance(obj,str) and obj.startswith('/') and '\n' not in obj:
  refs.append(dict(document=document,json_pointer_or_line=pointer,literal=obj,semantics=classify(document,pointer,obj)))
for name,b in cached.items():
 if name.endswith('.json'):walk(json.loads(b),name)
 elif name.endswith('.config'):
  for n,line in enumerate(b.decode().splitlines(),1):
   body=line.split('#',1)[0].strip()
   if not body:continue
   parts=body.split(None,1)
   if len(parts)==2 and parts[1].startswith('/'):
    refs.append(dict(document=name,json_pointer_or_line='line'+str(n)+':'+parts[0],literal=parts[1],semantics='ACTUAL_CONFIG_EXTERNAL_DEPENDENCY' if not Path(parts[1]).is_relative_to(S) else 'IN_TREE_ABSOLUTE_REFERENCE_PRESERVE_LITERAL'))
assert len(refs)<=4096
external={}
for row in refs:
 raw=row['literal']
 if Path(raw).is_relative_to(S) or raw in external:continue
 p=Path(raw)
 try:external[raw]=dict(lstat=meta(p),exists=True,hash_recomputed=False)
 except FileNotFoundError:external[raw]=dict(exists=False,hash_recomputed=False,disposition='Preserve historical literal; not every evidence/provenance path is an active runtime dependency. No source replay validity upgrade.')
 except OSError as exc:external[raw]=dict(exists=None,hash_recomputed=False,error=str(exc),disposition='Literal retained, not dereferenced or copied')
reference_semantics=dict(scope='All filesystem entries and all absolute single-line string values in every JSON/config inside the complete tree; raw/log prose and embedded historical shell scripts preserved as bytes, not interpreted/executed.',
 filesystem_links=dict(symlinks=[],symlink_count=0,symlink_policy='No dereferencing or alias rewriting; any newly appearing symlink invalidates this snapshot.',hardlink_groups=hardlinks),
 literal_references=refs,external_path_lstat=external,
 instructions=['Keep every stored JSON/config/command/provenance byte exactly; no path rebasing or rewriting during archive/native restoration.',
 'Copy tree includes its local oracle/input evidence snapshots, but actual configs still name original external oracle paths; native command uses external traces. Keep all original canonical source paths under SOURCE_KEEP.',
 'External dependencies, source repositories, parser/Q/manifest, shared libraries and traces are not added to this result-tree transfer. This is a full RESULT TREE copy, not a self-contained simulator replay installation or new runtime qualification.',
 'Embedded historical source/binary identities are retained provenance. The independently accepted point defines actual r5 runtime identity; never normalize older evidence objects to that identity.',
 'Archive/restore does not redirect E2/D readers, promote a new S/F pair, revive failures or authorize a science restart.'])
# Current exact inode readers include open aliases outside the tree and mappings.
selected={k:[x['absolute_path'] for x in v] for k,v in groups.items()};observed=[];gaps=[];np=nf=maps_bytes=vanished=0
for proc in [p for p in Path('/proc').iterdir() if p.name.isdigit()]:
 np+=1;assert np<=2048
 try:
  ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]);fds=list((proc/'fd').iterdir());nf+=len(fds);assert nf<=32768
  for fd in fds:
   try:
    q=fd.stat();key=(q.st_dev,q.st_ino)
    if key in selected:
     info=(proc/'fdinfo'/fd.name).read_text();flags=next(int(x.split()[1],8) for x in info.splitlines() if x.startswith('flags:'))
     observed.append(dict(pid=int(proc.name),start_ticks=ticks,kind='fd',fd=fd.name,selected_paths=selected[key],write_capable=(flags&os.O_ACCMODE)!=os.O_RDONLY))
   except (FileNotFoundError,ProcessLookupError):vanished+=1
   except PermissionError:gaps.append(dict(pid=int(proc.name),phase='fd'))
  with (proc/'maps').open('rb') as f:mb=f.read(4*1024*1024+1)
  maps_bytes+=len(mb);assert len(mb)<=4*1024*1024 and maps_bytes<=32*1024*1024
  for line in mb.decode(errors='replace').splitlines():
   f=line.split(None,5)
   if len(f)<5:continue
   a,b=(int(x,16) for x in f[3].split(':'));key=(os.makedev(a,b),int(f[4]))
   if key in selected:observed.append(dict(pid=int(proc.name),start_ticks=ticks,kind='mapping',permissions=f[1],selected_paths=selected[key],write_capable='w' in f[1]))
  assert ticks==int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
 except (FileNotFoundError,ProcessLookupError):vanished+=1
 except PermissionError:gaps.append(dict(pid=int(proc.name),phase='process_metadata'))
assert not gaps and not any(x['write_capable'] for x in observed)
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();old_processes=[]
for kind,key in [('native','native_process'),('guardian','guardian_process'),('controller','controller_process')]:
 old=exitdoc[key];p=Path('/proc')/str(old['pid']);current_ticks=None
 try:current_ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19])
 except FileNotFoundError:pass
 live=boot==old['boot_id'] and current_ticks==old['start_ticks'];assert not live
 old_processes.append(dict(role=kind,recorded_process=old,current_pid_start_ticks=current_ticks,original_identity_live=False))
assert all(meta(p)==v for p,v in source_before.items())
assert all(names(p)==lst for p,lst in directory_names.items())
assert small(REG,8*1024*1024)==reg
logical=sum(x['size'] for x in files);allocated=sum(v[0]['allocated_bytes'] for v in groups.values());dir_alloc=sum(x['allocated_bytes'] for x in directories)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
writer_close=dict(status='FINALIZED_AND_NO_SELECTED_WRITER_OBSERVED',true_native_exit0=True,true_wait_status0=True,original_processes=old_processes,
 central_state='COMPLETE_VALID',active_science_run_or_lease=active,controller=item['controller'],selected_inode_readers=observed,selected_writers=[],access_gaps=gaps,
 process_scan=dict(pids=np,fds=nf,maps_metadata_bytes=maps_bytes,vanished_observations=vanished),
 entire_tree_stat_and_directory_membership_stable_before_after_full_hash=True,
 owner_disposition='No further write/rebuild/retry of paid E057 endpoint or its binary aliases is planned. Future E2 audit and D paper readers retain canonical original paths and readonly access. T copy/verify adds independent target copies, no reader switch.',
 limit='Finalized owner lifecycle plus bounded current namespace observation, not a permanent OS lock against privileged future writers. Fresh source identity checks at actual copy are required; any change requires refreshed owner receipt.')
manifest=dict(schema='EPL2_E2_COMPLETE_RESULT_TREE_COPY_READY_V1',status='COPY_READY',owner='E2',project='EP_L2_E057',owner_offer_id='E2_E057_FULL_RESULT_TREE_SOURCE_KEEP_20261023_r1',at_utc=now,
 source_host=os.uname().nodename,source_boot_id=boot,source_root=str(ROOT),complete_tree_path=str(S),copy_relative_root=S.name,
 scope='ENTIRE_RECURSIVE_E057_RESULT_TREE_NEW_INVENTORY_NOT_OLD_SIDECAR_OFFER',source_policy='SOURCE_KEEP',source_release_authorized=False,
 counts=dict(regular_files=len(files),directories_including_tree_root=len(directories),symlinks=0,hardlink_groups=len(hardlinks),unique_regular_inodes=len(groups),zero_byte_files=sum(x['size']==0 for x in files)),
 bytes=dict(logical_regular_bytes=logical,unique_regular_allocated_bytes=allocated,directory_allocated_bytes=dir_alloc,source_tree_allocated_bytes=allocated+dir_alloc,full_file_hash_bytes_read=bytes_read),
 files=files,directories=directories,filesystem_link_semantics=reference_semantics['filesystem_links'],
 accepted=dict(status=point['status'],central_state='COMPLETE_VALID',attempt_id=attempt['attempt_id'],condition_id=attempt['condition_id'],source_identity=point['source_identity'],identity=point['identity'],qualification_id=point['qualification_id'],
 native_exit_code=0,instructions=point['instructions'],cycles=point['cycles'],physical_slices=point['physical_slices'],pair=False,point_ref=pointref,independent_terminal_ref=reviewref,accepted_result_pointer=accepted,
 current_sha_match_original_accepted_raw_binary_summary_status_native4_config_and_aux=True),
 write_closure=writer_close,reader_disposition=writer_close['owner_disposition'],
 transport='T must independently admit target space/tooling and assign a NEW full-tree transaction; old sidecar txid/receipt is not this transfer. No copy performed by E2.',
 source_preservation=dict(registry_sha256_before_after=sha(reg),registry_unchanged=True,original_T0=item['t0_unix'],actual_starts=57,new_application_starts=0,Goal='PAUSED_UNCHANGED',source_deleted_bytes=0,source_mutations=0,no_source_chmod_chown_unlink_rename_utime=True),
 target_requirements=['Transfer all regular files and all nested/empty directories, without include-list truncation. Use the complete manifest, not old five-sidecar allowlists.',
 'Verify full SHA/size and numeric uid/gid/mode/mtime for each file and directory, literal symlinks if any (none now), and declared in-scope hardlink equivalence. Record target device/inodes independently; do not pretend original inode numbers persist across filesystems.',
 'Known external binary aliases remain source-side; one selected binary path may be independently materialized at target. No dedup credit or source release may be claimed for retaining or dropping one original alias.',
 'Preserve byte-exact historical absolute references. Do not execute, rebase, reinterpret or independently promote old provenance statements into current qualification.',
 'After target full-tree archive/native restore receipt, E2 must independently recheck source SHA/stat and scientific references. All phases remain SOURCE_KEEP; destination PASS never authorizes source release.'],
 BA_boundary='AD_GEMM complete tree, including mapper nested directories, requires independently authored BA COPY_READY. E2 neither inventories nor signs BA assets.')
PACK.mkdir()
def save(n,v):(PACK/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
save('COPY_READY.json',manifest);save('REFERENCE_AND_LINK_SEMANTICS.json',reference_semantics);save('WRITE_CLOSURE_AND_READERS.json',writer_close)
(PACK/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['relative_path']+'\n' for x in files))
(PACK/'FILES_FROM.txt').write_text(''.join(x['relative_path']+'\n' for x in directories+files))
save('OWNER_REVIEW.json',dict(status='E2_INDEPENDENT_FULL_TREE_COPY_READY_SOURCE_KEEP',at_utc=now,copy_ready_sha256=sha((PACK/'COPY_READY.json').read_bytes()),
 all_files_fresh_entire_SHA=True,all_recursive_and_empty_directories_recorded=True,old_sidecar_COPY_READY_not_substituted=True,all_selected_writers_closed=True,source_keep=True,source_release_authorized=False,
 acceptance_refs_unchanged=True,full_tree_no_new_scientific_qualification=True,actual_starts=57,Goal='PAUSED',BA_not_signed=True))
(PACK/'README.md').write_text(f'E2 full-tree COPY_READY, SOURCE_KEEP\n\nFresh complete inventory of E057_b4a7e175: {len(files)} regular files, {len(directories)} directories including root (all nested and empty directories), {logical} logical bytes, zero symlinks. All regular files, including raw, binary, terminal/exit, input evidence, configs and empty logs, have whole-file SHA and full source stat. Old five-sidecar COPY_READY is not this offer.\n\naccel-sim.out has source nlink3: source canonical build and E056 aliases are fully recorded, owner-write-frozen0555 and kept. Only one alias belongs to this tree; target may materialize an independent complete byte-identical file. No external alias is added to transfer scope.\n\nSource is accepted diagnostic point E057 (not a new S/F pair); true native exit0, old process identities gone, no active campaign lease, no selected writer and stable full-tree stat/membership established. Future E2/D readers keep original canonical paths. Every stored historical source identity and absolute input/oracle/reference remains verbatim; the full RESULT TREE is not a self-contained trace/runtime installation.\n\nT independently handles target resources and tooling with a new full-tree transaction, complete file/directory/SHA/metadata validation and subsequent E2 source-owner recheck. No source release, goal restart, automatic rerun, reader redirection or science identity change is authorized. BA alone signs AD_GEMM full tree including mapper.\n')
shutil.copyfile(Path(__file__),PACK/'prepare_full_tree_copy_ready.py')
print(json.dumps(dict(status='COPY_READY_PREPARED_PENDING_GIT_PUBLICATION',path=str(PACK),counts=manifest['counts'],bytes=manifest['bytes'],selected_readers=len(observed),source_keep=True,actual_starts=57),indent=2))
