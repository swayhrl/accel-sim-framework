from pathlib import Path
from fractions import Fraction
import sys,types,json,copy,hashlib,math
sys.dont_write_bytecode=True
P=Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');D=A/'C_final_structure32_preparation_v1';D.mkdir(exist_ok=True);source=A/'final_structure32_readonly_audit.candidate.py';target=D/'final_structure32_readonly_audit.py';target.write_bytes(source.read_bytes());compile(target.read_bytes(),str(target),'exec');m=types.ModuleType('C_final32_CPU_only');m.__file__=str(target);exec(compile(target.read_bytes(),str(target),'exec'),m.__dict__);checks=[]
def ck(n,v):assert v,n;checks.append(dict(name=n,PASS=True))
def reject(n,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,TypeError):ck(n,True);return
 raise AssertionError('NOT_REJECTED '+n)
ck('import_inert_no_final_output',not m.OUTPUT.exists());base,refs=m.baselines();ck('actual_frozen16P0refs_6alias',len(refs)==16 and sum(bool(r['legal_prior_P0_alias'])for r in refs)==6)
# Pure accounting: actual consumption remains distinct from held unused identities.
expected=['CPU_ONLY_'+str(i)for i in range(28)];q=dict(budget=28,admitted_specs={c:'CPU_SPEC'for c in expected},consumed={c:dict(uuid='CPU_UUID_'+c)for c in expected[:-1]},remaining=1,model_automatic_retries=0,state='STOP_UNACCEPTED',admission_holds={expected[-1]:dict(cohort=expected[-1],state='UNUSED_FAMILY_HOLD',uuid=None,cycles=None,consumed=False,scientific_model_starts=0,no_budget_refund=True,no_model_retry=True,reason=dict(state='FAILED',CPU_ONLY=True))},terminal_unused_family_HOLD=dict(cohorts=[expected[-1]],no_budget_refund=True,no_spec_removal=True,no_model_retries=True));ck('27actual_plus1held_accounting_valid',m.validate_accounting(q,expected,28)=={expected[-1]})
for key,val in [('budget',27),('remaining',0),('model_automatic_retries',1),('state','RUNNING')]:bad=copy.deepcopy(q);bad[key]=val;reject('accounting_bad_'+key,lambda b=bad:m.validate_accounting(b,expected,28))
for key,val in [('uuid','fake'),('cycles',0),('consumed',True),('scientific_model_starts',False),('no_budget_refund',False),('no_model_retry',False)]:bad=copy.deepcopy(q);bad['admission_holds'][expected[-1]][key]=val;reject('unused_bad_'+key,lambda b=bad:m.validate_accounting(b,expected,28))
bad=copy.deepcopy(q);bad['admission_holds']={};reject('unused_without_certified_HOLD_rejected',lambda:m.validate_accounting(bad,expected,28));bad=copy.deepcopy(q);bad['terminal_unused_family_HOLD']['cohorts']=[];reject('terminal_must_enumerate_exact_unused',lambda:m.validate_accounting(bad,expected,28));bad=copy.deepcopy(q);bad['consumed'][expected[0]]['uuid']=bad['consumed'][expected[1]]['uuid'];reject('duplicate_UUID_rejected',lambda:m.validate_accounting(bad,expected,28));qall=dict(budget=4,admitted_specs={str(i):'CPU_SPEC'for i in range(4)},consumed={str(i):dict(uuid='CPU_UUID'+str(i))for i in range(4)},remaining=0,model_automatic_retries=0,state='RUNNING');ck('4fully_consumed_accounting_valid',not m.validate_accounting(qall,qall['admitted_specs'],4))
ck('empty_GM_null_not_zero',m.metric([])['GM']is None and m.metric([])['n']==0);ck('integer_exact_signs',m.metric([Fraction(2,1),Fraction(1,2),Fraction(1,1)])['positive_exact']==m.metric([Fraction(2,1),Fraction(1,2),Fraction(1,1)])['negative_exact']==m.metric([Fraction(2,1),Fraction(1,2),Fraction(1,1)])['zero_exact']==1);near=m.metric([Fraction(10**15+1,10**15)]);ck('nearzero_tolerance_not_exact_zero',near['positive_exact']==1 and near['zero_exact']==0 and near['zero_within1e_minus12']==1)
# Synthetic eight-input/four-variant matrix; these cycles/UUIDs are CPU fixtures only.
auth=m.read(m.AUTH);rows=[]
for j,v in enumerate(m.VARIANTS):
 for i,inp in enumerate(auth['inputs']):
  p=inp['population'];dh=base[p['program'],'DH']['cycles'];ch=base[p['program'],'CH']['cycles'];cycles=dh+[-7,0,11][(i+j)%3];rat={'S_DH':Fraction(dh,cycles),'Rnew':Fraction(ch,cycles),'Rold':Fraction(ch,dh)};rat['I']=rat['Rnew']/rat['Rold'];rows.append(dict(cohort='CPU_ONLY_'+str(j)+'_'+str(i),program=p['program'],suite=p['suite'],input_digest=p['input_digest'],variant=v,status='ACCEPTED_STRICT_ARCHIVE_RESTORE',accepted=True,cycles=cycles,uuid='CPU_ONLY_UUID_'+str(j)+'_'+str(i),native_simulator_observed=True,ratios={k:[x.numerator,x.denominator]for k,x in rat.items()}))
