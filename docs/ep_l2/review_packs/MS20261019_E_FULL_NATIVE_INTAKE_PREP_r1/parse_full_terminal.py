"""Full-system terminal adapter CANDIDATE, not native-qualified or a qualification grant.

Reuses the frozen structural decoder and old strict closure validator. Source
formats are from A Core066c60b1 and its44c940b7 disabled-observer correction. Full mode requires exact E combination qualification; no raw evidence is rewritten.
Actual native replay is required before this parser can be bound to E qualification.
"""
import sys
sys.path.insert(0,"/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e")
import policy_v2
import argparse
import json
from pathlib import Path
import re
from coordinator import (CAMPAIGN,Coordinator,NATIVE_GATES,digest,require,
                         tooling_binding,run_key,write_json)
from parse_unified_terminal import parse_structure
from validate import validate_summary

REASONS=('WB_DATA_SPACE','BANK_COMPATIBLE_LANDING','TAG_SET_PENDING','LINE_MSHR_FULL',
 'DESCRIPTOR_FULL','PER_LINE_CAP','WAD_FULL','SAME_ADDRESS_WB','PINNED_PAYLOAD',
 'FRONTEND_TRANSACTION','MISS_QUEUE_FULL','RESPONSE_QUEUE_FULL','DATA_SERVICE','COPY_PIPELINE',
 'ANY_FIRST_BLOCK_TO_ADMISSION','VICTIM_LOOKUP','READONLY_LOOKUP')
PROFILES={'S':(1,0,0),'U':(2,0,0),'S_COPY_FREE':(1,1,0),
          'S_L2_DATA_FREE':(1,0,1),'U_L2_DATA_FREE':(2,0,1)}
PROFILES.update({'W_ONLY':(2,0,0),'F':(2,0,0),'F_MINUS_V':(2,0,0),'F_MINUS_R':(2,0,0),
                 'WV_T':(2,0,0),'WV_M':(2,0,0),'F_L2_DATA_FREE':(2,0,1)})
EXEMPT=('response','fill','lower_wb','frontend','copy_read','copy_write')


def numbers(parts):
    out={}
    for part in parts:
        key,value=part.split('=',1)
        require(key not in out,'duplicate terminal field: '+key)
        if key=='measurement':
            require(value=='DISABLED_NOT_OBSERVED','unreviewed measurement state')
            out[key]=value;continue
        out[key]=[int(n) for n in value.split(',')] if key=='hist_log2' else int(value)
        require(all(n>=0 for n in out[key]) if isinstance(out[key],list) else out[key]>=0,'negative source counter: '+key)
    return out


def full_numbers(parts):
    strings={'manifest','scope','oracle','measurement','reason','metadata_PPA','metadata_clock_closure'}
    out={}
    for part in parts:
        key,value=part.split('=',1);require(key not in out,'duplicate full mechanism field')
        if key in strings:out[key]=value
        elif key=='hist_log2':
            out[key]=[int(n) for n in value.split(',')];require(all(n>=0 for n in out[key]),'negative full histogram')
        elif value=='NA' and key in ('epoch_begin_gpu_cycle','epoch_end_gpu_cycle','last_response_gpu_cycle'):out[key]='NA'
        else:
            out[key]=int(value);require(out[key]>=0,'negative full mechanism counter')
    return out


