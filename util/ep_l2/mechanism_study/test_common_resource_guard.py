"""Bounded A supervisor control with injected space; no E API/compiler/native.

Usage: python3 -B test_common_resource_guard.py --out NEW_DIRECTORY
This invokes the actual frozen run_owned with one owned sleeping process and a
separate controlled sentinel. It verifies margin stopping and raw preservation.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from common_resource_guard import check_runtime, ResourceLimit, finalize_limit


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    spec_path = root/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2/COMMON_NATIVE_BUILD_SPEC_r6.json'
    build_spec = json.loads(spec_path.read_text())
    frozen = Path(build_spec['framework'])/build_spec['supervisor']
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == build_spec['supervisor_SHA256']
    guard = load(frozen, 'actual_common_supervisor_control')
    policy = build_spec['expected_E_workspace_policy']
    floor, margin = policy['disk_floor_bytes'], policy['monitor_reserve_bytes']
    assert floor == 5*2**30 and margin == 2*2**30
    report = dict(campaign_id=build_spec['campaign_id'],disk_floor_bytes=floor+margin,
        authorized_task_floor_bytes=floor,memory_floor_bytes=64*2**30,
        monitor_reserve_bytes=margin,E_workspace_disk_policy=dict(policy,control_injected=True),commands=[])
    live = dict(disk_free_bytes=floor+margin+1,available_memory_bytes=80*2**30,
                source='CONTROL_INJECTED_NOT_REAL_RESOURCE_SURVEY')
    arguments = dict(report=report,out=out,live=live,share_free=42*2**30,
        written=0,built=0,memory_rss=1024,result_growth=2**20,build_growth=2**20,build_total=2**20)
    check_runtime(**arguments) # Safe above stop margin, even far below old48GiB.
    state = dict(samples=0)
    def resources():
        state['samples'] += 1
        actual = dict(live,disk_free_bytes=floor+margin+1 if state['samples']==1 else floor+margin)
        check_runtime(**dict(arguments,live=actual))
        return actual
    def identity(pid):
        proc=Path('/proc')/str(pid)
        fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
        return dict(pid=pid,start_ticks=int(fields[19]),
                    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
    def save():
        (out/'RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    sentinel=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(5)'],start_new_session=True)
    try:
        try:
            guard.run_owned([sys.executable,'-B','-c',
                "import time;print('A_CONTROL_CHILD_RAW_PRESERVED',flush=True);time.sleep(5)"],
                'owned_control',out,dict(os.environ),report,save,resources,identity,5)
        except ResourceLimit:
            pass
        else:
            raise AssertionError('owned process did not stop at policy reserve')
        incident=json.loads((out/'RESOURCE_LIMIT.json').read_text())
        assert incident['reasons']==['WORKSPACE_MONITORED_STOP_MARGIN']
        assert incident['actual_resources']['disk_free_bytes']==floor+margin
        assert sentinel.poll() is None, 'separate controlled process was affected'
        record=report['commands'][0]
        assert record['exit_code']==-signal.SIGTERM
        assert not Path('/proc',str(record['process']['pid'])).exists()
        raw=Path(record['log']).read_bytes()
        assert b'A_CONTROL_CHILD_RAW_PRESERVED' in raw
        assert record['log_sha256']==hashlib.sha256(raw).hexdigest()
        report['finished_UTC']='CONTROL_TERMINAL_NOT_SCIENCE'
        finalize_limit(report,out)
        final=json.loads((out/'RESOURCE_LIMIT.json').read_text())
        assert final['final_commands'][0]['exit_code']==-signal.SIGTERM
        assert final['final_commands'][0]['log_sha256']==hashlib.sha256(raw).hexdigest()
        result=dict(status='CONTROL_ONLY_DYNAMIC5G_MARGIN_AND_OWNED_TERMINATION_VERIFIED',
            observed_unix=time.time(),safe_above_stop_margin=True,stopped_at_margin=True,
            controlled_separate_sentinel_untouched=True,RESOURCE_LIMIT_and_raw_preserved=True,
            final_exit_and_log_hash_in_RESOURCE_LIMIT=True,
            disk_policy_injected_not_E_admission=policy,compiler_starts=0,native_starts=0,
            central_api_calls=0,central_registry_writes=0,
            real_resource_survey=False,real_E_policy_consumed=False,
            actual_supervisor_sha256=build_spec['supervisor_SHA256'],
            resource_guard_sha256=hashlib.sha256((Path(__file__).parent/'common_resource_guard.py').read_bytes()).hexdigest())
        (out/'CONTROL_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
    finally:
        if sentinel.poll() is None:
            os.killpg(sentinel.pid,signal.SIGTERM)
        sentinel.wait()


if __name__=='__main__':
    main()
