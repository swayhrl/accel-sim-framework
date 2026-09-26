#!/usr/bin/env python3
from __future__ import annotations
import csv,lzma,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path('/data/c16/awma/ai_translation_native_atlas_capture_20260926')
TARGETS={'L1':ROOT/'capture_L1/raw','L2':ROOT/'capture_L2/raw','M1':ROOT/'capture_M1_r2/raw','M2':ROOT/'capture_M2/raw'}
HEX=re.compile(r'^0x[0-9a-fA-F]+$')
def q(xs,p):
 if not xs:return ''
 a=sorted(xs);return a[min(len(a)-1,int((len(a)-1)*p))]
def parse(target,root):
 path=next(root.glob('*.trace.xz'));pages=set();r64=set();r2m=set();refs=ref_idx=bytes_=reads=writes=insts=0;hist=Counter();last={};revisit=[];new_gap=[];last_new=None;windows={1000:[set(),0,[]],10000:[set(),0,[]]};pc_chunk=defaultdict(Counter);chunk_total=Counter()
 with lzma.open(path,'rt',errors='replace') as f:
  for line in f:
   if not line or line[0] in '-#\n':continue
   t=line.split()
   if len(t)<10:continue
   try:
    pc=t[4];mask=int(t[5],16);nd=int(t[6]);oi=7+nd;op=t[oi];ns=int(t[oi+1]);wi=oi+2+ns;width=int(t[wi]);comp=int(t[wi+1])
   except (ValueError,IndexError):continue
   if not (op.startswith('LDG') or op.startswith('STG') or op.startswith('ATOM') or op.startswith('RED')):continue
   lanes=[i for i in range(32) if mask>>i&1]
   if not lanes or width<=0:continue
   ai=wi+2
   try:
    if comp==1:
     base=int(t[ai],16);stride=int(t[ai+1]);first=lanes[0];addrs=[base+(lane-first)*stride for lane in lanes]
    else:addrs=[int(x,16) for x in t[ai:ai+len(lanes)] if HEX.match(x)]
   except (ValueError,IndexError):continue
   if len(addrs)!=len(lanes):continue
   insts+=1;refs+=len(addrs);bytes_+=len(addrs)*width
   if op.startswith('LDG'):reads+=len(addrs)
   else:writes+=len(addrs)
   ipages={x>>12 for x in addrs};hist[len(ipages)]+=1
   for addr in addrs:
    ref_idx+=1
    page=addr>>12;chunk=addr>>21
    if page not in pages:
     if last_new is not None:new_gap.append(ref_idx-last_new)
     last_new=ref_idx
    if page in last and ref_idx%1024==0:revisit.append(ref_idx-last[page])
    last[page]=ref_idx;pages.add(page);r64.add(addr>>16);r2m.add(chunk)
    if op.startswith('LDG'):pc_chunk[chunk][pc]+=1;chunk_total[chunk]+=1
    for size,state in windows.items():
     state[0].add(page);state[1]+=1
     if state[1]==size:state[2].append(len(state[0]));state[0].clear();state[1]=0
 conc=[max(pc_chunk[c].values())/chunk_total[c] for c in chunk_total]
 weighted=sum(max(pc_chunk[c].values()) for c in chunk_total)/sum(chunk_total.values()) if chunk_total else ''
 virtual={'target_id':target,'raw_trace':str(path),'dynamic_memory_instructions':insts,'active_lane_refs':refs,'requested_bytes':bytes_,'read_refs':reads,'write_or_atomic_refs':writes,'unique_4k_pages':len(pages),'unique_64k_regions':len(r64),'unique_2m_regions':len(r2m),'max_unique_4k_pages_per_instruction':max(hist,default=0),'unique_4k_pages_per_instruction_histogram':';'.join(f'{k}:{v}' for k,v in sorted(hist.items())),'new_page_interarrival_p50_refs':q(new_gap,.5),'new_page_interarrival_p95_refs':q(new_gap,.95),'new_page_interarrival_p99_refs':q(new_gap,.99),'page_revisit_distance_p50_refs':q(revisit,.5),'page_revisit_distance_p95_refs':q(revisit,.95),'page_revisit_distance_p99_refs':q(revisit,.99),'page_revisit_quantile_sampling':'DETERMINISTIC_EVERY_1024TH_REVISIT','same_load_pc_within_2m_weighted_mean_top_share':weighted,'same_load_pc_within_2m_p95_top_share':q(conc,.95),'same_load_pc_within_2m_max_top_share':max(conc,default=''),'address_semantics':'VIRTUAL_ONLY_NO_PHYSICAL_OR_TLB_INFERENCE'}
 temporal=[]
 for size,state in windows.items():
  if state[1]:state[2].append(len(state[0]))
  vals=state[2];temporal.append({'target_id':target,'window_refs':size,'window_count':len(vals),'unique_4k_pages_mean':sum(vals)/len(vals) if vals else 0,'unique_4k_pages_p50':q(vals,.5),'unique_4k_pages_p95':q(vals,.95),'unique_4k_pages_max':max(vals,default=0),'address_semantics':'VIRTUAL_ONLY'})
 return virtual,temporal
def main():
 vs=[];ts=[]
 for k,p in TARGETS.items():v,t=parse(k,p);vs.append(v);ts+=t;print(k,v['active_lane_refs'],v['unique_4k_pages'])
 for path,rows in [(ROOT/'VIRTUAL_PAGE_BEHAVIOR.tsv',vs),(ROOT/'TEMPORAL_PAGE_BEHAVIOR.tsv',ts)]:
  with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
