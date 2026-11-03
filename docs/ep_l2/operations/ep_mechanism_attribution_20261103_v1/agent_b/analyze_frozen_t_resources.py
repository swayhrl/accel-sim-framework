import pathlib,json,collections,csv,hashlib
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1';Q=J/'research/mechanism_attribution_20261103_v1/agent_b'
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest(),bytes=P(p).stat().st_size)
basep=E/'analysis/primary_v1/ACCEPTED_PRIMARY_AND_MATCHED_REFERENCE_METRICS.json';base=json.loads(basep.read_text())['rows'][:3];kp=E/'analysis/primary_v1/T_KERNEL_CYCLE_DECOMPOSITION.json';ks=json.loads(kp.read_text())['rows'];rp=Q/'T_ACCEPTED_OFF_KERNEL_RESOURCE_RECORDS.json';rs=json.loads(rp.read_text())['rows']
MODE=['F_MINUS_T','LEGACY_F','CORRECTED_F'];agg={};refs=[ref(basep),ref(kp),ref(rp)];tp=[];lifecycle=[]
for a,k,r in zip(base,ks,rs):
 assert a['mode']==k['mode']==r['mode'];mode=a['mode'];agg[mode]={}
 for uid,name in [('1','Rows'),('2','Columns')]:
  fields=[x['fields']for x in r['records']if x['family']=='EPL2B0V1'and x['fields']['kernel_uid']==uid]
  assert len(fields)==64 and {int(x['slice'])for x in fields}==set(range(64)) and all(x['interval']=='kernel_shared_delta'and x['overlap_detected']=='0'for x in fields)
  vals={key:sum(int(x[key])for x in fields)for key in fields[0]if all(x[key].isdigit()for x in fields)and key not in ['slice','kernel_uid','start_cycle','completion_cycle']}
  m0=[x['fields']for x in r['records']if x['family']=='EPL2M0AV1'and x['fields']['kernel_uid']==uid]
  for key in m0[0]:
   if key.startswith('m0_')and all(x[key].isdigit()for x in m0):vals[key]=sum(int(x[key])for x in m0)
  vals['cycles']=k['row_kernel_cycles'if uid=='1'else'column_kernel_cycles'];agg[mode][name]=vals
 # No extra ON raw read: final GLOBAL route_joint already contains phase axes.
 p=E/'control/MECHANISM_METRICS'/a['cohort'].replace('_OFF_','_ON_');p=p.with_suffix('.json');d=json.loads(p.read_text());refs.append(ref(p));g=d['TP_final_GLOBAL'];assert g['closure_ok']and not g['output_invalid']and g['kernel_catalog']==[1,2]
 ni=E/'control/NI_RESULTS'/(a['cohort']+'.json');n=json.loads(ni.read_text());assert all(n['equal'].values());refs.append(ref(ni))
 groups={}
 for v in g['route_joint']:
  sl,ph,raw,res,requester,eligible,route,admitted,early,count=v;z=groups.setdefault(ph,collections.Counter());z['covered_head_cycles']+=count
  if route==2:z['consulted_miss_head_cycles']+=count
  if raw==3:
   assert res==8;z['raw_reservation_fail_head_cycles']+=count
   z['raw_fail_admitted_head_cycles'if admitted else'raw_fail_denied_head_cycles']+=count
   if eligible==2:
    z['structural_eligible_head_cycles']+=count;z['eligible_admitted_head_cycles'if admitted else'eligible_denied_head_cycles']+=count
    z['eligible_ro_candidate_head_cycles'if requester==0 else'eligible_nonro_head_cycles']+=count
    if route==2:z['eligible_relief_ro_head_cycles'if requester==0 else'eligible_relief_nonro_head_cycles']+=count
    if not admitted:z['eligible_denied_early_'+str(early)]+=count
 assert sum(z['raw_reservation_fail_head_cycles']for z in groups.values())==d['DETACH_DIAG_final_GLOBAL']['counters']['raw_reservation_fail']
 assert sum(z['consulted_miss_head_cycles']for z in groups.values())==d['DETACH_DIAG_final_GLOBAL']['counters']['detach_success']==a['ro_sums']['detached']
 tp.append(dict(mode=mode,kernel_catalog=g['kernel_catalog'],phase_to_kernel={'2':'Rows','3':'Columns'},counts={str(k):dict(v)for k,v in groups.items()},population='frontend same-request same-set same-tick head-cycle observations; repeated request wait heads are retained, not demand-unique NEW'))
 ro=d['mechanism_metrics']['full_mechanism_records']['readonly'];last=max(int(x['lower_concurrency']['last_response_gpu_cycle'])for x in ro.values());lifecycle.append(dict(mode=mode,max_last_ro_successful_response_gpu_cycle=last,rows_end_printed_cycles=k['row_kernel_cycles'],margin_before_rows_end=k['row_kernel_cycles']-last,last_response_semantics='physical GPU cycle of successful runtime RO response commit; not fill timestamp or standalone boundary live-RO census'))
