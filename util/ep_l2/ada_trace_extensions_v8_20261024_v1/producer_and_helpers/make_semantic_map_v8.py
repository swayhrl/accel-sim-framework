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

def main():
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('output');a=p.parse_args()
    binary=pathlib.Path(a.binary).resolve();out=pathlib.Path(a.output);out.mkdir(exist_ok=False, parents=True)
    cuda='/usr/local/cuda-12.8/bin/'
    cp=subprocess.run([cuda+'cuobjdump','-xelf','all',str(binary)],cwd=out,text=True,capture_output=True,check=True)
    (out/'cuobjdump.log').write_text(cp.stdout+cp.stderr)
    allrows=[];cubins=[]
    for cubin in sorted(out.glob('*.cubin')):
        text=subprocess.check_output([cuda+'nvdisasm','-plr','-lrm','narrow',str(cubin)],text=True)
        (out/(cubin.name+'.liveness')).write_text(text)
        rows=parse_liveness(text)
        cubins.append(dict(name=cubin.name,sha256=hashlib.sha256(cubin.read_bytes()).hexdigest(),instructions=len(rows)))
        allrows+=rows
    keys=[(x['function'],x['pc']) for x in allrows]
    if len(keys)!=len(set(keys)): raise ValueError('multiple cubins same function/pc: explicit selection required')
    (out/'semantic-map.tsv').write_text(''.join('%s\t%x\t%s\t%s\t%s\n'%(x['function'],x['pc'],','.join(map(str,x['dst'])) or '-',','.join(map(str,x['src'])) or '-',x['sass']) for x in allrows))
    manifest=dict(schema='ADA_LIVENESS_MAP_V1',binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),cubins=cubins,instructions=allrows)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(instructions=len(allrows),functions=len(set(x['function'] for x in allrows)),sha256=manifest['binary_sha256'])))

if __name__=='__main__':main()
