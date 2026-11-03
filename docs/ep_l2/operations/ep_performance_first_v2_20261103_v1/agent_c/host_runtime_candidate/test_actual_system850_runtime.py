"""Private actual engine+whole-parser controls; never register/launch real science."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,importlib.util,time,uuid
H=Path(__file__).resolve().parent;C=H.parent;R=H/'runtime';J=C.parents[2]
sys.path.insert(0,str(R));sys.path.insert(0,str(H))
import mode_contract as mc,mode_aware_terminal as parser,ep_perf_native_wv_modes_draft as eng,ep_perf_frontend as front
from bind_system850_specs import bind
T=H/'TEST_ONLY_PRIVATE'/str(uuid.uuid4());T.mkdir(parents=True)
def ref(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def put(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True));return ref(p)
def check(label,fn,reject=False,match=None):
 try:v=fn();ok=not reject;err=None
 except Exception as e:v=None;err=type(e).__name__+':'+str(e);ok=reject and(match is None or match in err)
 rows.append(dict(label=label,PASS=ok,error=err))
 if not ok:raise AssertionError(rows[-1])
 return v
rows=[];real=mc.read(eng.REG);reg=copy.deepcopy(real);eng.ROOT=T;eng.authority=lambda:(reg,{})
user=T/'control/USER_REQUEST.txt';user.parent.mkdir(exist_ok=True);user.write_text('TEST_ONLY_NOT_REAL_AUTHORIZATION')
auth=put(T/'TEST_ONLY_AUTH.json',dict(goal=eng.GOAL,user_request_ref=ref(user),TEST_ONLY=True,scientific_permission=False))
q=dict(budget=12,remaining=12,consumed={},admitted_specs={},runtime_versions={},authorization_ref=auth);reg['registered_future_requests'][eng.GOAL]=q
profiles=sorted({'PFV2_SYSTEM850_'+r['family']for r in mc.family_scope()['points']})
cpuq=put(T/'TEST_ONLY_MODE_CPU.json',dict(schema='EP_MAIN_SOURCE78_SYSTEM850_FORMAL_MODE_CPU_QUALIFICATION_V1',status='MAIN_REVIEWED_SOURCE78_SYSTEM850_CPU_PASS_NOT_APPLICATION',approved_by='EP-MAIN',TEST_ONLY=True,source_identity=mc.reference()['source_identity'],modes_qualified=['S','WV_ZERO_RO'],profiles_qualified=profiles,application_permission=False,B0_M0a_application_NI='NOT_PROVEN',new_profile_application_NI='NOT_MEASURED',evidence_refs={'protocol':ref(C/'cpu/PRODUCTION_CPU_RECEIPT.json'),'MS_domainNI':ref(C/'CPU_MS011_111_NEW_SYSTEM_DOMAIN_NI.json'),'actual282':ref(C/'ACTUAL_282_SYSTEM850_CPU_RECEIPT.json')}))
hostq=put(T/'TEST_ONLY_HOSTQ.json',dict(schema='EP_MAIN_SOURCE78_SYSTEM850_FAMILY_HOST_QUALIFICATION_V1',status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',approved_by='EP-MAIN',TEST_ONLY=True,source_identity=mc.reference()['source_identity'],modes_qualified=['S','WV_ZERO_RO'],profiles_qualified=profiles,modules=[ref(p)for p in R.rglob('*')if p.is_file()],application_permission=False))
sourceq=ref(J/'control/SOURCE_QUALIFICATION.json')
resource=ref(J/'execution_performance_first_20261103_v1/tools/resources_service.py');policy=ref(J/'execution_performance_first_20261103_v1/control/RESOURCE_POLICY.json')
specs=[];by={}
for cell in mc.family_scope()['points']:
 d=mc.exact(cell['candidate_spec_ref']);base=mc.exact(cell['old_REF850_spec_ref']);ids=cell['input_identity_sha256'];anchors={}
 for mode in ['S','WV_ZERO_RO']:
  br=next(z['old_REF850_spec_ref']for z in mc.family_scope()['points']if z['input_identity_sha256']==ids and z['mode']==mode);bs=mc.exact(br);pop=real['registered_future_requests'][eng.FRONTEND_GOAL]['consumed'][bs['cohort']]
  anchors[mode]=put(T/f'TEST_ONLY_ANCHOR_{ids}_{mode}.json',dict(schema='EP_MAIN_EXACT_EXISTING_S_REFERENCE_QUALIFICATION_V1'if mode=='S'else'EP_MAIN_EXACT_EXISTING_MODE_REFERENCE_QUALIFICATION_V1',status='EXACT_EXISTING_S_HARDWARE_INPUT_OBSERVERS_QUALIFIED_FOR_MATCHED_REFERENCE'if mode=='S'else'EXACT_EXISTING_HARDWARE_INPUT_OBSERVERS_REFERENCE_REUSE_QUALIFIED',approved_by='EP-MAIN',TEST_ONLY=True,spec_ref={k:v for k,v in br.items()if k!='bytes'},point_ref=pop['accepted_point_ref'],source_identity=bs['source_identity'],input_identity_sha256=ids,current_closed_state='CLOSED_ACCEPTED',currently_accepted_population=True,registry_population_request_id=eng.FRONTEND_GOAL,expected_effective_options_sha256=mc.digest_value(bs['expected_effective_options'])))
 elig=put(T/f'TEST_ONLY_INPUT_{ids}.json',dict(status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',source_identity=base['source_identity'],input_identity_sha256=ids,modes_qualified=['S','WV_ZERO_RO'],ordered_kernel_identity=mc.exact(base['input_binding_ref'])['ordered_kernel_identity'],TEST_ONLY=True,application_permission=False))
 s=bind(d,dict(host_qualification_ref=hostq,mode_cpu_qualification_ref=cpuq,source_qualification_ref=sourceq,eligibility_ref=elig,resource_module_ref=resource,resource_policy_ref=policy,absolute_REF850_S_anchor_qualification_ref=anchors['S'],absolute_REF850_EP_anchor_qualification_ref=anchors['WV_ZERO_RO'],authorization_ref=auth,native_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),native_mount_namespace=os.readlink('/proc/self/ns/mnt')))
 p=T/'cases'/s['cohort']/'control/FROZEN_SPEC.json';put(p,s);q['admitted_specs'][s['cohort']]=ref(p)['sha256'];q['runtime_versions'][s['host_engine_ref']['sha256']]=dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']);specs.append(s);by[s['cohort']]=s
for s in specs:
 check(s['cohort']+'_actual_static_modecontract',lambda s=s:eng.formal_mode_contract(s))
 check(s['cohort']+'_actual_engine_spec_for_prepare_only',lambda s=s:eng.spec_for(s['cohort'],require_release=False))
 if mc.family_row(s)['stage']=='PRIMARY_SINGLE_FAMILY':check(s['cohort']+'_actual_engine_default_initial',lambda s=s:eng.spec_for(s['cohort']))
 else:check(s['cohort']+'_default_combo_unreleased_rejected',lambda s=s:eng.spec_for(s['cohort']),True)
 if s['mode']=='S':check(s['cohort']+'_fair_reciprocal_pair',lambda s=s:mc.validate_fair_pair(s,by[s['same_background_peer_cohort']]))
base=copy.deepcopy(specs[0])
def mutate(fn):s=copy.deepcopy(base);fn(s);return s
for label,fn in [
 ('unknowncohort',lambda s:s.update(cohort='EP_PERF_OUTSIDE')),
 ('Source92',lambda s:s['source_identity'].update(core_source_commit='9'*40)),
 ('wrongELF',lambda s:s['source_identity'].update(binary_sha256='0'*64)),
 ('wronginput',lambda s:s.update(input_identity_sha256='0'*64)),
 ('badgeometry',lambda s:s['geometry'].update(ways=4)),
 ('clock1020',lambda s:s['expected_effective_options'].update({'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:1020.0'})),
 ('fixedlatency50',lambda s:s['expected_effective_options'].update({'-dram_latency':'50'})),
 ('P2',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_bank_ops':'2'})),
 ('MS0',lambda s:s['expected_effective_options'].update({'-gpgpu_ep_l2_ms_observer':'0'})),
 ('line256',lambda s:s['expected_effective_options'].update({'-gpgpu_cache:dl2':'S:64:128:16,L:B:m:L:P,A:256:1,128:0,32'})),
 ('badmodeF',lambda s:s.update(mode='F',M=True,T=True)),
 ('typed0notbool',lambda s:s.update(M=0)),
 ('oldREFasmatchedS',lambda s:s.update(REF850_usage='MATCHED_S')),
 ('wrongpeer',lambda s:s.update(same_background_peer_cohort=specs[-1]['cohort'])),
 ('extraoption',lambda s:s['expected_effective_options'].update({'-new':'1'})),
 ('missingoverlay',lambda s:s.update(ordered_configs=s['ordered_configs'][:-1])),
 ('reversedconfigs',lambda s:s.update(ordered_configs=list(reversed(s['ordered_configs'])))),
 ('ROcertinhere',lambda s:s.update(ro_qualification_ref={'path':'BAD','sha256':'0'*64})),
 ('changedkernels',lambda s:s.update(expected_kernel_scopes=[])),
 ('CTAtruncate',lambda s:s.update(expected_CTA=1)),
]:check('NEG_'+label,lambda fn=fn:eng.formal_mode_contract(mutate(fn)),True)
check('unrelated_frontend_native_guard',lambda:front.main(['experiment','prepare','EP_PERF_OUTSIDE','--project','EP_L2']),True)
# Full whole-terminal numeric parser. Build explicit synthetic zero-traffic fixtures from accepted small compact seeds.
N=J/'research/implementation_performance_v2_20261029_v1/agent_b';tree=ast.parse((N/'test_full_parser_synthetic_v2.py').read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['wire','build']]
parse,math=parser.numeric_math();ns=dict(parse=parse,reasons=parse.__globals__['REASONS']);exec(compile(ast.Module(body=selected,type_ignores=[]),'original_small_synthetic_builder','exec'),ns)
fixtures=T/'TEST_ONLY_SYNTHETIC_TERMINALS';fixtures.mkdir(exist_ok=True);outputs=[];rawby={}
for s in specs:
 cell=mc.family_row(s);bs=mc.exact(cell['old_REF850_spec_ref']);pop=real['registered_future_requests'][eng.FRONTEND_GOAL]['consumed'][bs['cohort']];ns['binding']=mc.exact(s['input_binding_ref']);ns['bundle']=mc.exact(pop['validation_ref']);raw=ns['build'](s);p=fixtures/(s['cohort']+'.TEST_ONLY.log');p.write_text(raw)
 qual=dict(formal_mode=s['mode'],mode_contract_ref=s['mode_contract_ref'],validation_module_ref=s['validation_module_ref'],mode_cpu_qualification_ref=s['mode_cpu_qualification_ref'],source_identity=s['source_identity'])
 v=check(s['cohort']+'_actual_full_terminal_parser',lambda s=s,p=p,qual=qual:parser.validate_case(p,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']))
 check(s['cohort']+'_parser_no_scientific_acceptance',lambda v=v:mc.need(v['scientific_acceptance_granted']is False,'parser cannot accept'))
 outputs.append(dict(cohort=s['cohort'],fixture_ref=ref(p),geometry=s['geometry'],numeric_body=v['math_binding']['numeric_body_sha256'],suffix=v['math_binding']['frozen_final_suffix_sha256']));rawby[s['cohort']]=(s,qual,raw)
s,qual,raw=next(v for v in rawby.values()if v[0]['geometry']['sets']==64 and v[0]['mode']=='WV_ZERO_RO')
for label,fn in [
 ('raw_other282',lambda x:x.replace('-gpgpu_cache:dl2 S:64:128:16','-gpgpu_cache:dl2 S:32:128:8')),
 ('missingB0',lambda x:'\n'.join(l for l in x.split('\n')if not l.startswith('EPL2B0V1|INVARIANT|'))),
 ('missingTVD',lambda x:'\n'.join(l for l in x.split('\n')if not l.startswith(('EPL2TVDV2|','EPL2TVDV3|')))),
 ('liveD',lambda x:x.replace('descriptor_used=0','descriptor_used=1')),
 ('bankP2',lambda x:x.replace('bank0=1','bank0=2')),
 ('noexit',lambda x:x.replace('GPGPU-Sim: *** exit detected ***','')),
 ('badinstructions',lambda x:x.replace('gpu_tot_sim_insn = '+str(s['expected_instructions']),'gpu_tot_sim_insn = 1')),
 ('ROunexpected',lambda x:x+'EPL2ROV1|SUMMARY|slice=0|live=0\n'),
 ('newobserver',lambda x:x+'EPL2LIFEV1|anything\n'),
 ('wrongsource',lambda x:x.replace(s['source_identity']['core_source_commit'],'0'*40))
]:
 p=fixtures/('NEG_'+label+'.TEST_ONLY.log');p.write_text(fn(raw));check('NEG_full_parser_'+label,lambda p=p:parser.validate_case(p,s,qual,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256']),True)

# Exercise the real conditional engine with private, explicitly TEST_ONLY terminal rows.
target=next(x for x in specs if mc.family_row(x)['stage']=='CONDITIONAL_COMBINATION'and x['mode']=='WV_ZERO_RO')
ident=target['input_identity_sha256'];anchor=mc.exact(target['absolute_REF850_EP_anchor_qualification_ref']);refpoint=mc.exact(anchor['point_ref']);baseline=refpoint['cycles']
def gate_rows(gcycles,scycles,Sslow=False):
 refs={}
 for family,cy in [('G64W16',gcycles),('FRFCFS256',scycles)]:
  for sp in [x for x in specs if x['input_identity_sha256']==ident and mc.family_row(x)['family']==family]:
   cid=sp['cohort'];u='TEST_ONLY_UUID_'+cid
   point=dict(status='EP_FULL_PERF_APPLICATION_ACCEPTED',TEST_ONLY=True,cohort=cid,mode=sp['mode'],uuid=u,source_identity=sp['source_identity'],input_identity_sha256=ident,hardware_drained=True,instructions=sp['expected_instructions'],CTA=sp['expected_CTA'],cycles=cy if sp['mode']=='WV_ZERO_RO'else baseline*(2 if Sslow else 1),spec_ref=ref(T/'cases'/cid/'control/FROZEN_SPEC.json'))
   ar=dict(status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS',TEST_ONLY=True,cohort=cid,uuid=u,source_keep=True,archive_ref=dict(path='/root/share/mnt164/TEST_ONLY_NOT_REAL_ARCHIVE/result.tar',sha256='a'*64),native_restores=[dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',target='TEST_ONLY_A',archive_sha256='a'*64),dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',target='TEST_ONLY_B',archive_sha256='a'*64)])
   pr=put(T/'TEST_ONLY_STAGE_POINT'/ (cid+'.json'),point);arref=put(T/'TEST_ONLY_STAGE_ARCHIVE'/(cid+'.json'),ar);q['consumed'][cid]=dict(state='CLOSED_ACCEPTED',TEST_ONLY=True,uuid=u,accepted_point_ref=pr,archive_receipt_ref=arref)
   if sp['mode']=='WV_ZERO_RO':refs[family+'_EP_point_ref']=pr
 q['remaining']=12-len(q['consumed'])
 review=put(T/'TEST_ONLY_COMBINATION_REVIEW.json',dict(schema='EP_MAIN_SYSTEM850_ABSOLUTE_EP_COMBINATION_GATE_REVIEW_V1',status='MAIN_REVIEWED_SYSTEM850_ABSOLUTE_EP_GATE_PASS',request_id=eng.GOAL,input_identity_sha256=ident,source_identity=target['source_identity'],reference_EP_point_ref=anchor['point_ref'],TEST_ONLY=True,**refs))
 for sp in [x for x in specs if x['input_identity_sha256']==ident and mc.family_row(x)['stage']=='CONDITIONAL_COMBINATION']:
  put(T/'control/conditional_release'/(sp['cohort']+'.json'),dict(status='MAIN_RELEASED_APPROVED_CONDITIONAL_CELL',request_id=eng.GOAL,cohort=sp['cohort'],spec_sha256=q['admitted_specs'][sp['cohort']],criterion_review_ref=review,TEST_ONLY=True))
gate_rows(baseline-3000,baseline-3000)
check('combo_released_absolute_EP_ge1percent_both_actual_engine',lambda:eng.spec_for(target['cohort']))
gate_rows(baseline+1000,baseline+1000,Sslow=True)
check('combo_signedPASS_but_onlySslower_ratio_gain_actual_engine_rejected',lambda:eng.spec_for(target['cohort']),True,'EP_ABSOLUTE_CRITERION_NOT_MET')
gate_rows(baseline-8000,baseline)
check('combo_one_ge3percent_othernonnegative_actual_engine',lambda:eng.spec_for(target['cohort']))
gate_rows(baseline-8000,baseline+1)
check('combo_onege3percent_otherregresses_actual_engine_rejected',lambda:eng.spec_for(target['cohort']),True,'EP_ABSOLUTE_CRITERION_NOT_MET')
gate_rows(baseline-3000,baseline-3000)
epid=next(x['id']for x in mc.family_scope()['points']if x['input_identity_sha256']==ident and x['family']=='G64W16'and x['mode']=='S');saved=copy.deepcopy(q['consumed'][epid]);q['consumed'][epid]['state']='ACCEPTED_PENDING_ARCHIVE'
check('combo_Sarm_notarchived_rejected',lambda:eng.spec_for(target['cohort']),True,'notclosed');q['consumed'][epid]=saved

receipt=dict(schema='EP_SYSTEM850_PRIVATE_ACTUAL_ENGINE_AND_FULL_TERMINAL_CPU_V1',status='PASS_PRIVATE_ENGINE_FULL_TERMINAL_SYNTHETIC_NOT_APPLICATION',controls=rows,total=len(rows),passed=sum(r['PASS']for r in rows),full_parser_fixtures=outputs,frozen_math=math,new_model_starts=0,real_native_operations=0,real_registry_writes=0,scope='TEST_ONLY private registry/reviews; real spec_for and full frozen numeric terminal parser; all raw synthesized from small compact STRUCT/scopes, not application or NI evidence; no Trace or oldraw scans')
(H/'ACTUAL_ENGINE_AND_FULL_PARSER_CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(status=receipt['status'],passed=receipt['passed'],total=receipt['total'])))
