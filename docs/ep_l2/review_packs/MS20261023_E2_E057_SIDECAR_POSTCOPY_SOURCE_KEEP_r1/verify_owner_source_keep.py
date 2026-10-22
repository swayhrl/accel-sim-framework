"""E2 owner-only post-copy source review; no transport, release or Goal resume."""
from pathlib import Path
import os, stat, sys, json, hashlib, datetime, shutil

E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
BASE=E/'docs/ep_l2/review_packs'
READY_DIR=BASE/'MS20261023_E2_E057_SIDECAR_COPY_READY_r1'
A=BASE/'MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1'
D=BASE/'MS20261023_E2_E057_SIDECAR_POSTCOPY_SOURCE_KEEP_r1'
REMOTE=Path('/tmp/e2_e057_postcopy_remote_20261023')
ROOT=Path('/workspace/ep_l2_ms20261019_e_results');S=ROOT/'E057_b4a7e175'
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
T_COMMIT='aecccb6ad757a17c1c254940b01e11d56a6480a1'
T_BASE='docs/ep_l2/operations/result_offload_pilot_20261023_v1/'
assert not D.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
def identity(p):
 s=p.lstat()
 return dict(dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,size=s.st_size,allocated_bytes=s.st_blocks*512,
    mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,atime_ns=s.st_atime_ns,uid=s.st_uid,gid=s.st_gid,
    mode=stat.S_IMODE(s.st_mode),mode_octal=format(stat.S_IMODE(s.st_mode),'04o'),file_type='regular' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'other')
def read(p,cap=2*1024*1024):
 before=identity(p);assert before['file_type']=='regular' and not p.is_symlink() and 0<before['size']<=cap
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:b=f.read(cap+1)
 finally:os.close(fd)
 assert len(b)==before['size'] and before==identity(p),str(p)
 return b,before
def jdoc(p,cap=2*1024*1024):
 b,i=read(p,cap);return json.loads(b),dict(path=str(p),sha256=sha(b),bytes=len(b)),i
def matches(got,want,keys):
 assert all(got[k]==want[k] for k in keys),[(k,got.get(k),want.get(k)) for k in keys if got.get(k)!=want.get(k)]
remote_names={
 'T_OWNER_POSTCOPY_HANDOFF_REQUEST.json':('OWNER_POSTCOPY_HANDOFF_REQUEST.json','8457f7249a98551da3d7b74834b3f9299c11e10b'),
 'T_ARCHIVE_AND_NATIVE_RESTORE_RECEIPT.json':('results/EP_L2_E057/ARCHIVE_AND_NATIVE_RESTORE_RECEIPT.json','8c6f9e6a23b18bf23a59d4a16b797ecff10e5a30'),
 'T_SOURCE_POSTCOPY_READONLY_CHECK.json':('results/EP_L2_E057/SOURCE_POSTCOPY_READONLY_CHECK.json','e3504a456a2518a433ce82ad78feca1e4ba782f2')}
remote_refs=[];remote_docs={}
for n,(rel,gitblob) in remote_names.items():
 b,_=read(REMOTE/n)
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==gitblob
 remote_docs[n]=json.loads(b)
 remote_refs.append(dict(repository='swayhrl/accel-sim-framework',commit=T_COMMIT,path=T_BASE+rel,git_blob_sha1=gitblob,whole_file_sha256=sha(b),bytes=len(b),local_evidence_name=n))
