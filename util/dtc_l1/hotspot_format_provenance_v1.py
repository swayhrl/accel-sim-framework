#!/usr/bin/env python3
"""Read-only Hotspot provenance diagnostics. Never emits a normalized trace.

One CPU process; one pass over the single frozen Hotspot member. Hypothetical
addresses are named explicitly and are not an input qualification.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

FROZEN = '18a68dcccd795f1b6cda75504e9450d00c9cee02'
MARCH = '0e2fddcdef37fc59ad786553892b75567a5f2cdb'
AUGUST = '475a282dd5baabfc481b3be44963e92fc3df34cc'
FIX = '756ed33d503704b4faf97bb3a051792f0450d14c'
SOURCE = 'util/tracer_nvbit/tracer_tool/tracer_tool.cu'
PARSER = 'gpu-simulator/trace-parser/trace_parser.cc'
MEMBER_SHA = 'ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8'
U64 = (1 << 64) - 1


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, revision, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', revision + ':' + path])


def function(text, start):
    i = text.index(start)
    begin = text.index('{', i)
    depth = 1
    end = begin + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[i:end]


def write_tsv(path, rows):
    rows = list(rows)
    if not rows:
        return
    with path.open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def oracle(base, stride, mask):
    """Mirror checked against the extracted frozen C++ function in cpu_test."""
    result = [0] * 32
    started = ended = False
    address = base
    for lane in range(32):
        if mask >> lane & 1 and not started:
            started = True
            result[lane] = base
        elif started and not ended:
            if mask >> lane & 1:
                address = (address + stride) & U64
                result[lane] = address
            else:
                ended = True
    return result


def cpu_test(repo, out):
    """Compile source excerpts; raw address fixtures precede all decoding."""
    old = git(repo, MARCH, SOURCE).decode()
    frozen = git(repo, FROZEN, PARSER).decode()
    encoder = git(repo, AUGUST, SOURCE).decode()
    width_fn = function(old, 'unsigned get_datawidth_from_opcode(')
    number_fn = function(old, 'bool is_number(')
    # Extract the *actual* March inline encoder without changing its body.
    start = old.index('int stride=0;')
    end = old.index('if(const_stride && enable_compress)', start)
    inline = old[start:end]
    march = ('bool march(const uint64_t *addresses, uint32_t execution, '
             'uint64_t &base, int &step) {\n'
             'struct { uint64_t addrs[32]; } storage; auto *ma=&storage;\n'
             'std::copy(addresses, addresses+32, ma->addrs);\n'
             'std::bitset<32> mask(execution);\n' + inline +
             '\nbase=addr; step=stride; return const_stride;\n}')
    enc = function(encoder, 'bool base_stride_compress(')
    dec = function(frozen, 'void inst_memadd_info_t::base_stride_decompress(')
    list_start = frozen.index('// read addresses one by one from the file')
    list_end = frozen.index('} else if (address_mode == address_format::base_stride)', list_start)
    list_body = frozen[list_start:list_end]
    src = ('#include <bits/stdc++.h>\n#define WARP_SIZE 32\n'
           'struct inst_memadd_info_t { uint64_t addrs[32]{}; '
           'void base_stride_decompress(unsigned long long,int,const std::bitset<32>&); };\n'
           + number_fn + '\n' + width_fn + '\n' + dec + '\n' + march + '\n' + enc + '\n'
           'void frozen_list(std::istream &ss, inst_memadd_info_t *memadd_info, '
           'const std::bitset<32> &mask_bits){\n'+list_body+'\n}\n'
           'int main(){ assert(get_datawidth_from_opcode({"LDS","U"})==4);'
           'assert(get_datawidth_from_opcode({"STS"})==4);'
           'uint32_t e,p; uint64_t a[32],b; int s; '
           'while(std::cin>>std::hex>>e>>p){for(auto &v:a)std::cin>>std::dec>>v; '
           'bool ok=march(a,e,b,s); std::cout<<ok<<" "<<b<<" "<<s; '
           'uint64_t b2=0;int s2=0;bool ok2=base_stride_compress(a,std::bitset<32>(e),b2,s2); '
           'std::cout<<" "<<ok2<<" "<<b2<<" "<<s2; '
           'inst_memadd_info_t d;d.base_stride_decompress(b,s,std::bitset<32>(p)); '
           'for(auto v:d.addrs)std::cout<<" "<<v;'
           'std::stringstream raw;for(auto v:a)raw<<std::hex<<v<<" ";'
           'inst_memadd_info_t l;frozen_list(raw,&l,std::bitset<32>(p));'
           'for(auto v:l.addrs)std::cout<<" "<<v;std::cout<<"\\n"; }}\n')
    build = out / 'build'
    build.mkdir(exist_ok=True)
    (build / 'oracle.cc').write_text(src)
    subprocess.run(['g++', '-std=c++17', '-O0', '-Wall', '-Wextra',
                    str(build / 'oracle.cc'), '-o', str(build / 'oracle')], check=True)
    # Independent, explicit uncompressed fixtures, including two indistinguishable
    # serialized records with different source lane addresses (loss proof).
    up = [128,132,136,140,144,148,152,156,160,164,168,172,176,180,184,188,
          192,196,200,204,208,212,216,220,224,228,232,236,240,244,248,252]
    shifted = [0,0,128,132,136,140,144,148,152,156,160,164,168,172,176,180,
               184,188,192,196,200,204,208,212,216,220,224,228,232,236,240,244]
    down = [124,120,116,112,108,104,100,96,92,88,84,80,76,72,68,64,
            60,56,52,48,44,40,36,32,28,24,20,16,12,8,4,0]
    zero_base = [0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,
                 64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124]
    fixtures = []
    for name, addresses, execution in [('full', up, 0xffffffff),
                                       ('start2', shifted, 0xfffffffc),
                                       ('negative', down, 0xffffffff),
                                       ('base0', zero_base, 0xffffffff),
                                       ('zero_stride', [128]*32, 0xffffffff),
                                       ('base0_zero_stride', [0]*32, 0xffffffff)]:
        for pname, pred in [('contiguous', 0x0000fffc), ('hole', 0xfffcfffc),
                            ('many_runs', 0xcccccccc), ('zero', 0)]:
            fixtures.append(dict(name=name+'_'+pname, addresses=addresses,
                                 execution_mask=execution, printed_mask=execution & pred,
                                 opcode_widths={'LDS.U':4, 'STS':4}))
    delta_path = out / 'DECODER_DELTA.tsv'
    if delta_path.exists():
        with delta_path.open() as f:
            for row in csv.DictReader(f,delimiter='\t'):
                d=json.loads(row['address_example_json'])
                if row['mode']=='0' and d['lanes'] and d['frozen']!=d['conditional_full_execution']:
                    fixtures.append(dict(name='fixed_member_mode0_independent_raw_vector',
                                         addresses=d['serialized_addresses'], execution_mask=0xffffffff,
                                         printed_mask=int(row['mask'],16), opcode_widths={'LDG.E.SYS':4},
                                         provenance=dict(member_sha256=MEMBER_SHA,line=int(row['first_line']),
                                                         line_sha256=row['line_sha256'])))
                    break
    fixtures.append(dict(name='execution_hole_encoder_rejects', addresses=up,
                         execution_mask=0xfffcfffc, printed_mask=0xfffcfffc,
                         opcode_widths={'LDS.U':4, 'STS':4}))
    payload = ''.join(f"{r['execution_mask']:x} {r['printed_mask']:x} " +
                      ' '.join(map(str, r['addresses']))+'\n' for r in fixtures)
    lines = subprocess.check_output([str(build / 'oracle')], input=payload.encode()).decode().splitlines()
    results = []
    for r, line in zip(fixtures, lines, strict=True):
        ok, base, stride, ok2, base2, stride2, *both = map(int, line.split())
        decoded, listed = both[:32], both[32:]
        assert ok == ok2
        if ok:
            assert (base, stride) == (base2, stride2)
            assert decoded == oracle(base, stride, r['printed_mask'])
        lanes = [s for s in range(32) if r['printed_mask'] >> s & 1]
        changed = [s for s in lanes if decoded[s] != r['addresses'][s]] if ok else []
        assert [listed[s] for s in lanes] == r['addresses'][:len(lanes)]
        results.append(dict(**r, encoder_accepts=bool(ok), base=base, stride=stride,
                            frozen_active_addresses=[decoded[s] for s in lanes] if ok else [],
                            frozen_list_active_addresses=[listed[s] for s in lanes],
                            changed_lanes=changed))
    a = next(r for r in results if r['name']=='full_hole')
    b = next(r for r in results if r['name']=='start2_hole')
    assert (a['printed_mask'],a['base'],a['stride']) == (b['printed_mask'],b['base'],b['stride'])
    assert a['addresses'][2] != b['addresses'][2]
    assert not results[-1]['encoder_accepts']
    assert [oracle(128,4,0xfffcfffc)[s] for s in [2,15,18,31]] == [128,180,0,0]
    receipt = dict(status='PASS_SOURCE_COUNTEREXAMPLES_NOT_INPUT_RECOVERY', cases=len(results),
                   full_source_sha256=sha(frozen.encode()),
                   frozen_function_sha256=sha(dec.encode()),
                   frozen_function_with_newline_sha256=sha((dec+'\n').encode()),
                   original_oracle_function_sha256=sha((dec+'\n\n').encode()),
                   frozen_list_body_sha256=sha(list_body.encode()),
                   actual_width_assertions={'LDS.U':4,'STS':4},
                   march_inline_sha256=sha(inline.encode()), august_encoder_sha256=sha(enc.encode()),
                   oracle_source_sha256=sha(src.encode()),
                   loss_proof=dict(serialized=['fffcfffc','0x80',4],
                                   execution_full_lane2=136, execution_start2_lane2=128),
                   results=results)
    (out / 'CPU_TEST_RESULTS.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='results'}), flush=True)


def scan(member, out):
    counters = Counter()
    groups = Counter()
    examples = {}
    h = hashlib.sha256()
    idx = out / 'AFFECTED_RECORD_INDEX.tsv.gz'
    with member.open('rb') as f, gzip.open(idx, 'wt') as index:
        index.write('line\tcta\twarp\tpc\topcode\tmask\tmode\tclass\tline_sha256\n')
        for lineno, line in enumerate(f, 1):
            h.update(line)
            if not line[:1] in b'0123456789abcdef' or not line.strip():
                continue
            t = line.split()
            if len(t)<8:
                continue
            counters['warp_records'] += 1
            mask = int(t[5],16)
            counters['active_thread_instructions'] += mask.bit_count()
            j = 7 + int(t[6])
            op = t[j].decode()
            nsrc = int(t[j+1])
            width = int(t[j+2+nsrc])
            if not width:
                continue
            tail = t[j+3+nsrc:]
            mode = int(tail[0])
            counters[f'mode{mode}_memory_records'] += 1
            lanes = [s for s in range(32) if mask >> s & 1]
            sparse = bool(lanes and lanes != list(range(lanes[0], lanes[-1]+1)))
            category = ''
            if mode == 1:
                assert len(tail)==3, (lineno,tail)
                base, stride = int(tail[1],16), int(tail[2])
                if sparse:
                    counters['sparse_mode1_records'] += 1
                if not lanes:
                    counters['mode1_zero_predicate'] += 1
                    continue
                if sparse or lanes[0] > 0:
                    category = 'SPARSE_AND_HIDDEN_ANCHOR' if sparse and lanes[0]>0 else 'SPARSE' if sparse else 'HIDDEN_ANCHOR'
                    old = oracle(base,stride,mask)
                    ordinal = [(base+i*stride)&U64 for i in range(len(lanes))]
                    lane_first = [(base+(s-lanes[0])*stride)&U64 for s in lanes]
                    anchor0 = [(base+s*stride)&U64 for s in lanes]
                    old_active = [old[s] for s in lanes]
                    counters['mode1_records_with_possible_hidden_anchor' if lanes[0]>0 else 'mode1_sparse_anchor0_unique_conditional'] += 1
                    counters['frozen_vs_ordinal_changed_lanes'] += sum(a!=b for a,b in zip(old_active,ordinal))
                    counters['frozen_vs_lane_first_changed_lanes'] += sum(a!=b for a,b in zip(old_active,lane_first))
                    counters['frozen_vs_anchor0_changed_lanes'] += sum(a!=b for a,b in zip(old_active,anchor0))
                    detail = dict(base=base,stride=stride,lanes=lanes,frozen=old_active,
                                  hypothetical_ordinal=ordinal,hypothetical_lane_first=lane_first,
                                  hypothetical_anchor0=anchor0,
                                  source_consistent_first_execution_lanes=list(range(min(lanes[0],30)+1)),
                                  width=width)
                    key = (op,t[4].decode(),f'{mask:08x}',mode,category,base,stride,0)
            elif mode == 0:
                addresses = [int(v,16) for v in tail[1:]]
                n = len(addresses)
                assert mask.bit_count() <= n <= 32, (lineno, n, mask)
                if n > mask.bit_count():
                    category = 'LIST_EXCESS_TOKENS'
                    counters['mode0_excess_address_records'] += 1
                    counters['mode0_excess_address_records_'+op] += 1
                    if n==32:
                        counters['mode0_full_execution_vector'] += 1
                        changed = sum(addresses[i]!=addresses[s] for i,s in enumerate(lanes))
                        counters['mode0_full_vector_changed_lanes_conditional'] += changed
                        if changed:
                            counters['mode0_full_vector_changed_records_conditional'] += 1
                    key = (op,t[4].decode(),f'{mask:08x}',mode,category,0,0,n)
                    detail = dict(lanes=lanes,serialized_addresses=addresses,
                                  frozen=[addresses[i] for i in range(len(lanes))],
                                  conditional_full_execution=[addresses[s] for s in lanes] if n==32 else None,
                                  width=width)
            else:
                raise AssertionError(('unexpected format in pre-version Hotspot', mode))
            if category:
                groups[key] += 1
                if key not in examples:
                    examples[key] = dict(first_line=lineno, cta=','.join(v.decode() for v in t[:3]),
                                         warp=t[3].decode(), line_sha256=sha(line), **detail)
                index.write(f"{lineno}\t{','.join(v.decode() for v in t[:3])}\t{t[3].decode()}\t{t[4].decode()}\t{op}\t{mask:08x}\t{mode}\t{category}\t{sha(line)}\n")
    assert h.hexdigest()==MEMBER_SHA, h.hexdigest()
    assert counters['sparse_mode1_records']==90792
    assert counters['active_thread_instructions']==377291004
    assert counters['warp_records']==13169524
    rows=[]
    for key,n in sorted(groups.items()):
        op,pc,mask,mode,category,base,stride,count=key
        ex=examples[key]
        rows.append(dict(opcode=op,pc=pc,mask=mask,mode=mode,category=category,base=base,stride=stride,
                         serialized_address_count=count,records=n,**{k:ex[k] for k in ['first_line','cta','warp','line_sha256']},
                         address_example_json=json.dumps({k:v for k,v in ex.items() if k not in ['first_line','cta','warp','line_sha256']},separators=(',',':'))))
    write_tsv(out/'DECODER_DELTA.tsv',rows)
    receipt = dict(status='HYPOTHESES_ONLY_HISTORICAL_EXECUTION_MASK_NOT_SERIALIZED',
                   member=str(member), member_sha256=h.hexdigest(), member_bytes=member.stat().st_size,
                   counters=dict(counters), unique_groups=len(rows),
                   record_index_sha256=sha(idx.read_bytes()), decoder_delta_sha256=sha((out/'DECODER_DELTA.tsv').read_bytes()))
    (out/'SCAN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['cpu-test','scan'])
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--member',type=Path)
    ap.add_argument('--output-dir',type=Path,required=True)
    a=ap.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    if a.action=='cpu-test':
        cpu_test(a.repo,a.output_dir)
    else:
        if a.member is None:
            ap.error('--member required for scan')
        scan(a.member,a.output_dir)


if __name__=='__main__':
    main()
