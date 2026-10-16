import csv,hashlib,json,pathlib,re,subprocess,datetime
R=pathlib.Path.cwd(); B=R/'docs/dtc_l1/iscas2027/service_closure_174_v1'; P=B/'review_pack'; C=pathlib.Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def tab(p): return list(csv.DictReader(pathlib.Path(p).open(),delimiter='\t'))
def js(p): return json.loads(pathlib.Path(p).read_text())
def git(*args,repo=R): return subprocess.check_output(['git','-C',str(repo),*args]).decode().strip()
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_CORRECTED_SOURCE_POLICY_ORDERING_AND_PRESERVATION_V2','model_input_or_configuration_changes':False,'new_jobs_or_signals':0}
source=tab(P/'r0/SOURCE_HASHES.tsv');assert len(source)==18
for row in source:
 data=subprocess.check_output(['git','-C',str(C),'show',row['core_commit']+':'+row['path']]);assert hashlib.sha256(data).hexdigest()==row['sha256']
out['all18_historical_source_git_objects']='PASS'
assert git('rev-parse','HEAD',repo=C)=='6fba0136f8465b59fe5858a950fa39efb265f654' and not git('status','--porcelain',repo=C)
s=(C/'src/gpgpu-sim/gpu-sim.cc').read_text();assert re.search(r'"-gpgpu_dtc_l1_finite_service".{0,350}?"0"\);',s,re.S)
out['current_core_clean_default_off']='PASS';out['gpu_sim_cc_sha256']=sha(C/'src/gpgpu-sim/gpu-sim.cc');out['finite_test_source_sha256']=sha(C/'tests/dtc_l1_finite_service_test.cc')
r0=datetime.datetime.fromisoformat(git('show','-s','--format=%cI','b412ed79d42a082c2d68f89c905a246c6bcea732'));created=datetime.datetime.fromtimestamp(1792138490,datetime.timezone.utc)
assert (r0-created).total_seconds()==399
states=tab(P/'checkpoint_20261016T2133Z/REGISTERED_R2_STATE.tsv');starts=[js(pathlib.Path(x['raw_dir'])/'RUN_START.json') for x in states if x['status']=='PASS_CHECKED_SCOPE']
first=min(datetime.datetime.fromisoformat(x['launch_utc']) for x in starts)
finite=min(datetime.datetime.fromisoformat(x['launch_utc']) for x in starts if x['spec']['core']=='6fba0136f8465b59fe5858a950fa39efb265f654')
last=max(datetime.datetime.fromisoformat(js(pathlib.Path(x['run_dir'])/'RUN_TERMINAL.json')['terminal_utc']) for x in tab(P/'r1/FINAL_CHECKS_V2.tsv'))
assert r0<first and last<finite
out['gates']={'R0_first_receipt_seconds':399,'R0_first_commit':str(r0),'first_any_R2':str(first),'last_R1_V2_full_NN_terminal':str(last),'first_finite_V2_R2':str(finite),'qualification':'R0 before all R2; R1 V2 before finite V2. Unchanged conventional TRAD96 pilots preserved during finite V2 requalification.','preserved_A1_failure':'POLICY_ORDERING_A1_FAILURE_PRESERVED.json'}
invalid=tab(P/'r2/INVALIDATED_FINITE_V1.tsv');assert len(invalid)==4
for x in invalid: assert js(pathlib.Path(x['run_dir'])/'RUN_TERMINAL.json')['exit_status']!=0
out['invalidated_finite_v1_four_raw_terminals']='PRESERVED_EXCLUDED'
old=P/'checkpoint_20261016T1612Z'; hashes=js(old/'FINAL_FILES_SHA256_V2.json')
for name,value in hashes.items():assert sha(old/name)==value
assert (old/'FINAL_MANIFEST_FAILURE_PRESERVED.json').exists();out['older_corrected_manifest']='PASS_ALL_'+str(len(hashes))+'_FILES_ORIGINAL_FAILURE_PRESERVED'
modern=tab(P/'checkpoint_20261016T2133Z/MODERN_BASELINE_ONLY.tsv');assert len(modern)==4
for x in modern:assert all(v is True for v in json.loads(x['qualification']).values()) and x['effective_mshr'].startswith('384_')
out['modern_baseline_four_effective_path_checks']='PASS_COUNTERFACTUAL_ONLY'
capacity=tab(P/'modern_capacity_v2/FROZEN629_CAPACITY_CALCULATION_V1.tsv');assert len(capacity)==629
for x in capacity:assert x['proposed_total_data_shared_kib']=='128' and x['proposed_dtc_kib']=='80' and x['service_and_execution']=='NOT_QUALIFIED_MODERN_DTC_HOLD'
out['capacity629']='ARITHMETIC_128KIB_NOT_SERVICE_OR_LEGAL_DOMAIN_QUALIFICATION'
resources=tab(P/'resource_vector_v1/RESOURCE_VECTOR.tsv');assert len(resources)==7 and all(x['logical_mapping_extra_data_bytes']=='0' for x in resources)
dtc=[x for x in resources if x['mode'] in ('2','3')];assert len(dtc)==3
for x in dtc:assert [int(x[k]) for k in ['dtc_data_bytes','ordinary_enabled_data_bytes','enabled_data_total_bytes','shared_capacity_bytes']]==[81920,16384,98304,98304]
out['historical_resource7']='PASS_3_DTC_ARMS_80KIB_PLUS_REAL16KIB_SIDE_ARRAY_LOGICALTAG_ZERO_DATA_NOT_AREA'
out['optional3070']='NOT_SELECTED_ZERO_RUNS; conditional maximum3, not required matrix. Bounded primary/derived evidence closed; no supported modernDTC legal organization to justify extension.'
(P/'final_closure_v1/SOURCE_POLICY_ORDERING_AND_PRESERVATION_V2.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
