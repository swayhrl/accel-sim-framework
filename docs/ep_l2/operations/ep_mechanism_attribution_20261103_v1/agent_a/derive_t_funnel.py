#!/usr/bin/env python3
"""Bounded offline reducer: accepted small JSON only; never reads raw/Trace or runs a model."""
import collections,csv,datetime,hashlib,json,pathlib
P=pathlib.Path
Q=P(__file__).resolve().parent
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1'
N=J/'research/implementation_performance_v2_20261029_v1/agent_d/core/src/gpgpu-sim'
W=J/'receipts/lane_o_v1r2_20261029/review/docs/ep_l2/operations/ep_main_implementation_performance_v2_20261029_v1/chatgpt_review_20261103_v1'
used={}
def ref(p):
 p=P(p);b=p.read_bytes();used[str(p)]={'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return used[str(p)]
def load(p):ref(p);return json.loads(P(p).read_text())
def check(x,m):
 if not x:raise AssertionError(m)
def dump(name,d): (Q/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
completed=load(W/'COMPLETED_EIGHT_RESULTS.json');ref(W/'CHATGPT_REVIEW_START_HERE.md')
addendum=load(E/'control/MAIN_NI_OFFLINE_CLOSEOUT_ADDENDUM.json');check(addendum['status']=='MAIN_CONFIRMED_THREE_SAME_ARM_NI_PASS_AFTER_OFFLINE_WRAPPER_REPAIR','Main NI addendum')
source={'core_source_commit':'1e07b263ca0879798387d2a712914a914f298775','framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':'54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505','archive_sha256':'4ea74720bec776712d56b84e493c376d364691d6eae40267f52bc836c703e2db'}
source_evidence=[]
for name,func,lo,hi in [('gpu-cache.cc','tag_array::probe',365,453),('gpu-cache.cc','l2_cache::preview_access ordinary paid virtual relief',2796,2840),('gpu-cache.cc','l2_cache::detach_diag_snapshot',3063,3099),('gpu-cache.cc','l2_cache::detach_diag_frontend',3104,3162),('gpu-cache.h','tag_array::diagnostic_way_class',1143,1152),('l2cache.cc','memory_sub_partition::cache_cycle frontend ordering',1322,1477),('l2cache.cc','actual access/accept',1587,1617),('ep-l2-ft-cache.inc','l2_cache::ft_access backend relieve and downstream gates',300,397),('ep-l2-ft-cache.inc','l2_cache::ft_physical_cycle',3,5),('ep-l2-ro-runtime.inc','ordinary_frontend_cycle shared paid port',108,123),('ep-l2-ro-runtime.inc','RO frontend query and preview',124,147),('ep-l2-ro-runtime.inc','detachable/relieve/RO preview',260,325),('ep-l2-ro-runtime.inc','Tag detach ownership/generation',179,203),('ep-l2-ro-transactions.h','merge reuse_seen and can_detach/detach',193,230),('ep-l2-ro-transactions.h','fill/response/retire',256,313),('ep-l2-ro-transactions.h','retire_if_done',396,404),('ep-l2-detach-diag.h','ledger once and closure',244,277),('ep-l2-detach-diag.h','commit_scope immediate result',303,304),('ep-l2-tagpressure-diag.h','route_joint exact tuple',107,136)]:
 source_evidence.append(dict(ref(N/name),function=func,line_start=lo,line_end=hi,github='https://github.com/swayhrl/gpgpu-sim/blob/'+source['core_source_commit']+'/src/gpgpu-sim/'+name+'#L'+str(lo)))
ref(E/'runtime_t/t3_counter_audit.py')
rows=[];audits=[];route_rows=[]
for arm in ['A_F_MINUS_T','B_LEGACY_F','C_CORRECTED_F']:
 cohort='EP_PERF_T3_CONV16X8_'+arm+'_ON_V1';p=E/'control/MECHANISM_METRICS'/(cohort+'.json');d=load(p);g=d['DETACH_DIAG_final_GLOBAL'];c=g['counters'];t=d['TP_final_GLOBAL'];h=t['histograms'];pc=d['P1_final_records_by_slice']
 check(g['closure_ok'] and g['epoch_closed'] and not g['overflow_invalid'] and not g['output_invalid'],'diag final valid')
 check(t['closure_ok'] and t['epoch_closed'] and t['sets']==16 and t['assoc']==8 and t['scope']=='FRONTEND_HEAD_CYCLE_SAME_TARGET_SET','TP final geometry/scope')
 check(g['cycle']==t['cycle'],'same final stamp')
 check(c['observed_heads']==c['probe_skipped']+t['counters']['covered'],'covered closure')
 check(sum(x[-1] for x in h['heads_raw_reserved'])==t['counters']['covered'],'TP covered population')
 check(sum(x[-1] for x in t['route_joint'])==t['counters']['covered'],'TP joint population')
 raw=c['raw_reservation_fail'];rawrows=[x for x in t['route_joint'] if x[2]==3]
 check(sum(x[-1] for x in rawrows)==raw and all(x[3]==8 for x in rawrows),'actual raw failure jointly R8')
 check(c['pressure_frontend_admitted']+c['pressure_frontend_denied']==raw,'front decision closure')
 check(c['pressure_prod_probe_reached']+c['pressure_prod_probe_not_reached']==raw,'preview reach closure')
 check(c['relieve_calls']==c['detach_calls']==c['detach_success']==c['post_relief_miss'],'relieve/detach/MISS closure')
 check(c['trigger_accepted_after_detach']+c['trigger_denied_after_detach']+c['trigger_exception_after_detach']==c['detach_success'],'immediate after-detach closure')
 check(c['detached_retired']==c['detached_responses']==c['detached_return_packets']==c['detached_return_sectors']==c['detach_success'] and g['live_detached']==0,'detached old transaction complete census')
 check(c['ro_admits']==c['ro_retired'] and c['ro_admits']+c['ro_merges']==c['ro_responses'],'all RO descriptor/transaction closure')
 physical_eligible=sum(x[-1]for x in h['heads_raw_reserved_eligible']if x[0]==3 and x[2]>0)
 physical_no_ro=sum(x[-1]for x in h['heads_raw_reserved_reasonmask']if x[0]==3 and x[2]==16)
 check(sum(x[-1]for x in h['heads_raw_reserved_eligible']if x[0]==3)==raw,'physical eligibility census')
 if g['T']:check(c['pressure_eligible']==physical_eligible,'T-enabled structural old/new observer agreement')
 else:check(c['pressure_eligible']==0,'T0 operational eligibility NA/disabled')
 checks=[];n=load(E/'control/NI_RESULTS'/('EP_PERF_T3_CONV16X8_'+arm+'_OFF_V1.json'))
 check(all(n['equal'].values()),'same mode compact NI')
 check(n['source_identity']==source,'exact NI Source5')
 for proof in n['proofs']:
  for k in ['accepted_point_ref','archive_receipt_ref']:
   rr=proof[k];check(ref(rr['path'])['sha256']==rr['sha256'],'accepted/archive SHA')
 for rr in [d['validation_ref']]:check(ref(rr['path'])['sha256']==rr['sha256'],'validation SHA')
 cp=next(x for x in completed['points']if x['cohort']==cohort);check(cp['source_identity']==source and cp['state']=='CLOSED_ACCEPTED' and cp['cycles']==g['cycle'] and cp['hardware_drained'],'accepted ON identity/completion')
 check(cp['instructions']==714547200 and cp['CTA']==27648 and cp['kernel_count']==2,'application completion population')
 p1={k:sum(int(v[k])for v in pc.values())for k in ['issued','paid_wait_gpu_cycles','port_wait_attempts']};check(len(pc)==64,'exact64slice P1 final')
 joint=collections.Counter()
 for x in rawrows:joint[tuple(x[4:9])]+=x[-1]
 for k,v in sorted(joint.items()):route_rows.append(dict(arm=arm,requester=['CERTIFIED_RO_CANDIDATE','NONRO_NATIVE_PATH','RUNTIME_OFF'][k[0]],structural_eligible=k[1]==2,route=['PROD_NOT_REACHED','NOT_CONSULTED','CONSULTED_MISS','CONSULTED_FAIL','EXISTING_HIT_RESERVED','ROUTE_OTHER'][k[2]],frontend_admit=bool(k[3]),early=['NONE','OWNER','DIRECTORY','PAID_QUERY','WAD','TVD'][k[4]],head_cycles=v))
 row=dict(arm=arm,cycles=g['cycle'],frontend_observed_head_cycles=c['observed_heads'],covered_head_cycles=t['counters']['covered'],frontend_skipped_head_cycles=c['probe_skipped'],raw_full_head_cycles=raw,raw_full_R8_joint_head_cycles=raw,raw_full_no_live_RO_head_cycles=physical_no_ro,raw_full_live_RO_head_cycles=raw-physical_no_ro,raw_full_structural_eligible_head_cycles=physical_eligible,operational_eligible_head_cycles=c['pressure_eligible'] if g['T']else'NOT_APPLICABLE_T_OFF',raw_full_frontend_allow=c['pressure_frontend_admitted'],raw_full_frontend_deny=c['pressure_frontend_denied'],raw_full_preview_probe_reached=c['pressure_prod_probe_reached'],raw_full_preview_not_reached=c['pressure_prod_probe_not_reached'],raw_full_preview_relief_not_consulted=c['pressure_relief_not_consulted'],raw_full_virtual_MISS=c['pressure_rewrite_miss'],backend_raw_TagFAIL=c['raw_tag_fail_commit'],backend_relieve=c['relieve_calls'],actual_detach=c['detach_success'],post_relief_MISS=c['post_relief_miss'],trigger_this_access_accepted=c['trigger_accepted_after_detach'],trigger_this_access_denied=c['trigger_denied_after_detach'],old_detached_fill_packets=c['detached_return_packets'],old_detached_responses=c['detached_responses'],old_detached_retired=c['detached_retired'],ordinary_query_issued=p1['issued'],ordinary_query_slice_GPU_wait_exposure=p1['paid_wait_gpu_cycles'],ordinary_query_port_wait_attempts=p1['port_wait_attempts'],all_RO_admit=c['ro_admits'],all_RO_merges=c['ro_merges'],all_RO_responses=c['ro_responses'],all_RO_retire=c['ro_retired'],strict_demand_unique_NEW='NOT_INSTRUMENTED',trigger_later_UID_completion='NOT_MEASURED',post_detach_denial_reason_joint='NOT_INSTRUMENTED',compact_same_mode_NI='PASS')
 rows.append(row);audits.append(dict(arm=arm,metrics_ref=ref(p),all_offline_closure_assertions='PASS',full_counter_copy=c,TP_raw_fail_histograms={k:[x for x in v if x[0]==3]for k,v in h.items()},accepted_ON=cp,NI_ref=ref(E/'control/NI_RESULTS'/('EP_PERF_T3_CONV16X8_'+arm+'_OFF_V1.json'))))
with(Q/'T_DETACH_FUNNEL_BY_ARM.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with(Q/'T_RAW_FULL_ROUTE_JOINT.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(route_rows[0]));w.writeheader();w.writerows(route_rows)
audit=dict(schema='EP_L2_T_COUNTER_POPULATION_AUDIT_V1',status='PASS_BOUNDED_OFFLINE_CENSUS_WITH_EXPLICIT_GAPS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_identity=source,input_identity_sha256='438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e',geometry={'slices':64,'sets_per_slice':16,'ways':8,'DRAM_channels':32,'dram_latency':100},rows=rows,arm_audits=audits,source_evidence=source_evidence,populations={'frontend':'actual L2 frontend callback; once per slice per (physical GPU cycle, requestUID); blocked UID recurs on later callbacks','raw_full':'passive raw tag probe RESERVATION_FAIL before modeled preview; TP joint census proves R8; includes native writeback and RO candidate, not strict demand NEW','structural_eligible':'at same snapshot/request/set/time: live RO && attached && !reuse_seen && (required & ~ready); physical TP records even T0; operational diag counts only T1','preview_reached':'production preview raw Tag probe reached, not backend ft_access reached','preview_virtual_MISS':'paid query ready plus structural candidate; no Tag mutation; allow decision still precedes real ft_access','backend_TagFAIL':'actual ft_access raw probe returned RESERVATION_FAIL; fewer than blocked frontend exposure by construction','query':'new timed metadata tickets, one shared port per slice per physical GPU cycle, ready at now+1; wait exposures summed across slices, not exclusive GPU cycles','detached_return':'old physical transaction, accepted fill packet/sector, response waiter and retirement counters have distinct units; equality happens in these single-waiter detached instances','completion':'full application/drain validated; per-trigger later UID chain and numerical application output not measured'},claim_boundaries={'PROVEN':['B ordinary eligible NOT_CONSULTED head-cycle joint12536; C ordinary eligible query-wait63 and virtualMISS allow63','B/C different trajectories/populations; counters cannot be subtracted as unique opportunities saved/lost','all actual detached old transactions retire and live_detached is zero','Corrected-F still slower than same ELF F-MINUS-T for this complete Conv input'], 'LIKELY':['changed eligibility exposure is affected by changed execution timing and earlier release; no fixed-UID attribution is available'], 'UNKNOWN':['how many distinct blocked demand UIDs each arm had','which later cycle accepted/completed the seven triggering accesses initially denied','specific resource reason jointly for these seven','per-detach critical path benefit and paid-query critical path penalty','physical PPA/timing closure','future performance after relaxing reuse_seen or other protections']},actions={'full_application_starts':0,'GPU_collection':0,'raw_streaming_passes':0,'Trace_scans':0,'production_source_edits':0,'registry_native_dispatcher_writes':0,'git_writes':0,'offline_json_reduction':'executed with exact closure/source/SHA checks','CPU_fixture':'none executed in this subtask; prior qualified fixtures only read','new_instrumentation':'candidate design only, not implemented or run'})
dump('T_COUNTER_POPULATION_AUDIT.json',audit)
dump('OFFLINE_EXECUTION_RECEIPT.json',dict(schema='EP_T_FUNNEL_OFFLINE_EXECUTION_RECEIPT_V1',status='PASS',utc=audit['utc'],source_files_read=list(used.values()),distinct_input_bytes=sum(x['bytes']for x in used.values()),actions=audit['actions'],output_files=['T_DETACH_FUNNEL_BY_ARM.csv','T_RAW_FULL_ROUTE_JOINT.csv','T_COUNTER_POPULATION_AUDIT.json']))
print(json.dumps({'status':'PASS','arms':rows,'source_files':len(used),'bytes':sum(x['bytes']for x in used.values())}))
