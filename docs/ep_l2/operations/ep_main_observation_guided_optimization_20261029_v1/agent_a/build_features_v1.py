import csv,datetime,hashlib,json,pathlib,re,collections,time,resource
START=time.time()
J=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
O=J/'receipts/lane_o_v1r2_20261029/review/docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1'
R=J/'research/observation_guided_20261029_v1/agent_a'
R.mkdir(parents=True,exist_ok=True)
READS={}
def read(p):
 p=pathlib.Path(p);b=p.read_bytes();READS[str(p)]={'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return b
def load(p):return json.loads(read(p))
def dump(n,a):
 p=R/n;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def csvout(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r));p=R/n
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in r.items()})
 return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
C=load(J/'agent_b/results_analysis_20261028_v1/CURRENT.json')
AR=next(x for x in C['files'] if x['path'].endswith('.json'));A=load(AR['path']);assert READS[AR['path']]['sha256']==AR['sha256']
CV=load(J/'agent_b/foreground_closeout_20261029_v1/v2/CURRENT_COVERAGE_BY_INPUT.json')
W=load(O/'agents/W_reference_metrics.json');V=load(O/'agents/V_ACCEPTED_REFERENCE_COUNTERS.json');M=load(O/'agents/coverage_snapshot/ACCEPTED_REFERENCE_MSHR_SUMMARY.json')
contract=read(O/'MEASUREMENT_CONTRACT.md');ni=read(O/'NI_MATRIX.md');md=read(O/'agents/M.md').decode()
E={e['cohort']:e for e in A['endpoints'] if e.get('accepted') and e['state']=='CLOSED_ACCEPTED'}
WM={};VM={};MM={};errors=[]
def check(cohort,inputid,sha):
 e=E.get(cohort)
 if not e or e['input_identity_sha256']!=inputid or e['validation_ref']['sha256']!=sha:
  errors.append({'cohort':cohort,'error':'LANE_O_TO_CURRENT_EXACT_ENDPOINT_IDENTITY_MISMATCH'});return False
 return True
for w in W['rows']:
 if check(w['cohort'],w['input_sha'],w['bundle_sha256']):WM[w['cohort']]=w
for v in V['rows']:
 if check(v['cohort'],v['input_identity_sha256'],v['bundle_ref']['sha256']):VM[v['cohort']]=v
for m in M['cases']:
 if check(m['cohort'],m['input_identity_sha256'],m['bundle_ref']['sha256']):MM[m['cohort']]=m
# The already-reviewed compact markdown table is exact integer evidence, not a new raw projection.
RO={}
for line in md.splitlines():
 if not line.startswith('|EP_PERF_'):continue
 q=line.strip('|').split('|')
 if len(q)!=9 or '/' not in q[1]:continue
 coh=q[0];e=E.get(coh)
 if e is None:continue
 # The markdown also carries the exact cohort's bundle ref and SHA; require this token match.
 if e['validation_ref']['sha256'] not in md:errors.append({'cohort':coh,'error':'M_MD_BUNDLE_SHA_NOT_FOUND'});continue
 cand,reads=map(int,q[1].split('/'));accepted,tx,merge=map(int,q[2:5]);assert accepted==tx+merge
 RO[coh]={'status':'OBSERVED','boundary':'ACCEPTED_GLOBAL_DEMAND_READ_AND_ACCEPTED_RO','candidate':cand,'accepted_global_demand_reads':reads,'accepted_ro':accepted,'transactions':tx,'merges':merge,'merge_fraction':None if accepted==0 else merge/accepted,'merge_ratio_contract':{'numerator':merge,'denominator':accepted,'class':'ACCEPTED_RO_REQUESTERS','boundary':'ADMISSION','dedup':'requester','complete':True},'max_slice_live_transactions':int(q[6]),'max_slice_pending_unique_lines':int(q[7]),'duplicate_sectors':int(q[8]) if q[8].isdigit() else None,'strict_before_ready':'NOT_COLLECTED','source':'Lane O agents/M.md exact accepted table; transaction live includes ready/draining'}
