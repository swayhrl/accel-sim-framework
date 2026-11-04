from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,textwrap
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');A=P/'research/performance_first_v4_20261104_v1/track_a';O=A/'private_main_integration';V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';OLD=V/'runtimes/midtag';B=P/'research/performance_first_v4_20261104_v1/track_b/private_runtime'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text())
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def repl(t,n,new):
 node=next(x for x in ast.parse(t).body if isinstance(x,ast.FunctionDef)and x.name==n);ls=t.splitlines(keepends=True);return ''.join(ls[:node.lineno-1])+textwrap.dedent(new).strip()+'\n'+''.join(ls[node.end_lineno:])
assert sha(B/'runtime_monitor_schema_v4_strict.py')=='540feb2cd00044dd9d62b8a0858181a2c026cb82ac63cb0be1e9bdb65ab8126b'
assert sha(B/'RUNTIME_FULL_43_CONTRACT_V4.json')=='29cb1d6a3a70917e2ce478b3ab38b11532c1072d8f05151ae71c619dfe9ea6f0'
oldspec=read(P/'execution_midtag_v3_20261104_v1/midtag/cases/EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1/control/FROZEN_SPEC.json')
closure=read(A/'SOURCE78_NATIVE_DEPENDENCY_CLOSURE.json');write(O/'SOURCE78_NATIVE_CLOSURE.json',closure)
extra=read(B/'TRACE_CHILD_HOST_DEPENDENCIES.json');extra['Source5']=closure['Source5'];extra['scope']='SOURCE78_ACTUAL_UNCHANGED_HELPER_LAUNCH_TOOL_DEPENDENCIES';write(O/'SOURCE78_HELPER_DEPENDENCIES.json',extra)
graphs=[]
for lane,filename in [('A1','A1_EXACT_REQUEST.json'),('A3','A3_OPTIONAL_EXACT_REQUEST.json')]:
 request=read(A/filename);root=O/lane;H=root/'runtime';E=root/'execution';H.mkdir(parents=True,exist_ok=True);(E/'control').mkdir(parents=True,exist_ok=True)
 for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py','REF_282_S.json']:shutil.copyfile(OLD/n,H/n)
 shutil.copytree(OLD/'deps',H/'deps',dirs_exist_ok=True)
 for n in ['native_route_guard_v3.py','safe_native_core_v3.py']:shutil.copyfile(V/'agent_d_execution'/n,H/n)
 cohorts=sorted(p['cohort']for p in request['exact_points']);goal=request['request_id'];specs={p['cohort']:read(p['spec_candidate_ref']['path'])for p in request['exact_points']}
 scope=dict(schema='EP_PFV4_SOURCE78_INDEPENDENT_REQUEST2_SCOPE_V1',request_id=goal,source_identity=closure['Source5'],points=[])
 for c,s in specs.items():
  base=s['accepted_same_mode_reference'];preview=H/'options'/(c+'.json');write(preview,s['expected_effective_options'])
  scope['points'].append(dict(id=c,mode=s['mode'],family='G64W8',geometry=s['geometry'],input_identity_sha256=s['input_identity_sha256'],old_REF850_spec_ref=base['spec_ref'],option_preview_ref=ref(preview),accepted_same_mode_ref=base))
 write(H/'FAMILY_SCOPE.json',scope)
 t=(H/'ep_perf_common_v2.py').read_text().replace(str(P/'execution_midtag_v3_20261104_v1/midtag'),str(E)).replace("GOAL = 'EP_L2_MID_TAG_850MHZ_V1_20261104'",'GOAL = '+repr(goal));(H/'ep_perf_common_v2.py').write_text(t)
 t=(V/'agent_c_resources/resources_midtag.py').read_text().replace("REQUEST='EP_L2_MID_TAG_850MHZ_V1_20261104'",'REQUEST='+repr(goal));(H/'resources_request2.py').write_text(t)
 t=(H/'mode_contract.py').read_text().replace("SYSTEM_REQUEST_ID='EP_L2_MID_TAG_850MHZ_V1_20261104'",'SYSTEM_REQUEST_ID='+repr(goal)).replace("FAMILY_SCOPE_SHA='ef03c2cb2789a901ec5390a9c42d4434ec97773bc6f0115e8262e86643b8c41c'",'FAMILY_SCOPE_SHA='+repr(sha(H/'FAMILY_SCOPE.json')))
 t=repl(t,'family_row',"""
 def family_row(s):
  rows=[r for r in family_scope()['points']if r['id']==s.get('cohort')];need(len(rows)==1,'outside exact independent request2 cells');return rows[0]
 """)
 t=repl(t,'check_background',"""
 def check_background(s):
  r=family_row(s);base=exact(r['old_REF850_spec_ref']);o=s['expected_effective_options'];g=r['geometry']
  need(s['science_request_id']==SYSTEM_REQUEST_ID and s['source_identity']==base['source_identity']==family_scope()['source_identity'],'request/Source5')
  need(s['mode']==r['mode']and s['geometry']==g==dict(sets=64,ways=8,slices=64,line_bytes=128),'exact mode/geometry')
  need(type(s['M'])is bool and type(s['T'])is bool and not s['M']and not s['T']and s.get('ro_qualification_ref')is None,'RO disabled typed booleans')
  for k in ['input_identity_sha256','input_binding_ref','trace_entry','all_unique_kernel_members','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','observer_env']:
   need(s.get(k)==base.get(k),'input/observer drift:'+k)
  expected=dict(base['expected_effective_options']);expected['-gpgpu_cache:dl2']='S:64:128:8,L:B:m:L:P,A:128:1,128:0,32'
  need(len(o)==282 and o==expected and o==exact(r['option_preview_ref']),'undeclared option drift or incomplete282')
  need(all(o[k]==v for k,v in flags(s['mode']).items()),'mode flags')
  need(o['-gpgpu_clock_domains']=='1132.0:1132.0:1132.0:850.0'and o['-dram_latency']=='100'and o['-gpgpu_frfcfs_dram_sched_queue_size']=='128','850/L100/FR128')
  need(all(o[k]=='1'for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats']),'observer111')
  need(s['same_background_peer_cohort']==expected_peer(s),'peer')
  need([q['sha256']for q in s['ordered_configs'][:-1]]==[q['sha256']for q in base['ordered_configs']],'accepted ordered config prefix bytes')
  for q in s['ordered_configs']:need(sha(q['path'])==q['sha256'],'config bytes')
  need(rmatch(s['absolute_REF850_spec_ref'],r['old_REF850_spec_ref']),'absolute REF origin')
  geometry_module().qualify_history_spec(s)
  return o
 """)
 t=repl(t,'validate_anchor',"""
 def validate_anchor(s,mode='S'):
  peer=next(p for p in family_scope()['points']if p['mode']==mode);r=peer['accepted_same_mode_ref'];a=exact(r['spec_ref']);p=exact(r['accepted_point_ref']);ar=exact(r['archive_receipt_ref'])
  need(a['mode']==p['mode']==mode and p['hardware_drained']and p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED','accepted REF population')
  need(a['source_identity']==p['source_identity']==s['source_identity']and a['input_identity_sha256']==s['input_identity_sha256'],'anchor identity')
  need(a['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128)and a['observer_env']==s['observer_env'],'anchor geometry/observer')
  need(ar['source_keep']and ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS','anchor archive receipt')
  need(len(ar['native_restores'])==2 and len({x['target']for x in ar['native_restores']})==2 and all(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'for x in ar['native_restores']),'anchor two independent restores')
  return dict(accepted_point_ref=r['accepted_point_ref'],source_keep=True,mode=mode)
 """)
 t=repl(t,'validate_mode_cpu',"""
 def validate_mode_cpu(s):
  q=exact(s['mode_cpu_qualification_ref']);prior=exact(q['prior_mode_cpu_qualification_ref'])
  need(q['source_identity']==prior['source_identity']==s['source_identity'],'CPU Source5')
  need(prior['status']=='MAIN_REVIEWED_MIDTAG_MODE_CPU_PASS_NOT_APPLICATION'and prior['approved_by']=='EP-MAIN','prior Main CPU qualification')
  ni=exact(prior['protocol_ref']);echo=exact(prior['actual282_ref']);g=s['geometry']
  need(ni['source_identity']==echo['source_identity']==s['source_identity'],'prior CPU Source identity')
  prior_cohort='EP_PERF_PFV3_MIDTAG_FWT_'+s['mode']+'_G64W8_V1'
  prior_echo=next((r for r in echo['runs']if r['cohort']==prior_cohort),None)
  need(prior_echo is not None and prior_echo['exact282_PASS']and prior_echo['actual_option_count']==282 and prior_echo['returncode']==0,'prior exact282 geometry/mode proof')
  prior_options=exact(prior_echo['option_ref'])
  need(len(prior_options)==282 and {k:v for k,v in prior_options.items()if k!='-trace'}=={k:v for k,v in s['expected_effective_options'].items()if k!='-trace'},'CPU actual282 background mismatch beyond exact input trace')
  need(s['expected_effective_options']['-trace']==exact(s['input_binding_ref'])['trace_entry'],'rebound exact input trace identity')
  need(any(p['sets']==g['sets']and p['ways']==g['ways']and p['mode']==s['mode']and p['PASS']for p in ni['pairs']),'exactgeometry mode prior CPU NI absent')
  need(s['cohort']in q['rebound_exact_cohorts']and q['original_tests_rerun']==0,'exact cohort engineering rebind')
  need(q['application_NI']=='NOT_MEASURED'and q['B0_M0a_application_NI']=='NOT_PROVEN_HELD_ON','NI claim')
  return dict(status='SOURCE78_PRIOR_CPU_MODE_GEOMETRY_REBOUND_NO_RETEST',application_NI='NOT_MEASURED',new_application_NI_is_launch_gate=False)
 """)
 t=repl(t,'validate_hostq',"""
 def validate_hostq(s):
  q=exact(s['host_qualification_ref']);need(q['source_identity']==s['source_identity']and q['status']=='PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE','Host engineering rebind')
  for r in q['modules']:need(sha(r['path'])==r['sha256'],'Host module drift')
  need(all(any(rmatch(x,r)for x in q['modules'])for r in[s['host_engine_ref'],s['validation_module_ref'],s['mode_contract_ref']]),'Host scope incomplete');return q
 """)
 (H/'mode_contract.py').write_text(t)
 t=(H/'mode_aware_terminal.py').read_text().replace("'mode_contract.py': '536260c779795f059aef96d76e28080f8edd1b79d9d24b7151d312255715310b'","'mode_contract.py': "+repr(sha(H/'mode_contract.py')));(H/'mode_aware_terminal.py').write_text(t)
 t=(H/'native_route_guard_v3.py').read_text().replace('x.startswith("EP_PERF_PFV3_")','x in '+repr(cohorts)).replace('wrong V3 cohort namespace','outside independent request2 namespace');(H/'native_route_guard_v3.py').write_text(t)
 t=(H/'ep_perf_native_wv_modes_draft.py').read_text();i=t.index('SCOPED_MODES =');j=t.index('ALLOWED_COHORTS=',i);t=t[:i]+'SCOPED_MODES = '+repr({c:specs[c]['mode']for c in cohorts})+'\n'+t[j:]
 t=t.replace("'outside exact8 midTag scope/mode'","'outside independent exact2 Source78 scope/mode'").replace("'not an exact8 midTag cohort'","'outside exact independent request2 cohort'")
 i=t.index('NATIVE_ROUTE_GUARD_REF=');j=t.index('\nMODE_CONTRACT_SHA=',i);t=t[:i]+'NATIVE_ROUTE_GUARD_REF='+repr(ref(H/'native_route_guard_v3.py'))+t[j:]
 t=t.replace("MODE_CONTRACT_SHA='536260c779795f059aef96d76e28080f8edd1b79d9d24b7151d312255715310b'",'MODE_CONTRACT_SHA='+repr(sha(H/'mode_contract.py'))).replace("NEW_VALIDATOR_SHA='0de4f89cfcdc83b3d4414b8075372448459d4248ce165e518f7f2051ca7bcda1'",'NEW_VALIDATOR_SHA='+repr(sha(H/'mode_aware_terminal.py')))
 schema_refs=dict(contract_ref=ref(B/'RUNTIME_FULL_43_CONTRACT_V4.json'),closure_ref=ref(O/'SOURCE78_NATIVE_CLOSURE.json'),extra_dependencies_ref=ref(O/'SOURCE78_HELPER_DEPENDENCIES.json'))
 t=t.replace('from ep_perf_common_v2 import *','from ep_perf_common_v2 import *\n_SCHEMA_REFS='+repr(schema_refs)+'\n_SCHEMA_MODULE='+repr(ref(B/'runtime_monitor_schema_v4_strict.py'))+"""
def validate_spec_contract(s,require_bound_cpu=False):
    return module(_SCHEMA_MODULE,'source78_strict43').validate_spec_contract(s,**_SCHEMA_REFS,require_bound_cpu=require_bound_cpu,check_current_domain=True,check_current_dependencies=True)
def engineering_spec_for(case):
    s=read(spec_path(case));validate_spec_contract(s)
    need(s['schema']=='EP_FULL_PERF_EXACT_SPEC_V1'and s['goal']==FRONTEND_GOAL and s['science_request_id']==GOAL and s['cohort']==case,'spec identity')
    need(s['host_engine_ref']==ref(__file__)and s['host_common_ref']==ref(P(__file__).with_name('ep_perf_common_v2.py')),'entry engine drift')
    authorized_scope_mode(s);formal_mode_contract(s)
    eligibility=exact(s['eligibility_ref']);binding=exact(s['input_binding_ref'])
    need(eligibility['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE'and eligibility['source_identity']==s['source_identity']and eligibility['input_identity_sha256']==s['input_identity_sha256']and s['mode']in eligibility['modes_qualified'],'input/mode eligibility')
    need(eligibility['ordered_kernel_identity']==binding['ordered_kernel_identity'],'eligibility kernel closure')
    source=exact(s['source_qualification_ref']);need(source['source_identity']==s['source_identity'],'Source qualification identity')
    prior_source=exact(source['prior_source_qualification_ref']);need(prior_source['source_identity']==s['source_identity'],'prior source identity')
    old_source=exact(prior_source['prior_sourceq_ref']);need(old_source['source_identity']==s['source_identity'],'original CPU Source5')
    for r in old_source['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'original Source CPU evidence changed')
    for p,h in s['pinned_files'].items():need(sha(p)==h,'host/runtime pin drift '+p)
    need(sha(s['binary_path'])==s['source_identity']['binary_sha256']and sha(s['static_library_path'])==s['source_identity']['archive_sha256'],'Source78 ELF/archive drift')
    return s
def fresh_science_authorization(s):
    a=exact(s['Main_scientific_launch_authorization'])
    need(a.get('explicit_user_approval')is True and a.get('approved_launches')==2 and a.get('allowed_cohorts')==sorted(ALLOWED_COHORTS)and a.get('goal')==GOAL and a.get('Source5')==s['source_identity'],'MISSING_FRESH_EXACT_REQUEST2_SCIENTIFIC_AUTHORIZATION')
    need(a.get('request_ref')==ref(ROOT/'control/EXACT_REQUEST.json'),'fresh request identity drift')
    return a
def preclaim_schema(case,binding=None):
    s=engineering_spec_for(case)
    if binding is not None:
        need(binding.get('cohort')==case and binding.get('spec_sha256')==sha(spec_path(case)),'preclaim binding identity')
        s=dict(s,host_cpu=binding['host_cpu']);validate_spec_contract(s,require_bound_cpu=True)
    fresh_science_authorization(s)
    return s
""")
 t=repl(t,'spec_for',"""
 def spec_for(case,require_release=True):
    s=engineering_spec_for(case);fresh_science_authorization(s)
    registry,unused=authority();q=registry['registered_future_requests'].get(GOAL)
    need(q is not None,'FRESH_REQUEST2_NOT_REGISTERED')
    need(q['budget']==2==len(q['admitted_specs'])and q['remaining']==2-len(q['consumed']),'fresh exact request2 budget arithmetic')
    need(q['admitted_specs'].get(case)==sha(spec_path(case))and q['authorization_ref']==s['Main_scientific_launch_authorization'],'registered Spec/approval binding')
    need(q['runtime_versions'].get(s['host_engine_ref']['sha256'])==dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']),'runtime version binding')
    scope=module(s['mode_contract_ref'],'request2_fair_pair');scope.validate_fair_pair(s,read(spec_path(s['same_background_peer_cohort'])))
    for row in scope.family_scope()['points']:
        r=row['accepted_same_mode_ref'];point=exact(r['accepted_point_ref']);namespace=r.get('request')or point.get('goal',FRONTEND_GOAL)
        accepted=registry['registered_future_requests'][namespace]['consumed'].get(r['cohort'],{})
        need(accepted.get('state')=='CLOSED_ACCEPTED'and accepted.get('accepted_point_ref')==r['accepted_point_ref'],'exact official accepted REF population')
    validate_spec_contract(s)
    return s
 """)
 t=t.replace("    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')\n","    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')\n    candidate=engineering_spec_for(case)\n    fresh_science_authorization(candidate)\n",1)
 t=t.replace("ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json'","ROOT/'control/NATIVE_ENTRY_ROUTE_V4.json'").replace("ROOT / 'control/NATIVE_ENTRY_ROUTE_V3.json'","ROOT / 'control/NATIVE_ENTRY_ROUTE_V4.json'").replace("P(entry['path'])==ROOT.parent/'bin/native_midtag_v3'","P(entry['path'])==P(__file__).with_name('native_request2')")
 t=t.replace("qualification['status'] == 'HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'","qualification['status'] == 'PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE'")
 t=t.replace("    s = dict(s, host_cpu=binding['host_cpu'])\n","    s = dict(s, host_cpu=binding['host_cpu'])\n    validate_spec_contract(s,require_bound_cpu=True)\n",1);(H/'ep_perf_native_wv_modes_draft.py').write_text(t)
 entry=H/'native_request2';entry.write_text("#!/usr/bin/python3\nimport os,sys,json\nsys.path.insert(0,"+repr(str(H))+")\nos.environ['EP_FULL_PERF_NATIVE_ENTRY']='1'\nfrom ep_perf_frontend import main\ntry:print(json.dumps(main(sys.argv[1:])))\nexcept Exception as e:\n print(json.dumps(dict(status='HOLD',reason=str(e),automatic_retry=False)),file=sys.stderr)\n sys.exit(2)\n");entry.chmod(0o755)
 write(E/'control/EXACT_REQUEST.json',request);write(E/'control/USER_AUTHORIZATION.json',dict(schema='EP_PFV4_FRESH_REQUEST2_AUTHORIZATION_REQUIRED_V1',goal=goal,explicit_user_approval=False,approved_launches=0,allowed_cohorts=cohorts,Source5=closure['Source5'],request_ref=ref(E/'control/EXACT_REQUEST.json'),status='PENDING_FRESH_SCIENTIFIC_AUTHORIZATION_MAIN_ONLY'))
 q=E/'control/MODE_CPU_EVIDENCE_REBIND.json';write(q,dict(status='SOURCE78_PRIOR_MODE_GEOMETRY_REBOUND_NO_RETEST',source_identity=closure['Source5'],prior_mode_cpu_qualification_ref=oldspec['mode_cpu_qualification_ref'],rebound_exact_cohorts=cohorts,original_tests_rerun=0,application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON',new_application_NI_is_launch_gate=False,scientific_launch_permission=False))
 sourceq=E/'control/SOURCE_CPU_EVIDENCE_REBIND.json';write(sourceq,dict(status='EXACT_ACCEPTED_SOURCE_CPU_EVIDENCE_REUSED_NOT_NEW_APP_ACCEPTED',source_identity=closure['Source5'],prior_source_qualification_ref=oldspec['source_qualification_ref'],new_application_acceptance=False))
 t=(H/'ep_perf_frontend.py').read_text();start=t.index('COHORTS=');end=t.index('\ndef main',start);t=t[:start]+'COHORTS='+repr(cohorts)+t[end:];t=t.replace('outside exact8 midTag scope','outside exact independent request2 scope')
 t=t.replace(" registry,_=authority();q=", " s=read(ROOT/'cases'/case/'control/FROZEN_SPEC.json');engine=module(s['host_engine_ref'],'frontend_preclaim_schema');engine.engineering_spec_for(case);engine.fresh_science_authorization(s)\n registry,_=authority();q=")
 (H/'ep_perf_frontend.py').write_text(t)
 t=(H/'ep_perf_archive.py').read_text().replace(str(Path('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_midtag_v3_20261104_v1/midtag')),'/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_pfv4_'+lane.lower()+'_source78_20261104_v1');(H/'ep_perf_archive.py').write_text(t)
 controller=H/'private_main_dispatcher.py';controller.write_text("""# Main-only private claim carrier; no import-time actions.
import ep_perf_native_wv_modes_draft as engine
def claim(case,binding):
    # Both schema and fresh request2 authorization precede locks or claim writes.
    s=engine.preclaim_schema(case,binding)
    engine.spec_for(case)
    with engine.locked(engine.GLOBAL_MAIN_ADMISSION_LOCK):
        path=engine.ROOT/'control/DISPATCH_CLAIMS.json'
        carrier=engine.read(path)if path.exists()else dict(claims={})
        engine.need(case not in carrier['claims'],'claim already exists; no retry')
        carrier['claims'][case]=dict(state='CLAIMED',spec_sha256=engine.sha(engine.spec_path(case)),host_cpu=binding['host_cpu'],estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],remaining_write_bytes=s['limits']['result_bytes'])
        engine.put(path,carrier)
    return dict(status='EXACT_UNSPENT_CLAIM_CREATED',cohort=case)
""")
 modules=[ref(f)for f in sorted(H.rglob('*'))if f.is_file()and '__pycache__'not in str(f)]+[ref(B/'runtime_monitor_schema_v4_strict.py'),ref(B/'RUNTIME_FULL_43_CONTRACT_V4.json')]
 hostq=E/'control/HOST_DELTA_QUALIFICATION_CANDIDATE.json';write(hostq,dict(status='PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE',source_identity=closure['Source5'],modules=modules,prior_host_qualification_ref=oldspec['host_qualification_ref'],prior_mode_cpu_ref=oldspec['mode_cpu_qualification_ref'],application_NI='NOT_MEASURED',applicationNI_NOT_MEASURED_is_new_launch_gate=False,shared_install=False,science_permission=False))
 for c,s in specs.items():
  s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',goal='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1',science_request_id=goal,application_budget=1,approved_launches=1,registered_starts=0,scientific_launch_permission=False,Main_scientific_launch_authorization=ref(E/'control/USER_AUTHORIZATION.json'),host_cpu=None,native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt'),host_engine_ref=ref(H/'ep_perf_native_wv_modes_draft.py'),host_common_ref=ref(H/'ep_perf_common_v2.py'),host_qualification_ref=ref(hostq),mode_contract_ref=ref(H/'mode_contract.py'),validation_module_ref=ref(H/'mode_aware_terminal.py'),native_entry_ref=ref(entry),native_route_guard_ref=ref(H/'native_route_guard_v3.py'),source_qualification_ref=ref(sourceq),mode_cpu_qualification_ref=ref(q),helpers_ref=oldspec['helpers_ref'],output_module_ref=oldspec['output_module_ref'],resource_module_ref=ref(H/'resources_request2.py'),resource_policy_ref=oldspec['resource_policy_ref'],absolute_REF850_spec_ref=s['accepted_same_mode_reference']['spec_ref'],REF850_usage='ABSOLUTE_REFERENCE_ONLY_NOT_SAME_BACKGROUND_S',status='PRIVATE_COMPLETE_CONDITIONAL_EXACT_SPEC_NO_AUTHORITY',conditional_one_start_fields_are_not_registered_budget=True)
  s.update(postprocess_module_ref=ref(H/'ep_perf_postprocess.py'),archive_module_ref=ref(H/'ep_perf_archive.py'),compact_module_ref=oldspec['compact_module_ref'],validation_contract_ref=oldspec['validation_contract_ref'])
  s['pinned_files']=closure['pinned_files'].copy()
  for x in extra['dependencies']:s['pinned_files'][x['path']]=x['sha256']
  for r in modules:s['pinned_files'][r['path']]=r['sha256']
  s['pinned_files'][str(hostq)]=sha(hostq);write(E/'cases'/c/'control/FROZEN_SPEC.json',s)
 write(E/'control/NATIVE_ENTRY_ROUTE_V4.json',dict(status='DRAFT_NOT_INSTALLED',goal=goal,scientific_scope_activated=False,approved_by=None,exact_cohorts=cohorts,entry_ref=ref(entry),guard_module_ref=ref(H/'native_route_guard_v3.py'),owned_runtime_pins=modules,frontend_ref=ref(H/'ep_perf_frontend.py'),install_authorization=False))
 graphs.append(dict(lane=lane,request_id=goal,requested_starts=2,approved_registered_consumed_starts=0,root=str(root),runtime=str(H),execution=str(E),candidate_specs=[ref(E/'cases'/c/'control/FROZEN_SPEC.json')for c in cohorts],entry_ref=ref(entry),hostq_ref=ref(hostq)))
write(O/'PRIVATE_GRAPH_INDEX.json',dict(schema='EP_PFV4_SOURCE78_PRIVATE_TWO_INDEPENDENT_REQUEST2_GRAPHS_V1',graphs=graphs,A2_not_integrated_due_WV_mode_eligibility_gap=True,old_track_a_pack_frozen_untouched=True,shared_graph_or_registry_mutations=0))
print(json.dumps(dict(private_graphs=len(graphs),points=4,science_starts=0)))

