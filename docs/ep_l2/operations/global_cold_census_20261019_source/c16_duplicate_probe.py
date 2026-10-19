import os,json,hashlib
from pathlib import Path
O=Path(__file__).parent; out=[]
for pkg in ['P2','P3']:
 root=Path('/workspace/c16_exchange/autodl_wave1/outbound')/('C16_GPU_PACKAGE_'+pkg+'_168c9714'); receipt=root/(pkg+'_LOCAL_MATERIALIZATION_RECEIPT.json'); b=receipt.read_bytes(); j=json.loads(b)
 for r in j['rows']:
  if not r.get('destination_relpath','').endswith('.safetensors'): continue
  dest=root/r['destination_relpath']; dep,fn=r['artifact_id'].split(':',1); sp=Path('/workspace/c16_assets/c16-a/download_logs/immutable_verified_receipts')/dep/(fn+'.json')
  if not sp.exists(): out.append(dict(destination=str(dest),status='SOURCE_RECEIPT_NOT_FOUND')); continue
  sb=sp.read_bytes(); sj=json.loads(sb); src=Path(sj['local_path']); row=dict(destination=str(dest),source=str(src),package_receipt=str(receipt),package_receipt_sha256=hashlib.sha256(b).hexdigest(),source_receipt=str(sp),source_receipt_sha256=hashlib.sha256(sb).hexdigest(),prior_payload_sha256=r['sha256'],prior_receipts_sha_match=r['sha256']==sj['sha256'],current_content_hashed=False,archive164_restore_evidence='NOT_FOUND_IN_REVIEWED_V9_TLS_INDEX',release_authority='NOT_GRANTED')
  for label,p in [('source',src),('destination',dest)]:
   s=p.lstat(); row[label+'_stat']=dict(device=s.st_dev,inode=s.st_ino,size=s.st_size,allocated_bytes=s.st_blocks*512,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid)
  row['same_inode']=row['source_stat']['device']==row['destination_stat']['device'] and row['source_stat']['inode']==row['destination_stat']['inode']; row['current_sizes_match_prior']=row['source_stat']['size']==row['destination_stat']['size']==r['size_bytes']==sj['expected_size_bytes']; out.append(row)
json.dump(dict(status='HISTORICAL_LOCAL_DUPLICATE_PROPOSAL_ONLY_NOT_TRUE164_RECOVERY',shards=out,shard_allocated_upper_bound=sum(r.get('destination_stat',{}).get('allocated_bytes',0) for r in out),current_guaranteed_releasable_bytes=0),open(O/'SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json','w'),indent=2)
print(len(out),'shards',sum(r.get('destination_stat',{}).get('allocated_bytes',0) for r in out)/2**30,'GiB','matches',sum(r.get('prior_receipts_sha_match',False) and r.get('current_sizes_match_prior',False) for r in out))
