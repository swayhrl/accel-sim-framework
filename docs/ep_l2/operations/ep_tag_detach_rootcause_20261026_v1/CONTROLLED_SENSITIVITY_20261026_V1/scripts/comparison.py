#!/usr/bin/env python3
"""Read-only extraction and bounded samebinary sensitivity comparison."""
import sys
sys.dont_write_bytecode = True
import json,pathlib,re
import experiment_runtime as v
import acceptance as a
P=pathlib.Path
UNKNOWN='UNKNOWN'
def numeric(value):
    try:return int(value)
    except ValueError:
        try:return float(value.rstrip('%'))
        except ValueError:return value
def wire(line):
    row={}
    for part in line.strip().split('|')[1:]:
        if '=' not in part:continue
        key,value=part.split('=',1)
        a.need(key not in row,'duplicate wire field '+key)
        row[key]=numeric(value)
    return row
def raw_extract(raw):
    """Final native snapshot only. Reads no trace instruction bodies."""
    standard={};b0={};dram={};l1={};clock=None
    for line in P(raw).open(errors='replace'):
        match=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
        if match:
            clock=int(match[1]);standard={};b0={};dram={};l1={}
        if clock is None:continue
        scalar=re.fullmatch(r'([A-Za-z][A-Za-z0-9_:().\[\]-]*)\s*=\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?%?)\s*',line)
        if scalar:standard[scalar[1]]=numeric(scalar[2])
        if line.startswith('EPL2B0V1|scope=application|'):
            row=wire(line);b0[str(row['slice'])]=row
        elif line.startswith('EPL2DRAMV1|scope=application|'):
            row=wire(line);dram[str(row['channel'])]=row
        elif line.startswith('EPL2L1V1|'):
            row=wire(line)
            key=str(row.get('kernel_uid','application'))+':'+str(row.get('scope','UNKNOWN'))
            l1[key]=row
    return {'native_final_cycle':clock,'standard_last_snapshot':standard,
            'b0_slice_last_application':b0,'dram_channel_last_application':dram,
            'l1_last_records':l1,
            'actual_effective_options':a.printed_options(raw)}
def ratio(x,y):
    return x/y if isinstance(x,(int,float)) and isinstance(y,(int,float)) and y else UNKNOWN
def tags(r5):
    g=r5['global_record'];h=g['histograms']
    heads=h['heads_raw_reserved'];elig=h['heads_raw_reserved_eligible']
    return {'final_cycle':r5['final_cycle'],'covered_heads':g['counters']['covered'],
            'skips_and_populations':g['counters'],
            'maximum_RESERVED_target_set':max((r[1] for r in heads),default=UNKNOWN),
            'new_tag_demand_heads':sum(r[-1] for r in heads if r[0] in (2,3)),
            'new_tag_demand_max_RESERVED':max((r[1] for r in heads if r[0] in (2,3)),default=UNKNOWN),
            'new_tag_and_structurally_eligible_heads':sum(r[-1] for r in elig if r[0] in (2,3) and r[2]>0),
            'raw_tag_fail_heads':sum(r[-1] for r in heads if r[0]==3),
            'raw_tag_fail_with_reuse_heads':sum(r[-1] for r in h['heads_raw_reserved_reasonmask'] if r[0]==3 and r[2]&4),
            'histograms':h,'route_joint':g['route_joint'],
            'scope':'same snapshot target-set joint counters; skipped populations remain NA'}
