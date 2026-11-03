"""Pure/private Host tests. No model/native/real registry mutation."""
import ast,copy,gzip,hashlib,importlib.util,json,os,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H/'runtime';V=H.parent;J=V.parents[2]
sys.path.insert(0,str(R))
import mode_contract as mc
import mode_aware_terminal as parser
import ep_perf_native_wv_modes_draft as eng
import ep_perf_frontend as front
from bind_highclock_specs import bind
T=H/'private_CPU';T.mkdir(exist_ok=True)
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def put(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True));return ref(p)
real_reg=eng.read(eng.REG);reg=copy.deepcopy(real_reg);eng.ROOT=T;eng.authority=lambda:(reg,{})
user=T/'control/USER_REQUEST.txt';user.parent.mkdir(exist_ok=True);user.write_text('TEST_ONLY_NO_USER_SCIENTIFIC_AUTHORIZATION')
auth=put(T/'TEST_ONLY_AUTH.json',dict(goal=eng.GOAL,user_request_ref=ref(user),TEST_ONLY=True))
q=dict(budget=6,remaining=6,consumed={},admitted_specs={},runtime_versions={},authorization_ref=auth);reg['registered_future_requests'][eng.GOAL]=q
source=mc.reference()['source_identity'];geometry=dict(slices=64,sets=32,ways=8,line_bytes=128)
evidence={n:ref(V/n)for n in ['NEW_SOURCE_AND_ELF_QUALIFICATION.json','WHOLE_TU_AND_ARCHIVE_AUDIT.json','cpu/CPU_PROTOCOL_AND_FREQUENCY_MATRIX.json','cpu/NEW_SOURCE_RO_MODE_CPU_MATRIX.json']}
sourceq=put(T/'TEST_ONLY_SOURCEQ.json',dict(schema='EP_MAIN_NEW_SOURCE_CC_CAM_CPU_QUALIFICATION_V1',status='MAIN_REVIEWED_NEW_SOURCE_CPU_AND_WHOLE_TU_QUALIFIED_NOT_APP_ACCEPTED',approved_by='EP-MAIN',source_identity=source,geometry=geometry,modes_qualified=['F','S'],application_acceptance_inherited=False,evidence_refs=evidence,TEST_ONLY=True))
modeq=put(T/'TEST_ONLY_MODEQ.json',dict(schema='EP_MAIN_NEW_SOURCE_CC_CAM_S_F_MODE_CPU_QUALIFICATION_V1',status='MAIN_REVIEWED_NEW_SOURCE_S_F_CPU_PASS_NOT_APPLICATION',approved_by='EP-MAIN',source_identity=source,geometry=geometry,modes_qualified=['F','S'],application_permission=False,evidence_refs=evidence,TEST_ONLY=True))
inputid='ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc'
loader=put(T/'TEST_ONLY_NEW_RO_LOADER_REBIND.json',dict(status='MAIN_REVIEWED_NEW_SOURCE_VECTOR_RO_LOADER_BINDING_PASS',source_identity=source,input_identity_sha256=inputid,evidence_refs=evidence,TEST_ONLY=True))
oldF=eng.read(J/'cases/EP_PERF_VECTOR4M_F_REF_V1/control/FROZEN_SPEC.json');ro=mc.exact(oldF['ro_qualification_ref']);ro.update(source_identity=source,new_source_loader_audit_ref=loader,TEST_ONLY=True);roq=put(T/'TEST_ONLY_NEW_ROQ.json',ro)
modules=[ref(p)for p in R.rglob('*')if p.is_file()];hostq=put(T/'TEST_ONLY_HOSTQ.json',dict(schema='EP_MAIN_NEW_SOURCE_CC_CAM_HIGH_CLOCK_HOST_QUALIFICATION_V1',status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',approved_by='EP-MAIN',source_identity=source,geometry=geometry,modes_qualified=['F','S'],cohorts_qualified=sorted(r['cohort']for r in mc.family_scope()['points']),modules=modules,evidence_refs=evidence,TEST_ONLY=True))
elig=put(T/'TEST_ONLY_INPUT_REBIND.json',dict(status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',source_identity=source,input_identity_sha256=inputid,modes_qualified=['S','F'],ordered_kernel_identity=mc.exact(oldF['input_binding_ref'])['ordered_kernel_identity'],TEST_ONLY=True))
oldprefix=J/'execution_performance_first_20261103_v1'
specs=[];by={};controls=[]
def check(name,fn,reject=False,contains=None):
 try:v=fn();ok=not reject;error=None
 except Exception as ex:v=None;error=type(ex).__name__+':'+str(ex);ok=reject and(contains is None or contains in error)
 controls.append(dict(label=name,PASS=ok,error=error));assert ok,controls[-1];return v
for f in sorted((H/'drafts').glob('*.json')):
 s=eng.read(f);bindings=dict(source_qualification_ref=sourceq,mode_cpu_qualification_ref=modeq,host_qualification_ref=hostq,eligibility_ref=elig,ro_qualification_ref=roq,resource_module_ref=ref(oldprefix/'tools/resources_service.py'),resource_policy_ref=ref(oldprefix/'agent_d/RESOURCE_POLICY_CANDIDATE.json'),authorization_ref=auth,native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt'))
 s=bind(s,bindings);p=T/'cases'/s['cohort']/'control/FROZEN_SPEC.json';put(p,s);q['admitted_specs'][s['cohort']]=ref(p)['sha256'];q['runtime_versions'][s['host_engine_ref']['sha256']]=dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']);specs.append(s);by[s['cohort']]=s
for s in specs:
 check(s['cohort']+'_static',lambda s=s:eng.formal_mode_contract(s));check(s['cohort']+'_exact_history',lambda s=s:mc.need(mc.history_for(s)['profile_semantics']['effective_options']==s['expected_effective_options'],'history drift'))
 if s['mode']=='S':check(s['cohort']+'_fair_pair',lambda s=s:mc.validate_fair_pair(s,by[s['same_background_peer_cohort']]))
for mode in ['S','F']:
 case=f'EP_PERF_CC_CAM_VECTOR4M_{mode}_850_V1';check(case+'_fresh850_no_accepted_anchor',lambda case=case:eng.spec_for(case))
case='EP_PERF_CC_CAM_VECTOR4M_S_1275_V1';reviewpath=T/'control/NEW_SOURCE_850_PAIR_MAIN_REVIEW_REF.json'
if reviewpath.exists():reviewpath.unlink()
check('1275_missing_new850_rejected',lambda:eng.spec_for(case),True)
# Fictional authority records exercise gating ONLY; never adopt or call these measured cycles.
def accept_fixture(mode,mhz,cycles):
 case=f'EP_PERF_CC_CAM_VECTOR4M_{mode}_{mhz}_V1';s=by[case];uid='TEST_ONLY_'+mode+'_'+str(mhz);point=put(T/'TEST_ONLY_POINTS'/(case+'.json'),dict(status='EP_FULL_PERF_APPLICATION_ACCEPTED',cohort=case,mode=mode,uuid=uid,hardware_drained=True,cycles=cycles,source_identity=source,input_identity_sha256=inputid,spec_ref=ref(T/'cases'/case/'control/FROZEN_SPEC.json'),TEST_ONLY=True,NOT_PERFORMANCE=True))
 arcsha='a'*64;receipt=put(T/'TEST_ONLY_ARCHIVES'/(case+'.json'),dict(status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS',cohort=case,uuid=uid,source_keep=True,archive_ref=dict(path='/root/share/mnt164/TEST_ONLY_NOT_AN_ACTUAL_ARCHIVE/'+case,sha256=arcsha),native_restores=[dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',archive_sha256=arcsha,restore_label=l)for l in ['FIRST','INDEPENDENT']],TEST_ONLY=True))
 q['consumed'][case]=dict(state='CLOSED_ACCEPTED',uuid=uid,accepted_point_ref=point,archive_receipt_ref=receipt);q['remaining']=q['budget']-len(q['consumed']);return point,receipt
for mode,c in [('S',60000),('F',61000)]:accept_fixture(mode,850,c)
baseline_review=dict(schema='EP_MAIN_CC_CAM_NEW_SOURCE_850_PAIR_ACCEPTANCE_REVIEW_V1',status='MAIN_REVIEWED_NEW_SOURCE_850_PAIR_ACCEPTED_ARCHIVED',source_identity=source,input_identity_sha256=inputid,accepted_point_refs={m:q['consumed'][f'EP_PERF_CC_CAM_VECTOR4M_{m}_850_V1']['accepted_point_ref']for m in ['S','F']},archive_receipt_refs={m:q['consumed'][f'EP_PERF_CC_CAM_VECTOR4M_{m}_850_V1']['archive_receipt_ref']for m in ['S','F']},TEST_ONLY=True)
br=put(T/'TEST_ONLY_BASELINE_REVIEW.json',baseline_review);put(reviewpath,br)
for mode in ['S','F']:check('1275_after_closed850_'+mode,lambda mode=mode:eng.spec_for(f'EP_PERF_CC_CAM_VECTOR4M_{mode}_1275_V1'))
for mode in ['S','F']:accept_fixture(mode,1275,59000 if mode=='S' else 60000)
case1700='EP_PERF_CC_CAM_VECTOR4M_S_1700_V1';rp=T/'control/conditional_release'/(case1700+'.json')
if rp.exists():rp.unlink()
check('1700_missing_explicit_release',lambda:eng.spec_for(case1700),True)
def criterion_record():return dict(status='MAIN_REVIEWED_CC_CAM_1700_EXTENSION_CRITERION_PASS',source_identity=source,input_identity_sha256=inputid,accepted_1275_point_refs={m:q['consumed'][f'EP_PERF_CC_CAM_VECTOR4M_{m}_1275_V1']['accepted_point_ref']for m in ['S','F']},archive_1275_receipt_refs={m:q['consumed'][f'EP_PERF_CC_CAM_VECTOR4M_{m}_1275_V1']['archive_receipt_ref']for m in ['S','F']},cpu1700_ref=ref(V/'cpu/CPU_PROTOCOL_AND_FREQUENCY_MATRIX.json'),TEST_ONLY=True)
def release_both():
 cr=put(T/'TEST_ONLY_1700_REVIEW.json',criterion_record())
 for m in ['S','F']:
  case=f'EP_PERF_CC_CAM_VECTOR4M_{m}_1700_V1';put(T/'control/conditional_release'/(case+'.json'),dict(status='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL',cohort=case,request_id=eng.GOAL,spec_sha256=q['admitted_specs'][case],family_stage='CONDITIONAL1700',criterion_review_ref=cr,TEST_ONLY=True))
release_both();check('1700_less_than3pct_rejected',lambda:eng.spec_for(case1700),True,'1.03')
accept_fixture('S',1275,57000);release_both()
for mode in ['S','F']:check('1700_approved_exact_pair_'+mode,lambda mode=mode:eng.spec_for(f'EP_PERF_CC_CAM_VECTOR4M_{mode}_1700_V1'))
# Explicit missing, stale and cross-source precursor checks.
row=q['consumed']['EP_PERF_CC_CAM_VECTOR4M_F_850_V1'];saved=copy.deepcopy(row);row['state']='ACCEPTED_PENDING_ARCHIVE';check('1275_requires_archive_closed',lambda:eng.spec_for(case),True);row.clear();row.update(saved)
ar=eng.read(row['archive_receipt_ref']['path']);orig=copy.deepcopy(ar);ar['native_restores'][1]['restore_label']='FIRST';row['archive_receipt_ref']=put(Path(row['archive_receipt_ref']['path']),ar);check('1275_reject_duplicate_restore',lambda:eng.spec_for(case),True);row['archive_receipt_ref']=put(Path(row['archive_receipt_ref']['path']),orig)
s0=by['EP_PERF_CC_CAM_VECTOR4M_S_850_V1']
def mut(fn):s=copy.deepcopy(s0);fn(s);return s
for label,fn in [('oldSource78',lambda s:s['source_identity'].update(core_source_commit='78f4b59e865b136eede74df74c44c210f5b4ca04')),('Source1e07',lambda s:s['source_identity'].update(core_source_commit='1e07b263ca0879798387d2a712914a914f298775')),('ELF_old',lambda s:s['source_identity'].update(binary_sha256=oldF['source_identity']['binary_sha256'])),('lib_old',lambda s:s['source_identity'].update(archive_sha256=oldF['source_identity']['archive_sha256'])),('profile_oldaccepted',lambda s:s.update(profile='REF32x8_L100')),('inherit_oldapp',lambda s:s.update(old_application_acceptance_inherited=True)),('wrongpeer',lambda s:s.update(same_background_peer_cohort=case1700)),('wronggeometry',lambda s:s['geometry'].update(ways=4)),('clockArbitrary',lambda s:s['expected_effective_options'].update({'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:2000.0'})),('clockCORE',lambda s:s['expected_effective_options'].update({'-gpgpu_clock_domains':'2264.0:1132.0:1132.0:850.0'})),('latency60',lambda s:s['expected_effective_options'].update({'-dram_latency':'60'})),('MissQ256',lambda s:s['expected_effective_options'].update({'-gpgpu_cache:dl2':'S:32:128:8,L:B:m:L:P,A:128:1,256:0,32'})),('D1024',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_descriptor_pool_size':'1024'})),('P2',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_bank_ops':'2'})),('observer',lambda s:s['observer_env'].update(EPL2_DETACH_DIAG='1')),('modeWV',lambda s:s.update(mode='WV_ZERO_RO')),('unknowncohort',lambda s:s.update(cohort='EP_PERF_CC_CAM_VECTOR6M_S_850_V1')),('wrongInput',lambda s:s.update(input_identity_sha256='0'*64)),('typedM',lambda s:s.update(M=0)),('missingOverlay',lambda s:s.update(ordered_configs=s['ordered_configs'][:-1]))]:check('NEG_'+label,lambda fn=fn:eng.formal_mode_contract(mut(fn)),True)
f=copy.deepcopy(by['EP_PERF_CC_CAM_VECTOR4M_F_850_V1']);f['ro_qualification_ref']=oldF['ro_qualification_ref'];check('F_oldSourceRO_certificate_rejected',lambda:eng.formal_mode_contract(f),True)
f=copy.deepcopy(by['EP_PERF_CC_CAM_VECTOR4M_F_850_V1']);f['ro_qualification_ref']=None;check('F_missing_newSource_RO_rejected',lambda:eng.formal_mode_contract(f),True)
oldq=eng.read(sourceq['path']);oldq['status']='EXACT_ACCEPTED_SOURCE_CPU_EVIDENCE_REUSED_NOT_NEW_APP_ACCEPTED';bad=put(T/'TEST_ONLY_BAD_SOURCE_ALIAS.json',oldq);check('newS_cannot_call_Source_accepted',lambda:eng.formal_mode_contract(dict(s0,source_qualification_ref=bad)),True)
# Full terminal CPU parser. S synthetic; F artificial transformed<=6MiB existing raw, clearly NOT a run/result.
_,math=parser.numeric_math();parse,_=parser.numeric_math();oldbuilder=J/'research/implementation_performance_v2_20261029_v1/agent_b/test_full_parser_synthetic_v2.py';tree=ast.parse(oldbuilder.read_text());ns=dict(parse=parse,reasons=parse.__globals__['REASONS']);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['wire','build']],type_ignores=[]),'trusted_existing_synthetic_builder','exec'),ns)
cache=None;fixtures=T/'TEST_ONLY_TERMINALS';fixtures.mkdir(exist_ok=True)
for s in specs:
 mode=s['mode'];oldcase=f'EP_PERF_VECTOR4M_{mode}_REF_V1';oldrow=real_reg['registered_future_requests'][eng.FRONTEND_GOAL]['consumed'][oldcase]
 if mode=='S':ns['binding']=mc.exact(s['input_binding_ref']);ns['bundle']=mc.exact(oldrow['validation_ref']);raw=ns['build'](s)
 else:
  if cache is None:
   point=mc.exact(oldrow['accepted_point_ref']);assert point['raw_stream_receipt']['raw_bytes']<6<<20
   with gzip.open(point['raw_stream_receipt']['path'],'rt')as inp:cache=inp.read()
  raw='# TEST_ONLY_ARTIFICIAL_NEW_SOURCE_BANNER_AND_CLOCK_NOT_PERFORMANCE\n'+cache.replace('78f4b59e865b136eede74df74c44c210f5b4ca04',source['core_source_commit']).replace('gpgpu-sim_git-commit-78f4b59','gpgpu-sim_git-commit-862376f').replace('1132.0:1132.0:1132.0:850.0',s['expected_effective_options']['-gpgpu_clock_domains'])
 fp=fixtures/(s['cohort']+'.TEST_ONLY.log');fp.write_text(raw);qual=dict(formal_mode=mode,mode_contract_ref=s['mode_contract_ref'],validation_module_ref=s['validation_module_ref'],mode_cpu_qualification_ref=s['mode_cpu_qualification_ref'],source_identity=source)
 value=check(s['cohort']+'_full_terminal_positive',lambda s=s,fp=fp,qual=qual:parser.validate_case(fp,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
 check(s['cohort']+'_parser_cannot_accept',lambda value=value:mc.need(value['scientific_acceptance_granted']is False,'pure parser accepted'))
 if mode=='F'and mc.family_row(s)['DRAM_MHz']==1275:
  badfile=fixtures/'NEG_OLD_SOURCE_BANNER.log';badfile.write_text(raw.replace('862376f','78f4b59'));check('full_parser_old_source_banner_rejected',lambda:parser.validate_case(badfile,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True)
  badfile2=fixtures/'NEG_OLD_CLOCK.log';badfile2.write_text(raw.replace('1132.0:1132.0:1132.0:1275.0','1132.0:1132.0:1132.0:850.0'));check('full_parser_clock_mismatch_rejected',lambda:parser.validate_case(badfile2,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True)
# Additional real terminal rejection and gzip controls on the same newSource candidate.
s=by['EP_PERF_CC_CAM_VECTOR4M_F_1275_V1'];fp=fixtures/(s['cohort']+'.TEST_ONLY.log');raw=fp.read_text();qual=dict(formal_mode='F',mode_contract_ref=s['mode_contract_ref'],validation_module_ref=s['validation_module_ref'],mode_cpu_qualification_ref=s['mode_cpu_qualification_ref'],source_identity=source)
mutations=[('missing_exit',lambda r:r.replace('GPGPU-Sim: *** exit detected ***','')),('missing_B0_invariant',lambda r:'\n'.join(l for l in r.split('\n')if not l.startswith('EPL2B0V1|INVARIANT|'))),('descriptor_live',lambda r:r.replace('descriptor_used=0','descriptor_used=1')),('WB_live',lambda r:r.replace('wb_live=0','wb_live=1')),('wrong_layout_mode',lambda r:r.replace('mode=2|wbuf=16','mode=1|wbuf=16')),('missing_option',lambda r:'\n'.join(l for l in r.split('\n')if not l.startswith('-gpgpu_dram_scheduler '))),('instruction_count',lambda r:__import__('re').sub(r'gpu_tot_sim_insn\s*=\s*\d+','gpu_tot_sim_insn = 1',r)),('CTA_count',lambda r:__import__('re').sub(r'gpu_tot_issued_cta\s*=\s*\d+','gpu_tot_issued_cta = 1',r)),('extra_optional_ET',lambda r:r+'\nEPETV1|anything\n'),('MS_hist_wrong',lambda r:r.replace('hist_log2='+','.join(['0']*65),'hist_log2=0'))]
for label,fn in mutations:
 bad=fixtures/('NEG_ADDED_'+label+'.TEST_ONLY.log');changed=fn(raw)
 if changed==raw:
  controls.append(dict(label='NEG_'+label+'_NOT_AVAILABLE_IN_REUSED_FIXTURE',PASS=True,scope='NOT_TESTED_NOT_CLAIMED'));continue
 bad.write_text(changed);check('full_terminal_NEG_'+label,lambda bad=bad:parser.validate_case(bad,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True)
gz=fixtures/'F1275.TEST_ONLY.log.gz'
with gzip.open(gz,'wb')as out:out.write(raw.encode())
v=check('full_terminal_lossless_gzip_positive',lambda:parser.validate_case(gz,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
check('gzip_logical_hash_equal',lambda:mc.need(v['raw_logical_sha256']==hashlib.sha256(raw.encode()).hexdigest(),'gzip census drift'))
for old_core in ['1093d2629e3d6a9130ba25b9dd119b6f3e16c092','9243f769620653f2a9d4df5599e9581e9dae6067','d010911e3174a3764791183cd108fe4664ba8731','11c02df1034112013523429894f1f931323adbef']:
 check('historical_Core_not_wildcard_'+old_core[:7],lambda old_core=old_core:eng.formal_mode_contract(mut(lambda x:x['source_identity'].update(core_source_commit=old_core))),True)
check('shared_admission_all_three_writes',lambda:mc.need((R/'ep_perf_native_wv_modes_draft.py').read_text().count("with locked(ROOT.parent/'control/ADMISSION.lock'):")==2 and (R/'ep_perf_archive.py').read_text().count("with locked(ROOT.parent/'control/ADMISSION.lock'):")==1,'shared lock scope'))
result=dict(schema='EP_NEW_SOURCE_CC_CAM_HIGH_CLOCK_HOST_CPU_CONTROLS_V1',status='PASS_PRIVATE_ENGINEERING_NOT_NATIVE_OR_APP_QUALIFIED',passed=len(controls),total=len(controls),controls=controls,source_identity=source,numeric_math=math,initial850_no_accepted_anchor_proven=True,app_NI='NOT_MEASURED',extra_observer_NI_points_proposed=0,science_launches=0,native_calls=0,real_registry_writes=0,TEST_ONLY_stage_rows_never_adopt_as_real=True)
(H/'HOST_CPU_CONTROLS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=result['status'],passed=len(controls))))
