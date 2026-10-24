"""Independent narrow raw-address/typed-operand/source-count check; no ELF execution."""
from pathlib import Path
import json,hashlib,lzma,re,struct,collections,subprocess,shutil,time

D=Path('/root/data/ada9_parent_cold_review_20261024_v1')
R=D/'ada_linear_texture_producer_v9_20261024_v1'
A=R/'native_attempts/CASE8_A2_capture_v1/ADA9_linear_U32_case8_A2/attempt001'
T=A/'traces'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'control/ADA9_LINEAR_TEXTURE_FIELD_CONTRACT_V1.json')=='be2711906a2b4a3ece4997112b7cf5a0e6e57570adb995028c885abc81222019'
assert sha(R/'source/actual_loaded_map_v1/semantic-map.tsv')=='717f0d849d49ea27e1aefc6ffe92b0c17e452748bf13beb5bd1628092ee969bc'
raw=next(T.glob('kernel*.trace.xz'))
def decode(path):
    rows=[]
    with lzma.open(path,'rt')as f:
        for line in f:
            if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
            prefix,suffix=line.split(' ADA9 ');p=iter(prefix.split())
            cta=tuple(int(next(p))for _ in range(3));warp=int(next(p));pc=int(next(p),16);mask=int(next(p),16)
            dest=[next(p)for _ in range(int(next(p)))];op=next(p);src=[next(p)for _ in range(int(next(p)))];width=int(next(p));addresses=[]
            if width:
                fmt=int(next(p));n=mask.bit_count()
                if fmt==0:addresses=[int(next(p),16)for _ in range(n)]
                elif fmt==1:
                    base=int(next(p),16);stride=int(next(p));addresses=[base+j*stride for j in range(n)]
                elif fmt==2:
                    addresses=[int(next(p),16)]
                    for _ in range(n-1):addresses.append(addresses[-1]+int(next(p)))
                else:raise ValueError('unknown compression')
            immediate=int(next(p));assert list(p)==[]
            s=iter(suffix.split());active=int(next(s),16);predicate=int(next(s),16);bank=int(next(s));offset=int(next(s));qualified=int(next(s));cw=int(next(s));mode=int(next(s))
            offsets=[int(next(s))for _ in range(mask.bit_count())]if bank>=0 else[]
            control=int(next(s));assert control==0;texture=int(next(s));resource=None;pairs=[]
            if texture:
                resource=[int(next(s))for _ in range(5)];pairs=[int(next(s))for _ in range(resource[4])]
            assert list(s)==[] and mask==active&predicate and qualified==1
            rows.append(dict(cta=cta,warp=warp,pc=pc,mask=mask,dest=dest,op=op,src=src,width=width,addresses=addresses,bank=bank,offset=offset,cw=cw,mode=mode,offsets=offsets,texture=texture,resource=resource,pairs=pairs))
    return rows

rows=decode(raw);assert len(rows)==26
mapping={}
for line in (R/'source/actual_loaded_map_v1/semantic-map.tsv').read_text().splitlines():
    fn,pc,dest,src,sass=line.split('\t');mapping[int(pc,16)]=([]if dest=='-'else['R'+n for n in dest.split(',')],[]if src=='-'else['R'+n for n in src.split(',')],sass.split()[0])
static={}
for line in (T/'ada-static.tsv').read_text().splitlines():
    fields=line.split('\t');static[int(fields[0],16)]=(int(fields[1],16),int(fields[4]),int(fields[5]),int(fields[6]))