# New read of compact validation metadata only for accepted reference endpoints not in W/V summaries.
# No Trace/raw is opened. Keep missing optional fields unknown; do not reconstruct all old summaries.
late={};newM={};reused_MSHR_count=len(MM)
for coh,e in E.items():
 if e['profile']!='REF32x8_L100' or (coh in WM and (e['mode']=='S' or coh in VM) and coh in MM):continue
 b=read(e['validation_ref']['path']);assert hashlib.sha256(b).hexdigest()==e['validation_ref']['sha256']
 validation=json.loads(b);model=validation['model'];mech=model.get('mechanism_metrics',{});vic=mech.get('full_mechanism_records',{}).get('victim',{})
 late[coh]={'cohort':coh,'input_identity_sha256':e['input_identity_sha256'],'mode':e['mode'],'bundle_ref':e['validation_ref'],'boundary':'VALIDATED_FINAL_SLICE_RECORDS','bottleneck':mech.get('bottleneck',{}),'local_service':mech.get('local_service',{}),'copy':mech.get('trigger',{}),'victim':{k:sum(z.get(k,0) for z in vic.values()) for k in ['read_responses','dirty_forward_responses','clean_installs','dirty_installs','served_sector_bytes']} if vic else None}
 if coh not in MM:
  scopes=validation.get('application',{}).get('application_scopes',{});b0=list(scopes.get('EPL2B0V1',{}).values());m0=list(scopes.get('EPL2M0AV1',{}).values())
  def agg(records,key,op):
   return op(int(x[key]) for x in records) if records and all(key in x for x in records) else None
  newM[coh]={'cohort':coh,'mode':e['mode'],'input_identity_sha256':e['input_identity_sha256'],'bundle_ref':e['validation_ref'],'status':'OBSERVED' if b0 else 'NOT_EMITTED','source_identity':e['source_identity'],'profile':e['profile'],'geometry':e['geometry'],'observer':e['observer'],'scope':'application_cumulative selected final records; max per-slice peaks not simultaneous GPU peak','slice_records_B0':len(b0),'slice_records_M0a':len(m0),'line_max_over_slices':agg(b0,'line_mshr_max',max),'descriptor_max_over_slices':agg(b0,'descriptor_max',max),'WAD_max_over_slices':agg(b0,'wad_max',max),'line_full_events_sum':agg(b0,'c7d_line_mshr_full_block',sum),'line_full_head_observations_sum':agg(m0,'m0_frontend_head_blocked_cycles_line_mshr',sum),'line_eligible_sum':agg(b0,'c7d_line_mshr_alloc_eligible',sum),'line_semantic_need_sum':agg(b0,'c7e_line_mshr_need',sum),'descriptor_full_events_sum':agg(b0,'c7d_descriptor_pool_full_block',sum),'head_reasons':{k:mech.get('bottleneck',{}).get(k) for k in ['LINE_MSHR_FULL','PER_ADDRESS_CAP','DESCRIPTOR_FULL','TAG_FAIL','LOWER_QUEUE','MISS_QUEUE']},'denominator_warning':'No unique-demand incidence inferred from MS/FT mixed class populations'}
  MM[coh]=newM[coh]
P=collections.defaultdict(list)
for p in A['pairs']:
 if p['profile']=='REF32x8_L100':P[p['input_identity_sha256']].append(p)
