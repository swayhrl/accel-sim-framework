from pathlib import Path
from fractions import Fraction
import json,hashlib,math,gzip,subprocess,datetime,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');R=Path('/root/data/dtc_stage_iia_first16_20261104_v1');O=A/'agents/C_final_all16_review_v1';F=A/'root_final_scientific_analysis_v1';rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,b,detail=None):checks.append({'check':n,'PASS':bool(b),'detail':detail})
M=rd(R/'control/MATRIX.json');points=M['points'];plan=rd(R/'control/EXECUTION_PLAN.json');auth=rd(R/'control/SCIENCE_AUTHORIZATION.json');regp=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reg=rd(regp);REQ=M['request'];q=reg['registered_future_requests'][REQ];ep=rd('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json');cs={x['cohort']for x in points};digests=list(dict.fromkeys(x['input_digest']for x in points));ck('Fixed5001 exact8/16 one-shot matrix and grants',M['contract_commit']==plan['approved_contract_commit']==q['approved_contract_commit']=='5001c3f35052f7f91f1ad41eeff83f2947a0878d'and len(digests)==8 and len(cs)==16 and cs==set(q['admitted_specs'])==set(auth['budgets'])==set(q['consumed'])and set(auth['budgets'].values())=={1}and q['budget']==16 and q['remaining']==0 and q['model_automatic_retries']==0 and all(v['charged']==1 for v in q['consumed'].values())and M['next48_authorized']is False and plan['no_extensions']and plan['remaining48_not_authorized'])
ck('Registry epoch SHA consistent',ep['native_registry_sha256']==sha(regp))
pins=[{'path':x['path'],'expected':x['sha256'],'observed':sha(x['path'])}for x in plan['source_pins']];ck('All62 frozen runtime/build/input/config pins current',len(pins)==62 and all(x['expected']==x['observed']for x in pins))
oldpre=rd(R/'control/actual_owner_attach_v2/OLD_REQUEST_IDENTITIES_BEFORE.json');oldcmp=[]
for name,old in oldpre.items():
 if name.startswith('DTC_'):
  current=reg['registered_future_requests'][name];oldcmp.append({'request':name,'unchanged':old=={k:current.get(k)for k in ['budget','remaining','consumed']}})
