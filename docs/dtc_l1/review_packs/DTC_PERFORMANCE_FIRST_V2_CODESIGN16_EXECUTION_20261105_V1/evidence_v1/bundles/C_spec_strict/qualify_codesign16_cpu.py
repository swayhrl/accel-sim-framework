from pathlib import Path
import json,hashlib,gzip,re,types,copy,ast
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/C_spec_strict_v1');T=O/'runtime';checks=[]
def rd(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append({'check':n,'PASS':True})
def reject(n,f):
 try:f()
 except(AssertionError,KeyError,ValueError,TypeError):ck(n,True);return
 raise AssertionError(n)
def load(p):
 m=types.ModuleType('CPU_PRIVATE_'+Path(p).stem);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
cap=load(T/'perf16_capacity_strict.py');matrix=rd(O/'cpu_sandbox/control/MATRIX.fixed.json');dep=rd(O/'DEPENDENCY_PINS.json');refrows=rd(O/'cpu_sandbox/control/SPEC_BUILD_REFERENCE_TABLE.json')['rows']
for p in T.glob('*.py'):ast.parse(p.read_text());ck('AST_compile_'+p.name,True)
ck('exact16unique_program_cross_profiles',len(matrix['points'])==16 and len({x['cohort']for x in matrix['points']})==16 and len({x['input_digest']for x in matrix['points']})==8 and matrix['variant_counts']=={'PHYS768_OOPIB192_TAG64x8':8,'PHYS1024_OOPIB192_TAG64x8':8})
actualspecs=[]
for p in matrix['points']:
 f=O/'cpu_sandbox/control/specs'/(p['cohort']+'.json');s=rd(f);r=next(x for x in refrows if x['cohort']==s['cohort']);base=rd(r['source_baseline_spec']['path']);ck(s['cohort']+'_original2delta270',len(s['expected_options'])==270 and set(r['effective_option_delta'])=={'-gpgpu_dtc_l1_physical_lines','-gpgpu_dtc_l1_oo_pib_entries'});ck(s['cohort']+'_preserved_ROI_argv_build_env_runtime',s['expected']==base['expected']and s['runtime_files']==base['runtime_files']and s['original_environment']==base['original_environment']and s['native_simulator_argv'][0]==base['native_simulator_argv'][0]);ck(s['cohort']+'_exactmirrorSHA',sha(f)==p['spec_sha256']==sha(O/'cpu_sandbox/control'/(s['cohort']+'_SPEC.json')))
 for x in s['configs']:x['path']=str(O/'cpu_sandbox'/Path(x['path']).relative_to('/root/data/dtc_perf_first_v2_codesign16_20261105_v1'))
 s['input_binding_path']=str(O/'cpu_sandbox/control/input_bindings'/(s['input_digest']+'.json'));shape=cap.validate_spec(s);ck(s['cohort']+'_actualfiles_shape_cpu',shape['OO_PIB_entries']==192 and shape['effective_lower_create_queue_bound']==192);actualspecs.append(s)
 for x in s['runtime_files']:ck(s['cohort']+'_runtime_link_'+x['target'],(O/'cpu_sandbox'/x['target']).resolve()==Path(x['actual_realpath']).resolve())
# Only a CLOSED historical raw is read. Synthetic option echo edits exist in memory
# only; all parsed cycles remain a fixture, never a new scientific RESULT.
dr=dep['selected'][0]['DH_reference'];r=rd(dr['source_RESULT_path']);root=Path(dr['source_RESULT_path']).parents[1];i=rd(root/'control/qualification_ledger'/(r['cohort']+'.INTENT.json'));out=Path(i['output']);done=rd(root/'control/qualification_ledger'/(r['cohort']+'.DONE.json'));ck('historical_fixture_closed_natural_pinned',done['stop_reason']is None and done['launcher_wait_returncode']==0 and done['uuid']==i['uuid']==r['uuid']and sha(out/'raw.log.gz')==done['raw_sha256']);rawb=gzip.decompress((out/'raw.log.gz').read_bytes());ck('historical_closed_fixture_rawbodySHA',hashlib.sha256(rawb).hexdigest()==done['raw_uncompressed_sha256']);raw=rawb.decode();domain=rd(actualspecs[0]['input_binding_path'])['qualification'];population=[]
for profile,physical in [('PHYS768_OOPIB192_TAG64x8',768),('PHYS1024_OOPIB192_TAG64x8',1024)]:
 s=next(x for x in actualspecs if x['profile']==profile and x['program']=='2DCONV');text,n=re.subn(r'(?m)^(-gpgpu_dtc_l1_physical_lines\s+)640(\s+#.*)$',lambda m:m[1]+str(physical)+m[2],raw);ck(profile+'_single_physical_echo_fixture_edit',n==1);text,n=re.subn(r'(?m)^(-gpgpu_dtc_l1_oo_pib_entries\s+)128(\s+#.*)$',r'\g<1>192\2',text);ck(profile+'_single_PI_echo_fixture_edit',n==1)
 result,binding=cap.population_from_verified_closed_text(text,s,domain);ck(profile+'_real_pure_population_twoflag_fixture',result['cycles']==r['cycles']and result['effective_options']==s['expected_options']and binding['replacement_count']==1);population.append({'profile':profile,'status':'PASS_SYNTHETIC_OPTION_ECHO_FIXTURE_ONLY_NOT_NEW_PERFORMANCE','source_closed_RESULT':{'path':dr['source_RESULT_path'],'sha256':dr['source_RESULT_sha256']},'source_raw':{'path':str(out/'raw.log.gz'),'sha256':done['raw_sha256']},'binding':binding,'new_scientific_result_or_cycles_emitted':False})
 wrong=text.replace('-gpgpu_dtc_l1_oo_pib_entries                  192','-gpgpu_dtc_l1_oo_pib_entries                  128');reject(profile+'_wrong270runtime_echo_rejected',lambda:cap.population_from_verified_closed_text(wrong,s,domain))
 bad,n=re.subn(r'(?m)^(DTC_L1_oo_pib_occupancy\s*=\s*)0\s*$',r'\g<1>1',text);ck(profile+'_terminalPIBfixture_target_found',n>0);reject(profile+'_terminalPIB_notdrained_rejected',lambda:cap.population_from_verified_closed_text(bad,s,domain))
 bad,n=re.subn(r'(?m)^(DTC_L1_lower_credit_released\s*=\s*)(\d+)\s*$',lambda m:m[1]+str(int(m[2])+1),text);ck(profile+'_lowerconservation_fixture_found',n>0);reject(profile+'_lowerconservation_rejected',lambda:cap.population_from_verified_closed_text(bad,s,domain))
 # The pure parser may accept physical occupancy >old640 only when all K0
 # conservation terms are deliberately adjusted consistently in this fixture.
 bad,n=re.subn(r'(?m)^(DTC_L1_oo_physical_allocated\s*=\s*)(\d+)\s*$',lambda m:m[1]+str(physical*64+1),text);ck(profile+'_capacitygauge_fixture_found',n>0);reject(profile+'_configured_capacity_overbound_rejected',lambda:cap.population_from_verified_closed_text(bad,s,domain))
 for field,value in [('profile','OO_PIB192'),('cell','CH'),('input_digest','0'*64),('core_commit','0'*40)]:
  badspec=copy.deepcopy(s);badspec[field]=value;reject(profile+'_badshape_'+field,lambda b=badspec:cap.validate_spec(b,False))
# Immutable old helper and original AG6 retained; only private helper schema fix.
old=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1/agents/C_codesign_v1/combo_shape_and_capacity_strict.py');original=old.read_text();current=(T/'perf16_capacity_strict.py').read_text();oldtail=" assert result['effective_options']==expected\n return result,binding";newtail=" # The unchanged pure population reader verifies all270 actual echo values\n # before returning, but its result schema omits this field. Add the already\n # validated vector here; do not pretend the old reader returned it.\n result=dict(result,effective_options=expected)\n return result,binding";ck('only_helper_returnschema_forward_fix',current.replace(newtail,oldtail,1)==original and sha(old)=='c4f91c12bf7ca27c895099dbbb1f87e230f53000c59f5356e1f5348eb25a2415');ck('original_ag6_bytes_unchanged',sha(cap.LEGACY_PATH)==cap.LEGACY_SHA)
(O/'CPU_POPULATION_FIXTURE_QUALIFICATION.json').write_text(json.dumps({'schema':'DTC_PERFV2_CODESIGN16_SPEC_STRICT_CPU_QUALIFICATION_V1','status':'PASS_CPU_ONLY_NOT_SCIENCE_ACCEPTANCE','checks':checks,'count':len(checks),'synthetic_population_fixtures':population,'scientific_registrations':0,'native_prepare_or_model_starts':0,'runtime_qualification':'NOT_RUN_REQUIRES_ROOT_FORMAL_SCIENCE_DISPATCH','source_shape_template_sha256':sha(old),'runtime_capacity_adapter_sha256':sha(T/'perf16_capacity_strict.py')},indent=2)+'\n');print('CPU_POPULATION_PASS',len(checks))
