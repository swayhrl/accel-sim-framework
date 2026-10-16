#!/usr/bin/env python3
"""Read-only full-file trace coverage/format audit; no simulator qualification."""
import os
import collections,hashlib,json,lzma,pathlib,re
repo=pathlib.Path(__file__).resolve().parents[3];pack=repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1';root=pathlib.Path(os.environ.get('DTC_NATIVE_ROOT','/data/c16/dtc_native_coverage_109_v1'));out=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for case,expected in [('SpMV',4),('LayerNorm_1024',6)]:
 d=root/'traces_env_ready'/case/'traces';kl=d/'kernelslist.g';entries=kl.read_text().splitlines();members=[x for x in entries if '.traceg' in x];assert len(members)==expected
 for order,member in enumerate(members):
  p=d/member;header={};blocks=set();warps=set();opcodes=collections.Counter();widths=collections.defaultdict(set);seen=0;declared=None;tb=None;warp=None;last=None;terminals=collections.Counter()
  with lzma.open(p,'rt') as f:
   for line in f:
    s=line.strip()
    if s.startswith('-') and '=' in s:k,v=s[1:].split('=',1);header[k.strip()]=v.strip()
    elif s.startswith('thread block ='):tb=tuple(map(int,s.split('=')[1].split(',')));blocks.add(tb)
    elif s.startswith('warp ='):
     if declared is not None:assert seen==declared,(case,member,tb,warp,seen,declared)
     if last:terminals[last]+=1
     warp=int(s.split('=')[1]);assert (tb,warp) not in warps;warps.add((tb,warp));seen=0;declared=None;last=None
    elif s.startswith('insts ='):declared=int(s.split('=')[1])
    elif re.match(r'^[0-9a-fA-F]+ [0-9a-fA-F]{8} ',s):
     tok=s.split();nd=int(tok[2]);op=tok[3+nd];ns=int(tok[4+nd]);width=int(tok[5+nd+ns]);opcodes[op]+=1;seen+=1;last=op
     if op.startswith(('LDG','STG','LDS','STS','LDGSTS')):widths[op].add(width)
  assert seen==declared
  if last:terminals[last]+=1
  grid=tuple(map(int,re.findall(r'\d+',header['grid dim'])));block=tuple(map(int,re.findall(r'\d+',header['block dim'])));nt=grid[0]*grid[1]*grid[2];nw=(block[0]*block[1]*block[2]+31)//32
  assert len(blocks)==nt and len(warps)==nt*nw,(case,member,len(blocks),nt,len(warps),nw)
  out.append(dict(case=case,order=order,role=('measured_complete_operator' if order==len(members)-1 else ('warmup' if case=='SpMV' or order>=2 else 'affine_initialization')),path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p),header=header,CTA_count=len(blocks),warp_count=len(warps),warp_instruction_records=sum(opcodes.values()),warp_terminal_opcodes=dict(terminals),dynamic_opcodes=dict(opcodes),memory_widths={k:sorted(v) for k,v in widths.items()},coverage='PASS_ALL_DECLARED_WARPS_IN_ALL_CTAS',simulator_admission='PENDING_174_OPCODE_TRACE_CONTRACT' if case=='SpMV' else 'NOT_ADMITTED_SM86_CUBIN_AND_IGNORED_CALL_REL_NOINC'))
  print(case,order,'CTAs',len(blocks),'warps',len(warps),'records',sum(opcodes.values()),'PASS',flush=True)
  (pack/f'{case}_kernelslist.g.txt').write_text(kl.read_text())
(pack/'TRACE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
for case in ['SpMV','LayerNorm_1024']:
 log=(root/'traces_env_ready'/case/'capture.log').read_text()
 print(case,'ignored_call_warnings=',log.count('Warning: Ignoring CALL.REL.NOINC'))
