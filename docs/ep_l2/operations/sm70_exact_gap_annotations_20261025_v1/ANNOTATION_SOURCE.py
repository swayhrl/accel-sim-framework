from pathlib import Path
import json,gzip,hashlib,collections,time,os
NAS=Path('/root/share/mnt164/huangrulin/traces')
T=NAS/'receipts/sm70_public_bootstrap_preparation_20261025_v1'
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
A=Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/ep_main_account_workload_audit_20261024_v2')
def sha(b):return hashlib.sha256(b).hexdigest()
def rawread(p,limit=128*2**20):
 with Path(p).open('rb') as f:b=f.read(limit+1)
 assert len(b)<=limit
 return b
def checked(ref):
 b=rawread(ref['path']);assert sha(b)==ref['sha256'];return json.loads(b)
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,str(p)
 else:
  with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==b
 return dict(path=str(p),sha256=sha(b),bytes=len(b))
def cas(b):return put(T/'proofs/sha256'/sha(b),b)
def jcas(d):return cas((json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode())
prior_ref=dict(path=str(T/'COMMIT_V3.json'),sha256='72f7004f48846a6bb27bea40718e46b23ae3b44eeeff6252f4d286a62e0ca3bb')
prior=checked(prior_ref);spec=checked(prior['prepared_template_ref'])
assert spec['schema'].endswith('TEMPLATE_UNRESOLVED_NOT_EXECUTABLE') and spec['body_reads_authorized'] is False and spec['protected_after_ref'] is None
issues=checked(spec['issues_ref']);B=checked(spec['base_all_bundles_ref'])
objraw=rawread(A/'TRACE_MEMBER_OBJECT_METADATA.json.gz',16*2**20)
with gzip.GzipFile(fileobj=__import__('io').BytesIO(objraw)) as f:decoded=f.read(128*2**20+1)
assert len(decoded)<=128*2**20
objects=json.loads(decoded)
raw_ref=cas(objraw);raw_ref.update(encoding='gzip',logical_sha256=sha(decoded),logical_bytes=len(decoded),content_kind='historical_metadata_only_no_trace_body')
source_refs={n:cas(rawread(A/n,2*2**20)) for n in ['scan_assets.py','build_report.py']}
alias_set={(a['host'],a['path']) for b in B for a in b['source_aliases']}
annotated=[];counts=collections.Counter();zero_keys=set();missing_refs=0
for i,row in enumerate(issues['expanded_input_observations']):
 assert row['complete_by_metadata'] is False and (row['host'],row['path']) not in alias_set
 reasons=[];zero=[];known_members=[]
 for key in row.get('member_object_keys',[]):
  if isinstance(key,str):
   obj=objects[key];assert obj['host']==row['host']
   known_members.append(dict(object_key=key,example_path=obj['example_path'],stat=obj['stat']))
   if obj['stat']['bytes']==0:
    zero.append(dict(object_key=key,example_path=obj['example_path'],stat=obj['stat']))
    zero_keys.add(key)
 if not row.get('exists'):reasons.append('COMMANDLIST_NOT_FOUND_IN_HISTORICAL_SNAPSHOT')
 else:
  if row.get('kernel_launches')==0:reasons.append('NO_KERNEL_LAUNCH_ENTRY_IN_COMMANDLIST')
  if row.get('missing_members',0)>0:
   reasons.append('DECLARED_KERNEL_MEMBERS_MISSING_IN_HISTORICAL_SNAPSHOT')
   missing_refs+=row['missing_members']
  if zero:reasons.append('ZERO_BYTE_DECLARED_KERNEL_MEMBER_IN_HISTORICAL_SNAPSHOT')
 assert reasons,(i,row['path'])
 for reason in reasons:counts[reason]+=1
 same=[b['bundle_id'] for b in B if b['suite']==row['suite'] and b['program']==row['program']]
 exact_version=[b['bundle_id'] for b in B if b['suite']==row['suite'] and b['program']==row['program'] and b['version']==row['version']]
 annotated.append(dict(original_observation_index=i,host=row['host'],path=row['path'],suite=row['suite'],program=row['program'],source_version_evidence=row['version'],extent=row['extent'],historical_metadata_failure_reasons=reasons,zero_byte_members=zero,existing_member_metadata=known_members,declared_missing_members=row.get('missing_members'),same_program_frozen_other_input_ids=sorted(same),same_version_frozen_other_input_ids=sorted(exact_version),other_inputs_do_not_resolve_this_exact_path=True,fresh_source_existence_or_body_rechecked=False))
assert len(annotated)==99 and sum(counts.values())==99 and len(zero_keys)==4
assert counts=={'COMMANDLIST_NOT_FOUND_IN_HISTORICAL_SNAPSHOT':85,'NO_KERNEL_LAUNCH_ENTRY_IN_COMMANDLIST':6,'DECLARED_KERNEL_MEMBERS_MISSING_IN_HISTORICAL_SNAPSHOT':4,'ZERO_BYTE_DECLARED_KERNEL_MEMBER_IN_HISTORICAL_SNAPSHOT':4}
enriched=dict(issues)
enriched.update(schema='SHARED_TRACE_INPUT_ISSUES_V3_BOOTSTRAP_WITH_EXACT_FAILURE_ANNOTATIONS_V1',
 original_issues_ref=spec['issues_ref'],historical_member_metadata_gzip_ref=raw_ref,
 historical_metadata_classifier_sources=source_refs,
 expanded_input_failure_annotations=annotated,
 failure_annotation_counts=dict(counts),
 classification_basis='Frozen historical metadata only. All99 original observations retained verbatim. Nonempty complete known125 graph unchanged; other inputs never repair an exact missing/empty/zero-byte input by program-name equivalence.',
 source_trace_payload_bytes_read=0,target_trace_stats=0,new_scientific_qualification=False)
iref=jcas(enriched)
new_spec=dict(spec);new_spec['issues_ref']=dict(path=iref['path'],sha256=iref['sha256'])
assert {k for k in new_spec if new_spec[k]!=spec[k]}=={'issues_ref'}
sref=jcas(new_spec)
report=dict(schema='ROOT_EXACT_INPUT_GAP_ANNOTATION_ACCEPTANCE_V1',status='PASS_ALL99_NEGATIVE_INPUTS_HAVE_EXPLICIT_METADATA_REASONS_NOT_RECOVERED_ASSETS',
 observed_unix=time.time(),prior_commit_ref=prior_ref,prior_template_ref=prior['prepared_template_ref'],prior_issues_ref=spec['issues_ref'],new_issues_ref=iref,new_template_ref=sref,
 historical_metadata_public_gzip_ref=raw_ref,classifier_source_refs=source_refs,observations=99,reason_counts=dict(counts),zero_byte_member_identity_keys=sorted(zero_keys),missing_kernel_member_references=missing_refs,
 original_all99_rows_and_archive_issues_preserved=True,exact_known125_scope_unchanged=True,zero_exact_alias_overlap_with_frozen125=True,
 metadata_source_original_gzip_full_CRC_verified=True,new_trace_body_reads=0,new_target_trace_stats=0,
 source_original_release_bytes=0,body_reads_authorized=False,production_activation=False,source_or_science_controls_modified=False,
 interpretation='These are historical path-level negative observations, not99 distinct workloads or source programs. Do not collapse versions, hosts or input parameters. Full Source2 binding and final actual qualification remain pending.')
rref=jcas(report)
commit=dict(schema='SM70_BOOTSTRAP_EXACT_GAP_REASON_INCREMENT_V4',metadata_only=True,activation=False,Source2_pending=True,body_read_authorized=False,protected_after_ref=None,prior_COMMIT_ref=prior_ref,prepared_template_ref=sref,new_issues_ref=iref,report_ref=rref)
raw=(json.dumps(commit,sort_keys=True,indent=2)+'\n').encode()
cref=put(T/'COMMIT_V4.json',raw)
put(R/'control/PARENT_EXACT_INPUT_GAP_ANNOTATION_ACCEPTANCE_V1.json',(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
print(json.dumps(dict(commit_ref=cref,report_ref=rref,issues_ref=iref,template_ref=sref,reason_counts=dict(counts),missing_member_references=missing_refs,raw_metadata_bytes=len(objraw),logical_metadata_bytes=len(decoded)),ensure_ascii=False))
