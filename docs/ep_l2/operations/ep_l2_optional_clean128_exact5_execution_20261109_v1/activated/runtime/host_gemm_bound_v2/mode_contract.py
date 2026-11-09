"""Exact new-Source conditional-F contract. No actors or authority writes."""
from pathlib import Path
import json,hashlib
P=Path
SOURCE={'core_source_commit': '812fe1e029b4fb09afaf3d8d25d3f909464cc06c', 'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7', 'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b', 'archive_sha256': 'a7e9c8ce045710c8f3655aebb82a65628a5a18638036af17fa0ec8c755580d3e', 'binary_sha256': 'a60600a418e6460e7aaf896b62469be0612046d0f4da34ac8c98da2eed3852e1'}
REQUEST='EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1'
CASES={'EP_PERF_UMT1_CONV3072_F_BASELINE_850_V1': 'F_BASELINE', 'EP_PERF_UMT1_CONV3072_F_PRESSURE_EPOCH_850_V1': 'F_PRESSURE_EPOCH'}
TABLE_REFS={'F_BASELINE': {'bytes': 11816, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/unified_memory_taxonomy_20261106_v1/agent_d/requests/CONV3072_F_BASELINE_EFFECTIVE_283.json', 'sha256': '89aa9bb4cec93c12d966fb0f03ced7900b725f8a42922256d3d4b06fe6d106a6'}, 'F_PRESSURE_EPOCH': {'bytes': 11816, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/unified_memory_taxonomy_20261106_v1/agent_d/requests/CONV3072_F_PRESSURE_EPOCH_EFFECTIVE_283.json', 'sha256': '8d11fe30bd4050f428ff80c49a3e6c5c4e3bc049802038830849f6936bbd85a1'}}
INPUT_ID='438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e'
MODES={x:(2,1,1,1,1,'F')for x in CASES.values()}
ROOT=P(__file__).parent
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):
 def pairs(xs):
  d={}
  for k,v in xs:need(k not in d,'duplicate JSON key');d[k]=v
  return d
 return json.loads(P(p).read_bytes(),object_pairs_hook=pairs)
def exact(r):need(sha(r['path'])==r['sha256'],'immutable ref drift');return read(r['path'])
def flags(mode):
 need(mode in MODES,'exact two F modes')
 return {'-gpgpu_ep_l2_ft_mode':'2','-gpgpu_ep_l2_tvd_clean':'1','-gpgpu_ep_l2_tvd_dirty':'1','-gpgpu_ep_l2_ro_tag_detach':'1','-gpgpu_ep_l2_ro_line_mshr_bypass':'1','-gpgpu_ep_l2_ro_pressure_epoch':str(int(mode=='F_PRESSURE_EPOCH'))}
def ro_enabled(mode):need(mode in MODES,'exact F mode');return True
def family_row(s):check_background(s);return dict(id=s['cohort'],cohort=s['cohort'],mode=s['mode'],DRAM_MHz=850)
def check_background(s):
 need(s['cohort']in CASES and s['mode']==CASES[s['cohort']],'exact newF cohort/mode')
 need(s['science_request_id']==REQUEST and s['source_identity']==SOURCE,'exact request/new Source5')
 need(s['input_identity_sha256']==INPUT_ID,'exact frozen Conv/Scan input')
 need(s['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'exact G32x8')
 need(s['profile']=='UMT1_CONV_850_G32W8_L100','exact service profile')
 need(s['T']is True and s['M']is True,'F T/M preserved')
 need(s['expected_effective_options']==exact(TABLE_REFS[s['mode']])and len(s['expected_effective_options'])==283,'exact283 values')
 need(all(s['expected_effective_options'][k]==v for k,v in flags(s['mode']).items()),'conditional F switch vector')
 need(s['old_application_acceptance_inherited']is False,'no oldSource application inheritance')
 return s['expected_effective_options']
def validate_ro(s):
 q=exact(s['ro_qualification_ref'])
 need(q['status']=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED','newSource actual RO loader')
 need(q['source_identity']==SOURCE and q['input_identity_sha256']==INPUT_ID,'new Source-specific RO identity')
 need(q['epoch']=='whole_commandlist'and q['line_bytes']==128 and q['address_domain']=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','whole epoch/canonical address')
 for k in ['manifest','ranges']:
  r=q[k+'_ref'];need(sha(r['path'])==r['sha256'],'RO content pin')
  need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+k]==r['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+k+'_sha256']==r['sha256'],'RO actual option/content binding')
 evidence=exact(q['new_source_loader_audit_ref'])
 need(evidence['source_identity']==SOURCE and evidence['input_identity_sha256']==INPUT_ID,'newSource loader audit identity')
 for r in evidence['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'RO loader proof drift')
 return dict(applicability='NEW_SOURCE_EXACT_INPUT_RO_LOADER_REQUIRED',qualification_ref=s['ro_qualification_ref'])
def validate_static(s,candidate=False):
 check_background(s)
 need(s['mode_contract_ref']['sha256']==sha(__file__),'mode contract self pin')
 for field in ['source_qualification_ref','eligibility_ref','mode_cpu_qualification_ref','host_qualification_ref']:
  q=exact(s[field]);need(q['source_identity']==SOURCE,'qualification newSource:'+field)
  need(q.get('application_acceptance_granted',False)is False,'engineering not application acceptance')
  for r in q.get('evidence_refs',{}).values():need(sha(r['path'])==r['sha256'],'engineering proof drift:'+field)
 host=exact(s['host_qualification_ref'])
 need(host['modes_qualified']==sorted(MODES)and host['cohorts_qualified']==sorted(CASES),'exact2 HostQ')
 for r in host['modules']:need(sha(r['path'])==r['sha256'],'Host module drift')
 need(all(s[k]in host['modules']for k in ['host_engine_ref','host_common_ref','mode_contract_ref','validation_module_ref']),'Host module graph')
 ro=validate_ro(s)
 if not candidate:
  main=exact(s['Main_engineering_binding_ref'])
  need(main.get('approved_by')=='EP-MAIN'and main.get('cpu_reviewed_by')=='EP-MAIN'and main.get('status')=='MAIN_REVIEWED_EXACT_SOURCE283'and main.get('independent_review_pass')is True,'Main independent engineering signature required')
  need(main['source_identity']==SOURCE and main['request_id']==REQUEST,'Main exact Source/request signature')
 return dict(schema='EP_PFV5_B1_NEW_SOURCE_F_BINDING_V1',mode=s['mode'],numeric_profile='F',T=True,M=True,RO=ro,launch_permission=False,scientific_acceptance_granted=False)
def validate_fair_pair(a,b):
 check_background(a);check_background(b)
 need(a['same_background_peer_cohort']==b['cohort']and b['same_background_peer_cohort']==a['cohort'],'reciprocal peers')
 need({a['mode'],b['mode']}==set(MODES),'same newSource F baseline/optimized pair')
 need(a['source_identity']==b['source_identity']and a['input_identity_sha256']==b['input_identity_sha256'],'same Source/input')
 ignored={'-gpgpu_ep_l2_ro_pressure_epoch'}
 need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'matched283 background')
 return dict(status='EXACT_SAME_SOURCE_MATCHED_F_POLICY_PAIR',scientific_acceptance_granted=False)
def history_for(s):
 check_background(s)
 return dict(identity=dict(feature_vector=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=True),termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile='F',formal_mode=s['mode'],profile_semantics=dict(effective_options=s['expected_effective_options'],research_switches=dict(V=1,T=1,M=1)),trace_files=[dict(name='commandlist',path=s['trace_entry'])],entry_trace_name='commandlist')
