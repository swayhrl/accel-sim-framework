from pathlib import Path
import json,re,gzip,hashlib,sys,importlib.util,datetime
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1')
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1')
DIGEST='4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def additive_interval(current,previous,initial=False):
 result={}
 for k in set(current)|set(previous):
  if k not in current:result[k]=None;continue
  v=current[k]
  if initial:result[k]=v # fixed constructor-zero basis, first snapshot only
  elif k not in previous:result[k]=None
  else:
   if v<previous[k]:raise ValueError('COUNTER_DECREASE_OR_RESET:'+k)
   result[k]=v-previous[k]
 return result
idxp=R/'control/ORIGINAL_REFERENCE_INDEX.json';idxb=idxp.read_bytes();idx=json.loads(idxb)
refs=[x for x in idx['rows'] if x['input_digest']==DIGEST and (x['cell'],x['profile'])in[('CH','P0'),('DH','P0'),('DH','F128'),('DH','F256')]]
assert len(refs)==4
newp=R/'analysis/E2-DTC2A16-4114a3dc0d06b55b-CH-F128-V1.RESULT.json'
refs.append({'cell':'CH','profile':'F128','input_digest':DIGEST,'source_path':str(newp),'sha256':sha(newp.read_bytes()),'source_role':'STAGEII_AUTHORIZED_CH'})
new256=R/'analysis/E2-DTC2A16-4114a3dc0d06b55b-CH-F256-V1.RESULT.json'
refs.append({'cell':'CH','profile':'F256','input_digest':DIGEST,'source_path':str(new256),'sha256':sha(new256.read_bytes()),'source_role':'STAGEII_AUTHORIZED_CH'})
specp=R/'control/specs/E2-DTC2A16-4114a3dc0d06b55b-CH-F256-V1.json';spec=json.loads(specp.read_bytes());bindp=Path(spec['input_binding_path']);bindb=bindp.read_bytes();assert sha(bindb)==spec['input_binding_sha256'];binding=json.loads(bindb);roi=spec['expected'];contract_kernels=binding['qualification']['rows'];assert len(contract_kernels)==roi['kernels']==2
(O/'ACTUAL_INPUT_AND_KERNEL_CONTRACT.json').write_text(json.dumps({'spec_path':str(specp),'spec_sha256':sha(specp.read_bytes()),'input_binding_path':str(bindp),'input_binding_sha256':sha(bindb),'input_digest':DIGEST,'roi_sha256':spec['original_environment']['DTC_AG7_ROI_SHA'],'expected':roi,'qualification':binding['qualification'],'source_scope':binding['current_source_scope']},indent=2)+'\n')
catp=A/'agents/B_counter_semantics_v1/COUNTER_SCOPE_CATALOG.json';assert sha(catp.read_bytes())=='b7bea76d9acbf7af32938ab109238c47b11784eb99f62ac26a220eea0a03f547'
(O/'CONSUMED_COUNTER_CATALOG.json').write_bytes(catp.read_bytes())
# Independently revalidate the new actual strict/archive/native restore through the frozen readonly adapter.
ap=A/'agents/B_runtime_adapter_v1/actual_readonly_adapter.py';assert sha(ap.read_bytes())=='c3310df8a4c8fb2d94ba57742339c3220367822c62128270810060d3967107a7';sp=importlib.util.spec_from_file_location('convseparable_readonly_adapter',ap);ad=importlib.util.module_from_spec(sp);sp.loader.exec_module(ad)
consumer,ct,bas=ad.frozen_inputs();q,plan,context=ad.registry_context()
for pf in ['F128','F256']:
 expected=next(x for x in ct['expected_CH'] if x['input_digest']==DIGEST and x['profile']==pf);old=next(x for x in bas['references'] if x['input_digest']==DIGEST and x['design']=='CH' and x['profile']=='P0');verified=ad.observation(expected,old,context,q);assert verified['accepted'] is True
 (O/('NEW_CH_'+pf+'_INDEPENDENT_QUALIFICATION.json')).write_text(json.dumps(verified,indent=2)+'\n')
