"""Frozen JSON arithmetic only. Does not refresh state, run tests or touch Git."""
import sys
sys.dont_write_bytecode=True
import copy,hashlib,importlib.util,json,pathlib,math
P=pathlib.Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
d=load(P/'PRIMARY_SNAPSHOT.json');s=load(P/'SUPPLEMENTAL_SNAPSHOT.json');anchor=P.parent/'results_refresh_20261028_v2/PRIMARY_SNAPSHOT.json';old=load(anchor)
tool=P/'build_report.source.py';assert sha(tool)==d['generator']['sha256']
sp=importlib.util.spec_from_file_location('qualified',tool);g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def flatten(report):return {r['cohort']:dict(r,program=report['programs'][i]['program'],suite=report['programs'][i]['suite'],input_digest=i,profile=f,cell=c)for i,fs in report['table'].items()for f,cs in fs.items()for c,r in cs.items()}
now,before=flatten(d),flatten(old);assert len(now)==350 and len(d['programs'])==35
unchanged=[c for c,r in before.items()if r['accepted']]
assert len(unchanged)==316 and all(now[c]['accepted']and now[c]['result_sha256']==before[c]['result_sha256']for c in unchanged)
new=[r for c,r in now.items()if r['accepted']and not before[c]['accepted']]
profiles=[f for f in d['profiles']if f!='P0'];pairs=[]
def changes(a,b):
 result={}
 for k in sorted(set(a)|set(b)):
  av,bv=a.get(k),b.get(k);numeric=type(av)in(int,float)and type(bv)in(int,float)
  result[k]=dict(P0=av,variant=bv,delta=bv-av if numeric else None,change_pct=100*(bv/av-1)if numeric and av else None,
   pct_status='ZERO_DENOMINATOR'if numeric and av==0 else'AVAILABLE'if numeric else'NONNUMERIC_OR_MISSING')
 return result
for i,info in d['programs'].items():
 base=d['table'][i]['P0']['DH']
 for f in profiles:
  r=d['table'][i][f]['DH'];paired=base['accepted']and r['accepted'];ratio=base['cycles']/r['cycles']if paired else None
  assert ratio==d['comparisons'][i][f]['DH_speedup']
  if paired:
   for k in ['core_commit','framework_commit','binary_sha256']:assert base[k]==r[k]and r[k]
  pairs.append(dict(**info,profile=f,paired=paired,DH_self_speedup=ratio,P0=base,variant=r,input_binding=d['stream_scopes'][i],
   counter_changes=changes(base.get('counters')or{},r.get('counters')or{})if paired else None))
common=set(d['programs'])
for f in profiles:common&={r['input_digest']for r in pairs if r['profile']==f and r['paired']}
assert common==set(d['fixed_all_profile_common_population']['ALL']['DH_speedup']['population'])
stats={}
for f in profiles:
 stats[f]={}
 for suite in ['ALL']+sorted({r['suite']for r in pairs}):
  rs=[r for r in pairs if r['profile']==f and(suite=='ALL'or r['suite']==suite)]
  values={r['input_digest']:r['DH_self_speedup']for r in rs if r['paired']}
  fixed={i:v for i,v in values.items()if i in common}
  stats[f][suite]=dict(available=g.aggregate(values,len(rs)),fixed_common=g.aggregate(fixed,sum(r['input_digest']in common for r in rs)))
  assert stats[f][suite]['available']['GM']==d['statistics'][f][suite]['DH_speedup']['GM']
assert not any(d['table'][i][f].get('CH',{}).get('accepted')for i in d['table']for f in profiles)
sr=s['result'];sc=s['canonical'];digest=sc['input_digest'];base=d['table'][digest]['P0']['DH'];counter=g.counter_projection(sr['proof'])
counter['L2_counter_scope']=d['stream_scopes'][digest]['L2_last_printed_scope']
supp=dict(accepted=s['accepted_by_existing_generator'],cohort=sc['cohort'],uuid=sr['uuid'],cycles=sr['cycles'],role=sc['scientific_role'],input_digest=digest,
 primary_member=False,automatic_union=False,original_negative_replaced=False,descriptive_DH_P0_over_R2=base['cycles']/sr['cycles'],P0=base,
 counters=counter,counter_changes=changes(base['counters'],counter),source_snapshots=s['source_snapshots'],lineage=sc['supplemental_trial_lineage'],archive=sr['archive'],
 option_identity_scope='Expected physics values declared by frozen specs; failed original runtime actual effective options not independently accepted. R2 own strict accepted identity inherited.')
