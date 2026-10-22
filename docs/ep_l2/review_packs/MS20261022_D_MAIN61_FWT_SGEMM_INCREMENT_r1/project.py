"""Offline projection of already E-accepted Git metadata. No acceptance or raw reader."""
import json,csv,pathlib,sys,hashlib,math,subprocess
# For reproducibility, run from this worktree root; no filesystem search.
ROOT=pathlib.Path.cwd(); P=ROOT/'docs/ep_l2/review_packs/MS20261022_D_MAIN61_FWT_SGEMM_INCREMENT_r1'
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_study_lane_d'));import full_v2_analysis as full
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
intake=json.loads((P/'INTAKE.json').read_text())
for r in intake['refs']:assert sha((P/r['local_path']).read_bytes())==r['sha256']
points=[];mechanisms=[];identity=[];closures=[];timing=[]
for stem,cohort in [('V4_SGEMM_MAIN61_EXPLORATORY_S_F','INDEPENDENT_MAIN61_SGEMM_FROZEN_TRACE_EXPLORATION'),('V4_FWT_MAIN61_RESTORE_S_F','ORIGINAL_MAIN61_FWT_RESTORATION')]:
 pair=json.loads((P/'E_evidence'/f'{stem}_ACCEPTED_PAIR.json').read_text());met=json.loads((P/'E_evidence'/f'{stem}_EXACT_METRICS.json').read_text());a=pair['accepted_pair'];es=met['endpoints'];assert a['status']=='CURRENT_ACCEPTED' and met['cohort']==cohort
 assert sha((P/'E_evidence'/f'{stem}_ACCEPTED_PAIR.json').read_bytes())==met['accepted_pair_artifact']['sha256']
 x,y=es['left'],es['right'];assert a['cycles_left']==x['cycles'] and a['cycles_right']==y['cycles'];assert x['instructions']==y['instructions'];assert x['identity']['trace_content_sha256']==y['identity']['trace_content_sha256'];assert x['identity']['binary_sha256']==y['identity']['binary_sha256']=='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
 assert (x['profile'],y['profile'])==('S','F')
 row={'workload':x['identity']['workload'],'pair_id':stem,'cohort':cohort,'S_attempt':x['attempt_id'],'F_attempt':y['attempt_id'],'S_cycles':x['cycles'],'F_cycles':y['cycles'],'F_minus_S_cycles':y['cycles']-x['cycles'],'speedup_S_over_F':x['cycles']/y['cycles'],'speedup_percent':100*(x['cycles']/y['cycles']-1),'F_cycle_change_percent':100*(y['cycles']/x['cycles']-1),'instructions_each':x['instructions'],'S_receipt_sha256':x['receipt']['sha256'],'F_receipt_sha256':y['receipt']['sha256'],'S_config_sha256':x['identity']['runtime_config_sha256'],'F_config_sha256':y['identity']['runtime_config_sha256'],'trace_sha256':x['identity']['trace_content_sha256'],'binary':x['identity']['binary_sha256']};points.append(row)
 projected=full.mechanism_table({'pair_id':stem,'workload':row['workload'],'baseline_mechanism_metrics':json.dumps(x['mechanism_metrics']),'variant_mechanism_metrics':json.dumps(y['mechanism_metrics'])})
 for r in projected:r['cohort']=cohort
 mechanisms+=projected
 for side,e in es.items():
  assert e['receipt']==a['endpoints'][side];assert e['cycles']==pair['endpoints'][side]['cycles'];assert e['mechanism_metrics']==pair['endpoints'][side]['mechanism_metrics']
  identity.append({'cohort':cohort,'pair_id':stem,'side':side,**{k:v for k,v in e.items() if k in ['attempt_id','identity','profile','qualification_id','receipt','source_identity','native_exit_receipt']},'raw':pair['endpoints'][side]['raw']})
  closures.append({'cohort':cohort,'pair_id':stem,'attempt_id':e['attempt_id'],'instructions':e['instructions'],'slices':e['slices'],'closure':e['closure'],'workload_termination':e['workload_termination'],'requester_exact_once_audit':e['requester_exact_once_audit'],'source_map':e['source_map'],'bank_P1_peaks':[max(v[f'bank{b}'] for b in range(4)) for v in e['structural_observations']['BANK_PEAK'].values()]})
  # Absence is retained, not filled with the whole-application duration or zero.
  assert pair['endpoints'][side]['kernel_completion'] is None
  timing.append({'attempt_id':e['attempt_id'],'pair_id':stem,'side':side,'kernel_UID_sequence':'UNKNOWN_NOT_EXPORTED','named_kernel_elapsed_cycles':'UNKNOWN_NOT_EXPORTED','per_kernel_mechanism_deltas':'UNKNOWN_NOT_EXPORTED','reported_F_native_snapshot_count':y['mechanism_metrics'].get('commandlist_lifecycle',{}).get('native_snapshot_count','UNKNOWN'),'accepted_pair_kernel_completion_field':None,'whole_application_cycles':e['cycles'],'E_terminal_summary_ref':pair['endpoints'][side]['terminal_summary'],'not_scientific_acceptance_failure':True})
