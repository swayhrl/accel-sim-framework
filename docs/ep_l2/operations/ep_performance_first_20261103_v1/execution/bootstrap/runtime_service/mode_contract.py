"""Pure draft mode/history contract. No registry, actor or acceptance writes."""
import pathlib,json,hashlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent;GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1';EXTENSION_GOAL='EP_L2_WV_RO_T_PERFORMANCE_EXPLORATION_V1'
MODES={'S':(1,0,0,0,0,'S'),'W_ONLY':(2,0,0,0,0,'W_ONLY'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R'),'F_MINUS_T':(2,1,1,0,1,'WV_M'),'F':(2,1,1,1,1,'F')}
VARIABLE={'-trace','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
REF_SHA='65474df0a47f5e16ce0314004b160cbd0a8da4d83473a1f3351e4bf5cc574062';HEAVY=('EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE')
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):
 def pairs(xs):
  d={}
  for k,v in xs:need(k not in d,'duplicate JSON field');d[k]=v
  return d
 return json.loads(P(p).read_bytes(),object_pairs_hook=pairs,parse_constant=lambda v:need(False,'nonfinite JSON'))
def exact(r):need(isinstance(r,dict)and sha(r['path'])==r['sha256'],'missing/changed immutable reference');return read(r['path'])
def digest_value(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def reference():need(sha(ROOT/'REF_282_S.json')==REF_SHA,'S282 reference drift');return read(ROOT/'REF_282_S.json')
def flags(mode):
 need(mode in MODES,'unknown formal mode');ft,c,d,t,m,_=MODES[mode]
 return {'-gpgpu_ep_l2_ft_mode':str(ft),'-gpgpu_ep_l2_tvd_clean':str(c),'-gpgpu_ep_l2_tvd_dirty':str(d),'-gpgpu_ep_l2_ro_tag_detach':str(t),'-gpgpu_ep_l2_ro_line_mshr_bypass':str(m)}
def ro_enabled(mode):need(mode in MODES,'unknown mode');return bool(MODES[mode][3]or MODES[mode][4])
FAMILY_SCOPE_SHA='99d60efe8a15121112265d52412f9a68f41040a486819197573d372fff3f7e82'
SERVICE_REQUEST_ID='EP_L2_PF_DRAM_SERVICE_FWT_GEMM_VECTOR4M_20261103_V1'
SERVICE_DATA_ROOT=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/service')
def family_scope():
 need(sha(ROOT/'FAMILY_SCOPE.json')==FAMILY_SCOPE_SHA,'DRAM family scope drift')
 q=read(ROOT/'FAMILY_SCOPE.json');need(q['request_id']==SERVICE_REQUEST_ID,'family request mismatch');return q
def family_row(s):
 rows=family_scope()['points'];found=[r for r in rows if s.get('cohort')=='EP_PERF_PF_'+r['id'].removeprefix('PF_')+'_V1']
 need(len(found)==1,'outside exact approved16 DRAM cells');r=found[0]
 need(s.get('service_family_point_id')==r['id'],'family point binding mismatch');return r
def service_profile(row):return 'PF_DRAM_'+str(row['DRAM_MHz'])+'_G32W8_L100'
def expected_peer(s):
 r=family_row(s);rows=family_scope()['points'];peers=[x for x in rows if x['input_identity_sha256']==r['input_identity_sha256'] and x['DRAM_MHz']==r['DRAM_MHz'] and x['mode']!=r['mode']]
 need(len(peers)==1,'family does not define exactly fairS/EP peer');return 'EP_PERF_PF_'+peers[0]['id'].removeprefix('PF_')+'_V1'
def check_background(s):
 r=family_row(s);base=exact(r['reference_spec_ref']);o=s['expected_effective_options']
 need(s['source_identity']==reference()['source_identity']==r['source5']==base['source_identity'],'unknown Source5 in DRAM family')
 need(s['geometry']==r['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'DRAM family geometry')
 need(s['mode']==r['mode'] and s['mode']in ['S','WV_ZERO_RO','F'],'mode outside exactcell')
 need(s['profile']==service_profile(r),'DRAM profile mismatch')
 need(type(s.get('T'))is bool and type(s.get('M'))is bool and(s['T'],s['M'])==(bool(MODES[s['mode']][3]),bool(MODES[s['mode']][4])),'typed mode switches')
 need(s.get('science_request_id')==SERVICE_REQUEST_ID and s.get('service_family_proposal_ref')==family_scope()['proposal_ref'],'scope/request binding')
 need(s.get('absolute_REF850_spec_ref')==r['reference_spec_ref'],'absolute REF850 binding')
 need(s.get('same_background_peer_cohort')==expected_peer(s),'same-background peer missing/wrong')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','program','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env','ro_qualification_ref']:
  need(s.get(k)==base.get(k),'family source/input/observer/reference field:'+k)
 need(o==exact(r['option_candidate_ref']) and len(o)==282 and all(type(k)is str and type(v)is str for k,v in o.items()),'exact family282 mismatch')
 expected=dict(base['expected_effective_options']);expected['-gpgpu_clock_domains']='1132.0:1132.0:1132.0:'+str(float(r['DRAM_MHz']))
 need(o==expected,'nonclock option changed');need(all(o[k]==v for k,v in flags(s['mode']).items()),'formal five flags mismatch')
 need(s['ordered_configs'][:-1]==base['ordered_configs'] and len(s['ordered_configs'])==len(base['ordered_configs'])+1,'base ordered configs plus exactly one final overlay required')
 overlay=s['ordered_configs'][-1];need(overlay==s.get('service_frequency_overlay_ref') and sha(overlay['path'])==overlay['sha256']==r['frequency_overlay_ref']['sha256'],'last frequency overlay mismatch')
 need(P(overlay['path']).is_relative_to(ROOT/'configs'/s['cohort']),'frequency overlay outside own runtime cohort')
 need(P(overlay['path']).read_bytes()==P(r['frequency_overlay_ref']['path']).read_bytes(),'frequency overlay bytes drift')
 for item in s['ordered_configs']:need(sha(item['path'])==item['sha256'],'ordered config drift')
 return o

def validate_anchor(s):
 q=exact(s['absolute_REF850_S_anchor_qualification_ref'])
 need(q.get('schema')=='EP_MAIN_EXACT_EXISTING_S_REFERENCE_QUALIFICATION_V1' and q.get('status')=='EXACT_EXISTING_S_HARDWARE_INPUT_OBSERVERS_QUALIFIED_FOR_MATCHED_REFERENCE' and q.get('approved_by')=='EP-MAIN','Main absolute850 source/input reference review required')
 a=exact(q['spec_ref']);p=exact(q['point_ref']);need(q.get('current_closed_state')=='CLOSED_ACCEPTED' and q.get('currently_accepted_population')is True,'REF850 no longer accepted')
 need(a['mode']==p['mode']=='S' and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED' and p['hardware_drained']is True,'REF850 not accepted completeS')
 need(a['source_identity']==p['source_identity']==s['source_identity']==q['source_identity'] and p['spec_ref']==q['spec_ref'],'absolute source/spec')
 need(a['input_identity_sha256']==p['input_identity_sha256']==s['input_identity_sha256']==q['input_identity_sha256'],'absolute input')
 need(a['geometry']==s['geometry'] and a['observer_env']==s['observer_env'],'absolute geometry/observer')
 need(q['expected_effective_options_sha256']==digest_value(a['expected_effective_options']),'absolute282 SHA')
 need(a['expected_effective_options']['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0','reference is not850MHz')
 need(s.get('REF850_usage')=='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S','REF850 cannot be matchedS_q')
 return q

def validate_fair_pair(a,b):
 check_background(a);check_background(b)
 need(a['same_background_peer_cohort']==b['cohort'] and b['same_background_peer_cohort']==a['cohort'],'not reciprocal same-background pair')
 need(a['input_identity_sha256']==b['input_identity_sha256'] and a['source_identity']==b['source_identity'],'same-background source/input mismatch')
 need('S'in {a['mode'],b['mode']} and a['mode']!=b['mode'],'pair must be S/EP')
 ignored=set(flags(a['mode']))|VARIABLE-{'-trace'}
 need({k:v for k,v in a['expected_effective_options'].items() if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items() if k not in ignored},'same-background hardware option mismatch')
 return dict(status='EXACT_SAME_BACKGROUND_PAIR_ENGINEERING_PASS',S_cohort=a['cohort']if a['mode']=='S'else b['cohort'],EP_cohort=b['cohort']if a['mode']=='S'else a['cohort'],REF850_usage='ABSOLUTE_ONLY',scientific_acceptance_granted=False)

def validate_ro(s):
 if not ro_enabled(s['mode']):need(s.get('ro_qualification_ref')is None,'ROdisabled mode must not inherit certificate authority');return dict(applicability='NOT_APPLICABLE_RO_RUNTIME_DISABLED_NOT_ZERO_INPUT_ORACLE')
 q=exact(s.get('ro_qualification_ref'));need(q.get('status')=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED'and q.get('qualified_by')=='Main','unknown ROqualification');need(q['source_identity']==s['source_identity']and q['input_identity_sha256']==s['input_identity_sha256'],'RO Source/input mismatch');need(q.get('epoch')=='whole_commandlist'and q.get('line_bytes')==128 and q.get('address_domain')=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','ROepoch/address/line scope')
 for k in ['manifest','ranges']:
  r=q[k+'_ref'];need(sha(r['path'])==r['sha256'],'RO artifact drift');need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+k]==r['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+k+'_sha256']==r['sha256'],'RO actual option binding')
 return dict(applicability='ENABLED_EXACT_CERTIFICATE_REQUIRED',qualification_ref=s['ro_qualification_ref'])

def validate_mode_cpu(s):
 if s['mode']not in ['W_ONLY','F_MINUS_T']:return dict(status='EXISTING_FORMAL_MODE_NEW_HOSTQ_STILL_REQUIRED')
 q=exact(s.get('mode_cpu_qualification_ref'));need(q.get('schema')=='EP_MAIN_SOURCE78_FORMAL_MODE_CPU_QUALIFICATION_V1'and q.get('status')=='EXACT_SOURCE78_FORMAL_MODE_CPU_PASS_NOT_APPLICATION_ACCEPTANCE'and q.get('approved_by')=='EP-MAIN','new mode CPU qualification not PASS')
 need(q['mode']==s['mode']and q['source_identity']==s['source_identity']and q['geometry']==s['geometry']and q['formal_flags']==flags(s['mode']),'modeCPU exactfamily mismatch');need(q.get('application_permission')is False,'CPUproof cannot grant app permission');need(q.get('evidence_refs'),'missing actual CPUevidence')
 for r in q['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'modeCPU evidence drift')
 if s['mode']=='W_ONLY':
  need(set(q.get('completed_controls',[]))>={'constructor32x8','partition_WAD128','a1_versions_reorder'},'WOnly exact3 not completed (HOLD/0 cannot pass)')
  actual=exact(q.get('actual_exact3_result_ref'));need(actual.get('status')=='EXACT3_ACTUAL_SOURCE78_CPU_COMPONENTS_PASS_NOT_APPLICATION_ACCEPTANCE'and actual.get('source_identity')==s['source_identity']and actual.get('model_starts')==0,'WOnly actual exact3 is HOLD/incomplete/otherSource')
  runs={x.get('label'):x for x in actual['steps']if x.get('label','').endswith('_run')};need(set(runs)=={'constructor32x8_run','partition_WAD128_run','a1_versions_reorder_run'}and all(x['returncode']==0 and x.get('process_group_closed')is True for x in runs.values()),'WOnly real completed cases/groups missing')
 return dict(status=q['status'],qualification_ref=s['mode_cpu_qualification_ref'])

def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q.get('schema')=='EP_MAIN_SOURCE78_DRAM_FAMILY_HOST_QUALIFICATION_V1'and q.get('status')=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED','new parser/engine HostQ required; oldHostQ not inherited');need(q['source_identity']==s['source_identity']and s['mode']in q['modes_qualified'],'HostQ Source/mode')
 refs=q['modules'];wanted=[s['host_engine_ref'],s['validation_module_ref'],s['mode_contract_ref']]
 for r in refs:need(sha(r['path'])==r['sha256'],'newHostQ module drift')
 need(all(r in refs for r in wanted),'newHostQ missing engine/parser/contract');return q

def validate_static(s):
 need(s['goal']==GOAL,'unchanged frontend native namespace only');o=check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'mode contract self identity');anchor=validate_anchor(s);ro=validate_ro(s);cpu=validate_mode_cpu(s);validate_hostq(s)
 return dict(schema='EP_C_SOURCE78_FORMAL_MODE_BINDING_V1',mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=s['T'],M=s['M'],RO=ro,modeCPU=cpu,anchor_qualification_ref=s['absolute_REF850_S_anchor_qualification_ref'],REF850_usage='ABSOLUTE_ONLY_NOT_MATCHED_S_Q',same_background_peer_cohort=s['same_background_peer_cohort'],physical_family='64slice32set8way/P1/1168/D512/WAD128/line128/REFqueues_DECLARED_DRAM_CLOCK/stats111/heavy0000',scientific_acceptance_granted=False,launch_permission=False)

def history_for(s):
 check_background(s);ft,v,dirty,t,m,profile=MODES[s['mode']];need(v==dirty,'initialfullV only');feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=ft==2)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=profile,formal_mode=s['mode'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')


def qualify_existing_reference(review_ref,target,formal_mode):
 """New Main closed-population review required. No acceptance/launch writes."""
 need(formal_mode in ['S','WV_ZERO_RO','F'],'only existing S/WV/F reference interface');q=exact(review_ref);need(q.get('schema')=='EP_MAIN_EXACT_EXISTING_MODE_REFERENCE_QUALIFICATION_V1'and q.get('status')=='EXACT_EXISTING_HARDWARE_INPUT_OBSERVERS_REFERENCE_REUSE_QUALIFIED'and q.get('approved_by')=='EP-MAIN','new exactreference review required')
 a=exact(q['spec_ref']);p=exact(q['point_ref']);need(q.get('current_closed_state')=='CLOSED_ACCEPTED'and q.get('currently_accepted_population')is True,'reference no longeraccepted');need(p['spec_ref']==q['spec_ref'],'reference original spec drift');need(a['mode']==p['mode']==formal_mode and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and p['hardware_drained']is True,'reference type/status')
 need(a['source_identity']==p['source_identity']==target['source_identity']and a['input_identity_sha256']==p['input_identity_sha256']==target['input_identity_sha256'],'referenceSource/input');need(a['geometry']==target['geometry']and a['observer_env']==target['observer_env']and a['expected_effective_options']==target['expected_effective_options'],'reference actualhardware/input/observers/options differ')
 return dict(status='EXACT_REFERENCE_REUSE_REVIEW_ONLY_NO_NEW_ACCEPTANCE',review_ref=review_ref,point_ref=q['point_ref'],launch_permission=False,scientific_acceptance_granted=False)
