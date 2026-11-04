from pathlib import Path
import types,sys,json,copy,math,collections,ast
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/A_cost_and_figures_v1')
p=O/'plot_codesign16.py';m=types.ModuleType('plot_codesign16_cpu');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
checks=[]
def ck(n,b):assert b,n;checks.append(dict(check=n,passed=True))
def reject(n,fn):
 try:fn()
 except(ValueError,KeyError,TypeError):ck(n,True);return
 raise AssertionError(n)
B=m.B_ROOT;actual=B/'snapshots/forward2_initial20_actual_source/PUBLICATION_PROVIDER.json';v=m.read(actual);ps=m.sha(actual)
reject('unqualified prelaunch provider cannot create scientific figures',lambda:m.load_provider(actual,ps))
reject('provider SHA mismatch rejected',lambda:m.load_provider(actual,'0'*64))
# Pure reference arithmetic/statistics from frozen B source; no collector or runtime call.
btree=ast.parse((B/'consumer.py').read_text());wanted=['metrics','sign','metric_stats','statset','summarize'];pure=ast.Module(body=[x for x in btree.body if isinstance(x,ast.FunctionDef)and x.name in wanted],type_ignores=[])
def require(x,s):assert x,s
ns=dict(math=math,collections=collections,require=require);exec(compile(pure,'B_pure_statistics_CPU','exec'),ns)
rows=[]
for i,(name,digest)in enumerate(m.FIXED_INPUTS):
 for j,var in enumerate(m.VARIANTS):
  accepted=i==0 or(i==1 and j==0);cycles=([800,1000][j]if i==0 else 1250)if accepted else None
  status='ACCEPTED_STRICT_ARCHIVE_RESTORE'if accepted else('ARCHIVED_NEGATIVE_NO_PERFORMANCE'if i==2 and j==0 else'UNUSED_SAFETY_HOLD'if i==3 and j==0 else'VERIFICATION_HOLD'if i==4 and j==0 else'AWAIT_CLOSED_RESULT')
  pc=900+j*100;qc=800 if i==0 else None
  phy=dict(input_digest=digest,variant='PHYS768_TAG64x8'if j==0 else'PHYS1024_TAG64x8',accepted=True,cycles=pc,status='CPU_SYNTHETIC');pib=dict(input_digest=digest,variant='OO_PIB192',accepted=qc is not None,cycles=qc,status='CPU_SYNTHETIC')
  r=dict(program=name,suite='CPU_SYNTHETIC_LAYOUT_NOT_SCIENCE',input_digest=digest,variant=var,design='DH',downstream_profile='P0',cohort='CPU_SYNTHETIC_NOT_NATIVE',uuid='CPU_SYNTHETIC'if accepted else None,status=status,accepted=accepted,cycles=cycles,baseline_DH_cycles=1000,baseline_CH_cycles=800,V1_physical=phy,V1_PIB=pib)
  r.update(ns['metrics'](cycles,1000,800,pc,qc));rows.append(r)
summary=ns['summarize'](rows);snap=dict(rows=rows);prov=dict(provider_sha256='CPU_SYNTHETIC_ONLY')
data=m.build_data(snap,summary,prov,synthetic=True)
ck('fixed sixteen cells eight full inputs two profiles',len(data['cells'])==16 and len(data['input_order'])==8)
ck('own n2/n1 differs but comparable common n1',data['own_available_set'][m.VARIANTS[0]]['S_combo']['n']==2 and data['own_available_set'][m.VARIANTS[1]]['S_combo']['n']==1 and data['common_metric_sets']['S_combo']['n']==1)
ck('J missing singlefactor kept null accepted combo',next(x for x in data['cells']if x['program']=='GEMM'and x['variant']==m.VARIANTS[0])['J']is None)
ck('exact J product arithmetic and common J same input',data['common_metric_sets']['J']['n']==1 and data['cells'][0]['J']==.9)
ck('negative and exactzero directions use integers',data['cells'][1]['S_combo_direction']=='exact_zero'and data['cells'][1]['R_combo_direction']=='negative')
ck('all nonaccepted missing no zero ratios',all(x['S_combo']is None and x['R_combo']is None and x['J']is None for x in data['cells']if not x['accepted']))
ck('negative safetyHOLD pending verification distinct',{x['display_state']for x in data['cells']}=={'ACCEPTED','NEGATIVE','UNUSED_HOLD','PENDING','VERIFY_HOLD'})
for label,mut in [('wrongfullinput',lambda x:x['rows'][0].update(input_digest='bad')),('fakecyclesonpending',lambda x:x['rows'][-1].update(cycles=0)),('wrongratio',lambda x:x['rows'][0].update(S_combo=4)),('wrongJ',lambda x:x['rows'][0].update(J=4)),('unknownprofile',lambda x:x['rows'][0].update(variant='TAG_UNAUTHORIZED'))]:
 bad=copy.deepcopy(snap);mut(bad);reject(label,lambda:m.build_data(bad,summary,prov))
badsummary=copy.deepcopy(summary);badsummary['common_combo_accepted_inputs']['ids']=[];reject('common denominator drift rejected',lambda:m.build_data(snap,badsummary,prov))
ck('rounded1 not an exact zero',m.compare(10**16,10**16+1)=='negative'and format(10**16/(10**16+1),'.3f')=='1.000')
cost=m.read(O/'COST_DATA.json');ck('cost declared counts80 96 128 only no PPA', [r['declared_128B_line_accounting_KiB_per_SM']for r in cost['cost_rows']]==[80,96,128]and all(r['RTL_or_PPA']=='UNKNOWN_NOT_MEASURED'for r in cost['cost_rows']))
# All-missing layout only: no synthetic performance values rendered, no actual preview.
missing=copy.deepcopy(rows)
for r in missing:r.update(status='AWAIT_CLOSED_RESULT',accepted=False,cycles=None,uuid=None,**ns['metrics'](None,1000,800,r['V1_physical']['cycles'],r['V1_PIB']['cycles']))
md=m.build_data(dict(rows=missing),ns['summarize'](missing),prov,synthetic=True)
root=m.configure_runtime(O/'cpu_layout');a=root/'all_missing_a';b=root/'all_missing_b';a.mkdir(exist_ok=True);b.mkdir(exist_ok=True);files,env=m.render(md,a,'2000-01-01T00:00:00+00:00',m.sha(p));m.render(md,b,'2000-01-01T00:00:00+00:00',m.sha(p))
ck('blank layout contains no fabricated performance',all(c[k]is None for c in md['cells']for k in m.METRICS))
ck('PNG SVG deterministic same source provider date',all(m.sha(x)==m.sha(b/x.name)for x in files))
(O/'CPU_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS_PURE_STATISTICS_AND_ALL_MISSING_LAYOUT_ONLY',checks=checks,check_n=len(checks),source_sha256=m.sha(p),environment=env,B_manifest_sha256=m.B_MANIFEST_SHA,actual_prelaunch_provider_sha256=ps,scientific_figures_created=0,all_missing_CPU_layout_only=True,new_models=0,services=0),indent=2)+'\n');print(json.dumps(dict(status='PASS',checks=len(checks),source=m.sha(p),environment=env)))

