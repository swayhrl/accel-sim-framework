#!/usr/bin/env python3
"""Reuse the registered risk index; sparse source checks, never rewrite input.

Btree: inspect its6000 original full32 lines. LUD: inspect only19840 indexed
global lines and check a disclosed, unbound source-model hypothesis. Other
original trace records, the629-body auditor and Hotspot are never read.
Passing this diagnostic does not establish capture/source applicability.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path

LUD_SOURCE_SHA = 'fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0'
BASE = 0x7fd9eb500000
DIM = 512
BLOCK = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


def model_address(kind, row, stage, cta, lane):
    """Default BLOCK16 source's ELSE branch: idx=threadIdx.x-BLOCK_SIZE."""
    require(16<=lane<32,'Only source-model second halfwarp is in scope')
    y = stage+row if kind=='dia' else stage+(cta+1)*BLOCK+row
    return BASE+4*(y*DIM+stage+lane-BLOCK)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prior-receipt',type=Path,required=True)
    ap.add_argument('--inventory',type=Path,required=True)
    ap.add_argument('--lud-source',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    a = ap.parse_args()
    prior = json.loads(a.prior_receipt.read_text())
    require(prior['selected_members']==65 and prior['index']['records']==104476,'Fixed index required')
    require(digest(a.lud_source)==LUD_SOURCE_SHA,'Exact archived/historical source required')
    index = Path(prior['index']['path'])
    require(digest(index)==prior['index']['sha256'],'Index container identity mismatch')
    inventory = {(r['workload'],r['ordinal']):r for r in csv.DictReader(a.inventory.open(),delimiter='\t')}
    selected = {r['path'] for r in prior['member_receipts']}
    for p in selected:
        require(Path(p).parent not in a.output_dir.resolve().parents,'Separate output namespace required')
    a.output_dir.mkdir(parents=True,exist_ok=False)
    counts = Counter()
    pc_counts = Counter()
    operation_map = {}
    examples = {}
    handles = {}
    decoded_hash = hashlib.sha256()
    try:
        with gzip.open(index,'rb') as f:
            header = None
            for line in f:
                decoded_hash.update(line)
                if header is None:
                    header = line.decode().rstrip('\n').split('\t')
                    continue
                r = dict(zip(header,line.decode().rstrip('\n').split('\t')))
                counts['index_'+r['workload']] += 1
                pc_counts[(r['workload'],r['kernel'],r['pc'],r['opcode'])] += 1
                if r['workload']=='2DConvolution':
                    continue  # Reuse indexed alternatives; no original body read.
                if r['workload']=='lud' and not r['opcode'].startswith(('LDG.','STG.')):
                    continue  # Do not repeat the shared-address investigation.
                inv = inventory[(r['workload'],r['ordinal'])]
                p = Path(inv['path'])
                require(str(p) in selected,'Record outside registered65 members')
                if p not in handles:
                    require(p.stat().st_size==int(inv['bytes']),'Original size changed')
                    handles[p] = p.open('rb')
                handle = handles[p]
                handle.seek(int(r['byte_offset']))
                raw = handle.readline()
                require(hashlib.sha256(raw).hexdigest()==r['original_line_sha256'],'Original indexed line changed')
                counts['original_records_sparsely_read'] += 1
                counts['original_bytes_sparsely_read'] += len(raw)
                t = raw.split()
                require(t[4].decode()==r['pc'] and t[5].decode()==r['mask'],'Indexed PC/mask mismatch')
                j = 7+int(t[6])
                m = j+3+int(t[j+1])
                before = [int(v,16) for v in r['frozen_addresses'].split(',')]
                active = [int(v) for v in r['active_lanes'].split(',')]
                if r['workload']=='btree':
                    require(r['pc']=='1c40' and r['opcode']=='LDG.E.SYS' and int(t[m])==0,'Btree scope')
                    words = [int(v,16) for v in t[m+1:]]
                    require(len(active)==1 and len(words)==32,'Btree full32 single-P witness changed')
                    candidate = [words[active[0]]]
                    require(before==words[:1] and candidate==[int(v,16) for v in r['firstE0_or_full32_addresses'].split(',')],'Index/raw association mismatch')
                    counts['btree_full32_verified'] += 1
                    counts['btree_P_only_list_contract_count_mismatch'] += 1
                    counts['btree_E_list_conditional_address_difference'] += before!=candidate
                    examples.setdefault('btree',dict(path=str(p),line=int(r['line']),byte_offset=int(r['byte_offset']),
                        original_line_sha256=r['original_line_sha256'],pc=r['pc'],mask=r['mask'],active_lane=active[0],
                        frozen=before,conditional_E_list=candidate,raw_address_count=32))
                    continue
                require(r['kernel']=='_Z13lud_perimeterPfii','Global risk outside perimeter kernel')
                require(active==list(range(16,32)) and int(t[m])==1 and int(t[m+2])==4,'LUD source-model lane/stride scope')
                ordinal = int(r['ordinal'])
                require(ordinal%3==2,'LUD source-model launch order')
                stage = ((ordinal-2)//3)*BLOCK
                cta = int(t[0])
                key = (r['pc'],r['opcode'])
                if key not in operation_map:
                    possibilities = []
                    for kind,rows in [('dia',range(8,16)),('peri_col',range(16))]:
                        if r['opcode'].startswith('STG.') and kind=='dia':
                            continue
                        for row in rows:
                            if before==[model_address(kind,row,stage,cta,lane) for lane in active]:
                                possibilities.append((kind,row))
                    require(len(possibilities)==1,'First sample does not identify one source operation under model')
                    operation_map[key] = possibilities[0]
                    counts['lud_PC_operation_labels_inferred_from_first_sample'] += 1
                else:
                    counts['lud_PC_operation_held_out_records'] += 1
                kind,row = operation_map[key]
                expected = [model_address(kind,row,stage,cta,lane) for lane in active]
                require(before==expected,'LUD frozen consumption disagrees with disclosed source model')
                base = int(t[m+1],16)
                anchors = [first for first in range(17)
                           if [base+(lane-first)*4 for lane in active]==expected]
                require(anchors==[16],'LUD source-model anchor is not unique16')
                counts['lud_global_source_model_matches'] += 1
                counts['lud_cacheable_load_model_matches' if r['opcode'].startswith('LDG.') else 'lud_global_store_model_matches'] += 1
                examples.setdefault('lud:'+r['pc'],dict(path=str(p),ordinal=ordinal,line=int(r['line']),
                    byte_offset=int(r['byte_offset']),original_line_sha256=r['original_line_sha256'],pc=r['pc'],
                    opcode=r['opcode'],stage_offset=stage,cta_x=cta,source_operation=kind,source_row=row,
                    frozen_lane16=hex(before[0]),firstE0_lane16=hex(base+16*4),source_model_lane16=hex(expected[0]),
                    model_compatible_anchor=16,capture_or_compiled_profile_binding=False))
    finally:
        for handle in handles.values():
            handle.close()
    require(decoded_hash.hexdigest()==prior['index']['decoded_sha256'],'Decoded index identity mismatch')
    require([counts['index_'+n] for n in ['btree','2DConvolution','lud']]==[6000,40940,57536],'Index census mismatch')
    require(counts['btree_full32_verified']==6000 and counts['btree_E_list_conditional_address_difference']==5792,'Btree count mismatch')
    require(counts['lud_global_source_model_matches']==19840 and counts['lud_cacheable_load_model_matches']==11904
            and counts['lud_global_store_model_matches']==7936,'LUD source-model counts mismatch')
    result = dict(status='PASS_BOUNDED_EVIDENCE_CHECK_NOT_SOURCE_BINDING',counts=dict(counts),
        raw_trace_members_sparsely_read=len(handles),index_sha256=prior['index']['sha256'],
        decoded_index_sha256=decoded_hash.hexdigest(),lud_source_sha256=LUD_SOURCE_SHA,
        model_assumptions=['Unbound historical source default BLOCK_SIZE16','matrix_dim512 from prior header/list/source geometry',
            'matrix base0x7fd9eb500000 from retained memcpy list','ordinal2+3s has offset16s per source host schedule',
            'PC-to-source-operation labels fitted on first sample only; other records held out; no SASS/predicate binding'],
        lud_model_interpretation='Frozen firstP16 consumption is source-model-consistent; not original capture identity or a selected input interpretation',
        examples=examples,original_trace_changes=False,formal_input_created=False,simulator_launches=0)
    (a.output_dir/'INDEX_AND_SOURCE_MODEL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    with (a.output_dir/'LUD_GLOBAL_PC_MODEL_CHECK.tsv').open('x') as f:
        w = csv.writer(f,delimiter='\t',lineterminator='\n')
        w.writerow(['pc','opcode','source_operation','source_row','records','model_compatible_firstE','status'])
        for (pc,opcode),(kind,row) in sorted(operation_map.items()):
            w.writerow([pc,opcode,kind,row,pc_counts[('lud','_Z13lud_perimeterPfii',pc,opcode)],16,'SOURCE_MODEL_CONSISTENT_NOT_CAPTURE_BOUND'])
    print(json.dumps(dict(status=result['status'],counts=result['counts'])),flush=True)


if __name__=='__main__':
    main()
