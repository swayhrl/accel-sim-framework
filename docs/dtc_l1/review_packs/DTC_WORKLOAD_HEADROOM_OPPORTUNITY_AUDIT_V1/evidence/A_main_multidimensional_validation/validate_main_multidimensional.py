import collections,csv,datetime,gzip,hashlib,json,math
from pathlib import Path

R=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_workload_headroom_opportunity_audit_20261106_v1')
A=R/'agents/A_opportunity_records_v1'
P=R/'review-worktree/docs/dtc_l1/review_packs/DTC_WORKLOAD_HEADROOM_OPPORTUNITY_AUDIT_V1'
O=R/'agents/A_main_multidimensional_validation_v1'
checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(n,v,detail=None):
 checks.append({'check':n,'pass':bool(v),'detail':detail})
 if not v:raise AssertionError((n,detail))
def eqfloat(x,y):return x==y or isinstance(x,(int,float))and isinstance(y,(int,float))and math.isclose(x,y,rel_tol=1e-14,abs_tol=1e-14)
def put(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def direction(p0,c):return'POSITIVE'if c<p0 else'NEGATIVE'if c>p0 else'EXACT_ZERO'

O.mkdir(exist_ok=False)
ck('Root_fixed_manifest_pin',sha(P/'MAIN_SUPPLEMENT_MANIFEST.json')=='fd0d1113d6e1540214247563817b1c2b2083ae8f1ad43a739dc7b6fd2c1b7ed3')
mf=json.loads((P/'MAIN_SUPPLEMENT_MANIFEST.json').read_text())
for r in mf['files']:ck('Root_member_SHA',sha(P/r['path'])==r['sha256'],r['path'])
ck('A_fixed_manifest_pin',sha(A/'MANIFEST.json')=='6ac899ecf8fec1b9b7559a14399c028e173b68b9c1b547d809f4e237fedfea41')
source=json.loads((A/'OPPORTUNITY_RECORD_INDEX.json').read_text());derived=json.loads((P/'WORKLOAD_OPPORTUNITY_CLASSIFICATION_MULTIDIMENSIONAL.json').read_text());main={r['input_digest']:r for r in derived['records']}
ck('complete_same32_population',len(main)==32 and set(main)=={r['input_digest']for r in source['records']})
categories=collections.Counter();gain=[];nogain=[];digestrows=[]
for entry in source['records']:
 path=A/entry['record'];ck('A_record_pin',sha(path)==entry['record_sha256'],entry['program']);a=json.loads(path.read_text());r=main[a['input_digest']];name=a['program'];p0=next(x for x in a['CH_DH_P0_F_six_cells']if x['design']=='DH'and x['comparison_profile']=='P0');ch0=next(x for x in a['CH_DH_P0_F_six_cells']if x['design']=='CH'and x['comparison_profile']=='P0');base=p0['cycles']
 ck('full_identity',r['program']==name and r['suite']==a['suite']and r['DH_P0']==base and r['CH_P0']==ch0['cycles'],name)
 ck('Root_source_record_exact_bytes',sha(P/r['source_record']['path'])==r['source_record']['sha256']==sha(path),name)
 ds=r['downstream'];expected={x['profile']:x for x in a['stageI_original_single_factor_DH']};observed={x['profile']:x for x in ds['original_factor_rows']};ck('all8_factor_profiles',len(expected)==len(observed)==8 and set(expected)==set(observed),name);d_sign=collections.Counter();d_speeds=[]
 for profile,x in expected.items():
  y=observed[profile];ck('downstream_accepted_status_cycles_source',y['accepted']==x['accepted']and y['status']==x['state']and y['cycles']==x['cycles']and y['source']==x['original_RESULT_or_engineering_evidence'],(name,profile))
  if x['accepted']:
   ck('downstream_self_speedup',eqfloat(y['self_speedup'],base/x['cycles']),(name,profile));d_sign[direction(base,x['cycles'])]+=1;d_speeds.append(base/x['cycles'])
  else:ck('unaccepted_not_performance',y['cycles']is None and y['self_speedup']is None,(name,profile))
 ck('downstream_counts',ds['accepted']==sum(d_sign.values())and ds['missing_or_negative']==8-sum(d_sign.values())and ds['signs']==dict(d_sign),name)
 ck('downstream_range',all(eqfloat(x,y)for x,y in zip(ds['observed_self_speedup_range'],[min(d_speeds),max(d_speeds)])),name)
 ck('matched_F_metrics',ds['matched_F_metrics']==a['matched_F_metrics'],name)
 local=r['local_structure'];l_sign=collections.Counter();localaccepted=0
 for key,original in [('single_factor_rows',a['structure_fixed8']),('R1_rows',a['R1_combinations_fixed8'])]:
  ys={x['variant']:x for x in local[key]};ck('local_all_fixed_rows',set(ys)=={x['variant']for x in original},(name,key))
  for x in original:
   y=ys[x['variant']];ck('local_exact_status_source',y['accepted']==x['accepted']and y['status']==x['status']and y['cycles']==x['cycles']and y['source']==x['source_RESULT'],(name,x['variant']))
   if x['accepted']:
    ck('local_self_speedup',eqfloat(y['self_speedup'],base/x['cycles']),(name,x['variant']));l_sign[direction(base,x['cycles'])]+=1;localaccepted+=1
   else:ck('local_negative_HOLD_null',y['cycles']is None and y['self_speedup']is None,(name,x['variant']))
   if key=='R1_rows':ck('actual_J_missingness',y['J']==x['J'],(name,x['variant']))
 ck('local_scope_counts',local['scope']==a['structure_coverage']and local['accepted']==localaccepted and local['signs']==dict(l_sign),name)
 ck('local_boundaries',local['missing_not_zero']is True and local['Tag_HOLD_is_not_performance']is True and local['PIB192_also_changes_lower_create_queue']is True,name)
 events=p0['counter_evidence']['whole_replay_selected_cumulative']
 for field,v in r['DH_P0_OO_reuse_and_lower_events'].items():
  ck('OO_original_cumulative_event',v['value']==events.get(field),(name,field))
  ck('OO_measured_vs_unavailable',v['status']=='MEASURED_ORIGINAL_CUMULATIVE_EVENT'if field in events else v['value']is None,(name,field))
 ck('traffic_exact_typed_projection',r['DH_P0_traffic']==p0['counter_evidence']['whole_replay_traffic'],name)
 kref=a['kernel_cycle_detail'];ck('kernel_companion_SHA',sha(A/kref['path'])==kref['sha256'],name)
 with gzip.open(A/kref['path'],'rt')as f:kd=json.load(f)
 ks=kd['source_proof_kernels_by_cell']['DH_P0'];ck('phase_all_kernel_count',r['phase']['kernel_count']==len(ks),name);top=sorted(ks,key=lambda x:(-x['cycles'],x['ordinal']))[:3];actual=r['phase']['dominant_duration_kernels'];ck('actual_top3_length',len(actual)==len(top),name)
 for x,y in zip(top,actual):
  ck('actual_top3_identity_cycles',all(y[k]==x[k]for k in ['ordinal','kernel','cycles','active_instructions','cumulative_CTA']),(name,x['ordinal']))
  ck('actual_duration_fraction',eqfloat(y['replay_cycle_fraction'],x['cycles']/base),(name,x['ordinal']))
 ck('phase_NOT_memory_fraction',r['phase']['duration_fraction_is_not_memory_fraction']is True and str(r['phase']['memory_vs_compute_stall_fraction']).startswith('UNKNOWN'),name)
 ck('kernel_ref_export_SHA',sha(P/r['phase']['complete_sixcell_kernel_evidence']['path'])==r['phase']['complete_sixcell_kernel_evidence']['sha256']==kref['sha256'],name)
 ck('memory_path_audit_not_timing',r['phase']['memory_instruction_path_audit']==a['capture_identity']['memory_instruction_paths'],name)
 d_nonzero=bool(d_sign['POSITIVE']or d_sign['NEGATIVE']);l_nonzero=bool(l_sign['POSITIVE']or l_sign['NEGATIVE'])
 category=('DOWNSTREAM_RESPONSE_LOCAL_UNKNOWN'if d_nonzero else'TESTED_ZERO_LOCAL_UNKNOWN')if not a['structure_fixed8']else('MIXED_OBSERVED_DOWNSTREAM_AND_LOCAL_RESPONSES'if d_nonzero and l_nonzero else'LOCAL_RESPONSE_DOWNSTREAM_TESTED_ZERO'if l_nonzero else'DOWNSTREAM_RESPONSE_LOCAL_TESTED_ZERO'if d_nonzero else'TESTED_ZERO_DOWNSTREAM_AND_LOCAL')
 ck('category_actual_observational_domain',r['classification']==category,(name,category));categories[category]+=1
 hasgain=bool(d_sign['POSITIVE']or l_sign['POSITIVE']);(gain if hasgain else nogain).append(name)
 ck('unproved_limits_preserved',str(r['critical_path_mechanism']).startswith('UNKNOWN')and all(v is None or isinstance(v,str)and v.startswith('UNKNOWN')for v in [r['potential_Oracle_S'],r['potential_Oracle_H'],r['theoretical_headroom']])and r['input_selection_changed']is False,name)
 ck('source_hypothesis_limits_unchanged',r['testable_hypothesis']==a['opportunity']and r['remaining_structure_constraints']==a['mandatory_limits']and r['initial_state_and_capture_limits']==a['declared_HtoD_and_source_scope'],name)
 digestrows.append({'program':name,'input_digest':a['input_digest'],'classification':category,'accepted_downstream':sum(d_sign.values()),'downstream_signs':dict(d_sign),'accepted_local_singles_plus_R1':localaccepted,'local_signs':dict(l_sign),'has_any_measured_gain':hasgain,'actual_longest_kernel_ordinal':top[0]['ordinal'],'actual_longest_kernel_duration_fraction':top[0]['cycles']/base})
ck('category_counts_match',dict(categories)==derived['category_counts'])
ck('expected6_11_13_1_1',sorted(categories.values())==[1,1,6,11,13])
ck('gain14_nogain18',len(gain)==14 and len(nogain)==18)
ck('zero_scientific_actions',derived['scientific_actions']==0)
readme=(P/'WORKLOAD_OPPORTUNITY_CLASSIFICATION_MULTIDIMENSIONAL.md').read_text();ck('prose_no_memoryfraction_claim','does not split that time into computation versus memory stalls'in readme and'UNKNOWN for every application'in readme)
put('VALIDATION.json',{'schema':'DTC_A_ROOT_MULTIDIMENSIONAL_DERIVATION_REVIEW_V1','status':'PASS','Root_manifest':{'path':str(P/'MAIN_SUPPLEMENT_MANIFEST.json'),'sha256':sha(P/'MAIN_SUPPLEMENT_MANIFEST.json')},'A_manifest':{'path':str(A/'MANIFEST.json'),'sha256':sha(A/'MANIFEST.json')},'checks_passed':len(checks),'checks':checks,'category_counts':dict(categories),'measured_gain_programs':gain,'no_measured_gain_programs':nogain,'classification_is_not_potential_or_input_selection':True,'scope':'Frozen A-derived records and exported Root supplement only; no old raw/archive audit or new experiment','models_core_runtime_or_Git_actions':0})
put('PROGRAM_CHECK_SUMMARY.json',digestrows)
(O/'README.md').write_text(f'# Independent lightweight derivation validation\n\nPASS: {len(checks)} CPU-only checks bind the Root fd0d supplement to frozen A6ac data. All32 full input identities, eight-factor accepted/status/cycles/source/signs, local singles+R1 scope and signs, OO cumulative events, typed traffic, actual longest-three kernel durations and complete six-cell references match.\n\nObserved gain14 / no observed gain18; observational categories6/11/13/1/1. These labels do not express theoretical headroom or admit/select workloads. Kernel duration shares remain distinct from memory/computation stall fractions and unique critical-path causes. Unaccepted engineering/safety outcomes retain null performance; scan has two different acceptedR1 cycles and missingJ.\n\nThe downstream field missing_or_negative counts unaccepted/missing scientific cells; accepted performance regressions are separately counted by NEGATIVE signs. No new simulation, GPU, source/Core/controller/registry/Goal action, old raw or archive rerun, or Root/A modification was performed.\n')
print(json.dumps({'output':str(O),'checks':len(checks),'categories':dict(categories),'gain':len(gain),'no_gain':len(nogain)}))
