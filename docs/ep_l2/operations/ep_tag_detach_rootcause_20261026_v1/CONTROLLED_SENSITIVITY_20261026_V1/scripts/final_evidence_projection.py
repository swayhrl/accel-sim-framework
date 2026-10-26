#!/usr/bin/env python3
"""Post-acceptance evidence projection; read immutable results, write review branch only."""
import pathlib,json,hashlib,csv,shutil
J=pathlib.Path('/root/data/ep_memory_path_sensitivity_20261026_v1')
R=pathlib.Path('/root/data/ep_tag_rootcause_20261026_v1/worktree')
D=R/'docs/ep_l2/operations/ep_tag_detach_rootcause_20261026_v1'
P=D/'CONTROLLED_SENSITIVITY_20261026_V1'
L=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger')
E1='EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1'
E2='EP_NATIVE_VECTOR_L1MISSQ32_SENSITIVITY_20261026_V1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def cp(p,q):q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
def compact(v):
 ss=v.pop('standard_last_snapshot',{})
 v['known_application_scalar_snapshot']={k:ss[k] for k in ['gpu_tot_ipc','gpu_tot_issued_cta','gpu_tot_sim_insn','gpu_stall_dramfull','gpu_stall_icnt2sh'] if k in ss}
 v.pop('b0_slice_last_application',None)
 ch=v.pop('dram_channel_last_application',{})
 v['DRAM_channels_present']=len(ch)
 v.pop('actual_effective_options',None)
 peaks=v['derived'].pop('RO_per_slice_peaks_do_not_sum')
 v['RO_per_slice_peak_ranges']={k:{'min':min(row[k] for row in peaks.values()),'max':max(row[k] for row in peaks.values())} for k in next(iter(peaks.values()))}
 t=v['r5_tagpressure'];r=t.pop('route_joint',[])
 t['route_joint_rows_in_full_comparison']=len(r)
 t['histograms']={k:a for k,a in t['histograms'].items() if k in ['heads_raw_reserved','heads_raw_reserved_eligible']}
 return v
