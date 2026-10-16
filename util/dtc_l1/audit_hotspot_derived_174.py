#!/usr/bin/env python3
"""Independent, read-only full-member admission audit for the fixed V2 input."""
import argparse
from collections import Counter
import gzip
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import re
import struct
import time

OLD = 'ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8'
NEW = '21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985'
PCS = {0x180:1364, 0x190:1364, 0x290:1364, 0x2a0:1364, 0xab0:58652, 0xac0:58652}
SHARED = {0x290:0, 0x2a0:1024, 0x890:0, 0x8a0:0, 0x8b0:0,
          0x8c0:1024, 0x960:0, 0x970:0, 0xa20:2048, 0xab0:2048, 0xac0:0, 0xb30:2048}


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2), b''): h.update(b)
    return h.hexdigest()


def decode(t, k, lanes):
    mode=int(t[k]); a=t[k+1:]
    if mode==0:
        require(len(a)>=len(lanes), 'short mode0')
        return [int(v,16) for v in a[:len(lanes)]]
    if mode==1:
        base=int(a[0],16); stride=int(a[1]); first=lanes[0] if lanes else 0
        consecutive=True; result=[]; previous=first-1
        for lane in lanes:
            consecutive = consecutive and lane==previous+1
            result.append(base+(lane-first)*stride if consecutive else 0)
            previous=lane
        return result
    raise ValueError('Unexpected mode '+str(mode))


def model(pc, bx, by, warp, lanes):
    ans=[]
    for lane in lanes:
        y,x=divmod(32*warp+lane,16)
        if pc==0x8a0: y=max(y-1,max(0,2-12*by))
        if pc==0x8b0: y=min(y+1,min(15,1025-12*by))
        if pc==0x960: x=max(x-1,max(0,2-12*bx))
        if pc==0x970: x=min(x+1,min(15,1025-12*bx))
        ans.append(4*(16*y+x)+SHARED[pc])
    return ans