def point(out, accepted_status=None):
    out=P(out)
    accepted=v.read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
    if accepted_status:a.need(accepted['status']==accepted_status,'point not independently accepted')
    a.assert_source(accepted['source_identity'])
    a.need(v.sha(out/'raw.log')==accepted['raw_sha256'],'accepted raw SHA drift')
    for field,file in [('model_summary_sha256','terminal_summary.json'),
                       ('old212_summary_sha256','R4_212_TERMINAL.json'),
                       ('r5_summary_sha256','R5_TAGPRESSURE_TERMINAL.json')]:
        a.need(v.sha(out/file)==accepted[field],'accepted terminal digest drift '+file)
    model=v.read(out/'terminal_summary.json')
    r4=v.read(out/'R4_212_TERMINAL.json')
    r5=v.read(out/'R5_TAGPRESSURE_TERMINAL.json')
    raw=raw_extract(out/'raw.log')
    a.need(raw['native_final_cycle']==model['cycles']==r5['final_cycle']==r4['final_cycle'],
           'final snapshot/decoder cycles disagree')
    a.need(set(raw['b0_slice_last_application'])==set(map(str,range(64))),'missing final64 B0 slices')
    a.need(set(raw['dram_channel_last_application'])==set(map(str,range(32))),'missing final32 DRAM channels')
    for row in raw['b0_slice_last_application'].values():
        a.need(row['completion_cycle']==model['cycles'] and row['samples']>0,'B0 stale/missing samples')
    opts=raw['actual_effective_options']
    clocks=[float(x) for x in opts['-gpgpu_clock_domains'].split(':')]
    a.need(len(clocks)==4 and all(x>0 for x in clocks),'actual clock domain mismatch')
    dr=list(raw['dram_channel_last_application'].values())
    num=sum(r['bandwidth_util_numerator_bytes'] for r in dr)
    den=sum(r['bandwidth_util_denominator_bytes'] for r in dr)
    ro=model['mechanism_metrics']['full_mechanism_records']['readonly']
    raw['derived']={'cycles':model['cycles'],'instructions':model['instructions'],
                    'simulated_seconds_core_clock':model['cycles']/(clocks[0]*1e6),
                    'clock_domains_MHz':dict(zip(('CORE','ICNT','L2','DRAM'),clocks)),
                    'DRAM_bandwidth_util_ratio_of_summed_byte_numerators_denominators':ratio(num,den),
                    'DRAM_bandwidth_util_numerator_bytes':num,
                    'DRAM_bandwidth_util_denominator_bytes':den,
                    'DRAM_successful_read_bytes':sum(r['successful_read_bytes'] for r in dr),
                    'DRAM_successful_write_bytes':sum(r['successful_write_bytes'] for r in dr),
                    'DRAM_scheduler_full_channel_ticks_sum':sum(r['scheduler_full_cycles'] for r in dr),
                    'DRAM_returnq_full_channel_ticks_sum':sum(r['returnq_full_cycles'] for r in dr),
                    'DRAM_cycles_per_channel':{str(r['channel']):r['dram_cycles'] for r in dr},
                    'RO_transactions_sum':sum(r['summary']['transactions'] for r in ro.values()),
                    'RO_merges_sum':sum(r['summary']['merges'] for r in ro.values()),
                    'RO_detached_sum':sum(r['summary']['detached'] for r in ro.values()),
                    'RO_lower_read_bytes_sum':sum(r['resource']['lower_read_bytes'] for r in ro.values()),
                    'RO_per_slice_peaks_do_not_sum':{str(k):{n:r['resource'][n] for n in
                        ('peak_transactions','peak_shared_descriptors','peak_shared_lines')} |
                        {'peak_lower_transactions':r['lower_concurrency']['peak_lower_transactions'],
                         'peak_independent_lower_lines':r['lower_concurrency']['peak_independent_lower_lines']}
                        for k,r in ro.items()},
                    'local_service':model['mechanism_metrics']['local_service']}
    b0=list(raw['b0_slice_last_application'].values())
    event_keys=('c7d_missq_full_block','c7d_l2_to_dram_full_block',
                'c7d_dram_scheduler_full_block','c7d_dram_credit_block',
                'c7d_dram_to_l2_full_block','c7e_dram_issue_attempt',
                'c7e_dram_successful_read_bytes','c7e_dram_successful_write_bytes',
                'c7e_dram_scheduler_full_observed','c7e_dram_scheduler_causal_block',
                'c7e_dram_to_l2_return_path_block')
    mean_keys=('missq_avg','lowerq_avg','descriptor_avg','wad_avg','c7d_reserved_avg',
               'c7d_dram_scheduler_occ_avg')
    max_keys=('missq_max','lowerq_max','descriptor_max','wad_max','c7d_reserved_max',
              'c7d_reserved_set_max','c7d_dram_scheduler_occ_max')
    raw['derived']['B0_events_sum_over_slices_not_global_cycles']={
        k:sum(r[k] for r in b0) if all(k in r for r in b0) else UNKNOWN for k in event_keys}
    raw['derived']['B0_mean_of_reported_slice_time_means_rounded_at_source']={
        k:sum(r[k] for r in b0)/len(b0) if all(k in r for r in b0) else UNKNOWN for k in mean_keys}
    raw['derived']['B0_maximum_of_slice_peaks_not_simultaneous_sum']={
        k:max(r[k] for r in b0) if all(k in r for r in b0) else UNKNOWN for k in max_keys}
    raw['r5_tagpressure']=tags(r5)
    raw['mechanism_waits']=model['mechanism_metrics']['bottleneck']
    raw['identity']={'uuid':accepted['uuid'],'output':str(out),'raw_sha256':accepted['raw_sha256'],
                     'source_identity':accepted['source_identity']}
    return raw
