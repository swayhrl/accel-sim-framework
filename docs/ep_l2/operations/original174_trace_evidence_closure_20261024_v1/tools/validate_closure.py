from closure_local import *
import posixpath,re,collections,ast
check={}
required=['LARGE_TRACE_CLOSURE_MATRIX.csv','POLYBENCH_FULL_COVERAGE.csv','RAW_RESULTS_RESTORABILITY.csv','AWMA_C16_RECOVERY_GAP_CLOSURE.md','SOURCE_TO_TRUE164_RECOVERY_MAP.json','ARCHIVE_ACTION_QUEUE.csv','RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json','FINAL_STATUS_AND_RECEIPT.md']
check['eight_deliverables']=all((R/n).is_file() for n in required)
m=rows(R/required[0]);p=rows(R/required[1]);top=[r for r in m if r['scope']=='MANDATORY_TOP30']
check['all_exact30_baseline_top_roots_covered']=len(top)==30 and {r['source_root'] for r in top}=={r['source_path'] for r in rows(B/'LARGE_ASSETS_TOP30.csv')}
check['all_exact28_baseline_poly_roots_covered']=len([r for r in p if int(r['polybench_index'])<=28])==28 and {r['source_root'] for r in p if int(r['polybench_index'])<=28}=={r['source_path'] for r in rows(B/'POLYBENCH_TRACE_INVENTORY.csv')}
check['all_status_or_precise_HOLD_separate_fields']=all(r['status'] and r['content_state'] and r['restore_state'] and r['scientific_acceptance_state'] and (r['remaining_hold'] or r['status']=='ARCHIVED_RESTORE_VERIFIED') for r in m)
ss=load(R/'evidence/TWENTY_SELECTORS_VS_CURRENT_WHOLE_SOURCE_DIRECTORY_DIFFERENCE.json');tc=load(R/'evidence/TWENTY_TRUE164_CURRENT_COMMITS_AND_EXTRA_FILE_LOCATORS.json')
check['all20_source_current_exact_identity']=len(ss)==20 and all(r['source_selector_old_full_SHA_reusable'] for r in ss)
check['all20_existing_164_commit_hashes_current']=len(tc)==20 and all(r['current_commit_matches_prior'] for r in tc)
check['existing20_RESTORE_entries_real_and_unexecuted']=all(r.get('entry_script_text') for r in load(R/'evidence/EXISTING_TWENTY_RESTORE_ENTRIES_CURRENT_READBACK_AND_NEW_TARGET_ABSENCE.json')['entries'])
check['all_five_native_scope_fifteen_not_tested_preserved']=sum(r['native_restore_status']=='RESTORE_VERIFIED_NATIVE_TARGET' for r in ss)==5
check['directory_extras_count_and_never_whole_scope_PASS']=sum(len(r['extra_regular_files']) for r in ss)==14040 and sum(r['extra_logical_bytes'] for r in ss)==277152797
six=load(R/'evidence/AWMA_SIX_MANIFEST_EXACT_DIGEST_AND_CURRENT_ARTIFACT_STAT_CLOSURE.json')['records']
check['six_metadata_read_cap_gaps_closed_exactSHA']=len(six)==6 and all(r['exact_catalog_digest_match'] and r['manifest_identity_stable'] and r['before']['size']>131072 and not r['artifact_metadata_mismatches'] for r in six)
check['all14200_artifact_sizes_current']=sum(r['artifact_count'] for r in six)==14200
legacy=load(R/'evidence/LEGACY_VM_ALL494_FILE_METADATA_VS_HISTORICAL_COMPLETE_SHA_RECORDS.json')
check['all494_legacy_file_size_evidence_closed']=legacy['file_stat_count']==494 and all(not r['metadata_mismatches'] for r in legacy['groups'].values())
scal=load(R/'evidence/Q05_NATIVE_SAMPLE_EXACT_TERMINAL_SCALAR_RECHECK.json');rest=load(R/'evidence/Q05_TRUE164_NATURAL_R0_NATIVE_TARGET_CONTENT_SAMPLE_RESTORE.json')
check['natural_q05_exact_SHA_native_restore_and_terminal']=rest['archive_and_native_restored_content_equal'] and rest['source_identity_stable'] and scal['terminal_scalar_fields']['gpu_sim_cycle']==['885681'] and scal['terminal_scalar_fields']['gpu_sim_insn']==['368696302'] and scal['terminal_scalar_fields']['gpu_tot_issued_cta']==['224']
check['Q05_fixed_window_identity_not_natural']=load(R/'evidence/AWMA_EXISTING_CONSUMER_AUDIT_AND_Q05_LOCAL_ORIGINAL.json')['q05_local_current'][0]['matches_accepted_raw_log_sha256'] and rest['accepted_scope'].startswith('Separate natural')
bc=load(B/'evidence/C16_CANONICAL_SOURCE_MODELS_CURRENT_IDENTITY_AND_IMMUTABLE_RECEIPTS.json');cc=load(R/'evidence/C16_SOURCE_PROTECTED_CANONICAL_CURRENT_METADATA_NO_MODEL_READ.json')['files']
check['six_protected_original_models_still_exact_identity']=len(cc)==6 and all(all(x.get(k)==y.get(k) for k in ['path','dev','inode','size','mtime_ns','ctime_ns']) for x,y in zip(bc,cc))
bt=load(B/'evidence/TRUE164_C16_AWMA_CATALOG_AND_SIX_MODEL_METADATA.json')['models'];ct=load(R/'evidence/C16_TRUE164_AUTHORITY_CURRENT_METADATA_NO_MODEL_READ.json')['files']
check['six_authority_current_path_size_mtime']=len(ct)==6 and all(all(x.get(k)==y.get(k) for k in ['path','size','mtime_ns']) for x,y in zip(bt,ct))
plans=[r for r in rows(R/'ARCHIVE_ACTION_QUEUE.csv') if r['status']=='REQUIRES_COPY_AUTHORIZATION' and r['queue_id'].startswith('TRACE_')];keys=set();planbytes=0
for r in plans:
 x=load(R/r['manifest_reference'])
 for f in x['selected_uncovered_members']:
  key=(f['dev'],f['inode']);assert key not in keys,(key,r['source']);keys.add(key);planbytes+=f['size'];assert posixpath.normpath(x['source_root']+'/'+f['relative_path'])==f['path']
