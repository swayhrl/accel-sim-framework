from closure_local import *
from closure_resources import UTIL
current={r['path']:r for r in load(R/'evidence/P0_P1_EXACT_SOURCE_MEMBER_AND_COMMANDLIST_AUDIT.json')['roots']}
out=[];target_req=[]
for r in load(T/'TRUE164_TRACE_RECOVERY_INDEX.json')['records']:
 m=load(T/r['all_original_numeric_metadata_and_SHA']);c=current[r['source_root']];names={x['relative_path']:x for x in c['members'] if x.get('type')=='file'}
 old={x['relative_path']:x for x in m['members']};missing=[p for p in old if p not in names]
 diffs=[p for p in old if p in names and any(names[p].get(k)!=old[p].get(k) for k in ['dev','inode','size','mtime_ns','ctime_ns'])]
 extras=[v for p,v in names.items() if p not in old]
 o=dict(asset_id=r['asset_id'],source_root=r['source_root'],selector_id=r['selector_id'],object_id=r['object_id'],exact_frozen_member_count=len(old),exact_frozen_member_logical_bytes=r['original_bytes'],current_whole_root_files=c['files'],current_whole_root_logical_bytes=c['logical_bytes'],source_missing=missing,source_identity_differences=diffs,extra_regular_files=extras,extra_logical_bytes=sum(x['size'] for x in extras),source_symlinks=c['symlinks'],source_commandlist_records=c['commandlists'],source_selector_old_full_SHA_reusable=not missing and not diffs,true164_tree=r['true164_tree'],native_restore_status=r['RESTORE_VERIFIED_NATIVE_TARGET'],native_restore_reference=r.get('native_restore_evidence'),old_manifest_reference=r['all_original_numeric_metadata_and_SHA'])
 out.append(o)
 target_req.append(dict(asset_id=r['asset_id'],tree=r['true164_tree'].replace('/home/shared/','/root/share/mnt164/',1),bundle=r.get('true164_bundle'),expected_commit=r.get('actual_target_commit_sha256'),existing_commit=r.get('actual_existing_commit_path'),extras=[x['relative_path'] for x in extras]))
save('evidence/TWENTY_SELECTORS_VS_CURRENT_WHOLE_SOURCE_DIRECTORY_DIFFERENCE.json',out)
code=UTIL+'\nreq='+repr(target_req)+r'''
import hashlib
out=[]
for r in req:
 row=dict(asset_id=r['asset_id'],tree=meta(r['tree']),extra_file_locators=[meta(r['tree']+'/'+p) for p in r['extras']])
 p=r['existing_commit'] or (r['bundle']+'/COMMIT.json' if r['bundle'] else None)
 if p:
  p=p.replace('/home/shared/','/root/share/mnt164/',1);s=meta(p)
  if s.get('type')=='file' and s.get('size',10**9)<131072:
   h=hashlib.sha256(Path(p).read_bytes()).hexdigest();row['current_commit_sha256']=h;row['expected_commit_sha256']=r['expected_commit'];row['current_commit_matches_prior']=h==r['expected_commit']
 out.append(row)
print(json.dumps(out))
'''
save('evidence/TWENTY_TRUE164_CURRENT_COMMITS_AND_EXTRA_FILE_LOCATORS.json',remote('hrl-174-new',code,70))
print('selector exactcurrentreuse',sum(r['source_selector_old_full_SHA_reusable'] for r in out),'extras',sum(len(r['extra_regular_files']) for r in out),'extra_bytes',sum(r['extra_logical_bytes'] for r in out))
