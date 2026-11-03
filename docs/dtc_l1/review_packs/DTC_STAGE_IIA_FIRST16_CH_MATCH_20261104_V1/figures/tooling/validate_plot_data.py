
from pathlib import Path
import json,importlib.util,hashlib,importlib.metadata,tempfile,copy
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_figures_v1');A=O.parents[1];s=importlib.util.spec_from_file_location('plot_qa',O/'plot_first8.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);provider=A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json';raw,p,r,summary,rows,common,sources=m.load_provider(provider);d=m.plot_data(p,r,summary,rows,common,sources,m.digest(raw));checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('fixed16_rows8_input_digests',len(d['rows'])==16 and len({x['input_digest']for x in d['rows']})==8)
ck('fixed_declared_program_order',[(x['program'],x['input_digest'])for x in d['fixed_order']]==m.FIXED)
ck('all_missing_F_metrics_remain_null',all(x['S_CH']is None and x['S_DH']is None and x['I']is None for x in d['rows']if x['plot_status']!='accepted'))
ck('accepted_count_equals_B_summary',sum(x['plot_status']=='accepted'for x in d['rows'])==summary['accepted_CH'])
ck('negative_I_retained',next(x for x in d['rows']if x['program']=='vectorAdd'and x['profile']=='F256')['I']<1)
ck('negative_CH_self_retained',next(x for x in d['rows']if x['program']=='vectorAdd'and x['profile']=='F256')['S_CH']<1)
ck('common_GM_source_exact',d['common_F128_F256_metrics']==summary['common_F128_F256_metrics'])
ck('common_population_exact',set(d['common_F128_F256_population'])==set(r['common_F128_F256_population']))
with tempfile.TemporaryDirectory(dir=O/'tmp')as td:
 bad=copy.deepcopy(p);row=next(x for x in bad['files']if x['path'].endswith('/RESULTS.json.gz'));row['sha256']='0'*64;badpath=Path(td)/'bad_provider.json';badpath.write_text(json.dumps(bad))
 try:m.load_provider(badpath)
 except AssertionError:ck('corrupt_source_SHA_fail_closed',True)
 else:raise AssertionError('BAD_PROVIDER_ACCEPTED')
 snap=json.loads((O/'PUBLICATION_PROVIDER.json').read_text());mf=json.loads(Path(snap['manifest']['path']).read_text());ck('every_export_SHA_rechecked',all(m.sha(Path(snap['snapshot'])/x['path'])==x['sha256']for x in mf['files']))
req=[]
for name in ['matplotlib','numpy','contourpy','cycler','fonttools','kiwisolver','pillow','pyparsing','python-dateutil','six','tzdata','packaging']:req.append(name+'=='+importlib.metadata.version(name))
(O/'requirements.lock.txt').write_text('\n'.join(req)+'\n');(O/'CPU_VALIDATION.json').write_text(json.dumps(dict(schema='DTC_STAGEIIA_FIRST8_FIGURE_CPU_VALIDATION_V1',status='PASS',checks=checks,assertions=len(checks),provider_sha256=m.digest(raw),plot_script_sha256=m.sha(O/'plot_first8.py'),models_started=0,registrations=0,synthetic_performance_published=False),indent=2)+'\n');print(json.dumps({'checks':len(checks),'status':'PASS','versions':req}))
