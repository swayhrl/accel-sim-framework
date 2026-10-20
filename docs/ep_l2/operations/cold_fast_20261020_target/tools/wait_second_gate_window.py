"""Finite foreground metadata wait over existing gates; never a receiver."""
import json,pathlib,subprocess,sys,time
D=pathlib.Path(__file__).resolve().parent
count=int(sys.argv[1]) if len(sys.argv)>1 else 5
interval=int(sys.argv[2]) if len(sys.argv)>2 else 75
assert 1<=count<=10 and 60<=interval<=120
for i in range(count):
    start=time.monotonic()
    result=subprocess.run([sys.executable,str(D/'check_second_gates.py')])
    if result.returncode:
        print('LIGHTWEIGHT_CHECK_UNAVAILABLE_KEEP_HOLD_NO_DATA_ACTION',flush=True)
        if i+1<count:time.sleep(max(0,interval-(time.monotonic()-start)))
        continue
    current=json.loads((D/'LATEST_SECOND_LIGHTWEIGHT_GATE.json').read_bytes())
    if current['status']=='ALL_ORIGINAL_LIGHTWEIGHT_GATES_PASS':
        print('GATES_PASS_CONTINUE_EXISTING_SECOND_TRANSACTION_NO_USER_APPROVAL',flush=True)
        raise SystemExit(0)
    if i+1<count:time.sleep(max(0,interval-(time.monotonic()-start)))
print('FINITE_CHECK_WINDOW_RESOURCE_HOLD_CONTINUE_AUTHORIZED_MONITORING',flush=True)