# Application counters: same field / same unit only. No means/peaks are summed into capacity claims.
selected=['bank_wait_cycles','c7d_bank_fill_write','c7d_bank_resident_hit_read','c7d_bank_wb_readout','c7d_tag_set_all_reserved_block','c7d_missq_full_block','c7d_l2_to_dram_full_block','c7d_dram_credit_block','c7d_dram_returnq_block','c7d_line_mshr_full_block','c7d_descriptor_pool_full_block','c7e_dram_scheduler_causal_block','c7e_dram_issue_attempt','c7e_dram_successful_read_bytes','c7e_dram_successful_write_bytes','c7e_dram_successful_read_issues','c7e_dram_successful_write_issues','c7e_tag_way_alloc_need']
rows=[]
def add(scope,metric,vals,unit,population,denominator='NOT_APPLICABLE'):
 x=dict(scope=scope,metric=metric,unit=unit,population=population,denominator=denominator,A=vals[0],B=vals[1],C=vals[2],B_minus_A=vals[1]-vals[0],C_minus_B=vals[2]-vals[1],C_minus_A=vals[2]-vals[0],evidence='PROVEN',causal_boundary='event/exposure delta is not exclusive GPU critical-path cycles');rows.append(x)
for name in ['Rows','Columns']:
 add(name,'cycles',[agg[m][name]['cycles']for m in MODE],'GPU_cycles','actual kernel printed cycles')
 for metric in selected:
  add(name,metric,[agg[m][name][metric]for m in MODE],'bytes'if metric.endswith('_bytes')else'counter_exposures_or_events','64 slice kernel_shared_delta; scheduler issue probes occur in DRAM domain, frontend counters in L2 domain; bank wait in physical GPU domain')
 for metric in ['m0_frontend_head_observed_cycles','m0_frontend_head_any_blocked_cycles','m0_frontend_head_blocked_cycles_tag_way','m0_useful_frontend_admit','m0_useful_response_enqueue']:
  add(name,metric,[agg[m][name][metric]for m in MODE],'L2_slice_head_observations'if 'cycles'in metric else'events','64 slice kernel_shared_delta; M0 population excludes handled/exempt paths', 'm0_frontend_head_observed_cycles'if'blocked'in metric else'NOT_APPLICABLE')
for metric in ['cycles','unique_requesters','wb_created']:
 add('application',metric,[r[metric]for r in base],'GPU_cycles'if metric=='cycles'else'events','same-Core accepted complete commandlist')
for group in ['B0_sum_64_slice_exposures','P1_sum_observations','victim_sums','ro_sums']:
 for metric in base[0][group]:
  add('application',group+'.'+metric,[r[group][metric]for r in base],('bytes'if metric.endswith('_bytes')else'payload_slot_GPU_cycles'if'retention_slot_cycles'in metric else'GPU_cycle_slice_exposures'if metric in ['paid_wait_gpu_cycles','lookup_wait_cycles','wb_wait_cycles','bank_wait_cycles']else'events_or_head_exposures'),group+' full commandlist; retain producer units; first-block reasons overlap')
with(Q/'T_RESOURCE_DELTA_BY_ARM.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(Q/'T_KERNEL_TAG_JOINT_AND_RO_BOUNDARY.json').write_text(json.dumps(dict(schema='EP_MAIN_FROZEN_T_KERNEL_JOINT_AND_BOUNDARY_ANALYSIS_V1',source_refs=refs,model_starts=0,on_raw_reads=0,tag_joint=tp,ro_response_boundary=lifecycle,raw_enum_contract='gpu-cache.h:59-66 raw RESERVATION_FAIL=3; crosschecked final legacy raw_reservation_fail',kernel_resource_aggregates=agg),indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(csv_rows=len(rows),ro_response_boundary=lifecycle,tag_joint=tp),indent=2))
