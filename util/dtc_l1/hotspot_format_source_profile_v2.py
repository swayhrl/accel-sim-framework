#!/usr/bin/env python3
"""Fixed-member source-profile verifier. No GPU, simulator, trace mutation or admission changes."""
from pathlib import Path
import csv,hashlib,json,re,collections,time
def require(condition, detail="Fixed Hotspot source-profile contract failed"):
    if not condition:
        raise ValueError(detail)


import argparse
ap=argparse.ArgumentParser(description='CPU-only verification of a reconstructed source profile; not a capture-binary receipt.')
ap.add_argument('--member',type=Path,required=True)
ap.add_argument('--sass',type=Path,required=True)
ap.add_argument('--output-dir',type=Path,required=True)
a=ap.parse_args();root=a.output_dir;root.mkdir(parents=True,exist_ok=True);member=a.member
sass=a.sass.read_text()
require(hashlib.sha256(sass.encode()).hexdigest()=='079d8b4d07c53f4c7bae0a9a9f484ceb2ff8eb3ad7487e1128eb68373472ec06', 'Fixed Hotspot source-profile contract failed')
can={}
for l in sass.splitlines():
 m=re.match(r'\s*/\*([0-9a-f]+)\*/\s+(?:@!?\w+\s+)?([\w.]+)\s+(.*?);',l)
 if not m:continue
 op=m[2];ops=m[3].split(',');reg=lambda x: re.fullmatch(r'-?(R(?:[0-9]+|Z))(?:\.[A-Za-z0-9]+)*',x.strip())
 dest=[];src=[]
 if op.startswith('ST'):src=re.findall(r'\bR(?:\d+|Z)\b',m[3])
 elif op.startswith('LD'):
  dest=re.findall(r'\bR(?:\d+|Z)\b',ops[0]);src=re.findall(r'\bR(?:\d+|Z)\b',','.join(ops[1:]))
 elif op.startswith('RET'):dest=re.findall(r'\bR(?:\d+|Z)\b',ops[0])
 else:
  if reg(ops[0]):dest=[reg(ops[0])[1]]
  src=[reg(x)[1] for x in ops[1:5] if reg(x)]
 norm=lambda a:tuple('R255' if v=='RZ' else v for v in a)
 can[int(m[1],16)]=(op.split('.')[0],norm(dest),norm(src))

counts=collections.Counter();failures=[];seen=set();pc_forms={};h=hashlib.sha256();delta=collections.Counter();firstexamples={};output_bases=collections.Counter();start=time.time()
# Independent source-level reference: Rodinia16x16 tile, pyramid2, 1024 grid.
# Compiled SASS profile supplies each effective address register and immediate.
shared_pc={0x290:'self',0x2a0:'power',0x890:'self',0x8a0:'north',0x8b0:'south',0x8c0:'power',0x960:'west',0x970:'east',0xa20:'temporary',0xab0:'temporary',0xac0:'self',0xb30:'temporary'}
ref_cache={}
def expected_shared(pc,bx,by,warp):
 tag=shared_pc[pc];result=[];xbase=bx*12-2;ybase=by*12-2
 xmin=max(0,-xbase);xmax=min(15,1023-xbase);ymin=max(0,-ybase);ymax=min(15,1023-ybase)
 key=(tag,xmin,xmax,ymin,ymax,warp)
 if key in ref_cache:return ref_cache[key]
 for lane in range(32):
  tid=warp*32+lane;y,x=divmod(tid,16)
  if tag=='north':y=max(y-1,ymin)
  elif tag=='south':y=min(y+1,ymax)
  elif tag=='west':x=max(x-1,xmin)
  elif tag=='east':x=min(x+1,xmax)
  result.append((y*16+x)*4+(1024 if tag=='power' else 2048 if tag=='temporary' else 0))
 ref_cache[key]=result
 return result

def frozen(base,stride,lanes):
 result=[];end=False;first=lanes[0];prev=first-1;addr=base
 for lane in lanes:
  if lane!=prev+1:end=True
  if lane==first:addr=base
  elif not end:addr+=stride
  result.append(0 if end else addr);prev=lane
 return result

def fail(kind,n,pc,**kw):
 counts['FAIL_'+kind]+=1
 if len(failures)<30:failures.append(dict(kind=kind,line=n,pc=f'{pc:04x}',**kw))

