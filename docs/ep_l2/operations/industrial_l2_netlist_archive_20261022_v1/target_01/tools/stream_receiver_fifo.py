
"""Sole finite Target receiver: stdin -> independent gzip chunks on genuine164.
No Share payload staging, no native restore claim, no scientific source writes.
"""
import pathlib,json,os,sys,hashlib,gzip,fcntl,time
import v9_transaction as v
import chunk_codec_adapter_v2 as a
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');T=B/'INDUSTRIAL_L2_9JSON_20261022_TARGET';P=json.loads((T/'TRANSFER_PLAN.json').read_bytes());M=json.loads((T/'TRANSACTION_MANIFEST_NORMALIZED.json').read_bytes());S=json.loads((B/'INDUSTRIAL_L2_9JSON_20261022_SOURCE/SOURCE_FROZEN_MANIFEST.json').read_bytes())
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]';assert a.scope(M)==S['transaction_id']==P['transaction_id'];lock=(B/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
root=pathlib.Path(M['destination_path_on_174new']);arc=a.Archive(root,M);os.nice(19)
def event(x):print(json.dumps(x),flush=True)
def gates():
 v.mount_identity(root);m=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;sv=os.statvfs('/root/share');assert m>=64*1024**3 and sv.f_bavail*sv.f_frsize>=40*1024**3;return dict(MemAvailable=m,Share_available=sv.f_bavail*sv.f_frsize)
skip=set(json.loads((T/'SKIP_VERIFIED_CHUNKS.json').read_bytes())['keys']);records=[json.loads(p.read_bytes()) for p in (root/'chunks').glob('*.json')];total=sum(r['raw_size'] for r in records);start=time.monotonic()
for row in S['files']:
 for c in row['chunks']:
  if row['file_id']+':'+str(c['offset']) in skip:continue
  g=gates();name=row['relative_path'];off=c['offset'];n=c['length'];key=arc.key(name,off);final=root/'chunks'/(key+'.gz');partial=root/'chunks'/(key+'.gz.partial');assert not partial.exists() and not final.exists();raw_hash=hashlib.sha256();left=n
  with partial.open('xb') as out:
   with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=1,mtime=0) as gz:
    while left:
     b=sys.stdin.buffer.read(min(1024**2,left));assert b,'SOURCE_STREAM_EOF';gz.write(b);raw_hash.update(b);left-=len(b);total+=len(b);arc.throttle(len(b))
   out.flush();os.fsync(out.fileno())
  assert raw_hash.hexdigest()==c['raw_sha256'],'STREAM_RAW_SHA_MISMATCH'
  for b in arc.iter_chunk(partial,c['raw_sha256'],n):pass
  zsha=v.hash_file(partial,throttle=arc.throttle);v.rename_noreplace(partial,final)
  r=dict(txid=arc.txid,relative_path=name,offset=off,raw_size=n,raw_sha256=c['raw_sha256'],codec=arc.codec,chunk_file=final.name,compressed_size=final.stat().st_size,compressed_sha256=zsha)
  v.exclusive_json(root/'chunks'/(key+'.json'),r);records.append(r);gates();event(dict(event='CHUNK_VERIFIED',file_id=row['file_id'],offset=off,bytes_received=total,compressed_bytes=sum(x['compressed_size'] for x in records),resource=g))
 event(dict(event='FILE_CHUNKS_DURABLE',file_id=row['file_id'],bytes_received=total))
assert not sys.stdin.buffer.read(1),'EXTRA_SOURCE_BYTES';seal=arc.seal();receipt=dict(status='ARCHIVE_VERIFIED',transaction_id=arc.txid,source_manifest_sha256=P['source_manifest_sha256'],files=9,logical_bytes=total,chunks=len(records),compressed_bytes=sum(r['compressed_size'] for r in records),all_whole_original_SHA_equal=True,chunk_close_reopen_and_decoded_raw_SHA=True,native164_restore='NOT_EXECUTED_USER_SIMPLIFIED_ARCHIVE_ONLY',source_action='SOURCE_KEEP',source_reclaimed_bytes=0,elapsed_seconds=time.monotonic()-start)
v.exclusive_json(root/'ARCHIVE_VERIFIED.json',receipt);v.exclusive_json(root/'TRANSACTION_CHUNK_INDEX.json',records);event(dict(event='ARCHIVE_VERIFIED',receipt=receipt))
