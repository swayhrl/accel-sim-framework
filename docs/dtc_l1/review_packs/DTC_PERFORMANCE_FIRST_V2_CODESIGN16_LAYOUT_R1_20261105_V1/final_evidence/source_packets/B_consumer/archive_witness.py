"""Read-only archive witness functions reused byte-for-byte from qualified old48 adapter.
No model/archive mutator imports. Per-call namespace is isolated.
"""
import pathlib,json,hashlib,os,subprocess,types
P=pathlib.Path
SOURCE_DEV=2128;ARCHIVE_DEV=39;RESTORE_DEV=2128

def require(v,msg):
 if not v:raise ValueError(msg)

def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()

def hashbytes(b):return hashlib.sha256(b).hexdigest()

def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def get(p):
 p=P(p);b=p.read_bytes();return json.loads(b),{'path':str(p),'sha256':hashbytes(b)}

def exact_safe(root,relative):
 root=P(root);q=P(relative)
 require(not q.is_absolute() and '..' not in q.parts,'UNSAFE_MANIFEST_RELATIVE_PATH')
 out=root/q
 require(out.parent.resolve().is_relative_to(root.resolve()) or out==root,'MANIFEST_PARENT_ESCAPE')
 return out

def verify_restore_rows(manifest,proof,restore_root):
 require(len(proof['rows'])==len(manifest['entries']),'RESTORE_PROOF_ROW_COUNT')
 rows={x['path']:x for x in proof['rows']};require(len(rows)==len(proof['rows']),'RESTORE_PROOF_DUPLICATE_PATH')
 for e in manifest['entries']:
  p=exact_safe(restore_root,e['path']);v=rows[e['path']];require(v['type']==e['type'],'RESTORE_TYPE_DISAGREES')
  require(v['identity']['dev']==RESTORE_DEV and p.lstat().st_dev==RESTORE_DEV,'RESTORE_NOT_NATIVE_DEVICE')
  if e['type']=='file':
   require(p.is_file() and not p.is_symlink(),'RESTORE_REGULAR_FILE_REQUIRED')
   require(p.stat().st_size==e['size'] and v['sha256']==e['sha256']==sha(p),'RESTORE_FILE_SIZE_SHA_MISMATCH:'+e['path'])
  elif e['type']=='directory':require(p.is_dir() and not p.is_symlink(),'RESTORE_DIRECTORY_MISMATCH')
  elif e['type']=='symlink':require(p.is_symlink() and os.readlink(p)==e['target']==v['target'],'RESTORE_ALIAS_MISMATCH')
  else:raise ValueError('UNSUPPORTED_RESTORE_MEMBER_TYPE')