oldq=reg['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];oldhash=hashlib.sha256(json.dumps(oldq,sort_keys=True,separators=(',',':')).encode()).hexdigest();ck('All preexisting DTC budgets/consumed/DONE and fullStageI request unchanged',all(x['unchanged']for x in oldcmp)and oldhash==rd(A/'agents/C/OWNER_AND_NATIVE_PATTERN_READONLY.json')['old_request_canonical_sha256']and oldq['budget']==len(oldq['consumed'])==360 and oldq['remaining']==0,oldcmp)
ck('Onlyone new DTC request and no other candidate grants',set(n for n in reg['registered_future_requests']if n.startswith('DTC_'))-set(n for n in oldpre if n.startswith('DTC_'))=={REQ} and q['all_other_candidate_grants']==0 and auth['all_other_candidate_grants']==0 and q['new_registration_only'] and q['old_request_budget_reused']is False)
uids={x['uuid']for x in q['consumed'].values()};other={v['uuid']for name,x in reg['registered_future_requests'].items()if name!=REQ for v in (x.get('consumed',{}).values()if isinstance(x.get('consumed'),dict)else [])if isinstance(v,dict)and'uuid'in v};ck('Sixteen distinct UUID no reuse across requests',len(uids)==16 and not(uids&other))
lease=rd('/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json');before=rd(R/'control/actual_owner_attach_v2/LEASE_BEFORE.json');expected=dict(before,additional_requests=before['additional_requests']+[REQ]);pp=Path('/proc/1498278');locks=[s for s in Path('/proc/locks').read_text().splitlines()if ' 1498278 'in s];ck('Sole existing ownerPID/start/controller and retained FD/FLOCK',lease==expected and int((pp/'stat').read_text().rsplit(')',1)[1].split()[19])==977758783 and os.readlink(pp/'fd'/str(lease['fd']))=='/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock'and 'FLOCK'in(pp/'fdinfo'/str(lease['fd'])).read_text()and sha(plan['parent_controller_path'])==lease['controller_sha256']=='de715b527c6194a65b30d0b921c34a26bc8af4433eddd78c957d98c123723c81'and len(locks)>=2,{'lease':lease,'locks':locks})
live=[]
for c,x in q['consumed'].items():
 pid=rd(R/'DTC/run/results'/x['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json');p=Path('/proc')/str(pid['pid'])
 if p.exists():
  s=(p/'stat').read_text().rsplit(')',1)[1].split()
  if int(s[19])==pid['start_ticks']and s[0]not in ['Z','X']:live.append(c)
batch=rd(R/'analysis/BATCH_STATE.json');ck('All16 model generations dead and finiteowner dispatch claims0',not live and not batch['running']and batch['claims']==0 and batch['consumed']==16 and batch['remaining']==0 and not batch['next48_released'],{'live_same_generation':live,'BATCH_STATE_sha256':sha(R/'analysis/BATCH_STATE.json'),'retained_errors_are_history_not_current_outcome':True})
refindex=rd(R/'control/ORIGINAL_REFERENCE_INDEX.json');refs=[];cycles={};options={};aliases=[]
source=rd('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/C/INDEPENDENT_SET_AUDIT.json')['source'];repo='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/planning-isolated.git';blob=subprocess.check_output(['git','--git-dir='+repo,'show',source['commit']+':'+source['git_path']]);originalpub=json.loads(gzip.decompress(blob));pubrows=originalpub['derived35']['rows'];originalmap={z['original'].get('RESULT_path'):z['original']for z in pubrows};ck('Historical331 vsnamed336 source unchanged',hashlib.sha256(blob).hexdigest()==source['sha256']and len(pubrows)==350 and sum(bool(z['original'].get('apparent_accepted'))for z in pubrows)==331 and originalpub['coverage']['derived35_selected']==336,{'source_commit':source['commit'],'git_path':source['git_path'],'sha256':source['sha256'],'original_rows':350,'original_accepted':331,'named_selected':336})
oldresult_rows=[z['original']for z in pubrows if z['original'].get('RESULT_sha256')];ck('All349 historical RESULT bytes stillpublishedSHA;18archivednegatives retained',len(oldresult_rows)==349 and all(sha(z['RESULT_path'])==z['RESULT_sha256']for z in oldresult_rows)and sum(z.get('raw_state')=='FAIL_L2MLP_ARCHIVED_NO_RETRY'for z in oldresult_rows)==18)
preaudit=rd('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/C/INDEPENDENT_SET_AUDIT.json');eng=next(c for c in preaudit['checks']if c['check']=='Original missing RESULT is typed engineering terminal negative')['detail'][0];ck('One original scanM16 engineeringnegative bytepreserved separately',sha(eng['path'])==eng['sha256']and len([z for z in pubrows if not z['original'].get('RESULT_sha256')])==1,eng)
for z in refindex['rows']:
 v=rd(z['source_path']);proof=v['proof'];key=z['input_digest'],z['cell'],z['profile'];cycles[key]=v['cycles'];options[key]=proof['effective_options'];p=originalmap[z['source_path']];good=sha(z['source_path'])==z['sha256']==p['RESULT_sha256']and p['apparent_accepted']and proof['input_digest']==z['input_digest']and proof['cell']==z['cell']and proof['downstream_profile']==z['profile']and v['cycles']==z['cycles']==p['cycles']and proof['performance_accepted'];alias=None
 if 'reference_result_path'in v:
  alias={'path':v['reference_result_path'],'sha256':v['reference_result_sha256'],'cohort':v['reference_cohort'],'state':v['state']};av=rd(alias['path']);good &= sha(alias['path'])==alias['sha256']and av['uuid']==v['uuid']and av['cycles']==v['cycles']and av['proof']==proof and all(v['reuse_verification'].values())and v['new_model_starts']==0;aliases.append(alias)
 ck('Original '+z['cohort']+' actualacceptedsource/alias',good)
 refs.append({'path':z['source_path'],'sha256':z['sha256'],'input_digest':z['input_digest'],'cell':z['cell'],'profile':z['profile'],'cohort':z['cohort'],'role':z['source_role'],'alias':alias})
ck('Exactly32 distinct original references; aliases nevernewCH',len(refs)==len({r['path']for r in refs})==32 and len(aliases)==6)
lifecycle=rd(O/'LIFECYCLE_ALL16.json')
for x in lifecycle['rows']:
 key=x['input_digest'],'CH',x['profile'];cycles[key]=x['cycles'];options[key]=x['effective_options'];v=rd(x['RESULT_path']);ck(x['cohort']+' StageII original/repair role isolation',v['scientific_role']=='STAGEII_AUTHORIZED_CH'and not v['original_or_repair_results_replaced']and v['new_contract_only'])
for digest in digests:
 for cell in ['CH','DH']:
  p=options[digest,cell,'P0']
  for prof,n in [('F128','128'),('F256','256')]:
   v=options[digest,cell,prof];diff={k for k in set(p)|set(v)if p.get(k)!=v.get(k)};ck(digest[:8]+cell+prof+'onlyF options fixed',diff=={'-gpgpu_frfcfs_dram_sched_queue_size'}and p['-gpgpu_frfcfs_dram_sched_queue_size']==['64']and v['-gpgpu_frfcfs_dram_sched_queue_size']==[n]and p['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']and p['-gpgpu_cache:dl2']==['S:128:128:16,L:B:m:L:L,A:192:4,32:0,32'])
S=rd(F/'quantitative/STATISTICS.json');ratios={};wide={r['input_digest']:r for r in S['six_cycle_wide_rows']}
for digest in digests:
 w=wide[digest];ck(digest[:8]+'six cycle wide values',all(w[cell+'_'+prof]==cycles[digest,cell,prof]for cell in ['CH','DH']for prof in ['P0','F128','F256']))
 for prof in ['F128','F256']:
  a,b,c,d=[cycles[digest,cell,pr]for cell,pr in [('CH','P0'),('CH',prof),('DH','P0'),('DH',prof)]];r={'S_CH':Fraction(a,b),'S_DH':Fraction(c,d),'R':Fraction(b,d),'R_P0':Fraction(a,c),'I':Fraction(b*c,a*d)};ratios[digest,prof]=r;data=next(x for x in S['per_input_metrics']if x['input_digest']==digest and x['profile']==prof);ck(digest[:8]+prof+' exactinteger rational metric/sign',all(data['exact_ratio_components'][k]=={'numerator':v.numerator,'denominator':v.denominator,'sign_vs1':(v>1)-(v<1)}and math.isclose(data['metrics'][k],float(v),rel_tol=1e-13)for k,v in r.items()))
def compare_summary(st,vals,pop):
 vals=list(vals);return st['n']==st['expected_n']==len(vals)and set(st['population'])==set(pop)and not st['missing']and st['missing_count']==0 and st['positive']==sum(v>1 for v in vals)and st['negative']==sum(v<1 for v in vals)and st['exact_zero']==sum(v==1 for v in vals)and math.isclose(st['GM'],math.exp(sum(math.log(float(v))for v in vals)/len(vals)),rel_tol=1e-13)
def direct(digest,key):
 a,b=[ratios[digest,pr]for pr in ['F128','F256']]
 return Fraction(cycles[digest,'CH','F128'],cycles[digest,'CH','F256'])if key=='CH_F128_over_F256'else Fraction(cycles[digest,'DH','F128'],cycles[digest,'DH','F256'])if key=='DH_F128_over_F256'else b['I']/a['I']
for prof in ['F128','F256']:
 for k,st in S['common_F128_F256_metrics'][prof].items():ck(prof+k+'common8 exactGM/population/signs',compare_summary(st,[ratios[d,prof][k]for d in digests],digests));ck(prof+k+'available uses same8',compare_summary(S['per_F_available_paired'][prof][k],[ratios[d,prof][k]for d in digests],digests))
for k,st in S['direct_F_comparison'].items():ck('DirectF '+k+' common8 exactGM/signs',compare_summary(st,[direct(d,k)for d in digests],digests))
for suite,g in S['suite_groups'].items():
 pop=[d for d in digests if wide[d]['suite']==suite];ck(suite+'fixedsuitepopulation',len(pop)==(3 if suite=='CUDA Samples'else 5)and set(g['expected_inputs'])==set(pop)and set(g['common_population'])==set(pop))
 for prof in ['F128','F256']:
  for k,st in g['common_F128_F256_metrics'][prof].items():ck(suite+prof+k+' commonGM',compare_summary(st,[ratios[d,prof][k]for d in pop],pop));ck(suite+prof+k+' availableGM',compare_summary(g['per_F_available'][prof][k],[ratios[d,prof][k]for d in pop],pop))
 for k,st in g['direct_F_comparison'].items():ck(suite+' direct '+k,compare_summary(st,[direct(d,k)for d in pop],pop))
ck('No missing/winner manipulation: unifiedF common8 fixedorder',S['no_best_per_program_selection']and S['no_missing_imputation']and S['exact_zero_counts_not_float_epsilon']and S['common_F128_F256_population']==digests and S['remaining48_locked'])
report={'schema':'C_FINAL_ALL16_IDENTITY_OWNER_STATISTICS_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_PASS':all(x['PASS']for x in checks),'checks':checks,'source_pins':pins,'original_references':refs,'alias_count':len(aliases),'registry_sha256':sha(regp),'oldStageI_canonical_sha256':oldhash,'live_DTC_model_generations':live,'recomputed_metrics':{prof:{k:S['common_F128_F256_metrics'][prof][k]for k in ['S_CH','S_DH','R','I']}for prof in ['F128','F256']},'new_model_starts':0,'science_or_owner_mutations':0};(O/'IDENTITY_OWNER_STATISTICS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'all_PASS':report['all_checks_PASS'],'failed':[z for z in checks if not z['PASS']],'sha256':sha(O/'IDENTITY_OWNER_STATISTICS.json')}))



