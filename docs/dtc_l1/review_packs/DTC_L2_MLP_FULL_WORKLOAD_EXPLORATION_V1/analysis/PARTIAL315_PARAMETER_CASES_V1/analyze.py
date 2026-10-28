"""Read only the published fixed dashboard; no live RESULT/raw reads or dispatch."""
import hashlib,json,math,pathlib,statistics

HERE=pathlib.Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
d=load(HERE/'report.source.json')
assert sha(HERE/'build_report.source.py')==d['generator']['sha256']
assert len(d['programs'])==35 and not d['uniform_option_errors']
profiles=[p for p in d['profiles'] if p!='P0']
core='9eedb3131937748f0492fa83aad37d3691118d70'
fw='02775fd795cde5aae1480d81cee6eb481d0a08f4'
binary='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
def ref(r):
 return {k:r.get(k) for k in ['cohort','uuid','state','accepted','cycles','result_path','result_sha256','core_commit','framework_commit','binary_sha256']}
def changes(a,b):
 out={}
 for k in sorted(set(a)|set(b)):
  av,bv=a.get(k),b.get(k)
  numeric=type(av) in (int,float) and type(bv) in (int,float)
  out[k]={'P0':av,'variant':bv,'delta':bv-av if numeric else None,
          'change_pct':100*(bv/av-1) if numeric and av!=0 else None,
          'pct_status':'ZERO_DENOMINATOR' if numeric and av==0 else 'AVAILABLE' if numeric else 'NONNUMERIC_OR_MISSING'}
 return out
rows=[]
for i,info in sorted(d['programs'].items()):
 base=d['table'][i]['P0']['DH']
 for p in profiles:
  r=d['table'][i][p]['DH']; paired=bool(base['accepted'] and r['accepted'])
  for a in [base,r]:
   if a['accepted']:
    assert a['core_commit']==core and a['framework_commit']==fw and a['binary_sha256']==binary
    assert a['result_sha256'] and a['cycles']>0
  ratio=base['cycles']/r['cycles'] if paired else None
  assert ratio==d['comparisons'][i][p]['DH_speedup']
  rows.append(dict(**info,profile=p,paired=paired,DH_self_speedup=ratio,P0=ref(base),variant=ref(r),
    input_binding=d['stream_scopes'][i],counter_changes=changes(base.get('counters') or {},r.get('counters') or {}) if paired else None,
    CH_variant_available=bool(d['table'][i][p].get('CH',{}).get('accepted')),relative_DTC_improvement=None))
common=set(d['programs'])
for p in profiles: common&={r['input_digest'] for r in rows if r['profile']==p and r['paired']}
assert len(common)==30
assert common==set(d['fixed_all_profile_common_population']['ALL']['DH_speedup']['population'])
def summary(rs,expected):
 vals=[r['DH_self_speedup'] for r in rs if r['paired']]
 return dict(n=len(vals),expected_n=expected,missing_n=expected-len(vals),GM=math.exp(math.fsum(map(math.log,vals))/len(vals)) if vals else None,
             positive=sum(v>1 for v in vals),neutral=sum(v==1 for v in vals),negative=sum(v<1 for v in vals),
             minimum=min(vals) if vals else None,maximum=max(vals) if vals else None,
             population=[r['input_digest'] for r in rs if r['paired']])
suites=sorted({v['suite'] for v in d['programs'].values()})
stats={}
for p in profiles:
 stats[p]={}
 for suite in ['ALL']+suites:
  subset=[r for r in rows if r['profile']==p and (suite=='ALL' or r['suite']==suite)]
  fixed=[r for r in subset if r['input_digest'] in common]
  stats[p][suite]={'available':summary(subset,len(subset)),'common30':summary(fixed,len(fixed))}
  assert stats[p][suite]['available']['n']==d['statistics'][p][suite]['DH_speedup']['n']
  assert math.isclose(stats[p][suite]['available']['GM'],d['statistics'][p][suite]['DH_speedup']['GM'],rel_tol=1e-12)
cases={p:{'positive':sorted([r for r in rows if r['profile']==p and r['paired'] and r['DH_self_speedup']>1],key=lambda r:-r['DH_self_speedup']),
          'negative':sorted([r for r in rows if r['profile']==p and r['paired'] and r['DH_self_speedup']<1],key=lambda r:r['DH_self_speedup']),
          'missing':[r for r in rows if r['profile']==p and not r['paired']]} for p in ['F128','F256']}
focus=['ATAX','MVT','BICG','3MM','GEMM','2DCONV','3DCONV','particlefilter_naive']
o={'schema':'PARTIAL315_PARAMETER_CASES_V1','source_commit':'280abe32e1090366cfaabaf5895662300c2f9f27','snapshot_utc':d['utc'],
 'source_report_sha256':sha(HERE/'report.source.json'),'source_generator':d['generator'],'analysis_script_sha256':sha(pathlib.Path(__file__)),
 'state_counts':d['state_counts'],'accepted_total':sum(v for k,v in d['state_counts'].items() if k.startswith('PASS_') or k.startswith('REFERENCE_')),
 'common30_population':sorted(common),'statistics':stats,'uniform_F_cases':cases,'focus_programs':focus,'pairs':rows,
 'limitations':['Published frozen report/RESULT SHA references only; no fresh terminal replay or raw scan.',
  'DH self benefit only; no accepted non-P0 CH, therefore relative improvement unavailable.',
  'Fixed common30 and changing per-profile available populations are separate; neither is final35.',
  'Counters are associations, not causal decomposition; L2 scope follows source stream contract.',
  'Last-printed MRQ average is not a weighted whole-application latency; gpu_stall_dramfull is ICNT-to-memory blockage.',
  'Null percentage may be explicit zero denominator; counters missing remain null.',
  'Original scan M16 negative is unaccepted, supplemental R2 excluded; unresolved7/derivedinputs excluded.']}
(HERE/'EVIDENCE.json').write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('accepted',o['accepted_total'],'common',len(common))
for p in profiles:
 s=stats[p]['ALL'];print(p,'available',s['available']['n'],s['available']['GM'],'fixed',s['common30']['GM'])
for p,c in cases.items(): print(p,'positives',[(r['program'],round(r['DH_self_speedup'],6)) for r in c['positive']],'negatives',[(r['program'],round(r['DH_self_speedup'],6)) for r in c['negative']])
for name in focus:
 print(name,[(r['profile'],None if r['DH_self_speedup'] is None else round(r['DH_self_speedup'],6)) for r in rows if r['program']==name])
