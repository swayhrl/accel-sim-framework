"""CPU-only fixed-eight structural figures. Reads only qualified B V3 snapshots.
No native/controller/registry/model/trace/log/Git/manuscript mutation.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,sys,copy
sys.dont_write_bytecode=True
P=Path
FIXED_PROVIDER=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/B_perf_results_consumer_v3/PUBLICATION_PROVIDER.json')
FIXED_INPUTS=[
 ('2DCONV','d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0'),
 ('GEMM','fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318'),
 ('convolutionSeparable','4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449'),
 ('scan','6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39'),
 ('ATAX','eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950'),
 ('MVT','f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079'),
 ('BICG','ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef'),
 ('vectorAdd','e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799')]
VARIANTS=['PHYS768_TAG64x8','PHYS1024_TAG64x8','OO_PIB192','TAG4BANK_PERBANK2_TOTAL8']
LABELS=['Pool 768','Pool 1024','PIB 192\n+ create-Q 192','Tag grants 2/bank\n4 banks, total 8']
TAG_VARIANTS={'TAG64x16_PHYS640','TAG128x8_PHYS640'}
STATUS={'ACCEPTED_STRICT_ARCHIVE_RESTORE':'ACCEPTED','ARCHIVED_NEGATIVE_NO_PERFORMANCE':'NEGATIVE','UNUSED_FAMILY_HOLD':'UNUSED_HOLD','AWAIT_ACTUAL_REGISTRY_GRANT':'PENDING','AWAIT_CLOSED_RESULT':'PENDING','VERIFICATION_HOLD':'VERIFY_HOLD','RUNTIME_VERIFICATION_HOLD':'VERIFY_HOLD'}
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(path):return sha_bytes(P(path).read_bytes())
def read(path):return json.loads(P(path).read_bytes())
def require(value,message):
 if not value:raise ValueError(message)
def checked(ref):
 p=P(ref['path']);b=p.read_bytes();require(sha_bytes(b)==ref['sha256'],'SOURCE_SHA_DRIFT '+str(p));return b
def gm(values):return math.exp(sum(math.log(x)for x in values)/len(values))if values else None
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
def exact_direction(numerator,denominator):return 'positive'if numerator>denominator else'negative'if numerator<denominator else'exact_zero'
def load_provider(path,expected_sha=None):
 p=P(path);require(p.resolve()==FIXED_PROVIDER.resolve(),'FIXED_V3_PROVIDER_ONLY');b=p.read_bytes();digest=sha_bytes(b)
 if expected_sha is not None:require(digest==expected_sha,'PROVIDER_SHA_MISMATCH')
 v=json.loads(b);require(v['schema']=='DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V3','PROVIDER_SCHEMA');require(v['report_only']is True and v['new_models']==v['native_writes']==0,'REPORT_ONLY_PROVIDER_REQUIRED');require(v['baseline_source_qualified']is True,'BASELINE_SOURCE_NOT_QUALIFIED')
 manifest=json.loads(checked(v['manifest']));require(manifest['schema']=='DTC_PERF_STRUCTURE48_SNAPSHOT_MANIFEST_V3','MANIFEST_SCHEMA');require(manifest['files']==v['files'],'PROVIDER_MANIFEST_FILESET_MISMATCH')
 payload={x['name']:checked(x)for x in v['files']};snapshot=json.loads(payload['SNAPSHOT.json']);summary=json.loads(payload['SUMMARY.json']);require(snapshot['summary']==summary==v['summary'],'SUMMARY_MISMATCH');require(snapshot['source_baselines_qualified']is True,'SNAPSHOT_BASELINE_NOT_QUALIFIED');require(sha(p)==digest,'PROVIDER_CHANGED_DURING_READ')
 return v,b,digest,snapshot,summary

def build_data(snapshot,summary,provenance,synthetic=False):
 rows=snapshot['rows'];expected=dict(FIXED_INPUTS);require(len(rows)==48,'PLAN48_REQUIRED');require(summary['fixed_input_n']==8 and summary['CORE32_population']is False,'FIXED8_NOT_CORE32');require(set((r['program'],r['input_digest'])for r in rows)==set(FIXED_INPUTS),'INPUT_IDENTITY_MISMATCH')
 require(all(r['design']=='DH'and r['downstream_profile']=='P0'for r in rows),'DESIGN_OR_DOWNSTREAM_MISMATCH')
 tag=[r for r in rows if r['variant']in TAG_VARIANTS];require(len(tag)==16 and all(r['status']=='SAFETY_HOLD_CPU_PROGRESS_NEGATIVE'and r['accepted']is False and r['cycles']is None for r in tag),'TAG_SAFETY_HOLD_IDENTITY')
 base={}
 for r in snapshot['baseline_sources']:
  require(r['program']in expected and r['input_digest']==expected[r['program']]and r['accepted']is True and r['source_profile']=='P0','BASELINE_IDENTITY');key=(r['program'],r['source_cell']);require(key not in base,'DUPLICATE_BASELINE');require(type(r['cycles'])is int and r['cycles']>0,'BASELINE_CYCLES');base[key]=r
 require(len(base)==16 and all((n,c)in base for n,_ in FIXED_INPUTS for c in ['CH','DH']),'SIXTEEN_BASELINES_REQUIRED')
 cells=[];index={}
 for r in rows:
  if r['variant']in TAG_VARIANTS:continue
  require(r['variant']in VARIANTS,'UNKNOWN_VARIANT');key=(r['program'],r['variant']);require(key not in index,'DUPLICATE_CELL');require(r['status']in STATUS,'UNKNOWN_STATUS '+r['status']);state=STATUS[r['status']]
  cell=dict(program=r['program'],suite=r['suite'],input_digest=r['input_digest'],variant=r['variant'],cohort=r.get('cohort'),uuid=r.get('uuid'),status=r['status'],display_state=state,reason=r.get('reason',r.get('verification_error')),accepted=r['accepted'],cycles=r['cycles'],CH_P0_cycles=base[r['program'],'CH']['cycles'],DH_P0_cycles=base[r['program'],'DH']['cycles'],S_DH=None,Rnew=None,S_DH_direction=None,Rnew_direction=None,source_references={k:copy.deepcopy(v)for k,v in r.items()if isinstance(v,dict)and'path'in v and'sha256'in v},baseline_references={c:{k:copy.deepcopy(base[r['program'],c][k])for k in ['canonical_RESULT','actual_bottom_RESULT','source_uuid','legal_prior_P0_alias']if k in base[r['program'],c]}for c in ['CH','DH']})
  if state=='ACCEPTED':
   require(r['accepted']is True and type(r['cycles'])is int and r['cycles']>0,'ACCEPTED_CYCLE_IDENTITY');sd=cell['DH_P0_cycles']/r['cycles'];rn=cell['CH_P0_cycles']/r['cycles'];require(near(sd,r['S_DH'])and near(rn,r['Rnew']),'METRIC_MISMATCH');cell.update(S_DH=sd,Rnew=rn,S_DH_direction=exact_direction(cell['DH_P0_cycles'],r['cycles']),Rnew_direction=exact_direction(cell['CH_P0_cycles'],r['cycles']))
  else:require(r['accepted']is False and r['cycles']is None and r.get('S_DH')is None and r.get('Rnew')is None,'UNACCEPTED_MUST_HAVE_NULL_PERFORMANCE')
  if state=='UNUSED_HOLD':require(r.get('uuid')is None,'UNUSED_HOLD_CANNOT_HAVE_EXECUTION_UUID')
  cells.append(cell);index[key]=cell
 require(len(cells)==32,'EXACT32_NON_TAG_CELLS')
 common=[d for n,d in FIXED_INPUTS if all(index[n,v]['display_state']=='ACCEPTED'for v in VARIANTS)];bs=summary['common_nonTag_accepted_intersection'];require(bs['n']==len(common)and set(bs['ids'])==set(common),'COMMON_SET_MISMATCH')
 common_stats={}
 for v in VARIANTS:
  selected=[index[n,v]for n,d in FIXED_INPUTS if d in common];common_stats[v]={metric:gm([c[metric]for c in selected])for metric in ['S_DH','Rnew']}
  for metric in ['S_DH','Rnew']:
   published=bs['variants'][v][metric];require(published['n']==len(common),'GM_DENOMINATOR_MISMATCH');require((common_stats[v][metric]is None and published['GM']is None)or(common_stats[v][metric]is not None and near(common_stats[v][metric],published['GM'])),'COMMON_GM_MISMATCH')
 return dict(schema='DTC_FIXED8_NON_TAG_STRUCTURE_FIGURE_DATA_V1',synthetic_layout_only=synthetic,scope='FIXED8_INPUT_SUBSET_NOT_CORE32',provenance=provenance,input_order=[dict(program=n,input_digest=d)for n,d in FIXED_INPUTS],variant_order=VARIANTS,cells=cells,Tag_safety_HOLD_excluded=16,Tag_HOLD_not_performance_negative=True,common_accepted_intersection=dict(n=len(common),input_digests=common,GM=common_stats),accepted_counts={v:sum(index[n,v]['accepted']for n,_ in FIXED_INPUTS)for v in VARIANTS},no_imputation=True,no_best_per_program=True,exact_zero_from_integer_cycles=True,hardware_boundary='Pool labels count128B-address/dependency slots; actualpayload/PPA unknown. Tag512fixed; PIB192 also lowercreate192; Taggrant quotas are not datasRAMports; CH/DH not equalarea/timing.')

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
 out=P(out);index={(r['program'],r['variant']):r for r in data['cells']};common=data['common_accepted_intersection'];state_styles={'PENDING':('#f1f3f5','PEND',''),'NEGATIVE':('#f8ded5','NEG','//'),'UNUSED_HOLD':('#ffefba','HOLD','..'),'VERIFY_HOLD':('#ebe0f2','CHECK','xx')};saved=[]
 for metric,filename,description in [('S_DH','DH_OWN_SPEEDUP','DH_P0 / candidate cycles  (>1: faster than DH_P0)'),('Rnew','CH0_OVER_DH_CANDIDATE','CH_P0 / candidate cycles  (>1: faster than CH_P0)')]:
  fig,ax=plt.subplots(figsize=(12.5,9.2));fig.subplots_adjust(left=.245,right=.87,top=.79,bottom=.235);cmap=plt.get_cmap('RdBu');norm=Normalize(-2,2);ax.set_xlim(-.5,3.5);ax.set_ylim(8.5,-.5)
  for i,(name,digest)in enumerate(FIXED_INPUTS):
   for j,v in enumerate(VARIANTS):
    c=index[name,v];value=c[metric]
    if c['display_state']=='ACCEPTED':
     color=cmap(norm(math.log2(value)));ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=color,edgecolor='white',linewidth=1.5));direction=c[metric+'_direction'];suffix={'positive':'↑','negative':'↓','exact_zero':'='}[direction];text=f'{value:.3f} {suffix}';ax.text(j,i,text,ha='center',va='center',fontsize=11,color='white'if abs(math.log2(value))>1.35 else'#17232e')
    else:
     color,label,hatch=state_styles[c['display_state']];ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=color,edgecolor='#ccd2d8',hatch=hatch,linewidth=.65));ax.text(j,i,label,ha='center',va='center',fontsize=9.5,color='#46525e')
  for j,v in enumerate(VARIANTS):
   value=common['GM'][v][metric];ax.add_patch(Rectangle((j-.5,7.5),1,1,facecolor='#e7edf2',edgecolor='white',linewidth=1.5));ax.text(j,8,'—'if value is None else f'{value:.3f}',ha='center',va='center',fontweight='bold',fontsize=11)
  ax.set_xticks(range(4));ax.set_xticklabels([LABELS[j]+f'\naccepted {data["accepted_counts"][v]}/8'for j,v in enumerate(VARIANTS)],fontsize=10);ax.xaxis.tick_top();ax.tick_params(axis='both',length=0,pad=10);ax.set_yticks(range(9));ax.set_yticklabels([n+'\n'+d[:8]for n,d in FIXED_INPUTS]+[f'Common-set GM\nsame n={common["n"]}/8'],fontsize=10);ax.axhline(7.5,color='#647481',linewidth=1.2)
  for spine in ax.spines.values():spine.set_visible(False)
  title='Structural exploration — fixed 8-input subset / 32 non-Tag candidates';title=('SYNTHETIC LAYOUT QA — NOT EXPERIMENTAL DATA\n'+title)if data['synthetic_layout_only']else title;fig.suptitle(title+'\n'+description,fontsize=14,fontweight='bold',y=.975)
  sm=plt.cm.ScalarMappable(cmap=cmap,norm=norm);bar=fig.colorbar(sm,ax=ax,fraction=.035,pad=.035,extend='both');bar.set_ticks([-2,-1,0,1,2]);bar.set_ticklabels(['0.25','0.5','1','2','4']);bar.set_label('Cycle ratio (log2 color scale)');handles=[Patch(facecolor='#f1f3f5',edgecolor='#ccd2d8',label='PEND: pending / not yet granted'),Patch(facecolor='#f8ded5',edgecolor='#ccd2d8',hatch='//',label='NEG: archived unaccepted run'),Patch(facecolor='#ffefba',edgecolor='#ccd2d8',hatch='..',label='HOLD: verified unused family hold'),Patch(facecolor='#ebe0f2',edgecolor='#ccd2d8',hatch='xx',label='CHECK: verification hold')];fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.54,.158),ncol=2,frameon=False,fontsize=9)
  notes=['GM uses only the SAME accepted input intersection across all four columns; missing cells never become zero.','Arrows use exact integer-cycle comparisons; a rounded 1.000 may still be ↑ or ↓. Color clips outside 0.25–4.','16 Tag-safety HOLD plan cells were not simulated and are excluded from this grid, not counted as performance negatives.','Costs: pool labels are 128B-line slot accounting, not verified payload/PPA. Tag512 and 850MHz downstream remain fixed.','PIB192 also raises create-Q; Tag2×4 grants do not imply 8 data ports. CH/DH are not equal area or timing.']
  fig.text(.065,.125,'\n'.join(notes),fontsize=8.3,color='#394958',va='top');fig.text(.065,.018,'B V3 observed '+stamp+' | provider '+data['provenance']['provider_sha256'][:12]+' | plot source '+source_sha[:12],fontsize=8,color='#5b6976')
  for ext in ['png','svg']:
   p=out/(filename+'.'+ext);metadata={'Software':'DTC CPU plot '+source_sha}if ext=='png'else{'Date':stamp,'Creator':'DTC CPU plot '+source_sha};fig.savefig(p,dpi=160,metadata=metadata);saved.append(p)
  plt.close(fig)
 return saved,dict(matplotlib=matplotlib.__version__,numpy=np.__version__)

def main(argv=None):
 a=argparse.ArgumentParser();a.add_argument('--provider',required=True);a.add_argument('--output-root',required=True);a.add_argument('--provider-sha256');args=a.parse_args(argv);root=configure_runtime(args.output_root);provider,provider_bytes,provider_sha,snapshot,summary=load_provider(args.provider,args.provider_sha256);source_sha=sha(__file__);provenance=dict(provider_path=str(P(args.provider).resolve()),provider_sha256=provider_sha,provider_manifest=provider['manifest'],files=provider['files'],plot_source_path=str(P(__file__).resolve()),plot_source_sha256=source_sha,observed_utc=provider['observed_utc'],provider_qualification_flags={k:provider.get(k)for k in ['baseline_source_qualified','all_existing_closed_results_qualified','admission_hold_metadata_qualified']});data=build_data(snapshot,summary,provenance);out=root/('snapshot_'+provider_sha[:16]+'_'+source_sha[:16])
 if out.exists():
  manifest=read(out/'MANIFEST.json');require(manifest['provider_sha256']==provider_sha and manifest['plot_source_sha256']==source_sha,'SNAPSHOT_REUSE_IDENTITY_MISMATCH')
  for ref in manifest['files']:require(sha(out/ref['name'])==ref['sha256'],'FROZEN_OUTPUT_DRIFT')
  return dict(status='VERIFIED_IMMUTABLE_SNAPSHOT_REUSED',output=str(out),manifest_sha256=sha(out/'MANIFEST.json'))
 out.mkdir();(out/'PROVIDER_SNAPSHOT.json').write_bytes(provider_bytes);(out/'FIGURE_DATA.json').write_text(json.dumps(data,indent=2)+'\n');files,environment=render(data,out,provider['observed_utc'],source_sha);(out/'SOURCE_PINS.json').write_text(json.dumps(dict(**provenance,render_environment=environment),indent=2)+'\n');entries=[dict(name=p.name,size_bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())if p.is_file()];manifest=dict(schema='DTC_FIXED8_STRUCTURE_FIGURE_SNAPSHOT_MANIFEST_V1',provider_sha256=provider_sha,plot_source_sha256=source_sha,source_baseline='qualified_B_V3_snapshot_only',scope='FIXED8_NOT_CORE32',synthetic=False,files=entries,common_accepted_n=data['common_accepted_intersection']['n'],Tag_safety_HOLD_excluded=16,model_starts=0,scientific_writes=0);(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');return dict(status='DRAFT_FIGURES_AWAIT_ROOT_VISUAL_REVIEW',output=str(out),manifest_sha256=sha(out/'MANIFEST.json'),accepted=sum(c['accepted']for c in data['cells']),common_n=data['common_accepted_intersection']['n'])
if __name__=='__main__':print(json.dumps(main()))
