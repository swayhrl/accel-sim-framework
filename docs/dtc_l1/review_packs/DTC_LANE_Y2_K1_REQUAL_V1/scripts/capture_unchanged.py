#!/usr/bin/env python3
"""Bound collateral read/write/credit paths against the frozen Git object."""
import hashlib,json,subprocess,sys
from pathlib import Path
from extract_production import braced
FROZEN='6fba0136f8465b59fe5858a950fa39efb265f654'
def capture(source,out):
 current=(source/'src/gpgpu-sim/shader.cc').read_text()
 old=subprocess.check_output(['git','-C',str(source),'show',FROZEN+':src/gpgpu-sim/shader.cc'],text=True)
 names=['bool ldst_unit::dtc_l1_oo_memory_cycle(','void ldst_unit::dtc_l1_oo_issue_lower_requests()','bool ldst_unit::dtc_l1_oo_consume_response(','bool ldst_unit::dtc_l1_oo_writeback_ready()','bool ldst_unit::dtc_l1_m4_observe_admit(','void ldst_unit::dtc_l1_m4_observe_complete(','bool ldst_unit::dtc_l1_oo_select_ready(']
 evidence=[]
 for name in names:
  a,_=braced(current,current.index(name));b,_=braced(old,old.index(name));assert a==b,name
  evidence.append(dict(symbol=name,new_sha256=hashlib.sha256(a.encode()).hexdigest(),frozen_sha256=hashlib.sha256(b.encode()).hexdigest(),identical=True))
 result=dict(frozen=FROZEN,methods=evidence,scope='Source equality complements CPU fixture/API evidence; does not execute full NoC, real dispatch, or ISA side effects')
 out.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':capture(Path(sys.argv[1]),Path(sys.argv[2]))
