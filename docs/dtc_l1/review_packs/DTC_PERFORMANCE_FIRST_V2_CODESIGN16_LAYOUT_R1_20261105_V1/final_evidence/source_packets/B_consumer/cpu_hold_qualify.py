"""CPU-only typed safety metadata fixtures in own isolated directory. No registry."""
import pathlib,json,hashlib,copy,shutil
import consumer as c
import safety_hold_overlay as h
D=pathlib.Path(__file__).resolve().parent;R=D/'fixtures/CPU_ONLY_NATIVE_LAYOUT';R.mkdir(parents=True,exist_ok=True)
for x in ['tools','control/specs','control/PROFILE_HOLD_DECISIONS','control/qualification_ledger','analysis']:(R/x).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
I=json.loads((D/'ADMISSION_HOLD_INTERFACE.json').read_bytes());shutil.copyfile(I['resource_source']['path'],R/'tools/perf16r1_resources.py');shutil.copyfile(I['ops_source']['path'],R/'tools/perf16r1_ops.py')
M=json.loads((D/'C_RESOURCE_CODESIGN_MATRIX.fixed.json').read_bytes());cs=M['candidates'];req=c.F['request16'];specs={};admitted={}
for cand in cs:
 co=cand['proposed_native_cohort'];s=dict(cohort=co,request=req,profile=cand['profile'],structure_variant=cand['profile'],input_digest=cand['input_digest'],cell='DH',downstream_profile='P0',host_cpu=None,CPU_ONLY_METADATA_NOT_SCIENTIFIC_SPEC=True);put(R/'control/specs'/(co+'.json'),s);shutil.copyfile(R/'control/specs'/(co+'.json'),R/'control'/(co+'_SPEC.json'));specs[co]=s;admitted[co]=sha(R/'control/specs'/(co+'.json'))
ctx={'root':str(R),'request':req,'source_qualified':True,'source_pins':[{'path':str(R/'tools'/n),'sha256':sha(R/'tools'/n)}for n in ['perf16r1_resources.py','perf16r1_ops.py']],'q':{'request':req,'budget':16,'remaining':16,'admitted_specs':admitted,'consumed':{},'admission_holds':{},'state':'ARMED'},'CPU_ONLY_NOT_ACTUAL_GRANT':True}
checks=[]
def ck(n,v):assert v,n;checks.append({'name':n,'PASS':True})
def should_reject(n,fn):
 try:fn();ok=False
 except Exception:ok=True
 ck(n,ok)
rows=[dict(cohort=x['proposed_native_cohort'],variant=x['profile'],input_digest=x['input_digest'],accepted=False,status='AWAIT_CLOSED_RESULT',cycles=None)for x in cs];first=rows[0];co=first['cohort'];profile=first['variant']
ck('empty_dict_means_no_HOLD',h.validate_unstarted(first,specs[co],cs,ctx,root=R)is None)
def decision_for(profile):
 ep=R/'CPU_ONLY_EVIDENCE.json';put(ep,{'schema':'CPU_ONLY_NO_MODEL_OR_RUNTIME_FAILURE','fixture':True});dp=R/'control/PROFILE_HOLD_DECISIONS'/(profile+'.json');decision=dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_PROFILE_HOLD_DECISION_V1',request=req,authority_commit=c.F['authority_commit'],profile=profile,classification='CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD',reason='CPU_ONLY_PROTOCOL_FIXTURE_NOT_ACTUAL_SAFETY_EVENT',evidence_path=str(ep),evidence_sha256=sha(ep),decided_by='DTC_MAIN',created_utc='CPU_ONLY_FIXTURE_TIME',approval_scope={'candidate_cohorts':[x['proposed_native_cohort']for x in cs if x['profile']==profile],'request':req,'profile':profile});put(dp,decision);v={k:decision[k]for k in ['profile','request','classification','reason','evidence_path','evidence_sha256','decided_by','created_utc']};v.update(decision_path=str(dp),decision_sha256=sha(dp),source_ops_sha256=sha(R/'tools/perf16r1_ops.py'));return v
hold=decision_for(profile);ctx['q']['admission_holds'][profile]=hold;v=h.validate_unstarted(first,specs[co],cs,ctx,root=R);ck('valid_profile_HOLD_explicit_no_UUID_cycles',v['classification']=='UNUSED_SAFETY_HOLD'and v['no_model_uuid_or_cycles']);held=[]
for r in rows:
 w=h.validate_unstarted(r,specs[r['cohort']],cs,ctx,root=R)
 if w is not None:held.append(r['cohort'])
