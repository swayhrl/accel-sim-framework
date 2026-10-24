#!/usr/bin/env python3
"""CPU-only body/geometry/path audit of the fixed629 ordered trace members."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import time


def audit(row):
    p=Path(row['path']);header={};coords=set();warps=set();ops=Counter();mem=Counter()
    refs=Counter();widths=Counter();h=hashlib.sha256();declared=None;seen=0;last=b''
    active=0;records=0;version=0;coord=None;warp=None;bad_stride=0;unaligned=0
    max_global_lines=0;max_local_width=0;zero_active_memory=0
    began=time.monotonic();throttled=0;observed=0
    with p.open('rb') as f:
        for line in f:
            h.update(line)
            observed+=len(line)
            if observed-throttled>=1024**2:
                delay=observed/(5*1024**2)-(time.monotonic()-began)
                if delay>0:time.sleep(delay)
                throttled=observed
            if line.startswith(b'-') and b' = ' in line:
                key,value=line.decode().strip().split(' = ',1);header[key]=value
                if key=='-accelsim tracer version':version=int(value)
            elif line.startswith(b'thread block = '):
                coord=tuple(map(int,line.split(b' = ')[1].split(b',')))
                assert coord not in coords;coords.add(coord)
            elif line.startswith(b'warp = '):
                if declared is not None:assert seen==declared and last==b'EXIT',(p,warp,seen,declared,last)
                warp=int(line.split(b' = ')[1]);assert (coord,warp) not in warps;warps.add((coord,warp))
            elif line.startswith(b'insts = '):
                declared=int(line.split(b' = ')[1]);seen=0
            elif declared is not None and line[:1] in b'0123456789abcdef' and line.strip():
                t=line.split();offset=0 if version>=3 else 4
                if offset:assert tuple(map(int,t[:3]))==coord and int(t[3])==warp
                mask=int(t[offset+1],16);dest=int(t[offset+2]);j=offset+3+dest
                op=t[j];src=int(t[j+1]);width=int(t[j+2+src]);root=op.split(b'.')[0]
                ops[op]+=1;seen+=1;records+=1;last=root;active+=mask.bit_count()
                if not width:continue
                tokens=op.split(b'.');parsed_width=4
                for token in tokens:
                    if token.isdigit():parsed_width=int(token)//8;break
                    if token.startswith(b'U') and token[1:].isdigit():parsed_width=int(token[1:])//8;break
                widths[(op.decode(),width,parsed_width)]+=1
                a=t[j+3+src:];mode=int(a[0]);count=mask.bit_count();addresses=[]
                if not count:zero_active_memory+=1
                if mode==0:
                    addresses=[int(s,16) for s in a[1:1+count]];assert len(addresses)==count
                elif mode==1:
                    base=int(a[1],16);stride=int(a[2]);addresses=[base+i*stride for i in range(count)]
                    lanes=[i for i in range(32) if mask&(1<<i)]
                    if lanes and lanes!=list(range(lanes[0],lanes[-1]+1)):bad_stride+=1
                elif mode==2:
                    if count:
                        addresses=[int(a[1],16)]
                        for d in a[2:2+count-1]:addresses.append(addresses[-1]+int(d))
                        assert len(addresses)==count
                else:raise AssertionError((p,'unsupported address format',mode))
                unaligned+=sum(addr%parsed_width!=0 for addr in addresses)
                if root in [b'LDG',b'LDL']:
                    bypass=(b'STRONG' in tokens and b'GPU' in tokens) or b'BYPASS' in tokens
                    path=('BYPASS_LOAD' if bypass else 'CACHEABLE_GLOBAL_LOAD' if root==b'LDG' else 'CACHEABLE_LOCAL_LOAD')
                    if root==b'LDL':max_local_width=max(max_local_width,parsed_width)
                elif root in [b'LDS',b'STS',b'LDSM',b'ATOMS']:path='SHARED'
                elif root in [b'LD',b'ST']:path='GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED'
                elif root in [b'LDC',b'ULDC']:path='CONSTANT'
                elif root in [b'STG',b'STL']:path='ORDINARY_STORE'
                elif root in [b'ATOM',b'ATOMG',b'RED']:path='ATOMIC_L2'
                else:path='OTHER_MEMORY_FORM_REVIEW'
                mem[path]+=1
                if path=='CACHEABLE_GLOBAL_LOAD':
                    lines={base//128 for addr in addresses for base in [addr,addr+parsed_width-1]}
                    max_global_lines=max(max_global_lines,len(lines));refs[len(lines)]+=1
    assert declared is not None and seen==declared and last==b'EXIT'
    grid=tuple(map(int,header['-grid dim'].strip('()').split(',')))
    block=tuple(map(int,header['-block dim'].strip('()').split(',')))
    assert len(coords)==math.prod(grid)
    assert all(all(0<=v<d for v,d in zip(c,grid)) for c in coords)
    assert len(warps)==len(coords)*math.ceil(math.prod(block)/32)
    assert all(0<=w<math.ceil(math.prod(block)/32) for _,w in warps)
    assert h.hexdigest()==row['actual_sha256']
    return dict(workload=row['workload'],ordinal=int(row['ordinal']),path=str(p),sha256=h.hexdigest(),
        kernel=header['-kernel name'],binary_version=int(header['-binary version']),trace_version=version,
        complete_ctas=len(coords),complete_warps=len(warps),warp_instruction_records=records,
        active_thread_instructions=active,opcodes={k.decode():v for k,v in ops.items()},
        memory_instruction_paths=dict(mem),width_counts=[dict(opcode=k[0],trace_width=k[1],parser_width=k[2],records=v) for k,v in widths.items()],
        max_global_128b_line_references=max_global_lines,cacheable_local_max_width=max_local_width,
        sparse_mask_base_stride_records=bad_stride,unaligned_lane_memory_addresses=unaligned,
        zero_active_memory_records=zero_active_memory,
        global_reference_histogram=dict(refs),coverage='ALL_DECLARED_WARPS_AND_FULL_GRID_WITH_TERMINAL_EXIT',
        steady_interval='NOT_PROVEN_BY_TRACE_GEOMETRY',source_input_shape='NOT_INFERRED_FROM_TRACE_OR_FILENAME')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory',required=True)
    ap.add_argument('--output-dir',required=True);ap.add_argument('--workers',type=int,default=2)
    a=ap.parse_args();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    rows=list(csv.DictReader(Path(a.inventory).open(),delimiter='\t'))
    assert len(rows)==629 and a.workers<=2
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        results=[]
        for r in pool.map(audit,rows,chunksize=1):
            results.append(r)
            with (out/(r['workload']+'_'+str(r['ordinal'])+'.json')).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
            if len(results)%25==0:print(json.dumps(dict(audited=len(results),total=len(rows))),flush=True)
    summary=dict(status='CPU_BODY_AUDIT_COMPLETE_NOT_NATIVE_VALIDATION',members=len(results),
        complete_ctas=sum(r['complete_ctas'] for r in results),complete_warps=sum(r['complete_warps'] for r in results),
        active_thread_instructions=sum(r['active_thread_instructions'] for r in results),
        max_global_line_references=max(r['max_global_128b_line_references'] for r in results),
        max_cacheable_local_width=max(r['cacheable_local_max_width'] for r in results),
        sparse_mask_base_stride_records=sum(r['sparse_mask_base_stride_records'] for r in results),
        unaligned_lane_memory_addresses=sum(r['unaligned_lane_memory_addresses'] for r in results))
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
