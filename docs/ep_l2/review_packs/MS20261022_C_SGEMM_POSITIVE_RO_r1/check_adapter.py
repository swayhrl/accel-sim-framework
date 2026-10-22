#!/usr/bin/env python3
"""New tiny offline adapter controls, never C++/native/application tests."""
import hashlib
import json
from pathlib import Path
import sys
import single_pass_oracle as adapter

root = Path(__file__).resolve().parents[4]
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=False)
header = '-accelsim tracer version = 3\n-grid dim = (1,1,1)\n-block dim = (32,1,1)\n#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = 3\n'
body = (header + '0010 00000001 1 R1 LDG.E 1 R2 4 0 0x1000\n'
        '0020 00000001 1 R1 LDG.E 1 R2 4 0 0x1084\n'
        '0030 00000001 0 STG.E 2 R2 R1 4 0 0x1080\n#END_TB\n').encode()
results = []
for name, later, wrong in [('positive', False, False), ('later_host_exclusion', True, False), ('wrong_body_hash', False, True)]:
    directory = out / name
    directory.mkdir()
    trace = directory / 'kernel-1.traceg'; trace.write_bytes(body)
    command = directory / 'kernelslist.g'
    command.write_text('MemcpyHtoD,0x1000,4\nkernel-1.traceg\n' + ('MemcpyHtoD,0x1001,1\n' if later else ''))
    oracle, _ = adapter.load_oracle(root)
    expected = '0'*64 if wrong else hashlib.sha256(body).hexdigest()
    try:
        m, r = adapter.classify(oracle, command, trace, expected, directory/'oracle', 'FIXTURE_ONLY', 3)
        assert not wrong
        assert r['body_opens'] == 1 and r['bytes_read'] == len(body)
        assert m['counts'].get('CERTIFIED_RO_lines', 0) == (0 if later else 1)
        assert m['counts']['SAME_LINE_STORE_lines'] == (2 if later else 1)
        ranges = (directory/'oracle/certified_ranges.csv').read_text()
        assert ('0000000000001000' in ranges) != later
        results.append(dict(case=name, status='PASS', body_opens=1))
    except ValueError as e:
        if not wrong or 'SHA' not in str(e): raise
        assert not (directory/'oracle/manifest.json').exists()
        results.append(dict(case=name, status='PASS_EXPECTED_HASH_REFUSAL_NO_MANIFEST'))
(out/'CONTROL_RESULTS.json').write_text(json.dumps(dict(status='PASS_OFFLINE_PYTHON_ONLY', cases=results),indent=2)+'\n')
print(json.dumps(results))
