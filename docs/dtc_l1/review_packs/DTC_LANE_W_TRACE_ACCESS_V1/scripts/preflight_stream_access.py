#!/usr/bin/env python3
"""Exercise the real streaming structure parser against synthetic in-memory input."""
import hashlib
import io
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from access_semantics import ContractGap
from stream_access_scan import consume_stream

ROOT=Path(__file__).resolve().parents[1]
HEADER='''-kernel name = fixture
-grid dim = (2,1,1)
-block dim = (32,1,1)
-binary version = 70
-accelsim tracer version = 3
-cuda stream id = 0
# synthetic in-memory fixture; no original trace bytes
'''
BODY='''#BEGIN_TB
thread block = 0,0,0
warp = 0
insts = 4
100 1 0 STG.E.SYS 1 R2 4 0 80
110 1 1 R1 LDG.E.SYS 1 R2 4 0 82
120 1 1 R1 LDG.E.SYS 1 R2 4 0 84
130 1 0 EXIT 0 0
#END_TB
#BEGIN_TB
thread block = 1,0,0
warp = 0
insts = 2
140 1 1 R1 LDG.E.SYS 1 R2 4 0 80
150 1 0 EXIT 0 0
#END_TB
'''
EXPECTED=dict(kernel='fixture',binary_version='70',trace_version='3',complete_ctas='2',complete_warps='2',
    warp_instruction_records='6',active_thread_instructions='6',
    memory_paths=json.dumps({'CACHEABLE_GLOBAL_LOAD':3,'ORDINARY_STORE':1}))


def reject(text,expected=EXPECTED):
    try:
        consume_stream(io.StringIO(text),expected)
    except (ContractGap,KeyError,ValueError):
        return
    raise AssertionError('Malformed/incomplete stream was accepted')


if __name__=='__main__':
    text=HEADER+BODY
    result=consume_stream(io.StringIO(text),EXPECTED)
    assert result['distinct_read_lines']==result['distinct_write_lines']==1
    assert result['same_kernel_line_aliases']==result['same_kernel_byte_overlaps']==1
    candidates=result['same_warp_candidates']
    assert len(candidates)==2 and sum(r['read_record_line_write_pc_candidates'] for r in candidates)==2
    assert {r['kind'] for r in candidates}=={'BYTE_OVERLAP','LINE_ALIAS_ONLY'}
    # Second CTA's read must not use another CTA's ordered-write history.
    assert '0x140' not in {r['read_pc'] for r in candidates}
    assert result['header']['cuda stream id']=='0'
    for broken in [text.replace('insts = 4','insts = 3'),text.rsplit('#END_TB',1)[0],
                   text.replace('thread block = 1,0,0','thread block = 0,0,0'),
                   text.replace('warp = 0','warp = 1'),text.replace('150 1 0 EXIT 0 0','150 1 0 NOP 0 0'),
                   text.replace('insts = 2','insts = 3')]:
        reject(broken)
    reject(text,dict(EXPECTED,active_thread_instructions='5'))
    reject(text,dict(EXPECTED,kernel='wrong_input'))
    receipt=dict(status='PASS_SYNTHETIC_STREAM_FIXTURE_ONLY',
        checked=['two_cta_full_grid','exact_warp_record_counts','terminal_exit','header_identity',
                 'accepted_instruction_total','duplicate_cta_rejection','warp_id_bounds',
                 'intra_warp_history_isolation','line_alias_vs_byte_overlap'],
        runner_sha256=hashlib.sha256((ROOT/'scripts/stream_access_scan.py').read_bytes()).hexdigest(),
        test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        original_trace_body_opens=0,native_or_simulator_executions=0,
        real_input_equivalence='UNAVAILABLE_NOT_SCANNED',cross_kernel_reduction='PENDING')
    (ROOT/'CPU_STREAM_PREFLIGHT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
