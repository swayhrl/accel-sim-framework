#!/usr/bin/env python3
"""Independent CPU SpMV trace/opcode admission audit, preserving SM89 identity."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import lzma
from pathlib import Path
import re


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--producer-root', required=True)
    ap.add_argument('--framework-root', required=True)
    ap.add_argument('--output-dir', required=True)
    a = ap.parse_args()
    producer = Path(a.producer_root)
    fw = Path(a.framework_root)
    out = Path(a.output_dir)
    out.mkdir(parents=True,exist_ok=False)
    audit = json.loads((producer/'git-receipts/TRACE_AUDIT.json').read_text())
    traces = producer/'payload-verified-v2/traces_env_ready/SpMV/traces'
    original_list = (traces/'kernelslist.g').read_text()
    assert original_list == (producer/'git-receipts/SpMV_kernelslist.g.txt').read_text()
    ordered = [s for s in original_list.splitlines() if s.endswith('.traceg.xz')]
    expected = [r for r in audit if r['case']=='SpMV']
    assert ordered == [Path(r['path']).name for r in expected] and len(ordered)==4
    ampere = (fw/'gpu-simulator/ISA_Def/ampere_opcode.h').read_text()
    maps = set(re.findall(r'\{\s*"([A-Z0-9]+)"',ampere))
    version_values = {int(v) for p in (fw/'gpu-simulator/ISA_Def').glob('*opcode.h')
                      for v in re.findall(r'#define\s+\w+BINART_VERSION\s+(\d+)',p.read_text())}
    assert 89 not in version_values
    results = []
    for name, reference in zip(ordered, expected):
        p = traces/name
        assert sha(p)==reference['sha256'] and p.stat().st_size==reference['bytes']
        text = lzma.decompress(p.read_bytes()).decode()
        header = dict(re.findall(r'^-([^=]+?) = (.*)$',text,re.M))
        assert header['binary version']=='89' and header['accelsim tracer version']=='5'
        coords = set(); warps = set(); ops = Counter(); widths = defaultdict(set)
        active_instructions=0; declared=None; seen=0; last=''; memory_modes=Counter()
        for line in text.splitlines():
            if line.startswith('thread block = '):
                coord=tuple(map(int,line.split(' = ')[1].split(',')))
                assert coord not in coords;coords.add(coord)
            elif line.startswith('warp = '):
                if declared is not None:
                    assert seen==declared and last=='EXIT'
                warp=(coord,int(line.split(' = ')[1]));assert warp not in warps;warps.add(warp)
            elif line.startswith('insts = '):
                declared=int(line.split(' = ')[1]);seen=0
            elif re.match(r'^[0-9a-f]+ [0-9a-f]{8} ',line):
                t=line.split();mask=int(t[1],16);dest=int(t[2]);j=3+dest
                op=t[j];src=int(t[j+1]);width=int(t[j+2+src]);address=t[j+3+src:]
                root=op.split('.')[0];assert root in maps,op
                assert not root.startswith(('CALL','RET','TEX','ATOM','LDGSTS'))
                ops[op]+=1;seen+=1;last=root;active_instructions+=mask.bit_count()
                if width:
                    widths[op].add(width);mode=int(address[0]);memory_modes[mode]+=1
                    assert op in ['LDG.E','STG.E'] and width==4
                    # Each instruction ends with the tracer5 immediate field.
                    count=mask.bit_count()
                    assert mode in [0,1,2]
                    if mode==0:assert len(address)==1+count+1
                    elif mode==1:assert len(address)==4
                    else:assert len(address)==1+1+max(count-1,0)+1
        assert seen==declared and last=='EXIT'
        assert coords=={(i,0,0) for i in range(36)} and warps=={((i,0,0),0) for i in range(36)}
        assert dict(ops)==reference['dynamic_opcodes'] and sum(ops.values())==2927
        results.append(dict(order=reference['order'],role=reference['role'],member=str(p),
            sha256=sha(p),binary_version=89,tracer_version=5,ctas=len(coords),warps=len(warps),
            warp_instruction_records=sum(ops.values()),active_thread_instructions=active_instructions,
            opcodes=dict(ops),memory_widths={k:sorted(v) for k,v in widths.items()},
            address_compression_modes=dict(memory_modes),
            opcode_roots_in_ampere_map=True,
            admission='NOT_ADMITTED_NO_SM89_DISPATCH_IN_FROZEN_FRAMEWORK',
            boundary='Opcode root overlap is insufficient to assert SM89 ISA/timing equivalence. No alias/header rewrite.'))
    (out/'SPMV_TRACE_OPCODE_AUDIT_V1.json').write_text(json.dumps(dict(
        producer_commit='890fb0be7e681a60419c49ca0a7aa85731d8c164',
        framework_source='18a68dcccd795f1b6cda75504e9450d00c9cee02',
        recognized_binary_versions=sorted(version_values),ordered_trace_list=str(traces/'kernelslist.g'),
        trace_list_sha256=sha(traces/'kernelslist.g'),kernels=results,
        total_active_thread_instructions=sum(r['active_thread_instructions'] for r in results),
        native_status='REUSED_USER_ACCEPTED_NATIVE_ONLY',
        layernorm_status='NOT_ADMITTED_SM86_AND_SKIPPED_CALL_REL_NOINC_NO_RECAPTURE',
        performance_claim='NONE'),indent=2)+'\n')
    print(json.dumps(dict(kernels=len(results),instructions=sum(r['active_thread_instructions'] for r in results),
                         admission='NOT_ADMITTED_NO_SM89_DISPATCH')))


if __name__=='__main__':
    main()
