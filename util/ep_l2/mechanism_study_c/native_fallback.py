"""D input-binding fallback: certify ZERO lines; no simulator or lease entry.

Full input hashes bind a complete commandlist, not a readonly proof. Use D's
bounded offline worker for real inputs. The CLI is plan-only without --execute.
The frozen Conv proof/generator/ranges are never edited or upgraded by this tool.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import ro_oracle

SCOPE = 'NO_READONLY_CERTIFICATION'
STATUS = 'SAFE_FALLBACK_NO_CERTIFIED_LINES'
EMPTY = b'first_line,last_line_inclusive\n'


def kernels(command):
    paths = []
    for text in command.read_text().splitlines():
        text = text.strip()
        if not text or text.startswith('#'):
            continue
        if text.startswith('kernel'):
            paths.append((command.parent / text).resolve())
        elif text.startswith(('MemcpyHtoD,', 'MemcpyDtoH,')):
            parts = text.split(',')
            if len(parts) != 3:
                raise ValueError('malformed host command')
            address, count = int(parts[1], 16), int(parts[2])
            if address < 0 or count < 0 or address + count > 1 << 64:
                raise ValueError('invalid host range')
        else:
            raise ValueError('unsupported commandlist; unavailable input is not fallback-qualified')
    if not paths:
        raise ValueError('complete declared input required')
    return paths


def build(command, out, reason, producer):
    command, out = Path(command).resolve(), Path(out)
    if not reason or len(reason) > 512:
        raise ValueError('explicit bounded fallback reason required')
    before = ro_oracle.sha256(command)
    bodies = [dict(path=str(p), sha256=ro_oracle.sha256(p), bytes=p.stat().st_size)
              for p in kernels(command)]
    if ro_oracle.sha256(command) != before:
        raise ValueError('commandlist changed')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'certified_ranges.csv').write_bytes(EMPTY)
    m = dict(schema=ro_oracle.SCHEMA, status=STATUS, scope=SCOPE,
             epoch='whole_commandlist', framework_source_commit=producer,
             address_domain='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS',
             commandlist=str(command), commandlist_sha256=before,
             kernels=bodies, kernel_count=len(bodies),
             unresolved_opcodes={'NO_READONLY_CERTIFICATION': 1},
             assumptions=[], fallback_reason=reason,
             counts={'CERTIFIED_RO_lines': 0, 'CERTIFIED_RO_read_lane_references': 0},
             artifacts={'certified_ranges.csv': hashlib.sha256(EMPTY).hexdigest()},
             runtime_qualification=False,
             policy='T/M flags remain fixed; empty oracle admits NO RO transaction. All lines use ordinary W/V/native paths. E must bind full input and qualify exact binary.')
    (out / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
    return m


def verify(out):
    out = Path(out)
    m = json.loads((out / 'manifest.json').read_text())
    if (m['schema'], m['status'], m['scope'], m['epoch']) != (ro_oracle.SCHEMA, STATUS, SCOPE, 'whole_commandlist'):
        raise ValueError('wrong fallback contract')
    if (out / 'certified_ranges.csv').read_bytes() != EMPTY:
        raise ValueError('fallback may not certify any line')
    if m['counts'] != {'CERTIFIED_RO_lines': 0, 'CERTIFIED_RO_read_lane_references': 0}:
        raise ValueError('fallback coverage must be zero')
    command = Path(m['commandlist'])
    if ro_oracle.sha256(command) != m['commandlist_sha256']:
        raise ValueError('changed commandlist')
    if [str(p) for p in kernels(command)] != [k['path'] for k in m['kernels']] or len(m['kernels']) != m['kernel_count']:
        raise ValueError('partial/reordered input')
    for k in m['kernels']:
        if ro_oracle.sha256(k['path']) != k['sha256']:
            raise ValueError('changed full input')
    if m['artifacts'] != {'certified_ranges.csv': hashlib.sha256(EMPTY).hexdigest()}:
        raise ValueError('changed fallback artifacts')
    return m


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commandlist', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--reason', required=True)
    p.add_argument('--source', required=True)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    if not a.execute:
        print(json.dumps(dict(status='PLAN_ONLY', scope=SCOPE, full_body_hashing='D bounded offline admission required', commandlist=str(a.commandlist), output=str(a.out))))
    else:
        repo = Path(__file__).resolve().parents[3]
        path = str(Path(__file__).resolve().relative_to(repo))
        if subprocess.check_output(['git', '-C', str(repo), 'show', a.source + ':' + path]) != Path(__file__).read_bytes():
            raise ValueError('fallback producer not frozen at source')
        print(json.dumps(build(a.commandlist, a.out, a.reason, a.source), indent=2))
