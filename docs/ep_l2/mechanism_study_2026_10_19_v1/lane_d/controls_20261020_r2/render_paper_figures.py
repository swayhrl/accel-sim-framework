"""Render frozen D tables only; no input acceptance or simulator invocation."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
rows={r['profile']:r for r in csv.DictReader((P/'CONV_CONDITION_PERFORMANCE.csv').open())}
profiles=['S','W_ONLY','F_MINUS_V','F'];labels=['S','W only','F minus V','F']
colors=['#92979a','#537c92','#aa6659','#365e75']
fig,axes=plt.subplots(1,2,figsize=(8.7,3.6));fig.subplots_adjust(left=.09,right=.98,top=.83,bottom=.25,wspace=.34)
ax=axes[0];values=[int(rows[p]['cycles'])-int(rows['S']['cycles']) for p in profiles]
ax.bar(labels,values,color=colors,width=.6);ax.axhline(0,color='#777777',lw=.7)
for n,v in enumerate(values):ax.annotate(f'{v:+,}',(n,v),xytext=(0,4 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
ax.set_ylim(-2000,950);ax.set_ylabel('Elapsed GPU cycles relative to S');ax.set_title('(a) Whole program',fontsize=11)
ax=axes[1]
for k,(profile,color) in enumerate(zip(['W_ONLY','F_MINUS_V','F'],colors[1:])):
 vals=[int(rows[profile][s+'_cycles'])-int(rows['S'][s+'_cycles']) for s in ['Rows','Columns']]
 xs=[n+(k-1)*.25 for n in range(2)];ax.bar(xs,vals,.24,label={'W_ONLY':'W only','F_MINUS_V':'F minus V','F':'F'}[profile],color=color)
 for x,v in zip(xs,vals):ax.annotate(f'{v:+,}',(x,v),xytext=(0,3 if v>=0 else -3),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=7)
ax.set_xticks([0,1],['Rows','Columns']);ax.axhline(0,color='#777777',lw=.7);ax.set_ylim(-1650,1750)
ax.set_title('(b) Named kernels; zero final residual',fontsize=11);ax.legend(frameon=False,fontsize=8,loc='upper right')
for ax in axes:ax.spines[['top','right']].set_visible(False)
fig.suptitle('Conv: accepted conditional controls on the same main61 binary',fontsize=12)
fig.text(.5,.045,'W only recovers 96.17% of the net S-to-F cycle improvement; this is not a copy-attribution fraction.\nF minus V is 1,994 cycles slower than F: Rows +1,555; Columns +439.',ha='center',fontsize=9)
for ext in ['pdf','png']:fig.savefig(P/('CONV_CONTROL_KERNEL_EFFECTS.'+ext),dpi=220)
plt.close(fig)
# Exact table rows; no estimated mechanism contribution columns.
lines=[r'% Standalone EN-v20 insertion candidate; mother manuscript untouched.',r'\begin{table}[t]',r'\centering',r'\caption{Conv conditional program and kernel cycle differences. Negative values favor the right endpoint. All final residuals are zero.}',r'\label{tab:conv-controls-kernels}',r'\begin{tabular}{lrrr}',r'\hline',r'Left $\rightarrow$ right & Rows & Columns & Total \\',r'\hline']
for l,r in [('S','W_ONLY'),('S','F'),('W_ONLY','F'),('F_MINUS_V','F')]:
 vals=[int(rows[r][s+'_cycles'])-int(rows[l][s+'_cycles']) for s in ['Rows','Columns']];v=int(rows[r]['cycles'])-int(rows[l]['cycles'])
 name={'S':'S','W_ONLY':'W','F_MINUS_V':r'F$-$V','F':'F'}
 lines.append(name[l]+r' $\rightarrow$ '+name[r]+f' & {vals[0]:+d} & {vals[1]:+d} & {v:+d} '+r'\\')
lines += [r'\hline',r'\end{tabular}',r'{\footnotesize W is W\_ONLY. These conditional differences are not an additive causal decomposition.}',r'\end{table}']
(P/'CONV_CONDITIONAL_KERNEL_TABLE.tex').write_text('\n'.join(lines)+'\n')