def verify_archive(c,result,out,done,successful,ctx,check_mount=True):
 a=result['archive'];receipt=a['receipt'];local,rr=get(R/'control'/(c+'_ARCHIVE_RECEIPT.json'));require(local==receipt,'LOCAL_RECEIPT_DIFFERS_FROM_RESULT')
 require(receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['cohort']==c,'ARCHIVE_RECEIPT_STATUS_IDENTITY')
 require(receipt['source_disposition']=='SOURCE_KEEP' and receipt['source_release_bytes']==0 and receipt['scientific_acceptance_granted_by_archive'] is False,'ARCHIVE_IS_NOT_SCIENTIFIC_ACCEPTANCE')
 target=P(receipt['target_mount_path']);restore=P(receipt['native_restore']);tx=receipt['txid']
 require(out.stat().st_dev==SOURCE_DEV and target.stat().st_dev==ARCHIVE_DEV and restore.stat().st_dev==RESTORE_DEV,'QUALIFIED_SOURCE_ARCHIVE_RESTORE_TIER_MISMATCH')
 require(target==NAS/c/tx and restore==R/'DTC/run/recovery'/tx,'ARCHIVE_OR_RESTORE_NAMESPACE_ESCAPE')
 require(receipt['true164_root']==str(target).replace('/root/share/mnt164','/home/shared',1),'TRUE164_RECEIPT_ROOT_MISMATCH')
 if check_mount:
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(target)],text=True))['filesystems'][0]
  require(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','TRUE164_ACTUAL_MOUNT_MISMATCH')
 arc_receipt,ar=get(target/'RECEIPT.json');require(arc_receipt==receipt,'ARCHIVE_LOCAL_RECEIPT_DISAGREES')
 manifest,mr=get(target/'SOURCE_MANIFEST.json');index,ir=get(target/'ARCHIVE_INDEX.json');commit,cr=get(target/'COMMIT.json');proof,pr=get(target/'RESTORE_VERIFIED_NATIVE_TARGET.json')
 require(manifest['cohort']==c and manifest['txid']==tx and manifest['source_root']==str(out),'ARCHIVE_MANIFEST_IDENTITY')
 require(manifest['scientific_status']==receipt['scientific_status']==(STRICT_STATUS if successful else 'STOP_UNACCEPTED'),'ARCHIVE_SCIENTIFIC_STATUS_DISAGREES')
 require(manifest['native_execution_receipt_sha256']==sha(out/'NATIVE_EXIT.json'),'MANIFEST_NATIVE_EXIT_SHA_MISMATCH')
 require(receipt['manifest_sha256']==commit['manifest_sha256']==hashbytes(canon(manifest)),'MANIFEST_CANONICAL_SHA_MISMATCH')
 require(commit['archive_index_sha256']==hashbytes(canon(index)) and commit['txid']==tx,'ARCHIVE_COMMIT_INDEX_SHA_MISMATCH')
 require(proof['txid']==tx,'RESTORE_PROOF_TXID_MISMATCH')
 require(index['archive_sha256']==receipt['archive_sha256'] and index['archive_bytes']==receipt['archive_bytes'],'ARCHIVE_INDEX_RECEIPT_SHA_SIZE_MISMATCH')
 total=0;stream=hashlib.sha256()
 for ch in index['chunks']:
  require(ch['offset']==total and ch['txid']==tx,'ARCHIVE_CHUNK_OFFSET_OR_TXID')
  p=exact_safe(target/'chunks',ch['name']);require(p.is_file() and not p.is_symlink()and p.stat().st_dev==ARCHIVE_DEV,'ARCHIVE_CHUNK_REGULAR_164_FILE_REQUIRED');require(p.stat().st_size==ch['size'],'ARCHIVE_CHUNK_SIZE')
  part=hashlib.sha256()
  with p.open('rb') as h:
   for b in iter(lambda:h.read(1024*1024),b''):part.update(b);stream.update(b)
  require(part.hexdigest()==ch['sha256'],'ARCHIVE_CHUNK_SHA_MISMATCH');total+=ch['size']
 require(total==index['archive_bytes'] and stream.hexdigest()==index['archive_sha256'],'ARCHIVE_STREAM_SHA_SIZE_MISMATCH')
 verify_restore_rows(manifest,proof,restore)
 entries={x['path']:x for x in manifest['entries']};require(len(entries)==len(manifest['entries']),'MANIFEST_DUPLICATE_MEMBER')
 critical=['NATIVE_EXIT.json','DOWNSTREAM_FROZEN_SPEC.json','DISPATCH_BINDING.json','raw.log.gz']+(['L2_STRICT.json'] if successful else [])
 for n in critical:
  require(n in entries and entries[n]['type']=='file' and entries[n]['sha256']==sha(out/n),'SOURCE_CRITICAL_MEMBER_MISMATCH:'+n)
 require(entries['raw.log.gz']['sha256']==done['raw_sha256'],'MANIFEST_RAW_GZIP_SHA_MISMATCH')
 require(a.get('independently_verified_entries')==len(manifest['entries']),'RESULT_ARCHIVE_ENTRY_VERIFICATION_COUNT')
 require(a.get('archive_overlay_sha256')==ctx['outbox_sha256'],'RESULT_ARCHIVE_OVERLAY_SOURCE_MISMATCH')
 return {'ARCHIVE_RECEIPT':rr,'NATIVE_RESTORE':pr},{'archive_receipt':ar,'source_manifest':mr,'archive_index':ir,'commit':cr,'native_restore':pr,'archive_stream_sha256':stream.hexdigest(),'native_restored_entries_verified':len(manifest['entries']),'critical_source_members':critical}

def verify_for(root,nas,strict_status,cohort,result,out,done,successful,outbox_sha,check_mount=True):
 env=dict(globals(),R=P(root),NAS=P(nas),STRICT_STATUS=strict_status)
 for name in ['verify_restore_rows','verify_archive']:
  original=globals()[name];f=types.FunctionType(original.__code__,env,name,original.__defaults__);env[name]=f
 return env['verify_archive'](cohort,result,P(out),done,successful,{'outbox_sha256':outbox_sha},check_mount=check_mount)
