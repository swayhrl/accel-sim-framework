#!/usr/bin/env python3
"""Parboil pinned source compare_floats contract, exact uint32/float32/EOF."""
import json,struct,sys,pathlib,math

def read(path):
 b=pathlib.Path(path).read_bytes(); n,=struct.unpack('<I',b[:4]);assert len(b)==4+4*n,'size/EOF mismatch';return struct.unpack('<'+str(n)+'f',b[4:])
def compare(r,c):
 if len(r)!=len(c) or not all(math.isfinite(x) for x in r+c):return False
 abstol=1e-4*max(map(abs,r));return all(abs(x-y)<=abstol or abs(x-y)<0.002*abs(x) for x,y in zip(r,c))
if __name__=='__main__':
 r=read(sys.argv[1]);c=read(sys.argv[2]);assert compare(r,r);assert not compare(r,tuple(x+1000000 for x in r));assert compare(r,c),'source predicate mismatch'
 print(json.dumps(dict(correctness='PASS_PARBOIL_SOURCE_PREDICATE_ALL_VALUES',elements=len(r),max_abs_error=max(abs(x-y) for x,y in zip(r,c)),abs_tolerance=1e-4*max(map(abs,r)),relative_tolerance=0.002,negative_fixture='PASS_REJECTED')))
