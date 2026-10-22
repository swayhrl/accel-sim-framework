"""Read-only, exact five-file E2 owner inventory. Never transport or release."""
from pathlib import Path
import os, sys, stat, json, hashlib, datetime, errno, subprocess

E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
ROOT=Path('/workspace/ep_l2_ms20261019_e_results')
SOURCE=ROOT/'E057_b4a7e175'
DEST=E/'docs/ep_l2/review_packs/MS20261023_E2_E057_SIDECAR_COPY_READY_r1'
A=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1'
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
NAMES=['NATIVE_EXIT.json']+[f'config-{i}.config' for i in range(4)]
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not DEST.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
def metadata(p):
 s=p.lstat()
 return {'absolute_path':str(p),'dev':s.st_dev,'dev_major':os.major(s.st_dev),'dev_minor':os.minor(s.st_dev),
  'inode':s.st_ino,'nlink':s.st_nlink,'size':s.st_size,'allocated_bytes':s.st_blocks*512,
  'mtime_ns':s.st_mtime_ns,'mtime_utc':datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc).isoformat(),
  'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'mode_octal':format(stat.S_IMODE(s.st_mode),'04o'),
  'file_type':'regular' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'other',
  'is_symlink':stat.S_ISLNK(s.st_mode)}
def stable_bytes(p,cap):
 before=metadata(p);assert before['file_type']=='regular' and not before['is_symlink'] and 0<before['size']<=cap
 flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME
 fd=os.open(p,flags)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:b=f.read(cap+1)
 finally:os.close(fd)
 assert len(b)==before['size'] and before==metadata(p),str(p)
 return b,before
def doc(p,cap=1024*1024):
 b,s=stable_bytes(p,cap);return json.loads(b),{'path':str(p),'sha256':sha(b),'bytes':len(b)}