static={'DTC_L1_baseline_mshr_entries','DTC_L1_lower_outstanding_cap'}
gauges={'DTC_L1_pib_occupancy','DTC_L1_lower_outstanding','DTC_L1_oo_inflight_current','DTC_L1_oo_pib_occupancy','DTC_L1_oo_active_refs','DTC_L1_oo_physical_allocated'}
counts=['gpu_stall_dramfull','L2_total_cache_accesses','L2_total_cache_misses','L2_total_cache_pending_hits','L2_total_cache_reservation_fails','DTC_L1_baseline_mshr_entry_full_events','DTC_L1_baseline_mshr_merge_full_events','DTC_L1_lower_cap_full_events','DTC_L1_lower_requests_acquired','DTC_L1_lower_requests_released','DTC_L1_nonexclusive_lower_cap_full_cycles','DTC_L1_nonexclusive_mshr_entry_full_cycles','DTC_L1_nonexclusive_mshr_merge_full_cycles','DTC_L1_nonexclusive_pib_full_cycles','DTC_L1_nonexclusive_tag_bank_conflict_cycles','DTC_L1_pib_admits','DTC_L1_pib_retires','DTC_L1_pib_full_events','DTC_L1_pib_occupancy_cycle_sum','DTC_L1_pib_occupancy_sample_cycles','DTC_L1_primary_stall_lower_cap','DTC_L1_primary_stall_pib_full','DTC_L1_primary_stall_tag_bank','DTC_L1_tag_conflicts','DTC_L1_tag_requests','DTC_L1_oo_lower_create_queue_full_stalls','DTC_L1_oo_lower_created','DTC_L1_oo_lower_issued','DTC_L1_oo_lower_responses','DTC_L1_oo_valid_hits','DTC_L1_oo_pending_hits','DTC_L1_oo_new_misses','DTC_L1_oo_tag_evictions','DTC_L1_oo_immediate_reclaims','DTC_L1_oo_deferred_reclaims','DTC_L1_oo_final_ref_reclaims','DTC_L1_oo_wakeups','DTC_L1_oo_retire_count','DTC_L1_oo_out_of_order_retires','DTC_L1_oo_ready_but_writeback_blocked_cycles','DTC_L1_oo_completion_dependency_count','DTC_L1_oo_completion_dependency_closed','DTC_L1_lower_credit_acquired','DTC_L1_lower_credit_released']+['DTC_SERVICE_V1_'+k for k in ['samples','pib_integral','physical_integral','collected_sectors','fully_ready_to_complete_sum','retired','ready_to_collect_sum','collection_cycles','wb_wait','map_loss_to_free_sum','map_loss_to_free_count']]+['DTC_L1_tag_bank_'+str(i)+'_requests' for i in range(4)]
rows=[]
for ref in refs:
 p=Path(ref['source_path']);rb=p.read_bytes();assert sha(rb)==ref['sha256'];r=json.loads(rb);pr=r['proof'];assert pr['performance_accepted'] is True and pr['input_digest']==DIGEST and pr['cell']==ref['cell'];assert pr.get('profile',pr.get('downstream_profile'))==ref['profile']
 for k,v in [('core_commit','9eedb3131937748f0492fa83aad37d3691118d70'),('framework_commit','02775fd795cde5aae1480d81cee6eb481d0a08f4'),('binary_sha256','02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')]:assert pr[k]==v
 if 'reference_result_path'in r:assert sha(Path(r['reference_result_path']).read_bytes())==r['reference_result_sha256']
 root=Path(r.get('reference_result_path',str(p))).parents[1]/'DTC/run/results'/r['uuid'];evb=(root/'NATIVE_EXIT.json').read_bytes();ev=json.loads(evb);assert ev['launcher_wait_returncode']==0 and ev['stop_reason']is None;gz=(root/'raw.log.gz').read_bytes();assert sha(gz)==ev['raw_sha256'];rawb=gzip.decompress(gz);assert sha(rawb)==ev['raw_uncompressed_sha256'];raw=rawb.decode();marks=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',raw,re.M));assert len(marks)==roi['kernels'];ks=[];prev={};prev_fail={};prevwall=0
 for n,m in enumerate(marks):
  b=raw[m.start():marks[n+1].start()if n+1<len(marks)else len(raw)];numeric={k:int(v)for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',b,re.M)};assert numeric['kernel_stream_id']==0
  buckets={kind+':'+status:int(v)for kind,status,v in re.findall(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',b,re.M)}
  for s in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS','TOTAL_ACCESS']:assert 'GLOBAL_ACC_R:'+s in buckets
  accepts=sum(buckets['GLOBAL_ACC_R:'+s]for s in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS']);assert accepts==buckets['GLOBAL_ACC_R:TOTAL_ACCESS'];miss=buckets['GLOBAL_ACC_R:MISS']+buckets['GLOBAL_ACC_R:SECTOR_MISS']
  dram=re.findall(r'^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',b,re.M);assert len(dram)==20;controllers={i:{k:int(v)for k,v in re.findall(r'(n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',line)}for i,line in dram};dr=sum(x['n_rd']+x['n_rd_L2_A']for x in controllers.values());dw=sum(x['n_write']+x['n_wr_bk']for x in controllers.values())
  cumulative={k:numeric[k]for k in counts if k in numeric};cumulative.update(L2_GLOBAL_read_accepted_sectors=accepts,L2_GLOBAL_read_miss_sectors=miss,DRAM_issued_read_atoms32B=dr,DRAM_issued_write_atoms32B=dw)
  delta=additive_interval(cumulative,prev,initial=(n==0))
  lat=re.findall(r'^\s*(avg_mrq_latency|averagemflatency|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=\s*(\S+)\s*$',b,re.M);fail={layer+':'+kind+':'+reason:int(v)for layer,kind,reason,v in re.findall(r'^\s*(\w*fail\w*)\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',b,re.M)}
  # Positive-only raw reason omissions are never silently replaced by zero.
  faildelta={k:(v if n==0 else v-prev_fail[k]if k in prev_fail else None)for k,v in fail.items()};wall=re.findall(r'^gpgpu_simulation_time = .*\((\d+) sec\)\s*$',b,re.M);wall=int(wall[0])if wall else None
  gauges_values={k:numeric[k]for k in gauges if k in numeric};peak={k:v for k,v in numeric.items()if k.startswith('DTC_')and'peak'in k}
  ks.append({'ordinal':n+1,'kernel':m[1],'cycles':numeric['gpu_sim_cycle'],'cumulative_cycles':numeric['gpu_tot_sim_cycle'],'instructions':numeric['gpu_sim_insn'],'cumulative_instructions':numeric['gpu_tot_sim_insn'],'cumulative_CTA':numeric['gpu_tot_issued_cta'],'cumulative_additive':cumulative,'print_boundary_interval_additive':delta,'raw_reason_cumulative_explicitly_printed':fail,'raw_reason_interval_only_when_both_snapshots_print_it':faildelta,'raw_reason_absence':'MISSING_NOT_ZERO; omitted positive-only reason cannot be filled','terminal_gauges':gauges_values,'running_peaks_no_differencing':peak,'configuration_values':{k:numeric[k]for k in static if k in numeric},'latency_tokens_diagnostic_only':lat,'latency_window_warning':'MRQ cumulative request mean is distinct; other means may omit un-folded tail at500000cycle sampling/cleanup boundary; no mean differencing','L2_buckets_cumulative':buckets,'DRAM_controllers_cumulative':controllers,'printed_cumulative_host_seconds':wall,'host_seconds_interval':wall-prevwall if wall is not None else None})
  prev=cumulative;prev_fail=fail;prevwall=wall or prevwall
 assert sum(k['cycles']for k in ks)==r['cycles'];assert ks[-1]['cumulative_instructions']==pr['instructions']==roi['instructions'];assert [k['instructions']for k in ks]==[k['active_thread_instructions']for k in contract_kernels];assert [k['kernel']for k in ks]==[k['kernel']for k in contract_kernels];assert ks[-1]['cumulative_CTA']==roi['CTA']
 rows.append({'cell':ref['cell'],'profile':ref['profile'],'role':ref['source_role'],'input_digest':DIGEST,'RESULT_path':str(p),'RESULT_sha256':sha(rb),'cohort':r['cohort'],'uuid':r['uuid'],'cycles':r['cycles'],'native_exit_sha256':sha(evb),'raw_path':str(root/'raw.log.gz'),'raw_gzip_sha256':ev['raw_sha256'],'raw_uncompressed_sha256':ev['raw_uncompressed_sha256'],'reference_alias_disclosed':r.get('reference_result_path'),'core_commit':pr['core_commit'],'framework_commit':pr['framework_commit'],'binary_sha256':pr['binary_sha256'],'effective_options':pr['effective_options'],'kernels':ks,'totals':prev,'raw_reason_final_explicitly_printed':prev_fail,'strict_latency_counters':pr.get('latency_counters'),'strict_metrics':pr['metrics'],'strict_traffic':pr['traffic']})

by={(r['cell'],r['profile']):r for r in rows};assert len(by)==6
changes=[];matched=[]
for profile in ['F128','F256']:
 for cell in ['CH','DH']:
  p,z=by[cell,'P0'],by[cell,profile];diff={k:{'P0':p['effective_options'].get(k),'variant':z['effective_options'].get(k)}for k in set(p['effective_options'])|set(z['effective_options'])if p['effective_options'].get(k)!=z['effective_options'].get(k)};assert diff=={'-gpgpu_frfcfs_dram_sched_queue_size':{'P0':['64'],'variant':[profile[1:]]}}
  for stage in ['TOTAL',1,2]:
   a=p['totals']if stage=='TOTAL'else p['kernels'][stage-1]['print_boundary_interval_additive'];b=z['totals']if stage=='TOTAL'else z['kernels'][stage-1]['print_boundary_interval_additive'];vals={}
   for k in sorted(set(a)|set(b)):
    x,y=a.get(k),b.get(k);vals[k]={'P0':x,'variant':y,'delta':y-x if x is not None and y is not None else None,'pct':100*(y/x-1)if x not in [None,0]and y is not None else None,'availability':'BOTH_EXPLICIT'if x is not None and y is not None else'MISSING_NOT_ZERO'}
   c0=p['cycles']if stage=='TOTAL'else p['kernels'][stage-1]['cycles'];cv=z['cycles']if stage=='TOTAL'else z['kernels'][stage-1]['cycles'];changes.append({'cell':cell,'profile':profile,'stage':stage,'cycles_P0':c0,'cycles_variant':cv,'cycles_delta':cv-c0,'speedup':c0/cv,'counter_changes':vals,'option_diff':diff})
 sc=by['CH','P0']['cycles']/by['CH',profile]['cycles'];sd=by['DH','P0']['cycles']/by['DH',profile]['cycles'];rf=by['CH',profile]['cycles']/by['DH',profile]['cycles'];matched.append({'profile':profile,'S_CH':sc,'S_DH':sd,'R_P0':by['CH','P0']['cycles']/by['DH','P0']['cycles'],'R_variant':rf,'I':sd/sc,'DH_cycles_over_CH_variant':1/rf,'CH_cycle_change_pct':100*(1/sc-1),'DH_cycles_reduction_pct':100*(1-sd**-1),'I_inverse_CH_speedup':1/sc,'I_factor_from_DH_speedup':sd})
l1diff={profile:{k:{'CH':by['CH',profile]['effective_options'].get(k),'DH':by['DH',profile]['effective_options'].get(k)}for k in set(by['CH',profile]['effective_options'])|set(by['DH',profile]['effective_options'])if by['CH',profile]['effective_options'].get(k)!=by['DH',profile]['effective_options'].get(k)}for profile in ['P0','F128','F256']}
data={'schema':'DTC_STAGEIIA_CONVSEPARABLE_P0_F128_F256_SIX_MATCHED_CLOSED_COUNTERS_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_input_digest':DIGEST,'reference_index_path':str(idxp),'reference_index_sha256':sha(idxb),'six_closed_sources':rows,'within_design_changes':changes,'matched_performance':matched,'CH_DH_deliberate_option_differences':l1diff,'missingness_rule':'After first known constructor-zero snapshot both endpoints explicitly required; no missing->0. Positive-only raw reasons remain missing when not printed. Means/gauges/peaks never differenced.','boundary_warning':'Completed-kernel print intervals are not request-origin attribution; cumulative last metrics contain mixed scopes.','no_model_or_runtime_actions':True,'capture_source_ELF_or_numerical_correctness_not_upgraded':True}
(O/'SIX_CLOSED_SOURCE_DATA.json').write_text(json.dumps(data,indent=2)+'\n');print('MATCHED',matched)
for r in rows:print('CYCLES',r['cell'],r['profile'],r['cycles'],[k['cycles']for k in r['kernels']])
