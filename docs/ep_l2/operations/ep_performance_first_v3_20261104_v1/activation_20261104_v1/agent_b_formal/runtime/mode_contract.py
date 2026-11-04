"""Exact Source862 W/WV engineering contract. No science approval or actors."""
import pathlib,json,hashlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent
MODES={'W_ONLY':(2,0,0,0,0,'W_ONLY'),'WV_ZERO_RO':(2,1,1,0,0,'F_MINUS_R')}
def need(ok,m):
 if not ok:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def exact(r):
 need(isinstance(r,dict) and sha(r['path'])==r['sha256'],'immutable reference drift')
 return read(r['path'])
def flags(mode):
 need(mode in MODES,'exact W/WV only');ft,c,d,t,m,_=MODES[mode]
 return dict(zip(['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'],map(str,[ft,c,d,t,m])))
def ro_enabled(mode):need(mode in MODES,'unknown mode');return False
def reference():
 need(sha(ROOT/'EXACT_NEW_SOURCE_S1700_REFERENCE.json')=='004800c87d26a10f4877cd21df8d7095e08826dda75c2d7c92a1f0f3b0aff0e5','reference drift');return read(ROOT/'EXACT_NEW_SOURCE_S1700_REFERENCE.json')
def check_background(s):
 b=reference();need(s['mode'] in MODES,'mode out of scope');need(s['source_identity']==b['source_identity'],'Source5 mismatch')
 need(s['geometry']==b['geometry'] and s['profile']==b['profile'],'exact1700 G32W8 L100')
 for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','program','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','command_count','observer_env']:
  need(s[k]==b[k],'input/observer drift '+k)
 o=dict(b['expected_effective_options']);o.update(flags(s['mode']))
 need(s['expected_effective_options']==o and len(o)==282,'exact282 mode-only changes')
 need(type(s['M'])is bool and type(s['T'])is bool and not s['M'] and not s['T'],'typedRO disabled')
 need(s['ro_qualification_ref'] is None,'disabled RO may not inherit certificate authority')
 need(s['ordered_configs'][:-1]==b['ordered_configs'],'same ordered base configs')
 for r in s['ordered_configs']:need(sha(r['path'])==r['sha256'],'config drift')
 return o