reg_bytes,reg_stat=stable_bytes(REG,8*1024*1024)
data=json.loads(reg_bytes);item=data['mechanism_study_20261019_v1']
assert item['actual_starts']==57 and item['controller']['state']=='STOPPED'
attempt=next(a for a in item['attempts'] if a['attempt_id']=='E057_b4a7e175')
assert attempt['state']=='COMPLETE_VALID' and attempt['actual_start'] is True
active=[{'group':g,'key':k,'record':r} for g in ('runs','resource_leases') for k,r in data[g].items()
 if r['status'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') and r.get('experiment_id')=='EPL2_MECHANISM_STUDY_20261019_V1']
assert not active
point,pointref=doc(A/'results/dwt2d/CURRENT_ACCEPTED_POINT.json')
review,reviewref=doc(A/'results/dwt2d/INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json')
assert point['status']=='CURRENT_ACCEPTED_DIAGNOSTIC_POINT' and point['attempt_id']==attempt['attempt_id']
assert point['endpoint_status']=='COMPLETE_VALID' and point['native_exit_code']==0
assert point['actual_terminal_receipt']==item['accepted_results'][attempt['attempt_id']]
assert point['independent_terminal_review']['sha256']==reviewref['sha256']
audit,auditref=doc(SOURCE/'input_audit.json')
assert auditref['sha256']==review['evidence']['input_audit']['sha256']
exitdoc,exitref=doc(SOURCE/'NATIVE_EXIT.json')
assert exitref['sha256']==review['evidence']['native4docs']['NATIVE_EXIT']['sha256']
assert exitdoc['exit_code']==0 and exitdoc['wait_status']==0 and exitdoc['exited_normally'] is True
assert exitdoc['binding']['attempt_id']==attempt['attempt_id'] and exitdoc['binding']['identity']==point['identity']
config_argv=[exitdoc['command'][i+1] for i,x in enumerate(exitdoc['command'][:-1]) if x=='-config']
assert config_argv==[str(SOURCE/n) for n in NAMES[1:]]
before={n:metadata(SOURCE/n) for n in NAMES}
dirs=[metadata(p) for p in (Path('/workspace'),ROOT,SOURCE)]
children=[metadata(p) for p in sorted(SOURCE.iterdir())]
assert len(children)<128 and all(not x['is_symlink'] for x in children)
files=[]
for idx,n in enumerate(NAMES):
 b,s=stable_bytes(SOURCE/n,1024*1024)
 expected=review['evidence']['native4docs']['NATIVE_EXIT'] if idx==0 else audit['configs'][idx-1]
 assert sha(b)==expected['sha256']
 if idx:assert len(b)==expected['bytes']
 files.append(dict(s,relative_path='E057_b4a7e175/'+n,sha256=sha(b),accepted_historical_sha256=expected['sha256'],accepted_historical_match=True,
    scientific_role='durable actual native wait4 exit receipt' if idx==0 else 'actual native argv ordered config snapshot '+str(idx-1)))
# Current namespace exact dev/inode readers; bounded /proc metadata only.
targets={(x['dev'],x['inode']):x['absolute_path'] for x in files}
dirids={(x['dev'],x['inode']):x['absolute_path'] for x in dirs}
readers=[];cwd_matches=[];gaps=[];pid_count=fd_count=maps_bytes=vanished=0
pids=[p for p in Path('/proc').iterdir() if p.name.isdigit()]
assert len(pids)<=2048
for proc in pids:
 pid_count+=1
 try:
  start0=(proc/'stat').read_text().rsplit(')',1)[1].split()[19]
  fds=list((proc/'fd').iterdir());fd_count+=len(fds);assert fd_count<=32768
  for fd in fds:
   try:
    fs=fd.stat();key=(fs.st_dev,fs.st_ino)
    if key in targets:
     info=(proc/'fdinfo'/fd.name).read_text();flag=next((int(x.split()[1],8) for x in info.splitlines() if x.startswith('flags:')),None)
     readers.append({'pid':int(proc.name),'start_ticks':int(start0),'kind':'open_fd','fd':fd.name,'path':targets[key],
       'fd_flags_octal':format(flag,'o') if flag is not None else None,'write_capable':flag is None or (flag&os.O_ACCMODE)!=os.O_RDONLY})
   except (FileNotFoundError,ProcessLookupError):vanished+=1
   except PermissionError:gaps.append({'pid':int(proc.name),'phase':'fd_stat','fd':fd.name})
  try:
   cs=(proc/'cwd').stat();key=(cs.st_dev,cs.st_ino)
   if key in dirids:cwd_matches.append({'pid':int(proc.name),'start_ticks':int(start0),'directory':dirids[key]})
  except (FileNotFoundError,ProcessLookupError):vanished+=1
  except PermissionError:gaps.append({'pid':int(proc.name),'phase':'cwd'})
  with (proc/'maps').open('rb') as f:mb=f.read(4*1024*1024+1)
  assert len(mb)<=4*1024*1024;maps_bytes+=len(mb);assert maps_bytes<=32*1024*1024
  for ln in mb.decode(errors='replace').splitlines():
   parts=ln.split(None,5)
   if len(parts)<5:continue
   maj,minr=(int(v,16) for v in parts[3].split(':'));key=(os.makedev(maj,minr),int(parts[4]))
   if key in targets:readers.append({'pid':int(proc.name),'start_ticks':int(start0),'kind':'memory_mapping','path':targets[key],'permissions':parts[1],'write_capable':'w' in parts[1]})
  start1=(proc/'stat').read_text().rsplit(')',1)[1].split()[19]
  if start1!=start0:gaps.append({'pid':int(proc.name),'phase':'pid_identity_changed'})
 except (FileNotFoundError,ProcessLookupError):vanished+=1
 except PermissionError:gaps.append({'pid':int(proc.name),'phase':'process_metadata'})
assert not any(r['write_capable'] for r in readers),'active writer must receive owner review before COPY_READY'
assert not gaps, 'unresolved /proc coverage requires owner review'
assert all(metadata(SOURCE/n)==before[n] for n in NAMES)
assert [metadata(p) for p in (Path('/workspace'),ROOT,SOURCE)]==dirs
assert [metadata(p) for p in sorted(SOURCE.iterdir())]==children
after_reg,_=stable_bytes(REG,8*1024*1024);assert after_reg==reg_bytes
reader_report={'schema':'E2_EXACT_SIDECAR_CURRENT_AND_PLANNED_READER_REVIEW_V1','at_utc':STAMP,
 'namespace':'original174 current visible /proc only; no claim about inaccessible external host/namespace',
 'scope':{'pid_count':pid_count,'fd_count':fd_count,'maps_metadata_bytes':maps_bytes,'vanished_process_or_fd_observations':vanished,'unresolved_access_gaps':gaps},
 'exact_file_open_fds_or_maps':readers,'directory_cwd_observations':cwd_matches,
 'active_E_campaign_registry_rows':active,'controller':item['controller'],
 'current_disposition':'No exact-file write-capable fd or mapping observed; source is finalized COMPLETE_VALID. All readers retain original paths; no process stopped for this inventory.',
 'planned_readers':[{'owner':'E2','purpose':'possible future accepted evidence audit/resume','disposition':'KEEP canonical original five paths; readonly access remains allowed, no rewrite of paid endpoint'},
 {'owner':'D','purpose':'incremental paper/causal evidence consumption','disposition':'Existing CURRENT_ACCEPTED/terminal/config references retained; no compulsory switch to copy'},
 {'owner':'T','purpose':'conditional sidecar transport and independent target verification','disposition':'New transaction, single transfer stream, exact five-file allowlist only; fresh source identity checks required before/after copy; SOURCE_KEEP throughout'}],
 'copy_requires_quiescing_readonly_readers':False,'active_or_planned_source_deletion':False,
 'limitations':'Point-in-time metadata check, not a permanent OS read/write lock; T must reject any changed source SHA/stat/owner/mode/directory record before copy or owner must issue refreshed ready.'}
ready={'schema':'EPL2_E2_EXACT_SIDECAR_COPY_READY_V1','status':'COPY_READY','owner':'E2','owner_project':'EP-L2',
 'owner_offer_id':'E2_E057_SIDECAR_SOURCE_KEEP_20261023_r1','at_utc':STAMP,'source_host':os.uname().nodename,
 'source_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'source_root':str(ROOT),'source_directory':str(SOURCE),
 'source_policy':'SOURCE_KEEP','source_release_authorized':False,'copy_scope':'EXACT_FIVE_SMALL_SIDECARS_ONLY_NOT_FULL_RESULT_RESTORE',
 'transport_transaction_id':'TO_BE_NEWLY_ASSIGNED_AND_VERIFIED_BY_T; no reuse of old V3 transaction',
 'single_stream_condition':'At most one actual sidecar transfer stream; E2 starts none. Synthetic test and destination/transport admission remain T responsibility.',
 'files':files,'file_count':5,'total_source_bytes':sum(x['size'] for x in files),'total_allocated_bytes':sum(x['allocated_bytes'] for x in files),
 'directory_records':dirs,'source_directory_entries_stat_only':children,
 'acceptance':{'attempt_id':attempt['attempt_id'],'current_central_state':attempt['state'],'point_status':point['status'],
    'pair':False,'scientific_scope':point['scientific_scope'],'native_exit_code':0,'native_wait_status':0,
    'native_exit_document_scientific_acceptance_field':exitdoc['scientific_acceptance'],
    'native_exit_not_standalone_scientific_PASS':'Independent CURRENT_ACCEPTED point and full terminal review, not NATIVE_EXIT alone, establish acceptance.',
    'instructions':point['instructions'],'cycles':point['cycles'],'physical_slices':point['physical_slices'],
    'point_ref':pointref,'independent_terminal_ref':reviewref,'input_audit_ref':auditref,'accepted_result_pointer':item['accepted_results'][attempt['attempt_id']]},
 'campaign_preservation':{'original_T0':item['t0_unix'],'actual_starts':57,'controller_state':'STOPPED','Goal_remains':'PAUSED','registry_sha256_before_after':sha(reg_bytes),'registry_unchanged':True,'new_application_starts':0},
 'reader_disposition':reader_report,
 'excluded':'raw.log, binary/archive, run_status, terminal_summary, traces/oracles and all other source files. Directory records are descriptive, not copy authorization for other children.',
 'target_requirements':['T independently verifies synthetic-test and new-transaction/single-stream conditions before real copy.',
 'Copy exactly the five listed relative paths without source rename/unlink/chmod/chown/utime, and retain source/canonical references.',
 'Destination must independently verify full bytes/SHA, exact path mapping, numeric uid/gid/mode/mtime and directories or report any unsupported metadata restoration without claiming PASS.',
 'Destination inode/device are expected to be target-specific: record them independently rather than pretending source inode/device were preserved.',
 'Owner E2 must independently reconfirm source identities and accepted scientific references after the copy; no source release is granted by COPY_READY or target PASS.'],
 'BA_boundary':'E2 does not own or sign DTC-L1 AD_GEMM RUN_START/RUN_TERMINAL/ACTUAL_PRODUCER_BINDING/STRICT; BA must independently issue its own exact COPY_READY.'}
DEST.mkdir()
def save(name,v):
 (DEST/name).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
save('COPY_READY.json',ready);save('READER_REVIEW.json',reader_report)
(DEST/'FILES_FROM.txt').write_text(''.join(x['relative_path']+'\n' for x in files))
(DEST/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['relative_path']+'\n' for x in files))
save('OWNER_REVIEW.json',{'status':'E2_OWNER_INDEPENDENT_COPY_READY_SOURCE_KEEP','owner':'E2','at_utc':STAMP,
 'copy_ready_sha256':sha((DEST/'COPY_READY.json').read_bytes()),'exact_five_current_SHA_match_historical_accepted_evidence':True,
 'stat_directory_reader_and_registry_stable_check':'PASS at inventory time; fresh T recheck remains required',
 'accepted_point_commit':'28c4c97b5083d8f21ef3eae09a8d962b5944cfd3','prior_final_pause_commit':'acfd1983b1c954ad7d42e7659d11f813a4045712',
 'source_keep_no_transport_no_new_run_no_registry_change':True,'not_a_GPG_signature':'Owner review recorded by E2 Git publication; T cannot sign on E2 behalf',
 'no_BA_signature_or_target_verification_claim':True})
(DEST/'README.md').write_text('E2 independently offers E057 NATIVE_EXIT.json and config-0/1/2/3.config as exact COPY_READY, SOURCE_KEEP throughout.\n\nCOPY_READY.json contains per-file original accepted SHA and current full stat, source directory records, accepted point/native exit distinction, and current/planned reader disposition. FILES_FROM.txt and SHA256SUMS describe the exact five-file transfer scope relative to /workspace/ep_l2_ms20261019_e_results. No raw, binary, full-result restore, source release or application start is authorized by this receipt.\n\nT must use a new transaction and a single transfer stream after its synthetic and independent admission checks; independently verify the destination and report target-specific device/inode and full metadata. E2 must reconfirm source identities and existing scientific references after copy. Original sources remain canonical and retained.\n\nE2 Goal remains PAUSED, actual starts57 and original controllerSTOPPED. DTC-L1 AD_GEMM four sidecars require a separately signed BA COPY_READY; this E2 receipt does not cover them.\n')
# Publish the small reproducible owner inventory tool; do not copy the five data files.
import shutil
shutil.copyfile(Path(__file__),DEST/'prepare_copy_ready.py')
print(json.dumps({'status':'COPY_READY_PREPARED_PENDING_GIT_PUBLICATION','path':str(DEST),'file_count':5,'source_bytes':ready['total_source_bytes'],'source_allocated_bytes':ready['total_allocated_bytes'],'readers':len(readers),'access_gaps':len(gaps),'registry_unchanged':True,'SOURCE_KEEP':True},indent=2))
