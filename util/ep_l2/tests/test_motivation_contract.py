#!/usr/bin/env python3
"""Permanent deterministic EPL2MOTV1 contract fixtures."""
from collections import deque

def bucket(d):
    for i, hi in enumerate((8,16,32,64,128,256,512,1024)):
        if d <= hi: return i
    return 8

class Reuse:
    def __init__(self): self.reset()
    def reset(self): self.seen=set(); self.stack=deque(); self.h=[0]*9; self.reuse=0
    def ref(self, x):
        if x in self.seen:
            self.reuse += 1
            try: d=self.stack.index(x); self.stack.remove(x)
            except ValueError: d=1025
            self.h[bucket(d)] += 1
        self.seen.add(x); self.stack.appendleft(x)
        if len(self.stack)>1025: self.stack.pop()

def dist(d):
    r=Reuse(); r.ref(0)
    for x in range(1,d+1): r.ref(x)
    r.ref(0); return r.h

r=Reuse(); r.ref(1); assert r.reuse == 0 and sum(r.h) == 0
r.ref(1); assert r.h[0] == 1
for d, expect in ((8,0),(9,1),(16,1),(17,2),(32,2),(33,3),(64,3),(65,4),(128,4),(129,5),(256,5),(257,6),(512,6),(513,7),(1024,7),(1025,8)):
    h=dist(d); assert h[expect] == 1 and sum(h) == 1, (d,h)
a,b=Reuse(),Reuse(); a.ref(7); b.ref(7); a.ref(7); assert a.reuse==1 and b.reuse==0
a.reset(); a.ref(7); assert a.reuse==0 and sum(a.h)==0

# A valid victim is an eviction observation regardless of whether it later
# creates a dirty writeback packet.  A re-reference consumes exactly one
# epoch-local opportunity, independently for clean and dirty victims.
class PostEviction:
    def __init__(self): self.seq=0; self.evicted={}; self.evictions=0; self.rerefs=0
    def evict(self, line, dirty):
        self.evictions += 1; self.evicted[line] = (self.seq, dirty)
    def ref(self, line):
        self.seq += 1
        if line in self.evicted:
            self.rerefs += 1; del self.evicted[line]

p=PostEviction(); p.ref('clean'); p.evict('clean', False); p.ref('clean')
p.ref('dirty'); p.evict('dirty', True); p.ref('dirty')
assert p.evictions == 2 and p.rerefs == 2 and not p.evicted

active={}
def create(k,t): assert k not in active; active[k]=t
def accept(k,t): assert k in active and t>=active[k]; del active[k]
create(1,10); assert len(active)==1
# The acceptance event is cache-side lower-interface enqueue.  Later DRAM
# issue or set_done events are deliberately not part of shadow occupancy.
accept(1,11); assert not active
def dram_issue_or_set_done(k): assert k not in active
dram_issue_or_set_done(1)
for k in range(4): create(k,20+k)
assert [len(active)>=c for c in (4,8,16)] == [True,False,False]
create(4,25)
for k in range(5,8): create(k,25+k)
assert [len(active)>=c for c in (4,8,16)] == [True,True,False]
for k in range(8,16): create(k,30+k)
assert [len(active)>=c for c in (4,8,16)] == [True,True,True]
accept(0,60); assert len(active)==15

# Lifecycle identity is the WB packet, not its address.  Concurrent packets
# and sequential reuse of one line cannot collide; WAD completion is separate
# from lower-interface WBUF release, and a naturally drained terminal is empty.
wb_active={}; wad_live=set()
def wb_create(packet, line): assert packet not in wb_active; wb_active[packet]=line; wad_live.add(line)
def wb_accept(packet): assert packet in wb_active; del wb_active[packet]
wb_create('p0', 'A'); wb_create('p1', 'A'); assert len(wb_active)==2
wb_accept('p0'); assert wb_active == {'p1':'A'} and 'A' in wad_live
wb_accept('p1'); wb_create('p2', 'A'); wb_accept('p2'); wad_live.remove('A')
assert not wb_active and not wad_live

def classify(wad=False, setfail=False, mshr=False, missq=False, dirty=False, active=0, cap=8, admitted=True):
    if wad: return 'WB_PATH'
    if setfail: return 'SET_ASSOC'
    if mshr: return 'MSHR_META'
    if missq: return 'MISSQ_LOWER'
    if dirty and active>=cap: return 'WB_PATH'
    return None if admitted else 'OTHER'

assert classify(setfail=True)=='SET_ASSOC'
assert classify(mshr=True)=='MSHR_META'
assert classify(missq=True)=='MISSQ_LOWER'
assert classify(wad=True)=='WB_PATH'
assert classify(dirty=True,active=8,cap=8)=='WB_PATH'
assert classify(wad=True,setfail=True,mshr=True)=='WB_PATH'
assert classify(setfail=True,mshr=True,missq=True)=='SET_ASSOC'
for cap in (4,8,16):
    cats=[classify(setfail=True,cap=cap), classify(mshr=True,cap=cap), classify(missq=True,cap=cap), classify(dirty=True,active=cap,cap=cap)]
    assert len(cats)==4 and all(cats)

# Demand writes share the frontend admission scope, but only their real path
# predicates participate: a locally absorbed clean write does not invent MSHR
# pressure.  Dirty write victims see the same simultaneous C=4/8/16 shadow.
assert classify() is None                         # clean demand write
assert classify(setfail=True) == 'SET_ASSOC'       # demand write, reserved set
assert [classify(dirty=True, active=4, cap=c) for c in (4,8,16)] == ['WB_PATH', None, None]
assert classify(missq=True, dirty=True, active=16, cap=4) == 'MISSQ_LOWER'
assert classify(setfail=True, missq=True, dirty=True, active=16, cap=4) == 'SET_ASSOC'
assert classify(wad=True, setfail=True, missq=True, dirty=True, active=16, cap=4) == 'WB_PATH'
# The same source-driven ordering remains unchanged for demand reads.
assert classify(mshr=True, missq=True, dirty=True, active=16, cap=4) == 'MSHR_META'
print('EPL2MOTV1 directed contract: PASS')
