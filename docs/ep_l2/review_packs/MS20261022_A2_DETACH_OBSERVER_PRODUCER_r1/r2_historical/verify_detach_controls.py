"""Bounded metadata/log analysis of already completed producer controls. Never runs tests."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify(spec_path, native_dir, destination):
    spec=json.loads(spec_path.read_text());report=json.loads((native_dir/'RECEIPT.json').read_text())
    assert report['status']=='PRODUCER_FINITE_PASS_PENDING_E_INDEPENDENT_QUALIFICATION'
    assert report['lease_released'] and report['application_starts']==0
    assert report['native_invocations_completed']==report['native_invocations_attempted']==48
    rows=[];group={};old={};stats={};all_on={};case_scope={}
    for case in spec['cases']:
        detail=native_dir/(case['id']+'.native.json');j=json.loads(detail.read_text())
        assert j['actual_exit']==0 and j['expectation_verified']
        raw=Path(j['raw_log']);assert raw.stat().st_size<=16*2**20 and sha(raw)==j['raw_log_sha256']
        text=raw.read_text();lines=text.splitlines();sig=[l for l in lines if l.startswith('EPL2MS_TEST|SEMANTIC|')]
        assert len(sig)==1;group.setdefault(case['control_class'],[]).append(sig[0])
        previous=[l for l in lines if l.startswith(('EPL2ROV1|','EPL2ROC1|'))]
        old.setdefault(case['control_class'],[]).append(previous)
        actual=[json.loads(l.split('|',1)[1]) for l in lines if l.startswith('EPL2DETACH_DIAG_V1|')]
        mode='reference' if case['target']=='ep_l2_detach_reference' else 'on' if case['observer'] else 'off'
        if mode!='on':assert not actual,'disabled observer emitted diagnostics'
        else:
            slices=[x for x in actual if x['record']=='SLICE'];phases=[x for x in actual if x['record']=='PHASE'];glob=[x for x in actual if x['record']=='GLOBAL'];samples=[x for x in actual if x['record']=='SAMPLE']
            assert slices and len(glob)==1 and len(samples)<=64
            assert len({x['slice'] for x in slices})==len(slices)
            keys=list(slices[0]['counters'])
            assert all(x['closure_ok'] and x['epoch_closed'] and not x['overflow_invalid'] and not x['output_invalid'] and x['live_detached']==0 for x in slices)
            assert all(x['closure_ok'] and not x['overflow_invalid'] and not x['output_invalid'] and x['live_detached']==0 for x in glob)
            for s in slices:
                part=[x for x in phases if x['slice']==s['slice']]
                assert part and all(sum(x['counters'][k] for x in part)==s['counters'][k] for k in keys)
            assert all(sum(x['counters'][k] for x in slices)==glob[0]['counters'][k] for k in keys)
            assert glob[0]['slice']>=len(slices),'GLOBAL.slice is registered-cache count; fixture may also construct an inactive unprinted cache'
            if glob[0]['slice']==len(slices):assert glob[0]['epoch_closed']
            c=glob[0]['counters'];all_on[case['control_class']]=c
            if previous:
                summaries=[dict(a.split('=',1) for a in l.split('|')[2:] if '=' in a) for l in previous if l.startswith('EPL2ROV1|SUMMARY|')]
                assert sum(int(x['detached']) for x in summaries)==c['detach_success']
                assert sum(int(x['transactions']) for x in summaries)==c['ro_admits']
                assert sum(int(x['merges']) for x in summaries)==c['ro_merges']
                assert sum(int(x['responses']) for x in summaries)==c['ro_responses']
            stats[case['control_class']]=dict(slice_records=len(slices),phase_records=len(phases),sample_records=len(samples),diagnostic_bytes=sum(len(l.encode())+1 for l in lines if l.startswith('EPL2DETACH_DIAG_V1|')),closure='PASS_SELECTED_CACHE_COUNTERS_NOT_FULL_GPU',global_registered_cache_instances=glob[0]['slice'],unprinted_inactive_cache_instances=glob[0]['slice']-len(slices),global_epoch_closed=glob[0]['epoch_closed'],global_counter_residual=0,full_GPU_terminal_qualification=False,counter_fields=len(keys))
        row=dict(case=case['id'],control_class=case['control_class'],mode=mode,actual_exit=0,scope=case['scope'],binary_sha256=j['binary_sha256'],native_pid=j['native_pid'],native_started_unix=j['native_started_unix'],receipt=dict(path=str(detail),sha256=sha(detail)),raw_log=dict(path=str(raw),sha256=j['raw_log_sha256'],bytes=raw.stat().st_size),signature=sig[0],control_scope_lines=[l for l in lines if l.startswith('CONTROL_SCOPE|')])
        rows.append(row)
    for name,sigs in group.items():assert len(sigs)==3 and all(s==sigs[0] for s in sigs),'cycle/state/event mismatch '+name
    for name,lines in old.items():assert len(lines)==3 and all(x==lines[0] for x in lines),'old counter mismatch '+name
    def need(case,key,minimum=1):assert all_on[case][key]>=minimum,(case,key,all_on[case][key])
    assert all_on['T_OFF']['ro_admits']==0;need('T_OFF','pressure_T_disabled')
    assert all_on['EMPTY_CERT']['ro_admits']==0;need('EMPTY_CERT','raw_reservation_fail')
    need('NO_PRESSURE_POSITIVE_RO','ro_admits');assert all_on['NO_PRESSURE_POSITIVE_RO']['raw_reservation_fail']==0
    need('PRESSURE_NO_LIVE_RO','pressure_no_live_ro')
    need('PRESSURE_ONLY_OTHER_SET_RO','pressure_no_live_ro')
    need('PRESSURE_STICKY_REUSE','way_reuse_seen');need('PRESSURE_STICKY_REUSE','reuse_seen_first_transition',16)
    need('PRESSURE_ELIGIBLE','pressure_rewrite_miss');need('PRESSURE_ELIGIBLE','detach_success')
    need('NATIVE_REQUESTER_RO_VICTIM','pressure_eligible');need('NATIVE_REQUESTER_RO_VICTIM','pressure_relief_not_consulted');need('NATIVE_REQUESTER_RO_VICTIM','detach_success')
    need('PREVIEW_BLOCKS_COMMIT','pressure_no_live_ro')
    need('DETACH_THEN_LATER_DENIAL','trigger_denied_after_detach');need('DETACH_THEN_LATER_DENIAL','denied_capacity')
    need('RESPONSE_BACKPRESSURE','detach_success');need('RESPONSE_BACKPRESSURE','detached_return_packets');need('RESPONSE_BACKPRESSURE','detached_retired')
    assert all_on['PRESSURE_STICKY_REUSE']['detach_success']==0
    assert all_on['PRESSURE_NO_MISSING']['detach_success']==0
    assert all_on['BOUNDED_OUTPUT']['detach_exception']==0
    for mode in ('0','1'):
        marker=json.loads((native_dir/('observer_output_cap_'+mode+'.json')).read_text().split('|',1)[1]);assert marker['record']=='OUTPUT_INVALID' and marker['output_invalid']
    destination.mkdir(parents=True,exist_ok=True)
    def save(name,j):(destination/name).write_text(json.dumps(j,indent=2)+'\n')
    save('CONTROL_RESULTS.json',dict(schema='A2_DETACH_OBSERVER_ACTUAL_CONTROL_RESULTS_V1',status='PASS_16_CLASSES_48_REAL_EXIT0_METADATA_VERIFIED',source_commit=report['core_source_commit'],main_sha256=report['binary_sha256'],classes=16,native_invocations=48,new_applications=0,controls=rows,observer_on_totals=all_on,diagnostic_records=stats,scope_caveats=['PRESSURE_NO_MISSING uses a real ready/pinned transaction and the actual pure can_detach predicate; does not manufacture raw all-reserved pressure for a ready Tag.','NATIVE_REQUESTER includes actual main-frontend suppression then an explicitly direct-cache control; their commit/head denominators differ.','BOUNDED_OUTPUT exercises local observer-only counter/sample/output storage; no Tag/payload/transaction model state is seeded.','ROLLUP_RESIDUAL exercises real selected-slice disjoint interval/overlap/unattributed buckets. The inherited fixture also constructs an inactive GPU cache: GLOBAL registered objects2 vs emitted selected SLICE1; GLOBAL epoch_closed remainsfalse and is not promoted to full-GPU PASS. Every global counter equals selected-slice sum, so unprinted residual event counts are exactly0 by existing unsigned totals, without synthesizing slice records. Actual64-slice complete application remains E independent future admission/result obligation.']))
    save('OBSERVATIONAL_EQUIVALENCE.json',dict(schema='A2_DETACH_OBSERVER_BOUNDED_NONINTERFERENCE_V1',status='PASS_16_GROUPS_EXACT_D010_ARCHIVE_VS_NEW_OFF_VS_NEW_ON',source_commit=report['core_source_commit'],groups=[dict(control_class=k,identical_signature=v[0],identical_old_ro_counter_records=True,profiles=3) for k,v in group.items()],scope='Bounded real production-directed cycles/event-order/UID/sector versions/Tag handle generation/finalstate/old counters only; supports passive-source applicability review, not whole-application or performance equivalence.'))
    save('CONTROL_VERIFICATION_RECEIPT.json',dict(status='PASS',spec=dict(path=str(spec_path),sha256=sha(spec_path)),native_receipt=dict(path=str(native_dir/'RECEIPT.json'),sha256=sha(native_dir/'RECEIPT.json')),verifier=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),actual_control_class_count=16,actual_native_processes=48,new_native_executions_by_verifier=0,new_builds_by_verifier=0,new_applications=0))
    return stats


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.spec,a.native,a.out)))
