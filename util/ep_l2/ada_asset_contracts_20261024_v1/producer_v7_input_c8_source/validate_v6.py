import argparse,collections,hashlib,json,lzma,pathlib,re
def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(2**20),b''):h.update(block)
    return h.hexdigest()

def parse(line):
    t=line.split();i=0
    pc=int(t[i],16);mask=int(t[i+1],16);i+=2
    nd=int(t[i]);i+=1;dst=[int(x[1:]) for x in t[i:i+nd]];i+=nd
    op=t[i];ns=int(t[i+1]);i+=2;src=[int(x[1:]) for x in t[i:i+ns]];i+=ns
    width=int(t[i]);i+=1;addrs={}
    lanes=[j for j in range(32)if mask>>j&1]
    if width:
        mode=int(t[i]);i+=1
        if mode==0:
            for lane in lanes:addrs[lane]=int(t[i],16);i+=1
        elif mode==1:
            base=int(t[i],16);stride=int(t[i+1]);i+=2
            for ix,lane in enumerate(lanes):addrs[lane]=base+ix*stride
        elif mode==2:
            base=int(t[i],16);i+=1
            for ix,lane in enumerate(lanes):
                if ix:base+=int(t[i]);i+=1
                addrs[lane]=base
        else:raise ValueError('address mode')
    imm=int(t[i]);i+=1
    assert t[i] in('ADA6','ADA7'),t[i:]
    active=int(t[i+1],16);pred=int(t[i+2],16);bank=int(t[i+3]);offset=int(t[i+4]);constant_offsets={}
    if t[i]=='ADA6':
        assert len(t[i:])==8
        regoffset=int(t[i+5]);qualified=int(t[i+6]);cw=int(t[i+7])
        if bank>=0:constant_offsets={j:offset for j in lanes}
    else:
        regoffset=0;qualified=int(t[i+5]);cw=int(t[i+6]);mode=int(t[i+7])
        assert mode==(1 if bank>=0 else 0)
        assert len(t[i:])==8+(len(lanes)if bank>=0 else 0)
        if bank>=0:constant_offsets=dict(zip(lanes,map(int,t[i+8:])))
    assert mask==active&pred and qualified==1 and regoffset==0
    assert 0<=len(src)<=24 and 0<=len(dst)<=8
    assert (bank==-1 and cw==0)or(bank>=0 and cw in(1,2,4,8,16))
    return dict(pc=pc,mask=mask,dst=dst,src=src,opcode=op,width=width,addrs=addrs,active=active,pred=pred,bank=bank,offset=offset,cw=cw,constant_offsets=constant_offsets)

def main():
    a=argparse.ArgumentParser();a.add_argument('attempt');a.add_argument('map');a.add_argument('--elements',type=int);a.add_argument('--threads',type=int);a=a.parse_args()
    R=pathlib.Path(a.attempt);M=json.loads(pathlib.Path(a.map).read_text());rows={(x['function'],x['pc']):x for x in M['instructions']}
    counts=collections.Counter();warps={};addresses=collections.defaultdict(list);headers={}
    files=list((R/'traces').glob('kernel*.trace.xz'));assert files
    for f in files:
        headers[f.name]={}
        with lzma.open(f,'rt')as stream:
            for line in stream:
                if line.startswith('-kernel name = '):function=line.split(' = ',1)[1].strip()
                if line.startswith('-grid dim = '):headers[f.name]['grid']=tuple(map(int,re.findall(r'\d+',line)))
                if line.startswith('-block dim = '):headers[f.name]['block']=tuple(map(int,re.findall(r'\d+',line)))
                if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
                keys=line.split(maxsplit=4);cta=tuple(map(int,keys[:3]));warp=int(keys[3]);r=parse(keys[4]);exp=rows[(function,r['pc'])]
                assert r['src']==exp['src'] and r['dst']==exp['dst'],(r,exp)
                w=warps.setdefault((f.name,cta,warp),dict(records=0,exited=0,active_lanes=0))
                assert not r['mask']&w['exited'],'instruction after exit'
                w['records']+=1
                if r['opcode']=='EXIT':w['exited']|=r['mask']
                counts['sass_records']+=1;counts['active_lane_instructions']+=r['mask'].bit_count();counts['zero_mask_records']+=r['mask']==0
                counts['predicate_mixed_records']+=r['pred']not in(0,0xffffffff)
                if r['bank']>=0 and r['mask']:
                    counts['constant_source_records']+=1;counts['constant_lane_accesses']+=r['mask'].bit_count()
                    counts['aux_uops']+=r['opcode'].split('.')[0]not in('LDC','ULDC')
                    if r['bank']==3 and a.elements is not None:
                        for lane,offset in r['constant_offsets'].items():
                            index=cta[0]*a.threads+warp*32+lane
                            assert offset==4*((index*7+3)&63)
                            counts['indexed_constant_lane_offsets_verified']+=1
                if r['width']:
                    counts['explicit_memory_records']+=1;counts['explicit_memory_lane_accesses']+=len(r['addrs'])
                    if a.elements is not None:
                        for lane,addr in r['addrs'].items():addresses[(f.name,r['pc'])].append((cta[0]*a.threads+warp*32+lane,addr))
    for name,h in headers.items():
        gx,gy,gz=h['grid'];bx,by,bz=h['block'];threads=bx*by*bz;nwarps=(threads+31)//32
        observed=[(cta,warp,w)for(fname,cta,warp),w in warps.items()if fname==name]
        assert len(observed)==gx*gy*gz*nwarps
        for cta,warp,w in observed:
            assert 0<=cta[0]<gx and 0<=cta[1]<gy and 0<=cta[2]<gz and 0<=warp<nwarps
            launched=min(32,threads-warp*32);assert w['exited']==(1<<launched)-1
    if a.elements is not None:
        assert len(warps)==((a.elements+a.threads-1)//a.threads)*((a.threads+31)//32)
        for (_,cta,warp),w in warps.items():assert w['exited']==0xffffffff
        for pc,ad in addresses.items():
            base=min(addr-index*4 for index,addr in ad)
            assert len(ad)==a.elements and sorted(x for x,_ in ad)==list(range(a.elements))
            assert all(addr==base+index*4 for index,addr in ad)
    out=dict(schema='ADA_TYPED_FULL_RECORD_VERIFICATION_V1',counts=dict(counts),ctas=len(set((k[0],k[1])for k in warps)),warps=len(warps),kernels=len(headers),all_declared_warps_terminate=True,memory_instruction_lanes={str(k):len(v)for k,v in addresses.items()},source_files={str(p):sha(p)for p in files},map_sha256=sha(pathlib.Path(a.map)))
    dest=R/'FULL_RECORD_VALIDATION.json'
    with dest.open('x')as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out))
if __name__=='__main__':main()
