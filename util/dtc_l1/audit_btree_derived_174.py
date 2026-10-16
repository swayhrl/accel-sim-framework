#!/usr/bin/env python3
"""Lane A full byte/consumer-domain check of the one authorized Btree bundle."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import re
import struct
import time
from collect_service_closure_attempts import sha

BUNDLE = '6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585'


def register(word):
    word = word.decode()
    for prefix, kind in [('UR', 1), ('UP', 3), ('R', 0), ('P', 2)]:
        if word.startswith(prefix):
            return str(kind)+':'+str(int(word[len(prefix):]))+','
    raise ValueError('Unknown register '+word)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--producer-review', type=Path, required=True)
    ap.add_argument('--original-dir', type=Path, required=True)
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    started = time.monotonic()
    identity = json.loads((a.producer_review/'INPUT_IDENTITY.json').read_text())
    contract = identity['identity_contract']
    assert hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == BUNDLE
    declared = {m['name']: m for m in contract['files']}
    assert (a.input_dir/'kernelslist.g').read_bytes() == (a.original_dir/'kernelslist.g').read_bytes()
    assert sha(a.input_dir/'kernelslist.g') == declared['kernelslist.g']['sha256']
    commands = (a.input_dir/'kernelslist.g').read_text().splitlines()
    assert [s for s in commands if not s.startswith('MemcpyHtoD,')] == contract['kernel_order']
    index = {int(r['line']): r for r in csv.DictReader((a.producer_review/'BTREE_DERIVATION_AUDIT.tsv').open(), delimiter='\t')}
    assert len(index) == 6000
    reference = json.loads((a.producer_review/'REFERENCE_DECODER.json').read_text())
    results = []
    for ordinal, expected in enumerate(reference['kernels'], 1):
        name = f'kernel-{ordinal}.traceg'
        oldhash, newhash, memoryhash, insthash, metahash = [hashlib.sha256() for _ in range(5)]
        counts = Counter(); opcodes = Counter(); coordinates = set(); warps = set()
        cta = -1; warp = None; remaining = 0; last = None; in_tb = False; offset = 0; headers = {}
        with (a.original_dir/name).open('rb') as oldfile, (a.input_dir/name).open('rb') as newfile:
            for number, (old, new) in enumerate(zip_longest(oldfile, newfile), 1):
                assert old is not None and new is not None, ('line-count', ordinal, number)
                oldhash.update(old); newhash.update(new)
                is_instruction = in_tb and old[:1].isdigit()
                if not is_instruction:
                    assert old == new, ('metadata-byte-change', ordinal, number)
                    metahash.update(new)
                    if old.startswith(b'-') and b' = ' in old:
                        key, value = old.decode().strip().split(' = ', 1); headers[key] = value
                    elif old.startswith(b'#BEGIN_TB'):
                        assert not in_tb; in_tb = True; cta += 1
                    elif old.startswith(b'thread block = '):
                        coord = tuple(map(int, old.split(b'=')[1].split(b',')))
                        assert coord not in coordinates; coordinates.add(coord)
                    elif old.startswith(b'warp = '):
                        assert remaining == 0 and (last is None or last == b'EXIT')
                        warp = int(old.split(b'=')[1]); assert (coord, warp) not in warps
                        warps.add((coord, warp)); last = None
                    elif old.startswith(b'insts = '):
                        remaining = int(old.split(b'=')[1])
                    elif old.startswith(b'#END_TB'):
                        assert in_tb and remaining == 0 and last == b'EXIT'; in_tb = False
                else:
                    t = new.split(); u = old.split()
                    assert tuple(map(int, t[:3])) == coord and int(t[3]) == warp
                    pc, mask, ndst = int(t[4], 16), int(t[5], 16), int(t[6])
                    oi = 7+ndst; ns = int(t[oi+1]); wi = oi+2+ns; mi = wi+1
                    op, width = t[oi], int(t[wi]); active = [i for i in range(32) if mask & (1 << i)]
                    assert t[:mi] == u[:mi]; remaining -= 1; assert remaining >= 0
                    last = op.split(b'.')[0]; opcodes[op.decode()] += 1
                    counts['warp_records'] += 1; counts['active_thread_instructions'] += len(active)
                    canonical = f'{cta}|{warp}|{pc}|{mask}|{op.decode()}|'+''.join(map(register, t[7:oi]))+'|'+''.join(map(register, t[oi+2:wi]))+f'|{width}'
                    if width:
                        assert op.startswith((b'LDG.', b'STG.'))
                        widths = [int(s.lstrip(b'U'))//8 for s in op.split(b'.') if re.fullmatch(rb'U?\d+', s)]
                        assert width == (widths[0] if widths else 4) and width in (4, 8)
                        mode = int(t[mi]); addresses = t[mi+1:]; vector = [0]*32
                        if mode == 0:
                            assert len(addresses) >= len(active)
                            values = [int(v, 16) for v in addresses[:len(active)]]
                        elif mode == 1:
                            assert len(addresses) == 2 and (not active or active == list(range(active[0], active[-1]+1)))
                            base, stride = int(addresses[0], 16), int(addresses[1])
                            values = [base+(lane-active[0])*stride for lane in active]
                        else:
                            raise ValueError('Unqualified address mode')
                        for lane, value in zip(active, values):
                            assert 0 <= value < 2**64 and value % width == 0 and value % 32+width <= 32 and value % 128+width <= 128
                            vector[lane] = value
                        memoryhash.update(struct.pack('<35Q', pc, mask, width, *vector))
                        counts['memory_records'] += 1; counts[f'memory_width_{width}'] += 1
                        counts['max_global_128b_lines'] = max(counts['max_global_128b_lines'], len({v//128 for v in values}))
                        counts['max_global_32b_sectors'] = max(counts['max_global_32b_sectors'], len({v//32 for v in values}))
                    else:
                        canonical += '|'+str(int(t[mi]) if len(t) > mi else 0)+'|0'
                    insthash.update((canonical+'\n').encode())
                    if ordinal == 1 and number in index:
                        r = index[number]; lane = mask.bit_length()-1
                        assert pc == 0x1c40 and op == b'LDG.E.SYS' and width == 4 and mask.bit_count() == 1
                        assert u[mi] == t[mi] == b'0' and len(u[mi+1:]) == 32 and len(t[mi+1:]) == 1
                        spans = list(re.finditer(rb'\S+', old))
                        assert new == old[:spans[mi+1].start()]+u[mi+1+lane]+b'\n'
                        assert offset == int(r['original_byte_offset']) and hashlib.sha256(old).hexdigest() == r['original_line_sha256'] and hashlib.sha256(new).hexdigest() == r['candidate_line_sha256']
                        assert int(r['active_lane']) == lane and int(r['old_address'], 16) == int(u[mi+1], 16) and int(r['new_address'], 16) == int(t[mi+1], 16)
                        counts['touched'] += 1; counts['changed_addresses'] += int(u[mi+1], 16) != int(t[mi+1], 16)
                        counts['sector_identity_changes'] += int(u[mi+1], 16)//32 != int(t[mi+1], 16)//32
                        counts['line_identity_changes'] += int(u[mi+1], 16)//128 != int(t[mi+1], 16)//128
                    else:
                        assert old == new, ('nonwhitelist-byte-change', ordinal, number)
                offset += len(old)
        grid = 6000 if ordinal == 1 else 10000
        assert not in_tb and remaining == 0 and coordinates == {(i, 0, 0) for i in range(grid)}
        assert cta+1 == grid and len(warps) == grid*8 and all(0 <= w < 8 for _, w in warps)
        assert oldhash.hexdigest() == contract['original_sha256'][name]
        assert newhash.hexdigest() == declared[name]['sha256'] and (a.input_dir/name).stat().st_size == declared[name]['bytes']
        assert headers == expected['headers'] and opcodes == expected['opcodes']
        for key in ['warp_records', 'active_thread_instructions', 'memory_records', 'memory_width_4', 'memory_width_8', 'max_global_128b_lines', 'max_global_32b_sectors']:
            assert counts[key] == expected['counts'][key], key
        assert insthash.hexdigest() == expected['instruction_sha256'] and memoryhash.hexdigest() == expected['consumer_memory_sha256'] and metahash.hexdigest() == expected['metadata_sha256']
        if ordinal == 1:
            assert [counts[k] for k in ['touched', 'changed_addresses', 'sector_identity_changes', 'line_identity_changes']] == [6000, 5792, 5792, 5792]
        result = dict(kernel_ordinal=ordinal, counts=dict(counts), complete_ctas=grid, complete_warps=grid*8, instruction_sha256=insthash.hexdigest(), consumer_memory_sha256=memoryhash.hexdigest(), metadata_sha256=metahash.hexdigest(), original_sha256=oldhash.hexdigest(), member_sha256=newhash.hexdigest())
        results.append(result); print(json.dumps(result), flush=True)
    receipt = dict(status='PASS_LANE_A_INDEPENDENT_COMPLETE_BYTE_AND_CONSUMER_DOMAIN_AUDIT', bundle_sha256=BUNDLE, kernels=results, input_directory=str(a.input_dir), source_sha256=sha(Path(__file__)), elapsed_host_seconds=time.monotonic()-started, utc=datetime.now(timezone.utc).isoformat(), capture_and_native_equivalence='NOT_PROVEN_CONDITIONAL_PRODUCER_FAMILY_ONLY', no_input_or_runtime_changes=True)
    with a.output.open('x') as f:
        json.dump(receipt, f, indent=2); f.write('\n')


if __name__ == '__main__':
    main()
