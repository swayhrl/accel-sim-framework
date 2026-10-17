#!/usr/bin/env python3
"""Ten small protocol scenarios; expected byte strings generated separately from reference.py."""
import json
from pathlib import Path
BASE=0x1000

def build():
 cases=[]
 def one(number,name,ops,production):
  memory=bytearray(i^0x5a for i in range(128));events=[];snap={};seq=0
  for op in ops:
   seq+=1;kind=op[0];e={'step':seq,'op':kind,'request_id':f'{number}-{seq}'}
   if kind=='store':
    _,offset,payload=op;data=bytes.fromhex(payload);assert len(data) in (4,8) and offset%len(data)==0
    memory[offset:offset+len(data)]=data;e.update(address=BASE+offset,size=len(data),data_hex=payload,byte_mask_128_hex=f'{((1<<len(data))-1)<<offset:032x}',sector_mask=1<<(offset//32),native_coalesced_request_bytes=32)
   elif kind=='read':
    _,offset,size,key=op;snap[key]=bytes(memory[offset:offset+size]);e.update(address=BASE+offset,size=size,snapshot_id=key,expected_hex=snap[key].hex())
   elif kind=='expect_snapshot':e.update(snapshot_id=op[1],expected_hex=snap[op[1]].hex())
   else:e.update(assertion=op[1])
   events.append(e)
  cases.append({'case_id':f'C{number:02d}','name':name,'line_address':BASE,'initial_line_hex':bytes(i^0x5a for i in range(128)).hex(),'events':events,'simulator_scope':production,'byte_reference_scope':'Independent numeric byte-address model only; not simulator byte output or lifecycle proof','RTL_adapter_must_check':'Apply ready/valid and lifecycle assertions; compare actual1024bit/byte-enable data, snapshots and exact-once/drain separately','final_line_hex':memory.hex()})
 one(1,'same_sector_two_32bit_producers',[('store',0,'01020304'),('store',8,'11223344'),('read',0,32,'r')],'NEW mask32 B/U: mask union8 and sector UID only, numeric bytes unobservable')
 one(2,'adjacent_64bit_cross_sector',[('store',24,'0102030405060708'),('store',32,'a1a2a3a4a5a6a7a8'),('read',0,64,'r')],'NEW mask64 B/U: masks16/sector labels/partial fill, no numeric merge claim')
 one(3,'delayed_read_then_partial_later_producer',[('store',0,'10203040'),('read',0,32,'held'),('observe','Hold response5cycles; conflicting store must remain uncommitted/pins1'),('observe','Consume held requester exactly once, then pins0'),('store',0,'55667788'),('expect_snapshot','held')],'NEW snapshot B/U: actual pin refusal, retained sector snapshot and commit release')
 one(4,'local_slot_reuse_before_WAD_completion',[('store',0,'11223344'),('observe','Dirty WB lower_accept releases local data; WAD remains live'),('observe','Reuse freed slot for another line; same-line demand refused'),('observe','True set_done releases WAD once; same-line demand may proceed'),('read',0,32,'r')],'REUSE WAD256 actual partition B/U + A1; numeric lower persistence not asserted')
 one(5,'bank_conflict_fixed_victim_retry',[('store',0,'abcd1234'),('observe','Existing contender owns victim bank; head retries with samevictim/token'),('observe','Independent ready other-bank hit remains blocked by pending frontend head'),('observe','Head later commits once; independent hit then proceeds'),('read',0,32,'r')],'NEW frontendHOL B/U + REUSE A1 native16way conflict/victim-binding')
 one(6,'legal_rollback_no_visible_commit',[('observe','Attempt write reserves resources but must not commit before acceptance'),('observe','Legal rollback cancels pending tokens and releases reservations once'),('read',0,32,'before'),('store',0,'01010101'),('read',0,32,'after')],'GAP: common ft_rollback source checked; no newly proven legal dynamic trigger')
 one(7,'response_lower_backpressure',[('store',0,'04030201'),('read',0,32,'held'),('observe','Stall lower/response consumer; hold payload pin and data snapshot'),('observe','Release ready; commit once and drain descriptors/WB/WAD'),('expect_snapshot','held')],'REUSE FT/A1 partition pressure; NEW snapshot covers held consumer only')
 one(8,'capacity_refusal_exact_once_release',[('observe','Fill configured WB/WAD boundary, then refuse capacity+1 before mutation'),('observe','After true release, retry exact same request once and drain'),('store',0,'99aabbcc'),('read',0,32,'r')],'REUSE WAD256257th refusal and earlier WBUF/Pool directed capacity cases')
 one(9,'stale_incarnation_after_payload_reuse',[('store',0,'11224488'),('observe','Retire old incarnation, reuse same physicalslot for newowner/generation'),('observe','Late oldhandle/event must not modify newowner; no wraparound claim'),('read',0,32,'new')],'NEW stale_handle B/U actual production type rejects oldgeneration; full packet/wrap gap')
 one(10,'partial_store_with_late_sector_fill',[('store',0,'0a0b0c0d'),('observe','Lower snapshot for untouched bytes arrives after partial producer'),('read',0,32,'merged'),('observe','Dirty byte mask stays4; other sectors and newincarnation remain unchanged')],'NEW partial mask/fill producer tests + REUSE sector merge; numeric byte merge remains RTL obligation')
 return {'schema':'EPL2_LANE3_LANE2_SHARED_MIN_STIMULUS_V1','line_bytes':128,'sector_bytes':32,'modes':['B16','S64','Unified'],'source_scope':'Finite non-atomic protocol; no RO/TVD/Ideal/whole-GPU proof','cycle_policy':'Event/precondition driven; do not copy fixture waits as free buffers or new pipeline assumptions','cases':cases}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();a.output.write_text(json.dumps(build(),indent=2)+'\n')
