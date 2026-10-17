#!/usr/bin/env python3
"""Synthetic CPU legality checks only; never opens any original trace or raw."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from access_semantics import (ContractGap, decode_record, line_masks,
                              frozen_base_stride, classify, WarpWriteHistory)

ROOT=Path(__file__).resolve().parents[1]
passed=[]


def decode(s,version=3,lineinfo=0,warp=0,ordinal=1):
    return decode_record(s,version,lineinfo,(0,0,0),warp,ordinal)


def case(name, check):
    check()
    passed.append(name)


def expect_gap(text, code, **kwargs):
    try:
        decode(text,**kwargs)
    except ContractGap as exc:
        assert code in str(exc), (code,str(exc))
    else:
        raise AssertionError('Missing contract rejection: '+code)


def layout():
    current=decode('0100 00000003 1 R1 LDG.E.SYS 1 R2 4 0 80 84')
    legacy=decode('0 0 0 0 0100 00000003 1 R1 LDG.E.SYS 1 R2 4 0 80 84',version=0)
    lined=decode('77 0100 00000003 1 R1 LDG.E.SYS 1 R2 4 0 80 84',lineinfo=1)
    assert current==legacy==lined
    assert current.pc==256 and current.lanes==((0,128),(1,132))
    expect_gap('1 0 0 0 100 1 0 EXIT 0 0','LEGACY_CTA_WARP',version=0)
    expect_gap('100 1 0 EXIT 0 0','UNREVIEWED_VERSION',version=6)
    expect_gap('100 1 2 R1 R2 LDG 0 0','UNREVIEWED_DEST_COUNT')
    expect_gap('100 1 0 EXIT 5 R1 R2 R3 R4 R5 0','UNREVIEWED_SOURCE_COUNT')


def addresses():
    r=decode('100 0000000e 1 R1 LDG.E.SYS 1 R2 4 1 88 -4')
    assert r.lanes==((1,136),(2,132),(3,128))
    d=decode('100 00000025 1 R1 LDG.E.SYS 1 R2 4 2 88 -4 -4')
    assert d.lanes==((0,136),(2,132),(5,128))
    assert not decode('100 0 1 R1 LDG.E.SYS 1 R2 4 1 80 4').lanes
    expect_gap('100 3 1 R1 LDG.E.SYS 1 R2 4 0 80','TRUNCATED')
    expect_gap('100 3 1 R1 LDG.E.SYS 1 R2 4 1 0 -4','ADDRESS_OVERFLOW')
    expect_gap('100 1 1 R1 LDG.E.SYS 1 R2 4 0 ffffffffffffffff','ADDRESS_OVERFLOW')
    expect_gap('100 1 1 R1 LDG.E.SYS 1 R2 4 4 80','UNREVIEWED_ADDRESS_MODE')


def masks():
    r=decode('100 1 1 R1 LDG.E.64.SYS 1 R2 4 0 7c')
    assert r.trace_width==4 and r.width==8
    assert line_masks(r)=={0:((15<<124),8),128:(15,1)}
    unaligned=decode('100 1 1 R1 LDG.E.SYS 1 R2 4 0 1f')
    assert line_masks(unaligned)=={0:(15<<31,3)}
    broadcast=decode('100 3 1 R1 LDG.E.SYS 1 R2 4 0 80 80')
    assert line_masks(broadcast)=={128:(15,1)}


def oracle():
    # Compare pure diagnostic helper to already sealed CPU oracle values;
    # no C++ compilation/execution or native tooling is involved.
    receipt=json.loads((ROOT/'inputs/ORACLE_RECEIPT.json').read_text())
    addresses=frozen_base_stride(int(receipt['input']['mask_hex'],16),
                                 receipt['input']['base'],receipt['input']['stride'])
    assert all(addresses[int(lane)]==value for lane,value in receipt['active_lane_addresses'].items())
    expect_gap('100 fffcfffc 1 R1 LDG.E.SYS 1 R2 4 1 80 4','SPARSE_MASK_BASE_STRIDE')


def classification():
    assert classify('LDG.E.SYS')=='CACHEABLE_GLOBAL_LOAD'
    assert classify('LDG.STRONG.GPU')=='BYPASS_GLOBAL_LOAD'
    assert classify('LDG.STRONG.SYS')=='CACHEABLE_GLOBAL_LOAD'
    assert classify('LDG.E.SYS',True)=='BYPASS_GLOBAL_LOAD'
    assert classify('ATOMG.E.ADD')=='ATOMIC'
    assert classify('RED.E.ADD')=='ATOMIC'
    assert classify('BAR.SYNC')=='CTA_BARRIER'
    assert classify('MEMBAR.SYS')=='FENCE'
    expect_gap('100 1 1 R1 LDGSTS 1 R2 4 0 80','UNREVIEWED_MEMORY_OPCODE')


def ordering():
    hist=WarpWriteHistory()
    assert hist.observe(decode('100 1 0 STG.E.SYS 1 R2 4 0 80',ordinal=1))==[]
    alias=hist.observe(decode('110 1 1 R1 LDG.E.SYS 1 R2 4 0 84',ordinal=2))
    assert len(alias)==1 and alias[0]['line_alias'] and not alias[0]['byte_overlap']
    overlap=hist.observe(decode('120 1 1 R1 LDG.E.SYS 1 R2 4 0 82',ordinal=3))
    assert overlap[0]['overlap_byte_count']==2
    assert overlap[0]['actual_happens_before']=='UNAVAILABLE'
    # Another warp must not inherit the first warp's ordered-write history.
    assert hist.observe(decode('130 1 1 R1 LDG.E.SYS 1 R2 4 0 80',warp=1,ordinal=1))==[]
    try:
        hist.observe(decode('140 1 1 R1 LDG.E.SYS 1 R2 4 0 80',ordinal=2))
    except ContractGap:
        pass
    else:
        raise AssertionError('Nonmonotonic sequence was accepted')


if __name__=='__main__':
    for name,check in [('version0_version3_lineinfo',layout),('signed_address_modes_and_rejections',addresses),
                       ('width_override_and_exact_masks',masks),('sealed_sparse_mask_oracle',oracle),
                       ('cache_atomic_fence_barrier_classes',classification),('warp_order_vs_byte_alias',ordering)]:
        case(name,check)
    result=dict(status='PASS_SYNTHETIC_CPU_LEGALITY_ONLY',passed=passed,
                native_or_simulator_executions=0,original_trace_body_opens=0,
                frozen_decoder_modified=False,original_trace_scan_started=False,
                analyzer_sha256=hashlib.sha256((ROOT/'scripts/access_semantics.py').read_bytes()).hexdigest(),
                test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                limits=['not full parser equivalence','not producer contract proof','not real trace scan',
                        'no across-warp time order','no values or native correctness inference'])
    (ROOT/'CPU_ACCESS_SEMANTICS_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
