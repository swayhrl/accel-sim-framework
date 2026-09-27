#!/usr/bin/env python3
"""Independent frozen consumer trace-parser-only check; no simulator run."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
FORMAL = ROOT / 'raw/formal_full5'
PARSER = Path('/data/c16/awma/simcompat-v2/ldgdepbar_diagnostic_20260917/frozen_traceparser_only')
PARSER_SOURCE = Path('/tmp/frozen_traceparser_only_smoke.cc')
PASS = re.compile(r'FROZEN_TRACEPARSER_ONLY_PASS instructions=(\d+) ldgdepbar=(\d+)')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(index: int, member: str) -> dict:
    path = FORMAL / 'raw' / member
    assert path.is_file()
    output = FORMAL / f'parser_{index:02d}.stdout.log'
    error = FORMAL / f'parser_{index:02d}.stderr.log'
    with output.open('w') as out, error.open('w') as err:
        result = subprocess.run([str(PARSER), str(path)], stdout=out, stderr=err,
                                timeout=1200)
    text = output.read_text()
    matches = PASS.findall(text)
    assert result.returncode == 0 and len(matches) == 1, (index, result.returncode, error.read_text()[-1000:])
    instructions, ldgdepbar = map(int, matches[0])
    assert instructions > 0
    return {'roi_launch_index': index, 'traceg_member': member,
            'parser_returncode': result.returncode,
            'parsed_instructions': instructions,
            'ldgdepbar_count': ldgdepbar,
            'parser_status': 'PASS',
            'parser_stdout_sha256': sha(output),
            'parser_stderr_sha256': sha(error)}


def main() -> None:
    members = (FORMAL / 'raw/kernelslist.g').read_text().splitlines()
    assert len(members) == 18
    rows_by_index = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(one, index, member): index
                   for index, member in enumerate(members)}
        for future in as_completed(futures):
            row = future.result()
            rows_by_index[row['roi_launch_index']] = row
            print(json.dumps({'parser_member': row['roi_launch_index'] + 1,
                              'instructions': row['parsed_instructions']}), flush=True)
    rows = [rows_by_index[index] for index in range(18)]
    with (ROOT / 'TRACE_PARSER_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    receipt = {'status': 'PASS', 'members': 18,
               'all_frozen_trace_parser_only_pass': True,
               'total_parsed_instructions': sum(row['parsed_instructions'] for row in rows),
               'parser_binary_sha256': sha(PARSER),
               'parser_smoke_source_sha256': sha(PARSER_SOURCE),
               'not_accel_sim_execution': True}
    (ROOT / 'TRACE_PARSER_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
