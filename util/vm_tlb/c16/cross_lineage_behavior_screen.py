#!/usr/bin/env python3
"""CPU-only, per-shard C16WARP1 cross-lineage behavior screen."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import struct
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path('/root/share/mnt164/huangrulin/c16_ai_workload')
OUT = Path('docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_CROSS_LINEAGE_BEHAVIOR_SCREEN_174NEW_V1')
HEADER = struct.Struct('<8sIIQQQ')
RECORD = struct.Struct('<6I32Q')
PRIOR_CONSUMER_COMMIT='08536be9940590be101c7f5bac2117ba82056db5'
PRIOR_GEOMETRY_COMMIT='2afdf832273f31df496d7424ec6b426c6aabdfc3'
E3_COMMIT='378487015e513ed666c0929ca3f6c00392ff11c3'
TEMPORAL_AUDIT_COMMIT='72fdd0f89aa0d4d4ae8b0d55daea492fbae2f293'
TERMINAL_COMMIT='ca6c33ae0431d91aa7c6a43cbb79522402dd7580'
LINEAGES = {
    'Q30': dict(run='C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678',kind='legacy',catalog='80c9d1309fb8d3f15514c9668ac00a6d8839cb6858aca7e347755eed58d2e434',ack='f59c9181eb5a6371d93cf648ff15aa771f4af6de04bd9121c9bf2090fb2731f4',manifest='259b34c75ed8adbd8132d56e23a41fc02da97338f8510027f7da77ccb52dcd83',weight_bytes=3145728,input_width=768,output_width=2048,scope='S2 Decode3 Layer24 natural Expert21 down_proj; isolated replay',routing='top-8/128',template='gemvx template 7'),
    'DEEPSEEK': dict(run='C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23',kind='legacy',catalog='9ece3f570fbdaa8e026da39bee94c7f15b2c60bf14e292a66f6026104d18d81d',ack='fe4768a91606bbbf89f1b28a897f0a6648fb8e83d3d621093313e03743ec1acf',manifest='d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638',weight_bytes=5767168,input_width=1408,output_width=2048,scope='S2 selected decode Layer1 natural Expert4 down_proj; isolated replay',routing='top-6/64 routed plus 2 shared',template='gemvx template 6'),
    'OLMOE': dict(run='C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf',kind='olmoe',catalog='676422708f865c6b3287998dcde3dd126a469e83d3245bcf00fe11d07b9c1637',ack='9c4d08a960f53acece00dbb3143cba460c22bc638ff4a879833c0e4460b98e39',manifest='8f3e5e338166a2ebc4da6b9a55986980d31227f3d0e383ca5a1f24d0d924f31b',weight_bytes=4194304,input_width=1024,output_width=2048,scope='S2_TEXT B1/T2048/D32 Layer1 natural Expert58 down_proj actual-JIT A; isolated replay',routing='top-8/64',template='gemvx template 6, receipt-bound'),
}
EXPECTED = {'Q30':(41,202,100352,3147776),'DEEPSEEK':(169,74,362496,11538432),'OLMOE':(129,114,132096,4196352)}
ROLES = ('WEIGHT','INPUT','OUTPUT','OTHER')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def historical_json(commit: str, path: str) -> dict:
    return json.loads(subprocess.check_output(['git','show',f'{commit}:{path}']))


def historical_tsv(commit: str, path: str) -> list[dict[str,str]]:
    data=subprocess.check_output(['git','show',f'{commit}:{path}']).decode('utf-8')
    return list(csv.DictReader(io.StringIO(data),delimiter='\t'))


def check_file(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    if digest(data) != expected:
        raise AssertionError(f'SHA mismatch: {path}')
    return data


def role_for(addr: int, bounds: list[tuple[str,int,int]]) -> str:
    found = [r for r,lo,hi in bounds if lo <= addr < hi]
    if len(found) > 1:
        raise AssertionError('overlapping typed address ranges')
    return found[0] if found else 'OTHER'


def normalized_role(value: str) -> str:
    upper=value.upper()
    return next((role for role in ('WEIGHT','INPUT','OUTPUT') if role in upper),'OTHER')


def context_bounds(data: bytes) -> list[tuple[str,int,int]]:
    value = json.loads(data)
    if 'ranges' in value:
        entries = [(normalized_role(str(item.get('semantic_role',item.get('class','OTHER')))),item.get('ptr',item.get('address_start_hex')),item.get('bytes',item.get('storage_bytes'))) for item in value['ranges']]
    else:
        entries = [(key.upper(),item['ptr'],item['bytes']) for key,item in value.items() if isinstance(item,dict) and 'ptr' in item and 'bytes' in item]
    out = [(r,int(p,0) if isinstance(p,str) else int(p), (int(p,0) if isinstance(p,str) else int(p))+int(n)) for r,p,n in entries]
    if not out:
        raise AssertionError('no typed address bounds')
    return out


def entries(lineage: str, run: Path, manifest: dict) -> list[dict]:
    if lineage != 'OLMOE':
        out = []
        for item in manifest['shards']:
            out.append(dict(static=int(item['static_index']),trace=run/item.get('trace_relative_path',item.get('trace')),context=run/item.get('address_context_relative_path',item.get('address_context')),trace_sha=item['trace_sha256'],context_sha=item['address_context_sha256'],declared=int(item.get('record_count',item.get('records'))),status=item.get('terminal_status',item.get('classification'))))
        return sorted(out,key=lambda x:x['static'])
    out = []
    for receipt in sorted(run.glob('shards/static_*/SUPERVISOR_RECEIPT.json')):
        item = json.loads(receipt.read_bytes())
        static = int(item['selected_static'])
        # The accepted OLMoE manifest closes each final trace/context hash.
        out.append(dict(static=static,trace=receipt.parent/'trace.bin',context=receipt.parent/'ADDRESS_CONTEXT.json',trace_sha=item['c16_trace_sha256'],context_sha=None,declared=None,status=item['phase']))
    return sorted(out,key=lambda x:x['static'])


def quantile(values: list[int|float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0,math.ceil(p*len(ordered))-1)]


def concentration(values: list[int]) -> dict:
    ordered = sorted(values,reverse=True)
    total = sum(ordered)
    n = len(ordered)
    if not n or not total:
        return dict(top1=None,top5=None,top10=None,top_decile=None,gini=None,cv=None,normalized_entropy=None)
    mean = total/n
    entropy = -sum((v/total)*math.log(v/total) for v in ordered if v)
    # Equal populations have Gini 0 and normalized entropy 1.
    increasing = list(reversed(ordered))
    gini = 2*sum(i*v for i,v in enumerate(increasing,1))/(n*total)-(n+1)/n
    return dict(top1=sum(ordered[:1])/total,top5=sum(ordered[:5])/total,top10=sum(ordered[:10])/total,top_decile=sum(ordered[:math.ceil(n/10)])/total,gini=max(0.0,gini),cv=statistics.pstdev(ordered)/mean,normalized_entropy=min(1.0,entropy/math.log(n)) if n>1 else 1.0)


def parse_shard(item: dict) -> tuple[dict,dict]:
    trace = check_file(item['trace'],item['trace_sha'])
    context_data = item['context'].read_bytes() if item['context_sha'] is None else check_file(item['context'],item['context_sha'])
    bounds = context_bounds(context_data)
    if len(trace) < HEADER.size or (len(trace)-HEADER.size)%RECORD.size:
        raise AssertionError('record alignment')
    magic,static,occ,produced,overflow,written = HEADER.unpack_from(trace)
    records = (len(trace)-HEADER.size)//RECORD.size
    if magic != b'C16WARP1' or static != item['static'] or occ != 0 or overflow != 0 or produced != written or written != records:
        raise AssertionError('C16WARP1 header closure')
    if item['declared'] is not None and item['declared'] != records:
        raise AssertionError('manifest record count')
    if records == 0 and 'ZERO' not in str(item['status']) and item['status'] != 'CLEAN_EXIT':
        raise AssertionError('zero shard without terminal')
    roles = Counter()
    role_warps = Counter()
    line_occ = defaultdict(Counter)  # role -> 128B line -> number of distinct warp records
    unique_lines = defaultdict(set)
    geometry = defaultdict(lambda: dict(warps=0,lanes=0,distinct_starts=0,lines=0,sectors=0,logical_bytes=0,unique_start_bytes=0,sector_proxy_bytes=0,full_warps=0,lane_sparse=0,same_line=0,multi_line=0,scattered=0,contiguous=0,duplicated_start=0,active_lane_hist=Counter(),unique_start_hist=Counter(),line_hist=Counter(),sector_hist=Counter(),stride_hist=Counter()))
    other = 0
    for rec in RECORD.iter_unpack(memoryview(trace)[HEADER.size:]):
        if rec[0] != item['static']:
            raise AssertionError('static index in record')
        mask = rec[1]
        if not mask:
            raise AssertionError('empty active warp')
        by_role = defaultdict(list)
        for lane,addr in enumerate(rec[6:]):
            if mask>>lane&1:
                role = role_for(addr,bounds)
                by_role[role].append(addr)
                roles[role] += 1
        if len(by_role)>1:
            raise AssertionError('mixed role in one record: denominator ambiguous')
        role,addresses = next(iter(by_role.items()))
        if role == 'OTHER':
            other += len(addresses)
        role_warps[role]+=1
        g=geometry[role]
        n=len(addresses)
        starts=set(addresses)
        lines={a//128 for a in addresses}
        sectors={a//32 for a in addresses}
        g['warps']+=1;g['lanes']+=n;g['distinct_starts']+=len(starts);g['lines']+=len(lines);g['sectors']+=len(sectors)
        g['logical_bytes']+=2*n;g['unique_start_bytes']+=2*len(starts);g['sector_proxy_bytes']+=32*len(sectors)
        g['full_warps']+=n==32;g['lane_sparse']+=n<16;g['same_line']+=len(lines)==1;g['multi_line']+=len(lines)>1;g['scattered']+=len(sectors)>=8;g['contiguous']+=len(sectors)<=2 and n>=16;g['duplicated_start']+=len(starts)<n
        for name,value in [('active_lane_hist',n),('unique_start_hist',len(starts)),('line_hist',len(lines)),('sector_hist',len(sectors))]:g[name][value]+=1
        ordered=sorted(starts)
        strides=[b-a for a,b in zip(ordered,ordered[1:])]
        if strides:g['stride_hist'][Counter(strides).most_common(1)[0][0]]+=1
        for line in lines:
            unique_lines[role].add(line)
            line_occ[role][line]+=1
    row = dict(static_index=item['static'],classification='EXECUTED' if records else 'ZERO_EXECUTION_PROVEN',warp_records=records,active_lane_events=sum(roles.values()),role=next(iter(role_warps)) if len(role_warps)==1 else 'MIXED' if roles else 'NONE',unique_128B_lines=sum(len(v) for v in unique_lines.values()),trace_sha256=item['trace_sha'],address_context_sha256=digest(context_data))
    for role in ROLES:
        row[f'{role}_warps']=role_warps[role];row[f'{role}_events']=roles[role];row[f'{role}_unique_lines']=len(unique_lines[role]);row[f'{role}_cross_warp_shared_lines']=sum(count>1 for count in line_occ[role].values())
    return row,geometry


def inspect_lineage(name: str, cfg: dict) -> tuple[dict,list[dict],dict]:
    run=ROOT/'raw'/cfg['run']
    manifest=check_file(run/'RUN_MANIFEST.json',cfg['manifest'])
    catalog=check_file(ROOT/'catalog'/'entries'/(cfg['run']+'.json'),cfg['catalog'])
    ack=check_file(ROOT/'reports'/'transfer_acks'/(cfg['run']+'.TRANSFER_ACK.json'),cfg['ack'])
    if not catalog or not ack:raise AssertionError('empty provenance')
    shard_manifest=json.loads((run/'WARP_SHARD_MANIFEST.json').read_bytes()) if name!='OLMOE' else {}
    items=entries(name,run,shard_manifest)
    if len(items)!=243 or len({x['static'] for x in items})!=243:
        raise AssertionError('243 selected static paths')
    all_rows=[]
    totals=defaultdict(lambda:defaultdict(int))
    hists=defaultdict(lambda:defaultdict(Counter))
    for item in items:
        row,geo=parse_shard(item)
        all_rows.append(row)
        for role,g in geo.items():
            for key,value in g.items():
                if isinstance(value,Counter):hists[role][key].update(value)
                else:totals[role][key]+=value
    executed=sum(row['classification']=='EXECUTED' for row in all_rows)
    zeros=243-executed
    warps=sum(row['warp_records'] for row in all_rows)
    lanes=sum(row['active_lane_events'] for row in all_rows)
    if (executed,zeros,warps,lanes)!=EXPECTED[name]:
        raise AssertionError(f'raw historical cross-check {name}: {(executed,zeros,warps,lanes)}')
    if sum(totals[r]['lanes'] for r in ROLES)!=lanes or sum(totals[r]['warps'] for r in ROLES)!=warps:
        raise AssertionError(f'role conservation {name}: lanes={lanes}, role_lanes={dict((r,totals[r]["lanes"]) for r in ROLES)}, warps={warps}, role_warps={dict((r,totals[r]["warps"]) for r in ROLES)}')
    summary=dict(lineage=name,run_id=cfg['run'],selected_static=243,executed_static=executed,zero_static=zeros,executed_fraction=executed/243,zero_fraction=zeros/243,warps=warps,events=lanes,warps_per_executed_shard=warps/executed,events_per_warp=lanes/warps,active_lane_density=lanes/(32*warps),weight_bytes=cfg['weight_bytes'],input_width=cfg['input_width'],output_width=cfg['output_width'],scope=cfg['scope'],routing=cfg['routing'],template=cfg['template'],manifest_sha256=cfg['manifest'],catalog_sha256=cfg['catalog'],transfer_ack_sha256=cfg['ack'])
    return summary,all_rows,dict(totals=totals,hists=hists)


def tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,delimiter='\t',lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({key:('UNKNOWN' if row.get(key) is None else row.get(key)) for key in fields})


def build(out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    summaries={}; shards={}; geometry={}
    for name,cfg in LINEAGES.items():
        summary,rows,g=inspect_lineage(name,cfg)
        summaries[name]=summary;shards[name]=rows;geometry[name]=g
    accepted=historical_json(PRIOR_CONSUMER_COMMIT,'docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/STATIC_EXECUTION_COMPARISON.json')
    for name,s in summaries.items():
        ref=accepted[name]
        if any(s[a]!=ref[b] for a,b in [('selected_static','selected_static_count'),('executed_static','executed_static_count'),('zero_static','proven_zero_static_count'),('warps','dynamic_warp_records'),('events','active_lane_events')]):
            raise AssertionError(f'prior accepted raw consumer mismatch: {name}')
        old=historical_tsv(PRIOR_CONSUMER_COMMIT,f'docs/vm_tlb/review_packs/C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1/{name}_PER_SHARD.tsv')
        previous={int(row['static_index']):row for row in old}
        if len(previous)!=243:
            raise AssertionError(f'prior per-shard table count: {name}')
        for row in shards[name]:
            prior=previous[row['static_index']]
            if (row['trace_sha256']!=prior['trace_sha256'] or row['address_context_sha256']!=prior['address_context_sha256'] or row['warp_records']!=int(prior['warp_records']) or row['active_lane_events']!=int(prior['active_lane_events']) or row['unique_128B_lines']!=int(prior['unique_128B_lines'])):
                raise AssertionError(f'prior per-shard raw recompute mismatch: {name}/{row["static_index"]}')
    prior_geometry=historical_json(PRIOR_GEOMETRY_COMMIT,'docs/vm_tlb/review_packs/C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1/FINAL_DECISION.json')
    if prior_geometry['status']!='WARP_REQUEST_GEOMETRY_CHARACTERIZED_SCOPED':raise AssertionError('prior geometry authority')
    e3=historical_json(E3_COMMIT,'docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1/NEXT_STEP_DECISION.json')
    if e3['decision']!='STOP_LIGHTWEIGHT_E3_NO_DEEP_CAPTURE':raise AssertionError('Q30 E3 authority')
    temporal=historical_json(TEMPORAL_AUDIT_COMMIT,'docs/vm_tlb/review_packs/C16_MOE_TEMPORAL_PERIODICITY_POSTHOC_AUDIT_V1/FINAL_DECISION.json')
    if temporal['cross_model_periodicity']['classification']!='NOT_COMPARABLE':raise AssertionError('routing temporal authority')
    ledger=[];coverage=[];warp_geometry=[];spatial=[];reuse=[];phase=[]
    for name,summary in summaries.items():
        cfg=LINEAGES[name]
        ledger.append(dict(lineage=name,authority_kind='accepted durable C16WARP1 selected expert down_proj replay',run_id=cfg['run'],raw_root=str(ROOT/'raw'/cfg['run']),raw_manifest_sha256=cfg['manifest'],catalog_sha256=cfg['catalog'],transfer_ack_sha256=cfg['ack'],prior_consumer='C16_THREE_LINEAGE_MOE_CONSUMER_174NEW_V1@'+PRIOR_CONSUMER_COMMIT,geometry_consumer='C16_MOE_WARP_REQUEST_GEOMETRY_SCREEN_174NEW_V1@'+PRIOR_GEOMETRY_COMMIT,scope=cfg['scope'],routing=cfg['routing'],implementation=cfg['template'],status='RAW_SHA_AND_COUNT_PASS'))
        weight_events=sum(r['WEIGHT_events'] for r in shards[name])
        coverage.append(dict(lineage=name,scope=cfg['scope'],selected_static=243,executed_static=summary['executed_static'],zero_static=summary['zero_static'],executed_fraction=summary['executed_fraction'],zero_fraction=summary['zero_fraction'],warps=summary['warps'],events=summary['events'],warps_per_executed_shard=summary['warps_per_executed_shard'],events_per_warp=summary['events_per_warp'],active_lane_density=summary['active_lane_density'],selected_modules=1,expert_invocations_in_replay=1,events_per_selected_module=summary['events'],weight_lane_logical_bytes_per_weight_byte=2*weight_events/summary['weight_bytes'],cross_lineage_token_denominator='UNKNOWN_UNMATCHED_DECODE_POINTS'))
        for role in ROLES:
            g=geometry[name]['totals'][role]
            h=geometry[name]['hists'][role]
            warps=g['warps']; events=g['lanes']; lines=g['lines']; sectors=g['sectors']
            warp_geometry.append(dict(lineage=name,role=role,warps=warps,events=events,event_share=events/summary['events'] if summary['events'] else None,warps_share=warps/summary['warps'] if summary['warps'] else None,active_lanes_per_warp=events/warps if warps else None,full_warp_fraction=g['full_warps']/warps if warps else None,lane_sparse_fraction=g['lane_sparse']/warps if warps else None,distinct_starts_per_warp=g['distinct_starts']/warps if warps else None,lines_128B_per_warp=lines/warps if warps else None,sectors_32B_proxy_per_warp=sectors/warps if warps else None,sector_proxy_share=(32*sectors)/sum(32*geometry[name]['totals'][r]['sectors'] for r in ROLES) if sectors else 0,same_line_warp_fraction=g['same_line']/warps if warps else None,multi_line_warp_fraction=g['multi_line']/warps if warps else None,scattered_warp_fraction=g['scattered']/warps if warps else None,contiguous_warp_fraction=g['contiguous']/warps if warps else None,duplicated_start_fraction=g['duplicated_start']/warps if warps else None,start_multiplicity=events/g['distinct_starts'] if g['distinct_starts'] else None,sector_fill=g['unique_start_bytes']/g['sector_proxy_bytes'] if g['sector_proxy_bytes'] else None,active_lanes_p50=quantile(list(h['active_lane_hist'].elements()),.5),unique_start_p50=quantile(list(h['unique_start_hist'].elements()),.5),line128_p50=quantile(list(h['line_hist'].elements()),.5),sector32_p50=quantile(list(h['sector_hist'].elements()),.5),modal_stride_bytes=h['stride_hist'].most_common(1)[0][0] if h['stride_hist'] else 'UNKNOWN',geometry_label='DESCRIPTIVE_ONLY'))
            subset=[row for row in shards[name] if row[f'{role}_events']>0]
            for scope,items in [('EXECUTED_ROLE_SHARDS',subset),('ALL_243_SELECTED_PATHS',shards[name])]:
                for metric,col in [('events',f'{role}_events'),('warps',f'{role}_warps'),('sum_per_shard_unique_lines',f'{role}_unique_lines')]:
                    c=concentration([r[col] for r in items])
                    spatial.append(dict(lineage=name,role=role,scope=scope,metric=metric,object_kind='static_MREF_shard',object_count=len(items),total=sum(r[col] for r in items),**c))
            unique=sum(r[f'{role}_unique_lines'] for r in shards[name]);shared=sum(r[f'{role}_cross_warp_shared_lines'] for r in shards[name])
            role_warp_line_visits=geometry[name]['totals'][role]['lines']
            footprint=[r[f'{role}_unique_lines']*128/summary['weight_bytes'] for r in shards[name] if role=='WEIGHT' and r[f'{role}_events']>0]
            reuse.append(dict(lineage=name,role=role,scope='sum of per-shard values; never a cross-shard union',dynamic_lane_refs=events,sum_unique_128B_lines=unique,unique_lines_per_lane_ref=unique/events if events else None,warp_line_visits=role_warp_line_visits,warp_visits_per_unique_line_within_shard=role_warp_line_visits/unique if unique else None,cross_warp_shared_line_fraction_within_shard=shared/unique if unique else None,short_window_reuse='UNKNOWN_NO_COMPARABLE_ORDER_AUTHORITY',same_role_reuse='DESCRIPTIVE_CROSS_WARP_LINE_SHARING_ONLY',cross_role_reuse='UNKNOWN_CROSS_SHARD_REPLAY_PROCESS_IDENTITY',median_per_executed_shard_footprint_fraction_of_weight_bytes=quantile(footprint,.5) if footprint else None,cache_hit_rate='UNKNOWN',dram_bytes='UNKNOWN'))
        phase.append(dict(lineage=name,scope=cfg['scope'],within_shard_record_order='UNKNOWN_COMPARABLE_TEMPORAL_ORDER',across_shard_order='UNKNOWN_SEPARATE_REPLAYS',early_middle_late='UNKNOWN',module_transition='UNKNOWN_ONE_MODULE_ANCHOR',expert_transition='UNKNOWN_ONE_SELECTED_EXPERT',operator_transition='UNKNOWN_ONE_DOWN_PROJ',phase_burst='UNKNOWN',phase_shift='UNKNOWN',working_set_reset='UNKNOWN',role_alternation='STATIC_PATH_ORDER_NOT_RUNTIME_ORDER'))

    tsv(out/'LINEAGE_AUTHORITY_LEDGER.tsv',ledger,list(ledger[0]))
    raw_index=[dict(lineage=name,run_id=LINEAGES[name]['run'],static_index=r['static_index'],classification=r['classification'],trace_sha256=r['trace_sha256'],address_context_sha256=r['address_context_sha256'],warp_records=r['warp_records'],active_lane_events=r['active_lane_events']) for name in LINEAGES for r in shards[name]]
    tsv(out/'RAW_SHARD_INDEX.tsv',raw_index,list(raw_index[0]))
    tsv(out/'EXECUTION_COVERAGE.tsv',coverage,list(coverage[0]))
    tsv(out/'WARP_REQUEST_GEOMETRY.tsv',warp_geometry,list(warp_geometry[0]))
    tsv(out/'SPATIAL_CONCENTRATION.tsv',spatial,list(spatial[0]))
    tsv(out/'REUSE_FOOTPRINT_PROXIES.tsv',reuse,list(reuse[0]))
    tsv(out/'PHASE_BEHAVIOR.tsv',phase,list(phase[0]))

    q=next(r for r in warp_geometry if r['lineage']=='Q30' and r['role']=='WEIGHT')
    d=next(r for r in warp_geometry if r['lineage']=='DEEPSEEK' and r['role']=='WEIGHT')
    o=next(r for r in warp_geometry if r['lineage']=='OLMOE' and r['role']=='WEIGHT')
    if not(q['sector_fill']<.1 and d['sector_fill']>.9 and o['sector_fill']>.9):raise AssertionError('geometry cross-check')
    if not all(30 < s['events_per_warp'] <= 32 for s in summaries.values()):raise AssertionError('active-lane cross-check')
    normalized={name:{'executed_fraction':s['executed_fraction'],'warps_per_executed_shard':s['warps_per_executed_shard'],'events_per_warp':s['events_per_warp'],'active_lane_density':s['active_lane_density']} for name,s in summaries.items()}
    # Every observed contrast must satisfy all five admission criteria.
    weight_reuse={r['lineage']:r for r in reuse if r['role']=='WEIGHT'}
    d_reuse=weight_reuse['DEEPSEEK']['warp_visits_per_unique_line_within_shard']
    q_reuse=weight_reuse['Q30']['warp_visits_per_unique_line_within_shard']
    o_reuse=weight_reuse['OLMOE']['warp_visits_per_unique_line_within_shard']
    weight_byte_ratio={r['lineage']:r['weight_lane_logical_bytes_per_weight_byte'] for r in coverage}
    deepseek_distinct=(d_reuse>=1.8 and q_reuse<=1.3 and o_reuse<=1.2 and weight_byte_ratio['DEEPSEEK']>1.9 and weight_byte_ratio['Q30']<1.1 and weight_byte_ratio['OLMOE']<1.1)
    gates=[dict(id='Q30_EXECUTED_COVERAGE',A=True,B=False,C=False,D=True,E=False,reason='41/243 versus 169/243 and 129/243 is a static coverage contrast; different code and one selected module per lineage'),dict(id='Q30_SCATTERED_REQUEST_GEOMETRY',A=True,B=True,C=True,D=False,E=True,reason='32-sector sparse Q30 versus one/two-sector DeepSeek/OLMoE persists per warp and role, but C16 warp geometry already classified familiar gemvx template/coalescing behavior; no new residual opportunity'),dict(id='DEEPSEEK_OLMOE_INPUT_BROADCAST',A=False,B=True,C=True,D=False,E=True,reason='DeepSeek and OLMoE share the two-lane input duplication; familiar within-warp broadcast and coupled template-6'),dict(id='DEEPSEEK_WEIGHT_LINE_REVISIT',A=deepseek_distinct,B=deepseek_distinct,C=deepseek_distinct,D=True,E=True,reason='within one shard, DeepSeek weight lines are touched by two warp records per unique line versus Q30 1.2 and OLMoE 1.0; survives role/warp/weight-byte normalization; different from the closed W4 cross-M mapping and from within-warp input broadcast, but exact cause and time value are unknown'),dict(id='SHARD_EVENT_CONCENTRATION',A=False,B=True,C=False,D=True,E=False,reason='top shares arise from differing executed static counts and one isolated module; no module/expert concentration population'),dict(id='PHASE_ROUTING',A=False,B=False,C=False,D=True,E=False,reason='C16WARP1 has no cross-shard chronology; Q30 E3 balanced proxy already sufficient, OLMoE lag-11 posthoc origin unresolved')]
    qualified=[x['id'] for x in gates if all(x[k] for k in 'ABCDE')]
    if qualified != ['DEEPSEEK_WEIGHT_LINE_REVISIT']:
        raise AssertionError(f'candidate gate changed: {qualified}')
    report='# Cross-lineage anomalies and admission\n\n'
    report+='The accepted observations are three different natural routed expert `down_proj` invocations replayed in isolation, not a matched population across all three models. All 243 selected static paths per model were hash checked.\n\n'
    report+='| Contrast | Q30 | DeepSeek | OLMoE | Reading |\n|---|---:|---:|---:|---|\n'
    report+=f"| Executed static paths | {summaries['Q30']['executed_static']}/243 | {summaries['DEEPSEEK']['executed_static']}/243 | {summaries['OLMOE']['executed_static']}/243 | Coverage and static code differ |\n"
    report+=f"| Warps per executed static path | {summaries['Q30']['warps_per_executed_shard']:.1f} | {summaries['DEEPSEEK']['warps_per_executed_shard']:.1f} | {summaries['OLMOE']['warps_per_executed_shard']:.1f} | Static instruction work differs even after coverage normalization |\n"
    report+=f"| Weight sector fill proxy | {q['sector_fill']:.4f} | {d['sector_fill']:.4f} | {o['sector_fill']:.4f} | Per warp/role geometry differs; cache traffic is unknown |\n\n"
    report+='Weight and input each contribute about half of active lane events in all three, while sector proxy differs. Q30 full warps touch widely separated sectors; DeepSeek/OLMoE input warps repeat 16 BF16 starts over 32 lanes and weight warps are compact. This geometry was already characterized as familiar coalescing under different gemvx templates.\n\n'
    report+=f"One additional within-shard contrast survives: DeepSeek has {d_reuse:.3f} warp-line visits per distinct weight line, Q30 {q_reuse:.3f}, OLMoE {o_reuse:.3f}. DeepSeek has {weight_byte_ratio['DEEPSEEK']:.3f} logical weight lane bytes per logical weight byte, versus {weight_byte_ratio['Q30']:.3f} and {weight_byte_ratio['OLMOE']:.3f}. These are repeated line touches within the same static shard replay, not measured cache misses or duplicate DRAM fetches. DeepSeek and OLMoE share a receipt-bound gemvx template-6 family but differ in K width and runtime shape; this screen does not assign causality to model lineage.\n\n"
    report+='The role-conditioned executed-shard event Gini values are 0.1333 (Q30 weight), 0.0433 (DeepSeek), and 0 (OLMoE). All-selected-path Gini is much larger because many static paths have proven zero execution. No module/expert population concentration is available from one selected expert each. Nearly all WEIGHT/INPUT records have 32 active lanes; sparse OUTPUT stores explain the small difference in overall active-lane density.\n\n'
    report+='No module or expert hotspot can be inferred from one selected module and one expert invocation per lineage. Static shard concentration is reported descriptively in `SPATIAL_CONCENTRATION.tsv`. The sum of per-shard unique lines is not a cross-replay address union. C16WARP1 does not supply comparable cross-shard time order or a matched token population; phase claims remain UNKNOWN.\n\n'
    report+='Admission gate (A lineage contrast, B normalization persistence, C beyond coverage, D distinct from closed C16 directions, E architectural relevance):\n\n'
    for g in gates:report+=f"- `{g['id']}`: {''.join(k if g[k] else '-' for k in 'ABCDE')}; {g['reason']}.\n"
    report+='\nOne descriptive phenomenon passes all five gates for **oracle screening only**: `DEEPSEEK_WEIGHT_LINE_REVISIT`. Its closest known capabilities are CUDA warp coalescing and GEMV implementation choice, as described in the [NVIDIA CUDA Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) and [cuBLAS GEMV documentation](https://docs.nvidia.com/cuda/cublas/). Existing C16 warp geometry explains the within-warp pattern but did not classify this within-shard cross-warp revisit contrast. A next CPU-only oracle would bound avoidable request/line service under the exact DeepSeek static path and compare a matched shape/backend control before any mechanism or native experiment. If the bound is small or software scheduling removes the revisit, stop. No independent lineage holdout exists. The accepted Q30 E3 result and OLMoE posthoc temporal audit remain scoped and do not establish cross-model routing skew.\n'
    (out/'CROSS_LINEAGE_ANOMALIES.md').write_text(report,encoding='utf-8')
    (out/'NORMALIZATION_CONTRACT.md').write_text('# Normalization contract\n\n- Denominator one: 243 selected static MREF paths per isolated module, with executed and terminal zero paths kept separately. Selected path identity differs across lineages.\n- Warps per executed path and lane events per warp remove raw path-count scale. Active-lane density is active lanes divided by 32 times warp records.\n- Each trace is one selected natural routed expert `down_proj` invocation. Per selected module and per invocation values are numerically identical to its selected replay total; they do not describe a model-wide population. Cross-lineage per-token or per-routing-event rates are UNKNOWN because Q30 Decode3, DeepSeek selected decode and OLMoE D32 are not matched tokens or equivalent expert populations.\n- Logical BF16 weight bytes (Q30 3,145,728; DeepSeek 5,767,168; OLMoE 4,194,304) normalize selected module scale. They do not describe measured bytes transferred.\n- Geometry conditions on WEIGHT, INPUT, OUTPUT and OTHER; unique start address, 32B sector proxy and 128B line proxy are counted within each warp record. A sector proxy is not a cache transaction.\n- Spatial concentration uses selected static MREF shards and is reported both among executed role shards and all 243 selected paths. Module/expert concentration is UNKNOWN with one module/expert per lineage.\n- Unique 128B lines and cross-warp shared-line fractions are computed within each shard only. Separate shard replays may have different process addresses. Do not union them, infer cache hits, or assign chronology.\n- C16WARP1 CTA/warp fields give spatial identity; its raw shards do not establish comparable natural ordering across paths. Short-window and phase metrics stay UNKNOWN.\n',encoding='utf-8')
    (out/'HOLDOUT_PLAN.md').write_text('# Holdout plan\n\nAll Q30, DeepSeek and OLMoE anchors were inspected for discovery. `NO_INDEPENDENT_LINEAGE_HOLDOUT`. The one candidate is discovery-only. Freeze a fourth independent lineage or an untouched matched implementation/shape before looking at its result. First complete a CPU-only, source-bound request/line-service oracle for the DeepSeek static path and compare a matched control. This Goal does not run or authorize a new experiment. A later GPU/model capture needs separate authorization.\n',encoding='utf-8')
    final=dict(schema_version=1,goal='C16_PROBLEM_DISCOVERY_V2_CROSS_LINEAGE_BEHAVIOR_SCREEN',status='PASS_CPU_ONLY',decision='CROSS_LINEAGE_ANOMALY_QUALIFIED_FOR_ORACLE_SCREEN',qualified_candidate_count=len(qualified),qualified_candidates=qualified,admission_gates=gates,discovery_lineages=list(LINEAGES),independent_lineage_holdout='NO_INDEPENDENT_LINEAGE_HOLDOUT',new_experiment_authorized=False,gpu_used=False,simulator_used=False,normalization=normalized,weight_revisit={name:{'warp_visits_per_unique_line_within_shard':weight_reuse[name]['warp_visits_per_unique_line_within_shard'],'cross_warp_shared_line_fraction_within_shard':weight_reuse[name]['cross_warp_shared_line_fraction_within_shard'],'logical_weight_lane_bytes_per_weight_byte':weight_byte_ratio[name]} for name in LINEAGES},authority={name:{key:cfg[key] for key in ('run','manifest','catalog','ack')} for name,cfg in LINEAGES.items()},boundaries=['one selected expert/module per lineage','different decode points and input widths','shared gemvx implementation family','no cross-shard chronology or address union','no cache/TLB/DRAM claim'])
    (out/'FINAL_DECISION.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (out/'README.md').write_text('# C16 cross-lineage behavior screen\n\nCPU-only raw C16WARP1 consumer. Start with `FINAL_DECISION.json`, then `CROSS_LINEAGE_ANOMALIES.md`; TSVs contain reproducible denominators and descriptive results. The accepted Q30 E3 and warp geometry screens are context, not new producer data.\n',encoding='utf-8')
    source_anchors=dict(schema_version=1,terminal_handoff_commit=TERMINAL_COMMIT,prior_three_lineage_consumer=PRIOR_CONSUMER_COMMIT,prior_warp_geometry_screen=PRIOR_GEOMETRY_COMMIT,q30_e3_routing=E3_COMMIT,olmoe_temporal_posthoc=TEMPORAL_AUDIT_COMMIT,raw_root=str(ROOT),lineages={name:{'run_id':cfg['run'],'run_manifest_sha256':cfg['manifest'],'catalog_sha256':cfg['catalog'],'transfer_ack_sha256':cfg['ack']} for name,cfg in LINEAGES.items()},record_schema={'header':'<8sIIQQQ','record':'<6I32Q','warp_record_bytes':RECORD.size,'no_cross_shard_launch_or_time_identity':True})
    (out/'SOURCE_ANCHORS.json').write_text(json.dumps(source_anchors,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    validation=dict(status='PASS',lineage_count=3,selected_static_each=243,raw_shards_checked=len(raw_index),raw_manifest_catalog_ack_sha_pass=True,record_header_and_count_pass=True,per_shard_sha_count_line_pass_against_prior_consumer=True,warp_role_line_conservation_pass=True,previous_geometry_screen_status=prior_geometry['status'],q30_e3_stop=e3['decision'],temporal_cross_model_status=temporal['cross_model_periodicity']['classification'],gpu_used=False,simulator_used=False)
    (out/'VALIDATION_SUMMARY.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (out/'OPEN_ISSUES.md').write_text('# Open issues\n\n- DeepSeek weight-line revisit is descriptive. Its source-level cause, cache transaction count, miss rate, DRAM traffic and elapsed-time contribution are UNKNOWN.\n- DeepSeek, OLMoE and Q30 differ in input width, selected decode point and gemvx template; a lineage causal claim needs a matched control.\n- All three available lineages were used in discovery; there is no independent lineage holdout.\n- Cross-shard address identity and chronology, whole-model operator role composition, module/expert population skew and phase behavior are not recoverable from these isolated shards.\n',encoding='utf-8')
    (out/'COMMIT_HISTORY.md').write_text(f'# Source and stage history\n\n- Terminal project state: `{TERMINAL_COMMIT}`.\n- Accepted three-lineage consumer: `{PRIOR_CONSUMER_COMMIT}`.\n- Accepted warp geometry screen: `{PRIOR_GEOMETRY_COMMIT}`.\n- Q30 E3 routing: `{E3_COMMIT}`.\n- OLMoE temporal posthoc audit: `{TEMPORAL_AUDIT_COMMIT}`.\n- This stage branches from the terminal state; the final stage commit is the Git HEAD containing this review pack.\n',encoding='utf-8')
    files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (out/'SHA256SUMS').write_text(''.join(f'{digest(p.read_bytes())}  {p.name}\n' for p in files),encoding='utf-8')
    return final


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=OUT);a=p.parse_args();print(json.dumps(build(a.out),sort_keys=True))


if __name__=='__main__':main()
