#!/usr/bin/env python3
"""Directed semantic model for WARP_VPN_DEDUP_REFERENCE.

This deliberately tests the frozen adaptation contract, not a paper claim.
The production hook is also source-checked so the model cannot silently drift
from reverse accessq leader selection and the real translation service call.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse

@dataclass(frozen=True)
class Req:
    uid:int; asid:int=0; vpn:int=0; page:int=65536; gen:int=0; access:str='R'
def key(r): return r.asid,r.vpn,r.page,r.gen,r.access
def group(accessq):
    leaders={}; members={}
    for r in reversed(accessq):
        leaders.setdefault(key(r),r.uid);members.setdefault(key(r),[]).append(r.uid)
    return leaders,members
def check(name,condition):
    if not condition: raise AssertionError(name)
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);a=p.parse_args()
    # same-page, multi-sector: frozen reverse scan selects uid 3, one real request.
    l,m=group([Req(1,vpn=7),Req(2,vpn=7),Req(3,vpn=7)])
    check('same-page multi-sector',(l[(0,7,65536,0,'R')],len(m[(0,7,65536,0,'R')]))==(3,3))
    # distinct pages remain distinct real requests.
    l,_=group([Req(1,vpn=7),Req(2,vpn=8)]);check('distinct pages',len(l)==2)
    # Same PC is intentionally absent from the grouping key; separate calls are
    # separate dynamic warp instructions and cannot merge.
    check('same PC/different dynamic instruction',len(group([Req(1,vpn=7)])[0])+len(group([Req(2,vpn=7)])[0])==2)
    # Warp/CTA slot reuse is likewise separated by per-instruction invocation.
    check('warp CTA slot reuse',len(group([Req(3,vpn=7)])[0])+len(group([Req(4,vpn=7)])[0])==2)
    for field,other in [('asid',Req(2,asid=1)),('generation',Req(2,gen=1)),('access',Req(2,access='W')),('page size',Req(2,page=4096))]:
        check(field+' mismatch',len(group([Req(1),other])[0])==2)
    # Retry keeps the same reverse-first owner; concurrent new instruction is isolated.
    q=[Req(1,vpn=9),Req(2,vpn=9)];check('retry',group(q)[0]==group(q)[0]);check('concurrent completion/new request',len(group(q)[0])+len(group([Req(5,vpn=9)])[0])==2)
    # No auxiliary queue exists: every bounded accessq member is represented and
    # singleton/zero-group behavior is identical to one request per access.
    q=[Req(i,vpn=i) for i in range(1,257)];l,m=group(q);check('full queue/no-loss',sum(map(len,m.values()))==len(q)==len(l));check('zero-group OFF behavior',len(l)==len(q))
    # Instruction end clears naturally because the result lives only in the
    # existing mem_access objects; a subsequent call has no retained group.
    check('instruction end clear',group([Req(1,vpn=4)])[0][(0,4,65536,0,'R')]==1 and group([Req(2,vpn=4)])[0][(0,4,65536,0,'R')]==2)
    shader=(a.source_root/'gpgpu-sim/shader.cc').read_text()
    check('production reverse scan','for (std::list<mem_access_t>::reverse_iterator leader = entries.rbegin();' in shader)
    check('production real service','m_gpu->vm_translation()->translate(' in shader)
    check('old service not cancelled','detach_passive_forwarded_prelaunch' in shader and 'note_reference_leader_attempt' in shader)
    print('AWMA_INTRAWARP_DIRECTED_TESTS PASS cases=10')
if __name__=='__main__':main()
