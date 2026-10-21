#!/usr/bin/env python3
"""Only small Git metadata/configuration preparation. No execution of producer/native/runner.
Does not read trace bodies, construct E Coordinator, write E registry, or compute E run/Q ids.
"""
import copy,datetime,hashlib,json,pathlib,shlex,subprocess
ROOT=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1')
OUT=pathlib.Path(__file__).resolve().parent
E_COMMIT='0b608f2f9142d44e53d54a55679c1b00b504d6a6'
OLD_CORE='d010911e3174a3764791183cd108fe4664ba8731'
FW='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
REFS=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(commit,path,role):
 raw=subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+path]);assert len(raw)<=1024*1024
 r={'repo':'swayhrl/accel-sim-framework','commit':commit,'path':path,'sha256':sha(raw),'role':role};REFS.append(r);return raw,r

def doc(commit,path,role):
 raw,r=blob(commit,path,role);return json.loads(raw),r

def write(n,d):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def options(paths):
 # Existing headroom_config.options grammar: shlex comments/quoted multiline/pairs.
 out={}
 for p in paths:
  ts=shlex.split(pathlib.Path(p).read_text(),comments=True);assert len(ts)%2==0
  for k,v in zip(ts[::2],ts[1::2]):assert k.startswith('-') and k!='-config';out[k]=v
 return out
q,qr=doc(E_COMMIT,'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_FWT_FIRST_PAIR_CONTINUATION_r1/FWT_7_21_QUALIFICATION.json','existing_exact_main61_FWT_Q_not_SGEMM_Q')
assert qr['sha256']=='1d3af457edec4aa6cd175a8c11bbbe4f9c6d6159f95789294850e2f2fd74c2c9'
assert q['source_identity']['core_source_commit']==OLD_CORE and q['status']=='INDEPENDENTLY_QUALIFIED'
ident=q['source_identity'];reg,rr=doc(E_COMMIT,'docs/ep_l2/review_packs/MS20261020_E2_MAIN_ROLLING_r1/EXPLORATORY_SGEMM_REGISTRATION.json','SGEMM_existing_frozen_trace_exploratory_HOLD')
assert reg['status']=='REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE'
release,ar=doc('0ae16a6c48bdffbdf38ced4da6c76dda4981a813','docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/RELEASE.json','formal_main61_producer_release')
assert release['source_identity']==ident
static,sr=doc('663fba57b7dc6428d613db443d6ff2f3c99e33d5','docs/ep_l2/review_packs/MS20261021_A2_DF_CANDIDATE_COMPATIBILITY_r1/SUPPORT_GAPS.json','prior_completed_static_review_reuse_only')
map_old,mr=doc(E_COMMIT,'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/GATE_COVERAGE.json','same_source_existing_native_case_map')
_,delta=doc(E_COMMIT,'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1/DELTA_APPLICABILITY_REVIEW.json','existing_E_same_source_delta_disposition')
paths=[];copied=[]
prefix='docs/ep_l2/review_packs/MS20261020_E_MAIN_SF_QUALIFICATION_r1/configs/'
for n in ['base-0.config','base-1.config','base-2.config']:
 raw,r=blob(E_COMMIT,prefix+n,'original_finite_H0_base_config');dest=OUT/'CONFIGS'/n;dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw);paths.append(dest);copied.append({'name':n,'path':str(dest),'sha256':sha(raw),'source_ref':r})
sraw,sref=blob(E_COMMIT,prefix+'FWT_7_21_S.config','same_policy_finite_S_overlay_no_input_specific_oracle')
fraw,fref=blob(E_COMMIT,prefix+'FWT_7_21_F.config','same_policy_finite_F_overlay_template_not_FWT_certificate_inheritance')
(OUT/'CONFIGS/S.config').write_bytes(sraw)
certkeys={'-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_scope'}
mech='''# PREPARATION ONLY / UNSEALED: fixed full F mechanism; C SGEMM artifact binding absent.
# T/M stay ON. Required five input-specific oracle binding options are deliberately absent.
# This file is not a launchable complete profile and must never inherit FWT/Conv ranges.
'''+''.join(line+'\n' for line in fraw.decode().splitlines() if not any(line.startswith(k+' ') for k in certkeys))
(OUT/'CONFIGS/F_MECHANISM_UNSEALED.config').write_text(mech)
S=options(paths+[OUT/'CONFIGS/S.config']);F=options(paths+[OUT/'CONFIGS/F_MECHANISM_UNSEALED.config'])
assert S==q['supported_profiles']['S']['effective_options']
assert F=={k:v for k,v in q['supported_profiles']['F']['effective_options'].items() if k not in certkeys}
assert all(k not in F for k in certkeys)
for d in [S,F]:
 assert '-gpgpu_ep_l2_diag_l2_large_capacity' not in d # Old main61 does not register this flag.
 assert d['-gpgpu_ep_l2_diag_copy_free']==d['-gpgpu_ep_l2_diag_l2_data_free']=='0'
 assert d['-gpgpu_ep_l2_descriptor_pool_size']=='512' and d['-gpgpu_ep_l2_descriptor_per_line_cap']=='32'
 assert d['-gpgpu_ep_l2_wad_entries']=='128' and d['-gpgpu_ep_l2_bank_ops']=='1'
 assert d['-gpgpu_ep_l2_payload_mode']=='2' and d['-gpgpu_ep_l2_wbuf_entries']=='16'
 assert d['-gpgpu_ep_l2_static_s64']==d['-gpgpu_ep_l2_tvd_fixed_entries']=='0'
 assert d.get('-gpgpu_max_cycle','0')=='0' and d.get('-gpgpu_max_insn','0')=='0'