o=dict(schema='RESULTS_REFRESH_20261028_V3',snapshot_utc=d['utc'],accepted_primary=sum(r['accepted']for r in now.values()),planned_primary=350,programs=35,
 state_counts=d['state_counts'],statistics=stats,fixed_common_population=sorted(common),new_since_v2=new,previous_accepted316_result_SHA_unchanged=True,
 all_cells=list(now.values()),pairs=pairs,supplemental=supp,CH_nonP0_accepted=0,relative_improvement_available=False,
 source_provenance=dict(primary_sha256=sha(P/'PRIMARY_SNAPSHOT.json'),supplemental_sha256=sha(P/'SUPPLEMENTAL_SNAPSHOT.json'),generator=d['generator'],
 previous_snapshot_path=str(anchor),previous_snapshot_sha256=sha(anchor),analyzer_sha256=sha(pathlib.Path(__file__)),Git_accessed=False),
 limitations=['Individually coherent file snapshots, not one controller-wide atomic transaction.',
 'Original accepted RESULT/strict/archive identities reused; no fresh full-options replay/native restore/raw scan/tests.',
 'Per-profile available and fixed common populations separated; no per-program best GM or final35 winner.',
 'No non-P0 CH: no relative DTC improvement inference.',
 'Counters are associations, missing stays null, zero denominator explicitly distinguished.',
 'MRQ last average is not a weighted whole-application latency; dramfull labels ICNT-to-memory blockage.',
 'R2 remains separate from original unaccepted M16; no automatic union.'])
write('EVIDENCE.json',o)
def case_name(rs):return ', '.join(f"{r['program']} {r['DH_self_speedup']:.6f}x"for r in rs)or'none'
lines=['# Accepted-results refresh V3 — 20:43 CST frozen snapshot',
f"UTC `{d['utc']}`: **319/350 primary accepted** (313 new +6 references),12 confirmed live,18 pending,1 original scan/M16 technical negative retained. **R2 separate accepted6,702,538 cycles**, excluded from every primary statistic. This directory is immutable; later results require a new version.",
'## Uniform profiles and populations',
f"DH self = same-input accepted DH P0 / DH variant cycles. Fixed all-eight-profile intersection remains **{len(common)} programs**. Available populations differ and must not be ranked as final35 results. No non-P0 CH is accepted; CH speedups, variant CH/DH and relative DTC improvement remain unavailable.",
'| Profile | Available n/35 | GM | + / = / - | Missing | Fixed common30 GM |','|---|---:|---:|---:|---:|---:|']
for f in profiles:
 a,c=stats[f]['ALL']['available'],stats[f]['ALL']['fixed_common'];lines.append(f"| {f} | {a['n']}/35 | {a['GM']:.6f} | {a['positive']} / {a['neutral']} / {a['negative']} | {a['missing_n']} | {c['GM']:.6f} |")
