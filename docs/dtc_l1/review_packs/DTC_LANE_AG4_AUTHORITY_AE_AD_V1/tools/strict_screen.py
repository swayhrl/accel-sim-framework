"""Independent AG full-input strict/calibration parser. Never launches or writes old raw."""
from common import *
import io
import re
import importlib.util

FINITE=['samples','pib_integral','physical_integral','collected_sectors','fully_ready_to_complete_sum',
        'retired','ready_to_collect_sum','collection_cycles','wb_wait','map_loss_to_free_sum','map_loss_to_free_count']
CALIBRATION_CYCLES={'GEMM':1071405,'Gaussian':3278356}


def require(ok,why):
    if not ok:raise ValueError(why)


def ordered(workload):
    with (PACK/'inputs/T/inputs/KERNEL_BODY_AUDIT.tsv').open() as f:
        rows=[r for r in csv.DictReader(f,delimiter='\t') if r['workload'].lower()==workload.lower()]
    return sorted(rows,key=lambda r:int(r['ordinal']))


def echo(text):
    result={}
    for line in text.splitlines():
        m=re.match(r'^(-\S+)\s+(.*?)\s*#',line)
        if m:
            require(m[1] not in result or result[m[1]]==m[2].split(),'conflicting_effective_option:'+m[1])
            result[m[1]]=m[2].split()
    return result


def numeric(block):
    result={}
    for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',block,re.M):
        if k in result:
            require(not k.startswith(('DTC_','gpu_','gpgpu_n_mem_','icnt_total_')),'duplicate_numeric_metric:'+k)
        result[k]=int(v)
    return result


def traffic(block):
    buckets={}
    for a,b,v in re.findall(r'^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$',block,re.M):
        k=a+':'+b;require(k not in buckets,'duplicate_L2_bucket');buckets[k]=int(v)
    dram=re.findall(r'^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',block,re.M)
    require(len(dram)==20 and {int(i) for i,_ in dram}==set(range(20)),'DRAM_population_20_controllers')
    controllers={str(int(i)):{k:int(v) for k,v in re.findall(r'(n_cmd|n_nop|n_act|n_pre|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',line)} for i,line in dram}
    reads=sum(buckets['GLOBAL_ACC_R:'+k] for k in ['HIT','HIT_RESERVED','MISS','SECTOR_MISS'])
    require(reads==buckets['GLOBAL_ACC_R:TOTAL_ACCESS'],'L2_accepted_read_bucket_partition')
    return dict(L2_buckets=buckets,L2_accepted_read_32B_sectors=reads,L2_read_payload_bytes=32*reads,
        DRAM_controllers=controllers,DRAM_atom_bytes=32,
        DRAM_issued_read_atoms=sum(r['n_rd']+r['n_rd_L2_A'] for r in controllers.values()),
        DRAM_issued_write_atoms=sum(r['n_write']+r['n_wr_bk'] for r in controllers.values()),
        DRAM_read_payload_bytes=32*sum(r['n_rd']+r['n_rd_L2_A'] for r in controllers.values()),
        DRAM_write_payload_bytes=32*sum(r['n_write']+r['n_wr_bk'] for r in controllers.values()),
        DRAM_n_ref_event='UNAVAILABLE_INHERITED_UNINITIALIZED_FIELD_RAW_PRESERVED')


