"""Bounded small-metadata merge. Never scans Trace/raw or writes old assets."""
import pathlib,json,hashlib,csv,datetime,collections
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');X=J/'execution_performance_first_20261103_v1';V=P(__file__).resolve().parent
oldpath=J/'research/performance_first_20261103_v1/agent_d/PERFORMANCE_CATALOG.json';old=json.loads(oldpath.read_bytes());xp=X/'control/RESULTS_CURRENT.json';xr=json.loads(xp.read_bytes());man=json.loads((X/'control/EXACT_EXECUTION_MANIFEST.json').read_bytes());idx=json.loads(P(man['approved_cells_ref']['path']).read_bytes());cells={z['cohort']:z['point']for z in idx['cells']}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
MECH={'-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass','-gpgpu_ep_l2_ordinary_ro_tag_relief'}
OBS={'-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats'}
PER_INPUT={'-trace','-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
records=[];sources={};hardware={};errors=[]
rawrows=[dict(z,_origin='PRIOR_ACCEPTED_237_CATALOG')for z in old['points']]+[dict(z,_origin='PERFORMANCE_FIRST_EXACT24_CURRENT')for z in xr['points']]
for z in rawrows:
 c=z['cohort'];s=read(z['spec_ref']['path']);assert sha(z['spec_ref']['path'])==z['spec_ref']['sha256'];o=s['expected_effective_options'];source=s['source_identity'];sid=digest(source);sources[sid]=source;cell=cells.get(c,{})
 modeflags={k:o[k]for k in sorted(MECH)if k in o};obs=dict(options={k:o[k]for k in sorted(OBS)if k in o},environment=s.get('observer_env',{}));obsid=digest(obs)
 hw={k:v for k,v in o.items()if k not in MECH|OBS|PER_INPUT};hwid=digest(hw);hardware.setdefault(hwid,dict(full_nonmode_noninput_nonobserver_option_fingerprint=hwid,representative_spec_ref=z['spec_ref'],geometry=s['geometry'],resource_options={k:v for k,v in hw.items()if any(t in k.lower()for t in ['cache:dl2','queue','sched','icnt','clock','descriptor','wad_entries','wbuf','bank_ops','latency'])}))
 profile=s['profile'];msni=cell.get('purpose')=='MODE_SPECIFIC_APPLICATION_NI_NOT_RANKED';ni=msni or s.get('observer_profile')=='T3_DIAG_ON'or 'APPLICATION_NI'in profile or 'MSOFF'in profile
 role='NI_OR_NONCANONICAL_OBSERVER_CONTROL'if ni else'PERFORMANCE_PRIMARY';dram=float(o['-gpgpu_clock_domains'].split(':')[-1]);geo=s['geometry'];ideal='IDEALIZED'in profile or o.get('-gpgpu_ep_l2_diag_copy_free')=='1'or o.get('-gpgpu_ep_l2_diag_l2_data_free')=='1'
 if ideal:scenario='IDEALIZED_DIAGNOSTIC_UPPER_BOUND'
 elif profile=='P_S64_VS_UNIFIED1168_MSOFF':scenario='DIAGNOSTIC_ALTERNATIVE_STATIC_PAYLOAD_BASELINE'
 elif ni:scenario='OBSERVER_NI_NOT_RANKED'
 elif dram>1132:scenario='HIGH_CLOCK_DIAGNOSTIC_SOURCE78_EP_UNQUALIFIED'
 elif dram!=850:scenario='NON850_SERVICE_SENSITIVITY_PPA_UNKNOWN'
 elif geo==dict(slices=64,sets=32,ways=8,line_bytes=128)and profile in ['REF32x8_L100','REF_G_P1168_MSOFF']:scenario='STANDARD850_REFERENCE_HARDWARE'
 elif cell.get('group')=='retention'or c.startswith('EP_PERF_PF_RET_'):scenario='STANDARD850_REFERENCE_HARDWARE'
 else:scenario='OTHER850_ARCHITECTURAL_VARIANT_PPA_UNKNOWN'
 dp=z.get('done_ref');d=read(dp['path'])if dp else{};ap=z.get('accepted_point_ref')
 if not ap and d.get('output'):
  p=P(d['output'])/'ACCEPTED_POINT.json'
  if p.exists():ap=ref(p)
 pt=read(ap['path'])if ap else{};archive=z.get('archive_receipt_ref')
 if not archive:
  p=P(z['spec_ref']['path']).parents[0]/'ARCHIVE_RECEIPT.json'
  if p.exists():archive=ref(p)
 state=z['state'];cycles=z.get('cycles')or pt.get('cycles');rank=state=='CLOSED_ACCEPTED'and role=='PERFORMANCE_PRIMARY'and not ideal and dram<=1132 and scenario!='DIAGNOSTIC_ALTERNATIVE_STATIC_PAYLOAD_BASELINE'
 rec=dict(cohort=c,origin=z['_origin'],program=s['program'],input_identity_sha256=s['input_identity_sha256'],input_binding_ref=s['input_binding_ref'],source_id=sid,source_identity=source,profile=profile,mode=s['mode'],mechanism_switches=modeflags,geometry=geo,nominal_Tag_data_address_coverage_bytes=geo['slices']*geo['sets']*geo['ways']*geo['line_bytes'],modeled_physical_Payload_bytes_allGPU=9568256 if source['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04'else'NOT_REASSERTED_FOR_OTHER_LINEAGE',physical_Payload_is_not_Tag_capacity=True,modeled_resource_cost_ref=s.get('modeled_resource_cost_ref'),hardware_id=hwid,observer_id=obsid,observer_contract=obs,DRAM_MHz=dram,dram_latency=o.get('-dram_latency'),effective_option_count=len(o),complete_effective_options_sha256=digest(o),spec_ref=z['spec_ref'],accepted_point_ref=ap,archive_receipt_ref=archive,done_ref=dp,state=state,cycles=cycles,instructions=z.get('instructions')or pt.get('instructions'),CTA=z.get('CTA')or pt.get('CTA'),kernel_count=z.get('kernel_count')or pt.get('kernel_count'),hardware_drained=pt.get('hardware_drained'),measurement_role=role,scientific_class=scenario,rank_eligible=rank,application_qualification='CLOSED_ACCEPTED_AND_ARCHIVED'if state=='CLOSED_ACCEPTED'else('TECHNICAL_FAILURE_CONSUMED_NO_REFUND'if state=='CLOSED_UNACCEPTED'else'NOT_APPLICATION_ACCEPTED'),estimated_RAM_bytes=s.get('estimated_peak_RAM_bytes'),wall_seconds=z.get('elapsed_seconds')or d.get('elapsed_seconds'),peak_RSS_bytes=z.get('peak_RSS_bytes')or z.get('peak_process_tree_RSS_bytes')or d.get('peak_process_tree_RSS_bytes'),peak_hot_bytes=z.get('peak_hot_bytes')or d.get('peak_hot_bytes'),stop_reason=z.get('stop_reason')or d.get('stop_reason'),same_background_S_over_EP=None,same_background_S_cohort=None,S_REF850_over_candidate=None,EP_REF850_over_same_mode_candidate=None,matched_pair_basis=None)
 records.append(rec)
assert len(records)==len({r['cohort']for r in records})==261
by={r['cohort']:r for r in records};explicit={z['EP']:z for z in old['accepted_matched_comparisons']};sindex=collections.defaultdict(list);ref850=collections.defaultdict(list)
for r in records:
 if r['state']=='CLOSED_ACCEPTED'and r['measurement_role']=='PERFORMANCE_PRIMARY':
  if r['mode']=='S':sindex[(r['source_id'],r['input_identity_sha256'],r['hardware_id'],r['observer_id'])].append(r)
  if r['scientific_class']=='STANDARD850_REFERENCE_HARDWARE':ref850[(r['source_id'],r['input_identity_sha256'],r['mode'])].append(r)
def choose(xs):return sorted(xs,key=lambda z:(0 if z['origin']=='PRIOR_ACCEPTED_237_CATALOG'else 1,z['cohort']))[0]if xs else None
pairs=[]
for r in records:
 if r['state']!='CLOSED_ACCEPTED'or not r['cycles']or r['measurement_role']!='PERFORMANCE_PRIMARY':continue
 s=None;basis=None
 if r['cohort']in explicit:s=by[explicit[r['cohort']]['S']];basis='PRIOR_MAIN_FORMAL_MATCHED_PAIR'
 elif r['mode']!='S':s=choose(sindex[(r['source_id'],r['input_identity_sha256'],r['hardware_id'],r['observer_id'])]);basis='EXACT_SOURCE_INPUT_NONMODE_HARDWARE_OBSERVER_MATCH; MODE_LEGALITY_FROM_ACCEPTED_NATIVE_CONTRACTS'
 if s and s['state']=='CLOSED_ACCEPTED'and s['source_id']==r['source_id']and s['input_identity_sha256']==r['input_identity_sha256']:
  r.update(same_background_S_over_EP=s['cycles']/r['cycles'],same_background_S_cohort=s['cohort'],matched_pair_basis=basis)
  pairs.append(dict(S_cohort=s['cohort'],EP_cohort=r['cohort'],source_id=r['source_id'],input_identity_sha256=r['input_identity_sha256'],hardware_id=r['hardware_id'],mode=r['mode'],scientific_class=r['scientific_class'],speedup=s['cycles']/r['cycles'],basis=basis,rank_eligible=r['rank_eligible']))
 ss=choose(ref850[(r['source_id'],r['input_identity_sha256'],'S')]);ee=choose(ref850[(r['source_id'],r['input_identity_sha256'],r['mode'])])
 if ss:r['S_REF850_over_candidate']=ss['cycles']/r['cycles'];r['S_REF850_cohort']=ss['cohort']
 if ee:r['EP_REF850_over_same_mode_candidate']=ee['cycles']/r['cycles'];r['EP_REF850_same_mode_cohort']=ee['cohort']
frontiers=[]
for sid,iid in sorted({(r['source_id'],r['input_identity_sha256'])for r in records}):
 for panel,predicate in [('FIXED_STANDARD850',lambda r:r['scientific_class']=='STANDARD850_REFERENCE_HARDWARE'),('NONIDEAL_LEGAL_OBSERVED_PPA_UNKNOWN',lambda r:r['scientific_class']not in ['IDEALIZED_DIAGNOSTIC_UPPER_BOUND','HIGH_CLOCK_DIAGNOSTIC_SOURCE78_EP_UNQUALIFIED','OBSERVER_NI_NOT_RANKED'])]:
  xs=[r for r in records if r['source_id']==sid and r['input_identity_sha256']==iid and r['mode']!='S'and r['rank_eligible']and predicate(r)]
  if xs:
   z=min(xs,key=lambda r:(r['cycles'],r['cohort']));frontiers.append(dict(source_id=sid,input_identity_sha256=iid,program=z['program'],panel=panel,cohort=z['cohort'],mode=z['mode'],cycles=z['cycles'],hardware_id=z['hardware_id'],same_background_S_over_EP=z['same_background_S_over_EP'],S_REF850_over_candidate=z['S_REF850_over_candidate'],PPA='UNKNOWN; NO_EQUAL_AREA_CLAIM',population='OBSERVED_LEGAL_SOURCE_SPECIFIC; NOT_UNIFORM_OR_GLOBAL_OPTIMUM'))
uniform=[]
for key in sorted({(r['source_id'],r['hardware_id'],r['mode'],r['observer_id'])for r in records if r['rank_eligible']and r['mode']!='S'}):
 xs=[r for r in records if(r['source_id'],r['hardware_id'],r['mode'],r['observer_id'])==key and r['rank_eligible']];ps=[r for r in xs if r['same_background_S_over_EP']is not None]
 uniform.append(dict(source_id=key[0],hardware_id=key[1],mode=key[2],observer_id=key[3],accepted_input_count=len({r['input_identity_sha256']for r in xs}),matched_S_input_count=len(ps),positive=sum(r['same_background_S_over_EP']>1 for r in ps),negative=sum(r['same_background_S_over_EP']<1 for r in ps),zero=sum(r['same_background_S_over_EP']==1 for r in ps),minimum_speedup=min((r['same_background_S_over_EP']for r in ps),default=None),maximum_speedup=max((r['same_background_S_over_EP']for r in ps),default=None),cohorts=[r['cohort']for r in xs],GM=None,coverage='NOT_A_FROZEN_COMMON_SET'))
diagnostics=[r for r in records if r['scientific_class']in ['IDEALIZED_DIAGNOSTIC_UPPER_BOUND','DIAGNOSTIC_ALTERNATIVE_STATIC_PAYLOAD_BASELINE','HIGH_CLOCK_DIAGNOSTIC_SOURCE78_EP_UNQUALIFIED']]
result=dict(schema='EP_MAIN_UNIFIED_SOURCE_SPECIFIC_PERFORMANCE_SCOREBOARD_V2',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),current_input_population=len({r['input_identity_sha256']for r in records}),source5_index=sources,hardware_index=hardware,points=records,matched_pairs=pairs,per_workload_best_legal=frontiers,uniform_hardware_mode_panels=uniform,diagnostic_bound_and_failure_cohorts=[r['cohort']for r in diagnostics],coverage=dict(frozen35_complete=False,main42_complete=False,ordinary96_complete=False,missing_metric='UNKNOWN_NOT_ZERO',no_global_GM=True),provenance=dict(prior_catalog_ref=ref(oldpath),current24_table_ref=ref(xp),original_24_manifest_ref=ref(X/'control/EXACT_EXECUTION_MANIFEST.json')),validation=dict(points=len(records),state_counts=dict(collections.Counter(r['state']for r in records)),accepted_only_for_performance=True,OFF_controls_never_ranked=not any(r['rank_eligible']and r['measurement_role']!='PERFORMANCE_PRIMARY'for r in records),no_cross_Source5_performance_pairs=all(by[p['S_cohort']]['source_id']==by[p['EP_cohort']]['source_id']for p in pairs),complete_frozen_specs_SHA_checked=True,Trace_or_raw_scans=0,model_starts=0,registry_writes=0))
(V/'UNIFIED_PERFORMANCE_SCOREBOARD.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
columns=['cohort','program','input_identity_sha256','source_id','profile','mode','state','cycles','instructions','CTA','kernel_count','DRAM_MHz','dram_latency','effective_option_count','scientific_class','measurement_role','rank_eligible','same_background_S_over_EP','same_background_S_cohort','S_REF850_over_candidate','EP_REF850_over_same_mode_candidate','wall_seconds','peak_RSS_bytes','peak_hot_bytes','matched_pair_basis']
with(V/'UNIFIED_PERFORMANCE_SCOREBOARD.csv').open('w',newline='')as f:w=csv.DictWriter(f,columns,extrasaction='ignore');w.writeheader();w.writerows(records)
with(V/'PER_WORKLOAD_BEST_LEGAL.csv').open('w',newline='')as f:
 cols=list(frontiers[0]);w=csv.DictWriter(f,cols);w.writeheader();w.writerows(frontiers)
with(V/'UNIFORM_CONFIG_PANELS.csv').open('w',newline='')as f:
 cols=[k for k in uniform[0]if k!='cohorts'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(uniform)
print(json.dumps(result['validation']));print('sources',len(sources),'uniformpanels',len(uniform),'paired',len(pairs),'bytes',(V/'UNIFIED_PERFORMANCE_SCOREBOARD.json').stat().st_size)
for r in records:
 if r['program']in ['fastWalshTransform','GEMM','stencil']and r['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04'and(r['profile']=='REF32x8_L100'or r['origin']=='PERFORMANCE_FIRST_EXACT24_CURRENT')and r['measurement_role']=='PERFORMANCE_PRIMARY':print(r['cohort'],r['state'],r['cycles'],r['same_background_S_over_EP'],r['S_REF850_over_candidate'],r['EP_REF850_over_same_mode_candidate'])

with(V/'SOURCE5_INDEX.csv').open('w',newline='')as f:
 cols=['source_id','core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256','archive_sha256'];w=csv.DictWriter(f,cols);w.writeheader();w.writerows(dict(source_id=k,**v)for k,v in sources.items())
