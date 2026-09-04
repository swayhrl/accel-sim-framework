#!/usr/bin/env python3
"""Exact streaming decoder for frozen NVBit warp-address trace records.

The tracer's address payload is a warp payload, not a single representative
address.  This utility deliberately reconstructs every predicated lane before
doing conservative runtime-range matching.  It never edits the frozen input.
"""
from __future__ import annotations
import argparse,json,lzma,hashlib,os,time
from bisect import bisect_right
from collections import Counter
from pathlib import Path
P64=65536; P2=2*1024*1024
class RangeIndex(list):
 def __init__(self,items):
  super().__init__(items);self.starts=[a for a,_,_ in items]
  if any(a>b for a,b in zip(self.starts,self.starts[1:])):
   raise AssertionError('RangeIndex.starts must be monotonic')
def pop(mask): return int(mask,16).bit_count()
def is_record(line):
 t=line.split(maxsplit=1)
 if not t or line.startswith(('#','-')): return False
 try: int(t[0],16); return True
 except ValueError: return False
def decode(line):
 t=line.split()
 if not is_record(line): return None
 try: int(t[0],16); lanes=pop(t[1]); dst=int(t[2]); i=3+dst; opcode=t[i]; i+=1; src=int(t[i]); i+=1+src; width=int(t[i]); i+=1
 except (ValueError,IndexError) as e: raise ValueError('truncated trace record') from e
 if width==0: return (opcode,0,[],None)
 try: fmt=int(t[i]); i+=1
 except (ValueError,IndexError): raise ValueError("missing address format")
 if fmt==0: add=[int(x,16) for x in t[i:i+lanes]]
 elif fmt==1:
  base=int(t[i],16); stride=int(t[i+1]); add=[base+j*stride for j in range(lanes)]
 elif fmt==2:
  base=int(t[i],16); i+=1; ds=[int(x) for x in t[i:i+lanes-1]]; add=[base]
  for d in ds: add.append(add[-1]+d)
 else: raise ValueError(f"unknown address format {fmt}")
 if len(add)!=lanes: raise ValueError(f"decoded {len(add)} != mask {lanes}")
 if any(a < 0 for a in add): raise ValueError('negative reconstructed address')
 return(opcode,width,add,fmt)
def merge(rs):
 out=[]
 for k in ('WEIGHT','KV_CACHE'):
  items=sorted((a,b) for a,b,l in rs if l==k)
  merged=[]
  for a,b in items:
   if merged and a<=merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]),k)
   else: merged.append((a,b,k))
  out.extend(merged)
 # Class-local merging is not an index order.  The binary-search RangeIndex
 # requires all starts to be globally ordered, including KV below Weight.
 return sorted(out,key=lambda x:(x[0],x[1],x[2]))
def ranges(side,roi):
 r=[(int(x['simva_start'],16),int(x['simva_start'],16)+x['size_bytes'],'WEIGHT') for x in side['allocations']]
 for x in side['kv_cache_events']:
  phase,step=x.get('phase'),x.get('step'); keep=(roi=='prefill' and phase=='PREFILL' and step==0) or (roi=='decode1' and ((phase=='PREFILL' and step==0) or (phase=='DECODE' and step==1)))
  if keep:r.append((int(x['simva_start'],16),int(x['simva_start'],16)+x['size_bytes'],'KV_CACHE'))
 for a,b,k in r:
  for c,d,l in r:
   if k!=l and max(a,c)<min(b,d): raise ValueError('WEIGHT/KV overlap')
 return RangeIndex(merge(r))
def kind(addr,width,r):
 # ranges() rejects cross-kind overlap and merge() collapses same-kind overlap,
 # so an address can only be inside its predecessor interval or touch its
 # successor at the upper boundary.
 i=bisect_right(r.starts,addr)-1
 hits=[];touching=False
 for j in (i,i+1):
  if 0<=j<len(r):
   a,b,k=r[j]
   if a<=addr and addr+width<=b:hits.append(k)
   if max(addr,a)<min(addr+width,b):touching=True
 return (hits[0] if len(hits)==1 else 'UNKNOWN', touching and not hits)