with member.open('rb') as f:
 for n,line in enumerate(f,1):
  h.update(line)
  if not line[:1] in b'0123456789abcdef' or not line.strip():continue
  t=line.split();bx,by,bz,warp=map(int,t[:4]);pc=int(t[4],16);mask=int(t[5],16);j=7+int(t[6]);op=t[j].decode();nsrc=int(t[j+1]);src=tuple(v.decode() for v in t[j+2:j+2+nsrc]);dest=tuple(v.decode() for v in t[7:j]);width=int(t[j+2+nsrc]);sig=(op.split('.')[0],dest,src)
  counts['records']+=1;counts['active_instructions']+=mask.bit_count()
  if pc not in seen:
   seen.add(pc);pc_forms[pc]=dict(pc=f'{pc:04x}',opcode=op,dest=dest,src=src,count=0)
  pc_forms[pc]['count']+=1
  if sig!=can.get(pc):fail('SIGNATURE',n,pc,observed=sig,candidate=can.get(pc))
  if not width:continue
  tail=t[j+3+nsrc:];mode=int(tail[0]);lanes=[i for i in range(32) if mask>>i&1]
  counts[f'memory_mode{mode}']+=1
  if not lanes:continue
  target=expected_shared(pc,bx,by,warp) if pc in shared_pc else None
  if mode==0:
   raw=[int(v,16) for v in tail[1:]]
   if len(raw)==32:decoded=[raw[i] for i in lanes]
   elif len(raw)==len(lanes):decoded=raw
   else:
    fail('LIST_COUNT',n,pc,count=len(raw),active=len(lanes));continue
   before=raw[:len(lanes)]
   if target:
    counts['independent_raw_shared_active_addresses']+=len(lanes)
    counts['independent_raw_shared_records']+=1
    if decoded!=[target[i] for i in lanes]:fail('RAW_SHARED',n,pc,observed=decoded,source=[target[i] for i in lanes])
   if pc in [0x180,0x190]:
    ptr=0x7f6005600000 if pc==0x180 else 0x7f6017c00000
    expected=[ptr+4*((by*12-2+(warp*32+i)//16)*1024+(bx*12-2+(warp*32+i)%16)) for i in lanes]
    counts['independent_raw_global_active_addresses']+=len(lanes)
    if decoded!=expected:fail('RAW_GLOBAL',n,pc,observed=decoded,source=expected)
   if pc==0xb60:
    bases=[addr-4*((by*12-2+(warp*32+i)//16)*1024+(bx*12-2+(warp*32+i)%16)) for i,addr in zip(lanes,decoded)]
    output_bases.update(bases)
  elif mode==1:
   base=int(tail[1],16);step=int(tail[2]);before=frozen(base,step,lanes)
   if target:
    # Enumerate every historical encoder-compatible execution interval;
    # compare its implied active addresses with the independent source model.
    candidates=[]
    for first in range(min(lanes[0],30)+1):
     vals=[base+(i-first)*step for i in lanes]
     if vals==[target[i] for i in lanes]:candidates.append(first)
    if len(candidates)!=1:fail('ANCHOR',n,pc,base=base,stride=step,candidates=candidates,expected=[target[i] for i in lanes])
    decoded=[target[i] for i in lanes];counts['source_qualified_shared_mode1_records']+=1
   else:
    if lanes[0] or lanes!=list(range(lanes[0],lanes[-1]+1)):fail('GLOBAL_MODE1_UNRESOLVED',n,pc)
    decoded=[base+k*step for k in range(len(lanes))]
  else:fail('MODE',n,pc,mode=mode);continue
  if before!=decoded:
   changed=sum(a!=b for a,b in zip(before,decoded));key=(pc,op,mode)
   delta[(key,'records')]+=1;delta[(key,'lanes')]+=changed
   firstexamples.setdefault(key,dict(line=n,cta=[bx,by,bz],warp=warp,mask=f'{mask:08x}',line_sha256=hashlib.sha256(line).hexdigest(),lanes=lanes,frozen=before,source_candidate=decoded))
require(h.hexdigest()=='ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8', 'Fixed Hotspot source-profile contract failed')
result=dict(status='PASS_CANDIDATE_SOURCE_PROFILE_NOT_IMMUTABLE_CAPTURE_RECEIPT' if not failures else 'FAIL_CANDIDATE_SOURCE_PROFILE',member_sha256=h.hexdigest(),source_profile_sass_sha256=hashlib.sha256(sass.encode()).hexdigest(),counts=dict(counts),static_pc_count=len(seen),failures=failures,output_pointer_bases={hex(k):v for k,v in output_bases.items()},elapsed_seconds=time.time()-start)
(root/'SOURCE_PROFILE_VALIDATION_V2.json').write_text(json.dumps(result,indent=2)+'\n')
with (root/'SOURCE_PROFILE_PC_FORMS_V2.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['pc','opcode','dest','src','count'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(pc_forms[k] for k in sorted(pc_forms))
with (root/'SOURCE_PROFILE_DELTA_V2.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['pc','opcode','mode','changed_records','changed_lanes','first_example_json'])
 for k in sorted(firstexamples):w.writerow([f'{k[0]:04x}',k[1],k[2],delta[(k,'records')],delta[(k,'lanes')],json.dumps(firstexamples[k],separators=(',',':'))])
print(json.dumps(result),flush=True)
if failures:
 raise SystemExit(1)
