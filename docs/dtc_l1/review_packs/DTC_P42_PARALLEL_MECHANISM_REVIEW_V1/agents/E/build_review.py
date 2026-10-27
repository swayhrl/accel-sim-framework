"""Read only fixed snapshots, closed receipt metadata and configuration/source files.
Never opens any raw log, trace, periodic CSV, controller or lease. Writes own E directory only.
Run on 174-new using stdin; no simulator imports or execution.
"""
import pathlib,json,hashlib,datetime,re
R=pathlib.Path('/root/data/dtc_hash_downstream18_20261027_v1')
A=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/E')
sources=[];checks=[]
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):
 p=pathlib.Path(p);b=p.read_bytes();sources.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return json.loads(b)
def check(name,value):
 checks.append({'check':name,'pass':bool(value)})
 if not value:raise AssertionError(name)
def write(n,v):
 p=A/n;p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n' if not isinstance(v,str) else v,encoding='utf8')
obs=load(A/'ALLOWED_OBSERVATION_SNAPSHOT.json');orec=load(A/'ALLOWED_OBSERVATION_RECEIPT.json')
prior=load(A/'CLOSED_ACCEPTED_RECEIPTS_SNAPSHOT.json')
snapshot=A/'FINAL_ALLOWED_AUTO_SUMMARY_SNAPSHOT.json'
summary=load(snapshot if snapshot.exists() else R/'analysis/AUTO_SUMMARY.json')
if not snapshot.exists():write('FINAL_ALLOWED_AUTO_SUMMARY_SNAPSHOT.json',summary)
timestamp=datetime.datetime.fromtimestamp(snapshot.stat().st_mtime,datetime.timezone.utc).isoformat()
specs={}
freeze=load(R/'control/FREEZE_MANIFEST.json')
check('freeze_manifest_matches_published_snapshot',sha(R/'control/FREEZE_MANIFEST.json')==obs['freeze_manifest_sha256'])
frozen_hashes={x['path']:x['sha256'] for x in freeze['files']}
for p in sorted((R/'control').glob('E2-DTCHASH18-*_SPEC.json')):
 check('frozen_spec_'+p.name,sha(p)==frozen_hashes[str(p)])
 s=load(p);specs[(s['program'],s['cell'],s['downstream_profile'])]=s
check('exactly_18_frozen_specs',len(specs)==18)
for pg in ['ATAX','MVT','BICG']:
 s=specs[(pg,'CH','P0')];binding=load(s['input_binding_path']);check('input_binding_sha_'+pg,sha(s['input_binding_path'])==s['input_binding_sha256'])
profiles=[]
for cell in ['CH','DH']:
 base=specs[('ATAX',cell,'P0')]['expected_options']
 for profile in ['P0','PQ','PS']:
  s=specs[('ATAX',cell,profile)];opts=s['expected_options'];diff={k:{'P0':base.get(k),'current':opts.get(k)} for k in set(base)|set(opts) if base.get(k)!=opts.get(k)}
  expected={} if profile=='P0' else {'-gpgpu_dram_partition_queues':{'P0':['64:64:64:64'],'current':['64:256:64:64']}} if profile=='PQ' else {'-gpgpu_clock_domains':{'P0':['1410.0:1410.0:1410.0:850.0'],'current':['1410.0:1410.0:1410.0:1700.0']}}
  check(f'{cell}_{profile}_only_authorized_option_diff',diff==expected)
  configs=[]
  for cfg in s['configs']:
   check(f'config_sha_{cell}_{profile}_{pathlib.Path(cfg["path"]).name}',sha(cfg['path'])==cfg['sha256']);configs.append(cfg)
  for pg in ['ATAX','MVT','BICG']:check(f'same_profile_{pg}_{cell}_{profile}',{k:v for k,v in specs[(pg,cell,profile)]['expected_options'].items() if k!='-trace'}=={k:v for k,v in opts.items() if k!='-trace'} and specs[(pg,cell,profile)]['configs']==s['configs'])
  profiles.append({'cell':cell,'profile':profile,'status':'STATIC_CONFIG_AND_FROZEN_SPEC_QUALIFIED','difference_from_P0':diff,'configs':configs,'options':opts})
