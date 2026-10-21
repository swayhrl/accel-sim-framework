import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;S=P/'accepted_snapshot_04'
def read(n):return list(csv.DictReader((S/n).open()))
def export(fig,name):
 for e in ['pdf','png']:fig.savefig(P/(name+'.'+e),dpi=220,bbox_inches='tight')
 plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
p={r['workload']:r for r in read('DIAGNOSTIC_PERFORMANCE.csv')};order=['cfd_097k','vectorAdd_4M','sad','dwt2d'];labels=['CFD','Vector','SAD','DWT'];vals=[float(p[w]['speedup_percent']) for w in order]
fig,ax=plt.subplots(figsize=(6.4,2.7));ax.bar(range(4),vals,color=['#ae6251' if v<0 else '#376d87' for v in vals]);ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(4),labels);ax.set_ylabel('100 (OFF / ON - 1), %');ax.set_ylim(-10,87);ax.set_title('Four accepted joint-capacity/data-service diagnostics; ON UNKNOWN',fontsize=10)
for i,v in enumerate(vals):ax.annotate(f'{v:+.3f}%',(i,v),xytext=(0,4 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top')
fig.text(.5,-.05,'Conv pair pending; original MAIN S/F and seven-input denominator unchanged.',ha='center',fontsize=8);export(fig,'CAPACITY_FOUR_PERFORMANCE')
r=[x for x in read('DIAGNOSTIC_KERNEL_AND_MECHANISM_DELTAS.csv') if x['workload']=='dwt2d'];v=[int(x['ON_minus_OFF_cycles']) for x in r]
fig,ax=plt.subplots(figsize=(7.2,2.8));ax.bar(range(len(v)),v,color=['#ae6251' if x>0 else '#376d87' for x in v]);ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(len(v)),['tail' if x['kernel_ordinal']=='FINAL_RESIDUAL' else 'K'+x['kernel_ordinal'] for x in r]);ax.set_ylabel('Elapsed GPU cycles, ON - OFF');ax.set_title('DWT: -9,485 cycles; K1/K5/K8 account for -8,773',fontsize=10);ax.set_ylim(-5200,650)
for i,x in enumerate(v):
 if abs(x)>20:ax.annotate(f'{x:+,}',(i,x),xytext=(0,-4 if x<0 else 4),textcoords='offset points',ha='center',va='top' if x<0 else 'bottom',fontsize=8)
export(fig,'DWT_CAPACITY_KERNEL_DELTAS')
