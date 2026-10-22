
"""Normalize immutable Source evidence without rehashing scientific originals.
Source industrial canonical(no newline) txid retained; V9 used as control pattern.
"""
import hashlib,json,stat
import v9_transaction as v
from chunk_codec_adapter import scope,NATIVE_PREFIX
SOURCE_PREFIX='/workspace/repos/gpu-l2-cache-verilog/build/'
def normalize(source_raw,dirs_raw):
 s=json.loads(source_raw);ds=json.loads(dirs_raw)
 v.require(s['status']=='SOURCE_FROZEN_SOURCE_KEEP' and s['source_disposition']=='SOURCE_KEEP' and s['source_release_authorized_bytes']==0,'Source not frozen KEEP')
 v.require(v.digest(dirs_raw)==s['source_directory_metadata_sha256'],'directory raw SHA binding')
 original_selector=json.dumps(s['files'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 v.require(v.digest(original_selector)==s['selector_sha256'],'Source selector SHA')
 native=s['proposed_native164_root_not_reserved'];v.require(native.startswith(NATIVE_PREFIX),'Source destination outside currentGoal')
 files=[]
 for r in s['files']:
  n=r['relative_path'];v.relpath(n);i=r['identity'];v.require(r['absolute_path']==SOURCE_PREFIX+n and stat.S_ISREG(i['mode']) and i['nlink']==1,'file path/type/link')
  row=dict(relative_path=n,type='regular',sha256=r['sha256'],**{k:i[k] for k in ['dev','inode','nlink','uid','gid','size','mtime_ns','ctime_ns']},mode=stat.S_IMODE(i['mode']),allocated=i['allocated_bytes'])
  off=0
  for c in r['chunks']:
   v.require(c['offset']==off and 0<c['length']<=128*1024**2 and len(c['raw_sha256'])==64,'Source raw chunk coverage/cap')
   off+=c['length']
  v.require(off==i['size'],'Source incomplete chunks');files.append(row)
 dirs=[]
 for d in ds:
  v.require(stat.S_ISDIR(d['mode']),'directory type')
  dirs.append(dict(relative_path=d['relative_path'],type='directory',**{k:d[k] for k in ['dev','inode','nlink','uid','gid','size','mtime_ns','ctime_ns']},mode=stat.S_IMODE(d['mode']),allocated=d['allocated_bytes']))
 m=dict(source_filesystem_identity=json.dumps(s['transaction_binding']['source_fs_id'],sort_keys=True,separators=(',',':')),source_root=s['source_root'],source_frozen_commit=s['source_git_head'],selector_sha256=v.digest(v.canonical(files)),source_selector_sha256=s['selector_sha256'],genuine164_destination_root=native,destination_path_on_174new=native.replace('/home/shared','/root/share/mnt164',1),files=files,directories=dirs,source_file_inventory_sha256=v.digest(v.canonical(files)),source_directory_inventory_sha256=v.digest(v.canonical(dirs)),source_originals_action='SOURCE_KEEP_NO_RELEASE_AUTHORITY',original_source_manifest_sha256=v.digest(source_raw),original_source_directory_sidecar_sha256=v.digest(dirs_raw),original_source_binding=s['transaction_binding'],source_transaction_id=s['transaction_id'])
 v.require(scope(m)==s['transaction_id'],'Source txid not retained')
 return m