lines+=['Per-suite available coverage and GM (fixed common populations and sign counts are also in JSON):','| Suite | E384 n / GM | E768 n / GM | M8 n / GM | M16 n / GM | Q64 n / GM | Q128 n / GM | F128 n / GM | F256 n / GM |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for suite in [x for x in stats[profiles[0]]if x!='ALL']:
 lines.append('| '+suite+' | '+' | '.join(f"{stats[f][suite]['available']['n']}/{stats[f][suite]['available']['expected_n']} / {stats[f][suite]['available']['GM']:.6f}"for f in profiles)+' |')
lines+=['All316 previously accepted RESULT SHAs are unchanged. Full available/common populations, per-suite sign/missing counts, source bindings and every cell/RESULT SHA are retained in EVIDENCE.json. Common30 excludes hybridsort,cutcp,SYRK,lavamd andscan; excluded means incomplete intersection, not discarded scientific data.',
'## Newly accepted since V2',
'| Program / profile / cell | Cycles | DH self | Counter observation |','|---|---:|---:|---|']
for r in new:
 ratio=d['comparisons'][r['input_digest']][r['profile']]['DH_speedup']
 c=r['counters'];lines.append(f"| {r['program']} / {r['profile']} / {r['cell']} | {r['cycles']:,} | {'—'if ratio is None else f'{ratio:.6f}'} | DRAM reads {c['DRAM_read_atoms']}; L2 reads {c['L2_read_sectors']}; reservation fails {c['L2_reservation_fail']}; last MRQ {c['avg_mrq_latency_last_printed']} |")
hybrid=next(i for i,v in d['programs'].items()if v['program']=='hybridsort')
lines+=['**Facts:** CUTCP F256 and M16 both equal DH P0 at4,490,473 cycles,1.0x. Recorded DRAM reads, L2 read misses, reservation failures and dramfull remain explicitly0; L2 reads1,605,996; MRQ missing. F256 GM falls from1.019762 (available31) to1.019138 (available32) only by adding a flat point; its common30 GM remains1.011969. M16 similarly adds a flat CUTCP point: GM1.000994 on31, common30 stays1.001027. No prior result changed.',
f"Hybridsort DH P0 is now18,563,916 cycles. Accepted variants currently paired for hybridsort: {sum(d['comparisons'][hybrid][f]['DH_speedup']is not None for f in profiles)}/8. Completing its baseline alone does not invent variant data or complete its CH/DH comparison.",
'## Per-program sensitivity and major signs',
'| Program / suite | E384 | E768 | M8 | M16 | Q64 | Q128 | F128 | F256 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for i,inf in sorted(d['programs'].items(),key=lambda x:(x[1]['suite'],x[1]['program'])):
 lines.append('| '+inf['program']+' / '+inf['suite']+' | '+' | '.join('—'if d['comparisons'][i][f]['DH_speedup']is None else f"{d['comparisons'][i][f]['DH_speedup']:.6f}"for f in profiles)+' |')
lines+=['The following extrema are listed separately for each uniform profile; they are never combined into an oracle GM.','| Uniform profile | Strongest two positives | Strongest two negatives |','|---|---|---|']
for f in profiles:
 rs=[r for r in pairs if r['profile']==f and r['paired']]
 pos=sorted([r for r in rs if r['DH_self_speedup']>1],key=lambda r:-r['DH_self_speedup'])[:2]
 neg=sorted([r for r in rs if r['DH_self_speedup']<1],key=lambda r:r['DH_self_speedup'])[:2]
 lines.append(f'| {f} | {case_name(pos)} | {case_name(neg)} |')
lines+=['F128/F256 have the same sign counts (7 positive,6 negative), **different program sets**: vectorAdd/GESUMMV are positive under F128 but negative under F256; ATAX/scalarProd have the reverse signs. These cases are descriptive observations of uniform configurations, not a per-program best suite.',
'## Counter associations and separate supplemental',
'F256 helps convolutionSeparable1.422263x,scan1.283635x and2DCONV1.078012x while vectorAdd regresses0.919938x. Faster convolutionSeparable/scan coexist with higher last MRQ averages321→905 and184→628. vectorAdd has unchanged DRAM reads and approximately51% fewer reservation-fail events despite slower completion. These events are not critical-path cycle attribution.',
'ATAX E384/E7681.028813x and F2561.017823x coexist with a Q128 regression0.943917x; MVT remains mostly flat/negative, BICG M16 improves1.012241x while M8 regresses0.967226x. 3MM/GEMM/particlefilter_naive are flat across their accepted DH scans. 3MM/GEMM DRAM counters are explicitly0, not missing: percentage null means zero denominator; MRQ is missing. Such simulator trace/kernel statistics do not prove zero DRAM access by the real application. GEMM and Parboil sgemm retain different input identities.',
f"R2 scan/M16 accepted independently at{sr['cycles']:,} cycles, descriptive DH P0/R2={supp['descriptive_DH_P0_over_R2']:.6f}x. It is not included in M16's31 primary pairs or common30. Original M16 remains unaccepted. R2 has nearly unchanged DRAM reads21,712,700→21,712,552 and last MRQ184→183; these counters do not explain causally its slight regression. The preserved lineage/certificate/RESULT/archive SHA are in EVIDENCE.json. Only declared expected physics option values can be compared to the original failed spec; the failed run has no accepted actual-effective-options verification.",
'**Cannot confirm:** final35 winning configuration, relative advantage over CH, queue occupancy, latency-critical path or causality. L2 counters follow the existing complete-single-stream header/binding scope; otherwise whole-declared-trace values stay null. DRAM is global cumulative; last MRQ is not a weighted application average, and dramfull is ICNT-to-memory blockage. Missing MSHR reasons stay missing. No instrumentation or new experiment is authorized by this report.',
'## Reproduction and publication boundary',
f"`collect.py` called existing qualified generator SHA `{d['generator']['sha256']}` once, writing only this new directory. PRIMARY_SNAPSHOT.json records coherent source SHA per file and live PID identity evidence. `analyze.py` reused the frozen V2 source snapshot for the delta and performs JSON arithmetic only. No Git access, raw-log scan, test rerun, native restore, controller/registry/source modification, model launch or budget action occurred. Main reviews and publishes via the existing sole publisher; this analysis is not another controller."]
body=lines[0]
for prev,line in zip(lines,lines[1:]):body+=('\n'if prev.startswith('|')and line.startswith('|')else'\n\n')+line
(P/'REPORT.md').write_text(body+'\n',encoding='utf-8')
write('MANIFEST.json',dict(schema='RESULTS_REFRESH_V3_MANIFEST',snapshot_utc=d['utc'],files=[dict(name=x.name,sha256=sha(x),bytes=x.stat().st_size)for x in sorted(P.iterdir())if x.is_file()and x.name!='MANIFEST.json']))
print(json.dumps(dict(utc=d['utc'],accepted=o['accepted_primary'],new=[(r['program'],r['profile'],r['cycles'])for r in new],common=len(common),manifest_sha256=sha(P/'MANIFEST.json'),report_sha256=sha(P/'REPORT.md'),evidence_sha256=sha(P/'EVIDENCE.json'))))
