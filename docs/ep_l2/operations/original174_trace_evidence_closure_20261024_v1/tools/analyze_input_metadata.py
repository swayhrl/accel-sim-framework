from closure_local import *
import posixpath,collections,re
current=load(R/'evidence/P0_P1_EXACT_SOURCE_MEMBER_AND_COMMANDLIST_AUDIT.json')['roots']
owner=load(R/'owner/EP_MAIN_CURRENT_EXACT_INPUT_INDEX.json')['document']
omap={r['path']:r for r in owner if r['host']=='174'}
out=[]
for r in current:
 names={m['path']:m for m in r['members'] if m.get('type')=='file'};syms={m['path']:m for m in r.get('symlinks',[])}
 c=[]
 for e in r.get('commandlists',[]):
  lines=e['ordered_kernel_lines'];missing=[];empty=[];matched=[]
  for line in lines:
   if line.startswith('/') or '..' in line.split('/'):missing.append(dict(member=line,reason='EXTERNAL_OR_UNSAFE_MEMBER_REFERENCE_NEEDS_OWNER'));continue
   p=posixpath.normpath(posixpath.dirname(e['path'])+'/'+line)
   if p not in names:missing.append(dict(member=line,reason='NOT_A_REGULAR_FILE_IN_CURRENT_TREE',symlink=p in syms))
   elif names[p]['size']<=0:empty.append(line)
   else:matched.append(p)
  o=omap.get(e['path']);c.append(dict(commandlist=e['path'],relative_path=e['relative_path'],sha256=e['sha256'],ordered_kernel_members=lines,kernel_launches=len(lines),missing_members=missing,empty_members=empty,regular_nonzero_metadata_complete=bool(lines) and not missing and not empty,stage='PROCESSED_SIMULATOR_ENTRY' if e['path'].endswith('kernelslist.g') else 'ORIGINAL_CAPTURE_LIST_DISTINCT_STAGE',owner_EP_MAIN_current_record=o,owner_commandlist_sha_matches=bool(o and o['commandlist_sha256']==e['sha256']),member_paths=matched))
 processed=[p for p in c if p['stage']=='PROCESSED_SIMULATOR_ENTRY']
 good=[p for p in processed if p['regular_nonzero_metadata_complete']]
 out.append(dict(source_root=r['path'],commands=c,processed_entry_count=len(processed),processed_metadata_complete_count=len(good),owner_bound_entry_count=sum(p['owner_commandlist_sha_matches'] for p in good),input_presence_state='PACKAGE_CONTENTS_NOT_REINDEXED' if r['asset_kind']=='COMPRESSED_PACKAGE_FILE' else 'CURRENT_PROCESSED_MEMBERS_COMPLETE' if good and len(good)==len(processed) else 'INPUT_METADATA_INCOMPLETE_OR_NO_PROCESSED_ENTRY',scientific_qualification='METADATA_ONLY_NOT_NEW_RUNTIME_SCIENTIFIC_ACCEPTANCE',owner_refs='0bc1aa9f3bfb3cceccdea32af4af668037769027:EXACT_INPUT_INDEX.json.gz'))
save('evidence/EXACT_INPUT_ORDER_MEMBER_PRESENCE_AND_LATEST_OWNER_BINDINGS.json',out)
print('states',collections.Counter(r['input_presence_state'] for r in out));print('incomplete',[(r['source_root'],r['processed_entry_count'],r['processed_metadata_complete_count']) for r in out if r['input_presence_state']=='INPUT_METADATA_INCOMPLETE_OR_NO_PROCESSED_ENTRY'])
