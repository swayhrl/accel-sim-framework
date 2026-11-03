"""Finite SYSTEM850 Host preflight candidate. Pure read/validate; no launch."""
import json,pathlib,hashlib
P=pathlib.Path;C=P(__file__).resolve().parent.parent
M=json.loads((C/'MATCHED_S_EP_CONFIG_MATRIX.json').read_text());SOURCE=M['source_identity'];CELLS={r['id']:r for r in M['cells']}
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def exact(r):need(sha(r['path'])==r['sha256'],'reference drift');return json.loads(P(r['path']).read_text())
def check(s):
 need(s['cohort'] in CELLS,'outside finite approved candidate domain');cell=CELLS[s['cohort']]
 need(s['source_identity']==SOURCE,'exactSource78 five identity');need(s['mode'] in ['S','WV_ZERO_RO'] and s['mode']==cell['mode'],'mode not qualified here')
 need(s['profile']=='PFV2_SYSTEM850_'+cell['family'],'profile mismatch');need(s['geometry']==cell['geometry'],'Tag geometry mismatch')
 need(s['input_identity_sha256']==cell['input_identity_sha256'],'input mismatch');base=exact(cell['old_REF850_spec_ref']);binding=exact(s['input_binding_ref']);need(binding['input_identity_sha256']==s['input_identity_sha256'],'binding input mismatch')
 for k in ['expected_CTA','expected_instructions','expected_kernel_scopes','expected_kernel_launches','all_unique_kernel_members','command_count','observer_env','numeric_output','original_capture_completeness','source_worktrees','binary_path','static_library_path','source_keep']:
  need(s[k]==base[k],'inherited input/observer contract changed '+k)
 opts=s['expected_effective_options'];expected=exact(cell['option_preview_ref']);need(len(opts)==282 and opts==expected,'exact282 options drift')
 need(opts['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0' and opts['-dram_latency']=='100','850/L100 boundary')
 need(opts['-gpgpu_ep_l2_ro_tag_detach']==opts['-gpgpu_ep_l2_ro_line_mshr_bypass']=='0','RO not in this scope')
 need(opts['-gpgpu_ep_l2_descriptor_pool_size']=='512' and opts['-gpgpu_ep_l2_descriptor_per_line_cap']=='32' and opts['-gpgpu_ep_l2_wad_entries']=='128' and opts['-gpgpu_ep_l2_bank_ops']=='1','fixed finite metadata/bank resources')
 need(s['ordered_configs'][:-1]==base['ordered_configs'],'base config order changed')
 for r in s['ordered_configs']:need(sha(r['path'])==r['sha256'],'ordered config SHA drift')
 need(s['source_keep'] is True,'SOURCE_KEEP required')
 need(s['launch_permission'] is False and s['goal'] is None and s['fresh_scope_request_id'] is None and s['automatic_retry'] is False and s['refund'] is False and s['old_application_acceptance_inherited'] is False,'candidate may not inherit science authority')
 return {'schema':'EP_PF_V2_SYSTEM850_HOST_CANDIDATE_CHECK_V1','status':'PASS_ENGINEERING_ONLY_NOT_NATIVE_QUALIFIED','cohort':s['cohort'],'geometry':s['geometry'],'full282':True,'input_population':True,'science_launch_permission':False}
