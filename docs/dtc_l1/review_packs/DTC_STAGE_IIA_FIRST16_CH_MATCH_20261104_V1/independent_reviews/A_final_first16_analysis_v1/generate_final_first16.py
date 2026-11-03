#!/usr/bin/env python3
"""Root-invoked final-first16 report; no execution/registration/controller API.
Both Root science_execution_complete and B terminal flags gate every output.
"""
import argparse,ast,datetime,gzip,hashlib,importlib.util,json,math,os,pathlib,sys
from fractions import Fraction
P=pathlib.Path;BASE=P(__file__).resolve().parent;A=BASE.parents[1];ACCEPT='ACCEPTED_MATCHED_QUADRUPLE';METRICS=('S_CH','S_DH','R','I','R_P0');FS=('F128','F256')
class FinalNotReady(RuntimeError):pass
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(P(p).read_bytes())
def verified(row):
 b=P(row['path']).read_bytes();assert sha_bytes(b)==row['sha256'],('SOURCE_SHA_MISMATCH',row['path']);return b
def dump(p,x):P(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n')
def read_contract():return json.loads((BASE/'GENERATOR_CONTRACT.json').read_text())
def fixed_inputs(contract):
 tree=ast.parse(verified(contract['plot_source']).decode());node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXED'for t in n.targets));fixed=ast.literal_eval(node.value);assert len(fixed)==8 and len({d for p,d in fixed})==8;return fixed

def root_gate(pointer_path):
 raw=P(pointer_path).read_bytes();pointer=json.loads(raw)
 if pointer.get('science_execution_complete')is not True:raise FinalNotReady('ROOT_SCIENCE_EXECUTION_NOT_COMPLETE')
 audit=json.loads(verified(pointer));assert audit['schema']=='DTC_STAGEII_FIRST16_ROOT_COMPLETION_AUDIT_V1'
 if audit.get('science_execution_complete')is not True:raise FinalNotReady('ROOT_AUDIT_SCIENCE_EXECUTION_NOT_COMPLETE')
 return raw,pointer,audit

def load_B(path,contract):
 raw=P(path).read_bytes();provider=json.loads(raw);assert provider['schema']=='DTC_STAGEIIA_FIRST16_ANALYSIS_PUBLICATION_PROVIDER_V1';manifest=json.loads(verified(provider['manifest']));pins={r['path']:r['sha256']for r in manifest['files']};payload={};source=[]
 for name in ['RESULTS.json.gz','SUMMARY.json.gz']:
  matches=[x for x in provider['files']if P(x['path']).name==name];assert len(matches)==1;f=matches[0];assert pins.get(f['path'])==f['sha256'];b=verified(f);payload[name]=json.loads(gzip.decompress(b));source.append(dict(path=f['path'],sha256=f['sha256'],bytes=len(b)))
 report=payload['RESULTS.json.gz'];summary=payload['SUMMARY.json.gz'];fixed=fixed_inputs(contract);assert report['fixed_plan_commit']==contract['fixed_plan_commit'];assert summary['request']==contract['request'];assert report['scientific_population']==summary['scientific_population']=='FIRST8_PREDECLARED_SUBSET_NOT_35_OR_CORE32';assert report['expected_programs']==[p for p,d in fixed]and report['expected_inputs']==[d for p,d in fixed];assert provider['observed_utc']==summary['observed_utc']==report['observed_utc'];assert report['no_best_per_program_selection']and report['no_missing_imputation']and report['no_IR_R2_EP_PQ_PS_substitution'];assert report['remaining48_locked']and summary['remaining48_locked'];rows={(x['input_digest'],x['profile']):x for x in report['rows']};assert len(rows)==16 and set(rows)=={(d,f)for p,d in fixed for f in FS}
 for p,d in fixed:
  r1,r2=[rows[(d,f)]for f in FS];assert r1['program']==r2['program']==p and r1['suite']==r2['suite'];assert r1['CH_P0']==r2['CH_P0']and r1['DH_P0']==r2['DH_P0']
  for r in [r1,r2]:
   for k in ['CH_P0','DH_P0','DH_F']:assert type(r[k])is int and r[k]>0
   if r['status']==ACCEPT:
    assert type(r['CH_F'])is int and r['CH_F']>0
    expected=exact_ratios(r)
    assert all(math.isclose(float(v),r['metrics'][k],rel_tol=1e-11,abs_tol=1e-12)for k,v in expected.items())
   else:assert all(r['metrics'].get(k)is None for k in METRICS)
 assert sum(r['status']==ACCEPT for r in rows.values())==summary['accepted_CH'];assert summary['accepted_CH']+summary['archived_negative_CH']+summary['verification_hold']+summary['await_result']==16
 return raw,provider,report,summary,rows,fixed,source

def require_B_terminal(provider,summary,rows):
 if provider.get('all_registered16_terminal_verified')is not True or summary.get('all_registered16_terminal_verified')is not True:raise FinalNotReady('B_REGISTERED16_NOT_ALL_TERMINAL')
 if summary.get('registered_consumed')!=16 or summary.get('registered_remaining')!=0:raise FinalNotReady('B_BUDGET_NOT_EXACT16_CONSUMED')
 if summary.get('verification_hold')!=0 or summary.get('await_result')!=0:raise FinalNotReady('B_VERIFICATION_OR_RESULT_PENDING')
 if summary.get('accepted_CH',0)+summary.get('archived_negative_CH',0)!=16:raise FinalNotReady('B_TERMINAL_CLASS_COUNT_NOT16')
 for r in rows.values():
  if r['status']!=ACCEPT and not ('NEGATIVE'in r['status'].upper()or'FAIL'in r['status'].upper()):raise FinalNotReady('NONTERMINAL_ROW:'+r['cohort'])

def exact_ratios(r):
 if r['status']!=ACCEPT:return {k:None for k in METRICS}
 c0,cf,d0,df=[r[k]for k in ['CH_P0','CH_F','DH_P0','DH_F']]
 return dict(S_CH=Fraction(c0,cf),S_DH=Fraction(d0,df),R=Fraction(cf,df),I=Fraction(d0*cf,df*c0),R_P0=Fraction(c0,d0))
def stats(values,population,expected):
 assert len(values)==len(population)and len(set(population))==len(population)
 if not values:gm=None
 else:gm=math.exp(sum(math.log(float(v))for v in values)/len(values))
 return dict(n=len(values),expected_n=len(expected),population=population,missing=[d for d in expected if d not in population],missing_count=len(expected)-len(values),GM=gm,positive=sum(v>1 for v in values),negative=sum(v<1 for v in values),exact_zero=sum(v==1 for v in values),zero_definition='exact integer-rational equality to1; no float epsilon')
def derive(report,summary,rows,fixed):
 expected=[d for p,d in fixed];by={key:exact_ratios(r)for key,r in rows.items()};common=[d for p,d in fixed if all(rows[(d,f)]['status']==ACCEPT for f in FS)];assert set(common)==set(report['common_F128_F256_population'])and len(common)==summary['common_both_F_n'];available={};paired={}
 for f in FS:
  pop=[d for p,d in fixed if rows[(d,f)]['status']==ACCEPT];available[f]={k:stats([by[(d,f)][k]for d in pop],pop,expected)for k in METRICS};paired[f]={k:stats([by[(d,f)][k]for d in common],common,expected)for k in METRICS}
  for k in METRICS:
   for ours,B in [(available[f][k],summary['per_profile_available_paired'][f][k]),(paired[f][k],summary['common_F128_F256_metrics'][f][k])]:
    assert ours['n']==B['n']and set(ours['population'])==set(B['population']);assert (ours['GM']is None and B['GM']is None)or math.isclose(ours['GM'],B['GM'],rel_tol=1e-11,abs_tol=1e-12)
 direct_values={k:[]for k in ['CH_F128_over_F256','DH_F128_over_F256','I_F256_over_F128']}
 for d in common:
  a,b=rows[(d,'F128')],rows[(d,'F256')];direct_values['CH_F128_over_F256'].append(Fraction(a['CH_F'],b['CH_F']));direct_values['DH_F128_over_F256'].append(Fraction(a['DH_F'],b['DH_F']));direct_values['I_F256_over_F128'].append(by[(d,'F256')]['I']/by[(d,'F128')]['I'])
 direct={k:stats(v,common,expected)for k,v in direct_values.items()}
 for k,x in direct.items():
  B=summary['direct_F_comparison'][k];assert x['n']==B['n']and set(x['population'])==set(B['population']);assert(x['GM']is None and B['GM']is None)or math.isclose(x['GM'],B['GM'],rel_tol=1e-11,abs_tol=1e-12)
 suite={}
 for name in sorted({r['suite']for r in rows.values()}):
  exp=[d for p,d in fixed if rows[(d,'F128')]['suite']==name];sc=[d for d in common if d in exp];suite[name]={'expected_inputs':exp,'common_population':sc,'common_F128_F256_metrics':{f:{k:stats([by[(d,f)][k]for d in sc],sc,exp)for k in METRICS}for f in FS},'per_F_available':{f:{k:stats([by[(d,f)][k]for d in exp if rows[(d,f)]['status']==ACCEPT],[d for d in exp if rows[(d,f)]['status']==ACCEPT],exp)for k in METRICS}for f in FS},'direct_F_comparison':{k:stats([v for d,v in zip(common,vals)if d in exp],sc,exp)for k,vals in direct_values.items()}}
 wide=[];per_input=[]
 for p,d in fixed:
  a,b=[rows[(d,f)]for f in FS]
  wide.append(dict(program=p,suite=a['suite'],input_digest=d,CH_P0=a['CH_P0'],CH_F128=a['CH_F']if a['status']==ACCEPT else None,CH_F256=b['CH_F']if b['status']==ACCEPT else None,DH_P0=a['DH_P0'],DH_F128=a['DH_F'],DH_F256=b['DH_F'],F128_status=a['status'],F256_status=b['status']))
  for f in FS:
   r=rows[(d,f)];rat=by[(d,f)];per_input.append(dict(program=p,suite=r['suite'],input_digest=d,profile=f,cohort=r['cohort'],status=r['status'],observed_status=r.get('observed_status'),metrics={k:(float(v)if v is not None else None)for k,v in rat.items()},exact_ratio_components={k:({'numerator':v.numerator,'denominator':v.denominator,'sign_vs1':1 if v>1 else -1 if v<1 else 0}if v is not None else None)for k,v in rat.items()},source_refs=r['source_refs']))
 return dict(schema='DTC_STAGEIIA_FIRST16_FINAL_STATISTICS_V1',scientific_population='FIRST8_PREDECLARED_SUBSET_NOT_CORE32_OR_FULL35',fixed_order=[dict(program=p,input_digest=d)for p,d in fixed],six_cycle_wide_rows=wide,per_input_metrics=per_input,per_F_available_paired=available,common_F128_F256_population=common,common_F128_F256_metrics=paired,direct_F_comparison=direct,suite_groups=suite,exact_zero_counts_not_float_epsilon=True,no_best_per_program_selection=True,no_missing_imputation=True,remaining48_locked=True)

def collect_references(rows,fixed,contract):
 old={};new={};inputs={};native=P(contract['native_root'])
 for p,d in fixed:
  for f in FS:
   r=rows[(d,f)]
   for role,ref in r['source_refs'].items():
    if ref is None:
     assert role=='CH_F'and r['status']!=ACCEPT;path=native/'analysis'/(r['cohort']+'.RESULT.json');ref=dict(path=str(path),sha256=sha(path),origin='expected terminal negative RESULT path; hash only; no performance import')
    verified(ref);item=dict(ref,program=p,input_digest=d,role=role,profile=f,cohort=r['cohort']if role=='CH_F'else None);target=new if role=='CH_F'else old
    if ref['path']in target:assert target[ref['path']]['sha256']==ref['sha256']
    else:target[ref['path']]=item
   if d not in inputs:
    spath=native/'control/specs'/(r['cohort']+'.json');sp=json.loads(spath.read_text());assert sp['input_digest']==d;bind=dict(path=sp['input_binding_path'],sha256=sp['input_binding_sha256']);raw=verified(bind);bd=json.loads(raw);assert bd['input_digest']==d;asset=bd['asset'];inputs[d]=dict(program=p,input_digest=d,spec=dict(path=str(spath),sha256=sha(spath)),input_binding=bind,trace_entry=sp['native_simulator_argv'][2],commandlist_sha256=asset['commandlist_sha256'],trace_member_SHA_contract=asset['members'],extent=asset.get('extent'),kind=asset.get('kind'),full_application_numerical_values='UNPROVEN')
 assert len(old)==32 and len(new)==16 and len(inputs)==8
 return dict(schema='DTC_STAGEIIA_FIRST16_FINAL_FULL_SHA_REFERENCES_V1',fixed_input_contracts=list(inputs.values()),original_reference_count=32,new_reference_count=16,original_references=list(old.values()),new_references=list(new.values()),no_IR_R2_EP_PQ_PS_substitution=True)

def validate_boundaries(contract):
 raw=verified(contract['resource_cost_manifest']);manifest=json.loads(raw);base=P(contract['resource_cost_manifest']['path']).parent
 for row in manifest['files']:verified(dict(path=str(base/row['path']),sha256=row['sha256']))
 verified(contract['warm_HtoD_semantics']);verified(contract['plot_source']);return dict(resource_cost=contract['resource_cost_manifest'],warm_HtoD=contract['warm_HtoD_semantics'],plot_source=contract['plot_source'])
def text_report(stat,summary,provenance):
 def n(x):return '—'if x is None else str(x)
 def g(x):return '—'if x is None else f'{x:.9f}'
 lines=['# Final Stage II-A first16 CH matching: fixed first8 subset','',f"B snapshot {summary['observed_utc']}; acceptedCH {summary['accepted_CH']}/16; archivednegativeCH {summary['archived_negative_CH']}/16. Root verified science execution complete. This is the predeclared first8 subset, not core32/full35 coverage or authorization for remaining48.",'', '## Six-cycle comparison','', '| Program | Input digest | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |','|---|---|---:|---:|---:|---:|---:|---:|']
 for r in stat['six_cycle_wide_rows']:lines.append('| '+r['program']+' | '+r['input_digest']+' | '+' | '.join(n(r[k])for k in ['CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256'])+' |')
 lines+=['','Cycle values are whole accepted replay cycles. Null/new negative cells are not zeros and remain in the fixed8 matrix. Full input/member SHA and32 old/16 new source paths are in FULL_SHA_REFERENCES.json.','', '## Per-input matching','', '| Program | F | Status | S_CH=CH0/CHF | S_DH=DH0/DHF | R=CHF/DHF | I=S_DH/S_CH |','|---|---|---|---:|---:|---:|---:|']
 for r in stat['per_input_metrics']:lines.append('| '+r['program']+' | '+r['profile']+' | '+r['status']+' | '+' | '.join(g(r['metrics'][k])for k in ['S_CH','S_DH','R','I'])+' |')
 lines+=['','All signs and exact-zero cases remain. I>1 means the relative change favoursDH; both designs can be slower thanP0. R>1, separately, means DH has fewer cycles thanCH. Neither proves equal area.','', '## Same-population summary','',f"F128/F256 common accepted input count {len(stat['common_F128_F256_population'])}/8. Primary GM and directF comparisons below use precisely this same population. Per-F available sets are preserved separately in STATISTICS.json and must not be compared as if their denominators match.",'', '| F | Metric | n/8 | GM | Positive | Negative | Exactzero | Missing |','|---|---|---|---:|---:|---:|---:|---:|']
 for f in FS:
  for k in METRICS:
   s=stat['common_F128_F256_metrics'][f][k];lines.append(f"| {f} | {k} | {s['n']}/8 | {g(s['GM'])} | {s['positive']} | {s['negative']} | {s['exact_zero']} | {s['missing_count']} |")
 lines+=['','Sign counts compare exact integer-rational ratios to1, without floatepsilon; exact numerator/denominator is retained per input. Zero response never fills a missing value.','', '| Direct same-set comparison | n/8 | GM | Positive | Negative | Exactzero | Missing |','|---|---|---:|---:|---:|---:|---:|']
 for k,s in stat['direct_F_comparison'].items():lines.append(f"| {k} | {s['n']}/8 | {g(s['GM'])} | {s['positive']} | {s['negative']} | {s['exact_zero']} | {s['missing_count']} |")
 lines+=['','CH_F128/F256 andDH_F128/F256 >1 meanF256 is faster. I_F256/I_F128 >1 favours the relativeDH change atF256. No per-program winner is spliced into a uniformGM.','', '## Suite groups on the same common inputs','', '| Suite | F | Metric | n/expected | GM | Positive | Negative | Exactzero | Missing |','|---|---|---|---|---:|---:|---:|---:|---:|']
 for suite,v in stat['suite_groups'].items():
  for f in FS:
   for k in ['S_CH','S_DH','R','I']:
    s=v['common_F128_F256_metrics'][f][k];lines.append(f"| {suite} | {f} | {k} | {s['n']}/{s['expected_n']} | {g(s['GM'])} | {s['positive']} | {s['negative']} | {s['exact_zero']} | {s['missing_count']} |")
 lines+=['','Suite directF and per-F available statistics are retained in STATISTICS.json. The first8 comprise only their declared suites; no Rodinia/Parboil or whole35 inference follows.','', '## Scientific and hardware boundaries','', 'FR-FCFS64→128/256 also raises sharedcredits255→319/447 per controller. L2 remains10MiB, MSHR192×4, missQ32 and DRAM850MHz. Fixed within-design L1/Hash/Tag/PIB and completion service are preserved. CH PAPER_BASE commonPIB256 and Tag scheduling are active; DH PAPER_OO PIB128 is active. Raw DHcommonPIB8 anddtcMSHR32 are not OO active capacities. Declared geometry, active paths and physical area differ; no equal-area, frequency, energy or implementation-free expansion claim. Resource-cost source SHA and line evidence is linked in PROVENANCE.json.','', 'The existing replay policy enables gpgpu_perf_sim_memcpy1 and flush_l2_cache0: HtoD command handling directly updates L2 tags rather than issuing ordinary timed DRAM requests. This is a matched initial-state policy, not a claim all copied lines remain resident. GEMM3MiB copy and2DCONV64MiB copy do not justify equal residency;64MiB exceeds10MiB. Source/capture ELF and original numeric-state binding remain uncertified; strict replay termination does not certify native application numerical correctness. Frozen input identity is unchanged.','', 'Traffic/blockage counter associations do not isolate L2-to-DRAM queue waiting or a sole causal bottleneck. Last printed strict metrics mix scopes; per-kernel endpoint/delta proof is needed before causal attribution. Static address repetition is not observed cachehit/MSHRmerge; missing counters remain unknown. These performance observations neither estimate unfinished cycles nor repair numeric semantics.','', '## Reproduction','', 'STATISTICS.json retains wide cycles, every input/Fmetric, exact ratio components, same-set GM/sign/missing populations and suite groups. FULL_SHA_REFERENCES.json retains input/full member SHA and source paths. Figures use the unchanged SHA-pinned9d plotting source. No simulation/registration/owner/history/manuscript operation is present in this generator. Remaining48 batching is not designed or released by this report.']
 return '\n'.join(lines)+'\n'

def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--provider',required=True);ap.add_argument('--root-audit-latest',required=True);ap.add_argument('--output-root',default=str(BASE/'outputs'));ap.add_argument('--no-figures',action='store_true');a=ap.parse_args(argv)
 # No directory/file writes before both independent execution-complete gates.
 rootraw,pointer,audit=root_gate(a.root_audit_latest);contract=read_contract();raw,provider,report,summary,rows,fixed,sources=load_B(a.provider,contract);require_B_terminal(provider,summary,rows);boundaries=validate_boundaries(contract);stat=derive(report,summary,rows,fixed);refs=collect_references(rows,fixed,contract)
 if not a.no_figures and importlib.util.find_spec('matplotlib')is None:raise FinalNotReady('MATPLOTLIB_UNAVAILABLE_USE_EXISTING_PLOT_VENV')
 tag=sha_bytes(raw)[:12]+'_'+pointer['sha256'][:12]+'_'+sha(__file__)[:12]+('_nofig'if a.no_figures else'_fig');out=P(a.output_root)/tag
 if out.exists():
  manifest=json.loads((out/'MANIFEST.json').read_text());assert all(sha(out/x['path'])==x['sha256']for x in manifest['files'])
 else:
  out.mkdir(parents=True,exist_ok=False);prov=out/'provenance';prov.mkdir();(prov/'B_PROVIDER.json').write_bytes(raw);(prov/'ROOT_AUDIT_POINTER.json').write_bytes(rootraw);(prov/'ROOT_AUDIT.json').write_bytes(verified(pointer));(prov/'GENERATOR_CONTRACT.json').write_bytes((BASE/'GENERATOR_CONTRACT.json').read_bytes());(prov/'generate_final_source.py').write_bytes(P(__file__).read_bytes());(prov/'plot_first8_source.py').write_bytes(verified(contract['plot_source']));(prov/'MEMCPY_INITIAL_L2_STATE.md').write_bytes(verified(contract['warm_HtoD_semantics']));provenance=dict(fixed_plan_commit=contract['fixed_plan_commit'],B_provider=dict(path=str(P(a.provider).resolve()),sha256=sha_bytes(raw)),B_sources=sources,Root_audit_pointer=dict(path=str(P(a.root_audit_latest).resolve()),sha256=sha_bytes(rootraw)),Root_audit=pointer,boundaries=boundaries,generator_sha256=sha(__file__),new_models_started=0,registrations=0,remaining48_locked=True)
  dump(out/'STATISTICS.json',stat);dump(out/'FULL_SHA_REFERENCES.json',refs);dump(out/'PROVENANCE.json',provenance);(out/'FINAL_FIRST16_REPORT.md').write_text(text_report(stat,summary,provenance))
  if not a.no_figures:
   temp=out/'plot-cache';temp.mkdir();os.environ['MPLCONFIGDIR']=str(temp);os.environ['TMPDIR']=str(temp);os.environ['TMP']=str(temp);os.environ['TEMP']=str(temp);s=importlib.util.spec_from_file_location('same9d_final_plotter',prov/'plot_first8_source.py');plot=importlib.util.module_from_spec(s);s.loader.exec_module(plot);figdir=out/'figures';figdir.mkdir();data=plot.plot_data(provider,report,summary,rows,stat['common_F128_F256_population'],sources,sha_bytes(raw));dump(figdir/'FIGURE_DATA.json',data);env=plot.render(figdir,data,rows,summary,stat['common_F128_F256_population']);dump(figdir/'ENVIRONMENT.json',env)
  files=[dict(path=str(p.relative_to(out)),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(out.rglob('*'))if p.is_file()and'plot-cache'not in p.parts and'__pycache__'not in p.parts and p.name!='MANIFEST.json'];dump(out/'MANIFEST.json',dict(schema='DTC_STAGEIIA_FIRST16_FINAL_REPORT_MANIFEST_V1',files=files,B_provider_sha256=sha_bytes(raw),Root_audit_sha256=pointer['sha256'],generator_sha256=sha(__file__),accepted_CH=summary['accepted_CH'],archived_negative_CH=summary['archived_negative_CH'],figures_generated=not a.no_figures,common_n=len(stat['common_F128_F256_population']),science_execution_complete=True,report_generated_after_terminal_gates=True,remaining48_design_or_release=False,new_models_started=0))
 latest=dict(path=str(out/'MANIFEST.json'),sha256=sha(out/'MANIFEST.json'),report=str(out/'FINAL_FIRST16_REPORT.md'),science_execution_complete=True,remaining48_locked=True,new_models_started=0);tmp=BASE/'.LATEST_FINAL_REPORT.writing';dump(tmp,latest);os.replace(tmp,BASE/'LATEST_FINAL_REPORT.json');print(json.dumps(dict(status='FINAL_FIRST16_REPORT_GENERATED',**latest)))
if __name__=='__main__':
 try:main()
 except FinalNotReady as e:print(json.dumps(dict(status='HOLD_NO_FINAL_OUTPUT',reason=str(e))),file=sys.stderr);sys.exit(2)