def parse_full(text,workload):
    expected=ordered(workload)
    names=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',text,re.M))
    require(len(names)==len(expected),'full_ordered_kernel_count')
    require([m[1] for m in names]==[r['kernel'] for r in expected],'full_ordered_kernel_names')
    original=(PACK/f'inputs/T/inputs/{workload}_kernelslist.g').read_text().splitlines()
    spec=json.loads((PACK/f'inputs/T/inputs/{workload}_OO128_SPEC.json').read_text())
    commands=[]
    for line in text.splitlines():
        if line.startswith('Processing kernel '):commands.append(Path(line[len('Processing kernel '):]).name)
        elif line.startswith('launching memcpy command : '):commands.append(line[len('launching memcpy command : '):])
    require(commands==[line for line in original if line.strip()],'all_original_commands_order_and_memcpy')
    require(re.findall(r'^Processing kernel (\S+)$',text,re.M)==[r['path'] for r in expected],'exact_original_member_paths')
    require(text.count('GPGPU-Sim: *** exit detected ***')==1,'one_natural_exit_marker')
    require(text.count('GPGPU-Sim: *** simulation thread exiting ***')==1,'one_simulation_thread_exit_marker')
    require('performance model initialization complete.' in text,'real_model_initialization')
    require(not re.search(r'assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|output mismatch',text,re.I),'forbidden_runtime_signature')
    require(not re.search(r'^DTC_INVALIDATE_V1_(SNAPSHOT|SUMMARY)',text,re.M),'K0_has_no_K1_only_export')
    blocks=[text[m.start():names[i+1].start() if i+1<len(names) else len(text)] for i,m in enumerate(names)]
    metrics=[];insns=ctas=0;previous=None
    for i,(block,row) in enumerate(zip(blocks,expected),1):
        d=numeric(block);insns+=int(row['active_thread_instructions']);ctas+=int(row['complete_ctas'])
        require(d['kernel_launch_uid']==i,'ordered_launch_UID')
        require(d['gpu_sim_insn']==int(row['active_thread_instructions']) and d['gpu_tot_sim_insn']==insns and d['gpu_tot_issued_cta']==ctas,'per_kernel_full_instructions_CTA:'+str(i))
        require('DTC_L1_mode = PAPER_OO' in block,'OO_mode')
        v=lambda key:d['DTC_L1_'+key]
        f=lambda key:d['DTC_SERVICE_V1_'+key]
        require(all(v(k)==0 for k in ['oo_pib_occupancy','oo_inflight_current','oo_active_refs','lower_outstanding']),'terminal_ownership_credit_drain')
        require(v('lower_credit_acquired')==v('lower_credit_released')==v('oo_lower_created')==v('oo_lower_issued')==v('oo_lower_responses'),'lower_create_inject_response_credit_conservation')
        require(v('oo_completion_dependency_count')==v('oo_completion_dependency_closed')==v('oo_valid_hits')+v('oo_pending_hits')+v('oo_new_misses'),'Ref_dependency_closed_population')
        require(sum(v('m4_'+x+'_admits') for x in ['store','atomic','bypass_load','proxy_fence'])==v('m4_source_completions')==v('m4_observation_retires'),'source_sidecar_conservation')
        require(0<=v('oo_physical_allocated')<=640*64,'physical_640_per_SM_capacity')
        require(v('oo_new_misses')==v('oo_physical_allocated')+v('oo_immediate_reclaims')+v('oo_final_ref_reclaims'),'K0_physical_allocation_conservation')
        require(all('DTC_SERVICE_V1_'+k in d for k in FINITE),'all_common_finite_fields_present')
        require(f('samples')==64*d['gpu_tot_sim_cycle'],'finite_population_64SM')
        require(f('fully_ready_to_complete_sum')==f('ready_to_collect_sum')+f('collection_cycles')+f('wb_wait'),'finite_postready_scope_decomposition')
        require(f('map_loss_to_free_count')==v('oo_immediate_reclaims')+v('oo_final_ref_reclaims'),'K0_map_loss_reclaim_population')
        if previous:
            require(all(f(k)>=previous['DTC_SERVICE_V1_'+k] for k in FINITE),'cumulative_finite_monotonic')
        previous=d;metrics.append(d)
    require(insns==spec['expected_instructions'],'whole_input_instruction_total')
    return dict(workload=workload,kernel_count=len(expected),CTA=ctas,active_instructions=insns,
        cycles=metrics[-1]['gpu_tot_sim_cycle'],metrics=metrics,traffic=traffic(blocks[-1]),effective_options=echo(text))


def common_comparable(d):
    return {k:v for k,v in d.items() if k.startswith(('DTC_L1_','DTC_SERVICE_V1_')) or
        k in ['gpu_sim_cycle','gpu_tot_sim_cycle','gpu_sim_insn','gpu_tot_sim_insn','gpu_tot_issued_cta',
              'gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','icnt_total_pkts_mem_to_simt','icnt_total_pkts_simt_to_mem']}


