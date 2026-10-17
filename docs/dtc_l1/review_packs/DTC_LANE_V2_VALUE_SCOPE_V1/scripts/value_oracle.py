#!/usr/bin/env python3
"""Synthetic byte/version and read-from checker, NOT a cache/K2/ISA simulator.

Allocation read-from choices and publish points are input assumptions. Neither
source_E nor ACK/kernel/ordinary markers invent a payload/coherence transition.
"""
import argparse
import json
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]

def observe(case):
    memory = bytearray.fromhex(case['initial_hex'])
    versions = [0] * len(memory)
    epoch = 0
    snapshots, writes, reads, markers = {}, {}, [], []
    for event in case['events']:
        op = event['op']
        if op == 'capture':
            snapshots[event['name']] = (bytes(memory), list(versions))
        elif op == 'write_intent':
            assert event['uid'] not in writes
            writes[event['uid']] = (event['offset'], bytes.fromhex(event['hex']), False)
        elif op == 'publish':
            off, data, done = writes[event['uid']]
            assert not done, 'one externally supplied publication per write'
            assert 0 <= off and off + len(data) <= len(memory)
            epoch += 1
            memory[off:off + len(data)] = data
            versions[off:off + len(data)] = [epoch] * len(data)
            writes[event['uid']] = (off, data, True)
        elif op == 'read':
            payload, version = (bytes(memory), versions) if event['from'] == 'memory' else snapshots[event['from']]
            off, size = event.get('offset', 0), event['size']
            assert 0 <= off and off + size <= len(payload)
            reads.append({'label': event['label'], 'hex': payload[off:off + size].hex(),
                          'versions': version[off:off + size], 'from': event['from']})
        else:
            assert op in ('source_E', 'ordinary_pending_commit', 'kernel_done',
                          'sidecar_complete', 'write_ack', 'proxy_fence', 'membar',
                          'hb_assertion', 'atomic_result'), op
            markers.append(event)
    # Literal expected bytes are authored in the fixture, independently of the
    # byte update operation. Unknown ISA/HB cases deliberately have no allowed set.
    requirements = case['required_reads']
    assert len(requirements) == len(reads)
    violations, unresolved = [], []
    for got, req in zip(reads, requirements):
        assert got['label'] == req['label']
        if req['allowed_hex'] is None:
            unresolved.append(got['label'])
        elif got['hex'] not in req['allowed_hex']:
            violations.append({'label': got['label'], 'observed': got['hex'],
                               'required_by_synthetic_contract': req['allowed_hex']})
    status = 'REJECT_SYNTHETIC_CONTRACT' if violations else (
        'UNPROVEN_NO_VALUE_PREDICATE' if unresolved else 'PASS_SYNTHETIC_CONDITIONAL')
    return {'case': case['id'], 'status': status,
            'semantic_exit': 1 if violations else 2 if unresolved else 0,
            'reads': reads, 'violations': violations, 'unresolved': unresolved,
            'markers': markers, 'scope': 'external payload/read-from assumptions; no production values'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True)
    parser.add_argument('--expect-status', required=True)
    args = parser.parse_args()
    cases = json.loads((PACK / 'inputs/value_cases.json').read_text())['cases']
    case = next(c for c in cases if c['id'] == args.case)
    result = observe(case)
    print(json.dumps(result, sort_keys=True))
    # Exit 0 means the checker observed the expected pass/reject/unproven status.
    # It never means production ISA correctness. Wrong expectations exit 1.
    return 0 if result['status'] == args.expect_status else 1

if __name__ == '__main__':
    raise SystemExit(main())
