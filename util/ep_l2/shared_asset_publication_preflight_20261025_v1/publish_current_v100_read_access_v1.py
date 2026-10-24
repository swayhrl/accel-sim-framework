from pathlib import Path
import sys,json,hashlib,os,re,time,collections,stat
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');NAS=Path('/root/share/mnt164/huangrulin/traces')
sys.path.insert(0,str(R/'tools'));import library_copy as e
gate=e.Resources();gate(True);v=e.v9()
raw=(R/'control/ALL_BUNDLES.json').read_bytes();bs=json.loads(raw);objs=json.loads((R/'control/ALL_OBJECTS.json').read_text())
old=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())['assets']
batch={}
for o in objs.values():
 bid=o['storage'].get('batch_id')
 if bid not in batch:
  batch[bid]=not bid or (NAS/'bundles/_payload'/bid/'COMMIT.json').is_file()
ready=[b for b in bs if all(batch[objs[m['sha256']]['storage'].get('batch_id')]for m in b['members'])]
os.chdir('/root/data/dtc_main_20261023_v1')
checks={};assets=[];excluded=[];seen=0
for b in ready:
 versions=set();object_rows=[]
 for m in b['members']:
  h=m['sha256'];o=objs[h];p=Path(o['storage']['path'])
  if h not in checks:
   gate();s=p.stat();assert p.is_file()and s.st_size==o['size']==m['size'];assert p.resolve().is_relative_to(NAS.parent.resolve())
   historical_identity_drift='expected_identity'in o['storage'] and [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]!=o['storage']['expected_identity']
   if historical_identity_drift:assert [s.st_dev,s.st_size,s.st_mtime_ns]==[o['storage']['expected_identity'][i]for i in [0,2,3]],'Drift beyond FUSE inode requires HOLD'
   with p.open('rb')as f:first=f.read(min(4096,s.st_size));f.seek(max(0,s.st_size-32));f.read(32)
   with p.open('rb')as f:assert f.read(min(64,s.st_size))==first[:64]
   is_command=m['relative_path']=='kernelslist.g'
   if is_command:assert hashlib.sha256(p.read_bytes()).hexdigest()==h
   match=re.search(rb'^-binary version\s*=\s*(\d+)\s*$',first,re.M)
   checks[h]={'sha256':h,'bytes':s.st_size,'storage_path':str(p),'sealed_identity':[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns],'observed_binary_version':match.group(1).decode()if match else None,'open_seek_reopen':True,'fresh_full_body_SHA_recomputed':is_command,'prior_closed_full_SHA_from_copy_commit':True,'storage_batch_id':o['storage'].get('batch_id'),'historical_FUSE_inode_drift':historical_identity_drift,'fresh_reuse_full_SHA_revalidation_pending':historical_identity_drift}
   seen+=1
   if seen%2000==0:print(json.dumps({'checked_objects':seen,'checked_candidate_inputs':len(assets),'unix':time.time()}),flush=True)
  row=checks[h];object_rows.append(row)
  if m['relative_path']!='kernelslist.g':versions.add(row['observed_binary_version'])
 if versions!={'70'}:
  excluded.append({'bundle_id':b['bundle_id'],'suite':b['suite'],'program':b['program'],'versions':list(versions),'reason':'Not all declared kernel headers proveSM70'});continue
 tree=NAS/'bundles'/b['bundle_id']/'tree';tree.mkdir(parents=True,exist_ok=True)
 for m in b['members']:
  dest=e.safe(tree,m['relative_path']);target=Path(objs[m['sha256']]['storage']['path']);dest.parent.mkdir(parents=True,exist_ok=True)
  if os.path.lexists(dest):assert dest.is_symlink()and dest.resolve()==target.resolve()
  else:dest.symlink_to(os.path.relpath(target,dest.parent))
  assert dest.is_file()and dest.stat().st_size==m['size']
  with dest.open('rb')as f:f.read(1)
 entry=tree/'kernelslist.g';cmd=next(m for m in b['members']if m['relative_path']=='kernelslist.g');assert hashlib.sha256(entry.read_bytes()).hexdigest()==cmd['sha256']
 alias=b.get('prior_asset_aliases',[]);prior=[a for a in old if set(a['aliases']).intersection(alias)]
 assets.append({'bundle_id':b['bundle_id'],'suite':b['suite'],'source_version_evidence':b['version'],'program':b['program'],'extent':b['extent'],'kind':'fraction'if b['extent']=='FRACTION_OR_TRIM_PATH'else'regular_capture_completeness_not_newly_certified','architecture':'SM70','kernel_launches':len(b['ordered_kernel_members']),'logical_bytes':sum(m['size']for m in b['members']),'trace_directory':str(tree).replace(str(NAS),'/root/workspace/assets/traces',1),'trace_entry':str(entry).replace(str(NAS),'/root/workspace/assets/traces',1),'commandlist_sha256':cmd['sha256'],'members':b['members'],'prior_asset_aliases':alias,'prior_scientific_contexts':[{k:a[k]for k in ['asset_id','scientific_contexts']}for a in prior],'source_aliases':b['source_aliases'],'data_status':'CURRENT_READABLE_SM70_PRIOR_COPY_SHA_FUSE_SELECTOR_REVALIDATION_PENDING'if any(r['historical_FUSE_inode_drift']for r in object_rows)else'CLOSED_COMMITTED_CONTENT_AND_CURRENT_ALL_MEMBERS_READABLE','scientific_qualification_granted':False})
