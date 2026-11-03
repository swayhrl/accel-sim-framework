"""Pure draft mode/history contract. No registry, actor or acceptance writes."""
import pathlib,json,hashlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent;GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1';EXTENSION_GOAL='EP_L2_WV_RO_T_PERFORMANCE_EXPLORATION_V1'
MODES={'S':(1,0,0,0,0,'S'),'F':(2,1,1,1,1,'F')}
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
REQUEST='EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'
SCOPE_SHA='08ce5e7c68e1e3d10ee533aaf1f2689ec5ab7660f49247d7ffb5c5d9b76d0e54'
SOURCE_REF_SHA='11098ceacfe7a00d0ac9048ffa26f848eed01b9012ba72b3e8ddf450165eb421'
def reference():
 need(sha(ROOT/'NEW_SOURCE_REFERENCE.json')==SOURCE_REF_SHA,'newSource reference drift');return read(ROOT/'NEW_SOURCE_REFERENCE.json')
def flags(mode):
 need(mode in MODES,'only exact S/F modes qualified');ft,v,d,t,m,_=MODES[mode]
 return {'-gpgpu_ep_l2_ft_mode':str(ft),'-gpgpu_ep_l2_tvd_clean':str(v),'-gpgpu_ep_l2_tvd_dirty':str(d),'-gpgpu_ep_l2_ro_tag_detach':str(t),'-gpgpu_ep_l2_ro_line_mshr_bypass':str(m)}
def ro_enabled(mode):need(mode in MODES,'unknown mode');return mode=='F'
def family_scope():
 need(sha(ROOT/'FAMILY_SCOPE.json')==SCOPE_SHA,'exact six-cell scope drift');return read(ROOT/'FAMILY_SCOPE.json')
def family_row(s):
 rows=[r for r in family_scope()['points']if r['cohort']==s.get('cohort')];need(len(rows)==1,'not exact six highclock cohorts');r=rows[0];need(s.get('service_family_point_id')==r['id'],'family point binding');return r
def expected_peer(s):
 r=family_row(s);p=[x for x in family_scope()['points']if x['DRAM_MHz']==r['DRAM_MHz']and x['mode']!=r['mode']];need(len(p)==1,'pair scope');return p[0]['cohort']