full.csvout(P/'NEW_PAIR_PERFORMANCE.csv',points);full.csvout(P/'NEW_PAIR_TERMINAL_MECHANISMS.csv',mechanisms);put('EXACT_ACCEPTED_IDENTITIES.json',identity);put('ACCEPTED_CLOSURE_PROJECTION.json',closures);put('KERNEL_TIMING_AVAILABILITY.json',timing)
old=ROOT/'docs/ep_l2/review_packs/MS20261021_D_PRIMARY_FOUR_SCIENCE_r1/MAIN_FIVE_PERFORMANCE.csv';prior_git=subprocess.check_output(['git','show','95a3c3ddfb50dbee368f4945582d671cccb09987:'+old.relative_to(ROOT).as_posix()]);assert prior_git==old.read_bytes();prior=list(csv.DictReader(old.open()));assert len(prior)==5 and 'FWT_7_21' not in [r['workload'] for r in prior]
fwt=next(r for r in points if r['workload']=='FWT_7_21');main=[dict(r,cohort='ORIGINAL_MAIN61_PRIOR_ACCEPTED_MAIN') for r in prior]+[fwt];full.csvout(P/'MAIN61_SIX_ACCEPTED_PERFORMANCE.csv',main)
gm=math.exp(sum(math.log(float(r['speedup_S_over_F'])) for r in main)/6)
put('SUMMARY.json',{'E_fetched_HEAD':intake['E_fetched_HEAD'],'new_pairs_consumed':2,'original_MAIN_accepted_pairs':6,'original_MAIN_required_pairs':7,'original_MAIN_accepted_six_subset_GM':gm,'six_subset_speedup_percent':100*(gm-1),'original_seven_MAIN_GM':'UNKNOWN_BTREE_HOLD','SGEMM_independent_exploration':next(r for r in points if r['workload']=='sgemm'),'distinct_measured_workloads':7,'seven_mixed_cohort_GM':'NOT_DEFINED_DO_NOT_COMPUTE','capacity_diagnostic':'UNCHANGED_FIVE_PAIRS_93a9_SEPARATE','raw_reads':0,'trace_reads':0,'native_runs':0,'builds':0,'controller_or_registry_actions':0,'per_kernel_timing':'UNKNOWN_NOT_EXPORTED','old_five_csv_sha256':sha(prior_git),'reused_tool':'full_v2_analysis.mechanism_table / csvout only; no validation/acceptance/launch entry point'})
print(json.dumps({'points':[(r['workload'],r['S_cycles'],r['F_cycles'],r['speedup_percent']) for r in points],'six_subset_GM':gm,'rows':len(mechanisms),'kernel_timing':'UNKNOWN_NOT_EXPORTED'}))
