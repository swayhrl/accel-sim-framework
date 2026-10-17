#!/usr/bin/env python3
"""Standalone evidence plots; no missing endpoint is drawn as zero."""
import argparse,csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
COLORS=['#376996','#c46b37']
def load(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('derived',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(exist_ok=False);pairs=load(a.derived/'finite_pairs.csv');pressure=load(a.derived/'pressure_and_banks.csv');ideals=load(a.derived/'local_ideal_endpoints.csv')
 def save(fig,name,caption):
  fig.savefig(a.out/(name+'.pdf'),bbox_inches='tight');fig.savefig(a.out/(name+'.svg'),bbox_inches='tight');fig.savefig(a.out/(name+'.png'),dpi=180,bbox_inches='tight');(a.out/(name+'_CAPTION.txt')).write_text(caption+'\n');plt.close(fig)
 conditions=['H0','Q4','WAD256_Q4','D2','D4','L25','ROP40_H0','ICNT2_H0']
 fig,axs=plt.subplots(2,2,figsize=(10.8,5.7),gridspec_kw={'height_ratios':[2.2,1]},layout='constrained')
 for col,work in enumerate(['convolutionSeparable','FWT_7_21']):
  rows=sorted([r for r in pairs if r['workload']==work],key=lambda r:conditions.index(r['condition']));x=np.arange(len(rows));labels=[r['condition'].replace('WAD256_Q4','WAD256\n(Q4)').replace('_H0','') for r in rows]
  for i,(key,label) in enumerate([('B_cycles','B16'),('U_cycles','Unified')]):
   axs[0,col].plot(x,[float(r[key])/1000 for r in rows],marker='o',label=label,color=COLORS[i],lw=1.6)
   for n,r in enumerate(rows):axs[0,col].annotate(f'{int(r[key]):,}',(n,float(r[key])/1000),xytext=(0,10 if float(r[key])>=float(r['U_cycles' if i==0 else 'B_cycles']) else -13),textcoords='offset points',ha='center',fontsize=6.5,color=COLORS[i])
  axs[0,col].set(title='Convolution' if col==0 else 'FWT',ylabel='Absolute GPU cycles (thousands)',xticks=x,xticklabels=labels);axs[0,col].grid(axis='y',alpha=.2);axs[0,col].legend(frameon=False)
  gains=[100*(float(r['S_EP'])-1) for r in rows];axs[1,col].bar(x,gains,color=[COLORS[0] if g>=0 else COLORS[1] for g in gains],width=.6)
  axs[1,col].axhline(0,color='black',lw=.6);axs[1,col].set(xticks=x,xticklabels=labels,ylabel='100 × (B/U − 1) [%]');axs[1,col].grid(axis='y',alpha=.2)
 fig.suptitle('Finite controls: absolute throughput and within-condition EP effect',fontsize=12)
 save(fig,'fig1_finite_controls','All points use Core7b8 / binary2309 and fixed full-input identity per workload. B/U share condition resources. FWT ROP/ICNT missing at this accepted snapshot and omitted. Raw absolute cycles shown; positive lower panels favor Unified. No error bars: deterministic executions, not independent stochastic replicates. CFD negative control is retained in tables/cases, not omitted from inference.')
 selected=['H0','Q4','WAD256_Q4','D2','D4','L25'];fig,axs=plt.subplots(2,3,figsize=(11.4,6),layout='constrained')
 for ri,work in enumerate(['convolutionSeparable','FWT_7_21']):
  for ci,(field,ylabel) in enumerate([('physical_WB_role_mean','Mean sampled physical WB roles / slice'),('c7d_wad_full_events','WAD-full retry events (thousands)'),('scheduler_refusal_per_actual_issue_attempt','DRAM scheduler refusals / issue attempt')]):
   ax=axs[ri,ci];scope_conditions=[c for c in selected if any(r['workload']==work and r['condition']==c for r in pressure)]
   for mi,mode in enumerate(['B16_BANKED','U_WB16']):
    rows=[next(r for r in pressure if r['workload']==work and r['condition']==c and r['mode']==mode and r['binary'].startswith('2309')) for c in scope_conditions]
    values=[float(r[field])/(1000 if field=='c7d_wad_full_events' else 1) for r in rows];ax.bar(np.arange(len(scope_conditions))+(mi-.5)*.35,values,width=.35,color=COLORS[mi],label='B16' if mi==0 else 'Unified')
   ax.set(xticks=np.arange(len(scope_conditions)),xticklabels=[c.replace('WAD256_Q4','WAD256') for c in scope_conditions],ylabel=ylabel,title=('Convolution' if ri==0 else 'FWT')+' — '+['local data','completion control','downstream'][ci]);ax.grid(axis='y',alpha=.2)
   if ri==0 and ci==0:ax.legend(frameon=False)
 save(fig,'fig2_data_control_downstream','Each panel has its own unit; do not add panels as execution time. Sampled physical WB-role occupancy comes from payload_store.wb_used() over actual slice observations, not staged-record maxima. Q4 removes local data queue fullness while WAD and detailed-DRAM scheduler refusals remain. WAD counts are retries, not unique requests. Clock and queue changes alter schedules and request streams; endpoint counters alone do not prove a critical path.')
 fig,axs=plt.subplots(1,2,figsize=(10.5,3.9),layout='constrained');names=[];distributions=[];waits=[];totals=[]
 for condition in ['H0','Q4','D4']:
  for mode in ['B16_BANKED','U_WB16']:
   r=next(r for r in pressure if r['workload']=='convolutionSeparable' and r['condition']==condition and r['mode']==mode);v=[float(r[f'bank{b}_logical_ops']) for b in range(4)];names.append(condition+'\n'+('B16' if mode=='B16_BANKED' else 'Unified'));distributions.append(np.array(v)/sum(v)*100);waits.append([float(r[f'bank{b}_wait_cycles'])/1e6 for b in range(4)]);totals.append(sum(v)/1e6)
 bottom=np.zeros(6)
 for bank,color in enumerate(['#376996','#68a3ae','#d3ae63','#b96b68']):
  vals=[v[bank] for v in distributions];axs[0].bar(np.arange(6),vals,bottom=bottom,color=color,label=f'bank {bank}');bottom+=vals
  axs[1].bar(np.arange(6)+(bank-1.5)*.18,[v[bank] for v in waits],width=.18,color=color)
 axs[0].axhline(25,color='black',lw=.5,ls='--');axs[0].set(xticks=np.arange(6),xticklabels=names,ylabel='Share of logical payload RAM operations [%]',title='Convolution: work placement');axs[0].legend(frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.5,1.19),fontsize=8)
 axs[1].set(xticks=np.arange(6),xticklabels=names,ylabel='Bank operation wait cycles (millions)',title='Operation waits; not exclusive GPU stalls')
 for i,t in enumerate(totals):axs[0].text(i,101,f'{t:.2f}M',ha='center',fontsize=7)
 axs[0].set_ylim(0,110)
 save(fig,'fig3_bank_work_and_placement','Real per-bank application cumulative counters. Labels above stacks are total logical RAM operations, not requests or GPU cycles. The B16 bank0 concentration is consistent with first-free static WB staging plus copy traffic; Unified changes organization and placement. Fewer waits/operations do not imply proportional or positive whole-application speedup: D4 Convolution Unified is slower. No pure-copy attribution without U_CAP16.')
 fig,axs=plt.subplots(1,3,figsize=(11.5,3.5),layout='constrained')
 local=[next(r for r in ideals if r['profile']==name) for name in ['I_WB','I_META','I_READ_HIT']];names=['OFF','I_WB','I_META','I_READ_HIT'];values=[int(local[0]['anchor_cycles']),*[int(r['ideal_cycles']) for r in local]]
 axs[0].bar(np.arange(4),values,color=['#777777',COLORS[1],COLORS[0],'#68a3ae'],width=.6);axs[0].set(xticks=np.arange(4),xticklabels=names,ylabel='Absolute GPU cycles',title='vectorAdd: local, binary37dc',ylim=(0,88000))
 for i,v in enumerate(values):axs[0].text(i,v+1200,f'{v:,}',ha='center',fontsize=8)
 broad=next(r for r in ideals if r['profile']=='I_MEM_ALL_DATA');vals=[int(broad['anchor_cycles']),int(broad['ideal_cycles'])]
 axs[1].bar([0,1],vals,color=['#777777',COLORS[0]],width=.6);axs[1].set(xticks=[0,1],xticklabels=['B16 OFF','ALL_DATA'],title='vectorAdd: full data, binaryfb67',ylim=(0,88000))
 for i,v in enumerate(vals):axs[1].text(i,v+1200,f'{v:,}',ha='center',fontsize=8)
 axs[1].text(.5,82500,f'{float(broad["operational_headroom"]):.3f}× operational headroom',ha='center',fontsize=8)
 axs[2].axis('off');axs[2].text(.02,.94,'Pending, not zero-valued endpoints',weight='bold',transform=axs[2].transAxes,fontsize=9);axs[2].text(.02,.78,'Conv/FWT: S64 and U_CAP16\nConv/FWT: matched local/full Ideal\nLocal/full contrast within binaryfb67\n\nEach panel uses its own same-source OFF.\nNo cross-release decomposition.\nNo EP speedup or universal bound.',va='top',linespacing=1.7,transform=axs[2].transAxes,fontsize=8)
 save(fig,'fig4_ideal_scope_and_pending','Separate accepted same-source contrasts: local diagnostics Corea26/binary37dc B16_OFF73696, I_WB73843 (headroom0.998009), I_META73696, I_READ_HIT43020 (headroom1.713064); full-data Core9bd30/binaryfb67 B16_OFF73696, ALL_DATA17247 (headroom4.273). Matching cycle counts of the two OFF anchors do not make the binaries identical. No within-binary local/full decomposition is available yet. ALL_DATA retains native instruction issue/producer dependencies/register consumption, uses symbolic byte-address versions, and reports physical data hierarchy N/A; it is not EP-L2 speedup or a universal mathematical bound. Missing strong-static/Conv/FWT endpoints stay explicitly pending.')
 print('Four standalone PDF/SVG/PNG figures written')
if __name__=='__main__':main()
