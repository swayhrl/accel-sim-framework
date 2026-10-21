"""Reproducible figure/table projection of D's accepted offline data only."""
import csv, hashlib, json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
def load(n):return json.loads((P/n).read_text())
def read(n):return list(csv.DictReader((P/n).open()))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def csvout(n,rows):
 with (P/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
def export(fig,name):
 for ext in ['pdf','png']:fig.savefig(P/(name+'.'+ext),dpi=230,bbox_inches='tight')
 plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
main=read('MAIN_FIVE_PERFORMANCE.csv');summary=load('SUMMARY.json');idents=load('ACCEPTED_ENDPOINT_IDENTITIES.json')
main={r['workload']:r for r in main};order=['convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M'];names=['Conv','CFD','DWT','SAD','Vector']
vals=[float(main[w]['speedup_percent']) for w in order]+[summary['GM_speedup_percent']]
fig,ax=plt.subplots(figsize=(6.5,2.7));ax.bar(range(6),vals,color=['#376d87' if x>=0 else '#ae6251' for x in vals],width=.58)
ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(6),names+['GM (5)']);ax.set_ylabel('Speedup: 100 (S/F - 1), %');ax.set_ylim(-2.35,1.35)
for i,v in enumerate(vals):ax.annotate(f'{v:+.3f}%',(i,v),xytext=(0,4 if v>=0 else -4),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
ax.set_title('Five accepted MAIN pairs, same main61 binary',fontsize=10)
fig.text(.5,-.05,'Five-pair subset only; original seven-input GM UNKNOWN. Controls do not replace MAIN F.',ha='center',fontsize=8)
export(fig,'MAIN_FIVE_PERFORMANCE')
tex=['% E ca2dbc456; main61; speedup uses S/F, not cycle reduction.','\\begin{tabular}{lrrr}','\\hline','Input & S cycles & F cycles & Speedup (\\%) \\\\','\\hline']
for w,n in zip(order,names):
 r=main[w];tex.append(f"{n} & {int(r['S_cycles']):,} & {int(r['F_cycles']):,} & {float(r['speedup_percent']):+.3f} \\\\")
tex+=['\\hline',f"GM (five) & --- & --- & {summary['GM_speedup_percent']:+.3f} \\\\",'GM (seven) & --- & --- & UNKNOWN \\\\','\\hline','\\end{tabular}']
(P/'MAIN_FIVE_PERFORMANCE.tex').write_text('\n'.join(tex)+'\n')
rows=read('KERNEL_TIMING_AND_MECHANISM_DELTAS.csv')
focused=[]
for r in rows:
 if (r['workload']=='dwt2d' and (r['left_profile'],r['right_profile']) in [('S','W_ONLY'),('W_ONLY','F_MINUS_R'),('F_MINUS_R','F')]) or (r['workload']=='convolutionSeparable' and 'DATA_FREE' in r['right_profile']) or r['workload']=='vectorAdd_4M': focused.append(r)
# Elapsed stages only: three aligned panels keep wait observations out of elapsed bars.
fig,axes=plt.subplots(3,1,figsize=(7.3,7.1),layout='constrained')
ax=axes[0];vr=[r for r in focused if r['workload']=='vectorAdd_4M'];v=[int(r['right_minus_left_cycles']) for r in vr]
ax.bar(range(len(v)),v,color=['#ae6251','#376d87']);ax.set_xticks(range(len(v)),['K1 VecAdd','Final residual']);ax.axhline(0,c='#666666',lw=.7);ax.set_title('(a) Vector F - S: +1,343 = +1,371 - 28',fontsize=10)
for i,x in enumerate(v):ax.text(i,x+(20 if x>=0 else -20),f'{x:+,}',ha='center',va='bottom' if x>=0 else 'top',fontsize=8)
ax.set_ylim(-220,1670);ax.set_ylabel('GPU cycles')
ax=axes[1];colors=['#7f9fac','#d1ac70','#ae6251'];labels=['W_ONLY - S','WV - W_ONLY','F - WV'];dw=[]
for j,(l,r) in enumerate([('S','W_ONLY'),('W_ONLY','F_MINUS_R'),('F_MINUS_R','F')]):
 rr=[x for x in focused if x['workload']=='dwt2d' and x['left_profile']==l and x['right_profile']==r and x['kernel_ordinal']!='FINAL_RESIDUAL'];v=[int(x['right_minus_left_cycles']) for x in rr]
 ax.bar(np.arange(1,11)+(j-1)*.24,v,.23,label=labels[j],color=colors[j]);dw.append(dict(left=l,right=r,total=sum(v),K1=v[0],K5=v[4],K8=v[7],other=sum(v)-v[0]-v[4]-v[7]))
ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(1,11),['K'+str(i) for i in range(1,11)]);ax.set_ylabel('GPU cycles');ax.set_title('(b) DWT: conditional elapsed differences; WV = F_MINUS_R',fontsize=10);ax.legend(fontsize=8,frameon=False,ncol=3,loc='upper left');ax.set_ylim(-350,930)
ax=axes[2]
for j,base in enumerate(['S','F']):
 rr=[x for x in focused if x['workload']=='convolutionSeparable' and x['left_profile']==base and x['right_profile']==base+'_L2_DATA_FREE' and x['kernel_ordinal']!='FINAL_RESIDUAL'];v=[int(x['right_minus_left_cycles']) for x in rr]
 ax.bar(np.arange(2)+(j-.5)*.32,v,.3,color=[colors[0],colors[2]][j],label=base+'_L2_DATA_FREE - '+base)
 for i,x in enumerate(v):ax.annotate(f'{x:+,}',(i+(j-.5)*.32,x),xytext=(0,3 if x>=0 else -3),textcoords='offset points',ha='center',va='bottom' if x>=0 else 'top',fontsize=8)
ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(2),['Rows (K1)','Columns (K2)']);ax.set_ylabel('GPU cycles');ax.set_title('(c) Conv service-exemption diagnostic; finite residual resources retained',fontsize=10);ax.legend(frameon=False,fontsize=8,ncol=1,loc='upper right');ax.set_ylim(-1120,1600)
export(fig,'PRIMARY_FOUR_ELAPSED_STAGES');csvout('DWT_CONDITIONAL_STAGE_TOTALS.csv',dw)
# Mechanism overview: counts are factual, separate units; no invented critical-path shares.
metrics=read('ACCEPTED_PAIR_TERMINAL_MECHANISMS.csv');vm=[r for r in metrics if r['pair_id']=='V2_MAIN_vectorAdd_4M_S_F_MAIN61_RESOURCE_RETRY'];vmap={(r['family'],r['metric']):r for r in vm}
fig,axes=plt.subplots(1,2,figsize=(7.4,2.8),layout='constrained')
keys=[('local_service','physical_bank_grants'),('local_service','lower_reads'),('local_service','lower_wb_bytes')];labs=['Bank grants','Lower reads','Lower WB bytes'];changes=[]
for k in keys:
 r=vmap[k];changes.append(100*(float(r['right'])/float(r['left'])-1))
