"""Narrow new wall-contract validation only, inside canonical strictly admitted role.

No old W1/W2 tests, guard/native process, simulator, signal or wall sleep.
All resource/time samples and altered terminal receipts are DECLARED_SYNTHETIC.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import time
from types import SimpleNamespace
import runtime_policy_b as policy
from wall_contract_guard import guard_contract

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
OLD=REPO/'docs/dtc_l1/review_packs/DTC_AG7_POLICYB_INTEGRATED_20261020_V1'

def qualify_wall_contract(evidence):
    began=time.monotonic_ns()
    old_path=REPO/'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py'
    before=next(n for n in ast.parse(old_path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='guard_contract')
    after=next(n for n in ast.parse((HERE/'wall_contract_guard.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='guard_contract')
    changed=0
    for node in ast.walk(after):
        if isinstance(node,ast.Constant) and node.value==21600:
            node.value=7200;changed+=1
    assert changed==1 and ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
    old_runtime=(OLD/'prepared_ag7/runtime_policy_b.py').read_text()
    assert (HERE/'runtime_policy_b.py').read_text()==old_runtime.replace('7200','21600') and old_runtime.count('7200')==3
    dispatch=ast.parse((HERE/'ag7_dispatch.py').read_text())
    outer=[n for n in ast.walk(dispatch) if isinstance(n,ast.Call) and isinstance(n.func,ast.Subscript) and isinstance(n.func.slice,ast.Constant) and n.func.slice.value=='run_guarded']
    assert len(outer)==1 and isinstance(outer[0].args[5],ast.Constant) and outer[0].args[5].value==21600
    assert policy.PROFILE==dict(nominal_sample_s=10,max_sample_gap_s=30,max_progress_age_s=30,no_retirement_s=600,max_cgroup_high_episode_s=1800,wall_deadline_s=21600)
    class Domain:
        def observe(self,*args):return dict(decision='CONTINUE',stop_reasons=[],warnings=[])
    class Runtime:
        def __init__(self,baseline,output):self.first=baseline;self.host=Domain();self.cgroup=Domain()
        def _project(self,sample):return sample
        def quick_stop(self):return None
    module=SimpleNamespace(Runtime=Runtime)
    start_ns=1_000_000_000
    baseline=dict(monotonic_ns=start_ns,disk_free_bytes=32*policy.GIB,output_filesystem_device=156,host_oom_kill=0,
        pressure={'io':{'full':{'avg10':0.0}}},cgroup_pressure_parsed={'io':{'full':{'avg10':0.0}}})
    runtime=policy.RuntimePolicyB(baseline,Path(evidence),resource_module=module,started_ns=start_ns,opt_in=True)
    at_old=None;at_new=None
    for seconds in range(10,21601,10):
        sample=dict(baseline,monotonic_ns=start_ns+seconds*10**9)
        decision=runtime.observe(sample,0,0,progress=dict(mono_ns=sample['monotonic_ns'],completed=seconds,end='NONE'),
            safety_checks={k:True for k in policy.SAFETY_KEYS},io_impact=dict(known_scope=True,harm_detected=False,conservative_host_episode_profile_accepted=True))
        if seconds==7200:at_old=decision['decision'];assert at_old=='CONTINUE'
        if seconds<21600:assert decision['decision']=='CONTINUE'
        else:at_new=decision;assert decision['stop_reasons']==['WALL_DEADLINE_21600S']
    manifest=json.loads((OLD/'AG7_FOUR_POINT_MANIFEST.json').read_text())
    spec=manifest['points'][0];run=Path(spec['destination'])
    start=json.loads((run/'RUN_START.json').read_text());terminal=json.loads((run/'RUN_TERMINAL.json').read_text());engine=json.loads((run/'ENGINE/TERMINAL.json').read_text())
    synthetic=copy.deepcopy(start);synthetic['timeout_seconds']=21600
    guard_contract(synthetic,terminal,engine,spec)
    rejected=False
    try:guard_contract(start,terminal,engine,spec)
    except ValueError:rejected=True
    assert rejected
    elapsed=(time.monotonic_ns()-began)/1e9
    assert elapsed<90
    receipt=dict(status='PASS_AD8_NARROW_WALL_CONTRACT',provenance='DECLARED_SYNTHETIC_TIME_RESOURCE_AND_ALTERED_TERMINAL_RECEIPTS_NOT_SCIENTIFIC_RESULTS',
        checks=dict(exact_guard_function_AST_except_one_wall_constant=True,exact_runtime_source_except_three_wall_tokens=True,
        outer_guard_argument_21600=True,inner_profile_and_deadline_21600=True,old_7200_runtime_does_not_stop=True,
        new_21600_runtime_stops=True,new_guard_terminal_accepts_21600_rejects_7200=True,all_other_profile_bounds_unchanged=True),
        synthetic_resource_samples=2160,real_wall_seconds=elapsed,old_CPU_tests_reexecuted=0,simulator_starts=0,guard_process_starts=0,signals=0,
        actual_7200_decision=at_old,actual_21600_stop_reasons=at_new['stop_reasons'],
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'runtime_policy_b.py',HERE/'wall_contract_guard.py',HERE/'ag7_dispatch.py']})
    with (Path(evidence)/'D1_WALL_CONTRACT_QUALIFICATION.json').open('x') as stream:stream.write(json.dumps(receipt,indent=2)+'\n')
    return receipt
