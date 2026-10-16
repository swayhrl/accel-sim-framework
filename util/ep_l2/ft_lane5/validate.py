"""Independent, fail-closed checks for producer adapters; never infer absent evidence."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


class InvalidEvidence(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidEvidence(message)


def integer(value):
    return type(value) is int and value >= 0


def sector_bytes(value):
    require(isinstance(value, str) and len(value) == 64, '32-byte sector payload required')
    try:
        return bytes.fromhex(value)
    except ValueError as error:
        raise InvalidEvidence('invalid sector data') from error


def reference_requests(program):
    """An externally specified ordered stimulus, separate from producer observations.

    Line/sector identities and initial/store bytes come from the test stimulus.
    Request IDs are epoch+slice scoped; no implicit initial-zero memory.
    Concurrent schedules require an explicitly linearized test stimulus.
    """
    memory, expected = {}, {}
    for op in program:
        key = (op['epoch'], op['slice'], op['line'], op['sector'])
        require(type(op['sector']) is int and 0 <= op['sector'] < 4, 'invalid sector')
        if op['op'] == 'initialize':
            require(key not in memory, 'duplicate initialization')
            memory[key] = sector_bytes(op['data'])
            continue
        request = (op['epoch'], op['slice'], op['request_id'])
        require(request not in expected, 'duplicate reference request identity')
        require(key in memory, 'uninitialized reference sector')
        if op['op'] == 'read':
            expected[request] = {'kind': 'read', 'data': memory[key]}
        elif op['op'] == 'write':
            memory[key] = sector_bytes(op['data'])
            expected[request] = {'kind': 'write', 'data': None}
        else:
            raise InvalidEvidence('unsupported reference operation; atomic needs a dedicated adapter')
    require(bool(expected), 'empty reference stimulus is not validation')
    return expected


def validate_events(program, events):
    expected = reference_requests(program)
    admitted, responded = set(), set()
    descriptors, payloads, wads, tags = {}, {}, {}, {}
    wb_created, wb_accepted, wb_completed = set(), set(), set()
    wb_to_wad = {}
    generations, bank_ops = {}, set()
    observed = Counter()
    terminal = None
    last_cycle = -1
    for event in events:
        kind = event['event']
        require(terminal is None, 'event after terminal')
        require(integer(event['cycle']) and event['cycle'] >= last_cycle, 'nonmonotonic observation')
        last_cycle = event['cycle']
        observed[kind] += 1
        scope = (event.get('epoch'), event.get('slice'))
        if kind == 'request_admitted':
            key = (*scope, event['request_id'])
            require(key in expected and key not in admitted, 'unknown or duplicate requester admission')
            admitted.add(key)
        elif kind == 'response':
            key = (*scope, event['request_id'])
            require(key in admitted and key not in responded, 'unadmitted or duplicate response')
            require(key in descriptors.values(), 'response has no live requester descriptor')
            reference = expected[key]
            require(event['kind'] == reference['kind'], 'wrong response kind')
            if reference['kind'] == 'read':
                require(sector_bytes(event['data']) == reference['data'], 'sector data/version mismatch')
            responded.add(key)
        elif kind in {'descriptor_alloc', 'descriptor_free'}:
            key = (*scope, event['id'])
            if kind.endswith('alloc'):
                req = (*scope, event['request_id'])
                require(key not in descriptors and req in admitted and req not in responded,
                        'duplicate/ownerless descriptor allocation')
                require(req not in descriptors.values(), 'requester owns multiple descriptors')
                descriptors[key] = req
                require(sum(k[:2] == scope for k in descriptors) <= 512, 'descriptor capacity exceeded')
            else:
                require(key in descriptors and descriptors[key] in responded,
                        'descriptor freed before response enqueue or unknown free')
                del descriptors[key]
        elif kind in {'payload_alloc', 'payload_role', 'payload_free'}:
            key = (*scope, event['id'])
            if kind == 'payload_alloc':
                generation = event['generation']
                require(integer(generation), 'invalid generation')
                require(key not in payloads and generation > generations.get(key, -1),
                        'double allocation or stale generation reuse')
                require(event['role'] != 'FREE', 'FREE is not a live payload owner')
                generations[key] = generation
                payloads[key] = (generation, event['role'])
            else:
                require(key in payloads and payloads[key][0] == event['generation'], 'stale payload handle')
                if kind == 'payload_free':
                    require(not any(k[:2] == scope and v[2:] == (event['id'], event['generation'])
                                    for k, v in tags.items()), 'freeing payload still visible through tag')
                    require(integer(event['pending_sectors']) and event['pending_sectors'] == 0
                            and integer(event['read_refs']) and event['read_refs'] == 0,
                            'payload freed with unfinished consumers')
                    if event.get('wb_id') is not None:
                        require((*scope, event['wb_id']) in wb_accepted, 'WB payload freed before lower accept')
                    del payloads[key]
                else:
                    require(event['role'] != 'FREE', 'use payload_free to retire an owner')
                    payloads[key] = (event['generation'], event['role'])
        elif kind == 'tag_bind':
            require(event['reason'] != 'detached_fill', 'detached fill reinstalled tag')
            key = (*scope, event['tag'])
            handle = (*scope, event['payload_id'])
            require(handle in payloads and payloads[handle][0] == event['payload_generation'],
                    'resident tag points to nonexistent payload')
            tags[key] = (event['line'], event['tag_generation'], event['payload_id'], event['payload_generation'])
        elif kind == 'tag_unbind':
            key = (*scope, event['tag'])
            require(key in tags and tags[key][1] == event['tag_generation'], 'stale tag unbind')
            del tags[key]
        elif kind == 'fill':
            handle = (*scope, event['payload_id'])
            require(handle in payloads and payloads[handle][0] == event['payload_generation'], 'fill has stale landing')
            if event['attached']:
                require(tags.get((*scope, event['tag'])) ==
                        (event['line'], event['tag_generation'], event['payload_id'], event['payload_generation']),
                        'stale fill mutated reused tag')
            else:
                require(event['installed_tag'] is False, 'detached fill installed tag')
        elif kind in {'wad_alloc', 'wad_free'}:
            key = (*scope, event['id'])
            if kind == 'wad_alloc':
                require(key not in wads, 'double WAD allocation')
                wads[key] = event['line']
            else:
                require(key in wads and (*scope, event['wb_id']) in wb_completed,
                        'WAD released before true WB set_done')
                require(wb_to_wad.get((*scope, event['wb_id'])) == key, 'wrong WAD/WB binding')
                del wads[key]
        elif kind.startswith('wb_'):
            key = (*scope, event['id'])
            if kind == 'wb_created':
                wad = (*scope, event['wad_id'])
                require(key not in wb_created and wad in wads, 'duplicate WB or missing pre-reserved WAD')
                wb_created.add(key)
                wb_to_wad[key] = wad
            elif kind == 'wb_lower_accepted':
                require(key in wb_created and key not in wb_accepted, 'unknown/duplicate WB lower accept')
                require(event['data_handoff_accounted'] is True, 'lower pointer is not an accounted data handoff')
                wb_accepted.add(key)
            elif kind == 'wb_completed':
                require(key in wb_accepted and key not in wb_completed, 'unknown/duplicate WB set_done')
                wb_completed.add(key)
            else:
                raise InvalidEvidence('unknown WB milestone')
        elif kind == 'bank_op':
            require(type(event['bank']) is int and 0 <= event['bank'] < 4, 'invalid bank')
            key = (*scope, event['cycle'], event['bank'])
            require(key not in bank_ops, 'multiple payload operations in one bank cycle')
            bank_ops.add(key)
        elif kind == 'terminal':
            terminal = event
        else:
            raise InvalidEvidence('unknown event type: ' + kind)
    require(terminal is not None, 'missing hardware terminal evidence')
    require(set(expected) == admitted == responded, 'requester exact-once closure failed')
    require(not descriptors and not wads, 'descriptor/WAD leak')
    require(wb_created == wb_accepted == wb_completed, 'WB lifecycle not drained')
    require(not payloads, 'directed fixture payloads not explicitly retired')
    require(terminal['hardware_drained'] is True, 'process exit does not prove hardware drained')
    # Coverage is reported; absence of a WB/RO/TVD event is never a test of that feature.
    return {'status': 'PASS', 'unique_requesters': len(expected),
            'responses': len(responded), 'wb_created': len(wb_created),
            'wb_lower_accepted': len(wb_accepted), 'wb_completed': len(wb_completed),
            'event_coverage': dict(observed)}


SUMMARY_FIELDS = {
    'cycles', 'instructions', 'unique_requesters', 'responses',
    'live_descriptors', 'live_line_mshrs', 'live_wad', 'pending_lower_reads',
    'pending_returns', 'pending_responses', 'wb_created', 'wb_lower_accepted',
    'wb_completed', 'payload_capacity', 'payload_free', 'payload_roles',
    'transient_payloads', 'hardware_drained', 'workload_termination',
}


def validate_summary(summary, identity):
    require(SUMMARY_FIELDS <= set(summary), 'missing explicit terminal metrics: ' + str(SUMMARY_FIELDS - set(summary)))
    for key in SUMMARY_FIELDS - {'payload_roles', 'hardware_drained', 'workload_termination'}:
        require(integer(summary[key]), 'invalid numeric metric: ' + key)
    require(summary['cycles'] > 0 and summary['instructions'] > 0, 'empty performance execution')
    require(summary['hardware_drained'] is True, 'hardware drain proof missing')
    require(summary['workload_termination'] == identity['termination_contract'], 'workload termination contract mismatch')
    require(summary['unique_requesters'] == summary['responses'], 'requester/response count mismatch')
    for key in ('live_descriptors', 'live_line_mshrs', 'live_wad', 'pending_lower_reads',
                'pending_returns', 'pending_responses', 'transient_payloads'):
        require(summary[key] == 0, 'nonempty terminal resource: ' + key)
    require(summary['wb_created'] == summary['wb_lower_accepted'] == summary['wb_completed'], 'WB terminal mismatch')
    roles = summary['payload_roles']
    require(isinstance(roles, dict) and bool(roles) and 'FREE' not in roles, 'live owner roles required, FREE separately counted')
    require(all(integer(value) for value in roles.values()), 'invalid role accounting')
    slices = summary.get('slices')
    require(slices == 64, 'performance summary must cover all 64 slices')
    capacity = identity['feature_vector']['payload_capacity_per_slice']
    require(capacity in (1168, 1160) and summary['payload_capacity'] == capacity * slices,
            'physical budget/scope mismatch')
    require(summary['payload_free'] + sum(roles.values()) == summary['payload_capacity'], 'payload conservation failure')
    require(summary.get('requester_exact_once_audit') is True, 'aggregate counts alone cannot prove exact-once responses')
    require(summary.get('data_correctness_qualification') is True, 'data correctness qualification missing')
    return {'status': 'PASS', 'scope': 'global sum of 64 slices', 'cycles_scope': 'native cumulative GPU cycles; never slice-summed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_events(json.loads(args.reference.read_text()),
            (json.loads(line) for line in args.events.open() if line.strip()))
    except (KeyError, TypeError, ValueError) as error:
        result = {'status': 'FAIL', 'detail': str(error)}
    result.update(reference_sha256=hashlib.sha256(args.reference.read_bytes()).hexdigest(),
                  events_sha256=hashlib.sha256(args.events.read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
