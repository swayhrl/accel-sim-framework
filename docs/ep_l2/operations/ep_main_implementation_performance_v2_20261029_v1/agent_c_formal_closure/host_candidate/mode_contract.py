"""Exact new Source three-arm16x8 Host contract. No launch or authority mutation."""
import pathlib,json,hashlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
REQUEST='EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1'
MODES={'F_MINUS_T':(2,1,1,0,1,'WV_M'),'LEGACY_F':(2,1,1,1,1,'F'),'CORRECTED_F':(2,1,1,1,1,'F')}
CORRECTION='-gpgpu_ep_l2_ordinary_ro_tag_relief'
HEAVY=('EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE')
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
 return json.loads(P(p).read_bytes(),object_pairs_hook=pairs,parse_constant=lambda x:need(False,'nonfinite'))
def exact(r):need(isinstance(r,dict)and sha(r['path'])==r['sha256'],'missing/changed immutable reference');return read(r['path'])
def digest_value(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def reference():return read(ROOT/'NEW_SOURCE_REFERENCE.json')
def flags(mode):
 need(mode in MODES,'unknown three-arm mode');ft,c,d,t,m,_=MODES[mode]
 return {'-gpgpu_ep_l2_ft_mode':str(ft),'-gpgpu_ep_l2_tvd_clean':str(c),'-gpgpu_ep_l2_tvd_dirty':str(d),'-gpgpu_ep_l2_ro_tag_detach':str(t),'-gpgpu_ep_l2_ro_line_mshr_bypass':str(m),CORRECTION:str(int(mode=='CORRECTED_F'))}
def ro_enabled(mode):need(mode in MODES,'unknown mode');return True
def check_background(s):
 r=reference();p=read(ROOT/'LEGACY_PARENT_BACKGROUND.json');o=s['expected_effective_options'];need(s['source_identity']==r['source_identity'],'exact new Source5 only; no Source78 projection');need(s['geometry']==p['geometry']==dict(slices=64,sets=16,ways=8,line_bytes=128),'exact16x8 only;32x8 HostQ not inherited');need(s['profile']=='G16_W8','exactG16W8 physical profile')
 need(type(s.get('T'))is bool and type(s.get('M'))is bool and s['M']is True and s['T']is(s['mode']!='F_MINUS_T'),'formal typedT/M differs');need(s['mode']in MODES,'unknown mode');need(type(s.get('ordinary_ro_tag_relief'))is bool and s['ordinary_ro_tag_relief']is(s['mode']=='CORRECTED_F'),'formal typed correction differs')
 need(type(o)is dict and len(o)==283 and all(type(k)is str and type(v)is str for k,v in o.items()),'actual283 strings');base=p['expected_effective_options'];need(set(o)==set(base)|{CORRECTION},'exact old282 plus correction key')
 for k,v in base.items():
  if k not in flags(s['mode']):need(o[k]==v,'undeclaredbackground/input/geometry/clock/queue/resource/stat:'+k)
 need(o['-trace']==s['trace_entry']==p['trace_entry']and s['input_identity_sha256']==p['input_identity_sha256'],'exact Conv input binding');need(all(o[k]==v for k,v in flags(s['mode']).items()),'formal sixflag mismatch');profile=s.get('observer_profile');need(profile in ['T3_PRIMARY_OFF','T3_DIAG_ON'],'explicit T3observerprofile');expected={k:'0'for k in HEAVY};expected['EPL2_LIFE_WIRE']='SUMMARY_STAGE'
 if profile=='T3_DIAG_ON':expected.update(EPL2_DETACH_DIAG='1',EPL2_TAGPRESSURE_DIAG='1')
 need(s['observer_env']==expected,'exact fourheavyOFF or declared TPDIAGON+SUMMARY_STAGE scope')
 need(s.get('old_application_acceptance_inherited')is False,'newELF may not inherit appacceptance');return o

def validate_source(s):
 q=exact(s['source_qualification_ref']);need(q.get('schema')=='EP_MAIN_NEW_SOURCE_T3_CPU_QUALIFICATION_V1'and q.get('status')=='MAIN_REVIEWED_NEW_SOURCE_CPU_AND_WHOLE_TU_QUALIFIED_NOT_APP_ACCEPTED'and q.get('approved_by')=='EP-MAIN','Main actualnewSource CPU/TU review required');need(q['source_identity']==s['source_identity']and q.get('geometry')==s['geometry']and q.get('modes_qualified')==sorted(MODES),'newSource scope');need(q.get('application_acceptance_inherited')is False,'CPU not applicationpermission');need(q.get('evidence_refs'),'source actualevidence missing')
 for r in q['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'newSource evidence drift')
 return q

def validate_ro(s):
 q=exact(s['ro_qualification_ref']);need(q.get('status')=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED'and q.get('qualified_by')=='Main','newSource Main ROloader qualification');need(q['source_identity']==s['source_identity']and q['input_identity_sha256']==s['input_identity_sha256'],'ROSource/input mismatch');need(q.get('epoch')=='whole_commandlist'and q.get('line_bytes')==128 and q.get('address_domain')=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','ROscope');need(q.get('new_source_loader_audit_ref'),'newSource loader/addresspath audit required');exact(q['new_source_loader_audit_ref'])
 for kind in ['manifest','ranges']:
  r=q[kind+'_ref'];need(sha(r['path'])==r['sha256'],'ROartifactdrift');need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind]==r['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind+'_sha256']==r['sha256'],'ROactualoptionbinding')
 return dict(applicability='ENABLED_EXACT_CERTIFICATE_REQUIRED_ALL_THREE',qualification_ref=s['ro_qualification_ref'])
def validate_mode_cpu(s):
 q=exact(s['mode_cpu_qualification_ref']);need(q.get('schema')=='EP_MAIN_NEW_SOURCE_T3_FORMAL_MODE_CPU_QUALIFICATION_V1'and q.get('status')=='MAIN_REVIEWED_NEW_SOURCE_16X8_THREE_ARM_CPU_PASS_NOT_APPLICATION'and q.get('approved_by')=='EP-MAIN','new16x8modeCPU required');need(q['source_identity']==s['source_identity']and q['geometry']==s['geometry']and q['modes_qualified']==sorted(MODES),'modeCPU exactSource/geometry/modes');need(q.get('application_permission')is False and q.get('evidence_refs'),'actualmodeCPU proof not apppermission')
 for r in q['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'modeCPU evidence drift')
 return dict(status=q['status'],qualification_ref=s['mode_cpu_qualification_ref'])
def validate_matrix(s):
 q=exact(s['three_arm_matrix_ref']);need(q.get('schema')=='EP_MAIN_EXACT_SAME_ELF_T3_BINDING_V1'and q.get('source_identity')==s['source_identity']and q.get('geometry')==s['geometry']and q.get('input_identity_sha256')==s['input_identity_sha256'],'matrixSource/input/geometry');need(q.get('science_request_id')==REQUEST and set(q['arms'])==set(MODES),'three unique arms/freshscope')
 p=read(ROOT/'LEGACY_PARENT_BACKGROUND.json');base=p['expected_effective_options']
 for mode,row in q['arms'].items():
  expected=dict(base);expected.update(flags(mode));need(row['effective_options_sha256']==digest_value(expected),'matrix arm optiondiff');need(row['source_identity']==s['source_identity']and row['observer_env']==s['observer_env'],'allarms sameELF/profile')
 need(q['arms'][s['mode']]['cohort']==s['cohort'],'matrix exactcohort')
def validate_hostq(s):
 q=exact(s['host_qualification_ref']);need(q.get('schema')=='EP_MAIN_NEW_SOURCE_T3_HOST_QUALIFICATION_V1'and q.get('status')=='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'and q.get('approved_by')=='EP-MAIN','new16x8 actualHostQ required');need(q['source_identity']==s['source_identity']and q['geometry']==s['geometry']and q['modes_qualified']==sorted(MODES),'HostQ Source/16x8/all3mode');refs=q['modules']
 for r in refs:need(sha(r['path'])==r['sha256'],'HostQ module drift')
 need(s['observer_profile']in q.get('observer_profiles_qualified',[]),'HostQ observerprofile notqualified');need(all(s[k]in refs for k in ['host_engine_ref','host_common_ref','validation_module_ref','mode_contract_ref']),'HostQ engine/common/parser/contract missing');return q

def validate_static(s):
 need(s['goal']==GOAL and s.get('science_request_id')==REQUEST,'frontend namespace distinct fromfreshTrequest');check_background(s);need(s['mode_contract_ref']['sha256']==sha(__file__),'mode contract selfidentity');validate_source(s);ro=validate_ro(s);cpu=validate_mode_cpu(s);validate_matrix(s);validate_hostq(s)
 return dict(schema='EP_NEW_SOURCE_T3_16X8_FORMAL_BINDING_V1',mode=s['mode'],numeric_profile=MODES[s['mode']][5],T=s['T'],M=s['M'],ordinary_ro_tag_relief=s['ordinary_ro_tag_relief'],RO=ro,modeCPU=cpu,scientific_acceptance_granted=False,launch_permission=False)
def history_for(s):
 check_background(s);ft,v,dirty,t,m,profile=MODES[s['mode']];feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=True)
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=profile,formal_mode=s['mode'],profile_semantics={'effective_options':s['expected_effective_options'],'research_switches':{'V':v,'T':t,'M':m}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')
