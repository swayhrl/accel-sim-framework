import collections,csv,datetime,gzip,hashlib,json,re,subprocess
from pathlib import Path

BASE=Path('/root/share/mnt164/huangrulin/host174_storage_recovery')
O=BASE/'dtc_workload_headroom_opportunity_audit_20261106_v1/agents/A_opportunity_records_v1'
A2=BASE/'dtc_stage_iia_remaining48_execution_20261104_v1'
F=BASE/'dtc_stage_iia_first16_execution_20261104_v1'
S=BASE/'dtc_perf_first_parallel_exploration_20261104_v1'
R1=BASE/'dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1'
I=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
STAGEI='361fa6fa0700825bb9cda43e25b9fd1f60e0b262'
W=A2/'execution-worktree'
PINS={};CHECKS=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p);r={'path':str(p),'sha256':sha(p)};PINS[str(p)]=r;return r
def load(p):ref(p);return json.loads(Path(p).read_bytes())
def put(p,d):
 p=O/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def gzput(p,d):
 p=O/p;p.parent.mkdir(parents=True,exist_ok=True)
 with gzip.GzipFile(str(p),'wb',mtime=0)as f:f.write((json.dumps(d,separators=(',',':'),ensure_ascii=False)+'\n').encode())
def ck(n,v,detail=None):
 CHECKS.append({'check':n,'pass':bool(v),'detail':detail})
 if not v:raise AssertionError((n,detail))
def git(*args):return subprocess.check_output(['git','-c','safe.directory='+str(W),'-C',str(W),*args])
def capture_provider(p,label,required):
 d=load(p)
 for k,v in required.items():ck('provider_gate',d.get(k)==v,(label,k))
 for r in d['files']:ck('provider_file_SHA',sha(r['path'])==r['sha256'],(label,r['name']))
 ck('provider_manifest_SHA',sha(d['manifest']['path'])==d['manifest']['sha256'],label)
 put(Path('captures')/(label+'_PROVIDER.fixed.json'),d)
 return d
def provider_member(p,name):return next(x['path']for x in p['files']if x['name']==name)
def source_result(p,expected_sha=None):
 ck('RESULT_exists',Path(p).exists(),str(p));actual=sha(p)
 if expected_sha:ck('RESULT_exact_SHA',actual==expected_sha,str(p))
 return load(p),{'path':str(p),'sha256':actual}
def classify(baseline,candidate):
 if baseline is None or candidate is None:return 'UNAVAILABLE'
 return 'POSITIVE'if candidate<baseline else'NEGATIVE'if candidate>baseline else'EXACT_ZERO'