def change(before,after):
    if isinstance(before,(int,float)) and isinstance(after,(int,float)):
        return {'baseline':before,'case':after,'delta':after-before,
                'case_over_baseline':ratio(after,before)}
    if isinstance(before,dict) and isinstance(after,dict):
        return {k:change(before.get(k,UNKNOWN),after.get(k,UNKNOWN)) for k in before.keys()|after.keys()}
    return {'baseline':before,'case':after}
def compare(case):
    v.bind(case)
    B=P(v.B);s=v.pins()
    done=v.read(v.LED/(case+'.DONE.json'))
    out=P(done['output'])
    a.need(out.resolve()==(B/'run/results'/done['uuid']).resolve(),'case output outside UUID root')
    base=point(a.BASE_OUT,'EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED')
    test=point(out,'EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED')
    a.need(base['identity']['source_identity']==test['identity']['source_identity'],'samebinary/source required')
    hist=v.read(B/'control/HISTORICAL_VECTOR_SPEC.json')
    audit=a.option_audit(out/'raw.log',hist,s)
    result={'schema':'EP_MEMORY_PATH_SENSITIVITY_SAMEBINARY_COMPARISON_V1',
            'case':case,'status':'ACCEPTED_POINTS_COMPARED','baseline':base,'variant':test,
            'actual_single_option_audit':audit,
            'baseline_cycles_over_case_cycles':ratio(base['derived']['cycles'],test['derived']['cycles']),
            'case_cycle_change_fraction':ratio(test['derived']['cycles']-base['derived']['cycles'],base['derived']['cycles']),
            'derived_metric_changes':change(base['derived'],test['derived']),
            'standard_counter_changes':change(base['standard_last_snapshot'],test['standard_last_snapshot']),
            'mechanism_wait_changes':change(base['mechanism_waits'],test['mechanism_waits']),
            'claim_boundary':['One finite samebinary clock or L1 MissQ sensitivity, no parameter scan.',
                'Core-cycle completion is the endpoint; DRAM channel ticks use their own clock.',
                'WB/read bytes, RO timing, replacements and detach are observed outcomes, never required equal.',
                'Blocked observations/reasons/slices overlap and cannot be summed into global stall cycles.',
                'Time means rounded by producer; per-slice/channel peaks are not simultaneous global MLP.',
                'LOCAL_XBAR is packet arbitration; byte traffic is not proof of physical NoC bandwidth saturation.',
                'No T-only speedup, numerical SASS output, metadata PPA or physical-hardware performance claim.']}
    a.put_once(out/'SENSITIVITY_COMPARISON.json',result)
    a.put_once(B/'control/SAMEBINARY_COMPARISON.json',result)
    return result
def offline_regression():
    baseline=point(a.BASE_OUT,'EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED')
    a.need(baseline['derived']['cycles']==75039,'baseline endpoint changed')
    a.need(baseline['r5_tagpressure']['raw_tag_fail_heads']==0,'baseline TagFAIL projection regression')
    return {'status':'OFFLINE_BASELINE_COMPARISON_EXTRACTION_ONLY','new_acceptance_granted':False,
            'cycles':baseline['derived']['cycles'],
            'dram_channels':len(baseline['dram_channel_last_application']),
            'B0_slices':len(baseline['b0_slice_last_application']),
            'bandwidth_util':baseline['derived']['DRAM_bandwidth_util_ratio_of_summed_byte_numerators_denominators'],
            'raw_sha256':baseline['identity']['raw_sha256'],
            'maximum_RESERVED_target_set':baseline['r5_tagpressure']['maximum_RESERVED_target_set']}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('case',nargs='?');p.add_argument('--offline-regression',action='store_true')
    x=p.parse_args()
    print(json.dumps(offline_regression() if x.offline_regression else compare(x.case),indent=2,sort_keys=True))