accepted=[];pending=[]
for key,s in sorted(specs.items()):
 cohort=s['cohort'];state=summary['states'].get(cohort,'PENDING');rp=R/'analysis'/(cohort+'.RESULT.json')
 if state!='PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE':
  pending.append({'program':s['program'],'cell':s['cell'],'profile':s['downstream_profile'],'cohort':cohort,'input_digest':s['input_digest'],'status':state,'cycles':None,'reason':'WAIT_FOR_NATURAL_DONE_STRICT_ARCHIVE_AND_NATIVE_RESTORE'});continue
 rr=load(rp);p=rr['proof'];dp=R/'control/qualification_ledger'/(cohort+'.DONE.json');done=load(dp)
 op=R/'DTC/run/results'/rr['uuid'];exitp=op/'NATIVE_EXIT.json';ex=load(exitp)
 check(cohort+'_done_matches_exit',done==ex and done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'])
 check(cohort+'_accepted',rr['state']==state and p['performance_accepted'] and p['performance_scope']=='NEW_DOWNSTREAM18_ONLY' and rr['new_contract_only'] and not rr['original_or_repair_results_replaced'])
 check(cohort+'_strict_input_and_build',p['input_digest']==s['input_digest'] and p['core_commit']==s['core_commit']==obs['core_commit'] and p['framework_commit']==s['framework_commit']==obs['framework_commit'] and p['binary_sha256']==s['binary_sha256']==obs['binary_sha256'])
 check(cohort+'_resolved_options_match_spec',p['effective_options']==s['expected_options'])
 check(cohort+'_population',p['instructions']==s['expected']['instructions'] and p['CTA']==s['expected']['CTA'] and p['kernel_count']==2 and sum(k['cycles'] for k in p['kernels'])==p['cycles']==rr['cycles'])
 check(cohort+'_archive_restore',rr['archive']['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and rr['archive']['receipt']['source_disposition']=='SOURCE_KEEP')
 check(cohort+'_raw_identity_done_strict',done['raw_sha256']==p['raw_gzip_sha256'] and done['raw_uncompressed_sha256']==p['raw_uncompressed_sha256'])
 acc={'program':s['program'],'cell':s['cell'],'profile':s['downstream_profile'],'cohort':cohort,'uuid':rr['uuid'],'input_digest':s['input_digest'],'cycles':rr['cycles'],'kernels':p['kernels'],'traffic':p['traffic'],'metrics':p['metrics'],'latency_counters':p['latency_counters'],'core_commit':p['core_commit'],'framework_commit':p['framework_commit'],'binary_sha256':p['binary_sha256'],'library_sha256':obs['core_library_sha256'],'raw_gzip_sha256':p['raw_gzip_sha256'],'raw_uncompressed_sha256':p['raw_uncompressed_sha256'],'raw_path':str(op/'raw.log.gz'),'result_path':str(rp),'result_sha256':sha(rp),'DONE_path':str(dp),'DONE_sha256':sha(dp),'archive':rr['archive'],'configs':s['configs'],'numerical_correctness':p['full_application_numerical_values'],'performance_scope':p['performance_scope']}
 accepted.append(acc)
idx={(v['program'],v['cell'],v['profile']):v for v in accepted}
comparisons=[]
for pg in ['ATAX','MVT','BICG']:
 for prof in ['PQ','PS']:
  for cell in ['CH','DH']:
   a=idx.get((pg,cell,'P0'));b=idx.get((pg,cell,prof));row={'program':pg,'cell':cell,'profile':prof,'status':'PENDING','speedup':None,'kernel_speedups':None}
   if a and b:
    check(f'paired_kernel_identities_{pg}_{cell}_{prof}',[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA']) for x in a['kernels']]==[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA']) for x in b['kernels']])
    row.update(status='ACCEPTED_NEW_DOWNSTREAM18_MATCHED',speedup=a['cycles']/b['cycles'],P0_cycles=a['cycles'],profile_cycles=b['cycles'],cycles_change_percent=100*(b['cycles']/a['cycles']-1),cohorts=[a['cohort'],b['cohort']],kernel_speedups=[{'ordinal':ka['ordinal'],'kernel':ka['kernel'],'P0_cycles':ka['cycles'],'profile_cycles':kb['cycles'],'speedup':ka['cycles']/kb['cycles'],'verdict':'EXACT_EQUAL' if ka['cycles']==kb['cycles'] else 'PROFILE_FASTER' if ka['cycles']>kb['cycles'] else 'PROFILE_SLOWER'} for ka,kb in zip(a['kernels'],b['kernels'])],traffic_changes={k:{'P0':a['traffic'][k],'profile':b['traffic'][k],'percent':100*(b['traffic'][k]/a['traffic'][k]-1) if a['traffic'][k] else None} for k in ['L2_accepted_read_32B_sectors','L2_read_payload_bytes','DRAM_issued_read_atoms','DRAM_read_payload_bytes']},latency_counters={'P0':a['latency_counters'],'profile':b['latency_counters'],'definition':'whole_declared_input aggregates, request populations differ; no segment mean subtraction'})
   comparisons.append(row)
relative=[]
for pg in ['ATAX','MVT','BICG']:
 for prof in ['PQ','PS']:
  req=[(pg,c,p) for c,p in [('CH','P0'),('DH','P0'),('CH',prof),('DH',prof)]];missing=[list(x) for x in req if x not in idx];v={'program':pg,'profile':prof,'status':'PENDING' if missing else 'ACCEPTED_NEW_DOWNSTREAM18_MATCHED','definition':f'K_{prof}=(DH_P0/DH_{prof})/(CH_P0/CH_{prof})','K':None,'missing_strict_accepted_cells':missing}
  if not missing:
   ch0,dh0,chp,dhp=[idx[x]['cycles'] for x in req];v.update(K=(dh0/dhp)/(ch0/chp),CH_over_DH_P0=ch0/dh0,CH_over_DH_profile=chp/dhp)
  relative.append(v)
first5=[]
for v in obs['comparisons']:
 slow=1 if v['program'] in ['ATAX','MVT'] else 2
 if v['kernel_ordinal']==slow and v['start_percent']==0 and v['end_percent']==5 and v['left'].endswith('_P0') and v['right'].endswith('_PS'):
  m=obs['source_maps'][v['program']]['kernels'][slow-1];expected=m['active_thread_instructions']*.05
  check(f'first5_semantic_frontier_{v["program"]}_{v["left"]}',all(abs(x['target_work']-expected)<1e-6 for x in [v['source_rows']['left'][-1],v['source_rows']['right'][-1]]))
  first5.append({'program':v['program'],'kernel_ordinal':slow,'left':v['left'],'right':v['right'],'work_frontier_active_thread_instructions':expected,'ratio':v['cycle_ratio'],'source_rows':v['source_rows'],'status':'PROVISIONAL_FIXED_SNAPSHOT_CORE_CYCLE_OBSERVATION_ONLY','whole_input_or_kernel_speedup':False})
fifo=[]
for c in obs['cases']:
 if c['profile']!='PQ':continue
 segs=c.get('segments',[]);seen=[x for x in segs if x.get('metrics') and 'l2_fifo_full_events' in x['metrics']]
 fifo.append({'program':c['program'],'cell':c['cell'],'profile':'PQ','snapshot_acceptance':c['acceptance'],'closed_now':(c['program'],c['cell'],'PQ') in idx,'observed_segments':len(seen),'all_observed_segment_fifo_full_high_zero':bool(seen) and all(x['metrics']['l2_fifo_full_events']['high']==0 for x in seen),'whole_kernel_snapshot_metrics':[{'kernel_ordinal':x['kernel_ordinal'],'cycles':x['cycles'],'l2_fifo_full_events':x['metrics']['l2_fifo_full_events']} for x in c.get('whole_kernel_segments',[]) if x.get('metrics')],'coverage_note':'Observed fixed snapshot only; no assertion about an unobserved tail or pending input.'})
definitions=[]
C=pathlib.Path('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim')
for n,a,b,meaning in [('l2cache.cc',488,497,'The second queue field is L2-to-DRAM FIFO capacity.'),('l2cache.cc',1103,1130,'L2 FIFO-full event admission check; an event count, not exclusive stalled core cycles.'),('l2cache.cc',305,329,'Fixed dram_latency is scheduled against core-cycle counter; PS does not halve this delay.'),('dram_sched.cc',229,251,'avg_mrq interval: dram_req creation to bank assignment; core-cycle timestamps, not full L2/DRAM round trip.'),('dram.cc',164,194,'FRFCFS queue bound and return-queue fullness are distinct constraints.'),('dram.cc',237,244,'dram_req timestamp is GPU core-cycle total.'),('gpu-sim.cc',1456,1470,'DRAM frequency determines DRAM tick period; core, ICNT, L2 clocks stay fixed.'),('mem_latency_stat.cc',351,370,'Printed avg_mrq_latency is total wait divided by selected request count, integer truncated.')]:
  p=C/n;ls=p.read_text().splitlines();definitions.append({'path':str(p),'sha256':sha(p),'lines':[a,b],'meaning':meaning,'excerpt':'\n'.join(f'{i+1}: {ls[i]}' for i in range(a-1,min(b,len(ls))))})
write('COUNTER_SOURCE_DEFINITIONS.json',definitions)
followups=[
 {'id':'PS_NS_MATCH','status':'NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED','goal':'Separate faster command/data opportunity from reductions in absolute DRAM timing delay.','design':'Keep DRAM=1700MHz; double each elapsed-time DRAM-clock parameter from the 850MHz P0 (RCD/RAS/RP/RC/CL/WL/RRD/WR/CDLR/RTPL, bank-group CCDL where applicable), after auditing derived expressions and constraints. Keep core-clock fixed delays such as dram_latency=100 and L2 ROP unchanged. Keep geometry, mapping, request/return queues, scheduler and input fixed.','caveat':'Do not blindly double nbk, nbkgrp or buswidth. Classify tCCD/CCDL and burst/data-command ratio explicitly: preserving all spacing in ns can also remove the intended throughput increase. State chosen sustained bandwidth and absolute-latency contract; this is not achieved by a single clock edit.','minimal_scope':'One strided kernel/input chosen before seeing new performance, both CH and DH, paired with fresh instrumented baseline only if build changes; exact budget to approve after finished18.'},
 {'id':'PQ_X_PS','status':'NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED','goal':'Test interaction between FIFO capacity and DRAM time-domain speed.','design':'2x2 of FIFO64/256 and850/1700MHz; existing P0/PQ/PS are three corners. Only after they close strict accepted, add joint corner for matched CH/DH using identical existing binary/config contract.','interaction_formula':'I_cell=C_PQ*C_PS/(C_P0*C_PQPS); multiplicative independent speedups imply1. Compare I_DH/I_CH. No additive speedup assumption.','minimal_scope':'A preregistered sentinel input (ATAX is informative if accepted PQ regression persists); two new model points CH/DH. Broaden only with new approval.'},
 {'id':'INSTRUMENT_STAGE_WAIT','status':'NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED','goal':'Distinguish FIFO backpressure removal, scheduler waiting, return congestion, L2 replacement/reissue and DTC completion service.','design':'Instrumentation-only build with counters for queue occupancy-cycle sums/high-water marks/full events; request UID+stage enqueue/dequeue timestamps for L2 miss/FIFO, dram-delay, FRFCFS, bank issue/data ready, return FIFO, DTC completion/retirement; per-kernel sums/counts/histograms. Bounded event sampling keyed by stable UID. Never change allocation/arbitration/admission.','qualification':'CPU tests plus at least a matched reference run verifying exact cycles, instructions, CTA and traffic against uninstrumented binary before causal consumption. Capture source hash, observer overhead, RSS/output limits, cross-kernel draining and request-cohort accounting.','minimal_scope':'One CH/DH sentinel pair at P0 and one discriminating perturbation; exact model-start budget requires new approval.'}
]
write('FOLLOWUP_EXPERIMENT_DESIGNS.json',followups)
write('CONFIGURATION_QUALIFICATION.json',{'schema':'DTC_E_CONFIG_QUAL_V1','profiles':profiles,'closed_resolved_option_qualified_cohorts':[v['cohort'] for v in accepted],'live_resolved_options':'NOT_READ_FROM_ACTIVE_RAW; static config/hash qualification only for pending cells'})
write('ACCEPTED_CELL_EVIDENCE.json',accepted)
write('PENDING_CONSUMPTION.json',pending)
data={'schema':'DTC_P42_AGENT_E_REVIEW_V1','observed_UTC':timestamp,'fixed_observation_UTC':obs['observed_UTC'],'accepted_cells':len(accepted),'pending_cells':len(pending),'accepted_input_identity_scope':'whole declared frozen trace; numerical values and full-application capture not newly certified','core_commit':obs['core_commit'],'framework_commit':obs['framework_commit'],'binary_sha256':obs['binary_sha256'],'core_library_sha256':obs['core_library_sha256'],'matched_comparisons':comparisons,'relative_recovery_factors':relative,'PS_first5_audit':first5,'PQ_fifo_snapshot_audit':fifo,'within_profile_CH_over_DH':[{'program':pg,'profile':prof,'status':'ACCEPTED' if (pg,'CH',prof) in idx and (pg,'DH',prof) in idx else 'PENDING','ratio':idx[(pg,'CH',prof)]['cycles']/idx[(pg,'DH',prof)]['cycles'] if (pg,'CH',prof) in idx and (pg,'DH',prof) in idx else None} for pg in ['ATAX','MVT','BICG'] for prof in ['P0','PQ','PS']],'source_inventory':sources,'PS_interpretation':'850->1700 MHz halves DRAM tick duration. Same command timing cycle counts halve corresponding absolute ns delay and change service opportunity. It is a composite frequency/timing sensitivity, not pure bandwidth doubling. Fixed core-clock dram_latency stays unchanged.','mechanism_limits':['L2 FIFO-full disappearance is not proof of scheduler/return-queue waiting disappearance.','avg_mrq_latency is an aggregate over differing request populations; not full round trip or per-segment mean.','Host wall time is not simulated GPU execution cycles.','No old2e3 baseline substitution; all matched baselines must be same new9eed build.','No final-cycle predictions from pending observations.'],'followup_experiment_designs':followups,'new_simulator_starts':0,'controller_or_lease_or_goal_changes':0,'active_raw_reads':0,'trace_reads':0,'tests':checks}
write('PQ_PS_INDEPENDENT_REVIEW.json',data)
lines=['# PQ/PS Independent Review — Agent E','',f'Cutoff: {timestamp}; accepted {len(accepted)}/18, pending {len(pending)}/18. Periodic observations are a fixed {obs["observed_UTC"]} snapshot.','', '## Accepted results','', '| Input | Cell | Perturbation | P0 cycles | Perturbed cycles | P0/perturbed | Cycles change |','|---|---|---|---:|---:|---:|---:|']
for v in comparisons:
 if v['speedup'] is not None:lines.append(f'| {v["program"]} | {v["cell"]} | {v["profile"]} | {v["P0_cycles"]:,} | {v["profile_cycles"]:,} | {v["speedup"]:.6f} | {v["cycles_change_percent"]:+.3f}% |')
lines+=['','These are strict accepted whole declared-input results, backed by successful natural DONE, matching NATIVE_EXIT, strict resolved-option/population checks, archive verification and independent native restore. They are separate from original288 and correctness repair data. They do not newly prove full-application numerical correctness.','', 'PQ is not uniformly beneficial: ATAX CH regresses despite zero FIFO-full events in the observed PQ intervals. MVT CH and BICG CH improve. This supersedes the early first5% “approximately unchanged” observation for whole-input reporting; that early statement remains valid only for its sampled work frontier.','', 'All K_PQ/K_PS values remain PENDING until the matching CH_P0,DH_P0,CH_perturbation,DH_perturbation cells all close. A completed BICG CHPS/DHPS pair alone cannot establish relative recovery from P0. Missing DH baselines are never filled with historical original-build data.','', '## Configuration qualification','', 'All18 frozen specs and24 profile config files match SHA pins. Within each CH or DH family, PQ changes only `-gpgpu_dram_partition_queues`64:64:64:64→64:256:64:64; PS changes only `-gpgpu_clock_domains`1410:1410:1410:850→1410:1410:1410:1700. Closed accepted resolved option dumps match their frozen expected options exactly. Pending cases receive static qualification only, without reading active raw. FRFCFS64, DRAM return192, L2 configuration, geometry, timing-count parameters, mapping and core/ICNT/L2 clocks remain identical within the relevant matched family.','', 'The second partition-queue field is the L2→DRAM FIFO. Enlarging it does not enlarge the FRFCFS scheduler or return queues. PS reduces DRAM tick time from1.17647ns to0.588235ns; e.g. unchanged RCD12 becomes14.1176ns→7.05882ns, RAS28 becomes32.9412ns→16.4706ns. Fixed `dram_latency=100` is scheduled in core-cycle units and remains about70.922ns. Therefore PS is not a pure bandwidth2x test.','', '## Kernel and sampled-work audit','', '| Input/cell/profile | Kernel1 speedup | Kernel2 speedup |','|---|---:|---:|']
for v in comparisons:
 if v['kernel_speedups']:lines.append(f'| {v["program"]}/{v["cell"]}/{v["profile"]} | {v["kernel_speedups"][0]["speedup"]:.6f} ({v["kernel_speedups"][0]["verdict"]}) | {v["kernel_speedups"][1]["speedup"]:.6f} ({v["kernel_speedups"][1]["verdict"]}) |')
lines+=['','The first5% PS comparisons use the same per-kernel active-thread-instruction frontier (3,569,049.6 for the slow strided kernel), and GPU core cycles, not elapsed host time. Sampling interpolates aggregate retirement, not an exact per-warp loop j. Enclosing sample brackets and bounds are retained in JSON. An approximately2x early result does not establish2x kernel or application acceleration. Exact equal complete-kernel cycles are labelled `EXACT_EQUAL`, not unresolved sampling precision. Completed kernels inside still-live inputs remain provisional and are not promoted here.','', '## Queue/traffic interpretation','', 'L2 FIFO-full counts are full-admission observations aggregated across subpartitions, not exclusive core stalled cycles and not latency. Fixed-snapshot observed PQ intervals have zero FIFO-full events. An unobserved tail is not presumed zero. There is no exported periodic FRFCFS/return-queue wait sum/count or causal UID stage ledger, so bottleneck transfer is UNPROVEN. Full accepted L2/DRAM read sectors/bytes, latencies and traffic changes are supplied in JSON. `avg_mrq_latency` measures dram_req construction to FRFCFS bank assignment in core cycles; it excludes earlier L2 FIFO residence and later full completion. Different request populations prevent a latency-only causal explanation.','', '## Designed follow-ups — not executed','']
for f in followups:lines +=[f'- **{f["id"]} — NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED:** {f["goal"]} {f["design"]}']
lines+=['','## Accepted traffic and latency associations','', '| Input / CH change | L2 accepted read traffic | DRAM issued reads | avg_mrq_latency (core cycles) |','|---|---:|---:|---:|']
for v in comparisons:
 if v['speedup'] is not None:
  tc=v['traffic_changes'];lc=v['latency_counters'];lines.append(f'| {v["program"]} / {v["profile"]} | {tc["L2_read_payload_bytes"]["percent"]:+.3f}% | {tc["DRAM_read_payload_bytes"]["percent"]:+.3f}% | {lc["P0"]["avg_mrq_latency"]} → {lc["profile"]["avg_mrq_latency"]} |')
lines+=['','PQ ATAX CH exhibits more DRAM traffic and longer total execution despite lower mean scheduler waiting; MVT CH improves with fewer DRAM reads despite a higher scheduler-wait mean. These facts rule out interpreting avg_mrq_latency alone as an application bottleneck measure. PS improves all three completed CH inputs while issuing substantially more DRAM reads (+31.6% to +66.0%), and mean scheduler wait decreases. Timing, reuse and request population interact; the new traffic totals are observed facts, not proof of a particular L2 eviction/reissue mechanism.','', 'The accepted BICG PS pair is CH 22,474,128 / DH 18,363,200 = 1.223868. It establishes DH faster than CH within this PS contract only; relative restoration K_PS remains PENDING without DH P0.','', '## Reproducibility','',f'Core `{obs["core_commit"]}`; Framework `{obs["framework_commit"]}`; binary SHA256 `{obs["binary_sha256"]}`; core library SHA256 `{obs["core_library_sha256"]}`.','', 'Use `ACCEPTED_CELL_EVIDENCE.json` for every input SHA, cohort/UUID, config SHA, RESULT/DONE SHA, raw path/hash, strict metrics and verified164 archive receipt; `COUNTER_SOURCE_DEFINITIONS.json` for exact source SHA/line ranges; `CONFIGURATION_QUALIFICATION.json` for complete resolved-option contracts; `PENDING_CONSUMPTION.json` for missing cells. Analysis code: `build_review.py`. No raw or trace was opened, no model started, no controller/lease/Goal changed, no original registry altered.','',f'Validation: {len(checks)} assertions passed. Historical English v0.23 remains unchanged.','']
write('PQ_PS_INDEPENDENT_REVIEW.md','\n'.join(lines));write('VALIDATION.json',{'passed':len(checks),'checks':checks})
print(json.dumps({'observed_UTC':timestamp,'accepted':len(accepted),'pending':len(pending),'checks':len(checks),'comparisons':[{k:v[k] for k in ['program','cell','profile','speedup']} for v in comparisons],'output':str(A)},indent=2))
