import pathlib,json,hashlib,subprocess,os,resource,importlib.util,sys
sys.dont_write_bytecode=True
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');C=V/'agents/C_codesign_v1';D=V/'agents/D_independent_review_v1';checks=[]
EXPECTED_C_MANIFEST='1a8415b1946589057b482d0a39b82be1b94b344c1a6202898f655e818ed1a002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
mf=C/'MANIFEST.json';ck('C frozen final manifest',sha(mf)==EXPECTED_C_MANIFEST)
for x in json.loads(mf.read_text())['files']:
 p=C/x.get('path',x.get('relative_path',x.get('name')));ck('C member '+str(p.relative_to(C)),sha(p)==x['sha256'])
matrix=json.loads((C/'C_RESOURCE_CODESIGN_MATRIX.json').read_text());authority=json.loads(pathlib.Path(matrix['authority']['path']).read_text());ck('Frozen8 authority exact',sha(pathlib.Path(matrix['authority']['path']))==matrix['authority']['sha256']=='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1')
build=matrix['frozen_build'];ck('Actual frozen simulator SHA',sha(pathlib.Path(build['binary_path']))==build['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d');ck('Actual frozen libcudart SHA',sha(pathlib.Path(build['core_library_path']))==build['core_library_sha256']=='694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56')
for k in ['source_BUILD_PROFILE','upstream_build_receipt']:
 pin=build[k];ck('Build receipt '+k,sha(pathlib.Path(pin['path']))==pin['sha256'])
for k,val in [('SM_count',64),('L2_capacity_MiB',10),('DRAM_MHz',850),('core_commit','9eedb3131937748f0492fa83aad37d3691118d70'),('framework_commit','02775fd795cde5aae1480d81cee6eb481d0a08f4')]:ck('Frozen build '+k,build[k]==val)
ck('Exactly16 candidates',len(matrix['candidates'])==16);ck('No created requestsUUIDmodels',matrix['new_UUIDs']==matrix['new_model_starts']==matrix['new_scientific_requests']==0)
byprogram={x['population']['program']:x for x in authority['inputs']};seen=set();configseen=set();physicalmap={768:[],1024:[]};qual=[]
module_spec=importlib.util.spec_from_file_location('D_REVIEW_ONLY_C_COMBO_VALIDATOR',C/'combo_shape_and_capacity_strict.py');mod=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(mod)
for row in matrix['candidates']:
 ident=row['program']+row['profile'];p=row['physical_lines'];physicalmap[p].append(row['input_digest']);a=byprogram[row['program']];base=next(z for z in a['P0_references'] if z['source_cell']=='DH');ck('Exact programinput '+ident,row['input_digest']==a['population']['input_digest']);ck('Onlynewplannednotconsumed '+ident,row['model_started'] is False and row['new_native_UUID'] is None and row['new_request'] is None and row['new_scientific_budget_registered'] is False and row['proposed_native_cohort_registered'] is False)
 ck('No invented performance '+ident,all(row[k] is None for k in ['performance_cycles','S_combo','CH_P0_over_newDH','J']))
 expect=dict(base['effective_options']);expect['-gpgpu_dtc_l1_physical_lines']=[str(p)];expect['-gpgpu_dtc_l1_oo_pib_entries']=['192'];ck('Exact270 P0 only2flags '+ident,len(row['expected_effective_options'])==270 and row['expected_effective_options']==expect);ck('ActivePIB lowercreate coupling '+ident,row['active_OO_PIB_entries']==row['effective_lower_create_queue_bound']==192);ck('Expectedinputscope '+ident,row['expected']==base['expected'] and row['input_binding']==base['input_binding'])
 for label in ['CH_P0_reference','DH_P0_reference']:
  ref=row[label];rp=pathlib.Path(ref['source_RESULT_path']);ck('P0 RESULT SHA '+ident+label,sha(rp)==ref['source_RESULT_sha256']);rr=json.loads(rp.read_text());ck('P0 accepted exact identity '+ident+label,ref['accepted'] and rr['proof']['performance_accepted'] and rr['cycles']==ref['cycles'] and ref['input_digest']==row['input_digest'])
 for label in ['V1_physical_reference','V1_PIB_reference']:
  r=row[label]
  if r['accepted']:
   pin=r['source_RESULT'];ck('V1 accepted source SHA '+ident+label,sha(pathlib.Path(pin['path']))==pin['sha256']);res=json.loads(pathlib.Path(pin['path']).read_text());ck('V1 accepted integercycles '+ident+label,res['cycles']==r['cycles'] and res['proof']['performance_accepted'] is True)
  else:ck('MissingV1 notpatched by inventedcycles '+ident+label,r['cycles'] is None)
 for pin in row['configs']+[row['input_binding']]:
  if pin['path'] not in configseen:configseen.add(pin['path']);ck('Configbinding file '+pin['path'],sha(pathlib.Path(pin['path']))==pin['sha256'])
 ck('Independent C shape validator '+ident,mod.validate_spec(row,check_files=False)['status']=='VALID_COMBO_CONFIGURATION_NO_EXECUTION_AUTHORITY');seen.add((row['input_digest'],row['profile']))
 if row['profile'] not in {z['profile'] for z in qual}:
  new,binding=mod.transformed_source(row);old=pathlib.Path(binding['legacy_source_path']).read_bytes();anchor=mod.ANCHOR.encode();replacement=('0 <= value("oo_physical_allocated") <= '+str(p)+' * 64, "physical_'+str(p)+'_per_SM_capacity"').encode();ck('Onlylegacy terminal gauge patch '+ident,new.replace(replacement,anchor,1)==old and binding['all_other_legacy_parser_bytes_unchanged']);qual.append(binding)
ck('Samefixed8inputs bothuniformprofiles',set(physicalmap[768])==set(physicalmap[1024]) and len(set(physicalmap[768]))==8 and len(seen)==16)
def restricted():os.nice(19);os.sched_setaffinity(0,{132});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
private=D/'private_cpu_C_replay';private.mkdir(exist_ok=False);exe=private/'codesign_cpu';args=['g++','-std=c++17','-O1','-I/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim',str(C/'codesign_lifecycle_cpu.cpp'),'-o',str(exe)];compiled=subprocess.run(args,preexec_fn=restricted,capture_output=True,text=True,timeout=60);ck('C originalheader independentcompile',compiled.returncode==0);(private/'compile.stderr').write_text(compiled.stderr);r=subprocess.run([str(exe)],preexec_fn=restricted,capture_output=True,text=True,timeout=60);ck('C actual independentlifecycle replay',r.returncode==0);cases=[json.loads(z) for z in r.stdout.splitlines() if z.strip()];expected=json.loads((C/'CPU_LIFECYCLE_QUALIFICATION.json').read_text())['positive_cases'];ck('C exact19 directed results',cases==expected and len(cases)==19)
negative=[]
for arg in ['duplicate_return','stale_generation']:
 r=subprocess.run([str(exe),arg],preexec_fn=restricted,capture_output=True,text=True,timeout=60);ck('Originalassert rejects '+arg,r.returncode==-6);negative.append({'case':arg,'returncode':r.returncode,'expected_SIGABRT':True})
o={'checks':checks,'C_manifest':{'path':str(mf),'sha256':sha(mf)},'source_matrix_sha256':sha(C/'C_RESOURCE_CODESIGN_MATRIX.json'),'strict_qualified_profile_bindings':qual,'CPU_replayed_positive_cases':cases,'CPU_replayed_negative_assertion_cases':negative,'CPU_policy':{'nice':19,'CPU':132,'max_AS':2*1024**3,'max_seconds_each':60,'max_parallel':1},'compile_argv':args,'private_binary_sha256':sha(exe),'scope':'Frozen16 Physical×PIB candidate contract/config/input/P0/V1 singlefactors/actual binary-library SHAs and originalheader bounded lifecycle qualification only. Newcombo actual270echo/lifecycle/fullarchive/native restore remain future scientific qualifications. Capacity adapter changes only terminal allocation gauge bound; no fabricated PIB pressure/peak counters, no numerical/coherence/complete capture or PPA certification.','actual_new_models':0,'native_registration_or_budget_writes':0,'production_Core_or_V1_changes':0}
p=D/'INDEPENDENT_C_MATRIX_AND_CPU_REPLAY_REVIEW.json';assert not p.exists();p.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'positive_cases':len(cases),'negative_cases':len(negative),'sha256':sha(p)}))