GAUGES={'DTC_L1_lower_outstanding','DTC_L1_pib_occupancy','DTC_L1_oo_active_refs','DTC_L1_oo_inflight_current','DTC_L1_oo_physical_allocated','DTC_L1_oo_pib_occupancy'}
REQUESTED=['DTC_L1_oo_valid_hits','DTC_L1_oo_pending_hits','DTC_L1_oo_new_misses','DTC_L1_oo_tag_evictions','DTC_L1_oo_lower_created','DTC_L1_oo_lower_issued','DTC_L1_oo_lower_responses','DTC_L1_oo_ready_but_writeback_blocked_cycles','DTC_L1_oo_lower_create_queue_full_stalls','DTC_L1_oo_immediate_reclaims','DTC_L1_oo_deferred_reclaims','DTC_L1_oo_final_ref_reclaims','DTC_L1_oo_out_of_order_retires','DTC_L1_oo_retire_count','DTC_L1_pib_full_events','DTC_L1_tag_conflicts','gpu_stall_dramfull','L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_reservation_fails']
def metric_projection(metrics,traffic,totals=None):
 m=dict(metrics or {});m.update(totals or {})
 events={k:m[k]for k in REQUESTED if k in m and k not in GAUGES}
 services={k:v for k,v in m.items()if k.startswith('DTC_SERVICE_V1_')}
 gauges={k:m[k]for k in GAUGES if k in m}
 peaks={k:v for k,v in m.items()if k.startswith('DTC_')and 'peak'in k}
 t=traffic or {};whole={k:t[k]for k in ['DRAM_atom_bytes','DRAM_issued_read_atoms','DRAM_issued_write_atoms','DRAM_read_payload_bytes','DRAM_write_payload_bytes','L2_accepted_read_32B_sectors','L2_read_payload_bytes']if k in t}
 for k in ['DRAM_read_atoms32B','DRAM_write_atoms32B','DRAM_controller_n_req','DRAM_issued_read_atoms32B','DRAM_issued_write_atoms32B','L2_GLOBAL_read_accepted_sectors','L2_GLOBAL_read_miss_sectors']:
  if k in m:whole[k]=m[k]
 ctrl=t.get('DRAM_controllers',{})
 if ctrl and all('n_req'in x for x in ctrl.values()):whole['DRAM_controller_request_objects']=sum(x['n_req']for x in ctrl.values())
 return {'whole_replay_selected_cumulative':events,'whole_replay_traffic':whole,'service_cumulative_integrals_item_sums_and_counts':services,'terminal_gauges_not_pressure_history':gauges,'running_peaks_not_perkernel':peaks,'unavailable_requested_fields':[k for k in REQUESTED if k not in m],'per_kernel_traffic':'UNAVAILABLE_FROM_FINAL_STRICT_ENDPOINT; existing reviewed raw-derived phase references may supply explicit endpoints','latency':'Diagnostic means retain original sampling windows; missing not zero. No new mean computed.'}

def proof_summary(d,rr,program,digest,profile,cell):
 p=d.get('proof',{});ks=p.get('kernels',[])
 if ks:
  ck('kernel_ordinal', [k['ordinal']for k in ks]==list(range(1,len(ks)+1)),rr['path'])
  ck('kernel_sum_accepted',sum(k['cycles']for k in ks)==d['cycles'],rr['path'])
  ck('proof_input_digest',p.get('input_digest')==digest,rr['path'])
 return {'program':program,'input_digest':digest,'design':cell,'comparison_profile':profile,'RESULT':rr,'actual_RESULT_cohort':d.get('cohort'),'actual_RESULT_profile':d.get('profile'),'actual_proof_profile':p.get('downstream_profile'),'actual_scientific_role':d.get('scientific_role'),'state':d.get('state'),'uuid':d.get('uuid'),'cycles':d.get('cycles'),'core_commit':p.get('core_commit'),'framework_commit':p.get('framework_commit'),'binary_sha256':p.get('binary_sha256'),'kernel_count':len(ks),'counter_evidence':metric_projection(p.get('metrics'),p.get('traffic'))}

assert not(O/'MANIFEST.json').exists(),'Frozen packet is immutable'
initial=load(O/'CORE32_INITIAL_INPUT_AND_SIXCELL_DATA.json');programs=initial['programs'];ids={x['input_digest']for x in programs};ck('fixed32',len(ids)==32)
auth=load(O/'AUTHORITY_RELATIONSHIP.initial.json')
for k,c in auth.items():
 if len(c)==40:ck('authority_commit_exists',git('cat-file','-t',c).decode().strip()=='commit',k)
