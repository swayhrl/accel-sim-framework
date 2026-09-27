#!/usr/bin/env python3
"""Build a conservative convert_layout -> native evidence ledger from Triton artifacts."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

OPS={
    'shuffle':re.compile(r'\bshfl\.',re.I),
    'shared_load':re.compile(r'\bld\.shared',re.I),
    'shared_store':re.compile(r'\bst\.shared',re.I),
    'barrier':re.compile(r'\bbar\.(?:sync|warp)',re.I),
}


def layout_defs(text: str) -> dict[str,str]:
    out={}
    for line in text.splitlines():
        m=re.match(r'^(#\w+) = (#[^\r\n]+)$',line)
        if m and not m.group(1).startswith('#loc'): out[m.group(1)]=m.group(2)
    return out


def loc_defs(text: str) -> dict[str,str]:
    return {m.group(1):m.group(2) for m in re.finditer(r'^(#loc\d*) = (.+)$',text,re.M)}


def resolve_loc(name: str, defs: dict[str,str], seen=None):
    seen=set() if seen is None else set(seen)
    if name in seen:return None
    seen.add(name);s=defs.get(name,'')
    m=re.search(r'"([^"]+)":(\d+):(\d+)',s)
    if m:return (m.group(1),int(m.group(2)),int(m.group(3)))
    refs=re.findall(r'#loc\d*',s)
    resolved=[resolve_loc(x,defs,seen) for x in refs]
    resolved=[x for x in resolved if x]
    preferred=[x for x in resolved if x[0].endswith('.py') and '/triton/language/' not in x[0]]
    return (preferred or resolved or [None])[-1]


def conversions(text: str):
    defs=loc_defs(text)
    out=[]
    for lineno,line in enumerate(text.splitlines(),1):
        if ' = ttg.convert_layout ' not in line:continue
        dst,rest=line.strip().split(' = ttg.convert_layout ',1)
        src,rest=rest.split(' : ',1)
        src_ty,rest=rest.split(' -> ',1)
        dst_ty,loc=rest.rsplit(' loc(#',1)
        loc_name='#'+loc.rstrip(')')
        out.append({'ir_line':lineno,'src_ssa':src,'dst_ssa':dst,'src_type':src_ty,'dst_type':dst_ty,'loc_name':loc_name,'source_loc':resolve_loc(loc_name,defs)})
    return out


def ptx_native_by_loc(text: str):
    files={int(m.group(1)):m.group(2) for m in re.finditer(r'^\s*\.file\s+(\d+)\s+"([^"]+)"',text,re.M)}
    out={};current=None
    for line in text.splitlines():
        m=re.search(r'\.loc\s+(\d+)\s+(\d+)\s+(\d+)',line)
        if m:
            current=(files.get(int(m.group(1)),f'PTX_FILE_{m.group(1)}'),int(m.group(2)))
            continue
        if current is None:continue
        row=out.setdefault(current,{k:0 for k in OPS})
        for k,pat in OPS.items():
            if pat.search(line):row[k]+=1
    return out


def expand_type(ty: str, defs: dict[str,str]):
    aliases=[x for x in re.findall(r'#\w+',ty) if x in defs]
    return ty + (' | '+ ' ; '.join(f'{x}={defs[x]}' for x in aliases) if aliases else '')


def classify(native):
    if native.get('shared_load',0) or native.get('shared_store',0) or native.get('barrier',0):return 'INTER_WARP_SHARED'
    if native.get('shuffle',0):return 'INTRA_WARP_SHUFFLE'
    return 'OTHER_UNKNOWN'


def build_rows(spec):
    rows=[]
    for item in spec['artifacts']:
        tt=Path(item['ttgir']);ptx=Path(item['ptx'])
        text=tt.read_text(errors='replace');ld=layout_defs(text);native=ptx_native_by_loc(ptx.read_text(errors='replace'))
        meta=json.loads(Path(item['meta']).read_text())
        for seq,c in enumerate(conversions(text),1):
            loc=c['source_loc'];n=native.get((loc[0],loc[1]),{}) if loc else {}
            cls=classify(n)
            rows.append({
                'target_id':item['target_id'],'config_id':item['config_id'],'sequence':seq,
                'tensor_producer_consumer':f"{c['src_ssa']}->{c['dst_ssa']}",
                'source_mapping':expand_type(c['src_type'],ld),'destination_mapping':expand_type(c['dst_type'],ld),
                'class':cls,'optimized_ir_region':f"{tt}:{c['ir_line']} {c['loc_name']}",
                'source_location':f"{loc[0]}:{loc[1]}:{loc[2]}" if loc else 'UNKNOWN',
                'ptx_native_range':('same_source_line_counts='+json.dumps(n,sort_keys=True)) if n else 'NOT_EXCLUSIVELY_TRACEABLE',
                'static_shared_bytes':meta.get('shared','UNKNOWN'),'registers_per_thread':item.get('registers_per_thread','UNKNOWN'),
                'global_scratch_bytes':meta.get('global_scratch_size','UNKNOWN'),
                'required_sync_scope':'CTA' if cls=='INTER_WARP_SHARED' else ('WARP' if cls=='INTRA_WARP_SHUFFLE' else 'UNKNOWN'),
                'barrier_other_dependency':item.get('barrier_other_dependency','UNKNOWN_NOT_SEPARABLE'),
                'dynamic_multiplicity':item.get('dynamic_multiplicity','UNKNOWN'),
                'evidence_limit':'PTX source-line attribution is not an exclusive time decomposition',
            })
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--output',required=True);ap.add_argument('--summary');a=ap.parse_args()
    spec=json.loads(Path(a.spec).read_text());rows=build_rows(spec)
    with open(a.output,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
    if a.summary:
        counts={}
        for r in rows:counts[r['class']]=counts.get(r['class'],0)+1
        Path(a.summary).write_text(json.dumps({'rows':len(rows),'classes':counts},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rows':len(rows),'output':a.output},sort_keys=True))

if __name__=='__main__':main()
