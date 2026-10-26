#!/usr/bin/env python3
"""Freeze actual nvdisasm register read/write liveness for every cubin function."""
import argparse, hashlib, json, pathlib, re, subprocess

def parse_liveness(text):
    result = []
    function = None
    banks = []
    digits = []
    columns = []
    aliases = {'GPR': 0, 'PRED': 320, 'UGPR': 256, 'UPRED': 328}
    for line in text.splitlines():
        sec = re.search(r'\.section\s+\.text\.([^,]+),', line)
        if sec:
            function = sec[1]; banks=[]; digits=[]; columns=[]
        if '//' not in line or not function: continue
        comment = line.split('//', 1)[1]
        if '|' not in comment: continue
        groups = comment.split('|')[1:-1]
        if any(x.strip() in aliases for x in groups):
            banks = [x.strip() for x in groups]
            if any(x not in aliases for x in banks): raise ValueError('unknown bank')
            digits=[]; columns=[]; continue
        if banks and '#' in comment:
            digits.append(groups)
            columns=[]
            for bi,g in enumerate(groups):
                cc=[]
                for pos,ch in enumerate(g):
                    if not ch.isdigit(): continue
                    num=''.join(row[bi][pos] if pos < len(row[bi]) and row[bi][pos].isdigit() else ' ' for row in digits)
                    num=int(num.strip())
                    cc.append((pos, aliases[banks[bi]]+num))
                columns.append(cc)
            continue
        if banks and not columns and any(any(c.isdigit() for c in g) for g in groups):
            digits.append(groups); continue
        inst = re.search(r'/\*([0-9a-fA-F]+)\*/\s*(.*?);', line)
        if not inst: continue
        if len(groups)!=len(columns): raise ValueError('liveness missing')
        src=[]; dst=[]
        for g,cc in zip(groups, columns):
            for pos,num in cc:
                if pos>=len(g): raise ValueError('truncated liveness')
                mark=g[pos]
                if mark in 'vx': src.append(num)
                if mark in '^x': dst.append(num)
                if mark not in ' vx:^': raise ValueError('unknown liveness mark '+mark)
        result.append(dict(function=function,pc=int(inst[1],16),sass=inst[2].strip(),src=src,dst=dst))
    if not result: raise ValueError('no instructions')
    labels={};pending=[]
    for line in text.splitlines():
        lab=re.match(r'\s*([.$_A-Za-z][\w$\.]*):',line)
        if lab: pending.append(lab[1])
        ins=re.search(r'/\*([0-9a-fA-F]+)\*/\s*(.*?);',line)
        if ins:
            for lab in pending:labels[lab]=int(ins[1],16)
            pending=[]
    for row in result:
        for lab,pc in labels.items():row['sass']=row['sass'].replace('`('+lab+')','0x%x'%pc)
    return result