points={}; archives={}
for label,case in [('E1',E1),('E2',E2)]:
 done=read(L/(case+'.DONE.json'))
 assert done['launcher_wait_returncode']==0 and done['stop_reason'] is None
 out=pathlib.Path(done['output']); point=read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 assert point['status']=='EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED'
 assert point['raw_sha256']==done['raw_sha256']==sha(out/'raw.log')
 arpath=J/'control'/(label+'_ARCHIVE_STDOUT.json')
 ar=read(arpath) if arpath.exists() and arpath.stat().st_size else None
 if ar is not None:assert ar['archive']['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
 if ar is not None:assert ar['independent_restore']['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS'
 cmp=read(out/'SENSITIVITY_COMPARISON.json')
 v=compact(cmp['variant'])
 points[label]=v
 if label=='E1':points['baseline']=compact(cmp['baseline'])
 r4=read(out/'R4_212_TERMINAL.json')
 v['production_global_r4_counters']=r4['global_counters']
 v['acceptance']=point
 v['comparison_to_baseline']={k:cmp[k] for k in ['baseline_cycles_over_case_cycles','case_cycle_change_fraction']}
 v['immutable_evidence']={n:sha(out/n) for n in ['raw.log','CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json','SENSITIVITY_COMPARISON.json','R4_212_TERMINAL.json','R5_TAGPRESSURE_TERMINAL.json','terminal_summary.json','ACTUAL_EFFECTIVE_OPTION_AUDIT.json']}
 v['native_done']=done
 for n in (['CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json','ACTUAL_EFFECTIVE_OPTION_AUDIT.json']+(['POSTRUN_ENTRY_ROUTE_EQUIVALENCE.json'] if label=='E2' else [])):
  cp(out/n,P/'evidence'/label/n)
 cp(J/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',P/'evidence'/label/(case+'.NATIVE_Q.json'))
 for suffix in ['INTENT.json','DONE.json']:
  cp(L/(case+'.'+suffix),P/'evidence'/label/(case+'.'+suffix))
 for n in ['FROZEN_SPEC.json','SPEC_AUTHORIZATION_BINDING.json']:
  cp(J/'cases'/case/'control'/n,P/'specs'/(case+'.'+n))
 a=({'archive_receipt':ar['archive']['receipt'],
    'independent_restore':{k:v for k,v in ar['independent_restore'].items() if k!='rows'},
    'independent_restore_inventory_rows':len(ar['independent_restore']['rows']),
    'full_receipt_runtime_path':str(J/'control'/(label+'_ARCHIVE_STDOUT.json')),
    'full_receipt_sha256':sha(J/'control'/(label+'_ARCHIVE_STDOUT.json'))} if ar is not None else {'status':'PENDING_RESOURCE_ADMISSION','source_disposition':'SOURCE_KEEP','no_scientific_rerun':True})
 archives[label]=a
 put(P/'evidence'/label/'ARCHIVE_AND_RESTORE_PROJECTION.json',a)
for n in ['E2_DECISION.json','E2_REGISTRATION_RECEIPT.json','E2_INPUT_REBIND_ENTRY_RECEIPT.json','E2_POSTRUN_ENTRY_RECEIPT.json','E2_ARCHIVE_CONTINUATION_ENTRY_RECEIPT.json','E2_ARCHIVE_RESOURCE_HOLD.json']:
 cp(J/'control'/n,P/'evidence'/n)
cp(J/'cases'/E2/'control/FRESH_INPUT_ASSET_BINDING.json',P/'evidence/E2_FRESH_INPUT_ASSET_BINDING.json')
for f in (J/'cases'/E2/'control/spec_history').iterdir():
 if f.is_file():cp(f,P/'specs/E2_prequalification_history'/f.name)
manifest=read(P/'ENGINEERING_SOURCE_MANIFEST.json')
for n in ['e2_fresh_input_dispatch.py','native_entry_e2_candidate.sh','prior_to_e2_entry.sh','e2_postrun_entry_adapter.py','peer_extended_native_entry.sh','native_entry_postrun_candidate.sh','final_evidence_projection.py','e2_archive_continuation.py','prior_postrun_native_entry.sh','native_entry_archive_continuation.sh']:
 p=J/'tools'/n;cp(p,P/'scripts'/n)
 manifest=[m for m in manifest if m['runtime_path']!=str(p)]
 manifest.append(dict(runtime_path=str(p),archive_path='scripts/'+n,sha256=sha(p),scope='E2 operational/postrun or offline projection tool; E1 frozen sources unchanged; see postrun equivalence proof'))
put(P/'ENGINEERING_SOURCE_MANIFEST.json',manifest)
for n in ['ARCHIVE_CONTINUATION_STAGE_PROOF.json','ARCHIVE_CONTINUATION_CLOSEOUT.json']:
 cp(J/'cases'/E2/'control'/n,P/'evidence/E2'/n)
samples=J/'cases'/E2/'control/ARCHIVE_CONTINUATION_RESOURCE_SAMPLES.jsonl'
rr=[json.loads(z) for z in samples.read_text().splitlines()]
put(P/'evidence/E2/ARCHIVE_CONTINUATION_RESOURCE_SAMPLES_PROJECTION.json',dict(full_runtime_path=str(samples),full_sha256=sha(samples),sample_count=len(rr),all_consistent=all(r['consistent_snapshot'] for r in rr),all_runtime_pass=all(r['runtime_pass'] for r in rr),all_admission_pass_remains_null=all(r['admission_pass'] is None for r in rr),minimum_free_bytes=min(r['free_bytes'] for r in rr),required_actual_free_bytes=max(r['required_bytes'] for r in rr),minimum_host_MemAvailable_bytes=min(r['host_MemAvailable_bytes'] for r in rr),minimum_cgroup_effective_headroom_bytes=min(r['cgroup_effective_headroom_bytes'] for r in rr),maximum_observed_local_logical_allocated_growth_bytes=[max(r['observed_local_growth_logical_allocated_bytes'][i] for r in rr) for i in [0,1]]))

put(P/'RESULTS_PROJECTION.json',{'schema':'EP_MEMORY_PATH_CONTROLLED_SENSITIVITY_RESULTS_V1','note':'No unscoped last-slice/channel snapshot. Histograms retain original joint populations. B0 means rounded at producer; maxima are per-slice peak extrema, not simultaneous sum. No raw or trace payload copied into Git.','points':points,'archives':archives})
rows=[]
def add(label,metric,value,unit,scope,evidence):
 rows.append(dict(point=label,metric=metric,value=value,unit=unit,scope=scope,evidence=evidence))
for label in ['baseline','E1','E2']:
 p=points[label];d=p['derived'];t=p['r5_tagpressure'];l1=next(v for v in p['l1_last_records'].values() if v['scope']=='application')
 for k,u,s in [('cycles','core_cycle','application'),('instructions','thread_instruction','application'),('DRAM_successful_read_bytes','byte','all_channels'),('DRAM_successful_write_bytes','byte','all_channels'),('DRAM_bandwidth_util_ratio_of_summed_byte_numerators_denominators','ratio','all_channels_byte_numerator_over_byte_denominator'),('DRAM_scheduler_full_channel_ticks_sum','channel_DRAM_tick','sum_32_channels'),('DRAM_returnq_full_channel_ticks_sum','channel_DRAM_tick','sum_32_channels'),('RO_transactions_sum','transaction','sum_64_slices'),('RO_merges_sum','merge','sum_64_slices'),('RO_detached_sum','detach','sum_64_slices')]:
  add(label,k,d[k],u,s,'derived.'+k)
 for k,v in l1.items():
  if k not in ['scope','kernel_uid']:add(label,'L1_'+k,v,'cache_access_or_retry_event','application; retries_not_unique_requests','l1_last_records.application.'+k)
 for group,unit,scope in [('B0_events_sum_over_slices_not_global_cycles','slice_L2_tick_event','sum_64_slices; may_overlap'),('B0_maximum_of_slice_peaks_not_simultaneous_sum','entry_or_Tag','max_of_64_slice_peaks_not_simultaneous_sum'),('B0_mean_of_reported_slice_time_means_rounded_at_source','entry_or_Tag','unweighted_mean_64_producer_rounded_slice_means')]:
  for k,v in d[group].items():add(label,k,v,('byte' if k.endswith('_bytes') else 'issue_attempt' if k.endswith('issue_attempt') else unit),scope,'derived.'+group+'.'+k)
 for k in ['covered_heads','new_tag_demand_heads','maximum_RESERVED_target_set','new_tag_demand_max_RESERVED','new_tag_and_structurally_eligible_heads','raw_tag_fail_heads','raw_tag_fail_with_reuse_heads']:
  add(label,k,t[k],'Tag' if 'RESERVED' in k else 'head_L2_tick','r5_covered_target_set_joint; skipped_NA','r5_tagpressure.'+k)
 if 'production_global_r4_counters' in p:
  for k in ['raw_tag_fail_commit','relieve_calls','detach_success','trigger_accepted_after_detach','closure_errors','commit_accepted','commit_denied','denied_bank','denied_landing','reuse_seen_first_transition']:
   add(label,k,p['production_global_r4_counters'][k],'production_event','global_sum_64_slices','production_global_r4_counters.'+k)
with (P/'SAME_IDENTITY_METRICS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps({'status':'PROJECTION_WRITTEN','projection_bytes':(P/'RESULTS_PROJECTION.json').stat().st_size,'rows':len(rows),'E2_cycles':points['E2']['derived']['cycles'],'E2_cycle_change':points['E2']['comparison_to_baseline']['case_cycle_change_fraction']}))
