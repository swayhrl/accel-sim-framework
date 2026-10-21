"""Render existing accepted D tables; no acceptance, native or trace reads."""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
G=json.loads((P/'CONV_TM_GRID.json').read_text());grid=G['corners']
fig,axes=plt.subplots(1,3,figsize=(10.6,3.9));fig.subplots_adjust(left=.07,right=.98,top=.79,bottom=.23,wspace=.4)
ax=axes[0];values=np.array([[grid['C00']['cycles'],grid['C01']['cycles']],[grid['C10']['cycles'],grid['C11']['cycles']]])
ax.imshow(values-values[0,0],cmap='Blues_r',vmin=-1100,vmax=0,aspect='auto')
for r in range(2):
 for c in range(2):ax.text(c,r,f'{values[r,c]:,}',ha='center',va='center',fontsize=11,color='#1d303c' if r==0 and c==0 else 'white')
ax.set_xticks([0,1],['M=0','M=1']);ax.set_yticks([0,1],['T=0','T=1']);ax.set_title('(a) Accepted program cycles',fontsize=10)
ax=axes[1];profiles=['WV_T','WV_M','F'];normal=[371495,0,0];avoided=[0,371495,371495];xs=range(3)
ax.bar(xs,normal,color='#a36d56',label='Allocated');ax.bar(xs,avoided,bottom=normal,color='#537c92',label='Avoided')
ax.set_xticks(xs,['T only','M only','T+M']);ax.set_ylabel('RO line-MSHR allocations');ax.set_yticks([0,100000,200000,300000,400000],['0','100k','200k','300k','400k']);ax.set_ylim(0,490000);ax.legend(frameon=False,fontsize=8,loc='upper center');ax.set_title('(b) Resource behavior differs',fontsize=10)
ax=axes[2];vals=[-706,1669,963];ax.bar(['Rows','Columns','Total'],vals,color=['#537c92','#a36d56','#a36d56']);ax.axhline(0,color='#777777',lw=.7)
for n,v in enumerate(vals):ax.annotate(f'{v:+,}',(n,v),xytext=(0,4 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
ax.set_ylim(-1100,2100);ax.set_ylabel('Signed GPU cycle interaction');ax.set_title('(c) C11 - C10 - C01 + C00',fontsize=10)
for ax in axes[1:]:ax.spines[['top','right']].set_visible(False)
fig.suptitle('Conv: equal timing does not imply functional equivalence',fontsize=12)
fig.text(.5,.035,'T or M enables the common RO path. Active corners have zero successful Tag detach.\nJoint saving is 963 cycles, rather than the sum of the two either-on savings (1,926).',ha='center',fontsize=9)
for ext in ['pdf','png']:fig.savefig(P/('CONV_TM_FACTORIAL.'+ext),dpi=220)
plt.close(fig)
rows=json.loads((P/'CFD_ELAPSED_STAGE_DECOMPOSITION.json').read_text())
fig,axes=plt.subplots(3,1,figsize=(7.6,6.1));fig.subplots_adjust(left=.14,right=.97,top=.9,bottom=.16,hspace=.64)
labels=['K1 init','K2 init','K3 init','K4 step','K5 flux']
for ax,row in zip(axes,rows):
 vals=row['kernel_deltas'];ax.bar(range(5),vals,color=['#a36d56' if v>0 else '#537c92' for v in vals],width=.55);ax.axhline(0,color='#777777',lw=.7)
 ax.set_title(f"{row['left']} → F | total {row['whole_program']:+,} cycles",fontsize=10);ax.set_xticks(range(5),labels,fontsize=8);ax.set_ylabel('F - left cycles',fontsize=9)
 span=max(max(vals)-min(vals),35);ax.set_ylim(min([0]+vals)-.22*span,max([0]+vals)+.28*span)
 for n,v in enumerate(vals):
  if v:ax.annotate(f'{v:+,}',(n,v),xytext=(0,3 if v>=0 else -3),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
 ax.spines[['top','right']].set_visible(False)
fig.suptitle('CFD: conditional flux gains differ from the main S-to-F result',fontsize=12)
fig.text(.5,.035,'Each panel has its own vertical scale. Negative favors F; all final residuals are zero.\nElapsed kernel durations close to program deltas; overlapping request waits are not GPU stalls.',ha='center',fontsize=9)
for ext in ['pdf','png']:fig.savefig(P/('CFD_CONDITIONAL_KERNEL_EFFECTS.'+ext),dpi=220)
plt.close(fig)
# Complete original-ten outcomes, including both nonaccepted resource stops.
rows=list(csv.DictReader((P/'TEN_AUTHORIZED_CONTROL_RESULTS.csv').open()))
lines=[r'% Standalone EN-v20 proposal; no mother edit or partial-run performance.',r'\begin{table*}[t]',r'\centering',r'\caption{Original ten authorized control attempts: eight complete accepted results and two RAM stops. Delta is control minus its original accepted anchor.}',r'\label{tab:ten-controls}',r'\begin{tabular}{llrlrr}',r'\hline',r'Input & Control & Attempt & Outcome & Cycles & $\Delta$ anchor \\',r'\hline']
for r in rows:
 workload={'convolutionSeparable':'Conv','cfd_097k':'CFD','dwt2d':'DWT'}[r['workload']];prof=r['profile'].replace('_',r'\_');aid=r['attempt_id'].split('_')[0];ok=r['scientific_acceptance']=='PASS';cycle=r['accepted_cycles'] if ok else '--';delta=f"{int(r['control_minus_anchor_cycles']):+d}" if ok else '--';status='Accepted' if ok else 'RAM stop'
 lines.append(f'{workload} & {prof} & {aid} & {status} & {cycle} & {delta} '+r'\\')
lines += [r'\hline',r'\end{tabular}',r'{\footnotesize W\_ONLY and S\_COPY\_FREE use S anchors; other controls use F anchors. COPY\_FREE is diagnostic. Original DWT partial cycles are excluded; later retries are separate.}',r'\end{table*}']
(P/'TEN_AUTHORIZED_CONTROL_RESULTS_TABLE.tex').write_text('\n'.join(lines)+'\n')
