"""Source-defined r19 pressure/residency extraction; missing observations stay missing."""
from pathlib import Path
from campaign_r0 import ft_metrics
from validate import require

SOURCE_CORE='7b8e6ac70b8fe0f1bd37efca11acb5284938825d'
SUM_FIELDS=('samples','c7d_l2_to_dram_full_block','c7d_dram_issue_eligible',
    'c7d_dram_scheduler_full_block','c7d_dram_credit_block','c7d_dram_returnq_block',
    'c7d_dram_to_l2_full_block','c7e_dram_issue_attempt','c7e_dram_successful_read_issues',
    'c7e_dram_successful_write_issues','c7e_dram_successful_read_bytes',
    'c7e_dram_successful_write_bytes','c7e_dram_scheduler_causal_block',
    'c7d_wad_full_events','c7d_wad_hazard_events','bank_wait_cycles','bank_logical_ops')


def parse_rows(lines):
    app={};windows=[];l2windows=[]
    for line in lines:
        if line.startswith(('EPL2B0V1|','EPL2DRAMV1|')):
            r=dict(p.split('=',1) for p in line.strip().split('|')[1:])
            if line.startswith('EPL2B0V1|') and r['scope']=='application':
                i=int(r['slice']);require(i not in app,'Repeated application aggregate');app[i]=r
            elif line.startswith('EPL2DRAMV1|') and r['scope']=='window':windows.append(r)
            elif line.startswith('EPL2B0V1|') and r['scope']=='window':l2windows.append(r)
    require(set(app)==set(range(64)),'Exact64 application pressure rows required')
    require(windows,'Missing detailed-DRAM window samples; no invented zero')
    totals={n:sum(int(r[n]) for r in app.values()) for n in SUM_FIELDS}
    samples=totals['samples'];eligible=totals['c7d_dram_issue_eligible'];require(samples>0 and eligible>0,'Pressure denominators absent/zero')
    ticks=sum(int(r['dram_cycles']) for r in windows);require(ticks>0,'Window DRAM ticks absent')
    agg={**totals,'L2_to_DRAM_full_per_sampled_L2_slice_cycle':totals['c7d_l2_to_dram_full_block']/samples,
        'scheduler_full_per_actual_issue_attempt':totals['c7d_dram_scheduler_full_block']/eligible,
        'credit_block_per_actual_issue_attempt':totals['c7d_dram_credit_block']/eligible,
        'returnq_block_per_actual_issue_attempt':totals['c7d_dram_returnq_block']/eligible,
        'successful_packets_per_GPU_slice_sample':(totals['c7e_dram_successful_read_issues']+totals['c7e_dram_successful_write_issues'])/samples,
        'WAD_lifetime_mean_of64_truncated_slice_avgs':sum(int(r['c7d_wad_lifetime_avg']) for r in app.values())/64,
        'WAD_lifetime_max_across_slices':max(int(r['c7d_wad_lifetime_max']) for r in app.values()),
        'WAD_occupancy_max_across_slices':max(int(r['wad_max']) for r in app.values()),
        'L2_to_DRAM_queue_peak_across_slices':max(int(r['lowerq_max']) for r in app.values()),
        'scheduler_occupancy_peak_across_windows':max(int(r['scheduler_occ_max']) for r in windows),
        'returnq_occupancy_peak_across_windows':max(int(r['returnq_occ_max']) for r in windows),
        'window_sampled_DRAM_channel_ticks':ticks,
        'scheduler_full_per_sampled_DRAM_channel_tick':sum(int(r['scheduler_full_cycles']) for r in windows)/ticks,
        'returnq_full_per_sampled_DRAM_channel_tick':sum(int(r['returnq_full_cycles']) for r in windows)/ticks,
        'window_successful_packets_per_sampled_DRAM_channel_tick':sum(int(r['successful_read_issues'])+int(r['successful_write_issues']) for r in windows)/ticks}
    return {'source_core':SOURCE_CORE,'aggregate':agg,'DRAM_windows':windows,'L2_windows':l2windows,
        'limitations':['L2-full denominator is sampled L2 slice-cycles, not an unrecorded eligible-read opportunity count.',
        'DRAM-issue opportunity and channel-tick window denominators are distinct; no equal-tick assumption across clock regimes.',
        'DRAM windows cover emitted5000-GPU-cycle intervals only; partial terminal tail is not invented.',
        'WAD average is mean of source-truncated per-slice lifetime averages, not global weighted mean or p95.',
        'FT staging_lifetime is a separate source metric; U slot release differs from WAD lifetime.',
        'No legacy C1 resident headroom, no additive total GPU stall or numerical SASS claim.']}


def analyze(directory):
    with (directory/'raw.log').open() as stream:r=parse_rows(stream)
    r['FT_staging']=ft_metrics(directory)
    return r