used={m['sha256']for a in assets for m in a['members']}
body={'schema':'AVAILABLE_V100_SM70_ACCESS_SNAPSHOT_V1','status':'CURRENT_READ_ACCESS_SNAPSHOT_NOT_FINAL_LIBRARY_OR_SCIENCE_ACCEPTANCE','access_scope':'ALL_PROJECTS_IN_174NEW_NAMESPACE','observed_unix':time.time(),'checked_from_cwd':'/root/data/dtc_main_20261023_v1','all_plan_inputs':len(bs),'committed_content_candidate_inputs':len(ready),'available_inputs':len(assets),'remaining_uncommitted_input_bundles':len(bs)-len(ready),'header_exclusions':excluded,'source_plan_sha256':hashlib.sha256(raw).hexdigest(),'assets':sorted(assets,key=lambda a:(a['suite'],a['program'],a['bundle_id'])),'objects':{h:checks[h]for h in sorted(used)},'full_body_integrity_basis':'Existing closed complete-source and true164 fullSHA COPY receipts; current check reads headers/tails/reopen and hashes commandlists only. Independent all-object full Native restore remains pending in the whole Goal.','new_scientific_starts':0,'source_payload_writes':0,'source_release_bytes':0,'consumer_or_budget_qualification_granted':False,'final_catalog_CURRENT_changed':False,'common_trace_assets_CLI_not_yet_published':True,'FUSE_identity_limit':'Historical inode-only drift is recorded, not accepted by old identity validator. This index proves current direct member-path reads/SM70 headers and retains prior closed COPY fullSHA. Re-importing such an input requires current fullSHA verification; separate20-asset readback is in progress. No old catalog or validator was changed.'}
payload=(json.dumps(body,indent=2,sort_keys=True)+'\n').encode();dst=NAS/'catalog/AVAILABLE_V100_SM70_20261025_V1.json'
e.publish_bytes(dst,payload,v)
local=R/'control/AVAILABLE_V100_SM70_20261025_V1.json';e.publish_bytes(local,payload,v)
summary={'status':body['status'],'available_inputs':len(assets),'all_plan_inputs':len(bs),'unique_objects_checked':len(used),'available_member_references':sum(len(a['members'])for a in assets),'header_exclusions':excluded,'by_suite':{s:{'inputs':sum(a['suite']==s for a in assets),'programs':sorted(set(a['program']for a in assets if a['suite']==s)),'extent_counts':dict(collections.Counter(a['extent']for a in assets if a['suite']==s))}for s in sorted(set(a['suite']for a in assets))},'public_index':'/root/workspace/assets/traces/catalog/AVAILABLE_V100_SM70_20261025_V1.json','index_sha256':hashlib.sha256(payload).hexdigest(),'index_bytes':len(payload),'all_member_views_opened_from_DTC_cwd':True,'inputs_requiring_fresh_FUSE_selector_revalidation':sum(a['data_status']=='CURRENT_READABLE_SM70_PRIOR_COPY_SHA_FUSE_SELECTOR_REVALIDATION_PENDING'for a in assets),'final_goal_complete':False}
e.publish_bytes(R/'control/AVAILABLE_V100_SM70_ACCESS_PUBLICATION_V1.json',(json.dumps(summary,indent=2)+'\n').encode(),v);print(json.dumps(summary),flush=True)