rows=[];gaps=[]
for c in CV['rows']:
 h=c['input_identity_sha256'];eps=[e for e in E.values() if e['input_identity_sha256']==h and e['profile']=='REF32x8_L100'] if h else []
 f={'program':c['program'],'suite':c['suite'],'input_identity_sha256':h,'program_id':c.get('program_id'),'member_ordinary96':c['member_ordinary96'],'member_main35':c['member_main35'],'member_main42':c['member_main42'],'coverage_status':c['coverage_status'],'execution_status':c['execution_status'],'qualification_status':c['qualification_status'],'old_RO_status':c.get('old_RO_status'),'old_RO_asof_utc':c.get('old_RO_asof_utc'),'model_limitations':c.get('model_limitations'),'runtime_boundary_status':c.get('runtime_boundary_status'),'scientific_launch_grant':False,'reference_accepted_modes':sorted(e['mode'] for e in eps),'reference_endpoints':[],'mechanism_opportunities':[],'historical_reuse_mapping':'IDENTITY_UNRESOLVED_NO_CURRENT_INPUT_AND_ORDERED_COMMANDLIST_MATCH','new_observer_NI':'NOT_PREPARED_NOT_QUALIFIED','complete_capture_and_numerical_output':'UNKNOWN'}
 for e in eps:
  e=dict(e);e.setdefault('RO_qualification_ref',None)
  coh=e['cohort'];w=WM.get(coh);v=VM.get(coh);m=MM.get(coh);l=late.get(coh)
  z={'cohort':coh,'mode':e['mode'],'source_identity':e['source_identity'],'spec_ref':e['spec_ref'],'semantic_population_digest':e['semantic_population_digest'],'validation_ref':e['validation_ref'],'point_ref':e['point_ref'],'archive_ref':e['archive_ref'],'geometry':e['geometry'],'cycles':e['cycles'],'observer':e['observer'],'RO_applicability':e['RO_applicability'],'RO_qualification_ref':e['RO_qualification_ref'],'RO_M':RO.get(coh,{'status':'NOT_APPLICABLE' if not e.get('M') else 'NOT_PROJECTED_EXISTING_ACCEPTED_BUNDLE_AVAILABLE','strict_before_ready':'NOT_COLLECTED' if e.get('M') else 'NOT_APPLICABLE'}),'W':{'status':'OBSERVED' if w else 'NOT_PROJECTED_EXISTING_ACCEPTED_BUNDLE_AVAILABLE'},'V':{'status':'NOT_APPLICABLE' if e['mode']=='S' else 'OBSERVED' if v else 'OBSERVED' if l and l['victim'] else 'NOT_PROJECTED_EXISTING_ACCEPTED_BUNDLE_AVAILABLE'},'ordinary_MSHR':m or {'status':'NOT_PROJECTED_EXISTING_ACCEPTED_BUNDLE_AVAILABLE'},'T':{'enabled':e['T'],'runtime_joint_status':'NOT_APPLICABLE' if not e.get('M') else 'NOT_COLLECTED','structural_joint_status':'NOT_APPLICABLE' if not e.get('M') else 'NOT_COLLECTED','heavy_tag_observer':e['observer']['env'].get('EPL2_TAG_LIFETIME'),'actual_detach_status':'NOT_PROJECTED_DO_NOT_INFER_ZERO'}}
  if w:
   z['W'].update({k:w[k] for k in ['wb_created','wb_completed','wb_lower_accepted','logical_copy_reads','logical_copy_writes','bank_logical_ops','bank_wait_cycles','wad_max','c7d_wad_full_events','c7d_wad_hazard_events','wad_avg_slice_range','c7d_wad_lifetime_avg_slice_range','c7d_wad_lifetime_max']})
   z['W']['head_reasons']={k:{s:w['MS_bottleneck'][k][s] for s in ['blocked_observations_over_slices','distinct_requests_first_block','request_wait_cycle_sum','request_wait_max','unknown_while_unresolved']} for k in ['SAME_ADDRESS_WB','WAD_FULL','WB_DATA_SPACE','COPY_PIPELINE','DATA_SERVICE']}
   obs=w['MS_observer'];den=sum(x['sampled_cycles'] for x in obs);z['W']['WBUF_time_mean_over_slice_ticks']=sum(x['wb_sum'] for x in obs)/den if den else None;z['W']['WBUF_peak_max_over_slices']=max(x['wb_peak'] for x in obs);z['W']['WBUF_occupancy_denominator_slice_ticks']=den;z['W']['incidence_rate']='UNKNOWN_MS_AND_FT_CLASS_POPULATIONS_NOT_PROVEN_EQUAL'
   if e['mode']=='S' and w['logical_copy_reads']+w['logical_copy_writes']>0:f['mechanism_opportunities'].append('W_COPY_ELIMINATION_OBSERVED_NOT_ISOLATED_GAIN')
   if e['mode']=='S' and w['MS_bottleneck']['WB_DATA_SPACE']['distinct_requests_first_block']>0:f['mechanism_opportunities'].append('W_WB_DATA_SPACE_HEAD_PRESSURE_OBSERVED')
  elif l:z['W'].update({'logical_copy_reads':l['copy'].get('logical_copy_reads'),'logical_copy_writes':l['copy'].get('logical_copy_writes'),'head_reasons':l['bottleneck'],'local_service':l['local_service'],'status':'PARTIAL_OBSERVED_NEW_SMALL_BUNDLE_PROJECTION'})
  if v:z['V']['metrics']=v['metrics'];z['V']['source']='REUSED_LANE_O_SMALL_SUMMARY'
  elif l and l['victim'] and e['mode']!='S':z['V']['metrics']=l['victim'];z['V']['source']='NEW_SMALL_ACCEPTED_BUNDLE_PROJECTION'
  if z['V'].get('metrics',{}).get('read_responses',0)>0:f['mechanism_opportunities'].append('V_ACTUAL_RESPONSE_SERVICE_OBSERVED_NOT_INDEPENDENT_GAIN')
  if RO.get(coh,{}).get('merges',0)>0:f['mechanism_opportunities'].append('M_LIVE_RO_MERGE_OBSERVED_FILL_BEFORE_REUSE_UNKNOWN')
  f['reference_endpoints'].append(z)
 f['mechanism_opportunities']=sorted(set(f['mechanism_opportunities'])) or ['UNKNOWN_NO_QUALIFIED_DYNAMIC_EVIDENCE' if not eps else 'NO_POSITIVE_OPPORTUNITY_IN_REUSED_SUBSET_NOT_PROOF_OF_ABSENCE']
 f['reference_performance']=[{k:p[k] for k in ['pair_key','treatment','S_cycles','F_cycles','speedup_S_over_treatment','hardware_background_digest','source_identity']} for p in P[h]] if h else []
 f['accepted_alternative_geometry_detach']=[d for d in A['actual_smallG_final_RO_detaches'] if d['input_identity_sha256']==h]
 for name,status,action in [('W_copy_WB_head_pressure','OBSERVED' if any(x['W']['status'].startswith(('OBSERVED','PARTIAL')) for x in f['reference_endpoints']) else 'NOT_PROJECTED_OR_NOT_RUN','REUSE_ACCEPTED_SUMMARY_OR_SMALL_BUNDLE_NO_MODEL'),('V_actual_response','OBSERVED' if any(x['V']['status']=='OBSERVED' for x in f['reference_endpoints']) else 'NOT_APPLICABLE' if eps and all(e['mode']=='S' for e in eps) else 'NOT_PROJECTED_OR_NOT_RUN','REUSE_LEGAL_F_WV_SUMMARY_NO_MODEL'),('ordinary_MSHR_pressure','OBSERVED' if any(e['cohort'] in MM for e in eps) else 'NOT_PROJECTED_OR_NOT_RUN','REUSE_EXISTING_SMALL_SUMMARY_FIRST'),('RO_live_merge','OBSERVED' if any(e['cohort'] in RO for e in eps) else 'NOT_APPLICABLE' if eps and all(not e.get('M') for e in eps) else 'NOT_PROJECTED_OR_NOT_RUN','REUSE_EXISTING_ACCEPTED_BUNDLE_BEFORE_NEW_COLLECTION'),('W_unified_stage_lifetime_RW_atomic_by_age','NOT_COLLECTED','IF_DECISION_REQUIRES_DEFAULT_OFF_EVENT_COUNTER_AND_PATH_NI'),('V_age_next_touch_reuse_distance','IDENTITY_UNRESOLVED_HISTORICAL_SMALL_ARTIFACTS','LOCATE_EXACT_HISTORICAL_MANIFEST_CSV_BEFORE_NEW_COLLECTION'),('ingress_gap_before_ready','NOT_COLLECTED_AT_INGRESS','REAL_PUSH_CHILD_HOOK_ONLY_IF_NEEDED_NOT_FIRST_HEAD'),('head_before_ready_and_pending_address_union','NOT_COLLECTED','EVENT_REFCOUNT_NORMAL_RO_UNION_AND_REQUIRED_SECTOR_READY'),('T_same_UID_set_tick_full_structural_RO','NOT_APPLICABLE' if eps and all(not e.get('M') for e in eps) else 'NOT_COLLECTED','LEGAL_F_STRUCTURAL_VS_POLICY_SEPARATE_AND_F_MINUS_T_CONTROL'),('exact_demand_WB_incidence','UNKNOWN_CLASS_DENOMINATOR','DO_NOT_DIVIDE_MS_HEAD_COUNTS_BY_FT_REQUESTERS'),('new_observer_NI','NOT_PREPARED_NOT_QUALIFIED','S_OFF_ON_DOES_NOT_COVER_F_WV')]:
  gaps.append({'program':c['program'],'input_identity_sha256':h,'program_id':c.get('program_id'),'metric':name,'status':status if h else 'IDENTITY_UNRESOLVED','action':action,'new_model_authorization':0})
 rows.append(f)