s=m.statistics(rows);ck('32accepted_8common_4variants',s['accepted']==32 and s['common_n']==8 and s['all32_actual_closed']and s['all32_accepted']and s['all32_accounted']);ck('S_DH_and_I_exact_algebra',all(r['ratios']['S_DH']==r['ratios']['I']for r in rows));ck('CH_ratio_not_equated_incremental_I',any(r['ratios']['Rnew']!=r['ratios']['I']for r in rows));ck('8programs_not_CORE32',s['programs']==8 and s['not_CORE32'])
# Compare independently computed Fraction/statistics against immutable B2 arithmetic (B3 unchanged).
sys.path.insert(0,str(A/'agents/B_perf_results_consumer_v2'));import snapshot as b
fixed,_,_=b.fixed_inputs()
def make_B(rr):
 brows=[]
 for r in rr:
  x=copy.deepcopy(r);x['route']='REMAINING28'
  for k in ['S_DH','Rnew','Rold','I']:x[k]=float(Fraction(*r['ratios'][k]))if r['accepted']else None
  brows.append(x)
 summary=b.summarize(brows,fixed);held=sum(r['status']=='UNUSED_FAMILY_HOLD'for r in rr);summary['unstarted_family_HOLD_points']=held;summary['all32_nonTag_closed_verified']=sum(r['accepted']or r['status']=='ARCHIVED_NEGATIVE_NO_PERFORMANCE'for r in rr)==32;summary['all32_scientific_success']=sum(r['accepted']for r in rr)==32;summary['all32_candidates_accounted_verified']=sum(r['accepted']or r['status']in['ARCHIVED_NEGATIVE_NO_PERFORMANCE','UNUSED_FAMILY_HOLD']for r in rr)==32
 return dict(rows=brows,summary=summary)
B=make_B(rows);m.compare_B(rows,s,B);ck('independent_GM_suite_signs_match_B2_B3_arithmetic',True)
partial=copy.deepcopy(rows);partial[0].update(accepted=False,status='ARCHIVED_NEGATIVE_NO_PERFORMANCE',cycles=None,ratios=None);sp=m.statistics(partial);bp=make_B(partial);m.compare_B(partial,sp,bp);ck('negative_removes_only_performance_denominator',sp['accepted']==31 and sp['archived_negative']==1 and sp['all32_actual_closed']and not sp['all32_accepted']and sp['common_n']==7)
held=copy.deepcopy(partial);held[0].update(status='UNUSED_FAMILY_HOLD',uuid=None,native_simulator_observed=False);sh=m.statistics(held);bh=make_B(held);m.compare_B(held,sh,bh);ck('31closed1unusedHOLD_accounted_not32closed',sh['accepted']==31 and sh['unused_family_HOLD']==1 and sh['archived_negative']==0 and sh['all32_accounted']and not sh['all32_actual_closed']and not sh['all32_accepted']);ck('common_same7_for_all4_no_best_stitching',sh['common_n']==7 and all(x['common']['S_DH']['n']==7 for x in sh['variants'].values())and sh['no_best_stitching'])
bad=copy.deepcopy(bh);bad['summary']['variants'][m.VARIANTS[0]]['available_set_metrics']['S_DH']['GM']*=1.01;reject('B_GM_drift_rejected',lambda:m.compare_B(held,sh,bad));bad=copy.deepcopy(bh);bad['rows'][1]['cycles']+=1;reject('B_cycle_drift_rejected',lambda:m.compare_B(held,sh,bad));bad=copy.deepcopy(bh);bad['summary']['common_nonTag_accepted_intersection']['ids'].pop();reject('B_intersection_drift_rejected',lambda:m.compare_B(held,sh,bad));bad=copy.deepcopy(bh);bad['summary']['all32_nonTag_closed_verified']=True;reject('B_HOLD_misreported_closed_rejected',lambda:m.compare_B(held,sh,bad))
# Actual current metadata cannot trigger final audit and cannot read a live raw file.
original_sha=m.sha
seen_raw=[]
def no_raw_sha(p):
 if P(p).name=='raw.log.gz':seen_raw.append(str(p));raise AssertionError('LIVE_RAW_MUST_NOT_BE_READ_IN_READINESS')
 return original_sha(p)
m.sha=no_raw_sha
try:m.readiness();raise AssertionError('UNEXPECTED_ACTUAL_FINAL_READINESS')
except(KeyError,AssertionError,FileNotFoundError)as e:actual_reason=repr(e)
ck('actual_partial_readiness_rejected_without_raw',not seen_raw and not m.OUTPUT.exists());m.sha=original_sha
ck('final_output_path_filename',str(m.OUTPUT/'FINAL_REVIEW.json')==str(A/'C_final_structure32_v1/FINAL_REVIEW.json'))
(D/'CPU_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS_CPU_PREPARATION_ONLY',count=len(checks),checks=checks,source_sha256=sha(target)if' sha'in globals()else hashlib.sha256(target.read_bytes()).hexdigest(),actual_readiness_reason=actual_reason,actual_final_audit_executed=False,actual_new_model_started=False,actual_final_review_exists=False),indent=2)+'\n');print('FINAL32_CPU',len(checks),hashlib.sha256(target.read_bytes()).hexdigest(),actual_reason)