def pipeline_contract(text,arm,final,sms=64):
    require('DTC_COLLECT_WB_PIPELINE_V1' not in text,'AC_not_in_AG3')
    if arm!='AD':
        require('DTC_PROGRESSIVE_WAKE_V1' not in text,'AD_OFF_no_ON_only_export')
        return dict(status='UNAVAILABLE_OFF_NOT_PRINTED',direct_comparison=False)
    frames=list(re.finditer(r'^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN .*?^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_END version=1$',text,re.M|re.S))
    require(bool(frames),'AD_ON_complete_normal_export')
    frame=frames[-1][0];summary={};fanout={};ldst={}
    for line in frame.splitlines():
        pairs=re.findall(r'(\w+)=(\d+)',line);values={k:int(v) for k,v in pairs}
        require(len(values)==len(pairs),'AD_duplicate_field')
        if line.startswith('DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN '):
            require(values['cycle']==final['gpu_tot_sim_cycle'] and values['sms']==sms,'AD_public_frame_cycle_population')
        elif line.startswith('DTC_PROGRESSIVE_WAKE_V1 '):
            sm=values['sm'];require(sm not in summary,'AD_duplicate_summary');summary[sm]=values
        elif line.startswith('DTC_PROGRESSIVE_WAKE_V1_FANOUT '):
            key=(values['sm'],values['bin']);require(key not in fanout,'AD_duplicate_fanout');fanout[key]=values['count']
        elif line.startswith('DTC_PROGRESSIVE_WAKE_V1_LDST '):
            sm=values['sm'];require(sm not in ldst,'AD_duplicate_LDST');ldst[sm]=values
    require(set(summary)==set(ldst)==set(range(sms)),'AD_all_SM_rows')
    require(set(fanout)=={(s,b) for s in range(sms) for b in range(33)},'AD_all_SM_fanout_bins')
    for sm,row in summary.items():
        require(sum(fanout[sm,b] for b in range(33))==row['broadcasts'],'AD_fanout_partition')
        require(row['last_notify_cycle_sum']-row['first_notify_cycle_sum']==row['span_sum'],'AD_span_conservation')
    require(sum(row['retired'] for row in ldst.values())==final['DTC_SERVICE_V1_retired'],'AD_common_retire_population_join')
    return dict(status='PASS_AD_ON_ONLY_DIAGNOSTIC',direct_comparison=False,summary=summary,fanout={str(s)+':'+str(b):v for (s,b),v in fanout.items()},ldst=ldst,post_ready_condition='AD_OWN_NOTIFIED_READY_DIFFERENT_FROM_BASE_BROADCAST_DONE',OFF='UNAVAILABLE_NOT_ZERO')


def compare_calibration(parsed,reference):
    differences=[]
    require(parsed['cycles']==CALIBRATION_CYCLES[parsed['workload']],'fixed_BASE_integer_cycle_calibration')
    require(len(parsed['metrics'])==len(reference['kernel_common_metrics']),'calibration_full_population')
    for i,(new,old) in enumerate(zip(parsed['metrics'],reference['kernel_common_metrics']),1):
        delta={k:[v,new.get(k)] for k,v in old.items() if new.get(k)!=v}
        if delta:differences.append(dict(ordinal=i,common_metric_differences=delta))
    if parsed['traffic']!=reference['traffic']:differences.append(dict(traffic_expected=reference['traffic'],traffic_actual=parsed['traffic']))
    require(not differences,'BASE_common_metric_or_traffic_calibration_mismatch:'+json.dumps(differences)[:4000])
    return dict(status='PASS_FULL_INPUT_CYCLES_AND_ALL_FROZEN_COMMON_METRICS',
        control_stdout_sha256=reference['stdout_sha256'],cycles=parsed['cycles'],compared_kernels=len(parsed['metrics']))


def input_identity(spec):
    require(sha(spec['trace_list'])==spec['trace_list_sha256'],'original_list_SHA256')
    members=[r for r in json.loads((PACK/'INPUT_STAT_IDENTITIES.json').read_text()) if r['workload']==spec['workload']]
    require(len(members)==spec['expected_kernels'],'frozen_member_population')
    for m in members:
        s=Path(m['path']).stat()
        require(m['stat_identity']=={k:getattr(s,k) for k in m['stat_identity']},'post_SHA_member_mutation:'+m['path'])
    return dict(status='PASS_FRESH_FROZEN_SHA_PLUS_CURRENT_STAT_STABILITY',members=len(members),
        member_table_sha256=sha(PACK/'ORIGINAL_MEMBERS_SHA256.tsv'),list_sha256=spec['trace_list_sha256'])


