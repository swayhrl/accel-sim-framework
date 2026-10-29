"""Bounded draft binding only; no registry/native/controller import or launch."""
import argparse,copy,hashlib,importlib.util,json,pathlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent;H=ROOT/'host_candidate'
sp=importlib.util.spec_from_file_location('bound_t3_contract',H/'mode_contract.py');mc=importlib.util.module_from_spec(sp);sp.loader.exec_module(mc)
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest())
def put(p,x):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n');return ref(p)
ap=argparse.ArgumentParser();ap.add_argument('--review-refs');args=ap.parse_args();reviews=mc.read(args.review_refs)if args.review_refs else{};required=['source_qualification_ref','mode_cpu_qualification_ref','ro_qualification_ref','host_qualification_ref','eligibility_ref'];actual=all(k in reviews for k in required)
if actual:
 for k in required:
  r=reviews[k];q=mc.exact(r);mc.need(not q.get('TEST_ONLY_SYNTHETIC_APPROVAL',False)and 'TEST_ONLY'not in r['path']and '/sandbox_controls/'not in r['path'],'synthetic approval cannot qualify realMain draft')
parent=mc.read(H/'LEGACY_PARENT_BACKGROUND.json');new=mc.reference();out=ROOT/('main_review_bound_drafts'if actual else'UNREVIEWED_EXACT_DRAFTS');out.mkdir(exist_ok=True);points=[]
modules={k:ref(H/name)for k,name in [('host_engine_ref','ep_perf_native_wv_modes_draft.py'),('host_common_ref','ep_perf_common_v2.py'),('mode_contract_ref','mode_contract.py'),('validation_module_ref','mode_aware_terminal.py')]}
for profile in ['T3_PRIMARY_OFF','T3_DIAG_ON']:
 specs=[]
 for arm,mode in zip('ABC',mc.MODES):
  s=copy.deepcopy(parent);s.update(schema='EP_FULL_PERF_EXACT_SPEC_V1',goal=mc.GOAL,science_request_id=mc.REQUEST,cohort='EP_PERF_T3_CONV16X8_'+arm+'_'+mode+('_ON_V1'if profile=='T3_DIAG_ON'else'_OFF_V1'),mode=mode,M=True,T=mode!='F_MINUS_T',ordinary_ro_tag_relief=mode=='CORRECTED_F',observer_profile=profile,source_identity=new['source_identity'],binary_path=new['binary_path'],static_library_path=new['static_library_path'],source_worktrees=dict(core=new['core_path'],framework=new['framework_path']),old_application_acceptance_inherited=False,authorization_status='NO_NEW_SCIENTIFIC_START_AUTHORIZATION',registered=False)
  s['observer_env']={k:'0'for k in mc.HEAVY};s['observer_env']['EPL2_LIFE_WIRE']='SUMMARY_STAGE'
  if profile=='T3_DIAG_ON':s['observer_env'].update(EPL2_DETACH_DIAG='1',EPL2_TAGPRESSURE_DIAG='1')
  s['expected_effective_options'].update(mc.flags(mode));s.update(modules)
  cfg=out/(arm+'_'+profile+'.config');cfg.write_text(''.join(k+' '+v+'\n'for k,v in mc.flags(mode).items()));s['ordered_configs']=list(parent['ordered_configs'])+[ref(cfg)]
  s['pinned_files']={p:d for p,d in parent['pinned_files'].items()if '/common-lib/'in p or'/EP/env/lib/'in p or '/tools/bin/'in p or '/tools/lib/'in p}
  for p in H.rglob('*'):
   if p.is_file():s['pinned_files'][str(p)]=ref(p)['sha256']
  for k in required:s[k]=reviews[k]if actual else dict(path='NOT_MAIN_QUALIFIED_'+k,sha256='NOT_MAIN_QUALIFIED')
  s['postprocess_module_ref']={'path':'NOT_INSTALLED_NEW_SCOPE_POSTPROCESS_BINDING_REQUIRED','sha256':'NOT_QUALIFIED'}
  s['scientific_option_contract']=dict(legacy_count=282,actual_count=283,new_option=mc.CORRECTION)
  s['NI_contract']=dict(primary_OFF_can_match_only_same_mode_ON=True,Source5_same=True,fullApplicationNI='NOT_EXECUTED',strict_demand_NEW='NOT_INSTRUMENTED',later_UID_completion_chain='NOT_MEASURED')
  specs.append(s)
 matrix=dict(schema='EP_MAIN_EXACT_SAME_ELF_T3_BINDING_V1',source_identity=new['source_identity'],geometry=parent['geometry'],input_identity_sha256=parent['input_identity_sha256'],science_request_id=mc.REQUEST,arms={s['mode']:dict(cohort=s['cohort'],source_identity=s['source_identity'],observer_env=s['observer_env'],effective_options_sha256=mc.digest_value(s['expected_effective_options']))for s in specs});mr=put(out/(profile+'_MATRIX.json'),matrix)
 for s in specs:
  s['three_arm_matrix_ref']=mr;mc.check_background(s);mc.validate_matrix(s)
  if actual:mc.validate_static(s)
  sr=put(out/(s['cohort']+'.json'),s);points.append(dict(cohort=s['cohort'],mode=s['mode'],observer_profile=profile,spec_ref=sr,status='MAIN_CPU_ENGINEERING_REVIEW_BOUND_NOT_AUTHORIZED'if actual else'EXACT_SOURCE_BOUND_MAIN_QUALIFICATION_HOLD'))
result=dict(status='ALL6_REAL_MAIN_STATIC_BINDINGS_PASS_NOT_START_PERMISSION'if actual else'ALL6_EXACT_SOURCE_DRAFTS_MAIN_REVIEW_HOLD',actualMainreviews=actual,source_identity=new['source_identity'],points=points,primary_starts=3,NI_ON_conditional_starts=3,conditional_total=6,authorized=0,registered=0,consumed=0,fullnative_activation='NOT_INSTALLED; exactfreshbudget/userauthorization/newruntime/soleentryversion/postprocess+archivebindings required inStageII',real_review_refs=reviews if actual else None)
put(ROOT/('MAIN_REVIEW_BOUND_DRAFT_RECEIPT.json'if actual else'UNREVIEWED_DRAFT_RECEIPT.json'),result);print(json.dumps(dict(status=result['status'],points=6,authorized=0)))
