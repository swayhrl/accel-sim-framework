#!/usr/bin/env python3
"""Small independent format witnesses; requires --reader CPU diagnostic binary."""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import tempfile

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--reader',type=Path,required=True)
a = ap.parse_args()
fixture = '''0 0 0 0 0010 0000000a 1 R1 LDG 1 R2 4 0 0x10 0x14 0x18 0x1c
0 0 0 0 0020 0000000a 1 R1 LDS 1 R2 4 1 0x10 4
0 0 0 0 0030 0000000c 1 R1 LDS 1 R2 4 1 0x10 0
0 0 0 0 0040 0000000f 1 R1 LDS 1 R2 4 1 0x10 -4
0 0 0 0 0050 00000000 1 R1 LDG 1 R2 4 0 0x10
0 0 0 0 0060 00000003 1 R1 LDG 1 R2 4 2 0x10 4
-accelsim tracer version = 3
0070 00000003 1 R1 LDG 1 R2 4 0 0x10 0x14
0080 0000000c 1 R1 LDG 1 R2 4 1 0x10 4
'''
expected = dict(memory_records=8,mode0=3,mode1=4,mode2=1,zero_mask=1,
                mode0_excess=2,mode0_short=0,mode1_sparse=1,
                mode1_nonzero_first_nonzero_stride=2,mode1_nonzero_first_zero_stride=1,
                mode1_bad_payload=0,mode2_excess=0,mode2_short=0,unknown_mode=0)
with tempfile.TemporaryDirectory(prefix='hotspot-format-fixture-') as d:
    root = Path(d)
    member = root/'fixture.traceg'
    member.write_text(fixture)
    inventory = root/'inventory.tsv'
    inventory.write_text('workload\tordinal\tmember\tpath\tbytes\texpected_sha256\tactual_sha256\tidentity\n'
                         f'fixture\t1\tfixture\t{member}\t{member.stat().st_size}\tx\tx\tPASS\n')
    command = [str(a.reader.resolve()),str(inventory),str(root/'counts.tsv'),str(root/'witnesses.tsv')]
    subprocess.run(command,check=True)
    row = next(csv.DictReader((root/'counts.tsv').open(),delimiter='\t'))
    if any(int(row[k]) != v for k,v in expected.items()):
        raise ValueError(row)
    before = (root/'counts.tsv').read_bytes()
    if subprocess.run(command,capture_output=True).returncode == 0 or (root/'counts.tsv').read_bytes()!=before:
        raise ValueError('Existing output not protected')
print(json.dumps(dict(status='PASS',expected=expected,existing_output_refused=True,
                      scope='Independent explicit E>P/sparse/zero/negative/version3/base_delta fixtures; no native address qualification.')))
