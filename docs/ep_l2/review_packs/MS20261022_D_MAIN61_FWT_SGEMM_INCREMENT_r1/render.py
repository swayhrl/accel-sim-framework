"""Render frozen E-receipt projections; run from D worktree root."""
import pathlib,csv,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=pathlib.Path('docs/ep_l2/review_packs/MS20261022_D_MAIN61_FWT_SGEMM_INCREMENT_r1')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
main=list(csv.DictReader((P/'MAIN61_SIX_ACCEPTED_PERFORMANCE.csv').open()));new=list(csv.DictReader((P/'NEW_PAIR_PERFORMANCE.csv').open()));metrics=list(csv.DictReader((P/'NEW_PAIR_TERMINAL_MECHANISMS.csv').open()));summary=json.loads((P/'SUMMARY.json').read_text())
by={r['workload']:r for r in main};newby={r['workload']:r for r in new}
def save(fig,name):
 for ext in ['pdf','png']:fig.savefig(P/(name+'.'+ext),dpi=220)
 plt.close(fig)
def bars(ax,labels,values):
 ax.bar(range(len(labels)),values,color=['#376d87' if x>=0 else '#ae6251' for x in values],width=.64);ax.axhline(0,color='.4',lw=.7);ax.set_xticks(range(len(labels)),labels);ax.set_ylim(-2.35,1.45)
 for i,v in enumerate(values):ax.annotate(f'{v:+.3f}',(i,v),xytext=(0,3 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=7)
fig,axes=plt.subplots(1,2,figsize=(7.05,2.55),gridspec_kw={'width_ratios':[5.5,1.5]});fig.subplots_adjust(left=.085,right=.98,bottom=.24,top=.75,wspace=.30)
order=['convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M','FWT_7_21'];vals=[float(by[w]['speedup_percent']) for w in order]+[summary['six_subset_speedup_percent']]
bars(axes[0],['Conv','CFD','DWT','SAD','Vector','FWT','GM6'],vals);axes[0].set_ylabel('Speedup 100(S/F − 1), %');axes[0].set_title('Original MAIN: accepted subset 6/7',fontsize=9);axes[0].patches[-1].set_hatch('//');axes[0].patches[-1].set_facecolor('#777f87')
bars(axes[1],['SGEMM'],[float(newby['sgemm']['speedup_percent'])]);axes[1].set_title('Independent exploration',fontsize=8)
fig.suptitle('Same main61 binary; all adverse MAIN results retained',fontsize=11,y=.97);fig.text(.5,.035,'Original-seven MAIN GM: UNKNOWN (Btree HOLD). No mixed-cohort or capacity-diagnostic GM.',ha='center',fontsize=8);save(fig,'MAIN61_PERFORMANCE_BY_COHORT')

def val(w,family,metric,profile):
 row=next(r for r in metrics if r['workload']==w and r['family']==family and r['metric']==metric);return float(row[profile])
fig,axes=plt.subplots(2,3,figsize=(7.05,4.2));fig.subplots_adjust(left=.09,right=.98,bottom=.18,top=.84,hspace=.55,wspace=.45)
for i,(w,label) in enumerate([('FWT_7_21','FWT'),('sgemm','SGEMM')]):
 for j,ax in enumerate(axes[i]):
  ax.set_xticks([0,1],['S','F'])
  if j==0:
   v=[val(w,'local_service','physical_bank_grants',p)/1e6 for p in ['S','F']];ax.bar([0,1],v,color=['#8ba6b3','#b28163'],width=.6);ax.set_ylabel(label+' bank grants (M)');ax.set_title(f'{100*(v[1]/v[0]-1):+.3f}% physical grants',fontsize=8)
  elif j==1:
   reads=np.array([val(w,'local_service','lower_read_bytes',p)/1e6 for p in ['S','F']]);wb=np.array([val(w,'local_service','lower_wb_bytes',p)/1e6 for p in ['S','F']]);ax.bar([0,1],reads,color='#8ba6b3',width=.6,label='read');ax.bar([0,1],wb,bottom=reads,color='#b28163',width=.6,label='WB');ax.set_ylabel('Lower bytes (MB)');ax.set_title('Read / WB traffic',fontsize=8);ax.set_ylim(0,max(reads+wb)*1.35)
   if i==0:ax.legend(fontsize=6,frameon=False,loc='upper center',ncol=2)
  else:
   v=[val(w,'trigger','logical_copy_reads',p)/1000 for p in ['S','F']];ax.bar([0,1],v,color=['#8ba6b3','#b28163'],width=.6);ax.set_ylabel('Copies per direction (k)');ax.set_title('Reads = writes; no sum',fontsize=8)
   for x,y in enumerate(v):ax.annotate(f'{y:g}',(x,y),xytext=(0,3),textcoords='offset points',ha='center',fontsize=7)
   if max(v)==0:ax.set_ylim(0,1);ax.text(.5,.45,'Both measured zero',ha='center',fontsize=7)
  ax.margins(y=.20)
fig.suptitle('Two new accepted pairs: service and traffic observations',fontsize=11,y=.98)
fig.text(.5,.055,'F victim reads: FWT 184,660; SGEMM 35,936. F RO admission / Tag detach: 0 / 0 in both.\nEmpty certification leaves actual RO opportunity UNKNOWN; counters do not identify causal cycle shares.',ha='center',fontsize=7.5);save(fig,'FWT_SGEMM_MECHANISM_PROFILE')
fig,axes=plt.subplots(1,2,figsize=(7.05,3.0),gridspec_kw={'width_ratios':[2.1,1]});fig.subplots_adjust(left=.09,right=.98,bottom=.35,top=.80,wspace=.35)
labels={'ANY_FIRST_BLOCK_TO_ADMISSION':'any first wait','COPY_PIPELINE':'copy','DATA_SERVICE':'data','MISS_QUEUE_FULL':'MissQ','WB_DATA_SPACE':'WB space','BANK_COMPATIBLE_LANDING':'landing','VICTIM_LOOKUP':'V query','SAME_ADDRESS_WB':'same WB'}
for ax,w,rs in [(axes[0],'FWT_7_21',list(labels)),(axes[1],'sgemm',['ANY_FIRST_BLOCK_TO_ADMISSION','DATA_SERVICE','VICTIM_LOOKUP'])]:
 x=np.arange(len(rs));
 for offset,p,color in [(-.17,'S','#8ba6b3'),(.17,'F','#b28163')]:ax.bar(x+offset,[val(w,'wait_'+r,'request_wait_cycle_sum',p)/1000 for r in rs],width=.34,label=p,color=color)
 ax.set_xticks(x,[labels[r] for r in rs],rotation=45,ha='right',fontsize=7);ax.set_title('FWT' if w=='FWT_7_21' else 'SGEMM',fontsize=9);ax.legend(frameon=False,fontsize=7);ax.set_ylabel('Request-cycle sum (k)')
fig.suptitle('Nonexclusive wait observations, not program stalls',fontsize=11,y=.96);fig.text(.5,.025,'Any / reason / request / slice observations overlap. No stacking or summation into GPU cycles.',ha='center',fontsize=8);save(fig,'FWT_SGEMM_WAIT_OBSERVATIONS')
