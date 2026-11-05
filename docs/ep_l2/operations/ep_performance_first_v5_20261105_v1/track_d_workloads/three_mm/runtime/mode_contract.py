# Exact eight mid-Tag engineering contract. No actors, imports never consume.
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
SYSTEM_REQUEST_ID='EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1';SERVICE_REQUEST_ID=SYSTEM_REQUEST_ID
MODES={'S':(1,0,0,0,0,'S'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R')}
FAMILY_SCOPE_SHA='ba830e36005a66dd0116408e2ab3ec6d04377c8d125f27169ba2b044c233f241'
GEOMETRY_SHA='c4faa55d51b59375b8c0d71bef65ef27b1b014b71f2de484b261c725bef8477e'
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):
 def pairs(xs):
  d={}
  for k,v in xs:need(k not in d,'duplicate JSON field');d[k]=v
  return d
 return json.loads(P(p).read_bytes(),object_pairs_hook=pairs,parse_constant=lambda v:need(False,'nonfinite JSON'))
def exact(r):need(isinstance(r,dict)and sha(r['path'])==r['sha256'],'missing/changed immutable reference');return read(r['path'])
def rmatch(a,b):return isinstance(a,dict)and isinstance(b,dict)and(a.get('path'),a.get('sha256'))==(b.get('path'),b.get('sha256'))
def digest_value(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def family_scope():need(sha(ROOT/'FAMILY_SCOPE.json')==FAMILY_SCOPE_SHA,'scope drift');q=read(ROOT/'FAMILY_SCOPE.json');need(q['request_id']==SYSTEM_REQUEST_ID,'scope request');return q
def family_row(s):
 rows=[r for r in family_scope()['points']if r['id']==s.get('cohort')];need(len(rows)==1,'outside exact independent request2 cells');return rows[0]
def flags(mode):
 need(mode in MODES,'unknown formal S/WV mode');f,c,d,t,m,_=MODES[mode];return dict(zip(['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'],map(str,[f,c,d,t,m])))
def ro_enabled(mode):need(mode in MODES,'mode');return False
def expected_peer(s):return family_row(s)['peer_cohort']
def geometry_module():
 p=ROOT/'deps/geometry_queue/geometry_queue_terminal.py';need(sha(p)==GEOMETRY_SHA,'frozen geometry math');z=importlib.util.spec_from_file_location('midtag_geometry',p);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);m.verify_pins();return m
def check_background(s):
 r=family_row(s);base=exact(r['old_REF850_spec_ref']);o=s['expected_effective_options'];g=r['geometry']
 need(s['science_request_id']==SYSTEM_REQUEST_ID and s['source_identity']==base['source_identity']==family_scope()['source_identity'],'request/Source5')
 need(s['mode']==r['mode']and s['geometry']==g and g['sets']in[32,64]and g['ways']==8 and g['slices']==64 and g['line_bytes']==128,'exact mode/geometry')
 need(type(s['M'])is bool and type(s['T'])is bool and not s['M']and not s['T']and s.get('ro_qualification_ref')is None,'RO disabled typed booleans')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','observer_env']:need(s.get(k)==base.get(k),'input/observer drift:'+k)
 expected=dict(base['expected_effective_options']);expected.update(flags(s['mode']));expected['-gpgpu_cache:dl2']='S:'+str(g['sets'])+':128:8,L:B:m:L:P,A:128:1,128:0,32'
 need(len(o)==282 and o==expected and o==exact(r['option_preview_ref']),'undeclared option drift or incomplete282')
 need(o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and o['-dram_latency']=='100'and o['-gpgpu_frfcfs_dram_sched_queue_size']=='128','850/L100/FR128')
 need(all(o[k]=='1'for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats']),'observer111')
 need(s['same_background_peer_cohort']==expected_peer(s),'peer')
 need([q['sha256']for q in s['ordered_configs'][:-1]]==[q['sha256']for q in base['ordered_configs']],'accepted ordered config prefix bytes')
 for q in s['ordered_configs']:need(sha(q['path'])==q['sha256'],'config bytes')
 geometry_module().qualify_history_spec(s);return o
def validate_fair_pair(a,b):
 check_background(a)
 anchor=family_row(a)['family']=='REF32W8_ANCHOR'
 if anchor:
  r=family_row(a);need(b==exact(r['peer_accepted_spec_ref'])and b['mode']=='S','exact reused S REF peer')
 else:
  check_background(b);need(a['same_background_peer_cohort']==b['cohort']and b['same_background_peer_cohort']==a['cohort'],'reciprocal pair')
 ignored=set(flags('S'));need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'unfair hardware/input pair')
 return dict(status='EXACT_MATCHED_S_WV_ENGINEERING_PAIR_OR_REF_ANCHOR_PASS',science_permission=False)
def validate_anchor(s,mode='S'):
 r=family_scope()['points'][0]['old_REF850_spec_ref'];a=exact(r)
 if mode=='WV_ZERO_RO':return dict(status='UNKNOWN_NO_ACCEPTED_3MM_WV_REF_NEW_ANCHOR_REQUESTED_NOT_YET_RUN',cycles=None,F_substitution=False)
 pointref=next(p['accepted_same_mode_ref']for p in family_scope()['points']if p['mode']=='S');p=exact(pointref['accepted_point_ref'])
 need(a['mode']==p['mode']=='S'and p['hardware_drained']and a['source_identity']==p['source_identity']==s['source_identity']and a['input_identity_sha256']==s['input_identity_sha256'],'accepted S REF identity')
 return dict(status='EXACT_ACCEPTED_S_REF_ONLY',point_ref=pointref['accepted_point_ref'],cycles=pointref['cycles'])
def validate_mode_cpu(s):
 q=exact(s['mode_cpu_qualification_ref']);need(q['Source5']==s['source_identity'],'CPU Source5')
 r=next(p for p in q['points']if p['cohort']==s['cohort']);prev=exact(r['basis_ref'])
 if r['kind'].startswith('EXACT_SOURCE78_ACCEPTED'):prev=prev['expected_effective_options']
 need(len(prev)==282 and {k:v for k,v in prev.items()if k!='-trace'}=={k:v for k,v in s['expected_effective_options'].items()if k!='-trace'},'281 hardware/mode background mismatch')
 wv=exact(q['source78_WV_CPU_ref']);need(wv['source_identity']==s['source_identity']and wv['actual_production_objects']['RO_runtime_absent'],'prior production WV no-RO CPU proof')
 need(s['expected_effective_options']['-trace']==exact(s['input_binding_ref'])['trace_entry'],'exact new trace binding')
 return dict(status='EXACT_SOURCE78_MODE_GEOMETRY_BACKGROUND_REBOUND_NO_RETEST',application_NI='NOT_MEASURED',new_application_NI_is_launch_gate=False)
def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q['source_identity']==s['source_identity']and q['status']=='PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE','Host engineering rebind')
 for r in q['modules']:need(sha(r['path'])==r['sha256'],'Host module drift')
 need(all(any(rmatch(x,r)for x in q['modules'])for r in[s['host_engine_ref'],s['validation_module_ref'],s['mode_contract_ref']]),'Host scope incomplete');return q
def validate_static(s):
 need(s['goal']==GOAL,'namespace');check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'modecontract pin')
 validate_anchor(s);validate_anchor(s,'WV_ZERO_RO');cpu=validate_mode_cpu(s);validate_hostq(s)
 return dict(mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=False,M=False,RO={'applicability':'NOT_APPLICABLE_RO_RUNTIME_DISABLED'},modeCPU=cpu,scientific_acceptance_granted=False,launch_permission=False)
def history_for(s):
 check_background(s);f,v,d,t,m,p=MODES[s['mode']];feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=f==2)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=p,formal_mode=s['mode'],actual_tag_geometry=s['geometry'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')
def validate_combo_release(*args,**kwargs):raise ValueError('midTag family has no conditional combination arm')
