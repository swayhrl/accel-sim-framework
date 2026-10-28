"""One-shot frozen JSON analysis. No live-state writes, raw scan or dispatch."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,math,pathlib
P=pathlib.Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=load(P/'PRIMARY_SNAPSHOT.json');s=load(P/'SUPPLEMENTAL_SNAPSHOT.json')
anchorpath=P.parent/'partial315_parameter_cases_v1/report.source.json';old=load(anchorpath)
tool=P/'build_report.source.py';assert sha(tool)==d['generator']['sha256']
sp=importlib.util.spec_from_file_location('qualified_source',tool);g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
profiles=[x for x in d['profiles']if x!='P0']
def flat(report):return {r['cohort']:dict(r,input_digest=i,profile=f,cell=c,**{k:report['programs'][i][k]for k in ['program','suite']})for i,fs in report['table'].items()for f,cs in fs.items()for c,r in cs.items()}
current,previous=flat(d),flat(old)
assert len(current)==350 and len(d['programs'])==35
unchanged=[];new=[]
for c,r in current.items():
 if previous[c]['accepted']:
  assert r['accepted'] and previous[c]['result_sha256']==r['result_sha256'];unchanged.append(c)
 elif r['accepted']:new.append(c)
assert len(unchanged)==315
def change(a,b):
 out={}
 for k in sorted(set(a)|set(b)):
  av,bv=a.get(k),b.get(k);numeric=type(av)in(int,float)and type(bv)in(int,float)
  out[k]=dict(P0=av,variant=bv,delta=bv-av if numeric else None,change_pct=100*(bv/av-1)if numeric and av else None,
   pct_status='ZERO_DENOMINATOR'if numeric and av==0 else'AVAILABLE'if numeric else'NONNUMERIC_OR_MISSING')
 return out
pairs=[]
for i,info in d['programs'].items():
 base=d['table'][i]['P0']['DH']
 for f in profiles:
  r=d['table'][i][f]['DH'];paired=base['accepted']and r['accepted']
  if paired:
   for k in ['core_commit','framework_commit','binary_sha256']:assert base[k]==r[k] and r[k]
  ratio=base['cycles']/r['cycles']if paired else None
  assert ratio==d['comparisons'][i][f]['DH_speedup']
  pairs.append(dict(**info,profile=f,paired=paired,DH_self_speedup=ratio,P0=base,variant=r,
   counter_changes=change(base.get('counters')or{},r.get('counters')or{})if paired else None,
   input_binding=d['stream_scopes'].get(i),CH_variant_available=bool(d['table'][i][f].get('CH',{}).get('accepted')),
   relative_DTC_improvement=None))
common=set(d['programs'])
for f in profiles:common&={r['input_digest']for r in pairs if r['profile']==f and r['paired']}
assert common==set(d['fixed_all_profile_common_population']['ALL']['DH_speedup']['population'])
stats={}
for f in profiles:
 stats[f]={}
 for suite in ['ALL']+sorted({v['suite']for v in d['programs'].values()}):
  rs=[r for r in pairs if r['profile']==f and(suite=='ALL'or r['suite']==suite)]
  matched={r['input_digest']:r['DH_self_speedup']for r in rs if r['paired']}
  fixed={i:v for i,v in matched.items()if i in common}
  stats[f][suite]=dict(available=g.aggregate(matched,len(rs)),fixed_common=g.aggregate(fixed,sum(r['input_digest']in common for r in rs)))
  assert stats[f][suite]['available']['GM']==d['statistics'][f][suite]['DH_speedup']['GM']
assert not any(r['CH_variant_available']for r in pairs)
original=load(P/'ORIGINAL_SCAN_M16_SPEC.json');base_spec=load(P/'SCAN_DH_P0_SPEC.json')
sc=s['canonical'];sr=s['result'];pr=sr['proof'];digest=sc['input_digest']
assert sc['scientific_role']=='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'and s['accepted_by_existing_generator']
assert sc['expected_options']==original['expected_options']==pr['effective_options']
assert sc['input_digest']==original['input_digest'] and len(sc['expected_options'])==270
base=d['table'][digest]['P0']['DH']
for k in ['core_commit','framework_commit','binary_sha256']:assert base[k]==pr[k]
scounter=g.counter_projection(pr);scounter['L2_counter_scope']=d['stream_scopes'][digest]['L2_last_printed_scope']
target_diff={k:{'P0':base_spec['expected_options'].get(k),'R2':v}for k,v in sc['expected_options'].items()if v!=base_spec['expected_options'].get(k)}
assert set(target_diff)=={'-gpgpu_cache:dl2'}
supp=dict(cohort=sc['cohort'],uuid=sr['uuid'],role=sc['scientific_role'],accepted=True,cycles=sr['cycles'],
 original_negative_cohort=original['cohort'],original_primary_state=current[original['cohort']]['state'],
 original_primary_cycles=current[original['cohort']]['cycles'],in_primary_GM=False,automatic_union=False,
 same_270_expected_physics_values_as_original_frozen_spec=True,identity_comparison_scope='R2 strict effective options equal expected values declared in both frozen specs; original failed runtime effective options not independently accepted',source_snapshots=s['source_snapshots'],lineage=sc['supplemental_trial_lineage'],
 specification_evidence={'original_M16':{'path':str(pathlib.Path(d['root'])/'control/specs'/(original['cohort']+'.json')),'sha256':sha(P/'ORIGINAL_SCAN_M16_SPEC.json')},
 'DH_P0':{'path':str(pathlib.Path(d['root'])/'control/specs'/(base_spec['cohort']+'.json')),'sha256':sha(P/'SCAN_DH_P0_SPEC.json')}},
 input_digest=digest,input_binding=d['stream_scopes'][digest],P0=base,descriptive_DH_P0_over_R2=base['cycles']/sr['cycles'],
 counters=scounter,counter_changes=change(base['counters'],scounter),target_option_diff_from_P0=target_diff,
 archive=sr['archive'],raw_gzip_sha256=pr['raw_gzip_sha256'],raw_uncompressed_sha256=pr['raw_uncompressed_sha256'],
 original_native_strict_inherited=True,fresh_native_restore_repeated=False)
o=dict(schema='RESULTS_REFRESH_20261028_V1',snapshot_utc=d['utc'],source_commit_at_request='2b545e7f54b0111a17c1ee1e5d124bd9acf1ee3d',
 sources=dict(primary_snapshot_sha256=sha(P/'PRIMARY_SNAPSHOT.json'),supplemental_snapshot_sha256=sha(P/'SUPPLEMENTAL_SNAPSHOT.json'),
 generator=d['generator'],anchor315_path=str(anchorpath),anchor315_sha256=sha(anchorpath),analysis_script_sha256=sha(pathlib.Path(__file__))),
 primary=dict(planned_cells=350,programs=35,state_counts=d['state_counts'],accepted=sum(r['accepted']for r in current.values()),
 raw_original_negative_preserved=True,unchanged_accepted315_result_sha256_verified=len(unchanged),newly_accepted=[current[c]for c in new],
 fixed_common_population=sorted(common),statistics=stats,all_cells=list(current.values()),pairs=pairs,
 no_nonP0_CH=True,relative_improvement_unavailable=True),supplemental=supp,
 limitations=['One-shot stable individual files, not an atomic experiment-wide transaction.',
 'Inherited accepted RESULT/strict/archive identities; no new native restore or full effective-options replay for primary.',
 'No raw log scan, new simulation, retries, registration, policy change or second controller.',
 'Different available populations are not final35 comparisons; no per-program best GM.',
 'Counter associations do not prove causal critical path or occupancy; missing not zero.',
 'Last-printed MRQ is not weighted whole-application latency; dramfull labels ICNT-to-memory blocking.',
 'Original negative remains unaccepted; R2 never supplies a primary M16 cell or GM.'])
write('ANALYSIS.json',o)
write('EVIDENCE.json',o)
lines=['# Accepted-results refresh — frozen 2026-10-28 18:09 CST',
f"Snapshot UTC `{d['utc']}`. **Primary {o['primary']['accepted']}/350 accepted** = 310 new runs + 6 references; 12 confirmed live, 21 pending, and original scan/M16 unaccepted technical negative. **Supplemental R2 accepted separately: {sr['cycles']:,} cycles.** This is one read-only analysis invocation, not an analysis daemon. Counts are frozen, not live promises.",
'## Uniform DH sensitivity and coverage',
f"DH self speedup = DH P0 / DH variant. Fixed intersection across all eight profiles is **{len(common)} programs**; available sets vary. No accepted non-P0 CH exists, so CH speedup, variant CH/DH and relative DTC improvement are unavailable. Neither table ranks a final 35-program winner.",
'| Profile | Available n/35 | GM | + / = / - | Missing | Fixed common30 GM |',
'|---|---:|---:|---:|---:|---:|']
for f,ss in stats.items():
 a,c=ss['ALL']['available'],ss['ALL']['fixed_common'];lines.append(f"| {f} | {a['n']}/35 | {a['GM']:.6f} | {a['positive']} / {a['neutral']} / {a['negative']} | {a['missing_n']} | {c['GM']:.6f} |")
lines+=['All previous315 accepted RESULT SHAs match the fixed published315 anchor. The only newly accepted primary cell in this snapshot is CUTCP DH-F128. Full per-suite populations, GMs, sign counts and every missing identity are in ANALYSIS.json; the following suite table preserves coverage explicitly.',
'| Suite | E384 n / GM | E768 n / GM | M8 n / GM | M16 n / GM | Q64 n / GM | Q128 n / GM | F128 n / GM | F256 n / GM |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for suite in [s for s in stats[profiles[0]]if s!='ALL']:
 lines.append('| '+suite+' | '+' | '.join(f"{stats[f][suite]['available']['n']}/{stats[f][suite]['available']['expected_n']} / {stats[f][suite]['available']['GM']:.6f}"for f in profiles)+' |')
lines+=['## Every frozen program, one uniform profile per column',
'All ratios below are DH-self. `—` means not yet paired accepted, never 1.0 or zero. The machine-readable pairs retain full input/binding SHA, suite, cohort, UUID, cycles, RESULT path/SHA, source Core/Framework/binary, scope and counters. No per-program best values are combined into a GM.',
'| Program / suite | E384 | E768 | M8 | M16 | Q64 | Q128 | F128 | F256 |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for i,inf in sorted(d['programs'].items(),key=lambda x:(x[1]['suite'],x[1]['program'])):
 vals=[d['comparisons'][i][f]['DH_speedup']for f in profiles]
 lines.append('| '+inf['program']+' / '+inf['suite']+' | '+' | '.join('—'if v is None else f'{v:.6f}'for v in vals)+' |')
lines+=['| Uniform profile | Two strongest observed positives | Two strongest observed negatives |',
 '|---|---|---|']
for f in profiles:
 pos=sorted([r for r in pairs if r['profile']==f and r['paired']and r['DH_self_speedup']>1],key=lambda r:-r['DH_self_speedup'])[:2]
 neg=sorted([r for r in pairs if r['profile']==f and r['paired']and r['DH_self_speedup']<1],key=lambda r:r['DH_self_speedup'])[:2]
 labels=lambda rs:', '.join(f"{r['program']} {r['DH_self_speedup']:.6f}x"for r in rs)or'none'
 lines.append(f'| {f} | {labels(pos)} | {labels(neg)} |')
lines+=['## Strongest observed cases — descriptive partial results',
'F256 helps convolutionSeparable **1.422263x**, scan **1.283635x**, 2DCONV **1.078012x**; it regresses vectorAdd **0.919938x**, MVT **0.988434x**, BICG **0.993156x**. F128 and F256 have the same positive/negative counts (7/6), but different program sets: vectorAdd and GESUMMV are positive for F128 and negative for F256, while ATAX and scalarProd are negative for F128 and positive for F256; adding flat CUTCP changes its available GM from 1.013004 to **1.012595**, without changing any existing result or its common30 GM **1.008535**. F256 remains 1.019762 on available31 and 1.011969 on common30.',
'ATAX E384/E768 are 1.028813x, F256 1.017823x, but Q128 0.943917x. MVT remains mostly flat-to-negative; BICG M16 is 1.012241x while M8 is 0.967226x. 3MM/GEMM and particlefilter_naive are flat across their complete DH scans. Larger entries or queues are not universally beneficial.',
'## New CUTCP and separate R2',
'**Fact — CUTCP F128:** 4,490,473 -> 4,490,473 cycles, exactly 1.0x. Its recorded DRAM reads, L2 read misses, reservation failures and dramfull are all explicitly zero; L2 reads stay 1,605,996; MRQ average is missing. Percentage nulls on zero counters mean zero denominator, not missing counts. F256 is still RUNNING_CONFIRMED at acquisition; M16 also running and M8/Q64/Q128 pending. No F256 value is inferred.',
f"**Fact — supplemental scan R2:** UUID `{sr['uuid']}`, strict accepted {sr['cycles']:,} cycles, the same 270 expected physics option values declared by the frozen specs, with the same input/Core/Framework/binary identity; this is a declared-spec comparison, not validation of the failed M16 run’s actual effective options. Its separately descriptive DH P0/R2 is **{supp['descriptive_DH_P0_over_R2']:.6f}x**, with P0 {base['cycles']:,} cycles. Original M16 remains absent/unaccepted in primary; no union is authorized and primary M16 still has30 pairs, not31. R2's archive contains23 independently verified entries; raw/RESULT/archive/lineage SHAs are in ANALYSIS.json and SUPPLEMENTAL_SNAPSHOT.json.",
'**Association — R2 vs P0:** DRAM reads are nearly unchanged (21,712,700 -> 21,712,552), L2 reads 21,859,084 -> 21,852,796, and the last MRQ average 184 -> 183. This does not identify why the independent M16 run is slightly slower. Its IO-qualified new launch and preserved negative lineage establish an independent result, not a repair correctness replacement.',
'## What counters do and do not establish',
'Observed F improvements often coexist with *higher* last-printed MRQ averages: convolutionSeparable F256 321 -> 905 and scan 184 -> 628. vectorAdd F256 has unchanged DRAM reads and roughly51% fewer reservation-fail events yet slower completion. ATAX F256 has 2.213% fewer DRAM reads and 3.100% fewer reservation-fail events with 1.017823x speedup; MVT/BICG F256 still regress. These are associations, not causal cycle decomposition or proof of queue occupancy/criticality. Specific MSHR reasons are absent, not zero.',
'3MM/GEMM DRAM counters explicitly remain0; their percent changes are undefined zero-denominator values. MRQ is missing. Kernel/preloaded trace statistics cannot establish zero DRAM traffic for the real application. GEMM (PolyBench) and sgemm (Parboil) retain different input identities.',
'The current pattern supports the already registered V3 rationale for full35 entries×FRFCFS, merge×sending/queue and wide/ablation tests; flat OFAT does not disprove interaction. This report adds no proposal, changes no stage gate and selects no final configuration. Required full35 parent evidence, distinct moderate/high CH/DH validation, original-negative disposition and the existing budget/owner remain authoritative.',
'## Reproduction and provenance',
f"`collect.py` called qualified generator SHA `{d['generator']['sha256']}` once, with every JSON source SHA retained in PRIMARY_SNAPSHOT.json. `analyze_refresh.py` only reads frozen JSON plus the fixed315 anchor (commit280abe32e1090366cfaabaf5895662300c2f9f27). Request-time GitHEAD was2b545e7f54b0111a17c1ee1e5d124bd9acf1ee3d; this independent output is not yet a new Git commit. Main alone publishes it.",
'Stream scope follows the existing header/binding qualification: whole-declared-trace L2 counters only under complete single-stream scope, otherwise null; DRAM counters are global cumulative. No huge raw log, native restore or prior test was rerun. Source files are individually coherent snapshots, not one atomic transaction across the controller. No live registry/controller/source or scientific identity was modified. `EVIDENCE.json` is the canonical machine-readable handoff; ANALYSIS.json is an identical alias. This directory is a frozen one-shot snapshot; subsequent results belong in a new directory, never by rerunning collect.py here.']
body=lines[0]
for previous,line in zip(lines,lines[1:]):body+=('\n'if previous.startswith('|')and line.startswith('|')else'\n\n')+line
(P/'REPORT.md').write_text(body+'\n',encoding='utf-8')
manifest=dict(schema='RESULTS_REFRESH_MANIFEST_V1',snapshot_utc=d['utc'],files=[dict(name=x.name,sha256=sha(x),bytes=x.stat().st_size)for x in sorted(P.iterdir())if x.is_file()and x.name!='MANIFEST.json'])
write('MANIFEST.json',manifest)
print(json.dumps(dict(primary_accepted=o['primary']['accepted'],new_primary=new,common=len(common),R2_cycles=sr['cycles'],R2_descriptive_speedup=supp['descriptive_DH_P0_over_R2'],files={x['name']:x['sha256']for x in manifest['files']if x['name']in['REPORT.md','ANALYSIS.json']})))
