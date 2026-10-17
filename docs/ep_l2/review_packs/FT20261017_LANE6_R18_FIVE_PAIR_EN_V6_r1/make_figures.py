"""Measured-data figures from the independently received complete cohort."""
import csv,json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
P=Path(__file__).resolve().parent
receipt=json.loads((P/'PAPER_CURRENT_FIVE_PAIR_INTAKE.json').read_text());assert receipt['status']=='PASS_ALL_FIVE_CURRENT_NATIVE_INTAKES'
provenance=json.loads((P/'FIGURE_PROVENANCE.json').read_text());assert hashlib.sha256((P/'PAIRED_RESULTS.csv').read_bytes()).hexdigest()==provenance['source_csv_sha256']
rows=list(csv.DictReader((P/'PAIRED_RESULTS.csv').open()));assert len(rows)==5
value=lambda key:np.array([float(r[key]) for r in rows])
plt.rcParams.update({'font.family':'STIXGeneral','font.size':8,'axes.labelsize':8,'axes.titlesize':8.5,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':7.8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.55,'xtick.major.width':.5,'ytick.major.width':.5,'savefig.pad_inches':.02})
labels=['SAD','Vector','CFD','Conv.','FWT'];gray='#6C7883';blue='#207F91';red='#B34E44';gold='#CC8B37';x=np.arange(5)
F=P/'figures';F.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(7.16,1.78));fig.subplots_adjust(left=.075,right=.99,bottom=.24,top=.8,wspace=.31)
a,b=axes;delta=value('cycle_reduction_percent');a.bar(x,delta,color=[blue if d>=0 else red for d in delta],width=.55)
a.axhline(0,color='black',lw=.6);a.set_ylim(-.32,.64);a.set_xticks(x,labels);a.set_ylabel('Cycle reduction (%)');a.set_title('(a) End-to-end change (expanded scale)',loc='left',pad=10)
for xx,d in zip(x,delta):a.text(xx,d+(.028 if d>=0 else -.025),f'{d:+.3f}',ha='center',va='bottom' if d>=0 else 'top',fontsize=7.8)
a.set_yticks([-.2,0,.2,.4,.6]);a.grid(axis='y',alpha=.18);a.set_axisbelow(True)
b.bar(x,value('copy_lines_B')/1000,width=.55,color=gray,label='B16 copies');b.scatter(x,value('copy_lines_U')/1000,color=blue,marker='D',s=18,zorder=4,label='U-WB16: all 0')
b.set_xticks(x,labels);b.set_ylabel('Completed copies (thousands)');b.set_ylim(-20,670);b.set_title('(b) Actual resident-to-WB copies',loc='left',pad=10)
for xx,y in zip(x,value('copy_lines_B')/1000):b.text(xx,y+13,f'{y:.2f}',ha='center',fontsize=7.7)
b.legend(loc='upper left',frameon=False,ncol=2,columnspacing=.7,handlelength=1);b.grid(axis='y',alpha=.18);b.set_axisbelow(True)
for ext in ['pdf','png']:fig.savefig(F/('fig2_results.'+ext),dpi=240)
plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(7.16,1.95),sharey=True);fig.subplots_adjust(left=.07,right=.99,bottom=.32,top=.78,wspace=.35)
a,b,c=axes;y=np.arange(5);height=.28
a.barh(y-height/2,value('wbuf_full_B')/1e6,height=height,color=gray,label='B16');a.barh(y+height/2,value('wbuf_full_U')/1e6,height=height,color=blue,label='U-WB16')
a.set_yticks(y,labels);a.invert_yaxis();a.set_xlim(0,1.02);a.set_xlabel('WB-full attempts (M)');a.set_title('(a) Local staging pressure',loc='left',pad=11)
for yy,n in enumerate(value('wbuf_full_B')):
 if n in (0,5):a.text(.027,yy-.10,'0' if n==0 else '5 events',va='center',fontsize=7.5)
a.text(.65,.98,'U: all 0',transform=a.transAxes,ha='center',fontsize=7.7)
logical=100*(1-value('bank_logical_ops_U')/value('bank_logical_ops_B'));grant=100*(1-value('bank_grants_U')/value('bank_grants_B'));assert np.allclose(logical,grant,rtol=0,atol=1e-12)
wait=100*(1-value('bank_wait_cycles_U')/value('bank_wait_cycles_B'))
b.barh(y-height/2,logical,height=height,color=blue,label='Ops / grants');b.barh(y+height/2,wait,height=height,color=gold,label='Op. wait sum')
b.set_xlabel('Reduction vs B16 (%)');b.set_title('(b) Bank work and waiting',loc='left',pad=11);b.set_xlim(0,26)
c.barh(y-height/2,value('c7d_l2_to_dram_full_block_B')/1e6,height=height,color=gray,label='B16');c.barh(y+height/2,value('c7d_l2_to_dram_full_block_U')/1e6,height=height,color=blue,label='U-WB16');c.set_xlim(0,1.95);c.set_xlabel('L2→DRAM full attempts (M)');c.set_title('(c) Downstream admission',loc='left',pad=11)
fig.legend(*a.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.19,0),frameon=False,ncol=2,columnspacing=.8,handlelength=1)
fig.legend(*b.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.53,0),frameon=False,ncol=2,columnspacing=.8,handlelength=1,fontsize=7.6)
for ax in axes:ax.xaxis.set_major_locator(MaxNLocator(3));ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
for ext in ['pdf','png']:fig.savefig(F/('fig3_pressure.'+ext),dpi=240)
plt.close(fig)
provenance['plot_generator']='make_figures.py';provenance['plot_generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();provenance['rendered_files']=[{'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(F.iterdir())];(P/'FIGURE_PROVENANCE.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
print('Fig2/Fig3 generated from complete independently accepted data')
