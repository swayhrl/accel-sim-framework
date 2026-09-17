#!/usr/bin/env python3
import argparse,collections,json,lzma
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('trace');p.add_argument('out');a=p.parse_args()
pages=collections.Counter();pc=collections.Counter();pw=collections.Counter();cp=set();wp=set();ctas=warps=insts=mem=lanes=0;modes=collections.Counter();ops=collections.Counter();fmt=False;openwarp=False
with lzma.open(a.trace,'rt') as f:
 for raw in f:
  z=raw.strip()
  if not fmt:
   fmt=z.startswith('#traces format') or fmt;continue
  if z=='#BEGIN_TB':cp=set();continue
  if z=='#END_TB':
   for q in cp:pc[q]+=1
   continue
  if z.startswith('thread block = '):ctas+=1;continue
  if z.startswith('warp = '):
   if openwarp:
    for q in wp:pw[q]+=1
   wp=set();openwarp=True;warps+=1;continue
  if not z or z.startswith(('insts = ','#','-')):continue
  x=z.split()
  try: mask=int(x[1],16);d=int(x[2]);i=3+d;op=x[i];s=int(x[i+1]);i+=2+s;width=int(x[i])
  except:continue
  insts+=1;ops[op]+=1
  if not width:continue
  mem+=1
  try:mode=int(x[i+1]);active=mask.bit_count()
  except:continue
  modes[str(mode)]+=1
  try:
   if mode==0:add=[int(v,16) for v in x[i+2:i+2+active]]
   elif mode==1:base=int(x[i+2],16);st=int(x[i+3]);add=[base+st*j for j in range(active)]
   elif mode==2:base=int(x[i+2],16);add=[base+int(v) for v in x[i+3:i+3+active]]
   else:add=[]
  except:add=[]
  for v in add:q=v>>16;pages[q]+=1;cp.add(q);wp.add(q);lanes+=1
if openwarp:
 for q in wp:pw[q]+=1
r={'trace_order_semantics':'STRUCTURAL_TRACE_ORDER_ONLY','cta_records':ctas,'warp_records':warps,'warp_instruction_records':insts,'memory_instruction_records':mem,'lane_address_events':lanes,'unique_64KiB_vpn':len(pages),'address_mode_counts':dict(modes),'opcode_counts':dict(ops),'vpn_reference_counts':{str(k):v for k,v in pages.items()},'vpn_cta_counts':{str(k):v for k,v in pc.items()},'vpn_warp_counts':{str(k):v for k,v in pw.items()}}
Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(r,sort_keys=True)+'\n')