#!/usr/bin/env python3
"""Common raw-evidence consumer for the three accepted C16 MoE anchors."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, struct
from collections import Counter
from pathlib import Path

HEADER=struct.Struct('<8sIIQQQ'); RECORD=struct.Struct('<6I32Q'); SIZES=(128,4096,65536,2*1024*1024)
CONFIG={
 'q30': {'run':'C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678','model':'Qwen3-30B-A3B','scope':'S2 Decode3 Layer24 natural Expert21 down_proj','topology':'top-8/128','widths':[768,2048],'shape':[2048,768],'weight_bytes':3145728,'historical':{'selected':243,'executed':41,'zero':202,'warps':100352,'lanes':3147776},'adapter':'q30'},
 'deepseek': {'run':'C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23','model':'DeepSeek-V2-Lite','scope':'S2 selected decode Layer1 natural Expert4 down_proj','topology':'top-6/64 routed + 2 shared','widths':[1408,2048],'shape':[2048,1408],'weight_bytes':5767168,'historical':{'selected':243,'executed':169,'zero':74,'warps':362496,'lanes':11538432},'adapter':'deepseek'},
 'olmoe': {'run':'C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf','model':'OLMoE-1B-7B','scope':'S2_TEXT B1/T2048/D32 Layer1 decode32 natural Expert58 down_proj actual-JIT variant A','topology':'top-8/64','widths':[1024,2048],'shape':[2048,1024],'weight_bytes':4194304,'historical':{'selected':243,'executed':129,'zero':114,'warps':132096,'lanes':4196352},'adapter':'olmoe'},
}

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def role(name):
    value=name.upper()
    if 'WEIGHT' in value:return 'WEIGHT'
    if 'INPUT' in value:return 'INPUT'
    if 'OUTPUT' in value:return 'OUTPUT'
    return 'OTHER'
def quant(values):
    values=sorted(values)
    if not values:return {str(k):None for k in ('min','p25','median','p75','p90','max')}
    def pick(p): return values[max(0,math.ceil(p*len(values))-1)]
    return {'min':values[0],'p25':pick(.25),'median':pick(.5),'p75':pick(.75),'p90':pick(.9),'max':values[-1]}
def ranges(context):
    out=[]
    if isinstance(context.get('ranges'),list):
        for item in context['ranges']:
            start=item.get('ptr',item.get('address_start_hex')); size=item.get('bytes',item.get('storage_bytes'))
            out.append((role(item.get('semantic_role',item.get('class','OTHER'))),int(start,0),int(start,0)+int(size)))
    else:
        for name,item in context.items():
            if isinstance(item,dict) and 'ptr' in item and 'bytes' in item:
                out.append((role(name),int(item['ptr'],0),int(item['ptr'],0)+int(item['bytes'])))
    if not out: raise ValueError('no address ranges')
    return out
def classify(addr,rs): return next((r for r,a,b in rs if a<=addr<b),'OTHER')
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def legacy_entries(root,kind):
    manifest=load(root/'WARP_SHARD_MANIFEST.json'); rows=[]
    for item in manifest['shards']:
        if kind=='q30':
            trace=item['trace_relative_path']; context=item['address_context_relative_path']; static=item['static_index']; declared=item['record_count']; terminal=item['terminal_status']
        else:
            trace=item['trace']; context=item['address_context']; static=item['static_index']; declared=item['records']; terminal=item['classification']
        rows.append((static,root/trace,root/context,declared,terminal))
    return rows
def olmoe_entries(root):
    out=[]
    for receipt in root.glob('shards/static_*/SUPERVISOR_RECEIPT.json'):
        meta=load(receipt); base=receipt.parent
        out.append((meta['selected_static'],base/'trace.bin',base/'ADDRESS_CONTEXT.json',None,(base/'stdout.log').read_text(encoding='utf-8',errors='replace')))
    return out
def analyze_one(static,trace,context,declared,terminal):
    raw=trace.read_bytes()
    if len(raw)<HEADER.size or (len(raw)-HEADER.size)%RECORD.size: raise ValueError('trace alignment')
    magic,index,occ,callback,overflow,written=HEADER.unpack_from(raw); count=(len(raw)-HEADER.size)//RECORD.size
    if magic!=b'C16WARP1' or index!=static or occ!=0 or overflow!=0 or callback!=written or written!=count: raise ValueError('trace header closure')
    if declared is not None and declared!=count: raise ValueError('manifest record count mismatch')
    if count==0 and not ('ZERO' in str(terminal) or 'C16_WARP_TERMINAL' in str(terminal)): raise ValueError('zero lacks terminal proof')
    rs=ranges(load(context)); roles=Counter(); unique={s:set() for s in SIZES}; lanes=0
    for off in range(HEADER.size,len(raw),RECORD.size):
        rec=RECORD.unpack_from(raw,off)
        if rec[0]!=static: raise ValueError('per-record static mismatch')
        for lane,address in enumerate(rec[6:]):
            if rec[1]>>lane&1:
                lanes+=1; roles[classify(address,rs)]+=1
                for size in SIZES: unique[size].add(address//size)
    nonzero=[k for k,v in roles.items() if v]
    shard_role=nonzero[0] if len(nonzero)==1 else 'MIXED' if nonzero else 'OTHER'
    row={'static_index':static,'classification':'EXECUTED' if count else 'ZERO_EXECUTION_PROVEN','warp_records':count,'active_lane_events':lanes,'role':shard_role,'role_events':dict(roles),'unique_128B_lines':len(unique[128]),'unique_4K_pages':len(unique[4096]),'unique_64K_pages':len(unique[65536]),'unique_2M_pages':len(unique[2*1024*1024]),'trace_sha256':sha(trace),'address_context_sha256':sha(context)}
    for label,key in [('128B','unique_128B_lines'),('4K','unique_4K_pages'),('64K','unique_64K_pages'),('2M','unique_2M_pages')]: row['density_'+label]=row[key]/lanes if lanes else None
    return row
def static_summary(root,kind):
    path=root/('STATIC_MREF_MAP.tsv' if kind!='olmoe' else 'selector_authority/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
    with path.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
    selected=[r for r in rows if (r.get('has_mref')=='1' and (r.get('memory_space',r.get('path_class')) in ('GLOBAL','GLOBAL_TO_SHARED')))]
    funcs=sorted({r.get('function_full_name','') for r in rows if r.get('function_full_name')})
    return {'static_map_path':str(path),'all_static_rows':len(rows),'selected_path_class_count':len(selected) if selected else len(rows),'opcode_counts':dict(Counter(r.get('opcode','') for r in selected or rows)),'function_evidence':funcs[:1]}
def recompute(kind,authority):
    cfg=CONFIG[kind]; root=authority/'raw'/cfg['run']; entries=legacy_entries(root,kind) if kind!='olmoe' else olmoe_entries(root)
    if len(entries)!=243 or len({x[0] for x in entries})!=243: raise ValueError('selected coverage not 243 unique')
    rows=[analyze_one(*entry) for entry in sorted(entries)]
    executed=[r for r in rows if r['classification']=='EXECUTED']; role_counts=Counter()
    for row in rows: role_counts.update(row['role_events'])
    total=sum(role_counts.values()); sums={k:sum(r[k] for r in rows) for k in ('unique_128B_lines','unique_4K_pages','unique_64K_pages','unique_2M_pages')}
    metrics={'active_lane_events':quant([r['active_lane_events'] for r in executed])}
    for k in ('unique_128B_lines','unique_4K_pages','unique_64K_pages','unique_2M_pages','density_128B','density_4K','density_64K','density_2M'):metrics[k]=quant([r[k] for r in executed if r[k] is not None])
    role_metrics={}
    for name in ('WEIGHT','INPUT','OUTPUT','OTHER','MIXED'):
        subset=[r for r in executed if r['role']==name]; role_metrics[name]={'count':len(subset),'active_lane_events':quant([r['active_lane_events'] for r in subset]),'unique_128B_lines':quant([r['unique_128B_lines'] for r in subset]),'unique_4K_pages':quant([r['unique_4K_pages'] for r in subset])}
    result={'schema_version':1,'status':'PASS','model':cfg['model'],'run_id':cfg['run'],'semantic_scope':cfg['scope'],'routing_topology':cfg['topology'],'input_width':cfg['widths'][0],'output_width':cfg['widths'][1],'weight_shape':cfg['shape'],'weight_bytes':cfg['weight_bytes'],'dtype':'BF16','selected_static_count':len(rows),'executed_static_count':len(executed),'proven_zero_static_count':len(rows)-len(executed),'failed_excluded_count':0,'executed_fraction':len(executed)/len(rows),'dynamic_warp_records':sum(r['warp_records'] for r in rows),'active_lane_events':total,'role_event_counts':dict(role_counts),'role_fractions':{k:role_counts[k]/total for k in ('WEIGHT','INPUT','OUTPUT','OTHER')},'weight_input_fraction_delta':abs(role_counts['WEIGHT']/total-role_counts['INPUT']/total),'SUM_OF_PER_SHARD_UNIQUES':sums,'quantile_definition':'nearest-rank: ceil(p*n)-1 on sorted executed-shard values','executed_shard_distributions':metrics,'role_conditioned':role_metrics,'static_implementation':static_summary(root,kind),'prohibited_analyses':['cross-shard absolute VA union','cross-shard chronology','reuse distance','cache/TLB causality']}
    return result,rows
def write(kind,result,rows,out):
    out.mkdir(parents=True,exist_ok=True)
    (out/(kind.upper()+'_RECOMPUTE.json')).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    fields=['static_index','classification','warp_records','active_lane_events','role','unique_128B_lines','unique_4K_pages','unique_64K_pages','unique_2M_pages','density_128B','density_4K','density_64K','density_2M','trace_sha256','address_context_sha256']
    with (out/(kind.upper()+'_PER_SHARD.tsv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser();p.add_argument('--authority-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--lineage',choices=CONFIG,required=True);a=p.parse_args();result,rows=recompute(a.lineage,a.authority_root);write(a.lineage,result,rows,a.out);print(json.dumps({'lineage':a.lineage,'status':result['status'],'warps':result['dynamic_warp_records'],'lanes':result['active_lane_events']}))
if __name__=='__main__':main()
