#!/usr/bin/env python3
import argparse,bz2,collections,json,lzma,math,re
from pathlib import Path

MEM_PREFIX=('LDG','STG','ATOM','RED','LDGSTS')
def quant(vals,q):
 vals=sorted(vals); return vals[min(len(vals)-1,int((len(vals)-1)*q))] if vals else 0
def analyze(path,page_size):
 pages=collections.Counter(); pcs=collections.Counter(); pc_pages=collections.defaultdict(set)
 page_warps=collections.defaultdict(set); page_ctas=collections.defaultdict(set)
 reuse_bins=collections.Counter(); run_bins=collections.Counter(); stride=collections.Counter()
 last_pos={}; prev_page=None; prev_addr=None; run=0; refs=transitions=meminst=0; cta=warp='NA'
 with lzma.open(path,'rt',errors='replace') as f:
  for line in f:
   s=line.strip()
   if s.startswith('thread block = '): cta=s.split('=',1)[1].strip(); continue
   if s.startswith('warp = '): warp=s.split('=',1)[1].strip(); continue
   t=s.split()
   if len(t)<7 or not re.fullmatch(r'[0-9a-fA-F]+',t[0]) or not t[2].isdigit(): continue
   try:
    nd=int(t[2]); oi=3+nd; op=t[oi]; ns=int(t[oi+1]); j=oi+2+ns
    if not op.startswith(MEM_PREFIX) or j+2>=len(t): continue
    width=int(t[j]); comp=int(t[j+1]); mask=int(t[1],16); active=mask.bit_count()
    if active==0: continue
    if comp==1:
     base=int(t[j+2],16); step=int(t[j+3]); addrs=[base+i*step for i in range(active)]
    else: addrs=[int(x,16) for x in t[j+2:j+2+active]]
   except (ValueError,IndexError): continue
   meminst+=1; pc=t[0].lower()
   for addr in addrs:
    page=addr//page_size; pages[page]+=1; pcs[pc]+=1; pc_pages[pc].add(page)
    page_warps[page].add((cta,warp)); page_ctas[page].add(cta)
    if prev_page is None or page!=prev_page:
     if prev_page is not None: transitions+=1; run_bins[int(math.log2(max(1,run)))]+=1
     run=1
    else: run+=1
    if page in last_pos:
     d=refs-last_pos[page]; reuse_bins[int(math.log2(max(1,d)))]+=1
    last_pos[page]=refs
    if prev_addr is not None: stride[addr-prev_addr]+=1
    prev_page=page; prev_addr=addr; refs+=1
 if run: run_bins[int(math.log2(max(1,run)))]+=1
 top_pages=pages.most_common(16); top_pcs=[]
 for pc,n in pcs.most_common(16): top_pcs.append({'pc':pc,'references':n,'unique_pages':len(pc_pages[pc])})
 top10=sum(n for _,n in pages.most_common(max(1,math.ceil(len(pages)*.1))))/refs if refs else 0
 shared_w=sum(1 for p in pages if len(page_warps[p])>1); shared_c=sum(1 for p in pages if len(page_ctas[p])>1)
 top_stride=stride.most_common(1)[0] if stride else (0,0)
 return {'page_size':page_size,'memory_instructions':meminst,'effective_references':refs,'unique_pages':len(pages),
  'page_transitions':transitions,'transition_rate':transitions/max(1,refs-1),'same_page_run_log2_hist':dict(run_bins),
  'reference_reuse_distance_log2_hist':dict(reuse_bins),'top10pct_page_reference_fraction':top10,
  'pages_shared_across_warps':shared_w,'pages_shared_across_ctas':shared_c,
  'dominant_address_stride_bytes':top_stride[0],'dominant_stride_fraction':top_stride[1]/max(1,refs-1),
  'top_pages':[{'page':p,'references':n} for p,n in top_pages],'top_pcs':top_pcs}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('target');ap.add_argument('trace');ap.add_argument('output');a=ap.parse_args()
 out={'target':a.target,'trace':a.trace,'method':'streaming reference-distance approximation; file order is simulator trace order',
      '64KiB':analyze(Path(a.trace),65536),'4KiB':analyze(Path(a.trace),4096)}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
main()