def validate_full_records(records,spec,victim,ro):
    expected=set()
    reasons=('TAG_SET_ALL_PENDING','LINE_MSHR_FULL','SHARED_DESCRIPTOR_FULL','PER_ADDRESS_FULL')
    for sid in range(64):
        if victim:
            expected|={('EPL2TVDV2','SUMMARY',sid,-1),('EPL2TVDV3','METADATA_COST',sid,-1)}
        if ro:
            expected|={('EPL2ROV1','SUMMARY',sid,-1)}
            expected|={('EPL2ROC1',kind,sid,-1) for kind in ('CLOSURE','RESOURCE','LOWER_CONCURRENCY')}
            expected|={('EPL2ROC1','WAIT',sid,r) for r in reasons}
    require(set(records)==expected,'exact64slice TVD/RO scope missing or unexpected')
    tvd={};readonly={};opts=spec['profile_semantics']['effective_options']
    for sid in range(64):
        if victim:
            v=records['EPL2TVDV2','SUMMARY',sid,-1];cost=records['EPL2TVDV3','METADATA_COST',sid,-1]
            require(v['mandatory']==0 and v['live']==v['role_tvd'],'victim mandatory state not drained or retained-role mismatch')
            require(v['served_sector_bytes']==v['served_sectors']*32,'victim sector-byte accounting mismatch')
            require(v['dirty_forward_responses']<=v['read_responses'],'invalid victim response subset')
            require(cost['frontend_cam_ports']==cost['completion_cam_ports']==1 and
                    cost['directory_bound_wb_uid_bits']==32 and cost['extra_packet_identity_bits']==0 and
                    cost['indexed_control_read_views']==cost['indexed_control_update_lanes']==3,
                    'unreviewed victim directory/identity/port cost')
            require(cost['metadata_PPA']==cost['metadata_clock_closure']=='UNKNOWN','unproved native metadata PPA')
            tvd[sid]=v
        if ro:
            r=records['EPL2ROV1','SUMMARY',sid,-1];close=records['EPL2ROC1','CLOSURE',sid,-1]
            resource=records['EPL2ROC1','RESOURCE',sid,-1];concurrency=records['EPL2ROC1','LOWER_CONCURRENCY',sid,-1]
            require(r['detach']==int(opts['-gpgpu_ep_l2_ro_tag_detach']) and
                    r['bypass']==int(opts['-gpgpu_ep_l2_ro_line_mshr_bypass']),'RO actual T/M flags mismatch')
            require(r['manifest']==opts['-gpgpu_ep_l2_ro_manifest_sha256'] and
                    r['scope']==resource['oracle']==opts['-gpgpu_ep_l2_ro_scope'],'RO exact oracle scope/hash mismatch')
            require(r['live']==close['ro_live']==close['shared_descriptor_used']==close['shared_line_used']==0 and
                    close['epoch_closed']==1,'RO/shared pool/whole-epoch not drained')
            require(close['scope']=='NATIVE_AND_RO_DISTINCT_SUBCOUNTERS_NOT_ALL_FRONTEND_REQUESTS',
                    'RO descriptor subcounts must not be relabeled all requesters')
            require(r['responses']==close['ro_descriptor_responses']==r['accepted_ro']==concurrency['completed_ro_requesters'],
                    'RO requester/response closure mismatch')
            require(r['transactions']+r['merges']==r['accepted_ro'] and
                    r['accepted_ro']<=r['accepted_oracle_candidates']<=r['accepted_global_reads'],
                    'RO admit/merge/candidate accounting mismatch')
            require(resource['shared_descriptor_capacity']==512 and resource['payload_capacity']==1168 and
                    resource['line_capacity']==128 and resource['query_ports_per_slice']==resource['query_latency_gpu_cycles']==1,
                    'RO shared capacity/query cost changed')
            require(resource['peak_shared_descriptors']<=512 and resource['peak_shared_lines']<=128 and
                    resource['peak_transactions']<=512,'RO peak exceeds shared budget')
            require(resource['lower_read_bytes']==32*r['lower_sectors'] and
                    resource['concurrent_duplicate_read_bytes']==32*r['concurrent_duplicate_sectors'],
                    'RO actual lower byte accounting mismatch')
            require(concurrency['scope']=='RO_ISSUED_NOT_RETURNED_PER_SLICE' and
                    concurrency['measurement']=='OBSERVER_ONLY_NO_ADMISSION_LOOKUP','RO concurrency scope changed')
            require(concurrency['epoch_begin_gpu_cycle']!='NA' and concurrency['epoch_end_gpu_cycle']!='NA' and
                    concurrency['epoch_begin_gpu_cycle']<=concurrency['epoch_end_gpu_cycle'], 'whole-epoch clocks missing/out of order')
            for reason in reasons:
                wait=records['EPL2ROC1','WAIT',sid,reason]
                require(wait['scope']=='SLICE_FRONTEND_HEAD_NONEXCLUSIVE_WAIT' and wait['pending_head']==0 and
                        len(wait['hist_log2'])==16 and sum(wait['hist_log2'])==wait['unique_head_requests'],
                        'RO wait head/histogram closure failed')
            readonly[sid]={'summary':r,'closure':close,'resource':resource,'lower_concurrency':concurrency}
    return tvd,readonly