def normalized_json_pc_opcodes(jd,cubin,out):
    """Resolve JSON embedded symbol views through actual ELF section/value identity."""
    sections_text=subprocess.check_output(['readelf','-SW',str(cubin)],text=True)
    symbols_text=subprocess.check_output(['readelf','-sW',str(cubin)],text=True)
    (out/(cubin.name+'.sections.txt')).write_text(sections_text)
    (out/(cubin.name+'.symbols.txt')).write_text(symbols_text)
    sections={}
    for line in sections_text.splitlines():
        m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s',line)
        if m:sections[int(m[1])]=dict(name=m[2],address=int(m[3],16),size=int(m[4],16))
    symbols={}
    for line in symbols_text.splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+|\d+)\s+\S+\s+\S+\s+\S+(?:\s+\[<other>:\s*[0-9a-fA-F]+\])?\s+(\d+)\s+(.+?)\s*$',line)
        if m:
            value,size,index,name=int(m[1],16),int(m[2],16 if m[2].startswith('0x') else 10),int(m[3]),m[4]
            row=dict(value=value,size=size,index=index)
            if name in symbols:assert symbols[name]==row,'conflicting ELF symbol'
            symbols[name]=row
    expected={};canonical={};aliases=[];section_extents={}
    for fn in jd[1]:
        name=fn['function-name'];assert name in symbols,('JSON function missing ELF symbol',name)
        sym=symbols[name];assert sym['index'] in sections,'missing ELF owner section'
        section=sections[sym['index']]
        assert section['name'].startswith('.text.'),'function owner not executable .text'
        owner=section['name'][6:]
        start=fn['start'];assert isinstance(start,int) and start==sym['value']-section['address'],'JSON start != ELF section-relative symbol value'
        assert start>=0 and start%16==0 and fn['length']%16==0 and start+fn['length']<=section['size'],'JSON extent outside executable section'
        insns=fn.get('sass-instructions',[]);assert 0<len(insns)*16<=fn['length'],'JSON instruction span exceeds function extent';section_extents[owner]=section['size']
        if name!=owner:aliases.append(dict(symbol=name,owner=owner,section_index=sym['index'],start=start,length=fn['length']))
        for i,ins in enumerate(insns):
            key=(owner,start+16*i)
            if key in canonical:assert canonical[key]==ins,('overlapping JSON symbol views disagree',key)
            canonical[key]=ins;expected[key]=ins['opcode']
    assert expected
    assert set(expected)=={(owner,pc) for owner,size in section_extents.items() for pc in range(0,size,16)},"JSON views do not close full executable owner section"
    return expected,aliases


def ordinal_extract(binary,out):
    import os
    hook=pathlib.Path(__file__).with_name('ordinal_extract_intercept_v1.so')
    hp=pathlib.Path(__file__).with_name('HOOK_SHA256')
    assert hook.is_file() and hashlib.sha256(hook.read_bytes()).hexdigest()==hp.read_text().strip(),'extract hook SHA mismatch'
    listing=subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lelf',str(binary)],text=True,timeout=120)
    names=re.findall(r'^ELF file\s+\d+:\s*(\S+)\s*$',listing,re.M)
    assert names and all('/' not in n and n.endswith('.cubin') for n in names),'unknown or unsafe ELF listing'
    env=dict(os.environ,LD_PRELOAD=str(hook),TMPDIR=str(out))
    cp=subprocess.run(['/usr/local/cuda-12.8/bin/cuobjdump','-xelf','all',str(binary)],cwd=out,text=True,capture_output=True,check=True,env=env,timeout=120)
    emitted=re.findall(r'^Extracting ELF file\s+\d+:\s*(\S+)\s*$',cp.stdout,re.M)
    assert emitted==names,'extract/list ordered names mismatch'
    expected=['%06d__%s'%(i+1,n)for i,n in enumerate(names)]
    assert sorted(p.name for p in out.glob('*.cubin'))==expected,'ordinal outputs do not exactly close listing'
    whole=subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-elf',str(binary)],text=True,timeout=120)
    blocks=[]
    for part in re.split(r'(?=Fatbin (?:elf|ptx) code:)',whole):
        if part.startswith('Fatbin elf code:'):
            assert '64bit elf:' in part,'unknown ELF dump format'
            blocks.append(part[part.index('64bit elf:'):].strip())
    assert len(blocks)==len(expected),'whole ELF dump count mismatch'
    evidence=[]
    for i,n in enumerate(expected):
        cubin=out/n
        assert cubin.read_bytes().startswith(b'\x7fELF'),'not ELF'
        text=subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-elf',str(cubin)],text=True,timeout=120)
        assert text.strip()==blocks[i],('ordinal ELF complete dump mismatch',i+1)
        evidence.append(dict(ordinal=i+1,listed_basename=names[i],preserved_filename=n,bytes=cubin.stat().st_size,sha256=hashlib.sha256(cubin.read_bytes()).hexdigest(),ordered_whole_elf_dump_sha256=hashlib.sha256(blocks[i].encode()).hexdigest(),full_dump_exact=True))
    (out/'ORDINAL_EXTRACTION.json').write_text(json.dumps(dict(schema='ORDINAL_EXTRACTION_CPU_ONLY_V1',listing=listing,rows=evidence,hook_sha256=hp.read_text().strip(),source_sha256=hashlib.sha256(binary.read_bytes()).hexdigest()),indent=2)+'\n')
    return cp

