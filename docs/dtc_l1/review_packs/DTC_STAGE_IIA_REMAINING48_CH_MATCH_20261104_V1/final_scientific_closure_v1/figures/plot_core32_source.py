#!/usr/bin/env python3
"""Read-only fixed CORE32 visualization of SHA-verified qualified B provider."""
import argparse,datetime,gzip,hashlib,json,math,os,pathlib,sys,platform,importlib.metadata,copy
sys.dont_write_bytecode=True
P=pathlib.Path;BASE=P(__file__).resolve().parent
for leaf in ['tmp','mpl-config']:(BASE/leaf).mkdir(parents=True,exist_ok=True)
for key in ['TMPDIR','TMP','TEMP']:os.environ[key]=str(BASE/'tmp')
os.environ['MPLCONFIGDIR']=str(BASE/'mpl-config')
FIXED=[('CUDA Samples', 'BlackScholes', 'b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0'), ('CUDA Samples', 'convolutionSeparable', '4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449'), ('CUDA Samples', 'fastWalshTransform', 'f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3'), ('CUDA Samples', 'histogram', '3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58'), ('CUDA Samples', 'mergeSort', 'dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48'), ('CUDA Samples', 'scalarProd', '2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954'), ('CUDA Samples', 'scan', '6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'), ('CUDA Samples', 'transpose', '65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc'), ('CUDA Samples', 'vectorAdd', 'e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'), ('Parboil', 'bfs', '1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0'), ('Parboil', 'cutcp', 'af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8'), ('Parboil', 'histo', '2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64'), ('Parboil', 'mri-q', 'dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4'), ('Parboil', 'sad', 'db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9'), ('Parboil', 'sgemm', 'ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453'), ('Parboil', 'stencil', 'c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266'), ('PolyBench/GPU', '2DCONV', 'd984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0'), ('PolyBench/GPU', '3DCONV', '79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d'), ('PolyBench/GPU', '3MM', '977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d'), ('PolyBench/GPU', 'ATAX', 'eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950'), ('PolyBench/GPU', 'BICG', 'ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef'), ('PolyBench/GPU', 'GEMM', 'fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318'), ('PolyBench/GPU', 'GESUMMV', '769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4'), ('PolyBench/GPU', 'MVT', 'f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079'), ('Rodinia', 'dwt2d', 'e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008'), ('Rodinia', 'gaussian', '16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3'), ('Rodinia', 'heartwall', '731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980'), ('Rodinia', 'lud', 'b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8'), ('Rodinia', 'myocyte', '977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992'), ('Rodinia', 'particlefilter_float', 'b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4'), ('Rodinia', 'particlefilter_naive', '3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e'), ('Rodinia', 'srad_v1', '0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4')]
F=('F128','F256');METRICS=('S_CH','S_DH','R','I','R_P0');COLORS={'P0':'#737B83','F128':'#146DA0','F256':'#CB6B18'};MARKERS={'P0':'o','F128':'s','F256':'^'}
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def dump(p,x):P(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def verified(path,want):
 b=P(path).read_bytes();assert digest(b)==want,('SHA_MISMATCH',str(path));return b
def gm(vals):return math.exp(sum(math.log(v)for v in vals)/len(vals))if vals else None
def near(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-12)
def exact_metrics(c):
 cp,dp,cf,df=(c[k]['cycles']for k in ['CH_P0','DH_P0','CH_F','DH_F']);assert all(type(v)is int and v>0 for v in [cp,dp,cf,df])
 pairs={'S_CH':(cp,cf),'S_DH':(dp,df),'R':(cf,df),'I':(dp*cf,df*cp),'R_P0':(cp,dp)}
 return {k:n/d for k,(n,d)in pairs.items()},{k:('EXACT_ZERO'if n==d else'POSITIVE'if n>d else'NEGATIVE')for k,(n,d)in pairs.items()}
def missing_label(row,f):
 ss=' '.join(str(x.get('status',''))for x in row['missing_by_profile'][f]).upper()
 if 'HOLD'in ss:return 'HOLD'
 if 'NEGATIVE'in ss or 'FAIL'in ss or 'STOP'in ss:return 'negative'
 return 'pending'
def validate_report(report,summary):
 assert report['schema']=='DTC_REMAINING48_CORE32_STATISTICS_V1'and report['authority_commit']=='5f67b4d6b94568a9f1acc80c3e56736bd81e4753'
 assert summary['source_qualified']and summary['core32_fixed_input_n']==32
 rows=report['all_programs'];assert [(r['suite'],r['program'],r['input_digest'])for r in rows]==[tuple(x)for x in FIXED]
 entries=[]
 for r in rows:
  slots=r['six_source_cells'];assert set(slots)=={'CH_P0','DH_P0','CH_F128','CH_F256','DH_F128','DH_F256'}
  for k,s in slots.items():
   assert s['input_digest']==r['input_digest']and s['program']==r['program']
   if s['accepted']:assert type(s['cycles'])is int and s['cycles']>0
   else:assert s['cycles']is None
  for f in F:
   c={k:slots[k]for k in ['CH_P0','DH_P0']};c.update(CH_F=slots['CH_'+f],DH_F=slots['DH_'+f]);complete=all(s['accepted']for s in c.values());provided=r['metrics_by_profile'][f]
   assert complete==(provided is not None)
   vals,signs=exact_metrics(c)if complete else({k:None for k in METRICS},{k:'MISSING'for k in METRICS})
   if complete:assert all(near(vals[k],provided[k])for k in METRICS),('METRIC_MISMATCH',r['program'],f)
   entries.append(dict(program=r['program'],suite=r['suite'],input_digest=r['input_digest'],profile=f,accepted_matched_quadruple=complete,plot_status='accepted'if complete else missing_label(r,f),metrics=vals,exact_integer_classification=signs,six_source_cells=slots,missing_sources=r['missing_by_profile'][f],population_origin=r['population_origin']))
 common=[r['input_digest']for r in rows if all(r['metrics_by_profile'][f]is not None for f in F)];assert common==report['same_input_both_F_ids'];stats=report['all_core32']['common_both_F'];assert len(common)==stats['n']==summary['core32_common_both_F_n']
 lookup={(e['input_digest'],e['profile']):e for e in entries};counts={}
 for f in F:
  counts[f]={}
  for k in METRICS:
   b=stats['profiles'][f][k];calc=gm([lookup[(d,f)]['metrics'][k]for d in common]);assert b['n']==len(common)and((calc is None and b['GM']is None)or(calc is not None and near(calc,b['GM'])))
   exact=[lookup[(d,f)]['exact_integer_classification'][k]for d in common];counts[f][k]=dict(n=len(common),positive=exact.count('POSITIVE'),negative=exact.count('NEGATIVE'),exact_zero=exact.count('EXACT_ZERO'),missing_out_of32=32-len(common))
 return entries,common,stats,counts

def load_provider(path):
 raw=P(path).read_bytes();provider=json.loads(raw);assert provider['schema']=='DTC_STAGEII_REMAINING48_ANALYSIS_PUBLICATION_PROVIDER_V1'and provider['source_qualified']is True
 assert provider['request']=='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
 verified(provider['qualification_manifest']['path'],provider['qualification_manifest']['sha256']);manifest=json.loads(verified(provider['manifest']['path'],provider['manifest']['sha256']));pins={x['path']:x['sha256']for x in manifest['files']};payload={};sources=[]
 for leaf in ['CORE32_RESULTS.json.gz','SUMMARY.json.gz']:
  matches=[x for x in provider['files']if P(x['path']).name==leaf];assert len(matches)==1;x=matches[0];assert pins[x['path']]==x['sha256'];b=verified(x['path'],x['sha256']);payload[leaf]=json.loads(gzip.decompress(b));sources.append(dict(path=x['path'],sha256=x['sha256']))
 report=payload['CORE32_RESULTS.json.gz'];summary=payload['SUMMARY.json.gz'];assert summary==provider['summary'];assert summary['observed_utc']==provider['observed_utc'];entries,common,stats,counts=validate_report(report,summary)
 return raw,provider,report,summary,entries,common,stats,counts,sources

def cohort_status(n):
 assert type(n)is int and 0<=n<=32
 return 'Complete matched data for fixed CORE32'if n==32 else'Partial matched cohort; not a full32-suite conclusion'

def render(out,data):
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'DTC_STAGEIIA_CORE32_FIGURES_V1','savefig.facecolor':'white'})
 entries={(e['input_digest'],e['profile']):e for e in data['entries']};n=len(data['common_F128_F256_population']);stats=data['common_both_F_statistics'];rows=data['programs32'];ts=data['observed_utc'];common=data['common_F128_F256_population']
 def annov(v,sgn):return f'{v:.3f}'+{'POSITIVE':'+','NEGATIVE':'-','EXACT_ZERO':'='}[sgn]
 def missing(ax,i,f,e):ax.text(i,.055 if f=='F128'else .015,('128 'if f=='F128'else'256 ')+e['plot_status'],transform=ax.get_xaxis_transform(),ha='center',fontsize=7,color='#A03B3B'if e['plot_status']=='negative'else'#676E75')
 def frame(ax,group,metric):
  ax.axhline(1,color='#626B74',ls='--',lw=.8);ax.grid(axis='y',color='#E1E6EB',lw=.6);ax.set_axisbelow(True);ax.set_xlim(-.6,len(group)-.4)
  labels=[r['program'].replace('convolutionSeparable','convSeparable').replace('particlefilter_','particlefilter_')+'\n'+r['input_digest'][:8]for r in group];ax.set_xticks(range(len(group)),labels,rotation=22,ha='right',fontsize=8)
  vals=[e['metrics'][metric]for r in group for f in F if(e:=entries[(r['input_digest'],f)])['accepted_matched_quadruple']]
  if metric=='R':vals+=[r['six_source_cells']['CH_P0']['cycles']/r['six_source_cells']['DH_P0']['cycles']for r in group]
  lo=min([1.]+vals);hi=max([1.]+vals);pad=max(.08,(hi-lo)*.20);ax.set_ylim(max(0,lo-pad),hi+pad)
 def points(ax,group,metric,p0=False):
  for i,r in enumerate(group):
   if p0:
    pv=1. if metric in ['S_CH','S_DH']else r['six_source_cells']['CH_P0']['cycles']/r['six_source_cells']['DH_P0']['cycles'];ax.plot(i-.30,pv,'o',color=COLORS['P0'],ms=4,zorder=3)
   for f,off in [('F128',-.10),('F256',.14)]:
    e=entries[(r['input_digest'],f)]
    if not e['accepted_matched_quadruple']:missing(ax,i,f,e);continue
    v=e['metrics'][metric];ax.plot(i+off,v,MARKERS[f],color=COLORS[f],ms=6,zorder=4);ax.annotate(annov(v,e['exact_integer_classification'][metric]),(i+off,v),xytext=((-4,-14)if f=='F128'else(4,9)),textcoords='offset points',ha='right'if f=='F128'else'left',fontsize=7,color=COLORS[f])
 def gmline(keys):
  if not n:return 'Common F128/F256 accepted intersection n=0/32: GM unavailable'
  pieces=[]
  for k in keys:pieces.append(k+': '+', '.join(f+' '+format(stats['profiles'][f][k]['GM'],'.4f')for f in F))
  return 'Common accepted intersection n='+str(n)+'/32 | '+' | '.join(pieces)
 def save(fig,name):fig.savefig(out/(name+'.png'),dpi=160);fig.savefig(out/(name+'.svg'),metadata={'Date':None});plt.close(fig)
 groups=[rows[i:i+8]for i in range(0,32,8)]
 fig,axes=plt.subplots(4,2,figsize=(19,16));fig.subplots_adjust(left=.055,right=.985,top=.91,bottom=.09,hspace=.72,wspace=.17)
 for ri,group in enumerate(groups):
  for ci,metric in enumerate(['S_CH','S_DH']):
   ax=axes[ri,ci];frame(ax,group,metric);points(ax,group,metric,True);ax.set_ylabel('Own P0 cycles / cycles');ax.set_title(('CH conventional cache'if ci==0 else'DH DTC-L1')+' | fixed inputs '+str(ri*8+1)+'–'+str(ri*8+len(group)),loc='left',fontsize=10,weight='bold')
  combined=[entries[(r['input_digest'],f)]['metrics'][k]for r in group for f in F for k in ['S_CH','S_DH']if entries[(r['input_digest'],f)]['accepted_matched_quadruple']]
  low=min([1.]+combined);high=max([1.]+combined);pad=max(.08,(high-low)*.20)
  for ax in axes[ri]:ax.set_ylim(max(0,low-pad),high+pad)
 for k in ['P0',*F]:axes[0,0].plot([],[],MARKERS[k],color=COLORS[k],label=k+(' reference'if k=='P0'else''),ms=6)
 axes[0,0].legend(loc='upper right',ncol=3,frameon=False,fontsize=8)
 fig.suptitle('Stage II-A fixed CORE32: CH / DH performance with own P0 = 1',fontsize=17,weight='bold',y=.98)
 fig.text(.055,.945,gmline(['S_CH','S_DH']),fontsize=11);fig.text(.055,.925,'Snapshot '+ts+' | Remaining48 accepted '+str(data['summary']['accepted_CH'])+'/48 | '+cohort_status(n),fontsize=10,color='#525C65')
 fig.text(.055,.032,'>1 faster; <1 slower. F shown only after complete matched CH/DH P0/F acceptance. Pending / negative / HOLD are labels, never values.\nSuffix + / - / = is exact integer-cycle classification; a displayed 1.000+ or 1.000- is not exact zero. Same common set for both F GMs; no per-program best choice.',fontsize=10,color='#525C65',linespacing=1.5)
 save(fig,'CH_DH_own_P0_normalized_CORE32')
 for metric,name,title,ylabel,explain in [('I','relative_change_I_CORE32','Relative change I = S_DH / S_CH','I = S_DH / S_CH','I > 1 favours DH relative to P0; I < 1 favours CH. This does not itself establish DH faster than CH.'),('R','absolute_CH_over_DH_R_CORE32','Absolute performance R = CH cycles / DH cycles','CH cycles / DH cycles','R > 1 means DH is faster than CH. Matched downstream options do not imply equal L1 resources, area or cost.')]:
  fig,axes=plt.subplots(4,1,figsize=(16,15));fig.subplots_adjust(left=.075,right=.98,top=.90,bottom=.09,hspace=.72)
  for ri,group in enumerate(groups):
   ax=axes[ri];frame(ax,group,metric);points(ax,group,metric,metric=='R');ax.set_ylabel(ylabel);ax.set_title('Fixed inputs '+str(ri*8+1)+'–'+str(ri*8+len(group)),loc='left',fontsize=10,weight='bold')
  for k in (['P0']if metric=='R'else[])+list(F):axes[0].plot([],[],MARKERS[k],color=COLORS[k],label=k,ms=6)
  axes[0].legend(loc='upper right',ncol=3,frameon=False)
  fig.suptitle('Stage II-A fixed CORE32: '+title,fontsize=16,weight='bold',y=.98);fig.text(.075,.945,gmline([metric]),fontsize=11);fig.text(.075,.925,'Snapshot '+ts+' | All signs retained; missing matches remain explicit | '+cohort_status(n),fontsize=10,color='#525C65')
  fig.text(.075,.032,explain+'\nExact + / - / = classification uses integer cycle cross-products; pending is never imputed. F128/F256 GM uses the same n/32 intersection.',fontsize=10,color='#525C65',linespacing=1.5);save(fig,name)
 return dict(python_executable=sys.executable,python=sys.version,matplotlib=matplotlib.__version__,numpy=importlib.metadata.version('numpy'),platform=platform.platform(),MPLCONFIGDIR=os.environ['MPLCONFIGDIR'],TMPDIR=os.environ['TMPDIR'])

