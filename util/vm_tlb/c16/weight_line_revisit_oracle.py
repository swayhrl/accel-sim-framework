#!/usr/bin/env python3
"""CPU-only, per-accepted-shard sector/byte revisit census; no GPU access."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import cross_lineage_behavior_screen as prior


def tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open('w', encoding='utf-8', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows({field: row.get(field, '') for field in fields} for row in rows)


def json_file(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def compact_starts(starts: list[int], line_base: int) -> str:
    offsets = sorted(addr - line_base for addr in starts)
    if len(offsets) > 1 and len(set(offsets)) == len(offsets) and all(b-a == 2 for a,b in zip(offsets, offsets[1:])):
        return f'{offsets[0]}..{offsets[-1]}:2'
    return ','.join(map(str, offsets))


def classify(visits: list[dict]) -> str:
    if len(visits) < 2:
        return 'UNKNOWN'
    if len(visits) > 2:
        return 'MIXED'
    a,b = visits
    common = a['sectors'] & b['sectors']
    if not common:
        return 'DISJOINT_SECTOR_COMPLEMENT'
    if a['sectors'] == b['sectors']:
        if set(a['starts']) == set(b['starts']):
            return 'EXACT_BYTE_REVISIT'
        return 'SAME_SECTOR_REVISIT'
    return 'PARTIAL_SECTOR_OVERLAP'


def scope_counts(visits: list[dict], unit: str) -> tuple[int,int]:
    by_item = defaultdict(Counter)
    for visit in visits:
        items = visit['sectors'] if unit == 'sector' else visit['starts']
        for item in items:
            by_item[item][visit['cta']] += 1
    same = sum(sum(count-1 for count in cta.values()) for cta in by_item.values())
    cross = sum(len(cta)-1 for cta in by_item.values())
    return same,cross


def line_row(lineage: str, static: int, line: int, visits: list[dict]) -> dict:
    unique_sectors = set().union(*(v['sectors'] for v in visits))
    unique_starts = set().union(*(set(v['starts']) for v in visits))
    sector_visits = sum(len(v['sectors']) for v in visits)
    dynamic_bytes = 2*sum(len(v['starts']) for v in visits)
    unique_bytes = 2*len(unique_starts)
    same_sector,cross_sector = scope_counts(visits,'sector')
    same_start,cross_start = scope_counts(visits,'start')
    assert sector_visits-len(unique_sectors) == same_sector+cross_sector
    assert dynamic_bytes-unique_bytes == 2*(same_start+cross_start)
    ctas = {v['cta'] for v in visits}
    warp_ids = {(v['cta'],v['warp']) for v in visits}
    base = line*128
    descriptors = []
    for v in visits:
        cta = ','.join(map(str,v['cta']))
        sectors = ','.join(str(s-4*line) for s in sorted(v['sectors']))
        starts = compact_starts(v['starts'],base)
        descriptors.append(f'cta={cta};warp={v["warp"]};record_ordinal={v["ordinal"]};mref={static};sector={sectors};bf16_start_offset={starts};byte_range=[{min(v["starts"])-base},{max(v["starts"])-base+2})')
    return dict(lineage=lineage,static_index=static,line_base_hex=hex(base),warp_visit_count=len(visits),
                unique_sector_count=len(unique_sectors),sector_visit_count=sector_visits,
                duplicate_sector_visits=sector_visits-len(unique_sectors),
                unique_byte_count=unique_bytes,dynamic_byte_count=dynamic_bytes,
                duplicate_byte_count=dynamic_bytes-unique_bytes,
                same_CTA_revisit=int(any(sum(v['cta']==cta for v in visits)>1 for cta in ctas)),
                cross_CTA_revisit=int(len(ctas)>1),distinct_warp_identities=len(warp_ids),
                same_warp_revisit=int(len(warp_ids)<len(visits)),cross_warp_revisit=int(len(warp_ids)>1),
                same_CTA_duplicate_sector_visits=same_sector,
                cross_CTA_duplicate_sector_visits=cross_sector,same_CTA_duplicate_bytes=2*same_start,
                cross_CTA_duplicate_bytes=2*cross_start,classification=classify(visits),
                sector_ids_relative=','.join(str(s-4*line) for s in sorted(unique_sectors)),
                warp_visit_detail='|'.join(descriptors))


def scan_shard(lineage: str, item: dict, expected_context_sha: str) -> tuple[list[dict],Counter,dict]:
    trace = prior.check_file(item['trace'],item['trace_sha'])
    context = prior.check_file(item['context'],expected_context_sha)
    bounds = prior.context_bounds(context)
    if len(trace) < prior.HEADER.size or (len(trace)-prior.HEADER.size)%prior.RECORD.size:
        raise AssertionError('bad trace record size')
    magic,static,occ,produced,overflow,written = prior.HEADER.unpack_from(trace)
    nrecords = (len(trace)-prior.HEADER.size)//prior.RECORD.size
    if (magic,static,occ,overflow,produced,written) != (b'C16WARP1',item['static'],0,0,nrecords,nrecords):
        raise AssertionError('trace header closure')
    if item['declared'] is not None and nrecords != item['declared']:
        raise AssertionError('declared record count')
    lines = defaultdict(list)
    counts = Counter()
    observed_ctas = set()
    observed_warps = set()
    for ordinal,rec in enumerate(prior.RECORD.iter_unpack(memoryview(trace)[prior.HEADER.size:])):
        if rec[0] != static or not rec[1]:
            raise AssertionError('bad static/mask')
        cta = tuple(rec[2:5]); warp = rec[5]
        observed_ctas.add(cta); observed_warps.add((cta,warp))
        by_role = defaultdict(list)
        for lane,addr in enumerate(rec[6:]):
            if rec[1]>>lane&1:
                by_role[prior.role_for(addr,bounds)].append(addr)
        if len(by_role)!=1:
            raise AssertionError('mixed role warp')
        role,addresses = next(iter(by_role.items()))
        counts[f'{role}_warps']+=1
        counts[f'{role}_lanes']+=len(addresses)
        if role != 'WEIGHT':
            continue
        by_line = defaultdict(list)
        for addr in addresses:
            if addr%2:
                raise AssertionError('unaligned BF16 address')
            by_line[addr//128].append(addr)
        for line,starts in by_line.items():
            sectors = {addr//32 for addr in starts}
            lines[line].append(dict(cta=cta,warp=warp,ordinal=ordinal,starts=starts,sectors=sectors))
    rows = [line_row(lineage,static,line,visits) for line,visits in sorted(lines.items())]
    counts['weight_unique_lines']=len(lines)
    counts['weight_warp_line_visits']=sum(len(v) for v in lines.values())
    return rows,counts,dict(static_index=static,observed_ctas=len(observed_ctas),observed_warps=len(observed_warps),warp_records=nrecords)


def build(out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    prior_index_path = prior.OUT/'RAW_SHARD_INDEX.tsv'
    with prior_index_path.open(encoding='utf-8',newline='') as f:
        accepted = {(r['lineage'],int(r['static_index'])):r for r in csv.DictReader(f,delimiter='\t')}
    if len(accepted)!=729:
        raise AssertionError('prior raw index not complete')
    all_rows=[]; sector_rows=[]; byte_rows=[]; scope_rows=[]; mref_rows=[]; summary={}; selected_maps={}
    for lineage in ('DEEPSEEK','OLMOE','Q30'):
        cfg=prior.LINEAGES[lineage]
        run=prior.ROOT/'raw'/cfg['run']
        prior.check_file(run/'RUN_MANIFEST.json',cfg['manifest'])
        prior.check_file(prior.ROOT/'catalog'/'entries'/(cfg['run']+'.json'),cfg['catalog'])
        prior.check_file(prior.ROOT/'reports'/'transfer_acks'/(cfg['run']+'.TRANSFER_ACK.json'),cfg['ack'])
        manifest=json.loads((run/'WARP_SHARD_MANIFEST.json').read_bytes()) if lineage!='OLMOE' else {}
        items=prior.entries(lineage,run,manifest)
        if len(items)!=243:
            raise AssertionError('selected static count')
        if lineage=='OLMOE':
            map_path=run/'selector_authority'/'VARIANT_A_COMPLETE_STATIC_SELECTOR.canonical_v1.json'
            source_rows=json.loads(map_path.read_bytes())['rows']
        else:
            map_path=run/'STATIC_MREF_MAP.tsv'
            with map_path.open(encoding='utf-8',newline='') as f:
                source_rows=list(csv.DictReader(f,delimiter='\t'))
        source_map={int(r.get('static_index',r.get('nvbit_static_index'))):r for r in source_rows}
        source_sha=hashlib.sha256(map_path.read_bytes()).hexdigest()
        if any(x['static'] not in source_map for x in items):
            raise AssertionError('selected static missing from source map')
        selected_maps[lineage]={x['static']:(str(source_map[x['static']].get('instruction_offset',source_map[x['static']].get('offset'))),source_map[x['static']]['opcode'],source_map[x['static']]['sass']) for x in items}
        tally=Counter(); class_counts=Counter(); observed=[]
        for item in items:
            key=(lineage,item['static'])
            reference=accepted[key]
            if item['trace_sha'] != reference['trace_sha256']:
                raise AssertionError('trace SHA vs prior accepted raw index')
            rows,counts,geometry=scan_shard(lineage,item,reference['address_context_sha256'])
            if geometry['warp_records']!=int(reference['warp_records']):
                raise AssertionError('record count vs prior accepted raw index')
            if sum(counts[f'{r}_lanes'] for r in prior.ROLES)!=int(reference['active_lane_events']):
                raise AssertionError('lane count vs prior accepted raw index')
            if rows:
                tally['executed_weight_shards']+=1
            tally.update(counts)
            observed.append(geometry)
            static_tally=Counter()
            for row in rows:
                if lineage!='Q30':
                    all_rows.append(row)
                class_counts[row['classification']]+=1
                for field in ('warp_visit_count','unique_sector_count','sector_visit_count','duplicate_sector_visits','unique_byte_count','dynamic_byte_count','duplicate_byte_count','same_warp_revisit','cross_warp_revisit','same_CTA_duplicate_sector_visits','cross_CTA_duplicate_sector_visits','same_CTA_duplicate_bytes','cross_CTA_duplicate_bytes'):
                    tally[field]+=row[field]
                    static_tally[field]+=row[field]
            source=source_map[item['static']]
            mref_rows.append(dict(lineage=lineage,static_index=item['static'],classification='EXECUTED_WEIGHT' if rows else 'NO_WEIGHT',
                                  source_map_sha256=source_sha,instruction_offset=source.get('instruction_offset',source.get('offset')),
                                  opcode=source['opcode'],sass=source['sass'],
                                  same_static_mref='YES_WITHIN_SHARD',cross_static_mref='UNKNOWN_NOT_UNIONED',
                                  loop_iteration='UNKNOWN_NO_ORDINAL',observed_ctas=geometry['observed_ctas'],
                                  observed_warps=geometry['observed_warps'],**static_tally))
        if (sum(x['warp_records']>0 for x in observed),sum(x['warp_records']==0 for x in observed),sum(x['warp_records'] for x in observed),sum(tally[f'{r}_lanes'] for r in prior.ROLES)) != prior.EXPECTED[lineage]:
            raise AssertionError('raw accepted cohort totals')
        expected_visits={'DEEPSEEK':(360448,180224,2.0),'OLMOE':(131072,131072,1.0),'Q30':(589824,491520,1.2)}[lineage]
        if (tally['weight_warp_line_visits'],tally['weight_unique_lines']) != expected_visits[:2]:
            raise AssertionError('prior line metric cross-check')
        sector_fraction=tally['duplicate_sector_visits']/tally['sector_visit_count'] if tally['sector_visit_count'] else None
        byte_fraction=tally['duplicate_byte_count']/tally['dynamic_byte_count'] if tally['dynamic_byte_count'] else None
        summary[lineage]=dict(run_id=cfg['run'],shards=243,executed_weight_shards=tally['executed_weight_shards'],
                              static_source_map_sha256=source_sha,
                              weight_warp_line_visits=tally['weight_warp_line_visits'],weight_unique_128B_lines=tally['weight_unique_lines'],
                              line_visits_per_unique=tally['weight_warp_line_visits']/tally['weight_unique_lines'],
                              O0_avoidable_128B_line_visits=tally['weight_warp_line_visits']-tally['weight_unique_lines'],
                              O0_avoidable_fraction=1-tally['weight_unique_lines']/tally['weight_warp_line_visits'],
                              O1_dynamic_sector_visits=tally['sector_visit_count'],O1_unique_sectors=tally['unique_sector_count'],
                              O1_avoidable_sector_visits=tally['duplicate_sector_visits'],O1_avoidable_fraction=sector_fraction,
                              O1_avoidable_byte_equivalent=32*tally['duplicate_sector_visits'],
                              O2_dynamic_logical_bytes=tally['dynamic_byte_count'],O2_unique_logical_bytes=tally['unique_byte_count'],
                              O2_avoidable_logical_bytes=tally['duplicate_byte_count'],O2_avoidable_fraction=byte_fraction,
                              same_CTA_duplicate_sector_visits=tally['same_CTA_duplicate_sector_visits'],
                              cross_CTA_duplicate_sector_visits=tally['cross_CTA_duplicate_sector_visits'],
                              same_CTA_duplicate_bytes=tally['same_CTA_duplicate_bytes'],cross_CTA_duplicate_bytes=tally['cross_CTA_duplicate_bytes'],
                              same_warp_revisited_lines=tally['same_warp_revisit'],cross_warp_revisited_lines=tally['cross_warp_revisit'],
                              classes=dict(sorted(class_counts.items())),
                              weight_lane_bytes_per_weight_bytes=tally['dynamic_byte_count']/cfg['weight_bytes'],
                              observed_cta_counts=sorted(set(x['observed_ctas'] for x in observed if x['warp_records'])),
                              observed_warp_counts=sorted(set(x['observed_warps'] for x in observed if x['warp_records'])))
        sector_rows.append(dict(lineage=lineage,dynamic_sector_visits=tally['sector_visit_count'],unique_sectors=tally['unique_sector_count'],
                                avoidable_sector_visits=tally['duplicate_sector_visits'],avoidable_fraction=sector_fraction,
                                avoidable_byte_equivalent=32*tally['duplicate_sector_visits'],**{f'lines_{k}':v for k,v in sorted(class_counts.items())}))
        byte_rows.append(dict(lineage=lineage,dynamic_logical_bytes=tally['dynamic_byte_count'],unique_logical_bytes=tally['unique_byte_count'],
                              avoidable_logical_bytes=tally['duplicate_byte_count'],avoidable_fraction=byte_fraction))
        scope_rows.append(dict(lineage=lineage,same_CTA_duplicate_sector_visits=tally['same_CTA_duplicate_sector_visits'],
                               cross_CTA_duplicate_sector_visits=tally['cross_CTA_duplicate_sector_visits'],
                               same_CTA_duplicate_bytes=tally['same_CTA_duplicate_bytes'],cross_CTA_duplicate_bytes=tally['cross_CTA_duplicate_bytes']))
    sector_fields=list(sector_rows[0])+sorted(set().union(*(r.keys() for r in sector_rows))-set(sector_rows[0]))
    for row in sector_rows:
        for field in sector_fields:
            if field.startswith('lines_'):
                row.setdefault(field,0)
    mref_fields=list(mref_rows[0])+sorted(set().union(*(r.keys() for r in mref_rows))-set(mref_rows[0]))
    for row in mref_rows:
        for field in mref_fields:
            if field not in row:
                row[field]=0
    tsv(out/'LINE_REVISIT_DETAIL.tsv',all_rows,list(all_rows[0]))
    tsv(out/'SECTOR_REVISIT_SUMMARY.tsv',sector_rows,sector_fields)
    tsv(out/'BYTE_REVISIT_SUMMARY.tsv',byte_rows,list(byte_rows[0]))
    tsv(out/'CTA_SCOPE_BREAKDOWN.tsv',scope_rows,list(scope_rows[0]))
    tsv(out/'STATIC_MREF_REVISIT_MAP.tsv',mref_rows,mref_fields)
    deep_map,olmoe_map=selected_maps['DEEPSEEK'],selected_maps['OLMOE']
    common=set(deep_map)&set(olmoe_map)
    map_comparison=dict(deepseek_selected=len(deep_map),olmoe_selected=len(olmoe_map),common_static_index_count=len(common),
                        identical_offset_opcode_sass_count=sum(deep_map[k]==olmoe_map[k] for k in common),
                        different_static_indices=sorted(k for k in common if deep_map[k]!=olmoe_map[k]))
    json_file(out/'TRAFFIC_ORACLE.json',dict(authority_commit='734e6a7ca49bd8cbf16eeb0702cf80755afc23f1',
                                            scope='independent accepted shard replays; no cross-shard address union',
                                            O0='optimistic 128B line first-touch reference, not sector service',
                                            O1='32B sector visits per warp-line vs unique sectors per shard',
                                            O2='logical 2B BF16 lane reads vs exact unique bytes per shard',
                                            cache_hit='UNKNOWN',L2_miss='UNKNOWN',DRAM_bytes='UNKNOWN',time_saving='UNKNOWN',
                                            lineages=summary,template6_static_map_comparison=map_comparison))
    return summary


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path('docs/vm_tlb/review_packs/C16_DEEPSEEK_WEIGHT_LINE_REVISIT_ORACLE_SCREEN_174NEW_V1'))
    args=p.parse_args()
    result=build(args.out)
    print(json.dumps({k:{m:v for m,v in d.items() if m.startswith(('O0_','O1_','O2_')) or m in ('classes','observed_cta_counts','observed_warp_counts')} for k,d in result.items()},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