assert len(rows)==103 and sum(r['member_ordinary96'] for r in rows)==96 and sum(r['member_main35'] for r in rows)==35 and sum(r['member_main42'] for r in rows)==42
assert not errors,errors
assert {e['input_identity_sha256'] for e in E.values()} <= {r['input_identity_sha256'] for r in rows}
assert next(r for r in rows if r['input_identity_sha256']=='fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e')['reference_accepted_modes']==['S','WV_ZERO_RO']
assert all(e['RO_M']['status']=='NOT_APPLICABLE' for r in rows for e in r['reference_endpoints'] if e['mode']=='S')
compact=[]
for r in rows:
 x={k:r[k] for k in ['program','suite','input_identity_sha256','program_id','member_ordinary96','member_main35','member_main42','coverage_status','qualification_status','old_RO_status','reference_accepted_modes','mechanism_opportunities','historical_reuse_mapping']}
 for e in r['reference_endpoints']:
  pre=e['mode'];x[pre+'_cycles']=e['cycles'];x[pre+'_W_status']=e['W']['status'];x[pre+'_WB_created']=e['W'].get('wb_created');x[pre+'_copy_read_ops']=e['W'].get('logical_copy_reads');x[pre+'_copy_write_ops']=e['W'].get('logical_copy_writes');x[pre+'_WB_space_first_block_UID']=e['W'].get('head_reasons',{}).get('WB_DATA_SPACE',{}).get('distinct_requests_first_block');x[pre+'_V_status']=e['V']['status'];x[pre+'_V_responses']=e['V'].get('metrics',{}).get('read_responses');x[pre+'_V_dirty_forward']=e['V'].get('metrics',{}).get('dirty_forward_responses');x[pre+'_RO_status']=e['RO_M']['status'];x[pre+'_RO_admitted']=e['RO_M'].get('accepted_ro');x[pre+'_RO_merges']=e['RO_M'].get('merges');x[pre+'_normal_line_MSHR_peak']=e['ordinary_MSHR'].get('line_max_over_slices');x[pre+'_MSHR_full_head_UID']='NOT_PROJECTED';x[pre+'_T_joint']=e['T']['runtime_joint_status']
 for p in r['reference_performance']:x['S_over_'+p['treatment']]=p['speedup_S_over_treatment']
 x['missing_metric_values']='Blank numeric cells accompany explicit unavailable/N_A statuses; never measured zero';compact.append(x)
