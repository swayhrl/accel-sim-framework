#!/usr/bin/env python3
"""Sequential P5 typed-canary selector sweep; never admits failed attempts."""
import csv, json, struct, subprocess, sys
from pathlib import Path

REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v39')
SUP=REPO/'util/vm_tlb/c16/olmoe_v40/run_nvbit_supervised.py'
TOOL='/data/c16/tools/v40_p5_c16warp1/mem_trace.so'
SELECTOR=Path('/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv')
ROOT=Path('/data/c16/olmoe_v40/typed_sweep')
FUNCTION=Path('/data/c16/olmoe_v39r2/function.txt')

def classify(trace, context):
    ranges=[]
    for x in json.loads(context.read_text())['ranges']:
        start=int(x['ptr'],16); ranges.append((x['semantic_role'],start,start+x['bytes']))
    raw=trace.read_bytes(); hits={x[0]:0 for x in ranges}
    for off in range(40,len(raw),280):
        r=struct.unpack_from('<6I32Q',raw,off); mask=r[1]
        for lane,a in enumerate(r[6:]):
            if mask>>lane&1:
                for role,lo,hi in ranges:
                    if lo<=a<hi: hits[role]+=1
    return hits

rows=list(csv.DictReader(SELECTOR.open(),delimiter='\t'))
ROOT.mkdir(parents=True,exist_ok=True)
receipt=ROOT/'TYPED_SWEEP.json'
state=json.loads(receipt.read_text()) if receipt.exists() else {'found':{},'attempts':[]}
found=state['found']; attempts=state['attempts']; done={x['static_index'] for x in attempts}
for row in rows:
    static=int(row['static_index']); tag=f'static_{static}'
    if static in done: continue
    root=Path('/data/c16/olmoe_v40/supervised')/tag
    cmd=[sys.executable,str(SUP),'--tag',tag,'--tool',TOOL,'--nvbit-version','1.7.7.1-p5','--instr-begin','0','--instr-end','1096','--target-function-file',str(FUNCTION),'--selected-static',str(static),'--c16-output',str(root/'trace.bin'),'--timeout-seconds','180']
    p=subprocess.run(cmd,cwd=REPO,text=True,capture_output=True)
    result=json.loads((root/'result.json').read_text()) if (root/'result.json').exists() else {}
    item={'static_index':static,'supervisor_rc':p.returncode,'result':result}
    if result.get('returncode')==0 and result.get('phase')=='CLEAN_EXIT' and (root/'trace.bin').is_file() and (root/'ADDRESS_CONTEXT.json').is_file():
        hits=classify(root/'trace.bin',root/'ADDRESS_CONTEXT.json'); item['hits']=hits
        for role,count in hits.items():
            if count and role not in found: found[role]=static
    attempts.append(item)
    receipt.write_text(json.dumps({'found':found,'attempts':attempts},indent=2)+'\n')
    if all(role in found for role in ('EXPERT_DOWN_INPUT','EXPERT_DOWN_WEIGHT','EXPERT_DOWN_OUTPUT')): break
receipt.write_text(json.dumps({'found':found,'attempts':attempts},indent=2)+'\n')
print(json.dumps(found,sort_keys=True))
