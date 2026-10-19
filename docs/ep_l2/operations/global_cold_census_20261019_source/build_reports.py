import os,json,csv,collections,datetime,subprocess,hashlib,shutil,re
from pathlib import Path
T=Path.cwd(); O=T/'audit_reports'; D=T/'docs/ep_l2/operations/global_cold_census_20261019_source'; D.mkdir(parents=True,exist_ok=True)
scans=[json.load(open(O/n)) for n in ['scan_checkpoint.json','scan_continuation.json']]; rows={r['path']:r for s in scans for r in s['rows']}; roots=sorted([r.copy() for r in rows.values() if r['path']==r['scan_root']],key=lambda r:-r['allocated_bytes']); act=json.load(open(O/'SOURCE_ACTIVITY_SNAPSHOT.json')); refs=json.load(open(O/'SOURCE_TRACKED_REFERENCE_EVIDENCE.json')); old=json.load(open(O/'TLS_V10_CLASSIFICATION_AND_EXCLUSIONS.json'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); dev=os.stat('/workspace').st_dev
shared_tokens=['decoupled-l2-pretraces','decoupled-l2-extract','c2p-polybench-full-20260821','decoupled-l2-trace-fraction','ccws-baseline-traces','decoupled-l2-fraction40-trim']

def activity(p):
 found=[]
 for r in act['processes']:
  if 'framework-global-cold-census' in r['cwd']: continue
  hits=[x for x in [r['cwd'],r['exe']]+r['argv_paths']+r['fd_paths'] if x==p or x.startswith(p+'/')]
  if hits: found.append(r['pid'])
 return found

def project(p):
 q=p.lower()
 if any(t in q for t in ['ep_l2','ep-l2','gpu-l2','gpu_l2']): return 'EP-L2'
 if any(t in q for t in ['dtc','decoupled-l1','fast64','wave-a','iscas2027','/m5-','/m5_','post-fast64']): return 'DTC-L1'
 if 'c2p' in q: return 'C2P'
 if 'm2d' in q: return 'M2D'
 if 'tls' in q: return 'TLS'
 if 'c16' in q: return 'C16'
 if 'awma' in q: return 'AWMA'
 if 'ai-arch' in q or 'ai_arch' in q: return 'AI-ARCH'
 if any(t in q for t in ['m4','vm-','/vm_','c14','c7e']): return 'Legacy_VM_GPU'
 if any(t in q for t in ['trace','bench','gpgpu-workloads']): return 'Bench_Traces'
 if p.startswith('/root/.cache/'): return 'Local_software_cache'
 if p.startswith('/root/.local/'): return 'Local_software_environment'
 if p.startswith('/tmp/'): return 'Other_tmp_scratch'
 return 'Other_legacy_GPU_and_unresolved'

def role(p):
 q=p.lower()
 if '.git' in q or q.endswith('.bundle'): return 'CODE_GIT_PROVENANCE'
 if any(t in q for t in ['trace','pretrace']): return 'TRACE_INPUT'
 if any(t in q for t in ['build','/tmp/c2p-','/tmp/m2d-']): return 'BUILD_OR_TEST_PRODUCT_REQUIRES_SOURCE_SPLIT'
 if any(t in q for t in ['assets','model','checkpoint','package']): return 'MODEL_INPUT_OR_PACKAGE'
 if 'cache' in q and p.startswith('/root/'): return 'SOFTWARE_CACHE_OR_ENVIRONMENT'
 if '/worktrees/' in p or '/repos/' in p: return 'MIXED_CODE_CONFIG_BUILD_RESULT'
 return 'RESULT_OR_SCRATCH_UNRESOLVED'

def status(p):
 pr=project(p)
 if pr=='EP-L2': return 'PROTECTED_EP_L2'
 if pr=='DTC-L1': return 'PROTECTED_DTC_L1'
 if any(t in p for t in shared_tokens): return 'SHARED_DEPENDENCY_KEEP'
 if activity(p): return 'ACTIVE_KEEP'
 if role(p)=='CODE_GIT_PROVENANCE': return 'CODE_GIT_KEEP'
 return 'HOLD'

def csvout(name,rs):
 if not rs:return
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with open(D/name,'w') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader();w.writerows(rs)

def jwrite(name,v): (D/name).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def decorate(r,**extra):
 p=r['path']; return dict(source_path=p,device=r.get('device'),inode=r.get('inode'),uid=r.get('uid'),gid=r.get('gid'),allocated_bytes=r['allocated_bytes'],allocated_GiB=round(r['allocated_bytes']/2**30,6),logical_bytes=r['logical_bytes'],measured_complete_excluding_git=r['complete'],project=project(p),status=status(p),role=role(p),max_observed_mtime_utc=datetime.datetime.fromtimestamp(r['max_mtime_ns']/1e9,datetime.timezone.utc).isoformat(),last_real_writer='NOT_PROVEN_BY_MTIME; see PID snapshot',current_pid_hits=';'.join(map(str,activity(p))),multiple_link_entries=r['multiple_link_entries'],duplicate_link_entry_bytes=r['duplicate_link_bytes'],sparse_files=r['sparse_files'],release_authority='NOT_GRANTED',currently_releasable_bytes=0,**extra)

# Primary root table is deliberately nonoverlapping; nested drilldowns are never added to it.
# Excludes Git contents and source mounts that are outside the explicit account scope.
top=[dict(rank=i+1,**decorate(r),allocation_scope='OBSERVED_SOURCE_ST_BLOCKS; partial root is LOWER_BOUND') for i,r in enumerate(roots[:20])];csvout('SOURCE_COLD_CENSUS_TOP20.csv',top)
ledger=[decorate(r) for r in roots if r['allocated_bytes']>=2**20 or ('c2p' in r['path'].lower() and r['dirs']>0)]
csvout('SOURCE_COLD_CENSUS_ROOT_LEDGER.csv',ledger)
# Partition the common decoupled-l2 root by direct hw_run child; retain a residual to avoid overlap.
partition=[]
for r in roots:
 if r['path']=='/workspace/worktrees/accel-sim-decoupled-l2':
  children=[v.copy() for v in rows.values() if v['path'].startswith(r['path']+'/hw_run/') and v['path'].count('/')==r['path'].count('/')+2]
  partition.extend(children); rem=r.copy(); rem['path']+=' [residual excluding enumerated hw_run children]'; rem['allocated_bytes']-=sum(c['allocated_bytes'] for c in children);rem['logical_bytes']-=sum(c['logical_bytes'] for c in children);partition.append(rem)
 else:partition.append(r)
summ=collections.defaultdict(lambda:dict(allocated_bytes=0,logical_bytes=0,protected_or_shared_bytes=0,active_keep_bytes=0,hold_or_code_bytes=0,partial_roots=0,root_count=0))
for r in partition:
 p=r['path']; k='Mixed_TLS_C2P_ACTIVE' if 'tls-c2p-v100-20260822' in p else ('Shared_protected_trace_dependencies' if any(t in p for t in shared_tokens) else project(p)); s=summ[k]; s['allocated_bytes']+=r['allocated_bytes'];s['logical_bytes']+=r['logical_bytes'];s['root_count']+=1;s['partial_roots']+=not r['complete']; st=status(p)
 s['protected_or_shared_bytes']+=r['allocated_bytes'] if st.startswith('PROTECTED') or st=='SHARED_DEPENDENCY_KEEP' else 0
 s['active_keep_bytes']+=r['allocated_bytes'] if st=='ACTIVE_KEEP' else 0;s['hold_or_code_bytes']+=r['allocated_bytes'] if st in ['HOLD','CODE_GIT_KEEP'] else 0
for k in ['TLS','AWMA','C16','AI-ARCH','C2P','M2D','EP-L2','DTC-L1','Legacy_VM_GPU','Bench_Traces','Local_software_cache']:summ[k]
summary=[]
for k,s in sorted(summ.items(),key=lambda kv:-kv[1]['allocated_bytes']):
 summary.append(dict(project=k,**s,allocated_GiB=round(s['allocated_bytes']/2**30,6),proven_scientific_exclusive_releasable_bytes=0,release_authority='NOT_GRANTED',coverage='NO_SEPARATE_ROOT_DISCOVERED_NOT_ZERO_PROVEN' if not s['root_count'] else 'BOUNDED_NAMED_ROOT_ATTRIBUTION; shared partition excluded; Git omitted; not a sole ownership proof'))
csvout('SOURCE_COLD_CENSUS_PROJECT_SUMMARY.csv',summary)
assert sum(s['allocated_bytes'] for s in summary)==sum(r['allocated_bytes'] for r in roots)

# All named C2P roots, separately itemized direct children of the four primary code trees,
# plus shared/mixed exclusions. Only rows tagged add_to_identified_subtotal are additive.
c2p=[]
for r in roots:
 if 'c2p' not in r['path'].lower(): continue
 c2p.append(decorate(r,scope='IDENTIFIED_NAMED_ROOT',add_to_identified_subtotal=True,ownership_proof='C2P checked Git lineage for four worktrees; other names are locators pending provenance and consumer join',prior164_proof='V9 only for two exact build children; never whole parent'))
 if r['path'].startswith('/workspace/worktrees/'):
  cs=[v for v in rows.values() if v['scan_root']==r['path'] and v['path'].count('/')==r['path'].count('/')+1]
  for v in sorted(cs,key=lambda v:-v['allocated_bytes']):c2p.append(decorate(v,scope='NONADDITIVE_WORKTREE_ROLE_BREAKDOWN',add_to_identified_subtotal=False))
  for v in rows.values():
   if v['scan_root']==r['path'] and '/hw_run/' in v['path'] and v['path'].count('/')==r['path'].count('/')+2:c2p.append(decorate(v,scope='NONADDITIVE_RUN_OR_ANALYSIS_BREAKDOWN',add_to_identified_subtotal=False))
for p in ['/tmp/c2p-gpgpu-pre-attribution-20260822/build','/tmp/c2p-gpgpu-build-20260821/build']:
 v=rows[p]; c2p.append(decorate(v,scope='NONADDITIVE_V9_EXACT_BUILD',add_to_identified_subtotal=False,prior_allocated_bytes=424570880 if 'pre-attribution' in p else 424419328,prior164_proof='SOURCE_V9_CURRENT_METADATA_JOIN.json; FULL_CONTENT_RESTORE_PLUS_NATIVE_METADATA_SAMPLE; SOURCE_KEEP'))
for r in partition:
 if r['path'].startswith('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/') and 'c2p' in r['path'].lower():
  c2p.append(decorate(r,scope='EXCLUDED_SHARED_OR_MIXED_ROOT',add_to_identified_subtotal=False,reason='No exclusive C2P claim; mixed offloader or protected DTC trace dependency'))
csvout('SOURCE_COLD_CENSUS_C2P_BREAKDOWN.csv',c2p)
identified=sum(r['allocated_bytes'] for r in roots if 'c2p' in r['path'].lower()); jwrite('SOURCE_COLD_CENSUS_C2P_SCOPE.json',dict(identified_named_root_allocated_bytes=identified,identified_named_root_GiB=identified/2**30,known_V9_build_current_bytes=sum(rows[p]['allocated_bytes'] for p in ['/tmp/c2p-gpgpu-pre-attribution-20260822/build','/tmp/c2p-gpgpu-build-20260821/build']),overall_C2P_total='UNKNOWN: undiscovered aliases, unnamed mixed artifacts, Git, shared and future consumers not fully proven',exclusive_reclaimable_bytes=0,identified_scope_complete_except_pruned_Git=True,breakdown_rows=len(c2p),named_root_count=sum('c2p' in r['path'].lower() for r in roots),M2D_excluded=True,mixed_TLS_C2P_excluded=True,shared_trace_roots_excluded=True))

shared=[]
for r in partition:
 if any(t in r['path'] for t in shared_tokens): shared.append(decorate(r,protected_consumers='EP-L2/DTC-L1; tracked payload/queue references; see SOURCE_TRACKED_REFERENCE_EVIDENCE.json'))
for r in roots:
 if r['path']=='/workspace/m5-trace-immutable':shared.append(decorate(r,protected_consumers='DTC-L1 full M5/fast64 lineage and tracked references'))
jwrite('SOURCE_COLD_CENSUS_SHARED_DEPENDENCIES.json',dict(status='KEEP_PROTECTED_NO_PATH_CHANGES',current_nonoverlapping_shared_roots=shared,historical_four_TLS_shared_trace_roots=old['shared_trace_dependencies'],historical_four_sum_bytes=old['shared_trace_allocated_total_bytes'],historical_roots_are_nested_do_not_add_to_current_roots=True,ownership_rule='Path names are locators only; checked Git manifests and live process paths independently establish consumers',reference_coverage='Bounded tracked source HEAD; absence of a hit never proves exclusivity',source_p9='SOURCE_KEEP; 141 files; nine range proofs are not a full group restore'))

# Preserve concise evidence; do not publish raw scan trees/logs or raw scheduler commands.
for name in ['SOURCE_ACTIVITY_SNAPSHOT.json','SOURCE_SCHEDULED_CONSUMER_PROBE.json','SOURCE_TRACKED_REFERENCE_EVIDENCE.json','SOURCE_V9_CURRENT_METADATA_JOIN.json','SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json','V9_COLD_ARCHIVE_AND_RESTORE_INDEX.json','V9_RESTORE_RECEIPT.json','TLS_V10_CLASSIFICATION_AND_EXCLUSIONS.json','TLS_V10_P9_PUBLIC_B0010_SOURCE_BLOCKED_AUDIT.json']:
 shutil.copyfile(O/name,D/name)

def current():
 r={}
 for p in ['/workspace','/root/data','/root/share']:
  s=os.statvfs(p); t=os.stat(p);r[p]=dict(device=t.st_dev,inode=t.st_ino,fsid=s.f_fsid,f_bavail=s.f_bavail,f_bfree=s.f_bfree,f_frsize=s.f_frsize,available_bytes=s.f_bavail*s.f_frsize,free_bytes=s.f_bfree*s.f_frsize)
 return r
start=json.load(open(O/'space_start.json')); end=current(); scope=dict(roots_enumerated=len(scans[0]['roots']),measured_unique_roots=len(roots),observed_allocated_bytes=sum(r['allocated_bytes'] for r in roots),entries_stat=sum(s['entries'] for s in scans),scanner_seconds=sum(s['elapsed_seconds'] for s in scans),primary_seconds=scans[0]['elapsed_seconds'],continuation_seconds=scans[1]['elapsed_seconds'],errors=sum(len(s['errors']) for s in scans),partial_roots=[r['path'] for r in roots if not r['complete']],Git_contents='PRUNED_NOT_MEASURED_KEEP',symlink_roots=[s for s in scans[0]['skipped'] if s['reason']=='SYMLINK'],supplementary_du_protected_repo='20 second targeted timeout returned 124; no exact size; retain original lower bound',no_full_physical_filesystem_crawl=True)
jwrite('CURRENT_OLD174_SPACE_AND_IO_PRESSURE.json',dict(schema='GLOBAL_COLD_CENSUS_READONLY_V1',base_commit='dc2f32bf28c85fded91beead53a2a3fd650de202',coordination_branch='hrl/old174-global-cold-storage-audit-20261019-v1',execution_branch='hrl/old174-global-cold-census-exec-20261019-v1',at_utc=now,source_namespace=os.readlink('/proc/self/ns/mnt'),hostname=os.uname().nodename,uid=os.getuid(),start=start,end_space=end,current_io_pressure=open('/proc/pressure/io').read(),current_cgroup_io_pressure=open('/sys/fs/cgroup/io.pressure').read(),scope=scope,resource_policy=dict(control_peak_allocation_budget_bytes=134217728,metadata_only=True,scanner_nice=19,scanner_ionice_class=3,no_source_hashing=True,no_TLS_sender_or_lease=True),accounting_caveats=['st_blocks counts visible inode allocation, not guaranteed writable overlay upper allocation; lower-only and reflink/COW sharing not established','Each hardlinked inode counted once within a pass; first-path attribution is not sole project ownership; cross-pass hardlink union not proven','Main top20 roots have zero multi-link entries; unknown/net lower bound remains zero','Source overlay0:156 and /root/data ext4 8:80 reflect same capacity/backing accounting; do not add their available bytes','Share /dev/md127 9:127 is separate, only statvfs read; no Share/164 payload tree scan','Excluded: Git object contents, unrelated root/scratch/toolchains, other tenants, all remote mounts; observed coverage does not explain all host df used bytes','Root mtime maxima are observations, never last true consumer proof; these are bounded sequential snapshots, not an atomic freeze','Primary and continuation root sets disjoint; no nested sum in project totals'],actions=dict(source_scientific_released_files=0,source_scientific_released_bytes=0,new_archived_bytes=0,scientific_payload_copies=0,TLS_B0001_B0009_retransfers=0,TLS_goal_restarts=0,registry_lease_mutations=0,control_reports_only=True)))

# /root/data is a separately scoped sidecar; never added to overlay project's totals.
data_du=(O/'root_data_du.tsv').read_text(); side=[]
for l in data_du.splitlines():
 b,p=l.split('\t',1);s=os.lstat(p);side.append(dict(path=p,device=s.st_dev,inode=s.st_ino,uid=s.st_uid,gid=s.st_gid,allocated_bytes=int(b),status='HOLD_ACCOUNT_C16_GENERATED_OR_GIT_BUNDLE',release_authority='NOT_GRANTED'))
jwrite('SOURCE_ROOT_DATA_BOUNDED_SIDECAR.json',dict(mount='rw ext4 /dev/sdf[/huangrulin]; UID0 local c16 generated roots only',scope='20s bounded du /root/data; 12 top-level build/bundle entries; no disk-wide traversal',rows=side,add_to_main_overlay_total=False,free_space_summing_forbidden=True,backing_alias_proof='findmnt mount source and matching capacity/free observations; inode identity across overlay not proven'))

c16=json.load(open(O/'SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json')); cp=c16['shard_allocated_upper_bound']
# Candidate research ranking, not a release selector. Keep disjoint candidates and explicit hard holds.
candidates=[]
def candidate(tier,p,why,proof,gate,estimate_minutes):
 r=rows[p]; candidates.append(dict(priority_tier=tier,path=p,observed_allocated_bytes=r['allocated_bytes'],prospective_source_gain_upper_bound_bytes=r['allocated_bytes'],guaranteed_or_authorized_gain_bytes=0,eligibility='HOLD_NO_EXACT_RELEASE_AUTHORITY',owner_project=project(p),uid=r['uid'],device=r['device'],inode=r['inode'],current_pid_hits=activity(p),benefit_reason=why,recovery_evidence=proof,remaining_gates=gate,estimated_validation_minutes=estimate_minutes))
candidate('HIGH','/workspace/c16_exchange/autodl_wave1/outbound','19.37 GiB six model shards have historical SHA-matched separately allocated local source copies. Package includes code/provenance to retain.','Local P2/P3 materialization + source immutable receipts; no reviewed true164 full restore.','C16 owner and planned-transfer queue signoff; exact model-only selector; fresh source stat/SHA if later admitted; normal COPY_ONLY resource plan and true164/native restore; separate exact release policy.',30)
candidate('MEDIUM','/workspace/c16_assets/c16-a/failed_downloads','1.35 GiB failed/incomplete model assets; qualification may be cheap, but directory name is not expendability proof.','No 164 evidence; C16 telemetry active in parent.','Pin exact partials, dead downloader/no future resume, immutable complete replacement owner evidence; separate exact ordinary cleanup or science release authorization.',15)
candidate('MEDIUM','/workspace/worktrees/accel-sim-vm-c16-p/artifacts','Native postprocess outputs may contain repeatable SQLite exports, but returned raw profiles are authority inputs.','Tracked S1/S2 source manifest; no 164 archive for full artifact tree.','C16 producer/native postprocess owner closure; split unique raw, SQLite exports, code and receipts; no directory release; archive any unique bytes before exact release.',45)
for p in ['/tmp/m2d-core-g21/build','/tmp/c2p-gpgpu-pre-attribution-20260822/build','/tmp/c2p-gpgpu-build-20260821/build']:
 candidate('LOW',p,'Small already-archived exact build; C2P intentionally lower priority.','V9 full independent content restore, limited native file metadata sample; current 205/205 file metadata exact matches.','No content freshness asserted; all-file native metadata import still missing; current readers/scheduled ownership, exact selector user release authorization, resource floors and qualified source journal.',25)
candidates[0]['prospective_source_gain_upper_bound_bytes']=cp
candidates[0]['code_provenance_and_nonselected_residual_bytes']=candidates[0]['observed_allocated_bytes']-cp
csvout('SOURCE_COLD_CENSUS_CANDIDATE_RANKING.csv',[{**r,'current_pid_hits':';'.join(map(str,r['current_pid_hits']))} for r in candidates]); jwrite('SOURCE_COLD_CENSUS_CANDIDATE_RANKING.json',candidates)

smap={s['project']:s for s in summary}; topmd='\n'.join(f"| {r['rank']} | `{r['source_path']}` | {'≥ ' if not r['measured_complete_excluding_git'] else ''}{r['allocated_GiB']:.3f} | {r['status']} |" for r in top)
projmd='\n'.join(f"| {s['project']} | {format(s['allocated_GiB'],'.3f') if s['root_count'] else 'UNKNOWN'} | {s['protected_or_shared_bytes']/2**30:.3f} | {s['active_keep_bytes']/2**30:.3f} |" for s in summary)
workspace_start=start['space']['/workspace']['available_bytes']; workspace_end=end['/workspace']['available_bytes']; share=end['/root/share']['available_bytes']; known=rows['/tmp/c2p-gpgpu-pre-attribution-20260822/build']['allocated_bytes']+rows['/tmp/c2p-gpgpu-build-20260821/build']['allocated_bytes']; mixed=rows['/workspace/worktrees/accel-sim-decoupled-l2/hw_run/tls-c2p-v100-20260822']['allocated_bytes']
progress=f'''# GLOBAL_COLD_CENSUS — bounded read-only source result

Observation UTC {now}; client timezone Asia/Shanghai (UTC+8). Base `dc2f32bf28c85fded91beead53a2a3fd650de202`; remote coordination HEAD checked exactly. Independent execution branch `hrl/old174-global-cold-census-exec-20261019-v1`.

## Fast measured leaderboard

GiB = 2^30 B. These are disjoint source-visible allocation roots, Git contents excluded. **One protected RTL root is a lower bound**, so this is an observed leaderboard, not proof of complete host ranking. All TOP20 roots have zero multiple-hardlink entries. No release bytes are inferred from these sizes.

| Rank | Canonical source root | Allocated GiB | Current protection/status |
|---|---|---:|---|
{topmd}

## Nonoverlapping project attribution

Project rows partition the measured roots, separating common trace children from their parent. Attributed bytes are not sole scientific ownership or authorized reclaim. AWMA/AI-ARCH rows with no discovered separate roots mean **unknown**, not absent or zero occupancy across aliases. Full EP-L2/DTC-L1 protection applies regardless of these provisional project labels.

| Project/accounting bucket | Observed GiB | Protected/shared GiB | Direct PID keep GiB |
|---|---:|---:|---:|
{projmd}

Total observed overlay scope: {scope['observed_allocated_bytes']:,} B ({scope['observed_allocated_bytes']/2**30:.3f} GiB); {scope['entries_stat']:,} metadata entries, {scope['measured_unique_roots']:,} disjoint roots. Primary scan stopped at 240s; optimized continuation visited only previously unvisited roots and took {scans[1]['elapsed_seconds']:.1f}s. No scan loop remains. `/root/data` sidecar is {int(data_du.splitlines()[-1].split()[0])/2**30:.3f} GiB, accounted separately; no free-space sum and no cross-view net-reclaim claim.

## C2P complete bounded breakdown and exclusions

All {sum('c2p' in r['path'].lower() for r in roots)} discovered C2P-named roots are itemized, including small `/tmp` sources/tests/figures, the four C2P worktrees, their top-level roles and individual `hw_run` entries: **{identified:,} B = {identified/2**30:.3f} GiB identified named scope**, excluding Git contents. Whole-project exclusive total remains **UNKNOWN** until unnamed roots/aliases, shared and future consumers are reconciled. This is explicitly not a releasable amount.

- Main Framework C2P cache worktree: {rows['/workspace/worktrees/accel-sim-c2p-cache']['allocated_bytes']/2**30:.3f} GiB; address-observe worktree: {rows['/workspace/worktrees/accel-sim-c2p-addr-observe']['allocated_bytes']/2**30:.3f} GiB. They include code, builds, PPA tools, run products and analysis. Existing C2P repair/analysis jobs and stopped child jobs retain reader claims.
- Exact V9 build C2P1 current {rows['/tmp/c2p-gpgpu-pre-attribution-20260822/build']['allocated_bytes']:,} B; C2P2 {rows['/tmp/c2p-gpgpu-build-20260821/build']['allocated_bytes']:,} B; total {known:,} B = {known/2**30:.6f} GiB, unchanged from historical allocation. Both build roots and 410/410 file metadata identities match V9. Their parent source trees contain additional bytes and are not V9 full-project archives.
- Mixed TLS/C2P root current {mixed:,} B ({mixed/2**30:.6f} GiB), above the historical 1,495,752,704 B by {mixed-1495752704:,} B (active logs/metadata can change). **Excluded** from exclusive C2P. Original offloader PID1920891/start_ticks408369842 remains alive with this exact local root; its old 80GiB gate is not cleanup permission.
- C2P polybench trace parent is shared/protected by DTC-L1's exact `FAST64_PAYLOAD_MANIFEST.tsv`, including GEMM and other workloads; **excluded** from exclusive C2P. Historical four TLS shared trace roots (7,340,679,168 B) are nested inputs, not additive C2P bytes.
- M2D remains separate: exact V9 build {rows['/tmp/m2d-core-g21/build']['allocated_bytes']:,} B, 205/205 current file metadata match; its whole parent is larger, and no release is authorized.

## High-value proof findings

The six P2/P3 C16 model shards alone occupy {cp:,} B ({cp/2**30:.3f} GiB). Historical local materialization SHA records equal source immutable receipt SHAs, both files currently exist with matching expected lengths and different inodes/nlink1. No payload was rehashed. This establishes a strong **duplicate review candidate**, not fresh content identity or 164/native recovery. Parent outbound packages also retain code and provenance, so no whole-package release is proposed.

C16 has a live asset telemetry owner PID280466; tracked C16-P native source manifests still depend on `returned` profiles. AWMA/AI-ARCH dormancy was not assumed. Large common roots `decoupled-l2-pretraces`, `decoupled-l2-extract`, C2P polybench traces and M5 immutable traces are protected by checked EP-L2/DTC-L1 manifests. Size is not eligibility.

## Resource admission and exact boundary

Workspace f_bavail: start {workspace_start:,} B ({workspace_start/2**30:.3f} GiB), end {workspace_end:,} B ({workspace_end/2**30:.3f} GiB). Share available {share:,} B ({share/2**30:.3f} GiB). See JSON for f_bfree distinction, RAM/cgroup and IO pressure. Concurrent free-space changes are **not audit reclaim**. Source remains below 16GiB TLS admission and below unrelated-project normal 48GiB workspace floor; TLS's narrow exception cannot authorize C16 work.

**Actions:** zero science unlink, zero payload archive/copy, zero TLS retransfers/restarts, zero registry/lease changes. Original B0010 and TLS Goals remain BLOCKED; B0001–B0009 remain closed ranges, not full P9 release proof. No sender, receiver or persistent watcher started.

**Next safe action:** source-owner C16 package closure and planned-reader review for the exact six model-shard paths in `SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json`, retaining code/provenance and source master models. Then draft one grouped model-only COPY_ONLY/recovery/release contract with realistic normal resource gates. No deletion approval is requested in this census. Current authorized/guaranteed immediate reclaim is **0 B**.

## Limits and handoff

Single scanner at nice19/ionice3; finite roots, deadlines and checkpoints; no `du /`, symlink following, Git object crawl, remote Share/164 payload read, or source payload hashes. The protected RTL repo exceeded 35s Python and 20s targeted du budgets, so retain its observed lower bound and do not recrawl. Scheduler probes are local only; historical references and mtime do not prove no future consumers. st_blocks is not an overlay-upper or reflink/net-df proof. Reports are SHA indexed, committed, pushed, fetched and independently read back from the remote execution commit; final verification is recorded by `REMOTE_READBACK_RECEIPT.json` in the isolated runtime directory and by the published follow-up receipt. This stage ends after publication; further archive or release is outside this Goal.
'''
(D/'SOURCE_COLD_CENSUS_PROGRESS.md').write_text(progress)
gates=f'''# Priority and release gates — no source release granted

All candidates are research/validation priorities, not an exact unlink selector. Guaranteed net df and currently authorized source release are **0 B**. Never sum parent/child candidate or shared input rows. No compression ratio is measured; do not turn gross allocation into a promise of recovery.

| Tier | Exact review scope | Observed upper bound GiB | Evidence / remaining risk |
|---|---|---:|---|
| High | C16 outbound model shards (six paths in duplicate evidence) | {cp/2**30:.3f} | Prior SHA-matched local copies; current size/inode checks; no fresh hashes or true164 restore. Need C16 future transfer/owner closure. Preserve package source/provenance. |
| Medium | C16 failed_downloads exact partials | {rows['/workspace/c16_assets/c16-a/failed_downloads']['allocated_bytes']/2**30:.3f} | No proven redundancy; parent telemetry live; failed name is insufficient. |
| Medium | C16-P artifacts, only after unique raw/export split | {rows['/workspace/worktrees/accel-sim-vm-c16-p/artifacts']['allocated_bytes']/2**30:.3f} | Native postprocess manifests cite authoritative returned profiles. No 164 proof. |
| Low | M2D exact archived build | {rows['/tmp/m2d-core-g21/build']['allocated_bytes']/2**30:.3f} | V9 all content restored; native file metadata sampled, current complete source stat join passes. |
| Low | C2P1 + C2P2 exact archived builds | {known/2**30:.3f} | User lower priority; same incomplete native metadata gate. Parent trees and other C2P outputs not covered. |

Time estimates in CSV are planning estimates only (15–45 min local owner/metadata validation; later transfer/restore duration depends on admission and destination, not measured here). All three scientific copy/release stages are separate:

1. **Current census:** source metadata and small report publication only. Source f_bavail about {workspace_end/2**30:.2f} GiB, not a new-project copy-ready gate. No active TLS sending lease.
2. **Future COPY_ONLY:** grouped project selector, preserved code/Git/provenance, confirmed inactive/planned readers, true164 identity/isolated absent destination and fresh 48GiB workspace /40GiB Share /64GiB RAM or separately granted narrowly scoped resource policy. The TLS-specific16GiB exception does not transfer. No staging before admission.
3. **Future source release:** exact user-approved SHA-frozen per-file selector, fresh source owner/identity/readers, current matching full original-byte archive and independent native restore including required all-file numeric metadata, qualified crash-safe exact-file journal and measured before/after f_bavail. No root/glob deletion; no unknown or protected dependency.

EP-L2 and DTC-L1 full lines and shared dependents remain absolutely protected. No existing Git/history, dirty source or editable configs qualify. Ordinary caches are proposals only, and known public cache removals from V10 are not repeated. C2P/M2D V9 has full content but only 11 native sampled files across615; do not call that full615 native import. P9 has705,152,417B of nine range evidence only; B0010 stays HOLD and all141 source files stay SOURCE_KEEP.

The highest measured **protected** buckets are not reclamation candidates. In particular common pretraces/extract roots contain real current and planned EP-L2/DTC-L1 references, even when stored under another project. Mixed TLS/C2P offloader is alive. Local process/scheduler absence is not evidence of remote/planned consumer absence.
'''
(D/'SOURCE_COLD_CENSUS_PRIORITY_AND_RELEASE_GATES.md').write_text(gates)
# Compact coverage, no ~25MB per-directory runtime JSON in Git.
jwrite('SOURCE_COLD_CENSUS_SCAN_COVERAGE.json',scope)
for p in [O/'census_scan.py',O/'census_continue.py',O/'activity_probe.py',O/'proof_probe.py',O/'reference_probe.py',O/'c16_duplicate_probe.py',O/'build_reports.py']:
 shutil.copyfile(p,D/p.name)
# Cross-source readback evidence records immutable commit provenance without new source-content hashing.
jwrite('SOURCE_EVIDENCE_PROVENANCE.json',dict(framework_base='dc2f32bf28c85fded91beead53a2a3fd650de202',V9_target_final_reference='c870ca77456d4d4d70a110411fa5c60934976666',V9_source_final_reference='3891fcd93a7ac5c3361d8f476d3c41036104b151',TLS_source_commit='f844d5fabef9aa615b121e77ddc13c32c5c8e472',TLS_target_reference='b574e7ff452a7554cea41bb0fc2a93509daf789a',immutable_receipt_copy_method='git show pinned Framework/TLS commits; no target payload reread',current_probe='Metadata only; existing payload SHA fields are historical evidence, not a new SHA measurement',scope_source_contract='docs/ep_l2/chatgpt_handoff/storage_ops_2026_10_19_global_cold_audit/GLOBAL_OLD174_COLD_ASSET_CENSUS_AND_RECOVERY_CONTRACT.md'))
files=[p for p in D.iterdir() if p.is_file() and p.name not in ['REPORT_SHA256_MANIFEST.json','REMOTE_PUBLICATION_READBACK.json']];jwrite('REPORT_SHA256_MANIFEST.json',dict(schema='SHA256_SMALL_CONTROL_REPORTS_ONLY',at_utc=now,files=[dict(path=str(p.relative_to(T)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)]))
print('PROJECTS');print('\n'.join(f"{s['project']}: {s['allocated_GiB']:.3f} GiB" for s in summary));print('REPORT_FILES',len(files)+1,'BYTES',sum(p.stat().st_size for p in D.iterdir() if p.is_file())); print('C2P',identified,identified/2**30,'known',known,'mixed',mixed); print('WS',workspace_start,workspace_end,'SHARE',share)
