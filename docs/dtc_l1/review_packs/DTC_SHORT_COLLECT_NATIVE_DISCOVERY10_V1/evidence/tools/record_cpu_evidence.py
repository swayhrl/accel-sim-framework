"""Record the bounded synthetic evidence tests without opening science admission."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / 'tools'
EVIDENCE = ROOT / 'evidence'
NAMES = ('mechanism_strict.py', 'mechanism_outbox.py',
         'test_mechanism_evidence_cpu.py', 'record_gate_arithmetic.py')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


env = dict(os.environ)
env.pop('DTC_R0_TRUE164', None)
run = subprocess.run([sys.executable, '-B', 'test_mechanism_evidence_cpu.py', '-v'],
                     cwd=TOOLS, env=env, text=True, capture_output=True, check=False)
output = run.stdout + run.stderr
count_ok = ('Ran 5 tests' in output and '\nOK\n' in output and run.returncode == 0)
log = EVIDENCE / 'R0_MECHANISM_EVIDENCE_CPU.log'
with log.open('x', encoding='utf-8') as stream:
    stream.write(output)
    stream.flush()
    os.fsync(stream.fileno())
receipt = dict(schema='DTC_SHORT_COLLECT_R0_MECHANISM_EVIDENCE_CPU_V1',
               utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               status='PASS_SYNTHETIC_ONLY' if count_ok else 'FAIL',
               test_exit_code=run.returncode,
               test_count=5 if count_ok else None,
               test_log=str(log), test_log_sha256=sha(log),
               tool_sha256={name: sha(TOOLS / name) for name in NAMES},
               actual_true164_positive_path_tested=False,
               actual_scientific_strict_tested=False,
               science_admission_granted=False,
               new_science_requests=0, model_starts=0)
path = EVIDENCE / 'R0_MECHANISM_EVIDENCE_CPU.json'
with path.open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, indent=2, sort_keys=True)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(receipt, indent=2, sort_keys=True))
if not count_ok:
    raise SystemExit(1)