def parse(raw,spec,qualification):
    identity=spec['identity'];feature=identity['feature_vector'];profile=spec['profile']
    require(profile in PROFILES,'unsupported qualified common terminal profile')
    policy_v2.combination_qualification(qualification,digest)
    mode,copy_free,data_free=PROFILES[profile]
    effective=spec['profile_semantics']['effective_options'];enabled=int(effective['-gpgpu_ep_l2_ms_observer'])
    require(enabled in (0,1),'observer must be explicitly ON/OFF')
    require(int(effective['-gpgpu_ep_l2_diag_copy_free'])==copy_free and
            int(effective['-gpgpu_ep_l2_diag_l2_data_free'])==data_free,'profile diagnostic mismatch')
    fixed={'-gpgpu_ep_l2_wbuf_entries':16,'-gpgpu_ep_l2_payload_mode':2,
        '-gpgpu_ep_l2_descriptor_pool_size':512,'-gpgpu_ep_l2_wad_entries':128,
        '-gpgpu_ep_l2_bank_ops':1,'-gpgpu_ep_l2_static_s64':0,'-gpgpu_ep_l2_wb_local_cap':0,
        '-gpgpu_ep_l2_mq2':0,'-gpgpu_ep_l2_rg1':0,'-gpgpu_ep_l2_ideal_meta':0,
        '-gpgpu_ep_l2_ideal_read_hit':0,'-gpgpu_ep_l2_ideal_wb':0,'-gpgpu_ep_l2_payload_policy':0,
        '-gpgpu_ep_l2_feature_unified_payload':0,'-gpgpu_ep_l2_feature_ro_pending_state':0,
        '-gpgpu_ep_l2_feature_tvd':0,'-gpgpu_ep_l2_feature_adaptive_policy':0,'-gpgpu_ep_l2_ft_mode':mode}
    require(all(int(effective[n])==v for n,v in fixed.items()),'unqualified non-initial profile/resource combination')
    require(feature['payload_capacity_per_slice']==1168 and feature['wbuf_entries']==16 and
            feature['ops_per_bank_cycle']==1 and feature['static_s64'] is False and
            feature['wb_local_cap']==0 and feature['unified_wb']==(mode==2),'wrong initial A-R1 physical budget/mode')
    require(qualification['campaign_id']==CAMPAIGN and qualification['qualified_by']=='E' and
            qualification['status']=='INDEPENDENTLY_QUALIFIED','data correctness needs E qualification')
    source=qualification['source_identity']
    require(all(source[n]==identity[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')),
            'wrong independently qualified producing source/binary')
    for name in NATIVE_GATES|set(qualification['affected_additional_gates']):
        gate=qualification['gates'][name]
        require(gate['status']=='PASS' and gate['production_driven'] is True and
                digest(gate['evidence_path'])==gate['evidence_sha256'],'missing/changed production gate: '+name)
    native={};final={};frames={};mechanisms={};current_clock=None;normal=False
    switches=spec['profile_semantics']['research_switches'];victim=bool(switches['V']);ro=bool(switches['T'] or switches['M'])
    for option,value in {'-gpgpu_ep_l2_tvd_clean':int(victim),'-gpgpu_ep_l2_tvd_dirty':int(victim),
        '-gpgpu_ep_l2_tvd_fixed_entries':0,'-gpgpu_ep_l2_ro_tag_detach':switches['T'],
        '-gpgpu_ep_l2_ro_line_mshr_bypass':switches['M']}.items():
        require(int(effective[option])==value,'actual full combination switch mismatch: '+option)
    for line in Path(raw).open(errors='replace'):
        normal|='GPGPU-Sim: *** exit detected ***' in line
        match=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if match:
            native[match[1]]=int(match[2])
            if match[1]=='cycle' and current_clock!=int(match[2]):
                current_clock=int(match[2]);frames={};mechanisms={}
        if line.startswith(('EPL2FTV1|SUMMARY|','EPL2FTV1|TERMINAL|','EPL2B0V1|INVARIANT|')):
            parts=line.strip().split('|');values=numbers(parts[2:]);kind=parts[1]
            if kind=='INVARIANT' and values['kernel_uid']!=18446744073709551615:continue
            final[kind,values['slice']]=values
        elif line.startswith(('EPL2MSV1|','EPL2MSV2|')):
            require(current_clock is not None,'mechanism snapshot lacks native clock context')
            parts=line.strip().split('|');kind=parts[1]
            require(kind in ('OBSERVER','WAIT','LOCAL_DIAGNOSTIC'),'unreviewed mechanism output kind')
            values=numbers(parts[2:]);key=(kind,values['slice'],values.get('reason',-1))
            require((parts[0]=='EPL2MSV2')==(kind=='WAIT' and values.get('reason',-1)>=15),
                    'mechanism wait reason namespace changed')
            require(key not in frames or frames[key]==values,'conflicting mechanism snapshot at same native clock')
            frames[key]=values
        elif line.startswith(('EPL2TVDV2|','EPL2TVDV3|','EPL2ROV1|','EPL2ROC1|')):
            require(current_clock is not None,'full mechanism snapshot lacks native clock')
            prefix,kind,*parts=line.strip().split('|');values=full_numbers(parts)
            key=(prefix,kind,values['slice'],values.get('reason',-1))
            require(key not in mechanisms or mechanisms[key]==values,'conflicting full mechanism snapshot')
            mechanisms[key]=values
    require(normal and set(native)=={'cycle','insn'} and min(native.values())>0,'missing complete native exit/counters')
    require(set(final)=={(kind,sid) for kind in ('SUMMARY','TERMINAL','INVARIANT') for sid in range(64)},
            'missing exact64slice FT/B0 terminal scope')
    expected={(kind,sid,-1) for kind in ('OBSERVER','LOCAL_DIAGNOSTIC') for sid in range(64)}
    if enabled:expected|={('WAIT',sid,r) for sid in range(64) for r in range(len(REASONS))}
    require(set(frames)==expected,'missing/unexpected exact64slice mechanism terminal scope')
    tvd,readonly=validate_full_records(mechanisms,spec,victim,ro)
    summaries=[];terminals=[];invariants=[];observations=[];local=[]
    waits={name:[] for name in REASONS}
    for sid in range(64):
        s,t,i=(final[kind,sid] for kind in ('SUMMARY','TERMINAL','INVARIANT'))
        if ro:require(readonly[sid]['closure']['native_descriptor_responses']==s['descriptor_responses'],
                      'native descriptor subcount mismatch across FT and RO closure')
        require(s['observed_cycles']==native['cycle'],'FT slice does not match final cumulative native cycle')
        require(s['mode']==mode and s['wbuf']==16 and s['physical_slots']==1168,'actual FT layout/mode mismatch')
        require(s['role_free']+s['role_resident']+s['role_bypass']+s['wb_slots']+(tvd[sid]['role_tvd'] if victim else 0)==1168,'per-slice payload conservation')
        require(s['ownership_consistent']==t['requester_exact_once']==t['hardware_drained']==1,'actual ownership/request/drain failed')
        require(not any(s[n] for n in ('reserved','read_refs','wb_live','wb_slots')),'live FT transient state')
        require(i['bank_pending']==0 and i['terminal_clean']==1 and i['resident_tag_payload_consistent']==1
                and i['payload_double_owner']==0,'native invariant or bank queue not closed')
        require(i['line_mshr_capacity']==128 and i['descriptor_capacity']==512 and i['descriptor_free']==512
                and i['wad_capacity']==128,'native MSHR/descriptor/WAD capacity or closure changed')
        require(s['wb_created']==s['wb_lower_accept']==s['wb_completed'],'actual WB lifecycle failed')
        o=frames['OBSERVER',sid,-1];d=frames['LOCAL_DIAGNOSTIC',sid,-1]
        require('measurement' not in o or enabled==0,'enabled observer labeled unmeasured')
        require(o['enabled']==enabled and d['copy_free']==copy_free and d['l2_data_free']==data_free,'actual observer/diagnostic flags mismatch')
        require(d['hardware_P1_throughput_eligible']==int(not(copy_free or data_free)),
                'diagnostic service mislabeled normal physical P1 throughput')
        require(d['physical_grants']>=0,'invalid physical grant counter')
        require(d['logical_copy_reads']>=0 and d['logical_copy_writes']>=0,'invalid logical copy counts')
        require(all(d['exempt_'+name]>=0 for name in EXEMPT),'invalid exempt service count')
        if not(copy_free or data_free):require(not any(d['exempt_'+n] for n in EXEMPT),'OFF still exempts service')
        if copy_free:
            require(not any(d['exempt_'+n] for n in ('response','fill','lower_wb','frontend')),'COPY_FREE exempted noncopy service')
        if copy_free or data_free:
            require(d['logical_copy_reads']==d['exempt_copy_read'] and d['logical_copy_writes']==d['exempt_copy_write'],
                    'copy logical/exempt accounting mismatch')
        if data_free:require(d['physical_grants']==0,'DATA_FREE still consumes physical data-bank grants')
        if enabled:
            require(o['sampled_cycles']>0 and o['unfinished_head']==0 and o['head_changes_without_admission']==0,
                    'observer head not closed or request identity changed before admission')
            for r,name in enumerate(REASONS):
                w=frames['WAIT',sid,r]
                require(len(w['hist_log2'])==65 and all(n>=0 for n in w['hist_log2']), 'bounded65bin histogram required')
                require(sum(w['hist_log2'])==w['resolved']==w['requests'],'wait resolution/histogram mismatch')
                waits[name].append(w)
        summaries.append(s);terminals.append(t);invariants.append(i);observations.append(o);local.append(d)
    # The unchanged structure decoder validates real bank peaks,1024/128/16
    # geometry,128B copy latch and responsibility quota; diagnostic exemptions
    # remain separate from these physical bank grants.
    structure=parse_structure(Path(raw),spec,final)
    def total(rows,key):return sum(r[key] for r in rows)
    bottleneck='UNKNOWN_OBSERVER_DISABLED'
    if enabled:
        bottleneck={name:{'distinct_requests_first_block':total(rows,'requests'),
             'blocked_observations_over_slices':total(rows,'observations'),
             'resolved_first_waits':total(rows,'resolved'),'request_wait_cycle_sum':total(rows,'sum'),
             'request_wait_max':max(r['max'] for r in rows),
             'unknown_while_unresolved':total(rows,'unknown_while_unresolved'),
             'hist_log2':[sum(r['hist_log2'][b] for r in rows) for b in range(65)]}
             for name,rows in waits.items()}
    metric={'full_mechanism_records':{'victim':tvd,'readonly':readonly},'bottleneck':bottleneck,'trigger':{'logical_copy_reads':total(local,'logical_copy_reads'),
        'logical_copy_writes':total(local,'logical_copy_writes'),
        'exempt_services':{n:total(local,'exempt_'+n) for n in EXEMPT},
        'diagnostic_flags':{'copy_free':bool(copy_free),'l2_data_free':bool(data_free)}},
        'local_service':{'physical_bank_grants':total(local,'physical_grants'),
            'physical_throughput_eligible':not(copy_free or data_free),
            'lower_reads':total(observations,'lower_reads') if enabled else 'UNKNOWN',
            'lower_read_bytes':total(observations,'lower_read_bytes') if enabled else 'UNKNOWN',
            'lower_write_bytes':total(observations,'lower_write_bytes') if enabled else 'UNKNOWN',
            'lower_wb_bytes':total(observations,'lower_wb_bytes') if enabled else 'UNKNOWN',
            'unclassified_refusal_observations':total(observations,'unclassified_refusal_observations') if enabled else 'UNKNOWN'},
        'interpretation_limits':'per-request first wait, overlapping reasons and slice observations are not disjoint GPU stall cycles; logical exempt operations are not paid hardware P1 service; no full-app causal speedup inferred'}
    result={'diagnostic_scope':'MECHANISM_STUDY_LOCAL_SERVICE_V1','cycles':native['cycle'],'instructions':native['insn'],
       'slices':64,'unique_requesters':total(terminals,'unique_requesters'),'responses':total(terminals,'responses'),
       'live_descriptors':total(invariants,'descriptor_used'),'live_line_mshrs':total(invariants,'line_mshr_used'),
       'live_wad':total(invariants,'wad_live'),'pending_lower_reads':total(terminals,'pending_lower_reads'),
       'pending_returns':total(terminals,'pending_returns'),'pending_responses':total(terminals,'pending_responses'),
       'wb_created':total(summaries,'wb_created'),'wb_lower_accepted':total(summaries,'wb_lower_accept'),
       'wb_completed':total(summaries,'wb_completed'),'payload_capacity':1168*64,
       'payload_free':total(summaries,'role_free'),'payload_roles':{'RESIDENT_OR_FILL':total(summaries,'role_resident'),
           'BYPASS':total(summaries,'role_bypass'),'WB_STAGED':total(summaries,'wb_slots'),'TVD_VALID':sum(r['role_tvd'] for r in tvd.values())},
       'transient_payloads':total(summaries,'wb_slots')+total(invariants,'resident_pending')+total(invariants,'bypass_live'),
       'hardware_drained':all(t['hardware_drained']==1 for t in terminals),
       'workload_termination':identity['termination_contract'],'requester_exact_once_audit':True,
       'data_correctness_qualification':True,'raw_log_sha256':digest(raw),'mechanism_metrics':metric,
       'structural_observations':structure,
       'mechanism_slice_records':{'observer':observations,'local_diagnostic':local},
       'source_map':{'full_system':'Actual common A FT/MSV1+MSV2/TVDV2+V3/ROV1+ROC1; no synthetic full-scheme fields','native':'native final gpu_tot_sim_cycle/insn, never slice summed',
           'data':'exact E version-specific production gate evidence, not aggregate counters',
           'closure':'actual FT TERMINAL + B0 INVARIANT for all64slices',
           'mechanism':'A066c60b1 EPL2MSV1 actual observer/local service output',
           'numeric_SASS_output_validated':False}}
    validate_summary(result,identity)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();tooling_binding();spec=json.loads(Path('input_spec.json').read_text());coord=Coordinator()
    item=coord.snapshot();coord.require_no_hold(item,spec['qualification_id'])
    row=item['qualifications'][spec['qualification_id']]
    require(digest(row['path'])==row['sha256'],'E qualification changed')
    write_json(args.out,parse(args.raw,spec,row['qualification']))

if __name__=='__main__':main()
