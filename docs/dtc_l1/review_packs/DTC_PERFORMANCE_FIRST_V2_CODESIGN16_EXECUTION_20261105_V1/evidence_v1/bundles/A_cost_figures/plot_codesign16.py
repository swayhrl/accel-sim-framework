"""Report-only fixed8 x2 Physical/PIB figures from immutable qualified B Forward2.
No model, daemon, native/registry/controller, trace or manuscript action.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,os,sys
sys.dont_write_bytecode=True
P=Path
B_ROOT=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/B_results_v1/forward_v2')
B_MANIFEST_SHA='7e9c5173008d6eef7607345f88892a3da51d48f9a801f0694f804f80d190161a'
FIXED_INPUTS=[('2DCONV', 'd984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0'), ('GEMM', 'fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318'), ('convolutionSeparable', '4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449'), ('scan', '6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'), ('ATAX', 'eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950'), ('MVT', 'f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079'), ('BICG', 'ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef'), ('vectorAdd', 'e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799')]
VARIANTS=['PHYS768_OOPIB192_TAG64x8','PHYS1024_OOPIB192_TAG64x8']
LABELS=['Physical 768 + OO PIB 192','Physical 1024 + OO PIB 192']
METRICS=['S_combo','R_combo','J']
STATES={'ACCEPTED_STRICT_ARCHIVE_RESTORE':'ACCEPTED','ARCHIVED_NEGATIVE_NO_PERFORMANCE':'NEGATIVE','UNUSED_SAFETY_HOLD':'UNUSED_HOLD','AWAIT_CLOSED_RESULT':'PENDING','AWAIT_ACTUAL_REGISTRY_GRANT':'PENDING','ACTUAL_REGISTERED_SOURCE_QUALIFIED':'PENDING','VERIFICATION_HOLD':'VERIFY_HOLD','RUNTIME_SOURCE_VERIFICATION_HOLD':'VERIFY_HOLD'}
def require(v,msg):
 if not v:raise ValueError(msg)
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(P(p).read_bytes())
def read(p):return json.loads(P(p).read_bytes())
def checked(ref):
 b=P(ref['path']).read_bytes();require(sha_bytes(b)==ref['sha256'],'SOURCE_SHA_DRIFT '+ref['path'])
 if 'bytes'in ref:require(len(b)==ref['bytes'],'SOURCE_SIZE_DRIFT')
 return b
def gm(xs):return math.exp(sum(math.log(x)for x in xs)/len(xs))if xs else None
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
def compare(a,b):return 'positive'if a>b else'negative'if a<b else'exact_zero'
def load_provider(path,expected_sha):
 p=P(path).resolve();require(p.is_relative_to((B_ROOT/'snapshots').resolve())and p.name=='PUBLICATION_PROVIDER.json','FIXED_FORWARD2_IMMUTABLE_SNAPSHOT_PROVIDER_ONLY')
 b=p.read_bytes();digest=sha_bytes(b);require(digest==expected_sha,'PROVIDER_SHA_MISMATCH');v=json.loads(b)
 require(v['schema']=='DTC_PERFV2_CODESIGN16_PUBLICATION_PROVIDER_V2'and v['report_only']is True and v['new_models']==v['native_writes']==0,'REPORT_PROVIDER_SCHEMA')
 require(v['runtime_source_qualified']is True,'NO_ACTUAL_SOURCE_QUALIFIED_RUNTIME_YET')
 require(sha(B_ROOT/'MANIFEST.json')==B_MANIFEST_SHA,'FIXED_CONSUMER_MANIFEST_DRIFT');bm=read(B_ROOT/'MANIFEST.json');source_index={x['name']:x['sha256']for x in bm['files']}
 manifest=json.loads(checked(v['manifest']));require(manifest['schema']=='DTC_PERFV2_CODESIGN16_SNAPSHOT_MANIFEST_V2'and manifest['files']==v['files'],'PROVIDER_MEMBER_IDENTITY')
 payload={x['name']:checked(x)for x in v['files']};snapshot=json.loads(payload['SNAPSHOT.json']);summary=json.loads(payload['SUMMARY.json'])
 require(snapshot['schema']=='DTC_PERFV2_CODESIGN16_READONLY_SNAPSHOT_V2'and snapshot['authority_commit']=='320b1365902a72502fa61ba114cb4a4a28b934bb','FROZEN_CONTRACT_IDENTITY')
 require(snapshot['summary']==summary==v['summary'],'SUMMARY_IDENTITY');require(snapshot['runtime_context']['source_qualified']is True,'SNAPSHOT_RUNTIME_UNQUALIFIED')
 for ref in snapshot['consumer_sources']:
  require(P(ref['path']).parent.resolve()==B_ROOT.resolve()and source_index[P(ref['path']).name]==ref['sha256'],'CONSUMER_SOURCE_NOT_IN_FROZEN_MANIFEST');checked(ref)
 require(sha(p)==digest,'PROVIDER_CHANGED_DURING_READ')
 return v,b,digest,snapshot,summary

def metric_stats(cells,metric):
 valid=[c for c in cells if c[metric]is not None]
 return dict(n=len(valid),GM=gm([c[metric]for c in valid]),positive_exact=sum(c[metric+'_direction']=='positive'for c in valid),negative_exact=sum(c[metric+'_direction']=='negative'for c in valid),zero_exact_arithmetic=sum(c[metric+'_direction']=='exact_zero'for c in valid),missing=len(cells)-len(valid))
def check_stats(actual,published,label):
 for k in ['n','positive_exact','negative_exact','zero_exact_arithmetic','missing']:require(actual[k]==published[k],'STATS_'+k+' '+label)
 require((actual['GM']is None and published['GM']is None)or(actual['GM']is not None and published['GM']is not None and close(actual['GM'],published['GM'])),'GM_MISMATCH '+label)

def build_data(snapshot,summary,provenance,synthetic=False):
 rows=snapshot['rows'];require(len(rows)==16 and summary['fixed_program_inputs']==8 and summary['uniform_profiles']==2 and summary['CORE32_population']is False,'EXACT8_X2_SCOPE')
 require(set((r['program'],r['input_digest'])for r in rows)==set(FIXED_INPUTS),'FIXED_FULL_INPUT_DIGESTS');index={};cells=[];baseline_cycles={}
 for row in rows:
  require(row['variant']in VARIANTS and row['status']in STATES,'UNKNOWN_PROFILE_OR_STATUS');key=(row['program'],row['variant']);require(key not in index,'DUPLICATE_CELL');require(row['design']=='DH'and row['downstream_profile']=='P0','CELL_OR_DOWNSTREAM')
  dh,ch=row['baseline_DH_cycles'],row['baseline_CH_cycles'];require(type(dh)is int and dh>0 and type(ch)is int and ch>0,'BASELINE_CYCLE_IDENTITY')
  require(row['program']not in baseline_cycles or baseline_cycles[row['program']]==(dh,ch),'PROFILE_BASELINES_MUST_MATCH_SAME_INPUT');baseline_cycles[row['program']]=(dh,ch)
  c=dict(program=row['program'],suite=row['suite'],input_digest=row['input_digest'],variant=row['variant'],cohort=row['cohort'],uuid=row.get('uuid'),status=row['status'],display_state=STATES[row['status']],accepted=row['accepted'],cycles=row['cycles'],DH_P0_cycles=dh,CH_P0_cycles=ch,S_combo=None,R_combo=None,J=None,S_combo_direction=None,R_combo_direction=None,J_direction=None,J_status=row['J_status'],sources={k:copy.deepcopy(v)for k,v in row.items()if k in ['baseline_DH_P0','baseline_DH_bottom','baseline_CH_P0','baseline_CH_bottom','V1_physical','V1_PIB','source_RESULT','actual_bottom_RESULT','native_EXIT','archive_witness','unused_safety_hold_verification']},reason=row.get('error',row.get('reason')))
  if c['display_state']=='ACCEPTED':
   n=row['cycles'];require(row['accepted']is True and type(n)is int and n>0,'ACCEPTED_POSITIVE_INTEGER_CYCLES');sd,rc=dh/n,ch/n
   require(close(sd,row['S_combo'])and close(rc,row['R_combo'])and close(sd,row['I']),'S_R_I_ARITHMETIC');c.update(S_combo=sd,R_combo=rc,S_combo_direction=compare(dh,n),R_combo_direction=compare(ch,n))
   phy,pib=row['V1_physical'],row['V1_PIB'];require(phy['input_digest']==pib['input_digest']==row['input_digest'],'SINGLE_FACTOR_INPUT_IDENTITY')
   require(phy['variant']==('PHYS768_TAG64x8'if row['variant']==VARIANTS[0]else'PHYS1024_TAG64x8')and pib['variant']=='OO_PIB192','SINGLE_FACTOR_PROFILE_IDENTITY')
   if phy['accepted']and pib['accepted']:
    p,q=phy['cycles'],pib['cycles'];require(type(p)is int and p>0 and type(q)is int and q>0,'ACCEPTED_SINGLE_FACTOR_CYCLES');j=p*q/(dh*n);require(row['J']is not None and close(j,row['J'])and row['J_status']=='ACTUAL_SAME_INPUT_CLOSED_TERMS','J_ARITHMETIC');c.update(J=j,J_direction=compare(p*q,dh*n))
   else:require(row['J']is None,'J_REQUIRES_BOTH_ACTUAL_SINGLE_FACTORS')
  else:
   require(row['accepted']is False and row['cycles']is None and all(row.get(k)is None for k in ['S_combo','R_combo','I','J']),'UNACCEPTED_CANNOT_HAVE_PERFORMANCE')
  if c['display_state']=='UNUSED_HOLD':require(row.get('uuid')is None,'UNUSED_HOLD_NULL_UUID')
  index[key]=c;cells.append(c)
 require(all((n,v)in index for n,d in FIXED_INPUTS for v in VARIANTS),'COMPLETE_PLANNED_GRID')
 own={};common_stats={};sets={}
 for v in VARIANTS:
  cc=[index[n,v]for n,d in FIXED_INPUTS];own[v]={k:metric_stats(cc,k)for k in METRICS}
  for k in METRICS:check_stats(own[v][k],summary['profiles'][v]['available_set'][k],v+' '+k+' own-set')
 for metric in METRICS:
  ids=[d for n,d in FIXED_INPUTS if all(index[n,v][metric]is not None for v in VARIANTS)];label='common_J_complete_terms_inputs'if metric=='J'else'common_combo_accepted_inputs';published=summary[label];require(published['n']==len(ids)and set(published['ids'])==set(ids),'COMMON_INTERSECTION '+metric);sets[metric]=dict(n=len(ids),input_digests=ids);common_stats[metric]={}
  for v in VARIANTS:
   selected=[index[n,v]for n,d in FIXED_INPUTS if d in ids];stats=metric_stats(selected,metric);check_stats(stats,published['profiles'][v][metric],v+' '+metric+' common-set');common_stats[metric][v]=stats
 return dict(schema='DTC_PERFV2_CODESIGN16_FIGURE_DATA_V1',synthetic_layout_only=synthetic,scope='FIXED8_INPUTS_TWO_UNIFORM_COMBOS_NOT_CORE32',provenance=provenance,input_order=[dict(program=n,input_digest=d)for n,d in FIXED_INPUTS],variant_order=VARIANTS,cells=cells,own_available_set=own,common_metric_sets=sets,common_metric_stats=common_stats,accepted_counts={v:sum(index[n,v]['accepted']for n,d in FIXED_INPUTS)for v in VARIANTS},no_imputation=True,no_per_program_best=True,exact_zero_uses_integer_arithmetic=True,Tag_A2_excluded=True,hardware_boundary='128B-address/dependency-line accounting only, not functional payload or SRAM/PPA; physical +20/+60%; active PIB and lower-create each +50%; Tag512, allocation4 and finite widths fixed; CH0/DH are not equal-area designs.')

def configure_runtime(output_root):
 root=P(output_root).resolve();require(root.is_relative_to(P('/root/share/mnt164').resolve()),'OUTPUT_AND_CACHE_MUST_BE_TRUE164');runtime=root/'.plot_runtime';(runtime/'tmp').mkdir(parents=True,exist_ok=True);(runtime/'mpl').mkdir(exist_ok=True)
 os.environ.update(TMPDIR=str(runtime/'tmp'),TMP=str(runtime/'tmp'),TEMP=str(runtime/'tmp'),MPLCONFIGDIR=str(runtime/'mpl'));return root

def render(data,out,stamp,source_sha):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 from matplotlib.colors import Normalize
 from matplotlib.patches import Rectangle,Patch
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':source_sha+data['provenance']['provider_sha256'],'svg.fonttype':'none'})
 out=P(out);index={(c['program'],c['variant']):c for c in data['cells']};saved=[];styles={'PENDING':('#f1f3f5','PEND',''),'NEGATIVE':('#f8ded5','NEG','//'),'UNUSED_HOLD':('#ffefba','HOLD','..'),'VERIFY_HOLD':('#ebe0f2','CHECK','xx')}
 descriptions={'S_combo':'DH_P0 / combo cycles  (>1: faster than DH_P0)','R_combo':'CH_P0 / DH combo cycles  (>1: faster than original CH_P0)','J':'S_combo / (S_physical × S_PIB)  (>1: above product of actual single-factor ratios)'}
 for metric in METRICS:
  fig,ax=plt.subplots(figsize=(11.5,10.5));fig.subplots_adjust(left=.29,right=.86,top=.83,bottom=.225);cmap=plt.get_cmap('RdBu');norm=Normalize(-2,2);ax.set_xlim(-.5,1.5);ax.set_ylim(9.5,-.5)
  for i,(name,digest)in enumerate(FIXED_INPUTS):
   for j,v in enumerate(VARIANTS):
    c=index[name,v];value=c[metric]
    if value is not None:
     ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=cmap(norm(math.log2(value))),edgecolor='white',linewidth=1.5));suffix={'positive':'↑','negative':'↓','exact_zero':'='}[c[metric+'_direction']];ax.text(j,i,f'{value:.3f} {suffix}',ha='center',va='center',fontsize=12,color='white'if abs(math.log2(value))>1.35 else'#17232e')
    else:
     color,label,hatch=('#e6edf1','MISSING REF','xx')if c['display_state']=='ACCEPTED'else styles[c['display_state']];ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=color,edgecolor='#ccd2d8',hatch=hatch,linewidth=.65));ax.text(j,i,label,ha='center',va='center',fontsize=10,color='#46525e')
  for j,v in enumerate(VARIANTS):
   for y,stats in [(8,data['own_available_set'][v][metric]),(9,data['common_metric_stats'][metric][v])]:
    ax.add_patch(Rectangle((j-.5,y-.5),1,1,facecolor='#f1f3f5'if y==8 else'#e1eaf1',edgecolor='white',linewidth=1.5));value=stats['GM'];label='—'if value is None else f'{value:.3f}';ax.text(j,y,label+f'  (n={stats["n"]}/8)',ha='center',va='center',fontweight='bold'if y==9 else'normal',fontsize=10.5)
  ax.set_xticks(range(2));ax.set_xticklabels([LABELS[j]+f'\naccepted {data["accepted_counts"][v]}/8'for j,v in enumerate(VARIANTS)],fontsize=10.5);ax.xaxis.tick_top();ax.tick_params(axis='both',length=0,pad=10);ax.set_yticks(range(10));ax.set_yticklabels([n+'\n'+d[:8]for n,d in FIXED_INPUTS]+['Per-profile GM\nown available set','Comparable GM\nSAME common inputs'],fontsize=10);ax.axhline(7.5,color='#647481',linewidth=1.2);ax.axhline(8.5,color='#a8b6c1',linewidth=.8)
  for spine in ax.spines.values():spine.set_visible(False)
  title='Physical × PIB combinations — fixed 8-input subset, 16 candidates';title=('CPU LAYOUT ONLY — NO EXPERIMENTAL PERFORMANCE\n'+title)if data['synthetic_layout_only']else title;fig.suptitle(title+'\n'+descriptions[metric],fontsize=13,fontweight='bold',y=.98)
  sm=plt.cm.ScalarMappable(cmap=cmap,norm=norm);bar=fig.colorbar(sm,ax=ax,fraction=.035,pad=.045,extend='both');bar.set_ticks([-2,-1,0,1,2]);bar.set_ticklabels(['0.25','0.5','1','2','4']);bar.set_label('Ratio (log2 color)')
  handles=[Patch(facecolor='#f1f3f5',edgecolor='#ccd2d8',label='PEND: not granted / not closed'),Patch(facecolor='#f8ded5',edgecolor='#ccd2d8',hatch='//',label='NEG: archived unaccepted run'),Patch(facecolor='#ffefba',edgecolor='#ccd2d8',hatch='..',label='HOLD: typed unused safety hold'),Patch(facecolor='#ebe0f2',edgecolor='#ccd2d8',hatch='xx',label='CHECK / MISSING REF: unavailable')];fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.55,.157),ncol=2,frameon=False,fontsize=8.8)
  notes=['Compare profiles only on the same common-set GM row; per-profile available-set denominators can differ.','J requires three actual closed runs plus matched DH_P0; no product prediction is a measured combo result.','Missing is never zero. Exact arrows use integer cycles/products; rounded 1.000 need not mean exact zero.','Physical 640/768/1024 → 80/96/128 KiB declared 128B-line accounting, not verified payload or SRAM/PPA.','PIB and lower-create each 128→192 (+50%); Tag512, allocation4, Tag quota4 and finite widths fixed.','Only the two fixed uniform combinations; no input-wise best stitching, Tag/A2 execution or CORE32 claim.']
  fig.text(.055,.13,'\n'.join(notes),fontsize=8.2,color='#394958',va='top');fig.text(.055,.017,'B Forward2 '+stamp+' | provider '+data['provenance']['provider_sha256'][:12]+' | plot source '+source_sha[:12],fontsize=7.8,color='#5b6976')
  for ext in ['png','svg']:
   p=out/(metric.upper()+'.'+ext);metadata={'Software':'DTC CPU plot '+source_sha}if ext=='png'else{'Date':stamp,'Creator':'DTC CPU plot '+source_sha};fig.savefig(p,dpi=160,metadata=metadata);saved.append(p)
  plt.close(fig)
 return saved,dict(matplotlib=matplotlib.__version__,numpy=np.__version__)

def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--provider',required=True);ap.add_argument('--provider-sha256',required=True);ap.add_argument('--output-root',required=True);args=ap.parse_args(argv)
 provider,pbytes,ps,snapshot,summary=load_provider(args.provider,args.provider_sha256);root=configure_runtime(args.output_root);source=sha(__file__);provenance=dict(provider_path=str(P(args.provider).resolve()),provider_sha256=ps,provider_manifest=provider['manifest'],provider_files=provider['files'],B_forward2_manifest=dict(path=str(B_ROOT/'MANIFEST.json'),sha256=B_MANIFEST_SHA),plot_source_path=str(P(__file__).resolve()),plot_source_sha256=source,observed_utc=snapshot['observed_utc'],V1_dynamic_reference_source=snapshot['V1_dynamic_reference_source']);data=build_data(snapshot,summary,provenance);out=root/('snapshot_'+ps[:16]+'_'+source[:16])
 if out.exists():
  m=read(out/'MANIFEST.json');require(m['provider_sha256']==ps and m['plot_source_sha256']==source,'FROZEN_SNAPSHOT_IDENTITY')
  for ref in m['files']:require(sha(out/ref['name'])==ref['sha256'],'FROZEN_OUTPUT_DRIFT')
  return dict(status='VERIFIED_IMMUTABLE_FIGURE_REUSED',output=str(out),manifest_sha256=sha(out/'MANIFEST.json'))
 out.mkdir();(out/'PROVIDER_SNAPSHOT.json').write_bytes(pbytes);(out/'FIGURE_DATA.json').write_text(json.dumps(data,indent=2)+'\n');files,env=render(data,out,snapshot['observed_utc'],source);(out/'SOURCE_PINS.json').write_text(json.dumps(dict(**provenance,render_environment=env),indent=2)+'\n');members=[dict(name=p.name,size_bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())if p.is_file()];m=dict(schema='DTC_PERFV2_CODESIGN16_FIGURE_MANIFEST_V1',provider_sha256=ps,plot_source_sha256=source,files=members,common_metric_sets=data['common_metric_sets'],models_started=0,services_started=0,scientific_writes=0,Root_visual_review_required=True,manuscript_approval=False);(out/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n');return dict(status='DRAFT_AWAIT_ROOT_VISUAL_REVIEW',output=str(out),manifest_sha256=sha(out/'MANIFEST.json'),accepted=sum(c['accepted']for c in data['cells']))
if __name__=='__main__':print(json.dumps(main()))
