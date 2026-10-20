"""One finite 28-row closed replay. No raw/trace/process access or run launch.

The proposal executes only inside the source-bound, admitted cpu_entry role.
If admission holds, the parent may call main(False) for old-rule arithmetic
and explicitly NOT_EXECUTED expected proposal decisions; it is not CPU PASS.
"""
import csv
import hashlib
import json
from pathlib import Path

PACK = Path(__file__).resolve().parent
WT = PACK.parents[3]
BB = WT / 'docs/dtc_l1/review_packs/DTC_AG6_IO_DIAG_20261020_V1'
EX = WT / 'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution'
E = Path('/workspace/dtc-ag6-bb2-policy-174-v1/evidence')
IDENTITY = dict(pid=1087098, start_ticks=918078939,
                input_id='AG6_AE_GEMM_ORIGINAL_FULL_INPUT', roi_id='ORIGINAL_FULL_INPUT',
                generation='77cbc367-150c-418d-85e0-3be23d952498')


def main(execute_proposal=True):
    original = (BB/'STOP_RECONSTRUCTION.tsv').read_bytes()
    hashes = list(csv.DictReader((BB/'FILES_SHA256.tsv').open(), delimiter='\t'))
    expected = next(x['sha256'] for x in hashes if x['path']=='STOP_RECONSTRUCTION.tsv')
    assert hashlib.sha256(original).hexdigest() == expected
    rows = list(csv.DictReader(original.decode().splitlines(), delimiter='\t'))
    assert len(rows) == 28
    proof = json.loads((BB/'EXECUTED_SOURCE_PROOF.json').read_text())
    old_record = next(x for x in proof['files'] if x['path'].endswith('/frozen_ag4_resource_policy.py.txt'))
    old_source = WT / old_record['path']
    assert hashlib.sha256(old_source.read_bytes()).hexdigest() == old_record['sha256']
    # Independent arithmetic implements only the pinned IO qualification rule.
    # Memory/OOM/disk/swap pass over all28 stored rows; no full guard requalification.
    last, counts = None, {'host':0, 'cgroup':0}
    proposal = None
    proposed_prelaunch = 'NOT_EXECUTED_RESOURCE_HOLD'
    if execute_proposal:
        from policy_b_offline import Params, PolicyB, SAFETY_KEYS
        # Illustrative replay durations ONLY, not proposed production defaults.
        params = Params(illustrative=True, max_sample_gap_s=40,
                        max_progress_age_s=3, no_progress_watchdog_s=20,
                        long_phase_grace_s=40, max_io_warning_s=60)
        proposal = PolicyB(params, offline_opt_in=True)
        admission = EX/'ag6_actual_cohort_stop_v2/session/admissions/AE_GEMM'
        first = json.loads((admission/'FIRST.json').read_text())
        second = json.loads((admission/'SECOND.json').read_text())
        a,b = first['snapshot'],second['snapshot']
        def psi(s,scope,kind):
            return float(s['pressure' if scope=='host' else 'cgroup_pressure_parsed'][kind]['full']['avg10'])
        def headroom(s):
            return int(s['cgroup']['memory.max'])-int(s['cgroup']['memory.current'])
        historical_r2 = all(s['host']=='huangrulin-174' and s['uid']==0 and
            s['host_MemAvailable_bytes']>=32*1024**3 and headroom(s)>=32*1024**3 and
            s['disk_free_bytes']-64*1024**2>5*1024**3 and
            all(psi(s,scope,kind)<=(25 if kind=='io' else 1)
                for scope in ['host','cgroup'] for kind in ['io','memory'])
            for s in [a,b])
        historical_r2 &= first['authority']['status']==second['authority']['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
        oom_unchanged = a['host_oom_kill']==b['host_oom_kill'] and all(
            a['cgroup']['events'][k]==b['cgroup']['events'][k] for k in ['oom','oom_kill'])
        assert historical_r2 and oom_unchanged
        initial=dict(phase='PRELAUNCH', timestamp_s=b['monotonic_ns']/1e9,
            identity=IDENTITY, output_free_bytes=b['disk_free_bytes'], expected_write_bytes=64*1024**2,
            host_io_full_avg10=psi(b,'host','io'), cgroup_io_full_avg10=psi(b,'cgroup','io'),
            host_memory_headroom_bytes=b['host_MemAvailable_bytes'],cgroup_memory_headroom_bytes=headroom(b),
            host_memory_full_avg10=psi(b,'host','memory'),cgroup_memory_full_avg10=psi(b,'cgroup','memory'),
            paired_r2=dict(host=historical_r2,cgroup=historical_r2,
                interval_s=(b['monotonic_ns']-a['monotonic_ns'])/1e9,oom_unchanged=oom_unchanged,
                exact_role_authority_pass=historical_r2),
            # Startup predicates only: no new runtime episode has begun. They
            # bind accepted historical admission, NOT new measured runtime impact.
            safety_checks={k:True for k in SAFETY_KEYS})
        proposed_prelaunch=proposal.evaluate(initial)['state']
        assert proposed_prelaunch == 'PRELAUNCH_READY'
    output=[]
    for r in rows:
        t=int(r['monotonic_ns'])
        qualified = last is None or t-last >= 30*10**9
        if qualified:
            for scope in counts:
                counts[scope]=counts[scope]+1 if float(r[scope+'_io_full_avg10'])>25 else 0
            last=t
        old='STOP' if any(v>=3 for v in counts.values()) else 'CONTINUE'
        assert old==r['decision']
        assert counts['host']==int(r['host_io_run']) and counts['cgroup']==int(r['cgroup_io_run'])
        assert qualified==(r['psi_qualification']=='True')
        assert float(r['host_memory_full_avg10'])==float(r['cgroup_memory_full_avg10'])==0
        assert int(r['disk_free_bytes'])>5*1024**3
        if execute_proposal:
            # Fields absent from history remain UNKNOWN. We do NOT fabricate
            # a measured replacement I/O-impact/scope predicate or runtime
            # projected output-growth/identity closure from a preflight PASS.
            sample=dict(phase='RUNTIME',timestamp_s=t/1e9,identity=IDENTITY,
                host_io_full_avg10=float(r['host_io_full_avg10']),
                cgroup_io_full_avg10=float(r['cgroup_io_full_avg10']),
                output_free_bytes=int(r['disk_free_bytes']),expected_write_bytes=None,
                safety_checks={},semantic_progress=dict(status='UNAVAILABLE'),
                actual_stop=r['decision']=='STOP')
            new=proposal.evaluate(sample)
        else:
            new=dict(state='RUNTIME_INSUFFICIENT_EVIDENCE',
                reason='EXPECTED_ONLY_NOT_EXECUTED_RESOURCE_HOLD_missing_semantic_and_runtime_safety_adapter')
        assert new['state']!='COMPLETE_CANDIDATE'
        output.append(dict(r,old_io_reproduced=old,
            old_io_qualified_run=counts['cgroup'],proposed_b_state=new['state'],proposed_b_reason=new['reason'],
            semantic_progress='UNAVAILABLE',replacement_io_impact='UNAVAILABLE',
            proposal_evaluator_executed=execute_proposal,
            counterfactual='UNDETERMINED_PROGRESS_NO_PRODUCTION_PROMOTION'))
    with (PACK/'HISTORICAL_28_ROW_REPLAY.tsv').open('w') as out:
        writer=csv.DictWriter(out,fieldnames=output[0],delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(output)
    receipt=dict(status='OFFLINE_REPLAY_ONLY_NO_PRODUCTION_PROMOTION',rows=28,
        original_28_sha256=expected,pinned_old_io_policy_sha256=old_record['sha256'],
        old_reproduced_decisions_match_all28=True,old_stop_line=28,
        old_stop_monotonic_ns=int(rows[-1]['monotonic_ns']),
        actual_proposal_evaluator_executed=execute_proposal,proposal_prelaunch=proposed_prelaunch,
        proposal_all28_insufficient=True,semantic_progress='UNAVAILABLE',
        replacement_runtime_impact_and_adapter_predicates='UNAVAILABLE_NOT_FABRICATED',
        no_historical_completion_or_infinite_safety_claim=True,
        counterfactual='UNDETERMINED_PROGRESS_NO_PRODUCTION_PROMOTION',
        synthetic_progress_inserted_into_history=False,
        scope='Pinned IO decision reproduction, not whole guard or production PolicyB qualification')
    (E/'REPLAY_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    raise SystemExit('Run only through admitted cpu_entry; parent may perform explicit source-only arithmetic mode.')
