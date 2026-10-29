"""Exact GROUP-only adoption metadata; no F9 re-execution, no closed-group body rehash."""
from pathlib import Path
import os,json,hashlib,re,stat
G=2**30
PINS={'frozen_ordinary_F9.py':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','frozen_parser_f4.py':'f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b','post_feature_tap_v1.py':'a093910fa6c2e0fdb04c2e192094d4c299306fd8749abc9d33558fc09da23194','postprocess_nas_sharded_v4.py':'5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'}
def need(v,m):
 if not v:raise RuntimeError(m)
def raw_meta(S,r):
 p=S.metadata_path(r['path']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and a.st_size==r['bytes']and a.st_size<=8*2**20,'BOUND_REGULAR_PRIOR_JSON')
  chunks=[];n=0
  while True:
   b=os.read(fd,min(65536,r['bytes']+1-n))
   if not b:break
   n+=len(b);need(n<=r['bytes'],'BOUNDED_PRIOR_METADATA');chunks.append(b)
  z=os.fstat(fd);key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);need(key(a)==key(z),'STABLE_PRIOR_META_FD')
 finally:os.close(fd)
 raw=b''.join(chunks);need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'PRIOR_RAW_JSON_SHA')
 return raw
def stat_match(S,path,expected):
 p=S.metadata_path(path);need(not p.is_symlink(),'NO_SOURCE_SYMLINK');s=p.stat();need(stat.S_ISREG(s.st_mode),'REGULAR_KEPT_SOURCE')
 need(all(v==expected[k]for k,v in {'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}.items()),'PRIOR_SHA_PROOF_REQUIRES_UNCHANGED_CURRENT_STAT')
 return p
def canonical_source_map(S,v):
 return {str(S.metadata_path(k)):h for k,h in v['source_files'].items()}
def admission(S,c):
 r=c['group_only_resume'];p=S.pinned(r['Root_resume_admission_ref'])
 need(p['schema']=='ROOT_EXACT_GROUP_ONLY_RESUME_AFTER_OLD_POST_CLOSED_V1'and p['status']=='ROOT_APPROVED_GROUP_ONLY_AFTER_FAILED_OR_EXPIRED_OWNED_CLOSED','ROOT_REAL_PRIOR_TERMINAL_ADMISSION')
 need(p['qid']==c['qid']and p['source_scope_sha256']==c['source_scope_sha256']and p['old_run_success_claimed']is False,'EXACT_OLD_FAILURE_NOT_RELABELED_PASS')
 need(p['old_status']in ['FAILED_RETAINED','EXPIRED_RETAINED'],'NO_HEALTHY_RUN_RESUME')
 need(all(p[k]is True for k in ['old_remote_owned_PIDs_absent_cgroup_empty','old_Native_owners_absent_asset4_released','old_CPU_role_slot_and_IO_released']),'OLD_FULL_OWNED_CLOSE_REQUIRED')
 need(p['old_post_scope_sha256']==r['old_post_scope_sha256']and p['old_run_id']==r['old_run_id'],'EXACT_PRIOR_SCOPE_RUN')
 for k in ['prior_F9_ref','prior_tap_ref','prior_code_manifest_ref','prior_START_ref','prior_RESOURCE_AND_CLOSURE_ref','payload_origin_START_ref','prior_grouped_root','closed_groups','pending_groups']:need(p[k]==r[k],'ROOT_EXACT_PRIOR_REUSE_PIN_'+k)
 start=S.pinned(r['prior_START_ref']);closed=S.pinned(r['prior_RESOURCE_AND_CLOSURE_ref']);mf=S.pinned(r['prior_code_manifest_ref'])
 need(start['scope_sha256']==closed['scope_sha256']==r['old_post_scope_sha256']and start['run_id']==closed['run_id']==r['old_run_id'],'OLD_START_TERMINAL_SCOPE_RUN')
 need(start['code_manifest_sha256']==closed['code_manifest_sha256']==r['prior_code_manifest_ref']['sha256'],'OLD_EXACT_CODE_MF')
 need(start['owner']==closed['owner']and start['boot']==closed['boot']and closed['tracked_children']==[]and closed['canonical_IO_closed_after_owned']is True,'OLD_REAL_RESOURCE_CLOSURE')
 need(start['boot']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'SAME_REMOTE_BOOT')
 who=Path('/proc',str(start['owner'][0]),'stat')
 if who.exists():need(who.read_text().rsplit(')',1)[1].split()[19]!=start['owner'][1],'OLD_OWNER_STILL_LIVE')
 cg=Path(closed['cgroup']);need(cg.is_absolute()and '..'not in cg.parts and cg.is_relative_to('/sys/fs/cgroup'),'OLD_CGROUP_DOMAIN')
 if cg.exists():need(int(dict(x.split()for x in(cg/'cgroup.events').read_text().splitlines())['populated'])==0,'OLD_CGROUP_STILL_POPULATED')
 for n,h in PINS.items():need(mf['files'][n]['sha256']==h,'ORIGINAL_F9_F4_TAP_5D_PIN')
 v=S.pinned(r['prior_F9_ref']);tap=S.pinned(r['prior_tap_ref'])
 need(v['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and v['strict_single_stream_ordinary']is True and v['stream_ids']==[0]and v['kernels']==c['header_count']and v['counts']['sass_records']==c['declared_source_records'],'ALL_RECORDS_PRIOR_F9_CLOSED')
 need(v['map_sha256']==c['metadata_refs']['map']['sha256']and len(v['per_kernel'])==c['header_count']and {k['name']for k in v['per_kernel']}==set(c['command_names']),'ORIGINAL_ALL_KERNEL_SET_MAP')
 need(tap['records']==v['counts']['sass_records'],'SAME_PASS_PRIOR_FEATURE_TAP')
 sources=canonical_source_map(S,v)
 for name in c['command_names']:
  path=stat_match(S,str(Path(c['source_root'])/'traces'/name),c['raw_source_metadata'][name]);need(str(path)in sources,'PRIOR_F9_SOURCE_SHA_COMPLETE_SET')
 closed_names=set(r['closed_groups']);pending=set(r['pending_groups']);need(not(closed_names&pending)and closed_names|pending==set(c['command_names']),'ALL_KERNEL_RESUME_LEDGER_EXACT_PARTITION')
 root=S.metadata_path(r['prior_grouped_root']);origin=S.pinned(r['payload_origin_START_ref']);origin_start_path=S.metadata_path(r['payload_origin_START_ref']['path']);need(root==origin_start_path.parent/c['qid']/'grouped'and root.is_dir()and not root.is_symlink(),'EXACT_ORIGIN_CASE_GROUPED_ROOT_NO_ARBITRARY_TARGET')
 return r,v,tap
def paths(S,c,out,name):
 r=c['group_only_resume'];dest=S.metadata_path(r['prior_grouped_root'])/name.replace('.trace.xz','.traceg.xz')
 if name in r['closed_groups']:work=out/'adopted'/name
 else:
  p=r['pending_groups'][name]
  need(p['mode']in ['CONTINUE_COMPLETE_PARTITION','FRESH_WORK_KEEP_PRIOR_PARTIAL'],'EXACT_PENDING_GROUP_MODE')
  if p['mode']=='CONTINUE_COMPLETE_PARTITION':
   state=S.pinned(p['checkpoint_ref']);need(state['partition_complete']is True,'ONLY_CLOSED_PARTITION_CONTINUE');priorF9=S.pinned(r['prior_F9_ref']);source=S.metadata_path(str(Path(c['source_root'])/'traces'/name));need(state['source_sha256']==canonical_source_map(S,priorF9)[str(source)],'CONTINUE_ONLY_SAME_F9_SOURCE_SHA')
   work=S.metadata_path(p['prior_work_root']);need(S.metadata_path(p['checkpoint_ref']['path'])==work/'CHECKPOINT.json','EXACT_PRIOR_WORK_CHECKPOINT')
  else:work=out/'scratch'/name
 return dest,work
def adopt_group(S,c,out,name,v):
 r=c['group_only_resume'];row=r['closed_groups'][name];gr=S.pinned(row['group_receipt_ref']);state=S.pinned(row['checkpoint_ref'])
 k=next(x for x in v['per_kernel']if x['name']==name);src=S.metadata_path(str(Path(c['source_root'])/'traces'/name));dest,work=paths(S,c,out,name);sources=canonical_source_map(S,v)
 need(gr['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and gr['source_sha256']==sources[str(src)]and gr['records']==k['counts']['sass_records']and gr['ctas']==k['ctas']and gr['warps']==k['warps']and gr['closed_reopened_full_xz_crc']is True,'PRIOR_CLOSED_FULL_GROUP_PROOF')
 need(gr['grouped_sha256']==row['grouped_sha256']and gr['grouped_bytes']==row['grouped_stat']['bytes'],'PRIOR_GROUPED_WHOLESHA_AND_SIZE')
 need(stat_match(S,str(dest),row['grouped_stat'])==dest,'EXACT_UNCHANGED_CLOSED_GROUPED_FILE')
 need(state['partition_complete']is True and state['source_sha256']==gr['source_sha256']and sum(x['records']for x in state['groups'].values())==gr['records']and len(state['groups'])==gr['shards'],'PRIOR_GROUP_CHECKPOINT_ALL_SHARDS')
 # Reuse already closed immutable wholeSHA/CRC proof; do not rerun GROUP or rehash body.
 work.mkdir(parents=True,exist_ok=False)
 for key,file in [('group_receipt_ref','GROUP_RECEIPT.json'),('checkpoint_ref','CHECKPOINT.json')]:
  with(work/file).open('xb')as f:f.write(raw_meta(S,row[key]));f.flush();os.fsync(f.fileno())
 with(work/'PRIOR_CLOSED_GROUP_ADOPTION.json').open('x')as f:json.dump(dict(prior_refs=row,source_KEEP=True,body_rehash_or_regroup=False),f,indent=2)
 return dest,work
