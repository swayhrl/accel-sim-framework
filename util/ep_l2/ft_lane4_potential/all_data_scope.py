"""Check reference-scope conservation. Native trace qualification remains Lane5's gate."""
import argparse
import hashlib
import json
from pathlib import Path


def check(log):
    rows={}
    for line in log.splitlines():
        if not line.startswith('EPL2MEMREFV1|'):continue
        pieces=line.strip().split('|')[1:]
        kind=pieces[0] if '=' not in pieces[0] else 'SUMMARY'
        values=dict(p.split('=',1) for p in pieces if '=' in p)
        if kind!='SPACE':rows[kind]=values
    a=rows['SUMMARY'];s=rows['SNAPSHOTS'];i=rows['IDENTITY'];u=rows['UNIQUENESS']
    n=lambda row,key:int(row[key])
    assert a['mode']=='I_MEM_ALL_DATA' and a['instruction_path']=='NATIVE'
    assert a['data_hierarchy']=='NOT_APPLICABLE'
    assert n(a,'instructions')==n(a,'instructions_consumed')==n(u,'original_instructions')
    assert n(a,'requests')==n(a,'ready')==n(a,'consumed')
    assert n(a,'store_fragments')==n(a,'store_fragment_commits')
    assert n(a,'stores')==n(a,'store_reference_commits')==n(i,'native_stores_issued')==n(i,'native_stores_committed')
    assert n(a,'instructions')==n(a,'stores')+n(s,'loads')+n(s,'barriers')
    for key in ['pending_requests','pending_instructions','memory_resource_wait','ready_latency_violations']:assert n(a,key)==0
    for key in ['pending_barriers','pending_native_stores']:assert n(i,key)==0
    assert n(a,'drained')==1
    assert n(s,'bytes_ready')==n(s,'bytes_consumed')==n(s,'known_bytes')+n(s,'symbolic_bytes')
    assert n(s,'ready_digest')==n(s,'consumed_digest')
    assert n(i,'issued_instruction_digest')==n(i,'consumed_instruction_digest')
    assert u['duplicate_policy']=='FAIL_CLOSED'
    return dict(status='REFERENCE_CONSERVATION_PASS_NOT_FULL_APPLICATION_ACCEPTANCE',
        physical_cache_wb_scope='NOT_APPLICABLE',rows=rows,
        required_external_gates=['exact released source/binary/effective configs',
         'full native trace/kernel/instruction identities and space/opcode coverage',
         'producer native directed qualification including +1 clock and actual RF writeback',
         'default OFF equivalence on common release',
         'current central run-key/budget/terminal and independent Lane5 acceptance'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);a=p.parse_args()
    result=check(a.log.read_text());result['log_sha256']=hashlib.sha256(a.log.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
