#!/usr/bin/env python3
"""Bounded CPU proof. Refuses overwrites; never starts a simulator/GPU or edits A.

Run g0, unit (C++), derive, reference, production full (C++), then compare.
Any failed invariant raises; scientific failures must be retained, not reinterpreted.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

ROOT=Path('/workspace/dtc-btree-format-stability-cpu-174-v1')
REPO=Path(__file__).resolve().parents[2]
PACK=REPO/'docs/dtc_l1/review_packs/BTREE_E_LIST_STABILITY_CPU_V1'
OLD=Path('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces')
INDEX=Path('/workspace/dtc-hotspot-format-174-v1/other-input-risk-v1/FLAGGED_RECORDS.tsv.gz')
B=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-hotspot-format-174-v1')
A=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-service-closure-174-v1')
FROZEN=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
ORIGINAL={'kernelslist.g':'26315d4ae044e91094d54134ec94e25d70fd4eda8c0fe01767bc2a9437d73467',
          'kernel-1.traceg':'80c00c479a79c4a0c470de34c0b5b4421eb8e737e6cbb3a4046304b1f555395e',
          'kernel-2.traceg':'3c67f85abf952be8a0d109497baabaf97a53d15d4f40e9d1ba2d74ddb1fdc481'}
def need(ok, detail):
    if not ok: raise ValueError(detail)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()
def save(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
def facts(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def rows():
    with gzip.open(INDEX,'rt') as f:return list(csv.DictReader(f,delimiter='\t'))
def shape(line,version=0):
    t=line.split(); off=4 if version<3 else 0; pc=int(t[off],16);mask=int(t[off+1],16)
    j=off+3+int(t[off+2]);ns=int(t[j+1]);wi=j+2+ns;k=wi+1
    return t,pc,mask,j,wi,k
def g0():
    PACK.mkdir(parents=True,exist_ok=False)
    need('huangrulin-174'==subprocess.check_output(['hostname'],text=True).strip(),'original174 host')
    need(git(REPO,'branch','--show-current')=='hrl/iscas2027-dtc-btree-format-stability-174-v1','execution branch')
    need(git(REPO,'rev-parse','HEAD')=='f2c106a1b767042733600fcfe3b4ba88f1e6ef26','authorized base')
    need(sha(INDEX)=='2266153d542547398f7ec807eb92a3be1c68678b2bab888bd50011d5220c15b7','risk index identity')
    with gzip.open(INDEX,'rb') as f:need(hashlib.sha256(f.read()).hexdigest()=='80b75370094146b98fb08c8ced504f72f2454351cfd95ec50b4eb4657beef2b6','decoded index')
    rr=rows();need(len(rr)==104476,'reused bounded index');rr=[r for r in rr if r['workload']=='btree'];need(len(rr)==6000,'fixed6000')
    originals=[facts(OLD/name) for name in ORIGINAL]
    for item in originals:need(item['sha256']==ORIGINAL[Path(item['path']).name],'original member/list SHA')
    changed=0
    with (OLD/'kernel-1.traceg').open('rb') as f:
        for r in rr:
            f.seek(int(r['byte_offset']));line=f.readline();t,pc,mask,j,wi,k=shape(line)
            need(hashlib.sha256(line).hexdigest()==r['original_line_sha256'],'G0 original line SHA')
            need(pc==0x1c40 and mask.bit_count()==1 and t[j]==b'LDG.E.SYS' and int(t[wi])==4 and t[k]==b'0' and len(t[k+1:])==32,'G0 fixed shape')
            lane=mask.bit_length()-1;raw=[int(v,16) for v in t[k+1:]]
            need(mask==int(r['mask'],16) and raw[0]==int(r['frozen_addresses'],16) and raw[lane]==int(r['firstE0_or_full32_addresses'],16),'G0 index addresses')
            changed+=raw[0]!=raw[lane]
    need(changed==5792,'G0 change count')
    producer=Path('/workspace/dtc-hotspot-format-174-v1/evidence/march.cu')
    need(sha(producer)=='8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a','producer source')
    status=Path('/workspace/dtc-service-closure-174-v1/r2-attempts/SCOPED_DISPATCH_STATUS.json')
    authority=json.loads(status.read_text());need(authority['coordinator_pid']==520970 and authority['active_launcher']=='SCOPED_CONTINUATION','A existing authority')
    pids=[520970,495652,495657,606201,606209,624461,638023];proc=[]
    for pid in pids:
        d=Path(f'/proc/{pid}');s=(d/'stat').read_text().rsplit(')',1)[1].split()
        proc.append(dict(pid=pid,start_ticks=s[19],command=(d/'cmdline').read_bytes().replace(b'\0',b' ').decode()))
    protected=[FROZEN/'gpu-simulator/trace-parser/trace_parser.cc',FROZEN/'gpu-simulator/trace-parser/trace_parser.h',FROZEN/'gpu-simulator/trace-driven/trace_driven.cc',
      Path('/workspace/dtc-service-closure-174-v1/build-r1-a1/accel-sim.out'),
      A/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv']
    trad=json.loads(Path('/workspace/dtc-service-closure-174-v1/hotspot-derived-paired-v2/specs/HS_SOURCE_PROFILE_V2_TRAD96.json').read_text());protected.append(Path(trad['runtime']))
    docs=REPO/'docs/dtc_l1/iscas2027/experiment_registry/2026-10-16_v1/btree_format_stability_v1'
    receipt=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),host='huangrulin-174',task='DTC_BTREE_FORMAT_STABILITY_CPU_174_V1',execution_branch=git(REPO,'branch','--show-current'),authorized_base=git(REPO,'rev-parse','HEAD'),remote_document_head=git(REPO,'rev-parse','origin/hrl/iscas2027-dtc-experiment-registry-v1'),documents=[facts(docs/n) for n in ['SCIENTIFIC_DECISION.md','GOAL_CPU_ONLY_174.md']],
      isolation=dict(worktree=str(REPO),output=str(ROOT),creation='new; no same-name local/remote branch, worktree, output or task process before creation; checked before first mutation',existing_lane_A_unmodified=True),
      originals=originals,index=facts(INDEX),producer=facts(producer),g0_rows=6000,changed=changed,same=6000-changed,
      lane_A_head=git(A,'rev-parse','HEAD'),frozen_B_head=git(B,'rev-parse','HEAD'),frozen_framework_head=git(FROZEN,'rev-parse','HEAD'),lane_A_authority_snapshot=authority,existing_processes=proc,
      locks=[dict(path=str(p),inode=p.stat().st_ino,access='stat only; never acquired') for p in [status.with_name('SCOPED_DISPATCH.lock'),status.with_name('CRITICAL_LAUNCH.lock')]],protected=[facts(p) for p in protected],gpu_launches=0,simulator_launches=0)
    save(PACK/'PRECHECK_RECEIPT.json',receipt)
    with (ROOT/'unit.trace-lines').open('x') as f:
        for lane in range(32):f.write(f'0 0 0 0 1c40 {1<<lane:08x} 1 R11 LDG.E.SYS 1 R4 4 0 {0x1000+4*lane:x}\n')
    print('G0 PASS; original 6000 raw lines verified',flush=True)
def derive():
    need(json.loads((ROOT/'unit.json').read_text())['status']=='PASS','independent production parser unit first')
    dest=ROOT/'candidate';dest.mkdir(exist_ok=False)
    rr={int(r['line']):r for r in rows() if r['workload']=='btree'}
    audit=[];offset=0;oldh=hashlib.sha256();newh=hashlib.sha256()
    with (OLD/'kernel-1.traceg').open('rb') as f,(dest/'kernel-1.traceg').open('xb') as g:
        for number,line in enumerate(f,1):
            oldh.update(line);new=line
            if number in rr:
                r=rr[number];t,pc,mask,j,wi,k=shape(line);lane=mask.bit_length()-1
                need(offset==int(r['byte_offset']) and hashlib.sha256(line).hexdigest()==r['original_line_sha256'],'derive whitelist raw SHA/offset')
                raw=[int(v,16) for v in t[k+1:]];need(len(raw)==32 and mask.bit_count()==1,'derive shape')
                # Retain the exact instruction/mode prefix and chosen original address token.
                words=list(re.finditer(rb'\S+',line));new=line[:words[k+1].start()]+t[k+1+lane]+b'\n'
                oldaddr,newaddr=raw[0],raw[lane]
                audit.append(dict(line=number,original_byte_offset=offset,pc='1c40',opcode='LDG.E.SYS',width=4,P=f'{mask:08x}',active_lane=lane,old_address=hex(oldaddr),new_address=hex(newaddr),old_sector32=hex(oldaddr//32),new_sector32=hex(newaddr//32),old_line128=hex(oldaddr//128),new_line128=hex(newaddr//128),address_changed=int(oldaddr!=newaddr),sector_changed=int(oldaddr//32!=newaddr//32),line_changed=int(oldaddr//128!=newaddr//128),original_line_sha256=hashlib.sha256(line).hexdigest(),candidate_line_sha256=hashlib.sha256(new).hexdigest()))
            newh.update(new);g.write(new);offset+=len(line)
    need(oldh.hexdigest()==ORIGINAL['kernel-1.traceg'] and len(audit)==6000 and sum(r['address_changed'] for r in audit)==5792,'G1 counts and identity')
    for name in ['kernelslist.g','kernel-2.traceg']:
        shutil.copyfile(OLD/name,dest/name);need(sha(dest/name)==ORIGINAL[name],'unchanged list/kernel2')
    with (PACK/'BTREE_DERIVATION_AUDIT.tsv').open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(audit)
    receipt=dict(status='PASS',touched=6000,changed_addresses=5792,same_addresses=208,sector_identity_changes=sum(r['sector_changed'] for r in audit),line_identity_changes=sum(r['line_changed'] for r in audit),original_sha256=oldh.hexdigest(),candidate_sha256=newh.hexdigest(),members=[facts(dest/n) for n in ORIGINAL],unit=facts(ROOT/'unit.json'),tool=facts(Path(__file__)))
    save(PACK/'G1_DERIVATION.json',receipt);print(json.dumps(receipt),flush=True)
def reg(v):
    s=v.decode();typ=1 if s.startswith('UR') else 0 if s.startswith('R') else 3 if s.startswith('UP') else 2
    return f'{typ}:{int(s.lstrip("RUP"))},'
def reference():
    rr={int(r['line']):r for r in rows() if r['workload']=='btree'}
    result=[]
    for ordinal in (1,2):
        name=f'kernel-{ordinal}.traceg';original=OLD/name;candidate=ROOT/'candidate'/name
        hs=[hashlib.sha256(),hashlib.sha256()];mh=hashlib.sha256();ih=hashlib.sha256();metadata=hashlib.sha256();counts=Counter();ops=Counter();modes=Counter();headers={};coords=set();warps=set();ct=-1;w=None;declared=None;n=0;last=None;coord=None;inside=False;ended=0;offset=0
        with original.open('rb') as f,candidate.open('rb') as g:
            for number,(old,new) in enumerate(zip_longest(f,g),1):
                need(old is not None and new is not None,'line count');hs[0].update(old);hs[1].update(new)
                record=inside and bool(old.strip()) and old[:1] in b'0123456789abcdef'
                if not record:
                    need(old==new,('metadata bytes',number));metadata.update(old)
                    if old.startswith(b'-') and b' = ' in old:
                        key,value=old.decode().strip().split(' = ',1);headers[key]=value
                    elif old.startswith(b'#BEGIN_TB'):
                        need(not inside,'nested TB');inside=True;ct+=1
                    elif old.startswith(b'thread block = '):
                        coord=tuple(map(int,old.split(b'=')[1].split(b',')));need(coord not in coords,'duplicate CTA');coords.add(coord)
                    elif old.startswith(b'warp = '):
                        if declared is not None:need(n==declared and last==b'EXIT','declared/terminal warp')
                        w=int(old.split(b'=')[1]);need((coord,w) not in warps,'duplicate warp');warps.add((coord,w))
                    elif old.startswith(b'insts = '):declared=int(old.split(b'=')[1]);n=0
                    elif old.startswith(b'#END_TB'):
                        need(inside and n==declared and last==b'EXIT','complete TB');inside=False;ended+=1
                else:
                    t,pc,mask,j,wi,k=shape(old);u,upc,umask,uj,uwi,uk=shape(new)
                    need(tuple(map(int,t[:3]))==coord and int(t[3])==w,'raw coordinate agreement')
                    need(t[:k]==u[:uk],'instruction/control prefix');op=t[j];width=int(t[wi]);lanes=[i for i in range(32) if mask>>i&1]
                    counts['warp_records']+=1;counts['active_thread_instructions']+=len(lanes);n+=1;last=op.split(b'.')[0];ops[op.decode()]+=1
                    dest=''.join(map(reg,t[7:j]));src=''.join(map(reg,t[j+2:wi]))
                    canonical=f'{ct}|{w}|{pc}|{mask}|{op.decode()}|{dest}|{src}|{width}'
                    if width:
                        inferred=4
                        for tok in op.split(b'.'):
                            if re.fullmatch(rb'U?\d+',tok):inferred=int(tok.lstrip(b'U'))//8;break
                        need(inferred==width and width in (1,2,4,8,16),'production opcode/Core legal data width')
                        need(op.startswith((b'LDG.',b'STG.')),'qualified global-only memory path')
                        mode=int(u[uk]);a=u[uk+1:];modes[str(mode)]+=1;vec=[0]*32
                        if mode==0:
                            need(len(a)>=len(lanes),'short P-list')
                            values=[int(v,16) for v in a[:len(lanes)]]
                        elif mode==1:
                            need(len(a)==2,'mode1 shape');base=int(a[0],16);step=int(a[1]);need(not lanes or lanes==list(range(lanes[0],lanes[-1]+1)),'no sparse mode1 frozen unsupported tail');values=[base+(lane-lanes[0])*step for lane in lanes]
                        else:raise ValueError('unqualified memory mode')
                        for lane,value in zip(lanes,values):
                            need(0<=value<2**64 and value%width==0 and value%32+width<=32 and value%128+width<=128,'aligned legal response domain');vec[lane]=value
                        counts[f'memory_width_{width}']+=1
                        counts['memory_records']+=1;counts['max_global_128b_lines']=max(counts['max_global_128b_lines'],len({v//128 for v in values}))
                        counts['max_global_32b_sectors']=max(counts['max_global_32b_sectors'],len({v//32 for v in values}))
                        if not lanes:counts['zero_active_memory_records']+=1
                        mh.update(struct.pack('<35Q',pc,mask,width,*vec))
                    else:
                        imm=int(t[k]) if len(t)>k else 0;canonical+=f'|{imm}|0'
                    ih.update((canonical+'\n').encode())
                    if ordinal==1 and number in rr:
                        r=rr[number];need(hashlib.sha256(old).hexdigest()==r['original_line_sha256'] and offset==int(r['byte_offset']),'G2 original raw SHA and offset')
                        need(pc==0x1c40 and mask.bit_count()==1 and width==4 and op==b'LDG.E.SYS' and t[k]==u[uk]==b'0' and len(t[k+1:])==32 and len(u[uk+1:])==1,'G2 whitelist exact shape')
                        lane=lanes[0];need(int(u[uk+1],16)==int(t[k+1+lane],16),'independent E-list selection')
                        words=list(re.finditer(rb'\S+',old));need(new==old[:words[k+1].start()]+t[k+1+lane]+b'\n','exact bytes whitelist')
                        counts['touched']+=1;counts['changed_addresses']+=int(t[k+1],16)!=int(u[uk+1],16)
                    else:need(old==new,('nonwhitelist change',ordinal,number))
                offset+=len(old)
        need(not inside and n==declared and last==b'EXIT','end scope')
        grid=6000 if ordinal==1 else 10000
        need(ended==len(coords)==grid and len(warps)==grid*8 and coords=={(i,0,0) for i in range(grid)},'complete declared grid')
        need(all(0<=warp<8 for _,warp in warps),'warp domain')
        need(hs[0].hexdigest()==ORIGINAL[name],'G2 original identity')
        need(counts['warp_records']==(7683724 if ordinal==1 else 7925603) and counts['active_thread_instructions']==(217350912 if ordinal==1 else 227116937),'expected full instruction counts')
        if ordinal==1:need(counts['touched']==6000 and counts['changed_addresses']==5792,'G2 fixed transformation')
        r=dict(kernel_ordinal=ordinal,original_sha256=hs[0].hexdigest(),candidate_sha256=hs[1].hexdigest(),counts=dict(counts),complete_ctas=len(coords),complete_warps=len(warps),headers=headers,opcodes=dict(ops),memory_modes=dict(modes),consumer_memory_sha256=mh.hexdigest(),instruction_sha256=ih.hexdigest(),metadata_sha256=metadata.hexdigest())
        result.append(r);print(json.dumps(r),flush=True)
    need((OLD/'kernelslist.g').read_bytes()==(ROOT/'candidate/kernelslist.g').read_bytes(),'list ordered commands bytes')
    save(PACK/'REFERENCE_DECODER.json',dict(status='PASS',tool=facts(Path(__file__)),kernels=result,total_active_thread_instructions=444467849,total_warp_records=15609327,scope='whole two-kernel list; one changed member; independent full byte/geometry/address audit'))
def compare():
    ref=json.loads((PACK/'REFERENCE_DECODER.json').read_text());actual=[json.loads(l) for l in (ROOT/'production.jsonl').read_text().splitlines()]
    need(len(actual)==2,'actual parser full two kernels')
    for r,c in zip(ref['kernels'],actual):
        for key in ['kernel_ordinal','complete_ctas','complete_warps','consumer_memory_sha256','instruction_sha256']:need(r[key]==c[key],('G2 production/reference',key))
        for key in ['warp_records','active_thread_instructions','memory_records']:need(r['counts'][key]==c[key],('G2 count',key))
    save(PACK/'BTREE_CONSUMER_EQUIVALENCE.json',dict(status='PASS',actual_production_results=actual,reference_receipt=facts(PACK/'REFERENCE_DECODER.json'),actual_driver=facts(REPO/'util/dtc_l1/btree_production_parser_cpu_v1.cc'),actual_driver_binary=facts(ROOT/'btree-production-parser-cpu'),frozen_parser=facts(FROZEN/'gpu-simulator/trace-parser/trace_parser.cc'),unit=facts(ROOT/'unit.json'),production_stdout=facts(ROOT/'production.stdout'),production_jsonl=facts(ROOT/'production.jsonl'),scope='actual unchanged complete production trace_parser.cc: list -> kernel -> get_next_threadblock_traces -> inst_trace_t; no simulator/Core execution',native_equivalence='NOT_PROVEN',capture_binding='COMPATIBLE_BUT_UNBOUND'))
    print('G2 full actual production parser / independent reference PASS',flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['g0','derive','reference','compare']);a=ap.parse_args()
    try:globals()[a.phase]()
    except Exception as e:
        p=ROOT/(a.phase+'_FAIL_STOP.json')
        if not p.exists():save(p,dict(status='FAIL_STOP',phase=a.phase,error=repr(e)))
        raise
if __name__=='__main__':main()
