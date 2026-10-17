"""Pure CPU reduction helpers; only compare completed, supplied kernel indexes.

No trace reads, file opens, launches, values or runtime ordering claims.
Line masks and PC masks are unions across a segment, not dynamic event pairs.
"""


def sectors(byte_mask):
    return sum(1<<s for s in range(4) if (byte_mask>>(32*s))&((1<<32)-1))


def compare(previous,current):
    rr=wr=rr_bytes=wr_bytes=0
    pc_pairs={}
    for line,now in current['lines'].items():
        old=previous['lines'].get(line)
        if old is None or not now['r']:
            continue
        if old['r']:
            rr+=1
            rr_bytes+=bool(old['r'] & now['r'])
        if old['w']:
            wr+=1
            wr_bytes+=bool(old['w'] & now['r'])
            for wp,wm in old['w_pcs'].items():
                for rp,rm in now['r_pcs'].items():
                    counts=pc_pairs.setdefault((wp,rp),[0,0,0])
                    counts[0]+=1
                    counts[1]+=bool(wm & rm)
                    counts[2]+=bool(sectors(wm) & sectors(rm))
    return dict(prior_read_current_read_distinct_lines=rr,
                prior_read_current_read_byte_overlap_lines=rr_bytes,
                prior_write_current_read_distinct_lines=wr,
                prior_write_current_read_byte_overlap_lines=wr_bytes,
                pc_pairs=[dict(write_pc=w,read_pc=r,line_alias_count=n[0],
                    byte_overlap_line_count=n[1],sector_overlap_line_count=n[2],
                    ordering='LIST_KERNEL_ORDINAL_CANDIDATE_ONLY',
                    actual_happens_before='UNAVAILABLE',actual_old_mapping_exposure='UNAVAILABLE')
                    for (w,r),n in sorted(pc_pairs.items())])


def reusable_distinct_lines(prior_indexes,current):
    current_reads={line for line,v in current['lines'].items() if v['r']}
    prior_reads={line for p in prior_indexes for line,v in p['lines'].items() if v['r']}
    prior_writes={line for p in prior_indexes for line,v in p['lines'].items() if v['w']}
    return dict(read_lines_seen_in_any_prior_kernel=len(current_reads & prior_reads),
                read_lines_written_in_any_prior_kernel=len(current_reads & prior_writes))