diff={k:{'S':S.get(k),'F':F.get(k)} for k in sorted(set(S)|set(F)) if S.get(k)!=F.get(k)}
assert set(diff)=={'-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'}
common={k:v for k,v in S.items() if k not in diff}
write('OPTION_DIFF_AND_INVARIANTS.json',{'schema':'A2_MAIN61_SGEMM_FINITE_S_F_RAW_OPTION_PROPOSAL_V1','status':'PREPARED_CONFIG_MECHANISM_ONLY_UNSEALED_F_ORACLE','source_identity':ident,'ordered_common_configs':copied,'S_profile':{'path':str(OUT/'CONFIGS/S.config'),'sha256':sha(sraw),'source_ref':sref},'F_mechanism_unsealed':{'path':str(OUT/'CONFIGS/F_MECHANISM_UNSEALED.config'),'sha256':sha(mech.encode()),'template_ref':fref},'S_effective_options':S,'F_mechanism_effective_options_without_input_binding':F,'mechanism_option_diff':diff,'shared_invariants':common,'pending_F_binding_options':sorted(certkeys),'complete_F_diff':'Five mechanism toggles above plus five actual C SGEMM candidate artifact binding options after publication; no other variable options','runtime_config_or_run_key':'NOT_COMPUTED_E_OWNER_ONLY','scope':'Ordered raw assets/options are exact preparation, not E qualification or a launch spec.'})
# Verify and map all eighteen ALREADY accepted same-main61 gate metadata, without rerunning tests.
gates=[]
E_ROOT='/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/'
for name,g in q['gates'].items():
 assert g['status']=='PASS' and g['production_driven']
 rel=g['evidence_path'].removeprefix(E_ROOT);obj,ref=doc(E_COMMIT,rel,'existing_main61_production_gate_metadata')
 assert ref['sha256']==g['evidence_sha256']
 gates.append({'gate':name,'existing_status':'PASS_ALREADY_E_ACCEPTED_ON_EXACT_MAIN61','same_source_reuse_proposed':True,'evidence_ref':ref,'current_native_cases_from_E_map':map_old['gate_current_case_map'].get(name,[]),'new_runs_required_by_this_packet':0,'SGEMM_specific_remainder':'E confirms exact profile/input binding and gate applicability; no copied qualification id'})