def main():
    ap=argparse.ArgumentParser()
    for key in ['identity','sass','source','original','candidate','output-dir']: ap.add_argument('--'+key,required=True)
    a=ap.parse_args(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=False)
    identity=json.loads(Path(a.identity).read_text()); contract=identity['identity_contract']
    bundle=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(bundle==identity['bundle_sha256']=='dd0da35f5a3e3a2467a1cd23a53ce3966cd7eb6ee31035733e26f48dc532c169','bundle identity')
    require(sha(a.sass)==contract['reconstruction']['sass_sha256'],'SASS identity')
    require(sha(a.source)==contract['reconstruction']['source_sha256'],'source identity')
    listing=Path(a.candidate).parent/'kernelslist.g'
    require(sha(listing)==contract['list']['sha256'] and listing.stat().st_size==92,'list identity')
    require(listing.read_bytes()==(Path(a.original).parent/'kernelslist.g').read_bytes(),'list commands/order')
    require(listing.read_text().splitlines()==['MemcpyHtoD,0x00007f6005600000,4194304','MemcpyHtoD,0x00007f6017c00000,4194304','kernel-1.traceg'],'list scope')
    sass={}
    for line in Path(a.sass).read_text().splitlines():
        m=re.match(r'\s*/\*([0-9a-f]+)\*/\s+(?:@!?\w+\s+)?([\w.]+)\s+(.*?);',line)
        if not m: continue
        op=m[2].split('.')[0]; operands=m[3].split(',')
        regs=lambda s:tuple('R255' if r=='RZ' else r for r in re.findall(r'\bR(?:\d+|Z)\b',s))
        if op.startswith('ST'): dst=(); src=regs(m[3])
        elif op.startswith('LD'): dst=regs(operands[0]); src=regs(','.join(operands[1:]))
        elif op.startswith('RET'): dst=regs(operands[0]); src=()
        else:
            direct=lambda s:bool(re.fullmatch(r'\s*-?R(?:\d+|Z)(?:\.\w+)*\s*',s))
            dst=regs(operands[0]) if direct(operands[0]) else ()
            src=tuple(r for s in operands[1:5] if direct(s) for r in regs(s))
        sass[int(m[1],16)]=(op.encode(),tuple(x.encode() for x in dst),tuple(x.encode() for x in src))
    hs=[hashlib.sha256(),hashlib.sha256()]; addresses=hashlib.sha256(); control=hashlib.sha256()
    counts=Counter(); changed=Counter(); changed_lanes=Counter(); seenpc=Counter(); ops=Counter()
    coords=set(); warps=set(); coord=None; warp=None; declared=None; nwarp=0; last=None
    offsets=[0,0]; started=time.time(); indexhash=hashlib.sha256(); headers={}
    indexpath=out/'ALL_ADDRESS_CHANGES.jsonl.gz'
    with Path(a.original).open('rb') as f, Path(a.candidate).open('rb') as g, gzip.open(indexpath,'xb') as idx:
        for number, pair in enumerate(zip_longest(f,g),1):
            old,new=pair; require(old is not None and new is not None,('line count',number))
            hs[0].update(old); hs[1].update(new)
            record=bool(old.strip()) and old[:1] in b'0123456789abcdef' and declared is not None
            if not record:
                require(old==new,('metadata change',number)); control.update(old)
                if old.startswith(b'-') and b' = ' in old:
                    k,v=old.decode().strip().split(' = ',1); headers[k]=v
                elif old.startswith(b'thread block = '):
                    coord=tuple(map(int,old.split(b' = ')[1].split(b','))); require(coord not in coords,'duplicate CTA'); coords.add(coord)
                elif old.startswith(b'warp = '):
                    if declared is not None: require(nwarp==declared and last==b'EXIT','full warp exit')
                    warp=int(old.split(b' = ')[1]); require((coord,warp) not in warps,'duplicate warp'); warps.add((coord,warp))
                elif old.startswith(b'insts = '): declared=int(old.split(b' = ')[1]); nwarp=0
            else:
                t=old.split(); u=new.split(); bx,by,bz,w=map(int,t[:4]); pc=int(t[4],16); mask=int(t[5],16)
                require((bx,by,bz)==coord and w==warp,'record coordinates')
                j=7+int(t[6]); ns=int(t[j+1]); wi=j+2+ns; k=wi+1; op=t[j]; width=int(t[wi])
                require(t[:k]==u[:k],('instruction/control prefix',number)); control.update(b' '.join(t[:k])+b'\n')
                require((op.split(b'.')[0],tuple(t[7:j]),tuple(t[j+2:wi]))==sass[pc],('SASS root/GPR',number,pc))
                counts['warp_records']+=1; counts['active_thread_instructions']+=mask.bit_count(); nwarp+=1
                seenpc[pc]+=1; ops[op.decode()]+=1; last=op.split(b'.')[0]
                if width:
                    tokens=op.split(b'.'); parsed_width=4
                    for v in tokens:
                        if v.isdigit(): parsed_width=int(v)//8; break
                        if v.startswith(b'U') and v[1:].isdigit(): parsed_width=int(v[1:])//8; break
                    require(width==parsed_width==4,'memory width')
                    lanes=[i for i in range(32) if mask>>i&1]; before=decode(t,k,lanes); after=decode(u,k,lanes)
                    counts['memory_records']+=1
                    vec=[0]*32
                    for lane,value in zip(lanes,after): vec[lane]=value
                    addresses.update(struct.pack('<35Q',pc,mask,parsed_width,*vec))
                    if pc in SHARED and lanes:
                        expected=model(pc,bx,by,w,lanes)
                        require(after==expected,('candidate shared model',number,pc))
                        if int(t[k])==0:
                            raw=[int(v,16) for v in t[k+1:]]
                            require(len(raw)==len(lanes),'shared explicit list count')
                            require(raw==expected,('original explicit shared',number))
                            counts['explicit_shared_addresses']+=len(lanes); counts['explicit_shared_records']+=1
                        else:
                            base=int(t[k+1],16); step=int(t[k+2]); anchors=[i for i in range(min(lanes[0],30)+1) if all(base+(lane-i)*step==v for lane,v in zip(lanes,expected))]
                            require(len(anchors)==1,('model anchor ambiguity',number,anchors)); counts['unique_shared_mode1_anchors']+=1
                    if pc in (0x180,0x190) and lanes:
                        raw=[int(v,16) for v in t[k+1:]]; require(int(t[k])==0 and len(raw) in (32,len(lanes)),'global list domain')
                        direct=[raw[lane] for lane in lanes] if len(raw)==32 else raw
                        base=0x7f6005600000 if pc==0x180 else 0x7f6017c00000
                        expect=[base+4*((12*by-2+(32*w+lane)//16)*1024+12*bx-2+(32*w+lane)%16) for lane in lanes]
                        require(direct==expect==after,('global source/raw addresses',number)); counts['explicit_global_load_addresses']+=len(lanes)
                    if pc==0xb60 and lanes:
                        require(all(v==0x7f6005a00000+4*((12*by-2+(32*w+lane)//16)*1024+12*bx-2+(32*w+lane)%16) for lane,v in zip(lanes,after)),'output store addresses')
                        counts['output_store_addresses']+=len(lanes)
                    if old!=new:
                        require(pc in PCS and int(u[k])==0 and len(u[k+1:])==len(lanes) and before!=after,('undeclared delta',number))
                        changed[pc]+=1; changed_lanes[pc]+=sum(v!=w for v,w in zip(before,after))
                        row=dict(line=number,pc=f'{pc:04x}',offsets=offsets.copy(),old_sha256=hashlib.sha256(old).hexdigest(),new_sha256=hashlib.sha256(new).hexdigest(),lanes=lanes,old=before,new=after)
                        data=(json.dumps(row,separators=(',',':'),sort_keys=True)+'\n').encode(); idx.write(data); indexhash.update(data)
                    if op.startswith(b'LDG'):
                        require(all(v%4==0 for v in after),'global alignment')
                        counts['max_global_128b_lines']=max(counts['max_global_128b_lines'],len({v//128 for v in after}))
                else: require(old==new,('nonmemory change',number))
                if counts['warp_records']%2000000==0: print(json.dumps(dict(event='PROGRESS',records=counts['warp_records'],seconds=time.time()-started)),flush=True)
            if old==new: counts['byte_identical_lines']+=1
            offsets[0]+=len(old); offsets[1]+=len(new)
    require(nwarp==declared and last==b'EXIT','final warp scope')
    require(hs[0].hexdigest()==OLD and hs[1].hexdigest()==NEW,'member SHA')
    require(offsets==[1041309456,1093377608],'member sizes')
    require(dict(changed)==PCS and sum(changed_lanes.values())==2944024,'six PC delta')
    require(counts['warp_records']==13169524 and counts['active_thread_instructions']==377291004 and len(seenpc)==185,'full instruction range')
    require(counts['byte_identical_lines']==13268655,'unchanged byte scope')
    require(counts['explicit_shared_addresses']==16950260 and counts['explicit_shared_records']==660820 and counts['unique_shared_mode1_anchors']==336608,'shared source qualification coverage')
    require(counts['explicit_global_load_addresses']==3720992 and counts['output_store_addresses']==1048576,'global source coverage')
    require(len(coords)==86*86 and len(warps)==86*86*8 and all(0<=x<86 and 0<=y<86 and z==0 for x,y,z in coords),'full grid')
    result=dict(status='PASS_CPU_INPUT_SCOPE_AWAITING_ACTUAL_CONSUMER',bundle_sha256=bundle,original_sha256=hs[0].hexdigest(),derived_sha256=hs[1].hexdigest(),list_sha256=sha(listing),counts=dict(counts),complete_ctas=len(coords),complete_warps=len(warps),headers=headers,pc_counts={f'{p:04x}':n for p,n in sorted(seenpc.items())},opcodes=dict(ops),changed_records={f'{p:04x}':n for p,n in sorted(changed.items())},changed_addresses={f'{p:04x}':n for p,n in sorted(changed_lanes.items())},consumer_memory_sha256=addresses.hexdigest(),control_scope_sha256=control.hexdigest(),all_changes_index=dict(path=str(indexpath.resolve()),sha256=sha(indexpath),decoded_sha256=indexhash.hexdigest()),audit_source_sha256=sha(__file__),elapsed_seconds=time.time()-started,scope='FIXED_SOURCE_PROFILE_DERIVED_NOT_HISTORICAL_ELF_OR_NATIVE_EQUIVALENCE')
    (out/'CPU_INPUT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result),flush=True)


if __name__=='__main__': main()
