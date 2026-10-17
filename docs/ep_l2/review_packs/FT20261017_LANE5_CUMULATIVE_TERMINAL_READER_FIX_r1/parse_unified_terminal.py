#!/usr/bin/env python3
"""Existing FT terminal adapter extended for explicitly qualified local diagnostic backing."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw, spec):
    final={};native={};ideal={};ideal_frames={}
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(spec['scope_tool']['path']).parent))
    if digest(spec['scope_tool']['path'])!=spec['scope_tool']['sha256']:raise ValueError('local scope tool changed')
    from unified_scope import features
    features(spec["identity"],spec["producer_profile"])
    with raw.open(errors='replace') as stream:
        for line in stream:
            match=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
            if match:native[match[1]]=int(match[2])
            if line.startswith('EPL2IDEALV1|scope=application|'):
                values=dict(v.split('=',1) for v in line.strip().split('|')[1:]);slice_id=int(values['slice']);
                if 'cycle' not in native:raise ValueError('cumulative ideal snapshot lacks native clock context')
                row={k:(v if k in ('scope','reference') else int(v)) for k,v in values.items()};key=(native['cycle'],slice_id)
                if key in ideal_frames and ideal_frames[key]!=row:raise ValueError('conflicting ideal snapshot in one native clock context')
                ideal_frames[key]=row
            if not line.startswith(('EPL2FTV1|SUMMARY|','EPL2FTV1|TERMINAL|','EPL2B0V1|INVARIANT|')):continue
            parts=line.strip().split('|');values=dict(v.split('=',1) for v in parts[2:])
            kind=parts[1]
            if kind=='INVARIANT' and values['kernel_uid']!='18446744073709551615':continue
            final[kind,int(values['slice'])]={k:int(v) for k,v in values.items()}
    ideal={sid:row for (cycle,sid),row in ideal_frames.items() if cycle==native['cycle']}
    expected={(kind,s) for kind in ('SUMMARY','TERMINAL','INVARIANT') for s in range(64)}
    if set(final)!=expected:raise ValueError('missing exact 64-slice FT/B0 terminal snapshot')
    feature=spec['identity']['feature_vector'];cap=feature['nominal_payload_capacity_per_slice']
    enabled=any(spec['identity']['ideal_vector'].values())
    if set(ideal)!=(set(range(64)) if enabled else set()):raise ValueError('exact ideal slice scope missing/unexpected')
    extras={}
    for slice_id,row in ideal.items():
        for key,value in spec['identity']['ideal_vector'].items():
            if key=='mem_all_data':continue
            if row['ideal_'+key]!=int(value):raise ValueError('actual ideal flags differ from identity')
        if row['reference_responses_live'] or row['reference_arrivals_live']:raise ValueError('local reference state not drained')
        if spec['identity']['ideal_vector']['wb'] and row['wb_data_full']:raise ValueError('ideal WB capacity still refused')
        if spec['identity']['ideal_vector']['meta'] and any(row[k] for k in ('line_mshr_full','descriptor_full','per_address_full')):raise ValueError('ideal metadata capacity still refused')
        extra=row['diagnostic_wb_extra_slots']
        if not 0<=extra<=128 or (not spec['identity']['ideal_vector']['wb'] and extra):raise ValueError('undeclared diagnostic payload backing')
        extras[slice_id]=extra
    summaries=[final['SUMMARY',s] for s in range(64)];terminals=[final['TERMINAL',s] for s in range(64)]
    invariants=[final['INVARIANT',s] for s in range(64)]
    for slice_id,(s,t,i) in enumerate(zip(summaries,terminals,invariants)):
        if s['observed_cycles']!=native['cycle']:raise ValueError('FT terminal snapshot does not match final native cumulative clock')
        actual_cap=cap+extras.get(slice_id,0)
        if enabled and s['wbuf_full']!=ideal[slice_id]['wb_data_full']:raise ValueError('inconsistent WB refusal counters')
        if s['physical_slots']!=actual_cap or s['wbuf']!=feature['wbuf_entries'] or s['mode']!=(2 if feature['unified_wb'] else 1):
            raise ValueError('source-emitted mode/budget does not match run identity')
        if s['role_free']+s['role_resident']+s['role_bypass']+s['wb_slots']!=actual_cap:
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
    structure=parse_structure(raw,spec,final)
    return {'structural_observations':structure,'cycles':native['cycle'],'instructions':native['insn'],'slices':64,
        'unique_requesters':total(terminals,'unique_requesters'),'responses':total(terminals,'responses'),
        'live_descriptors':total(invariants,'descriptor_used'),'live_line_mshrs':total(invariants,'line_mshr_used'),
        'live_wad':total(invariants,'wad_live'),'pending_lower_reads':total(terminals,'pending_lower_reads'),
        'pending_returns':total(terminals,'pending_returns'),'pending_responses':total(terminals,'pending_responses'),
        'wb_created':total(summaries,'wb_created'),'wb_lower_accepted':total(summaries,'wb_lower_accept'),
        'wb_completed':total(summaries,'wb_completed'),'payload_capacity':cap*64+sum(extras.values()),'nominal_payload_capacity':cap*64,'diagnostic_payload_extra_slots':sum(extras.values()),'diagnostic_payload_extra_by_slice':{str(k):extras.get(k,0) for k in range(64)},'diagnostic_scope':'UNIFIED_NATIVE_V1','local_ideal_observations':ideal,
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



def parse_structure(raw,spec,final):
    frames={};clock=None
    for line in Path(raw).open():
        match=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
        if match:clock=int(match[1])
        if not line.startswith('EPL2STRUCTV1|'):continue
        parts=line.strip().split('|');row={k:int(v) for k,v in (p.split('=',1) for p in parts[2:])};key=(parts[1],row['slice'])
        if clock is None:raise ValueError('Structural cumulative snapshot lacks native clock context')
        key=(clock,*key)
        if key in frames and frames[key]!=row:raise ValueError('Conflicting structural terminal in one native clock context')
        frames[key]=row
    records={(kind,sid):row for (cycle,kind,sid),row in frames.items() if cycle==clock}
    if set(records)!={(kind,s) for kind in ['BANK_PEAK','WB_QUOTA','CONFIG'] for s in range(64)}:raise ValueError('Missing exact64 structural config/peak/quota scope')
    f=spec['identity']['feature_vector'];s64=f['static_s64']
    for sid in range(64):
        config=records['CONFIG',sid];bank=records['BANK_PEAK',sid];quota=records['WB_QUOTA',sid]
        expected={'slice':sid,'static_s64':int(s64),'physical_slots':final['SUMMARY',sid]['physical_slots'],'resident_nominal':1024,'bypass_capacity':80 if s64 else 128,'wb_begin':1104 if s64 else 1152,'static_wb_capacity':64 if s64 else 16,'legacy_wbuf':16,'bank_count':4,'bank_ops_per_physical_cycle':f['ops_per_bank_cycle'],'copy_latch_bytes':128}
        if config!=expected:raise ValueError('Source structural getter layout/budget changed')
        if bank['ops_per_physical_cycle']!=f['ops_per_bank_cycle'] or any(not 0<=bank['bank'+str(n)]<=f['ops_per_bank_cycle'] for n in range(4)):raise ValueError('Actual physical bank service budget exceeded')
        if quota['cap']!=f['wb_local_cap'] or quota['reserved'] or quota['live']:raise ValueError('WB responsibility quota not drained/mismatched')
        if quota['cap'] and (quota['total_peak']>quota['cap'] or quota['reserved_peak']>quota['cap'] or quota['live_peak']>quota['cap']):raise ValueError('Reserved+live WB responsibility cap exceeded')
    return {kind:{str(s):records[kind,s] for s in range(64)} for kind in ['BANK_PEAK','WB_QUOTA','CONFIG']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();spec=json.loads(Path('input_spec.json').read_text());value=parse(args.raw,spec)
    args.out.write_text(json.dumps(value,indent=2)+'\n')

if __name__=='__main__':main()