ck('one_profile_applies_to_exact8',len(held)==8 and set(held)==set(x['proposed_native_cohort']for x in cs if x['profile']==profile))
bad=copy.deepcopy(ctx);bad['q']['admission_holds'][profile]={};should_reject('empty_profile_record_is_malformed',lambda:h.validate_unstarted(first,specs[co],cs,bad,root=R))
for key,value,name in [('classification','PERFORMANCE_REGRESSION','performance_regression_not_typed_safety'),('evidence_sha256','0'*64,'bad_evidence_SHA'),('decided_by','CPU_UNKNOWN_OWNER','wrong_decider'),('profile','PHYS_INVALID','wrong_profile'),('cycles',0,'unused_HOLD_cannot_have_cycle0')]:
 bad=copy.deepcopy(ctx);bad['q']['admission_holds'][profile][key]=value;should_reject(name,lambda bad=bad:h.validate_unstarted(first,specs[co],cs,bad,root=R))
dp=pathlib.Path(hold['decision_path']);saved=dp.read_bytes();decision=json.loads(saved);decision['approval_scope']['candidate_cohorts'].pop();put(dp,decision);bad=copy.deepcopy(ctx);bad['q']['admission_holds'][profile]['decision_sha256']=sha(dp);should_reject('decision_scope7_rejected',lambda:h.validate_unstarted(first,specs[co],cs,bad,root=R));dp.write_bytes(saved)
ip=R/'control/qualification_ledger'/(co+'.INTENT.json');put(ip,{'CPU_ONLY_NO_NATIVE_INTENT':True});should_reject('unused_HOLD_with_INTENT_rejected',lambda:h.validate_unstarted(first,specs[co],cs,ctx,root=R));assert ip.resolve().is_relative_to((D/'fixtures').resolve());ip.unlink()
consumed=copy.deepcopy(ctx);consumed['q']['consumed'][co]={'CPU_ONLY_CONSUMPTION_METADATA':True};ck('consumed_healthy_identity_not_relabelled',h.validate_unstarted(first,specs[co],cs,consumed,root=R)is None)
# Both profiles can be legitimately unused only via two independent exact8 decisions.
for p in {r['variant']for r in rows}:ctx['q']['admission_holds'][p]=decision_for(p)
qualified=[]
for row in rows:
 h.validate_unstarted(row,specs[row['cohort']],cs,ctx,root=R);qualified.append(dict(row,status='UNUSED_SAFETY_HOLD'))
ctx['q']['state']='STOP_UNACCEPTED_WITH_UNUSED_CREDITS';ctx['q']['terminal_unused_safety_HOLD']=dict(cohorts=[r['cohort']for r in rows],remaining_credits_preserved=16,no_budget_refund=True,no_spec_removal=True,no_model_retries=True,UTC='CPU_ONLY_FIXTURE_TIME');put(R/'analysis/EXECUTION_TERMINAL.json',dict(status='ALL_ACTUAL_MODELS_TERMINAL_WITH_UNUSED_SAFETY_HOLD',budget=16,new_prepare_disabled=True,remaining_credits_preserved=16,states={r['cohort']:'UNUSED_SAFETY_HOLD'for r in rows},unused_safety_HOLD={r['cohort']:ctx['q']['admission_holds'][r['variant']]for r in rows}));account=h.accounting(qualified,ctx,root=R);ck('all_accounted_with_unused_is_not_actual_closed',account['all16_candidates_accounted_verified']and not account['all16_actual_scientific_closed']and account['unused_safety_HOLD_n']==16)
bad=copy.deepcopy(ctx);bad['q']['state']='RUNNING';ck('global_RUNNING_not_terminal_accounted',not h.accounting(qualified,bad,root=R)['all16_candidates_accounted_verified']);bad=copy.deepcopy(ctx);bad['q']['terminal_unused_safety_HOLD']['no_budget_refund']=False;ck('refund_cannot_verify_accounted',not h.accounting(qualified,bad,root=R)['all16_candidates_accounted_verified']);bad=copy.deepcopy(ctx);bad['q']['admission_holds']['CPU_OUTSIDE_SCOPE']={};ck('unknown_hold_key_blocks_verified_terminal',not h.accounting(qualified,bad,root=R)['all16_candidates_accounted_verified'])
# STOP by itself creates no per-candidate HOLD.
q0=copy.deepcopy(ctx);q0['q']['admission_holds']={};ck('global_STOP_does_not_infer_profile_HOLD',h.validate_unstarted(first,specs[co],cs,q0,root=R)is None)
put(D/'HOLD_CPU_QUALIFICATION.json',{'schema':'CPU_ONLY_TYPED_SAFETY_HOLD_CONSUMER_FIXTURE_V1','all_pass':True,'count':len(checks),'checks':checks,'shared_resource_AST':I['admission_hold_AST_sha256'],'isolated_root':str(R),'accounting_fixture':account,'fixtures_are_not_actual_scientific_hold_or_grant':True,'native_R4_writes':0,'registry_writes':0,'new_models':0});print('HOLD PASS',len(checks))
