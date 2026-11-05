import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
SYSTEM_REQUEST_ID='EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1';SERVICE_REQUEST_ID=SYSTEM_REQUEST_ID
MODES={'S':(1,0,0,0,0,'S'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R')}
FAMILY_SCOPE_SHA='3687d8ccfb60594d7dfb6c64480bea0ede5b7e0ec18614b2fa2797fb6e40baf0'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def exact(r):need(sha(r['path'])==r['sha256'],'immutable metadata drift');return read(r['path'])
def rmatch(a,b):return a==b
def family_scope():need(sha(ROOT/'FAMILY_SCOPE.json')==FAMILY_SCOPE_SHA,'scope drift');return read(ROOT/'FAMILY_SCOPE.json')
def family_row(s):
 rows=[r for r in family_scope()['points']if r['id']==s['cohort']];need(len(rows)==1,'outside exact3');return rows[0]
def flags(mode):
 need(mode in MODES,'mode');return dict(zip(['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'],map(str,MODES[mode][:5])))
def ro_enabled(mode):need(mode in MODES,'mode');return False
def expected_peer(s):return family_row(s)['peer_cohort']
def check_background(s):
 row=family_row(s);base=exact(row['base_input_spec_ref']);options=exact(row['option_preview_ref'])
 need(s['science_request_id']==SYSTEM_REQUEST_ID and s['source_identity']==family_scope()['source_identity'],'exact request/newSource')
 need(s['source_feature_profile']==row['source_feature_profile'] and s['mode']==row['mode']and s['geometry']==row['geometry'],'exact profile/mode/geometry')
 need(s['expected_effective_options']==options and len(options)==283,'full283 exact background')
 need(not s['T']and not s['M']and s['ro_qualification_ref']is None,'no RO authority')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','observer_env']:
  need(s[k]==base[k],'frozen complete input/observer drift:'+k)
 need(all(options[k]==v for k,v in flags(s['mode']).items()),'exact source mode switches')
 need(options['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and options['-dram_latency']=='100'and options['-gpgpu_frfcfs_dram_sched_queue_size']=='128','background')
 need(options['-gpgpu_cache:dl2']=='S:32:128:8,L:B:m:L:P,A:128:1,128:0,32','exact geometry')
 need(all(options[k]=='1'for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats']),'observer111')
 need(s['same_background_peer_cohort']==row['peer_cohort'],'peer')
 need([r['sha256']for r in s['ordered_configs'][:-1]]==[r['sha256']for r in base['ordered_configs']],'frozen config prefix')
 for r in s['ordered_configs']:need(sha(r['path'])==r['sha256'],'ordered config drift')
 return options
def qualify_history_spec(s):
 check_background(s);return dict(status='EXACT_NEW_SOURCE_G32W8_FULL283_MATCH',old_Source_performance_inherited=False)
def geometry_module():
 class G:
  @staticmethod
  def qualify_history_spec(s):return qualify_history_spec(s)
 return G()
def validate_fair_pair(a,b):
 check_background(a);check_background(b);need(a['source_identity']==b['source_identity']and a['input_identity_sha256']==b['input_identity_sha256'],'matched source/input')
 ignored=set(flags('S'))|{'-gpgpu_ep_l2_tvd_cold_filter'}
 need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'unfair background')
 if a['mode']==b['mode']:need(set(k for k in a['expected_effective_options']if a['expected_effective_options'][k]!=b['expected_effective_options'][k])=={'-gpgpu_ep_l2_tvd_cold_filter'},'WV optimization delta')
 return dict(status='SAME_SOURCE_MATCHED_ENGINEERING_ONLY',science_permission=False)
def validate_anchor(s,mode='S'):return dict(status='NO_ACCEPTED_NEW_SOURCE_ANCHOR_OLD_SOURCE_CONTEXT_ONLY')
def validate_mode_cpu(s):
 q=exact(s['mode_cpu_qualification_ref']);need(q['Source5']==s['source_identity'],'CPU Source5');r=exact(q['actual283_ref'])
 need(r['Source5']==s['source_identity']and all(x['returncode']==0 and x['constructor_pass']and x['expected_options']==x['actual_options']==283 and not x['mismatches']for x in r['runs']),'actual283 constructor proof')
 need(exact(q['maps'][s['source_feature_profile']])==s['expected_effective_options'],'profile map')
 return dict(status='NEW_SOURCE_PRODUCTION_CPU283_MODE_REBIND',application_NI='NOT_MEASURED',new_application_NI_is_launch_gate=False)
def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q['source_identity']==s['source_identity']and q['status']=='PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE','Host qualification')
 for r in q['modules']:need(sha(r['path'])==r['sha256'],'Host module pin')
 return q
def validate_static(s):
 need(s['goal']==GOAL,'namespace');check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'modecontract pin');cpu=validate_mode_cpu(s);validate_hostq(s)
 return dict(mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=False,M=False,RO={'applicability':'NOT_APPLICABLE_RO_RUNTIME_DISABLED'},modeCPU=cpu,scientific_acceptance_granted=False,launch_permission=False)
def history_for(s):
 check_background(s);f,v,d,t,m,p=MODES[s['mode']];feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=f==2)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=p,formal_mode=s['mode'],actual_tag_geometry=s['geometry'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')
def validate_combo_release(*a,**kw):raise ValueError('no conditional new budget or modes')
