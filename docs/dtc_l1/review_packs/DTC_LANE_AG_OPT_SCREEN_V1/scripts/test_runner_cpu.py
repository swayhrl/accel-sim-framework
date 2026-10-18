#!/usr/bin/env python3
"""Bounded wrapper negatives and one owned Python child; never runs a simulator."""
from common import *
import run_screen as runner
import copy
import signal
import sys
import time
from test_resource_policy import sample as resource_sample

def main():
 root=RAW/'cpu-qualification'/('runner-guards-'+sha(PACK/'scripts/run_screen.py')[:12]);root.mkdir(parents=True,exist_ok=False)
 cases=[]
 child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],close_fds=True)
 fd=os.pidfd_open(child.pid)
 try:
  time.sleep(.1)
  p=runner.proc(child.pid);assert p
  maps=Path('/proc',str(child.pid),'maps').read_text();paths=runner.mapped_files(maps)
  loader=next(x for x in paths if 'ld-linux' in x)
  library=next(x for x in paths if '/libc.so' in x)
  files=[dict(path=x,sha256=sha(x)) for x in paths]
  spec=dict(runtime_path=p['exe'],runtime_sha256=sha(p['exe']),runtime_library_path=library)
  manifest=dict(runtime_files=files,loader=dict(path=loader,sha256=sha(loader)))
  _,_,_,attest=runner.attest_child(child.pid,spec,manifest);assert attest['identity_pass']
  cases.append('actual_owned_CPU_child_ELF_loader_all_mappings_attested')
  bad=copy.deepcopy(manifest);bad['runtime_files'][0]['sha256']='0'*64
  assert not runner.attest_child(child.pid,spec,bad)[3]['identity_pass']
  cases.append('changed_or_unregistered_actual_mapping_rejected')
  assert runner.proc(child.pid)['start_ticks']==p['start_ticks']
  event_file=root/'CPU_MOCK_memory.events'
  event_file.write_text('oom 0\noom_kill 17\n')
  watch=runner.start_oom_watchdog(child.pid,fd,dict(oom=0,oom_kill=17),root/'CPU_OOM_WATCH.jsonl',event_file)
  time.sleep(.05);event_file.write_text('oom 0\noom_kill 18\n')
  child.wait(timeout=5);assert child.returncode==-signal.SIGTERM
  watch[0].set();watch[1].join()
  assert watch[2]['reason']=='NEW_CGROUP_OOM_OR_OOM_KILL_LIGHT_WATCHDOG' and watch[2]['signal_sent']
  cases.append('independent_quarter_second_OOM_watchdog_owned_pidfd_STOP_during_main_work')
  cases.append('only_direct_owned_Python_child_pidfd_SIGTERM_and_reap')
 finally:
  if child.poll() is None:
   signal.pidfd_send_signal(fd,signal.SIGTERM);child.wait(timeout=5)
  os.close(fd)
 # All dummy accounting lives under this CPU-only fixture directory, outside
 # the real RAW/attempts ledger and outside the eight scientific reservations.
 original={k:getattr(runner,k) for k in ['RAW','publication_check','input_identity','admission','snapshot','collect','final_pre_popen_snapshot']}
 try:
  runner.RAW=root/'fixture-namespace';runner.RAW.mkdir()
  dummy=dict(point='CPU_NEGATIVE_NOT_A_SIMULATION',attempt_uuid='CPU_WRAPPER_ONLY_NOT_SCIENTIFIC_UUID',arm='BASE',workload='GEMM',
      configs=[],runtime_path='/NONEXISTENT_AG_CPU_NEGATIVE_DO_NOT_REPLACE',trace_list='/CPU_ONLY_NO_TRACE_OPEN',runtime_environment={'PATH':'/usr/bin:/bin'})
  fake=resource_sample()
  runner.publication_check=lambda:({}, {})
  runner.input_identity=lambda s:dict(status='CPU_MOCK_NO_TRACE_OPEN')
  runner.admission=lambda *args:({},fake)
  runner.snapshot=lambda:fake
  runner.final_pre_popen_snapshot=lambda *args:fake
  runner.collect=lambda *args:dict(status='EXPECTED_CPU_POPEN_FAILURE',performance_accepted=False)
  assert runner.budget([dummy])==[]
  result=runner.run_one(dummy,[dummy],{}, {},{})
  assert result['status']=='EXPECTED_CPU_POPEN_FAILURE'
  assert runner.budget([dummy])==[dummy['attempt_uuid']]
  terminal=json.loads(next((runner.RAW/'attempts').glob('*/RUN_TERMINAL.json')).read_text())
  assert terminal['returncode'] is None and 'FileNotFoundError' in terminal['forced_reason']
  cases.append('failed_Popen_consumes_CPU_fixture_reservation_and_retains_terminal')
  try:runner.run_one(dummy,[dummy],{}, {},{})
  except ValueError as exc:assert 'NO_RETRY' in str(exc)
  else:raise AssertionError('same dummy UUID retried')
  cases.append('second_start_same_UUID_rejected_before_Popen')
  duplicate=runner.RAW/'attempts/duplicate';duplicate.mkdir()
  write(duplicate/'RUN_START.json',dict(attempt_uuid=dummy['attempt_uuid']))
  try:runner.budget([dummy])
  except ValueError:pass
  else:raise AssertionError('duplicate receipt accepted')
  cases.append('duplicate_UUID_ledger_rejected')
 finally:
  for k,v in original.items():setattr(runner,k,v)
 write(PACK/'RUNNER_CPU_GUARDS.json',dict(status='PASS_BOUNDED_CPU_WRAPPER_GUARDS',cases=cases,
     runner_sha256=sha(PACK/'scripts/run_screen.py'),test_sha256=sha(Path(__file__)),
     owned_Python_children=1,full_simulations_started=0,scientific_UUIDs_consumed=0,
     raw=str(root),foreign_signals=0))
 print('PASS: 7 CPU wrapper guards including independent OOM watchdog; own Python child only; zero scientific UUIDs consumed')

if __name__=='__main__':main()
