"""Pure exact12 SYSTEM850 contract; original geometry/queue math is byte-preserved."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
SYSTEM_REQUEST_ID='EP_L2_SYSTEM_850MHZ_PARAMETER_FAMILY_V2_20261104_V1'
SERVICE_REQUEST_ID=SYSTEM_REQUEST_ID
SERVICE_DATA_ROOT=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_system850_v2_20261104_v1/system')
MODES={'S':(1,0,0,0,0,'S'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R')}
VARIABLE={'-trace','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
FAMILY_SCOPE_SHA='8b2adf18c38eaf140c3d61e11829d3ff0266428cff77ed657e1f7b0ee3548535'
REF_SHA='65474df0a47f5e16ce0314004b160cbd0a8da4d83473a1f3351e4bf5cc574062'
GEOMETRY_SHA='a9d11c3f1e04ceb26849a8f083e2725ef0a4aa648916776d2d6ee353752000b9'
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
def rmatch(a,b):return isinstance(a,dict)and isinstance(b,dict)and(a.get('path'),a.get('sha256'))==(b.get('path'),b.get('sha256'))
def reference():need(sha(ROOT/'REF_282_S.json')==REF_SHA,'S282 reference drift');return read(ROOT/'REF_282_S.json')
def geometry_module():
 p=ROOT/'deps/geometry_queue/geometry_queue_terminal.py';need(sha(p)==GEOMETRY_SHA,'frozen geometry math entry drift')
 sp=importlib.util.spec_from_file_location('system850_original_geometry_queue',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.verify_pins();return m
def family_scope():
 need(sha(ROOT/'FAMILY_SCOPE.json')==FAMILY_SCOPE_SHA,'SYSTEM850 exact scope drift');q=read(ROOT/'FAMILY_SCOPE.json');need(q['request_id']==SYSTEM_REQUEST_ID,'request scope mismatch');return q
def family_row(s):
 found=[r for r in family_scope()['points']if r['id']==s.get('cohort')];need(len(found)==1,'outside exact12 SYSTEM850 cells');r=found[0];need(s.get('system_family_point_id')==r['id'],'point binding mismatch');return r
def service_profile(r):return 'PFV2_SYSTEM850_'+r['family']
def flags(mode):
 need(mode in MODES,'unknown SYSTEM850 S/WV mode');ft,c,d,t,m,_=MODES[mode]
 return dict(zip(['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'],map(str,[ft,c,d,t,m])))
def ro_enabled(mode):need(mode in MODES,'mode');return False
def expected_peer(s):
 r=family_row(s);p=[x for x in family_scope()['points']if x['family']==r['family']and x['input_identity_sha256']==r['input_identity_sha256']and x['mode']!=r['mode']];need(len(p)==1,'exact reciprocal S/WV peer missing');return p[0]['id']
def baseline_row(s,mode):
 r=family_row(s);return next(x for x in family_scope()['points']if x['input_identity_sha256']==r['input_identity_sha256']and x['mode']==mode)
def check_background(s):
 r=family_row(s);base=exact(r['old_REF850_spec_ref']);o=s['expected_effective_options']
 need(s['source_identity']==base['source_identity']==family_scope()['source_identity']==reference()['source_identity'],'unknown Source5')
 need(s['mode']==r['mode']and s['mode']in MODES,'mode not exact cell');need(s['geometry']==r['geometry'],'new geometry not exactcell')
 need(s['profile']==service_profile(r),'SYSTEM850 profile mismatch');need(type(s.get('M'))is bool and type(s.get('T'))is bool and not s['M']and not s['T'],'typedROswitches')
 need(s.get('science_request_id')==SYSTEM_REQUEST_ID and s.get('system_family_proposal_ref')==family_scope()['proposal_ref'],'new scope/request contract')
 need(rmatch(s.get('absolute_REF850_spec_ref'),r['old_REF850_spec_ref']),'old same-mode absolute reference mismatch')
 need(s.get('same_background_peer_cohort')==expected_peer(s),'wrong reciprocal pair')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env']:
  need(s.get(k)==base.get(k),'input/observer binding drift:'+k)
 need(s.get('ro_qualification_ref')is None,'ROdisabled no inherited oracle authority')
 need(len(o)==282 and o==exact(r['option_preview_ref']),'exact282 preview drift')
 expected=dict(base['expected_effective_options'])
 for k,v in r['option_delta'].items():need(expected[k]==v['before'],'base delta before drift');expected[k]=v['after']
 need(o==expected and all(o[k]==v for k,v in flags(s['mode']).items()),'undeclared hardware/mode difference')
 need(o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and o['-dram_latency']=='100','850/L100 fixed')
 need(all(o[k]=='1'for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats']),'stats111 required')
 need(s['ordered_configs'][:-1]==base['ordered_configs'],'original ordered config prefix changed')
 overlay=s['ordered_configs'][-1];need(rmatch(overlay,s.get('system_final_overlay_ref')),'final overlay ref mismatch')
 need(P(overlay['path']).is_relative_to(ROOT/'configs'/s['cohort']),'overlay outside exact runtime cohort')
 need(P(overlay['path']).read_bytes()==P(r['final_overlay_ref']['path']).read_bytes(),'final overlay bytes drift')
 for q in s['ordered_configs']:need(sha(q['path'])==q['sha256'],'ordered config changed')
 geometry_module().qualify_history_spec(s)
 return o
def validate_anchor(s,mode='S'):
 field='absolute_REF850_S_anchor_qualification_ref'if mode=='S'else'absolute_REF850_EP_anchor_qualification_ref';q=exact(s[field])
 need(q.get('approved_by')=='EP-MAIN'and q.get('current_closed_state')=='CLOSED_ACCEPTED'and q.get('currently_accepted_population')is True,'Main closed absolute850 reference review required')
 if mode=='S':need(q.get('schema')=='EP_MAIN_EXACT_EXISTING_S_REFERENCE_QUALIFICATION_V1'and q.get('status')=='EXACT_EXISTING_S_HARDWARE_INPUT_OBSERVERS_QUALIFIED_FOR_MATCHED_REFERENCE','S absolute review schema/status')
 else:need(q.get('schema')=='EP_MAIN_EXACT_EXISTING_MODE_REFERENCE_QUALIFICATION_V1'and q.get('status')=='EXACT_EXISTING_HARDWARE_INPUT_OBSERVERS_REFERENCE_REUSE_QUALIFIED','EP absolute review schema/status')
 base_row=baseline_row(s,mode);a=exact(q['spec_ref']);p=exact(q['point_ref'])
 need(rmatch(q['spec_ref'],base_row['old_REF850_spec_ref'])and rmatch(p['spec_ref'],q['spec_ref']),'absolute reference is not exact accepted REF spec')
 need(a['mode']==p['mode']==mode and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and p['hardware_drained']is True,'accepted reference mode/drain')
 need(a['source_identity']==p['source_identity']==s['source_identity']==q['source_identity'],'absolute Source')
 need(a['input_identity_sha256']==p['input_identity_sha256']==s['input_identity_sha256']==q['input_identity_sha256'],'absolute input')
 need(a['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128)and a['observer_env']==s['observer_env'],'absolute reference must remain default32x8, not relabelled newgeometry')
 need(q['expected_effective_options_sha256']==digest_value(a['expected_effective_options']),'absolute282SHA')
 need(a['expected_effective_options']['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and a['expected_effective_options']['-gpgpu_frfcfs_dram_sched_queue_size']=='128','850/defaultscheduler anchor')
 need(s.get('REF850_usage')=='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S','old REF is not matched newhardware S')
 return q
def validate_fair_pair(a,b):
 check_background(a);check_background(b);need(a['same_background_peer_cohort']==b['cohort']and b['same_background_peer_cohort']==a['cohort'],'reciprocal pair')
 need(a['source_identity']==b['source_identity']and a['input_identity_sha256']==b['input_identity_sha256'],'Source/input peer')
 need({a['mode'],b['mode']}=={'S','WV_ZERO_RO'},'fair S/WV only')
 ignored=set(flags('S'))|VARIABLE-{'-trace'}
 need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'samehardware pair drift')
 return dict(status='EXACT_SAME_BACKGROUND_PAIR_ENGINEERING_PASS',science_permission=False)
def validate_ro(s):need(s.get('ro_qualification_ref')is None,'RO certificate forbidden');return dict(applicability='NOT_APPLICABLE_RO_RUNTIME_DISABLED_NOT_ZERO_INPUT_ORACLE')
def validate_mode_cpu(s):
 q=exact(s['mode_cpu_qualification_ref']);need(q.get('schema')=='EP_MAIN_SOURCE78_SYSTEM850_FORMAL_MODE_CPU_QUALIFICATION_V1'and q.get('status')=='MAIN_REVIEWED_SOURCE78_SYSTEM850_CPU_PASS_NOT_APPLICATION'and q.get('approved_by')=='EP-MAIN','Main SYSTEM850 modeCPU required')
 need(q['source_identity']==s['source_identity']and s['mode']in q['modes_qualified']and s['profile']in q['profiles_qualified'],'CPU Source/mode/profile')
 need(q.get('application_permission')is False and q.get('B0_M0a_application_NI')=='NOT_PROVEN'and q.get('new_profile_application_NI')=='NOT_MEASURED','CPU NI claim boundary')
 for r in q['evidence_refs'].values():exact(r)
 protocol=exact(q['evidence_refs']['protocol']);ni=exact(q['evidence_refs']['MS_domainNI']);echo=exact(q['evidence_refs']['actual282'])
 need(protocol.get('status')=='PASS_BOUNDED_CONSTRUCTOR_PROTOCOL_NOT_APPLICATION'and protocol.get('core')==s['source_identity']['core_source_commit']and protocol.get('archive_sha256')==s['source_identity']['archive_sha256'],'actual protocol proof not sameSourcePASS')
 need(all(z.get('exit_code')==0 for z in protocol['runs']),'incomplete production CPU controls')
 need(ni.get('status')=='PASS_6_MODE_PROFILE_CPU_PAIRS_NOT_APPLICATION_NI'and ni.get('B0_M0a_application_NI')=='NOT_PROVEN_ALL_HELD_ON','actual CPU NI scope/status')
 needed=family_row(s)['family'];need(any(z['family']==needed and z['mode']==s['mode']and z.get('PASS')is True for z in ni['pairs']),'missing exactmode/profile CPU NI pair')
 need(echo.get('status')=='PASS_ALL12_CORE_PLUS_TRACE_OPTION_ECHO'and echo['source_identity']==s['source_identity']and any(z['id']==s['cohort']and z.get('exact282_PASS')is True for z in echo['runs']),'actual CPU282 exactcell absent')
 return dict(status=q['status'],qualification_ref=s['mode_cpu_qualification_ref'],application_NI='NOT_MEASURED')
def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q.get('schema')=='EP_MAIN_SOURCE78_SYSTEM850_FAMILY_HOST_QUALIFICATION_V1'and q.get('status')=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED','new SYSTEM850 HostQ required')
 need(q['source_identity']==s['source_identity']and s['mode']in q['modes_qualified']and s['profile']in q['profiles_qualified'],'Host Source/mode/profile')
 for r in q['modules']:need(sha(r['path'])==r['sha256'],'HostQ module drift')
 need(all(r in q['modules']for r in [s['host_engine_ref'],s['validation_module_ref'],s['mode_contract_ref']]),'HostQ missing runtime')
 return q
def validate_static(s):
 need(s['goal']==GOAL,'frontend namespace');check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'contractselfidentity')
 a=validate_anchor(s);b=validate_anchor(s,'WV_ZERO_RO');cpu=validate_mode_cpu(s);validate_hostq(s)
 return dict(schema='EP_SYSTEM850_FORMAL_MODE_BINDING_V1',mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=False,M=False,RO=validate_ro(s),modeCPU=cpu,geometry_queue_math_binding=geometry_module().qualify_history_spec(s),same_background_peer_cohort=s['same_background_peer_cohort'],REF850_usage='ABSOLUTE_ONLY_NOT_MATCHED_NEW_HARDWARE',scientific_acceptance_granted=False,launch_permission=False)
def history_for(s):
 check_background(s);ft,v,d,t,m,p=MODES[s['mode']];feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=ft==2)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=p,formal_mode=s['mode'],actual_tag_geometry=s['geometry'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')

def validate_combo_release(s,registry,release_path,data_root=SERVICE_DATA_ROOT):
 r=family_row(s)
 if r['stage']!='CONDITIONAL_COMBINATION':return dict(status='PRIMARY_SINGLE_FAMILY_NO_RELEASE_NEEDED')
 release=read(release_path)
 need(release.get('status')=='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL'and release.get('cohort')==s['cohort']and release.get('request_id')==SYSTEM_REQUEST_ID,'combination not Main released')
 specfile=SERVICE_DATA_ROOT/'cases'/s['cohort']/'control/FROZEN_SPEC.json'
 # RegisteredSHA is canonical; CPU sandbox may relocate actual specfile only.
 q=registry['registered_future_requests'][SYSTEM_REQUEST_ID]
 need(release.get('spec_sha256')==q['admitted_specs'][s['cohort']],'conditional exact specSHA')
 review=exact(release.get('criterion_review_ref'))
 need(review.get('schema')=='EP_MAIN_SYSTEM850_ABSOLUTE_EP_COMBINATION_GATE_REVIEW_V1'and review.get('status')=='MAIN_REVIEWED_SYSTEM850_ABSOLUTE_EP_GATE_PASS'and review.get('request_id')==SYSTEM_REQUEST_ID,'Main exact absoluteEP review required')
 need(review.get('input_identity_sha256')==s['input_identity_sha256']and review.get('source_identity')==s['source_identity'],'gate Source/input')
 anchor=validate_anchor(s,'WV_ZERO_RO');refpoint=exact(anchor['point_ref'])
 need(rmatch(review.get('reference_EP_point_ref'),anchor['point_ref']),'gate baselineEP reference')
 cycles=[]
 for family in ['G64W16','FRFCFS256']:
  points=[z for z in family_scope()['points']if z['family']==family and z['input_identity_sha256']==s['input_identity_sha256']]
  need(len(points)==2,'gate single-family pair absent')
  for cell in points:
   row=q['consumed'].get(cell['id'],{})
   need(row.get('state')=='CLOSED_ACCEPTED','gate bothS_WV single-family arms notclosed')
   pt=exact(row['accepted_point_ref']);ar=exact(row['archive_receipt_ref'])
   need(pt.get('cohort')==cell['id']and pt['spec_ref']['sha256']==q['admitted_specs'][cell['id']]and pt['spec_ref']['path']==str(data_root/'cases'/cell['id']/'control/FROZEN_SPEC.json'),'gate exact official spec population')
   need(pt.get('uuid')==row.get('uuid')==ar.get('uuid'),'gate UUID population')
   need(pt.get('status')=='EP_FULL_PERF_APPLICATION_ACCEPTED'and pt.get('hardware_drained')is True and pt['source_identity']==s['source_identity']and pt['input_identity_sha256']==s['input_identity_sha256']and pt['mode']==cell['mode'],'gate acceptedpoint identity')
   need(ar.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and ar['cohort']==cell['id'],'gate mandatoryarchive')
   need(ar.get('source_keep')is True and '/mnt164/'in ar['archive_ref']['path'],'gate true164 SourceKEEP')
   rr=ar.get('native_restores',[]);need(len(rr)==2 and all(x.get('status')=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'for x in rr)and len({x['target']for x in rr})==2 and all(x['archive_sha256']==ar['archive_ref']['sha256']for x in rr),'gate twoindependentrestores')
   need(pt['instructions']==s['expected_instructions']and pt['CTA']==s['expected_CTA'],'gate fullinput population')
   if cell['mode']=='WV_ZERO_RO':
    need(rmatch(review.get(family+'_EP_point_ref'),row['accepted_point_ref']),'gate review point population');cycles.append(pt['cycles'])
 n=refpoint['cycles'];g,f=cycles;need(all(type(v)is int and v>0 for v in [n,g,f]),'gate completedcycle types')
 passed=((100*(n-g)>=n and 100*(n-f)>=n)or(100*(n-g)>=3*n and n-f>=0)or(100*(n-f)>=3*n and n-g>=0))
 need(passed,'EP_ABSOLUTE_CRITERION_NOT_MET_RATIO_OR_S_SLOWDOWN_CANNOT_RELEASE')
 return dict(status='ABSOLUTE_EP_COMBINATION_CRITERION_PASS',reference_EP_cycles=n,geometry_EP_cycles=g,scheduler_EP_cycles=f,S_ratio_not_used=True)
