"""Six CPU-only negative-path scenarios, using unchanged actual E38 classes."""
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import types

P = pathlib.Path
HERE = P(__file__).resolve().parent
E38 = HERE.parent / 'large_job_aging_v1'
sys.path.insert(0, str(E38))
from large_job_aging import AgingChooser, G
from aging_runtime_frames import RuntimeFrames
from frame_read_guard import FrameReadGuard


def digest(path):
    return hashlib.sha256(P(path).read_bytes()).hexdigest()


def frame():
    return dict(now=0, budget_bytes=200*G, effective_total_growth_bytes=180*G,
        memory_utilization_fraction=.88, own_live=[], consumed={}, claim_cohorts=[], closures=[],
        pending=[dict(cohort='SHORT', input_digest='short', program='short', cell='DH', profile='P0',
                      cost_bytes=G, first_eligible_monotonic=0)],
        active_input_digests=[], started_programs=[], pressure_reasons=[],
        total_padding_discount_bytes=0, padding_discount_by_cohort={}, accounted_growth_by_cohort={})


def main():
    pins = {'large_job_aging.py': 'b4e69ea06c017898ce9c5f5fcbb57cfb380ee47942c19cd88520abfaaf07d1ff',
            'aging_runtime_frames.py': '98d5b5c6e6b4a35ec06565c347080b93cb89ed4d4fe8621f978517ff671603a2'}
    # Explicit hashes below are recorded and checked against the actual frozen copy.
    actual = {name: digest(E38/name) for name in pins}
    assert actual == pins
    checks = []
    sleeps = []
    chosen = []
    def original(pool, *args):
        chosen.append([p['cohort'] for p in pool])
        return dict(cohort=pool[0]['cohort']) if pool else None
    def call(gate):
        return gate.wrapper([{'cohort':'SHORT'}], {}, {}, {}, None, {}, 0)
    def build(provider):
        aging = AgingChooser(original, provider)
        return aging, FrameReadGuard(aging, sleeper=sleeps.append)

    # 1 Actual RuntimeFrames half-written RESULT, then closed complete bytes.
    with tempfile.TemporaryDirectory() as tmp:
        root=P(tmp);(root/'control').mkdir();(root/'analysis').mkdir()
        (root/'control/ACTUAL_CANARY_QUALIFICATION.json').write_text('{}')
        (root/'control/MATRIX_CURRENT.json').write_text(json.dumps({'points':[{'cohort':'DONE','program':'done','input_digest':'d'}]}))
        result=root/'analysis/DONE.RESULT.json';result.write_text('{"uuid":')
        q={'consumed':{'DONE':{'uuid':'DONE-UUID','execution_receipt':{'stop_reason':None,'launcher_wait_returncode':0}}}}
        baseline=dict(own_ram_forecasts=[],utc='CPU',total_projected_additional_RAM_bytes=0,
            admission_decision=dict(admission_RAM_budget_bytes=G,memory_utilization_fraction=.88,pressure_reasons=[]))
        provider=RuntimeFrames(root, types.SimpleNamespace(registered=lambda:(None,None,q,None)),
            types.SimpleNamespace(resources=lambda *a:copy.deepcopy(baseline)),
            types.SimpleNamespace(accepted=lambda v:v.get('accepted')is True),lambda b:[])
        aging=AgingChooser(original,provider)
        gate=FrameReadGuard(aging,sleeper=lambda seconds:result.write_text(json.dumps({'uuid':'DONE-UUID','accepted':True})))
        f=gate.frames([],{}, {},{},None,{},0)
        assert f['closures'][0]['accepted_strict_archive_restore'] and gate.last_recovery['attempts']==2
        assert len(provider.completion_cache)==1 and all(provider.completion_cache.values())
        checks.append('actual_E38_half_RESULT_recovers_without_false_cache')
        # 2 Persistent corrupt actual RESULT: no valid frame, no state advance.
        result.write_text('{"uuid":')
        aging=AgingChooser(original,provider);gate=FrameReadGuard(aging,sleeper=lambda s:None)
        before=copy.deepcopy(aging.state.__dict__);n=len(chosen)
        assert gate.wrapper([],{}, {},{},None,{},0) is None
        assert aging.state.__dict__==before and aging.calls==0 and len(chosen)==n
        assert gate.last_issue['attempts']==3 and gate.last_issue['retry_sleep_seconds']==.07
        checks.append('persistent_actual_RESULT_corruption_failclosed_state_unchanged')

    # 3 File disappears between exists/stat/read, then recovers.
    counts=[0]
    def disappearing(*args):
        counts[0]+=1
        if counts[0]==1:raise FileNotFoundError('CPU exists/stat/read race')
        return frame()
    aging,gate=build(disappearing)
    assert call(gate)['cohort']=='SHORT' and gate.last_recovery['attempts']==2
    checks.append('ENOENT_race_recovers_fresh_no_stale_frame')

    # 4 Failure on fresh post-choice frame: restore already-advanced accounting.
    counts=[0]
    def second_bad(*args):
        counts[0]+=1
        if counts[0]>1:raise json.JSONDecodeError('CPU partial', '{', 1)
        return frame()
    aging,gate=build(second_bad);before=copy.deepcopy(aging.state.__dict__);n=len(chosen)
    assert call(gate)is None and len(chosen)==n+1
    assert aging.state.__dict__==before and aging.calls==0 and aging.frame_provider is second_bad
    checks.append('second_frame_failure_rolls_back_private_aging_and_returns_no_proposal')

    # 5 Invalid UTF-8 / filesystem I/O never fabricate a resource snapshot.
    for failure in (UnicodeDecodeError('utf8',b'\xff',0,1,'CPU partial UTF8'),OSError('CPU I/O')):
        def unavailable(*args):raise failure
        aging,gate=build(unavailable);before=copy.deepcopy(aging.state.__dict__)
        assert call(gate)is None and aging.state.__dict__==before and gate.failclosed_passes==1
        assert not gate.last_issue['stale_frame_reused'] and not gate.last_issue['resource_snapshot_fabricated']
    checks.append('UTF8_and_IO_failclosed_without_stale_or_empty_snapshot')

    # 6 Scientific/invariant exceptions are not relabelled as transient reads.
    for failure in (AssertionError('identity changed'),KeyError('contract missing')):
        def invariant(*args):raise failure
        aging,gate=build(invariant)
        try:call(gate)
        except type(failure):pass
        else:raise AssertionError('invariant swallowed')
        assert aging.frame_provider is invariant and gate.failclosed_passes==0
    checks.append('identity_assertions_and_missing_contract_keys_not_swallowed')

    output=dict(status='PASS',checks=checks,count=len(checks),frozen_E38_sha256=actual,
        candidate_sha256=digest(HERE/'frame_read_guard.py'),models_started=0,signals_sent=0,
        production_installed=False,max_retry_sleep_seconds=.07)
    (HERE/'CPU_QUALIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output))

if __name__=='__main__':main()
