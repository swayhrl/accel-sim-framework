"""Registered strict-R2 CPU protocol/guard qualification, never starts a model."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest

P=Path(__file__).resolve().parent
E=Path('/workspace/dtc-ag7-policyb-integrated-174-v1/evidence')
G=E/'w0_frozen_authority'
B=E.parent/'build'
Q=E/'w2_qualification_once'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path,value):
    with path.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')


def main():
    assert sys.argv==[str(P/'w2_qualification_entry.py')]
    Q.mkdir(exist_ok=False)
    reg=json.loads((P/'W2_QUALIFICATION_REGISTRATION.json').read_text());role=reg['role']
    assert role['cwd']==os.getcwd() and sha(sys.executable)==role['executable_sha256']
    for path,h in role['source_sha256'].items():assert sha(path)==h,path
    sys.path[:0]=[str(P/'prepared_ag7/vendor'),str(P/'prepared_ag7'),str(P),str(G/'vendor'),str(G)]
    from cpu_admission_v2 import CPUAdmission
    from w1_cpu_entry import images,identity
    gate=CPUAdmission(reg,[role]);own=identity();image_binding=images()
    admissions=[]
    def admit(name):
        target=Q/name;target.mkdir(exist_ok=False)
        pair=[];checks={}
        for n in range(2):
            if n:time.sleep(10.1)
            s=gate.sample();pair.append(s);write(target/('FIRST.json' if n==0 else 'SECOND.json'),s)
            c=gate.checks(s)  # Original strict host IO<=25, no exception.
            c['self_instance_unchanged']=identity()==own
            c['images_unchanged_before_entry']=images()==image_binding
            c['output_device']=os.stat(E).st_dev==s['output_filesystem_device']
            c['expected_writes']=s['disk_free']-64*1024**2>5*1024**3
            checks.update({str(n+1)+'_'+k:v for k,v in c.items()})
            if not all(c.values()):
                write(target/'ADMISSION.json',dict(status='RESOURCE_HOLD',checks=checks));return False
        a,b=pair
        checks.update(gap_ge10s=b['monotonic_ns']-a['monotonic_ns']>=10*10**9,
            host_oom_same=a['host_oom_kill']==b['host_oom_kill'],
            cgroup_oom_same=all(a['cgroup_events'][k]==b['cgroup_events'][k] for k in ['oom','oom_kill']),
            output_device_same=a['output_filesystem_device']==b['output_filesystem_device'])
        write(target/'ADMISSION.json',dict(status='PASS_STRICT_HEAVY_R2' if all(checks.values()) else 'RESOURCE_HOLD',checks=checks))
        admissions.append(dict(name=name,first_ns=a['monotonic_ns'],second_ns=b['monotonic_ns']))
        return all(checks.values())
    if not admit('protocol_tests_admission'):
        write(Q/'RESULT.json',dict(status='RESOURCE_HOLD',simulator_starts=0));return 0
    import test_integration
    transcript=io.StringIO()
    result=unittest.TextTestRunner(stream=transcript,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_integration))
    write(Q/'PURE_PROTOCOL_TESTS.json',dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),transcript=transcript.getvalue(),provenance='DECLARED_SYNTHETIC_EXCEPT_REAL_SELF_SOCKET_CREDENTIALS'))
    print(transcript.getvalue())
    if not result.wasSuccessful():
        write(Q/'RESULT.json',dict(status='ENGINEERING_TEST_FAILURE',simulator_starts=0));return 1
    # Dependencies loaded by the tests are bound before the next real entry.
    image_binding=images()
    if not admit('native_probe_admission'):
        write(Q/'RESULT.json',dict(status='RESOURCE_HOLD_AFTER_PROTOCOL_TESTS',simulator_starts=0));return 0
    compile_argv=reg['native_compile_argv']
    with (Q/'native_compile.stdout').open('xb') as out,(Q/'native_compile.stderr').open('xb') as err:
        built=subprocess.run(compile_argv,stdout=out,stderr=err,timeout=60)
    assert built.returncode==0,'NATIVE_PROBE_BUILD_FAILED'
    # No model library or trace is linked or loaded by this component program.
    actual=subprocess.run([str(B/'ag7-progress-header-probe-v2')],capture_output=True,text=True,timeout=10)
    write(Q/'NATIVE_HEADER_PROBE.json',dict(returncode=actual.returncode,stdout=actual.stdout,stderr=actual.stderr,
        binary_sha256=sha(B/'ag7-progress-header-probe-v2'),Core_or_simulator_loaded=False))
    assert actual.returncode==0
    from freeze_static import freeze_executable
    from guarded_process import run_guarded
    from telemetry_receiver import TelemetryReceiver
    from runtime_policy_b import TerminalClosure
    # Static dependency resolution never executes the model ELF.
    manifest,objects=freeze_executable(B/'ag7-progress-header-probe-v2',B)
    write(Q/'CPU_NATIVE_MAPPING_MANIFEST.json',manifest)
    image_binding=images()
    cases=[]
    for mode in ['normal','conflict']:
        if not admit('guard_'+mode+'_admission'):
            write(Q/'RESULT.json',dict(status='RESOURCE_HOLD_BEFORE_GUARD_'+mode.upper(),cases=cases,simulator_starts=0));return 0
        parent,child=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM|socket.SOCK_NONBLOCK)
        parent.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);os.set_inheritable(child.fileno(),True)
        env=dict(os.environ,DTC_AG7_POLICY_B_PROGRESS='1',DTC_AG7_PROGRESS_FD=str(child.fileno()),
            DTC_AG7_GENERATION='DECLARED_SYNTHETIC_GUARD_'+mode,DTC_AG7_INPUT_SHA='0'*64,DTC_AG7_ROI_SHA='1'*64)
        receiver=[None];records=[];bindings=[]
        before=time.monotonic_ns();dest=Q/('guard_'+mode)
        def observer(pid,full_hint,ownership):
            instance=ownership.confirmed.get(pid)
            if instance is None:return 'EXACT_CPU_GUARD_ROOT_NOT_CONFIRMED'
            if receiver[0] is None:
                binding=dict(proven_actual_root=True,pid=pid,start_ticks=instance['start_ticks'],
                    generation=env['DTC_AG7_GENERATION'],input='0'*64,roi='1'*64)
                receiver[0]=TelemetryReceiver(parent,binding,started_ns=before,opt_in=True);bindings.append(binding)
            state=receiver[0].drain(time.monotonic_ns());records.extend(state['records'])
            if mode=='conflict' and state['terminal']=='NATURAL':return 'DECLARED_CPU_CONFLICT_STOP_AFTER_NATURAL_PACKET'
            if time.monotonic_ns()-before>20*10**9:return 'CPU_QUALIFICATION_DEADLINE'
            return None
        terminal=run_guarded([str(B/'ag7-progress-header-probe-v2'),mode],env,
            {str(B/'ag7-progress-header-probe-v2'):manifest},dest,'CPU_FIXTURE',25,None,observer)
        # Short roots can exit between periodic hooks; final drain still binds
        # only the actual CHILD receipt written by the guard before resumption.
        child_info=json.loads((dest/'CHILD.json').read_text())
        if receiver[0] is None:
            binding=dict(proven_actual_root=True,pid=child_info['pid'],start_ticks=child_info['start_ticks'],
                generation=env['DTC_AG7_GENERATION'],input='0'*64,roi='1'*64)
            receiver[0]=TelemetryReceiver(parent,binding,started_ns=before,opt_in=True);bindings.append(binding)
        state=receiver[0].drain(time.monotonic_ns());records.extend(state['records'])
        parent.close();child.close()
        valid=(terminal['status']=='PASS_GUARDED_NATURAL_EXIT0' and terminal['identity_pass'] and terminal['returncode']==0) if mode=='normal' else (terminal['status']=='STOP_GUARDED_PROCESS' and terminal['owned_children_live']==0 and any(r['returncode']==-9 for r in terminal['owned_process_exit_instances']))
        assert valid,terminal
        cases.append(dict(mode=mode,guard_status=terminal['status'],root=child_info,
            bindings=bindings,actual_records=records,terminal_packet=receiver[0].terminal,
            actual_exit_instances=terminal['owned_process_exit_instances'],controlled_root_SIGKILL=(mode=='conflict'),
            current_owned_live=terminal['owned_children_live'],simulator_starts=terminal['simulator_starts'],passed=valid,
            scope='DECLARED_SYNTHETIC_COUNTERS_REAL_NATIVE_PROCESS_CREDENTIALS_PTRACE_FORK_REAP'))
        write(Q/('GUARD_'+mode.upper()+'_RESULT.json'),cases[-1])
    write(Q/'RESULT.json',dict(status='W2_TARGETED_CPU_PROTOCOL_AND_GUARD_PASS',pure_tests=result.testsRun,
        native_probe_exit=actual.returncode,guard_cases=cases,admissions=admissions,
        simulator_starts=0,Core_or_model_execution_starts=0,foreign_signals=0,
        controlled_own_CPU_SIGKILL=1,old_guard_source_modified=False))
    print('W2_TARGETED_CPU_PROTOCOL_AND_GUARD_PASS')
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        if Q.exists():write(Q/'EXCEPTION.json',dict(error=repr(exc),simulator_starts=0))
        raise