pp=capture_provider(A2/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json','StageII_final',{'source_qualified':True,'all_registered48_terminal_verified':True})
sp=capture_provider(S/'agents/B_perf_results_consumer_v3/PUBLICATION_PROVIDER.json','Structure_final',{'all32_nonTag_closed_verified':True,'all32_candidates_accounted_verified':True})
rp=capture_provider(R1/'agents/B_results_v1/driver_packet_v1/runs/root_live_v2/PUBLICATION_PROVIDER.json','R1_final',{'runtime_source_qualified':True,'all16_actual_scientific_closed':True})
structure=load(provider_member(sp,'SNAPSHOT.json'));r1=load(provider_member(rp,'SNAPSHOT.json'));ck('R1_16accepted',len(r1['rows'])==16 and all(x['accepted']for x in r1['rows']))
put('captures/Structure_ROWS_SOURCE.json',{'provider_manifest':sp['manifest'],'observed_utc':structure['observed_utc'],'rows':[{k:v for k,v in x.items()if k not in ['actual_effective_options','metrics_mixed_scope','traffic','archive_witness']}for x in structure['rows']]})
matrix=load(I/'control/MATRIX_CURRENT.json');intake=load(I/'control/WORKLOAD_INTAKE.json');unresolved=load(I/'control/UNRESOLVED7.json');intakes={r['input_digest']:r for r in intake['rows']}
ck('35_frozen',len(intakes)==35 and len(matrix['points'])==350)
stageI=[];stageIcounts=collections.Counter();result_cache={}
for point in matrix['points']:
 q=I/'analysis'/(point['cohort']+'.RESULT.json');d=None;rr=None;accepted=False
 if q.exists():
  d,rr=source_result(q);accepted=d['state']in['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START'];stageIcounts['ACCEPTED'if accepted else'ARCHIVED_NEGATIVE']+=1
  if accepted:ck('accepted_positive_cycles',isinstance(d['cycles'],int)and d['cycles']>0,point['cohort'])
  result_cache[point['cohort']]=(d,rr)
 else:
  ck('only_known_scan_engineering_absence',point['cohort']=='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1',point['cohort']);stageIcounts['ENGINEERING_NEGATIVE']+=1
  e=next((BASE/'dtc_l2_mlp_full_workload_exploration_v1/engineering_negative_evidence_v1'/point['cohort']).rglob('ENGINEERING_TERMINAL_NEGATIVE.json'));eng=load(e);rr=ref(e)
 row={**point,'source_family':'STAGEI_ORIGINAL_350','accepted':accepted,'cycles':d['cycles']if accepted else None,'state':d['state']if d else'PRESERVED_ENGINEERING_NEGATIVE_NO_RESULT','original_RESULT_or_engineering_evidence':rr,'uuid':d.get('uuid')if d else eng.get('uuid'),'original_negative_not_replaced':not accepted}
 if accepted:
  row['proof_evidence']=proof_summary(d,rr,point['program'],point['input_digest'],point['profile'],point['cell'])
 stageI.append(row)
ck('original350_identity_counts',dict(stageIcounts)=={'ACCEPTED':331,'ARCHIVED_NEGATIVE':18,'ENGINEERING_NEGATIVE':1},dict(stageIcounts))
put('STAGEI_ORIGINAL350_ROLE_PRESERVED_INDEX.json',{'authority':STAGEI,'counts':dict(stageIcounts),'independent_named_view336':'SEPARATE_VIEW_NOT_SUBSTITUTED_OR_USED_TO_FILL_ORIGINAL_NEGATIVES','rows':stageI})

# Reuse the closed final24 derived endpoints and first8 reviewed packages, never raw.
B=next((A2/'agents/B_final24_consumption_preparation_v1/updates').iterdir());ref(B/'MANIFEST.json')
metadata=collections.defaultdict(dict);phases=collections.defaultdict(list);cyclepos=collections.defaultdict(list)
for prefix,target in [('source_metadata',metadata),('phase_summaries',phases),('six_cell_kernel_cycles',cyclepos)]:
 for f in sorted((B/'public/details').glob(prefix+'.*.gz')):
  ref(f)
  with gzip.open(f,'rt')as stream:
   for line in stream:
    r=json.loads(line)
    if prefix=='source_metadata':metadata[r['input_digest']][r['cell']+'_'+r['profile']]=r
    else:target[r['input_digest']].append(r)
first8cycle=load(A2/'agents/B_first8_sixcell_kernel_cycles_companion_20261105_v1/FIRST8_SIX_CELL_KERNEL_CYCLES.json')
for r in first8cycle['matched_kernel_cycles']:cyclepos[r['input_digest']].append(r)
first8authority=load(A2/'agents/B_first8_sixcell_kernel_cycles_companion_20261105_v1/REUSED_AUTHORITY_AND_SCOPE.json')
constraints=load(S/'agents/A_structure_config_v1/CONSTRAINTS_AND_COUPLINGS.json')
put('STRUCTURE_CONSTRAINTS_AND_COUPLINGS_REFERENCE.json',{'source':ref(S/'agents/A_structure_config_v1/CONSTRAINTS_AND_COUPLINGS.json'),'details':constraints})
old8paths={'ATAX':F/'agents/B_atax_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','MVT':F/'agents/B_mvt_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','BICG':F/'agents/B_bicg_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','vectorAdd':F/'agents/B_vectoradd_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','scan':F/'agents/B_scan_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','convolutionSeparable':F/'agents/A_convseparable_three_profiles_v1/SIX_CLOSED_SOURCE_DATA.json','GEMM':F/'agents/B_gemm_2d_f128_controls_v1/GEMM/MATCHED_FOUR_SOURCE_DATA.json','2DCONV':F/'agents/B_gemm_2d_f128_controls_v1/2DCONV/MATCHED_FOUR_SOURCE_DATA.json'}
old8={n:load(p)for n,p in old8paths.items()}
uploads=load(A2/'agents/A_host_upload_scope_inventory_v1/CORE32_HTOD_INVENTORY.json');uploadmap={r['input_digest']:r for r in uploads['rows']}
ref(A2/'agents/A_host_upload_scope_inventory_v1/P0_EFFECTIVE_OPTIONS64.json')
cat=load(A2/'agents/B_closed_samples_analysis_v1/CONSUMED_COUNTER_CATALOG.json');put('COUNTER_SEMANTICS_REFERENCE.json',{'original_scoped_catalog':ref(A2/'agents/B_closed_samples_analysis_v1/CONSUMED_COUNTER_CATALOG.json'),'items':cat['items'],'further_scope':'Final24 explicit single-stream metadata and checked source endpoints, not automatic promotion of first8 limits; baseline/structure/R1 per-kernel traffic remains unavailable when only strict final endpoint exists.'})
put('FIRST8_AUTHORITY_FORWARD_INDEX.json',first8authority)

common_limits=[
 'Whole registered trace timing only; capture-source/ELF/macros and numerical correctness are not newly certified.',
 'Declared HtoD order is not live hook timing, changed values or overlap proof; prefill1/flushL1=1/flushL2=0/OO-source-event-invalidate0. Coherence remains a separate question.',
 'L2 GLOBAL reads/misses are32B sectors, DRAM issued reads/writes32B atoms; request objects differ. Write misses may not issue DRAM reads. Zero DRAM does not prove compute-bound or cold/warm state.',
 'Retry/admission counts are not critical-path time or occupancy histories. Terminal gauges and running peaks are not phase work. Service sample/item means are not active-SM peaks or critical-path latency.',
 'MRQ spans request construction to bank assignment, excludes later service. Diagnostic latency means retain conditional sampling/tail windows. Missing is not zero.',
 'CH common PIB256 and DH OO128 are distinct active structures; generic DH PIB8 is inactive. Physical slots do not increase searchable512Tag. No equal-area or hardware PPA claim.',
 'OO PIB192 also enlarges the bounded lower-create candidate queue128→192; finite create/inject widths remain1. TagService8 is a configured grant ceiling, not proven integrated8-request/cycle throughput. Both1024Tag/640physical candidates remain CPU-progress-negative safetyHOLD, not simulated performance.',
 'FR-FCFS capacity and shared credits change together; structure/R1 use downstreamP0. source families are not concatenated into one uniform configuration.',
 'Observed best accepted cycles are exploratory references with selected configuration identity, not theoretical upper bounds or a per-program-best suite GM.'
]
special={
 'MVT':('Physical-lifetime interaction has observed positive evidence; compare K1 rather than using Tag eviction count alone. R1 and physical single factors test whether the observed response survives PIB enlargement.','If extra physical capacity changes misses/lower traffic but does not consistently shorten K1, a simple miss-volume critical-path account is insufficient.'),
 'BICG':('Physical enlargement retains an observed negative control; K2 response must remain separate from K1. More physical capacity or fewer OO misses alone does not guarantee throughput.','Compare same-contract K2 lower/L2/DRAM volume and finite-service counters; stable or lower misses with slower K2 falsifies a monotone miss-count explanation.'),
 'ATAX':('F-relative improvement must be decomposed into CH regression versus DH own improvement; preserve both serial kernels and absolute matched R.','A positive I with R<=1 does not show DH surpasses CH; use actual own-design kernel deltas and preserve opposite CH response.'),
 'convolutionSeparable':('Rows and Columns both respond to coupled downstream expansion. Compare shared CH benefit with the smaller additional DH benefit; whole DH speedup is not DTC-exclusive.','Large speedup with near-constant read traffic argues against volume reduction alone; retry direction can disagree within a kernel.'),
 '2DCONV':('Use CH downstream zero response and DH response as controls; physical-only and physical×PIB changes are distinct interventions.','An observed PIB/combination regression must remain even if physical-only is exactly zero. No unreviewed F256 counter mechanism is implied.'),
 'GEMM':('Retain exact F-zero response and observed structural responses as controls under the actual prefilled replay.','Zero DRAM exposure only limits this replay test of the FR window; it does not establish compute-bound execution or a universal headroom ceiling.'),
 '3MM':('Retain zero downstream response under current trace/preload policy, independent from historical Hash studies.','Candidate source copies uninitialized E/F/G and uses +=; capture binding/numerical correctness is unproved. Do not infer historical numerical error or repair the input.'),
 'vectorAdd':('Streaming-like candidate source is a negative/zero response control; all measured regressions stay in the opportunity record.','No locality/port/PIB improvement is presumed from source form; only actual accepted cycle/counter changes can support it.'),
 'scan':('Use the actual33-kernel ordered sequence, not11 assumed identical triplets. Preserve V1 monitor-cadence negative identities separately from acceptedR1.','V1 structure failure is not a negative performance value or family-safety proof; R1 cannot fill single-factor J terms that never accepted.'),
 'fastWalshTransform':('CH/DH opposite small F responses remain a counterexample to monotone retry/miss reasoning. K6 is a read-active print interval.','Read-active does not prove cold-start/compulsory misses or request-origin membership; prefill and later intervals remain explicit.'),
 'myocyte':('Retain5993 actual kernels and interkernel uploads as a semantic/coherence control before architecture claims.','5993=13×461 does not prove accepted integration steps, solver attempts or full application; phase_epoch is not kernelordinal.'),
 'srad_v1':('Preserve502 actual kernels and seven disjoint source-candidate phases, including450CTA versus1CTA reduce passes.','Registered sequence and tiny13-read-atom observations do not prove native full-app completeness, bank balance or numerical freshness.'),
 '3DCONV':('Preserve254 actual instances and small opposite design responses; no scalar loop index is assigned from ordinal.','Source scalar_i/capture binding remains unknown; small aggregate counter shifts do not establish critical-path cause.'),
 'mri-q':('Small DH gain and CH zero response provide a low-response control; preserve interkernel upload boundary.','Reduced misses do not establish reduced full DRAM-service or application critical-path latency.'),
 'GESUMMV':('One closed kernel exposes nonmonotone F response: DH-F128 gains while F256 regresses; source traffic and retry direction must be considered separately.','Fewer OO misses/retries can coexist with slower execution; no isolated causal bottleneck follows from endpoint totals.')
}
flat=[];records=[];scope_counts=collections.Counter()
for p in programs:
 name=p['program'];digest=p['input_digest'];baseDH=p['six_source_cells']['DH_P0']['cycles'];baseCH=p['six_source_cells']['CH_P0']['cycles'];six=[];source_kernel_sequences={}
 for slot,s in p['six_source_cells'].items():
  d,rr=source_result(s['source_RESULT_path'],s['source_RESULT_sha256']);x=proof_summary(d,rr,name,digest,slot.split('_')[1],slot.split('_')[0]);x['legal_source_identity']=s;source_kernel_sequences[slot]=d['proof']['kernels']
  if digest in metadata and slot in metadata[digest]:
   m=metadata[digest][slot];ck('derived_metadata_RESULT',m['RESULT_sha256']==rr['sha256'],(name,slot));x['reviewed_raw_derived_cumulative']=metric_projection({},None,m['totals']);x['reviewed_final24_metadata_scope']=m['scope']
  six.append(x)
 facts=[]
 if name in old8:
  data=old8[name];sources=data.get('six_closed_sources',data.get('four_closed_sources',[]));facts={'original_source':ref(old8paths[name]),'raw_derived_sources':[{k:r[k]for k in ['cell','profile','RESULT_path','RESULT_sha256','cycles','totals']if k in r}for r in sources],'within_design_derived_changes':data.get('within_design_changes'),'original_missingness_rule':data.get('missingness_rule'),'F256_counter_scope':'NOT_COVERED_BY_F128_CONTROL_PACKET'if name in ['GEMM','2DCONV']else'REUSED_SIX_SOURCE_SCOPE'}
 sf=[]
 for row in stageI:
  if row['input_digest']==digest and row['cell']=='DH'and row['profile']!='P0':
   sf.append({**row,'DH_self_speedup':baseDH/row['cycles']if row['accepted']else None,'performance_direction':classify(baseDH,row['cycles'])if row['accepted']else'NONPERFORMANCE','matching_CH_nonP0':'AVAILABLE_ONLY_FOR_F128_F256_FROM_STAGEII'if row['profile'].startswith('F')else'NOT_MEASURED_DO_NOT_INFER_FAIR_CH_RELATIVE_GAIN'})
 struct=[]
 for r in structure['rows']:
  if r['input_digest']!=digest:continue
  z={k:r.get(k)for k in ['program','input_digest','variant','status','accepted','cycles','uuid','cohort','source_scientific_role','source_union_scope','source_validated_union_authorized','source_RESULT','STRICT','native_EXIT','S_DH','Rnew','I','reason']};z['source_family']='PERF_FIRST_STRUCTURE_FIXED8';z['performance_direction']=classify(baseDH,r['cycles'])if r['accepted']else'NONPERFORMANCE';z['downstream_profile']='P0';
  if r['accepted']:
   d,rr=source_result(r['source_RESULT']['path'],r['source_RESULT']['sha256']);z['counter_evidence']=metric_projection(r.get('metrics_mixed_scope'),r.get('traffic'));z['kernel_cycles']=r.get('kernels')
  struct.append(z)
 combos=[]
 for r in r1['rows']:
  if r['input_digest']!=digest:continue
  d,rr=source_result(r['source_RESULT']['path'],r['source_RESULT']['sha256']);z={k:r.get(k)for k in ['program','input_digest','variant','status','accepted','cycles','uuid','cohort','source_scientific_role','source_union_scope','source_validated_union_authorized','source_RESULT','STRICT','S_combo','R_combo','I','J','J_status','S_PIB','S_physical','V1_PIB','V1_physical','kernel_cycle_comparisons']};z['source_family']='R1_COMBINATION_FIXED8';z['performance_direction']=classify(baseDH,r['cycles']);z['counter_evidence']=metric_projection(r.get('metrics_mixed_scope'),r.get('traffic'));z['kernel_cycles']=r.get('kernels');combos.append(z)
 eligible=[{'family':'STAGEII_DH','variant':x['comparison_profile'],'cycles':x['cycles'],'source':x['RESULT']}for x in six if x['design']=='DH']+ [{'family':'STAGEI_SINGLE_FACTOR','variant':x['profile'],'cycles':x['cycles'],'source':x['original_RESULT_or_engineering_evidence']}for x in sf if x['accepted']]+[{'family':x['source_family'],'variant':x['variant'],'cycles':x['cycles'],'source':x['source_RESULT']}for x in struct+combos if x['accepted']]
 minimum=min(x['cycles']for x in eligible);best=[x for x in eligible if x['cycles']==minimum]
 hyp,falsify=special.get(name,('Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.','No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.'))
 limits=common_limits.copy()
 if name in ['myocyte','srad_v1','3DCONV','3MM','fastWalshTransform','scan']:limits.append(special[name][1])
 normalized=[]
 reference_signature=[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA'])for x in source_kernel_sequences['DH_P0']]
 for slot,ks in source_kernel_sequences.items():ck('sixcell_shape_instruction_CTA',[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA'])for x in ks]==reference_signature,(name,slot))
 old_by_ordinal={x.get('ordinal',x.get('trace_ordinal')):x for x in cyclepos[digest]}
 for ordinal in range(1,len(source_kernel_sequences['DH_P0'])+1):
  refkernel=source_kernel_sequences['DH_P0'][ordinal-1]
  values={slot:ks[ordinal-1]['cycles']for slot,ks in source_kernel_sequences.items()}
  old=old_by_ordinal[ordinal]
  ck('derived_cycles_vs_proof',old['cycles']==values,(name,ordinal))
  normalized.append({'ordinal':ordinal,'kernel':refkernel['kernel'],'active_instructions':refkernel['active_instructions'],'cumulative_CTA':refkernel['cumulative_CTA'],'cycles':values})
 kfile=Path('kernel_cycles')/(digest+'.json.gz');gzput(kfile,{'program':name,'input_digest':digest,'source_family':'STAGEII_FIXED_SIX_CELLS','source_identity':p['six_source_cells'],'positions':normalized,'source_proof_kernels_by_cell':source_kernel_sequences,'no_counter_or_numeric_promotion':True})
 rec={'schema':'DTC_WORKLOAD_HEADROOM_OPPORTUNITY_RECORD_V1','program':name,'suite':p['suite'],'input_digest':digest,'population_role':'FIXED_CORE32_NOT_35_OR_8','authority':auth,'capture_identity':{k:intakes[digest].get(k)for k in ['program_id','input_binding_path','input_binding_sha256','trace_entry','commandlist_sha256','expected','identity_freeze','source_scope','memory_instruction_paths','historical_repair_evidence']},'CH_DH_P0_F_six_cells':six,'matched_F_metrics':p['metrics_by_profile'],'stageI_original_single_factor_DH':sf,'structure_fixed8':struct,'R1_combinations_fixed8':combos,'structure_coverage':'FIXED8_MEASURED'if struct else'NOT_MEASURED_OUTSIDE_FIXED8','R1_coverage':'FIXED8_MEASURED'if combos else'NOT_MEASURED_OUTSIDE_FIXED8','kernel_cycle_detail':{'path':str(kfile),'sha256':sha(O/kfile),'positions':len(cyclepos[digest]),'source_kernel_rows':len(cyclepos[digest])*6},'closed_raw_derived_counter_reference':facts,'registered_phase_summaries':phases[digest]if digest in phases else'REUSE_FIRST8_SCOPED_REPORT','declared_HtoD_and_source_scope':uploadmap[digest],'opportunity':{'testable_hypothesis':hyp,'falsification_or_limiting_case':falsify,'evidence_class':'OBSERVED_RESPONSE_PLUS_CONDITIONAL_MECHANISM_HYPOTHESIS_NOT_CAUSAL_PROOF','theoretical_upper_bound':'UNKNOWN_NO_ORACLE','next_scientific_starts_authorized_by_this_packet':False},'best_observed_DH_cycles_exploratory_only':{'cycles':minimum,'self_speedup':baseDH/minimum,'tied_observed_sources':best,'not_uniform_configuration_or_GM':True},'mandatory_limits':limits}
 out=Path('records')/(name+'.json');put(out,rec);records.append({'program':name,'suite':p['suite'],'input_digest':digest,'record':str(out),'record_sha256':sha(O/out)})
 for family,values in [('StageII_sixcell',six),('StageI_DH_singlefactor',sf),('Structure',struct),('R1_combo',combos)]:
  for x in values:
   accepted=x.get('accepted',True);prof=x.get('comparison_profile',x.get('profile',x.get('variant')));cell=x.get('design',x.get('cell','DH'));cyc=x.get('cycles')if accepted else None
   flat.append({'program':name,'suite':p['suite'],'input_digest':digest,'family':family,'profile_or_variant':prof,'design':cell,'accepted':accepted,'status':x.get('state',x.get('status')),'cycles':cyc,'DH_self_speedup':baseDH/cyc if accepted and cell=='DH'else None,'direction':classify(baseDH,cyc)if accepted and cell=='DH'else'NOT_DH_PERFORMANCE_COMPARISON','source':json.dumps(x.get('RESULT',x.get('source_RESULT',x.get('original_RESULT_or_engineering_evidence'))),sort_keys=True)});scope_counts[family]+=1
 # Independent light per-program view, all source evidence remains in the JSON.
 lines=[f'# {name}: observed opportunity record','',f'Full input identity `{digest}`; {p["suite"]}; fixed CORE32.','',f'CH-P0 {baseCH:,} cycles; DH-P0 {baseDH:,}. This is an evidence dossier, not a theoretical upper bound or a release for experiments.','','|Source family|Profile|Accepted cycles|DH own speedup|','|---|---|---:|---:|']
 for r in flat:
  if r['input_digest']==digest:lines.append(f"|{r['family']}|{r['design']} {r['profile_or_variant']}|{r['cycles']if r['cycles']is not None else r['status']}|{r['DH_self_speedup']if r['DH_self_speedup']is not None else 'N/A'}|")
 lines+=['',hyp,'',f'Counterexample/boundary: {falsify}','',f'Best observed DH cycles {minimum:,} (self speedup {baseDH/minimum:.9f}) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.','','Kernel-cycle detail: `'+str(kfile)+'`; '+str(len(cyclepos[digest]))+' positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.','','Structure and combination scope: '+rec['structure_coverage']+' / '+rec['R1_coverage']+'.','','Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.']
 (O/'records'/(name+'.md')).write_text('\n'.join(lines)+'\n')

outside={r['input_digest']:r for r in intake['rows']if r['input_digest']not in ids}
put('OUTSIDE_CORE32_IDENTITY_AND_MISSINGNESS.json',{'frozen35_minus_core32':[{'program':r['program'],'input_digest':d,'expected':r['expected'],'input_binding_path':r['input_binding_path'],'input_binding_sha256':r['input_binding_sha256'],'reason':'Excluded from core32 original matched coverage; preserve original failures and supplemental/deferred CH candidacy; no promotion','original_stageI_rows':[x for x in stageI if x['input_digest']==d]}for d,r in outside.items()],'unresolved7':unresolved,'original350_counts':dict(stageIcounts),'independent_named336':'SEPARATE_IDENTITY_VIEW_NOT_IMPORTED_AS_ORIGINAL_ACCEPTANCE','historic72_and288':'UNCHANGED_NOT_SUBSTITUTED','root_paper':'EnglishLaTeXv0.23 unchanged'})
put('OPPORTUNITY_RECORD_INDEX.json',{'authority':auth,'records':records,'fixed_programs':32,'same_input_full_SHA_join':True,'source_family_cell_counts':dict(scope_counts),'best_observed_GM':'PROHIBITED_NOT_COMPUTED','theoretical_bound':'UNKNOWN','starts':0,'core_or_runtime_changes':0})
with(O/'OPPORTUNITY_MATRIX.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
put('OPPORTUNITY_MATRIX.json',{'rows':flat,'same_input_full_SHA_only':True,'no_best_GM':True})
put('SOURCE_PINS.json',list(PINS.values()))
put('CPU_VALIDATION.json',{'checks_passed':len(CHECKS),'checks':CHECKS,'large_archive_audits_rerun':0,'raw_logs_read':0,'models_GPU_or_scientific_runtime_actions':0,'original350_counts':dict(stageIcounts),'matrix_family_counts':dict(scope_counts),'input_counts':{'core32':32,'outside_core32_frozen':len(outside),'unresolved':len(unresolved['rows'])}})
print(json.dumps({'output':str(O),'records':len(records),'matrix_rows':len(flat),'checks':len(CHECKS),'stageI_counts':dict(stageIcounts),'family_counts':dict(scope_counts)}))