bases={r['pc']-static[r['pc']][0]for r in rows};assert len(bases)==1;pcbase=bases.pop()
copies=re.findall(r'HTOD_BEGIN id=(\d+) ctx=(\w+) dst=(\w+) bytes=(\d+) api=(\w+)',(T/'ada9-resource-journal.tsv').read_text());assert len(copies)==3
copy_bases=[int(x[2],16)for x in copies];assert [int(x[3])for x in copies]==[512,148,8]
inputs=struct.unpack('<128I',(T/'ada9-htod-000.bin').read_bytes());indices=struct.unpack('<37i',(T/'ada9-htod-001.bin').read_bytes());handle=struct.unpack('<Q',(T/'ada9-htod-002.bin').read_bytes())[0]
assert 0<handle<=0xffffffff and inputs==tuple(0x12340000+19*i for i in range(128))and indices==tuple((13*i+7)%128 for i in range(37))
assert struct.unpack('<37I',(A/'HOST_OUTPUT_U32.bin').read_bytes())==tuple(inputs[i]for i in indices)
source_lanes=aux_lanes=constant_lanes=aux_records=0;mem=collections.Counter();texlines={};store_bases=set();seen_stores=set()
for r in rows:
    assert r['cta']==(0,0,0)and r['warp']in[0,1]
    w=r['warp'];n=32 if w==0 else 5;assert r['mask']==(1<<n)-1
    off=r['pc']-pcbase;assert(r['dest'],r['src'],r['op'])==mapping[off]
    _,bank,co,cw=static[r['pc']];assert(r['bank'],r['offset'],r['cw'])==(bank,co,cw)
    source_lanes+=n
    if bank>=0:
        assert r['mode']==1 and r['offsets']==[co]*n and not r['width']
        constant_lanes+=n
        if r['op'].split('.')[0]not in['LDC','ULDC']:aux_lanes+=n;aux_records+=1
    if r['width']:
        assert r['width']==4 and len(r['addresses'])==n
        mem[r['op']]+=n
        for lane,address in enumerate(r['addresses']):
            tid=w*32+lane
            if off==0x60:assert address==copy_bases[2]
            elif off==0x80:assert address==copy_bases[1]+4*tid
            elif off==0x90:
                assert r['texture']==1 and r['resource']==[copy_bases[0],512,handle,1,n]
                pair=r['pairs'][lane];assert pair>>32==handle and(pair&0xffffffff)==indices[tid]
                assert address==copy_bases[0]+4*indices[tid]
                texlines.setdefault(str(w),set()).add(address//128*128)
            elif off==0xb0:
                store_bases.add(address-4*tid);assert tid not in seen_stores;seen_stores.add(tid)
            else:raise ValueError('unmodeled explicit memory PC')
    elif r['texture']:raise ValueError('texture metadata on nonmemory record')
for w in[0,1]:assert sorted(r['pc']-pcbase for r in rows if r['warp']==w)==list(range(0,0xd0,16))
assert len(store_bases)==1 and seen_stores==set(range(37))
storebase=next(iter(store_bases));ranges=sorted([(copy_bases[0],copy_bases[0]+512),(copy_bases[1],copy_bases[1]+148),(copy_bases[2],copy_bases[2]+8),(storebase,storebase+148)])
assert all(ranges[i][1]<=ranges[i+1][0]for i in range(3))
assert source_lanes==481 and aux_lanes==185 and source_lanes+aux_lanes==666 and aux_records==10 and constant_lanes==222
assert sum(map(len,texlines.values()))==6 and dict(mem)=={'LDG.E':74,'TLD.SCR.B.LZ':37,'STG.E':37}

# Actual full-record verifier rejection of omitted implicit UR / wrong CBANK lane.
fixtures=D/'parent_negative_fullrecord_v1';fixtures.mkdir(exist_ok=False);negatives=[]
for label in['omit_implicit_UR','wrong_constant_lane_offset']:
    clone=fixtures/label;shutil.copytree(R,clone)
    target=clone/raw.relative_to(R);body=lzma.open(target,'rt').read()
    if label=='omit_implicit_UR':
        needle='LDG.E 4 R2 R3 R260 R261';assert body.count(needle)==2
        body=body.replace(needle,'LDG.E 3 R2 R3 R261',1)
    else:
        needle='0 40 1 4 1 40';assert body.count(needle)==2
        body=body.replace(needle,'0 40 1 4 1 44',1)
    with lzma.open(target,'wt')as f:f.write(body)
    proof=fixtures/(label+'.unexpected_pass.json')
    q=subprocess.run(['python3','-B',str(clone/'control/verify_full_ADA9_case8_A2_cpu_v2.py'),str(clone),str(proof)],capture_output=True,text=True,timeout=30)
    assert q.returncode!=0 and not proof.exists()and 'AssertionError'in q.stderr
    (fixtures/(label+'.log')).write_text(q.stdout+q.stderr)
    negatives.append({'case':label,'exit':q.returncode,'expected_assertion_rejected':True,'mutated_raw_sha256':sha(target)})
out={'status':'PARENT_INDEPENDENT_ADA9_EXACT_RAW_TYPED_CBANK_EVERY_MEMORY_LANE_AND_NEGATIVES_PASS','raw_sha256':sha(raw),'producer_SO_sha256':sha(R/'producer_A2/producer_A2.so'),'actual_source_binary_sha256':sha(R/'source/application/linear_tex_u32_indirect_v2'),'source_records':26,'source_lane_instructions':481,'embedded_constant_aux_records':10,'embedded_constant_aux_lane_instructions':185,'predicted_total_lane_instructions':666,'all_constant_source_lane_accesses':222,'width8_policy':'One 8B auxiliary for each embedded8B operand; direct ULDC64 remains one source load, not word-split','explicit_memory_lane_accesses':dict(mem),'TEX128B_line_bases_by_warp':{k:sorted(v)for k,v in texlines.items()},'predicted_TEX_requests':6,'stores37_contiguous_nonoverlapping':True,'output_base_scope':'Inferred solely from original STG addresses; not an API output-allocation snapshot','negative_fullrecord_fixtures':negatives,'GPU_or_simulator_execution':False,'consumer_application_release':'PENDING_FROZEN_NATIVE_SPEC_REVIEW','scope':'Exact source9d5/loaded83f26/producerf4c693/contractbe271/one LINEAR U32 object and37 threads; no bulk, filtered, array, hardware timing or EP scientific grant','verifier_sha256':sha(Path(__file__)),'unix':time.time()}
p=D/'PARENT_INDEPENDENT_SOURCE_TRACE_REVIEW.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
assert sum(p.stat().st_blocks*512 for p in D.rglob('*')if p.is_file())<64*1024**2
print(json.dumps(out))
