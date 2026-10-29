"""Reproduce tables/figures from immutable JSON only; no model, controller or Git access."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,math,statistics,csv,collections
sys.path.insert(0,'/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/D/report_v1/.python-deps')
import matplotlib
matplotlib.use('Agg')
sys.path.insert(0,'/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/D/report_v1/.python-deps')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
import numpy as np
P=pathlib.Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=load('PRIMARY_SNAPSHOT.json');anchor=load('ANCHOR_EVIDENCE.json');ap=load('ANCHOR_PAIRED_FACTOR.json')
assert sha(P/'ANCHOR_EVIDENCE.json')=='e1bd15a1f8a91f750090de6290ae49224f6e0ae0c5e5dbee07ed267b7fdc2de3'
fs=['E384','E768','M8','M16','Q64','Q128','F128','F256']
ids=sorted(d['programs'],key=lambda i:(d['programs'][i]['suite'],d['programs'][i]['program'],i))
rows=[dict(**d['programs'][i],profile=f,cell=c,**r) for i in ids for f,cs in d['table'][i].items() for c,r in cs.items()]
old={r['cohort']:r for r in anchor['all_cells']}
assert len(rows)==350 and len(ids)==35
assert all(r['accepted'] and r['result_sha256']==old[r['cohort']]['result_sha256'] for r in rows if old[r['cohort']]['accepted'])
new=[r for r in rows if r['accepted'] and not old[r['cohort']]['accepted']]
def write(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def csvout(name,rs,fields):
 with (P/name).open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rs)
def agg(values,expected_ids):
 a=list(values.values());n=len(a)
 return dict(n=n,expected_n=len(expected_ids),missing_n=len(expected_ids)-n,GM=math.exp(math.fsum(math.log(x) for x in a)/n) if n else None,positive=sum(x>1 for x in a),neutral=sum(x==1 for x in a),negative=sum(x<1 for x in a),minimum=min(a) if n else None,p10=float(np.quantile(a,.1)) if n else None,median=statistics.median(a) if n else None,p90=float(np.quantile(a,.9)) if n else None,maximum=max(a) if n else None,population=list(values),missing_population=[i for i in expected_ids if i not in values],values=values)
def cycles(i,f):
 r=d['table'][i][f]['DH'];return r['cycles'] if r['accepted'] else None
def values(numer,denom,pop):return {i:cycles(i,numer)/cycles(i,denom) for i in pop if cycles(i,numer) and cycles(i,denom)}
common=[i for i in ids if all(cycles(i,f) for f in ['P0']+fs)]
assert len(common)==31 and set(common)==set(anchor['fixed_common_population'])
stats={f:{'available':agg(values('P0',f,ids),ids),'common31':agg(values('P0',f,common),common)} for f in fs}
for f in fs:assert math.isclose(stats[f]['common31']['GM'],anchor['statistics'][f]['ALL']['fixed_common']['GM'],abs_tol=1e-14)
factors={a+'_to_'+b:{'numerator':a,'denominator':b,'available_paired':agg(values(a,b,ids),ids),'common31':agg(values(a,b,common),common)} for a,b in [('E384','E768'),('M8','M16'),('Q64','Q128'),('F128','F256')]}
assert math.isclose(factors['F128_to_F256']['common31']['GM'],ap['GM'],abs_tol=1e-14)
suites={suite:{f:{'available':agg(values('P0',f,[i for i in ids if d['programs'][i]['suite']==suite]),[i for i in ids if d['programs'][i]['suite']==suite]),'common31':agg(values('P0',f,[i for i in common if d['programs'][i]['suite']==suite]),[i for i in common if d['programs'][i]['suite']==suite])} for f in fs} for suite in sorted({d['programs'][i]['suite'] for i in ids})}
paired=[];counterrows=[]
for i in ids:
 base=d['table'][i]['P0']['DH']
 for f in fs:
  v=d['table'][i][f]['DH'];paired.append(dict(**d['programs'][i],profile=f,paired=base['accepted'] and v['accepted'],speedup=values('P0',f,[i]).get(i),P0_cycles=base['cycles'],variant_cycles=v['cycles'],P0_state=base['state'],variant_state=v['state'],P0_cohort=base['cohort'],variant_cohort=v['cohort'],P0_result_sha256=base['result_sha256'],variant_result_sha256=v['result_sha256']))
  if base['accepted'] and v['accepted']:
   assert all(base[k]==v[k] and v[k] for k in ['core_commit','framework_commit','binary_sha256'])
   for metric in sorted(set(base['counters'])|set(v['counters'])):
    a,b=base['counters'].get(metric),v['counters'].get(metric);numeric=type(a) in (int,float) and type(b) in (int,float)
    counterrows.append(dict(**d['programs'][i],profile=f,metric=metric,P0=json.dumps(a),variant=json.dumps(b),delta=b-a if numeric else None,change_pct=100*(b/a-1) if numeric and a else None,percentage_status='ZERO_DENOMINATOR' if numeric and a==0 else 'AVAILABLE' if numeric else 'MISSING_OR_NONNUMERIC'))
write('ALL_CELLS.json',rows)
csvout('all350_cells.csv',rows,['suite','program','input_digest','profile','cell','cohort','accepted','cycles','state','raw_reported_cycles','uuid','result_path','result_sha256','core_commit','framework_commit','binary_sha256'])
csvout('all280_DH_pairs.csv',paired,list(paired[0]))
csvout('all_paired_counter_observations.csv',counterrows,list(counterrows[0]))
summary=dict(schema='CURRENT_PERFORMANCE_REPORT_20261029_V1',status='PROVISIONAL_PARTIAL_COVERAGE',snapshot_utc=d['utc'],accepted_primary=sum(r['accepted'] for r in rows),planned_primary=350,frozen_inputs=35,original_state_counts=d['state_counts'],controller_context=d['batch'],statistics=stats,paired_factors=factors,suite_statistics=suites,common31_population=common,all35_population=ids,new_accepted_since_E_v4=new,old_accepted322_SHA_unchanged=True,independent_union=False,relative_DTC_improvement_available=False,source_files=[dict(name=n,sha256=sha(P/n)) for n in ['PRIMARY_SNAPSHOT.json','ANCHOR_EVIDENCE.json','ANCHOR_PAIRED_FACTOR.json','qualified_generator.source.py']],notes=['Original matrix only; 6 proven references accepted, IR/R2/engineering/derived excluded.','Every original matrix cell retained; missing cycles=null; failed raw-reported cycles never used.','Exact cycle signs, no epsilon. No repeated simulations or uncertainty intervals.','Individually coherent files, no controller-wide atomic transaction.','English v0.23 unchanged; seven UNRESOLVED inputs excluded.'])
write('SUMMARY.json',summary)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(10,4.5));x=np.arange(len(fs))
ax.axhline(1,color='0.3',lw=1)
ax.plot(x,[stats[f]['common31']['GM'] for f in fs],'o-',color='#2166ac',label='Same 31 inputs (all eight profiles)')
ax.plot(x,[stats[f]['available']['GM'] for f in fs],'s--',color='#b35806',label='Available paired inputs (different coverage)')
for j,f in enumerate(fs):ax.annotate('n='+str(stats[f]['available']['n']),(j,stats[f]['available']['GM']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
ax.set_xticks(x,fs);ax.set_ylabel('Geometric mean DH P0 / DH profile cycles');ax.set_title('Uniform profiles: population-sensitive summaries (35 frozen inputs)');ax.grid(axis='y',alpha=.2);ax.legend(loc='upper left',fontsize=9);fig.tight_layout();fig.savefig(P/'profile_GM.png');fig.savefig(P/'profile_GM.svg');plt.close(fig)
arr=np.array([[values('P0',f,[i]).get(i,np.nan) for f in fs] for i in ids]);log=np.log2(arr);bound=max(abs(np.nanmin(log)),abs(np.nanmax(log)))
fig,ax=plt.subplots(figsize=(10,12));cm=plt.colormaps['RdBu'].copy();cm.set_bad('#dadada');im=ax.imshow(log,cmap=cm,vmin=-bound,vmax=bound,aspect='auto')
for j in range(len(ids)):
 for k in range(len(fs)):
  a=arr[j,k];ax.text(k,j,'NA' if np.isnan(a) else f'{a:.3f}',ha='center',va='center',fontsize=7.5,color='white' if not np.isnan(a) and abs(log[j,k])>.65*bound else 'black')
ax.set_yticks(np.arange(len(ids)),[d['programs'][i]['suite']+' / '+d['programs'][i]['program'] for i in ids],fontsize=8);ax.set_xticks(np.arange(len(fs)),fs);ax.set_title('Every frozen input: accepted DH P0 / DH profile cycles\nBlue >1 faster; red <1 slower; gray NA (pending, failed or unaccepted)');fig.colorbar(im,ax=ax,label='log2(speedup)',fraction=.025,pad=.03);fig.tight_layout();fig.savefig(P/'all35_heatmap.png');fig.savefig(P/'all35_heatmap.svg');plt.close(fig)
fig,axes=plt.subplots(1,4,figsize=(13,9),sharey=True)
for ax,(name,e) in zip(axes,factors.items()):
 v=e['common31']['values'];ys=np.arange(len(common));xs=np.array([v[i] for i in common]);ax.axvline(1,color='0.4',lw=1);ax.scatter(xs,ys,c=np.where(xs>1,'#2166ac',np.where(xs<1,'#b2182b','#777777')),s=24);ax.xaxis.set_major_locator(MaxNLocator(3));ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'));ax.set_title(name.replace('_to_',' → ')+'\nGM='+f"{e['common31']['GM']:.6f}",fontsize=10);ax.grid(axis='x',alpha=.25);ax.set_xlabel('Earlier / later cycles');ax.set_yticks(ys,[d['programs'][i]['program'] for i in common],fontsize=8);ax.set_xlim(min(.94,float(xs.min())*.98),max(1.03,float(xs.max())*1.02))
axes[0].invert_yaxis()
fig.suptitle('Paired factor changes on the same 31 inputs; all signs retained',fontsize=12);fig.tight_layout();fig.savefig(P/'paired_factors.png');fig.savefig(P/'paired_factors.svg');plt.close(fig)
def fmt(x):return 'NA' if x is None else f'{x:.6f}'
def signs(a):return f"{a['positive']}/{a['neutral']}/{a['negative']}"
lines=['# Current accepted DTC-L2 performance snapshot',f"**PROVISIONAL_PARTIAL_COVERAGE** — {d['utc']}. Original matrix **323/350 accepted =317 fresh +6 ratified references**, 35 fixed inputs. All 322 accepted E-v4 RESULT hashes remain identical. No simulation or production change was performed.",'', 'DH speedup is same-input accepted DH P0 cycles / DH variant cycles. A value above 1 is faster. Each row uses one uniform profile. The all-profile intersection remains 31 inputs; all other inputs and every failed/missing cell remain visible in the full tables. Exact equality determines neutral; these deterministic runs do not supply sampling confidence intervals.','', '| Profile | Available n/35 | Available GM | +/=/- | Missing | Same31 GM | Same31 +/=/- |','|---|---:|---:|---:|---:|---:|---:|']
for f in fs:
 a,b=stats[f]['available'],stats[f]['common31'];lines.append(f"| {f} | {a['n']}/35 | {fmt(a['GM'])} | {signs(a)} | {a['missing_n']} | {fmt(b['GM'])} | {signs(b)} |")
lines+=['','Configuration remains Core9eedb313 / Framework02775fd7 / binary02a28936; DRAM850MHz, L2 capacity10MiB, Hash/DTC/clock fixed. P0 has MSHR entries192, merge4, miss queue32 per L2 subpartition, FRFCFS64 per controller. E384/E768 change entries; M8/M16 change merge; Q64/Q128 change miss queue; F128/F256 change FRFCFS. Structural resource limits do not measure occupancy or area; FRFCFS changes also affect memory-partition credit coupling. Exact options and source-spec hashes are in PRIMARY_SNAPSHOT.json.','','![Uniform GM by population](profile_GM.png)','','The available GM uses different coverage in each profile and is not a final35 ranking. F256 **same31 GM=1.011580804**, while its **available33 GM='+fmt(stats['F256']['available']['GM'])+'** includes the additional accepted paired inputs. These denominators must remain distinct.','','| Factor direction | Paired n/35 | GM | +/=/- | Missing | min / median / max | Same31 GM |','|---|---:|---:|---:|---:|---:|---:|']
for n,e in factors.items():
 a=e['available_paired'];lines.append(f"| {n.replace('_to_',' → ')} | {a['n']}/35 | {fmt(a['GM'])} | {signs(a)} | {a['missing_n']} | {fmt(a['minimum'])} / {fmt(a['median'])} / {fmt(a['maximum'])} | {fmt(e['common31']['GM'])} |")
lines+=['','F128→F256 is computed per same input before the GM: **1.003295031571× on same31 (7 positive,20 equal,4 negative)**. It is not a quotient of GMs from different available populations. Distributions, p10/p90, every full input digest, missing populations and suite splits are in `SUMMARY.json`.','','![All paired factor effects](paired_factors.png)','','Suite GMs use the accepted paired members of each frozen suite, with n shown explicitly:','','| Suite | '+' | '.join(fs)+' |','|---|'+'---:|'*len(fs)]
for s,ss in suites.items():lines.append('| '+s+' | '+' | '.join(f"{ss[f]['available']['n']}/{ss[f]['available']['expected_n']} · {fmt(ss[f]['available']['GM'])}" for f in fs)+' |')
lines+=['','![All35 per-input results](all35_heatmap.png)','','Heatmap numbers are rounded; exact signs and full-precision ratios remain in the tables. Every original cohort, input digest, cycles, acceptance state and RESULT source SHA is in `all350_cells.csv` / `ALL_CELLS.json`; all 280 DH comparisons are in `all280_DH_pairs.csv`. Blank CSV numeric fields mean missing, never zero. Accepted-result counter values and zero-denominator flags are in `all_paired_counter_observations.csv`.','','Observed cases (all are associations; no critical-path or causal attribution):','','| Input | E384 | E768 | M8 | M16 | Q64 | Q128 | F128 | F256 |','|---|'+'---:|'*8]
case_names=['ATAX','MVT','BICG','2DCONV','3DCONV','particlefilter_naive','3MM','GEMM','vectorAdd','convolutionSeparable','scan','hybridsort']
for name in case_names:
 matching=[i for i in ids if d['programs'][i]['program'].lower()==name.lower()]
 for i in matching:lines.append('| '+d['programs'][i]['program']+' | '+' | '.join(fmt(values('P0',f,[i]).get(i)) for f in fs)+' |')
lines+=['','- ATAX shows an E384/E768 gain and a Q128 regression; MVT is mostly flat/negative; BICG improves under M16 and regresses under M8. These different responses prevent a universal monotonic capacity/MLP conclusion.','- F256 helps 2DCONV, convolutionSeparable and scan, while vectorAdd regresses. convolutionSeparable/scan gains coexist with higher last-printed MRQ averages (321→405 and184→228). vectorAdd has unchanged DRAM read atoms and fewer reservation failures despite taking more cycles.','- 3MM/GEMM/particlefilter_naive are exactly flat across accepted DH scans. 3MM/GEMM recorded DRAM counters are explicitly0; their MRQ values are missing. This is scoped simulator evidence, not proof of zero real-application DRAM traffic. GEMM and Parboil sgemm are distinct identities.','- The only newly accepted original result since E-v4 is hybridsort F256: **16,370,955 cycles**, versus P0 **18,563,916**, speedup **'+fmt(18563916/16370955)+'×**. This does not fill its failed/missing variants or alter the same31 intersection.','- Keep the 35 input identities fixed, retain failures/negative gains, and finish their existing tails before claiming final35 superiority. No non-P0 CH result is accepted: the selected CH-F25635 follow-up remains a review proposal; relative DTC improvement cannot be computed.','','Original350 status at acquisition: `'+json.dumps(d['state_counts'],sort_keys=True)+'`. Controller context separately lists '+str(len(d['batch'].get('running',[])))+' active running memberships and remaining='+str(d['batch'].get('remaining'))+' across a broader scope including independent IR; original350 has only '+str(d['state_counts'].get('RUNNING_CONFIRMED',0))+' confirmed live cells. A controller membership is not acceptance. Failed cells retain source SHA and optional raw-reported cycles solely for diagnostics. Pending/FAIL/HOLD/repair data never enter performance arithmetic.','','IR, R2, engineering and namedDerived35 are excluded from every formal statistic here; no automatic union or substitution. The original scan M16 remains unaccepted. The independently accepted R2 is documented by frozen E-v4 only, with cycles6,702,538; that result does not replace its original negative. Historical J work is outside this report. English v0.23 is unchanged and the seven UNRESOLVED inputs remain outside the frozen35.','','L2 values follow the existing single-stream binding evidence; unsupported whole-trace values remain null. DRAM counters are globally cumulative. Last-printed MRQ is not a weighted application mean; dramfull denotes ICNT-to-memory blockage. Missing MSHR reasons do not mean zero. Counter changes cannot establish causality or numerical full-application correctness.','','Reproduce on an environment with Python, numpy and matplotlib: `python3 analyze.py`. `collect.py` was run once using the previously qualified generator SHA9ad9cdf8…; it acquires individually coherent source files (not an atomic controller transaction). `PRIMARY_SNAPSHOT.json` contains their exact paths and SHA256. No fresh native/engineering audit, production/controller/Goal/READY/Git operation, model launch or new scope registration occurred. `MANIFEST.json` hashes every delivered file.']
(P/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
write('MANIFEST.json',dict(schema='CURRENT_PERFORMANCE_REPORT_MANIFEST_V1',status=summary['status'],snapshot_utc=d['utc'],files=[dict(name=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in sorted(P.iterdir()) if p.is_file() and p.name!='MANIFEST.json']))
print(json.dumps(dict(accepted=summary['accepted_primary'],common=len(common),stats={f:{'n':s['available']['n'],'gm':s['available']['GM']} for f,s in stats.items()},manifest_sha256=sha(P/'MANIFEST.json'),new=[(r['program'],r['profile'],r['cycles']) for r in new])))