hist=[]
HD=pathlib.Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/chatgpt_handoff')
for n,core,fw,state in [('MOTIVATION_FINAL_CHATGPT_REVIEW.md','2a6a31591bc42023e5997cca969e4b672efe0405','02f36816f60afcff55e910cdef2b60937e691cdc','DATA_SEMANTICS_PASS_PACKAGING_NOT_FINAL'),('STREAMING_REUSE_PREFINAL_CHATGPT_REVIEW.md','ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919','db1c90182fad02aacbd282b67ecdc57b8e4cc365','DIRECTION_PASS_FIX_REQUIRED_NOT_FINAL')]:
 read(HD/n);hist.append({'review_ref':READS[str(HD/n)],'core':core,'framework':fw,'acceptance_boundary':state,'current_input_mapping':'IDENTITY_UNRESOLVED','missing':['ordered_kernel_and_commandlist_binding','exact_input_content_manifest','small_CSV_and_aggregation_manifest_locator','final_delta_and_recency_tie_fix_for_streaming'],'no_new_trace_scan':True})
strata={}
for r in rows:
 for e in r['reference_endpoints']:
  key=json.dumps({'source_identity':e['source_identity'],'profile':'REF32x8_L100','geometry':e['geometry'],'observer':e['observer']},sort_keys=True)
  if key not in strata:strata[key]={'source_identity':e['source_identity'],'profile':'REF32x8_L100','geometry':e['geometry'],'observer':e['observer'],'endpoint_cohorts':[],'modes':collections.Counter()}
  strata[key]['endpoint_cohorts'].append(e['cohort']);strata[key]['modes'][e['mode']]+=1
