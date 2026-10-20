"""Render frozen accepted-endpoint tables; never accepts/runs an application."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
rows={r['profile']:r for r in csv.DictReader((P/'CONV_SIX_CONDITION_PERFORMANCE.csv').open())}
profiles=['S','W_ONLY','S_COPY_FREE','F_MINUS_V','F_MINUS_R','F']
labels=['S','W only','S copy-free','F minus V','F minus R','F']
fig,axes=plt.subplots(1,2,figsize=(10.2,4.1));fig.subplots_adjust(left=.08,right=.985,top=.83,bottom=.27,wspace=.3)
ax=axes[0];vals=[int(rows[p]['cycles'])-int(rows['S']['cycles']) for p in profiles]
ax.bar(range(len(vals)),vals,color=['#969c9f','#537c92','#b27060','#b27060','#537c92','#365e75'],width=.6)
ax.set_xticks(range(len(vals)),labels,rotation=30,ha='right',fontsize=8)
for n,v in enumerate(vals):ax.annotate(f'{v:+,}',(n,v),xytext=(0,3 if v>=0 else -3),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
ax.set_ylim(-1900,1300);ax.set_ylabel('Elapsed GPU cycle change');ax.set_title('(a) Program cycles relative to S',fontsize=11)
ax=axes[1];pairs=[('S','W_ONLY'),('S','S_COPY_FREE'),('W_ONLY','F'),('F_MINUS_V','F'),('F_MINUS_R','F')]
for j,(stage,color) in enumerate([('Rows','#b27060'),('Columns','#537c92')]):
 v=[int(rows[r][stage+'_cycles'])-int(rows[l][stage+'_cycles']) for l,r in pairs];x=[n+(j-.5)*.35 for n in range(len(pairs))]
 ax.bar(x,v,.34,label=stage,color=color)
 for xi,yi in zip(x,v):ax.annotate(f'{yi:+,}',(xi,yi),xytext=(0,3 if yi>=0 else -3),textcoords='offset points',ha='center',va='bottom' if yi>=0 else 'top',fontsize=7)
ax.set_xticks(range(len(pairs)),['S → W','S → CF','W → F','F−V → F','F−R → F'],rotation=25,ha='right',fontsize=8)
ax.set_ylim(-2200,2500);ax.set_title('(b) Right-minus-left named kernel cycles',fontsize=11);ax.legend(frameon=False,fontsize=8,loc='upper right')
for ax in axes:ax.axhline(0,color='#777777',lw=.7);ax.spines[['top','right']].set_visible(False)
fig.suptitle('Conv: adverse diagnostics and conditional effects are retained',fontsize=12)
fig.text(.5,.035,'CF = S_COPY_FREE (diagnostic); W = W_ONLY. Each pair closes exactly with zero final residual.\n96.17% is recovery of net program-cycle improvement, not a copy-attribution fraction.\nRemove-one differences are conditional; the original main-F results and seven-input denominator remain unchanged.',ha='center',fontsize=8.5)
for ext in ['pdf','png']:fig.savefig(P/('CONV_SIX_CONDITION_EFFECTS.'+ext),dpi=220)
plt.close(fig)
lines=[r'% Standalone EN-v20 insertion candidate; manuscript unchanged.',r'\begin{table}[t]',r'\centering',r'\caption{Conv same-input accepted endpoints (GPU cycles). CF is the traditional copy-free diagnostic, not a hardware scheme.}',r'\label{tab:conv-six-conditions}',r'\begin{tabular}{lrrr}',r'\hline',r'Condition & Rows & Columns & Total \\',r'\hline']
names={'S':'S','W_ONLY':'W only','S_COPY_FREE':'S (CF)','F_MINUS_V':r'F$-$V','F_MINUS_R':r'F$-$R','F':'F'}
for p in profiles:
 r=rows[p];lines.append(names[p]+f" & {r['Rows_cycles']} & {r['Columns_cycles']} & {r['cycles']} "+r'\\')
lines += [r'\hline',r'\end{tabular}',r'{\footnotesize All residuals are zero. CF exempts copy service and the fixed copy-staging delay, retaining finite static WB organization.}',r'\end{table}']
(P/'CONV_SIX_CONDITION_TABLE.tex').write_text('\n'.join(lines)+'\n')
