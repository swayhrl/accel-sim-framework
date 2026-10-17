#!/usr/bin/env python3
"""Guarded single-worker CPU scan of only the pinned Gaussian/GEMM originals.

Default is admission-only, with zero trace body opens. --scan is also refused
before opening any body whenever resource/U/source admission fails. No tools,
decoder mutations, simulator invocations, subprocesses or automatic restarts.
Local derived indexes are not automatically published into the review pack.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import sys
import time
from datetime import datetime, timezone
sys.dont_write_bytecode=True
from access_semantics import ContractGap, decode_record, line_masks, WarpWriteHistory

PACK=Path(__file__).resolve().parents[1]
SCRATCH=Path('/workspace/dtc-lane-w-trace-semantics-174-v1/scan')
MAX_LINE_ENTRIES=250000
MAX_INDEX_BYTES=128*1024*1024
MAX_OUTPUT_BYTES=2*1024*1024*1024
MAX_WARP_LINE_ENTRIES=250000


def tsv(name):
    with (PACK/name).open() as f:
        return list(csv.DictReader(f,delimiter='\t'))


def admission():
    reasons=[]
    io=Path('/proc/pressure/io').read_text()
    avg10=float(io.split('full avg10=')[1].split()[0])
    if avg10>=5:
        reasons.append('IO_FULL_AVG10_GE_5_PERCENT')
    disk=shutil.disk_usage(PACK)
    if disk.used/(disk.used+disk.free)>=.98:
        reasons.append('FILESYSTEM_USED_GE_98_PERCENT')
    memory=Path('/proc/meminfo').read_text()
    available=int(re.search(r'MemAvailable:\s+(\d+)',memory).group(1))*1024
    if available<32*1024**3:
        reasons.append('HOST_AVAILABLE_MEMORY_LT_32_GIB')
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>1024*1024:
        reasons.append('SCANNER_RSS_PEAK_GE_1_GIB')
    u_pids=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit() or int(entry.name)==os.getpid():
            continue
        try:
            command=(entry/'cmdline').read_bytes()
        except (OSError,ProcessLookupError):
            continue
        if b'/workspace/dtc-t1c-holdout-174-v1/' in command:
            u_pids.append(int(entry.name))
    if u_pids:
        reasons.append('U_PATH_PROCESS_OBSERVED')
    for r in tsv('SOURCE_IDENTITY_CHECKS.tsv'):
        if hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()!=r['expected_sha256']:
            reasons.append('FROZEN_SOURCE_OR_PROOF_CHANGED:'+r['path'])
    for name,receipt_name,key in [('access_semantics.py','CPU_ACCESS_SEMANTICS_PREFLIGHT.json','analyzer_sha256'),
                                  ('stream_access_scan.py','CPU_STREAM_PREFLIGHT.json','runner_sha256')]:
        try:
            receipt=json.loads((PACK/receipt_name).read_text())
            if hashlib.sha256((PACK/'scripts'/name).read_bytes()).hexdigest()!=receipt[key]:
                reasons.append('CPU_PREFLIGHT_IDENTITY_MISMATCH:'+name)
        except (OSError,KeyError,ValueError):
            reasons.append('CPU_PREFLIGHT_RECEIPT_MISSING:'+name)
    return dict(utc=datetime.now(timezone.utc).isoformat(),reasons=reasons,
        io=io,filesystem_free=disk.free,available_memory=available,u_path_pids=u_pids,
        decision='REFUSE_BEFORE_BODY_OPEN' if reasons else 'ADMISSIBLE_CPU_ONLY')


def save_json(path,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    if len(data)>MAX_INDEX_BYTES:
        raise ContractGap('PER_KERNEL_INDEX_OUTPUT_LIMIT')
    total=sum(p.stat().st_size for p in SCRATCH.glob('*.json'))
    if total+len(data)>MAX_OUTPUT_BYTES:
        raise ContractGap('TOTAL_INDEX_OUTPUT_LIMIT')
    tmp=path.with_suffix('.tmp')
    tmp.write_bytes(data)
    os.replace(tmp,path)


class KernelAccumulator:
    def __init__(self):
        self.lines={}
        self.classes=Counter()
        self.pcs=Counter()
        self.warp_history=WarpWriteHistory()
        self.warp_pairs=Counter()
        self.records=0
        self.active_instructions=0

    def begin_warp(self):
        # A complete warp stream has ended before this is called. Its ordered
        # history has no relevance to another warp, and need not be retained.
        self.warp_history=WarpWriteHistory()

    def observe(self,r):
        self.records+=1
        self.active_instructions+=r.mask.bit_count()
        self.classes[r.access_class]+=1
        if r.access_class not in ('CACHEABLE_GLOBAL_LOAD','ORDINARY_STORE','ATOMIC','BYPASS_GLOBAL_LOAD'):
            return
        self.pcs[(hex(r.pc),r.opcode,r.access_class)]+=1
        for candidate in self.warp_history.observe(r):
            key=(hex(candidate['write_pc']),hex(candidate['read_pc']),
                 'BYTE_OVERLAP' if candidate['byte_overlap'] else 'LINE_ALIAS_ONLY')
            self.warp_pairs[key]+=1  # Count read-record/line/write-PC candidates.
        if len(self.warp_history.writes)>MAX_WARP_LINE_ENTRIES:
            raise ContractGap('INTRA_WARP_HISTORY_LIMIT')
        for line,(bm,sm) in line_masks(r).items():
            key=str(line)
            entry=self.lines.setdefault(key,{'r':0,'w':0,'r_pcs':{},'w_pcs':{}})
            kind='r' if r.access_class=='CACHEABLE_GLOBAL_LOAD' else 'w' if r.access_class in ('ORDINARY_STORE','ATOMIC') else None
            if kind:
                entry[kind]|=bm
                bypc=entry[kind+'_pcs']
                pc=hex(r.pc)
                bypc[pc]=bypc.get(pc,0)|bm
            # Bypass PCs are counted, but cannot establish DTC lookup reuse.
        if len(self.lines)>MAX_LINE_ENTRIES:
            raise ContractGap('DISTINCT_LINE_MEMORY_LIMIT')

    def result(self):
        return dict(warp_records=self.records,active_thread_instructions=self.active_instructions,
            classes=dict(self.classes),pcs=[dict(pc=pc,opcode=op,access_class=c,warp_records=n)
                for (pc,op,c),n in sorted(self.pcs.items())],
            same_warp_candidates=[dict(write_pc=w,read_pc=r,kind=k,read_record_line_write_pc_candidates=n,
                ordering='SAME_WARP_TRACE_RECORD_ORDER_ONLY') for (w,r,k),n in sorted(self.warp_pairs.items())],
            distinct_read_lines=sum(bool(v['r']) for v in self.lines.values()),
            distinct_write_lines=sum(bool(v['w']) for v in self.lines.values()),
            same_kernel_line_aliases=sum(bool(v['r'] and v['w']) for v in self.lines.values()),
            same_kernel_byte_overlaps=sum(bool(v['r'] & v['w']) for v in self.lines.values()),
            cross_warp_order='UNKNOWN',actual_happens_before='UNAVAILABLE',actual_load_values='UNAVAILABLE',lines=self.lines)


def consume_stream(lines, expected, tick=lambda:None):
    """Strict CTA/warp streaming structure, usable with StringIO CPU fixtures."""
    header={}
    body=False
    active_tb=False
    ctas=set()
    warp_ids=set()
    warp=None
    cta=None
    declared=None
    ordinal=0
    completed_warps=0
    last_opcode=None
    acc=KernelAccumulator()

    def finish_warp():
        nonlocal completed_warps
        if warp is None:
            return
        if declared is None or ordinal!=declared:
            raise ContractGap('DECLARED_WARP_RECORD_COUNT_MISMATCH')
        if declared and last_opcode!='EXIT':
            raise ContractGap('WARP_WITHOUT_TERMINAL_EXIT')
        completed_warps+=1

    for raw in lines:
        tick()
        line=raw.strip()
        if not line:
            continue
        if not body:
            if line.startswith('-') and '=' in line:
                k,v=line[1:].split('=',1)
                header[k.strip()]=v.strip()
                continue
            if line.startswith('#') and line!='#BEGIN_TB':
                body=True
                continue
            raise ContractGap('MISSING_KERNEL_HEADER_TERMINATOR')
        if line=='#BEGIN_TB':
            if active_tb:
                raise ContractGap('NESTED_CTA')
            active_tb=True
            cta=warp=declared=None
            ordinal=0
            warp_ids=set()
            continue
        if line=='#END_TB':
            if not active_tb or cta is None:
                raise ContractGap('END_CTA_WITHOUT_START')
            finish_warp()
            block=tuple(map(int,re.findall(r'\d+',header['block dim'])))
            if len(warp_ids)!=math.ceil(math.prod(block)/32):
                raise ContractGap('MISSING_DECLARED_CTA_WARPS')
            active_tb=False
            warp=None
            continue
        if not active_tb:
            raise ContractGap('BODY_RECORD_OUTSIDE_CTA')
        if line.startswith('thread block ='):
            if cta is not None:
                raise ContractGap('DUPLICATE_CTA_HEADER')
            cta=tuple(map(int,line.split('=',1)[1].split(',')))
            grid=tuple(map(int,re.findall(r'\d+',header['grid dim'])))
            if len(cta)!=3 or len(grid)!=3 or any(not 0<=x<g for x,g in zip(cta,grid)) or cta in ctas:
                raise ContractGap('INVALID_OR_DUPLICATE_CTA')
            ctas.add(cta)
        elif line.startswith('warp ='):
            finish_warp()
            warp=int(line.split('=',1)[1])
            block=tuple(map(int,re.findall(r'\d+',header['block dim'])))
            if warp in warp_ids or not 0<=warp<math.ceil(math.prod(block)/32):
                raise ContractGap('DUPLICATE_OR_INVALID_WARP_ID')
            warp_ids.add(warp)
            declared=None
            ordinal=0
            last_opcode=None
            acc.begin_warp()
        elif line.startswith('insts ='):
            if warp is None or declared is not None:
                raise ContractGap('UNEXPECTED_INSTS_DECLARATION')
            declared=int(line.split('=',1)[1])
            if declared<0:
                raise ContractGap('NEGATIVE_RECORD_COUNT')
        else:
            if cta is None or warp is None or declared is None or ordinal>=declared:
                raise ContractGap('RECORD_WITHOUT_STRUCTURAL_IDENTITY')
            ordinal+=1
            r=decode_record(line,int(header.get('accelsim tracer version','0')),
                int(header.get('enable lineinfo','0')),cta,warp,ordinal)
            last_opcode=r.opcode.split('.')[0]
            acc.observe(r)
    if active_tb:
        raise ContractGap('TRUNCATED_CTA')
    for key in ('kernel name','grid dim','block dim','binary version'):
        if key not in header:
            raise ContractGap('MISSING_REQUIRED_KERNEL_HEADER:'+key)
    if header['kernel name']!=expected['kernel'] or int(header['binary version'])!=int(expected['binary_version']):
        raise ContractGap('KERNEL_NAME_OR_BINARY_VERSION_MISMATCH')
    if int(header.get('accelsim tracer version','0'))!=int(expected['trace_version']):
        raise ContractGap('TRACE_VERSION_MISMATCH')
    for actual,key in [(len(ctas),'complete_ctas'),(completed_warps,'complete_warps'),
                       (acc.records,'warp_instruction_records'),(acc.active_instructions,'active_thread_instructions')]:
        if actual!=int(expected[key]):
            raise ContractGap('ACCEPTED_BODY_PROOF_MISMATCH:'+key)
    if len(ctas)!=math.prod(tuple(map(int,re.findall(r'\d+',header['grid dim'])))):
        raise ContractGap('INCOMPLETE_GRID')
    result=acc.result()
    observed_memory={c:n for c,n in result['classes'].items() if c not in ('NON_MEMORY','CTA_BARRIER')}
    if observed_memory!=json.loads(expected['memory_paths']):
        raise ContractGap('MEMORY_PATH_COUNT_MISMATCH')
    result.update(header=header,complete_ctas=len(ctas),complete_warps=completed_warps)
    return result


def main(scan):
    SCRATCH.mkdir(parents=True,exist_ok=True)
    check=admission()
    check.update(phase='PRE_BODY_ADMISSION',scan_requested=scan,body_opens_at_admission=0,
                 new_simulation_attempts=0)
    save_json(SCRATCH/'ADMISSION.json',check)
    if not scan or check['reasons']:
        print(json.dumps(dict(**check,body_opens=0)))
        return 2 if check['reasons'] else 0
    os.nice(19)
    analyzer_sha=hashlib.sha256((PACK/'scripts/access_semantics.py').read_bytes()).hexdigest()
    runner_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    proof={(r['workload'].lower(),r['ordinal']):r for r in tsv('inputs/KERNEL_BODY_AUDIT.tsv')}
    scope=tsv('TRACE_SCOPE_SHA256.tsv')
    try:
        for workload in ('Gaussian','GEMM'):
            listing=next(r for r in scope if r['workload']==workload and r['kind']=='original_list')
            if hashlib.sha256(Path(listing['path']).read_bytes()).hexdigest()!=listing['sha256']:
                raise ContractGap('ORIGINAL_LIST_IDENTITY_CHANGED')
            for row in [r for r in scope if r['workload']==workload and r['kind']=='trace_member']:
                gate=admission()
                if gate['reasons']:
                    raise ContractGap('RESOURCE_OR_U_STOP:'+','.join(gate['reasons']))
                path=Path(row['path'])
                if path.suffix!='.traceg':
                    raise ContractGap('ONLY_PINNED_PLAIN_TRACEG_SUPPORTED')
                before=path.stat()
                member_stat={k:getattr(before,k) for k in ('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns')}
                if before.st_size!=int(row['bytes']):
                    raise ContractGap('ORIGINAL_MEMBER_SIZE_CHANGED')
                target=SCRATCH/f'{workload}_{int(row["ordinal"]):04d}.json'
                if target.exists():
                    previous=json.loads(target.read_text())
                    if (previous['member_sha256'],previous['analyzer_sha256'],previous['runner_sha256'])!=(row['sha256'],analyzer_sha,runner_sha):
                        raise ContractGap('CHECKPOINT_IDENTITY_MISMATCH_NO_OVERWRITE')
                    if previous['member_stat']!=member_stat:
                        raise ContractGap('COMPLETED_MEMBER_STAT_CHANGED_NO_AUTOMATIC_REUSE')
                    continue
                digest=hashlib.sha256()
                read_bytes=0
                started=last_check=time.monotonic()
                def tick():
                    nonlocal last_check
                    now=time.monotonic()
                    if now-started>1800:
                        raise ContractGap('PER_KERNEL_30_MINUTE_LIMIT')
                    if now-last_check>=1:
                        current=admission()
                        if current['reasons']:
                            raise ContractGap('RESOURCE_OR_U_STOP:'+','.join(current['reasons']))
                        last_check=now
                def stream(f):
                    nonlocal read_bytes
                    while True:
                        data=f.readline(65537)
                        if not data:
                            break
                        if len(data)>65536:
                            raise ContractGap('RECORD_TEXT_EXCEEDS_64_KIB_LIMIT')
                        digest.update(data)
                        read_bytes+=len(data)
                        # Bound physical read demand; only this CPU worker sleeps.
                        delay=read_bytes/(4*1024*1024)-(time.monotonic()-started)
                        if delay>0:
                            time.sleep(min(delay,.1))
                        yield data.decode('ascii')
                with path.open('rb',buffering=16384) as f:
                    result=consume_stream(stream(f),proof[(workload.lower(),row['ordinal'])],tick)
                after=path.stat()
                if digest.hexdigest()!=row['sha256'] or member_stat!={k:getattr(after,k) for k in member_stat}:
                    raise ContractGap('ORIGINAL_MEMBER_IDENTITY_CHANGED')
                result.update(workload=workload,ordinal=int(row['ordinal']),member_sha256=row['sha256'],
                    analyzer_sha256=analyzer_sha,runner_sha256=runner_sha,
                    status='COMPLETE_CPU_MEMBER_SCAN_NOT_NATIVE_CORRECTNESS',bytes_read=read_bytes,member_stat=member_stat)
                save_json(target,result)
        save_json(SCRATCH/'COMPLETE.json',dict(status='ALL_511_PRIMARY_MEMBERS_SCANNED',analyzer_sha256=analyzer_sha,
            runner_sha256=runner_sha,new_simulation_attempts=0,requires_cross_kernel_reduction=True))
    except (ContractGap,UnicodeError,KeyError,ValueError,MemoryError) as exc:
        save_json(SCRATCH/'STOP.json',dict(status='STOPPED_NO_AUTOMATIC_RETRY',reason=str(exc),
            current_member=str(path) if 'path' in locals() else 'UNAVAILABLE',
            incomplete_current_member_discarded=True,completed_members_preserved=True,new_simulation_attempts=0))
        print('STOP:',str(exc))
        return 2
    return 0


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--scan',action='store_true',help='request CPU scan only after all gates pass')
    sys.exit(main(p.parse_args().scan))
