"""Pre-performance strict collector. Read-only raw; never starts or retries a simulator."""
from common import *
from event_snapshots import snapshot as event_snapshot
BASELINES={32:Path('/workspace/dtc-service-closure-174-v1/r2-attempts/R2_V2_COHORT_OO_Gaussian_41e02b7d-474d-4bf1-9f2b-b515aa326179/simulator.stdout'),64:Path('/workspace/dtc-tag-pilot-174-v1/attempts/DTC_TAG_PILOT_V1_T1_C_Gaussian_63f15c5a-a731-4c07-a3ce-c65312142a50/simulator.stdout')}
FINITE=['samples','pib_integral','physical_integral','collected_sectors','fully_ready_to_complete_sum','retired','ready_to_collect_sum','collection_cycles','wb_wait','map_loss_to_free_sum','map_loss_to_free_count']
U='UNAVAILABLE'

def require(ok,why):
    if not ok:raise ValueError(why)

def input_check(spec):
    require(sha(spec['trace_list'])==spec['trace_list_sha256'],'original_list_SHA')
    ms=json.loads((PACK/'inputs/AA4/INPUT_STAT_IDENTITY.json').read_text())['members'];require(len(ms)==510,'members510')
    for m in ms:
        st=Path(m['path']).stat()
        require((st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(m['device'],m['inode'],m['bytes'],m['mtime_ns'],m['ctime_ns']),'member_mutation:'+m['path'])
    return dict(status='PASS_510_ACCEPTED_MEMBER_SHA_PLUS_NO_POST_HASH_STAT_MUTATION',members=510,manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),list_sha256=sha(spec['trace_list']))

def echo(text):
    result={}
    for l in text.splitlines():
        m=re.match(r'^(-\S+)\s+(.*?)\s*#',l)
        if m:
            require(m[1] not in result or result[m[1]]==m[2].split(),'conflicting_duplicate_config_echo:'+m[1]);result[m[1]]=m[2].split()
    return result

def numeric(block):
    pairs=re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',block,re.M);out={}
    for k,v in pairs:

        if k in out:
            require(not (k.startswith(('DTC_','gpu_','gpgpu_n_mem_','icnt_total_'))),'duplicate_metric:'+k)
        out[k]=int(v)
    return out