ax=axes[0];ax.bar(range(3),changes,color=['#376d87','#999999','#ae6251']);ax.axhline(0,c='#666666',lw=.7);ax.set_xticks(range(3),labs,fontsize=8);ax.set_ylabel('Vector F / S - 1 (%)');ax.set_title('(a) Fewer services, unchanged reads',fontsize=10);ax.set_ylim(-9,2)
for i,v in enumerate(changes):ax.text(i,v+(.18 if v>=0 else -.18),f'{v:+.3f}%',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
ax=axes[1];families=[('victim','directory_queries'),('victim','read_responses'),('readonly_summary','accepted_ro'),('readonly_summary','transactions'),('readonly_summary','merges'),('readonly_summary','detached')];counts=[int(vmap[k]['right']) for k in families]
ax.barh(range(6),np.array(counts)/1e6,color=['#7f9fac','#ae6251','#376d87','#7f9fac','#7f9fac','#ae6251']);ax.set_yticks(range(6),['V queries','V reads','RO admissions','RO transactions','RO merges','Tag detach'],fontsize=8);ax.invert_yaxis();ax.set_xlim(0,1.25);ax.set_xlabel('Million events in accepted F');ax.set_title('(b) Active queries; zero V reads / detach',fontsize=10)
for i,v in enumerate(counts):ax.text(v/1e6+.025,i,f'{v:,}',va='center',fontsize=8)
export(fig,'VECTOR_MECHANISM_COUNTS')
# Full final scalar evidence including actual lower-WB accept events, not just staging.
extra=[]
for aid in ['E013_33cffb17','E033_f01f6993']:
 i=next(x for x in idents if x['attempt_id']==aid);path=Path(i['receipt_path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==i['receipt_sha256'];r=json.loads(path.read_text());s=r['summary']
 extra.append(dict(profile=i['profile'],attempt_id=aid,wb_created=s['wb_created'],wb_lower_accepted=s['wb_lower_accepted'],wb_completed=s['wb_completed'],payload_free=s['payload_free'],payload_capacity=s['payload_capacity'],payload_roles=s['payload_roles'],unique_requesters=s['unique_requesters'],responses=s['responses'],scope='E-accepted final counters, not an independent native requalification'))
save('VECTOR_TERMINAL_PAYLOAD_WB.json',extra)
# Exact frozen accepted-declaration consistency, without rerunning any E gate.
f=load('E_FINAL_RECEIPT.json');allpairs={**f['accepted_main_pairs'],**f['accepted_controls']}
for delivery in load('E_D_DELIVERY_INDEX.json')['deliveries']:
 pid=delivery['receipt']['accepted_pair_id'];a=load('E_'+pid+'_CURRENT_ACCEPTED.json');c={**a['accepted_main_pairs'],**a['accepted_controls']}
 assert c[pid]==allpairs[pid]
 assert load('E_'+pid+'_ACCEPTED_PAIR.json')['accepted_pair']==allpairs[pid]
 dp=P/('E_'+pid+'_D_DELIVERY_RECEIPT.json');assert hashlib.sha256(dp.read_bytes()).hexdigest()==delivery['delivery']['sha256']
assert math.isclose(summary['GM_S_over_F'],math.prod(float(main[w]['speedup_S_over_F']) for w in order)**.2,rel_tol=1e-14)
assert int(main['vectorAdd_4M']['F_minus_S_cycles'])==1343
assert [r['total'] for r in dw]==[273,-74,925]
assert dw[-1]==dict(left='F_MINUS_R',right='F',total=925,K1=-91,K5=694,K8=384,other=-62)
# Every elapsed contrast and each accepted endpoint closes, including residuals.
groups={}
for r in rows:groups.setdefault((r['workload'],r['left_profile'],r['right_profile']),[]).append(r)
point={(i['workload'],i['profile']):i for i in idents}
for (w,l,r),rr in groups.items(): assert sum(int(x['right_minus_left_cycles']) for x in rr)==point[w,r]['cycles']-point[w,l]['cycles']
checks=load('DATA_VALIDATION.json');checks.update(four_delivery_checkpoints_exactly_equal_final_declarations=True,four_delivery_receipt_hashes_equal_E_index=True,GM_log_and_product_methods_agree=True,DWT_chain_cycles=[166519,166792,166718,167643],DWT_WV_to_F=[-91,694,384,-62],Vector_kernel_plus_residual=[1371,-28],Conv_S_diag_Rows_Columns=[985,-386],Conv_F_diag_Rows_Columns=[-786,637],five_F_successful_Tag_detach=[int(next(r['right'] for r in metrics if r['pair_id']==p['pair_id'] and r['family']=='readonly_summary' and r['metric']=='detached')) for p in main.values()],all_ten_contrast_elapsed_closures=len(groups)==10,raw_active_or_trace_reads=0)
save('DATA_VALIDATION.json',checks)
print(json.dumps(dict(GM=summary['GM_S_over_F'],checks=checks,figures=3),indent=2))