out={'schema':'EP_OBSERVATION_WORKLOAD_FEATURES_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_snapshot_utc':A['utc'],'coverage_snapshot_utc':CV['utc'],'counts':{'rows':len(rows),'ordinary96':96,'main35':35,'main42':42,'unresolved_slots':7,'accepted_endpoints':len(E),'all_matched_pairs':len(A['pairs']),'reference_endpoint_count':sum(len(r['reference_endpoints']) for r in rows),'reused_W_endpoints':len(WM),'reused_V_endpoints':len(VM),'reused_MSHR_endpoints':reused_MSHR_count,'new_MSHR_small_metadata_projections':len(newM),'reused_RO_markdown_endpoints':len(RO),'new_small_bundle_projections':len(late)},'reference_source_observer_strata':list(strata.values()),'coverage_counts':CV['counts'],'identity_join':'INPUT_SHA_AND_COHORT_AND_ACCEPTED_VALIDATION_SHA_EXACT; no name joins; ordered commandlist carried by spec_ref and semantic_population_digest','measurement_contract_ref':READS[str(O/'MEASUREMENT_CONTRACT.md')],'NI_matrix_ref':READS[str(O/'NI_MATRIX.md')],'source_refs':list(READS.values()),'historical_reuse':hist,'rows':rows,'new_models':0,'trace_body_reads':0,'raw_log_reads':0,'source_changes':0,'registry_writes':0,'git_writes':0,'rate_boundaries':'Only ROmerge/acceptedRO and WBUF area/sliceTicks computed with explicit matched populations. MS/FT incidence and V response/query rates UNKNOWN. No additive overlapping stall cycle claim.'}
files=[dump('WORKLOAD_FEATURE_AND_OPPORTUNITY.json',out),csvout('WORKLOAD_FEATURE_AND_OPPORTUNITY.csv',rows),csvout('WORKLOAD_FEATURE_COMPACT.csv',compact),csvout('METRIC_GAPS_BY_INPUT.csv',gaps),dump('HISTORICAL_REUSE_IDENTITY_AUDIT.json',{'scope':'Existing small authority documents and named asset indices only; no filesystem-wide search','rows':hist,'new_models':0,'trace_scans':0}),dump('LATE_REFERENCE_SMALL_BUNDLE_PROJECTION.json',{'rows':list(late.values()),'no_raw_or_trace':True}),dump('NEW_REFERENCE_MSHR_PROJECTION.json',{'rows':list(newM.values()),'reference_source_observer_strata':list(strata.values()),'reused_MSHR_endpoints':reused_MSHR_count,'new_MSHR_endpoint_projections':len(newM),'no_raw_or_trace':True})]
text='''# Observation-driven feature reuse and scientific boundary\n\nThe table covers all 96 deduplicated ordinary inputs plus seven unresolved representative slots. Membership projections close exactly to 35 frozen representatives and 42 program slots. Accepted evidence is joined by full input SHA, cohort and accepted validation SHA; same program names do not join different inputs. The inherited closure qualification axes remain as-of records, not new scientific launch grants.\n\nW evidence demonstrates copying and independent head pressure, V demonstrates actual finite-directory response service, M demonstrates live RO merge separately from ordinary MSHR pressure, and T has real accepted alternative-geometry detach witnesses. None of these isolated counts establishes an independent speedup. Scan is an essential W-pressure negative-performance control; Stencil, 3MM and GEMM are stronger actual-V-service positive-performance candidates. FWT remains legal S/WV: no RO-F substitution. Vector4M and Vector6M remain separate inputs.\n\n## Prioritized observations\n\n1. W: eliminate measured copying or reclaim WB data space only when that resource is actually pressured. Request-retry observations and unique blocked heads differ greatly. MS and FT request classes are not proven equal, so exact WB demand incidence remains UNKNOWN. WBUF occupancy uses area/summed sampled slice ticks, not a mean of slice quantiles.\n2. V: actual response counts are selective across workloads and do not define a victim hit rate, a capacity curve, or avoided lower reads. Retention slot-cycles are occupancy area, not lifetime. The most useful missing distribution is service/reclaim age stratified by retained object kind, needed to choose a small retention policy.\n3. M/T: accepted live-transaction merge does not prove strict ingress-before-ready repeat. Ordinary and RO peaks cannot be added to infer simultaneous distinct-address demand. T needs the same request, same target set and same clock instant jointly full with a structural candidate; S runtime RO metrics are N/A. Actual detach is not T independent gain.\n\n## Historical reuse first\n\nMotivation final10 DATA/SEMANTICS acceptance and Streaming prefinal evidence already exist. The exact small CSV/manifest locator and current-input/ordered-commandlist match were not recovered from the named authority documents and small indices. They remain IDENTITY_UNRESOLVED. Do not rescan huge Trace or turn approximate old review values into fresh measurements. Required recovery objects are exact input manifests, ordered kernel/commandlist binding, aggregation manifest and the existing CSV; Streaming additionally needs final recency-tie fix/delta evidence. These source families are not Source78.\n\n## Minimal collection decision\n\nNo new full application is authorized. First reuse the attached endpoint projections and any still-unprojected accepted compact bundle fields. If choosing W/V policy genuinely requires new data, prioritize WB stage/age and retained-entry first-service/reclaim age over a universal detailed trace. Add ingress only if the causal question requires original arrival rather than first-head. A legal WV FWT validates its hooks; S does not cover WV or F. New source/ELF, CPU cases and per-actually-enabled-mode OFF/ON NI must be separately listed. No fixed 4+1 or four-candidate budget is assumed.\n\n## Actual execution\n\nThis analysis reads small JSON/CSV/Markdown evidence only; the few late reference bundle projections are existing accepted metadata. Zero model starts, Trace/body reads, raw-log scans, Core changes, registry/controller changes or Git writes. No new CPU protocol test or application NI was executed. Missing values are null/status strings, never padded with zero. Scientific output numerical correctness and original complete capture remain UNKNOWN.\n'''
text+='\n## Exact-input discriminating examples\n\n|Input prefix / program|S-over-F or S-over-WV|S copy-read + copy-write ops|S WB_DATA_SPACE distinct first-block UID|Actual F/WV V responses|\n|---|---:|---:|---:|---:|\n'
for name in ['stencil','3MM','GEMM','fastWalshTransform','scan','convolutionSeparable']:
 for r in rows:
  if r['program']!=name or not r['reference_performance']:continue
  s=next((e for e in r['reference_endpoints'] if e['mode']=='S'),None)
  if not s:continue
  for p in r['reference_performance']:
   t=next(e for e in r['reference_endpoints'] if e['mode']==p['treatment']);w=s['W'];copy=w.get('logical_copy_reads',0)+w.get('logical_copy_writes',0);space=w.get('head_reasons',{}).get('WB_DATA_SPACE',{}).get('distinct_requests_first_block','UNKNOWN');vs=t['V'].get('metrics',{}).get('read_responses','UNKNOWN')
   text+=f"|{r['input_identity_sha256'][:8]} / {name} ({p['treatment']})|{p['speedup_S_over_treatment']:.6f}|{copy}|{space}|{vs}|\n"
text+='\nThese count populations differ: copy ops, distinct blocked heads and completed Victim responses must not be directly subtracted or used as one another\'s denominator. All rows use REF32x8_L100 / Source78. F/WV payload ownership is pooled; its WB-role peak is not an overflow of S\'s fixed WBUF16.\n'
(R/'OBSERVATION_AND_PRIORITY.md').write_text(text)
files.append({'path':str(R/'OBSERVATION_AND_PRIORITY.md'),'bytes':(R/'OBSERVATION_AND_PRIORITY.md').stat().st_size,'sha256':hashlib.sha256((R/'OBSERVATION_AND_PRIORITY.md').read_bytes()).hexdigest()})
print(json.dumps({'status':'PASS','counts':out['counts'],'files':files,'elapsed_seconds':time.time()-START,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
dump('DELIVERY_MANIFEST.json',{'schema':'EP_OBSERVATION_AGENT_A_DELIVERY_V1','utc':out['utc'],'files':files,'source_refs':list(READS.values()),'counts':out['counts'],'actual_execution':{'elapsed_seconds':time.time()-START,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'models':0,'Trace_reads':0,'raw_reads':0,'registry_writes':0,'Git_writes':0}})
