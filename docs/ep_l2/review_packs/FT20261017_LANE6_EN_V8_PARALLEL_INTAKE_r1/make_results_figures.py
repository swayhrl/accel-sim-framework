"""Derived plots from complete native receipts; no simulation or science-ledger writes."""
from pathlib import Path
import csv,json,math,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent;A=P/'analysis/current1';F=P/'figures';F.mkdir(exist_ok=True)
rows=list(csv.DictReader((A/'CONDITION_CYCLES.csv').open()));R={(r['workload'],r['regime'],r['mode']):r for r in rows};order=['sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21'];short=['SAD','Vector','CFD','Conv.','FWT'];colors={'H0':'#6c7985','Q4':'#c17b24','D4':'#187d8d'};markers={'H0':'o','Q4':'s','D4':'^'}
plt.rcParams.update({'font.family':'serif','font.size':9,'axes.labelsize':9,'axes.titlesize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
metrics=[]
for w in order:
 b0=int(R[w,'H0','B16_BANKED']['cycles']);u0=int(R[w,'H0','U_WB16']['cycles'])
 for h in ['H0','Q4','D4']:
  if (w,h,'B16_BANKED') not in R:continue
  b=int(R[w,h,'B16_BANKED']['cycles']);u=int(R[w,h,'U_WB16']['cycles']);s=b/u
  metrics.append({'workload':w,'condition':h,'cycles_B':b,'cycles_U':u,'S_B_over_U':s,'J_over_same_workload_H0':s/(b0/u0),'B_speed_ratio_over_same_mode_H0':b0/b,'U_speed_ratio_over_same_mode_H0':u0/u,'B_cycle_change_percent_vs_H0':100*(b-b0)/b0,'U_cycle_change_percent_vs_H0':100*(u-u0)/u0,'cohort':'H0_PRIMARY_FIVE' if h=='H0' else ('R19_D4_EXTENSION' if w in ('sad','vectorAdd_4M') else 'R19_'+h+'_PRIMARY_TWO')})
with (P/'PAIRED_EFFECTS.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(metrics[0]),lineterminator='\n');w.writeheader();w.writerows(metrics)
lookup={(r['workload'],r['condition']):r for r in metrics}
def absolute(axes):
 for i,(w,ax) in enumerate(zip(order,axes)):
  for j,h in enumerate(['H0','Q4','D4']):
   if (w,h) not in lookup:
    ax.text(j,.04,'n/a',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,color='#777777');continue
   r=lookup[w,h];ax.bar(j-.16,r['cycles_B']/1000,width=.30,color=colors[h],edgecolor=colors[h]);ax.bar(j+.16,r['cycles_U']/1000,width=.30,facecolor='white',edgecolor=colors[h],hatch='///',linewidth=.8)
  ax.set_xticks(range(3),['H0','Q4','D4']);ax.set_title(short[i]);ax.set_ylim(bottom=0);ax.set_xlim(-.6,2.6);ax.grid(axis='y',alpha=.20);ax.set_axisbelow(True)
 axes[0].set_ylabel('GPU cycles (thousands)')
def effects(axes,copy=True):
 for j,(kind,label) in enumerate([('S_B_over_U','(b) Same-condition $S=C_B/C_U$'),('J_over_same_workload_H0','(c) Interaction $J=S/S(H0)$')]):
  ax=axes[j]
  for k,h in enumerate(['H0','Q4','D4']):
   if j==1 and h=='H0':continue
   xs=[];ys=[]
   for i,w in enumerate(order):
    if (w,h) in lookup:xs.append(i+(k-1)*.15);ys.append(lookup[w,h][kind])
   ax.plot(xs,ys,linestyle='none',marker=markers[h],color=colors[h],label=h,markersize=4.5)
  ax.axhline(1,color='#777777',linewidth=.8);ax.set_xticks(range(5),['SAD','Vec.','CFD','Conv.','FWT']);ax.set_xlim(-.5,4.5);ax.set_title(label);ax.set_ylim(.981,1.008);ax.set_yticks([.985,.995,1.000,1.005]);ax.grid(axis='y',alpha=.2);ax.legend(loc='lower left',ncol=3,handletextpad=.2,columnspacing=.55,frameon=False)
 if copy:
  ax=axes[2];h0=list(csv.DictReader((P.parent/'FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1/PAIRED_RESULTS.csv').open()));c={r['workload']:int(r['copy_lines_B']) for r in h0};xx=np.arange(5);vals=[c[w]/1000 for w in order];ax.bar(xx,vals,width=.58,color=colors['H0'],label='B16');ax.scatter(xx,[0]*5,marker='D',color=colors['D4'],s=15,label='U-WB: all 0',zorder=3)
  for x,y in zip(xx,vals):ax.text(x,y+11,f'{y:.1f}',ha='center',fontsize=8)
  ax.set_xticks(xx,['SAD','Vec.','CFD','Conv.','FWT']);ax.set_ylim(0,650);ax.set_title('(d) H0 copies (thousands)');ax.grid(axis='y',alpha=.2);ax.legend(loc='upper left',frameon=False,ncol=1)
fig=plt.figure(figsize=(7.25,3.45));gs=fig.add_gridspec(2,15,height_ratios=[1,1.18],hspace=.74,wspace=2.5);aa=[fig.add_subplot(gs[0,i*3:(i+1)*3]) for i in range(5)];absolute(aa);bb=[fig.add_subplot(gs[1,i*5:(i+1)*5]) for i in range(3)];effects(bb)
fig.text(.5,.995,'(a) Absolute cycles: solid B16, hatched U-WB; absent conditions marked n/a',ha='center',va='top',fontsize=9);fig.subplots_adjust(left=.072,right=.99,top=.88,bottom=.085);fig.savefig(F/'fig2_all_conditions.pdf');fig.savefig(F/'fig2_all_conditions.png',dpi=220);plt.close(fig)
fig,aa=plt.subplots(1,5,figsize=(7.25,1.8));absolute(aa);fig.suptitle('Absolute application cycles: solid B16, hatched U-WB',fontsize=10);fig.tight_layout(pad=.5);fig.savefig(F/'absolute_cycles.pdf');fig.savefig(F/'absolute_cycles.png',dpi=220);plt.close(fig)
fig,aa=plt.subplots(1,2,figsize=(7.25,1.9));effects(aa,copy=False);fig.tight_layout(pad=.5);fig.savefig(F/'same_condition_effects.pdf');fig.savefig(F/'same_condition_effects.png',dpi=220);plt.close(fig)
cohorts={}
for name,h,members in [('H0_PRIMARY_FIVE','H0',order),('R19_D4_PRIMARY_TWO','D4',['convolutionSeparable','FWT_7_21']),('R19_Q4_PRIMARY_TWO','Q4',['convolutionSeparable','FWT_7_21']),('R19_D4_EXTENSION','D4',['vectorAdd_4M','sad'])]:
 selected=[lookup[w,h] for w in members if (w,h) in lookup];cohorts[name]={'condition':h,'members':members,'complete':len(selected)==len(members),'received_pairs':len(selected),'geomean_S':math.exp(math.fsum(math.log(r['S_B_over_U']) for r in selected)/len(members)) if len(selected)==len(members) else None,'geomean_J':math.exp(math.fsum(math.log(r['J_over_same_workload_H0']) for r in selected)/len(members)) if len(selected)==len(members) else None}
assert abs(cohorts['H0_PRIMARY_FIVE']['geomean_S']-1.0016002037656606)<1e-14
(P/'FIXED_COHORTS.json').write_text(json.dumps(cohorts,indent=2)+'\n')
(P/'FIGURE_PROVENANCE.json').write_text(json.dumps({'input_cycles_sha256':hashlib.sha256((A/'CONDITION_CYCLES.csv').read_bytes()).hexdigest(),'input_native_index_sha256':hashlib.sha256((P/'RECEIVED_NATIVE_PAIRS.json').read_bytes()).hexdigest(),'input_H0_copy_csv':'../FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1/PAIRED_RESULTS.csv','absolute_cycle_scope':'Native complete-application GPU cumulative; no summation over slices or clock-domain renormalization','same_condition_effects':'S=C_B(h)/C_U(h); J=S/S(H0), matching source/binary/full input','same_mode_H0_columns':'Both B and U absolute changes/speed ratios in PAIRED_EFFECTS.csv','group_definitions':'FIXED_COHORTS.json; no pooled 11-pair mean','single_deterministic_runs_no_error_bars':True,'missing_conditions':'omitted or n/a, never zero-filled','pressure_figure':'Unchanged EN-v7 H0 fig3_pressure.pdf; counters/grants/wait/event definitions unchanged'},indent=2)+'\n');print(json.dumps(cohorts))
