"""Read-only point-in-time accepted-cycle analysis. No dispatch imports."""
import datetime,hashlib,json,math,pathlib,statistics,subprocess
ROOT=pathlib.Path(__file__).parent
REMOTE_ROOT='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/A/current_results_analysis_v1'
remote=r'''
import datetime,hashlib,json,pathlib
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):
 b=p.read_bytes();return json.loads(b),{'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
matrix,mp=read(R/'control/MATRIX_CURRENT.json');summary,sp=read(R/'analysis/AUTO_SUMMARY.json');batch,bp=read(R/'analysis/BATCH_STATE.json')
paths=sorted((R/'analysis').glob('*.RESULT.json'));results=[]
keys=['status','performance_accepted','input_digest','program','suite','cell','profile','cycles','instructions','CTA','kernel_count','core_commit','framework_commit','binary_sha256','raw_gzip_sha256','raw_uncompressed_sha256','uuid','performance_scope']
for p in paths:
 x,src=read(p);proof=x.get('proof',{});opts=proof.get('effective_options',{})
 out={k:v for k,v in x.items() if k not in ['archive','proof']};out['source']=src;out['proof']={k:proof.get(k) for k in keys}
 out['proof']['effective_target_options']={k:opts.get(k) for k in ['-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size','-gpgpu_clock_domains','-gpgpu_dram_partition_queues']}
 out['proof']['effective_options_canonical_sha256']=hashlib.sha256(json.dumps(opts,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out['archive_status']=x.get('archive',{}).get('receipt',{}).get('status')
 out['raw_gzip_path']=str(R/'DTC/run/results'/x.get('uuid','UNKNOWN')/'raw.log.gz')
 if x.get('reference_result_path'):out['raw_gzip_path']=str(pathlib.Path(x['reference_result_path']).parent.parent/'DTC/run/results'/x['uuid']/'raw.log.gz')
 results.append(out)
print(json.dumps({'capture_start_utc':start,'capture_end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matrix':matrix,'matrix_source':mp,'summary_state_counts':summary['state_counts'],'summary_utc':summary['utc'],'summary_source':sp,'batch':batch,'batch_source':bp,'results':results}))
'''
p=subprocess.run(['ssh','hrl-174-new','python3','-'],input=remote.encode(),capture_output=True,timeout=100,check=True)
snapshot=json.loads(p.stdout);(ROOT/'SOURCE_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
matrix=snapshot['matrix'];points=matrix['points'];profiles=[p for p in matrix['initial_profiles'] if p!='P0'];bycohort={p['cohort']:p for p in points}
programs={p['input_digest']:{'program':p['program'],'suite':p['suite'],'input_digest':p['input_digest'],'expected':p['expected']} for p in points}
accepted={};states={};validation=[]
for r in snapshot['results']:
 state=r.get('state');states[state]=states.get(state,0)+1
 if state not in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START']:continue
 pt=bycohort[r['cohort']];pf=r['proof'];errs=[]
 if not isinstance(r.get('cycles'),int) or r['cycles']<=0:errs.append('invalid_cycles')
 if pf['cycles']!=r['cycles']:errs.append('proof_cycle_mismatch')
 if pf['input_digest']!=pt['input_digest'] or pf['cell']!=pt['cell']:errs.append('identity_mismatch')
 if pf['core_commit']!='9eedb3131937748f0492fa83aad37d3691118d70':errs.append('core_mismatch')
 if pf['framework_commit']!='02775fd795cde5aae1480d81cee6eb481d0a08f4':errs.append('framework_mismatch')
 if pf['binary_sha256']!='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d':errs.append('binary_mismatch')
 if pf['instructions']!=pt['expected']['instructions'] or pf['CTA']!=pt['expected']['CTA'] or pf['kernel_count']!=pt['expected']['kernels']:errs.append('population_mismatch')
 if state=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE' and pf['performance_accepted'] is not True:errs.append('not_performance_accepted')
 if state=='REFERENCE_ACCEPTED_NO_NEW_START' and not all(r['reuse_verification'].values()):errs.append('reuse_not_verified')
 validation.append({'cohort':r['cohort'],'errors':errs})
 if errs:continue
 accepted[(pt['input_digest'],pt['cell'],pt['profile'])]=r

def stat(rows,denom=35):
 vals=[r['value'] for r in rows]
 return {'n':len(vals),'target_n':denom,'missing_n':denom-len(vals),'GM':math.exp(sum(map(math.log,vals))/len(vals)) if vals else None,'median':statistics.median(vals) if vals else None,'positive':sum(v>1 for v in vals),'negative':sum(v<1 for v in vals),'equal':sum(v==1 for v in vals),'minimum':min(vals) if vals else None,'maximum':max(vals) if vals else None,'population':[r['input_digest'] for r in rows],'values':rows}

rows=[]
for digest,meta in sorted(programs.items(),key=lambda kv:kv[1]['program'].lower()):
 for profile in ['P0',*profiles]:
  a=accepted.get((digest,'DH','P0'));b=accepted.get((digest,'DH',profile));c=accepted.get((digest,'CH','P0'));d=accepted.get((digest,'CH',profile))
  sdh=a['cycles']/b['cycles'] if a and b else None;sch=c['cycles']/d['cycles'] if c and d else None
  rows.append({**meta,'profile':profile,'DH_P0_cycles':a['cycles'] if a else None,'DH_variant_cycles':b['cycles'] if b else None,'DH_speedup':sdh,'CH_P0_cycles':c['cycles'] if c else None,'CH_variant_cycles':d['cycles'] if d else None,'CH_speedup':sch,'relative_DTC_improvement':sdh/sch if sdh and sch else None,'CH_over_DH_same_profile':d['cycles']/b['cycles'] if b and d else None,'matched_quad':bool(a and b and c and d),'DH_result_source':b['source'] if b else None,'P0_result_source':a['source'] if a else None})
aggregates={}
for profile in profiles:
 profile_rows=[r for r in rows if r['profile']==profile];groups={}
 for suite in ['ALL',*sorted({p['suite'] for p in programs.values()})]:
  rr=[r for r in profile_rows if suite=='ALL' or r['suite']==suite];n=len(rr);m={}
  for metric in ['DH_speedup','CH_speedup','relative_DTC_improvement','CH_over_DH_same_profile']:
   m[metric]=stat([{'program':r['program'],'suite':r['suite'],'input_digest':r['input_digest'],'value':r[metric]} for r in rr if r[metric] is not None],n)
  groups[suite]=m
 aggregates[profile]=groups
complete=set(programs)
for profile in profiles:complete&={r['input_digest'] for r in rows if r['profile']==profile and r['DH_speedup'] is not None}
common={p:stat([{'program':r['program'],'suite':r['suite'],'input_digest':r['input_digest'],'value':r['DH_speedup']} for r in rows if r['profile']==p and r['input_digest'] in complete]) for p in profiles}
pairwise={}
for a in profiles:
 for b in profiles:
  if a>=b:continue
  aset={r['input_digest'] for r in rows if r['profile']==a and r['DH_speedup'] is not None};bset={r['input_digest'] for r in rows if r['profile']==b and r['DH_speedup'] is not None};intersection=aset&bset
  pairwise[a+'__'+b]={'profileA':a,'profileB':b,'population':sorted(intersection),'n':len(intersection),'A_GM':stat([{'input_digest':r['input_digest'],'value':r['DH_speedup']} for r in rows if r['profile']==a and r['input_digest'] in intersection])['GM'],'B_GM':stat([{'input_digest':r['input_digest'],'value':r['DH_speedup']} for r in rows if r['profile']==b and r['input_digest'] in intersection])['GM']}
sensitive=[];equal=[];no_base=[]
for digest,meta in programs.items():
 rr=[r for r in rows if r['input_digest']==digest and r['profile']!='P0'];observed=[r for r in rr if r['DH_speedup'] is not None]
 item={**meta,'observed_profile_count':len(observed),'missing_profiles':[r['profile'] for r in rr if r['DH_speedup'] is None],'speedups':{r['profile']:r['DH_speedup'] for r in rr}}
 if any(r['DH_speedup']!=1 for r in observed):sensitive.append(item)
 elif observed:equal.append(item)
 else:no_base.append(item)
baseline={}
for suite in ['ALL',*sorted({p['suite'] for p in programs.values()})]:
 rr=[r for r in rows if r['profile']=='P0' and (suite=='ALL' or r['suite']==suite)]
 baseline[suite]=stat([{'program':r['program'],'suite':r['suite'],'input_digest':r['input_digest'],'value':r['CH_over_DH_same_profile'],'CH_P0_cycles':r['CH_P0_cycles'],'DH_P0_cycles':r['DH_P0_cycles']} for r in rr if r['CH_over_DH_same_profile'] is not None],len(rr))
out={'schema':'DTC_L2_MLP_AGENT_A_CURRENT_RESULTS_V1','capture_start_utc':snapshot['capture_start_utc'],'capture_end_utc':snapshot['capture_end_utc'],'source_snapshot_sha256':hashlib.sha256((ROOT/'SOURCE_SNAPSHOT.json').read_bytes()).hexdigest(),'matrix_source':snapshot['matrix_source'],'summary_source':snapshot['summary_source'],'batch_source':snapshot['batch_source'],'immutable_results_seen_n':len(snapshot['results']),'accepted_states':states,'accepted_validated_n':len(accepted),'matrix_cells_n':len(points),'pending_or_unaccepted_cells_n':len(points)-len(accepted),'running_snapshot_n':len(snapshot['batch']['running']),'summary_state_counts_independent_timestamp':snapshot['summary_state_counts'],'source_validation':validation,'validation_errors':[v for v in validation if v['errors']],'aggregates':aggregates,'P0_CH_over_DH_paired_subset':baseline,'all_profiles_common_population':{'n':len(complete),'population':sorted(complete),'profiles':common},'profile_pairwise_same_population':pairwise,'sensitive_observed':sensitive,'exactly_cycle_equal_observed':equal,'no_DH_pair_yet':no_base,'full_table':rows,'uniform_profile_policy':'No per-input best-of values; missing values null; comparisons across profiles use explicit same-input intersection. All subgroup statistics are incomplete frozen-trace subsets, not full35 finalGM.','matched_CH_nonP0_n':sum(r['matched_quad'] for r in rows if r['profile']!='P0'),'model_launches':0}
(ROOT/'ANALYSIS.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
tz=datetime.timezone(datetime.timedelta(hours=8));ts=datetime.datetime.fromisoformat(snapshot['capture_end_utc']).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S CST')
report=['# Agent A current uniform L2-factor cycle analysis','',f'Snapshot: **{ts}**. Read-only analysis; zero model launches or registrations.',
 '',f"Accepted source receipts: **{len(accepted)}/{len(points)}** ({states}). Running snapshot: {len(snapshot['batch']['running'])}. Sources read over {snapshot['capture_start_utc']}–{snapshot['capture_end_utc']}; atomic per-file reads, not a global filesystem transaction. AUTO_SUMMARY is an independently timestamped cross-check, not the source of raw cycles.",
 '', '## Uniform-profile DH speedups','', 'Speedup=DH_P0/DH_variant, >1 faster. Each row has its own explicit population; unequal row populations are not a ranking.', '', '|Profile|Pairs/35|GM|Median|+/equal/−|Min–max|','|---|---:|---:|---:|---:|---:|']
for p in profiles:
 s=aggregates[p]['ALL']['DH_speedup'];f=lambda x:'null' if x is None else f'{x:.9f}'
 report.append(f"|{p}|{s['n']}/35|{f(s['GM'])}|{f(s['median'])}|{s['positive']}/{s['equal']}/{s['negative']}|{f(s['minimum'])}–{f(s['maximum'])}|")
report+=['',f"Common population across **all8** profiles: **{len(complete)}/35**. "+', '.join(programs[d]['program'] for d in sorted(complete)) +'.',
 'Same-common-population GM: '+', '.join(p+'='+str(common[p]['GM']) for p in profiles)+'.',
 '', f"Non-P0 matched CH/DH quads: **{out['matched_CH_nonP0_n']}**. Missing CH variants remain null; neither CH system gains nor relative DTC improvements can yet be claimed.",
 '', '## P0 CH/DH absolute-performance paired subset','',
 'This is a partially completed same-build P0 input subset, not the full suite. CH/DH>1 means DTC is faster. It is distinct from DH_P0/DH_variant above.',
 '', '|Suite|Pairs/expected|GM CH/DH|Median|DTC faster/equal/slower|','|---|---:|---:|---:|---:|']
for suite,s in baseline.items():
 report.append(f"|{suite}|{s['n']}/{s['target_n']}|{s['GM']}|{s['median']}|{s['positive']}/{s['equal']}/{s['negative']}|")
report+=['','|Program|CH P0 cycles|DH P0 cycles|CH/DH|','|---|---:|---:|---:|']
for r in baseline['ALL']['values']:report.append(f"|{r['program']}|{r['CH_P0_cycles']}|{r['DH_P0_cycles']}|{r['value']:.9f}|")
report+=['', 'Exact input identities for this subset: '+', '.join(r['program']+' `'+r['input_digest']+'`' for r in baseline['ALL']['values'])+'.',
 '', '## Program results and what remains unknown','']
for x in sorted(equal,key=lambda r:r['program'].lower()):report.append(f"- {x['program']} ({x['suite']}, `{x['input_digest']}`): all {x['observed_profile_count']} available paired factor results are **exactly equal integer cycles** to P0; missing: {', '.join(x['missing_profiles']) or 'none'}. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.")
for x in sensitive:report.append(f"- Sensitive observed: {x['program']} `{x['input_digest']}`: {x['speedups']}.")
report+=['', 'No paired data yet for: '+', '.join(sorted(x['program'] for x in no_base))+'.',
 '', 'The outstanding PolyBench matrix/strided kernels, larger Rodinia and other pending programs may change both GM and which uniform factor is promising. ATAX/MVT/BICG entries are not inferred from old PQ or PS; those are different factors. In particular, 3MM/GEMM and 2DCONV/3DCONV must finish before judging preserved Hash gains or new concurrency benefits. None are skipped because current short/fast inputs appear neutral.',
 '', '## Structural overhead and selection boundaries','',
 'Fixed data capacity10MiB, 40 L2 subpartitions, 20 DRAM/controller objects. Logical formulas: MSHR atom-key entries40E; request-reference upper bound40EM (merge includes first request); configured miss slots40Q; FRFCFS request slots20F. Physical area and actual queue occupancy are unknown.',
 'E384/E768 double/quadruple baseline MSHR keys (15360/30720 versus7680). M8/M16 double/quadruple the per-key request list bound. Q64/Q128 double/quadruple configured miss slots (2560/5120 versus1280). F128/F256 double/quadruple FRFCFS slots (2560/5120 versus1280) AND increase shared credits/controller from255 to319/447. Partition FIFOs and DRAM850MHz stay fixed.',
 'No final uniform candidate, plateau, physical upper bound or boundary-extension decision is justified by an incomplete subset with unchanged cycles. Continue the already registered matrix; use all applicable frozen inputs and matched CH verification before promotion.',
 '', '## Evidence','',
 f"- Matrix `{snapshot['matrix_source']['path']}` SHA256 `{snapshot['matrix_source']['sha256']}`.",
 f"- Summary `{snapshot['summary_source']['path']}` SHA256 `{snapshot['summary_source']['sha256']}` (timestamp {snapshot['summary_utc']}).",
 f"- Full captured receipt metadata and per-result path/SHA/raw gzip SHA: `SOURCE_SNAPSHOT.json`, SHA256 `{out['source_snapshot_sha256']}`.",
 '- Every per-program raw-cycle pair and exact input SHA is in `ANALYSIS.json/full_table`; the source receipt path/SHA accompanies each accepted cycle. Missing/unfinished values are null.',
 f"- Accepted identity: Core `{matrix.get('core_commit','9eedb3131937748f0492fa83aad37d3691118d70')}`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`.",
 '- `../PARAMETER_CONTRACT.json` supplies exact source-file SHA and line ranges for parser, MSHR key/merge, miss admission, and credits coupling.',
 f"- Source validation errors: **{len(out['validation_errors'])}**. Historical results, repairs, original ledgers, controllers and budgets unchanged."]
(ROOT/'REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
print(json.dumps({'capture':ts,'accepted':len(accepted),'running':len(snapshot['batch']['running']),'paired_profiles':{p:{k:v for k,v in aggregates[p]['ALL']['DH_speedup'].items() if k not in ['population','values']} for p in profiles},'P0_absolute':{k:v for k,v in baseline['ALL'].items() if k not in ['population','values']},'common_n':len(complete),'sensitive':sensitive,'errors':out['validation_errors']}))
