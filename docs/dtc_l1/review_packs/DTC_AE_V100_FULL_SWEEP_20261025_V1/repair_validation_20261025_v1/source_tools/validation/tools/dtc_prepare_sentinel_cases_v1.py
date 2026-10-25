import pathlib,json,hashlib,copy,re,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=R/'control/sentinels';N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,o):
 with P(p).open('x') as f:json.dump(o,f,sort_keys=True,indent=2);f.write('\n')
basepath=T/'control/E2-AEV100-e7bb67e63e3c3847-DM_SPEC.json';base=read(basepath);assets=read(D/'ASSETS_CANDIDATE_V1.json')['assets'];modes={'LEGACY':(0,None),'BASE':(1,'PAPER_BASE'),'IO':(2,'PAPER_IO'),'OO':(3,'PAPER_OO'),'SECTOR':(4,'MODERN_OO_SECTOR')};cases=[];configrows={}
caprows=[]
for arm in ['CM','CH','DM']:
 p=T/'analysis'/('E2-AEV100-e7bb67e63e3c3847-'+arm+'.RESULT.json');r=read(p);assert r['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE';exitpath=T/'DTC/run/results'/r['uuid']/'NATIVE_EXIT.json';e=read(exitpath);caprows.append({'path':str(exitpath),'sha256':sha(exitpath),'raw_uncompressed_bytes':e['raw_uncompressed_bytes'],'peak_result_logical_bytes':e['peak_result_logical_bytes'],'source_input_elements':6000000,'actual_elapsed_seconds':e['elapsed_seconds'],'whole_trace_accepted_in_original_identity':True})
cap=D/'OUTPUT_CAP32_COMPONENT_EVIDENCE_V1.json';put(cap,{'schema':'COMPONENT_SENTINEL_OUTPUT32MiB_OPERATIONS_V1','observed_original_6M_vectorAdd_closed_outputs':caprows,'max_observed_result_logical_bytes':max(x['peak_result_logical_bytes'] for x in caprows),'new_operational_result_cap_bytes':32*1024**2,'new_vecadd_original_elements':4000000,'new_mixed_warp_instruction_records':9,'extra_new_metadata_and_evidence_reserve_bytes':1024**2,'reason':'Existing full 6M vectorAdd max result footprint 2.54MB; new full4M is smaller. Authored mixed is one CTA/9 instructions, diagnostic-event limit0, no per-event source debug. 32MiB allows >12x measured vector footprint plus metadata. This is an operational ceiling, not a guarantee about future unexpected debug output; cap guard remains fail-closed.','scope':'Only these10 new engineering sentinels; original and13 full-input repair caps unchanged','source_keep':True,'raw_logs_not_truncated':True,'no_simulator_starts_to_measure_new_cases':True})
for label,(mode,mode_label) in modes.items():
 folder=R/'DTC/env/component_sentinels'/label;folder.mkdir(parents=True,exist_ok=False);rows=[]
 for i,c in enumerate(base['configs']):
  b=P(c['path']).read_text()
  if i==1:b=re.sub(r'(?m)^-gpgpu_dtc_l1_finite_service \d+$','-gpgpu_dtc_l1_finite_service '+('1' if mode in [2,3] else '0'),b)
  if i==3:b=re.sub(r'(?m)^-gpgpu_dtc_l1_mode \d+$','-gpgpu_dtc_l1_mode '+str(mode),b)
  p=folder/('config-'+str(i)+'.config')
  with p.open('x') as f:f.write(b)
  rows.append({'path':str(p),'sha256':sha(p),'parent_config_path':c['path'],'parent_config_sha256':c['sha256']})
 configrows[label]=rows
for a in assets:
 binding=read(a['binding_path']);q=binding['qualification'];isvec=a['name']=='VECTORADD_ORIGINAL4M';program='COMPONENT_SENTINEL_NOT_FORMAL:'+a['name'];constants={'DTC_L1_m4_dynamic_loads':250000 if isvec else 3,'DTC_L1_m4_dynamic_stores':125000 if isvec else 1,'DTC_L1_m4_dynamic_atomics':0 if isvec else 2,'DTC_L1_m4_source_reachable_fence_ops':0,'DTC_L1_m4_proxy_fence_admits':0}
 for label,(mode,mode_label) in modes.items():
  s=copy.deepcopy(base);cohort='E2-AEREPAIR-SENT-'+a['input_digest'][:16]+'-'+label+'-V1';cfg=configrows[label];s.update(schema='DTC_REPAIR_ENGINEERING_COMPONENT_SENTINEL_SPEC_TEMPLATE_V1',cohort=cohort,cell=label,request='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1',suite='COMPONENT_SENTINEL_NOT_FORMAL',program=program,workload=a['input_digest'],input_digest=a['input_digest'],input_binding_path=a['binding_path'],input_binding_sha256=sha(a['binding_path']),expected={'CTA':q['expected_CTA'],'instructions':q['expected_instructions'],'kernels':q['expected_kernels']},configs=[{k:v for k,v in c.items() if k in ['path','sha256']} for c in cfg],correctness_validation_only=True,validation_kind='COMPONENT_SENTINEL_NOT_FORMAL',component_mode=label,source_kind=a['classification'],native_numerical_values='UNPROVEN',prior_formal_workload_membership=False)
  s['native_simulator_argv']=[base['native_simulator_argv'][0],'-trace',q['trace_entry']]+sum((['-config',c['path']] for c in cfg),[]);s['expected_options']['-gpgpu_dtc_l1_mode']=[str(mode)];s['expected_options']['-gpgpu_dtc_l1_finite_service']=['1' if mode in [2,3] else '0'];assert len(s['expected_options'])==270
  allowed={'-gpgpu_dtc_l1_mode','-gpgpu_dtc_l1_finite_service'};diff={k:{'parent':base['expected_options'][k],'sentinel':s['expected_options'][k]} for k in s['expected_options'] if s['expected_options'][k]!=base['expected_options'][k]};assert set(diff)<=allowed
  oldconfig_paths={x['path']:i for i,x in enumerate(base['configs'])};runtime=[]
  for row in base['runtime_files']:
   row=copy.deepcopy(row)
   if row['actual_realpath'] in oldconfig_paths:
    c=cfg[oldconfig_paths[row['actual_realpath']]];row.update(actual_realpath=c['path'],sha256=c['sha256'],target=str(P(c['path']).relative_to(R)))
   runtime.append(row)
  s['runtime_files']=runtime;s['original_environment']['DTC_AG7_INPUT_SHA']=a['input_digest'];s['original_environment']['DTC_AG7_ROI_SHA']=hashlib.sha256(json.dumps({'input_digest':a['input_digest'],'scope':'WHOLE_DECLARED_COMPONENT_INPUT','kernel_names':[x['kernel'] for x in q['rows']]},sort_keys=True,separators=(',',':')).encode()).hexdigest()
  contract={'mode_label':mode_label,'zero_counters':[],'equal_counter_pairs':[],'constant_counters':{},'mode_option':str(mode),'required_terminal':'NATURAL_FULL_DECLARED_TRACE','native_numerical_values':'UNPROVEN'}
  if mode==0:contract['absent_counter_prefixes']=['DTC_L1_']
  else:
   contract['constant_counters']=copy.deepcopy(constants);contract['zero_counters']=['DTC_L1_lower_outstanding'];contract['equal_counter_pairs']=[['DTC_L1_lower_requests_acquired','DTC_L1_lower_requests_released'],['DTC_L1_m4_source_completions','DTC_L1_m4_observation_retires']]
   if mode==1:
    contract['zero_counters']+=['DTC_L1_pib_occupancy'];contract['equal_counter_pairs']+=[['DTC_L1_pib_admits','DTC_L1_pib_retires']];contract['constant_counters'].update({k:0 for k in ['DTC_L1_m4_store_admits','DTC_L1_m4_atomic_admits','DTC_L1_m4_bypass_load_admits','DTC_L1_m4_source_completions','DTC_L1_m4_observation_retires']})
   else:
    prefix={2:'io',3:'oo',4:'sector'}[mode];contract['zero_counters']+=['DTC_L1_'+prefix+'_inflight_current','DTC_L1_'+prefix+'_pib_occupancy'];contract['equal_counter_pairs'] += [['DTC_L1_'+prefix+'_lower_created','DTC_L1_'+prefix+'_lower_issued'],['DTC_L1_'+prefix+'_lower_created','DTC_L1_'+prefix+'_lower_responses'],['DTC_L1_'+prefix+'_completion_dependency_count','DTC_L1_'+prefix+'_completion_dependency_closed']]
    if mode in [3,4]:contract['zero_counters'].append('DTC_L1_'+prefix+'_active_refs')
    if mode==2:contract['zero_counters']+=['DTC_L1_io_inflight_identity_mismatch','DTC_L1_io_partial_entries_current','DTC_L1_io_partial_lines_held_current']
    total=125000 if isvec else 4;contract['constant_counters'].update({'DTC_L1_m4_store_admits':125000 if isvec else 1,'DTC_L1_m4_atomic_admits':0 if isvec else 2,'DTC_L1_m4_bypass_load_admits':0 if isvec else 1,'DTC_L1_m4_source_completions':total,'DTC_L1_m4_observation_retires':total})
  s['terminal_contract']=contract;sp=D/(cohort+'.SPEC_TEMPLATE.json');put(sp,s);cases.append({'cohort':cohort,'input_digest':a['input_digest'],'program':program,'mode':mode,'component_mode':label,'validation_kind':'COMPONENT_SENTINEL_NOT_FORMAL','source_kind':a['classification'],'spec_template_path':str(sp),'spec_template_sha256':sha(sp),'input_binding_path':a['binding_path'],'input_binding_sha256':sha(a['binding_path']),'terminal_contract':contract,'operational_result_cap_bytes':32*1024**2,'output_cap_evidence_path':str(cap),'output_cap_evidence_sha256':sha(cap),'expected':s['expected'],'option_vector_changes_from_original_DM':diff,'input_source_KEEP':True})
policy=F/'framework/docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md';source=F/'core/src/gpgpu-sim/shader.cc';statkeys=set(re.findall(r'"(DTC_L1_[A-Za-z0-9_]+) =',source.read_text()));allkeys=set()
for c in cases:
 co=c['terminal_contract'];allkeys.update(co['zero_counters']);allkeys.update(co['constant_counters']);allkeys.update(k for pair in co['equal_counter_pairs'] for k in pair)
assert allkeys<=statkeys,sorted(allkeys-statkeys)
o={'schema':'DTC_REPAIR_TEN_ENGINEERING_SENTINEL_CASES_CANDIDATE_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':cases,'point_count':10,'new_scientific_model_starts':0,'original288_membership':False,'source_policy':{'path':str(policy),'sha256':sha(policy),'section7_lines':[188,201],'five_mode_lines':[194,198],'mixed_line':199,'interpretation':'One mixed sentinel is minimum; run same authored component across five modes as broad correctness regression under current explicit user repair-testing authorization.'},'model_platform':'Same original Volta-based FAST64 options/config bytes except selected DTC mode and finite_service enabled only whole-line IO/OO; not stock physical V100 or performance calibration','cold_state_contract':{'new_process_per_case':True,'reused_results':False,'checkpoint_option':'0','resume_option':'0','all_initial_lifecycle_state_from_original_Core_constructors':True,'no_manual_reset_of_live_or_original_state':True,'retained_valid_Ref0_cachelines_not_required_zero_at_terminal':True},'config_bytes':configrows,'source_stats_path':str(source),'source_stats_sha256':sha(source),'source_unchanged_core_commit':read(F/'control/CORE_BUILD_PROFILE.json')['core_commit'],'assets_manifest_path':str(D/'ASSETS_CANDIDATE_V1.json'),'assets_manifest_sha256':sha(D/'ASSETS_CANDIDATE_V1.json'),'source_keep':True,'not_authority_registration':True,'not_an_entry_switch':True}
put(R/'control/SENTINEL_CASES_CANDIDATE_V1.json',o);print(json.dumps({'path':str(R/'control/SENTINEL_CASES_CANDIDATE_V1.json'),'sha256':sha(R/'control/SENTINEL_CASES_CANDIDATE_V1.json'),'cases':len(cases),'assets':[{k:a[k] for k in ['name','input_digest','classification']} for a in assets],'new_model_starts':0},indent=2))