def main():
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('output');a=p.parse_args()
    binary=pathlib.Path(a.binary).resolve();out=pathlib.Path(a.output);out.mkdir(exist_ok=False, parents=True)
    cuda='/usr/local/cuda-12.8/bin/'
    cp=ordinal_extract(binary,out)
    (out/'cuobjdump.log').write_text(cp.stdout+cp.stderr)
    allrows=[];cubins=[]
    for cubin in sorted(out.glob('*.cubin')):
        text=subprocess.check_output([cuda+'nvdisasm','-plr','-lrm','narrow',str(cubin)],text=True)
        (out/(cubin.name+'.liveness')).write_text(text)
        jcp=subprocess.run([cuda+'nvdisasm','-json',str(cubin)],text=True,capture_output=True,check=True)
        (out/(cubin.name+'.disasm.json')).write_text(jcp.stdout)
        jd=json.loads(jcp.stdout)
        assert isinstance(jd,list) and len(jd)==2 and isinstance(jd[1],list),'unknown nvdisasm JSON schema'
        arch=jd[0]['SM']['version'];assert arch=={'major':8,'minor':9},'ordinary cubin must beSM89'
        njson=sum(len(fn.get('sass-instructions',[])) for fn in jd[1])
        if njson==0:
            assert not jd[1] and not re.search(r'/\*[0-9a-fA-F]+\*/.*?;',text),'not independently empty'
            rows=[];aliases=[];status='VERIFIED_EMPTY_NO_EXECUTABLE_SASS'
        else:
            rows=parse_liveness(text)
            expected,aliases=normalized_json_pc_opcodes(jd,cubin,out)
            present={(row['function'],row['pc']) for row in rows}
            assert {k for k,op in expected.items() if op!='NOP'}<=present,'PLR missing non-NOP SASS'
            for row in rows:
                ts=row['sass'].split();op=ts[1] if ts[0].startswith('@') else ts[0]
                assert expected[(row['function'],row['pc'])]==op,'PLR/json opcode/PC mismatch'
            # nvdisasm PLR omits padding NOPs; any unexpectedly executed omittedPC still fails producer lookup.
            status='FULL_PLR_NON_NOP_JSON_ELF_OWNER_PC_OPCODE_CLOSURE'
        cubins.append(dict(name=cubin.name,sha256=hashlib.sha256(cubin.read_bytes()).hexdigest(),instructions=len(rows),json_instruction_count=njson,actual_cubin_arch=arch,nvdisasm_json_exit=jcp.returncode,json_embedded_symbol_aliases=aliases,status=status))
        allrows+=rows
    assert allrows,'no nonempty executable cubin'
    keys=[(x['function'],x['pc']) for x in allrows]
    if len(keys)!=len(set(keys)): raise ValueError('multiple cubins same function/pc: explicit selection required')
    (out/'semantic-map.tsv').write_text(''.join('%s\t%x\t%s\t%s\t%s\n'%(x['function'],x['pc'],','.join(map(str,x['dst'])) or '-',','.join(map(str,x['src'])) or '-',x['sass']) for x in allrows))
    manifest=dict(schema='ADA_LIVENESS_MAP_ELF_OWNER_ORDINAL_CANDIDATE_V1',mapper_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),empty_cubin_policy='nvdisasmJSON nofunctions/noSASS +PLR noSASS verified; nonempty failures remain closed',binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),cubins=cubins,instructions=allrows)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(instructions=len(allrows),functions=len(set(x['function'] for x in allrows)),sha256=manifest['binary_sha256'])))

if __name__=='__main__':main()