def traffic(block):
    l2={f'{a}:{b}':int(v) for a,b,v in re.findall(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',block,re.M)}
    ds=re.findall(r'^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',block,re.M)
    require(len(ds)==20 and {int(i) for i,_ in ds}==set(range(20)),'DRAM_controller_population')
    # n_ref_event is not initialized in inherited model; preserve raw, never use as a measured count.
    dram={int(i):{k:int(v) for k,v in re.findall(r'(n_cmd|n_nop|n_act|n_pre|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',l)} for i,l in ds}
    accepted=sum(l2['GLOBAL_ACC_R:'+k] for k in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS'])
    require(accepted==l2['GLOBAL_ACC_R:TOTAL_ACCESS'],'L2_accepted_read_partition')
    return dict(L2_buckets=l2,L2_read_sectors_32B=accepted,L2_read_bytes=32*accepted,DRAM_controllers=dram,DRAM_read_bytes=32*sum(d['n_rd']+d['n_rd_L2_A'] for d in dram.values()),DRAM_write_bytes=32*sum(d['n_write']+d['n_wr_bk'] for d in dram.values()),DRAM_n_ref_event='UNAVAILABLE_UNINITIALIZED_IN_INHERITED_MODEL_RAW_PRESERVED')

def parse(text,K,old=False):
    starts=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',text,re.M));require(len(starts)==510,'ordered_kernel_count')
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text());require([m[1] for m in starts]==[m['kernel'] for m in ordered],'ordered_kernel_names')
    require(re.findall(r'^Processing kernel (\S+)$',text,re.M)==[m['member_path'] for m in ordered],'ordered_member_paths')
    require(len(re.findall(r'^launching memcpy command : MemcpyHtoD,',text,re.M))==3,'513commands_3HtoD')
    require(text.count('GPGPU-Sim: *** exit detected ***')==1 and text.count('GPGPU-Sim: *** simulation thread exiting ***')==1,'natural_terminal_markers')
    require('performance model initialization complete.' in text,'real_model_initialized')
    blocks=[text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)] for i,m in enumerate(starts)]
    metrics=[];events=[];ctas=insns=0;previous=None
    for i,(block,expected) in enumerate(zip(blocks,ordered)):
        d=numeric(block);ctas+=expected['complete_ctas'];insns+=expected['active_instructions']
        require(d['gpu_sim_insn']==expected['active_instructions'] and d['gpu_tot_sim_insn']==insns and d['gpu_tot_issued_cta']==ctas,'kernel_instructions_CTAs:'+str(i+1))
        require(d['kernel_launch_uid']==i+1,'kernel_launch_uid')
        require('DTC_L1_mode = PAPER_OO' in block,'OO_scope')
        ev=event_snapshot(block,K);R=ev['reclaimed_at_event'] if K else 0
        v=lambda k:d['DTC_L1_'+k];f=lambda k:d['DTC_SERVICE_V1_'+k]
        require(all(v(k)==0 for k in ['oo_pib_occupancy','oo_inflight_current','oo_active_refs','lower_outstanding']),'terminal_refs_inflight_pib_credit:'+str(i+1))
        require(v('lower_credit_acquired')==v('lower_credit_released')==v('oo_lower_created')==v('oo_lower_issued')==v('oo_lower_responses'),'lower_credit_created_response_balance')
        require(v('oo_completion_dependency_count')==v('oo_completion_dependency_closed')==v('oo_valid_hits')+v('oo_pending_hits')+v('oo_new_misses'),'Ref_completion_balance')
        require(sum(v('m4_'+x+'_admits') for x in ['store','atomic','bypass_load','proxy_fence'])==v('m4_source_completions')==v('m4_observation_retires'),'ordinary_completion_balance')
        require(0<=v('oo_physical_allocated')<=640*64,'physical_capacity')
        require(v('oo_new_misses')==v('oo_physical_allocated')+v('oo_immediate_reclaims')+v('oo_final_ref_reclaims')+R,'physical_conservation_independent_R')
        require(all('DTC_SERVICE_V1_'+x in d for x in FINITE),'finite11_presence')
        require(f('samples')==64*d['gpu_tot_sim_cycle'],'finite_population_64SM')
        require(f('fully_ready_to_complete_sum')==f('ready_to_collect_sum')+f('collection_cycles')+f('wb_wait'),'finite_postready_decomposition')
        require(f('map_loss_to_free_count')==v('oo_immediate_reclaims')+v('oo_final_ref_reclaims')+R,'finite_reclaim_population')
        if previous:
            for key in FINITE:
                require(f(key)>=previous['DTC_SERVICE_V1_'+key],'cumulative_finite_monotonic:'+key)
        previous=d;metrics.append(d);events.append(ev)
    require(ctas==65790 and insns==283685120,'whole_input_totals')
    return dict(metrics=metrics,events=events,traffic=traffic(blocks[-1]),kernel_count=510,active_instructions=insns,CTAs=ctas,cycles=metrics[-1]['gpu_tot_sim_cycle'],config=echo(text))

def comparable(d):
    return {k:v for k,v in d.items() if k.startswith(('DTC_L1_','DTC_SERVICE_V1_')) or k in ['gpu_sim_cycle','gpu_tot_sim_cycle','gpu_sim_insn','gpu_tot_sim_insn','gpu_tot_issued_cta','gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','icnt_total_pkts_mem_to_simt','icnt_total_pkts_simt_to_mem']}

def calibration(parsed,sets):
    path=BASELINES[sets];old=parse(path.read_text(),0,True);diff=[]
    for i,(a,b) in enumerate(zip(parsed['metrics'],old['metrics']),1):
        a,b=comparable(a),comparable(b)
        if a!=b:diff.append(dict(kernel=i,differences={k:[b.get(k),a.get(k)] for k in set(a)|set(b) if a.get(k)!=b.get(k)}))
    if parsed['traffic']!=old['traffic']:diff.append(dict(final_traffic_old=old['traffic'],final_traffic_new=parsed['traffic']))
    return dict(status='PASS_EXACT_ALL_510_PUBLIC_MECHANISM_AND_CYCLE_CONTROL' if not diff else 'FAIL_K0_CALIBRATION_STOP_K1',old_stdout=str(path),old_stdout_sha256=sha(path),old_cycles=old['cycles'],new_cycles=parsed['cycles'],differences=diff)