def reviewed(r,schema,status,s):
 q=exact(r)
 need(q.get('schema')==schema and q.get('status')==status and q.get('approved_by')=='EP-MAIN' and not q.get('TEST_ONLY',False),'Main review missing: '+schema)
 need(q.get('source_identity')==s['source_identity'] and q.get('geometry')==s['geometry'],'Main review Source/geometry mismatch')
 need(q.get('evidence_refs'),'Main review actual evidence required')
 for r in q['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'Main evidence drift')
 return q
def validate_static(s):
 check_background(s)
 need(s['mode_contract_ref']['sha256']==sha(__file__),'contract self pin')
 cpu=exact(s['mode_cpu_qualification_ref'])
 need(cpu.get('schema')=='EP_V3_SOURCE862_W_WV_REAL_CPU_NI_RECEIPT_V1' and cpu['status']=='PASS' and cpu['models_started']==0 and cpu['application_NI']=='NOT_MEASURED','CPU candidate identity')
 need(cpu.get('Source5')==s['source_identity'],'CPU Source5 identity mismatch')
 lib=cpu.get('production_library_ref',{})
 need(lib.get('path')==s['static_library_path'] and lib.get('sha256')==s['source_identity']['archive_sha256'] and sha(lib['path'])==lib['sha256'],'CPU production library identity mismatch')
 build=exact(cpu['fixture_build_ref'])
 need(build['returncode']==0 and build['Source5']==s['source_identity'] and build['library_sha256']==lib['sha256'],'CPU fixture actual build mismatch')
 cases={'normal','dual','return_full'}
 pairs=[p for p in cpu['pairs'] if p['mode']==s['mode']]
 need(len(pairs)==3 and {p['scenario']for p in pairs}==cases and all(p['PASS']is True for p in pairs),'exact nonempty three CPU mode pairs required')
 rows=[r for r in cpu['rows']if r['mode']==s['mode']]
 need(len(rows)==6 and {(r['scenario'],r['observer'])for r in rows}=={(c,o)for c in cases for o in ['000','111']},'exact CPU000/111 row stamps required')
 need(all(r['returncode']==0 and r['pass_test']is True and len(r['signature'])==1 for r in rows),'actual six CPU runs required')
 for case in cases:
  rr=[r for r in rows if r['scenario']==case]
  need(rr[0]['signature']==rr[1]['signature'],'CPU event identity mismatch')
 need(s.get('approved_launches')==1 and s.get('application_budget')==1 and s.get('source_keep')is True and s.get('automatic_retry')is False,'exact authorized one-start contract')
 modeq=reviewed(s['mode_cpu_review_ref'],'EP_MAIN_VECTOR1700_W_WV_MODE_CPU_REVIEW_V1','MAIN_REVIEWED_VECTOR1700_W_WV_MODE_CPU_PASS_NOT_APPLICATION',s)
 need(modeq['cpu_evidence_ref']==s['mode_cpu_qualification_ref'] and modeq['modes_qualified']==sorted(MODES),'Main modeCPU exact evidence/scope')
 hostq=reviewed(s['host_qualification_ref'],'EP_MAIN_VECTOR1700_W_WV_HOST_QUALIFICATION_V1','HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',s)
 need(hostq['modes_qualified']==sorted(MODES) and hostq['cohorts_qualified']==sorted('EP_PERF_PFV3_VECTOR4M_'+m+'_1700_V1'for m in MODES),'Host exact two modes/cohorts')
 for r in hostq['modules']:need(sha(r['path'])==r['sha256'],'Host module pin drift')
 need(all(s[k]in hostq['modules']for k in ['host_engine_ref','host_common_ref','mode_contract_ref','validation_module_ref','postprocess_module_ref','archive_module_ref']),'Host module binding absent')
 reuse=reviewed(s['matched_controls_review_ref'],'EP_MAIN_VECTOR1700_S_F_REFERENCE_REUSE_V1','MAIN_REVIEWED_EXACT_SOURCE862_S_F1700_REUSE_PASS',s)
 for mode,cycles in [('S',45974),('F',55925)]:
  c=reuse['controls'][mode];p=exact(c['accepted_point_ref']);a=exact(c['spec_ref']);ar=exact(c['archive_receipt_ref'])
  need(c['state']=='CLOSED_ACCEPTED' and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED' and p['hardware_drained']is True and p['cycles']==cycles,'accepted sameSource S/F control population')
  need(p['source_identity']==a['source_identity']==s['source_identity'] and p['input_identity_sha256']==s['input_identity_sha256'] and a['observer_env']==s['observer_env'] and a['geometry']==s['geometry'],'control Source/input/background')
  need(ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS','accepted control archive closure')
 need(s.get('scientific_scope_activated')is True,'Main frozen scope activation required')
 return dict(mode=s['mode'],RO=dict(applicability='NOT_APPLICABLE_RO_DISABLED'),modeCPU=s['mode_cpu_qualification_ref'],scientific_acceptance_granted=False,launch_permission=False,status='MAIN_REVIEWED_VECTOR1700_W_WV_MODE_BINDING_NOT_ACCEPTANCE')
def validate_fair_pair(a,b):
 check_background(a);check_background(b);need({a['mode'],b['mode']}==set(MODES),'exact W/WV pair')
 need(a['same_background_peer_cohort']==b['cohort'] and b['same_background_peer_cohort']==a['cohort'],'reciprocal pair')
 return dict(status='EXACT_NEW_SOURCE_W_WV_BACKGROUND_ENGINEERING_PASS',launch_permission=False)
def history_for(s):
 check_background(s)
 ft,v,d,t,m,profile=MODES[s['mode']]
 return dict(identity=dict(feature_vector=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=True),termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile=profile,formal_mode=s['mode'],profile_semantics=dict(effective_options=s['expected_effective_options'],research_switches=dict(V=v,T=t,M=m)),trace_files=[dict(name='commandlist',path=s['trace_entry'])],entry_trace_name='commandlist')