handoff=remote_docs['T_OWNER_POSTCOPY_HANDOFF_REQUEST.json']
offer=next(x for x in handoff['projects'] if x['project']=='EP_L2_E057' and x['owner']=='E2')
envelope=remote_docs['T_ARCHIVE_AND_NATIVE_RESTORE_RECEIPT.json'];target=envelope['receipt']
canonical_receipt=(json.dumps(target,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
assert sha(canonical_receipt)==offer['target_receipt_sha256']==envelope['receipt_sha256']
assert target['txid']==offer['txid'] and target['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
assert target['source_disposition']=='SOURCE_KEEP' and target['source_released_bytes']==0
tcheck=remote_docs['T_SOURCE_POSTCOPY_READONLY_CHECK.json'];assert tcheck['txid']==offer['txid']
ready,readyref,_=jdoc(READY_DIR/'COPY_READY.json')
assert readyref['sha256']==target['owner_ready_sha256']==tcheck['owner_ready_sha256']
assert target['owner_publication']=='febccc8d4470781b0a15aa07aa3ad86a8804e883'
assert offer['files']==target['files']==ready['file_count']==5
assert offer['bytes']==target['raw_bytes']==ready['total_source_bytes']==16113
reg_bytes,reg_before=read(REG,8*1024*1024);data=json.loads(reg_bytes);ledger=data['mechanism_study_20261019_v1']
assert ledger['actual_starts']==57 and ledger['controller']['state']=='STOPPED'
assert ledger['t0_unix']==ready['campaign_preservation']['original_T0']
attempt=next(a for a in ledger['attempts'] if a['attempt_id']=='E057_b4a7e175')
assert attempt['actual_start'] is True and attempt['state']=='COMPLETE_VALID'
accepted=ledger['accepted_results'][attempt['attempt_id']]
assert accepted==ready['acceptance']['accepted_result_pointer']
active=[dict(group=g,key=k,record=v) for g in ('runs','resource_leases') for k,v in data[g].items() if v['status'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') and v.get('experiment_id')=='EPL2_MECHANISM_STUDY_20261019_V1']
assert not active
rows=[];source_after={}
keys=['dev','inode','nlink','size','allocated_bytes','mtime_ns','ctime_ns','uid','gid','mode']
for original in ready['files']:
 p=Path(original['absolute_path']);assert p.parent==S
 b,now=read(p,1024*1024);matches(now,original,keys)
 t=next(x for x in target['paths'] if x['source']==str(p))
 proof=next(x for x in tcheck['files'] if x['relative_path']==original['relative_path'])
 assert sha(b)==original['sha256']==t['sha256']==proof['sha256'] and len(b)==t['size']
 matches(now,t['source_identity'],['dev','inode','uid','gid','mode','mtime_ns','ctime_ns'])
 proof_id=dict(proof['identity']);proof_id['allocated_bytes']=proof_id.pop('allocated');matches(now,proof_id,keys)
 source_after[p]=now
 rows.append(dict(absolute_path=str(p),relative_path=original['relative_path'],sha256=sha(b),source_identity=now,
   matches_owner_COPY_READY=True,matches_T_target_source_identity=True,matches_T_source_postcopy_proof=True,
   source_read='O_RDONLY|O_NOFOLLOW|O_NOATIME; same stat including atime before/after',
   archive_path_as_reported_by_T=t['archive'],native_restore_path_as_reported_by_T=t['native_restore'],
   target_restored_identity_as_reported_by_T=t['restored_identity']))
dirs=[]
for original in ready['directory_records']:
 p=Path(original['absolute_path'])
 if p not in (ROOT,S):continue
 now=identity(p);matches(now,original,keys)
 dirs.append(dict(absolute_path=str(p),current_identity=now,original_owner_directory_identity_match=True))
children=[dict(absolute_path=str(p),**identity(p)) for p in sorted(S.iterdir())]
assert len(children)==len(ready['source_directory_entries_stat_only'])
for now,original in zip(children,ready['source_directory_entries_stat_only']):
 assert now['absolute_path']==original['absolute_path'];matches(now,original,keys)
# Recheck the original accepted pointers and exact immutable evidence, not a new science run.
evidence=[]
for oldref in (ready['acceptance']['point_ref'],ready['acceptance']['independent_terminal_ref'],ready['acceptance']['input_audit_ref']):
 b,_=read(Path(oldref['path']));assert sha(b)==oldref['sha256']
 evidence.append(dict(original_ref=oldref,current_sha256=sha(b),status='UNCHANGED'))
point=json.loads(read(Path(ready['acceptance']['point_ref']['path']))[0])
review=json.loads(read(Path(ready['acceptance']['independent_terminal_ref']['path']))[0])
assert point['actual_terminal_receipt']==accepted and point['status']=='CURRENT_ACCEPTED_DIAGNOSTIC_POINT'
assert point['native_exit_code']==0 and point['identity']==attempt['identity']
for oldref in [accepted,review['evidence']['terminal_summary'],review['evidence']['final_manifest'],review['evidence']['spec'],review['evidence']['Q']]:
 b,_=read(Path(oldref['path']),32*1024*1024);assert sha(b)==oldref['sha256']
 evidence.append(dict(original_ref=oldref,current_sha256=sha(b),status='UNCHANGED'))
exitdoc=json.loads(read(S/'NATIVE_EXIT.json')[0]);assert exitdoc['exit_code']==exitdoc['wait_status']==0
assert exitdoc['binding']['identity']==point['identity']
# One bounded current selected-file writer check. No raw/trace or other science work.
selected={(v['dev'],v['inode']):str(p) for p,v in source_after.items()};readers=[];gaps=[];pid_count=fd_count=maps_bytes=vanished=0
for proc in [p for p in Path('/proc').iterdir() if p.name.isdigit()]:
 pid_count+=1;assert pid_count<=2048
 try:
  ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]);fds=list((proc/'fd').iterdir());fd_count+=len(fds);assert fd_count<=32768
  for fd in fds:
   try:
    s=fd.stat();key=(s.st_dev,s.st_ino)
    if key in selected:
     info=(proc/'fdinfo'/fd.name).read_text();flags=next(int(x.split()[1],8) for x in info.splitlines() if x.startswith('flags:'))
     readers.append(dict(pid=int(proc.name),start_ticks=ticks,path=selected[key],kind='fd',fd=fd.name,write_capable=(flags&os.O_ACCMODE)!=os.O_RDONLY))
   except (FileNotFoundError,ProcessLookupError):vanished+=1
   except PermissionError:gaps.append(dict(pid=int(proc.name),phase='fd'))
  with (proc/'maps').open('rb') as f:mb=f.read(4*1024*1024+1)
  assert len(mb)<=4*1024*1024;maps_bytes+=len(mb);assert maps_bytes<=32*1024*1024
  for line in mb.decode(errors='replace').splitlines():
   fields=line.split(None,5)
   if len(fields)<5:continue
   a,b=(int(x,16) for x in fields[3].split(':'));key=(os.makedev(a,b),int(fields[4]))
   if key in selected:readers.append(dict(pid=int(proc.name),start_ticks=ticks,path=selected[key],kind='mapping',permissions=fields[1],write_capable='w' in fields[1]))
  assert ticks==int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
 except (FileNotFoundError,ProcessLookupError):vanished+=1
 except PermissionError:gaps.append(dict(pid=int(proc.name),phase='process_metadata'))
assert not gaps and not any(x['write_capable'] for x in readers)
assert all(identity(p)==v for p,v in source_after.items())
assert identity(REG)==reg_before
assert read(REG,8*1024*1024)[0]==reg_bytes
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt=dict(schema='EPL2_E2_OWNER_POSTCOPY_SOURCE_KEEP_RECONFIRMATION_V1',status='OWNER_SOURCE_KEEP_RECONFIRMED',owner='E2',project='EP_L2_E057',
 at_utc=now,source_host=os.uname().nodename,source_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 txid=offer['txid'],target_receipt_sha256=offer['target_receipt_sha256'],
 target_receipt_hash_scope='SHA256 of UTF8 json.dumps(receipt,sort_keys=True,separators=(comma,colon),ensure_ascii=False) plus newline; independently reproduced',
 target_receipt_whole_file_sha256=next(x['whole_file_sha256'] for x in remote_refs if x['local_evidence_name']=='T_ARCHIVE_AND_NATIVE_RESTORE_RECEIPT.json'),
 T_published_evidence=remote_refs,original_owner_ready_ref=readyref,original_owner_ready_commit=target['owner_publication'],
 files=rows,file_count=5,total_source_bytes=16113,directory_records=dirs,source_directory_all_entries_unchanged=True,
 accepted_state=dict(central_attempt='COMPLETE_VALID',point='CURRENT_ACCEPTED_DIAGNOSTIC_POINT',pair=False,attempt_id=attempt['attempt_id'],qualification_id=attempt['qualification_id'],
 instructions=point['instructions'],cycles=point['cycles'],physical_slices=point['physical_slices'],original_accepted_result_pointer=accepted,original_accepted_references='UNCHANGED',evidence=evidence),
 reader_disposition=dict(current_exact_file_readers=readers,selected_writers=[],access_gaps=gaps,bounded_processes=pid_count,bounded_fds=fd_count,maps_metadata_bytes=maps_bytes,vanished_observations=vanished,
 namespace='current original174 /proc point-in-time only',planned_readers='Original E2/D readonly scientific paths stay canonical; T archive/native target are additional sidecar copies. No reader reroute or source writer/restart authorized.'),
 source_policy='SOURCE_KEEP',source_released_bytes=0,source_release_authorized=False,
 source_mutations=dict(unlink=0,rename=0,chmod=0,chown=0,utime=0,copy_or_transfer=0),
 scientific_campaign=dict(original_T0=ledger['t0_unix'],actual_starts=57,new_application_starts=0,controller=ledger['controller'],active_science_rows=active,Goal='PAUSED_UNCHANGED',registry_sha256_before_after=sha(reg_bytes),registry_unchanged=True),
 verification_scope='Independent E2 source bytes/stat/accepted-reference review. Target receipt Git blob and canonical receipt SHA independently verified; native target filesystem restoration remains independently performed by T, not claimed as rerun by E2.',
 BA_boundary='AD_GEMM is outside E2 ownership; BA must publish its own independent postcopy review.',
 science_acceptance_not_upgraded='No full result restore, new S/F pair, new qualification, experiment or Goal completion claimed.')
D.mkdir()
for n in remote_names:shutil.copyfile(REMOTE/n,D/n)
(D/'OWNER_POSTCOPY_SOURCE_KEEP_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
(D/'SHA256SUMS_SOURCE_FILES').write_text(''.join(x['sha256']+'  '+x['relative_path']+'\n' for x in rows))
(D/'README.md').write_text('E2 independently reconfirms SOURCE_KEEP for the exact E057 NATIVE_EXIT and four config sidecars after T copy.\n\nAll five source SHAs, device/inode/nlink/size/allocation/mtime/ctime/uid/gid/mode match original E2 COPY_READY and T published postcopy evidence. Original CURRENT_ACCEPTED point, central accepted pointer, run_status, terminal_summary, independent review, input audit and manifest/spec/Q references are unchanged. Source remains canonical; zero source bytes released.\n\nOWNER_POSTCOPY_SOURCE_KEEP_RECEIPT.json binds T commit aecccb6ad757a17c1c254940b01e11d56a6480a1, exact EP_L2_E057 txid and the canonical target receipt SHA. It separately records the whole receipt file SHA. The three T Git blobs are preserved byte-for-byte with their original blob and SHA identities. E2 does not claim to have rerun T native target restoration.\n\nScientific Goal remains paused, actual starts57, controllerSTOPPED. BA AD_GEMM review requires BA own independent identity. No release/transport/science restart is authorized by this receipt.\n')
shutil.copyfile(Path(__file__),D/'verify_owner_source_keep.py')
print(json.dumps(dict(status=receipt['status'],txid=offer['txid'],target_receipt_sha256=offer['target_receipt_sha256'],files=5,bytes=16113,original_acceptance='UNCHANGED',registry_unchanged=True,source_released_bytes=0,directory=str(D)),indent=2))
