#!/usr/bin/env python3
"""Fail-closed FT terminal adapter; independent data qualification is an input."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw, spec):
    final={};native={}
    for line in raw.open(errors='replace'):
        match=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if match:native[match[1]]=int(match[2])
        if not line.startswith(('EPL2FTV1|SUMMARY|','EPL2FTV1|TERMINAL|','EPL2B0V1|INVARIANT|')):continue
        parts=line.strip().split('|');values=dict(v.split('=',1) for v in parts[2:])
        kind=parts[1]
        if kind=='INVARIANT' and values['kernel_uid']!='18446744073709551615':continue
        final[kind,int(values['slice'])]={k:int(v) for k,v in values.items()}
    expected={(kind,s) for kind in ('SUMMARY','TERMINAL','INVARIANT') for s in range(64)}
    if set(final)!=expected:raise ValueError('missing exact 64-slice FT/B0 terminal snapshot')
    feature=spec['identity']['feature_vector'];cap=feature['payload_capacity_per_slice']
    summaries=[final['SUMMARY',s] for s in range(64)];terminals=[final['TERMINAL',s] for s in range(64)]
    invariants=[final['INVARIANT',s] for s in range(64)]
    for s,t,i in zip(summaries,terminals,invariants):
        if s['physical_slots']!=cap or s['wbuf']!=feature['wbuf_entries'] or s['mode']!=(2 if feature['unified_wb'] else 1):
            raise ValueError('source-emitted mode/budget does not match run identity')
        if s['role_free']+s['role_resident']+s['role_bypass']+s['wb_slots']!=cap:
            raise ValueError('per-slice payload conservation failed')
        if not(s['ownership_consistent']==t['requester_exact_once']==t['hardware_drained']==1):
            raise ValueError('source-emitted ownership/request-token/drain gate failed')
        if s['reserved'] or s['read_refs'] or s['wb_live'] or s['wb_slots']:
            raise ValueError('live FT transient state at terminal')
        if s['wb_created']!=s['wb_lower_accept'] or s['wb_created']!=s['wb_completed']:
            raise ValueError('source-emitted WB lifecycle failed')
    def total(rows,key):return sum(r[key] for r in rows)
    qualification=False
    release_path=spec.get('qualified_release')
    if release_path:
        release=json.loads(Path(release_path).read_text())
        gate=release['gates']['sector_reference_data']
        qualification=(release['qualified_by']=='lane5' and release['status']=='INDEPENDENTLY_QUALIFIED'
            and release['evidence_kind']=='PRODUCTION_DRIVEN' and gate['status']=='PASS'
            and gate['production_driven'] is True and digest(gate['evidence_path'])==gate['evidence_sha256'])
    return {'cycles':native['cycle'],'instructions':native['insn'],'slices':64,
        'unique_requesters':total(terminals,'unique_requesters'),'responses':total(terminals,'responses'),
        'live_descriptors':total(invariants,'descriptor_used'),'live_line_mshrs':total(invariants,'line_mshr_used'),
        'live_wad':total(invariants,'wad_live'),'pending_lower_reads':total(terminals,'pending_lower_reads'),
        'pending_returns':total(terminals,'pending_returns'),'pending_responses':total(terminals,'pending_responses'),
        'wb_created':total(summaries,'wb_created'),'wb_lower_accepted':total(summaries,'wb_lower_accept'),
        'wb_completed':total(summaries,'wb_completed'),'payload_capacity':cap*64,
        'payload_free':total(summaries,'role_free'),'payload_roles':{'RESIDENT_OR_FILL':total(summaries,'role_resident'),
            'BYPASS':total(summaries,'role_bypass'),'WB_STAGED':total(summaries,'wb_slots')},
        'transient_payloads':total(summaries,'wb_slots')+total(invariants,'resident_pending')+total(invariants,'bypass_live'),
        'hardware_drained':all(t['hardware_drained']==1 for t in terminals),
        'workload_termination':spec['identity']['termination_contract'],'requester_exact_once_audit':True,
        'data_correctness_qualification':qualification,'raw_log_sha256':digest(raw),
        'source_map':{'native':'terminal gpu_tot_sim_cycle/insn; not slice-summed','requesters':'FT TERMINAL actual admission/response token insert/erase',
            'drain':'FT TERMINAL actual memory_sub_partition::l2_char_no_resource_leak',
            'WB':'FT SUMMARY real packet-created/lower-push/set_done counts','roles':'FT SUMMARY sole payload-store ownership',
            'data_qualification':'separate Lane 5 qualified_release artifact; never inferred from aggregate counters'}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();spec=json.loads(Path('input_spec.json').read_text());value=parse(args.raw,spec)
    args.out.write_text(json.dumps(value,indent=2)+'\n')

if __name__=='__main__':main()
