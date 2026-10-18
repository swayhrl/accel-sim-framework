"""Read-only AG3 outcome/typed diagnostics; never starts or resumes anything."""
from common import *
from fractions import Fraction
from decimal import Decimal,localcontext
from audit_site import snapshot,proc
from review_authority import review
import re


def main():
 reservations=json.loads((PACK/'UUID_RESERVATIONS.json').read_text())['rows']
 terminal_path=RAW/'COHORT_TERMINAL.json'
 require=bool(terminal_path.is_file())
 if not require:raise ValueError('NO_COHORT_TERMINAL_NOT_FINAL_REPORT')
 cohort=json.loads(terminal_path.read_text());rows=[];results={};indices=[];mechanisms=[];identities=[]
 for row in reservations:
  run=RAW/'attempts'/(row['point']+'_'+row['attempt_uuid']);start=run/'RUN_START.json';strict=run/'STRICT.json'
  result=json.loads(strict.read_text()) if strict.exists() else None
  results[row['point']]=result
  accepted=bool(result and result['performance_accepted']);engine=run/'ENGINE/FORK_CHILD.json';actual=bool(engine.is_file())
  state=result['status'] if result else ('STOP_AFTER_REAL_START_NO_STRICT' if actual else 'STOP_BEFORE_REAL_START' if run.exists() else 'NOT_STARTED_COHORT_STOP' if cohort['status']=='STOP' else 'NOT_STARTED')
  rows.append(dict(order=row['order'],point=row['point'],arm=row['arm'],workload=row['workload'],attempt_uuid=row['attempt_uuid'],status=state,reservation_consumed=int(start.exists()),actual_fork_exec_start=int(actual),full_strict_pass=int(accepted),integer_cycles=result['cycles'] if accepted else 'UNAVAILABLE',same_input_new_BASE_cycles='UNAVAILABLE',speed_BASE_over_ON='UNAVAILABLE',exact_ratio='UNAVAILABLE',raw=str(run) if run.exists() else 'NOT_CREATED'))
  if run.exists():
   output=run/'simulator.stdout';headers=0
   if output.exists():
    with output.open(errors='replace') as f:headers=sum(line.startswith('kernel_name = ') for line in f)
   indices.append(dict(point=row['point'],attempt_uuid=row['attempt_uuid'],raw=str(run),status=state,raw_index_sha256=sha(run/'FILES_SHA256.tsv') if (run/'FILES_SHA256.tsv').exists() else 'UNAVAILABLE',strict_sha256=sha(strict) if strict.exists() else 'UNAVAILABLE',engine_terminal_sha256=sha(run/'ENGINE/TERMINAL.json') if (run/'ENGINE/TERMINAL.json').exists() else 'UNAVAILABLE',observed_kernel_name_headers_nonperformance=headers))
   eventpath=run/'ENGINE/MAP_EVENTS.jsonl';images={};snapshots=0;owned_events=[]
   if eventpath.exists():
    with eventpath.open() as events:
     for line in events:
      e=json.loads(line)
      if 'maps' not in e:
       if 'new_owned_pid' in e:owned_events.append(e)
       continue
      snapshots+=1;key=(e['pid'],e['exe']);image=images.setdefault(key,dict(pid=e['pid'],exe=e['exe'],snapshots=0,initial_exec=None,first_cache_present=None,first_cache_removed=None,first_startup_closed=None,last_snapshot=None))
      image['snapshots']+=1;image['last_snapshot']=e
      if e['stage']=='INITIAL_EXEC' and image['initial_exec'] is None:image['initial_exec']=e
      if e['cache_present'] and image['first_cache_present'] is None:image['first_cache_present']=e
      if '/etc/ld.so.cache' in e['removed_files'] and image['first_cache_removed'] is None:image['first_cache_removed']=e
      if e['startup_closed'] and image['first_startup_closed'] is None:image['first_startup_closed']=e
   et=run/'ENGINE/TERMINAL.json'
   identities.append(dict(point=row['point'],attempt_uuid=row['attempt_uuid'],actual_start=actual,map_events_sha256=sha(eventpath) if eventpath.exists() else 'UNAVAILABLE',full_map_snapshots=snapshots,images=list(images.values()),owned_fork_clone_events=owned_events,terminal=json.loads(et.read_text()) if et.exists() else 'UNAVAILABLE',early_coverage='actual syscall entry/exit and initial exec; registered hash/stat/role checked by frozen production verifier',negative_coverage='CPU qualification only; no deliberate identity corruption injected into a scientific attempt'))
  if accepted:
   metrics=result['final_metrics'];mechanisms.append(dict(point=row['point'],final_common_metrics=metrics,traffic=result['traffic'],ON_only_diagnostic=result.get('AC_pipeline_diagnostic'),postready_comparison='AD readiness-condition population differs; no causal mean subtraction',tag_set_bank_histogram='UNAVAILABLE_NOT_PRINTED',actual_collection_WB_overlap='UNAVAILABLE_NOT_PRINTED',K1_only='UNAVAILABLE_K0',numeric_load_values='UNAVAILABLE',native_correctness='UNPROVEN'))
 for row in rows:
  base=results.get('BASE_'+row['workload'])
  if row['full_strict_pass'] and base and base['performance_accepted']:
   numerator=base['cycles'];denominator=row['integer_cycles'];ratio=Fraction(numerator,denominator)
   with localcontext() as ctx:ctx.prec=24;value=str(Decimal(numerator)/Decimal(denominator))
   row.update(same_input_new_BASE_cycles=numerator,speed_BASE_over_ON=value,exact_ratio=f'{ratio.numerator}/{ratio.denominator}')
 table(PACK/'FULL_MATRIX.tsv',rows);table(PACK/'RUN_ARTIFACT_INDEX.tsv',indices or [dict(point='NONE',status='ZERO_ATTEMPT_PRELAUNCH_STOP')])
 dictionary=list(csv.DictReader((PACK/'METRIC_DICTIONARY.tsv').open(),delimiter='\t'));metric_rows=[]
 def metric_value(result,entry):
  if not result or not result['performance_accepted']:return 'UNAVAILABLE'
  source=entry['source_key'];den=entry['denominator']
  metrics=result['final_metrics'];numerator=result.get('traffic',{}).get(source[8:]) if source.startswith('traffic.') else metrics.get(source)
  denominator=1 if den=='1' else metrics.get(den)
  if not isinstance(numerator,int) or not isinstance(denominator,int):return 'UNAVAILABLE'
  if denominator==0:return 'UNDEFINED_ZERO_DENOMINATOR'
  return str(Fraction(numerator,denominator))
 for row in rows:
  result=results[row['point']];base=results.get('BASE_'+row['workload'])
  for entry in dictionary:
   actual=metric_value(result,entry);control=metric_value(base,entry)
   scope=entry['comparability']
   on_detail=bool(scope=='NONCOMPARATIVE_ON_DIAGNOSTIC' and result and result['performance_accepted'] and result.get('AC_pipeline_diagnostic',{}).get('status')=='PASS_AD_ON_ONLY_DIAGNOSTIC')
   availability='MEASURED_ON_ONLY_PER_SM' if on_detail else 'UNAVAILABLE' if actual=='UNAVAILABLE' else actual if actual=='UNDEFINED_ZERO_DENOMINATOR' else 'MEASURED_CHANGED_READY_CONDITION' if scope=='AD_READY_CONDITION_CHANGED_NO_CAUSAL_MEAN_DIFFERENCE' and row['arm']=='AD' else 'MEASURED_SAME_DEFINITION'
   if on_detail:actual='AVAILABLE_PER_SM_IN_TYPED_DIAGNOSTIC'
   permitted=scope=='PUBLIC_SAME_DEFINITION_ONLY' or (scope=='AD_READY_CONDITION_CHANGED_NO_CAUSAL_MEAN_DIFFERENCE' and row['arm']!='AD')
   difference='UNAVAILABLE'
   if permitted and actual not in ('UNAVAILABLE','UNDEFINED_ZERO_DENOMINATOR') and control not in ('UNAVAILABLE','UNDEFINED_ZERO_DENOMINATOR'):difference=str(Fraction(actual)-Fraction(control))
   metric_rows.append(dict(point=row['point'],arm=row['arm'],workload=row['workload'],field=entry['field'],source=entry['source_key'],unit=entry['unit'],denominator=entry['denominator'],value_exact=actual,availability=availability,same_input_new_BASE_value_exact=control,arm_minus_BASE_exact=difference,comparability=scope,ON_only_detail='TYPED_MECHANISM_RESULTS.json' if on_detail else 'UNAVAILABLE_OFF_OR_INCOMPLETE' if scope=='NONCOMPARATIVE_ON_DIAGNOSTIC' else 'NOT_APPLICABLE',note='AD ready-conditioned values descriptive only; no causal subtraction' if scope=='AD_READY_CONDITION_CHANGED_NO_CAUSAL_MEAN_DIFFERENCE' else 'same frozen metric dictionary; missing is not zero'))
 table(PACK/'PER_ARM_METRICS.tsv',metric_rows)
 write(PACK/'TYPED_MECHANISM_RESULTS.json',dict(rows=mechanisms,missing='UNAVAILABLE_NOT_ZERO',discovery_not_holdout=True,GM12=False))
 write(PACK/'ACTUAL_LOADER_LIFECYCLE_EVIDENCE.json',dict(rows=identities,full_lifecycle_PASS_requires_engine_identity_and_scientific_strict=True,raw_maps_and_logs_remain_outside_Git=True))
 resources=[];locks=[];admissions=[];previous_lock_states={}
 def lock_rows(point,phase,snap,auth=None):
  checked={(x['pid'],str(x['fd']),x['path']):x for x in (auth or {}).get('remaining_DTC_FLOCKs',[])}
  prior=previous_lock_states.get((point,phase),{});current={}
  for item in snap['FLOCKs']:
   reviewed=checked.get((item['pid'],str(item['fd']),item['path']))
   classification='OWN_AG3_EXECUTION' if reviewed and reviewed.get('own_AG_execution') else 'REVIEWED_OUTPUT_ONLY' if reviewed and reviewed.get('output_only_collector') else 'EXTERNAL_EP_L2_RESOURCE_COUNTED' if reviewed and reviewed.get('external_EP_L2_resource_counted') else 'DTC_FLOCK_UNCLASSIFIED' if reviewed else 'OTHER_OBSERVED_FLOCK_OUTSIDE_REVIEWED_DTC_SET' if auth else 'FIRST_RESOURCE_SAMPLE_UNREVIEWED_SEPARATELY'
   state=dict(point=point,phase=phase,holder_pid=item['pid'],holder_start_ticks=item['start_ticks'],fd=item['fd'],path=item['path'],fdinfo_sha256=hashlib.sha256(item['fdinfo'].encode()).hexdigest(),classification=classification,authority_status=auth['status'] if auth else 'UNAVAILABLE_FIRST_RESOURCE_SAMPLE')
   signature=tuple(state.items())
   if signature in prior:
    interval=prior[signature];interval['last_observed_utc']=snap['utc'];interval['consecutive_samples']+=1
   else:
    interval=dict(**state,first_observed_utc=snap['utc'],last_observed_utc=snap['utc'],consecutive_samples=1);locks.append(interval)
   current[signature]=interval
  previous_lock_states[point,phase]=current
 for folder in sorted((RAW/'admissions').glob('*')):
  decision_path=folder/'DECISION.json';decision=json.loads(decision_path.read_text()) if decision_path.exists() else None
  for phase in ('FIRST','SECOND'):
   path=folder/(phase+'.json')
   if not path.exists():continue
   s=json.loads(path.read_text());auth=decision['authority'] if decision and phase=='SECOND' else None
   admissions.append(dict(point=folder.name,phase=phase,utc=s['utc'],monotonic_ns=s['monotonic_ns'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_headroom_bytes=int(s['cgroup']['memory.max'])-int(s['cgroup']['memory.current']),disk_free_bytes=s['disk_free_bytes'],memory_full=s['pressure']['memory']['full']['avg10'],io_full=s['pressure']['io']['full']['avg10'],authority=auth['status'] if auth else 'UNAVAILABLE_FIRST_RESOURCE_SAMPLE',all_pair_resource_checks_pass=all(decision['resource_checks'].values()) if decision else 'UNAVAILABLE',snapshot_path=str(path),snapshot_sha256=sha(path)))
   lock_rows(folder.name,phase,s,auth)
 for path in sorted((RAW/'attempts').glob('*/FINAL_PRE_FORK.json')):
  d=json.loads(path.read_text());s=d['snapshot'];auth=d['authority']
  admissions.append(dict(point=path.parent.name,phase='FINAL_PRE_FORK',utc=s['utc'],monotonic_ns=s['monotonic_ns'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_headroom_bytes=int(s['cgroup']['memory.max'])-int(s['cgroup']['memory.current']),disk_free_bytes=s['disk_free_bytes'],memory_full=s['pressure']['memory']['full']['avg10'],io_full=s['pressure']['io']['full']['avg10'],authority=auth['status'],all_pair_resource_checks_pass='SEE_FIRST_SECOND_PAIR_NOT_A_NEW_PAIR',snapshot_path=str(path),snapshot_sha256=sha(path)))
  lock_rows(path.parent.name,'FINAL_PRE_FORK',s,auth)
 for run in sorted((RAW/'attempts').glob('*')):
  path=run/'RESOURCE_MONITOR.jsonl'
  if not path.exists():continue
  with path.open() as f:
   for line in f:
    rec=json.loads(line);s=rec['snapshot'];d=rec['decision'];o=rec['own'];resources.append(dict(point=run.name,utc=s['utc'],monotonic_ns=s['monotonic_ns'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],cgroup_current=s['cgroup']['memory.current'],cgroup_swap=s['cgroup']['memory.swap.current'],pswpin=s['pswpin'],pswpout=s['pswpout'],memory_full=s['pressure']['memory']['full']['avg10'],io_full=s['pressure']['io']['full']['avg10'],own_RSS_bytes=o['rss_bytes'] if o else 'UNAVAILABLE',own_majflt=o['majflt'] if o else 'UNAVAILABLE',decision=d['decision'],reasons=';'.join(d['warnings']+d['stop_reasons']),authority=rec['authority']['status']))
    lock_rows(run.name,'RUNTIME',s,rec['authority'])
 table(PACK/'ADMISSION_TIMELINE.tsv',admissions or [dict(point='NONE',phase='UNAVAILABLE_NO_ADMISSION')])
 table(PACK/'RESOURCE_TIMELINE.tsv',resources or [dict(point='NONE',decision='UNAVAILABLE_ZERO_SAMPLES')])
 write(PACK/'RESOURCE_WARNING_SUMMARY.json',dict(total_samples=len(resources),warning_samples=[r for r in resources if r['decision']=='WARN'],stop_samples=[r for r in resources if r['decision']=='STOP'],global_swap_is_not_process_attribution=True,own_RSS_and_major_fault_scope='discrete proc snapshots; not final wait4 rusage or a guaranteed exact RSS peak',final_wait4_rusage='UNAVAILABLE_NOT_CAPTURED_BY_FROZEN_ENGINE'))
 snap=snapshot();auth=review(snap);write(RAW/'FINAL_SITE_SNAPSHOT.json',snap,exclusive=True);write(PACK/'FINAL_SITE_AUTHORITY.json',auth)
 lock_rows('COHORT','FINAL_SITE',snap,auth)
 table(PACK/'FLOCK_TIMELINE.tsv',locks or [dict(point='NONE',classification='NO_OBSERVED_FLOCK')])
 own_raw=str(RAW/'AG_execution.lock');ownlocks=[x for x in snap['FLOCKs'] if x['path']==own_raw]
 child_instances=[]
 for path in (RAW/'attempts').glob('*/ENGINE/CHILD.json'):
  child=json.loads(path.read_text());live=proc(child['pid']);child_instances.append(dict(pid=child['pid'],start_ticks=child['start_ticks'],same_instance_live=bool(live and live['start_ticks']==child['start_ticks'])))
 own_processes=[x for x in snap['processes'] if any(str(x.get(k,'')).startswith(str(RAW.parent)+'/') for k in ('exe','cwd'))]
 assert not ownlocks and not any(x['same_instance_live'] for x in child_instances) and not own_processes
 summary=dict(status=cohort['status'],reason=cohort['reason'],reserved_slots=6,reservation_consumed=sum(r['reservation_consumed'] for r in rows),actual_starts=sum(r['actual_fork_exec_start'] for r in rows),full_strict_passes=sum(r['full_strict_pass'] for r in rows),core='c8090115bd57512b1b23fca7d925301fa620c751',preregistration='7b16a8519fae54540048cb37ae38080f20e56e7d',max_concurrency=1,rows=rows,old_AG=dict(actual_starts=1,budget=8,full_strict=0,UUID='5de274d3-f296-4ee8-a577-17cc661e718e',unchanged=True),old_AA5=dict(actual_starts=1,budget=4,full_strict=0,UUID='d0a29a82-c171-46e4-b077-d7ccfd2c4b7a',unchanged=True),no_paper_or_old44_GM12_edits=True,own_execution_FLOCKs=0,child_instances=child_instances,no_automatic_dispatch=True)
 write(PACK/'RESULT_SUMMARY.json',summary)
 lines=['# AG3 — '+cohort['status'],'',f"Actual new starts {summary['actual_starts']}/6; consumed reservations {summary['reservation_consumed']}/6; complete strict PASS {summary['full_strict_passes']}. Core c8090115bd57512b1b23fca7d925301fa620c751. Published executable preregistration7b16a8519fae54540048cb37ae38080f20e56e7d preceded every new start.",'', 'Reason: `'+str(cohort['reason'])+'`. No retry, replacement, canary or seventh start.','', '|Point|Status|Integer cycles|new same-input BASE / arm|','|---|---|---:|---:|']
 for row in rows:lines.append('|'+ '|'.join(str(row[k]) for k in ['point','status','integer_cycles','speed_BASE_over_ON'])+'|')
 lines+=['','Only full strict, calibrated current BASEs permit ratios. Prefixes, raw partial cycles, CPU fixture/wall time and historical T are not current BASE data. Two known workloads are discovery, not independent validation or GM12. Missing/ON-only fields stay UNAVAILABLE; AD post-ready conditioning and AE hardware XOR/timing assumptions remain explicit. See FULL_MATRIX.tsv, TYPED_MECHANISM_RESULTS.json, RESOURCE_TIMELINE.tsv, RUN_ARTIFACT_INDEX.tsv and the scientific/resource/runner contracts.','','Historical AG remains1/8 actual,0 full strict; AA5 remains1/4,0 full strict and its451.4s/67-kernel single-page resource STOP. No old UUID/raw/STOP changed, no paper v0.14-R1/old44/GM12 edit. Own children gone, own execution FLOCK0, no automatic dispatch.']
 (PACK/'LATEST_REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','child_instances']}))
if __name__=='__main__':main()
