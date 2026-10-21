"""Paper plots from E-accepted/cache-derived CSVs only; no simulation or intake."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent; S=P/'accepted_snapshot_05'
ORDER=['convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M']
LABELS=['Conv','CFD','DWT','SAD','Vector']
BLUE='#376d87';RED='#ae6251';OFF='#8ba6b3';ON='#b28163'
plt.rcParams.update({'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.facecolor':'white'})
def rows(name):return list(csv.DictReader((S/name).open()))
def export(fig,name):
 for ext in ['pdf','png']:fig.savefig(P/(name+'.'+ext),dpi=240,bbox_inches='tight',pad_inches=.04)
 plt.close(fig)
perf={r['workload']:r for r in rows('DIAGNOSTIC_PERFORMANCE.csv')}
summary=json.loads((S/'SUMMARY.json').read_text());gm=summary['complete_five_diagnostic_GM']
values=[float(perf[w]['speedup_percent']) for w in ORDER]+[100*(gm-1)]
fig,ax=plt.subplots(figsize=(3.5,2.65));fig.subplots_adjust(left=.17,right=.98,top=.83,bottom=.24)
bars=ax.bar(range(6),values,width=.64,color=[RED if x<0 else BLUE for x in values[:5]]+['#727c85']);bars[-1].set_hatch('//')
ax.axhline(0,color='#555555',lw=.7);ax.set_xticks(range(6),LABELS+['GM']);ax.set_ylim(-12,86);ax.set_yticks([0,20,40,60,80]);ax.set_ylabel('100 (OFF / ON - 1), %',fontsize=8)
for i,v in enumerate(values):ax.annotate(f'{v:+.2f}',(i,v),xytext=(0,3 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=7)
fig.suptitle('Joint capacity + data-service diagnostic',fontsize=9,y=.98);fig.text(.57,.865,'Same new binary; all ON classes UNKNOWN',ha='center',fontsize=7)
fig.text(.5,.035,'Five fixed diagnostic inputs; GM is separate from MAIN.',ha='center',fontsize=7);export(fig,'CAPACITY_FIVE_PERFORMANCE')
stages=rows('DIAGNOSTIC_KERNEL_AND_MECHANISM_DELTAS.csv');conv=[r for r in stages if r['workload']=='convolutionSeparable'];named=conv[:2]
fig,axes=plt.subplots(1,3,figsize=(7.05,2.55));fig.subplots_adjust(left=.075,right=.99,bottom=.23,top=.80,wspace=.48)
x=np.arange(2)
for j,(label,color) in enumerate([('OFF',OFF),('ON',ON)]):axes[0].bar(x+(j-.5)*.32,[int(r[label+'_gpu_sim_cycle'])/1000 for r in named],.30,label=label,color=color)
axes[0].set_xticks(x,['K1 rows','K2 columns']);axes[0].set_ylabel('Elapsed GPU cycles (thousands)');axes[0].set_title('(a) Named kernel duration',fontsize=8);axes[0].legend(frameon=False,fontsize=7);axes[0].set_ylim(0,195)
vals=[int(r['ON_minus_OFF_cycles']) for r in conv];axes[1].bar(range(3),vals,color=BLUE);axes[1].axhline(0,color='#666666',lw=.7);axes[1].set_xticks(range(3),['K1','K2','residual']);axes[1].set_ylabel('Elapsed GPU cycles, ON - OFF');axes[1].set_title('(b) Total reduction: 24,815',fontsize=8);axes[1].set_ylim(-29000,4800)
for i,v in enumerate(vals):axes[1].annotate(f'{v:+,}',(i,v),xytext=(0,-4 if v<0 else 3),textcoords='offset points',ha='center',va='top' if v<0 else 'bottom',fontsize=7)
for j,(key,label,color) in enumerate([('lower_read_bytes','read',OFF),('lower_wb_bytes','WB',ON)]):
 axes[2].bar(x+(j-.5)*.32,[int(r['OFF_EPL2MSV1_'+key])/1e6 for r in named],.30,label=label,color=color)
axes[2].set_xticks(x,['K1 rows','K2 columns']);axes[2].set_ylabel('OFF - ON lower bytes (MB)');axes[2].set_title('(c) Both ON traffic counts = 0',fontsize=8);axes[2].legend(frameon=False,fontsize=7);axes[2].set_ylim(0,48)
fig.suptitle('Conv: columns contribute 90.61% of the observed elapsed reduction',fontsize=9,y=.98)
fig.text(.5,.025,'Elapsed phases are not exclusive stalls. Counter reductions do not identify causal shares.',ha='center',fontsize=7);export(fig,'CONV_CAPACITY_PHASES')
metrics=rows('DIAGNOSTIC_TERMINAL_MECHANISMS.csv')
def metric(w,k):return next(r for r in metrics if r['workload']==w and r['family']=='local_service' and r['metric']==k)
fig,axes=plt.subplots(1,2,figsize=(7.05,2.65));fig.subplots_adjust(left=.08,right=.99,bottom=.24,top=.80,wspace=.30)
for ax,key,title in zip(axes,['lower_read_bytes','lower_wb_bytes'],['(a) Lower read traffic','(b) Lower WB traffic']):
 for j,(label,color) in enumerate([('OFF',OFF),('ON',ON)]):
  v=[int(metric(w,key)[label])/1e6 for w in ORDER];xs=np.arange(5)+(j-.5)*.32;ax.bar(xs,v,.3,label=label,color=color)
  for xx,vv in zip(xs,v):
   if vv==0:ax.annotate('0',(xx,0),xytext=(0,2),textcoords='offset points',ha='center',fontsize=6)
 ax.set_xticks(range(5),LABELS);ax.set_ylabel('MB (decimal)');ax.set_title(title,fontsize=9);ax.legend(frameon=False,fontsize=7);ax.set_ylim(0,85)
fig.suptitle('Accepted whole-application lower-interface byte counts',fontsize=9,y=.98);fig.text(.5,.025,'Issue/service accounting, not DRAM bandwidth or numerical output verification.',ha='center',fontsize=7);export(fig,'CAPACITY_FIVE_LOWER_TRAFFIC')
fig,axes=plt.subplots(5,1,figsize=(7.05,7.0));fig.subplots_adjust(left=.15,right=.985,top=.93,bottom=.08,hspace=.92)
for ax,w,label in zip(axes,ORDER,LABELS):
 rr=[r for r in stages if r['workload']==w];v=[int(r['ON_minus_OFF_cycles']) for r in rr];ax.bar(range(len(v)),v,color=[RED if z>0 else BLUE for z in v]);ax.axhline(0,color='#777777',lw=.65);ax.set_xticks(range(len(v)),['residual' if r['kernel_ordinal']=='FINAL_RESIDUAL' else 'K'+r['kernel_ordinal'] for r in rr]);ax.tick_params(labelsize=7);ax.set_title(f"{label} | total ON - OFF = {int(perf[w]['ON_minus_OFF_cycles']):+,}",fontsize=8);ax.set_ylabel('GPU cycles',fontsize=7)
 span=max(max(v)-min(v),abs(min(v)),abs(max(v)),10);ax.set_ylim(min(min(v),0)-span*.32,max(max(v),0)+span*.32)
 for n,z in enumerate(v):
  if z:ax.annotate(f'{z:+,}',(n,z),xytext=(0,-3 if z<0 else 3),textcoords='offset points',ha='center',va='top' if z<0 else 'bottom',fontsize=7)
fig.suptitle('Five diagnostic pairs: elapsed phase differences, including adverse values',fontsize=10,y=.985);fig.text(.5,.015,'Named durations + final residual close to accepted program time; no summation of request waits.',ha='center',fontsize=7);export(fig,'CAPACITY_FIVE_STAGE_DELTAS')
lines=['% Same93a9 binary diagnostic; all ON UNKNOWN; separate from original MAIN.','\\begin{tabular}{lrrrl}','\\hline','Input & OFF cycles & ON cycles & OFF/ON & ON class \\\\','\\hline']
for w,l in zip(ORDER,LABELS):
 r=perf[w];lines.append(f"{l} & {int(r['OFF_cycles']):,} & {int(r['ON_cycles']):,} & {float(r['ratio_OFF_over_ON']):.4f} & UNKNOWN \\\\")
lines.extend(['\\hline',f'GM ($n=5$) & -- & -- & {gm:.4f} & -- \\\\','\\hline','\\end{tabular}']);(P/'CAPACITY_FIVE_TABLE.tex').write_text('\n'.join(lines)+'\n')
