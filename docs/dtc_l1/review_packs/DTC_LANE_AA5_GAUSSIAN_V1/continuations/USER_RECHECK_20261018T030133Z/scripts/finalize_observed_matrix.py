"""Render frozen four-cell formulas and typed observations after coordinator terminal. No launch."""
from pathlib import Path
import sys,csv,json,hashlib,re,shutil
from fractions import Fraction
from decimal import Decimal,localcontext
P=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa5-gaussian-convergence-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1')
sys.path.insert(0,str(P/'scripts'))
from common import *
from run_matrix import check_budget
Q=ROOT/'user_recheck_20261018T030133Z';C=P/'continuations/USER_RECHECK_20261018T030133Z'
U='UNAVAILABLE'
def put(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def tab(path,rows):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def ratio(a,b):return str(Fraction(a,b)) if isinstance(a,int) and isinstance(b,int) and b>0 else U
def observed_closed(run):
 if not (run/'RUN_TERMINAL.json').exists():return U
 t=(run/'simulator.stdout').read_text();m=re.findall(r'^gpu_tot_sim_cycle\s*=\s*(\d+)',t,re.M)
 return int(m[-1]) if m else U

def main():
 assert (Q/'MATRIX_EXECUTION_TERMINAL.json').exists(),'COORDINATOR_NOT_TERMINAL'
 owner=json.loads((Q/'AUTHORITY_ACTIVE.json').read_text());live=proc(owner['pid']);assert live is None or live['start_ticks']!=owner['start_ticks'],'COORDINATOR_STILL_ACTIVE_WAIT_FOR_LOG_WRITERS'
 end=json.loads((Q/'MATRIX_EXECUTION_TERMINAL.json').read_text());starts=check_budget();assert len(starts)<=4
 matrix=[];events=[];mechan=[];resources=[];receipts=[];accepted={};actual={}
 for label,uid,k,sets,ways,cal in POINTS:
  spec=json.loads((C/'specs'/f'{label}.json').read_text());run=ROOT/'attempts'/(label+'_'+uid)
  started=(run/'RUN_START.json').exists();s=json.loads((run/'STRICT.json').read_text()) if (run/'STRICT.json').exists() else dict(status='HOLD_NOT_STARTED' if not started else 'HOLD_NO_STRICT_RECEIPT',performance_accepted=False)
  term=json.loads((run/'RUN_TERMINAL.json').read_text()) if (run/'RUN_TERMINAL.json').exists() else {}
  valid=s.get('performance_accepted',False);cy=s.get('cycles',U);rawcy=observed_closed(run) if started else U
  if valid:accepted[label]=cy
  actual[label]=dict(strict=s,terminal=term,run=str(run),valid=valid,started=started)
  receipt=dict(point=label,UUID=uid,actual_start=started,status=s['status'],performance_accepted=valid,raw_directory=str(run) if started else 'NOT_CREATED',raw_public_cycles=rawcy,accepted_cycles=cy if valid else U,spec_sha256=sha(C/'specs'/f'{label}.json'),Core=spec['source_Core_commit'],binary_sha256=spec['runtime_sha256'],library_sha256=spec['runtime_library_sha256'],raw_strict_sha256=sha(run/'STRICT.json') if (run/'STRICT.json').exists() else U,strict_receipt=s,natural_terminal_receipt=term)
  put(C/'run_receipts'/f'{uid}.json',receipt);put(P/'run_receipts'/f'{uid}.json',receipt);put(P/'run_receipts'/uid/'STRICT.json',receipt)
  if started and (run/'FILES_SHA256.tsv').exists():
   shutil.copy2(run/'FILES_SHA256.tsv',P/'run_receipts'/uid/'RAW_SHA256.tsv')
   for item in csv.DictReader((run/'FILES_SHA256.tsv').open(),delimiter='\t'):assert sha(run/item['path'])==item['sha256'],str(run/item['path'])
  else:tab(P/'run_receipts'/uid/'RAW_SHA256.tsv',[dict(path='NO_ACTUAL_UUID_RAW_CREATED',sha256=U,status='NOT_RUN')])
  receipts.append(receipt)
  matrix.append(dict(point=label,UUID=uid,K=k,Tag_sets=sets,Tag_ways=ways,actual_starts=int(started),strict=s['status'],natural_exit0=term.get('natural_exit',U),observed_cycles_raw=rawcy,accepted_cycles=cy if valid else U,kernels=s.get('kernels',U),CTA=s.get('CTA',U),active_instructions=s.get('active_instructions',U),K0_calibration=s.get('calibration',{}).get('status','NOT_RUN'),historical_reference_cycles=cal if k==0 else 'NOT_A_CONTROL',Core=spec['source_Core_commit'],binary_sha256=spec['runtime_sha256'],library_sha256=spec['runtime_library_sha256'],config_profile_sha256=spec['effective_profile_sha256'],spec_sha256=sha(C/'specs'/f'{label}.json'),raw_directory=str(run) if started else 'NOT_CREATED',raw_strict_sha256=receipt['raw_strict_sha256']))
  ev=s.get('final_events',{});et=ev.get('totals',{}) if k and valid else {}
  events.append(dict(point=label,UUID=uid,K=k,availability='OBSERVED_LAST_NORMAL64SM_FRAME' if et else 'UNAVAILABLE_K0_NOT_OUTPUT' if k==0 and valid else 'UNAVAILABLE_NOT_STRICT_ACCEPTED',public_cycle=ev.get('public_cycle',U),**{f:et.get(f,U) for f in ['requests','idle','membar','config','unspecified','ordinary_commits','changed','retained_at_event','reclaimed_at_event','no_op_requests','event_records_omitted']},population='LAST_NORMAL_FRAME64_SM_SAME_PUBLIC_CYCLE_NOT_SUM_OF_KERNEL_SNAPSHOTS',comparison='K1_ONLY_NONCOMPARATIVE_DIAGNOSTIC_NO_K0_ZERO_OR_EVENT_DELTA'))
  if k and valid:put(C/'normal_terminal_events'/f'{uid}.json',ev)
  d=s.get('final_metrics',{}) if valid else {};traffic=s.get('traffic',{}) if valid else {}
  get=lambda f:d.get(f,U)
  ready=get('DTC_L1_oo_valid_hits');pending=get('DTC_L1_oo_pending_hits');new=get('DTC_L1_oo_new_misses');refs=ready+pending+new if valid else U
  values=[('cycles',cy if valid else U,'GPU_core_cycles',1),('active_instructions',s.get('active_instructions',U),'active_thread_instructions',1),('CTA',s.get('CTA',U),'CTAs',1),('ready',ready,'accepted_128B_logical_references',1),('pending',pending,'accepted_128B_logical_references',1),('new',new,'accepted_128B_logical_references',1),('accepted_references',refs,'accepted_128B_logical_references',1),('ready_fraction',ready,'fraction_of_accepted_references',refs),('pending_fraction',pending,'fraction_of_accepted_references',refs),('new_fraction',new,'fraction_of_accepted_references',refs),('lower_created',get('DTC_L1_oo_lower_created'),'lower_created_requests',1),('Tag_evictions',get('DTC_L1_oo_tag_evictions'),'capacity_victim_mapping_events_NOT_source_invalidations',1),('source_requests',et.get('requests',U),'source_request_events',1),('source_changed',et.get('changed',U),'revoked_query_mappings_at_source_event',1),('source_retained',et.get('retained_at_event',U),'revoked_mappings_whose_physical_owner_retained',1),('source_reclaimed',et.get('reclaimed_at_event',U),'independently_observed_reclaimed_at_event_R',1),('ordinary_commits',et.get('ordinary_commits',U),'ordinary_deferred_commit_invocations',1),('pib_integral',get('DTC_SERVICE_V1_pib_integral'),'PIB_entry_core_cycles',1),('physical_integral',get('DTC_SERVICE_V1_physical_integral'),'128B_line_core_cycles',1),('samples',get('DTC_SERVICE_V1_samples'),'nominal_64SM_core_cycle_samples',1),('pib_mean',get('DTC_SERVICE_V1_pib_integral'),'PIB_entries_per_nominal_SM_cycle',get('DTC_SERVICE_V1_samples')),('physical_mean_lines',get('DTC_SERVICE_V1_physical_integral'),'128B_lines_per_nominal_SM_cycle',get('DTC_SERVICE_V1_samples')),('finite_retired',get('DTC_SERVICE_V1_retired'),'finite_retired_population',1),('post_ready_sum',get('DTC_SERVICE_V1_fully_ready_to_complete_sum'),'core_cycles_summed_over_finite_retired',1),('post_ready_mean',get('DTC_SERVICE_V1_fully_ready_to_complete_sum'),'core_cycles_per_finite_retired',get('DTC_SERVICE_V1_retired')),('ready_to_collect_sum',get('DTC_SERVICE_V1_ready_to_collect_sum'),'core_cycles_summed_over_finite_retired',1),('collection_cycles',get('DTC_SERVICE_V1_collection_cycles'),'core_cycles_summed_over_finite_retired',1),('wb_wait',get('DTC_SERVICE_V1_wb_wait'),'core_cycles_summed_over_finite_retired',1),('collected_sectors',get('DTC_SERVICE_V1_collected_sectors'),'finite_collected_32B_sectors',1),('map_loss_to_free_sum',get('DTC_SERVICE_V1_map_loss_to_free_sum'),'core_cycles_summed_completed_map_loss_intervals',1),('map_loss_to_free_count',get('DTC_SERVICE_V1_map_loss_to_free_count'),'completed_map_loss_intervals_not_censored_allocations',1),('map_loss_to_free_mean',get('DTC_SERVICE_V1_map_loss_to_free_sum'),'core_cycles_per_completed_map_loss_interval',get('DTC_SERVICE_V1_map_loss_to_free_count')),('L2_read_sectors',traffic.get('L2_read_sectors_32B',U),'accepted_32B_sectors_at_L2',1),('L2_read_bytes',traffic.get('L2_read_bytes',U),'bytes_at_L2_accepted_32B_sector_stage',1),('DRAM_read_bytes',traffic.get('DRAM_read_bytes',U),'bytes_at_DRAM_RD_RD_L2_A_32B_command_stage',1),('DRAM_write_bytes',traffic.get('DRAM_write_bytes',U),'bytes_at_DRAM_WRITE_WR_BK_32B_command_stage',1)]
  for field,numerator,unit,denominator in values:
   mechanism=dict(point=label,UUID=uid,field=field,numerator=numerator,denominator=denominator,exact_value=ratio(numerator,denominator),typed_unit=unit,availability='OBSERVED_STRICT_ACCEPTED' if isinstance(numerator,int) and valid else U,comparison='K1_ONLY_DIAGNOSTIC' if field.startswith(('source_','ordinary_commits')) else 'SAME_DEFINITION_AND_PATH_ONLY',population_note='Completed conditional interval populations can differ; no additive causal decomposition')
   mechan.append(mechanism)
  adm=Q/'admissions'/label
  if (adm/'EXECUTION_RESOURCES.tsv').exists():
   for row in csv.DictReader((adm/'EXECUTION_RESOURCES.tsv').open(),delimiter='\t'):resources.append(dict(point=label,**row))
  if started:
   put(C/'execution_receipts'/f'{uid}.json',dict(terminal=term,PID=json.loads((run/'PID.json').read_text()) if (run/'PID.json').exists() else U,actual_loaded_identity=json.loads((run/'PROCESS_IDENTITY.json').read_text()) if (run/'PROCESS_IDENTITY.json').exists() else U,loaded_files_sha256=sha(run/'LOADED_FILES_SHA256.json') if (run/'LOADED_FILES_SHA256.json').exists() else U,resource_monitor_sha256=sha(run/'RESOURCE_MONITOR.jsonl') if (run/'RESOURCE_MONITOR.jsonl').exists() else U))
 effects=[];formulas=[('Q32','c/a'),('Q64','d/b'),('T0','b/a'),('T1','d/c'),('I','Q64/Q32=T1/T0=ad/(bc)'),('logI','ln(a)+ln(d)-ln(b)-ln(c)'),('Delta','a+d-b-c'),('K_main_effect','((c-a)+(d-b))/2'),('Tag_main_effect','((b-a)+(d-c))/2')]
 vals={}
 if len(accepted)==4:
  a,b,c,d=[Fraction(accepted[label]) for label,_,_,_,_,_ in POINTS]
  vals=dict(Q32=c/a,Q64=d/b,T0=b/a,T1=d/c,I=a*d/(b*c),Delta=a+d-b-c,K_main_effect=((c-a)+(d-b))/2,Tag_main_effect=((b-a)+(d-c))/2)
  assert vals['I']==vals['Q64']/vals['Q32']==vals['T1']/vals['T0']
  assert vals['Delta']==(d-b)-(c-a)
  with localcontext() as ctx:ctx.prec=50;vals['logI']=(Decimal(vals['I'].numerator)/Decimal(vals['I'].denominator)).ln()
 for n,f in formulas:
  v=vals.get(n,U);effects.append(dict(quantity=n,frozen_formula=f,exact_value=str(v),decimal_display=str(float(v)) if isinstance(v,Fraction) else str(v),typed_unit='GPU_core_cycles' if n in ['Delta','K_main_effect','Tag_main_effect'] else 'natural_log_dimensionless' if n=='logI' else 'dimensionless_cycle_quotient',accepted_new_cells=len(accepted),population='NEW_SAME_BINARY_FULL_GAUSSIAN_STRICT_ACCEPTED_ONLY_NO_HISTORICAL_IMPUTATION'))
 for n,rows in [('FULL_MATRIX.tsv',matrix),('ACTUAL_EVENTS.tsv',events),('TERMINAL_MECHANISM_COMPARISON.tsv',mechan),('FACTORIAL_EFFECTS.tsv',effects)]:tab(C/n,rows);tab(P/n,rows)
 if resources:tab(C/'EXECUTION_RESOURCES_ALL_POINTS.tsv',resources);tab(P/'EXECUTION_RESOURCES.tsv',resources)
 audit=dict(status='FOUR_STRICT_ACCEPTED_POINTS' if len(accepted)==4 else 'STOP_OR_HOLD_INCOMPLETE_ACCEPTED_FACTORIAL',matrix_execution_terminal=end,actual_starts=len(starts),accepted_new_points=len(accepted),accepted_integer_cycles=accepted,normal_export_gate='PASS_PRIOR_INDEPENDENT_PRODUCTION_CPU_GATE',K0_equivalence={n:actual[n]['strict'].get('calibration',{}) for n in ['K0_32x4','K0_64x8']},strict_receipts=receipts,private_counter_policy='Absent fields UNAVAILABLE, never fabricated measured PASS',limitations=['W fulladdressscan unavailable','Numerical loads not proved','CrossSM coherence not proved','IOK1/PPA/zero hardwarecost not proved','No precise crosskernel reuse share without direct line+generation linkage'])
 put(C/'STRICT_AUDIT.json',audit);put(P/'STRICT_AUDIT.json',audit);put(P/'STRICT.json',audit)
 put(C/'Z2_INDEPENDENT_RECALCULATION.json',dict(status='PASS_EXACT_NEW_INTEGER_FORMULAS' if len(accepted)==4 else 'UNAVAILABLE_INCOMPLETE_STRICT_CELLS',integer_cycles=accepted,formulas=effects,independent_identities_checked=len(accepted)==4,baseline_history_not_imputed=True,log_precision_decimal=50))
 shutil.copy2(C/'Z2_INDEPENDENT_RECALCULATION.json',P/'Z2_INDEPENDENT_RECALCULATION.json')
 shutil.copy2(Q/'MATRIX_EXECUTION_TERMINAL.json',C/'MATRIX_EXECUTION_TERMINAL.json');shutil.copy2(Q/'AUTHORITY_TERMINAL.json',C/'AUTHORITY_TERMINAL.json');shutil.copy2(Q/'CONTINUATION_PUBLICATION_READBACK.json',C/'CONTINUATION_PUBLICATION_READBACK.json')
 put(C/'ATTEMPT_BUDGET_FINAL.json',dict(actual_shared_AA_through_AA5_starts=len(starts),shared_total_start_limit=4,UUIDs={p[0]:p[1] for p in POINTS},RUN_START_receipts=starts,UUID_reset=False,automatic_retry=False,continuation_terminal=True))
 shutil.copy2(C/'ATTEMPT_BUDGET_FINAL.json',P/'ATTEMPT_BUDGET_FINAL.json')
 print(json.dumps(dict(status=audit['status'],actual_starts=len(starts),accepted_cycles=accepted,coordinator_terminal=end),indent=2))
if __name__=='__main__':main()
