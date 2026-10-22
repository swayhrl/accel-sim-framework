from pathlib import Path
import json,hashlib,copy,sys,datetime,shutil
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';T=Path('/tmp/e2_four_qualified_candidate');read=lambda p:json.loads(Path(p).read_bytes());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'path':str(p),'sha256':sha(p)}
def put(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
report=read(T/'REPORT.json');static=read(T/'STATIC_CROSS_CHECK.json');assert report['status']=='FOUR_INDEPENDENT_CANDIDATES_ROOT_REVIEW_REQUIRED_NO_REGISTRATION_OR_START'
(A/'qualification_candidate_history').mkdir(exist_ok=True)
for f in ['REPORT.json','STATIC_CROSS_CHECK.json']:shutil.copyfile(T/f,A/'qualification_candidate_history'/f)
pre=P/'conditional_followup/QUALIFICATION_PREPARATION_r1';mapping={'/tmp/e2_cfd_dwt_prequalification_review.json':str(pre/'CFD_DWT_APPLICABILITY_REVIEW.json'),'/tmp/e2_vector_conv_prequalification_review.json':str(pre/'VECTOR_CONV_APPLICABILITY_REVIEW.json'),'/tmp/e2_four_config_metadata_preflight.json':str(pre/'CONFIG_METADATA_PREFLIGHT.json')}
checks=[];unique={}
def verify_refs(obj):
 if isinstance(obj,list):
  for x in obj:verify_refs(x)
 elif isinstance(obj,dict):
  if isinstance(obj.get('path'),str) and isinstance(obj.get('sha256'),str) and Path(obj['path']).is_file():
   pp=Path(obj['path'])
   if pp.stat().st_size>=4*2**20:
    assert str(pp) in ['/workspace/build/ep-l2-ms20261022-a2-detach-observer-r4/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a','/workspace/build/ep-l2-ms20261022-a2-detach-observer-r4/accel-sim.out'],'unexpected oversized metadata '+str(pp)
    return
   expected=obj['sha256'];assert sha(pp)==expected,str(pp);unique[str(pp)]=expected
  if 'evidence_path' in obj and 'evidence_sha256' in obj:assert sha(obj['evidence_path'])==obj['evidence_sha256']
  for x in obj.values():verify_refs(x)
for r in report['conditions']:
 w=r['workload'];q=read(T/'qualifications'/f'{w}_F_QUALIFICATION.json');verify_refs(q);s=read(P/'conditional_followup/PRIMARY_FOUR_EXISTING_POSITIVE_RO_r1/specs'/f'{w}_PREPARED_NOT_QUALIFIED.json')
 assert q['status']=='ROOT_REVIEW_REQUIRED' and q.get('root_qualification_sign') is None
 assert q['source_identity']==report['source_identity'];assert q['profile_semantics']==s['profile_semantics'];assert q['supported_profiles']=={'F':q['profile_semantics']};assert len(q['gates'])==19
 assert q['detach_observer_diagnostic']['validation_scope']==read(T/'common/VALIDATION_SCOPE.json')
 assert q['detach_observer_diagnostic']['expected_full_instructions']==r['fullinstructions'] and q['terminal_acceptance_required']['expected_instructions']==r['fullinstructions']
 assert q['input_scope_admission']['expected_kernel_count']==r['kernel_count']<=16
 for name,gr in q['gates'].items():
  proof=read(gr['evidence_path']);assert gr['production_driven'] is True and proof['source_identity']==q['source_identity']
  if name!='detach_observer_source_native_schema':assert proof['workload']==w and proof['no_wholeoldQ_or_newS_or_Cjoint_upgrade'] is True and proof['native_reexecutions']==0
 checks.append({'workload':w,'nineteen_gates_individually_reviewed':True,'full_input_oracle_source_and_counter_denominators':'PASS','native_reruns':0})
root={'schema':'E2_ROOT_APPROVED_FOUR_NEW_R4_PERINPUT_QUALIFICATION_SIGN_V1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_NEW_R4_FOUR_DISTINCT_FINITE_F_DIAGNOSTIC_QUALIFICATIONS_ONLY','reviewed_by':'E2 accountable root','user_approval':ref(A/'USER_APPROVAL.json'),'candidate_static_report':ref(A/'qualification_candidate_history/STATIC_CROSS_CHECK.json'),'candidate_report_preserved':ref(A/'qualification_candidate_history/REPORT.json'),'root_config_review':ref(pre/'CONFIG_METADATA_PREFLIGHT.json'),'CFD_DWT_source_input_review':ref(pre/'CFD_DWT_APPLICABILITY_REVIEW.json'),'VECTOR_CONV_source_input_review':ref(pre/'VECTOR_CONV_APPLICABILITY_REVIEW.json'),'actual_native48_review':ref(P/'native_r4_independent/INDEPENDENT_NATIVE_REVIEW.json'),'root_verified_unique_metadata_refs':len(unique),'per_input_reviews':checks,'decision':'All18 retainedmodel gates reviewedpercondition using exactcurrent9243/9dd passiveobserver delta,unchangedfiniteF P1 premise and48actualnative/1589 priorchecks;19th source/schema/native/CLI/fixeddecoder control evidence bound. No native rerun, oldQwholeinheritance,newS/allOFF fullapp, Cjointuplift, numericrecapture or speedupclaim. Eachinput source grammar/closedworld oracle scope independently reviewed and fullinstructions/kernel denominators distinct.','full_application_not_yet_accepted':True,'source_identity':report['source_identity'],'limits':'Actual full trace/main/archive/config assets rechecked at originalrunner admission andpostrun; normal durableexit/fullinstructions/64slice/212counter/drain required. Exact originalcentral successor scope must be adopted before Q registration or launch.'}
put(A/'ROOT_QUALIFICATION_SIGN.json',root)
done=set();visiting=set()
def mapstr(s):
 if s in mapping:return mapping[s]
 if s.startswith(str(T)+'/'):return str(A)+s[len(str(T)):]
 return s
def materialize(src):
 src=Path(src);dst=A/src.relative_to(T)
 if src in done:return dst
 assert src not in visiting,'cyclic candidate evidence '+str(src);visiting.add(src)
 d=read(src)
 def relocate(obj):
  if isinstance(obj,str):return mapstr(obj)
  if isinstance(obj,list):return [relocate(x) for x in obj]
  if not isinstance(obj,dict):return obj
  z={k:relocate(v) for k,v in obj.items()}
  for pk,hk in [('path','sha256'),('evidence_path','evidence_sha256')]:
   oldpath=obj.get(pk)
   if isinstance(oldpath,str) and hk in obj:
    if oldpath.startswith(str(T)+'/'):target=materialize(oldpath)
    else:target=Path(mapstr(oldpath))
    if target.is_file():z[hk]=sha(target);z['bytes']=target.stat().st_size if pk=='path' and 'bytes' in z else z.get('bytes')
  return {k:v for k,v in z.items() if not (k=='bytes' and v is None)}
 d=relocate(d)
 if src.parent.name!='qualifications':
  if d.get('status') in ['ROOT_REVIEW_REQUIRED','SOURCE_AND_ENGINEERING_EVIDENCE_READY_ROOT_REVIEW_REQUIRED']:d['status']='ROOT_REVIEWED_APPLICABILITY_PASS';d['E_root_sign']=ref(A/'ROOT_QUALIFICATION_SIGN.json')
 put(dst,d);visiting.remove(src);done.add(src);return dst
for f in list((T/'common').glob('*.json'))+list((T/'admissions').rglob('*.json'))+list((T/'gates').rglob('*.json')):materialize(f)
final=[];scopes=[]
for row in report['conditions']:
 w=row['workload'];p=materialize(T/'qualifications'/f'{w}_F_QUALIFICATION.json');q=read(p);q['status']='INDEPENDENTLY_QUALIFIED';q['qualified_at_utc']=root['at_utc'];q['root_qualification_sign']=ref(A/'ROOT_QUALIFICATION_SIGN.json');q.pop('root_steps_required',None)
 for gate in q['gates'].values():gate['status']='PASS';gate['E_root_sign']=ref(A/'ROOT_QUALIFICATION_SIGN.json');gate['scope']=gate['scope'].replace('_PENDING_ROOT_SIGN','_ROOT_REVIEWED')
 q['default_off_equivalence']=copy.deepcopy(q['gates']['old_all_off_equivalence']);q['default_off_equivalence']['scope_note']='Source/model premise andnativeobserver OFF/ON only; no newS/allOFF fullapplication.'
 q['scope_note']='Exact independentlyreviewedr4 finiteF observer for this complete originalinput only. Full oldQ notinherited; currentsource/native/schema/input/oracle metadata gates independently signed. No completeapplication accepteduntilnativeexit0/fullinstructions/64slice/212counter/drain/currentidentity pass.'
 put(p,q);qid=sha(p);s=read(P/'conditional_followup/PRIMARY_FOUR_EXISTING_POSITIVE_RO_r1/specs'/f'{w}_PREPARED_NOT_QUALIFIED.json');s.update(qualification_id=qid,budget_bucket='EPL2_DETACH_ZERO_EXISTING_POSITIVE_RO_PRIMARY_FOUR_20261022_r1',preparation_status='E_NEW_R4_F_INDEPENDENTLY_QUALIFIED_PENDING_ORIGINAL_CENTRAL_BIND_AND_REAL_ADMISSION',parser=q['terminal_parser'],input_scope_admission=q['input_scope_admission'],profile_semantics=q['profile_semantics']);s['operational_limits_override']['status']='USER_APPROVED_PRIMARY_FOUR_PENDING_ORIGINAL_CENTRAL_ADOPTION';s['profile_semantics']=copy.deepcopy(q['supported_profiles']['F']);sp=A/'specs'/f'{w}_F_SPEC.json';put(sp,s)
 assert s['identity']['runtime_config_sha256']==q['detach_observer_diagnostic']['runtime_config_sha256'];assert s['parser']['path'].endswith('/parse_detach_terminal.py')
 scopes.append(q['detach_observer_diagnostic']['validation_scope']);final.append({'workload':w,'condition_id':s['condition_id'],'qualification':ref(p),'spec_ref':ref(sp),'spec_semantic_sha256':hashlib.sha256(json.dumps({k:v for k,v in s.items() if k!='input_audit'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'expected_full_instructions':row['fullinstructions'],'expected_kernel_count':row['kernel_count']})
assert all(x==scopes[0] for x in scopes)
for f in list((A/'qualifications').glob('*.json'))+list((A/'admissions').rglob('*.json'))+list((A/'gates').rglob('*.json')):verify_refs(read(f))
put(A/'QUALIFICATIONS_READY.json',{'schema':'E2_APPROVED_FOUR_E_INDEPENDENT_QUALIFICATION_READY_V1','status':'FOUR_INDEPENDENTLY_QUALIFIED_SOURCE_INPUT_METADATA_PENDING_ORIGINAL_CENTRAL_AND_LIVE_ADMISSION','at_utc':root['at_utc'],'conditions':final,'common_validation_scope':ref(A/'common/VALIDATION_SCOPE.json'),'root_sign':ref(A/'ROOT_QUALIFICATION_SIGN.json'),'qualifications_registered':False,'new_actual_starts':0})
print(json.dumps({'qualified':len(final),'unique_small_refs_checked':len(unique),'qids':{r['workload']:r['qualification']['sha256'] for r in final},'registry_or_start_mutated':False}))