def add_pages(s,a,w):
 for p in range(a//s,(a+w-1)//s+1): yield p
def new_output(root,roi):
 side=json.loads((root/'allocation-sidecar.json').read_text()); rs=ranges(side,roi); keys=('WEIGHT','KV_CACHE','UNKNOWN'); o={'schema_version':'m4a-exact-address-coverage-v2','label':'runtime-range matching (not per-instruction tensor lifetime attribution)','roi':roi,'memory_instructions':0,'lane_references':0,'requested_bytes':0,'decoder_invariant_failures':0,'boundary_or_ambiguous_references':0,'addresses_ge_2p49':0,'addresses_ge_2p56':0,'minimum_observed_simva':None,'maximum_observed_simva':None,'address_format_counts':Counter(),'observed_ranges':[{ 'start':hex(a),'end_exclusive':hex(b),'object_kind':k} for a,b,k in rs],'by_object':{k:{'references':0,'bytes':0,'pages_64k':set(),'pages_2m':set(),'min_classifiable_address':None,'max_classifiable_address':None} for k in keys}}
 return o,rs
def scan_file(f,rs,roi):
 o,_=new_output_for_ranges(rs,roi)
 with lzma.open(f,'rt',errors='replace') as h:
  for line in h:
   try: x=decode(line)
   except ValueError as e: raise RuntimeError(f'{f}: {e}: {line[:200]!r}') from e
   if not x or not x[1]: continue
   op,w,aa,fmt=x; o['memory_instructions']+=1; o['lane_references']+=len(aa); o['requested_bytes']+=w*len(aa); o['address_format_counts'][str(fmt)]+=1
   for a in aa:
    o['addresses_ge_2p49']+=a>=2**49;o['addresses_ge_2p56']+=a>=2**56
    o['minimum_observed_simva']=a if o['minimum_observed_simva'] is None else min(o['minimum_observed_simva'],a)
    o['maximum_observed_simva']=a+w-1 if o['maximum_observed_simva'] is None else max(o['maximum_observed_simva'],a+w-1)
    k,boundary=kind(a,w,rs); q=o['by_object'][k];q['references']+=1;q['bytes']+=w;q['pages_64k'].update(add_pages(P64,a,w));q['pages_2m'].update(add_pages(P2,a,w))
    if boundary:o['boundary_or_ambiguous_references']+=1
    if k!='UNKNOWN':
     q['min_classifiable_address']=a if q['min_classifiable_address'] is None else min(q['min_classifiable_address'],a)
     q['max_classifiable_address']=a+w-1 if q['max_classifiable_address'] is None else max(q['max_classifiable_address'],a+w-1)
 return o
def new_output_for_ranges(rs,roi):
 keys=('WEIGHT','KV_CACHE','UNKNOWN'); return {'schema_version':'m4a-exact-address-coverage-v2','label':'runtime-range matching (not per-instruction tensor lifetime attribution)','roi':roi,'memory_instructions':0,'lane_references':0,'requested_bytes':0,'decoder_invariant_failures':0,'boundary_or_ambiguous_references':0,'addresses_ge_2p49':0,'addresses_ge_2p56':0,'minimum_observed_simva':None,'maximum_observed_simva':None,'address_format_counts':Counter(),'observed_ranges':[{ 'start':hex(a),'end_exclusive':hex(b),'object_kind':k} for a,b,k in rs],'by_object':{k:{'references':0,'bytes':0,'pages_64k':set(),'pages_2m':set(),'min_classifiable_address':None,'max_classifiable_address':None} for k in keys}},rs
def finish(o):
 for q in o['by_object'].values():
  q['pages_64k']=sorted(q['pages_64k']);q['pages_2m']=sorted(q['pages_2m'])
  for n in ('min_classifiable_address','max_classifiable_address'):
   if q[n] is not None:q[n]=hex(q[n])
 o['address_format_counts']=dict(o['address_format_counts']); return o
def run(root,roi):
 o,rs=new_output(root,roi)
 for f in sorted((root/'traces').glob('*.traceg.xz')):
  x=scan_file(f,rs,roi); merge_output(o,x)
 return summary(o)
def merge_output(dst,src):
 for n in ('memory_instructions','lane_references','requested_bytes','decoder_invariant_failures','boundary_or_ambiguous_references','addresses_ge_2p49','addresses_ge_2p56'):dst[n]+=src[n]
 for n,fn in (('minimum_observed_simva',min),('maximum_observed_simva',max)):
  if src[n] is not None:dst[n]=src[n] if dst[n] is None else fn(dst[n],src[n])
 dst['address_format_counts'].update(src['address_format_counts'])
 for k,q in src['by_object'].items():
  d=dst['by_object'][k];d['references']+=q['references'];d['bytes']+=q['bytes'];d['pages_64k'].update(q['pages_64k']);d['pages_2m'].update(q['pages_2m'])
  for n,fn in (('min_classifiable_address',min),('max_classifiable_address',max)):
   if q[n] is not None:d[n]=q[n] if d[n] is None else fn(d[n],q[n])
def summary(o):
 x=finish(o)
 for q in x['by_object'].values():q['pages_64k']=len(q['pages_64k']);q['pages_2m']=len(q['pages_2m'])
 return x
def selftest():
 assert decode('100 00000005 0 LDG 0 4 0 0x10 0x20 0')[2]==[16,32]
 assert decode('100 00000007 0 LDG 0 4 1 0x10 4 0')[2]==[16,20,24]
 assert decode('100 00000007 0 LDG 0 4 2 0x10 -8 16 0')[2]==[16,8,24]
 assert decode('100 00000001 0 LDG 0 8 0 0x100 0')[2]==[256]
 assert decode('100 ffffffff 0 IADD 0 0 0')[2]==[]
 try: decode('100 3 0 LDG 0 4 2 0x1'); raise AssertionError
 except ValueError: pass
 try: decode('100 3 0 LDG'); raise AssertionError
 except ValueError: pass
 assert list(add_pages(P64,65535,2))==[0,1]
 side={'allocations':[{'simva_start':'0x1000','size_bytes':16}],
       'kv_cache_events':[{'simva_start':'0x2000','size_bytes':16,'phase':'PREFILL','step':0},
                          {'simva_start':'0x3000','size_bytes':16,'phase':'DECODE','step':1},
                          {'simva_start':'0x4000','size_bytes':16,'phase':'DECODE','step':2}]}
 assert kind(0x2000,4,ranges(side,'prefill'))[0]=='KV_CACHE'
 assert kind(0x3000,4,ranges(side,'prefill'))[0]=='UNKNOWN'
 assert kind(0x3000,4,ranges(side,'decode1'))[0]=='KV_CACHE'
 assert kind(0x4000,4,ranges(side,'decode1'))[0]=='UNKNOWN'
 assert kind(0x100e,4,ranges(side,'prefill'))==( 'UNKNOWN', True)
 below={'allocations':[{'simva_start':'0x3000','size_bytes':16}],
        'kv_cache_events':[{'simva_start':'0x1000','size_bytes':16,'phase':'PREFILL','step':0}]}
 above={'allocations':[{'simva_start':'0x1000','size_bytes':16}],
        'kv_cache_events':[{'simva_start':'0x3000','size_bytes':16,'phase':'PREFILL','step':0}]}
 below_index=ranges(below,'prefill');above_index=ranges(above,'prefill')
 assert below_index.starts==sorted(below_index.starts)
 assert above_index.starts==sorted(above_index.starts)
 assert kind(0x1000,4,below_index)[0]=='KV_CACHE'
 assert kind(0x3000,4,below_index)[0]=='WEIGHT'
 assert kind(0x1000,4,above_index)[0]=='WEIGHT'
 assert kind(0x3000,4,above_index)[0]=='KV_CACHE'
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path);p.add_argument('--roi',choices=('prefill','decode1'));p.add_argument('--output',type=Path);p.add_argument('--self-test',action='store_true');a=p.parse_args()
 if a.self_test:selftest();print('PASS exact address decoder self-test');return
 if not(a.run and a.roi and a.output):p.error('run roi output required')
 o=run(a.run,a.roi);a.output.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True))
if __name__=='__main__':main()
