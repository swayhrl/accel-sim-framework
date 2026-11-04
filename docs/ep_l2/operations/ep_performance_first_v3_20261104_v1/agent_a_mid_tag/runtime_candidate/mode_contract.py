# Exact eight mid-Tag engineering contract. No actors, imports never consume.
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
SYSTEM_REQUEST_ID='EP_L2_MID_TAG_850MHZ_V1_20261104';SERVICE_REQUEST_ID=SYSTEM_REQUEST_ID
MODES={'S':(1,0,0,0,0,'S'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R')}
FAMILY_SCOPE_SHA='ef03c2cb2789a901ec5390a9c42d4434ec97773bc6f0115e8262e86643b8c41c'
GEOMETRY_SHA='a9d11c3f1e04ceb26849a8f083e2725ef0a4aa648916776d2d6ee353752000b9'
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
 rows=[r for r in family_scope()['points']if r['id']==s.get('cohort')];need(len(rows)==1,'outside exact eight midTag cells');return rows[0]
def flags(mode):
 need(mode in MODES,'unknown formal S/WV mode');f,c,d,t,m,_=MODES[mode];return dict(zip(['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'],map(str,[f,c,d,t,m])))
def ro_enabled(mode):need(mode in MODES,'mode');return False
def expected_peer(s):
 r=family_row(s);q=[p['id']for p in family_scope()['points']if p['family']==r['family']and p['input_identity_sha256']==r['input_identity_sha256']and p['mode']!=r['mode']];need(len(q)==1,'peer population');return q[0]
def geometry_module():
 p=ROOT/'deps/geometry_queue/geometry_queue_terminal.py';need(sha(p)==GEOMETRY_SHA,'frozen geometry math');z=importlib.util.spec_from_file_location('midtag_geometry',p);m=importlib.util.module_from_spec(z);z.loader.exec_module(m);m.verify_pins();return m
def check_background(s):
 r=family_row(s);base=exact(r['old_REF850_spec_ref']);o=s['expected_effective_options'];g=r['geometry']
 need(s['science_request_id']==SYSTEM_REQUEST_ID and s['source_identity']==base['source_identity']==family_scope()['source_identity'],'request/Source5')
 need(s['mode']==r['mode']and s['geometry']==g and (g['sets'],g['ways'])in[(32,16),(64,8)]and g['slices']==64 and g['line_bytes']==128,'exact mode/geometry')
 need(s['profile']=='PFV3_MIDTAG_'+r['family'],'profile')
 need(type(s['M'])is bool and type(s['T'])is bool and not s['M']and not s['T']and s.get('ro_qualification_ref')is None,'RO disabled typed booleans')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env']:
  need(s.get(k)==base.get(k),'input/observer drift:'+k)
 expected=dict(base['expected_effective_options']);expected['-gpgpu_cache:dl2']='S:'+str(g['sets'])+':128:'+str(g['ways'])+',L:B:m:L:P,A:128:1,128:0,32'
 need(len(o)==282 and o==expected and o==exact(r['option_preview_ref']),'undeclared option drift or incomplete282')
 need(all(o[k]==v for k,v in flags(s['mode']).items()),'mode flags')
 need(o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and o['-dram_latency']=='100'and o['-gpgpu_frfcfs_dram_sched_queue_size']=='128','850/L100/FR128')
 need(all(o[k]=='1'for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats']),'observer111')
 need(s['same_background_peer_cohort']==expected_peer(s),'peer')
 need(s['ordered_configs'][:-1]==base['ordered_configs'],'ordered config prefix')
 for q in s['ordered_configs']:need(sha(q['path'])==q['sha256'],'config bytes')
 need(rmatch(s['absolute_REF850_spec_ref'],r['old_REF850_spec_ref']),'absolute REF origin')
 geometry_module().qualify_history_spec(s)
 return o
def validate_fair_pair(a,b):
 check_background(a);check_background(b);need(a['same_background_peer_cohort']==b['cohort']and b['same_background_peer_cohort']==a['cohort'],'reciprocal pair')
 ignored=set(flags('S'));need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'unfair hardware/input pair')
 return dict(status='EXACT_MATCHED_S_WV_CPU_ENGINEERING_PASS',science_permission=False)
def validate_anchor(s,mode='S'):
 k='absolute_REF850_S_anchor_qualification_ref'if mode=='S'else'absolute_REF850_EP_anchor_qualification_ref';r=family_row(s);need(rmatch(s[k],r[k]),'anchor binding');q=exact(s[k]);p=exact(q['point_ref']);a=exact(q['spec_ref'])
 need(q.get('approved_by')=='EP-MAIN'and q['current_closed_state']=='CLOSED_ACCEPTED'and q['currently_accepted_population']is True,'accepted REF evidence')
 need(a['mode']==p['mode']==mode and p['hardware_drained']and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED','accepted REF population')
 need(a['source_identity']==p['source_identity']==s['source_identity']and a['input_identity_sha256']==s['input_identity_sha256'],'anchor identity')
 need(a['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128)and a['observer_env']==s['observer_env'],'anchor geometry/observer')
 need(s['REF850_usage']=='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S','not newgeometry matched S')
 return q
def validate_mode_cpu(s):
 q=exact(s['mode_cpu_qualification_ref']);need(q['status']=='PASS_MIDTAG_CPU_ENGINEERING_NOT_APPLICATION'and q['source_identity']==s['source_identity'],'CPU qualification')
 ni=exact(q['protocol_ref']);echo=exact(q['actual282_ref']);g=s['geometry'];need(any(p['sets']==g['sets']and p['ways']==g['ways']and p['mode']==s['mode']and p['PASS']for p in ni['pairs']),'exactgeometry mode CPU NI absent')
 need(any(p['cohort']==s['cohort']and p['exact282_PASS']for p in echo['runs']),'exact282 absent')
 need(q['application_NI']=='NOT_MEASURED'and q['B0_M0a_application_NI']=='NOT_PROVEN_HELD_ON','NI claim')
 return dict(status=q['status'],application_NI='NOT_MEASURED')
def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q['status']=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'and q['source_identity']==s['source_identity'],'Host qualification')
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