def self_test():
 q=lambda x:dict(cycles=x)
 c=dict(CH_P0=q(10**12+1),CH_F=q(10**12),DH_P0=q(10**12),DH_F=q(10**12));v,s=exact_metrics(c);assert format(v['S_CH'],'.3f')=='1.000'and s['S_CH']=='POSITIVE';assert s['S_DH']=='EXACT_ZERO'and s['I']=='NEGATIVE'
 c=dict(CH_P0=q(9),CH_F=q(10),DH_P0=q(8),DH_F=q(10));v,s=exact_metrics(c);assert s['S_CH']==s['S_DH']==s['I']=='NEGATIVE'
 assert missing_label({'missing_by_profile':{'F128':[{'status':'ARCHIVED_NEGATIVE'}]}},'F128')=='negative';assert missing_label({'missing_by_profile':{'F128':[{'status':'VERIFICATION_HOLD'}]}},'F128')=='HOLD'
 assert gm([])is None and near(gm([.5,2]),1.)
 return dict(status='PASS',independent_cases=6,exact_classification_from_integer_cycles=True,missing_never_zero=True,no_model_starts=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--provider');ap.add_argument('--output-root',default=str(BASE/'snapshots'));ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
 if a.self_test:result=self_test();dump(BASE/'CPU_PLOT_FIXTURE_QUALIFICATION.json',result);print(json.dumps(result));return
 assert a.provider;raw,p,r,s,entries,common,stats,counts,sources=load_provider(a.provider);psha=digest(raw);ownsha=sha(__file__);tag=p['observed_utc'].replace('-','').replace(':','').replace('.','').replace('+0000','Z')+'_'+psha[:10]+'_'+ownsha[:8];out=P(a.output_root)/tag
 if out.exists():
  m=json.loads((out/'MANIFEST.json').read_text());assert m['source_provider_sha256']==psha and m['plot_source_sha256']==ownsha and all(sha(out/x['path'])==x['sha256']for x in m['files'])
 else:
  out.mkdir(parents=True,exist_ok=False);data=dict(schema='DTC_STAGEIIA_CORE32_FIGURE_DATA_V1',observed_utc=p['observed_utc'],fixed_order=[dict(suite=x[0],program=x[1],input_digest=x[2])for x in FIXED],source_provider_sha256=psha,verified_source_pins=sources,summary=s,programs32=r['all_programs'],entries=entries,common_F128_F256_population=common,common_both_F_statistics=stats,common_exact_integer_sign_counts=counts,full_CORE32_complete=len(common)==32,comparison_boundary='FIRST8 completed references plus authorized Remaining24; incomplete common subset is descriptive only. No unregistered result, missing imputation, best-per-program or area equivalence.',new_models_started=0,scientific_registrations=0);dump(out/'FIGURE_DATA.json',data);(out/'PROVIDER_INPUT.json').write_bytes(raw);dump(out/'ENVIRONMENT.json',render(out,data));(out/'plot_core32_source.py').write_bytes(P(__file__).read_bytes());m=dict(schema='DTC_STAGEIIA_CORE32_FIGURE_MANIFEST_V1',source_provider_sha256=psha,plot_source_sha256=ownsha,observed_utc=p['observed_utc'],common_both_F_n=len(common),accepted_new48=s['accepted_CH'],files=[dict(path=x.name,sha256=sha(x),bytes=x.stat().st_size)for x in sorted(out.iterdir())if x.is_file()]);dump(out/'MANIFEST.json',m)
 latest=dict(schema='DTC_STAGEIIA_CORE32_FIGURE_PROVIDER_V1',snapshot=str(out),manifest=dict(path=str(out/'MANIFEST.json'),sha256=sha(out/'MANIFEST.json')),plot_source_sha256=ownsha,source_provider_sha256=psha,accepted_new48=m['accepted_new48'],common_both_F_n=m['common_both_F_n'],files=[dict(name=x['path'],path=str(out/x['path']),sha256=x['sha256'])for x in m['files']],native_actions=0,sole_publisher='ROOT_ONLY');tmp=BASE/'.PUBLICATION_PROVIDER.writing';dump(tmp,latest);os.replace(tmp,BASE/'PUBLICATION_PROVIDER.json');print(json.dumps(dict(status='CORE32_FIGURES_VERIFIED',snapshot=str(out),accepted_new48=m['accepted_new48'],common_n=m['common_both_F_n'],manifest_sha256=sha(out/'MANIFEST.json'))))
if __name__=='__main__':main()
