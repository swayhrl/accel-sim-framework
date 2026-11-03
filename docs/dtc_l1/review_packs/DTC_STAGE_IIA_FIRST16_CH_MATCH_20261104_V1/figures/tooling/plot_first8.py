#!/usr/bin/env python3
"""Read-only Matplotlib consumer of SHA-verified B PUBLICATION_PROVIDER only."""
import argparse,datetime,gzip,hashlib,json,math,os,pathlib,sys,platform,importlib.metadata
P=pathlib.Path;BASE=P(__file__).resolve().parent
for name in ['tmp','mpl-config']: (BASE/name).mkdir(exist_ok=True)
for key in ['TMPDIR','TMP','TEMP']:os.environ.setdefault(key,str(BASE/'tmp'))
os.environ.setdefault('MPLCONFIGDIR',str(BASE/'mpl-config'))
FIXED=[('convolutionSeparable','4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449'),('scan','6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'),('2DCONV','d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0'),('ATAX','eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950'),('MVT','f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079'),('BICG','ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef'),('vectorAdd','e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799'),('GEMM','fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318')]
F=('F128','F256');ACCEPT='ACCEPTED_MATCHED_QUADRUPLE';COLORS={'P0':'#727980','F128':'#176DA0','F256':'#C96B18'};MARKERS={'P0':'o','F128':'s','F256':'^'}
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def dump(p,x):P(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def verified(path,want):
 b=P(path).read_bytes();assert digest(b)==want,('SHA_MISMATCH',str(path));return b
def near(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-12)
def gm(values):return math.exp(sum(math.log(v)for v in values)/len(values))if values else None

def load_provider(path):
 raw=P(path).read_bytes();provider=json.loads(raw);assert provider['schema']=='DTC_STAGEIIA_FIRST16_ANALYSIS_PUBLICATION_PROVIDER_V1'
 manifest=json.loads(verified(provider['manifest']['path'],provider['manifest']['sha256']));mp={r['path']:r['sha256']for r in manifest['files']};payload={};sources=[]
 for leaf in ['RESULTS.json.gz','SUMMARY.json.gz']:
  candidates=[r for r in provider['files']if P(r['path']).name==leaf];assert len(candidates)==1;r=candidates[0];assert mp.get(r['path'])==r['sha256'];b=verified(r['path'],r['sha256']);payload[leaf]=json.loads(gzip.decompress(b));sources.append(dict(path=r['path'],sha256=r['sha256'],bytes=len(b)))
 report=payload['RESULTS.json.gz'];summary=payload['SUMMARY.json.gz'];assert report['fixed_plan_commit']=='5001c3f35052f7f91f1ad41eeff83f2947a0878d';assert report['scientific_population']==summary['scientific_population']=='FIRST8_PREDECLARED_SUBSET_NOT_35_OR_CORE32'
 assert report['expected_programs']==[p for p,d in FIXED]and report['expected_inputs']==[d for p,d in FIXED]
 assert report['observed_utc']==summary['observed_utc']==provider['observed_utc'];assert report['no_best_per_program_selection']and report['no_missing_imputation']and report['no_IR_R2_EP_PQ_PS_substitution'];assert len(report['rows'])==16
 rows={(r['input_digest'],r['profile']):r for r in report['rows']};assert len(rows)==16 and set(rows)=={(d,f)for p,d in FIXED for f in F}
 for p,d in FIXED:
  a,b=(rows[(d,f)]for f in F);assert a['program']==b['program']==p;assert a['CH_P0']==b['CH_P0']and a['DH_P0']==b['DH_P0']
  for r in [a,b]:
   for key in ['CH_P0','DH_P0','DH_F']:assert type(r[key])is int and r[key]>0
   metrics=r['metrics'];accepted=r['status']==ACCEPT
   if accepted:
    assert type(r['CH_F'])is int and r['CH_F']>0
    expected={'S_CH':r['CH_P0']/r['CH_F'],'S_DH':r['DH_P0']/r['DH_F'],'R':r['CH_F']/r['DH_F'],'R_P0':r['CH_P0']/r['DH_P0']};expected['I']=expected['S_DH']/expected['S_CH']
    assert all(near(metrics[k],v)for k,v in expected.items()),('METRIC_MISMATCH',p,r['profile'])
   else:assert all(metrics.get(k)is None for k in ['S_CH','S_DH','R','I','R_P0']),('UNACCEPTED_METRIC',p,r['profile'])
 common=[d for p,d in FIXED if all(rows[(d,f)]['status']==ACCEPT for f in F)];assert set(common)==set(report['common_F128_F256_population']);assert len(common)==summary['common_both_F_n']
 assert report['common_F128_F256_metrics']==summary['common_F128_F256_metrics']
 for f in F:
  for metric in ['S_CH','S_DH','R','I','R_P0']:
   stat=summary['common_F128_F256_metrics'][f][metric];assert stat['n']==len(common)and set(stat['population'])==set(common)
   calc=gm([rows[(d,f)]['metrics'][metric]for d in common]);assert(calc is None and stat['GM']is None)or(calc is not None and near(calc,stat['GM']))
 return raw,provider,report,summary,rows,common,sources

def missing_label(row):
 s=row['status'].upper()
 if 'NEGATIVE'in s or 'FAIL'in s:return 'negative'
 if 'HOLD'in s:return 'HOLD'
 return 'pending'
def plot_data(provider,report,summary,rows,common,sources,provider_sha):
 entries=[]
 for p,d in FIXED:
  for f in F:
   r=rows[(d,f)];ok=r['status']==ACCEPT
   entries.append(dict(program=p,input_digest=d,profile=f,cohort=r['cohort'],status=r['status'],observed_status=r.get('observed_status'),plot_status='accepted'if ok else missing_label(r),CH_P0_cycles=r['CH_P0'],DH_P0_cycles=r['DH_P0'],CH_F_cycles=r['CH_F']if ok else None,DH_F_cycles=r['DH_F'],S_CH=r['metrics']['S_CH']if ok else None,S_DH=r['metrics']['S_DH']if ok else None,I=r['metrics']['I']if ok else None,source_refs=r['source_refs']))
 return dict(schema='DTC_STAGEIIA_FIRST8_SCIENTIFIC_FIGURE_DATA_V1',observed_utc=provider['observed_utc'],population='FIRST8_PREDECLARED_SUBSET_NOT_CORE32_OR_FULL35',fixed_order=[dict(program=p,input_digest=d)for p,d in FIXED],provider_sha256=provider_sha,verified_sources=sources,rows=entries,common_F128_F256_population=common,common_F128_F256_metrics=summary['common_F128_F256_metrics'],accepted_CH=summary['accepted_CH'],missing_CH=16-summary['accepted_CH'],all_registered16_terminal_verified=summary['all_registered16_terminal_verified'],comparison_policy='Only complete accepted quadruples plotted for F. Missing data never zero or one; P0 is a reference, not an imputed F result. F128/F256 GM share B-declared common population, all signs preserved.',CH_DH_equal_downstream_not_equal_L1_area=True,new_models_started=0,registrations=0)

def render(out,data,rows,summary,common):
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'DTC_STAGEIIA_FIRST8_FIGURES_V1','savefig.facecolor':'white'})
 labels=[('convSeparable'if p=='convolutionSeparable'else p)+'\n'+d[:8]for p,d in FIXED]+['GM\ncommon n='+str(len(common))+'/8'];xs=list(range(8))+[8.75];offset={'P0':-.22,'F128':0.,'F256':.22};time_label=datetime.datetime.fromisoformat(data['observed_utc']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S CST')
 def frame(ax,ylabel,limits):
  ax.axhline(1.,color='#50565D',ls='--',lw=1.,zorder=1);ax.axvline(8.2,color='#B3B9BF',lw=.8);ax.set_xticks(xs,labels);ax.set_xlim(-.65,9.35);ax.set_ylim(*limits);ax.set_ylabel(ylabel);ax.grid(axis='y',color='#E3E7EA',lw=.7);ax.set_axisbelow(True)
 def pending(ax,index,f,row):
  label=missing_label(row);color='#9A3737'if label=='negative'else'#696F75'
  ax.text(index,.075 if f=='F128'else .025,('128 'if f=='F128'else'256 ')+label,transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=7.5,color=color)
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=180);fig.savefig(out/(name+'.svg'),metadata={'Date':None});plt.close(fig)
 allself=[rows[(d,f)]['metrics'][metric]for p,d in FIXED for f in F for metric in ['S_CH','S_DH']if rows[(d,f)]['status']==ACCEPT]
 limits=(max(0,min([1.]+allself)-.17),max([1.]+allself)+.16)
 fig,axes=plt.subplots(2,1,figsize=(15.5,9.2),sharex=True);fig.subplots_adjust(left=.075,right=.98,top=.88,bottom=.17,hspace=.25)
 for ax,metric,title in zip(axes,['S_CH','S_DH'],['CH: conventional cache','DH: DTC-L1']):
  frame(ax,'Speedup: own P0 cycles / cycles',limits);ax.set_title(title,loc='left',weight='bold')
  for i,(p,d)in enumerate(FIXED):
   ax.plot(i+offset['P0'],1.,MARKERS['P0'],color=COLORS['P0'],ms=5,zorder=3)
   for f in F:
    r=rows[(d,f)]
    if r['status']==ACCEPT:
     v=r['metrics'][metric];ax.plot(i+offset[f],v,MARKERS[f],color=COLORS[f],ms=7,zorder=4);ax.annotate(f'{v:.3f}',(i+offset[f],v),xytext=((7,9)if f=='F256'else(-7,-16)),textcoords='offset points',ha='left'if f=='F256'else'right',fontsize=8,color=COLORS[f])
    else:pending(ax,i,f,r)
  if common:
   ax.plot(xs[-1]+offset['P0'],1.,MARKERS['P0'],color=COLORS['P0'],ms=5)
   for f in F:
    v=summary['common_F128_F256_metrics'][f][metric]['GM'];ax.plot(xs[-1]+offset[f],v,MARKERS[f],color=COLORS[f],ms=7);ax.annotate(f'{v:.3f}',(xs[-1]+offset[f],v),xytext=((7,9)if f=='F256'else(-7,-16)),textcoords='offset points',ha='left'if f=='F256'else'right',fontsize=8,color=COLORS[f])
  else:ax.text(xs[-1],.025,'no common\naccepted input',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,color='#696F75')
  ax.text(.01,.96,'>1 faster; <1 slower',transform=ax.transAxes,va='top',fontsize=9,color='#50565D')
 for key in ['P0',*F]:axes[0].plot([],[],MARKERS[key],color=COLORS[key],label=key+(' reference'if key=='P0'else' (complete four-way only)'),ms=6)
 axes[0].legend(loc='upper right',ncol=3,frameon=False,fontsize=9)
 fig.suptitle('Stage II-A first 8 predeclared programs (subset): P0 / F128 / F256',fontsize=16,weight='bold',y=.97)
 fig.text(.075,.915,f"Snapshot {time_label} | CH accepted {summary['accepted_CH']}/16 | Fixed 8 inputs; no per-program winner selection",fontsize=10,color='#50565D')
 fig.text(.075,.065,'Pending / negative / HOLD labels are status annotations, not plotted values. Both panels omit F until its matched quadruple is accepted.\nGM uses exactly the same F128/F256 common set shown as n/8. Matched downstream options do not imply equal L1 area or cost.',fontsize=10,color='#50565D',linespacing=1.5)
 save(fig,'CH_DH_P0_normalized_first8')
 values=[rows[(d,f)]['metrics']['I']for p,d in FIXED for f in F if rows[(d,f)]['status']==ACCEPT];limits=(max(0,min([1.]+values)-.14),max([1.]+values)+.12)
 fig,ax=plt.subplots(figsize=(15.5,6.2));fig.subplots_adjust(left=.075,right=.98,top=.79,bottom=.26);frame(ax,'Extra relative DH benefit: I = S_DH / S_CH',limits)
 for i,(p,d)in enumerate(FIXED):
  for f,off in [('F128',-.11),('F256',.11)]:
   r=rows[(d,f)]
   if r['status']==ACCEPT:
    v=r['metrics']['I'];ax.plot(i+off,v,MARKERS[f],color=COLORS[f],ms=8,zorder=3);ax.annotate(f'{v:.3f}\n({(v-1)*100:+.1f}%)',(i+off,v),xytext=((8,12)if f=='F256'else(-8,-20)),textcoords='offset points',ha='left'if f=='F256'else'right',fontsize=8,color=COLORS[f])
   else:pending(ax,i,f,r)
 if common:
  for f,off in [('F128',-.11),('F256',.11)]:
   v=summary['common_F128_F256_metrics'][f]['I']['GM'];ax.plot(xs[-1]+off,v,MARKERS[f],color=COLORS[f],ms=8);ax.annotate(f'{v:.3f}',(xs[-1]+off,v),xytext=((8,12)if f=='F256'else(-8,-16)),textcoords='offset points',ha='left'if f=='F256'else'right',fontsize=8,color=COLORS[f])
 else:ax.text(xs[-1],.025,'no common\naccepted input',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,color='#696F75')
 for f in F:ax.plot([],[],MARKERS[f],color=COLORS[f],label=f,ms=7)
 ax.legend(loc='upper right',ncol=2,frameon=False);ax.text(.01,.96,'I > 1: relative change favours DH\nI < 1: relative change favours CH',transform=ax.transAxes,va='top',fontsize=9,color='#50565D')
 fig.suptitle('Stage II-A first 8 predeclared programs (subset): matched downstream interaction',fontsize=15,weight='bold',y=.96)
 fig.text(.075,.86,f'Snapshot {time_label} | Complete four-way matches only; negative cases retained | Common-set GM n={len(common)}/8',fontsize=10,color='#50565D')
 fig.text(.075,.075,'Blank entries carry explicit status labels; no missing speedup is imputed. GM uses B summary common population at both F levels.\nI measures change relative to P0; I > 1 does not itself prove DH is faster than CH, or equal hardware cost.',fontsize=10,color='#50565D',linespacing=1.5)
 save(fig,'relative_extra_DH_benefit_I_first8')
 return {'matplotlib':matplotlib.__version__,'numpy':importlib.metadata.version('numpy'),'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),'matplotlib_backend':matplotlib.get_backend(),'MPLCONFIGDIR':os.environ['MPLCONFIGDIR'],'new_models_started':0}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--provider',required=True);ap.add_argument('--output-root',default=str(BASE/'snapshots'));a=ap.parse_args();raw,provider,report,summary,rows,common,sources=load_provider(a.provider);psha=digest(raw);ownsha=sha(__file__);tag=provider['observed_utc'].replace('-','').replace(':','').replace('.','').replace('+0000','Z')+'_'+psha[:10]+'_'+ownsha[:8];out=P(a.output_root)/tag
 if out.exists():
  manifest=json.loads((out/'MANIFEST.json').read_text());assert all(sha(out/f['path'])==f['sha256']for f in manifest['files']);assert manifest['provider_sha256']==psha and manifest['plot_script_sha256']==ownsha
 else:
  out.mkdir(parents=True,exist_ok=False);data=plot_data(provider,report,summary,rows,common,sources,psha);dump(out/'FIGURE_DATA.json',data);(out/'PROVIDER_INPUT.json').write_bytes(raw);environment=render(out,data,rows,summary,common);dump(out/'ENVIRONMENT.json',environment);(out/'plot_first8_source.py').write_bytes(P(__file__).read_bytes());files=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(out.iterdir())if p.is_file()];manifest=dict(schema='DTC_STAGEIIA_FIRST8_FIGURE_MANIFEST_V1',provider_path=str(P(a.provider).resolve()),provider_sha256=psha,plot_script_sha256=ownsha,observed_utc=provider['observed_utc'],accepted_CH=summary['accepted_CH'],common_both_F_n=len(common),files=files,new_model_starts=0,registrations=0);dump(out/'MANIFEST.json',manifest)
 latest=dict(schema='DTC_STAGEIIA_FIRST8_FIGURE_PROVIDER_V1',snapshot=str(out),manifest=dict(path=str(out/'MANIFEST.json'),sha256=sha(out/'MANIFEST.json')),source_provider_sha256=psha,accepted_CH=summary['accepted_CH'],common_both_F_n=len(common),files=[dict(name=f['path'],path=str(out/f['path']),sha256=f['sha256'])for f in manifest['files']],model_starts=0)
 tmp=BASE/'.PUBLICATION_PROVIDER.writing';dump(tmp,latest);os.replace(tmp,BASE/'PUBLICATION_PROVIDER.json');print(json.dumps(dict(status='FIGURES_SHA_VERIFIED',snapshot=str(out),accepted_CH=summary['accepted_CH'],common_both_F_n=len(common),manifest_sha256=sha(out/'MANIFEST.json'))))
if __name__=='__main__':main()
