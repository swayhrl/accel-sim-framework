from exec_local import *
sc=load(R/'FROZEN_AUTHORIZED_EXECUTION_SCOPES.json')['scopes']
for alias in ['hrl','hrl-174-new']:
 req=[dict(asset_id=x['asset_id'],root=x['source_root'],files=x['files'],kind=x['kind']) for x in sc if x['source_alias']==alias]
 code='import os,json,stat,time,pathlib\nreq='+repr(req)+r'''
out=[];total=0
for row in req:
 root=row['root'];allow=('/workspace/','/root/share/accel-sim/','/root/share/workspace_migrated_20260905/','/root/workspace/')
 if not root or not root.startswith(allow) or '..' in pathlib.Path(root).parts:out.append(dict(asset_id=row['asset_id'],status='ROOT_IDENTITY_HOLD'));continue
 z=dict(asset_id=row['asset_id'],source_root=root,source_realpath=os.path.realpath(root),namespace=os.readlink('/proc/self/ns/mnt'),regular_files_checked=0,logical_bytes=0,matching_frozen_identity_files=0,identity_mismatches=[],source_payload_bytes_read=0)
 for f in row['files']:
  rel=f['relative_path'];p=pathlib.Path(root)/rel
  if pathlib.Path(rel).is_absolute() or '..' in pathlib.Path(rel).parts:z['identity_mismatches'].append(dict(path=rel,reason='UNSAFE_RELATIVE'));continue
  try:
   s=p.lstat();actual=dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode));expected={k:f.get(k) for k in actual}
   if isinstance(expected['mode'],str):expected['mode']=int(expected['mode'],8)
   z['regular_files_checked']+=1;z['logical_bytes']+=s.st_size
   if stat.S_ISREG(s.st_mode) and all(actual[k]==expected[k] for k in actual):z['matching_frozen_identity_files']+=1
   else:z['identity_mismatches'].append(dict(path=str(p),actual=actual,expected=expected))
  except OSError as e:z['identity_mismatches'].append(dict(path=str(p),error=str(e)))
 z['status']='CURRENT_FROZEN_FILE_IDENTITIES_MATCH' if not z['identity_mismatches'] else 'PRECISE_SOURCE_IDENTITY_HOLD';out.append(z);total+=z['regular_files_checked']
print(json.dumps(dict(unix=time.time(),host=os.uname().nodename,scopes=out,total_metadata_files=total,Source_payload_read_bytes=0,no_sha_or_sender_started=True)))
'''
 x=remote(alias,code,80);save('readonly/'+('ORIGINAL_SOURCE' if alias=='hrl' else 'NATIVE_Q05')+'_CURRENT_REGISTERED_FILE_IDENTITY_PREPARATION.json',x);print(alias,'scopes',len(x['scopes']),'files',x['total_metadata_files'],'matching scopes',sum(r['status']=='CURRENT_FROZEN_FILE_IDENTITIES_MATCH' for r in x['scopes']))
