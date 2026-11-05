"""Exact Main-signed closed-result metadata compatibility, no source relabel/write/start."""
from pathlib import Path
import gzip,hashlib,json,os
HERE=Path(__file__).resolve().parent
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def exact(r):need(type(r)is dict and sha(r['path'])==r['sha256'],'exact banner evidence SHA drift');return read(r['path'])
def check(s,raw,approval_ref,consumer_ref):
 a=exact(approval_ref)
 need(a.get('schema')=='EP_MAIN_PFV5_A_EXACT_BUILD_BANNER_COMPATIBILITY_V1'and a.get('approved_by')=='EP-MAIN'and a.get('explicit_Main_closed_consumer_approval')is True,'Main signed exact banner compatibility required')
 need(a.get('allowed_scope')=='ONLY_THREE_ALREADY_SPENT_A_COHORTS'and a.get('Source5')==s['source_identity']and a['canonical_core_commit']==s['source_identity']['core_source_commit'],'canonical Source5 unchanged')
 need(a.get('consumer_entry_ref')==consumer_ref and a.get('compatibility_verifier_ref')==dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),'Main signed exact consumer/verifier bytes required')
 need(a['no_Source_Spec_raw_HOLD_changes']is True and a['science_starts']==0 and a['consume_count_refund_or_remaining_changes']is False,'no replay/refund/relabel compatibility')
 rows=a['exact_cohort_rows'];need(len(rows)==3 and len({r['cohort']for r in rows})==3,'exact three closed cohorts')
 row=next((r for r in rows if r['cohort']==s['cohort']),None);need(row is not None and row['source_feature_profile']==s['source_feature_profile'],'outside exact closed cohort/profile')
 need(exact(row['sealed_spec_ref'])==s and sha(row['original_root_spec_ref']['path'])==row['sealed_spec_ref']['sha256'],'original root/sealed Spec identity')
 need(str(Path(raw))==row['raw_ref']['path']and sha(raw)==row['raw_ref']['sha256'],'exact original closed raw required')
 oldhold=exact(row['original_HOLD_ref']);need(oldhold['spent_start_preserved']is True and oldhold['scientific_acceptance_granted']is False,'original HOLD missing')
 done=exact(row['NativeExit_ref']);need(done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']and done['source_identity']==s['source_identity'],'same natural complete model required')
 # Main signs all the original build evidence; verify actual full bytes, not prefixes.
 final=exact(a['final_whole_byte_ref']);first=exact(a['full_recompile_ref']);closure=exact(a['source_hash_closure_ref'])
 need(final['full_recompile_ref']==a['full_recompile_ref']and final['ELF_complete_SHA_MATCH']is True and final['gpgpusim_library_complete_SHA_MATCH']is True and final['ELF_executions']==first['ELF_executions']==0,'full CPU byte proof required')
 need(first['translation_units']==first['object_byte_MATCH']==142 and not first['object_mismatches']and len(first['all_archive_results'])==8,'all142 TU and8 archive proof')
 for r in [final['original_output_ref'],final['new_output_ref']]:need(sha(r['path'])==r['sha256']==s['source_identity']['binary_sha256'],'whole original/reproduced ELF proof mismatch')
 for r in [first['original_gpgpusim_library_ref'],first['reproduced_gpgpusim_library_ref']]:need(sha(r['path'])==r['sha256']==s['source_identity']['archive_sha256'],'whole gpgpusim library mismatch')
 cp=exact(first['compile_plan_ref']);need(cp['translation_units']==142 and len(cp['rows'])==142,'exact compile plan population')
 need(all(r['member_order_MATCH']and r['byte_MATCH']and r['original_ref']['sha256']==r['new_ref']['sha256']for r in first['all_archive_results']),'ordered archive proof mismatch')
 need(closure['core_commit']==s['source_identity']['core_source_commit']and closure['count']==len(closure['rows'])==832 and closure['all_current_tracked_files_MATCH_commit']is True,'complete tracked Source7b4 closure')
 main=exact(a['Main_independent_build_review_ref'])
 need(main['status']=='MAIN_INDEPENDENT832_SOURCE142_OBJECT8_ARCHIVE_AND_WHOLE_ELF_BYTE_REPRODUCTION_PASS'and main['Source7b4_tracked_count']==832 and len(main['objects'])==142 and main['archive_count']==8 and main['models_or_ELF_executions']==0,'Main independent full build review absent')
 need(main['actual_ELF_SHA256']==s['source_identity']['binary_sha256']and main['actual_library_SHA256']==s['source_identity']['archive_sha256']and main['final_proof_ref']['sha256']==a['final_whole_byte_ref']['sha256']and main['full_recompile_ref']['sha256']==a['full_recompile_ref']['sha256']and main['tracked_source_closure_ref']['sha256']==a['source_hash_closure_ref']['sha256'],'Main independent review exact proof refs')
 # Reuse the Main-signed full object/archive/source audit; no repeated large
 # build/hash suite. Current sealed ELF/library SHA checks above remain strict.
 # Literal banner validation remains strict and separate from canonical Source identity.
 core=[];framework=[];op=gzip.open if str(raw).endswith('.gz')else open
 with op(raw,'rt')as f:
  for line in f:
   if 'gpgpu-sim_git-commit-'in line:core.append(line.rstrip('\n'))
   if 'accelsim-commit-'in line:framework.append(line.rstrip('\n'))
 need(core==a['exact_core_banner_lines']==row['observed_core_banner_lines']and framework==a['exact_framework_banner_lines']==row['observed_framework_banner_lines'],'full exact observed banner lines changed')
 need(a['exact_core_tokens']==['78f4b59']and a['exact_framework_tokens']==['9dd1ee5'],'nonfinite banner token exception')
 return dict(approval_ref=approval_ref,canonical_Source5=s['source_identity'],actual_core_banner_lines=core,actual_framework_banner_lines=framework,actual_core_tokens=a['exact_core_tokens'],actual_framework_tokens=a['exact_framework_tokens'],full142_TU_8_archives_wholeELF_wholeLibrary_and832_Source_proof=True,final_whole_byte_ref=a['final_whole_byte_ref'],source_hash_closure_ref=a['source_hash_closure_ref'],original_HOLD_ref=row['original_HOLD_ref'],raw_ref=row['raw_ref'],no_source_relabel=True,no_raw_rewrite=True,scientific_permission=False)
