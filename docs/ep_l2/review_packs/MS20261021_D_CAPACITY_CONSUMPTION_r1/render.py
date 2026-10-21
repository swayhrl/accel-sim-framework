"""Measured-data plots from exact accepted snapshots, no simulation/qualification."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;D=P/'accepted_snapshot_03'
def read(n):return list(csv.DictReader((D/n).open()))
def export(fig,name):
 for ext in ['pdf','png']:fig.savefig(P/(name+'.'+ext),dpi=220,bbox_inches='tight')
 plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
rows=read('DIAGNOSTIC_PERFORMANCE.csv');order=['cfd_097k','vectorAdd_4M','sad'];labels=['CFD','Vector','SAD'];idx={r['workload']:r for r in rows}
fig,ax=plt.subplots(figsize=(6.2,2.6));v=[float(idx[w]['speedup_percent']) for w in order];ax.bar(range(3),v,color=['#ae6251' if x<0 else '#376d87' for x in v]);ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(3),labels);ax.set_ylabel('100 (OFF / ON - 1), %');ax.set_title('Joint capacity + free data service; accepted ON class: UNKNOWN',fontsize=10);ax.set_ylim(-10,87)
for i,x in enumerate(v):ax.annotate(f'{x:+.3f}%',(i,x),xytext=(0,3 if x>=0 else -3),textcoords='offset points',ha='center',va='bottom' if x>=0 else 'top')
fig.text(.5,-.05,'Same new binary within each pair. Separate from main61 S/F; not a hardware bound.',ha='center',fontsize=8);export(fig,'CAPACITY_THREE_PERFORMANCE')
t=read('DIAGNOSTIC_KERNEL_AND_MECHANISM_DELTAS.csv');fig,axes=plt.subplots(1,3,figsize=(8.6,2.85),layout='constrained')
for ax,w,name in zip(axes,order,labels):
 r=[x for x in t if x['workload']==w];v=[int(x['ON_minus_OFF_cycles']) for x in r];ax.bar(range(len(v)),v,color=['#ae6251' if x>0 else '#376d87' for x in v]);ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(len(v)),['tail' if x['kernel_ordinal']=='FINAL_RESIDUAL' else 'K'+x['kernel_ordinal'] for x in r]);ax.set_title(name+' | ON - OFF',fontsize=10)
 for i,x in enumerate(v):
  if x:ax.annotate(f'{x:+,}',(i,x),xytext=(0,3 if x>0 else -3),textcoords='offset points',ha='center',va='bottom' if x>0 else 'top',fontsize=8)
 lo,hi=ax.get_ylim();pad=max(hi-lo,1)*.25;ax.set_ylim(lo-pad,hi+pad);ax.set_ylabel('Elapsed GPU cycles')
export(fig,'CAPACITY_KERNEL_STAGE_DELTAS')
m=read('DIAGNOSTIC_TERMINAL_MECHANISMS.csv');get=lambda w,k:next(x for x in m if x['workload']==w and x['family']=='local_service' and x['metric']==k)
fig,axes=plt.subplots(1,2,figsize=(7.2,2.6),layout='constrained')
for ax,key,title in zip(axes,['lower_read_bytes','lower_wb_bytes'],['Lower read bytes','Lower WB bytes']):
 for j,label in enumerate(['OFF','ON']):
  v=[int(get(w,key)[label])/1e6 for w in order];x=[i+(j-.5)*.32 for i in range(3)];ax.bar(x,v,.3,label=label,color=['#8ba6b3','#b28163'][j])
  for xx,vv in zip(x,v):ax.text(xx,vv+.4,f'{vv:.3f}',ha='center',fontsize=7,rotation=90)
 ax.set_xticks(range(3),labels);ax.set_ylabel('MB, decimal');ax.set_title(title,fontsize=10);ax.set_ylim(0,40 if key=='lower_read_bytes' else 17);ax.legend(frameon=False,fontsize=8)
export(fig,'CAPACITY_LOWER_TRAFFIC')
lines=['\\begin{tabular}{lrrrl}','\\hline','Input & OFF & ON & Speedup (\\%) & ON class \\\\','\\hline']
for w,n in zip(order,labels):
 r=idx[w];lines.append(f"{n} & {int(r['OFF_cycles']):,} & {int(r['ON_cycles']):,} & {float(r['speedup_percent']):+.3f} & UNKNOWN \\\\")
lines+=['\\hline','\\end{tabular}'];(P/'CAPACITY_THREE_TABLE.tex').write_text('\n'.join(lines)+'\n')