check['copy_plan_source_files_identity_dedup_relative_paths']=len(keys)==24378 and planbytes==199409597483
check['proposed_new_164_root_still_absent']=bool(load(R/'evidence/EXISTING_TWENTY_RESTORE_ENTRIES_CURRENT_READBACK_AND_NEW_TARGET_ABSENCE.json')['proposed_future_target_root'].get('error'))
check['empty_roots_rejected_before_cwd']=len(load(R/'evidence/P2_OWNER_SCOPED_NONEMPTY_ROOT_REQUESTS.json')['rejected_empty'])==3
resource=load(R/'RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json')
check['no_transfer_Source_mutation_science_start']=resource['new_archive_transfer_bytes']==0 and resource['new_Source_writes_or_deletes']==0 and resource['new_scientific_starts_stops_or_budget_mutations']==0
check['no_large_trace_or_model_rehash']=resource['big_trace_or_model_full_SHA_passes']==0
p2=load(R/'evidence/P2_BOUNDED_CURRENT_FULL_SOURCE_RAW_FILE_SHA_MANIFEST.json')
check['P2_63_exact_raw_scopes_full_Source_SHA']=p2['status']=='ALL_SOURCE_RAW_SCOPES_FROZEN' and p2['read_bytes']==222915898 and len(p2['results'])==63 and sum(len(z['files']) for z in p2['results'])==774 and all(f['identity_stable'] for z in p2['results'] for f in z['files'])
check['P2_current_Owner_digest_bindings']=all(all(z[k] in {f['sha256'] for f in z['files']} for k in ['owner_stdout_sha256','owner_terminal_sha256','owner_spec_sha256','manifest_sha256'] if z.get(k)) for z in p2['results'])
check['no_raw_payload_or_secret_upload_extensions']=not any(f.suffix in ['.traceg','.tgz','.zst','.safetensors','.pem','.key','.log'] for f in R.rglob('*') if f.is_file())
secret=[]
for f in R.rglob('*'):
 if f.is_file() and re.search(rb'-----BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY-----|(?:sk-proj-|ghp_)[A-Za-z0-9]{24,}',f.read_bytes()):secret.append(f.name)
check['no_credential_signatures']=not secret
save('VALIDATION.json',dict(checks=check,all_pass=all(check.values()),scope='Audit closure arithmetic, evidence bindings, project scope, native small restore and confidentiality only; not new science test or generic implementation-mirroring unit tests'))
print(json.dumps(check,indent=2));assert all(check.values())