gaps=[
 {'id':'SGEMM-CANDIDATE-FALLBACK-BINDING','owner':'C then A2/E2','status':'MISSING_PENDING_C_PUBLICATION','need':'Own exact SGEMM empty ranges and SAFE_FALLBACK_NO_CERTIFIED_LINES manifest with NO_READONLY_CERTIFICATION, exact command SHA/whole-commandlist, input identity, pinned source commit/path/SHA. Unknown RO remains UNKNOWN; T/M ON. No borrowed Conv/FWT certificate.'},
 {'id':'SGEMM-EXACT-S_F-INPUT-Q','owner':'E2','status':'PENDING_INDEPENDENT_QUALIFICATION','need':'Review existing exploratory frozen trace registration scope, original complete byte/grammar/non-atomic evidence, mandatory current content identity and own approved input_semantics binding for exact main61; no old-runtime or FWT input Q inheritance.'},
 {'id':'SGEMM-PARSER-CONFIG-FALLBACK-SEAL','owner':'E2','status':'PENDING_INDEPENDENT_QUALIFICATION','need':'Bind S/F ordered raw configs, actual effective finite geometry/P1/service, C candidate artifacts and own parser/profile/input Q/run hashes. Confirm existing main61 parser supports chosen fallback/profile without modifying current capacity parser or registry.'},
 {'id':'SGEMM-NATIVE-EVIDENCE-DISPOSITION','owner':'E2','status':'REUSE_18_EXACT_MAIN61_GATES_PROPOSED_NOT_NEW_Q','need':'Review same-source coverage table and existing native fallback case; only a real unclosed input-specific obligation can justify a later separately authorized bounded native, no automatic17/OFF replay or rebuild.'},
 {'id':'SGEMM-FUTURE-APP-AUTHORITY','owner':'E2/user','status':'NOT_AUTHORIZED_BY_BATCH','need':'After qualification, submit explicit independent cohort/2 starts/2x384MiB endpoint reservation plus actual metadata/qualification/collector margin/resources and walltime UNKNOWN. No queue or execution here.'}
]
write('QUALIFICATION_COVERAGE_MAP.json',{'schema':'A2_SAME_MAIN61_EVIDENCE_REUSE_AND_SGEMM_INPUT_GAPS_V1','source_identity':ident,'existing_FWT_qualification_ref':qr,'FWT_original_exact_Q_retained':True,'reuse_boundary':'Same producer general native production obligations may be reused subject E review; FWT/Conv input-specific Q, oracle and endpoint results never become SGEMM qualification. New93a9 F evidence is not needed for choosing this unchanged main61 cohort, and cannot substitute it.','existing_gate_count':18,'existing_native_gates':gates,'E_prior_delta_disposition_ref':delta,'input_specific_gaps':gaps,'old_joint_fixture_ref':q['unqualified_extra_joint_scope'],'joint_scope':'Frozen failed/unqualified joint fixture remains so; no promotion or replacement test here','source_recapture_and_numeric':'Missing exact source/capture/numeric payloads retained in F packet. They limit those claims, not a new universal gate revoking existing frozen-trace Q; E must decide exact SGEMM requested model scope.'})
entry=next(x['commandlist_path'] for x in json.loads((ROOT/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/CANDIDATE_AUDIT.json').read_text())['results'] if x['workload']=='sgemm') if (ROOT/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/CANDIDATE_AUDIT.json').exists() else '/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sgemm/_i___data_medium_input_matrix1_txt___data_medium_input_matrix2t_txt___data_medium_input_matrix2t_txt__o_matrix3_txt/traces/kernelslist.g'
write('PROPOSAL.json',{'schema':'A2_MAIN61_SGEMM_CONFIGURATION_PREPARATION_V1','batch_id':'EPL2_WORKLOAD_PREPARATION_BATCH_r2','task_id':'A2-SGEMM-MAIN61-CONFIG-PROPOSAL-r1','status':'MISSING_C_PUBLISHED_BINDING_NOT_E_QUALIFIED_NOT_ADOPTED','source_identity':ident,'binary':{'path':release['binary_path'],'sha256':release['binary_sha256']},'archive':release['production_archive'],'producer_release_ref':ar,'registration_ref':rr,'registration_id':reg['registration_id'],'cohort':'INDEPENDENT_EXPLORATORY_FROZEN_TRACE_MODEL_NOT_ORIGINAL_SEVEN_MAIN_OR_CAPACITY','input':{'entry':entry,'trace_content_sha256':reg['trace_content_sha256'],'trace_manifest':reg['trace_manifest'],'complete_commandlist':reg['complete_commandlist'],'expected_instructions':reg['expected_full_instructions'],'kernel_count':1,'epochs':'all','source_capture_numeric_scope':reg['capture_source_scope'],'large_trace_rehashed_or_scanned':False},'proposed_profiles':['S','F'],'fixed_F_switches':{'W':1,'V':1,'T':1,'M':1},'finite_geometry':{'payload_slots':1168,'resident_tags':1024,'line_MSHR':128,'descriptors':512,'per_address':32,'shared_WAD_TVD':128,'legacy_WB_parameter':16,'banks':4,'bank_ops_per_physical_cycle':1,'sector_bytes':32,'line_bytes':128},'raw_options':'OPTION_DIFF_AND_INVARIANTS.json','C_fallback_binding':None,'F_binding_file':'CONFIGS/F_MECHANISM_UNSEALED.config','complete_F_config_available':False,'input_specific_qualification':'PENDING_E_ONLY','launch_spec_qualification_run_key_created':False,'prior_static_review_ref':sr,'qual_coverage':'QUALIFICATION_COVERAGE_MAP.json','configuration_proposal_does_not_authorize_execution':True,'no_capacity_flag':'Old main61 has no capacity master option; do not append either0 or1. All mechanism/local ideal flags fixed finite as original policies.','work_performed':{'new_simulations':0,'new_native':0,'main_binary_rebuilds':0,'new_mechanisms':0,'E_registry_CLIENT_lease_changes':0,'large_trace_scan':0},'proposed_future_cost_only':{'starts_if_separately_approved':2,'endpoint_cap_bytes_each':402653184,'endpoint_pair_cap_bytes':805306368,'native_collector_metadata_overhead':'Separately compute during original E admission; not included or allocated here','walltime':'UNKNOWN_NOT_STATIC_SCAN_TIME'},'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
write('REFERENCES.json',{'source_refs':REFS,'ref_scope':'Small existing exact published metadata/configs only; no native assertions manufactured or repeated'})
print(json.dumps({'status':'MISSING_C_PUBLISHED_BINDING','existing_same_main61_gate_refs_verified':len(gates),'S_options':len(S),'F_unsealed_options':len(F),'mechanism_changes':len(diff),'new_native_build_app':0}))