def collect(run,spec):
    receipt=dict(utc=now(),point=spec['point'],uuid=spec['attempt_uuid'],status='HOLD',performance_accepted=False)
    try:
        term=json.loads((run/'RUN_TERMINAL.json').read_text());require(term['returncode']==0 and term['forced_reason'] is None,'natural_exit0')
        require(term['identity_pass'],'loaded_runtime_identity')
        inp=input_check(spec);text=(run/'simulator.stdout').read_text()
        require('gpgpu-sim_git-commit-e32afdcf_modified_0.0.' in text,'Core_embedded_version')
        a=parse(text,spec['K']);expected=spec['expected_full_default_and_config_echo'];require(len(expected)==267,'267_config_expected')
        diff={k:[v,a['config'].get(k)] for k,v in expected.items() if a['config'].get(k)!=v};require(not diff,'config_echo:'+str(diff))
        require(a['config'].get('-hw_perf_bench_name')==[],'blank_registered_option')
        require(set(a['config'])==set(expected)|{'-hw_perf_bench_name'},'unknown_or_missing_real_option')
        for c in spec['configs']:require(sha(c['path'])==c['sha256'],'frozen_config_changed')
        for c in json.loads((run/'RUN_START.json').read_text())['config_copies']:require(sha(c['path'])==c['sha256'],'run_config_changed')
        cal=calibration(a,spec['sets']) if spec['K']==0 else dict(status='NOT_A_K0_CONTROL')
        receipt.update(status='PASS_STRICT_BOUNDED_OO_MODEL',performance_accepted=True,cycles=a['cycles'],kernels=a['kernel_count'],CTA=a['CTAs'],active_instructions=a['active_instructions'],input=inp,config267='PASS_PLUS_EMPTY_hw_perf_bench_name',calibration=cal,final_metrics=a['metrics'][-1],final_events=a['events'][-1],traffic=a['traffic'],snapshots_validated=510,event_aggregation='LAST_NORMAL_SNAPSHOT_ONLY_SUM_64SM_NOT_KERNEL_SNAPSHOTS',physical_equation='new=allocated+immediate+final_ref+independently_observed_reclaimed_at_event; K0_structural_R=0',unavailable=dict(numeric_load_values=U,per_address_W_scan=U,cross_SM_coherence=U,ordinary_MSHR_internal_occupancy=U,per_sector_generation_raw_terminal_receipt=U,per_line_generation_reuse_causality=U),bounded_invariant_basis='Observed public aggregate balances plus immutable production guards and Y2 independent negative/safety scope; unavailable private receipts are NOT declared measured PASS')
        if spec['K']==0 and (cal['status'].startswith('FAIL') or a['cycles']!=spec['calibration_cycles']):receipt.update(status='FAIL_K0_CALIBRATION_STOP_K1',performance_accepted=False)
        table(run/'KERNEL_STRICT.tsv',[dict(ordinal=i+1,kernel=e['kernel'],cycles=d['gpu_sim_cycle'],total_cycles=d['gpu_tot_sim_cycle'],active_instructions=d['gpu_sim_insn'],cumulative_CTA=d['gpu_tot_issued_cta'],physical_allocated=d['DTC_L1_oo_physical_allocated'],independent_R=a['events'][i]['reclaimed_at_event'] if spec['K'] else U,strict='PASS_AGGREGATE_BOUNDED_MODEL') for i,(d,e) in enumerate(zip(a['metrics'],json.loads((PACK/'ORDERED_KERNELS.json').read_text())))])
        write(run/'NORMAL_EVENT_SNAPSHOTS.json',dict(snapshots=a['events'],aggregation='LAST_ONLY_NEVER_SUM_CUMULATIVE_KERNEL_SNAPSHOTS'))
    except Exception as exc:receipt.update(status='HOLD_STRICT_FAILED',failure=repr(exc))
    write(run/'STRICT.json',receipt)
    return receipt

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--baseline-check',action='store_true');args=ap.parse_args()
    if args.baseline_check:
        rows=[]
        for sets,p in BASELINES.items():
            a=parse(p.read_text(),0,True);rows.append(dict(sets=sets,stdout_sha256=sha(p),cycles=a['cycles'],kernels=a['kernel_count'],instructions=a['active_instructions'],CTA=a['CTAs'],finite11_and_public_balances='PASS'))
        write(PACK/'HISTORICAL_PARSER_CPU_CHECK.json',dict(status='PASS_EXISTING_RAW_PARSER_NO_NEW_SIM',rows=rows));print(rows)