def check_background(s):
 r=family_row(s);base=exact(r['reference_spec_ref']);o=s['expected_effective_options'];need(s['source_identity']==reference()['source_identity']==r['source5'],'exact862/083a/5901 Source5 only')
 need(base['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04','config template lineage')
 need(s['geometry']==r['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'exact32x8 geometry')
 need(s['profile']=='CC_CAM_'+str(r['DRAM_MHz'])+'_G32W8_L100'and s['mode']==r['mode'],'exact mode/profile')
 need(type(s.get('M'))is bool and type(s.get('T'))is bool and(s['M'],s['T'])==((True,True)if s['mode']=='F'else(False,False)),'typed S/F switches')
 need(s.get('science_request_id')==REQUEST and s.get('service_family_proposal_ref')==family_scope()['proposal_ref'],'fresh request/family binding')
 need(s.get('configuration_template_spec_ref')==r['reference_spec_ref']and s.get('configuration_template_usage')=='OLD_SOURCE_CONFIG_INPUT_ONLY_NOT_ACCEPTANCE','template is not newSource acceptance')
 need(s.get('old_application_acceptance_inherited')is False,'no oldELF app inheritance')
 need(s.get('same_background_peer_cohort')==expected_peer(s),'exact reciprocal peer required')
 need(s.get('REF850_usage')=='NEW_SOURCE_BASELINE_PAIR_REQUIRES_OWN_ACCEPTANCE_FOR_HIGH_CLOCK','new850 baseline scope')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','program','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env']:
  need(s.get(k)==base.get(k),'newSource input/observer '+k)
 need(type(o)is dict and len(o)==282 and all(type(k)is str and type(v)is str for k,v in o.items())and o==exact(r['option_candidate_ref']),'exact282 family option values')
 expected=dict(base['expected_effective_options']);expected['-gpgpu_clock_domains']='1132.0:1132.0:1132.0:'+str(float(r['DRAM_MHz']));need(o==expected and all(o[k]==v for k,v in flags(s['mode']).items()),'only declared DRAM clock/mode changes')
 need(s['ordered_configs'][:-1]==base['ordered_configs']and len(s['ordered_configs'])==len(base['ordered_configs'])+1,'original ordered configs plus one last overlay')
 overlay=s['ordered_configs'][-1];need(overlay==s.get('service_frequency_overlay_ref')==r['frequency_overlay_ref'],'exact last overlay ref')
 for item in s['ordered_configs']:need(sha(item['path'])==item['sha256'],'ordered config drift')
 return o

def reviewed(s,field,schema,status):
 q=exact(s[field]);need(q.get('schema')==schema and q.get('status')==status and q.get('approved_by')=='EP-MAIN','newSource Main review required: '+field);need(q.get('source_identity')==s['source_identity'],'newSource qualification identity: '+field);need(q.get('evidence_refs'),'actual qualification evidence missing: '+field)
 for r in q['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'qualification evidence drift')
 return q

def validate_source(s):
 q=reviewed(s,'source_qualification_ref','EP_MAIN_NEW_SOURCE_CC_CAM_CPU_QUALIFICATION_V1','MAIN_REVIEWED_NEW_SOURCE_CPU_AND_WHOLE_TU_QUALIFIED_NOT_APP_ACCEPTED')
 need(q.get('application_acceptance_inherited')is False and q.get('geometry')==s['geometry']and q.get('modes_qualified')==sorted(MODES),'newCPU/build source scope')
 return q

def validate_mode_cpu(s):
 q=reviewed(s,'mode_cpu_qualification_ref','EP_MAIN_NEW_SOURCE_CC_CAM_S_F_MODE_CPU_QUALIFICATION_V1','MAIN_REVIEWED_NEW_SOURCE_S_F_CPU_PASS_NOT_APPLICATION')
 need(q.get('geometry')==s['geometry']and q.get('modes_qualified')==sorted(MODES)and q.get('application_permission')is False,'new S/F modeCPU scope')
 return dict(status=q['status'],qualification_ref=s['mode_cpu_qualification_ref'])

def validate_ro(s):
 if not ro_enabled(s['mode']):need(s.get('ro_qualification_ref')is None,'S may not inherit RO authority');return dict(applicability='NOT_APPLICABLE_RO_DISABLED_NOT_ZERO_ORACLE')
 q=exact(s['ro_qualification_ref']);need(q.get('status')=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED'and q.get('qualified_by')=='Main','newSource RO qualification required');need(q.get('source_identity')==s['source_identity']and q.get('input_identity_sha256')==s['input_identity_sha256'],'RO must be rebound to actual new Source and input')
 need(q.get('epoch')=='whole_commandlist'and q.get('line_bytes')==128 and q.get('address_domain')=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','RO scope')
 audit=exact(q.get('new_source_loader_audit_ref'));need(audit.get('status')=='MAIN_REVIEWED_NEW_SOURCE_VECTOR_RO_LOADER_BINDING_PASS'and audit.get('source_identity')==s['source_identity']and audit.get('input_identity_sha256')==s['input_identity_sha256'],'newSource actual loader/address audit required')
 need(audit.get('evidence_refs'),'loader proof missing')
 for r in audit['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'loader audit drift')
 for kind in ['manifest','ranges']:
  r=q[kind+'_ref'];need(sha(r['path'])==r['sha256'],'RO data identity drift');need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind]==r['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind+'_sha256']==r['sha256'],'RO content/282 mismatch')
 return dict(applicability='NEW_SOURCE_EXACT_VECTOR_RO_LOADER_REQUIRED',qualification_ref=s['ro_qualification_ref'])

def validate_hostq(s):
 q=reviewed(s,'host_qualification_ref','EP_MAIN_NEW_SOURCE_CC_CAM_HIGH_CLOCK_HOST_QUALIFICATION_V1','HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED')
 need(q.get('geometry')==s['geometry']and q.get('modes_qualified')==sorted(MODES)and q.get('cohorts_qualified')==sorted(r['cohort']for r in family_scope()['points']),'exact six HostQ scope')
 refs=q['modules']
 for r in refs:need(sha(r['path'])==r['sha256'],'Host module drift')
 need(all(s[k]in refs for k in ['host_engine_ref','host_common_ref','mode_contract_ref','validation_module_ref']),'Host module bindings absent');return q

def validate_static(s):
 need(s['goal']==GOAL and s.get('science_request_id')==REQUEST,'frontend/fresh scope namespace');check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'self identity');validate_source(s);cpu=validate_mode_cpu(s);ro=validate_ro(s);validate_hostq(s)
 return dict(schema='EP_NEW_SOURCE_CC_CAM_S_F_BINDING_V1',mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=s['T'],M=s['M'],RO=ro,modeCPU=cpu,source_qualification_ref=s['source_qualification_ref'],accepted_anchor_required_for_first850=False,same_background_peer_cohort=s['same_background_peer_cohort'],scientific_acceptance_granted=False,launch_permission=False)

def validate_fair_pair(a,b):
 check_background(a);check_background(b);need(a['same_background_peer_cohort']==b['cohort']and b['same_background_peer_cohort']==a['cohort']and {a['mode'],b['mode']}=={'S','F'},'new sameclock S/F pair')
 ignored=set(flags('F'))|VARIABLE-{'-trace'};need({k:v for k,v in a['expected_effective_options'].items()if k not in ignored}=={k:v for k,v in b['expected_effective_options'].items()if k not in ignored},'S/F hardware difference')
 return dict(status='EXACT_NEW_SOURCE_SAME_BACKGROUND_S_F_PAIR',Source=a['source_identity'],scientific_acceptance_granted=False)

def history_for(s):
 check_background(s);ft,v,d,t,m,profile=MODES[s['mode']];feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=ft==2)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=profile,formal_mode=s['mode'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')
