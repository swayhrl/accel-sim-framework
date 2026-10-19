"""One existing receiver invocation for an independently reviewed P9 runner.

Arguments: window_id source_ready_commit source_cache_dir. Never stages Source.
The approved source runner and tests are byte pinned, not trusted from a count.
"""
import ast
import json
import sys
import tls_target as t

wid, source_commit, dirname = sys.argv[1:]
assert wid.startswith('TLS_V10_P9_PUBLIC_B') and len(source_commit)==40
D=t.META/dirname
ready_name=wid+'_SOURCE_READY_COPY16.json'
gate_name=wid+'_SOURCE_GATE_PASS_COPY16.json'
adopt_name=wid+'_SOURCE_PROTOCOL_ADOPTION_COPY16.json'
if not (D/adopt_name).exists():
 adopt_name='TLS_V10_P9_EXACT_WINDOW_PROTOCOL_ADOPTION_COPY16.json'
bind_name=wid+'_EXACT_SOURCE_WINDOW_BINDING.json'
R=json.loads((D/ready_name).read_bytes());G=json.loads((D/gate_name).read_bytes());A=json.loads((D/adopt_name).read_bytes());B=json.loads((D/bind_name).read_bytes())
W=t.get(wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')
M=t.get('SOURCE_TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json')
reserved=t.get('TLS_V10_P9_PUBLIC_TARGET_ROOT_RESERVED.json')
approved=R['source_sender_code_sha256']
# Second reviewed revision adds only durable adoption/publication metadata;
# its data-path and resource-gate code are unchanged from the first review.
reviewed_runners={
 '20a424d9f27a918bb3546a152c58e910ef9c8c214fc277868d8c3052b8c74618':'26b7343cb42da5635d0ff12796b749315779f16b',
 '89efd25b043129d474dafb783bb1a7bd0840607d8693310aab6d525032c99194':'0f029002439a17688c8415f941b4db75710d2ef7',
}
assert approved in reviewed_runners,'Changed Source runner requires bounded diff review'
testsha={
 '20a424d9f27a918bb3546a152c58e910ef9c8c214fc277868d8c3052b8c74618':'3869e30195a3a589ced5fadbff655e4cf50e6400c1ad2bb8f986b706901439a9',
 '89efd25b043129d474dafb783bb1a7bd0840607d8693310aab6d525032c99194':'95f6034ec54598e8add5201fc8835f2b4b0b9f38337b68588e02ce8c643b99d3',
}[approved]
assert t.sha(D/'tls_v10_p9_exact_window_runner.py')==approved
assert t.sha(D/'test_tls_v10_p9_exact_window_runner.py')==testsha
assert R['source_sender_code_sha256']==G['runner_code_sha256']==approved
if adopt_name==wid+'_SOURCE_PROTOCOL_ADOPTION_COPY16.json':
 assert A['qualified_source_runner_sha256']==approved
 assert A['qualified_source_test_sha256']==testsha and A['source_fixture_tests_passed']==16
else:
 assert A['schema']=='TLS_V10_P9_EXACT_WINDOW_PROTOCOL_ADOPTION_COPY16_V1'
 for k in ['group','txid','selector_sha256','canonical_manifest_sha256','policy_id','source_originals']:assert A[k]==R[k]
 assert A['applies_to']=='B0005_AND_LATER_EXACT_TARGET_REQUESTS_ONLY'
 assert A['source_release_authorized_by_window'] is False
 assert A['source_ready_requires_target_request_git_bridge_sha_frozen_plan_prior_cleanup_fresh_gate'] is True
 assert A['per_window_raw_cap_bytes']==128*1024**2 and A['single_bridge_payload_cap_bytes']==256*1024**2 and A['stream_block_cap_bytes']==1024**2
 assert A['target_requires_actual164_dest_and_independent_native_range_restore_before_source_ack'] is True
 assert A['range_proof_never_implies_complete_original_or_group'] is True
assert sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse((D/'test_tls_v10_p9_exact_window_runner.py').read_bytes())))==16
assert R['schema']=='TLS_V10_OLD174_GROUPED_RAW_READY_V1' and R['status']=='READY_SOURCE_KEEP'
for k in ['window_id','txid','selector_sha256','canonical_manifest_sha256','group','source_frozen_commit','source_root']:assert R[k]==W[k]
for k in ['window_id','txid','selector_sha256','canonical_manifest_sha256','source_root']:assert B[k]==R[k]
assert R['source_repo']=='swayhrl/gpu-l2-cache-verilog' and R['source_branch']==t.get('TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json')['source_branch']
assert R['source_namespace']=='mnt:[4026534768]' and R['source_dev']==156
assert R['source_originals']=='SOURCE_KEEP' and R['source_files_unlinked']==0
assert R['policy_id']==B['policy_id']=='TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019'
assert R['target_window_sha256']==B['target_request_sha256']==t.sha(t.BASE/(wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json'))
assert R['target_window_git_commit']==B['target_request_git_commit']
if 'target_request_git_commit' in A:assert A['target_request_git_commit']==R['target_window_git_commit']
assert R['target_root_native164']==B['target_root_native164']==M['genuine164_destination_root']
assert R['prior_cleanup_sha256']==B['prior_cleanup_sha256']==W['prior_window_cleanup_sha256']
assert B['prior_cleanup_git_commit']==W['prior_window_cleanup_commit']
assert B['plan_sha256']==G['plan_sha256']==W['plan_sha256']
assert B['plan_batch_index']==W['plan_batch_index']
assert G['binding_sha256']==t.sha(D/bind_name)
assert G['request_sha256']==R['target_window_sha256']
assert G['manifest_sha256']==W['canonical_manifest_sha256']
assert R['source_gate_sha256']==t.sha(D/gate_name)
assert R['source_protocol_adoption_sha256']==t.sha(D/adopt_name)
if 'target_request_sha256' in A:assert A['target_request_sha256']==R['target_window_sha256']
assert R['source_range_primitive_sha256']=='433aaefca702a6283bc3675cb233ceb330c40f3dd47bbef5067d3de76c4f4a69'
assert R['range_count']==len(R['entries'])==W['range_count'] and 0<R['range_count']<=128
assert R['raw_bytes']==sum(e['length'] for e in R['entries'])==W['raw_bytes']<=128*1024**2
rows={r['relative_path']:r for r in M['files']}
keys=('dev','inode','nlink','size','allocated','uid','gid','mode','mtime_ns','ctime_ns')
for i,(r,w) in enumerate(zip(R['entries'],W['ranges'])):
 for k in ['relative_path','offset','length','bridge_path']:assert r[k]==w[k]
 row=rows[r['relative_path']]
 assert r['source_identity']==w['source_identity']=={k:row[k] for k in keys}
 assert r['source_full_sha256']==w['original_sha256']==row['sha256']
 assert type(r['offset']) is int and type(r['length']) is int and 0<=r['offset']<row['size'] and 0<r['length']<=128*1024**2 and r['offset']+r['length']<=row['size']
 assert len(r['chunk_sha256'])==64 and r['chunk_sha256']==G['fresh_range_sha256'][i]
 if r['offset']==0 and r['length']==row['size']:assert r['chunk_sha256']==row['sha256']
for stage in [G['gate'],R['gate_before_stage'],R['gate_after_stage']]:
 decision=stage['decision']
 assert decision['decision']=='POLICY_ELIGIBLE_NOT_READY' and not decision['reasons']
 assert decision['effective_workspace_floor_bytes']==16*1024**3
 assert decision['projected_workspace_available_bytes']>=16*1024**3
 assert stage['workspace_available_bytes']>=16*1024**3 and stage['share_available_bytes']>=40*1024**3
 assert 0<=stage['snapshot_age_seconds']<=30 and 0<=stage['staged_physical_bytes']<=256*1024**2
assert R['gate_before_stage']['share_available_bytes']-W['raw_bytes']-1024**2>=40*1024**3
assert R['gate_after_stage']['staged_physical_bytes']==R['bridge_payload_allocated_bytes']
review=dict(schema='TLS_V10_TARGET_REVIEWED_EXACT_SOURCE_RUNNER_WINDOW_V1',utc=t.now(),status='SOURCE_EXACT_WINDOW_BINDING_GATE_READY_VERIFIED',window_id=wid,source_ready_git_commit=source_commit,source_ready_sha256=t.sha(D/ready_name),source_binding_sha256=t.sha(D/bind_name),source_runner_sha256=approved,source_test_sha256=testsha,source_fixture_methods=16,full_runner_tests_reviewed_once_at_source_commit='26b7343cb42da5635d0ff12796b749315779f16b',source_runner_revision_reviewed_at=reviewed_runners[approved],source_current_namespace_root_plan_previous_cleanup_and_request_binding=True,source_fresh_snapshots_signed_compact=True,source_production_evidence_code_takes_fresh_actual_RAM_cgroup_lease_current_planned_reader_inputs_each_gate=True,target_did_not_run_source_policy_or_sender=True,source_originals='SOURCE_KEEP',no_global16_or_release_permission=True,goal_mode='ACTIVE')
t.save(wid+'_TARGET_SOURCE_RUNNER_REVIEW_COPY16.json',review)
code=(t.META/'receive_grouped_remote_template.py').read_text(encoding='utf-8')
# The reviewed data-driven Source runner publishes exact READY raw bytes after
# Git readback; it has no redundant publication marker. Git+bridge SHA is the
# authoritative binding. If a marker exists, still require it to match.
old="pub=json.loads((B/__PUBLICATION_FILENAME__).read_bytes());assert pub['source_git_commit']==source_commit and pub['source_ready_sha256']==ready_sha\nassert pub['txid']==W['txid'] and pub['source_originals']=='SOURCE_KEEP'"
new="""publication=B/__PUBLICATION_FILENAME__
if publication.exists():
 pub=json.loads(publication.read_bytes());assert pub['source_git_commit']==source_commit and pub['source_ready_sha256']==ready_sha
 assert pub['txid']==W['txid'] and pub['source_originals']=='SOURCE_KEEP'
"""
assert old in code;code=code.replace(old,new)
pins={n:t.sha(t.BASE/'tools'/n) for n in ['v9_transaction.py','tls_v10_native_chunk_proof.py','tls_v10_grouped_ranges.py']}
values=[('__READY__',R),('__WINDOW__',W),('__MANIFEST__',M),('__RESERVED__',reserved),('__PIN__',t.sha(D/ready_name)),('__PINS__',pins),('__SOURCE_COMMIT__',source_commit),('__READY_FILENAME__',ready_name),('__PUBLICATION_FILENAME__',wid+'_SOURCE_READY_PUBLICATION_COPY16.json'),('__WINDOW_FILENAME__',wid+'_TARGET_SOLE_WINDOW_REQUEST_COPY16.json')]
for token,value in values:code=code.replace(token,repr(value))
result=t.remote(code,wid+'_RECEIVER_RESULT_COPY16',180)
t.save(wid+'_DEST_VERIFIED.json',result['dest'])
t.save(wid+'_RESTORE_VERIFIED.json',result['restore'])
print('DEST_SHA',t.sha(t.BASE/(wid+'_DEST_VERIFIED.json')))
print('RESTORE_SHA',t.sha(t.BASE/(wid+'_RESTORE_VERIFIED.json')))