def collect(run,spec):
    result=dict(utc=now(),arm=spec['arm'],workload=spec['workload'],attempt_uuid=spec['attempt_uuid'],
        status='HOLD_STRICT_FAILED',performance_accepted=False,cycles='UNAVAILABLE')
    try:
        term=json.loads((run/'RUN_TERMINAL.json').read_text())
        require(term['returncode']==0 and term['forced_reason'] is None and term['identity_pass'],'natural_exit0_and_actual_loaded_identity')
        identity=input_identity(spec)
        text=(run/'simulator.stdout').read_text()
        require(not re.search(r'assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|output mismatch',
            (run/'simulator.stderr').read_text(),re.I),'forbidden_stderr_runtime_signature')
        require(spec['expected_embedded_core_version'] in text,'actual_Core_embedded_version')
        require(spec['expected_embedded_framework_version'] in text,'actual_Framework_embedded_version')
        parsed=parse_full(text,spec['workload'])
        pipeline=pipeline_contract(text,spec['arm'],parsed['metrics'][-1])
        require(parsed['effective_options']==spec['expected_full_effective_options'],'all_effective_options_exact_population_and_values')
        require(parsed['effective_options']['-gpgpu_dtc_l1_invalidate_on_source_event']==['0'],'fixed_K0')
        for config in spec['configs']:require(sha(config['path'])==config['sha256'],'registered_config_mutation')
        for config in json.loads((run/'RUN_START.json').read_text())['config_copies']:
            require(sha(config['path'])==config['sha256'],'actual_config_copy_mutation')
        calibration='NOT_BASE_POINT'
        if spec['arm']=='BASE':
            ref=json.loads((PACK/f'controls/{spec["workload"]}_CALIBRATION_REFERENCE.json').read_text())
            calibration=compare_calibration(parsed,ref)
        result.update(status='PASS_STRICT_DISCOVERY_OPT_BOUNDED_MODEL',performance_accepted=True,
            cycles=parsed['cycles'],kernels=parsed['kernel_count'],active_instructions=parsed['active_instructions'],
            CTA=parsed['CTA'],input_identity=identity,calibration=calibration,traffic=parsed['traffic'],
            final_metrics=parsed['metrics'][-1],K1_only_fields='UNAVAILABLE_K0_NOT_PRINTED',
            AC_pipeline_diagnostic=pipeline,
            common_metric_scope='LAST_CUMULATIVE_FINAL_SNAPSHOT_NOT_SUM_OF_KERNEL_SNAPSHOTS',
            numeric_load_values='UNAVAILABLE',cross_SM_query_reuse='UNAVAILABLE',private_terminal_generation_sector_receipts='UNAVAILABLE')
        table(run/'KERNEL_STRICT.tsv',[dict(ordinal=i,kernel=row['kernel'],cycles=d['gpu_sim_cycle'],total_cycles=d['gpu_tot_sim_cycle'],
            active_instructions=d['gpu_sim_insn'],cumulative_CTA=d['gpu_tot_issued_cta'],status='PASS_BOUNDED_PUBLIC_INVARIANTS')
            for i,(d,row) in enumerate(zip(parsed['metrics'],ordered(spec['workload'])),1)])
    except Exception as exc:
        result['failure']=repr(exc)
    write(run/'STRICT.json',result,exclusive=True)
    return result


def prepare_references():
    source=json.loads(json.dumps(list(csv.DictReader(io.StringIO(blob(FW_REPO,T,T_PACK+'/FULL_MATRIX.tsv').decode()),delimiter='\t'))))
    rows=[]
    for workload in ['GEMM','Gaussian']:
        original=next(r for r in source if r['candidate']=='T1-C' and r['workload']==workload)
        path=Path(original['raw_dir'])/'simulator.stdout'
        require(sha(path)==original['stdout_sha256'],'published_T_full_control_SHA256')
        data=parse_full(path.read_text(),workload)
        require(data['cycles']==CALIBRATION_CYCLES[workload],'published_T_control_integer_cycles')
        reference=dict(role='OLD_K0_CALIBRATION_REFERENCE_ONLY_NOT_AG_BASE_NOT_AA5_PREFIX',
            workload=workload,source_commit=T,stdout=str(path),stdout_sha256=sha(path),
            cycles=data['cycles'],active_instructions=data['active_instructions'],CTA=data['CTA'],
            kernel_common_metrics=[common_comparable(d) for d in data['metrics']],traffic=data['traffic'],
            effective_options=data['effective_options'],new_simulations_started=0)
        write(PACK/f'controls/{workload}_CALIBRATION_REFERENCE.json',reference)
        rows.append(dict(workload=workload,cycles=data['cycles'],kernels=data['kernel_count'],
            source_stdout_sha256=reference['stdout_sha256'],common_per_kernel_comparison=True,complete_traffic=True))
    write(PACK/'CALIBRATION_REFERENCE_CPU_CHECK.json',dict(status='PASS_BOTH_PUBLISHED_FULL_OLD_K0_CONTROLS_PARSED',
        rows=rows,strict_sha256=sha(Path(__file__)),new_simulations_started=0,AA5_prefix_used=False))
    print(json.dumps(rows))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--prepare-references',action='store_true');a=p.parse_args()
    if a.prepare_references:prepare_references()
